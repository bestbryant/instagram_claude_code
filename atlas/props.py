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
from .render import glow, hexc, mix, moth, round_tree, stamp

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
    # a child on the shoulders: both hands up holding its shins
    "carry": dict(head=(0, .915), neck=(0, .83), hip=(0, .5), le=(.12, .68), lh=(.16, .8), re=(.14, .67), rh=(.18, .79),
                  lk=(-.05, .25), lf=(-.07, 0), rk=(.05, .25), rf=(.07, 0)),
    # the child up there: pointing at something ahead, or asleep, slumped over the carrier's head
    "point": dict(head=(.02, .92), neck=(0, .82), hip=(0, .45), le=(-.08, .62), lh=(-.04, .5), re=(.22, .9), rh=(.44, 1.06),
                  lk=(.2, .42), lf=(.24, .12), rk=(.23, .4), rf=(.28, .1)),
    "asleep": dict(head=(.3, .6), neck=(.18, .66), hip=(0, .45), le=(.24, .56), lh=(.34, .44), re=(.26, .55), rh=(.36, .42),
                   lk=(.2, .42), lf=(.24, .12), rk=(.23, .4), rf=(.28, .1)),
    # sitting on the ground, knees up, arms round them
    "ground": dict(head=(.0, .52), neck=(.0, .44), hip=(-.04, .08), le=(.1, .3), lh=(.2, .24), re=(.12, .29), rh=(.22, .23),
                   lk=(.2, .28), lf=(.3, 0), rk=(.22, .26), rf=(.32, 0)),
    # asleep sitting up, head down on the knees
    "nap": dict(head=(.13, .4), neck=(.05, .42), hip=(-.04, .08), le=(.1, .3), lh=(.2, .24), re=(.12, .29), rh=(.22, .23),
                lk=(.2, .28), lf=(.3, 0), rk=(.22, .26), rf=(.32, 0)),
    # a hand cupped behind the ear, listening
    "listen": dict(head=(0, .915), neck=(0, .83), hip=(0, .5), le=(-.13, .66), lh=(-.15, .5), re=(.17, .8), rh=(.08, .93),
                   lk=(-.05, .25), lf=(-.07, 0), rk=(.05, .25), rf=(.07, 0)),
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
    if ctx.near_layer.E is not None:              # light drawn on the ridge behind (glowing rims) stays behind the ledge
        cover = np.zeros_like(ctx.near_layer.A)
        stamp(np.zeros_like(ctx.near_layer.P), cover, [("poly", poly)], np.ones(3))
        ctx.near_layer.E *= (1 - cover)[..., None]
    ctx.stage_y = lambda x: float(np.interp(x, xs, ys)) + 2


def cartographer(ctx, avoid_x=None):
    """The narrator, in a yellow coat with a map, somewhere in every print."""
    if ctx.globe is not None:
        return
    W, H = ctx.W, ctx.H
    rng = ctx.rng("cartographer")
    layer = ctx.near_layer
    h = H * 0.06

    def cost(x):      # standing in front of the gag's figures, a sign or a house hides the joke
        y = int(_ground(ctx, x))
        box = layer.A[max(y - int(h * 1.3), 0): max(y - 3, 1), max(int(x - h * .45), 0): int(x + h * .45)]
        ink = float(box.mean()) if box.size else 1.0
        low = y > H * 0.8          # under Instagram's caption strip, or down at the waterline off the land
        return ink + (0.5 if avoid_x is not None and abs(x - avoid_x) < W * 0.22 else 0.0) + (2.0 if low else 0.0)
    x = min((W * rng.uniform(0.12, 0.88) for _ in range(12)), key=cost)
    y = _ground(ctx, x)
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


def _gag_ghost(ctx):
    """Hollow, a moment earlier: the ghost still upright, the visitor about to say boo. Same place and camera
    as fainted_ghost, so an onset from one to the other is the ghost keeling over."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    x = W * 0.44
    y = _ground(ctx, x)
    s = H * 0.11
    body, eyes = ghost(x, y, s)
    _ink(ctx, layer, body, ctx.light)
    _ink(ctx, layer, eyes, ctx.dark)
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
# also by name: flower, kettle, kite, child, child_asleep; and as the whole figure: shadow (only the shadow is left),
# shadowed (a person and their shadow), aloft (a person in mid-jump), shout and echo (sound going out, coming back),
# sing (warm arcs going out), sit (on the ground), nap, doze, walk and hand (a raised hand: a vote)


def _gag_moth_roof(ctx):
    """A cottage with a lit window and a kite-sized moth sitting on its roof, looking in (when the planet has moths)."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    if ctx.stage_y is None:
        _stage(ctx, 0.74)
    x = W * 0.42
    y = _ground(ctx, x)
    s = H * 0.085
    _ink(ctx, layer, house(x, y, s), ctx.dark)
    if layer.E is None:
        layer.E = np.zeros_like(layer.P)
    _ink(ctx, layer, [("poly", [(x - s * .22, y - s * .45), (x + s * .02, y - s * .45), (x + s * .02, y - s * .22), (x - s * .22, y - s * .22)])], ctx.pal.light)
    glow(layer.E, x - s * .1, y - s * .33, s * .2, ctx.pal.light, 0.9)
    if ctx.spec.moths:
        _ink(ctx, layer, moth(x + s * 0.12, y - s * 1.08, s * 0.42), ctx.dark)
    ctx.marks["house"] = (x / W, (y - s / 2) / H)
    ctx.focus = (x / W, (y - s * 0.7) / H)


