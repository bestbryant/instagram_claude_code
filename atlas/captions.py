"""Captions and alt text. Plain on purpose: the story, one line of context, three tags."""
from __future__ import annotations

from .render import Spec
from .text import CTA


def _footer(entry, by):
    found = f"Found for {by}. " if by else ""
    return f"{found}No. {entry['id']} in the atlas. {CTA}"


def carousel(entry: dict, by: str | None = None) -> str:
    return "\n\n".join([entry["name"], entry["story"], _footer(entry, by), " ".join(entry["tags"][:3])])


def reel(entry: dict, by: str | None = None) -> str:
    return "\n\n".join([entry["story"], _footer(entry, by), " ".join(entry["tags"][:3])])


def alt_text(entry: dict, spec: Spec) -> str:
    bits = []
    if spec.giant:
        bits.append("a ringed gas giant" if spec.ring else "a banded gas giant")
    if spec.big_moon:
        bits.append("an enormous cratered moon low on the horizon")
    if spec.suns == 2:
        bits.append("two suns")
    elif spec.suns == 1:
        bits.append("a low sun")
    if spec.moons:
        bits.append(f"{spec.moons} small moon{'s' if spec.moons > 1 else ''}")
    if spec.aurora:
        bits.append("green and violet aurora")
    if spec.islands:
        bits.append("floating islands with pines")
    if spec.moths:
        bits.append("giant moths")
    ground = {"peaks": "jagged mountain ranges", "hills": "rolling hills", "dunes": "sand dunes", "mesas": "flat-topped mesas",
              "spires": "needle-like spires", "crystal": "angular crystal ridges"}[spec.terrain]
    if spec.snow:
        ground = "snowy " + ground
    scene = [f"layers of {ground} fading into mist"]
    if spec.water:
        scene.append("a still sea reflecting the sky")
    if spec.glass_waves:
        scene.append("giant frozen waves of green glass")
    if spec.trees == "pines":
        scene.append("pine trees")
    elif spec.trees == "giant":
        scene.append("colossal pine trees")
    elif spec.trees == "lone":
        scene.append("a single round tree")
    if spec.lanterns:
        scene.append("glowing pumpkins along the shore")
    if spec.lighthouse:
        scene.append("a lighthouse on a cliff")
    if spec.house:
        scene.append("a small house with a lit window")
    if spec.figure:
        scene.append("a tiny lone figure")
    sky = _join(bits) if bits else "a starry sky"
    return (f"Screen-print style illustration of the imaginary planet {entry['name']}: {sky} above "
            f"{_join(scene)}. Printed on cream paper with the title '{entry['name']}, {entry['subtitle']}' underneath.")


def _join(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]
