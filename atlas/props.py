"""Characters and visual gags.

Each planet's funniest detail is drawn into the nearest layer at a readable
size, so the picture carries the joke, not just the caption. Figures are posed
from a small skeleton (stand, walk, sit, lie, reach, cup) and every print hides
the cartographer: a figure in a yellow coat with a map.
"""
from __future__ import annotations

import math
from types import SimpleNamespace

import numpy as np

from .render import COAT as YELLOW
from .render import glow, hexc, mix, round_tree, stamp

LIGHT = hexc("#f1e9d8")

# joint positions in units of figure height: u to the right (facing), v up from the feet
POSES = {
    "stand": dict(head=(0, .915), neck=(0, .83), hip=(0, .5), le=(-.13, .66), lh=(-.15, .5), re=(.13, .66), rh=(.15, .5),
                  lk=(-.05, .25), lf=(-.07, 0), rk=(.05, .25), rf=(.07, 0)),
    "walk": dict(head=(.02, .915), neck=(.01, .83), hip=(0, .5), le=(-.1, .66), lh=(-.2, .55), re=(.12, .66), rh=(.2, .52),
                 lk=(-.1, .26), lf=(-.17, 0), rk=(.1, .26), rf=(.16, 0)),
    "reach": dict(head=(0, .915), neck=(0, .83), hip=(0, .5), le=(-.13, .66), lh=(-.15, .5), re=(.1, .98), rh=(.12, 1.14),
                  lk=(-.05, .25), lf=(-.07, 0), rk=(.05, .25), rf=(.07, 0)),
    "cup": dict(head=(0, .915), neck=(0, .83), hip=(0, .5), le=(.14, .7), lh=(.1, .9), re=(.16, .72), rh=(.12, .9),
                lk=(-.05, .25), lf=(-.07, 0), rk=(.05, .25), rf=(.07, 0)),
    "sit": dict(head=(-.06, .76), neck=(-.04, .67), hip=(0, .34), le=(.04, .5), lh=(.16, .38), re=(.06, .5), rh=(.18, .4),
                lk=(.26, .36), lf=(.26, 0), rk=(.28, .34), rf=(.3, 0)),
    "doze": dict(head=(.04, .66), neck=(-.03, .64), hip=(0, .34), le=(.05, .48), lh=(.18, .38), re=(.07, .47), rh=(.2, .39),
                 lk=(.26, .36), lf=(.26, 0), rk=(.28, .34), rf=(.3, 0)),
}


def _tf(x, y, h, facing, ang):
    ca, sa = math.cos(ang), math.sin(ang)

    def f(u, v):
        uu, vv = u * ca - v * sa, u * sa + v * ca
        return (x + facing * uu * h, y - vv * h)
    return f


def figure(x, y, h, pose="stand", facing=1, ang=0.0, coat=True):
    """Return (body shapes, coat shape, anchor points) for a posed figure with feet at (x, y)."""
    p = POSES[pose]
    T = _tf(x, y, h, facing, ang)
    leg, arm = h * 0.065, h * 0.05
    body = []
    for k, f in (("lk", "lf"), ("rk", "rf")):
        pts = [T(*p["hip"]), T(*p[k]), T(*p[f])]
        body.append(("line", (pts, leg)))
        fx, fy = pts[-1]
        body.append(("ellipse", (fx - leg * 0.7, fy - leg * 0.6, fx + leg * 0.9 * facing ** 2, fy + leg * 0.2)))
    nu, nv = p["neck"]
    hu, hv = p["hip"]
    for side, e, hd in ((-1, "le", "lh"), (1, "re", "rh")):
        pts = [T(nu + side * 0.08, nv - 0.03), T(*p[e]), T(*p[hd])]
        body.append(("line", (pts, arm)))
        for (jx, jy) in pts[1:]:
            body.append(("ellipse", (jx - arm / 2, jy - arm / 2, jx + arm / 2, jy + arm / 2)))
    hu2, hv2 = p["head"]
    cx, cy = T(hu2, hv2)
    r = h * 0.085
    body.append(("ellipse", (cx - r, cy - r, cx + r, cy + r)))
    hem = 0.2 if coat else 0.0
    coat_shape = ("poly", [T(nu - 0.1, nv), T(nu + 0.1, nv), T(hu + 0.12, hv - hem), T(hu - 0.12, hv - hem)])
    anchors = {k: T(*v) for k, v in p.items()}
    return body, coat_shape, anchors


def rotate(shapes, ax, ay, theta):
    """Rotate shapes about (ax, ay); ellipses keep their size and move their centre."""
    c, s = math.cos(theta), math.sin(theta)

    def R(pt):
        dx, dy = pt[0] - ax, pt[1] - ay
        return (ax + dx * c - dy * s, ay + dx * s + dy * c)
    out = []
    for kind, g in shapes:
        if kind == "poly":
            out.append(("poly", [R(q) for q in g]))
        elif kind == "line":
            out.append(("line", ([R(q) for q in g[0]], g[1])))
        else:
            mx, my = R(((g[0] + g[2]) / 2, (g[1] + g[3]) / 2))
            hw, hh = (g[2] - g[0]) / 2, (g[3] - g[1]) / 2
            out.append(("ellipse", (mx - hw, my - hh, mx + hw, my + hh)))
    return out


# --------------------------------------------------------------------------
# props (all anchored at the ground point (x, y), size s ~ figure height)

