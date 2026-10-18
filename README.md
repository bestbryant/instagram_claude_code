# Atlas of Elsewhere 🪐

An Instagram account built around one idea: **an atlas of places that aren't on any map, one a day, and anyone can leave a name in the comments to get the planet that goes with it.**

Each entry is a screen-print style illustration on cream paper, a short written entry, and a 13-second Reel. The art is drawn by the code in this repo, not by an AI image model. See [STRATEGY.md §2](STRATEGY.md) for how the account avoids looking like AI slop.

This repo is the whole content engine. It draws the prints, sets the type, cuts the Reels (with an original soundtrack), writes plain captions and alt text, and can publish through Meta's official Graph API.

- **[STRATEGY.md](STRATEGY.md):** account setup, launch calendar, daily routine, growth plan to 50k, and what to avoid
- **[docs/PUBLISHING.md](docs/PUBLISHING.md):** manual posting, or automatic posting with the official API
- **`output/launch/`:** 12 ready-to-post worlds (carousel + Reel + captions each)
- **`output/grid-preview.jpg`:** how the profile will look
- **`output/profile-picture.jpg`:** the avatar

## Quick start

```bash
pip install -r requirements.txt     # numpy + Pillow; ffmpeg is needed for Reels

python -m atlas launch --jobs 4     # (re)render the 12 launch worlds
python -m atlas grid                # preview the profile grid
python -m atlas avatar              # profile picture

# someone commented "Biscuit": chart their planet
python -m atlas planet "Biscuit" --by @their_handle
#   -> output/requests/biscuit/{1-cover.jpg, 2-notes.jpg, reel.mp4, captions…}

# Halloween mini-series
python -m atlas launch --file content/halloween.json

# with the official API configured (docs/PUBLISHING.md)
python -m atlas next --base-url $BASE      # post the next scheduled item
python -m atlas inbox --chart              # turn comment requests into planets

python tests/test_smoke.py                 # smoke tests
```

The same name always produces the same planet, so a request can be re-rendered any time and comes out identical.

## How it works

| Module | What it does |
|---|---|
| `atlas/render.py` | Procedural landscapes: layered terrain (peaks, dunes, mesas, spires, crystal…), gas giants with rings, cratered moons, aurora, seas with reflections, floating islands, lighthouses, tiny figures. Built as parallax layers so stills and Reels share one world. Ends with a screen-print finish: k-means ink palette plus a spot colour, stochastic screening, paper texture. |
| `atlas/text.py` | The print layout (art on paper, title in the margin), the book-page notes slide, and Reel captions kept clear of Instagram's UI. |
| `atlas/reel.py` | 13-second 1080×1920 Reel: hook → story → name reveal, with slow parallax, twinkling stars and drifting particles. |
| `atlas/audio.py` | An original ambient pad per planet, so there are no music-licensing issues. |
| `atlas/lore.py` | Entries for name requests, each paired with the visuals it needs. |
| `atlas/captions.py` | Plain captions (story, one line, 3 hashtags) and alt text. |
| `atlas/publish.py` | Official Instagram Graph API publisher (carousels, Reels, comments). Uses tokens, never passwords. |
| `content/launch.json` | The 12 hand-written launch worlds. Edit freely. |
| `content/schedule.json` | Posting order used by `python -m atlas next`. |

Fonts: [Inter](https://github.com/rsms/inter) and [EB Garamond](https://github.com/octaviopardo/EBGaramond12), both under the SIL Open Font License (see `assets/fonts/`).
