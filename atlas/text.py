"""Typography: the five carousel slides and the Reel captions."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS = Path(__file__).resolve().parent.parent / "assets" / "fonts"
BRAND = "Atlas of Elsewhere"
CTA = "Leave a name in the comments and I'll find its planet."

PAGE = (1080, 1350)
MARGIN = 54
ART = (PAGE[0] - 2 * MARGIN, 1116)        # the printed image on slide 1
DETAIL = (PAGE[0] - 2 * MARGIN, 540)      # the close-up on slide 2

INK = (42, 36, 32)
MUTED = (124, 110, 96)


@lru_cache(maxsize=None)
def font(kind: str, size: int, weight: str = "Regular") -> ImageFont.FreeTypeFont:
    path = {"sans": "Inter.ttf", "serif": "EBGaramond.ttf", "italic": "EBGaramond-Italic.ttf"}[kind]
    f = ImageFont.truetype(str(FONTS / path), size)
    try:
        f.set_variation_by_name(weight)
    except (OSError, ValueError):
        pass
    return f


def typeset(text):
    """Curly quotes and apostrophes for set text (captions stay plain ASCII)."""
    text = re.sub(r"(?<=\w)'|'(?=[\s.,!?;:)]|$)", "’", text)
    return text.replace("'", "‘")


def wrap(draw, text, fnt, width):
    """Greedy wrap that keeps non-breaking spaces together, honours newlines as hard breaks,
    and never leaves one word alone on the last line of a paragraph."""
    return [ln for para in typeset(text).split("\n") for ln in _wrap_para(draw, para, fnt, width)]


def _wrap_para(draw, text, fnt, width):
    lines, cur = [], ""
    for word in text.split(" "):
        if not word:
            continue
        trial = (cur + " " + word).strip()
        if draw.textlength(trial.replace(" ", " "), font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if len(lines) > 1 and " " not in lines[-1].replace(" ", " ").strip():
        prev = lines[-2].split(" ")
        moved = prev[-1] + " " + lines[-1]
        if len(prev) > 1 and draw.textlength(moved.replace(" ", " "), font=fnt) <= width:
            lines[-2], lines[-1] = " ".join(prev[:-1]), moved
    return [ln.replace(" ", " ") for ln in lines]


def _fit(draw, text, kind, size, width, weight="Regular", floor=24):
    while size > floor and draw.textlength(text, font=font(kind, size, weight)) > width:
        size -= 2
    return font(kind, size, weight)


def paper(seed=0, size=PAGE):
    W, H = size
    rng = np.random.default_rng(seed)
    p = np.ones((H, W, 3), np.float32) * np.array([243, 236, 222], np.float32) / 255
    fib = Image.fromarray((rng.random((H // 8, W // 8)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    p *= 0.975 + 0.035 * np.asarray(fib, np.float32)[..., None] / 255
    p += rng.normal(0, 0.008, (H, W, 1))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    p *= (1 - 0.08 * (((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2))[..., None]
    return Image.fromarray((np.clip(p, 0, 1) * 255).astype(np.uint8))


INVITES = [
    "Leave a name in the comments. I chart a few every evening.",
    "Names welcome below. I find a few planets each evening.",
    "Comment a name (a pet's name works) and I'll go looking for its planet.",
    "Drop a name below and I'll chart where it lives.",
    "Got a name? Put it below and I'll find the planet it came from.",
    "Any name will do. Leave one and I'll look it up in the atlas.",
    "Tell me a name in the comments. I haven't found one without a planet yet.",
]
ASIDES = ["A dog's name works. So does your grandmother's.", "Pets, towns, nicknames. All of them have one.",
          "The odder the name, the odder the planet.", "Your cat's name will do nicely."]
SCHEDULE = Path(__file__).resolve().parent.parent / "content" / "schedule.json"


def pick(options, key):
    """Rotate through options by atlas number, so consecutive posts don't repeat."""
    digits = "".join(c for c in key if c.isdigit())
    return options[(int(digits) if digits else sum(map(ord, key))) % len(options)]


@lru_cache(maxsize=None)
def _slots():
    """Walk the schedule once: each post takes the next invite that neither of the two
    posts before it used, nor any earlier post of the same planet."""
    try:
        schedule = json.loads(SCHEDULE.read_text())
    except (OSError, ValueError):
        return {}
    out, recent, used = {}, [], {}
    for i, x in enumerate(schedule):
        for k in range(len(INVITES)):
            j = (i + k) % len(INVITES)
            if j not in recent[-2:] and j not in used.get(x["entry"], ()):
                break
        out[(x["entry"], x["kind"])] = j
        recent.append(j)
        used.setdefault(x["entry"], set()).add(j)
    return out