def chair(x, y, s, facing=1):
    f = facing
    return [("poly", [(x - .05 * s * f, y - .36 * s), (x + .36 * s * f, y - .36 * s), (x + .36 * s * f, y - .3 * s), (x - .05 * s * f, y - .3 * s)]),
            ("poly", [(x - .1 * s * f, y - .8 * s), (x - .02 * s * f, y - .8 * s), (x + .0 * s * f, y - .3 * s), (x - .08 * s * f, y - .3 * s)]),
            ("line", ([(x - .02 * s * f, y - .3 * s), (x - .04 * s * f, y)], s * .035)),
            ("line", ([(x + .32 * s * f, y - .3 * s), (x + .34 * s * f, y)], s * .035)),
            ("poly", [(x - .1 * s * f, y - .55 * s), (x + .36 * s * f, y - .48 * s), (x + .36 * s * f, y - .42 * s), (x - .1 * s * f, y - .47 * s)])]


def house(x, y, s, broken=False):
    w = s * 0.55
    if not broken:
        return [("poly", [(x - w, y), (x - w, y - s * .6), (x, y - s), (x + w, y - s * .6), (x + w, y)])]
    t = s * 0.05
    return [("line", ([(x - w, y), (x - w, y - s * .6), (x, y - s), (x + w, y - s * .6), (x + w, y)], t)),
            ("line", ([(x - w, y - s * .3), (x + w * .2, y - s * .3)], t)),
            ("poly", [(x + w * .2, y), (x + w, y), (x + w, y - s * .6), (x + w * .6, y - s * .78), (x + w * .2, y - s * .5)])]


def kettle(x, y, s):
    return [("ellipse", (x - s * .3, y - s * .45, x + s * .3, y)),
            ("poly", [(x + s * .22, y - s * .3), (x + s * .5, y - s * .5), (x + s * .52, y - s * .44), (x + s * .26, y - s * .18)]),
            ("line", ([(x - s * .22, y - s * .38), (x - s * .1, y - s * .62), (x + s * .1, y - s * .62), (x + s * .22, y - s * .38)], s * .05)),
            ("ellipse", (x - s * .05, y - s * .52, x + s * .05, y - s * .42))]


def umbrella_down(x, y, s):
    """An open umbrella with its canopy hanging below (x, y): for rain that falls up."""
    arc = [(x + s * .5 * math.cos(a), y + s * .08 + s * .35 * math.sin(a)) for a in np.linspace(0, math.pi, 13)]
    return [("poly", arc[::-1] + [(x + s * .5, y + s * .08)]), ("line", ([(x, y + s * .3), (x, y - s * .02)], s * .05))]


def cat(x, y, s, facing=1):
    """A cat sitting upright at (x, y), tail curled up behind it."""
    f = facing
    hx = x + s * .04 * f
    return [("ellipse", (x - s * .17, y - s * .5, x + s * .17, y)),
            ("ellipse", (hx - s * .13, y - s * .72, hx + s * .13, y - s * .47)),
            ("poly", [(hx - s * .125, y - s * .62), (hx - s * .1, y - s * .83), (hx - s * .02, y - s * .7)]),
            ("poly", [(hx + s * .02, y - s * .7), (hx + s * .1, y - s * .83), (hx + s * .125, y - s * .62)]),
            ("line", ([(x - s * .1 * f, y - s * .05), (x - s * .3 * f, y - s * .06), (x - s * .4 * f, y - s * .2),
                       (x - s * .38 * f, y - s * .38)], s * .065))]


def bench(x, y, s):
    return [("poly", [(x - s * .5, y - s * .28), (x + s * .5, y - s * .28), (x + s * .5, y - s * .22), (x - s * .5, y - s * .22)]),
            ("poly", [(x - s * .5, y - s * .5), (x + s * .5, y - s * .5), (x + s * .5, y - s * .44), (x - s * .5, y - s * .44)]),
            ("line", ([(x - s * .42, y - s * .22), (x - s * .42, y)], s * .05)), ("line", ([(x + s * .42, y - s * .22), (x + s * .42, y)], s * .05))]


def ghost(x, y, s):
    pts = [(x - s * .3, y)]
    for k in range(7):
        pts.append((x - s * .3 + s * .6 * (k + .5) / 7, y - s * (.06 if k % 2 else 0)))
    pts += [(x + s * .3, y), (x + s * .3, y - s * .55)] + [(x + s * .3 * math.cos(a), y - s * .55 - s * .3 * math.sin(a)) for a in np.linspace(0, math.pi, 9)] + [(x - s * .3, y - s * .55)]
    return [("poly", pts)], [("ellipse", (x - s * .14, y - s * .7, x - s * .05, y - s * .58)), ("ellipse", (x + s * .05, y - s * .7, x + s * .14, y - s * .58))]


def letter(x, y, s, ang=0.0):
    w, h = s * .36, s * .24
    shp = [("poly", [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)])]
    return rotate(shp, x, y, ang)


def folds(x, y, s, ang=0.0, kind="map"):
    """The lines that make a letter() read as paper: a map's folds or an envelope flap."""
    w, h = s * .36, s * .24
    t = max(1.2, s * .02)
    if kind == "map":
        shp = [("line", ([(x + k * w / 6, y - h / 2), (x + k * w / 6, y + h / 2)], t)) for k in (-1, 1)]
        shp.append(("line", ([(x - w * .32, y + h * .22), (x - w * .12, y - h * .05), (x + w * .1, y + h * .12), (x + w * .3, y - h * .2)], t * .8)))
    else:
        shp = [("line", ([(x - w / 2, y - h / 2), (x, y + h * .08), (x + w / 2, y - h / 2)], t))]
    return rotate(shp, x, y, ang)


