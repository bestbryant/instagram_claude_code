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

    speak = voiced(entry)
    render_shots(reel_shots(spec, seed, entry, requested_by, speak=speak), out, seed=seed, speak=speak)
    if cover_path is not None:
        to_image(still(cover_shot(spec, seed, entry))).save(cover_path, quality=92)
    return Path(out)


VOICE_DEFAULT = False   # story Reels read aloud by the cartographer; an entry or episode can set "voice" either way


def voiced(entry: dict) -> bool:
    if entry.get("short"):
        want = entry["short"].get("version", "A") in ("B", "C")
    elif entry.get("episode"):
        want = entry["episode"].get("voice", entry.get("voice", VOICE_DEFAULT))
    else:
        return False
    if want:
        from . import voice
        return voice.available()
    return False


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


def story_shots(spec: Spec, seed: int, entry: dict, requested_by: str | None = None, speak: bool = False) -> list:
    """A story episode: the opener on a wide shot, then one shot per beat, then the end card,
    which pans back to the opening frame so the Reel loops cleanly. With speak, the cartographer
    reads every line, and each shot lasts at least as long as she takes plus a breath."""
    from .video import Shot, overlay
    if speak:
        from . import voice
        spoken = lambda line, at, breath: at + voice.seconds(line) + breath if line.strip() else 0.0
    else:
        spoken = lambda line, at, breath: 0.0
    ep = entry["episode"]
    series = f"No. {entry['id']} · {text.BRAND}"
    left = dict(align="left", x=96, width=W_SAFE)
    first = ep.get("opener") or entry.get("opener") or entry["hook"]
    kicker = entry.get("kicker")
    opener = overlay([dict(text=kicker or series, y=0.2, kind="italic", size=42 if kicker else 36, **left),
                      dict(text=first, y=0.235, kind="serif", weight="Medium", size=84, leading=1.12, **left)])
    read = lambda line, extra=0.9: round(max(2.4, 0.3 * len(line.split()) + extra), 1)
    say_hook = f"{kicker or ''}\n{first}".strip()
    t_hook = round(max(read(f"{kicker or ''} {first}".strip()), spoken(say_hook, 0.05, 0.45)), 2)
    cam = entry.get("camera", {}).get("hook", {})
    shots = [Shot(t_hook, spec, seed, pan=50, zoom=tuple(cam.get("zoom", (1.0, 1.12))),
                  focus=tuple(cam["focus"]) if "focus" in cam else None, cards=[(opener, 0.0, t_hook, 0.0, 0.0)],
                  say=say_hook if speak else "", say_at=0.05)]
    for i, beat in enumerate(ep["beats"]):
        last = i == len(ep["beats"]) - 1
        secs = beat.get("seconds") or read(beat["text"], 1.3 if last else 0.9)
        secs = round(max(secs, spoken(beat["text"], 0.15, 0.75 if last else 0.4)), 2)
        card = overlay([dict(text=beat["text"], y=beat.get("text_y", 0.2), kind="italic", size=64, leading=1.16, **left)])
        shot = _beat_shot(spec, seed, beat, card, secs)
        shot.say = beat["text"] if speak else ""
        shots.append(shot)
    end = ep.get("end") or ("Found for " + requested_by if requested_by else "Your name has a planet too.")
    if "{next}" in end:
        nxt = next_stop(entry)
        end = end.replace("{next}", nxt) if nxt else "Your name has a planet too."
    ty = entry.get("text_y", {}).get("name", 0.3)
    name = overlay([dict(text=series, y=ty, kind="italic", size=36),
                    dict(text=entry["name"], y=ty + 0.035, kind="serif", weight="Medium", size=170),
                    dict(text=end, y=ty + 0.145, kind="italic", size=46)])
    ncam = entry.get("camera", {}).get("name", {})
    say_end = f"{entry['name']}.\n{end}"
    t_end = round(max(2.6, read(end, 1.4), spoken(say_end, 0.2, 0.9)), 2)   # the end line is the one people screenshot: long enough to read twice
    shots.append(Shot(t_end, spec, seed, pan=50, zoom=tuple(ncam.get("zoom", (1.08, 1.0))),
                      focus=tuple(ncam["focus"]) if "focus" in ncam else (tuple(cam["focus"]) if "focus" in cam else None),
                      cards=[(name, 0.0, t_end, 0.0, 0.0)], tick=True, reverse=True, say=say_end if speak else "", say_at=0.2))
    return shots


