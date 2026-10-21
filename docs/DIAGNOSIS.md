# Diagnosis log

Newest first. Each entry gives the symptom (numbers), the hypotheses, the evidence for and against, what was changed, and how we'll know it worked.

## 2026-10-21 06:15 UTC: Max at 12 h, and the slot moves to 22:00 UTC
- **Max at 12 h:** reach 14 (strangers about 11), skip 44%, about 44% of the Reel watched. Retention is the best of any Reel so far (Maren: skip 59%, 18% watched), but its reach is about a quarter of Maren's at the same age.
- **When the showings came:** Max gained nothing from 18:09 to 23:00 UTC, then all 14 between 23:00 and 06:00 UTC. Maren (posted 21:15) was being shown within 2 h and gained 58% of its reach between 22:00 and 06:00 UTC. Luna (12:24) never started. The only hourly-tracked Reels both find their strangers in the US evening.
- **Change:** the daily slot moves from 18:00 to 22:00 UTC from today (Thessaly tonight). Halloween already posts at 22:00, so every short is now at one hour; the request queue uses the same slot (SLOT_HOUR) and Halloween rows are flagged fixed_date. Also fixed: Elsewhere (000) was still waiting for Hush part two, which is held, so it would never have posted; it now stands alone.
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
