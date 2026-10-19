# Atlas of Elsewhere: growth strategy

**Goal:** 50,000 real followers.
**Concept:** an atlas of places that aren't on any map, one entry a day. Each planet has one absurd, very ordinary problem: nine-minute nights, rain that falls up, a tide that comes in every eleven years. It's told by a dry narrator who has been there and drawn as a screen-print style illustration. The growth mechanic is that **anyone can leave a name in the comments and get the planet that goes with it.**

Account: **@bestblueberrys** (rename it, see §6). Posting is automatic through Meta's official API (§5).

---

## 1. What the research said, and what changed

A critique of the first version and a fact-checked research pass (Oct 2026) found:

| Finding | Source | What we changed |
|---|---|---|
| Instagram's top ranking signals are **watch time, likes per reach and sends per reach**. Sends matter most for reaching non-followers. | Mosseri, via Social Media Today 2025 | Every planet is built around a joke worth sending to a friend, and hooks are framed around relatable habits ("A planet for people who reply to texts five days late"). |
| Reels have a **skip rate**: the share of viewers who leave in the first 3 seconds. | Instagram, Aug 2025 | The hook is on screen from **frame 1**, with motion immediately (push-in). |
| On-screen text needs **about 0.3 s per word**. | subtitle standards | Each text beat is timed to its word count. |
| Carousels get **re-served starting from slide 2**. | Mosseri / Buffer | 5 slides. Slide 2 is a standalone close-up plus one odd line. |
| **Replays count as views.** | Instagram, Apr 2025 | Reels end on the same wide shot they open on, so they loop. |
| Personalised **"your name" content** has a viral precedent (accounts gained 100k+ in days, 2020). | Refinery29, 2020 | Name requests are the main growth series. They get a real atlas number and a "Discovered by @you" credit. |
| Hashtags are capped at 5 and don't drive reach. Keywords do. | Dec 2025 | Captions open with "Imaginary planet No. 004: Maren". Max 3 tags. |
| Strange Planet (6M+) grew on **one fixed style, one deadpan voice, one recurring cast**. | Wikipedia / Variety | A recurring character, **the cartographer in a yellow coat**, is hidden in every print, and running institutions recur (the council, the postwoman, local rules). |
| Asking for a specific word or emoji in comments is down-ranked as engagement bait. | Meta guidelines | The invitation is worded differently each time. Questions are open-ended. |
| "AI slop" means low effort, mass-produced and samey. Viewers try to tell AI from human work. | Merriam-Webster 2025; ACM 2026 | Every print draws its own joke, and weekly process Reels show the layers being drawn in code. |

The old version's biggest problems were that the Reels cut the punchline, the prints didn't show the joke, and the first second was a static landscape. All three are fixed.

---

## 2. The content system

**Daily planet: carousel, 5 slides**
1. The print, with the hook in the margin ("The longest night on Veyra lasts nine minutes.")
2. A close-up of the visual gag with one odd line ("Population about 40,000. Most of them asleep in armchairs.")
3. The written entry, set like a book page
4. Field guide: day length, moons, gravity, population, and a **local rule** ("Naps longer than nine minutes must be registered with the council.")
5. "Your name has a planet too." (worded differently each time)

**Daily planet: Reel, 12–15 s, loops**
hook on frame 1 + push-in → close-up of the gag + setup line → punchline → name card on the opening shot. The cover is the gag plus a short hook.

**Name requests (the growth engine)**
"@sam asked for: Biscuit" on frame 1 → the planet → the punchline → "Found for @sam". The planet gets the next atlas number and "Discovered by @sam" on its plate. The caption asks them to repost it.

**Sequels.** Some entries end on an open question that pays off later. *Hush* (Oct 21): "He proposed across the valley in March. Her answer arrives Thursday." Then *Hush, part two* goes up that Thursday.

**Tap to stop.** Every planet flashes by. "Tap to stop. That's where you're moving." It drives comments ("I got Ovo").

**Process Reels, weekly.** "No image generator. Ovo is drawn in code, one layer at a time." This is the honest answer to "is this AI?" The art is code; the writing was drafted with Claude.

**Ideas queued for later** (from the research; build once the basics are working):
- Birth-month planets (13 slides)
- "Pick a planet" (3 doors)
- Weekly "Discovered this week" request roundup (up to 20 slides)
- Tourism-board posters
- "Real or Elsewhere?" quiz (one real NASA exoplanet fact against three of ours)
- A dictionary word per planet

---

## 3. Keeping it from looking like AI slop

- **Every print draws its own joke.** No interchangeable landscapes, and props are rationed (no spare moons, no stock cabin in every scene).
- **One narrator with a voice.** Specific details, harder punchlines, no em dashes, no "whimsical", no emoji bullets, no hashtag walls.
- **Recurring cast and institutions** reward people who follow along.
- **Show the process** every week.
- **Be honest.** The art is code, not an image generator, and the writing is AI-assisted. Never claim it's hand-drawn or human-written. If asked, say so plainly.
- **Add a human line** to request captions when you can. One sentence of your own beats any amount of polish.

---

## 4. Schedule (`content/schedule.json`)

