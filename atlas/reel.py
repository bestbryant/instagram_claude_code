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
    from .video import render_shots, still

    render_shots(reel_shots(spec, seed, entry, requested_by), out, seed=seed)
    if cover_path is not None:
        to_image(still(cover_shot(spec, seed, entry))).save(cover_path, quality=92)
    return Path(out)


def cover_shot(spec: Spec, seed: int, entry: dict):
    from .video import Shot, overlay

    left = dict(align="left", x=96, width=W_SAFE)
    hook = entry.get("cover") or entry["hook"]
    y = entry.get("text_y", {}).get("cover", 0.24)
    card = overlay([dict(text=hook, y=y, kind="serif", weight="Medium", size=96, leading=1.1, **left)])
    cam = entry.get("camera", {}).get("cover", {})
    return Shot(1.0, spec, seed, pan=50, zoom=tuple(cam.get("zoom", (1.7, 1.7))), focus=tuple(cam["focus"]) if "focus" in cam else None,
                cards=[(card, 0, 1, 0, 0)])


# camera presets a story beat can ask for by name: (zoom start, zoom end, focus)
FRAMINGS = {
    "wide": ((1.0, 1.08), None),
    "medium": ((1.35, 1.45), None),
    "close": ((1.9, 2.05), None),
    "gag": ((1.9, 2.05), "gag"),             # the joke itself, even when a sign shares the frame
    "crowd": ((1.7, 1.8), "crowd"),
    "sky": ((1.3, 1.4), (0.5, 0.3)),
    "left": ((1.5, 1.6), ("x", 0.3)),       # this x, at the height of the scene's gag
    "right": ((1.5, 1.6), ("x", 0.7)),
    "sign": ((1.8, 1.9), "sign"),
    "cartographer": ((2.0, 2.15), "cartographer"),
    "house": ((1.8, 1.9), "house"),          # a house standing on the stage (else the gag)
}


def _beat_shot(spec: Spec, seed: int, beat: dict, card, seconds: float):
    """One story beat: its framing (a preset name or an explicit camera) and any scene variant."""
    from dataclasses import replace
    from .video import Shot
    shot = beat.get("shot") or "medium"
    if isinstance(shot, str):
        shot = {"framing": shot}
    zoom, focus = FRAMINGS.get(shot.get("framing", "medium"), FRAMINGS["medium"])
    zoom = tuple(shot.get("zoom", zoom))
    focus = tuple(shot["focus"]) if "focus" in shot else focus
    variant = replace(spec, **beat["spec"]) if beat.get("spec") else spec
    return Shot(seconds, variant, seed, pan=50, zoom=zoom, focus=focus, cards=[(card, 0.0, seconds, 0.0, 0.0)])


def next_stop(entry: dict) -> str:
    """The planet that follows this one in the posting queue (for the end card's teaser)."""
    import json
    from pathlib import Path
    try:
        from .__main__ import content_entries
        sched = json.loads((Path(__file__).resolve().parent.parent / "content" / "schedule.json").read_text())
        reels = [x for x in sched if x["kind"] == "reel" and not x.get("hold")]
        ids = [x["entry"] for x in reels]
        i = ids.index(entry["id"])
        names = content_entries()
        for x in ids[i + 1:]:
            if x in names and x != entry["id"]:
                return names[x]["name"]
    except (ValueError, OSError, KeyError):
        pass
    return ""


def story_shots(spec: Spec, seed: int, entry: dict, requested_by: str | None = None) -> list:
    """A story episode: the opener on a wide shot, then one shot per beat, then the end card,
    which pans back to the opening frame so the Reel loops cleanly."""
    from .video import Shot, overlay
    ep = entry["episode"]
    series = f"No. {entry['id']} · {text.BRAND}"
    left = dict(align="left", x=96, width=W_SAFE)
    first = ep.get("opener") or entry.get("opener") or entry["hook"]
    kicker = entry.get("kicker")
    opener = overlay([dict(text=kicker or series, y=0.2, kind="italic", size=42 if kicker else 36, **left),
                      dict(text=first, y=0.235, kind="serif", weight="Medium", size=84, leading=1.12, **left)])
    read = lambda line, extra=0.9: round(max(2.4, 0.3 * len(line.split()) + extra), 1)
    t_hook = read(f"{kicker or ''} {first}".strip())
    cam = entry.get("camera", {}).get("hook", {})
    shots = [Shot(t_hook, spec, seed, pan=50, zoom=tuple(cam.get("zoom", (1.0, 1.12))),
                  focus=tuple(cam["focus"]) if "focus" in cam else None, cards=[(opener, 0.0, t_hook, 0.0, 0.0)])]
    for i, beat in enumerate(ep["beats"]):
        last = i == len(ep["beats"]) - 1
        secs = beat.get("seconds") or read(beat["text"], 1.3 if last else 0.9)
        card = overlay([dict(text=beat["text"], y=beat.get("text_y", 0.2), kind="italic", size=64, leading=1.16, **left)])
        shots.append(_beat_shot(spec, seed, beat, card, secs))
    end = ep.get("end") or ("Found for " + requested_by if requested_by else "Your name has a planet too.")
    if "{next}" in end:
        nxt = next_stop(entry)
        end = end.replace("{next}", nxt) if nxt else "Your name has a planet too."
    ty = entry.get("text_y", {}).get("name", 0.3)
    name = overlay([dict(text=series, y=ty, kind="italic", size=36),
                    dict(text=entry["name"], y=ty + 0.035, kind="serif", weight="Medium", size=170),
                    dict(text=end, y=ty + 0.145, kind="italic", size=46)])
    ncam = entry.get("camera", {}).get("name", {})
    shots.append(Shot(2.6, spec, seed, pan=50, zoom=tuple(ncam.get("zoom", (1.08, 1.0))),
                      focus=tuple(ncam["focus"]) if "focus" in ncam else (tuple(cam["focus"]) if "focus" in cam else None),
                      cards=[(name, 0.0, 2.6, 0.0, 0.0)], tick=True, reverse=True))
    return shots


