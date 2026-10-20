"""Shot-list video engine: cuts, pans, push-ins and timed text, for faster Reels.

A Reel is a list of Shots. Each shot is a planet scene (or a still) shown for a
few seconds with its own camera move and text; shots are joined with hard cuts
and a soft tick on the soundtrack so the edit has rhythm.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import wave
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

from . import audio, text
from .render import Spec, bloom_threshold, build, frame, ink_palette, print_finish, spec_inks, to_image

W, H = 1080, 1920


@dataclass
class Shot:
    seconds: float
    spec: Spec | None = None
    seed: int = 0
    still: np.ndarray | None = None          # use a ready image instead of a scene
    pan: float = 160.0                       # px the nearest layer travels during the shot
    zoom: tuple = (1.0, 1.0)                 # start and end scale (>= 1, centred on focus)
    focus: tuple | str | None = None         # zoom centre as fractions of the frame, a scene mark ("sign",
                                             # "cartographer"), or None for the scene's gag
    cards: list = field(default_factory=list)  # (rgba card array, t0, t1) in shot seconds
    tick: bool = True                        # click on the cut into this shot
    reverse: bool = False                    # pan backwards (the end card, so its last frame is the hook's first)
    say: str = ""                            # what the narrator reads over this shot (voiced Reels only)
    say_at: float = 0.15                     # seconds into the shot she starts
    swap: tuple | None = None                # (t, Spec[, motion]): the scene becomes this variant t s in, with a hit on the
                                             # soundtrack. motion "auto" (default): what it adds rises into place from its
                                             # own baseline like a pop-up page (a big change, like a palette, just cuts);
                                             # "rise" forces that, "cut" forces a hard cut with a small camera punch


def _fade(ts, start, end, ramp):
    if ts < start or ts > end:
        return 0.0
    v = min(1.0, (ts - start) / ramp if ramp else 1.0, (end - ts) / ramp if ramp else 1.0)
    return v * v * (3 - 2 * v)


def _zoom(img: np.ndarray, s: float, focus) -> np.ndarray:
    if s <= 1.0001:
        return img
    h, w = img.shape[:2]
    cw, ch = w / s, h / s
    x0 = min(max(focus[0] * w - cw / 2, 0), w - cw)
    y0 = min(max(focus[1] * h - ch / 2, 0), h - ch)
    im = to_image(img).resize((w, h), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
    return np.asarray(im, np.float32) / 255


def _whole(box, focus, z_lo, z_hi, margin=0.06):   # margin covers the parallax pan (up to ~5% of the width)
    """Nudge the camera so a sign board is either fully in the crop or fully out of it, never cut at the edge.
    The crop window is checked at both ends of the shot's zoom (and the punch on an onset)."""
    def window(c, z):
        w = 1 / z
        a = min(max(c - w / 2, 0.0), 1 - w)
        return a, a + w

    def state(f):
        """'in' if the board is whole in every crop of the shot, 'out' if it never shows, else 'cut'."""
        ins, outs = [], []
        for ax, (b0, b1) in enumerate(((box[0], box[2]), (box[1], box[3]))):
            lo_a, lo_b = window(f[ax], z_lo)
            hi_a, hi_b = window(f[ax], z_hi)
            ins.append(hi_a <= b0 - 0.01 and b1 + 0.01 <= hi_b)
            outs.append(b1 <= lo_a - 0.01 or b0 >= lo_b + 0.01)
        return "in" if all(ins) else "out" if any(outs) else "cut"

    f = list(focus)
    if state(f) != "cut":
        return tuple(f), True
    for ax, (b0, b1) in enumerate(((box[0], box[2]), (box[1], box[3]))):
        lo_a, lo_b = window(f[ax], z_lo)          # widest crop
        hi_a, hi_b = window(f[ax], z_hi)          # tightest crop
        w_hi, w_lo = 1 / z_hi, 1 / z_lo
        moves = []
        if b1 - b0 + 2 * margin <= w_hi:          # bring it fully in
            moves.append((b0 - margin) - hi_a if b0 - margin < hi_a else (b1 + margin) - hi_b)
        moves.append((b1 + margin) - lo_a if (b0 + b1) / 2 < (lo_a + lo_b) / 2 else (b0 - margin) - lo_b)   # push it out
        for d in sorted(moves, key=abs):
            g = list(f)
            g[ax] += d
            if abs(d) <= 0.3 * w_lo and state(g) != "cut":    # don't swing the camera off its subject
                return tuple(g), True
    return tuple(focus), False


def _ease(t):
    return t * t * (3 - 2 * t)


RISE = 0.45   # seconds an onset object takes to rise into place
SLIDE = 0.8   # seconds an onset object takes to slide in from the side (a forest walking in)