def _held(ctx, layer, kind, hx, hy, h, i=0):
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
    elif kind == "flower":
        _ink(ctx, layer, [("line", ([(hx, hy + h * .06), (hx + h * .03, hy - h * .36)], h * .03))], ctx.dark)
        cx, cy, r = hx + h * .03, hy - h * .42, h * .09
        petals = [(cx + r * .55 * math.cos(t), cy + r * .55 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
        _ink(ctx, layer, [("ellipse", (px - r * .4, py - r * .3, px + r * .4, py + r * .3)) for px, py in petals], LIGHT)
        _ink(ctx, layer, [("ellipse", (cx - r * .3, cy - r * .3, cx + r * .3, cy + r * .3))], YELLOW)
    elif kind == "kettle":
        _ink(ctx, layer, kettle(hx, hy + h * .14, h * .32), LIGHT)
    elif kind == "cup":
        _ink(ctx, layer, [("poly", [(hx - h * .06, hy - h * .1), (hx + h * .06, hy - h * .1), (hx + h * .05, hy + h * .04), (hx - h * .05, hy + h * .04)])], LIGHT)
    elif kind == "kite":
        # every kite leans the same way: it's one wind
        lift = 2.1 + 0.9 * ((i * 5) % 3)          # strings of different lengths, so a crowd of kites fills the sky
        kx, ky, k = hx + h * .38 * lift, hy - h * lift, h * .3
        _ink(ctx, layer, [("line", ([(hx, hy), (hx + (kx - hx) * .55, hy + (ky + k - hy) * .5), (kx, ky + k)], h * .012))], LIGHT)
        _ink(ctx, layer, [("line", ([(kx, ky + k), (kx - h * .08, ky + k * 1.8), (kx + h * .04, ky + k * 2.5), (kx - h * .05, ky + k * 3.2)], h * .012))], LIGHT)
        _ink(ctx, layer, [("poly", [(kx, ky - k), (kx + k * .7, ky), (kx, ky + k), (kx - k * .7, ky)])], ctx.spot)


def _shadow(ctx, layer, x, y, h, facing, sun_left=True):
    """A standing figure's shadow, cast long across the ground away from the sun."""
    body, coat, _ = figure(x, y, h, "stand", facing)
    away = 1 if sun_left else -1
    T = lambda q: (q[0] + (y - q[1]) * 1.1 * away, y + (y - q[1]) * 0.3)
    flat = []
    for kind, g in body + [coat]:
        if kind == "poly":
            flat.append(("poly", [T(q) for q in g]))
        elif kind == "line":
            flat.append(("line", ([T(q) for q in g[0]], g[1])))
        else:
            cx, cy = T(((g[0] + g[2]) / 2, (g[1] + g[3]) / 2))
            hw, hh = (g[2] - g[0]) / 2, (g[3] - g[1]) / 2
            flat.append(("ellipse", (cx - hw * 1.4, cy - hh * 0.5, cx + hw * 1.4, cy + hh * 0.5)))
    _ink(ctx, layer, flat, mix(ctx.dark, np.zeros(3), 0.5), 0.75)


def _child(ctx, layer, a, h, facing, asleep=False):
    """A child riding on the carrier's shoulders: pointing ahead, or asleep over the carrier's head."""
    nx, ny = a["neck"]
    hc = h * 0.55
    hip_y = ny - h * 0.13                    # sitting on the shoulders, the carrier's head showing in front
    _person(ctx, layer, nx - h * 0.07 * facing, hip_y + hc * 0.45, hc, "asleep" if asleep else "point", facing)


def _crowd(ctx):
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    sp = ctx.spec
    n = sp.crowd
    h = H * G
    items = [t.strip() for t in sp.crowd_items.split(",") if t.strip()] or ITEMS
    if sp.crowd_x:
        xs = sp.crowd_x * W + (np.arange(n) - (n - 1) / 2) * W * sp.crowd_gap
    elif sp.sign:
        # with a sign, the crowd keeps to the left so the board (placed right) hides no one
        xs = np.linspace(W * 0.08, W * 0.54, n)
    else:
        xs = np.linspace(W * 0.2, W * 0.8, n)
    mid = float(xs.mean())
    for i, x in enumerate(xs):
        face = {"in": 1 if x < mid or (n == 1) else -1, "out": -1 if x < mid else 1,
                "left": -1, "right": 1}.get(sp.crowd_facing, 1 if i % 2 else -1)
        kind = items[i % len(items)]
        carry = kind.startswith("child")
        hi = h * (0.92 + 0.08 * ((i * 7) % 3) / 2)
        if kind in ("shadow", "shadowed"):
            _shadow(ctx, layer, x, _ground(ctx, x), hi, face, sun_left=(sp.sun_x if sp.sun_x is not None else 0.3) < 0.5)
            if kind == "shadow":
                continue
            kind = "nothing"
        if kind == "shout":
            # an unkind shout: jagged red arcs going out
            a = _person(ctx, layer, x, _ground(ctx, x), hi, "cup", face)
            mx, my = a["rh"]
            for k in range(3):
                r = W * (0.05 + 0.06 * k)
                ang = np.linspace(-0.5, 0.45, 9)
                pts = [(mx + face * r * (1 + (0.09 if j % 2 else -0.09)) * math.cos(t), my + r * (1 + (0.09 if j % 2 else -0.09)) * math.sin(t))
                       for j, t in enumerate(ang)]
                stamp(layer.P, layer.A, [("line", (pts, H * 0.005))], ctx.spot, 0.9 - 0.2 * k)
            continue
        if kind == "sing":
            # a song going out: smooth warm arcs from cupped hands
            a = _person(ctx, layer, x, _ground(ctx, x), hi, "cup", face)
            mx, my = a["rh"]
            for k in range(3):
                r = W * (0.05 + 0.06 * k)
                a0, a1 = (-0.45, 0.45) if face > 0 else (math.pi - 0.45, math.pi + 0.45)
                stamp(layer.P, layer.A, [arc_line(mx, my, r, a0, a1, H * 0.007)], YELLOW, 0.95 - 0.2 * k)
            continue
        if kind == "echo":
            # the echo coming back: smooth, thicker, warm arcs facing the listener, who has a hand to the ear
            a = _person(ctx, layer, x, _ground(ctx, x), hi, "listen", face)
            mx, my = a["head"]
            for k in range(3):
                r = W * (0.05 + 0.06 * k)
                a0, a1 = (math.pi - 0.45, math.pi + 0.45) if face > 0 else (-0.45, 0.45)
                stamp(layer.P, layer.A, [arc_line(mx + face * W * 0.3, my, r, a0, a1, H * 0.008)], YELLOW, 0.95 - 0.2 * k)
            continue
        if kind in ("sit", "doze", "walk", "hand", "nap"):
            _person(ctx, layer, x, _ground(ctx, x), hi, {"hand": "reach", "sit": "ground"}.get(kind, kind), face)
            continue
        if kind == "aloft":
            gy = _ground(ctx, x)
            _ink(ctx, layer, [("ellipse", (x - hi * .22, gy - hi * .03, x + hi * .22, gy + hi * .03))], LIGHT, 0.35)
            _person(ctx, layer, x, gy - hi * 3.0, hi, "point", face)     # low gravity: a jump clears the hills
            continue
        a = _person(ctx, layer, x, _ground(ctx, x), hi, "carry" if carry else "stand", face)
        if carry:
            _child(ctx, layer, a, h, face, asleep=kind == "child_asleep")
        else:
            _held(ctx, layer, kind, a["rh"][0], a["rh"][1], h, i)
    ctx.focus = (mid / W, (_ground(ctx, mid) - h * .6) / H)
    ctx.marks["crowd"] = ctx.focus
    ctx.marks["group"] = (mid / W, _ground(ctx, mid) / H - 0.13)   # framed lower: people above the caption, scenery above them


def _daisies(ctx):
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    rng = ctx.rng("daisies")
    for _ in range(ctx.spec.daisies):
        x = rng.uniform(0, W * 1.2)
        y = _ground(ctx, x) + rng.uniform(H * 0.01, H * 0.12)
        if y > H - 4:
            continue
        r = H * rng.uniform(0.008, 0.016)
        # separate petals with gaps between them, seen a little from above, so a close-up reads as a daisy
        k0 = rng.uniform(0, 1)
        petals = []
        for k in range(11):
            t = 2 * math.pi * (k + k0) / 11
            c, s_ = math.cos(t), math.sin(t)
            petals.append(("poly", [(x + r * (u * c - v * s_), y + r * .62 * (u * s_ + v * c))
                                    for u, v in ((.3, 0), (.55, .13), (.92, .1), (1, 0), (.92, -.1), (.55, -.13))]))
        _ink(ctx, layer, petals, LIGHT)
        _ink(ctx, layer, [("ellipse", (x - r * .3, y - r * .22, x + r * .3, y + r * .22))], YELLOW)


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
    ctx.marks["sign_box"] = (x0 / W, y0 / H, (x0 + bw) / W, (y0 + bh) / H)   # so a camera never cuts the board in half


def _house(ctx):
    """A small house with a lit window, standing on the stage clear of the gag."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    s = H * 0.06

    def crowded(x):   # ink already standing on the ledge where the house would go, plus a pull away from the gag
        y = int(_ground(ctx, x))
        box = layer.A[max(y - int(s * 1.4), 0): max(y - 3, 1), max(int(x - s * .8), 0): int(x + s * .8)]
        return float(box.mean()) if box.size else 1.0 + 0.3 * max(0.0, 0.3 - abs(x / W - ctx.focus[0]))
    x = ctx.spec.house_x * W if ctx.spec.house_x else min((W * f for f in (0.82, 0.18, 0.7, 0.3, 0.9, 0.1)), key=crowded)
    y = _ground(ctx, x)
    _ink(ctx, layer, house(x, y, s), ctx.dark)
    if layer.E is None:
        layer.E = np.zeros_like(layer.P)
    wP, wA = np.zeros_like(layer.P), np.zeros_like(layer.A)
    stamp(wP, wA, [("poly", [(x - s * .22, y - s * .22), (x + s * .02, y - s * .22), (x + s * .02, y - s * .44), (x - s * .22, y - s * .44)])], np.ones(3))
    layer.E += wA[..., None] * ctx.pal.light * 1.1
    glow(layer.E, x - s * .1, y - s * .33, 6, ctx.pal.light, 0.5)
    ctx.marks["house"] = (x / W, (y - s / 2) / H)


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
    if ctx.spec.house and ctx.spec.stage:
        _house(ctx)        # last, so it can find a patch of ledge the others left empty


def _gag_big_cloud(ctx):
    """One very large, very slow cloud, low over the hills, and the long shade it throws."""
    W, H = ctx.W, ctx.H
    layer = ctx.far_layer
    rng = ctx.rng("big_cloud")
    cx, cy, cw = W * rng.uniform(0.42, 0.58), H * 0.36, W * 0.95
    puffs = cloud(cx, cy, cw) + [("ellipse", (cx - cw * .38, cy - cw * .08, cx - cw * .02, cy + cw * .08)),
                                 ("ellipse", (cx + cw * .02, cy - cw * .22, cx + cw * .32, cy + cw * .06))]
    stamp(layer.P, layer.A, puffs, mix(LIGHT, ctx.pal.sky[1], 0.25), 0.97)
    stamp(layer.P, layer.A, [("ellipse", (cx - cw * .5, cy + cw * .02, cx + cw * .5, cy + cw * .085))], mix(LIGHT, ctx.dark, 0.35), 0.5)
    ctx.focus = (cx / W, (cy - cw * .05) / H)


def _moon_disc(ctx, layer, x, y, r, tag):
    base = mix(ctx.pal.accent, LIGHT, 0.45)
    # the shaded side is a darker disc showing round the edge of the lit one, so nothing spills outside the moon
    stamp(layer.P, layer.A, [("ellipse", (x - r, y - r, x + r, y + r))], mix(base, ctx.dark, 0.5), 1.0)
    stamp(layer.P, layer.A, [("ellipse", (x - r, y - r * .9, x + r * .8, y + r * .9))], base, 1.0)
    rng = ctx.rng(tag)
    for _ in range(5):
        cx, cy, cr = x + rng.uniform(-.55, .3) * r, y + rng.uniform(-.5, .5) * r, r * rng.uniform(.08, .18)
        stamp(layer.P, layer.A, [("ellipse", (cx - cr, cy - cr, cx + cr, cy + cr))], mix(base, ctx.dark, 0.18), 0.8)


def _two_moons(ctx, aligned):
    """Two moons that circle each other: apart, or lined up (the small one in front of the big one)."""
    W, H = ctx.W, ctx.H
    layer = ctx.far_layer
    y = H * 0.4
    big, small = W * 0.13, W * 0.075
    bx, sx = (W * 0.5, W * 0.52) if aligned else (W * 0.37, W * 0.67)
    _moon_disc(ctx, layer, bx, y, big, "moon_big")
    _moon_disc(ctx, layer, sx, y + (H * 0.01 if aligned else -H * 0.05), small, "moon_small")
    ctx.focus = (0.5, y / H)


def snowflake(x, y, r, width):
    """Six arms, each with two pairs of side branches: always the same shape."""
    shapes = []
    for k in range(6):
        a = math.pi / 2 + k * math.pi / 3
        ca, sa = math.cos(a), math.sin(a)
        shapes.append(("line", ([(x, y), (x + r * ca, y - r * sa)], width)))
        for f, b in ((0.45, 0.32), (0.72, 0.22)):
            bx, by = x + r * f * ca, y - r * f * sa
            for side in (-1, 1):
                ab = a + side * math.pi / 4
                shapes.append(("line", ([(bx, by), (bx + r * b * math.cos(ab), by - r * b * math.sin(ab))], width * 0.8)))
    return shapes


def _gag_same_flakes(ctx):
    """Every snowflake the same shape: a few big ones drifting down, all identical."""
    W, H = ctx.W, ctx.H
    layer = ctx.far_layer
    rng = ctx.rng("flakes")
    col = mix(LIGHT, ctx.pal.sky[1], 0.1)
    big = (W * 0.5, H * 0.42, W * 0.12)
    flakes = [big] + [(rng.uniform(0.08, 0.92) * W, rng.uniform(0.3, 0.6) * H, W * rng.uniform(0.025, 0.06)) for _ in range(9)]
    for x, y, r in flakes:
        if (x, y, r) != big and abs(x - big[0]) < big[2] * 1.6 and abs(y - big[1]) < big[2] * 1.6:
            continue
        stamp(layer.P, layer.A, snowflake(x, y, r, max(2.0, r * 0.07)), col, 0.95)
    ctx.focus = (big[0] / W, big[1] / H)


# --- dream_whale (the shared dream, a request concept in atlas/lore.py)

def _smooth(pts, n=6, closed=True):
    """Catmull-Rom through a handful of control points: a soft outline (closed) or a soft line (open)."""
    p = [np.asarray(q, np.float64) for q in pts]
    m = len(p)
    out = []
    for i in range(m if closed else m - 1):
        p0 = p[(i - 1) % m] if closed or i > 0 else p[0]
        p1, p2 = p[i], p[(i + 1) % m]
        p3 = p[(i + 2) % m] if closed or i + 2 < m else p[-1]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)))
    if not closed:
        out.append(tuple(p[-1]))
    return out


def _dotted_ring(poly, mask, off, gap):
    """Points every `gap` px along the outline pushed `off` px outwards, skipping any that come near the shape."""
    pts = np.array(poly)
    tang = np.roll(pts, -1, axis=0) - np.roll(pts, 1, axis=0)
    nrm = np.stack([tang[:, 1], -tang[:, 0]], 1)
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
    H, W = mask.shape
    probe = pts[0] + nrm[0] * off
    if mask[int(np.clip(probe[1], 0, H - 1)), int(np.clip(probe[0], 0, W - 1))] > 0.5:
        nrm = -nrm                                   # the outline ran the other way round: point the normals out
    ring = pts + nrm * off
    seg = np.linalg.norm(np.roll(ring, -1, axis=0) - ring, axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    k = int(off * 0.75)
    dots = []
    for d in np.arange(0, cum[-1], gap):
        i = min(int(np.searchsorted(cum, d, side="right")) - 1, len(ring) - 1)
        qx, qy = ring[i] + (ring[(i + 1) % len(ring)] - ring[i]) * ((d - cum[i]) / max(seg[i], 1e-6))
        iy, ix = int(qy), int(qx)
        box = mask[max(iy - k, 0):max(iy + k, 1), max(ix - k, 0):max(ix + k, 1)]
        if box.size and box.max() < 0.05:
            dots.append((qx, qy))
    return dots


def _gag_dream_whale(ctx):
    """The shared dream: a large, pale, very polite whale over two lit cottages, lifting its hat to ask the way.
    Thought-bubble dots rise from both windows to the same whale. The house on the ledge is props._house (drawn
    after the gag), so pin house_x; the neighbours' cottage is drawn here."""
    W, H = ctx.W, ctx.H
    layer = ctx.near_layer        # in front of every ridge (a far-layer whale loses its head behind tall spires),
    s = H * 0.06                  # and it pans with the cottages, so the dots stay joined to their windows
    hx = (ctx.spec.house_x or 0.72) * W          # pin house_x: props._house goes wherever the ledge is clear
    gy = _ground(ctx, hx)
    f = 1 if hx > W * 0.5 else -1                 # it faces the house, bowing towards it
    L = W * 0.5                                   # nose to fluke tip: 0.55 of the frame
    cx, cy = hx - f * L * 0.42, H * 0.515
    ca, sa = math.cos(-0.07), math.sin(-0.07)     # head dipped: a small bow

    def T(u, v):                                  # whale space (u towards the head, v up) to pixels
        return (cx + f * (u * ca - v * sa) * L, cy - (u * sa + v * ca) * L)
    pale = LIGHT
    shade = mix(LIGHT, ctx.pal.sky[1], 0.4)
    ink = mix(ctx.dark, ctx.pal.sky[0], 0.3)
    line = max(2.5, L * 0.008)

    # body and flukes as one outline, so the dotted dream-line can follow it round
    shape = [(0.50, -0.02), (0.49, 0.08), (0.44, 0.15), (0.33, 0.195), (0.18, 0.19), (0.02, 0.155), (-0.14, 0.105),
             (-0.28, 0.06), (-0.38, 0.042), (-0.445, 0.06), (-0.505, 0.115), (-0.56, 0.165), (-0.597, 0.152),
             (-0.575, 0.075), (-0.578, 0.01), (-0.6, -0.065), (-0.565, -0.078), (-0.5, -0.03), (-0.44, -0.004),
             (-0.38, -0.01), (-0.26, -0.035), (-0.10, -0.09), (0.06, -0.135), (0.22, -0.155), (0.36, -0.135), (0.46, -0.085)]
    poly = [T(*q) for q in _smooth(shape, 8)]
    # the whole whale is inked on its own sheet, then laid down at 0.9 so the night shows faintly through
    P, A = np.zeros_like(layer.P), np.zeros_like(layer.A)
    stamp(P, A, [("poly", poly)], pale)
    r = L * 0.0065
    dots = _dotted_ring(poly, A, L * 0.04, L * 0.032)        # only sketched in: it's a dream
    stamp(layer.P, layer.A, [("ellipse", (x - r, y - r, x + r, y + r)) for x, y in dots], pale, 0.6)
    for k in range(4):                                       # throat pleats
        pts = [T(u, v + 0.028 * k) for u, v in ((0.43, -0.075), (0.33, -0.115), (0.2, -0.13), (0.06, -0.115 + 0.01 * k))]
        stamp(P, A, [("line", (_smooth(pts, 6, closed=False), max(2.0, L * 0.007)))], shade, 0.9)
    # a closed, contented eye and a long, gentle smile
    ex, ey = T(0.33, 0.045)
    stamp(P, A, [arc_line(ex, ey, L * 0.028, 0.15, math.pi - 0.15, line * 1.1, 12)], ink)
    stamp(P, A, [("line", (_smooth([T(0.495, -0.03), T(0.42, -0.04), T(0.32, -0.035), T(0.27, -0.015)], 6, closed=False), line))], ink)

    # a small bowler hat, lifted clear of its head: round crown, a band, a brim curled up at both ends
    hcx, hcy = T(0.31, 0.275)
    hw = L * 0.085
    c, sn = math.cos(-f * 0.32), math.sin(-f * 0.32)

    def R(u, v):
        return (hcx + hw * (u * c - v * sn), hcy + hw * (u * sn + v * c))
    crown = [R(0.74 * math.cos(a), -0.1 - math.sin(a) ** 0.85) for a in np.linspace(0, math.pi, 20)]
    brim = [R(u, v) for u, v in ((-1.18, -0.2), (-1.08, -0.04), (-0.8, 0.04), (0, 0.07), (0.8, 0.04), (1.08, -0.04), (1.18, -0.2))]
    for col, wd in ((pale, hw * 0.16 + line * 2.2), (ink, hw * 0.16)):      # cream edge first, so it reads on a night sky
        ends = [("ellipse", (x - wd / 2, y - wd / 2, x + wd / 2, y + wd / 2)) for x, y in (brim[0], brim[-1])]
        crown_shape = ("line", (crown + [crown[0]], line * 2.2)) if col is pale else ("poly", crown)
        stamp(P, A, [crown_shape, ("line", (brim, wd))] + ends, col)
    stamp(P, A, [("poly", [R(-0.74, -0.1), R(0.74, -0.1), R(0.73, -0.26), R(-0.73, -0.26)])], mix(ink, LIGHT, 0.3))
    # ...by the near flipper, raised from behind the eye, its tip under the back of the brim
    fl = [(0.19, -0.08), (0.21, -0.01), (0.235, 0.08), (0.255, 0.17), (0.262, 0.235), (0.25, 0.268), (0.232, 0.262),
          (0.21, 0.205), (0.175, 0.12), (0.13, 0.04), (0.09, -0.02), (0.085, -0.07)]
    fpoly = [T(*q) for q in _smooth(fl, 6)]
    stamp(P, A, [("line", (fpoly + [fpoly[0]], line * 1.3))], mix(LIGHT, ctx.pal.sky[1], 0.7))
    stamp(P, A, [("poly", fpoly)], pale)
    root = [(0.2, -0.075), (0.205, -0.03), (0.15, -0.025), (0.085, -0.04), (0.08, -0.09), (0.2, -0.11)]
    stamp(P, A, [("poly", [T(*q) for q in _smooth(root, 6)])], pale)      # no outline where it joins the body
    layer.P = layer.P * (1 - 0.9 * A[..., None]) + 0.9 * P
    layer.A = layer.A * (1 - 0.9 * A) + 0.9 * A

    def bubbles(x0, y0, x1, y1, sizes, lean):
        n = len(sizes)
        for k, rr in enumerate(sizes):
            q = (k + 0.15) / (n - 0.4)
            bx, by = x0 + (x1 - x0) * q + lean * W * 0.012 * math.sin(q * math.pi), y0 + (y1 - y0) * q
            rad = H * rr
            stamp(layer.P, layer.A, [("ellipse", (bx - rad, by - rad, bx + rad, by + rad))], pale, 0.88)
    # one dream, from the house's lit window...
    bubbles(hx - s * 0.1, gy - s * 1.25, *T(0.12, -0.19), (0.0065, 0.0095, 0.013), f)
    # ...and exactly the same one from the neighbours' cottage, further along the ledge
    nx = hx - f * W * 0.5
    ny, ns = _ground(ctx, nx), s * 0.75
    _ink(ctx, layer, house(nx, ny, ns), ctx.dark)
    if layer.E is None:
        layer.E = np.zeros_like(layer.P)
    wP, wA = np.zeros_like(layer.P), np.zeros_like(layer.A)
    stamp(wP, wA, [("poly", [(nx - ns * .22, ny - ns * .22), (nx + ns * .02, ny - ns * .22), (nx + ns * .02, ny - ns * .44), (nx - ns * .22, ny - ns * .44)])], np.ones(3))
    layer.E += wA[..., None] * ctx.pal.light * 1.1
    glow(layer.E, nx - ns * .1, ny - ns * .33, 5, ctx.pal.light, 0.5)
    bubbles(nx - ns * 0.1, ny - ns * 1.3, *T(-0.18, -0.12), (0.005, 0.0075, 0.0105), -f)

    # the joke's close-up ("gag" framing, ~2x) is the face, the lifted hat and the house's dots; "dream" marks the
    # middle of the whole picture (whale, hat and both cottages) for a wider push-in
    fx, _ = T(0.3, 0.12)
    ctx.focus = (fx / W, 0.48)
    xs = [T(-0.6, 0)[0], T(0.5, 0)[0], hx, nx]
    ctx.marks["dream"] = ((min(xs) + max(xs)) / 2 / W, 0.515)

# GAGS entry:  "dream_whale": _gag_dream_whale,


# --- valley_clocks (the slow valleys, a request concept in atlas/lore.py)

# add to GAGS:  "valley_clocks": _gag_valley_clocks,
# (uses existing props.py helpers bench, _stage, _steam; new helpers _clock, _skyline, _raise_peak clash with nothing)


def _clock(ctx, layer, cx, cy, r, hour, minute, ink, blur=False):
    """A round clock face: dark rim, cream face, twelve ticks, two hands and a red pin. blur: the minute hand is
    going round so fast it leaves ghosts."""
    rim = r * 1.18
    _ink(ctx, layer, [("ellipse", (cx - rim, cy - rim, cx + rim, cy + rim))], ink)
    _ink(ctx, layer, [("ellipse", (cx - r, cy - r, cx + r, cy + r))], LIGHT)
    ticks = []
    for k in range(12):
        a = k * math.pi / 6
        r0 = r * (0.64 if k % 3 == 0 else 0.76)
        ticks.append(("line", ([(cx + r0 * math.sin(a), cy - r0 * math.cos(a)),
                                (cx + r * .9 * math.sin(a), cy - r * .9 * math.cos(a))], r * (0.13 if k % 3 == 0 else 0.06))))
    _ink(ctx, layer, ticks, ink, 0.9)

    def hand(a, ln, w):
        return ("line", ([(cx - ln * .2 * math.sin(a), cy + ln * .2 * math.cos(a)), (cx + ln * math.sin(a), cy - ln * math.cos(a))], w))
    ha = (hour % 12 + minute / 60) / 12 * 2 * math.pi
    ma = minute / 60 * 2 * math.pi
    if blur:
        for j, back in enumerate((0.95, 0.6, 0.3)):
            _ink(ctx, layer, [hand(ma - back, r * .8, r * .1)], ink, 0.16 + 0.12 * j)
    _ink(ctx, layer, [hand(ha, r * .5, r * .17), hand(ma, r * .8, r * .1)], ink)
    _ink(ctx, layer, [("ellipse", (cx - r * .13, cy - r * .13, cx + r * .13, cy + r * .13))], ctx.spot)


def _skyline(layer, w):
    """The top row of a layer's solid ground in each column (its height where the column is empty)."""
    A = layer.A[:, :w] > 0.5
    return np.where(A.any(axis=0), A.argmax(axis=0), layer.A.shape[0]).astype(np.float32)


def _raise_peak(ctx, layer, px, sy, hw, flat, side, rng):
    """Push a craggy summit up out of a layer's ridge to the height sy at px, hazed with depth like the rest of the layer.
    Returns the new ridge line per column (None if the layer has no room for one)."""
    H = ctx.H
    P, A = layer.P, layer.A
    w = A.shape[1]
    top = _skyline(layer, w)
    solid = A[:, :w] > 0.5
    floor = int(np.median(H - np.argmax(solid[::-1], axis=0)))       # where the layer stops: the frame's foot, or a waterline
    # depth below the ridge -> colour, read off the layer's own columns (the haze thickens the same way in each)
    D = int(min(H * 0.32, floor - np.percentile(top, 80) - 2))
    cols = [c for c in np.linspace(0, w - 1, 48).astype(int) if top[c] + D < floor]
    if D < 8 or len(cols) < 6:
        return None
    table = np.median(np.stack([P[int(top[c]):int(top[c]) + D, c] for c in cols]), axis=0)
    x0, x1 = 0, w                     # the whole width, so both flanks run down into the hills before they end
    xs = np.arange(x0, x1, dtype=np.float32)
    dx = xs - px
    out = dx * side > 0                                                # the far flank, away from the valley
    cap = np.where(out, flat, flat * 0.3)                              # a small shelf on top, most of it on the far side
    run = np.clip(np.abs(dx) - cap, 0, None)
    # straight steep flanks broken up like the rest of the range: big creases, small crags, a shoulder on the far side
    k1 = np.arange(x0 - 80, x1 + 80, 34, dtype=np.float32)
    k2 = np.arange(x0 - 80, x1 + 80, 11, dtype=np.float32)
    crag = H * (0.03 * np.abs(np.interp(xs, k1, rng.uniform(-1, 1, len(k1)))) + 0.006 * np.interp(xs, k2, rng.uniform(-1, 1, len(k2))))
    s0 = hw * rng.uniform(0.38, 0.5)
    shoulder = H * 0.045 * np.exp(-((run - s0) / (hw * 0.08)) ** 2) * out
    prof = (sy + np.abs(dx).clip(0, flat) * 0.12 * out + run * np.where(out, 1.2, 1.55) + crag * np.clip(run / flat, 0, 1) - shoulder).astype(np.float32)
    sel = prof < top[x0:x1] + 1
    if not sel.any():
        return None
    yy = np.arange(H, dtype=np.float32)[:, None]
    a = np.clip(yy - prof[None, :] + 0.5, 0, 1) * (yy < floor)
    soft = np.convolve(np.pad(prof, 40, mode="edge"), np.ones(81) / 81, mode="same")[40:-40]
    # haze by depth under the smoothed ridge (no streaks under the crags), meeting the old ridge's own haze where they join
    d = np.clip(yy - np.minimum(soft, top[x0:x1])[None, :], 0, D - 1).astype(int)
    newP = table[d] * a[..., None]
    reg = (slice(None), slice(x0, x1))
    keep = ~sel[None, :]
    P[reg] = np.where(keep[..., None], P[reg], newP + P[reg] * (1 - a[..., None]))
    A[reg] = np.where(keep, A[reg], a + A[reg] * (1 - a))
    return np.minimum(prof, top)


def _gag_valley_clocks(ctx):
    """The slow valleys: the clock down in the valley says five past nine; the one up on the peak says twenty to five."""
    W, H = ctx.W, ctx.H
    if ctx.stage_y is None:
        _stage(ctx, 0.72)
    near, hill = ctx.near_layer, ctx.mid_layer
    rng = ctx.rng("valley_clocks")
    # the peak: pushed up out of the middle hills, on whichever side they already climb higher
    top = _skyline(hill, W)
    sides = [(float(top[int(W * .62):int(W * .76)].min()), W * 0.69), (float(top[int(W * .24):int(W * .38)].min()), W * 0.31)]
    px = min(sides)[1] + W * rng.uniform(-0.02, 0.02)
    sy = H * 0.49
    sgn = 1 if px > W * 0.5 else -1                   # which side the peak is on; the valley clock takes the other
    r_hi = W * 0.04
    ground = _raise_peak(ctx, hill, px, sy, W * 0.36, r_hi * 2.0, sgn, rng)
    if ground is None:                                # no room to raise one: the hills' own top, kept out of the text
        ground = np.clip(top, H * 0.45, H * 0.62)
        sy = float(ground[int(px)])
    hc = hill.P[min(int(sy) + 8, H - 1), int(px)]
    ink_hi = mix(ctx.dark, hc, 0.2)
    cy_hi = sy - H * 0.028 - r_hi
    _ink(ctx, hill, [("line", ([(px, sy + 6), (px, cy_hi)], r_hi * .22)),
                     ("poly", [(px - r_hi * .34, sy + 6), (px + r_hi * .34, sy + 6), (px + r_hi * .16, sy - r_hi * .25), (px - r_hi * .16, sy - r_hi * .25)])], ink_hi)
    _clock(ctx, hill, px, cy_hi, r_hi, 4, 40, ink_hi, blur=True)
    # someone up there in a hurry, already with a long white beard and a stick
    hw = H * 0.04
    wx = px + sgn * r_hi * 1.5
    wy = float(ground[int(wx)])
    a = _person(ctx, hill, wx, wy + 2, hw, "walk", -sgn, color=ink_hi)
    sx, sy_ = a["rh"]
    _ink(ctx, hill, [("line", ([(sx, sy_ - hw * .02), (sx - sgn * hw * .1, wy + 2)], max(1.5, hw * .04)))], ink_hi)
    hx, hy = a["head"]
    f = -sgn
    _ink(ctx, hill, [("poly", [(hx + f * hw * .02, hy + hw * .03), (hx + f * hw * .14, hy), (hx + f * hw * .15, hy + hw * .18),
                               (hx + f * hw * .1, hy + hw * .34), (hx + f * hw * .06, hy + hw * .44), (hx + f * hw * .03, hy + hw * .3)])], LIGHT)
    sky = ctx.sky_P[int(wy - hw * .6), int(min(max(wx + sgn * hw * .5, 0), W - 1))]
    whoosh = ctx.dark if 0.2126 * sky[0] + 0.7152 * sky[1] + 0.0722 * sky[2] > 0.55 else LIGHT
    for j in range(3):
        ly = wy - hw * (0.42 + 0.17 * j)
        _ink(ctx, hill, [("line", ([(wx + sgn * hw * .3, ly), (wx + sgn * hw * (.62 + .1 * j), ly)], max(1.5, hw * .035)))], whoosh, 0.8)
    # the low clock: on the valley floor, across the frame
    vx = px - sgn * W * 0.33
    vy = _ground(ctx, vx)
    r_lo = W * 0.05
    cy_lo = min(vy - H * 0.085 - r_lo, H * 0.615)     # a lower ledge gets a taller post, so the face stays above the caption
    _ink(ctx, near, [("line", ([(vx, vy + 4), (vx, cy_lo)], r_lo * .2)),
                     ("poly", [(vx - r_lo * .4, vy + 4), (vx + r_lo * .4, vy + 4), (vx + r_lo * .2, vy - r_lo * .3), (vx - r_lo * .2, vy - r_lo * .3)]),
                     ("ellipse", (vx - r_lo * .18, cy_lo - r_lo * 1.42, vx + r_lo * .18, cy_lo - r_lo * 1.06))], ctx.dark)
    _clock(ctx, near, vx, cy_lo, r_lo, 9, 5, ctx.dark)
    # and someone down here in no hurry at all: a bench, a cup of tea
    bx = vx + sgn * W * 0.1
    by = _ground(ctx, bx)
    h = H * G
    _ink(ctx, near, bench(bx, by, h * 1.15), ctx.dark)
    a = _person(ctx, near, bx - sgn * h * .12, by - h * .02, h, "sit", sgn)
    hx, hy = a["rh"]
    _ink(ctx, near, [("poly", [(hx - h * .06, hy - h * .1), (hx + h * .06, hy - h * .1), (hx + h * .05, hy + h * .04), (hx - h * .05, hy + h * .04)])], LIGHT)
    _steam(ctx, near, hx, hy - h * .12, h * .35)
    top_, bot = cy_hi - r_hi * 1.2, cy_lo + r_lo * 1.2
    ctx.focus = ((px + vx) / 2 / W, ((top_ + bot) / 2 - H * 0.036) / H)
    ctx.marks["clock_high"] = (px / W, cy_hi / H)
    ctx.marks["clock_low"] = (vx / W, cy_lo / H)


# --- uphill_river (the uphill rivers, a request concept in atlas/lore.py)

# ---- the uphill rivers ------------------------------------------------------------------------------------------

def _ur_mask(H, w, shapes):
    """Rasterise shapes into a fresh (H, w) coverage mask."""
    m = np.zeros((H, w), np.float32)
    if shapes:
        stamp(np.zeros((H, w, 3), np.float32), m, shapes, np.ones(3, np.float32))
    return m


def _ur_wash(layer, m, color, shine=0.0):
    """Lay an ink into a layer through a coverage mask (the mask may be wider or narrower than the layer);
    shine also lights it a little in the layer's emissive buffer."""
    w = min(layer.A.shape[1], m.shape[1])
    rows = np.flatnonzero(m[:, :w].max(axis=1) > 0)
    if not len(rows):
        return
    r0, r1 = rows[0], rows[-1] + 1
    mm = m[r0:r1, :w]
    col = np.asarray(color, np.float32)
    layer.P[r0:r1, :w] = layer.P[r0:r1, :w] * (1 - mm[..., None]) + col * mm[..., None]
    layer.A[r0:r1, :w] = layer.A[r0:r1, :w] * (1 - mm) + mm
    if shine:
        if layer.E is None:
            layer.E = np.zeros_like(layer.P)
        layer.E[r0:r1, :w] += mm[..., None] * col * shine


def _ur_bezier(p0, p1, p2, p3, n):
    s = np.linspace(0, 1, n)[:, None]
    q = (1 - s) ** 3 * np.array(p0) + 3 * (1 - s) ** 2 * s * np.array(p1) + 3 * (1 - s) * s ** 2 * np.array(p2) + s ** 3 * np.array(p3)
    return q[:, 0], q[:, 1]


def _ur_meander(x, y, amp, waves, ph, flat=0.5):
    """Swing a centre line from side to side across its own direction, dying away towards its end and squashed
    vertically (the valley is seen from low down)."""
    s = np.linspace(0, 1, len(x))
    dx, dy = np.gradient(x), np.gradient(y)
    L = np.hypot(dx, dy) + 1e-6
    k = amp * np.sin(2 * math.pi * waves * s + ph) * (1 - s) ** 0.7 * np.minimum(1, s * 5 + 0.2)
    return x - dy / L * k, y + dx / L * k * flat


def _ur_ribbon(x, y, w):
    """A band of width w along a centre line, its end rounded off."""
    dx, dy = np.gradient(x), np.gradient(y)
    L = np.hypot(dx, dy) + 1e-6
    nx, ny = -dy / L, dx / L
    left = list(zip(x + nx * w / 2, y + ny * w / 2))
    right = list(zip(x - nx * w / 2, y - ny * w / 2))
    return [("poly", left + right[::-1]), ("ellipse", (x[-1] - w[-1] / 2, y[-1] - w[-1] / 2, x[-1] + w[-1] / 2, y[-1] + w[-1] / 2))]


def _ur_ripples(x, y, w, H, gap=1.7, lo=7):
    """Little '^' ripples along the stretches of a river that climb, pointing the way the water goes (towards the
    end of the course)."""
    out = []
    dx, dy = np.gradient(x), np.gradient(y)
    L = np.hypot(dx, dy) + 1e-6
    arc = np.concatenate([[0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
    nxt = 8.0
    for k in range(2, len(x) - 4):
        if arc[k] < nxt:
            continue
        wk = w[k]
        tx, ty = dx[k] / L[k], dy[k] / L[k]
        if wk < lo or y[k] > H - 2 or ty > -0.3:     # only where the water is going up
            continue
        nxt = arc[k] + max(wk * gap, 12)
        px, py = -ty, tx
        hw = wk * 0.27
        cx, cy = x[k], y[k]
        pts = [(cx - tx * hw * 0.5 + px * hw, cy - ty * hw * 0.5 + py * hw),
               (cx + tx * hw * 0.25 + px * hw * 0.45, cy + ty * hw * 0.25 + py * hw * 0.45),
               (cx + tx * hw * 0.5, cy + ty * hw * 0.5),
               (cx + tx * hw * 0.25 - px * hw * 0.45, cy + ty * hw * 0.25 - py * hw * 0.45),
               (cx - tx * hw * 0.5 - px * hw, cy - ty * hw * 0.5 - py * hw)]
        out.append(("line", (pts, max(1.7, wk * 0.1))))
    return out


def _ur_pool(x, y, a, d):
    """A pool seen from a little below: (the bank showing under its front edge, the water)."""
    return [("ellipse", (x - a * 0.99, y - d * 0.8, x + a * 0.99, y + d * 1.28))], [("ellipse", (x - a, y - d, x + a, y + d))]


def _ur_spray(x, y, w):
    """Water thrown up where a climbing fall tips over into the pool above it: a crown and a few drops."""
    out = []
    for side in (-1, 1):
        out.append(("line", ([(x + side * w * 0.35, y), (x + side * w * 0.62, y - w * 0.55), (x + side * w * 0.95, y - w * 0.9),
                              (x + side * w * 1.3, y - w * 1.0)], max(1.6, w * 0.16))))
    for u, v, r in ((-0.75, -1.55, 0.17), (0.0, -1.9, 0.2), (0.8, -1.6, 0.16), (-0.25, -1.35, 0.12)):
        cx, cy = x + u * w, y + v * w
        out.append(("ellipse", (cx - r * w, cy - r * w * 1.25, cx + r * w, cy + r * w * 1.25)))
    return out


def _gag_uphill_river(ctx):
    """Every river runs uphill: two rivers meet in the valley and climb the highest mountain a pool at a time, up a
    staircase of little falls that splash at the top, into one lake. The lake is nearly at the red line on its
    gauge, and somebody is checking."""
    W, H = ctx.W, ctx.H
    far, mid, near = ctx.far_layer, ctx.mid_layer, ctx.near_layer
    rng = ctx.rng("uphill_river")
    fr = ctx.far_ridge

    # ---- the lake: on the broadest high part of the far ridge near the middle, clear of the text band
    a = W * 0.07                                       # half-width
    d = a * 0.2                                        # half-depth of the surface (seen from a little below)
    best = None
    for x in np.arange(W * 0.34, W * 0.66, 6):
        crest = max(ctx.ridge_at(fr, u) for u in np.linspace(x - a * 1.15, x + a * 1.15, 15))
        y = max(crest + d * 1.8, H * 0.45)             # backed by rock all the way across
        score = y + abs(x - W * 0.5) * 0.25
        if best is None or score < best[0]:
            best = (score, float(x), float(y))
    _, lx, ly = best

    water_col = mix(LIGHT, mix(ctx.pal.water, ctx.pal.sky[2], 0.5), 0.2)
    lake_col = mix(LIGHT, ctx.pal.light, 0.15)
    mark_col = mix(water_col, ctx.dark, 0.45)
    # a pale far ridge (pastel, snow, noon) needs the water outlined to read
    gy = int(min(ly, H - 1))
    bg = far.P[gy, int(lx)] / max(float(far.A[gy, int(lx)]), 1e-3)
    pale = float(0.2126 * bg[0] + 0.7152 * bg[1] + 0.0722 * bg[2]) > 0.6

    # ---- the climb: a staircase of pools up the mountain face, each fall running up into the one above
    dirn = 1 if rng.random() < 0.5 else -1
    K = 3
    step = min(H * 0.036, max(H * 0.026, (H * 0.72 - ly) / K))     # the lowest pool stays above the caption
    pa = [a * f for f in (0.5, 0.44, 0.38)]
    py = [ly + step * (K - k) for k in range(K)]       # k = 0 lowest
    px = [0.0] * K
    px[K - 1] = lx - dirn * a * 0.55
    for k in range(K - 2, -1, -1):
        px[k] = px[k + 1] - dirn * (pa[k] + pa[k + 1]) * 0.62
    tops = [(px[k], py[k], pa[k], pa[k] * 0.22) for k in range(K)] + [(lx, ly, a, d)]
    banks, waters, falls, sprays = [], [], [], []
    for x, y, a_, d_ in tops:
        b, w_ = _ur_pool(x, y, a_, d_)
        banks += b
        waters += w_
    fw = W * 0.013
    for k in range(K):
        x0, y0, a0, _ = tops[k]
        x1, y1, a1, d1 = tops[k + 1]
        ox = x0 + dirn * a0 * 0.62                     # out of this pool's far end, straight up into the next
        iy = y1 + d1 * 0.5
        fx = ox + np.sin(np.linspace(0, math.pi, 40)) * fw * 0.25 * dirn
        falls.append((fx, np.linspace(y0, iy, 40), np.full(40, fw)))
        sprays += _ur_spray(ox, iy - fw * 0.2, fw)

    # ---- the river across the valley: wide in the foreground, swinging side to side, into the lowest pool
    n = 360
    s = np.linspace(0, 1, n)
    bx, by = px[0] - dirn * pa[0] * 0.5, py[0] + pa[0] * 0.15
    x0 = float(np.clip(bx + W * rng.uniform(-0.15, 0.15), W * 0.25, W * 0.75))
    ry = by + (H * 1.03 - by) * (1 - s) ** 1.5
    rx = x0 + (bx - x0) * (1 - (1 - s) ** 1.3)
    rx = rx + W * 0.16 * np.sin(2 * math.pi * 1.25 * s ** 0.75 + rng.uniform(0, 2 * math.pi)) * (1 - s) ** 0.8 * (1 - s ** 4)
    rw = W * 0.014 + (W * 0.07 - W * 0.014) * (1 - s) ** 1.4
    main = [(rx, ry, rw)]
    # a second river comes in across the valley from the far side of the frame and joins it on the way up
    k = int(rng.uniform(0.7, 0.8) * (n - 1))
    jx, jy = rx[k], ry[k]
    sd = 1 if jx > W * 0.5 else -1
    p0 = (W * 0.5 - sd * W * 0.53, jy + H * rng.uniform(0.06, 0.08))
    tx, ty = _ur_bezier(p0, (p0[0] + sd * W * 0.25, p0[1] - H * 0.01), (jx - sd * W * 0.1, jy + H * 0.035), (jx, jy), 260)
    tx, ty = _ur_meander(tx, ty, W * 0.035, 1.7, rng.uniform(0, 2 * math.pi), flat=0.55)
    sw = np.linspace(0, 1, 260)
    trib = [(tx, ty, rw[k] * 0.75 + (W * 0.03 - rw[k] * 0.75) * (1 - sw) ** 1.2)]

    # ---- the gauge, the water just short of its red line, and somebody reaching up to check it
    gx, gh, tw = lx + dirn * a * 0.7, H * 0.028, H * 0.0048
    tick = lambda f, t: [("line", ([(gx - tw, ly - gh * f), (gx + tw, ly - gh * f)], H * t))]
    post = [("line", ([(gx, ly + d * 0.3), (gx, ly - gh)], H * 0.0036))]
    body, coat, _ = figure(lx + dirn * a * 1.12, ly + d * 0.9, H * 0.03, "reach", -dirn)

    # The foreground reach is printed on the near ground and everything above it on the middle hills, lake and
    # all, so the whole climb moves as one in a pan. (Ground between the middle and near layers can hide a stretch
    # of the valley river: it reads as the river passing behind a hill.)
    Wm = max(mid.A.shape[1], near.A.shape[1])
    on_near = np.zeros((H, Wm), np.float32)
    on_near[:, :near.A.shape[1]] = near.A[:, :Wm] > 0.5
    up = 1 - on_near
    ribbons = lambda cs, grow=0.0: sum((_ur_ribbon(x, y, w + grow) for x, y, w in cs), [])
    ripples = lambda cs: sum((_ur_ripples(x, y, w, H) for x, y, w in cs), [])
    if pale:
        rims = [("ellipse", (x - a_ - 3, y - d_ - 3, x + a_ + 3, y + d_ + 3)) for x, y, a_, d_ in tops]
        _ur_wash(mid, _ur_mask(H, Wm, rims + ribbons(main + trib + falls, 5)) * up, mix(ctx.dark, bg, 0.45))
    _ur_wash(mid, _ur_mask(H, Wm, banks) * up, mix(water_col, ctx.dark, 0.4))
    _ur_wash(mid, np.maximum(_ur_mask(H, Wm, ribbons(main + trib + falls)), _ur_mask(H, Wm, waters)) * up, water_col, 0.1)
    _ur_wash(mid, _ur_mask(H, Wm, waters[-1:]) * up, lake_col, 0.15)
    lines = [("line", ([(lx - a * 0.62, ly - d * 0.15), (lx - a * 0.18, ly - d * 0.15)], max(1.5, d * 0.16))),
             ("line", ([(lx - a * 0.05, ly + d * 0.35), (lx + a * 0.3, ly + d * 0.35)], max(1.5, d * 0.16)))]
    _ur_wash(mid, _ur_mask(H, Wm, lines) * up, mix(lake_col, ctx.pal.water, 0.3))
    _ur_wash(mid, _ur_mask(H, Wm, ripples(main + trib + falls)) * up, mark_col)
    _ur_wash(mid, _ur_mask(H, Wm, sprays) * up, water_col, 0.1)
    _ur_wash(mid, _ur_mask(H, Wm, post + body + [coat]) * up, ctx.dark)
    _ur_wash(mid, _ur_mask(H, Wm, tick(0.55, 0.0026) + tick(0.8, 0.0026)) * up, LIGHT)
    _ur_wash(mid, _ur_mask(H, Wm, tick(0.24, 0.0042)) * up, ctx.spot)
    _ur_wash(near, _ur_mask(H, Wm, ribbons(main)) * on_near, water_col, 0.1)
    _ur_wash(near, _ur_mask(H, Wm, ripples(main)) * on_near, mark_col)

    ctx.marks["lake"] = (lx / W, ly / H)
    # framed on the climb, the lake a little above the middle: at the hook zoom (about 1.75-1.9) the gauge clears the
    # text and the lowest pool clears the caption
    ctx.focus = ((lx * 0.6 + px[0] * 0.4) / W, ly / H + 0.025)


# --- washed_up (the lost property coast, a request concept in atlas/lore.py)

def _wu_ell(x0, y0, x1, y1, n=18):
    """An ellipse as a polygon, so it turns with rotate()."""
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    return ("poly", [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)])


def _wu_tilt(shapes, ax, ay, theta):
    return rotate([_wu_ell(*g) if k == "ellipse" else (k, g) for k, g in shapes], ax, ay, theta)


def _wu_bbox(shapes):
    xs, ys = [], []
    for k, g in shapes:
        if k == "poly":
            pts = g
        elif k == "ellipse":
            pts = [(g[0], g[1]), (g[2], g[3])]
        else:
            pts = [(x + d * g[1] / 2, y + d * g[1] / 2) for x, y in g[0] for d in (-1, 1)]
        xs += [p[0] for p in pts]
        ys += [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def _wu_shift(shapes, dx, dy):
    out = []
    for k, g in shapes:
        if k == "poly":
            out.append((k, [(x + dx, y + dy) for x, y in g]))
        elif k == "ellipse":
            out.append((k, (g[0] + dx, g[1] + dy, g[2] + dx, g[3] + dy)))
        else:
            out.append((k, ([(x + dx, y + dy) for x, y in g[0]], g[1])))
    return out


def _wu_ring(cx, cy, r, w, flat=1.0, n=22):
    """A ring outline: flat < 1 is a ring lying down, seen a little from above."""
    return ("line", ([(cx + r * math.cos(a), cy + r * flat * math.sin(a)) for a in np.linspace(0, 2 * math.pi, n + 1)], w))


def sock(x, y, s, facing=1):
    """An odd sock hanging from the middle of its cuff at (x, y), toe pointing `facing`: (sock, cuff/heel/toe, stripes)."""
    f, w, L, fh = facing, s * .26, s * .66, s * .25
    X = lambda u: x + f * (u - w / 2)
    r, rh = fh / 2, w * .62
    tx = w + s * .46 - r
    toe = [(X(tx + r * math.cos(a)), y + L + r + r * math.sin(a)) for a in np.linspace(-math.pi / 2, math.pi / 2, 8)]
    heel = [(X(rh + rh * math.cos(a)), y + L + fh - rh + rh * math.sin(a)) for a in np.linspace(math.pi / 2, math.pi, 6)]
    body = [("poly", [(X(-.02 * s), y), (X(w + .02 * s), y), (X(w), y + L)] + toe + heel)]
    band = lambda a, b: ("poly", [(X(-.02 * s), y + s * a), (X(w + .02 * s), y + s * a), (X(w + .01 * s), y + s * b), (X(-.01 * s), y + s * b)])
    trim = [band(0, .12), ("poly", toe + [(X(tx - r * .1), y + L + fh), (X(tx - r * .1), y + L)]),
            ("poly", heel + [(X(rh), y + L + fh - rh)])]
    return body, trim, [band(.22, .3), band(.38, .46), band(.54, .62)]


def umbrella_open(x, y, s):
    """An open umbrella, ferrule at (x, y) and the canopy s wide below it, shaft down to a hooked handle."""
    cw, ch = s * .5, s * .34
    rim = y + s * .4
    pts = [(x + cw * math.cos(a), rim - ch * math.sin(a)) for a in np.linspace(0, math.pi, 15)]
    n = 4
    for k in range(n):
        pts.append((x - cw + (2 * k + 1) * cw / n, rim - s * .06))
        if k < n - 1:
            pts.append((x - cw + (2 * k + 2) * cw / n, rim))
    return [("poly", pts), ("line", ([(x, y), (x, rim - ch + 2)], s * .035)),
            ("line", ([(x, rim - ch * .5), (x, y + s * .95)], s * .04)),
            arc_line(x + s * .08, y + s * .95, s * .08, math.pi, 0, s * .045, n=10)]


def umbrella_boat(x, y, s):
    """An open umbrella upside down on the water, its waterline at (x, y): canopy for a hull, handle up for a mast."""
    cw, rim = s * .5, y - s * .27
    hull = [(x + cw * math.cos(a), min(rim + s * .4 * math.sin(a), y)) for a in np.linspace(0, math.pi, 17)]
    n = 4
    for k in range(n):       # the rib tips, now pointing up, with the cloth sagging between them
        hull.append((x - cw + (2 * k + 1) * cw / n, rim + s * .06))
        if k < n - 1:
            hull.append((x - cw + (2 * k + 2) * cw / n, rim - s * .03))
    return [("poly", hull), ("line", ([(x, rim + s * .05), (x, y - s * .9)], s * .04)),
            arc_line(x + s * .08, y - s * .9, s * .08, math.pi, 2 * math.pi, s * .045, n=10)]


def house_key(x, y, s):
    """A key lying on its side, bow centred at (x, y), shaft s long to the right, bit hanging below."""
    r = s * .17
    t = s * .08
    return [("line", ([(x + r * math.cos(a), y + r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 23)], t)),
            ("poly", [(x + r, y - t * .7), (x + s, y - t * .55), (x + s, y + t * .55), (x + r, y + t * .7)]),
            ("poly", [(x + r + t * .2, y - t * 1.1), (x + r + t * .9, y - t * 1.1), (x + r + t * .9, y + t * 1.1), (x + r + t * .2, y + t * 1.1)]),
            ("poly", [(x + s * .6, y), (x + s * .6, y + s * .16), (x + s * .68, y + s * .16), (x + s * .68, y + s * .1),
                      (x + s * .76, y + s * .1), (x + s * .76, y + s * .19), (x + s * .84, y + s * .19), (x + s * .84, y + s * .12),
                      (x + s * .92, y + s * .12), (x + s * .98, y)])]


def _wu_glint(ctx, layer, x, y, r):
    """A ring catching the light: a four-point star and a little glow."""
    _ink(ctx, layer, [("poly", [(x, y - r), (x + r * .16, y), (x, y + r), (x - r * .16, y)]),
                      ("poly", [(x - r * .75, y), (x, y + r * .14), (x + r * .75, y), (x, y - r * .14)])], LIGHT)
    bright = float(np.dot(ctx.pal.sky[2], (0.2126, 0.7152, 0.0722)))     # against a pale sea the glow only blurs it
    glow(layer.E, x, y, r * .35, mix(LIGHT, ctx.pal.light, 0.5), 0.85 - 0.55 * bright)


def _wu_people_xs(ctx):
    """Where props.extras will stand the crowd (it runs after the gag), so nothing lands under someone's feet."""
    sp, W = ctx.spec, ctx.W
    n = sp.crowd
    if not n:
        return []
    if sp.crowd_x:
        return list(sp.crowd_x * W + (np.arange(n) - (n - 1) / 2) * W * sp.crowd_gap)
    if sp.sign:
        return list(np.linspace(W * 0.08, W * 0.54, n))
    return list(np.linspace(W * 0.2, W * 0.8, n))


def _gag_washed_up(ctx):
    """The lost property coast: an umbrella, a kettle, house keys and a heap of wedding rings washed up along the
    waterline, odd socks hanging off them, and one more umbrella still sailing in, a sock for a flag."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    if ctx.stage_y is None:
        _stage(ctx, 0.72)            # the shore itself is down in the caption strip: give the tide a ledge
    if layer.E is None:
        layer.E = np.zeros_like(layer.P)
    red = ctx.spot

    def hung(px, py, s, facing, col, trim, stripes=None, ang=0.0):
        b, t, st = sock(px, py, s, facing)
        out = [(_wu_tilt(b, px, py, ang), col), (_wu_tilt(t, px, py, ang), trim)]
        return out + ([(_wu_tilt(st, px, py, ang), stripes)] if stripes is not None else [])

    # each item is built at the origin as [(shapes, colour), ...], then packed along the waterline
    items = []
    s = H * 0.052                                        # an umbrella on its side, a striped sock on the handle
    um = _wu_tilt(umbrella_open(0, 0, s), 0, 0, -1.92)
    hx, hy = max(um[-1][1][0], key=lambda p: p[1])
    items.append(("umbrella", [(um, red)] + hung(hx, hy - s * .02, H * 0.03, 1, LIGHT, red, red, 0.1)))
    k = H * 0.054                                        # the kettle, tipped back, a yellow sock over its spout
    kt = _wu_tilt(kettle(0, 0, k), 0, 0, -0.25)
    sx, sy = rotate([("poly", [(k * .5, -k * .48)])], 0, 0, -0.25)[0][1][0]
    items.append(("kettle", [(kt, LIGHT)] + hung(sx + k * .01, sy, H * 0.025, 1, YELLOW, red, None, 0.12)))
    r = W * 0.0145                                       # a surprising number of wedding rings
    wr = r * .36
    rings = [_wu_ring(-1.75 * r, -.45 * r, r, wr, .42), _wu_ring(1.75 * r, -.45 * r, r, wr, .42), _wu_ring(0, -.4 * r, r, wr, .42),
             _wu_ring(-.9 * r, -1.3 * r, r, wr), _wu_ring(.9 * r, -1.3 * r, r, wr), _wu_ring(0, -2.4 * r, r, wr, .9)]
    items.append(("rings", [(rings, YELLOW)]))
    kk = H * 0.035                                       # the house keys
    items.append(("key", [(_wu_tilt(house_key(0, 0, kk), 0, 0, -0.16), LIGHT)]))

    # pack them left to right round the centre, stepping round anyone the crowd will stand there: of all the ways
    # to do that, the one that keeps the row tight and centred (where the hook camera looks)
    gap = W * 0.011
    sink = H * 0.004
    boxes = [_wu_bbox([sh for grp in parts for sh in grp[0]]) for _, parts in items]
    widths = [bx[2] - bx[0] for bx in boxes]
    people = _wu_people_xs(ctx)
    obstacles = [(px, W * 0.03) for px in people]
    if ctx.spec.house and ctx.spec.house_x:
        obstacles.append((ctx.spec.house_x * W, W * 0.07))
    cx = W * 0.5
    total = sum(widths) + gap * (len(widths) - 1)

    def pack(start):
        xs, cur = [], start
        for w in widths:
            for _ in range(len(obstacles) + 1):
                hit = [ox + ow for ox, ow in obstacles if cur < ox + ow and cur + w > ox - ow]
                if not hit:
                    break
                cur = max(hit) + gap * .5
            xs.append(cur)
            cur += w + gap
        end = cur - gap
        spill = max(0.0, W * .275 - xs[0]) + max(0.0, end - W * .725)     # past the hook frame, under the cartographer
        return abs((xs[0] + end) / 2 - cx) + 0.5 * (end - xs[0] - total) + 3 * spill, xs
    xs = min((pack(st) for st in np.linspace(cx - total - W * .12, cx + W * .02, 90)), key=lambda c: c[0])[1]
    placed = {}
    for (name, parts), bx, x0 in zip(items, boxes, xs):
        gy = _ground(ctx, x0 + (bx[2] - bx[0]) / 2) - 2 + sink
        dx, dy = x0 - bx[0], gy - bx[3]
        for shapes, col in parts:
            _ink(ctx, layer, _wu_shift(shapes, dx, dy), col)
        placed[name] = (dx, dy, x0, x0 + bx[2] - bx[0])
    lo, hi = xs[0] - 4, placed["key"][3] + 4
    # half buried: the ledge covers whatever sank into it
    _ink(ctx, layer, [("poly", [(x, _ground(ctx, x) - 2) for x in np.linspace(lo, hi, 60)] +
                       [(hi, _ground(ctx, hi) + H * .03), (lo, _ground(ctx, lo) + H * .03)])], ctx.ground)
    dx, dy = placed["rings"][:2]                         # the rings catch the light
    _wu_glint(ctx, layer, dx + .9 * r + r * .75, dy - 1.3 * r - r * .7, r * 1.2)
    _wu_glint(ctx, layer, dx - r * .45, dy - 2.4 * r - r * .8, r * .9)

    # one still coming in: an umbrella upside down on the water, sailing in with a sock for a flag
    gy = _ground(ctx, cx)
    band = gy - ctx.spec.horizon * H
    if ctx.spec.water and band > H * 0.045:
        spots = [(placed["rings"][2] + placed["key"][3]) / 2, (placed["rings"][2] + placed["rings"][3]) / 2,
                 (placed["key"][2] + placed["key"][3]) / 2, (placed["kettle"][3] + placed["rings"][2]) / 2]
        bx_ = min(spots, key=lambda x: abs(x - cx) * .3 + sum(W * .2 for px in people if abs(x - px) < W * .06))
        wy = gy - min(max(band * 0.45, H * 0.034), H * 0.05)
        bs = H * 0.046
        _ink(ctx, layer, umbrella_boat(bx_, wy, bs), YELLOW)
        hx, hy = bx_ + bs * .16, wy - bs * .9
        for shapes, col in hung(hx, hy, H * 0.026, 1, red, LIGHT, None, -0.35):
            _ink(ctx, layer, shapes, col)
        t = max(2.0, H * .0013)
        _ink(ctx, layer, [("line", ([(bx_ - bs * .82, wy), (bx_ - bs * .36, wy)], t)), ("line", ([(bx_ + bs * .36, wy), (bx_ + bs * .82, wy)], t)),
                          ("line", ([(bx_ - bs * .5, wy + bs * .1), (bx_ - bs * .12, wy + bs * .1)], t)),
                          ("line", ([(bx_ + bs * .12, wy + bs * .1), (bx_ + bs * .5, wy + bs * .1)], t))], LIGHT, 0.7)
    ctx.focus = (cx / W, (gy - H * 0.04) / H)


# and in GAGS:  "washed_up": _gag_washed_up,


# --- coast_letters (the lighthouse letters, a request concept in atlas/lore.py)

def _envelope(x, y, w, ang):
    """An envelope seen from the back, centred at (x, y), w wide, turned by ang: (key line, sheet, flap, seal)."""
    h = w * 0.62
    k = max(2.0, w * 0.05)
    box = lambda a, b: [("poly", [(x - a, y - b), (x + a, y - b), (x + a, y + b), (x - a, y + b)])]
    tip = (x, y + h * 0.1)
    r = w * 0.085
    parts = (box(w / 2 + k, h / 2 + k), box(w / 2, h / 2),
             [("line", ([(x - w / 2, y - h / 2), tip, (x + w / 2, y - h / 2)], k * 0.9))],
             [("ellipse", (tip[0] - r, tip[1] - r, tip[0] + r, tip[1] + r))])
    return [rotate(s, x, y, ang) for s in parts]


def _paw(x, y, w, ang):
    """A paw print about 0.3 w across, centred on (x, y): the dog has signed this one."""
    r = w * 0.045
    toes = [(-0.12, -0.11), (-0.045, -0.165), (0.045, -0.165), (0.12, -0.11)]
    shp = [("ellipse", (x - w * 0.095, y - w * 0.07, x + w * 0.095, y + w * 0.07))]
    shp += [("ellipse", (x + u * w - r, y + v * w - r * 1.2, x + u * w + r, y + v * w + r * 1.2)) for u, v in toes]
    return rotate(shp, x, y, ang)


def _tower(x, gy, t, b):
    """A lighthouse standing at (x, gy), t tall, b half-width at the foot: (tower, lamp room, top of the tower)."""
    top = gy - t
    rail = max(3.0, t * 0.04)
    tower = [("poly", [(x - b, gy + 2), (x - b * 0.62, top), (x + b * 0.62, top), (x + b, gy + 2)])]
    room = [("poly", [(x - b * 0.95, top), (x + b * 0.95, top), (x + b * 0.95, top + rail), (x - b * 0.95, top + rail)]),
            ("poly", [(x - b * 0.45, top - t * 0.12), (x + b * 0.45, top - t * 0.12), (x + b * 0.45, top - t * 0.1), (x - b * 0.45, top - t * 0.1)]),
            ("line", ([(x - b * 0.42, top), (x - b * 0.42, top - t * 0.11)], max(1.5, b * 0.12))),
            ("line", ([(x + b * 0.42, top), (x + b * 0.42, top - t * 0.11)], max(1.5, b * 0.12))),
            ("poly", [(x - b * 0.6, top - t * 0.11), (x, top - t * 0.24), (x + b * 0.6, top - t * 0.11)])]
    return tower, room, top


def _striped(ctx, layer, x, gy, t, b, body, stripe, frame):
    """A white lighthouse with two red bands; returns where its lamp is."""
    tower, room, top = _tower(x, gy, t, b)
    _ink(ctx, layer, tower, body)
    for k in (0.22, 0.6):
        yb, yt = top + t * (k + 0.16), top + t * k
        wb, wt = b * (0.62 + 0.38 * (k + 0.16)), b * (0.62 + 0.38 * k)
        _ink(ctx, layer, [("poly", [(x - wt, yt), (x + wt, yt), (x + wb, yb), (x - wb, yb)])], stripe)
    _ink(ctx, layer, room, frame)
    return x, top - t * 0.055


def _gag_coast_letters(ctx):
    """Every cove has a lighthouse, and each keeper writes to the next one along the coast: across the water, the
    next cove's smaller striped lighthouse, the letters on their way between the two lamps, and one more lamp on the
    horizon where the route goes on."""
    layer, W, H = ctx.near_layer, ctx.W, ctx.H
    if layer.E is None:
        layer.E = np.zeros_like(layer.P)
    left = ctx.spec.shore != "right"
    d = 1 if left else -1                       # from our lighthouse out across the water
    th = H * 0.13                               # our lighthouse's height (render.build)
    hy = ctx.spec.horizon * H                   # the waterline
    if ctx.geo.get("lighthouse") is not None:
        lx = float(ctx.geo["lighthouse"])
        ly = ctx.ridge_at(ctx.near_ridge, lx) + 4 - th * 1.05      # its lamp
    else:                                       # no lighthouse charted: put up our own
        lx = W * (0.16 if left else 0.84)
        gy = _ground(ctx, lx)
        tower, room, top = _tower(lx, gy, th * 0.8, W * 0.024)
        _ink(ctx, layer, tower + room, ctx.dark)
        ly = top - th * 0.8 * 0.055
        glow(layer.E, lx, ly, 7, ctx.pal.light, 1.4)
    fx = lx + d * W * 0.58                      # close enough that a hook shot holds both lamps
    land = np.flatnonzero(np.asarray(ctx.near_ridge[:int(W)]) < H - 2)
    if 0 < len(land) < W * 0.8:                 # and out past the end of our shore
        fx = max(fx, land.max() + W * 0.12) if left else min(fx, land.min() - W * 0.12)
    fx = min(max(fx, W * 0.1), W * 0.9)
    haze = mix(ctx.pal.haze, ctx.pal.sky[2], 0.5)
    far = mix(ctx.dark, haze, 0.3)
    white = mix(LIGHT, haze, 0.2)
    # the next cove along: a low headland across the water and its lighthouse, half the size of ours
    base = hy + H * 0.004
    hw = W * 0.11
    rock = [(fx - hw * 1.1, base + 3)] + [(fx + hw * u, base - H * 0.022 * (1 - abs(u)) ** 0.6 - H * 0.004 * math.sin(u * 9))
                                         for u in np.linspace(-1.0, 0.8, 12)] + [(fx + hw * 0.85, base + 3)]
    _ink(ctx, layer, [("poly", rock)], far)
    fx, fy = _striped(ctx, layer, fx, base - H * 0.018, th * 0.55, W * 0.016, white, ctx.spot, far)
    glow(layer.E, fx, fy, 6, ctx.pal.light, 1.8)
    bA, bP = np.zeros_like(layer.A), np.zeros_like(layer.P)        # its beam, pointed back at ours
    reach = abs(fx - lx) * 0.75
    stamp(bP, bA, [("poly", [(fx, fy - 2), (fx - d * reach, fy - H * 0.035), (fx - d * reach, fy + H * 0.025), (fx, fy + 2)])], np.ones(3))
    gx = np.arange(bA.shape[1], dtype=np.float32)[None, :]
    layer.E += (bA * np.clip(1 - np.abs(gx - fx) / reach, 0, 1) ** 1.6 * 0.14)[..., None] * ctx.pal.light
    # and the cove after that, tiny on the horizon: the letters go all the way round
    nx = fx + d * min(W * 0.2, abs((W if left else 0) - fx) * 0.75)
    nx, ny = _striped(ctx, layer, nx, hy + 2, H * 0.024, W * 0.0055, mix(white, haze, 0.25), mix(ctx.spot, haze, 0.25), far)
    glow(layer.E, nx, ny, 3, ctx.pal.light, 1.2)
    # the route, dashed like a line on a map, in whichever ink shows against this sky
    sky = np.asarray(ctx.sky_P[max(int(min(ly, fy) - H * 0.08), 0), int((lx + fx) / 2)])
    ink = ctx.dark if float(np.dot(sky, [0.2126, 0.7152, 0.0722])) > 0.6 else LIGHT

    def dashes(P, t0, t1, step, width, value):
        for t in np.arange(t0, t1, step):
            _ink(ctx, layer, [("line", ([tuple(P(t)), tuple(P(t + step * 0.5))], width))], ink, value)
    p0, p1 = np.array([lx, ly]), np.array([fx, fy])
    low = max(ly, fy)
    c = np.array([(lx + fx) / 2, min(ly, fy) - H * 0.145])
    P = lambda t: (1 - t) ** 2 * p0 + 2 * t * (1 - t) * c + t * t * p1
    ts = np.linspace(0, 1, 41)
    while min(P(t)[1] for t in ts) < low - H * 0.235:      # lamps far apart in height: a flatter arc, so it all fits a hook shot
        c[1] += H * 0.005
    apex = min(P(t)[1] for t in ts)
    dashes(P, 0.05, 0.95, 0.03, max(2.0, H * 0.0016), 0.7)
    q1 = np.array([nx, ny])
    qc = np.array([(fx + nx) / 2, min(fy, ny) - H * 0.05])
    Q = lambda t: (1 - t) ** 2 * p1 + 2 * t * (1 - t) * qc + t * t * q1
    dashes(Q, 0.12, 0.9, 0.08, max(1.5, H * 0.0012), 0.45)
    # the letters in transit, smaller as they cross the bay, each with two strokes trailing behind it
    rng = ctx.rng("coast_letters")
    ew = W * 0.082
    for i, t in enumerate((0.2, 0.39, 0.58, 0.77)):
        x, y = P(t)
        tx, ty = (P(t + 0.01) - P(t - 0.01)) * d
        ang = max(-0.55, min(0.55, math.atan2(ty, tx))) + rng.uniform(-0.12, 0.12)
        w = ew * (1 - 0.32 * t)
        ux, uy = math.cos(ang) * d, math.sin(ang) * d
        for s in (-0.18, 0.18):
            ox, oy = x - ux * w * 0.62 - uy * w * s, y - uy * w * 0.62 + ux * w * s
            _ink(ctx, layer, [("line", ([(ox, oy), (ox - ux * w * 0.32, oy - uy * w * 0.32)], max(1.5, w * 0.035)))], ink, 0.75)
        key, sheet, flap, seal = _envelope(x, y, w, ang)
        _ink(ctx, layer, key, ctx.dark)
        _ink(ctx, layer, sheet, LIGHT)
        _ink(ctx, layer, flap, ctx.dark, 0.7)
        if i == 0:        # the one just sent is mostly about the weather, and a dog
            _ink(ctx, layer, _paw(x - math.sin(ang) * w * 0.07, y + math.cos(ang) * w * 0.07, w, ang), ctx.spot)
        else:
            _ink(ctx, layer, seal, ctx.spot)
    ctx.marks["far_lighthouse"] = (fx / W, fy / H)
    # between the lamps, with the letters' arc and the lower lamp centred a little below the middle of the frame
    ctx.focus = (float((lx + fx) / 2 / W), float(((apex - H * 0.025 + low) / 2 - H * 0.03) / H))


# and in GAGS:   "coast_letters": _gag_coast_letters,


GAGS = {
    "big_cloud": _gag_big_cloud, "same_flakes": _gag_same_flakes,
    "dream_whale": _gag_dream_whale, "valley_clocks": _gag_valley_clocks, "uphill_river": _gag_uphill_river,
    "washed_up": _gag_washed_up, "coast_letters": _gag_coast_letters,
    "two_moons": lambda ctx: _two_moons(ctx, False), "two_moons_aligned": lambda ctx: _two_moons(ctx, True),
    "chair_sleepers": _gag_chair_sleepers, "seabed_town": _gag_seabed_town, "slow_shout": _gag_slow_shout,
    "pole_post": _gag_pole_post, "kettles": _gag_kettles, "moon_letters": _gag_moon_letters,
    "glass_surfers": _gag_glass_surfers, "tiny_planet": _gag_tiny_planet, "umbrella_feet": _gag_umbrella_feet,
    "road_tourists": _gag_road_tourists, "tree_cloud": _gag_tree_cloud, "fainted_ghost": _gag_fainted_ghost, "ghost": _gag_ghost,
    "megaphones": _gag_megaphones, "stirrers": _gag_stirrers, "moth_roof": _gag_moth_roof,
}


def make_ctx(**kw):
    return SimpleNamespace(**kw)
