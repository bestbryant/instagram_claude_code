"""Check a writers' room batch and add it to the content files and the queue (held until rendered and checked).

    python3 tools/add_batch.py room/batch8/group*.json            # check only: prints every problem
    python3 tools/add_batch.py room/batch8/group*.json --apply    # add the entries and the held schedule rows
    python3 tools/add_batch.py --release 091 092                  # after qa_reel.py passes: release those rows

Name planets (a top-level kicker "Every <name> gets this planet.") go to content/names.json, place planets to
content/launch.json. New rows go at the end of the queue, two a day at 14:00 and 20:00 UTC, in id order, held.
With --slot 14 --from 2026-12-01 they take that one slot a day from that date instead, and the unposted rows
they displace move later, keeping their order (rows with a fixed_date or an 'after' keep their dates).
--post-by ID=YYYY-MM-DD marks a seasonal Reel; tools/shift_queue.py warns if a shift moves it past that date.
"""
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from atlas.render import Spec  # noqa: E402

CONTENT = ROOT / "content"
FILES = ["launch.json", "names.json", "sequels.json", "halloween.json", "charted.json"]
SLOTS = (14, 20)


def load(name):
    p = CONTENT / name
    return json.loads(p.read_text()) if p.exists() else []


def template_keys():
    ex = {e["id"]: e for f in ("launch.json", "names.json") for e in load(f)}
    return set(ex["090"]) - {"kicker"}, set(ex["090"]["short"]) | set(ex["089"]["short"])


def problems(e, used_names, used_ids):
    out = []
    top, short_keys = template_keys()
    miss = top - set(e)
    if miss:
        out.append(f"missing keys {sorted(miss)}")
    sh = e.get("short") or {}
    if sh.get("version") != "E":
        out.append("short.version is not E")
    if sh.get("sign") != "Every name has a planet.":
        out.append(f"sign is {sh.get('sign')!r}")
    if not sh.get("end_kicker"):
        out.append("no end_kicker")
    if len(sh.get("beats", [])) != 3:
        out.append(f"{len(sh.get('beats', []))} beats, not 3")
    for k in ("kicker", "title", "onset", "beats", "end"):
        if not sh.get(k):
            out.append(f"short.{k} missing")
    if sh.get("title", "").lower().startswith("here,"):
        out.append("title starts with 'Here,'")
    if len((sh.get("end") or "").split()) > 6:
        out.append(f"end line has {len(sh['end'].split())} words")
    for i, b in enumerate(sh.get("beats", []), 1):
        if len(b.get("text", "").split()) > 12:
            out.append(f"beat {i} has {len(b['text'].split())} words")
    try:
        Spec(**e["spec"])
        from dataclasses import replace
        base = Spec(**e["spec"])
        for part in [sh.get("spec") or {}, (sh.get("onset") or {}).get("spec") or {}, sh.get("end_spec") or {},
                     (sh.get("end_onset") or {}).get("spec") or {}] + \
                    [b.get("spec") or {} for b in sh.get("beats", [])] + \
                    [(b.get("onset") or {}).get("spec") or {} for b in sh.get("beats", [])]:
            replace(base, **part)
    except Exception as err:
        out.append(f"spec: {type(err).__name__}: {err}")
    if e.get("name") in used_names:
        out.append(f"name {e['name']} already used")
    if e.get("id") in used_ids:
        out.append(f"id {e['id']} already used")
    return out


