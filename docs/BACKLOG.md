# Growth backlog

Goal: 50,000 followers. Every hourly run that isn't busy posting or fixing something takes the top unfinished item, moves it forward, and ticks it off or notes progress here. Keep items small enough to finish or advance in one run.

## Posting-rate experiment
Current gap: **3 h** (8 Reels a day), from 2026-10-19 21:20 UTC. Steps: 4 h, then 3 h, then 2 h (the floor, 12 a day). Meta's hard cap is 50 API posts in 24 h.
- After about 16 posts at a gap, compare reach and views at about 3 h and 12 h old (content/stats_history.jsonl) with earlier posts at the same age. If the median held within about 30%, go one step faster; if it fell clearly, or Meta blocked or limited us, go one step slower.
- Log: 2026-10-19 21:20 UTC, gap set to 3 h at the owner's request. Baseline at about 12 h: Ovo reach 100 (posted 03:00, before the API block); Luna reach 2 (posted 12:24, just before the block).

## Now
- [~] **Batch 2 episodes (No. 019-030)**: written, edited and queued 2026-10-19 (10 kept: 019, 021-026, 028-030); rendering now. Still to do: add their registry rows to docs/HOUSE_RULES.md, and frame-check each Reel as it finishes. Original plan:: twelve new planets from the writers' room's best unused ideas (scratchpad/room/B1/_blind_top.md: Pebb, Whisk, Lode, Fibb's horse, Pell on 18 November, "Every planet has one", "Your name is a job there", ...). Written to docs/HOUSE_RULES.md, checked with apply_episodes.py, rendered, frame-checked, added to schedule.json after Bramble so the 4-a-day rate continues past Friday 23 October.
- [ ] **Read the first 48 h of story-episode stats** (Luna, Maren, Hush part one, Kess). Compare skip rate and average watch with Veyra and Ovo. If the opener is losing people in the first 2 s, rewrite the next five openers before they post.

## Next
- [ ] **Batch 3 (No. 031-042)**, started as soon as batch 2 is rendered. The queue needs about 24 episodes ahead at 8 a day. Write 12 to the house rules; include more name planets if the stats favour them.
- [ ] **Refresh docs/OWNER_TODO.md's comment list** on or after 2026-10-22 (the owner finished all 15 on 2026-10-19; next, about every 3-5 days): fresh, verified posts from the docs/community.md accounts, one specific comment each. The scratchpad workflow peer-post-comments does this; keep the owner's list to three a day.
- [ ] **Name-planet episodes on demand**: requests get a story episode, not just a still. Write a short episode template the inbox can fill (resident, rule, turn) so a requested name posts within a day.
- [ ] **Batch 4**, chosen by what the stats say works (name planets vs. place planets, comic vs. tender, sign turns vs. picture turns).
- [ ] **Series hooks**: a recurring "Atlas update" Reel every ten episodes (the cartographer's map filling in), which gives followers a reason to follow rather than just like.
- [ ] **Trial Reels** once the account reaches 200 followers: A/B two openers for each new episode.
- [ ] **Carousels with sound**: the held carousels go out once there are followers (API carousels can't carry audio, so they reach followers only).

## Owner-only (the bot can't do these)
- Pin first comments when told (the API can post comments but not pin them).
- Comments on peer accounts' posts (drafts in docs/community.md). The API can't comment on other accounts' posts, and automating it would read as spam. Collab posts once there's a body of work.
- Done by the owner, 2026-10-19: profile photo and bio, followed the peer accounts, username @atlas.in.elsewhere.
- Keep Account Status clean; if Meta blocks the API again, check the developer dashboard.

## Done
- 2026-10-19: 20-person writers' room (3 blind rounds, 2 review rounds, final 5-lens review) -> 21 story episodes, house rules, running order.
- 2026-10-19: renderer additions (crowds, carried child, moth_roof, house on the stage, cartographer placement, size cap under jsDelivr's 20 MB).
- 2026-10-19: posting at about 4 Reels a day; API hold after OAuthException; scheduled and first comments; inbox 'check' for caption answers.