Day 1 = Oct 18. The daily run posts whatever is due, so a missed day catches up.

| Day | Posts |
|---|---|
| 1 ✅ | Carousels: Elsewhere (pin it), Veyra, Orrin |
| 2 | Reel: Veyra |
| 3 | Reel: Ovo |
| 4 | Reel: Hush ("answer due Thursday"), carousel: Ovo |
| 5 | Reel: Kess, carousel: Hush |
| 6 | Reel: Maren, carousel: Kess |
| 7 | **Reel: Hush, part two** |
| 8 | Process Reel: Ovo (pin it) |
| 9 | Reel: Thessaly, carousel: Maren |
| 10 | Reel: Orrin, **Tap to stop** |
| 11 | Reel: Hollow (Halloween), carousel: Thessaly |
| 12 | Reel: Luma |
| 13 | Reel: Lantern, carousel: Hollow |
| 14 | Reel: Bramble, carousel: Luma |
| 15 | Reel: Mothwing (Halloween night, US), carousel: Lantern |
| 16–21 | Selk, process: Veyra, Cinderwake, Elsewhere Reel, process: Kess, remaining carousels |

Name-request planets go out on top of this, up to 2 a day.

---

## 5. What runs automatically

A Claude routine wakes this session **every day at 00:13 UTC** (evening in the Americas). Each run:
1. posts whatever is due in the schedule (official Graph API; images from GitHub, Reels uploaded directly)
2. reads recent comments, turns name requests into planets, posts up to 2 a day, and replies to the people who asked
3. refreshes the access token before it expires
4. logs everything to `content/published.json` and `content/requests.json`

To stop it, disable the routine "Atlas of Elsewhere: daily post" in your Claude routines.

---

## 6. Things only you can do (the API can't)

1. **Rename the account.** Profile → Edit profile → Username → `atlasofelsewhere` (or the closest available). The current handle, @bestblueberrys, doesn't match the brand.
2. **Name field:** `Atlas of Elsewhere · imaginary planets`. It currently reads "Claude Code". The name field is searchable, and a mismatched name makes the account look like a bot.
3. **Bio:**
   ```
   Places that aren't on any map. One a day.
   Leave a name in the comments and I'll find its planet.
   Illustrated in code.
   ```
4. **Profile photo:** `output/profile-picture.jpg`
5. **Pin** the Elsewhere post now, and the Ovo process Reel when it goes up (day 8).
6. **Stories** (they can't be fully automated with stickers): share each new post with a **Question sticker, "Name a planet"**, and once a week an **Add Yours** sticker ("the planet with your name").
7. **Check Account Status:** Settings → Account Status. If it says some content "can't be recommended", follow its steps. Recommendations to non-followers are the only reach a new account gets.
8. **Act like a person for a few minutes a day:** follow 15–20 illustration and worldbuilding accounts you actually like, and leave a real comment on two or three of their posts. An account that only ever posts through the API looks automated.
9. **Collabs, the only way to reach someone else's followers.** Once the profile is fixed, DM 3–5 small sci-fi or worldbuilding artists and offer them a planet named after them as a Collab Reel. The agent renders it and you post it from the app with the Collab invite: the API's collaborators field needs Facebook Login. Accept any collab invites you receive; that can't be done through this API either.
10. **After about a week, pin the 3 Reels with the most shares** (`python -m atlas stats` lists them).
11. **Security:** change your Instagram password and turn on two-factor authentication. Rotate the Meta **app secret** (it was pasted in chat). The access token keeps working after both.

---

## 6b. Cadence (changed 19 Oct after the reach research)

Reels only, about three a day (`next --asap --gap-hours 8`), so the queue runs in about a week and every Reel tests a hook. Not faster: Meta's spam policy covers "very high frequencies", accounts posting only through the API have drawn "suspected automation" warnings at 1–3 posts a day, and more volume didn't bring small accounts more followers. Carousels are held, because the API can't give them audio and Instagram doesn't show silent carousels to non-followers. Judge each Reel 48–72 h after it posts by shares, likes, watch time and skip rate, not day-1 reach. Trial Reels open at 200 followers (`trial_params`).

## 7. What not to do

- No bought followers, likes or views. No follow/unfollow, no pods, no "growth services".
- Don't reply to comments in bulk or with copy-paste text. Replies should be individual and spread out.
- Never re-upload the same Reel file. Re-cut it instead (Instagram's originality rules).
- Don't post AI-generated images or faces. They break the look, and AI-person profiles get labelled.

---

## 8. Honest expectations

| Milestone | Typical timing | What gets you there |
|---|---|---|
| 200 | first 2–3 weeks | daily Reels + first name requests. Unlocks Trial Reels, so hooks can be tested on non-followers. |
| 1,000 | weeks 3–8 | request flywheel + reposts by requesters |
| 10,000 | months 2–5 | one or two Reels breaking out (100k+ views) |
| 50,000 | months 5–12 | daily posting, requests as the main series, cross-posting to TikTok/Shorts/Pinterest |

**Check weekly in Insights:**
- skip rate (lower is better)
- sends per reach (the best growth predictor)
- comments per post (name requests)
- profile visits → follows

Make more of what gets sent. Stop what gets skipped.
