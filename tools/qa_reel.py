"""Check rendered Reels before they are released (the hourly routine's step 3).

    python3 tools/qa_reel.py 091 092                 # every check
    python3 tools/qa_reel.py --no-voice 091          # skip the transcript (frames, size and freshness only)

Per Reel it checks:
- FRESH: the render matches the content (check_item: not stale, not missing, cover present, preflight passes);
- size under 19.5 MB and the duration;
- frames: a sheet of the real video at frame 0, just after each onset and in every shot, written to
  output/_preview/<id>-<name>_qa.jpg with a red line at 75% of the height (nothing that matters below it). Look at it;
- voice: the narrator's audio transcribed with faster-whisper (base.en) against the lines the Reel should say;
  word error rate 15% or less passes (a name the transcriber spells differently costs a word, so read the misses).
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PIL import Image, ImageDraw  # noqa: E402

from atlas.__main__ import SCHEDULE, _find, check_item, content_entries  # noqa: E402
from atlas.render import Spec, seed_from  # noqa: E402
from atlas.reel import short_shots, voiced  # noqa: E402

LIMIT_MB = 19.5
TW, TH = 360, 640


def _frame(mp4: Path, t: float) -> Image.Image:
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "f.png"
        subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(mp4), "-frames:v", "1", str(out)], check=True)
        return Image.open(out).convert("RGB")


def _duration(mp4: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


_ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen " \
        "seventeen eighteen nineteen".split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def _say(n: int) -> str:
    """Digits the transcriber writes ("50") as the words the narrator said ("fifty"), up to 9,999."""
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n // 10] + ("" if n % 10 == 0 else " " + _ONES[n % 10])
    if n < 1000:
        return _ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " and " + _say(n % 100))
    return _say(n // 1000) + " thousand" + ("" if n % 1000 == 0 else " " + _say(n % 1000))


def _words(s: str) -> list:
    s = s.lower().replace("’", "'").replace("-", " ")
    s = re.sub(r"(?<=\d),(?=\d{3})", "", s)
    s = re.sub(r"\d+", lambda m: _say(int(m.group())) if int(m.group()) < 10000 else m.group(), s)
    s = re.sub(r"[^a-z0-9' ]+", " ", s)
    return [w.strip("'") for w in s.split() if w.strip("'")]


def wer(ref: list, hyp: list) -> float:
    d = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        prev, d[0] = d[0], i
        for j, h in enumerate(hyp, 1):
            cur = min(d[j] + 1, d[j - 1] + 1, prev + (r != h))
            prev, d[j] = d[j], cur
    return d[len(hyp)] / max(1, len(ref))


_whisper = None


def transcribe(mp4: Path) -> str:
    global _whisper
    import numpy as np
    import soundfile as sf
    if _whisper is None:
        from faster_whisper import WhisperModel
        _whisper = WhisperModel("base.en", device="cpu", compute_type="int8")
    with tempfile.TemporaryDirectory() as d:
        wav = Path(d) / "a.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp4), "-ac", "1", "-ar", "16000", str(wav)], check=True)
        audio, _ = sf.read(str(wav), dtype="float32")      # an array, not a path (a path trips an av TypeError)
    segs, _ = _whisper.transcribe(np.asarray(audio, dtype=np.float32), language="en", beam_size=5)
    return " ".join(s.text.strip() for s in segs)


def qa(entry_id: str, entries: dict, rows: dict, do_voice: bool) -> dict:
    e = entries[entry_id]
    row = rows.get(entry_id, {"entry": entry_id, "kind": "reel", "day": 0})
    folder = _find(row)
    res = {"id": entry_id, "name": e["name"]}
    problem = check_item(row, folder, entries)
    res["fresh"] = problem is None
    if problem:
        res["problem"] = problem
    if folder is None or not (folder / "reel.mp4").exists():
        return res
    mp4 = folder / "reel.mp4"
    res["mb"] = round(mp4.stat().st_size / 1e6, 2)
    res["seconds"] = round(_duration(mp4), 2)
    speak = voiced(e)
    shots = short_shots(Spec(**e["spec"]), seed_from(e["name"]), e, speak=speak)
    starts, t = [], 0.0
    for s in shots:
        starts.append(t)
        t += s.seconds
    marks = [("frame 0", 0.05)]
    for i, s in enumerate(shots):
        what = "hook" if i == 0 else ("end" if i == len(shots) - 1 else f"beat {i}")
        if s.swap:
            marks.append((f"{what} onset+0.8", starts[i] + min(s.swap[0] + 0.8, s.seconds - 0.1)))
        else:
            marks.append((what, starts[i] + s.seconds * 0.6))
    marks = [(lab, min(ts, res["seconds"] - 0.05)) for lab, ts in marks]
    cols = 4
    rows_n = (len(marks) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (TW + 8) + 8, rows_n * (TH + 34) + 8), (24, 24, 28))
    d = ImageDraw.Draw(sheet)
    for k, (lab, ts) in enumerate(marks):
        x, y = 8 + (k % cols) * (TW + 8), 8 + (k // cols) * (TH + 34)
        sheet.paste(_frame(mp4, ts).resize((TW, TH), Image.LANCZOS), (x, y + 26))
        d.text((x + 4, y + 6), f"{lab} @{ts:.1f}s", fill=(235, 235, 235))
        d.line([(x, y + 26 + int(TH * 0.75)), (x + TW, y + 26 + int(TH * 0.75))], fill=(255, 80, 80))
    out = ROOT / "output" / "_preview"
    out.mkdir(parents=True, exist_ok=True)
    res["sheet"] = str(out / f"{folder.name}_qa.jpg")
    sheet.save(res["sheet"], quality=88)
    if do_voice and speak:
        expect = " ".join(s.say for s in shots if s.say)
        heard = transcribe(mp4)
        ref, hyp = _words(expect), _words(heard)
        res["wer"] = round(100 * wer(ref, hyp), 1)
        res["heard"] = heard
        res["missed"] = sorted(set(ref) - set(hyp))
    res["pass"] = (res["fresh"] and res["mb"] < LIMIT_MB and (res.get("wer", 0) <= 15))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--no-voice", action="store_true")
    a = ap.parse_args()
    entries = content_entries()
    rows = {r["entry"]: r for r in json.loads(SCHEDULE.read_text()) if r["kind"] == "reel"}
    for i in a.ids:
        if i not in entries:
            print(f"{i}: not in the content files")
            continue
        r = qa(i, entries, rows, not a.no_voice)
        head = f"{r['id']} {r['name']}: {'FRESH' if r['fresh'] else 'NOT FRESH (' + r.get('problem', '') + ')'}"
        if "mb" in r:
            head += f", {r['mb']} MB, {r['seconds']} s"
        if "wer" in r:
            head += f", WER {r['wer']}%" + (f" (missed: {' '.join(r['missed'])})" if r["missed"] else "")
        head += "  PASS" if r.get("pass") else "  FAIL"
        print(head)
        if "heard" in r:
            print(f"   heard: {r['heard']}")
        if "sheet" in r:
            print(f"   sheet: {r['sheet']}")


if __name__ == "__main__":
    main()
