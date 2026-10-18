"""Captions and alt text. Searchable first line, the story, one closing line, three tags."""
from __future__ import annotations

from .render import Spec
from .text import INVITES, pick


def _closing(entry, by):
    lines = []
    if by:
        lines.append(f"Found for {by}. Repost it so they see their planet.")
    q = entry.get("question")
    lines.append((q + " " if q else "") + pick(INVITES, entry["id"] + entry["name"]))
    return "\n".join(lines)


def carousel(entry: dict, by: str | None = None) -> str:
    parts = [f"Imaginary planet No. {entry['id']}: {entry['name']}", entry["story"]]
    if entry.get("rule"):
        parts.append(f"Local rule: {entry['rule']}")
    parts += [_closing(entry, by), " ".join(entry["tags"][:3])]
    return "\n\n".join(parts)


def reel(entry: dict, by: str | None = None) -> str:
    head = f"{entry['hook']} (Imaginary planet No. {entry['id']}: {entry['name']})"
    parts = [head, entry.get("extra") or entry["story"], _closing(entry, by), " ".join(entry["tags"][:3])]
    return "\n\n".join(parts)


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
    gag = GAG_ALT.get(spec.gag)
    if gag:
        scene.append(gag)
    if spec.cartographer:
        scene.append("a small figure in a yellow coat holding a map")
    sky = _join(bits) if bits else "a starry sky"
    return (f"Screen-print style illustration of the imaginary planet {entry['name']}: {sky} above "
            f"{_join(scene)}. Printed on cream paper with the title '{entry['name']}' underneath.")


GAG_ALT = {
    "chair_sleepers": "people asleep in armchairs under blankets on the cliff",
    "seabed_town": "small wooden houses on the dry seabed, two of them half taken apart, and people carrying planks",
    "slow_shout": "a person shouting with cupped hands, the sound drawn as slow arcs crossing the valley, and someone far away reading a letter",
    "pole_post": "a postwoman reaching a letter up to a floating island on a very long pole",
    "kettles": "kettles steaming on warm rocks",
    "moon_letters": "children holding letters up to the moon, with more letters stuck to its surface",
    "glass_surfers": "surfers with boards standing under the frozen curl of a wave",
    "tiny_planet": "a tiny round planet with one bakery, one tree, one bench, one cat and a person in a yellow coat",
    "umbrella_feet": "people wearing red umbrellas on their feet",
    "road_tourists": "tourists lying on their backs in the road while locals walk around them",
    "tree_cloud": "one enormous tree with its own small rain cloud and a few lit houses in its branches",
    "fainted_ghost": "a small ghost that has fainted on the grass and a person looking down at it",
}


def _join(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]
