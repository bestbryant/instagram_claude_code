"""Atlas of Elsewhere: content engine CLI.

  python -m atlas launch [--only 000,001] [--no-reels] [--jobs 4] [--file content/halloween.json]
  python -m atlas planet "Biscuit" [--by @someone] [--no-reel]
  python -m atlas grid
  python -m atlas avatar
  python -m atlas process 001              # "how it's made" Reel
  python -m atlas tapstop                  # "Tap to stop. That's where you're moving."
  python -m atlas publish output/launch/001-veyra --kind reel --base-url https://… [--dry-run]
  python -m atlas prepare --days 1         # render what is due today and tomorrow
  python -m atlas next --base-url https://… [--dry-run]
  python -m atlas inbox [--chart]          # name requests from comments
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image

from . import captions, text
from .render import Spec, build, frame, ink_palette, printed, seed_from, spec_inks, to_image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
LAUNCH = ROOT / "content" / "launch.json"
SCHEDULE = ROOT / "content" / "schedule.json"
LOG = ROOT / "content" / "published.json"
STATS = ROOT / "content" / "stats.json"
ENGINE = 5   # bump when a change to the Reel renderer should re-render every unposted Reel
GITHUB_REPO = os.environ.get("ATLAS_GITHUB_REPO", "bestbryant/instagram_claude_code")   # public repo that serves the videos


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "planet"


def _resize(img: np.ndarray, size) -> np.ndarray:
    return np.asarray(to_image(img).resize(size, Image.LANCZOS), np.float32) / 255


def focus_crop(raw: np.ndarray, focus, size, zoom=2.0) -> np.ndarray:
    """A close-up window centred on the gag."""
    H, W = raw.shape[:2]
    cw = int(W / zoom)
    ch = min(int(cw * size[1] / size[0]), H)
    x0 = int(np.clip(focus[0] * W - cw / 2, 0, W - cw))
    y0 = int(np.clip(focus[1] * H - ch * 0.55, 0, H - ch))
    return _resize(raw[y0:y0 + ch, x0:x0 + cw], size)


SLIDES = ("1-cover.jpg", "2-detail.jpg", "3-punch.jpg", "4-page.jpg", "5-invite.jpg")


def make(entry: dict, spec: Spec, seed: int, folder: Path, reel=True, by=None, requested_by=None) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    for old in ("2-notes.jpg", "3-page.jpg", "4-guide.jpg"):
        (folder / old).unlink(missing_ok=True)
    W, H = text.ART
    scene = build(spec, seed, int(W * 1.5), int(H * 1.5))
    raw = frame(scene, grain=0)
    inks = ink_palette(_resize(raw, text.ART), extra=spec_inks(spec))
    s16 = seed & 0xFFFF
    # slide 1 leans in on the joke; slide 2 (where Instagram re-serves carousels) goes closer still
    framing = entry.get("framing", {})
    art = focus_crop(raw, scene.focus, text.ART, framing.get("cover", 1.3)) if framing.get("cover", 1.3) > 1 else _resize(raw, text.ART)
    art_img = printed(art, inks, s16)
    zoom = framing.get("detail", 1.9 if "sign" in scene.marks and spec.gag else 2.4)
    close = printed(focus_crop(raw, scene.focus, (text.PAGE[0] - 2 * text.MARGIN, 1010), zoom), inks, (seed >> 16) & 0xFFFF)
    slides = [text.cover(art_img, entry, s16), text.detail(close, entry, s16), text.punch(entry, s16),
              text.page(entry, s16), text.invite(close, entry, s16)]
    for name, img in zip(SLIDES, slides):
        img.save(folder / name, quality=93, subsampling=0)
    (folder / "caption-carousel.txt").write_text(captions.carousel(entry, by) + "\n")
    (folder / "caption-reel.txt").write_text(captions.reel(entry, by) + "\n")
    (folder / "alt-text.txt").write_text(captions.alt_text(entry, spec) + "\n")
    (folder / "entry.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False) + "\n")
    if reel:
        from .reel import render_reel
        render_reel(spec, seed, entry, folder / "reel.mp4", cover_path=folder / "reel-cover.jpg", requested_by=requested_by)
        (folder / "reel-entry.json").write_text(json.dumps({**entry, "_engine": ENGINE}, indent=2, ensure_ascii=False) + "\n")
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


NUMBERS = ROOT / "content" / "numbers.json"


def next_number() -> str:
    """Requested planets get real atlas numbers, starting at 101."""
    state = json.loads(NUMBERS.read_text()) if NUMBERS.exists() else {"next": 101}
    n = state["next"]
    NUMBERS.write_text(json.dumps({"next": n + 1}) + "\n")
    return f"{n:03d}"


def cmd_planet(a):
    from .lore import chart
    entry, spec, seed = chart(a.name, a.number or (next_number() if a.by else None), by=a.by)
    if a.by:
        entry["discovered_by"] = a.by
    folder = make(entry, spec, seed, OUT / "requests" / f"{entry['id']}-{slug(entry['name'])}", reel=not a.no_reel, by=a.by, requested_by=a.by)
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
    caption = (f"How {entry['name']} gets made: the sky first, then each ridge from the farthest to the nearest, "
               f"then the people, then the inks, like a screen print. Every layer is drawn in code.\n\n"
               f"Leave a name in the comments and I'll draw its planet next.\n\n#illustration #creativecoding #worldbuilding")
    dest.with_suffix(".txt").write_text(caption + "\n")
    print(dest.relative_to(ROOT))


def cmd_tapstop(a):
    """'Tap to stop' Reel: every planet flashes by; wherever you pause is where you're moving."""
    from .video import H as VH, W as VW, Shot, overlay, render_shots
    from .render import print_finish
    entries = [e for f in (LAUNCH, ROOT / "content" / "halloween.json") for e in json.loads(f.read_text())]
    stills = []
    for e in entries:
        spec, seed = Spec(**e["spec"]), seed_from(e["name"])
        img = frame(build(spec, seed, VW, VH), grain=0)
        stills.append((e, print_finish(img, ink_palette(img, extra=spec_inks(spec)), seed & 0xFFFF)))
        print("drew", e["name"], flush=True)
    top = overlay([dict(text="Tap to stop.", y=0.2, kind="serif", weight="Medium", size=92),
                   dict(text="That's where you're moving.", y=0.255, kind="italic", size=62)], scrim=0.3)
    shots = []
    order = stills + stills[::-1][1:-1]     # there and back, so the loop has no jump
    for e, img in order:
        label = overlay([dict(text=e["name"], y=0.6, kind="serif", weight="Medium", size=130),
                         dict(text=e["subtitle"], y=0.675, kind="italic", size=48)], scrim=0.25)
        shots.append(Shot(a.beat, still=img, cards=[(label, 0, a.beat, 0, 0)], tick=True))
    dest = OUT / "specials" / "tap-to-stop.mp4"
    render_shots(shots, dest, seed=7, overlays=[(top, 0, sum(x.seconds for x in shots), 0, 0)])
    dest.with_suffix(".txt").write_text(
        "Tap to stop. Wherever it lands is where you're moving.\n\n"
        "Tell me where you ended up, and what you'll miss about home.\n\n#worldbuilding #illustration #imaginaryworlds\n")
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
    rel = (folder.parent if kind in ("process", "special") else folder).relative_to(OUT).as_posix()
    url = lambda f: f"{base_url.rstrip('/')}/{rel}/{f}"
    p = Publisher(dry_run=dry_run)
    if kind in ("process", "special"):
        video = folder
        return p.reel(_video_url(video, dry_run), video.with_suffix(".txt").read_text().strip(),
                      audio_name=f"Atlas of Elsewhere · {video.stem.split('-', 1)[-1].replace('-', ' ').title()} (process)")
    if kind == "carousel":
        cap = (folder / "caption-carousel.txt").read_text().strip()
        slides = sorted((f.name for f in folder.glob("[0-9]*-*.jpg")), key=lambda n: int(n.split("-")[0]))
        return p.carousel([url(f) for f in slides], cap)
    cap = (folder / "caption-reel.txt").read_text().strip()
    entry = json.loads((folder / "reel-entry.json").read_text()) if (folder / "reel-entry.json").exists() else {}
    name = entry.get("name", "")
    media = p.reel(_video_url(folder / "reel.mp4", dry_run), cap, cover_url=url("reel-cover.jpg"),
                   audio_name=f"Atlas of Elsewhere · {name}" if name else None)
    epilogue = content_entries().get(entry.get("id"), {}).get("first_comment")
    if epilogue and not dry_run:
        # the planet's one-line epilogue, as the first comment (the owner can pin it from the app)
        try:
            p.comment(media, epilogue)
        except Exception as err:   # the Reel is up either way
            print("epilogue comment failed:", err)
    return media


