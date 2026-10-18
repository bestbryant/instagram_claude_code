"""Atlas of Elsewhere: content engine CLI.

  python -m atlas launch [--only 000,001] [--no-reels] [--jobs 4] [--file content/halloween.json]
  python -m atlas planet "Biscuit" [--by @someone] [--no-reel]
  python -m atlas grid
  python -m atlas avatar
  python -m atlas process 001              # "how it's made" Reel
  python -m atlas publish output/launch/001-veyra --kind reel --base-url https://… [--dry-run]
  python -m atlas next --base-url https://… [--dry-run]
  python -m atlas inbox [--chart]          # name requests from comments
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image

from . import captions, text
from .render import Spec, build, frame, ink_palette, printed, render_raw, seed_from, to_image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
LAUNCH = ROOT / "content" / "launch.json"
SCHEDULE = ROOT / "content" / "schedule.json"
LOG = ROOT / "content" / "published.json"


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "planet"


def _resize(img: np.ndarray, size) -> np.ndarray:
    return np.asarray(to_image(img).resize(size, Image.LANCZOS), np.float32) / 255


def detail_crop(raw: np.ndarray, size=text.DETAIL, zoom=1.5) -> np.ndarray:
    """The busiest window of the image (silhouettes, figures, lights) for the close-up."""
    H, W = raw.shape[:2]
    cw = int(W / zoom)
    ch = int(cw * size[1] / size[0])
    g = raw[::4, ::4].mean(2)
    edges = np.abs(np.diff(g, axis=0))[:, :-1] + np.abs(np.diff(g, axis=1))[:-1]
    best, pos = -1.0, (0, 0)
    for y0 in np.linspace(int(H * 0.15), H - ch, 8).astype(int):
        for x0 in np.linspace(0, W - cw, 7).astype(int):
            score = edges[y0 // 4:(y0 + ch) // 4, x0 // 4:(x0 + cw) // 4].sum()
            if score > best:
                best, pos = score, (y0, x0)
    y0, x0 = pos
    return _resize(raw[y0:y0 + ch, x0:x0 + cw], size)


def make(entry: dict, spec: Spec, seed: int, folder: Path, reel=True, by=None) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    W, H = text.ART
    raw = render_raw(spec, seed, int(W * 1.5), int(H * 1.5))
    art = _resize(raw, text.ART)
    inks = ink_palette(art)
    text.cover(printed(art, inks, seed & 0xFFFF), entry, seed & 0xFFFF).save(folder / "1-cover.jpg", quality=93, subsampling=0)
    detail = printed(detail_crop(raw), inks, (seed >> 16) & 0xFFFF)
    text.notes(detail, entry, seed & 0xFFFF).save(folder / "2-notes.jpg", quality=93, subsampling=0)
    (folder / "caption-carousel.txt").write_text(captions.carousel(entry, by) + "\n")
    (folder / "caption-reel.txt").write_text(captions.reel(entry, by) + "\n")
    (folder / "alt-text.txt").write_text(captions.alt_text(entry, spec) + "\n")
    (folder / "entry.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False) + "\n")
    if reel:
        from .reel import render_reel
        render_reel(spec, seed, entry, folder / "reel.mp4", cover_path=folder / "reel-cover.jpg")
    return folder


def _launch_one(args):
    entry, reel, dest = args
    folder = OUT / dest / f"{entry['id']}-{slug(entry['name'])}"
    make(entry, Spec(**entry["spec"]), seed_from(entry["name"]), folder, reel=reel)
    return f"{entry['id']} {entry['name']} -> {folder.relative_to(ROOT)}"


def cmd_launch(a):
    src = Path(a.file) if a.file else LAUNCH
    dest = a.dest or ("launch" if src.resolve() == LAUNCH else src.stem)
    entries = json.loads(src.read_text())
    if a.only:
        keep = set(a.only.split(","))
        entries = [e for e in entries if e["id"] in keep]
    jobs = [(e, not a.no_reels, dest) for e in entries]
    if a.jobs > 1:
        with ProcessPoolExecutor(a.jobs) as pool:
            for line in pool.map(_launch_one, jobs):
                print(line, flush=True)
    else:
        for j in jobs:
            print(_launch_one(j), flush=True)


def cmd_planet(a):
    from .lore import chart
    entry, spec, seed = chart(a.name, a.number)
    folder = make(entry, spec, seed, OUT / "requests" / slug(a.name), reel=not a.no_reel, by=a.by)
    print(f"{entry['name']}: {entry['subtitle']} -> {folder.relative_to(ROOT)}")


def cmd_grid(a):
    """Preview of the profile grid (newest first, 3:4 tiles like the app)."""
    covers = sorted((OUT / "launch").glob("*/1-cover.jpg"), reverse=True)
    if not covers:
        sys.exit("render the launch batch first: python -m atlas launch")
    tw, th, gap = 360, 480, 4
    rows = (len(covers) + 2) // 3
    sheet = Image.new("RGB", (3 * tw + 2 * gap, rows * th + (rows - 1) * gap), (255, 255, 255))
    for i, p in enumerate(covers):
        im = Image.open(p)
        w = int(im.height * 3 / 4)
        im = im.crop(((im.width - w) // 2, 0, (im.width + w) // 2, im.height)).resize((tw, th), Image.LANCZOS)
        sheet.paste(im, ((i % 3) * (tw + gap), (i // 3) * (th + gap)))
    dest = OUT / "grid-preview.jpg"
    sheet.save(dest, quality=90)
    print(dest.relative_to(ROOT))


def cmd_process(a):
    """'How it's made' Reel for a launch entry id (e.g. 001, H02) or any name."""
    from .reel import render_process
    entries = {e["id"]: e for f in (LAUNCH, ROOT / "content" / "halloween.json") for e in json.loads(f.read_text())}
    if a.target in entries:
        entry = entries[a.target]
        spec, seed = Spec(**entry["spec"]), seed_from(entry["name"])
    else:
        from .lore import chart
        entry, spec, seed = chart(a.target)
    dest = OUT / "process" / f"{entry['id']}-{slug(entry['name'])}.mp4"
    render_process(spec, seed, entry, dest)
    caption = (f"How {entry['name']} was made: sky first, then each ridge from the farthest to the nearest, "
               f"then the inks. Every print in the atlas is drawn this way, in code, one layer at a time.\n\n"
               f"{text.CTA}\n\n#illustration #processvideo #worldbuilding")
    dest.with_suffix(".txt").write_text(caption + "\n")
    print(dest.relative_to(ROOT))


