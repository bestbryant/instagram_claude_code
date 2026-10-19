"""Procedural planet landscapes.

A scene is a stack of layers, far to near. Each layer holds premultiplied
colour, alpha, optional emissive light and a parallax speed, so one world can
be flattened into a still postcard or panned into a Reel.
"""
from __future__ import annotations

import hashlib
import math
import zlib
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


# --------------------------------------------------------------------------
# seeds & noise

def seed_from(text: str) -> int:
    """Stable 64-bit seed for a planet name (case and spacing insensitive)."""
    key = " ".join(text.lower().split())
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")


class Seeds:
    """Independent random streams per feature, so a world looks the same at
    any canvas size (changing one feature never reshuffles another)."""

    def __init__(self, seed: int):
        self.seed = seed

    def key(self, *tags):
        return [self.seed & 0xFFFFFFFF, self.seed >> 32] + [zlib.crc32(str(t).encode()) for t in tags]

    def rng(self, *tags) -> np.random.Generator:
        return np.random.default_rng(self.key(*tags))


def fbm(seeds: Seeds, tag, u, octaves=5, freq=2.0, pers=0.5, lac=2.0):
    """1-D fractal value noise over world positions u (1.0 == canvas width)."""
    out = np.zeros_like(u, dtype=np.float64)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        r = seeds.rng(tag, "oct", o)
        xs = u * freq + r.uniform(0, 64)
        lat = r.uniform(-1, 1, int(np.floor(xs.max())) + 2)
        i = np.floor(xs).astype(int)
        f = xs - i
        f = f * f * (3 - 2 * f)
        out += amp * (lat[i] * (1 - f) + lat[i + 1] * f)
        total += amp
        amp *= pers
        freq *= lac
    return out / total


def noise2d(rng: np.random.Generator, h: int, w: int, cells: int, octaves=3) -> np.ndarray:
    """Smooth 2-D noise in [0,1] by upscaling random grids."""
    out = np.zeros((h, w), np.float32)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        c = cells * (2 ** o)
        grid = rng.random((max(2, int(c * h / max(w, 1))) + 1, c + 1)).astype(np.float32)
        img = Image.fromarray(grid, mode="F").resize((w, h), Image.BICUBIC)
        out += amp * np.asarray(img)
        total += amp
        amp *= 0.5
    return np.clip(out / total, 0, 1)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    return a + (b - a) * t


def hexc(h: str) -> np.ndarray:
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def lum(c) -> float:
    return float(0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2])


# --------------------------------------------------------------------------
# palettes

PALETTES = {
    #               sky top / mid / horizon             sun        haze       land       accent     water      light
    "gold_hour":   (["#1d1238", "#6b2f63", "#f3a35f"], "#fff0c2", "#e9936a", "#170c22", "#f6c58f", "#2c1a3c", "#ffcf7a"),
    "mint_dawn":   (["#0e2a3b", "#2f7f86", "#bfeccf"], "#fffbe0", "#9fd8c3", "#0a1d26", "#f4d7a1", "#174b56", "#ffe7a3"),
    "violet_ice":  (["#0b0a24", "#2d2a6b", "#8f9cf0"], "#e9ecff", "#7f86d6", "#0a0a1f", "#cfd6ff", "#1c1f4a", "#ffd58a"),
    "pastel":      (["#6fa3e8", "#b9aef0", "#ffd6e0"], "#fffaf0", "#e9c6e6", "#4d3b74", "#ffffff", "#9aa7e6", "#fff1b8"),
    "crimson":     (["#12020a", "#5a0f1d", "#ff6a3d"], "#ffe2a8", "#c8463a", "#14040a", "#ff9c6b", "#3a0a14", "#ffb36b"),
    "teal_night":  (["#01060f", "#06283a", "#1b7a8c"], "#d9fff6", "#1e6b7a", "#010a10", "#e7efe9", "#03202b", "#ffd48a"),
    "rust_desert": (["#3a1f2b", "#b4553f", "#f6c27a"], "#fff3d6", "#e0a06a", "#3a1a14", "#f9e0b0", "#7a3b2b", "#ffe0a0"),
    "rose_fog":    (["#3e2a4f", "#a5678e", "#ffd3c4"], "#fff6ee", "#e6b4b4", "#2a1830", "#ffe6d6", "#6b4a70", "#ffd9a0"),
    "abyss":       (["#000d14", "#04384a", "#2a9d8f"], "#e9f5db", "#2c7f80", "#00090e", "#e9d8a6", "#012a36", "#ffe3a3"),
    "toxic":       (["#06120a", "#1f4d2a", "#c9f26b"], "#f7ffd1", "#7fae4b", "#04100a", "#e9ff9a", "#0f2f1a", "#fff2a8"),
    "sepia":       (["#2a2420", "#7d6550", "#e8d3ad"], "#fff8e7", "#c9b08a", "#221b16", "#f2e4c8", "#5a4a3c", "#ffe2a8"),
    "cobalt_noon": (["#0d3b8c", "#3f86d9", "#cfe9ff"], "#ffffff", "#9cc8f0", "#0b2147", "#ffe9c2", "#2b5fa8", "#fff0c0"),
    "lilac_dusk":  (["#1a1033", "#52327a", "#e7a3c7"], "#fff0f6", "#b98bc0", "#140c26", "#ffd7ea", "#33215a", "#ffcf8a"),
    "polar_night": (["#020617", "#0b1f3a", "#2b4f6e"], "#e8f4ff", "#3d6683", "#020713", "#dfe9f5", "#0b1f33", "#ffc978"),
    "pumpkin":     (["#120a1c", "#4a1f3d", "#ff8a3d"], "#ffe3b0", "#c4643a", "#0c0610", "#ffb26b", "#2a1020", "#ffb347"),
}


@dataclass
class Palette:
    sky: list
    sun: np.ndarray
    haze: np.ndarray
    land: np.ndarray
    accent: np.ndarray
    water: np.ndarray
    light: np.ndarray

    @classmethod
    def get(cls, name: str) -> "Palette":
        sky, *rest = PALETTES[name]
        return cls([hexc(c) for c in sky], *[hexc(c) for c in rest])


TERRAINS = ["peaks", "hills", "dunes", "mesas", "spires", "crystal"]


# --------------------------------------------------------------------------
# spec

@dataclass
class Spec:
    palette: str = "gold_hour"
    terrain: str = "peaks"
    layers: int = 5
    horizon: float = 0.62          # fraction of canvas height
    relief: float = 1.0            # terrain height multiplier
    water: bool = False
    shore: str = "none"            # none | left | right (foreground land over water)
    suns: int = 1
    sun_x: float | None = None     # fractions of canvas
    sun_y: float | None = None
    sun_size: float = 0.05         # radius as fraction of width
    giant: bool = False            # gas giant in the sky
    ring: bool = False
    giant_size: float = 0.24
    giant_x: float | None = None
    giant_y: float | None = None
    moons: int = 0
    big_moon: bool = False         # a moon close enough to fill the sky
    aurora: bool = False
    stars: float | None = None     # None = from sky darkness
    islands: int = 0               # floating islands
    trees: str = "none"            # none | pines | giant | lone
    snow: bool = False
    figure: bool = False
    lighthouse: bool = False
    house: bool = False
    particles: str = "none"        # none | rain | rain_up | embers | snow | snow_up
    glass_waves: bool = False
    lanterns: int = 0              # glowing pumpkins along the hills
    moths: int = 0                 # giant moths against the sky
    mist: float = 0.5
    gag: str = ""                  # the planet's visual joke (see props.GAGS)
    cartographer: bool = True      # the narrator in a yellow coat, hidden in the print
    spot: str = ""                 # extra spot-colour ink, e.g. red umbrellas
    glow_rims: bool = False        # canyon edges that glow at night
    sign: str = ""                 # a signpost; lines separated by "|"
    crowd: int = 0                 # a row of people, each holding something
    daisies: int = 0               # flowers across the foreground
    lamp: bool = False             # a tall lamp aimed at the sky
    stage: float = 0.0             # flat foreground ledge at this height for the extras (0: natural ground)