def _video_url(path: Path, dry_run: bool = False) -> str:
    """A public URL for a pushed video. The Instagram-login API needs video_url (no
    resumable upload), and raw.githubusercontent serves octet-stream, so this uses
    jsDelivr at the exact commit, which serves video/mp4 and never goes stale."""
    import subprocess
    import urllib.request
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    rel = path.resolve().relative_to(ROOT).as_posix()
    u = f"https://cdn.jsdelivr.net/gh/{GITHUB_REPO}@{sha}/{rel}"
    if dry_run:
        return u
    with urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=60) as r:
        size = int(r.headers.get("Content-Length", 0))
        if size != path.stat().st_size or "video" not in r.headers.get("Content-Type", ""):
            raise RuntimeError(f"{u} serves {size} bytes of {r.headers.get('Content-Type')}; push the commit first")
    return u


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
    t = re.sub(r"[\s,]+(please|pls|plz|thanks|thank you|thx|ty)$", "", t, flags=re.I).strip(" .!?:;,\"'“”")
    words = t.split()
    if not 1 <= len(words) <= 3 or len(t) > 24 or not any(c.isalpha() for c in t):
        return None
    if len(words) > 1 and not any(w[0].isupper() for w in words):
        return None
    if t.lower() in {"wow", "nice", "love", "love it", "amazing", "beautiful", "cool", "omg", "yes", "no", "me", "first"}:
        return None
    return t