def _paper(ctx, P, A, x, y, s, ang=0.0, kind="map", turn=None):
    """Stamp a map or letter with its folds; turn=(ax, ay, theta) rotates it with its owner."""
    sheet, marks = letter(x, y, s, ang), folds(x, y, s, ang, kind)
    if turn:
        sheet, marks = rotate(sheet, *turn), rotate(marks, *turn)
    stamp(P, A, sheet, LIGHT)
    stamp(P, A, marks, ctx.dark, 0.55)


def arc_line(cx, cy, r, a0, a1, width, n=24):
    return ("line", ([(cx + r * math.cos(a), cy + r * math.sin(a)) for a in np.linspace(a0, a1, n)], width))


def cloud(x, y, w):
    return [("ellipse", (x - w * .5, y - w * .12, x + w * .1, y + w * .08)), ("ellipse", (x - w * .25, y - w * .25, x + w * .2, y + w * .05)),
            ("ellipse", (x - w * .05, y - w * .18, x + w * .5, y + w * .08))]


# --------------------------------------------------------------------------
# gags

G = 0.075   # gag figure height as a fraction of the frame: readable on a phone


def _ink(ctx, layer, shapes, color, value=1.0):
    stamp(layer.P, layer.A, shapes, color, value)


def _person(ctx, layer, x, y, h, pose="stand", facing=1, ang=0.0, coat_color=None, color=None):
    body, coat, anchors = figure(x, y, h, pose, facing, ang)
    col = ctx.dark if color is None else color
    _ink(ctx, layer, body + [coat], col)
    if coat_color is not None:
        _ink(ctx, layer, [coat], coat_color)
    return anchors


def _ground(ctx, x):
    if ctx.stage_y is not None:
        return ctx.stage_y(x)
    return ctx.ridge_at(ctx.near_ridge, x) + 2


def _stage(ctx, y_frac, color=None):
    """A flat foreground ledge across the frame for gags that need room."""
    W, H = ctx.W, ctx.H
    y_frac = ctx.spec.stage or y_frac      # an entry can lift the ledge clear of Instagram's caption area
    rng = ctx.rng("stage")
    xs = np.linspace(-20, W * 3, 40)
    ys = H * y_frac + H * 0.006 * np.sin(xs / W * 9 + rng.uniform(0, 6))
    poly = list(zip(xs, ys)) + [(W * 3, H + 20), (-20, H + 20)]
    _ink(ctx, ctx.near_layer, [("poly", poly)], ctx.ground if color is None else color)
    ctx.stage_y = lambda x: float(np.interp(x, xs, ys)) + 2


def cartographer(ctx, avoid_x=None):
    """The narrator, in a yellow coat with a map, somewhere in every print."""
    if ctx.globe is not None:
        return
    W, H = ctx.W, ctx.H
    rng = ctx.rng("cartographer")
    for _ in range(12):
        x = W * rng.uniform(0.12, 0.88)
        if avoid_x is None or abs(x - avoid_x) > W * 0.22:
            break
    layer = ctx.near_layer
    y = _ground(ctx, x)
    h = H * 0.06
    a = _person(ctx, layer, x, y, h, "stand", rng.choice([-1, 1]), coat_color=YELLOW)
    hx, hy = a["rh"]
    _paper(ctx, layer.P, layer.A, hx, hy - h * .08, h * 1.1, 0.2)
    ctx.marks["cartographer"] = (x / W, (y - h / 2) / H)


def armchair(x, y, s, facing=1):
    """Side-on armchair standing at (x, y): high back, seat, a padded arm."""
    f = facing
    X = lambda u: x + u * s * f
    return [("poly", [(X(-.16), y - s * .82), (X(-.04), y - s * .86), (X(.02), y - s * .36), (X(-.1), y - s * .3)]),   # back
            ("poly", [(X(-.1), y - s * .42), (X(.42), y - s * .42), (X(.44), y - s * .26), (X(-.1), y - s * .26)]),     # seat
            ("poly", [(X(-.02), y - s * .58), (X(.42), y - s * .55), (X(.46), y - s * .48), (X(.4), y - s * .42), (X(-.02), y - s * .46)]),  # arm
            ("poly", [(X(.36), y - s * .55), (X(.44), y - s * .55), (X(.44), y - s * .26), (X(.36), y - s * .26)]),     # arm front
            ("line", ([(X(-.06), y - s * .26), (X(-.08), y)], s * .05)), ("line", ([(X(.4), y - s * .26), (X(.42), y)], s * .05))]


def zzz(x, y, s):
    shapes = []
    for k, (dx, dy, sz) in enumerate(((0, 0, 1.0), (.22, -.3, .75), (.4, -.55, .55))):
        a, b = x + s * dx, y + s * dy
        w = s * .16 * sz
        shapes.append(("line", ([(a, b), (a + w, b), (a, b + w), (a + w, b + w)], max(1.5, s * .035))))
    return shapes


