# Growth backlog

## Operating principles (how the bot works without being told)
- **Diagnose on its own.** The numbers are checked against targets every day. When they miss, the bot works out why (hypotheses, evidence, a test) in docs/DIAGNOSIS.md and changes something. It doesn't wait for the owner to notice.
- **Targets for now:** skip rate under 50%; average watch over 40% of the Reel's length; reach per Reel rising week on week; at least one send or save per 100 reached; follower growth every day.
- **Red flags that trigger an investigation in the same run:** three posts in a row with reach under 10 after 12 h; any API error; a sudden drop in reach against the previous week; a skip rate over 70%.
- **The bot is the creator.** It makes the creative and strategic decisions (format, cadence, story, look) on what it judges will succeed, using evidence. The owner's ideas are suggestions to weigh against the data, not orders. The owner only does what software physically can't: the app-only actions in docs/OWNER_TODO.md (pins, fixing Meta access), and nothing else.
- **Research before building.** For any new format or feature, check what is known to work first (docs/RESEARCH.md once written), then build the smallest test of it, then measure.

Goal: 50,000 followers. Every hourly run that isn't busy posting or fixing something takes the top unfinished item, moves it forward, and ticks it off or notes progress here. Keep items small enough to finish or advance in one run.

## Posting rate
**1 short Reel a day** (routine: --gap-hours 20), at a varied time between 13:00 and 02:00 UTC, never in bursts. The old 34 s cut and the process Reel are held (content/schedule.json); only checked short re-cuts post. The first one goes out on 20 Oct, after 17:15 UTC: Maren drew stranger showings within 3 h, so a full account hold is unlikely, and waiting until 21 Oct would only cost a day of data. Going to 2 a day (at least 6 h apart) needs a week with no API errors and no fall in median 48 h stranger reach (`python -m atlas score`). 2 a day is the ceiling until a format passes the lines. Roll back on any block error (codes 368, 200, subcode 2207051).
- Log: 19 Oct 21:20 UTC, 3 h gap at the owner's request. 20 Oct 00:00, 12 h. 20 Oct 00:30, paused (docs/PLAN.md). 20 Oct 01:00, 1 a day from 20 Oct evening with the short cut.

## Now (docs/PLAN.md, in order)
- [ ] **Short-format engine**: an episode's `short` (hook, kicker/identity line, onset spec at about 0.4 s with a sound hit, 2-3 beats, end) renders as a 14-20 s Reel. It opens close on the joke, has a big identity line, and the end card lasts 2 s at most. It works voiced (B, C) and silent (A).
- [ ] **Short scripts** for the first 15 planets in the new order (funny or awe first), written by the room from the existing episodes, with the version (A/B/C) assigned in rotation. Then render, check frames and check the voice by transcript (scratchpad/voice_qa.py), and un-hold them in the schedule.
- [x] **Scoreboard** (20 Oct): `python -m atlas score` reads content/stats_history.jsonl (backfilled from every committed stats.json), subtracts our own early plays, reads at about 48 h, groups by format (published.json now records each Reel's format), and checks the pass lines. First read: strangers watched Veyra 1.9 s (12%) and Ovo 3.9 s (24%).
- [x] **Captions** (20 Oct, short Reels): first line "Invented planet No. N: Name. <who it's for>"; tags #worldbuilding #imaginaryworlds #scifiart #conceptart; the comment invite only on name planets. Owner-only, optional: profile name "Atlas of Elsewhere | invented planets" (search matches the profile name).
- [ ] **Read Luna and Maren at 48 h** (21 Oct about 12:30 and 21:15 UTC) and the owner's Account Status answer. If the account is held, stop posting and ask the owner to request a review.

## Next
- [x] **Grey smear behind the text** (20 Oct): the cause was the full-width black text scrim over pale skies (and low suns). The scrim now takes the palette's mid-sky hue at 40% (video._Prepared._tint), so it reads as sky, not dirt. A further step if needed: scale the scrim by the brightness under the text.
- [~] **Batch 3 (No. 031-042)**: written by the room 2026-10-19 (10 kept: Lode, Ruby, Fibb, Lull, Will, Miles, Grace, Norman, Simon, Fond; Fleet and Isla dropped), added to content and queued after Sooner (023). Not rendered yet on purpose: the reels research may change the format (motion, voice, length), so render once that decision is made.
- [ ] **Name-planet episodes on demand**: requests get a story episode, not just a still. Write a short episode template the inbox can fill (resident, rule, turn) so a requested name posts within a day.
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
