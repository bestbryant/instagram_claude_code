"""Captions and alt text. Searchable first line, the story, one closing line, three tags."""
from __future__ import annotations

from .render import Spec
from .text import invite_line


def _closing(entry, by, kind, question=True):
    lines = []
    if by:
        lines.append(f"Found for {by}.")   # the @mention notifies them; asking for reposts gets posts down-ranked
    if question and entry.get("question"):
        lines.append(entry["question"])
    lines.append(invite_line(entry, kind))
    return "\n".join(lines)


def carousel(entry: dict, by: str | None = None) -> str:
    # the story is already on slide 4, so the caption adds something the slides don't say
    parts = [f"Imaginary planet No. {entry['id']}: {entry['name']}. {entry['hook']}", entry.get("extra") or entry["story"],
             _closing(entry, by, "carousel"), " ".join(entry["tags"][:3])]
    return "\n\n".join(parts)


SHORT_TAGS = "#worldbuilding #imaginaryworlds #scifiart #conceptart"   # specific and on-topic; Instagram caps tags at 5


def reel(entry: dict, by: str | None = None) -> str:
    if entry.get("short"):
        # a plain, searchable first line; the episode's setting for anyone who reads on; the comment invite only on
        # name planets, where it's natural (repeating one ask on every post reads as engagement bait)
        ep = entry.get("episode") or {}
        parts = [f"Invented planet No. {entry['id']}: {entry['name']}. {entry['hook']}",
                 (ep.get("caption") or entry.get("extra") or entry["story"]).strip()]
        if by:
            parts.append(f"Found for {by}.")
        if entry.get("kicker") and not by:
            parts.append(invite_line(entry, "reel"))
        parts.append(SHORT_TAGS)
        return "\n\n".join(parts)
    head = f"{entry['hook']} (Imaginary planet No. {entry['id']}: {entry['name']})"
    ep = entry.get("episode") or {}
    if ep.get("caption"):
        # an episode's caption carries the setting the video has no room for, and ends on its own question
        parts = [head, ep["caption"].strip(), _closing(entry, by, "reel", question=False), " ".join(entry["tags"][:3])]
        return "\n\n".join(parts)
    parts = [head, entry.get("extra") or entry["story"], _closing(entry, by, "reel"), " ".join(entry["tags"][:3])]
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
    if spec.moons or spec.gag == "tiny_planet":
        n = spec.moons or 1
        bits.append(f"{['one', 'two', 'three', 'four'][min(n, 4) - 1]} small moon{'s' if n > 1 else ''}")
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
    scene = [] if spec.gag == "tiny_planet" else [f"layers of {ground} fading into mist"]
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
    if spec.lamp:
        scene.append("a tall lamp shining a beam straight up")
    if spec.crowd:
        scene.append("a row of people, each holding something different")
    if spec.daisies:
        scene.append("a meadow full of daisies")
    if spec.sign:
        scene.append("a sign reading '" + spec.sign.replace("|", " ") + "'")
    if spec.cartographer and spec.gag != "tiny_planet":   # the globe has its own cartographer
        scene.append("a small figure in a yellow coat holding a map")
    sky = _join(bits) if bits else "a starry sky"
    return (f"Screen-print style illustration of the imaginary planet {entry['name']}: {sky} above "
            f"{_join(scene)}. Printed on cream paper with the title '{entry['name']}' underneath.")


GAG_ALT = {
    "chair_sleepers": "people asleep in armchairs under blankets on the cliff",
    "seabed_town": "small wooden houses on the dry seabed, two of them half taken apart, and people carrying planks",
    "slow_shout": "a person shouting with cupped hands, the sound drawn as slow arcs crossing the valley towards someone far away, cupping an ear",
    "pole_post": "a postwoman reaching a letter up to a floating island on a very long pole",
    "kettles": "kettles steaming on warm rocks",
    "moon_letters": "children holding letters up to the moon, with more letters stuck to its surface",
    "glass_surfers": "surfers with boards standing under the frozen curl of a wave",
    "tiny_planet": "a tiny round planet floating in the dark, with one bakery, one tree, one lamp, one person in a yellow coat with a map, and one cat sitting on the only bench",
    "umbrella_feet": "people wearing red umbrellas on their feet",
    "road_tourists": "tourists lying on their backs in the road while locals walk around them",
    "tree_cloud": "one enormous tree with its own small rain cloud and a few lit houses in its branches",
    "fainted_ghost": "a small ghost that has fainted on the grass and a person looking down at it",
    "megaphones": "three people shouting through megaphones, sound rings spreading from each one",
    "stirrers": "people stirring the brown ground with giant wooden spoons",
    "moth_roof": "a cottage with one lit window and a moth the size of a kite sitting on its roof, looking in",
}


def _join(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]