SENSITIVE = re.compile(r"\b(passed|rip|r\.i\.p|rest in peace|rainbow bridge|in memory|memorial|died|dying|put down|"
                       r"lost (him|her|them|my)|miss(ing)? (him|her|them|you)|gone too soon|funeral|late (mum|mom|dad|"
                       r"husband|wife|son|daughter|brother|sister|grandma|grandpa|nan)|grave|angel|cancer|hospice|"
                       r"miscarriage|stillborn|loss|grief|grieving)\b", re.I)
TITLES = {"grandma", "grandpa", "granny", "nan", "nana", "nanna", "aunt", "auntie", "uncle", "mr", "mrs", "ms",
          "dr", "captain", "sir", "lady", "baby", "little", "big", "old"}


def first_name_only(name: str) -> str:
    """'Emma Johnson' -> 'Emma': no private surnames on public posts. Keeps 'Grandma Rose'."""
    words = name.split()
    if len(words) >= 2 and all(w[:1].isupper() for w in words) and words[0].lower() not in TITLES:
        return words[0]
    return name


def queue_request(entry_id: str, by: str, now=None) -> str:
    """Give a requested planet's Reel the next daily 18:00 UTC slot at least 6 h away (time to render and check it).
    The short Reels from that slot on move back a day each; fixed nights (Halloween at 22:00) keep their dates.
    The row is held until the Reel has been checked (scratchpad/room/add_shorts.py --release ID)."""
    from datetime import datetime, time, timedelta, timezone
    now = now or datetime.now(timezone.utc)
    sched = json.loads(SCHEDULE.read_text())
    posted = {(x["entry"], x["kind"]) for x in (json.loads(LOG.read_text()) if LOG.exists() else [])}
    when = lambda r: datetime.fromisoformat(r["not_before"].replace("Z", "+00:00"))
    live = [r for r in sched if r.get("not_before") and r["kind"] == "reel" and not r.get("hold") and (r["entry"], r["kind"]) not in posted]
    fixed = {when(r).date() for r in live if when(r).hour != 18}
    day = (now + timedelta(hours=6)).date()
    if datetime.combine(day, time(18), timezone.utc) < now + timedelta(hours=6):
        day += timedelta(days=1)
    while day in fixed:
        day += timedelta(days=1)
    slot = datetime.combine(day, time(18), timezone.utc)
    later = sorted((r for r in live if when(r).hour == 18 and when(r) >= slot), key=when)
    d = day
    for r in later:
        d += timedelta(days=1)
        while d in fixed:
            d += timedelta(days=1)
        r["not_before"] = f"{d.isoformat()}T18:00:00Z"
    row = {"day": later[0]["day"] if later else 1, "entry": entry_id, "kind": "reel", "hold": True,
           "note": f"request from {by}: held until rendered and checked", "not_before": f"{day.isoformat()}T18:00:00Z"}
    at = sched.index(later[0]) if later else len(sched)
    sched.insert(at, row)
    SCHEDULE.write_text(json.dumps(sched, indent=1, ensure_ascii=False) + "\n")
    return row["not_before"]