def _gag_chair_sleepers(ctx):
    """Veyra: nobody owns a bed, so people sleep in armchairs on the cliff."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    h = H * G
    lx = ctx.geo.get("lighthouse")
    left = ctx.spec.shore != "right"
    # the flattest, highest ground on the cliff, away from the lighthouse
    xs_all = np.linspace(W * (0.04 if left else 0.55), W * (0.45 if left else 0.96), 60)
    ys_all = np.array([_ground(ctx, x) for x in xs_all])
    order = np.argsort(ys_all)
    xs = []
    for i in order:
        x = xs_all[i]
        if lx is not None and abs(x - lx) < W * 0.06:
            continue
        if all(abs(x - q) > W * 0.09 for q in xs):
            xs.append(x)
        if len(xs) == 3:
            break
    xs.sort()
    f = -1 if left else 1
    for x in xs:
        y = _ground(ctx, x)
        _ink(ctx, layer, armchair(x, y, h, f), ctx.dark)
        a = _person(ctx, layer, x + h * .1 * f, y - h * .06, h, "doze", f)
        hx, hy = a["head"]
        _ink(ctx, layer, zzz(hx + h * .1, hy - h * .22, h * .9), LIGHT)
    mid = xs[len(xs) // 2] if xs else W * 0.3
    ctx.focus = (mid / W, (_ground(ctx, mid) - h * .7) / H)


def _gag_seabed_town(ctx):
    """Orrin: a town on the dry seabed, taken apart plank by plank before the tide."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    far = ctx.far_layer
    hy = ctx.ridge_at(ctx.far_ridge, W * 0.5) + H * 0.01
    stamp(far.P, far.A, [("poly", [(0, hy - H * .004), (W * 3, hy - H * .004), (W * 3, hy + H * .004), (0, hy + H * .004)])], LIGHT, 0.85)
    s = H * 0.1
    xs = [W * 0.16, W * 0.4, W * 0.64, W * 0.86]
    for i, x in enumerate(xs):
        _ink(ctx, layer, house(x, _ground(ctx, x), s, broken=i in (1, 2)), ctx.dark)
    for x in (W * 0.28, W * 0.52):
        h = H * G
        a = _person(ctx, layer, x, _ground(ctx, x), h, "walk", 1)
        sx, sy = a["neck"]
        _ink(ctx, layer, [("line", ([(sx - h * .6, sy + h * .03), (sx + h * .65, sy - h * .05)], h * .07))], LIGHT)
    ctx.focus = (0.4, (_ground(ctx, W * .4) - s * .5) / H)


def _gag_slow_shout(ctx):
    """Hush: a shout crawls across the valley towards someone waiting to hear it."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    _stage(ctx, 0.86)
    h = H * G
    x = W * 0.2
    y = _ground(ctx, x)
    a = _person(ctx, layer, x, y, h, "cup", 1)
    mx, my = a["rh"]
    col = ctx.dark if ctx.spec.snow else LIGHT
    for k in range(4):
        r = W * (0.07 + 0.09 * k)
        stamp(layer.P, layer.A, [arc_line(mx, my, r, -0.6, 0.45, H * 0.006)], col, 0.85 - 0.17 * k)
    x2 = W * 0.8
    _person(ctx, layer, x2, _ground(ctx, x2), h * 0.9, "cup", -1)
    ctx.focus = (0.3, (y - h * .7) / H)


def _gag_pole_post(ctx):
    """Maren: the post goes up to the floating farms on a very long pole."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    isl = ctx.geo.get("islands") or []
    tx, ty = (isl[0][0], isl[0][1] + isl[0][2] * 0.6) if isl else (W * .4, H * .3)
    x = min(max(tx + W * 0.14, W * .15), W * .85)
    y = _ground(ctx, x)
    h = H * G
    a = _person(ctx, layer, x, y, h, "reach", -1 if tx < x else 1)
    hx, hy = a["rh"]
    _ink(ctx, layer, [("line", ([(hx, hy + h * .3), (tx, ty)], H * 0.005))], ctx.dark)
    _paper(ctx, layer.P, layer.A, tx, ty + h * .1, h * 1.5, -0.3, kind="letter")
    ctx.focus = ((x + tx) / 2 / W, (y + ty) / 2 / H)


def _steam(ctx, layer, x, y, s):
    for k in range(3):
        pts = [(x + s * (0.12 * k - 0.1) + s * 0.08 * math.sin(t * 5 + k), y - s * t) for t in np.linspace(0, 1.1, 12)]
        stamp(layer.P, layer.A, [("line", (pts, s * 0.05))], LIGHT, 0.65)


