"""Typography: the print (slide 1), the notes page (slide 2) and Reel captions."""
from __future__ import annotations

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


def wrap(draw, text, fnt, width):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


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


def cover(art: Image.Image, entry: dict, seed: int = 0) -> Image.Image:
    """Slide 1: the image printed on paper, title set in the bottom margin."""
    W, H = PAGE
    m = MARGIN
    page = paper(seed)
    page.paste(art.resize(ART, Image.LANCZOS) if art.size != ART else art, (m, m))
    d = ImageDraw.Draw(page)
    y1, y2 = m + ART[1] + 76, m + ART[1] + 122
    number = f"No. {entry['id']}"
    d.text((W - m, y1), number, font=font("serif", 30), fill=MUTED, anchor="rs")
    d.text((W - m, y2), BRAND, font=font("italic", 27), fill=MUTED, anchor="rs")
    room = W - 2 * m - max(d.textlength(BRAND, font=font("italic", 27)), d.textlength(number, font=font("serif", 30))) - 40
    d.text((m, y1), entry["name"], font=_fit(d, entry["name"], "serif", 66, room, "Medium"), fill=INK, anchor="ls")
    d.text((m, y2), entry["subtitle"], font=_fit(d, entry["subtitle"], "italic", 31, room), fill=MUTED, anchor="ls")
    return page


def notes(detail: Image.Image, entry: dict, seed: int = 0) -> Image.Image:
    """Slide 2: a close-up and the written entry, set like a book page."""
    W, H = PAGE
    m = MARGIN
    page = paper(seed + 1)
    page.paste(detail.resize(DETAIL, Image.LANCZOS) if detail.size != DETAIL else detail, (m, m))
    d = ImageDraw.Draw(page)
    y = m + DETAIL[1] + 88
    d.text((m, y), entry["name"], font=font("serif", 58, "Medium"), fill=INK, anchor="ls")
    d.text((W - m, y), f"No. {entry['id']}", font=font("serif", 28), fill=MUTED, anchor="rs")
    y += 44
    d.text((m, y), entry["subtitle"], font=font("italic", 30), fill=MUTED, anchor="ls")

    facts = list(entry.get("facts", {}).items())
    bottom = H - m - (92 if facts else 46)
    top = y + 40
    size = 36
    while True:
        f = font("serif", size)
        lines = wrap(d, entry["story"], f, W - 2 * m)
        lh = int(size * 1.4)
        if top + lh * len(lines) <= bottom or size <= 26:
            break
        size -= 1
    for j, ln in enumerate(lines):
        d.text((m, top + j * lh), ln, font=f, fill=INK)

    if facts:
        lab, val = font("italic", 25), font("serif", 25)
        while facts:
            width = sum(d.textlength(k + " ", font=lab) + d.textlength(v, font=val) for k, v in facts) + 34 * (len(facts) - 1)
            if width <= W - 2 * m:
                break
            facts = facts[:-1]
        x, fy = m, H - m - 52
        for k, v in facts:
            d.text((x, fy), k + " ", font=lab, fill=MUTED, anchor="ls")
            x += d.textlength(k + " ", font=lab)
            d.text((x, fy), v, font=val, fill=INK, anchor="ls")
            x += d.textlength(v, font=val) + 34
    d.text((m, H - m - 6), CTA, font=font("italic", 25), fill=MUTED, anchor="ls")
    return page


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