def cmd_inbox(a):
    """Collect name requests from recent comments into content/requests.json."""
    from .publish import Publisher
    p = Publisher(dry_run=a.dry_run)
    queue = json.loads(REQUESTS.read_text()) if REQUESTS.exists() else []
    seen = {q["comment_id"] for q in queue}
    me = "" if a.dry_run else p.username()
    new = []
    for media in ([] if a.dry_run else p.recent_media(a.limit)):
        # a story episode's caption ends on a question, so a short comment there may be an answer
        # ("Mum", "Umbrella") rather than a name: those wait for a person to read them
        asks = any(line.strip().endswith("?") for line in (media.get("caption") or "").split("\n"))
        for c in p.recent_comments(media["id"]):
            if c["id"] in seen or c.get("username") == me:
                continue
            text_ = c.get("text", "")
            name = request_name(text_)
            if name:
                status = "needs_owner" if SENSITIVE.search(text_) else ("check" if asks and not LEAD_RE.match(text_.strip()) else "new")
                new.append({"comment_id": c["id"], "media_id": media["id"], "by": "@" + c.get("username", ""),
                            "name": first_name_only(name), "text": text_, "status": status})
    queue += new
    if not a.dry_run:
        REQUESTS.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(new)} new request(s); {sum(q['status'] == 'new' for q in queue)} waiting; "
          f"{sum(q['status'] == 'check' for q in queue)} to check (maybe an answer to the caption's question); "
          f"{sum(q['status'] == 'needs_owner' for q in queue)} held for the owner (sensitive)")
    for q in queue:
        if q["status"] in ("new", "check"):
            print(f"  [{q['status']}] {q['by']:<22} {q['name']:<24} ← “{q['text'][:60]}”")
    if a.chart:
        from .lore import chart
        for q in queue:
            if q["status"] != "new":
                continue
            entry, spec, seed = chart(q["name"], next_number(), by=q["by"])
            entry["discovered_by"] = q["by"]
            folder = make(entry, spec, seed, OUT / "requests" / f"{entry['id']}-{slug(entry['name'])}", reel=not a.no_reel, by=q["by"], requested_by=q["by"])
            q["status"], q["folder"], q["entry"] = "charted", str(folder.relative_to(ROOT)), entry["id"]
            charted = json.loads(CHARTED.read_text()) if CHARTED.exists() else []
            CHARTED.write_text(json.dumps(charted + [entry], indent=2, ensure_ascii=False) + "\n")
            slot = queue_request(entry["id"], q["by"])
            print(f"charted {q['name']} -> {q['folder']}; queued (held until checked) for {slot}")
        if not a.dry_run:
            REQUESTS.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n")


LAUNCH_DAY = "2026-10-18"   # schedule day 1


def _find(item):
    if item["kind"] == "process":
        return next((OUT / "process").glob(f"{item['entry']}-*.mp4"), None)
    if item["kind"] == "special":
        hit = OUT / "specials" / f"{item['entry']}.mp4"
        return hit if hit.exists() else None
    for group in ("launch", "halloween", "sequels", "names", "requests"):
        hit = next((OUT / group).glob(f"{item['entry']}-*"), None)
        if hit:
            return hit
    return None


CONTENT_FILES = ("launch.json", "halloween.json", "sequels.json", "names.json", "charted.json")
CHARTED = ROOT / "content" / "charted.json"     # planets charted for comment requests


def content_entries() -> dict:
    out = {}
    for f in CONTENT_FILES:
        path = ROOT / "content" / f
        if path.exists():
            out.update({e["id"]: e for e in json.loads(path.read_text())})
    return out


def video_ok(path: Path) -> bool:
    import subprocess
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                           capture_output=True, text=True, timeout=60)
        return r.returncode == 0 and float(r.stdout.strip() or 0) > 3.0
    except (ValueError, subprocess.SubprocessError):
        return False


def file_hash(path: Path) -> str:
    import hashlib
    return hashlib.sha1(Path(path).read_bytes()).hexdigest()


def preflight(path: Path) -> str | None:
    """What would stop Instagram recommending this Reel: not full-frame 9:16, silent, or a re-upload."""
    import subprocess
    if not video_ok(path):
        return "video missing or broken"
    if path.stat().st_size >= 19.5e6:
        return "over jsDelivr's 20 MB file limit (re-encode at a lower bitrate)"
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True, timeout=60)
    if r.stdout.strip() != "1080,1920":
        return f"not 1080x1920 ({r.stdout.strip()})"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-map", "0:a:0", "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True, timeout=120)
    m = re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr)
    if not m or float(m.group(1)) < -45:
        return "no audible audio (Reels without sound are shown less)"
    log = json.loads(LOG.read_text()) if LOG.exists() else []
    if file_hash(path) in {x.get("sha1") for x in log}:
        return "this exact file was already posted (re-uploads aren't recommended)"
    return None