def _gag_kettles(ctx):
    """Cinderwake: the rock is warm enough to boil a kettle."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    _stage(ctx, 0.88)
    s = H * 0.075
    for x in (W * 0.32, W * 0.48, W * 0.64):
        y = _ground(ctx, x)
        _ink(ctx, layer, [("ellipse", (x - s * .5, y - s * .14, x + s * .5, y + s * .1))], ctx.dark)
        _ink(ctx, layer, kettle(x, y - s * .1, s), ctx.dark)
        _steam(ctx, layer, x + s * .48, y - s * .58, s * .9)
    x = W * 0.8
    _person(ctx, layer, x, _ground(ctx, x), H * G, "cup", -1)
    ctx.focus = (0.48, (_ground(ctx, W * .48) - s * .7) / H)


def _gag_moon_letters(ctx):
    """Luma: children press letters against the moon as it drifts past."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    bm = ctx.geo.get("big_moon")
    h = H * 0.065
    xs = [W * 0.4, W * 0.5, W * 0.6]
    for i, x in enumerate(xs):
        a = _person(ctx, layer, x, _ground(ctx, x), h * (0.85 if i != 1 else 1.0), "reach", 1 if i < 1 else -1)
        _paper(ctx, layer.P, layer.A, a["rh"][0], a["rh"][1] - h * .1, h * 1.3, 0.25 * (i - 1), kind="letter")
    if bm:
        cx, cy, r = bm
        rng = ctx.rng("moonletters")
        for _ in range(8):
            ang = rng.uniform(1.2 * math.pi, 1.8 * math.pi)       # upper half, above the hills
            d = r * rng.uniform(0.35, 0.85)
            lx, ly = cx + d * math.cos(ang), cy + d * math.sin(ang) * 0.85
            ra = rng.uniform(-0.6, 0.6)
            stamp(ctx.sky_P, ctx.sky_A, letter(lx, ly, h * 1.7, ra), ctx.dark, 0.9)
            _paper(ctx, ctx.sky_P, ctx.sky_A, lx, ly, h * 1.45, ra, kind="letter")
    ctx.focus = (0.5, (_ground(ctx, W * .5) - h * 1.2) / H)


def _gag_glass_surfers(ctx):
    """Selk: surfers stand very still under waves that froze mid-break."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    curls = ctx.geo.get("wave_curls") or [(W * .5, H * .7)]
    h = H * G
    picked = [c for c in curls if W * .12 < c[0] < W * .88][:2] or curls[:1]
    for (cx, _) in picked:
        for j, dx in enumerate((-0.05, 0.035)):
            x = cx + W * dx
            y = _ground(ctx, x)
            _person(ctx, layer, x, y, h, "stand", 1 if j else -1)
            bx = x + h * .24 * (1 if j else -1)
            _ink(ctx, layer, [("ellipse", (bx - h * .08, y - h * 1.18, bx + h * .08, y))], LIGHT)
    x0 = picked[0][0]
    ctx.focus = (x0 / W, (_ground(ctx, x0) - h * 1.2) / H)


def _gag_tiny_planet(ctx):
    """Ovo: the ground is a small globe with one of everything on it."""
    W, H = ctx.W, ctx.H
    layer = ctx.globe
    # the whole planet in frame, so it reads as a planet and not a hill
    R = min(W * 0.44, H * 0.36)
    cx, cy = W * 0.5, H * 0.97 - R
    stamp(layer.P, layer.A, [("ellipse", (cx - R, cy - R, cx + R, cy + R))], ctx.land)
    # lit from the upper left, so the globe has a round, printed shading
    y0, y1 = max(int(cy - R) - 2, 0), min(int(cy + R) + 3, H)
    x0, x1 = max(int(cx - R) - 2, 0), int(cx + R) + 3
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    nx, ny = (xx - cx) / R, (yy - cy) / R
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    lam = np.clip(nx * -0.5 + ny * -0.62 + nz * 0.6, 0, 1) ** 1.3
    lit = mix(ctx.pal.water, ctx.pal.haze, 0.3)
    shade = ctx.land[None, None, :] * (1 - lam[..., None]) + lit[None, None, :] * lam[..., None]
    a = layer.A[y0:y1, x0:x1, None]
    layer.P[y0:y1, x0:x1] = shade * a
    # the footpath that goes all the way round, on the near side of the globe
    tilt = -0.32
    for k in range(34):
        p0, p1 = math.pi * (0.04 + k / 34 * 0.92), math.pi * (0.04 + (k + 0.45) / 34 * 0.92)
        seg = []
        for ph in np.linspace(p0, p1, 4):
            u, v = R * 0.93 * math.cos(ph), R * 0.3 * math.sin(ph)
            seg.append((cx + u * math.cos(tilt) - v * math.sin(tilt), cy + 0.12 * R + u * math.sin(tilt) + v * math.cos(tilt)))
        stamp(layer.P, layer.A, [("line", (seg, max(1.5, R * 0.008)))], LIGHT, 0.45)
    # its one moon
    mr = W * 0.032
    mx, my = W * 0.9, H * 0.31
    stamp(ctx.sky_P, ctx.sky_A, [("ellipse", (mx - mr, my - mr, mx + mr, my + mr))], mix(LIGHT, ctx.pal.accent, 0.3))
    stamp(ctx.sky_P, ctx.sky_A, [("ellipse", (mx - mr * .45, my - mr * .2, mx - mr * .05, my + mr * .2)),
                                 ("ellipse", (mx + mr * .2, my + mr * .25, mx + mr * .45, my + mr * .5))], mix(LIGHT, ctx.pal.haze, 0.6))
    s = H * 0.065
    items = [(-0.68, "bakery"), (-0.34, "tree"), (-0.04, "person"), (0.26, "bench"), (0.6, "lamp")]
    for th, kind in items:
        ax, ay = cx + R * math.sin(th), cy - R * math.cos(th) + 2
        if kind == "bakery":
            shp = house(ax, ay, s * 1.3) + [("poly", [(ax - s * .8, ay - s * .78), (ax + s * .8, ay - s * .78), (ax + s * .7, ay - s * .62), (ax - s * .7, ay - s * .62)])]
            stamp(layer.P, layer.A, rotate(shp, ax, ay, th), ctx.dark)
            stamp(layer.P, layer.A, rotate([("poly", [(ax - s * .25, ay - s * .55), (ax + s * .25, ay - s * .55), (ax + s * .25, ay - s * .25), (ax - s * .25, ay - s * .25)])], ax, ay, th), ctx.light)
        elif kind == "tree":
            stamp(layer.P, layer.A, rotate(round_tree(ax, ay, s * 2.6, ctx.rng("ovo-tree")), ax, ay, th), ctx.dark)
        elif kind == "person":
            body, coat, anchors = figure(ax, ay, s * 1.2, "stand", 1)
            hx, hy = anchors["rh"]
            stamp(layer.P, layer.A, rotate(body + [coat], ax, ay, th), ctx.dark)
            stamp(layer.P, layer.A, rotate([coat], ax, ay, th), YELLOW)
            _paper(ctx, layer.P, layer.A, hx, hy - s * .1, s * 1.3, 0.2, turn=(ax, ay, th))
        elif kind == "bench":
            b = s * 1.25
            # the cat always comes first: it has the bench
            stamp(layer.P, layer.A, rotate(bench(ax, ay, b) + cat(ax + b * .18, ay - b * .27, s * 1.05, -1), ax, ay, th), ctx.dark)
        else:
            stamp(layer.P, layer.A, rotate([("line", ([(ax, ay), (ax, ay - s * 1.6)], s * .06)), ("ellipse", (ax - s * .12, ay - s * 1.78, ax + s * .12, ay - s * 1.54))], ax, ay, th), ctx.dark)
            lx, ly = ax + s * 1.66 * math.sin(th), ay - s * 1.66 * math.cos(th)
            glow(layer.E, lx, ly, s * .18, ctx.pal.light, 0.8)
    mid = 0.11
    ctx.focus = ((cx + R * math.sin(mid)) / W, (cy - R * math.cos(mid) - s * .7) / H)


def _gag_umbrella_feet(ctx):
    """Thessaly: rain falls up, so umbrellas are worn on the feet."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    lo, hi = (0.62, 0.9) if ctx.spec.shore == "right" else (0.1, 0.38)
    h = H * G
    xs = np.linspace(W * lo, W * hi, 3)
    for i, x in enumerate(xs):
        y = _ground(ctx, x) - h * 0.22
        a = _person(ctx, layer, x, y, h, "stand" if i != 1 else "walk", 1 if i % 2 else -1)
        for foot in ("lf", "rf"):
            fx, fy = a[foot]
            _ink(ctx, layer, umbrella_down(fx, fy, h * .36), ctx.spot)
    ctx.focus = (xs[1] / W, (_ground(ctx, xs[1]) - h * .55) / H)


