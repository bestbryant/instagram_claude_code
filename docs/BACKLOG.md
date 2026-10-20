# Growth backlog

## Operating principles (how the bot works without being told)
- **Diagnose on its own.** The numbers are checked against targets every day. When they miss, the bot works out why (hypotheses, evidence, a test) in docs/DIAGNOSIS.md and changes something. It doesn't wait for the owner to notice.
- **Targets for now:** skip rate under 50%; average watch over 40% of the Reel's length; reach per Reel rising week on week; at least one send or save per 100 reached; follower growth every day.
- **Red flags that trigger an investigation in the same run:** three posts in a row with reach under 10 after 12 h; any API error; a sudden drop in reach against the previous week; a skip rate over 70%.
- **The bot is the creator.** It makes the creative and strategic decisions (format, cadence, story, look) on what it judges will succeed, using evidence. The owner's ideas are suggestions to weigh against the data, not orders. The owner only does what software physically can't: the app-only actions in docs/OWNER_TODO.md (pins, fixing Meta access), and nothing else.
- **Research before building.** For any new format or feature, check what is known to work first (docs/RESEARCH.md once written), then build the smallest test of it, then measure.

Goal: 50,000 followers. Every hourly run that isn't busy posting or fixing something takes the top unfinished item, moves it forward, and ticks it off or notes progress here. Keep items small enough to finish or advance in one run.

## Posting-rate experiment
Current gap: **12 h** (2 Reels a day), from 2026-10-20 00:00 UTC. Steps: 12 h, 8 h, 6 h (the ceiling for now, 4 a day). Meta's hard cap is 50 API posts in 24 h, but that is not a target.
- Why 12 h (decided 20 Oct from docs/RESEARCH.md): measured data only covers up to about 10 posts a week. Nothing measures 3+ a day, and Meta's spam policy names high frequency plus repetitive content. We are a 2-day-old automated account that was API-blocked on 19 Oct, and Luna got no stranger test showing at all. More posts of the same template into a possibly held account add nothing and add risk.
- Go one step faster only when all of these hold: (1) Account Status is confirmed clean; (2) a week with no API blocks; (3) the median skip rate of the last 5 Reels is under 60% at 48 h, with reach of 20 or more each.
- Judge every post at 48 h, not 3-12 h (new accounts are tested on strangers over the first 1-2 days).
- Log: 2026-10-19 21:20 UTC, gap set to 3 h at the owner's request. 2026-10-20 00:00 UTC, back to 12 h after the research and critique (docs/RESEARCH.md): the evidence didn't support 8 a day, and the account may be held.

## Now
- [~] **Batch 2 episodes (No. 019-030)**: written, edited and queued 2026-10-19 (10 kept: 019, 021-026, 028-030); rendering now. Still to do: add their registry rows to docs/HOUSE_RULES.md, and frame-check each Reel as it finishes. Original plan:: twelve new planets from the writers' room's best unused ideas (scratchpad/room/B1/_blind_top.md: Pebb, Whisk, Lode, Fibb's horse, Pell on 18 November, "Every planet has one", "Your name is a job there", ...). Written to docs/HOUSE_RULES.md, checked with apply_episodes.py, rendered, frame-checked, added to schedule.json after Bramble so the 4-a-day rate continues past Friday 23 October.
- [ ] **Read the first 48 h of story-episode stats** (Luna, Maren, Hush part one, Kess). Compare skip rate and average watch with Veyra and Ovo. If the opener is losing people in the first 2 s, rewrite the next five openers before they post.

## Next
- [ ] **Grey smear behind the text** (critic, 20 Oct): not the mist. A low sun's wide glow sits behind the text at close framings; the black text scrim turns it grey and the print dither makes it blotchy (seen on Frank, Maren, Daisy, Sefe, Bella, Mothwing). Fix: tint the scrim with the scene's darkest ink instead of black, and/or keep the glow out of the top-left text zone at close framings. Test on Frank beat 6 (scratchpad/mist_test.py).
- [~] **Batch 3 (No. 031-042)**: written by the room 2026-10-19 (10 kept: Lode, Ruby, Fibb, Lull, Will, Miles, Grace, Norman, Simon, Fond; Fleet and Isla dropped), added to content and queued after Sooner (023). Not rendered yet on purpose: the reels research may change the format (motion, voice, length), so render once that decision is made.
- [ ] **Name-planet episodes on demand**: requests get a story episode, not just a still. Write a short episode template the inbox can fill (resident, rule, turn) so a requested name posts within a day.
- [ ] **Batch 4**, chosen by what the stats say works (name planets vs. place planets, comic vs. tender, sign turns vs. picture turns).
- [ ] **Series hooks**: a recurring "Atlas update" Reel every ten episodes (the cartographer's map filling in), which gives followers a reason to follow rather than just like.
- [ ] **Trial Reels** once the account reaches 200 followers: A/B two openers for each new episode.
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
