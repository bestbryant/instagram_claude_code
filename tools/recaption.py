"""Rebuild the caption of every queued Reel from the content and atlas/captions.py, without re-rendering.

    python3 tools/recaption.py            # show which queued Reels' captions would change
    python3 tools/recaption.py --write    # write caption-reel.txt (and caption-carousel.txt) for them

Run it whenever atlas/captions.py changes (OFFER_FIRST, the promise lines) or an entry's caption text changes.
A changed episode.caption also changes the entry, which makes the Reel stale (check_item compares the rendered
entry with the content); for a change to the caption alone the picture and the voice are unaffected, so --write
also updates the caption in the rendered snapshot (reel-entry.json and entry.json), and nothing else in it.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from atlas import captions  # noqa: E402
from atlas.__main__ import LOG, SCHEDULE, _find, content_entries  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    entries = content_entries()
    done = {(x["entry"], x["kind"]) for x in json.loads(LOG.read_text())}
    changed = 0
    for row in json.loads(SCHEDULE.read_text()):
        if row["kind"] != "reel" or (row["entry"], row["kind"]) in done:
            continue
        folder, e = _find(row), entries.get(row["entry"])
        if folder is None or e is None:
            continue
        by = e.get("requested_by")
        new = captions.reel(e, by) + "\n"
        old = (folder / "caption-reel.txt").read_text() if (folder / "caption-reel.txt").exists() else ""
        snap = folder / "reel-entry.json"
        cap_new = (e.get("episode") or {}).get("caption")
        snap_e = json.loads(snap.read_text()) if snap.exists() else {}
        cap_old = (snap_e.get("episode") or {}).get("caption")
        if new == old and cap_new == cap_old:
            continue
        changed += 1
        print(f"{row['entry']} {e['name']}: " + ("caption text" if new != old else "") + (" + snapshot caption" if cap_new != cap_old else ""))
        if a.write:
            (folder / "caption-reel.txt").write_text(new)
            (folder / "caption-carousel.txt").write_text(captions.carousel(e, by) + "\n")
            if cap_new != cap_old:
                for name in ("reel-entry.json", "entry.json"):
                    p = folder / name
                    if p.exists():
                        d = json.loads(p.read_text())
                        if isinstance(d.get("episode"), dict):
                            d["episode"]["caption"] = cap_new
                            p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print(f"{changed} queued Reels {'rewritten' if a.write else 'would change'}")


if __name__ == "__main__":
    main()