class _Prepared:
    def __init__(self, shot: Shot, cache: dict):
        self.shot = shot
        self._grew = False
        if shot.still is not None:
            self.scene = None
            return
        self.scene, self.thr, self.inks = self._built(shot.spec, cache)
        self.after = self._built(shot.swap[1], cache) if shot.swap else None
        if isinstance(shot.focus, str):
            # an object the onset brings in (no mark before it) is framed where it will appear
            later = getattr(self.after[0], "marks", {}).get(shot.focus) if self.after else None
            shot.focus = tuple(getattr(self.scene, "marks", {}).get(shot.focus) or later or getattr(self.scene, "focus", (0.5, 0.5)))
        if shot.focus is None:
            shot.focus = getattr(self.scene, "focus", (0.5, 0.5))
        elif shot.focus[0] == "x":                # ("x", fx): that x, at the height of the scene's gag
            shot.focus = (shot.focus[1], getattr(self.scene, "focus", (0.5, 0.5))[1])
        box = getattr(self.scene, "marks", {}).get("sign_box")
        if box and max(shot.zoom) > 1.05:
            shot.focus, ok = _whole(box, shot.focus, min(shot.zoom), max(shot.zoom) * 1.04)
            if not ok and not shot.swap:              # no camera fixes it: this close shot simply doesn't show the board
                from dataclasses import replace
                self.scene, self.thr, self.inks = self._built(replace(shot.spec, sign=""), cache)

    def _built(self, spec, cache):
        key = (repr(spec), self.shot.seed, self.shot.pan)
        if key not in cache:
            scene = build(spec, self.shot.seed, W, H, pan=self.shot.pan)
            mid = frame(scene, 0.5, self.shot.pan, 0.0, grain=0)
            cache[key] = (scene, bloom_threshold(mid), ink_palette(mid, extra=spec_inks(spec)))
        return cache[key]

    def image(self, ts: float, t_global: float) -> np.ndarray:
        s = self.shot
        u = ts / max(s.seconds, 1e-6)
        swapped = s.swap is not None and ts >= s.swap[0]
        rose = False
        if self.scene is None:
            img = s.still
        else:
            tt = 1 - u if s.reverse else u
            how = (s.swap[2] if len(s.swap) > 2 else "auto") if s.swap else "cut"
            if swapped and ts < s.swap[0] + (SLIDE if how == "slide" else RISE) and how != "cut":
                if how == "slide":
                    img, rose = self._slide((ts - s.swap[0]) / SLIDE, tt, t_global)
                else:
                    img, rose = self._rise((ts - s.swap[0]) / RISE, tt, t_global, force=how == "rise")
            if not rose:
                scene, thr, inks = self.after if swapped else (self.scene, self.thr, self.inks)
                img = frame(scene, t=tt, pan=s.pan, fps_t=t_global, grain=0, bloom_thr=thr)
            img = print_finish(img, (self.after if swapped else (self.scene, self.thr, self.inks))[2], seed=s.seed & 0xFFFF, dither=0.045)
        z = s.zoom[0] + (s.zoom[1] - s.zoom[0]) * _ease(u)
        if swapped and not self._grew:
            z *= 1 + 0.04 * np.exp(-(ts - s.swap[0]) / 0.14)     # a hard change gets a small punch, settling in about 0.4 s
        img = _zoom(img, z, s.focus)
        tint = self._tint()
        for c in s.cards:
            card, t0, t1 = c[:3]
            ramp_in = c[3] if len(c) > 3 else (0.12 if t1 - t0 < 1.5 else 0.25)
            ramp_out = c[4] if len(c) > 4 else ramp_in
            op = _fade2(ts, t0, t1, ramp_in, ramp_out)
            if op > 0:
                al = card[..., 3:4] * op
                rgb = card[..., :3]
                if tint is not None:          # the shade behind the text takes the sky's own hue, not grey
                    rgb = rgb + tint * (1 - rgb)
                img = img * (1 - al) + rgb * al
        return img

    def _rise(self, p, tt, t_global, force=False):
        """The onset as motion: whatever the new scene adds (pixels that differ) rises out of its own baseline,
        easing out with a slight overshoot. Returns (raw image, True), or (None, False) when the change is too big
        to be an object (then the caller cuts)."""
        s = self.shot
        a = frame(self.scene, t=tt, pan=s.pan, fps_t=t_global, grain=0, bloom_thr=self.thr)
        b = frame(self.after[0], t=tt, pan=s.pan, fps_t=t_global, grain=0, bloom_thr=self.after[1])
        m = (np.abs(b - a).max(axis=-1) > 0.035).astype(np.float32)
        if not force and m.mean() > 0.22:
            self._grew = False
            return None, False
        self._grew = True
        rows = np.flatnonzero(m.max(axis=1))
        if not len(rows):
            return b, True
        h_obj = rows[-1] - rows[0] + 1
        base = np.where(m.any(axis=0), m.shape[0] - 1 - np.argmax(m[::-1], axis=0), -1)    # lowest changed row per column
        c1 = 1.4
        e = 1 + (c1 + 1) * (p - 1) ** 3 + c1 * (p - 1) ** 2      # ease-out with overshoot
        off = int(round((1 - e) * h_obj))                       # >0: still below its baseline; <0: overshooting up
        bs, ms = np.zeros_like(b), np.zeros_like(m)
        if off >= 0:
            bs[off:], ms[off:] = b[:b.shape[0] - off], m[:m.shape[0] - off]
        else:
            bs[:off], ms[:off] = b[-off:], m[-off:]
        yy = np.arange(m.shape[0])[:, None]
        ms *= (yy <= base[None, :])                               # hidden below its own baseline, like a pop-up page
        ms = ms[..., None]
        return a * (1 - ms) + bs * ms, True

    def _slide(self, p, tt, t_global):
        """The onset as a sideways arrival: whatever the new scene adds slides in from the right edge and settles
        with a slight overshoot."""
        s = self.shot
        a = frame(self.scene, t=tt, pan=s.pan, fps_t=t_global, grain=0, bloom_thr=self.thr)
        b = frame(self.after[0], t=tt, pan=s.pan, fps_t=t_global, grain=0, bloom_thr=self.after[1])
        self._grew = True
        m = (np.abs(b - a).max(axis=-1) > 0.035).astype(np.float32)
        c1 = 1.2
        e = 1 + (c1 + 1) * (p - 1) ** 3 + c1 * (p - 1) ** 2
        off = int(round((1 - e) * m.shape[1] * 0.45))            # >0: still to the right of its place
        bs, ms = np.zeros_like(b), np.zeros_like(m)
        if off >= 0:
            bs[:, off:], ms[:, off:] = b[:, :b.shape[1] - off], m[:, :m.shape[1] - off]
        else:
            bs[:, :off], ms[:, :off] = b[:, -off:], m[:, -off:]
        ms = ms[..., None]
        return a * (1 - ms) + bs * ms, True

    def _tint(self):
        if self.scene is None:
            return None
        if not hasattr(self, "_tint_rgb"):
            self._tint_rgb = (np.asarray(self.scene.pal.sky[1], np.float32) * 0.4).astype(np.float32)
        return self._tint_rgb