def cmd_avatar(a):
    """Profile picture: a ringed planet that still reads at 110 px."""
    spec = Spec(palette="lilac_dusk", horizon=1.6, layers=1, giant=True, ring=True, giant_size=0.23,
                giant_x=0.5, giant_y=0.5, suns=0, moons=0, mist=0.0, stars=0.8)
    seed = seed_from(a.seed)
    img = printed(frame(build(spec, seed, 1080, 1080), grain=0))
    dest = OUT / "profile-picture.jpg"
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, quality=94)
    print(dest.relative_to(ROOT))


def _publish(folder: Path, kind: str, base_url: str, dry_run: bool):
    from .publish import Publisher
    folder = folder.resolve()
    rel = folder.relative_to(OUT).as_posix()
    url = lambda f: f"{base_url.rstrip('/')}/{rel}/{f}"
    p = Publisher(dry_run=dry_run)
    if kind == "carousel":
        cap = (folder / "caption-carousel.txt").read_text().strip()
        return p.carousel([url("1-cover.jpg"), url("2-notes.jpg")], cap)
    cap = (folder / "caption-reel.txt").read_text().strip()
    return p.reel_file(folder / "reel.mp4", cap, cover_url=url("reel-cover.jpg"))


def cmd_publish(a):
    print("published media id:", _publish(Path(a.folder), a.kind, a.base_url, a.dry_run))


REQUESTS = ROOT / "content" / "requests.json"
URL_RE = re.compile(r"https?://|www\.", re.I)
LEAD_RE = re.compile(r"^(please|pls|plz|can you|could you|do|chart|map|make|planet|my name is|name|for|try|"
                     r"my (dog|cat|pet|puppy|kitten|bird|bunny|hamster|horse|grandma|grandpa|nan|mom|mum|dad|"
                     r"sister|brother|friend|son|daughter|baby|girlfriend|boyfriend|wife|husband)('?s name is)?)"
                     r"\b[:,]?\s*", re.I)


def request_name(comment: str) -> str | None:
    """Pull a planet name out of a comment, or None if it isn't a request."""
    import unicodedata
    if URL_RE.search(comment):
        return None
    t = re.sub(r"@[\w.]+", " ", comment)
    t = "".join(c for c in t if unicodedata.category(c)[0] in "LNPZ")
    t = " ".join(t.split())
    while LEAD_RE.match(t):
        t = LEAD_RE.sub("", t, count=1)
    t = t.strip(" .!?:;,\"'“”")
    words = t.split()
    if not 1 <= len(words) <= 3 or len(t) > 24 or not any(c.isalpha() for c in t):
        return None
    if len(words) > 1 and not any(w[0].isupper() for w in words):
        return None
    if t.lower() in {"wow", "nice", "love", "love it", "amazing", "beautiful", "cool", "omg", "yes", "no", "me", "first"}:
        return None
    return t


