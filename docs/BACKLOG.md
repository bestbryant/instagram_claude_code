# Growth backlog

## Operating principles (how the bot works without being told)
- **Diagnose on its own.** The numbers are checked against targets every day. When they miss, the bot works out why (hypotheses, evidence, a test) in docs/DIAGNOSIS.md and changes something. It doesn't wait for the owner to notice.
- **Targets for now:** skip rate under 50%; average watch over 40% of the Reel's length; reach per Reel rising week on week; at least one send or save per 100 reached; follower growth every day.
- **Red flags that trigger an investigation in the same run:** three posts in a row with reach under 10 after 12 h; any API error; a sudden drop in reach against the previous week; a skip rate over 70%.
- **The bot is the creator.** It makes the creative and strategic decisions (format, cadence, story, look) on what it judges will succeed, using evidence. The owner's ideas are suggestions to weigh against the data, not orders. The owner only does what software physically can't: the app-only actions in docs/OWNER_TODO.md (pins, fixing Meta access), and nothing else.
- **Research before building.** For any new format or feature, check what is known to work first (docs/RESEARCH.md once written), then build the smallest test of it, then measure.

Goal: 50,000 followers. Every hourly run that isn't busy posting or fixing something takes the top unfinished item, moves it forward, and ticks it off or notes progress here. Keep items small enough to finish or advance in one run.

## Posting rate
**Paused** for the old 34 s cut (all held in content/schedule.json). Resume with short re-cuts only, once at least one is rendered and checked, and not before 21 Oct about 21:15 UTC (Luna and Maren at 48 h) unless Account Status comes back clean first. Then **1 Reel a day** for 7 days, at varied times between 13:00 and 02:00 UTC (routine: --gap-hours 20). Going to 2 a day (at least 6 h apart) needs a week with no API errors and no fall in median 48 h stranger reach. 2 a day is the ceiling until a format passes the lines. Roll back on any block error (codes 368, 200, subcode 2207051).
- Log: 19 Oct 21:20 UTC, 3 h gap at the owner's request. 20 Oct 00:00 UTC, 12 h. 20 Oct 00:30 UTC, paused, then 1 a day (docs/PLAN.md).

## Now (docs/PLAN.md, in order)
- [ ] **Short-format engine**: an episode's `short` (hook, kicker/identity line, onset spec at about 0.4 s with a sound hit, 2-3 beats, end) renders as a 14-20 s Reel. It opens close on the joke, has a big identity line, and the end card lasts 2 s at most. It works voiced (B, C) and silent (A).
- [ ] **Short scripts** for the first 15 planets in the new order (funny or awe first), written by the room from the existing episodes, with the version (A/B/C) assigned in rotation. Then render, check frames and check the voice by transcript (scratchpad/voice_qa.py), and un-hold them in the schedule.
- [x] **Scoreboard** (20 Oct): `python -m atlas score` reads content/stats_history.jsonl (backfilled from every committed stats.json), subtracts our own early plays, reads at about 48 h, groups by format (published.json now records each Reel's format), and checks the pass lines. First read: strangers watched Veyra 1.9 s (12%) and Ovo 3.9 s (24%).
- [x] **Captions** (20 Oct, short Reels): first line "Invented planet No. N: Name. <who it's for>"; tags #worldbuilding #imaginaryworlds #scifiart #conceptart; the comment invite only on name planets. Owner-only, optional: profile name "Atlas of Elsewhere | invented planets" (search matches the profile name).
- [ ] **Read Luna and Maren at 48 h** (21 Oct about 12:30 and 21:15 UTC) and the owner's Account Status answer. If the account is held, stop posting and ask the owner to request a review.

## Next
- [ ] **Grey smear behind the text** (critic, 20 Oct): not the mist. A low sun's wide glow sits behind the text at close framings; the black text scrim turns it grey and the print dither makes it blotchy (seen on Frank, Maren, Daisy, Sefe, Bella, Mothwing). Fix: tint the scrim with the scene's darkest ink instead of black, and/or keep the glow out of the top-left text zone at close framings. Test on Frank beat 6 (scratchpad/mist_test.py).
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