def reel_shots(spec: Spec, seed: int, entry: dict, requested_by: str | None = None) -> list:
    """The Reel's shot list (hook, setup, punchline, name card), also used to check frames before rendering."""
    from .video import Shot, overlay
    if entry.get("episode"):
        return story_shots(spec, seed, entry, requested_by)

    series = f"No. {entry['id']} · {text.BRAND}"
    beats = entry.get("beats") or entry["reel_lines"]
    left = dict(align="left", x=96, width=W_SAFE)
    # per-entry text heights, to keep lines off bright suns and lamps
    ty = {"setup": 0.24, "punch": 0.24, "name": 0.3, **entry.get("text_y", {})}
    first = entry.get("opener") or entry["hook"]
    if requested_by:
        opener = overlay([dict(text=f"{requested_by} asked for", y=0.2, kind="italic", size=48, **left),
                          dict(text=entry["name"], y=0.235, kind="serif", weight="Medium", size=150, **left)])
    else:
        # name planets carry "Every Luna gets this planet." as a small kicker above the joke
        opener = overlay([dict(text=entry.get("kicker") or series, y=0.2, kind="italic", size=36 if not entry.get("kicker") else 42, **left),
                          dict(text=first, y=0.235, kind="serif", weight="Medium", size=84, leading=1.12, **left)])
    setup = overlay([dict(text=beats[0], y=ty["setup"], kind="italic", size=66, leading=1.15, **left)])
    punch = overlay([dict(text=beats[1], y=ty["punch"], kind="italic", size=66, leading=1.15, **left)])
    cta = entry.get("cta") or ("Found for " + requested_by if requested_by else "Your name has a planet too.")
    name = overlay([dict(text=series, y=ty["name"], kind="italic", size=36),
                    dict(text=entry["name"], y=ty["name"] + 0.035, kind="serif", weight="Medium", size=170),
                    dict(text=cta, y=ty["name"] + 0.145, kind="italic", size=46)])
    # about 0.3 s per word plus time to settle, so every line can actually be read
    read = lambda line, extra=0.9: round(max(2.4, 0.3 * len(line.split()) + extra), 1)
    t_hook = read(entry["name"] if requested_by else f"{entry.get('kicker', '')} {first}".strip(), 1.0 if requested_by else 0.9)
    t_setup, t_punch = read(beats[0]), read(beats[1], 1.2)
    # text cuts with the picture: fading a card also fades the dark band behind it, which
    # flashes the bright scene for a few frames. The end card pans backwards so its last
    # frame is the hook's first, and the loop has no jump.
    # an entry can move the camera per shot: "camera": {"setup": {"zoom": [a, b], "focus": [x, y]}}
    cam = entry.get("camera", {})
    move = lambda k, zoom: dict(zoom=tuple(cam.get(k, {}).get("zoom", zoom)),
                                focus=tuple(cam[k]["focus"]) if "focus" in cam.get(k, {}) else None)
    return [
        Shot(t_hook, spec, seed, pan=50, cards=[(opener, 0.0, t_hook, 0.0, 0.0)], **move("hook", (1.0, 1.12))),
        Shot(t_setup, spec, seed, pan=50, cards=[(setup, 0.0, t_setup, 0.0, 0.0)],
             **move("setup", (1.55, 1.65) if spec.sign and spec.gag else (1.9, 2.05))),
        Shot(t_punch, spec, seed, pan=50, cards=[(punch, 0.0, t_punch, 0.0, 0.0)], **move("punch", (1.4, 1.28))),
        Shot(2.4, spec, seed, pan=50, cards=[(name, 0.0, 2.4, 0.0, 0.0)], tick=True, reverse=True,
             **move("name", (1.08, 1.0))),
    ]


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
