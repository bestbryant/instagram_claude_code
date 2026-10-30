# Diagnosis log

Newest first. Each entry gives the symptom (numbers), the hypotheses, the evidence for and against, what was changed, and how we'll know it worked.

## 2026-10-30 daily review (12:25 UTC): every breakout was posted at 14:00
- **Numbers (strangers):** Fond (E, place, 14:39) at 22 h: 1,034 reached, 25% skip (the lowest yet), 73% watched, 1.45 views each, 5 likes, 1 save; it took off between 05 and 10 UTC (401 to 1,029). Frank (B, name, 14:16) final at 46 h: 366, 30% skip, 75% watched, 1.59 views each, 0 likes, 0 sends. Sedge (E, place, 22:11) at 38 h: 128, 30%. Lantern (E, place, converted, 22:09) at 14 h: 148, 41%. Daisy final 40%, Charlie final 41%. **Followers 3** (the first new follower since 19 Oct, during Fond's run). 7 days: 3,365 reached, 18 profile visits.
- **Finding: the slot, not the version, separates the breakouts.** Every spoken short since 23 Oct by slot: 14:00 UTC: Max 127, Bella 114, Summer 1,103, Whisk 111, Daisy 108, Frank 366, Fond 1,034 (3 of 7 past 300). 22:00 UTC: Thessaly 116, Cinderwake 106, Fibb 120, Sefe 182, Charlie 113, Sedge 128, Lantern 148 (0 of 7 past 182). The kinds cross both slots (E place: Fond broke out at 14:00, Sefe, Sedge and Lantern didn't at 22:00; name: Summer and Frank at 14:00, Charlie not at 22:00), so this isn't the name/place effect. 3 of 7 against 0 of 7 is suggestive (one-sided p about 0.1), not proof. A reading: the voice and the planets are British (Mum, Nan, sausage rolls), and 22:00 UTC is 10 pm in the UK and early evening in the US; 14:00 is the UK afternoon and the US morning.
- **Change:** the second daily slot moves from 22:00 to 20:00 UTC from 1 Nov (8 pm UK, 3-4 pm US East), and the posting guard drops from 6 h to 5 h so a 14:xx post doesn't push the 20:00 one to 21:07. Halloween keeps 22:00 (Hollow tonight, Mothwing tomorrow). The tight-cut test still alternates its slot, so it stays balanced. 29 queued Reels moved.
- **How we'll know:** breakouts (past 300 strangers at 48 h) and median reach for 20:00 posts against 14:00 posts over the next 10 days of each. If 20:00 still never breaks out, try both posts in the daytime (for example 10:00 and 16:00).

## 2026-10-29 daily review (12:40 UTC): the payoff comes after most strangers have gone
- **Numbers (strangers):** Daisy (E, name) final at 46 h: 108 reached, 40% skip, 54% watched, 0 likes, 0 sends. Sefe (E, place) at 48 h: 182, 33%. Charlie (C, name) at 38 h: 113, 41%, 1 share. Frank (B, name) at 22 h: 183 and climbing (his morning pool arrived 05-12 UTC), skip down to 36%, 65% watched, 1.58 views each. Sedge (E, place) at 14 h: 115, 29%. Followers 2.
- **Against the targets:** skip under 50%: met by every E and every name planet. Watched over 40%: met by E (median 54%). Reach rising week on week: missed (median 116 last week, 114 this week; only Summer has left the test pool). Sends or saves 1 per 100: missed everywhere (about 3 in 2,250 strangers). Likes: about 0.5 per 100, against a typical 3-5. Follower growth: missed (0 follows from 11 profile visits in 7 days).
- **The next stop didn't move profile visits.** Account insights by Pacific day: 20-25 Oct (before the next stop) 20 visits from 4,120 reached, 4.9 per 1,000; 26-28 Oct (with it) 6 from 1,263, 4.8 per 1,000. The "1 per 1,000" baseline in the backlog came from one 24 h reading and was wrong. It stays (no sign of harm), but it isn't the follow lever. Visits that don't convert point at the profile (owner tasks).
- **Finding: strangers leave before the payoff.** Voiced timings of the 12 posted spoken shorts (scratchpad/short_preview.py): the last beat (the turn) starts at 7.3-8.9 s and the end line lands at about 11-13 s; since the next stop, Reels run 16.5-20 s voiced. Strangers' average watch is 5.5-10.8 s (median about 8.5 s), and it doesn't grow with length. So the median stranger leaves around the turn and never reaches the end line, the laugh or ache that likes and sends would come from. That fits the numbers: E and the name planets fix the first second (skip 29-40%), but likes and sends stay near 0 on every version.
- **Change:** a timing rule in docs/HOUSE_RULES.md (the payoff before the median stranger leaves): the turn on screen and in the voice by about 5.5 s, the end line by about 9 s, two beats at most, a title of 7 words or fewer, voiced total 13 s or less with the next stop. Batch 6 (No. 067-078, all E) is written to it now, in the writers' room. Its Reels go into the queue one a day from 3 Nov, opposite a Reel from the current queue on the same day, so tight against standard is compared in the same week. The queue behind moves back.
- **How we'll know:** at 48 h, tight E against standard E (place against place, name against name): watched % (expected up mechanically), likes per 100 and sends or saves per 100 pooled over 6 Reels each, and reach. If pooled likes plus sends per 100 at least doubles with skip no worse, every later batch is tight and the standard queue gets a tightening pass.

## 2026-10-29 (02:10 UTC): the account funnel, first look
- **Numbers (account insights, last 28 days):** 2,815 accounts reached, 25 engaged, 21 profile visits, 0 link taps, 0 follows (followers still 2). In the last 24 h: 276 reached, 1 profile visit.
- **Reading:** about 0.75% of the people a Reel reaches open the profile. That is low but within the normal range for a small account. None of the 21 followed. With 21 visits, a 10% follow rate would give about 2, so 0 is weak evidence on its own. The grid (montage of the last 12) is a consistent run of illustrated cards with a headline each, so the grid isn't the obvious leak. The bio still says "One a day", the name field has no search words, and nothing is pinned. Those are owner tasks (docs/OWNER_TODO.md); the API can't edit the profile.
- **Changed:** `stats` now logs the last 7 days of reach, profile visits and accounts engaged with the follower count, so every review sees the funnel and not just the follower total. (First tried 24 h, but Instagram counts account insights by its own Pacific day, so just after its midnight that window read 0. Last 7 days at 07:10 UTC 29 Oct: 2,210 reached, 11 profile visits, 0 follows.)
- **How we'll know:** if visits rise with reach and follows stay at 0 for another 20 or more visits after the bio and pins change, the profile is the leak. If visits stay under 1% of reach, the Reels don't make people curious about the account, and the fix belongs in the Reels (the end card's "next stop" promise is the lever there).

## 2026-10-28 daily review (12:20 UTC): rule met, the place planets become atlas cuts
- **Numbers (strangers):** Daisy (E, name, 14:19) at 22 h: 108 reached, 38% skip, 55% of 19 s watched, 1.39 views each. Charlie (C, name, 22:09) at 14 h: 110 reached, 40% skip, 55% watched, 1.40 views each, and the account's first share. Sefe (E, place) at 38 h: 182, 33%. Whisk (B, place) at 46 h: 111, 59%. Followers 2.
- **The table now:**
  - B: name Max 40 | place Cinderwake 55, Fibb 64, Whisk 59
  - C: name Bella 34, Charlie 40 | place Thessaly 53
  - E: name Summer 32, Daisy 38 | place Sefe 33
  Every name planet, in any version and at either hour, held strangers at 32-40%. Every place planet in B or C lost 53-64%. The one place planet cut as E held at 33%. Charlie, the name planet posted at night, held at 40%, so the hour isn't it (Whisk already showed that).
- **Decision (rule set 27 Oct):** Daisy came in at 38%, under 40%, so the 12 queued place-planet B/C shorts became E: Lantern, Hollow, Mothwing, Kess, Orrin, Tessel, Lode, Selk, Bramble, Luma, Lull, Brumm. Each gets its entry's own dedication ("A planet for people who leave the porch light on.") above the title, with the sub kept where it carries the premise. The name-planet B/C shorts keep their versions, since they already hold strangers, and so does batch 4's crossed design.
- **Engine fix found on the way:** five of the dedications wrap to two lines and ran into the title. A wrapping dedication now grows upwards (atlas/reel.py). The previews are clean, and no Reel already rendered has a wrapping dedication.
- **Rendering:** the 12 are held and rendering in posting order (Lantern first, 29 Oct 22:00). Each is released after its frame and voice check.
- **Still open:** sends. Charlie's single share is the first in about 2,400 strangers.

## 2026-10-27 daily review (12:30 UTC): it isn't the hour; the atlas cut holds strangers on any planet
- **Numbers (strangers, `python -m atlas score`):** Sefe (E, place, posted 22:12) at 14 h: 168 reached, 31% skip, 44% of a 20 s Reel watched, 1.22 views each, 1 like, 0 sends. Whisk (B, place, 14:12) at 22 h: 110, 59%. Fibb (B, place, 22:02) at 38 h: 120, 64%. Summer at 46 h: 1,103, 32%, 1 save. Followers 2. Still no share on any Reel.
- **The slot hypothesis fails:** Whisk is a place planet posted in the afternoon and skipped 59%, like the place planets posted at night (53-64%). The hour isn't what separated yesterday's two groups.
- **What the table shows (new in `score`: version x kind):**
  - B: name Max 40 | place Cinderwake 55, Fibb 64, Whisk 59
  - C: name Bella 34 | place Thessaly 53
  - E: name Summer 32 | place Sefe 31
  In B and C, name planets hold strangers far better than place planets (34-40% against 53-64%). The atlas cut (E) holds both kinds at about 31%: Sefe is the first place planet under 50%.
- **What E changes:** in the engine, E is B with a dedication line above the title ("A planet for people who keep every compliment.", not read aloud), usually no sub, and tender atlas-style writing. So the lever is one of those three: the dedication line names a person in the first second (which is what the name planets do), the shorter hook, or the writing. Two Reels can't separate them.
- **Change today:** `score` now shows each Reel's planet kind and a version x kind table, so this comparison updates itself every run.
- **Decision for tomorrow's review (28 Oct), set now so it isn't fitted to the data later:** Daisy (E, name, 14:00 today) and Charlie (C, name, 22:00 today) report their first pools overnight. If Daisy skips 40% or less, the atlas cut has held three for three, and the queued place-planet B/C shorts become E: kicker = the entry's own "A planet for..." hook, title kept, sub cut where the dedication now does its job, starting with Lantern (29 Oct 22:00) and Kess (1 Nov). Name-planet B/C shorts stay as they are, since they already hold strangers and keep the B/C arms alive. If Daisy skips over 50%, E's two results were luck: keep the queue and wait for the 8 Nov verdict.
- **Untouched problem:** sends. 2,000 strangers, 0 shares, 3 saves. If the atlas cut keeps more people watching, the next lever is the reason to send (the person in the dedication is the person to send it to). Revisit after the E decision.

## 2026-10-26 daily review (12:35 UTC): afternoon posts hold strangers better, or name planets do
- **Numbers (strangers, `python -m atlas score`):** Bella (C) at 46 h: 114 reached, 34% skip, watched to the end (one looper), 2 likes, 0 shares or saves, so it fails only the send line. Willow (D, silent) 116, 74% skip. Summer (E) 1,103 reached, 32% skip, 58% watched, 8 likes, 1 save. Fibb (B, the first Reel with the next-stop end card) 118 at 14 h, 64% skip. Followers 2. No Reel has a share; 3 saves in total.
- **Against the targets:** skip 60% or less: Summer, Bella, Max, Thessaly, Cinderwake (Fibb misses). 40% watched: Summer, Bella, Max, Cinderwake. 1 send per 100: nobody. Follows: none from 1,100 reached.
- **Finding:** among the spoken shorts, every one posted in the afternoon held strangers better than every one posted at night. Summer 32%, Bella 34%, Max 40% (posted 14:10, 14:09, 18:09) against Thessaly 53%, Cinderwake 55%, Fibb 64% (all about 22:05). The pools also arrive at different hours: a 22:00 post meets its strangers at 00-05 UTC (the Americas' evening); a 14:00 post meets them at 05-09 UTC the next morning (Europe's morning, Asia's afternoon). Summer was the exception: its pool came at 16-20 UTC the same day and grew to 1,100.
- **Checked and ruled out:** the opening. Frames at 0, 0.4, 0.9 and 1.6 s of all nine posted shorts (scratchpad/review26/) share one grammar: a two-line hook, an onset change at 0.4 s, figures on a horizon. Nothing in the first second separates the low-skip group from the high-skip one, apart from the voice (the two silent D cuts skip 74%).
- **The confound:** the slot split is also a planet split. The three afternoon Reels are name planets (Max, Bella, Summer), and the three night Reels are place planets (Thessaly, Cinderwake, Fibb). Three against three with no overlap happens by chance about 1 time in 20, for either explanation. The API can't separate them by audience: it returns no audience-by-country data for an account this small (tried `reached_audience_demographics`: empty).
- **What breaks it:** the queue already crosses them. Whisk (place, B, 14:00 today), Sefe (place, E, 22:00 today), Daisy (name, E, 14:00 27 Oct) and Charlie (name, C, 22:00 27 Oct) give a 2x2 by the morning of 29 Oct. The E verdict must use it: Summer (name, afternoon) against Sefe (place, night) differs in three ways at once. Judge Sefe against Fibb and Cinderwake (same slot and kind), and Daisy against Bella and Max.
- **Changes today:**
  1. `score` now shows each Reel's posting hour and the spoken shorts' medians by slot.
  2. The second slot ran out after Hush (30 Oct), so from 31 Oct the queue had dropped to one a day until 18 Nov. The 18 November shorts now post two a day (14:00 and 22:00 UTC) from 1 to 9 Nov. Their order is unchanged, so every "Next stop" end card is still right (nextstop/apply.py: no changes).
  3. The queue now ends on 9 Nov: new planets go to the writers' room now (BACKLOG).
- **Then:** if the slot explains it (the place planets skip less in the afternoon and the name planets more at night), move the night slot earlier. If the planet kind explains it, the new planets lean to name planets.

## 2026-10-25 20:15 UTC: the first Reel past the test pool, and nobody follows
- **Summer (E, the first narrated atlas cut), 6 h:** 974 strangers, 1,440 views, 32% skip, 58% watched, 7 likes, 0 shares, 0 saves.
  - It is the first Reel past the 100-150 ceiling, and it got there by 4 h, from a 14:00 post.
  - The silent atlas cut Willow (same style) stopped at 113 with 75% skip. The voice is the difference.
- **The new bottleneck, the funnel:** last 24 h, 983 accounts reached, 1 profile visit, 8 accounts engaged, 0 follows (followers still 1). Viewers watch but have no reason to come back: no visible series promise, no next-episode hook, no character on screen they'd want more of.
- **Action:** a research workflow (wp10f470w) on turning Reel reach into follows (official Meta guidance, measured case studies, a skeptical critique of our end card, caption and grid). It reports an evidence-ranked plan for tomorrow's daily review. Measure: follows and profile visits per 1,000 reached.

## 2026-10-25 daily review (12:15 UTC)
- **Numbers (strangers only):**
  - Pebb (A, silent) at 48 h: 148 reached, 58% skip, 26% watched, 0.7 sends per 100. It fails.
  - Sooner (D, silent) at 48 h: 23 reached, 74% skip. It fails.
  - Cinderwake (B), 38 h: 105 reached, 55% skip, 49% watched, 0 likes.
  - Bella (C), 22 h: 108 reached, 34% skip (the best yet), 2 likes (1.9 per 100), 1.5 views each.
  - Willow (D), 14 h: 112 reached, 75% skip, 16% watched.
  - Followers: 1.
- **Against the targets:**
  - Skip under 50%: only Max (40%) and Bella (34%), both voiced.
  - 40% watched: only the voiced shorts.
  - 1 share or save per 100: none.
  - Followers: none.
- **The pattern, now over 9 Reels:**
  - Voiced: skip 34-55%, watched 39-49%.
  - Silent: skip 58-75%, watched 10-37% (Pebb, Sooner, Willow, Veyra, Ovo).
  - No silent Reel has beaten any voiced one on skip.
  - The A/B/C test was meant to run to about 6 Reels a version (8 Nov), but the silent arm has lost every comparison so far, and RESEARCH.md ranks speech in the first 3 s as the strongest lever.
- **Change:** the silent short arm (A) ends early. The 9 queued A shorts (Fibb tonight, Frank, Mothwing, Milo, Tessel, Will, Bramble, Grace, Brumm) become B, read by the narrator, and re-render in posting order. The test continues between voiced styles: B (narrator), C (second person, "You've just landed..."), E (the atlas cut, narrated, from 08:20 today).
  - Name requests stay silent (A), so the voice never mispronounces a requester's name; they are scored as "request", outside the test.
- **Measurement fix:** Bella's average watch reads 43 s on a 14 s Reel, which means one viewer left it looping (about 2 h of total watch time). The scoreboard now caps watched at 100% and flags it with *, so one looper can't pass the watch line for everyone.
- **Still the open problem:** sends. 2 saves and 0 shares from about 990 stranger reaches. The end-card send line has been live since Bella and Willow; read it on the next six.

## 2026-10-25 08:20 UTC: the silent atlas cut loses three-quarters of strangers in the first second
- **Numbers (strangers):**
  - Willow (D), 10 h, past its morning showing: 111 reached, 75% skip, 17% watched, 0 likes.
  - Sooner (D), 42 h: 23 reached, 74% skip; it never got a wider showing.
  - The shorts on their first showings: 35-58% skip.
  - Bella (C, second-person voice), 18 h: 105 reached, 35% skip, 1 like, about 1.5 views each. Its average watch reads 44 s on a 14 s Reel, almost certainly one viewer leaving it to loop, so not counted yet.
- **Pattern by sound:** every voiced short held strangers better than every silent Reel.
  - Voiced (B, C): skip 35-55%, watched 39-55%.
  - Silent short (A, Pebb): 58% skip, 26% watched.
  - Silent atlas cut (D): 74-75% skip, 17-37% watched.
  - RESEARCH.md already ranks speech in the first 3 s as the strongest measured retention lever.
- **Decision:** don't spend another slot on a silent atlas cut, and don't drop the atlas style on the strength of its silence alone. The six queued atlas cuts become **version E**: the same pictures and words, read by the narrator (the cartographer reading the journal, which is what the style is).
  - Summer (14:00 today) is re-rendered and checked (voice WER 3%); Sefe, Daisy, Sedge, Fond and Hush render next.
  - Scored as short-E.
- **How we'll know:** if E also loses about three-quarters in the first second over Summer and Sefe, the second slot goes to shorts from 28 Oct. If E holds near the voiced shorts, the atlas style stays, voiced.

## 2026-10-24 daily review (12:30 UTC)
- **Numbers (strangers only):**
  - Thessaly (C) at 48 h: 116 reached, 53% skip, 39% watched, 1.7 likes per 100, 0 sends. It fails the watch line by a point and the send line.
  - Pebb (A), 38 h: 148 reached, 58% skip, 26% watched, 1 save (0.7 per 100).
  - Cinderwake (B), 14 h: 102 reached, 55% skip, 49% watched, 0 likes, 0 sends. Its main showing came at 2-6 h, overnight, then stopped near 100.
  - Sooner (the first D), 22 h: 22 reached, 74% skip. It never got the morning showing the shorts get; it looks like it failed its first small test. That is one Reel. Willow (D) posts tonight.
  - Account, last 6 days: 639 reached, 9 profile visits, 0 follows. Followers: 1.
- **Against the targets:** skip under 50% missed by every Reel; 40% watched met only by the voiced B shorts (Max 46%, Cinderwake 49%); sends or saves: 2 saves and 0 shares from about 740 stranger reaches over all Reels (0.27 per 100, target 1); follower growth none.
- **Patterns:** the ceiling holds (every short stops at 100-150 strangers). The voice keeps people watching (B 46-49%, C 39%, A 26%).
- **Diagnosis, the send line:** no short says who to send it to. RESEARCH.md finding 1 names the identity line ("A planet for people who...", "Every Bella gets this planet") as the send mechanic. It is not on screen in any A/B/C short (their titles are premise jokes), and only small on D's first frame. The caption opens with it, but few people read captions.
- **Change:** the end card now closes on a short dedication under the planet's name and last line: "For people who save the good plates for best.", "Every Bella gets this planet." Written by hand for all 33 queued shorts (short.end_kicker, at most about 10 words) and added to the request template ("Every <Name> gets this planet."). The first second doesn't change, so the skip rate shouldn't move; the end card gets 0.5-1 s longer so the line can be read. Bella (14:00 today) is re-rendered and checked; the other 32 render in posting order (about 9 min each, 5 h).
  - Not done, and why: a "send this to..." line in the caption (Meta demotes share-bait on Facebook, and few read captions); the identity line on frame 0 (more to read in the first second, where the skip is decided).
- **How we'll know:** sends and saves per 100 on the next six shorts against 0.27 per 100 so far. A first share would already be news.
- **D:** decide on Sooner, Willow and Summer together (27 Oct), not on Sooner alone, since one Reel that never got shown says little about the format.

## 2026-10-23 20:10 UTC: the showings arrive at a time of day, not an age
- **Symptom:** Sooner (023, D, posted 14:15 UTC) has 8 strangers at 6 h. The 22:00 posts had 31-56 by then.
- **Reach over time, by clock time (`stats_history.jsonl`):**
  - Max (posted 18:09): 14 by 06:09, 126 by 10:09.
  - Thessaly (posted 22:10): 31 by 04:10, 117 by 06:10.
  - Pebb (posted 22:09): 56 by 04:09, 141 by 06:09.
  - Maren (posted 21:15) is the exception: it rose gradually for 24 h.
- **Reading:** each short's main jump (about 100 strangers) lands between about 04:00 and 10:00 UTC, whenever it was posted. The posting time changes how long a Reel waits for that jump, not how far it goes (116-145 each time). So the 14:00 slot is probably not the problem.
  - A guess, not checked: 04:00-10:00 UTC is late morning to afternoon in South and Southeast Asia, so the first test pool may be weighted there. Instagram only shows audience location from 100 followers.
- **Check:** Sooner should jump tomorrow between 04:00 and 10:00 UTC.
  - If it is still under 20 at 12:00 UTC on 24 Oct, the 14:00 slot or the D cut is the cause. The two formats swap hours each day, so later Ds at 22:00 will separate the two.
  - Cinderwake (22:00 tonight) lands in the same morning window, which will also show whether two Reels on the same morning split one pool.
- **Change:** none. The schedule already balances the hours across formats.

## 2026-10-23 daily review (12:17 UTC)
- **Pebb (short-A, the first with its punchline drawn on screen), 14 h:**
  - 145 strangers reached, the most of any Reel at that age.
  - Its first 56 viewers were the best audience yet: 24% skip, about 2.3 views each (replays), and 1 save.
  - The wider audience behaved like every other Reel's: 57% skip, 26% watched, 0 likes. Overall it has 0.7 sends per 100.
- **Pattern 1, the ceiling:** every Reel stops at about 100-145 strangers (Ovo 100, Max 127, Thessaly 116, Pebb 145). That looks like Instagram's first test pool, and nothing has earned a wider showing yet. That needs stronger watch and send signals inside the pool.
- **Pattern 2, voice and watch time:** the voiced shorts hold viewers longer than the silent one: B (Max) 46%, C (Thessaly) 39%, A (Pebb) 26%.
  - That is one Reel each, so it's a hypothesis.
  - If it holds, the silent atlas cut (D) starts at a disadvantage on watch time; its first read is Sooner's at 48 h.
- **Change (measurement):** the scoreboard now shows loops (views per stranger), because replays count toward watch time and Pebb's first audience replayed it. Pebb is at 1.12 overall; every Reel so far is between 1.03 and 1.33.
- **Next:**
  - Sooner (the first D) posts at 14:00 today and Cinderwake (B, revised) at 22:00.
  - Pebb's 48 h read is tomorrow at 22:09.
  - Sooner's 48 h read (25 Oct 14:00) decides whether to write more D planets.

## 2026-10-22 daily review (12:12 UTC)
- **Against the targets (strangers only):**
  - Max (short-B, 42 h): 127 reached, 40% skip, 46% watched, 0 likes, 0 shares or saves. It meets the skip and watch lines but fails the send line.
  - Thessaly (short-C, 14 h): 116 reached, 53% skip, 39% watched, 2 likes (1.7 per 100). Those are the first likes on any short.
  - Followers: still 1.
- **Slot test:** Thessaly (22:00 UTC) had 113 strangers at 6 h; Max (18:09 UTC) had 0 at 6 h and 14 at 12 h.
  - This is one pair, so it's not proof, but it is the biggest gap we've measured.
  - The 22:00 slot stays. The new 14:00 slot alternates between the two formats, so it can't bias the format test.
- **Changes since yesterday (each logged above):**
  - All 28 queued shorts are revised so their joke is visible on screen. Twenty-seven are re-rendered and checked; four are left in the queue.
  - A fourth version, D (the atlas cut), is added. All 8 are released for 23-30 Oct.
  - Posting goes to 2 a day from 23 Oct.
  - New props: a dog, armchairs, sleep Zs.
  - The render queue now survives the idle container, and requests fit a two-slot day.
- **Next reads:**
  - Pebb at 22:00 tonight: the first short with a visible punchline. Compare its likes and sends per 100 with Max (0) and Thessaly (1.7).
  - Sooner at 14:00 tomorrow: the first D. Its 48 h read is 25 Oct; it decides how many new D planets to write for 31 Oct onward.
  - A second props pass for Will and Luma (the dogs their lines mention) before they post on 9 and 13 Nov.

## 2026-10-21 23:30 UTC: the joke is only in the text
- **Symptom:** strangers stay but never act. Max: 127 reached, 40% skip, 46% watched, and 0 likes, 0 shares, 0 saves. Thessaly has just posted.
- **Looking at the frames, not the numbers:** in Max, Thessaly and Pebb (next) the picture barely changes after the onset, and the punchline is a sentence over the same picture.
  - Thessaly: "Then, this afternoon, it rains down." The frame shows the same three people with umbrellas on their feet, with no rain landing on them.
  - Pebb: the "ball" that orbits reads as a moon. Nothing shows who chewed it. The end says "Now she throws two." over one ball.
  - Viewers on a silent feed reward what they can see; a joke you have to read earns a nod, not a like or a send.
- **Change:** beats and the end card can now carry their own onset, so the punchline lands on screen as an event with a sound hit (`onset` per beat, `end_onset`; existing shorts render byte-identical).
  - Workflow wi4pqkela revises the 28 queued shorts so each frame shows its line and the end card shows the joke. It changes the picture first; voiced B/C versions keep their words so the voice test stays clean.
  - Each revision gets a sound-off stranger judge and a fix pass. Then any missing props get built, and the shorts are re-rendered, checked and swapped in, Pebb first.
- **How we'll know:** likes and sends per 100 strangers on the revised shorts against Max and Thessaly (both 0 so far). The A/B/C versions stay interleaved, so the format test is unaffected.

## 2026-10-21 daily review (12:15 UTC)
- **Against the targets (strangers only):**
  - Max, the first short (18 h): 125 reached, 41% skip, 46% watched. It meets the skip and watch lines; the old long cut (Maren) is at 61% and 17%. The format change works where it was meant to: people stay.
  - Luna, the long cut (48 h): 3 reached, a fail.
  - Veyra and Ovo (48 h): fails, as recorded.
  - Followers: still 1.
- **What isn't moving:** nobody acts. Max has 0 likes, 0 shares and 0 saves from 125 strangers. Sends at 0 of 125 is within chance (we'd expect about 1). Likes at 0 is unusual: small accounts usually see 2-5 per 100.
- **Change today (measurement):** the scoreboard now shows likes per 100 strangers (one of Instagram's three top signals per docs/RESEARCH.md, and the one we weren't tracking) and reach at 6 h (for the 22:00 slot test). Nothing creative changes on the strength of one short: the A/B/C test needs about 6 of each version before it means anything.
- **Next:** Thessaly (version C, second-person POV with voice) posts at 22:00 tonight. Max's 48 h read is tomorrow at about 18:10. If likes stay near 0 across the first five shorts while watch holds, the end card is the suspect: the 2 s card gives the turn but no moment to react to. The fix to try then is a final beat that lands the joke on screen.

## 2026-10-21 06:15 UTC: Max at 12 h, and the slot moves to 22:00 UTC
- **Max at 12 h:** reach 14 (strangers about 11), skip 44%, about 44% of the Reel watched. Retention is the best of any Reel so far (Maren: skip 59%, 18% watched), but its reach is about a quarter of Maren's at the same age.
- **When the showings came:** Max gained nothing from 18:09 to 23:00 UTC, then all 14 between 23:00 and 06:00 UTC. Maren (posted 21:15) was being shown within 2 h and gained 58% of its reach between 22:00 and 06:00 UTC. Luna (12:24) never started. The only hourly-tracked Reels both find their strangers in the US evening.
- **Change:** the daily slot moves from 18:00 to 22:00 UTC from today (Thessaly tonight). Halloween already posts at 22:00, so every short is now at one hour; the request queue uses the same slot (SLOT_HOUR) and Halloween rows are flagged fixed_date. Also fixed: Elsewhere (000) was still waiting for Hush part two, which is held, so it would never have posted; it now stands alone.
- **08:09 UTC (14 h):** Max jumped from 20 to 42 reached in an hour (European morning), with skip down to 32% and about half the Reel watched. A second wave of showings, and the best retention yet: the short cut is doing its job once it is shown. The slot question is about how fast the first showings start, not whether they come.
- **09:08 UTC (15 h):** Max is at 120 reached and 151 views, our biggest Reel so far, with 41% skip and about 46% watched: it meets the skip and watch lines. Most of it came 07:00-09:00 UTC, so showings arrive in waves at any hour and the case for the slot move is weak. Keeping 22:00 anyway, because one fixed hour for every remaining short (Halloween included) keeps the format test clean; it is a constant now, not a claimed improvement. Shares and saves are still 0, the line that's left.
- **How we'll know:** compare reach in the first 6 h and at 12 h for Thessaly, Pebb and Cinderwake against Max (0 at 3 h, 14 at 12 h). If 22:00 doesn't beat 18:00 on first-6 h reach across those three, try 01:00 UTC.

## 2026-10-20 21:10 UTC: watch, Max has no showings after 3 h
- **What:** Max (013, short-B, posted 18:09 UTC) has reach 0 and views 0 at 1, 2 and 3 h. The media is fine (REELS, shared to feed, thumbnail present). Maren had 3 at 1.9 h and 12 at 3.2 h.
- **Pattern so far (n=5 Reels):** the two Reels posted in the European/US daytime both stalled: Luna (12:24 UTC) has been stuck at 2-3, and Max (18:09 UTC) is at 0. The three posted 21:00-03:00 UTC (Veyra 00:07, Ovo 03:00, Maren 21:15) all reached 37-100 strangers. By chance alone that split has odds of about 1 in 10, so it's a hypothesis, not a finding. Other candidates: an account-level limit (Account Status is still unchecked; it's the owner's top item) or slow first showings that catch up.
- **22:08 UTC (4 h):** reach and views still 0, but average watch time now reads 27 s, so someone has watched it and reach is lagging behind watch time in the API. That points to slow reporting more than no showings. Keep watching.
- **Next:** read Max at 6 h and 12 h. If it is still under 10 at 12 h, treat the slot as the likely cause and test a 23:00 UTC slot for the next three shorts (Thessaly, Pebb, Cinderwake), then compare first-12 h reach. Ask the owner once, in the morning, to check Account Status.

## 2026-10-20 daily review (12:15 UTC)
- **Numbers (strangers only, `python -m atlas score`):** Maren, 34 s, 15 h: reach 68 and still rising about 4-5 an hour; skip 61%; watch 6.4 s (19% of the Reel); 0 shares or saves. Its first test audiences skipped 29-43%, and the wider pools from hour 6 on about 60% (the usual cold-start shape). Luna is stuck at reach 3 at 24 h. Veyra 62% skip, 1.5 s; Ovo 73%, 4.3 s. Followers: 1.
- **Against the targets:** skip under 50% missed (61%); 40% watched missed (19%); 1 send or save per 100 missed (0); follower growth none. The one positive: Maren is getting steady stranger distribution, so a full account hold is ruled out (Luna was probably a weak first test).
- **What it means:** strangers give the long cut about 6 s and leave before its payoff (25 s+). This is the evidence behind the switch to the short, hook-first format, whose first Reel (Max, version B) posts tonight at 18:00 UTC.
- **Change today:** measurement. The test is judged on each Reel at 48 h, but posts older than 12 h were only snapshotted every 6 h, so a 48 h read could be 3 h off. The hourly run now pulls every post up to 50 h old (`stats --recent 50`): one more API call per live post, well inside the budget.
- **Next read:** Max at 48 h (22 Oct, 18:00 UTC); the first three versions (Max B, Thessaly C, Pebb A) by 24 Oct.

## 2026-10-20: research back; the format and the cadence change
- **Symptom (corrected):** Veyra and Ovo were 16 s Reels, not 20-37 s. Ovo reach 100, 73% skip, 3.9 s average watch (about 24% of its length). Veyra's 11.3 s watch includes our own early plays (it read 75 s at reach 2), so strangers watched about 2-7 s. Luna (34 s): reach 2, frozen from 8.9 h to 10.7 h, posted about 4 h before the API block.
- **Findings (docs/RESEARCH.md, docs/PLAN.md):** the first 2-3 s decide distribution (Meta's Reels card predicts "watch less than 3 s"); sends per reach drive non-follower reach; speech in the first 3 s is the strongest measured retention lever; motion onset, not ongoing motion, grabs attention; nothing supports 3+ posts a day; Meta's spam policy names high-frequency, repetitive posting.
- **Hypotheses ranked:** (1) a recommendation hold on the account (Luna got no stranger showing at all); (2) a near-still first second with a wide shot and tiny joke; (3) payoffs at 20-30 s when strangers leave at about 4 s; (4) no voice or character, and the reason to send is the smallest text; (5) every Reel looks alike.
- **Changes:** posting rate 8 a day -> paused, then 1 a day; the 39 queued long Reels held; the owner asked to check Account Status; a short, hook-first format with a 0.4 s onset event; the narrator's voice (atlas/voice.py) as test version B; a labelled A/B/C format test.
- **Update 20 Oct 00:30 UTC:** Maren (34 s, posted 21:15) went from reach 3 at 1.9 h to reach 12 at 3.2 h, skip 29%. So the account is getting stranger test showings again, which weakens the account-hold hypothesis (Luna may just have drawn a poor first test). Account Status is still worth checking. The format plan is unchanged: the retention problem stands on its own.
- **How we'll know:** Luna and Maren at 48 h (21 Oct) say whether the account is held. Then, per version over about 5 Reels at 48 h: skip 60% or less, at least 40% of the Reel watched by strangers, at least 1 share or save per 100 reached. If no version passes after about 30 Reels, rethink the concept (for example, a recurring character series), not the posting rate.

## 2026-10-19: low reach and high early skip
- **Symptom:** Ovo reach 100 with a 73% skip rate and 3.9 s average watch on a 16 s Reel (corrected 20 Oct; it was logged as 20 s). Veyra 58% skip. Luna and Maren reach 2-3 after several hours. 1 follower.
- **Hypotheses:**
  1. Frame 1 doesn't stop the scroll: a static landscape with no motion and a text block to read.
  2. Text-only with ambient sound is weak against voiceover and music in the feed.
  3. The account is held back after the 19 Oct API block, or as a new API-only account.
  4. Posting volume and timing.
- **Action:** research across four angles, plus a critique of our actual Reels and a ranked plan (the reels-research workflow, 2026-10-19). Building waits until the plan is in. Findings will go in docs/RESEARCH.md.
- **Missed:** this should have been opened as soon as Ovo's 73% skip appeared, not after the owner asked.