def invite_line(entry: dict, kind: str = "carousel") -> str:
    """The comment invite for this post, so neighbouring posts (and a Reel and
    carousel of the same planet) never share one."""
    i = _slots().get((entry["id"], kind))
    return INVITES[i] if i is not None else pick(INVITES, entry["id"])


def aside_line(entry: dict, invite: str) -> str:
    """A small line under the invite; it doesn't repeat a point the invite already made."""
    options = [a for a in ASIDES if not re.search(r"pet|dog|cat", a, re.I)] if re.search(r"pet", invite) else ASIDES
    return pick(options, entry["name"])


def cover(art: Image.Image, entry: dict, seed: int = 0) -> Image.Image:
    """Slide 1: the print on paper; title and hook set in the bottom margin."""
    W, H = PAGE
    m = MARGIN
    page = paper(seed)
    page.paste(art.resize(ART, Image.LANCZOS) if art.size != ART else art, (m, m))
    d = ImageDraw.Draw(page)
    y1 = m + ART[1] + 62
    number = f"No. {entry['id']}"
    d.text((W - m, y1), number, font=font("serif", 30), fill=MUTED, anchor="rs")
    d.text((m, y1), entry["name"], font=_fit(d, entry["name"], "serif", 60, W - 2 * m - 200, "Medium"), fill=INK, anchor="ls")
    line2 = entry.get("hook") or entry["subtitle"]
    f = font("italic", 37)
    lines = wrap(d, line2, f, W - 2 * m)
    if len(lines) > 2:
        f = font("italic", 33)
        lines = wrap(d, line2, f, W - 2 * m)
    for j, ln in enumerate(lines[:2]):
        d.text((m, y1 + 46 + j * 40), ln, font=f, fill=INK, anchor="ls")
    return page


def detail(close: Image.Image, entry: dict, seed: int = 0) -> Image.Image:
    """Slide 2: a close-up of the joke and one odd line. Instagram re-serves
    carousels from slide 2, so this has to work as a first impression."""
    W, H = PAGE
    m = MARGIN
    size = (W - 2 * m, 1010)
    page = paper(seed + 1)
    page.paste(close.resize(size, Image.LANCZOS) if close.size != size else close, (m, m))
    d = ImageDraw.Draw(page)
    line = entry.get("odd_line") or entry["hook"]
    f = font("italic", 46)
    lines = wrap(d, line, f, W - 2 * m)
    if len(lines) > 2:
        f = font("italic", 38)
        lines = wrap(d, line, f, W - 2 * m)
    y = m + size[1] + 70
    for j, ln in enumerate(lines[:3]):
        d.text((m, y + j * int(f.size * 1.25)), ln, font=f, fill=INK, anchor="ls")
    tail = f" · discovered by {entry['discovered_by']}" if entry.get("discovered_by") else ""
    d.text((W - m, H - m + 4), f"{entry['name']} · No. {entry['id']}{tail}", font=font("serif", 25), fill=MUTED, anchor="rs")
    return page


def page(entry: dict, seed: int = 0) -> Image.Image:
    """Slide 3: the written entry, set like a page from the atlas."""
    W, H = PAGE
    m = 96
    pg = paper(seed + 2)
    d = ImageDraw.Draw(pg)
    d.text((m, 170), "From the atlas", font=font("italic", 30), fill=MUTED, anchor="ls")
    d.text((m, 262), entry["name"], font=font("serif", 84, "Medium"), fill=INK, anchor="ls")
    d.text((m, 316), entry["subtitle"], font=font("italic", 36), fill=MUTED, anchor="ls")
    d.line([(m, 362), (W - m, 362)], fill=(200, 186, 164), width=2)
    rule = entry.get("rule")
    top, bottom = 410, H - (300 if rule else 150)
    size = 50
    while True:
        f = font("serif", size)
        lines = wrap(d, entry["story"], f, W - 2 * m)
        lh = int(size * 1.42)
        if top + lh * len(lines) <= bottom or size <= 30:
            break
        size -= 1
    for j, ln in enumerate(lines):
        d.text((m, top + j * lh), ln, font=f, fill=INK)
    if rule:
        y = top + lh * len(lines) + 50
        d.text((m, y + 30), "Local rule", font=font("italic", 32), fill=(150, 92, 60), anchor="ls")
        rf = font("italic", 40)
        for j, ln in enumerate(wrap(d, rule, rf, W - 2 * m)[:3]):
            d.text((m, y + 84 + j * 52), ln, font=rf, fill=INK, anchor="ls")
    d.text((W / 2, H - 80), f"No. {entry['id']}", font=font("serif", 26), fill=MUTED, anchor="ms")
    return pg