def _fade2(ts, t0, t1, ramp_in, ramp_out):
    """Opacity with separate in/out ramps; a ramp of 0 means fully on at that edge."""
    if ts < t0 or ts > t1:
        return 0.0
    a = 1.0 if ramp_in <= 0 else min(1.0, (ts - t0) / ramp_in)
    b = 1.0 if ramp_out <= 0 else min(1.0, (t1 - ts) / ramp_out)
    v = min(a, b)
    return v * v * (3 - 2 * v)


def _mix_ticks(wav_path: str, times: list[float]):
    """Add a soft paper-like tick at each cut."""
    with wave.open(wav_path, "rb") as f:
        sr, n = f.getframerate(), f.getnframes()
        pcm = np.frombuffer(f.readframes(n), "<i2").reshape(-1, 2).astype(np.float32) / 32767
    rng = np.random.default_rng(3)
    L = int(0.05 * sr)
    t = np.arange(L) / sr
    click = rng.normal(0, 1, L) * np.exp(-t / 0.008)
    click = np.convolve(click, np.ones(6) / 6, mode="same") * 0.22
    for tt in times:
        i = int(tt * sr)
        j = min(i + L, len(pcm))
        if i < j:
            pcm[i:j] += click[: j - i, None]
    pcm = np.clip(pcm, -1, 1)
    with wave.open(wav_path, "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((pcm * 32767).astype("<i2").tobytes())


def _mix_hits(wav_path: str, times: list[float]):
    """A soft, low pluck where something appears or changes on screen."""
    with wave.open(wav_path, "rb") as f:
        sr, n = f.getframerate(), f.getnframes()
        pcm = np.frombuffer(f.readframes(n), "<i2").reshape(-1, 2).astype(np.float32) / 32767
    L = int(0.6 * sr)
    t = np.arange(L) / sr
    rng = np.random.default_rng(5)
    body = (np.sin(2 * np.pi * 196 * t) + 0.45 * np.sin(2 * np.pi * 392 * t) + 0.2 * np.sin(2 * np.pi * 587 * t)) * np.exp(-t / 0.16)
    click = np.convolve(rng.normal(0, 1, L) * np.exp(-t / 0.004), np.ones(8) / 8, mode="same")
    hit = ((body * 0.32 + click * 0.18) * (1 - np.exp(-t / 0.002))).astype(np.float32)
    for tt in times:
        i = int(tt * sr)
        j = min(i + L, len(pcm))
        if i < j:
            pcm[i:j] += hit[: j - i, None]
    pcm = np.clip(pcm, -1, 1)
    with wave.open(wav_path, "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((pcm * 32767).astype("<i2").tobytes())


def _mix_voice(wav_path: str, clips: list):
    """Lay the narrator's lines (t0, mono clip at the wav's rate) over the bed, ducking the bed under them."""
    with wave.open(wav_path, "rb") as f:
        sr, n = f.getframerate(), f.getnframes()
        pcm = np.frombuffer(f.readframes(n), "<i2").reshape(-1, 2).astype(np.float32) / 32767
    voice = np.zeros(len(pcm), np.float32)
    duck = np.zeros(len(pcm), np.float32)
    for t0, clip in clips:
        i = int(t0 * sr)
        j = min(i + len(clip), len(pcm))
        if i < j:
            voice[i:j] += clip[: j - i]
            duck[max(0, i - int(0.12 * sr)):min(len(pcm), j + int(0.3 * sr))] = 1.0
    k = np.hanning(int(0.25 * sr))
    duck = np.convolve(duck, k / k.sum(), mode="same")
    pcm = pcm * (1 - 0.6 * duck)[:, None] + voice[:, None] * 0.78
    peak = np.abs(pcm).max()
    if peak > 0.97:
        pcm *= 0.97 / peak
    with wave.open(wav_path, "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((pcm * 32767).astype("<i2").tobytes())


def render_shots(shots: list[Shot], out: Path, seed: int = 0, fps: int = 30, overlays=(), cover_at: float | None = None,
                 cover_path: Path | None = None, speak: bool = False) -> Path:
    """Render shots back to back. overlays: (card, t0, t1) on the whole timeline.
    speak: the narrator reads each shot's `say` line over the bed."""
    out = Path(out)
    tmp_out = out.with_name(out.stem + ".partial.mp4")   # renamed into place only when complete
    out.parent.mkdir(parents=True, exist_ok=True)
    cache = {}
    prepared = [_Prepared(s, cache) for s in shots]
    starts = np.cumsum([0.0] + [s.seconds for s in shots])
    seconds = float(starts[-1])
    n = int(round(seconds * fps))
    with tempfile.TemporaryDirectory() as tmp:
        wav = audio.ambient(max(seconds, 3.0), seed, str(Path(tmp) / "a.wav"), loop=True)
        _mix_ticks(wav, [float(starts[i]) for i, s in enumerate(shots) if s.tick and i > 0])
        hits = [float(starts[i]) + s.swap[0] for i, s in enumerate(shots) if s.swap]
        if hits:
            _mix_hits(wav, hits)
        if speak:
            from . import voice as vo
            _mix_voice(wav, [(float(starts[i]) + s.say_at, vo.line(s.say)) for i, s in enumerate(shots) if s.say])
        cmd = ["ffmpeg", "-y", "-loglevel", "error",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-i", wav,
               "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "3800k", "-bufsize", "7600k",   # stays under jsDelivr's 20 MB per file at 40 s
               "-pix_fmt", "yuv420p", "-profile:v", "high", "-r", str(fps),
               "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart", "-f", "mp4", str(tmp_out)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        cover = None
        try:
            for f in range(n):
                tg = f / fps
                k = min(int(np.searchsorted(starts, tg, side="right")) - 1, len(shots) - 1)
                img = prepared[k].image(tg - starts[k], tg)
                for c in overlays:
                    card, t0, t1 = c[:3]
                    op = _fade2(tg, t0, t1, c[3] if len(c) > 3 else 0.15, c[4] if len(c) > 4 else 0.15)
                    if op > 0:
                        al = card[..., 3:4] * op
                        img = img * (1 - al) + card[..., :3] * al
                if cover_at is not None and cover is None and tg >= cover_at:
                    cover = img.copy()
                proc.stdin.write((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        finally:
            proc.stdin.close()
            proc.wait()
        if proc.returncode:
            tmp_out.unlink(missing_ok=True)
            raise RuntimeError(f"ffmpeg failed ({proc.returncode})")
        os.replace(tmp_out, out)
    if cover_path is not None and cover is not None:
        to_image(cover).save(cover_path, quality=92)
    return out


def still(shot: Shot) -> np.ndarray:
    """One frame from the middle of a shot, for covers."""
    return _Prepared(shot, {}).image(shot.seconds / 2, 0.0)


def overlay(items: list[dict], scrim: float = 0.42, size=(W, H)) -> np.ndarray:
    """Text overlay card. items: dict(text, y, kind='serif'|'italic'|'sans', size, weight, align, x, width)."""
    return text.overlay(size, items, scrim)
