"""Smoke tests: any name must chart and render without errors.

Run: python -m pytest tests  (or python tests/test_smoke.py)
"""
import json
import random
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from atlas import captions, text  # noqa: E402
from atlas.lore import chart  # noqa: E402
from atlas.render import Spec, build, frame, seed_from, to_image  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def _names(n, seed=7):
    rnd = random.Random(seed)
    fixed = ["Biscuit", "grandma rose", "Ω", "a", "José", "Mr. Whiskers III", "東京", "x" * 40, "  spaced   out  "]
    rand = ["".join(rnd.choice(string.ascii_letters + " '-") for _ in range(rnd.randint(1, 18))).strip() or "q"
            for _ in range(n)]
    return fixed + rand


def test_random_names_render(n=60):
    for name in _names(n):
        entry, spec, seed = chart(name)
        img = to_image(frame(build(spec, seed, 216, 270), grain_seed=1))
        assert img.size == (216, 270)
        assert captions.carousel(entry) and captions.reel(entry) and captions.alt_text(entry, spec)


def test_same_name_same_planet():
    assert chart("Biscuit")[0] == chart("  biscuit ")[0]
    assert seed_from("Biscuit") == seed_from("BISCUIT")


def test_launch_entries_valid():
    for f in ("launch.json", "halloween.json"):
        for e in json.loads((ROOT / "content" / f).read_text()):
            spec = Spec(**e["spec"])
            img = to_image(frame(build(spec, seed_from(e["name"]), 216, 270), grain_seed=1))
            text.cover(img.resize((1080, 1350)), e)
            assert len(e["tags"]) <= 5
            assert len(captions.carousel(e)) < 2200, "Instagram caption limit"


def test_request_names():
    from atlas.__main__ import request_name
    cases = {"Biscuit!": "Biscuit", "do my dog Pepper": "Pepper", "please chart Grandma Rose 🙏": "Grandma Rose",
             "my cat's name is Toast": "Toast", "can you do Lisbon?": "Lisbon", "@friend look at this": None,
             "This is so beautiful, I love the colors": None, "wow": None, "https://spam.example": None}
    for comment, want in cases.items():
        assert request_name(comment) == want, (comment, request_name(comment))


if __name__ == "__main__":
    test_request_names()
    test_same_name_same_planet()
    test_launch_entries_valid()
    test_random_names_render(int(sys.argv[1]) if len(sys.argv) > 1 else 60)
    print("ok")