def punch(entry: dict, seed: int = 0) -> Image.Image:
    """Slide 3: the punchline on its own, big enough to screenshot and send."""
    W, H = PAGE
    pg = paper(seed + 3)
    d = ImageDraw.Draw(pg)
    line = (entry.get("beats") or entry.get("reel_lines") or [entry["hook"]])[-1]
    size = 84
    while True:
        f = font("serif", size, "Medium")
        lines = wrap(d, line, f, W - 2 * 120)
        if len(lines) <= 6 or size <= 56:
            break
        size -= 4
    lh = int(size * 1.22)
    y = H / 2 - lh * len(lines) / 2 + size * 0.7
    for j, ln in enumerate(lines):
        d.text((W / 2, y + j * lh), ln, font=f, fill=INK, anchor="ms")
    d.text((W / 2, H - 90), f"{entry['name']} · No. {entry['id']}", font=font("italic", 30), fill=MUTED, anchor="ms")
    return pg


def guide(entry: dict, seed: int = 0) -> Image.Image:
    """Slide 4: a field-guide plate with the facts and one local rule."""
    W, H = PAGE
    pg = paper(seed + 3)
    d = ImageDraw.Draw(pg)
    x0, y0, x1, y1 = 90, 130, W - 90, H - 120
    d.rectangle([x0, y0, x1, y1], outline=(150, 132, 110), width=3)
    d.rectangle([x0 + 12, y0 + 12, x1 - 12, y1 - 12], outline=(190, 174, 150), width=1)
    cx = W / 2
    d.text((cx, y0 + 120), "Field guide to", font=font("italic", 44), fill=MUTED, anchor="ms")
    d.text((cx, y0 + 235), entry["name"], font=_fit(d, entry["name"], "serif", 110, x1 - x0 - 120, "Medium"), fill=INK, anchor="ms")
    y = y0 + 350
    lab, val = font("italic", 42), font("serif", 44)
    for k, v in list(entry.get("facts", {}).items())[:4]:
        d.text((x0 + 70, y), k, font=lab, fill=MUTED, anchor="ls")
        d.text((x1 - 70, y), v, font=val, fill=INK, anchor="rs")
        d.line([(x0 + 70 + d.textlength(k, font=lab) + 18, y - 9), (x1 - 70 - d.textlength(v, font=val) - 18, y - 9)], fill=(205, 192, 170), width=2)
        y += 86
    rule = entry.get("rule")
    if rule:
        y += 40
        d.line([(x0 + 70, y), (x1 - 70, y)], fill=(170, 152, 128), width=2)
        y += 96
        d.text((cx, y), f"Local rule No. {entry.get('rule_no', int(''.join(c for c in entry['id'] if c.isdigit()) or 1))}",
               font=font("italic", 42), fill=(150, 92, 60), anchor="ms")
        y += 40
        f = font("serif", 52)
        lines = wrap(d, rule, f, x1 - x0 - 160)
        if len(lines) > 4:
            f = font("serif", 44)
            lines = wrap(d, rule, f, x1 - x0 - 160)
        for j, ln in enumerate(lines):
            d.text((cx, y + 30 + j * int(f.size * 1.3)), ln, font=f, fill=INK, anchor="ma")
    credit = f"Discovered by {entry['discovered_by']}" if entry.get("discovered_by") else "Issued by the Atlas of Elsewhere"
    d.text((cx, H - 62), credit, font=font("italic", 30 if entry.get("discovered_by") else 26), fill=MUTED, anchor="ms")
    return pg


def invite(close: Image.Image, entry: dict, seed: int = 0) -> Image.Image:
    """Slide 5: the invitation, under a strip of the close-up."""
    W, H = PAGE
    m = MARGIN
    pg = paper(seed + 4)
    sh = int(close.width * 0.42)
    top = max(0, min(close.height - sh, int(close.height * 0.5 - sh / 2)))
    strip = close.crop((0, top, close.width, top + sh)).resize((W - 2 * m, int((W - 2 * m) * 0.42)), Image.LANCZOS)
    pg.paste(strip, (m, m))
    d = ImageDraw.Draw(pg)
    y = m + strip.height + 250
    f = font("serif", 84, "Medium")
    for j, ln in enumerate(wrap(d, "Your name has a planet too.", f, W - 2 * 110)):
        d.text((W / 2, y + j * 100), ln, font=f, fill=INK, anchor="ms")
    y += 230
    f2 = font("italic", 42)
    line = invite_line(entry, "carousel")
    for j, ln in enumerate(wrap(d, line, f2, W - 2 * 130)):
        d.text((W / 2, y + j * 56), ln, font=f2, fill=INK, anchor="ms")
    y += 170
    d.text((W / 2, y), typeset(aside_line(entry, line)), font=font("italic", 32), fill=MUTED, anchor="ms")
    d.text((W / 2, H - m - 10), f"No. {entry['id']} · {BRAND}", font=font("serif", 26), fill=MUTED, anchor="ms")
    return pg