def random_spec(seed: int) -> Spec:
    """A plausible, varied world for any seed."""
    r = Seeds(seed).rng("spec")
    pal = str(r.choice(list(PALETTES)))
    s = Spec(palette=pal)
    s.terrain = str(r.choice(TERRAINS, p=[0.26, 0.18, 0.14, 0.14, 0.14, 0.14]))
    s.layers = int(r.integers(4, 7))
    s.horizon = float(r.uniform(0.56, 0.68))
    s.relief = float(r.uniform(0.8, 1.25))
    s.water = r.random() < 0.3
    if s.water:
        s.shore = str(r.choice(["none", "left", "right"], p=[0.3, 0.35, 0.35]))
        s.layers = int(r.integers(3, 5))
    dark = 1 - lum(Palette.get(pal).sky[0])
    s.suns = int(r.choice([0, 1, 1, 1, 2], p=[0.15 + 0.2 * (dark > 0.9), 0.3, 0.2, 0.15, 0.2 - 0.2 * (dark > 0.9)]))
    s.sun_size = float(r.uniform(0.035, 0.07))
    s.giant = r.random() < 0.35
    s.ring = s.giant and r.random() < 0.55
    s.giant_size = float(r.uniform(0.16, 0.3))
    s.moons = int(r.choice([0, 0, 1, 2, 3]))
    s.big_moon = (not s.giant) and r.random() < 0.12
    s.aurora = dark > 0.88 and r.random() < 0.45
    s.islands = int(r.choice([0, 0, 0, 0, 2, 3]))
    s.trees = str(r.choice(["none", "pines", "pines", "giant", "lone"], p=[0.45, 0.25, 0.1, 0.08, 0.12]))
    s.snow = pal in ("violet_ice", "polar_night", "pastel") and r.random() < 0.5
    s.figure = r.random() < 0.45
    s.lighthouse = s.water and s.shore != "none" and r.random() < 0.5
    s.house = (not s.lighthouse) and r.random() < 0.25
    s.particles = str(r.choice(["none", "none", "none", "rain_up", "embers", "snow"]))
    if s.particles in ("snow", "snow_up") and not s.snow:
        s.particles = "none"
    s.mist = float(r.uniform(0.3, 0.8))
    return s


# --------------------------------------------------------------------------
# drawing primitives