def cmd_inbox(a):
    """Collect name requests from recent comments into content/requests.json."""
    from .publish import Publisher
    p = Publisher(dry_run=a.dry_run)
    queue = json.loads(REQUESTS.read_text()) if REQUESTS.exists() else []
    seen = {q["comment_id"] for q in queue}
    me = "" if a.dry_run else p.username()
    new = []
    for media in ([] if a.dry_run else p.recent_media(a.limit)):
        for c in p.recent_comments(media["id"]):
            if c["id"] in seen or c.get("username") == me:
                continue
            name = request_name(c.get("text", ""))
            if name:
                new.append({"comment_id": c["id"], "media_id": media["id"], "by": "@" + c.get("username", ""),
                            "name": name, "text": c.get("text", ""), "status": "new"})
    queue += new
    if not a.dry_run:
        REQUESTS.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(new)} new request(s); {sum(q['status'] == 'new' for q in queue)} waiting")
    for q in queue:
        if q["status"] == "new":
            print(f"  {q['by']:<22} {q['name']:<24} ← “{q['text'][:50]}”")
    if a.chart:
        from .lore import chart
        for q in queue:
            if q["status"] != "new":
                continue
            entry, spec, seed = chart(q["name"])
            folder = make(entry, spec, seed, OUT / "requests" / slug(q["name"]), reel=not a.no_reel, by=q["by"])
            q["status"], q["folder"] = "charted", str(folder.relative_to(ROOT))
            print(f"charted {q['name']} -> {q['folder']}")
        if not a.dry_run:
            REQUESTS.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n")


def cmd_next(a):
    schedule = json.loads(SCHEDULE.read_text())
    log = json.loads(LOG.read_text()) if LOG.exists() else []
    done = {(x["entry"], x["kind"]) for x in log}
    todo = [s for s in schedule if (s["entry"], s["kind"]) not in done]
    if not todo:
        print("schedule complete; chart some requested planets next")
        return
    item = todo[0]
    folder = next((OUT / "launch").glob(f"{item['entry']}-*"), None)
    if folder is None:
        sys.exit(f"missing output for {item['entry']}; run: python -m atlas launch --only {item['entry']}")
    media = _publish(folder, item["kind"], a.base_url, a.dry_run)
    print(f"posted {item['entry']} as {item['kind']}: {media}")
    if not a.dry_run:
        from datetime import datetime, timezone
        log.append({**item, "media_id": media, "at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        LOG.write_text(json.dumps(log, indent=2) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="atlas", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("launch", help="render the launch batch")
    s.add_argument("--only")
    s.add_argument("--no-reels", action="store_true")
    s.add_argument("--jobs", type=int, default=1)
    s.add_argument("--file", help="another entries file, e.g. content/halloween.json")
    s.add_argument("--dest", help="folder under output/ (default: launch, or the file's name)")
    s.set_defaults(fn=cmd_launch)
    s = sub.add_parser("planet", help="chart the planet for any name (comment requests)")
    s.add_argument("name")
    s.add_argument("--by", help="who asked, e.g. @handle")
    s.add_argument("--number")
    s.add_argument("--no-reel", action="store_true")
    s.set_defaults(fn=cmd_planet)
    s = sub.add_parser("grid", help="preview the profile grid")
    s.set_defaults(fn=cmd_grid)
    s = sub.add_parser("process", help="'how it's made' Reel for an entry id or a name")
    s.add_argument("target")
    s.set_defaults(fn=cmd_process)
    s = sub.add_parser("avatar", help="render the profile picture")
    s.add_argument("--seed", default="Atlas of Elsewhere")
    s.set_defaults(fn=cmd_avatar)
    s = sub.add_parser("publish", help="publish one folder via the Graph API")
    s.add_argument("folder")
    s.add_argument("--kind", choices=["carousel", "reel"], required=True)
    s.add_argument("--base-url", required=True, help="public URL that serves the output/ directory")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_publish)
    s = sub.add_parser("next", help="publish the next item in content/schedule.json")
    s.add_argument("--base-url", required=True)
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_next)
    s = sub.add_parser("inbox", help="collect name requests from recent comments (Graph API)")
    s.add_argument("--limit", type=int, default=10, help="how many recent posts to scan")
    s.add_argument("--chart", action="store_true", help="also render planets for new requests")
    s.add_argument("--no-reel", action="store_true")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_inbox)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