notes = detail  # older name


# --------------------------------------------------------------------------
# Reel captions: transparent RGBA cards composited per frame with an opacity.

def _shadowed(base: Image.Image, painter, blur=6, strength=150):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    painter(ImageDraw.Draw(layer))
    a = layer.getchannel("A")
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow.putalpha(a.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: min(255, v * strength // 255)))
    out = Image.alpha_composite(base.convert("RGBA"), shadow)
    return Image.alpha_composite(out, layer)


def reel_card(size, lines, kind="hook"):
    """Pre-render a block of Reel text, kept inside Instagram's safe zone."""
    W, H = size
    base = Image.new("RGBA", size, (0, 0, 0, 0))
    m = 96
    usable = W - m - 170   # the right edge is covered by the like/comment buttons
    white = (250, 246, 238, 255)

    def paint(d):
        if kind == "hook":
            f = font("serif", 80, "Medium")
            y = H * 0.30
            for ln in wrap(d, lines[0], f, usable):
                d.text((m, y), ln, font=f, fill=white)
                y += 92
        elif kind == "lore":
            f = font("italic", 62)
            y = H * 0.30
            for text in lines:
                for ln in wrap(d, text, f, usable):
                    d.text((m, y), ln, font=f, fill=white)
                    y += 74
                y += 30
        else:  # name card
            name, number, cta = lines
            d.text((W / 2, H * 0.30), f"No. {number}, {BRAND}", font=font("italic", 36), fill=white, anchor="ms")
            d.text((W / 2, H * 0.40), name, font=_fit(d, name, "serif", 170, W - 2 * m, "Medium"), fill=white, anchor="ms")
            d.text((W / 2, H * 0.447), cta, font=_fit(d, cta, "italic", 42, W - 2 * m), fill=white, anchor="ms")

    out = _shadowed(base, paint, blur=12, strength=190)
    # soft dark band behind the text block, fading with the card
    a = np.asarray(out.getchannel("A"), np.float32)
    rows = np.flatnonzero(a.max(axis=1) > 8)
    if len(rows):
        c, half = (rows[0] + rows[-1]) / 2, (rows[-1] - rows[0]) / 2 + 90
        y = np.arange(H, dtype=np.float32)
        band = np.exp(-np.maximum(np.abs(y - c) - half * 0.6, 0) ** 2 / (2 * (half * 0.5) ** 2)) * 0.3
        scrim = np.zeros((H, W, 4), np.float32)
        scrim[..., 3] = band[:, None] * 255
        out = Image.alpha_composite(Image.fromarray(scrim.astype(np.uint8), "RGBA"), out)
    return np.asarray(out, np.float32) / 255


def overlay(size, items, scrim=0.42):
    """General text card for Reels.

    items: dicts with text, y (fraction of height, or "after": below the previous item plus gap),
    kind ('serif'|'italic'|'sans'), size, weight, align ('center'|'left'), x (px for left align), width (px wrap).
    """
    W, H = size
    base = Image.new("RGBA", size, (0, 0, 0, 0))
    white = (250, 246, 238, 255)

    def paint(d):
        y = 0.0
        for it in items:
            f = font(it.get("kind", "serif"), it.get("size", 64), it.get("weight", "Regular"))
            width = it.get("width", W - 2 * 96)
            lines = wrap(d, it["text"], f, width)
            lh = int(f.size * it.get("leading", 1.18))
            y = y + H * it.get("gap", 0.012) if it["y"] == "after" else H * it["y"]
            for ln in lines:
                if it.get("align", "center") == "center":
                    d.text((W / 2, y), ln, font=f, fill=it.get("color", white), anchor="ma")
                else:
                    d.text((it.get("x", 96), y), ln, font=f, fill=it.get("color", white))
                y += lh

    out = _shadowed(base, paint, blur=12, strength=190)
    if scrim:
        a = np.asarray(out.getchannel("A"), np.float32)
        rows = np.flatnonzero(a.max(axis=1) > 8)
        if len(rows):
            c, half = (rows[0] + rows[-1]) / 2, (rows[-1] - rows[0]) / 2 + 90
            y = np.arange(H, dtype=np.float32)
            band = np.exp(-np.maximum(np.abs(y - c) - half * 0.6, 0) ** 2 / (2 * (half * 0.5) ** 2)) * scrim
            sc = np.zeros((H, W, 4), np.float32)
            sc[..., 3] = band[:, None] * 255
            out = Image.alpha_composite(Image.fromarray(sc.astype(np.uint8), "RGBA"), out)
    return np.asarray(out, np.float32) / 255