def is_name_planet(e):
    return str(e.get("kicker", "")).startswith("Every ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--release", nargs="+", metavar="ID")
    ap.add_argument("--slot", type=int, choices=SLOTS)
    ap.add_argument("--from", dest="start")
    ap.add_argument("--post-by", nargs="*", default=[], metavar="ID=DATE")
    a = ap.parse_args()
    schedule = json.loads((CONTENT / "schedule.json").read_text())

    if a.release:
        for r in schedule:
            if r["kind"] == "reel" and r["entry"] in a.release and r.get("hold"):
                r.pop("hold")
                r["note"] = "short cut, checked"
                print(f"released {r['entry']} ({r['not_before']})")
        (CONTENT / "schedule.json").write_text(json.dumps(schedule, indent=1, ensure_ascii=False) + "\n")
        return

    batch = []
    for f in a.files:
        data = json.loads(Path(f).read_text())
        batch += data if isinstance(data, list) else [data]
    batch.sort(key=lambda e: e["id"])
    existing = [e for f in FILES for e in load(f)]
    used_names = {e["name"] for e in existing}
    used_ids = {e["id"] for e in existing}
    bad = 0
    seen = set()
    for e in batch:
        p = problems(e, used_names, used_ids)
        if e["name"] in seen:
            p.append("name repeated within the batch")
        seen.add(e["name"])
        kind = "name" if is_name_planet(e) else "place"
        print(f"{e['id']} {e['name']:10} {kind:5} " + ("ok" if not p else "; ".join(p)))
        bad += bool(p)
    if bad:
        print(f"{bad} entries with problems: nothing written")
        return
    if not a.apply:
        print("all ok (add --apply to write)")
        return

    names, launch = load("names.json"), load("launch.json")
    for e in batch:
        (names if is_name_planet(e) else launch).append(e)
    (CONTENT / "names.json").write_text(json.dumps(names, indent=2, ensure_ascii=False) + "\n")
    (CONTENT / "launch.json").write_text(json.dumps(launch, indent=2, ensure_ascii=False) + "\n")

    iso = lambda r: datetime.fromisoformat(r["not_before"].replace("Z", "+00:00"))
    z = lambda t: t.strftime("%Y-%m-%dT%H:%M:%SZ")
    post_by = dict(x.split("=", 1) for x in a.post_by)
    new_rows = [{"day": 8, "entry": e["id"], "kind": "reel", "not_before": "", "hold": True,
                 "note": "short cut, held until rendered and checked"} for e in batch]
    for r in new_rows:
        if r["entry"] in post_by:
            r["post_by"] = post_by[r["entry"]]
    if a.slot:
        start = datetime.fromisoformat(a.start + "T00:00:00+00:00")
        done = {(x["entry"], x["kind"]) for x in json.loads((CONTENT / "published.json").read_text())}
        moving = sorted([r for r in schedule if r["kind"] == "reel" and r.get("not_before") and not r.get("hold")
                         and not r.get("fixed_date") and not r.get("after") and (r["entry"], r["kind"]) not in done
                         and iso(r) >= start], key=iso)
        pinned = {r["not_before"] for r in schedule if r["kind"] == "reel" and (r["entry"], r["kind"]) not in done
                  and (r.get("fixed_date") or r.get("after")) and r.get("not_before") and iso(r) >= start}
        fresh, old = list(new_rows), list(moving)
        t = start.replace(hour=SLOTS[0])
        while fresh or old:
            if z(t) not in pinned:
                pick = fresh if (t.hour == a.slot and fresh) or not old else old
                pick.pop(0)["not_before"] = z(t)
            h = next((s_ for s_ in SLOTS if s_ > t.hour), None)
            t = t.replace(hour=h) if h else (t + timedelta(days=1)).replace(hour=SLOTS[0])
        for r in moving:
            r["note"] = (r.get("note", "") + f"; moved later on {datetime.now():%d %b} for batch 8").lstrip("; ")
    else:
        t = max(iso(r) for r in schedule if r["kind"] == "reel" and r.get("not_before") and not r.get("fixed_date"))
        for r in new_rows:
            h = next((s_ for s_ in SLOTS if s_ > t.hour), None)
            t = (t.replace(hour=h) if h else (t + timedelta(days=1)).replace(hour=SLOTS[0])).replace(minute=0, second=0)
            r["not_before"] = z(t)
    schedule.extend(new_rows)
    names_by_id = {e["id"]: e["name"] for e in batch}
    for r in new_rows:
        print(f"queued {r['entry']} {names_by_id[r['entry']]} at {r['not_before']} (held)" + (f", post by {r['post_by']}" if r.get("post_by") else ""))
    (CONTENT / "schedule.json").write_text(json.dumps(schedule, indent=1, ensure_ascii=False) + "\n")
    print("written: content/names.json, content/launch.json, content/schedule.json")


if __name__ == "__main__":
    main()