def check_item(item, folder, entries) -> str | None:
    """Why an item can't be posted yet, or None if it's ready."""
    if folder is None:
        return "not rendered"
    if item["kind"] in ("process", "special"):
        return preflight(folder)
    src = entries.get(item["entry"])
    rendered = folder / ("reel-entry.json" if item["kind"] == "reel" else "entry.json")
    # fields only the other format uses don't make this one stale
    skip = ({"framing", "odd_line", "rule", "subtitle", "facts", "_engine"} if item["kind"] == "reel" else {"camera", "text_y", "opener", "kicker", "cta", "episode"}) | {"first_comment"}
    if item["kind"] == "reel" and rendered.exists() and json.loads(rendered.read_text()).get("_engine") != ENGINE:
        return "stale: rendered with an older Reel engine"
    if item["kind"] == "reel" and src is not None and not src.get("episode") and not src.get("short"):
        return "waiting for its story episode"      # every Reel from here on is a story; older cuts stay unposted
    same = lambda a, b: {k: v for k, v in a.items() if k not in skip} == {k: v for k, v in b.items() if k not in skip}
    if src is not None and (not rendered.exists() or not same(json.loads(rendered.read_text()), src)):
        return "stale: content changed since it was rendered"
    if item["kind"] == "reel":
        problem = preflight(folder / "reel.mp4")
        if problem:
            return problem
        if not (folder / "reel-cover.jpg").exists():
            return "reel cover missing"
    elif not list(folder.glob("[0-9]*-*.jpg")):
        return "slides missing"
    return None


COMMENTS = ROOT / "content" / "comments.json"


def post_due_comments(now, dry_run=False):
    """Comments the account adds to its own posts later (a sequel's 'part two is up', an epilogue a few
    days on), once their time has come and the post they belong on is live. The owner pins them in the app."""
    if not COMMENTS.exists():
        return
    from .publish import Publisher
    from datetime import datetime
    todo = json.loads(COMMENTS.read_text())
    media = {x["entry"]: x["media_id"] for x in (json.loads(LOG.read_text()) if LOG.exists() else []) if x["kind"] == "reel"}
    changed = False
    for c in todo:
        if c.get("posted") or now < datetime.fromisoformat(c["post_at"].replace("Z", "+00:00")) or c["on"] not in media:
            continue
        if c.get("after") and c["after"] not in media:
            continue                                    # e.g. 'part two is up' waits for part two
        if dry_run:
            print(f"would comment on {c['on']}: {c['text'][:60]}")
            continue
        c["comment_id"] = Publisher().comment(media[c["on"]], c["text"])
        c["posted"], changed = True, True
        print(f"commented on {c['on']}" + (" -- PIN THIS in the app" if c.get("pin") else "") + f": {c['text'][:60]}")
    if changed:
        COMMENTS.write_text(json.dumps(todo, indent=2, ensure_ascii=False) + "\n")