def _gag_road_tourists(ctx):
    """Kess: tourists lie in the road to watch the aurora; locals step round them."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    _stage(ctx, 0.8)
    road = mix(ctx.ground, ctx.dark, 0.3)
    top = ctx.stage_y(W * 0.5) + H * 0.03
    _ink(ctx, layer, [("poly", [(-20, top), (W * 3, top), (W * 3, top + H * .07), (-20, top + H * .07)])], road)
    h = H * G
    for x in (W * 0.3, W * 0.45, W * 0.6):
        _person(ctx, layer, x, top + H * .04, h, "stand", 1, ang=math.pi / 2)
    for x, f in ((W * 0.18, 1), (W * 0.78, -1)):
        _person(ctx, layer, x, top + H * .055, h, "walk", f)
    ctx.focus = (0.45, (top + H * .02) / H)


def _gag_tree_cloud(ctx):
    """Bramble: the tallest tree has its own small cloud and a village near the top."""
    W, H = ctx.W, ctx.H
    t = ctx.geo.get("tallest_tree")
    if not t:
        return
    layer, x, top, h = t
    if layer.E is None:
        layer.E = np.zeros_like(layer.P)
    cw = W * 0.22
    cy = top - H * 0.03
    stamp(layer.P, layer.A, cloud(x, cy, cw), ctx.light, 0.95)
    for k in range(9):
        rx = x - cw * .35 + cw * .7 * k / 8
        stamp(layer.P, layer.A, [("line", ([(rx, cy + cw * .1), (rx - cw * .03, cy + cw * .1 + H * .06)], 2.0))], ctx.light, 0.75)
    s = H * 0.04
    for k, fy in enumerate((0.16, 0.26, 0.36)):
        hx = x + (s * 1.3 if k % 2 else -s * 1.3)
        hy = top + h * fy
        stamp(layer.P, layer.A, house(hx, hy, s), ctx.dark)
        glow(layer.E, hx, hy - s * .35, s * .22, ctx.pal.light, 1.0)
    ctx.focus = (x / W, (top + h * .18) / H)


def _gag_fainted_ghost(ctx):
    """Hollow: say boo and the ghost faints."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    x = W * 0.44
    y = _ground(ctx, x)
    s = H * 0.11
    body, eyes = ghost(x, y, s)
    _ink(ctx, layer, rotate(body, x, y - s * .02, -math.pi / 2), ctx.light)
    _ink(ctx, layer, rotate(eyes, x, y - s * .02, -math.pi / 2), ctx.dark)
    _person(ctx, layer, x + W * 0.13, _ground(ctx, x + W * .13), H * G, "cup", -1)
    ctx.focus = (x / W + 0.05, (y - s * .4) / H)


