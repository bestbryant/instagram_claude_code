"""Render a vertical Reel: parallax drift, timed text, ambient audio."""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np

from . import audio, text
from .render import Spec, bloom_threshold, build, frame, ink_palette, print_finish, to_image


def _fade(ts, start, end, ramp=0.45):
    if ts < start or ts > end:
        return 0.0
    a = min(1.0, (ts - start) / ramp)
    b = min(1.0, (end - ts) / ramp)
    v = min(a, b)
    return v * v * (3 - 2 * v)


def render_reel(spec: Spec, seed: int, entry: dict, out: Path, cover_path: Path | None = None,
                requested_by: str | None = None) -> Path:
    """About 12 s, built to loop: hook on frame 1 with a push-in, a close-up on the
    gag for the setup, the punchline, then the name card on the same wide shot
    the Reel opens on."""
    from .video import Shot, overlay, render_shots, still

    series = f"No. {entry['id']} · {text.BRAND}"
    beats = entry.get("beats") or entry["reel_lines"]
    left = dict(align="left", x=96, width=W_SAFE)
    if requested_by:
        opener = overlay([dict(text=f"{requested_by} asked for", y=0.2, kind="italic", size=48, **left),
                          dict(text=entry["name"], y=0.235, kind="serif", weight="Medium", size=150, **left)])
    else:
        opener = overlay([dict(text=series, y=0.2, kind="italic", size=36, **left),
                          dict(text=entry["hook"], y=0.235, kind="serif", weight="Medium", size=84, leading=1.12, **left)])
    setup = overlay([dict(text=beats[0], y=0.24, kind="italic", size=66, leading=1.15, **left)])
    punch = overlay([dict(text=beats[1], y=0.24, kind="italic", size=66, leading=1.15, **left)])
    cta = entry.get("cta") or ("Found for " + requested_by if requested_by else "Your name has a planet too.")
    name = overlay([dict(text=series, y=0.3, kind="italic", size=36),
                    dict(text=entry["name"], y=0.335, kind="serif", weight="Medium", size=170),
                    dict(text=cta, y=0.445, kind="italic", size=46)])
    # about 0.3 s per word plus time to settle, so every line can actually be read
    read = lambda line, extra=0.9: round(max(2.4, 0.3 * len(line.split()) + extra), 1)
    t_hook = read(entry["name"] if requested_by else entry["hook"], 1.0 if requested_by else 0.9)
    t_setup, t_punch = read(beats[0]), read(beats[1], 1.2)
    shots = [
        Shot(t_hook, spec, seed, pan=50, zoom=(1.0, 1.12), cards=[(opener, 0.0, t_hook, 0.0, 0.12)]),
        Shot(t_setup, spec, seed, pan=50, zoom=(1.55, 1.65) if spec.sign and spec.gag else (1.9, 2.05),
             cards=[(setup, 0.05, t_setup, 0.15, 0.12)]),
        Shot(t_punch, spec, seed, pan=50, zoom=(1.4, 1.28), cards=[(punch, 0.05, t_punch, 0.15, 0.12)]),
        Shot(2.4, spec, seed, pan=50, zoom=(1.08, 1.0), cards=[(name, 0.05, 2.4, 0.15, 0.0)], tick=True),
    ]
    render_shots(shots, out, seed=seed)
    if cover_path is not None:
        hook = entry.get("cover") or entry["hook"]
        card = overlay([dict(text=hook, y=0.24, kind="serif", weight="Medium", size=96, leading=1.1, **left)])
        to_image(still(Shot(1.0, spec, seed, pan=50, zoom=(1.7, 1.7), cards=[(card, 0, 1, 0, 0)]))).save(cover_path, quality=92)
    return Path(out)


W_SAFE = W_REEL = 1080 - 96 - 170   # text width that stays clear of the like/comment buttons


def render_process(spec: Spec, seed: int, entry: dict, out: Path, fps=30, W=1080, H=1920) -> Path:
    """A 'how it's made' Reel: the print is built up layer by layer, then inked."""
    from dataclasses import replace

    out = Path(out)
    tmp_out = out.with_name(out.stem + ".partial.mp4")   # renamed into place only when complete
    out.parent.mkdir(parents=True, exist_ok=True)
    scene = build(spec, seed, W, H)
    full = frame(scene, grain=0)
    thr = bloom_threshold(full)
    inks = ink_palette(full)
    paper = np.ones((H, W, 3), np.float32) * np.array([243, 236, 222], np.float32) / 255
    steps = [paper]
    sky_only = replace(scene, layers=[], water_y=None)
    steps.append(frame(sky_only, grain=0, bloom_thr=thr))
    back = [layer for layer in scene.layers if layer.stage == 0]
    order = back + [layer for layer in scene.layers if layer.stage == 1]
    for i in range(1, len(order) + 1):
        water = scene.water_y if i >= len(back) else None
        steps.append(frame(replace(scene, layers=order[:i], water_y=water), grain=0, bloom_thr=thr))
    final = print_finish(steps[-1], inks, seed=seed & 0xFFFF, dither=0.045)
    steps.append(final)

    title = text.reel_card((W, H), [f"How {entry['name']} gets made, one layer at a time."], "hook")
    name = text.reel_card((W, H), [entry["name"], entry["id"], text.CTA], "name")
    step_t = 0.55
    build_end = 0.6 + step_t * (len(steps) - 2)
    ink_end = build_end + 1.4
    seconds = ink_end + 3.2
    n = int(seconds * fps)
    with tempfile.TemporaryDirectory() as tmp:
        wav = audio.ambient(seconds, seed, str(Path(tmp) / "a.wav"))
        cmd = ["ffmpeg", "-y", "-loglevel", "error",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-i", wav,
               "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-maxrate", "12M", "-bufsize", "24M",
               "-pix_fmt", "yuv420p", "-profile:v", "high", "-r", str(fps),
               "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart", "-f", "mp4", str(tmp_out)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        try:
            for f in range(n):
                ts = f / fps
                if ts < 0.6:
                    img = steps[0]
                elif ts < build_end:
                    k = (ts - 0.6) / step_t
                    i = int(k)
                    a = min(1.0, (k - i) / 0.6)
                    img = steps[i] * (1 - a) + steps[i + 1] * a
                elif ts < ink_end:
                    a = (ts - build_end) / (ink_end - build_end)
                    a = a * a * (3 - 2 * a)
                    img = steps[-2] * (1 - a) + final * a
                else:
                    img = final
                for card, t0, t1 in ((title, 0.2, min(3.4, build_end)), (name, ink_end + 0.3, seconds + 1)):
                    op = _fade(ts, t0, t1)
                    if op > 0:
                        al = card[..., 3:4] * op
                        img = img * (1 - al) + card[..., :3] * al
                proc.stdin.write((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        finally:
            proc.stdin.close()
            proc.wait()
        if proc.returncode:
            tmp_out.unlink(missing_ok=True)
            raise RuntimeError(f"ffmpeg failed ({proc.returncode})")
        os.replace(tmp_out, out)
    return out
