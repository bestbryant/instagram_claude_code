"""Render a vertical Reel: parallax drift, timed text, ambient audio."""
from __future__ import annotations

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


def render_reel(spec: Spec, seed: int, entry: dict, out: Path, seconds=13.0, fps=30, W=1080, H=1920,
                pan=240.0, cover_path: Path | None = None) -> Path:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    scene = build(spec, seed, W, H, pan=pan)
    hook = text.reel_card((W, H), [entry["hook"]], "hook")
    lore = text.reel_card((W, H), entry["reel_lines"], "lore")
    name = text.reel_card((W, H), [entry["name"], entry["id"], text.CTA], "name")
    timeline = [(hook, 0.0, 3.6), (lore, 3.8, 8.9), (name, 9.1, seconds + 1)]

    n = int(seconds * fps)
    mid = frame(scene, 0.5, pan, 0.0, grain=0)
    thr = bloom_threshold(mid)
    inks = ink_palette(mid)
    with tempfile.TemporaryDirectory() as tmp:
        wav = audio.ambient(seconds, seed, str(Path(tmp) / "a.wav"))
        cmd = ["ffmpeg", "-y", "-loglevel", "error",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
               "-i", wav,
               "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-maxrate", "12M", "-bufsize", "24M",
               "-pix_fmt", "yuv420p", "-profile:v", "high", "-r", str(fps),
               "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        cover_frame = None
        try:
            for f in range(n):
                ts = f / fps
                img = frame(scene, t=f / max(n - 1, 1), pan=pan, fps_t=ts, grain=0, bloom_thr=thr)
                img = print_finish(img, inks, seed=seed & 0xFFFF, dither=0.045)
                for card, a, b in timeline:
                    op = _fade(ts, a, b)
                    if op > 0:
                        al = card[..., 3:4] * op
                        img = img * (1 - al) + card[..., :3] * al
                if cover_path is not None and abs(ts - 10.5) < 0.5 / fps:
                    cover_frame = img.copy()
                proc.stdin.write((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        finally:
            proc.stdin.close()
            proc.wait()
        if proc.returncode:
            raise RuntimeError(f"ffmpeg failed ({proc.returncode})")
    if cover_path is not None and cover_frame is not None:
        to_image(cover_frame).save(cover_path, quality=92)
    return out


def render_process(spec: Spec, seed: int, entry: dict, out: Path, fps=30, W=1080, H=1920) -> Path:
    """A 'how it's made' Reel: the print is built up layer by layer, then inked."""
    from dataclasses import replace

    out = Path(out)
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

    title = text.reel_card((W, H), [f"Building {entry['name']}, one layer at a time."], "hook")
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
               "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out)]
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
            raise RuntimeError(f"ffmpeg failed ({proc.returncode})")
    return out