def _gag_megaphones(ctx):
    """Max: the vote to remove the quiet setting, cast by megaphone."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    _stage(ctx, 0.8)
    h = H * G
    for x, f in ((W * 0.3, -1), (W * 0.5, 1), (W * 0.7, 1)):
        y = _ground(ctx, x)
        a = _person(ctx, layer, x, y, h, "cup", f)
        hx, hy = a["head"]
        nx, ny = hx + h * .1 * f, hy + h * .02
        wx, wy = hx + h * .5 * f, hy - h * .14
        _ink(ctx, layer, [("poly", [(nx, ny - h * .04), (nx, ny + h * .04), (wx, wy + h * .15), (wx, wy - h * .15)])], LIGHT)
        a0, a1 = (-0.95, 0.25) if f > 0 else (math.pi - 0.25, math.pi + 0.95)
        for k, r in enumerate((.22, .38, .54)):
            stamp(layer.P, layer.A, [arc_line(wx, wy, h * r, a0, a1, max(1.5, h * .035))], LIGHT, 0.9 - 0.25 * k)
    ctx.focus = (0.5, (_ground(ctx, W * .5) - h * .8) / H)


def _gag_stirrers(ctx):
    """Milo: the soil is chocolate malt, so farming is mostly stirring."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    _stage(ctx, 0.8)
    h = H * G
    swirl = mix(ctx.ground, LIGHT, 0.4)
    for i, x in enumerate((W * 0.26, W * 0.5, W * 0.74)):
        f = 1 if i % 2 == 0 else -1
        y = _ground(ctx, x)
        _person(ctx, layer, x, y, h, "stand", f)
        tx, ty = x + h * .5 * f, y + h * .05
        pts = [(tx + h * (.06 + .05 * t) * math.cos(t * 2.4), ty + h * (.06 + .05 * t) * .3 * math.sin(t * 2.4))
               for t in np.linspace(0, 6.5, 60)]
        _ink(ctx, layer, [("line", (pts, max(1.5, h * .025)))], swirl)
        _ink(ctx, layer, [("line", ([(x + h * .02 * f, y - h * 1.0), (tx, ty)], h * .05)),
                          ("ellipse", (x - h * .02 * f - h * .07, y - h * 1.12, x - h * .02 * f + h * .07, y - h * .96))], LIGHT)
    ctx.focus = (0.5, (_ground(ctx, W * .5) - h * .6) / H)


# --------------------------------------------------------------------------
# extras: generic props a planet can combine with its gag

ITEMS = ["spade", "spoon", "nothing", "book", "fish", "umbrella", "cup"]


def _held(ctx, layer, kind, hx, hy, h):
    # held up and printed light, so they read against the dark figures
    if kind == "spade":
        tx, ty = hx + h * .12, hy - h * .62
        _ink(ctx, layer, [("line", ([(hx - h * .03, hy + h * .12), (tx, ty)], h * .045)),
                          ("poly", [(tx - h * .1, ty + h * .02), (tx + h * .12, ty - h * .02), (tx + h * .1, ty - h * .26), (tx + h * .01, ty - h * .32), (tx - h * .1, ty - h * .22)])], LIGHT)
    elif kind == "spoon":
        _ink(ctx, layer, [("line", ([(hx, hy + h * .08), (hx + h * .02, hy - h * .42)], h * .045)),
                          ("ellipse", (hx - h * .08, hy - h * .68, hx + h * .12, hy - h * .38))], LIGHT)
    elif kind == "book":
        _ink(ctx, layer, [("poly", [(hx - h * .12, hy - h * .1), (hx + h * .12, hy - h * .1), (hx + h * .12, hy + h * .08), (hx - h * .12, hy + h * .08)])], LIGHT)
    elif kind == "fish":
        _ink(ctx, layer, [("ellipse", (hx - h * .02, hy - h * .05, hx + h * .3, hy + h * .07)),
                          ("poly", [(hx + h * .28, hy), (hx + h * .4, hy - h * .08), (hx + h * .4, hy + h * .1)])], LIGHT)
    elif kind == "umbrella":
        arc = [(hx + h * .3 * math.cos(a), hy - h * .55 - h * .22 * math.sin(a)) for a in np.linspace(0, math.pi, 11)]
        _ink(ctx, layer, [("poly", arc + [(hx - h * .3, hy - h * .55)]), ("line", ([(hx, hy - h * .55), (hx, hy + h * .05)], h * .04))], ctx.spot)
    elif kind == "cup":
        _ink(ctx, layer, [("poly", [(hx - h * .06, hy - h * .1), (hx + h * .06, hy - h * .1), (hx + h * .05, hy + h * .04), (hx - h * .05, hy + h * .04)])], LIGHT)


def _crowd(ctx):
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    n = ctx.spec.crowd
    h = H * G
    # with a sign, the crowd keeps to the left so the board (placed right) hides no one
    xs = np.linspace(W * 0.08, W * 0.54, n) if ctx.spec.sign else np.linspace(W * 0.2, W * 0.8, n)
    for i, x in enumerate(xs):
        a = _person(ctx, layer, x, _ground(ctx, x), h * (0.92 + 0.08 * ((i * 7) % 3) / 2), "stand", 1 if i % 2 else -1)
        _held(ctx, layer, ITEMS[i % len(ITEMS)], a["rh"][0], a["rh"][1], h)
    mid = float(xs.mean())
    ctx.focus = (mid / W, (_ground(ctx, mid) - h * .6) / H)


