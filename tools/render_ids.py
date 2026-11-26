"""Re-render the Reels for the given entry ids (only the ones whose output is stale or missing).

    python3 tools/render_ids.py 018 046          # render in order, one at a time
    python3 tools/render_ids.py --force 018      # render even if the output matches the content
    python3 tools/render_ids.py --list           # list every unposted Reel (held ones too) that is stale or missing

Same job as `python -m atlas prepare`, but for chosen ids. Logs 'done: <id>' or 'failed: <id>' per id.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from atlas.__main__ import CONTENT_FILES, LOG, OUT, SCHEDULE, _find, _group, _prepare_job, check_item, content_entries, slug  # noqa: E402


def main():
    args = sys.argv[1:]
    force = "--force" in args
    ids = [a for a in args if a not in ("--force", "--list")]
    entries = content_entries()
    if "--list" in args:
        done = {(x["entry"], x["kind"]) for x in json.loads(LOG.read_text())}
        n = 0
        for r in json.loads(SCHEDULE.read_text()):
            if r["kind"] != "reel" or (r["entry"], "reel") in done or r["entry"] not in entries:
                continue
            problem = check_item(r, _find(r), entries)
            if problem:
                n += 1
                print(f"{r['entry']} {entries[r['entry']]['name']} ({r.get('not_before', '')}"
                      f"{', held' if r.get('hold') else ''}): {problem}")
        print(f"{n} queued Reel(s) need rendering")
        return
    groups = {}
    for f in CONTENT_FILES:
        path = ROOT / "content" / f
        if path.exists():
            groups.update({e["id"]: _group(f) for e in json.loads(path.read_text())})
    rows = {r["entry"]: r for r in json.loads(SCHEDULE.read_text()) if r["kind"] == "reel"}
    for i in ids:
        e = entries.get(i)
        if e is None:
            print(f"failed: {i} (not in content files)", flush=True)
            continue
        row = rows.get(i, {"entry": i, "kind": "reel", "day": 0})
        problem = check_item(row, _find(row), entries)
        if not problem and not force:
            print(f"skip: {i} (fresh)", flush=True)
            continue
        folder = str(OUT / groups[i] / f"{i}-{slug(e['name'])}")
        for attempt in (1, 2):
            try:
                print(f"rendering {i} ({problem or 'forced'}), attempt {attempt}", flush=True)
                print("done:", _prepare_job((e, folder, True, False)), flush=True)
                break
            except Exception as err:  # retry once, then report
                print(f"error on {i}: {err}", flush=True)
        else:
            print(f"failed: {i}", flush=True)


if __name__ == "__main__":
    main()
