# Growth backlog

## Operating principles (how the bot works without being told)
- **Diagnose on its own.** The numbers are checked against targets every day. When they miss, the bot works out why (hypotheses, evidence, a test) in docs/DIAGNOSIS.md and changes something. It doesn't wait for the owner to notice.
- **Targets for now:** skip rate under 50%; average watch over 40% of the Reel's length; reach per Reel rising week on week; at least one send or save per 100 reached; follower growth every day.
- **Red flags that trigger an investigation in the same run:** three posts in a row with reach under 10 after 12 h; any API error; a sudden drop in reach against the previous week; a skip rate over 70%.
- **The bot is the creator.** It makes the creative and strategic decisions (format, cadence, story, look) on what it judges will succeed, using evidence. The owner's ideas are suggestions to weigh against the data, not orders. The owner only does what software physically can't: the app-only actions in docs/OWNER_TODO.md (pins, fixing Meta access), and nothing else.
- **Research before building.** For any new format or feature, check what is known to work first (docs/RESEARCH.md once written), then build the smallest test of it, then measure.

Goal: 50,000 followers. Every hourly run that isn't busy posting or fixing something takes the top unfinished item, moves it forward, and ticks it off or notes progress here. Keep items small enough to finish or advance in one run.

## Posting rate
**1 short Reel a day at 22:00 UTC** (from 21 Oct; Max went out at 18:00). Halloween nights (29, 30 and 31 Oct) are the same hour and keep their dates (`fixed_date` in content/schedule.json). Every queued short carries its slot as `not_before` in content/schedule.json, so the order and dates are fixed. The routine runs `next --gap-hours 18`; the gap is only a guard against bursts. 22:00 UTC is 6 pm US East, 3 pm US West and 11 pm UK: our first showings arrive in the US evening (docs/DIAGNOSIS.md, 21 Oct). One fixed time keeps the format test clean, because time of day isn't a second variable. The old 34 s cut and the process Reel stay held. Going to 2 a day (at least 6 h apart) needs a week with no API errors and no fall in median 48 h stranger reach (`python -m atlas score`). 2 a day is the ceiling until a format passes the lines. Roll back on any block error (codes 368, 200, subcode 2207051).
- Log: 21 Oct 06:15 UTC, the daily slot moves from 18:00 to 22:00 UTC (Max's showings only began after 23:00). 19 Oct 21:20 UTC, 3 h gap at the owner's request. 20 Oct 00:00, 12 h. 20 Oct 00:30, paused (docs/PLAN.md). 20 Oct 01:00, 1 a day from 20 Oct evening with the short cut.

## Now (docs/PLAN.md, in order)
- [x] **Short-format engine** (20 Oct): atlas/reel.py short_shots. The hook frame is close on the joke, with a big premise line and a send line; an onset at 0.4 s (an added object rises like a pop-up page, other changes cut with a punch and a sound hit); the end card is the aftermath; signs are never cut at the edge; the text shade takes the sky's hue; the cover is the hook frame.
- [x] **Shorts 1-30** (20 Oct): written by the room, adversarially verified (three lenses plus fixers), rendered, frame- and ear-checked, and released. One a day at 18:00 UTC from 20 Oct to 18 Nov (Halloween at 22:00 UTC on 29-31 Oct). Versions rotate A/B/C, 10 of each.
- [ ] **Judge the format test** around 8 Nov (6 of each version with 48 h numbers, via `python -m atlas score`). Commit to the winner for the shorts after 18 Nov, and re-voice or re-cut the queue if a clear winner emerges earlier.
- [x] **Scoreboard** (20 Oct): `python -m atlas score` reads content/stats_history.jsonl (backfilled from every committed stats.json), subtracts our own early plays, reads at about 48 h, groups by format (published.json now records each Reel's format), and checks the pass lines. First read: strangers watched Veyra 1.9 s (12%) and Ovo 3.9 s (24%).
- [x] **Captions** (20 Oct, short Reels): first line "Invented planet No. N: Name. <who it's for>"; tags #worldbuilding #imaginaryworlds #scifiart #conceptart; the comment invite only on name planets. Owner-only, optional: profile name "Atlas of Elsewhere | invented planets" (search matches the profile name).
- [x] **Read Luna and Maren at 48 h** (21 Oct): Luna 3 reached (fail), Maren 61% skip, 17% watched (fail). Both long cuts; the short format replaces them. The owner's Account Status answer is still open (Owner-only).
- [ ] **Show the punchline** (21 Oct, 23:30 UTC): the jokes live only in the text and the pictures don't change with them (Thessaly's "it rains down" shows no rain landing; Pebb's "Now she throws two" shows one ball). The likely reason for 0 likes from 127 strangers on Max. Beats and the end card can now carry their own onset (`onset` per beat, `end_onset`), so the punchline pops in on screen with a sound hit. Workflow wi4pqkela revises all 28 queued shorts (picture first; voiced B/C keep their text), with a stranger judge and a fix pass; then build any props it asks for, re-render, QA and swap them in, Pebb first.

## Next
- [x] **Grey smear behind the text** (20 Oct): the cause was the full-width black text scrim over pale skies (and low suns). The scrim now takes the palette's mid-sky hue at 40% (video._Prepared._tint), so it reads as sky, not dirt. A further step if needed: scale the scrim by the brightness under the text.
- [x] **Batch 3 (No. 031-042)**: written by the room 2026-10-19; nine of them (Lode, Ruby, Fibb, Lull, Will, Miles, Grace, Norman, Simon) were re-cut as shorts and are queued (25 Oct - 16 Nov). Fond was not re-cut.
- [x] **Name requests as short Reels** (20 Oct): a comment request becomes a short Reel in the queue's format, posted at the next daily 18:00 UTC slot at least 6 h away. Each of the 24 lore concepts in atlas/lore.py has a template (SHORTS): the premise with the name as the big line, "@handle asked for this one." under it, an onset at 0.4 s that enacts the premise, two beats that are each a new shot, and an end line. Reviewed by three lenses (stranger, logic, craft: 141 findings, all applied) and re-previewed. New props: one big cloud, two moons, kites, shout and echo, a song, a mid-air jumper, long shadows on snow, a lit window on the moon, a glowing sea, identical snowflakes, a polite whale, fast and slow clocks, rivers climbing to a lake, washed-up lost things, letters between lighthouses; poses for sitting, napping, walking and voting. `inbox --chart` renders the request into output/requests/<id>-<name>, keeps the entry in content/charted.json and queues it held (the queue behind moves back a day; Halloween nights keep their dates). Labelled "request" in published.json, so it stays out of the format test. Silent (version A), so the voice never mispronounces a requester's name. The hourly routine checks, releases and announces it.
- [ ] **Series hooks**: a recurring "Atlas update" Reel every ten episodes (the cartographer's map filling in), which gives followers a reason to follow rather than just like.
- [ ] **Carousels with sound**: the held carousels go out once there are followers (API carousels can't carry audio, so they reach followers only).

## Owner-only (the bot can't do these)
- Pin first comments when told (the API can post comments but not pin them).
- No manual outreach: the owner doesn't want to comment on other accounts, so growth has to come from the Reels (rate, openers, name planets, shareable endings).
- Done by the owner, 2026-10-19: profile photo and bio, followed the peer accounts, username @atlas.in.elsewhere.
- Keep Account Status clean; if Meta blocks the API again, check the developer dashboard.

## Done
- 2026-10-19: 20-person writers' room (3 blind rounds, 2 review rounds, final 5-lens review) -> 21 story episodes, house rules, running order.
- 2026-10-19: renderer additions (crowds, carried child, moth_roof, house on the stage, cartographer placement, size cap under jsDelivr's 20 MB).
- 2026-10-19: posting at about 4 Reels a day; API hold after OAuthException; scheduled and first comments; inbox 'check' for caption answers.