def _daisies(ctx):
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    rng = ctx.rng("daisies")
    for _ in range(ctx.spec.daisies):
        x = rng.uniform(0, W * 1.2)
        y = _ground(ctx, x) + rng.uniform(H * 0.01, H * 0.12)
        if y > H - 4:
            continue
        r = H * rng.uniform(0.008, 0.016)
        _ink(ctx, layer, [("ellipse", (x - r, y - r * .7, x + r, y + r * .7))], LIGHT)
        _ink(ctx, layer, [("ellipse", (x - r * .38, y - r * .3, x + r * .38, y + r * .3))], YELLOW)


def _lamp(ctx):
    """A tall lamp pointed at the sky, standing in for a moon."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    if layer.E is None:
        layer.E = np.zeros_like(layer.P)
    x = W * 0.5
    y = _ground(ctx, x)
    top = y - H * 0.22
    _ink(ctx, layer, [("line", ([(x, y), (x, top)], H * 0.008)),
                      ("poly", [(x - H * .025, top), (x + H * .025, top), (x + H * .035, top - H * .03), (x - H * .035, top - H * .03)])], ctx.dark)
    beam = np.zeros_like(layer.A)
    bP = np.zeros_like(layer.P)
    stamp(bP, beam, [("poly", [(x - H * .03, top - H * .03), (x + H * .03, top - H * .03), (x + W * .2, 0), (x - W * .2, 0)])], np.ones(3))
    gy = np.arange(beam.shape[0], dtype=np.float32)[:, None]
    fade = np.clip(gy / max(top, 1), 0, 1) ** 1.5
    layer.E += (beam * fade * 0.35)[..., None] * ctx.pal.light
    glow(layer.E, x, top - H * .03, H * .02, ctx.pal.light, 1.2)
    ctx.focus = (0.5, (top + H * .05) / H)


def _sign(ctx):
    """A signpost whose board carries a short line of text in the atlas typeface."""
    from PIL import Image, ImageDraw
    from .text import font
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    lines = [t for t in ctx.spec.sign.split("|") if t]
    fx = ctx.focus[0] * W
    x = W * 0.72 if fx < W * 0.55 else W * 0.28
    y = _ground(ctx, x)
    fs = max(10, int(H * 0.022))
    f = font("serif", fs, "Medium")
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    bw = int(max(probe.textlength(t, font=f) for t in lines) + fs * 1.4)
    bh = int(len(lines) * fs * 1.25 + fs * 0.9)
    post = H * 0.09
    x0, y0 = int(x - bw / 2), int(y - post - bh)
    _ink(ctx, layer, [("line", ([(x - bw * .3, y), (x - bw * .3, y0 + bh)], H * .007)),
                      ("line", ([(x + bw * .3, y), (x + bw * .3, y0 + bh)], H * .007)),
                      ("poly", [(x0 - 3, y0 - 3), (x0 + bw + 3, y0 - 3), (x0 + bw + 3, y0 + bh + 3), (x0 - 3, y0 + bh + 3)])], ctx.dark)
    _ink(ctx, layer, [("poly", [(x0, y0), (x0 + bw, y0), (x0 + bw, y0 + bh), (x0, y0 + bh)])], LIGHT)
    board = Image.new("L", (bw, bh), 0)
    d = ImageDraw.Draw(board)
    for j, t in enumerate(lines):
        d.text((bw / 2, fs * 0.5 + j * fs * 1.25), t, font=f, fill=255, anchor="ma")
    m = np.asarray(board, np.float32) / 255
    h_, w_ = layer.A.shape
    ys, xs = slice(max(y0, 0), min(y0 + bh, h_)), slice(max(x0, 0), min(x0 + bw, w_))
    mm = m[ys.start - y0: ys.stop - y0, xs.start - x0: xs.stop - x0]
    layer.P[ys, xs] = layer.P[ys, xs] * (1 - mm[..., None]) + ctx.dark * mm[..., None]
    sx, sy = x / W, (y0 + bh / 2) / H
    # the close-up has to show the sign: frame it on its own, or halfway between it and the gag
    ctx.focus = (sx, sy) if ctx.focus == (0.5, 0.62) else ((ctx.focus[0] + sx) / 2, (ctx.focus[1] + sy) / 2)
    ctx.marks["sign"] = (sx, sy)


def extras(ctx):
    if ctx.spec.stage and ctx.stage_y is None:
        _stage(ctx, ctx.spec.stage)
    if ctx.spec.daisies:
        _daisies(ctx)
    if ctx.spec.crowd:
        _crowd(ctx)
    if ctx.spec.lamp:
        _lamp(ctx)
    if ctx.spec.sign:
        _sign(ctx)


GAGS = {
    "chair_sleepers": _gag_chair_sleepers, "seabed_town": _gag_seabed_town, "slow_shout": _gag_slow_shout,
    "pole_post": _gag_pole_post, "kettles": _gag_kettles, "moon_letters": _gag_moon_letters,
    "glass_surfers": _gag_glass_surfers, "tiny_planet": _gag_tiny_planet, "umbrella_feet": _gag_umbrella_feet,
    "road_tourists": _gag_road_tourists, "tree_cloud": _gag_tree_cloud, "fainted_ghost": _gag_fainted_ghost,
    "megaphones": _gag_megaphones, "stirrers": _gag_stirrers,
}


def make_ctx(**kw):
    return SimpleNamespace(**kw)