def cmd_next(a):
    """Post every scheduled item that is due (day <= today), oldest first, at most --max per run.
    With --asap the days are ignored: post the next ready item in schedule order, once at least
    --gap-hours have passed since the last post. Items that aren't ready are skipped with a warning."""
    from datetime import date, datetime, timedelta, timezone
    schedule = json.loads(SCHEDULE.read_text())
    log = json.loads(LOG.read_text()) if LOG.exists() else []
    done = {(x["entry"], x["kind"]) for x in log}
    now = datetime.now(timezone.utc)
    today = (date.today() - date.fromisoformat(LAUNCH_DAY)).days + 1
    pause = ROOT / "content" / "PAUSED"
    if pause.exists():
        print("posting paused:", pause.read_text().strip())
        return
    post_due_comments(now, a.dry_run)
    if a.asap:
        last = max((datetime.fromisoformat(x["at"]) for x in log), default=None)
        if last and now - last < timedelta(hours=a.gap_hours):
            print(f"last post {last:%H:%M} UTC; next one allowed after {last + timedelta(hours=a.gap_hours):%H:%M} UTC")
            return
    due = [s for s in schedule if (s["entry"], s["kind"]) not in done and (a.asap or s.get("day", 0) <= today)]
    if not due:
        left = [s for s in schedule if (s["entry"], s["kind"]) not in done]
        print(f"day {today}: nothing due" + (f"; next is day {left[0]['day']}" if left else "; schedule complete"))
        return
    entries = content_entries()
    posted = 0
    for item in due:
        if posted >= a.max:
            break
        if item.get("hold"):
            continue                                    # parked (see its note)
        if item.get("not_before") and now < datetime.fromisoformat(item["not_before"].replace("Z", "+00:00")):
            continue                                    # held for its date (e.g. Halloween night)
        if item.get("after") and tuple(item["after"]) not in done:
            continue                                    # a sequel waits for the post it follows
        folder = _find(item)
        problem = check_item(item, folder, entries)
        if problem:
            print(f"SKIP {item['entry']} {item['kind']} (day {item['day']}): {problem}")
            continue
        media = _publish(folder, item["kind"], a.base_url, a.dry_run)
        posted += 1
        print(f"posted {item['entry']} as {item['kind']}: {media}")
        if not a.dry_run:
            video = folder if item["kind"] in ("process", "special") else folder / "reel.mp4"
            sha = {"sha1": file_hash(video)} if item["kind"] != "carousel" else {}
            fmt = {"format": reel_format(entries.get(item["entry"], {}))} if item["kind"] == "reel" else {}
            log.append({**item, "media_id": media, "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **sha, **fmt})
            LOG.write_text(json.dumps(log, indent=2) + "\n")
            done.add((item["entry"], item["kind"]))
    if posted:
        post_due_comments(datetime.now(timezone.utc), a.dry_run)   # a sequel's note on the part before it goes up with it


def cmd_stats(a):
    """Pull reach, views, watch time, likes, shares and saves for every post into content/stats.json."""
    from datetime import datetime, timezone
    from .publish import GraphError, Publisher
    p = Publisher()
    log = json.loads(LOG.read_text()) if LOG.exists() else []
    out = {}
    reel_metrics = ["reach", "views", "likes", "comments", "shares", "saved", "ig_reels_avg_watch_time", "reels_skip_rate"]
    feed_metrics = ["reach", "views", "likes", "comments", "shares", "saved"]
    now = datetime.now(timezone.utc)
    old = json.loads(STATS.read_text()).get("posts", {}) if STATS.exists() else {}
    value = lambda d: (d.get("values") or [{}])[0].get("value", (d.get("total_value") or {}).get("value"))
    history = []
    for x in log:
        age = (now - datetime.fromisoformat(x["at"])).total_seconds() / 3600
        if a.recent and age > a.recent:
            if x["media_id"] in old:
                out[x["media_id"]] = old[x["media_id"]]       # keep the last full pull for older posts
            continue
        wanted = feed_metrics if x["kind"] == "carousel" else reel_metrics
        vals = {}
        try:                                               # one call for all metrics (stays well inside the hourly call budget)
            vals = {d["name"]: value(d) for d in p._call("GET", f"{x['media_id']}/insights", metric=",".join(wanted)).get("data", [])}
        except GraphError as err:
            if "API on hold" in str(err) or "OAuthException" in str(err):
                raise
            for m in wanted:                               # an unsupported metric fails the whole call: fall back to one at a time
                try:
                    d = p._call("GET", f"{x['media_id']}/insights", metric=m).get("data", [])
                    if d:
                        vals[m] = value(d[0])
                except GraphError:
                    pass
        out[x["media_id"]] = {"entry": x["entry"], "kind": x["kind"], "at": x["at"], **vals}
        history.append({"t": now.isoformat(timespec="seconds"), "entry": x["entry"], "kind": x["kind"], "age_h": round(age, 1), **vals})
        r = vals.get("reach") or 0
        print(f"{x['at'][:16]} {x['entry']:>4} {x['kind']:<8} reach {r:>5}  views {vals.get('views', '-'):>5}  "
              f"likes {vals.get('likes', '-'):>3}  shares {vals.get('shares', '-'):>3}  saves {vals.get('saved', '-'):>3}  "
              f"watch {vals.get('ig_reels_avg_watch_time', '-')}  skip {vals.get('reels_skip_rate', '-')}")
    acct = p._call("GET", p.user_id, fields="followers_count,media_count")
    print(f"followers {acct.get('followers_count')}  posts {acct.get('media_count')}")
    with (ROOT / "content" / "stats_history.jsonl").open("a") as f:      # reach over time, for the posting-rate experiment
        for h in history:
            f.write(json.dumps(h) + "\n")
        f.write(json.dumps({"t": now.isoformat(timespec="seconds"), "followers": acct.get("followers_count"), "posts": acct.get("media_count")}) + "\n")
    STATS.write_text(json.dumps({"fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                 "followers": acct.get("followers_count"), "posts": out}, indent=1) + "\n")


def reel_format(entry: dict) -> str:
    """Which format test version a Reel is (docs/PLAN.md): short-A/B/C, long (34 s story) or postcard."""
    if entry.get("discovered_by"):
        return "request"                               # a requester's planet: warm viewers, kept out of the format test
    if entry.get("short"):
        return "short-" + entry["short"].get("version", "A")
    return "long" if entry.get("episode") else "postcard"


def cmd_score(a):
    """Stranger-only scoreboard from content/stats_history.jsonl, read at about 48 h (docs/PLAN.md).

    Our own plays come first (the owner, the bot's checks): the last snapshot before reach passes 3 is
    taken as that baseline and subtracted. Pass lines: skip 60% or less, strangers watch at least 40% of the
    Reel, at least 1 share or save per 100 strangers reached."""
    import statistics
    import subprocess
    log = json.loads(LOG.read_text()) if LOG.exists() else []
    hist = [json.loads(line) for line in (ROOT / "content" / "stats_history.jsonl").read_text().splitlines() if line.strip()]
    entries = content_entries()
    rows = []
    for x in log:
        if x["kind"] != "reel":
            continue
        snaps = sorted((h for h in hist if h.get("entry") == x["entry"] and h.get("kind") == "reel"), key=lambda h: h["age_h"])
        if not snaps:
            continue
        early = []                                            # our own plays: the snapshots before reach passes 3
        for h in snaps:
            if (h.get("reach") or 0) > 3:
                break
            early.append(h)
        base = early[-1] if early and early[-1] is not snaps[-1] else {}   # the last of them (nothing after it: no strangers yet)
        at48 = min(snaps, key=lambda h: abs(h["age_h"] - a.hours))
        g = lambda h, k: h.get(k) or 0
        reach = g(at48, "reach") - g(base, "reach")
        views = g(at48, "views") - g(base, "views")
        watch_total = g(at48, "ig_reels_avg_watch_time") * g(at48, "views") - g(base, "ig_reels_avg_watch_time") * g(base, "views")
        skips = g(at48, "reels_skip_rate") * g(at48, "views") - g(base, "reels_skip_rate") * g(base, "views")
        watch = watch_total / views / 1000 if views > 0 else None
        skip = skips / views if views > 0 else None
        mp4 = _find({"entry": x["entry"], "kind": "reel"})
        length = None
        if mp4 is not None and (mp4 / "reel.mp4").exists():
            r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4 / "reel.mp4")],
                               capture_output=True, text=True)
            length = float(r.stdout.strip() or 0) or None
        sends = g(at48, "shares") + g(at48, "saved")
        fmt = x.get("format") or {"001": "postcard", "008": "postcard"}.get(x["entry"]) or reel_format(entries.get(x["entry"], {}))
        row = dict(entry=x["entry"], name=entries.get(x["entry"], {}).get("name", "?"), format=fmt, age=at48["age_h"],
                   reach=reach, views=views, skip=skip, watch=watch, length=length,
                   watched=(watch / length if watch is not None and length else None), per100=(100 * sends / reach if reach > 0 else None))
        row["pass"] = (reach >= 20 and skip is not None and skip <= 60 and (row["watched"] or 0) >= 0.4 and (row["per100"] or 0) >= 1)
        rows.append(row)
    f = lambda v, fmt_: "-" if v is None else fmt_.format(v)
    print(f"{'entry':>5} {'name':<11} {'format':<9} {'age':>5} {'reach':>5} {'skip%':>5} {'watch':>6} {'len':>5} {'watched':>7} {'sends/100':>9}  pass")
    for r in rows:
        print(f"{r['entry']:>5} {r['name'][:11]:<11} {r['format']:<9} {r['age']:>5.1f} {r['reach']:>5} {f(r['skip'], '{:.0f}'):>5} "
              f"{f(r['watch'], '{:.1f}s'):>6} {f(r['length'], '{:.0f}s'):>5} {f(r['watched'], '{:.0%}'):>7} {f(r['per100'], '{:.1f}'):>9}  "
              f"{'yes' if r['pass'] else ('too early' if r['age'] < a.hours - 6 else 'no')}")
    print("\nby format (Reels at least 40 h old with reach 20+; medians):")
    for fmt in sorted({r["format"] for r in rows}):
        rs = [r for r in rows if r["format"] == fmt and r["age"] >= 40 and r["reach"] >= 20]
        med = lambda k: statistics.median([r[k] for r in rs if r[k] is not None]) if any(r[k] is not None for r in rs) else None
        print(f"  {fmt:<9} n={len(rs)}  reach {f(med('reach'), '{:.0f}')}  skip {f(med('skip'), '{:.0f}%')}  "
              f"watched {f(med('watched'), '{:.0%}')}  sends/100 {f(med('per100'), '{:.1f}')}")


def _prepare_job(job):
    e, folder, need_reel, process = job
    spec, seed = Spec(**e["spec"]), seed_from(e["name"])
    if process:
        from .reel import render_process
        render_process(spec, seed, e, Path(folder))
        return f"{e['id']} process Reel"
    make(e, spec, seed, Path(folder), reel=need_reel)
    return f"{e['id']} {'Reel and slides' if need_reel else 'slides'}"


def cmd_prepare(a):
    """Render whatever is due in the next --days days (or, with --all, everything not yet posted)
    that is missing or stale. One job per planet folder, so --jobs can render several at once."""
    from datetime import date
    schedule = json.loads(SCHEDULE.read_text())
    log = json.loads(LOG.read_text()) if LOG.exists() else []
    done = {(x["entry"], x["kind"]) for x in log}
    today = (date.today() - date.fromisoformat(LAUNCH_DAY)).days + 1
    entries = content_entries()
    groups = {}
    for f in CONTENT_FILES:
        path = ROOT / "content" / f
        if path.exists():
            groups.update({e["id"]: ("launch" if f == "launch.json" else Path(f).stem) for e in json.loads(path.read_text())})
    jobs = {}
    for item in schedule:
        if (item["entry"], item["kind"]) in done or item.get("hold") or (not a.all and item["day"] > today + a.days):
            continue
        problem = check_item(item, _find(item), entries)
        if not problem:
            continue
        e = entries.get(item["entry"])
        if e is None:
            print(f"cannot prepare {item['entry']}: not in content files")
            continue
        print(f"preparing {item['entry']} {item['kind']} (day {item['day']}): {problem}", flush=True)
        if item["kind"] == "process":
            dest = OUT / "process" / f"{e['id']}-{slug(e['name'])}.mp4"
            jobs[str(dest)] = (e, str(dest), False, True)
            continue
        folder = str(OUT / groups[e["id"]] / f"{e['id']}-{slug(e['name'])}")
        prev = jobs.get(folder)
        jobs[folder] = (e, folder, item["kind"] == "reel" or bool(prev and prev[2]), False)
    if a.jobs > 1 and len(jobs) > 1:
        with ProcessPoolExecutor(a.jobs) as pool:
            for line in pool.map(_prepare_job, jobs.values()):
                print("done:", line, flush=True)
    else:
        for job in jobs.values():
            print("done:", _prepare_job(job), flush=True)
    print("prepared")


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
    s = sub.add_parser("tapstop", help="'Tap to stop' Reel across every planet")
    s.add_argument("--beat", type=float, default=0.27, help="seconds per planet")
    s.set_defaults(fn=cmd_tapstop)
    s = sub.add_parser("avatar", help="render the profile picture")
    s.add_argument("--seed", default="Atlas of Elsewhere")
    s.set_defaults(fn=cmd_avatar)
    s = sub.add_parser("publish", help="publish one folder via the Graph API")
    s.add_argument("folder")
    s.add_argument("--kind", choices=["carousel", "reel"], required=True)
    s.add_argument("--base-url", required=True, help="public URL that serves the output/ directory")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_publish)
    s = sub.add_parser("next", help="publish what is due in content/schedule.json")
    s.add_argument("--base-url", required=True)
    s.add_argument("--max", type=int, default=3)
    s.add_argument("--asap", action="store_true", help="ignore the days: post the next ready item once --gap-hours have passed")
    s.add_argument("--gap-hours", type=float, default=2.5)
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_next)
    s = sub.add_parser("prepare", help="render what is due soon and not ready yet")
    s.add_argument("--days", type=int, default=1, help="look this many days ahead of today")
    s.add_argument("--all", action="store_true", help="everything not yet posted")
    s.add_argument("--jobs", type=int, default=1)
    s.set_defaults(fn=cmd_prepare)
    s = sub.add_parser("stats", help="reach, views, watch time, likes, shares and saves for every post")
    s.add_argument("--recent", type=float, default=0, help="only posts younger than this many hours (a light hourly check)")
    s.set_defaults(fn=cmd_stats)
    s = sub.add_parser("score", help="stranger-only scoreboard at about 48 h, by format version (no API calls)")
    s.add_argument("--hours", type=float, default=48)
    s.set_defaults(fn=cmd_score)
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
