"""Preview a short before rendering it (HOUSE_RULES S7): stills of every moment that matters, plus the voiced timing.

    python3 tools/short_preview.py 090 086                    # entries from the content files
    python3 tools/short_preview.py --file draft.json          # a draft entry, or a list of them, not yet in content
    python3 tools/short_preview.py --file draft.json --out /some/dir --silent

For each entry it writes <out>/<id>-<name>_preview.jpg, a contact sheet of: frame 0 (the hook as a stranger
first sees it), just after the hook's onset, each beat (before and after its own onset, if it has one) and the
end card. It prints when each shot starts, the turn (the first beat with an onset, or the last beat), when the end
line lands and the total, against S4: the turn by about 7.5 s, the end line by about 11 s, about 14 s in all.
With the narrator installed (kokoro_onnx) the timing is the real voiced timing; --silent skips the voice.
About 20-40 s per entry, against about 9 min for a full render.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PIL import Image, ImageDraw  # noqa: E402

from atlas.__main__ import content_entries, slug  # noqa: E402
from atlas.render import Spec, seed_from, to_image  # noqa: E402
from atlas.reel import short_shots, voiced  # noqa: E402
from atlas.video import _Prepared  # noqa: E402

TW, TH = 360, 640          # thumbnail size (a third of 1080 x 1920)
BOTTOM = 0.75              # S1/R4: nothing that matters below 75% of the height (the caption sits there)


def moments(shots):
    """(label, shot index, seconds into the shot) for every frame worth looking at."""
    out = [("frame 0", 0, 0.05)]
    s0 = shots[0]
    if s0.swap:
        out.append((f"onset +0.8 s", 0, min(s0.swap[0] + 0.8, s0.seconds - 0.05)))
    else:
        out.append(("hook (mid)", 0, s0.seconds / 2))
    for i, s in enumerate(shots[1:-1], 1):
        if s.swap:
            out.append((f"beat {i} before", i, max(0.05, s.swap[0] - 0.1)))
            out.append((f"beat {i} after", i, min(s.swap[0] + 0.8, s.seconds - 0.05)))
        else:
            out.append((f"beat {i}", i, s.seconds * 0.6))
    e = len(shots) - 1
    if shots[e].swap:
        out.append(("end before", e, max(0.05, shots[e].swap[0] - 0.1)))
        out.append(("end after", e, min(shots[e].swap[0] + 0.8, shots[e].seconds - 0.05)))
    else:
        out.append(("end card", e, shots[e].seconds * 0.6))
    return out


def sheet(frames, path):
    cols = min(4, len(frames))
    rows = (len(frames) + cols - 1) // cols
    pad, lab = 8, 26
    im = Image.new("RGB", (cols * (TW + pad) + pad, rows * (TH + lab + pad) + pad), (24, 24, 28))
    d = ImageDraw.Draw(im)
    for k, (label, img) in enumerate(frames):
        x = pad + (k % cols) * (TW + pad)
        y = pad + (k // cols) * (TH + lab + pad)
        im.paste(img.resize((TW, TH), Image.LANCZOS), (x, y + lab))
        d.text((x + 4, y + 6), label, fill=(235, 235, 235))
        yb = y + lab + int(TH * BOTTOM)          # the line below which nothing important may sit
        d.line([(x, yb), (x + TW, yb)], fill=(255, 80, 80), width=1)
    im.save(path, quality=88)


def preview(e, out: Path, silent: bool):
    spec, seed = Spec(**e["spec"]), seed_from(e["name"])
    speak = (not silent) and voiced(e)
    shots = short_shots(spec, seed, e, speak=speak)
    starts, t = [], 0.0
    for s in shots:
        starts.append(t)
        t += s.seconds
    beats = e["short"].get("beats", [])
    turn_i = next((i for i, b in enumerate(beats) if b.get("onset")), len(beats) - 1) + 1
    turn_at = starts[turn_i] + (shots[turn_i].swap[0] if shots[turn_i].swap else 0.0)
    print(f"\n{e['id']} {e['name']}  ({'voiced' if speak else 'silent timing'})")
    for i, s in enumerate(shots):
        what = "hook" if i == 0 else ("end card" if i == len(shots) - 1 else f"beat {i}")
        line = (s.say or "").replace("\n", " / ") if speak else ""
        print(f"  {starts[i]:5.2f} s  {what:9} {s.seconds:4.2f} s  {line}")
    end_at = starts[-1]
    print(f"  turn {turn_at:.1f} s (S4: about 7.5)  end line {end_at:.1f} s (about 11)  total {t:.1f} s (about 14)"
          + ("  ** long" if t > 16.5 or turn_at > 8.5 else ""))
    cache = {}
    frames = []
    for label, i, ts in moments(shots):
        p = _Prepared(shots[i], cache)
        frames.append((f"{label} @{starts[i] + ts:.1f}s", to_image(p.image(ts, starts[i] + ts))))
    path = out / f"{e['id']}-{slug(e['name'])}_preview.jpg"
    sheet(frames, path)
    print(f"  sheet: {path}")
    return {"id": e["id"], "turn": round(turn_at, 2), "end": round(end_at, 2), "total": round(t, 2), "sheet": str(path)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--file", help="a JSON entry, or a list of entries, not yet in the content files")
    ap.add_argument("--out", default=str(ROOT / "output" / "_preview"))
    ap.add_argument("--silent", action="store_true", help="skip the narrator (faster; timing is then the silent timing)")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    todo = []
    if a.file:
        data = json.loads(Path(a.file).read_text())
        todo += data if isinstance(data, list) else [data]
    if a.ids:
        entries = content_entries()
        for i in a.ids:
            if i not in entries:
                print(f"not found: {i}")
                continue
            todo.append(entries[i])
    for e in todo:
        if not e.get("short"):
            print(f"{e.get('id')}: no short to preview")
            continue
        try:
            preview(e, out, a.silent)
        except Exception as err:            # a draft with a bad field should not stop the others
            print(f"{e.get('id')} {e.get('name')}: preview failed: {type(err).__name__}: {err}")


if __name__ == "__main__":
    main()