def stamp(P, A, shapes, color, value=1.0, ss=4):
    """Rasterise polygons/ellipses (anti-aliased) into a premultiplied layer.

    shapes: list of ("poly", [(x,y),...]) or ("ellipse", (x0,y0,x1,y1)) or
    ("line", ([(x,y),...], width)).
    """
    xs, ys = [], []
    for kind, g in shapes:
        if kind == "poly":
            xs += [p[0] for p in g]
            ys += [p[1] for p in g]
        elif kind == "ellipse":
            xs += [g[0], g[2]]
            ys += [g[1], g[3]]
        else:
            pts, wdt = g
            xs += [p[0] - wdt for p in pts] + [p[0] + wdt for p in pts]
            ys += [p[1] - wdt for p in pts] + [p[1] + wdt for p in pts]
    H, W = A.shape
    x0, x1 = int(math.floor(min(xs))) - 2, int(math.ceil(max(xs))) + 2
    y0, y1 = int(math.floor(min(ys))) - 2, int(math.ceil(max(ys))) + 2
    cx0, cx1, cy0, cy1 = max(x0, 0), min(x1, W), max(y0, 0), min(y1, H)
    if cx0 >= cx1 or cy0 >= cy1:
        return
    im = Image.new("L", ((x1 - x0) * ss, (y1 - y0) * ss), 0)
    d = ImageDraw.Draw(im)
    for kind, g in shapes:
        if kind == "poly":
            d.polygon([((x - x0) * ss, (y - y0) * ss) for x, y in g], fill=255)
        elif kind == "ellipse":
            d.ellipse([(g[0] - x0) * ss, (g[1] - y0) * ss, (g[2] - x0) * ss, (g[3] - y0) * ss], fill=255)
        else:
            pts, wdt = g
            d.line([((x - x0) * ss, (y - y0) * ss) for x, y in pts], fill=255, width=max(1, int(wdt * ss)))
    m = np.asarray(im.resize((x1 - x0, y1 - y0), Image.BOX), np.float32) / 255 * value
    m = m[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
    sl = (slice(cy0, cy1), slice(cx0, cx1))
    P[sl] = P[sl] * (1 - m[..., None]) + np.asarray(color, np.float32) * m[..., None]
    A[sl] = A[sl] * (1 - m) + m


def glow(E, x, y, radius, color, strength=1.0):
    """Additive soft light into an emissive buffer."""
    H, W = E.shape[:2]
    r = int(radius * 4)
    x0, x1, y0, y1 = max(int(x) - r, 0), min(int(x) + r + 1, W), max(int(y) - r, 0), min(int(y) + r + 1, H)
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d2 = ((xx - x) ** 2 + (yy - y) ** 2) / (radius * radius)
    k = (np.exp(-d2 * 0.5) + 0.35 * np.exp(-np.sqrt(d2) * 0.9)) * strength
    E[y0:y1, x0:x1] += k[..., None] * np.asarray(color, np.float32)


def pine(x, y, h, rng):
    """Jagged conifer silhouette standing at (x, y)."""
    tiers = int(rng.integers(5, 9)) + int(h / 70)
    w = h * rng.uniform(0.26, 0.36)
    left, right = [(x, y - h)], []
    for j in range(1, tiers + 1):
        f = j / tiers
        yy = y - h + h * 0.88 * f
        ww = w * (0.25 + 0.75 * f) * rng.uniform(0.85, 1.1)
        left += [(x - ww, yy), (x - ww * 0.42, yy - h * 0.02)]
        right += [(x + ww * 0.42, yy - h * 0.02), (x + ww, yy)]
    trunk = h * 0.035
    body = left[:-1] + [(x - trunk, y - h * 0.12), (x - trunk, y + 2), (x + trunk, y + 2), (x + trunk, y - h * 0.12)] + right[::-1][1:]
    return [("poly", body)]


def round_tree(x, y, h, rng):
    trunk_w = h * 0.06
    shapes = [("poly", [(x - trunk_w, y + 2), (x - trunk_w * 0.6, y - h * 0.55), (x + trunk_w * 0.6, y - h * 0.55), (x + trunk_w, y + 2)])]
    for _ in range(7):
        cx = x + rng.uniform(-0.28, 0.28) * h
        cy = y - h * rng.uniform(0.55, 0.85)
        rr = h * rng.uniform(0.18, 0.3)
        shapes.append(("ellipse", (cx - rr, cy - rr, cx + rr, cy + rr)))
    return shapes


def person(x, y, h):
    """A small standing figure, coat to the knees, facing the view."""
    hw = h * 0.13
    head = h * 0.085
    shapes = [
        ("ellipse", (x - head, y - h, x + head, y - h + 2 * head)),
        ("poly", [(x - hw * 0.55, y - h + 2.1 * head), (x + hw * 0.55, y - h + 2.1 * head),
                  (x + hw, y - h * 0.62), (x + hw * 1.25, y - h * 0.28), (x - hw * 1.25, y - h * 0.28), (x - hw, y - h * 0.62)]),
        ("poly", [(x - hw * 0.62, y - h * 0.3), (x - hw * 0.1, y - h * 0.3), (x - hw * 0.2, y + 1), (x - hw * 0.6, y + 1)]),
        ("poly", [(x + hw * 0.1, y - h * 0.3), (x + hw * 0.62, y - h * 0.3), (x + hw * 0.6, y + 1), (x + hw * 0.2, y + 1)]),
    ]
    return shapes


def moth(x, y, s):
    """Moth silhouette centred at (x, y) with wingspan about 2*s."""
    up = [(x, y - s * 0.05), (x - s * 0.55, y - s * 0.75), (x - s * 1.05, y - s * 0.6), (x - s * 1.0, y - s * 0.05), (x - s * 0.2, y + s * 0.12)]
    lo = [(x, y + s * 0.05), (x - s * 0.7, y + s * 0.3), (x - s * 0.55, y + s * 0.75), (x - s * 0.08, y + s * 0.4)]
    mirror = lambda pts: [(2 * x - px, py) for px, py in pts]
    shapes = [("poly", catmull(p + [p[0]], 5)) for p in (up, lo, mirror(up), mirror(lo))]
    shapes.append(("ellipse", (x - s * 0.08, y - s * 0.3, x + s * 0.08, y + s * 0.55)))
    shapes.append(("line", ([(x - s * 0.03, y - s * 0.28), (x - s * 0.3, y - s * 0.62)], max(1.0, s * 0.03))))
    shapes.append(("line", ([(x + s * 0.03, y - s * 0.28), (x + s * 0.3, y - s * 0.62)], max(1.0, s * 0.03))))
    return shapes


def catmull(pts, n=8):
    """Smooth a closed-ish polyline with Catmull-Rom splines."""
    p = np.asarray(pts, float)
    out = []
    for i in range(len(p) - 1):
        p0, p1, p2, p3 = p[max(i - 1, 0)], p[i], p[i + 1], p[min(i + 2, len(p) - 1)]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(p[-1])
    return [tuple(q) for q in out]


WAVE = [(0.0, 0.0), (0.2, 0.3), (0.4, 0.62), (0.55, 0.85), (0.68, 0.97), (0.8, 1.0), (0.9, 0.95), (0.97, 0.83),
        (0.985, 0.7), (0.93, 0.71), (0.88, 0.78), (0.82, 0.76), (0.78, 0.66), (0.78, 0.5), (0.84, 0.3), (0.95, 0.1), (1.06, 0.0)]


# --------------------------------------------------------------------------
# scene

@dataclass(eq=False)
class Layer:
    P: np.ndarray                  # premultiplied rgb (H, w, 3)
    A: np.ndarray                  # alpha (H, w)
    speed: float                   # parallax factor (0 = fixed sky, 1 = nearest)
    E: np.ndarray | None = None    # emissive, added after blending
    stage: int = 0                 # 0: reflected in water, 1: in front of water
    pulse: float = 0.0             # emissive blink frequency (Hz), 0 = steady
    drift: tuple = (0.0, 0.0)      # particles: wrap-around motion, canvas widths per second


@dataclass
class Scene:
    W: int
    H: int
    spec: Spec
    pal: Palette
    sky: np.ndarray                # (H, w, 3)
    aurora: list                   # two additive images to cross-fade
    stars: list                    # star groups (H, w), twinkle independently
    star_mask: np.ndarray          # 0 where a celestial body hides the stars
    layers: list = field(default_factory=list)
    water_y: int | None = None
    sun_xy: list = field(default_factory=list)
    sky_speed: float = 0.03


def _ridge(kind, seeds, tag, u, rng):
    if kind == "peaks":
        base = fbm(seeds, tag + "b", u, 7, 2.4, 0.52)
        ridged = 1 - np.abs(fbm(seeds, tag + "r", u, 5, 3.0, 0.5))
        h = 0.5 + 0.75 * base
        h = 0.55 * h + 0.45 * ridged ** 2
    elif kind == "hills":
        h = 0.5 + 0.9 * fbm(seeds, tag, u, 4, 1.5, 0.42)
    elif kind == "dunes":
        warp = fbm(seeds, tag + "w", u, 3, 0.8, 0.5)
        freq = rng.uniform(2.2, 4)
        p = (u * freq + warp * 2.5) % 1.0
        saw = np.where(p < 0.78, p / 0.78, (1 - p) / 0.22)
        saw = saw * saw * (3 - 2 * saw)
        env = np.clip(0.5 + 1.2 * fbm(seeds, tag + "e", u, 2, 1.3, 0.5), 0.1, 1)
        h = 0.45 * saw * env + 0.55 * (0.5 + 0.8 * fbm(seeds, tag, u, 3, 1.0, 0.4))
    elif kind == "mesas":
        b = 0.5 + 0.9 * fbm(seeds, tag, u, 3, 2.0, 0.45)
        plateau = 1 / (1 + np.exp(-(b - 0.55) * 26))
        h = 0.12 + 0.72 * plateau + 0.06 * fbm(seeds, tag + "d", u, 5, 12, 0.5)
    elif kind == "spires":
        h = 0.18 + 0.25 * (0.5 + fbm(seeds, tag, u, 4, 2.0, 0.45))
        n = int(u.max() * rng.uniform(8, 16)) + 1
        for p, ht, w in zip(rng.uniform(0, u.max(), n), rng.uniform(0.35, 1.0, n), rng.uniform(0.006, 0.02, n)):
            h = np.maximum(h, ht * np.clip(1 - np.abs(u - p) / w, 0, 1) ** 0.6)
    elif kind == "crystal":
        xs = np.cumsum(rng.uniform(0.015, 0.07, int(u.max() / 0.015) + 4)) - 0.05
        ys = rng.uniform(0.15, 1.0, len(xs)) ** 1.3
        h = np.interp(u, xs, ys)
    else:
        raise ValueError(kind)
    return np.clip(h, 0, 1.2)


def build(spec: Spec, seed: int, W=1080, H=1350, pan=0.0) -> Scene:
    """Build a scene. pan = pixels the nearest layer travels (0 for stills)."""
    seeds = Seeds(seed)
    pal = Palette.get(spec.palette)
    hy = spec.horizon * H

    def width(speed):
        return W + int(math.ceil(pan * speed)) + 2

    # ---- sky ------------------------------------------------------------
    sw = width(0.03)
    y = (np.arange(H, dtype=np.float32) / H)[:, None]
    c0, c1, c2 = pal.sky
    a = smoothstep(0, spec.horizon * 0.55, y)
    b = smoothstep(spec.horizon * 0.45, spec.horizon, y)
    col = mix(mix(c0, c1, a[..., None]), c2, b[..., None])
    sky = np.broadcast_to(col, (H, sw, 3)).astype(np.float32).copy()
    sky += pal.haze * 0.18 * np.exp(-((y - spec.horizon) / 0.07) ** 2)[..., None]
    xx = np.arange(sw, dtype=np.float32)[None, :]
    yy = np.arange(H, dtype=np.float32)[:, None]

    sr = seeds.rng("sun")
    suns = []
    for k in range(spec.suns):
        if k == 0:
            sx = (spec.sun_x if spec.sun_x is not None else sr.uniform(0.22, 0.78)) * W
            sy = (spec.sun_y if spec.sun_y is not None else sr.uniform(0.3, 0.85) * spec.horizon) * H
        else:
            side = -1 if suns[0][0] > W / 2 else 1
            sx = suns[0][0] + side * sr.uniform(0.2, 0.3) * W
            sy = suns[0][1] + sr.uniform(-0.1, -0.03) * H
        rad = spec.sun_size * W * (0.62 if k == 1 else 1.0)
        suns.append((sx, sy, rad))
        d = np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2) / W
        sky += pal.sun * (0.5 * np.exp(-d / 0.05) + 0.22 * np.exp(-d / 0.22))[..., None] * (0.7 if k else 1.0)

    mask = np.ones((H, sw), np.float32)

    def body(cx, cy, r, base, bands=False, ring=False, craters=False, haze_amt=0.15, tag="b"):
        rng = seeds.rng("body", tag)
        if suns:
            lx, ly = suns[0][0] - cx, suns[0][1] - cy
            n = math.hypot(lx, ly) + 1e-6
            L = np.array([lx / n * 0.85, ly / n * 0.85, rng.uniform(-0.2, 0.45)])
        else:
            L = np.array([-0.6, -0.5, rng.uniform(-0.1, 0.5)])
        L /= np.linalg.norm(L)
        ext = 2.4 if ring else 1.05
        x0, x1 = int(max(cx - r * ext, 0)), int(min(cx + r * ext + 1, sw))
        y0, y1 = int(max(cy - r * ext, 0)), int(min(cy + r * ext + 1, H))
        if x0 >= x1 or y0 >= y1:
            return
        gy, gx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        nx, ny = (gx - cx) / r, (gy - cy) / r
        d2 = nx * nx + ny * ny
        region = sky[y0:y1, x0:x1]
        bg = region.copy()

        if ring:
            tilt = rng.uniform(-0.5, 0.5)
            k = rng.uniform(0.16, 0.32)
            ca, sa = math.cos(tilt), math.sin(tilt)
            xr = nx * ca + ny * sa
            yr = -nx * sa + ny * ca
            rr = np.sqrt(xr ** 2 + (yr / k) ** 2)
            prof = np.zeros_like(rr)
            prof = 0.22 * smoothstep(1.3, 1.4, rr) * (1 - smoothstep(1.95, 2.05, rr))
            for _ in range(7):
                c, w, o = rng.uniform(1.35, 2.05), rng.uniform(0.03, 0.16), rng.uniform(0.35, 0.9)
                prof = np.maximum(prof, o * np.exp(-((rr - c) / w) ** 2))
            gap = rng.uniform(1.6, 1.8)
            prof *= 1 - 0.85 * np.exp(-((rr - gap) / 0.025) ** 2)
            prof *= smoothstep(1.25, 1.35, rr) * (1 - smoothstep(2.05, 2.25, rr))
            ring_col = mix(base, pal.sun, 0.35)

            def draw_ring(sel):
                al = prof * sel
                region[:] = region * (1 - al[..., None]) + ring_col * al[..., None]
                mask[y0:y1, x0:x1] *= 1 - al
            draw_ring(yr < 0)

        inside = d2 < 1
        nz = np.sqrt(np.clip(1 - d2, 0, 1))
        alpha = np.clip((1 - np.sqrt(d2)) * r, 0, 1)
        lam = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
        shade = 0.06 + 0.94 * lam ** 0.85
        colr = np.broadcast_to(base, nx.shape + (3,)).copy()
        if bands:
            tex = noise2d(rng, y1 - y0, x1 - x0, 6)
            v = ny + 0.08 * (tex - 0.5) * 4
            pat = 0.5 + 0.5 * np.sin(v * rng.uniform(9, 16) + rng.uniform(0, 6) + 1.5 * np.sin(v * 3))
            pat2 = 0.5 + 0.5 * np.sin(v * rng.uniform(25, 40) + rng.uniform(0, 6))
            cb = mix(base, pal.sky[1], 0.55)
            colr = mix(colr, cb, (pat * 0.75 + pat2 * 0.25)[..., None] * 0.85)
        if craters:
            tex = noise2d(rng, y1 - y0, x1 - x0, 5, octaves=4)
            maria = smoothstep(0.5, 0.62, noise2d(rng, y1 - y0, x1 - x0, 3, octaves=2))
            colr = colr * (0.78 + 0.32 * tex[..., None]) * (1 - 0.22 * maria[..., None])
            for _ in range(int(min(60, 6 + r / 6))):
                a_, d_ = rng.uniform(0, 2 * math.pi), math.sqrt(rng.random()) * 0.92
                ccx, ccy = math.cos(a_) * d_, math.sin(a_) * d_
                cr = r * 0.25 * rng.power(0.15) + 1.0
                dist = np.sqrt((nx - ccx) ** 2 + (ny - ccy) ** 2) * r / cr
                floor = np.clip(1 - dist, 0, 1) > 0
                rim = np.exp(-((dist - 1) / 0.12) ** 2)
                side = np.clip(((nx - ccx) * L[0] + (ny - ccy) * L[1]) * r / cr, -1, 1)
                colr = colr * (1 - 0.14 * floor[..., None]) + (rim * side * 0.08)[..., None]
        lit = colr * shade[..., None]
        lit = mix(lit, bg, haze_amt + (1 - haze_amt) * 0.55 * (1 - lam[..., None]) * 0.5)
        rim = np.exp(-(1 - np.sqrt(np.clip(d2, 0, 1))) * 9) * inside * (0.25 + 0.75 * lam)
        lit += mix(pal.haze, pal.sun, 0.5) * rim[..., None] * 0.35
        region[:] = region * (1 - alpha[..., None]) + lit * alpha[..., None]
        mask[y0:y1, x0:x1] *= 1 - alpha
        if ring:
            draw_ring(yr >= 0)

    # sun disks
    for sx, sy, rad in suns:
        x0, x1 = int(max(sx - rad * 2, 0)), int(min(sx + rad * 2, sw))
        y0, y1 = int(max(sy - rad * 2, 0)), int(min(sy + rad * 2, H))
        if x0 < x1 and y0 < y1:
            gy, gx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
            al = np.clip(rad - np.sqrt((gx - sx) ** 2 + (gy - sy) ** 2) + 0.5, 0, 1)
            sky[y0:y1, x0:x1] = mix(sky[y0:y1, x0:x1], pal.sun * 1.05, al[..., None])
            mask[y0:y1, x0:x1] *= 1 - al

    br = seeds.rng("bodies")
    geo = {"islands": [], "wave_curls": [], "tallest_tree": None, "big_moon": None}
    if spec.giant:
        r = spec.giant_size * W
        gx_ = (spec.giant_x if spec.giant_x is not None else br.choice([br.uniform(0.12, 0.35), br.uniform(0.65, 0.88)])) * W
        gy_ = (spec.giant_y if spec.giant_y is not None else br.uniform(0.12, 0.32)) * H
        base = mix(pal.accent, pal.sky[1], br.uniform(0.0, 0.45))
        body(gx_, gy_, r, base, bands=True, ring=spec.ring, haze_amt=0.12, tag="giant")
    if spec.big_moon:
        r = 0.42 * W
        mx_, my_ = br.uniform(0.35, 0.65) * W, hy - r * br.uniform(0.25, 0.55)
        geo["big_moon"] = (mx_, my_, r)
        body(mx_, my_, r, mix(pal.accent, pal.haze, 0.25), craters=True, haze_amt=0.28, tag="bigmoon")
    for k in range(spec.moons):
        r = br.uniform(0.012, 0.045) * W
        body(br.uniform(0.08, 0.92) * W, br.uniform(0.08, 0.6) * hy, r, mix(pal.accent, pal.haze, br.uniform(0, 0.5)),
             craters=True, haze_amt=0.1, tag=("moon", k))

    # stars
    dark = 1 - lum(pal.sky[0])
    density = spec.stars if spec.stars is not None else max(0.0, (dark - 0.55) / 0.45)
    groups = [np.zeros((H, sw), np.float32) for _ in range(3)]
    if density > 0:
        rs = seeds.rng("stars")
        n = int(1600 * density * sw / W * H / 1350)
        px = rs.uniform(0, sw, n)
        py = rs.uniform(0, min(hy, H - 1), n)
        bright = rs.power(0.35, n) * 0.9 + 0.1
        grp = rs.integers(0, 3, n)
        fade = 1 - smoothstep(0.35, 1.0, py / hy)
        for x_, y_, b_, g_, f_ in zip(px, py, bright, grp, fade):
            ix, iy = int(x_), int(y_)
            if b_ > 0.75:
                glow_patch = groups[g_]
                rr = 2
                y0, y1, x0, x1 = max(iy - rr, 0), min(iy + rr + 1, H), max(ix - rr, 0), min(ix + rr + 1, sw)
                gy, gx = np.mgrid[y0:y1, x0:x1]
                glow_patch[y0:y1, x0:x1] += b_ * f_ * np.exp(-((gx - x_) ** 2 + (gy - y_) ** 2) / 1.2)
            elif 0 <= iy < H and 0 <= ix < sw:
                groups[g_][iy, ix] += b_ * f_ * 0.8
        groups = [g * mask for g in groups]

    # aurora: two variants cross-faded in motion
    aur = []
    if spec.aurora:
        u = np.arange(sw, dtype=np.float64) / W
        green, pink = hexc("#5dffb0"), hexc("#d56bff")
        for v in range(2):
            img = np.zeros((H, sw, 3), np.float32)
            for c in range(2):
                tag = ("aur", c)
                base_y = hy - H * (0.2 + 0.14 * c + 0.1 * fbm(seeds, tag, u, 3, 1.4, 0.5))
                rays = np.clip(0.55 + 1.3 * fbm(seeds, (tag, "rays", v), u, 3, 26, 0.55), 0, 1) ** 2
                rays *= np.clip(0.5 + 1.2 * fbm(seeds, (tag, "env"), u, 2, 2.2, 0.5), 0, 1)
                dy = (base_y[None, :] - yy) / H
                env = np.where(dy > 0, np.exp(-dy / (0.13 + 0.05 * c)), np.exp(dy / 0.008))
                inten = (env * rays[None, :]).astype(np.float32) * (0.75 - 0.25 * c)
                tint = mix(green, pink, np.clip(dy / 0.28, 0, 1)[..., None])
                img += tint * inten[..., None]
            aur.append(img * mask[..., None])

    scene = Scene(W, H, spec, pal, sky, aur, groups, mask, sun_xy=[(s[0], s[1]) for s in suns])

    # ---- terrain ----------------------------------------------------------
    n_layers = max(1, spec.layers)
    snow_col = hexc("#e9eef8") * 0.92 + pal.haze * 0.08
    near_col = mix(snow_col, pal.haze, 0.25) if spec.snow else pal.land
    tree_dark = mix(pal.land, pal.sky[0], 0.3)
    ridges = []
    for i in range(n_layers):
        t = i / (n_layers - 1) if n_layers > 1 else 1.0
        speed = 0.06 + 0.7 * t ** 1.5
        w = width(speed)
        u = np.arange(w, dtype=np.float64) / W
        tag = f"ridge{i}"
        h = _ridge(spec.terrain, seeds, tag, u, seeds.rng(tag))
        if spec.water:
            base = np.full(w, hy)
            amp = H * mix(0.2, 0.07, t) * spec.relief
            if spec.terrain in ("mesas", "spires"):
                amp *= 1.1
        else:
            base = np.full(w, hy + (H - hy) * 0.88 * t ** 1.25)
            amp = H * mix(0.21, 0.12, t) * spec.relief
        ridge_y = base - amp * h
        fog = (1 - t) ** 1.15 * 0.86 if n_layers > 1 else 0.0
        if spec.water:
            fog = 0.3 + 0.6 * (1 - t)
        lc = mix(near_col, mix(pal.haze, pal.sky[2], 0.3), fog)
        gy = np.arange(H, dtype=np.float32)[:, None]
        A = np.clip(gy - ridge_y[None, :] + 0.5, 0, 1).astype(np.float32)
        if spec.water:
            A *= (gy < hy + 0.5)
        depth = (gy - ridge_y[None, :]) / H
        mf = spec.mist * smoothstep(0.0, 0.2 + 0.1 * t, depth) * (0.85 - 0.45 * t)
        if spec.snow:
            mf *= 0.6
        cpix = mix(lc, mix(pal.haze, pal.sky[2], 0.5), mf[..., None]).astype(np.float32)
        P = cpix * A[..., None]
        layer = Layer(P, A, speed)
        ridges.append((layer, ridge_y, t, lc))
        scene.layers.append(layer)

        # mist band drifting in front of this layer
        if spec.mist > 0.2 and i < n_layers - 1:
            mw = width(speed + 0.04)
            mu = np.arange(mw, dtype=np.float64) / W
            ny_ = (base[0] if not spec.water else hy) - amp * 0.15 + 0.02 * H * fbm(seeds, (tag, "mist"), mu, 3, 2, 0.5)
            th = H * (0.018 + 0.02 * (1 - t))
            ma = np.exp(-((gy - ny_[None, :]) / th) ** 2) * np.clip(0.55 + 0.9 * fbm(seeds, (tag, "mista"), mu, 4, 3, 0.55), 0, 1)
            ma = (ma * spec.mist * (0.25 if spec.water else 0.7)).astype(np.float32)
            mcol = mix(pal.haze, pal.sky[2], 0.5)
            scene.layers.append(Layer((mcol * ma[..., None]).astype(np.float32), ma, speed + 0.04))

    # floating islands sit between the far layers
    if spec.islands:
        ri = seeds.rng("islands")
        speed = 0.18
        w = width(speed)
        P = np.zeros((H, w, 3), np.float32)
        A = np.zeros((H, w), np.float32)
        E = np.zeros((H, w, 3), np.float32)
        col = mix(pal.land, pal.haze, 0.45)
        for k in range(spec.islands):
            iw = W * ri.uniform(0.12, 0.26) * (1.0 if k else 1.35)
            cx = W * (0.2 + 0.6 * (k + ri.uniform(-0.25, 0.25)) / max(spec.islands - 1, 1)) if spec.islands > 1 else W * 0.5
            cy = hy * ri.uniform(0.35, 0.8)
            depth = iw * ri.uniform(0.55, 0.95)
            top = [(cx - iw / 2 + iw * f, cy - ri.uniform(0, iw * 0.04)) for f in np.linspace(0, 1, 9)]
            bot = []
            for f in np.linspace(1, 0, 9)[1:-1]:
                bx = cx - iw / 2 + iw * f
                prof = 1 - abs(f - 0.5) * 2
                bot.append((bx + ri.uniform(-0.03, 0.03) * iw, cy + depth * prof ** 0.7 * ri.uniform(0.6, 1.0)))
            stamp(P, A, [("poly", top + bot)], col)
            geo["islands"].append((cx, cy, depth, iw))
            for _ in range(int(ri.integers(2, 6))):
                tx = cx + ri.uniform(-0.4, 0.4) * iw
                stamp(P, A, pine(tx, cy + 2, iw * ri.uniform(0.15, 0.3), ri), col)
            for _ in range(int(ri.integers(3, 7))):
                vx = cx + ri.uniform(-0.3, 0.3) * iw
                vy = cy + depth * 0.3 * ri.uniform(0.5, 1)
                vl = depth * ri.uniform(0.4, 1.0)
                stamp(P, A, [("line", ([(vx, vy), (vx + ri.uniform(-4, 4), vy + vl)], 1.4))], col, value=0.8)
        scene.layers.insert(min(2, len(scene.layers)), Layer(P, A, speed, E))

    # glass waves rise from the second layer
    if spec.glass_waves and len(ridges) >= 2:
        layer, ridge_y, t, lc = ridges[1]
        rg = seeds.rng("waves")
        glass = mix(hexc("#9fe8d0"), pal.haze, 0.35)
        hi = mix(glass, pal.sun, 0.6)
        P2 = np.zeros_like(layer.P)
        A2 = np.zeros_like(layer.A)
        for k in range(3):
            ww = W * rg.uniform(0.32, 0.5)
            wh = H * rg.uniform(0.2, 0.32)
            x0 = W * (k * 0.42 - 0.1) + rg.uniform(-0.05, 0.05) * W
            yb = float(ridge_y[int(np.clip(x0 + ww / 2, 0, len(ridge_y) - 1))]) + H * 0.03
            pts = catmull([(x0 + ww * px, yb - wh * py) for px, py in WAVE], 6)
            stamp(P2, A2, [("poly", pts)], glass, value=0.82)
            geo["wave_curls"].append((x0 + ww * 0.88, yb))
            crest = pts[len(pts) // 4: int(len(pts) * 0.52)]
            stamp(P2, A2, [("line", (crest, 2.2))], hi, value=0.7)
        scene.layers.insert(scene.layers.index(layer), Layer(P2, A2, layer.speed))

    # ---- foreground objects ---------------------------------------------
    ro = seeds.rng("objects")
    near_layer, near_ridge, _, near_lc = ridges[-1]

    def ridge_at(r_, x):
        return float(r_[int(np.clip(x, 0, len(r_) - 1))])

    def local_peak(r_, lo, hi):
        lo, hi = int(lo), int(hi)
        seg = r_[lo:hi]
        return lo + int(np.argmin(seg))

    if spec.water and spec.shore != "none":
        speed = 1.0
        w = width(speed)
        u = np.arange(w, dtype=np.float64) / W
        side = spec.shore
        reach = ro.uniform(0.32, 0.48)
        if side == "left":
            ramp = smoothstep(reach, reach - 0.12, u)
        else:
            ramp = smoothstep(1 - reach, 1 - reach + 0.12, u)
        top = (H - hy) * ro.uniform(0.38, 0.55)
        bumps = 0.82 + 0.18 * (0.5 + fbm(seeds, "shore", u, 5, 7, 0.55))
        ridge_y = H + 4 - (top * bumps + H * 0.02) * ramp ** 0.6
        gy = np.arange(H, dtype=np.float32)[:, None]
        A = np.clip(gy - ridge_y[None, :] + 0.5, 0, 1).astype(np.float32) * (ramp[None, :] > 0.01)
        lc = near_col if not spec.snow else mix(snow_col, pal.haze, 0.5) * 0.85
        depth = (gy - ridge_y[None, :]) / H
        shade = mix(lc, lc * 0.55 + pal.land * 0.45, smoothstep(0, 0.3, depth)[..., None]) if spec.snow else np.broadcast_to(lc, depth.shape + (3,))
        P = (shade * A[..., None]).astype(np.float32)
        shore = Layer(P, A, speed, np.zeros((H, w, 3), np.float32), stage=1)
        scene.layers.append(shore)
        near_layer, near_ridge, near_lc = shore, ridge_y, lc
        if spec.lighthouse:
            lo_, hi_ = ((0.08, reach - 0.16) if side == "left" else (1 - reach + 0.16, 0.92))
            lx = local_peak(ridge_y, lo_ * W, hi_ * W)
            geo["lighthouse"] = lx
            gyl = ridge_at(ridge_y, lx) + 4
            th, bw = H * 0.13, W * 0.028
            top = gyl - th
            stamp(P, A, [("poly", [(lx - bw, gyl), (lx - bw * 0.62, top), (lx + bw * 0.62, top), (lx + bw, gyl)]),
                         ("poly", [(lx - bw * 0.9, top), (lx + bw * 0.9, top), (lx + bw * 0.9, top + 5), (lx - bw * 0.9, top + 5)]),
                         ("poly", [(lx - bw * 0.45, top - th * 0.1), (lx + bw * 0.45, top - th * 0.1), (lx + bw * 0.45, top), (lx - bw * 0.45, top)]),
                         ("poly", [(lx - bw * 0.6, top - th * 0.1), (lx, top - th * 0.2), (lx + bw * 0.6, top - th * 0.1)])], lc)
            lamp_y = top - th * 0.05
            glow(shore.E, lx, lamp_y, 7, pal.light, 1.4)
            beam = np.zeros_like(A)
            beamP = np.zeros_like(P)
            dirn = 1 if side == "left" else -1
            reach_px = W * 0.75
            stamp(beamP, beam, [("poly", [(lx, lamp_y - 3), (lx + dirn * reach_px, lamp_y - H * 0.06), (lx + dirn * reach_px, lamp_y + H * 0.04), (lx, lamp_y + 3)])], np.ones(3))
            gx = np.arange(beam.shape[1], dtype=np.float32)[None, :]
            fall = np.clip(1 - np.abs(gx - lx) / reach_px, 0, 1) ** 1.6
            shore.E += (beam * fall * 0.22)[..., None] * pal.light
            shore.pulse = 0.25

    if spec.trees == "pines":
        for layer, r_, t, lc in ridges[-3:]:
            n = int(ro.integers(6, 22) * (0.6 + t))
            colr = tree_dark if spec.snow else lc
            for _ in range(n):
                x = ro.uniform(0, layer.A.shape[1])
                h = H * ro.uniform(0.02, 0.055) * (0.5 + t)
                stamp(layer.P, layer.A, pine(x, ridge_at(r_, x) + h * 0.15, h, ro), colr)
    elif spec.trees == "giant":
        for layer, r_, t, lc in ridges[-3:]:
            colr = tree_dark if spec.snow else lc
            for _ in range(int(ro.integers(3, 7))):
                x = ro.uniform(0, layer.A.shape[1])
                h = H * ro.uniform(0.35, 0.75) * (0.55 + 0.45 * t)
                stamp(layer.P, layer.A, pine(x, ridge_at(r_, x) + 30, h, ro), colr)
                best = geo["tallest_tree"]
                if W * 0.15 < x < W * 0.85 and (best is None or h > best[3] or best[0] is not layer):
                    geo["tallest_tree"] = (layer, x, ridge_at(r_, x) + 30 - h, h)
    elif spec.trees == "lone":
        x = W * ro.choice([ro.uniform(0.18, 0.35), ro.uniform(0.65, 0.82)])
        x = local_peak(near_ridge, max(x - W * 0.1, 0), min(x + W * 0.1, len(near_ridge) - 1))
        h = H * ro.uniform(0.14, 0.22)
        stamp(near_layer.P, near_layer.A, round_tree(x, ridge_at(near_ridge, x) + 6, h, ro), tree_dark if spec.snow else near_lc)

    if spec.house:
        layer, r_, t, lc = ridges[-1] if not spec.water else (near_layer, near_ridge, 1.0, near_lc)
        hx = local_peak(r_, W * 0.55, W * 0.9) if ro.random() < 0.5 else local_peak(r_, W * 0.1, W * 0.45)
        hy_ = ridge_at(r_, hx) + 6
        hs = H * 0.028
        colr = tree_dark if spec.snow else lc
        stamp(layer.P, layer.A, [("poly", [(hx - hs, hy_), (hx - hs, hy_ - hs), (hx, hy_ - hs * 1.7), (hx + hs, hy_ - hs), (hx + hs, hy_)]),
                                 ("poly", [(hx + hs * 0.4, hy_ - hs * 1.3), (hx + hs * 0.65, hy_ - hs * 1.3), (hx + hs * 0.65, hy_ - hs * 1.75), (hx + hs * 0.4, hy_ - hs * 1.75)])], colr)
        if layer.E is None:
            layer.E = np.zeros_like(layer.P)
        wP, wA = np.zeros_like(layer.P), np.zeros_like(layer.A)
        stamp(wP, wA, [("poly", [(hx - hs * 0.45, hy_ - hs * 0.35), (hx - hs * 0.05, hy_ - hs * 0.35), (hx - hs * 0.05, hy_ - hs * 0.75), (hx - hs * 0.45, hy_ - hs * 0.75)])], np.ones(3))
        layer.E += wA[..., None] * pal.light * 1.1
        glow(layer.E, hx - hs * 0.25, hy_ - hs * 0.55, 6, pal.light, 0.5)

    if spec.figure:
        layer, r_, t, lc = (near_layer, near_ridge, 1.0, near_lc) if spec.water and spec.shore != "none" else ridges[-1]
        if spec.water and spec.shore == "none":
            layer, r_, t, lc = ridges[-1]
        lo, hi = (W * 0.25, W * 0.48) if ro.random() < 0.5 else (W * 0.52, W * 0.75)
        if spec.water and spec.shore == "left":
            lo, hi = W * 0.25, W * 0.4
        if spec.water and spec.shore == "right":
            lo, hi = W * 0.6, W * 0.75
        fx = local_peak(r_, lo, hi)
        fh = H * 0.032
        stamp(layer.P, layer.A, person(fx, ridge_at(r_, fx) + 3, fh), tree_dark if spec.snow else lc)

    if spec.lanterns:
        rl = seeds.rng("lanterns")
        hosts = [(near_layer, near_ridge, 1.0)] + [(l_, r_, t_) for l_, r_, t_, _ in ridges[-2:]]
        orange = hexc("#ff8a2a")
        for k in range(spec.lanterns):
            layer, r_, t = hosts[k % len(hosts)]
            if layer.E is None:
                layer.E = np.zeros_like(layer.P)
            w = layer.A.shape[1]
            x = rl.uniform(0.05, 0.95) * min(w, W * 1.2)
            sz = H * rl.uniform(0.012, 0.028) * (0.45 + 0.55 * t)
            gy_ = ridge_at(r_, x) + sz * 0.15
            body_ = [("ellipse", (x - sz * 1.15, gy_ - sz * 1.5, x + sz * 1.15, gy_)),
                     ("ellipse", (x - sz * 0.6, gy_ - sz * 1.55, x + sz * 0.6, gy_ + sz * 0.05)),
                     ("poly", [(x - sz * 0.1, gy_ - sz * 1.45), (x + sz * 0.05, gy_ - sz * 1.85), (x + sz * 0.18, gy_ - sz * 1.8), (x + sz * 0.1, gy_ - sz * 1.45)])]
            lp, la = np.zeros_like(layer.P), np.zeros_like(layer.A)
            stamp(lp, la, body_, orange)
            layer.P = layer.P * (1 - la[..., None]) + lp * 0.55
            layer.A = layer.A * (1 - la) + la
            layer.E += lp * 0.35
            glow(layer.E, x, gy_ - sz * 0.75, sz * 0.9, pal.light, 0.22)

    if spec.moths:
        rm = seeds.rng("moths")
        speed = 0.22
        w = width(speed)
        P = np.zeros((H, w, 3), np.float32)
        A = np.zeros((H, w), np.float32)
        E = np.zeros((H, w, 3), np.float32)
        col = mix(pal.land, pal.sky[1], 0.35)
        for k in range(spec.moths):
            mx = W * (0.1 + 0.8 * (k + rm.uniform(0.1, 0.9)) / spec.moths)
            my = hy * rm.uniform(0.2, 0.75)
            sz = W * rm.uniform(0.025, 0.06)
            stamp(P, A, moth(mx, my, sz), col)
            glow(E, mx, my + sz * 1.2, sz * 0.9, pal.accent, 0.25)
        scene.layers.insert(min(3, len(scene.layers)), Layer(P, A, speed, E))

    if spec.glow_rims:
        orange = hexc("#ff7a2a")
        for layer, r_, t, _ in ridges[-3:]:
            if layer.E is None:
                layer.E = np.zeros_like(layer.P)
            gy = np.arange(H, dtype=np.float32)[:, None]
            d = gy - r_[None, :]
            band = np.exp(-(d / (H * 0.007)) ** 2) * (d > -1) * (0.35 + 0.35 * t)
            layer.E += (band * layer.A)[..., None].astype(np.float32) * orange

    # the planet's visual joke and the cartographer
    scene.focus, scene.marks = (0.5, 0.62), {}
    if spec.gag or spec.cartographer or spec.sign or spec.crowd or spec.daisies or spec.lamp:
        from . import props
        globe = None
        if spec.gag == "tiny_planet":
            globe = Layer(np.zeros((H, width(1.0), 3), np.float32), np.zeros((H, width(1.0)), np.float32), 1.0,
                          np.zeros((H, width(1.0), 3), np.float32), stage=1)
            scene.layers.append(globe)
        ctx = props.make_ctx(
            W=W, H=H, spec=spec, pal=pal, geo=geo, globe=globe,
            near_layer=near_layer, near_ridge=near_ridge, ridge_at=ridge_at,
            far_layer=ridges[0][0], far_ridge=ridges[0][1], mid_layer=ridges[len(ridges) // 2][0],
            dark=tree_dark if spec.snow else near_lc, light=props.LIGHT, land=pal.land, ground=near_lc, stage_y=None,
            spot=hexc(spec.spot) if spec.spot else hexc("#c8452f"),
            sky_P=scene.sky, sky_A=np.ones(scene.sky.shape[:2], np.float32),
            rng=lambda tag: seeds.rng("gag", tag), focus=(0.5, 0.62), marks={})
        if spec.gag:
            props.GAGS[spec.gag](ctx)
        props.extras(ctx)
        if spec.cartographer:
            props.cartographer(ctx, avoid_x=ctx.focus[0] * W)
        scene.focus, scene.marks = ctx.focus, ctx.marks

    # particles
    if spec.particles != "none":
        rp = seeds.rng("particles")
        E = np.zeros((H, W, 3), np.float32)
        if spec.particles in ("rain_up", "rain"):
            up = spec.particles == "rain_up"
            col = mix(pal.sun, pal.haze, 0.3)
            for _ in range(500):
                x, y0 = rp.uniform(0, W), rp.uniform(0, H)
                ln = rp.uniform(0.015, 0.05) * H
                ys = np.arange(int(y0), int(min(y0 + ln, H)))
                if len(ys) == 0:
                    continue
                f = np.linspace(1, 0, len(ys)) ** 1.5 * rp.uniform(0.08, 0.3)
                E[ys, int(x)] += (f if up else f[::-1])[:, None] * col
            drift = (0.0, -0.35) if up else (-0.02, 0.6)
        elif spec.particles == "embers":
            for _ in range(160):
                glow(E, rp.uniform(0, W), rp.uniform(0, H), rp.uniform(1.0, 2.6), mix(pal.light, hexc("#ff5a2a"), rp.random()), rp.uniform(0.3, 1.0))
            drift = (0.01, -0.05)
        else:
            for _ in range(450):
                glow(E, rp.uniform(0, W), rp.uniform(0, H), rp.uniform(0.7, 2.2), hexc("#ffffff"), rp.uniform(0.15, 0.6))
            drift = (0.01, -0.05) if spec.particles == "snow_up" else (0.01, 0.06)
        scene.layers.append(Layer(np.zeros_like(E), np.zeros((H, W), np.float32), 0.0, E, stage=1, drift=drift))

    if spec.water:
        scene.water_y = int(hy)
    return scene


# --------------------------------------------------------------------------
# compositing

def _rows(arr) -> tuple[int, int]:
    """Row span holding any non-zero content."""
    m = np.abs(arr).reshape(arr.shape[0], -1).max(axis=1) > 1e-4
    idx = np.flatnonzero(m)
    return (int(idx[0]), int(idx[-1]) + 1) if len(idx) else (0, 0)


def frame(scene: Scene, t: float = 0.0, pan: float = 0.0, fps_t: float = 0.0, grain: float = 0.022,
          grain_seed: int | None = None, bloom_thr: float | None = None) -> np.ndarray:
    """Flatten the scene to an (H, W, 3) float image.

    t: 0..1 progress through the pan; fps_t: seconds (for twinkle/drift).
    """
    W, H = scene.W, scene.H

    def crop(arr, speed, r0=0, r1=None):
        off = pan * speed * t
        i = int(math.floor(off))
        f = off - i
        a = arr[r0:r1, i:i + W]
        if f < 1e-3:
            return a
        b = arr[r0:r1, i + 1:i + 1 + W]
        return a + (b - a) * f

    out = crop(scene.sky, scene.sky_speed).astype(np.float32).copy()
    if scene.aurora:
        k = 0.5 + 0.5 * math.sin(fps_t * 0.9)
        out += crop(scene.aurora[0], scene.sky_speed) * (1 - k) + crop(scene.aurora[1], scene.sky_speed) * k
    star_col = np.array([1.0, 0.97, 0.92], np.float32)
    for g, grp in enumerate(scene.stars):
        if not hasattr(scene, "_star_rows"):
            scene._star_rows = {}
        r0, r1 = scene._star_rows.setdefault(g, _rows(grp))
        if r1 > r0:
            tw = 0.75 + 0.25 * math.sin(fps_t * (2.1 + g * 0.7) + g * 2.1)
            out[r0:r1] += crop(grp, scene.sky_speed, r0, r1)[..., None] * (star_col * tw)

    def blend(layer):
        if layer.drift != (0.0, 0.0):
            dx = int(layer.drift[0] * W * fps_t) % W
            dy = int(layer.drift[1] * H * fps_t) % H
            out[:] += np.roll(layer.E, (dy, dx), axis=(0, 1))
            return
        if not hasattr(layer, "rows"):
            r0, r1 = _rows(layer.A)
            if layer.E is not None:
                e0, e1 = _rows(layer.E)
                r0, r1 = (min(r0, e0), max(r1, e1)) if e1 > e0 else (r0, r1)
            layer.rows = (r0, r1)
        r0, r1 = layer.rows
        if r1 <= r0:
            return
        A = crop(layer.A, layer.speed, r0, r1)
        region = out[r0:r1]
        region *= 1 - A[..., None]
        region += crop(layer.P, layer.speed, r0, r1)
        if layer.E is not None:
            k = 1.0 if not layer.pulse else 0.55 + 0.45 * math.cos(2 * math.pi * layer.pulse * fps_t)
            region += crop(layer.E, layer.speed, r0, r1) * k

    for layer in scene.layers:
        if layer.stage == 0:
            blend(layer)
    if scene.water_y is not None:
        out = _water(scene, out, fps_t)
    for layer in scene.layers:
        if layer.stage == 1:
            blend(layer)
    return _post(out, grain, grain_seed, bloom_thr)


def bloom_threshold(img: np.ndarray) -> float:
    return max(0.72, float(np.percentile(img.max(axis=2), 88)))


def _water(scene: Scene, img: np.ndarray, ts: float) -> np.ndarray:
    W, H, wy = scene.W, scene.H, scene.water_y
    pal = scene.pal
    rows = np.arange(wy, H)
    depth = (rows - wy) / max(H - wy, 1)
    src = np.clip(2 * wy - rows - 1, 0, H - 1)
    amp = 1.5 + 14 * depth ** 1.2
    dx = amp * np.sin(rows * 0.21 + ts * 2.2) + 0.6 * amp * np.sin(rows * 0.057 - ts * 1.3)
    xi = (np.arange(W)[None, :] + dx[:, None]).astype(int) % W
    refl = img[src[:, None], xi]
    k = 9
    cs = np.cumsum(np.pad(refl, ((0, 0), (k, k), (0, 0)), mode="edge"), axis=1)
    refl = (cs[:, 2 * k:] - cs[:, :-2 * k]) / (2 * k)
    refl = refl[:, :W] if refl.shape[1] >= W else np.pad(refl, ((0, 0), (0, W - refl.shape[1]), (0, 0)), mode="edge")
    kv = 14  # vertical smear turns reflected discs into glitter columns
    cs = np.cumsum(np.pad(refl, ((kv, kv), (0, 0), (0, 0)), mode="edge"), axis=0)
    refl = (cs[2 * kv:] - cs[:-2 * kv]) / (2 * kv)
    refl = refl[:len(rows)]
    bright = np.clip((refl.max(axis=2, keepdims=True) - 0.6) / 0.4, 0, 1)
    f = (0.22 + 0.5 * depth ** 0.7)[:, None, None] * (1 - 0.6 * bright)
    refl = mix(refl * 0.85, pal.water, f)
    rng = np.random.default_rng(int(ts * 4) + 7)
    for sx, sy in scene.sun_xy:
        n = 260
        ry = rng.uniform(0, 1, n) ** 1.6 * (H - wy)
        rx = sx + rng.normal(0, 1, n) * (W * 0.012 + ry * 0.12)
        ln = rng.uniform(6, 40, n) * (0.4 + ry / (H - wy))
        for x_, y_, l_ in zip(rx, ry, ln):
            yi = int(y_)
            x0, x1 = int(max(x_ - l_ / 2, 0)), int(min(x_ + l_ / 2, W))
            if x0 < x1 and yi < len(rows):
                refl[yi, x0:x1] += pal.sun * 0.35 * (1 - yi / len(rows)) ** 0.5
    img = img.copy()
    img[wy:] = refl
    img[wy:wy + 2] = mix(img[wy:wy + 2], pal.haze, 0.2)
    return img


@lru_cache(maxsize=4)
def _vignette(H, W):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r2 = ((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2
    return (1 - 0.22 * r2)[..., None]


@lru_cache(maxsize=8)
def _grain(H, W, grain, seed):
    return np.random.default_rng(seed).normal(0, grain, (H, W, 1)).astype(np.float32)


def _post(img: np.ndarray, grain: float, grain_seed, thr: float | None = None) -> np.ndarray:
    H, W = img.shape[:2]
    # bloom
    lm = img.max(axis=2)
    thr = bloom_threshold(img) if thr is None else thr
    l = np.clip((lm - thr) / max(1.0 - thr, 0.08), 0, 1)
    small = Image.fromarray((np.clip(img * l[..., None], 0, 1) * 255).astype(np.uint8)).resize((W // 6, H // 6), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(10))
    bloom = np.asarray(small.resize((W, H), Image.BILINEAR), np.float32) / 255
    img = img + bloom * 0.22
    img = img * _vignette(H, W)
    # lift the mid-tones and add a little contrast so prints hold up on a phone screen
    img = 0.5 + (np.clip(img, 0, 1) ** 0.88 - 0.5) * 1.07
    if grain:
        img = img + _grain(H, W, grain, grain_seed)
    return np.clip(img, 0, 1)


# --------------------------------------------------------------------------
# print finish: a limited ink palette with stochastic screening and paper
# texture, so frames read like a screen print rather than a smooth render.

LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)
PAPER = np.array([243, 236, 222], np.float32) / 255


COAT = hexc("#e9b434")   # the cartographer's yellow coat, always its own ink


def spec_inks(spec: Spec) -> list:
    """Inks a print must keep exactly: the cartographer's coat and any gag spot colour."""
    inks = [COAT] if spec.cartographer or spec.gag == "tiny_planet" else []
    if spec.spot or spec.gag == "umbrella_feet":
        inks.append(hexc(spec.spot or "#c8452f"))
    return inks


def ink_palette(img: np.ndarray, k: int = 8, extra=()) -> np.ndarray:
    """k-means inks for an image, plus a highlight ink (sun cores, stars), a spot colour and any extra inks."""
    px = np.ascontiguousarray(img[::5, ::5].reshape(-1, 3), np.float32)
    order = np.argsort(px @ LUMA)
    cent = px[order[np.linspace(0, len(px) - 1, k).astype(int)]].copy()
    sq = (px ** 2).sum(1)[:, None]
    for _ in range(14):
        a = (sq - 2 * px @ cent.T + (cent ** 2).sum(1)[None]).argmin(1)
        for j in range(k):
            m = a == j
            if m.any():
                cent[j] = px[m].mean(0)
    sat = px.max(1) - px.min(1)
    spot = px[np.argsort(sat * (0.3 + px @ LUMA))[int(len(px) * 0.997)]]   # a spot colour, as riso prints have
    return np.vstack([cent, px[order[int(len(px) * 0.999)]][None], spot[None]] + [np.asarray(e, np.float32)[None] for e in extra])


@lru_cache(maxsize=4)
def _screen(H, W, seed):
    """Static screening noise (fine + 2px clusters) and paper texture."""
    rng = np.random.default_rng(seed)
    fine = rng.normal(0, 1, (H, W)).astype(np.float32)
    fine -= sum(np.roll(fine, (dy, dx), (0, 1)) for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9 * 0.7
    coarse = np.repeat(np.repeat(rng.normal(0, 1, ((H + 1) // 2, (W + 1) // 2)), 2, 0), 2, 1)[:H, :W]
    noise = (0.55 * fine + 0.65 * coarse).astype(np.float32)[..., None]
    low = Image.fromarray((rng.random((H // 40 + 2, W // 40 + 2)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    fiber = rng.random((H, W)).astype(np.float32)
    fiber = (fiber + np.roll(fiber, 1, 1) + np.roll(fiber, 1, 0)) / 3
    paper = (0.96 + 0.06 * np.asarray(low, np.float32) / 255) * (0.975 + 0.05 * fiber)
    speck = rng.random((H, W)) > 0.9985
    return noise, paper[..., None].astype(np.float32), speck[..., None]


def print_finish(img: np.ndarray, inks: np.ndarray, seed: int = 1, dither: float = 0.05) -> np.ndarray:
    H, W, _ = img.shape
    noise, paper, speck = _screen(H, W, seed)
    x = (img + noise * dither).reshape(-1, 3)
    idx = (-2 * x @ inks.T + (inks ** 2).sum(1)[None]).argmin(1)
    out = inks[idx].reshape(H, W, 3)
    out = (out * 0.93 + PAPER * 0.07) * paper
    out = np.where(speck, out * 0.5 + PAPER * 0.5, out)
    return np.clip(out, 0, 1)


def to_image(img: np.ndarray) -> Image.Image:
    return Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))


def render_raw(spec: Spec, seed: int, W=1080, H=1350) -> np.ndarray:
    """Flattened scene before the print finish (float RGB)."""
    return frame(build(spec, seed, W, H), grain=0)


def printed(img: np.ndarray, inks: np.ndarray | None = None, seed: int = 1) -> Image.Image:
    return to_image(print_finish(img, ink_palette(img) if inks is None else inks, seed))


def render_still(spec: Spec, seed: int, W=1080, H=1350) -> Image.Image:
    return printed(render_raw(spec, seed, W, H))
