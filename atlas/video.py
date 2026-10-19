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


def _ease(t):
    return t * t * (3 - 2 * t)


class _Prepared:
    def __init__(self, shot: Shot, cache: dict):
        self.shot = shot
        if shot.still is not None:
            self.scene = None
            return
        key = (repr(shot.spec), shot.seed, shot.pan)
        if key not in cache:
            scene = build(shot.spec, shot.seed, W, H, pan=shot.pan)
            mid = frame(scene, 0.5, shot.pan, 0.0, grain=0)
            cache[key] = (scene, bloom_threshold(mid), ink_palette(mid, extra=spec_inks(shot.spec)))
        self.scene, self.thr, self.inks = cache[key]
        if isinstance(shot.focus, str):
            shot.focus = tuple(getattr(self.scene, "marks", {}).get(shot.focus) or getattr(self.scene, "focus", (0.5, 0.5)))
        if shot.focus is None:
            shot.focus = getattr(self.scene, "focus", (0.5, 0.5))
        elif shot.focus[0] == "x":                # ("x", fx): that x, at the height of the scene's gag
            shot.focus = (shot.focus[1], getattr(self.scene, "focus", (0.5, 0.5))[1])

    def image(self, ts: float, t_global: float) -> np.ndarray:
        s = self.shot
        u = ts / max(s.seconds, 1e-6)
        if self.scene is None:
            img = s.still
        else:
            img = frame(self.scene, t=1 - u if s.reverse else u, pan=s.pan, fps_t=t_global, grain=0, bloom_thr=self.thr)
            img = print_finish(img, self.inks, seed=s.seed & 0xFFFF, dither=0.045)
        z = s.zoom[0] + (s.zoom[1] - s.zoom[0]) * _ease(u)
        img = _zoom(img, z, s.focus)
        for c in s.cards:
            card, t0, t1 = c[:3]
            ramp_in = c[3] if len(c) > 3 else (0.12 if t1 - t0 < 1.5 else 0.25)
            ramp_out = c[4] if len(c) > 4 else ramp_in
            op = _fade2(ts, t0, t1, ramp_in, ramp_out)
            if op > 0:
                al = card[..., 3:4] * op
                img = img * (1 - al) + card[..., :3] * al
        return img


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


def render_shots(shots: list[Shot], out: Path, seed: int = 0, fps: int = 30, overlays=(), cover_at: float | None = None,
                 cover_path: Path | None = None) -> Path:
    """Render shots back to back. overlays: (card, t0, t1) on the whole timeline."""
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
        cmd = ["ffmpeg", "-y", "-loglevel", "error",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-i", wav,
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "7M", "-bufsize", "14M",
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
