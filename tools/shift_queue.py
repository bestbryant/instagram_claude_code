"""Move every unposted row of the queue later by whole days (the outage rule: never catch up).

    python3 tools/shift_queue.py --days 1            # show what would change
    python3 tools/shift_queue.py --days 1 --apply    # write schedule.json, comments.json and the content files
    python3 tools/shift_queue.py --auto              # after an outage: the fewest whole days that put the next
                                                     # unposted row in the future (add --apply to write)

It shifts not_before on every unposted schedule row (rows marked fixed_date keep their dates, and so do
held rows whose date has already passed, like a cut parked long ago; a new Reel held until it is checked moves),
shifts post_at on every unposted comment, and re-dates each unposted part one's teaser
(short.sign 'Part two, <Weekday>: ...') to the weekday its part two now posts. A part one whose
teaser changed must be re-rendered and checked before it posts (check_item reports it stale).
"""
import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
CONTENT_FILES = ["launch.json", "names.json", "sequels.json", "charted.json"]
TEASER = re.compile(r"^Part two, (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday):")


def _iso(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _z(d):
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int)
    ap.add_argument("--auto", action="store_true", help="shift by the fewest whole days that put the next unposted row "
                    "at least 30 minutes in the future")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    schedule = json.loads((CONTENT / "schedule.json").read_text())
    log = json.loads((CONTENT / "published.json").read_text())
    done = {(x["entry"], x["kind"]) for x in log}
    if a.auto:
        now = datetime.now(timezone.utc)
        floating = [_iso(r["not_before"]) for r in schedule if r["kind"] == "reel" and (r["entry"], r["kind"]) not in done
                    and r.get("not_before") and not r.get("fixed_date") and not (r.get("hold") and _iso(r["not_before"]) < now)]
        first = min(floating)
        days = 0
        while first + timedelta(days=days) < now + timedelta(minutes=30):
            days += 1
        print(f"next unposted row: {_z(first)}; behind by {days} day(s); it moves to {_z(first + timedelta(days=days))}")
        if days == 0:
            print("nothing to shift")
            return
        a.days = days
    if a.days is None:
        ap.error("give --days N or --auto")
    delta = timedelta(days=a.days)
    new_slot = {}
    now = datetime.now(timezone.utc)
    for row in schedule:
        if (row["entry"], row["kind"]) in done or row.get("fixed_date") or not row.get("not_before"):
            continue
        if row.get("hold") and _iso(row["not_before"]) < now:     # a row parked long ago (008's process cut), not a
            continue                                               # new Reel held until it is checked: leave it be
        old = row["not_before"]
        row["not_before"] = _z(_iso(old) + delta)
        new_slot[row["entry"]] = _iso(row["not_before"])
        print(f"{row['entry']:5} {old} -> {row['not_before']}")


    # a seasonal Reel (post_by, e.g. Christmas) that the shift pushed past its date swaps slots with the latest ordinary
    # floating Reel that still lands on or before that date, so every slot stays filled and nothing misses its season
    moved = [r for r in schedule if r["kind"] == "reel" and (r["entry"], r["kind"]) not in done and r.get("not_before")
             and not r.get("fixed_date") and not r.get("after") and r["entry"] in new_slot]
    for row in sorted((r for r in moved if r.get("post_by")), key=lambda r: r["post_by"]):
        if row["not_before"][:10] <= row["post_by"]:
            continue
        swaps = [r for r in moved if not r.get("post_by") and r["not_before"][:10] <= row["post_by"]
                 and r["not_before"] < row["not_before"]]
        if not swaps:
            print(f"  WARNING: {row['entry']} must post by {row['post_by']} and no ordinary Reel is early enough to swap with")
            continue
        other = max(swaps, key=lambda r: r["not_before"])
        print(f"  seasonal: {row['entry']} {row['not_before']} <-> {other['entry']} {other['not_before']} (post by {row['post_by']})")
        row["not_before"], other["not_before"] = other["not_before"], row["not_before"]
        new_slot[row["entry"]], new_slot[other["entry"]] = _iso(row["not_before"]), _iso(other["not_before"])

    comments = json.loads((CONTENT / "comments.json").read_text())
    for c in comments:
        if c.get("posted") or not c.get("post_at"):
            continue
        old = c["post_at"]
        c["post_at"] = _z(_iso(old) + delta)
        print(f"comment on {c.get('on')}: {old} -> {c['post_at']}")

    rerender = []
    changed_files = {}
    for f in CONTENT_FILES:
        path = CONTENT / f
        if not path.exists():
            continue
        entries = json.loads(path.read_text())
        dirty = False
        for e in entries:
            sign = (e.get("short") or {}).get("sign") or ""
            m = TEASER.match(sign)
            if not m or e["id"] not in new_slot or f"{e['id']}b" not in new_slot:
                continue
            day = new_slot[f"{e['id']}b"].strftime("%A")
            if day != m.group(1):
                e["short"]["sign"] = sign.replace(m.group(1), day, 1)
                dirty = True
                rerender.append(e["id"])
                print(f"teaser {e['id']}: '{sign}' -> '{e['short']['sign']}'")
        if dirty:
            changed_files[path] = entries

    if a.apply:
        dump = lambda obj, ind: json.dumps(obj, indent=ind, ensure_ascii=False) + "\n"
        (CONTENT / "schedule.json").write_text(dump(schedule, 1))   # the files' own indents (checked 17 Nov)
        (CONTENT / "comments.json").write_text(dump(comments, 2))
        for path, entries in changed_files.items():
            path.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n")
        print("written." + (f" Re-render and check: {' '.join(rerender)}" if rerender else ""))
    else:
        print("dry run (add --apply to write)." + (f" Would need re-renders: {' '.join(rerender)}" if rerender else ""))


if __name__ == "__main__":
    main()
