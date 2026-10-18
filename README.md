# Atlas of Elsewhere 🪐

An Instagram account built around one idea: **an atlas of places that aren't on any map, one a day, and anyone can leave a name in the comments to get the planet that goes with it.**

Each planet has one absurd, ordinary problem (nine-minute nights, rain that falls up), a visual gag drawn into the print, a five-slide carousel and a looping Reel. The art is drawn by the code in this repo, not by an AI image model; the writing was drafted with Claude. See [STRATEGY.md](STRATEGY.md) for the research behind the formats and how the account avoids looking like AI slop.

This repo is the whole content engine. It draws the prints, sets the type, cuts the Reels (with an original soundtrack), writes plain captions and alt text, and can publish through Meta's official Graph API.

- **[STRATEGY.md](STRATEGY.md):** account setup, launch calendar, daily routine, growth plan to 50k, and what to avoid
- **[docs/PUBLISHING.md](docs/PUBLISHING.md):** manual posting, or automatic posting with the official API
- **`output/launch/`, `output/halloween/`, `output/sequels/`:** ready-to-post worlds (5-slide carousel, Reel, cover, captions, alt text)
- **`output/process/`, `output/specials/`:** "drawn in code" process Reels and the "Tap to stop" Reel
- **`output/grid-preview.jpg`:** how the profile will look
- **`output/profile-picture.jpg`:** the avatar

## Quick start

```bash
pip install -r requirements.txt     # numpy + Pillow; ffmpeg is needed for Reels

python -m atlas launch --jobs 4     # (re)render the 12 launch worlds
python -m atlas launch --file content/sequels.json   # Hush, part two
python -m atlas process 008         # "No image generator" process Reel
python -m atlas tapstop             # "Tap to stop. That's where you're moving."
python -m atlas grid                # preview the profile grid
python -m atlas avatar              # profile picture

# someone commented "Biscuit": chart their planet
python -m atlas planet "Biscuit" --by @their_handle
#   -> output/requests/biscuit/{1-cover.jpg, 2-notes.jpg, reel.mp4, captions…}

# Halloween mini-series
python -m atlas launch --file content/halloween.json

# with the official API configured (docs/PUBLISHING.md)
python -m atlas next --base-url $BASE      # post everything due today (day 1 = 2026-10-18)
python -m atlas inbox --chart              # turn comment requests into planets

python tests/test_smoke.py                 # smoke tests
```

The same name always produces the same planet, so a request can be re-rendered any time and comes out identical.

## How it works

| Module | What it does |
|---|---|
| `atlas/render.py` | Procedural landscapes: layered terrain (peaks, dunes, mesas, spires, crystal…), gas giants with rings, cratered moons, aurora, seas with reflections, floating islands, lighthouses, tiny figures. Built as parallax layers so stills and Reels share one world. Ends with a screen-print finish: k-means ink palette plus a spot colour, stochastic screening, paper texture. |
| `atlas/text.py` | The five carousel slides (print, close-up, book page, field guide, invitation) and Reel text kept clear of Instagram's UI. |
| `atlas/props.py` | Posable figures and one visual gag per planet (sleepers in armchairs, a seabed town, umbrellas worn on feet, a tiny globe with one of everything...), plus the cartographer in a yellow coat hidden in every print. |
| `atlas/video.py` | Shot-list Reel engine: hard cuts, push-ins, parallax, timed text, a tick on each cut. |
| `atlas/reel.py` | The looping planet Reel (hook on frame 1, close-up, punchline, name card), request Reels, and process Reels. |
| `atlas/audio.py` | An original ambient pad per planet, so there are no music-licensing issues. |
| `atlas/lore.py` | Entries for name requests, each paired with the visuals it needs. |
| `atlas/captions.py` | Keyword-first captions (story, local rule, a varied invitation, 3 hashtags) and alt text. |
| `atlas/publish.py` | Official Instagram Graph API publisher (carousels from GitHub-hosted images, Reels by direct upload, comments). Uses tokens, never passwords. |
| `content/launch.json` | The hand-written worlds: hook, beats, odd line, story, local rule, question, gag. Edit freely. |
| `content/schedule.json` | Posting order used by `python -m atlas next`. |

Fonts: [Inter](https://github.com/rsms/inter) and [EB Garamond](https://github.com/octaviopardo/EBGaramond12), both under the SIL Open Font License (see `assets/fonts/`).