def short_shots(spec: Spec, seed: int, entry: dict, speak: bool = False) -> list:
    """The short, hook-first cut (about 14-20 s), from docs/PLAN.md: frame 0 is close on the joke with the
    premise as one big line and the reason to send it under it; something appears or changes at about 0.4 s
    (with a hit on the soundtrack); two or three beats put the turn by about 8 s; a 2 s end card."""
    from dataclasses import replace
    from .video import Shot, overlay
    sh = entry["short"]
    left = dict(align="left", x=96, width=W_SAFE)
    if speak:
        from . import voice
        spoken = lambda line, at, breath: at + voice.seconds(line) + breath if line.strip() else 0.0
    else:
        spoken = lambda line, at, breath: 0.0
    read = lambda line, extra=0.6: round(max(1.8, 0.28 * len(line.split()) + extra), 2)

    title, sub = sh["title"], sh.get("sub", "")
    items = [dict(text=title, y=sh.get("title_y", 0.17), kind="serif", weight="Medium", size=88, leading=1.1, **left)]
    if sub:
        items.append(dict(text=sub, y="after", gap=0.02, kind="italic", size=58, leading=1.14, **left))
    hook_card = overlay(items)
    say_hook = f"{title}\n{sub}".strip()
    t_hook = round(max(read(say_hook, 1.0), spoken(say_hook, 0.05, 0.35)), 2)
    onset = sh.get("onset") or {}
    flips = {"sign", "palette", "particles", "aurora", "stars", "lamp", "glow_rims", "mist", "snow"}   # changes, not objects: cut
    motion = onset.get("motion") or ("cut" if set(onset.get("spec") or {}) <= flips else "auto")
    swap = (float(onset.get("at", 0.4)), replace(spec, **onset["spec"]), motion) if onset.get("spec") else None
    base = replace(spec, **sh["spec"]) if sh.get("spec") else spec       # the scene before the onset
    zoom, focus = FRAMINGS.get(sh.get("framing", "gag"), FRAMINGS["gag"])
    zoom = tuple(sh.get("zoom", (zoom[0] * 0.92, zoom[1] * 0.92)))
    shots = [Shot(t_hook, base, seed, pan=50, zoom=zoom, focus=tuple(sh["focus"]) if "focus" in sh else focus,
                  cards=[(hook_card, 0.0, t_hook, 0.0, 0.0)], tick=False, say=say_hook if speak else "", say_at=0.05,
                  swap=swap)]
    after = swap[1] if swap else spec         # beats continue from the changed scene
    for i, beat in enumerate(sh["beats"]):
        last = i == len(sh["beats"]) - 1
        secs = beat.get("seconds") or read(beat["text"], 1.0 if last else 0.6)
        secs = round(max(secs, spoken(beat["text"], 0.1, 0.55 if last else 0.3)), 2)
        card = overlay([dict(text=beat["text"], y=beat.get("text_y", 0.18), kind="italic", size=70, leading=1.14, **left)])
        shot = _beat_shot(after, seed, beat, card, secs)
        shot.say = beat["text"] if speak else ""
        shot.say_at = 0.1
        shots.append(shot)
    series = f"No. {entry['id']} · {text.BRAND}"
    end = sh.get("end") or entry["episode"].get("end", "")
    ty = sh.get("name_y", entry.get("text_y", {}).get("name", 0.3))
    name = overlay([dict(text=series, y=ty, kind="italic", size=36),
                    dict(text=entry["name"], y=ty + 0.035, kind="serif", weight="Medium", size=170),
                    dict(text=end, y=ty + 0.145, kind="italic", size=50)])
    t_end = round(max(2.0, spoken(end, 0.15, 0.5)), 2)
    shots.append(Shot(t_end, after, seed, pan=50, zoom=(1.12, 1.04), focus=focus if isinstance(focus, tuple) else None,
                      cards=[(name, 0.0, t_end, 0.0, 0.0)], say=end if speak else "", say_at=0.15))
    return shots


def reel_shots(spec: Spec, seed: int, entry: dict, requested_by: str | None = None, speak: bool = False) -> list:
    """The Reel's shot list (hook, setup, punchline, name card), also used to check frames before rendering."""
    from .video import Shot, overlay
    if entry.get("short"):
        return short_shots(spec, seed, entry, speak=speak)
    if entry.get("episode"):
        return story_shots(spec, seed, entry, requested_by, speak=speak)

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
