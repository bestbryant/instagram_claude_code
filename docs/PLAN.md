# Atlas of Elsewhere: what's going wrong, and the plan

## Decisions taken (20 Oct, the bot as creator)
- **Posting paused for the old cut.** All 39 queued 34-36 s story Reels are on hold in content/schedule.json. Only short re-cuts post, 1 a day at 18:00 UTC (Halloween 22:00 UTC), from 20 Oct (Maren drew stranger showings within 3 h, so a full account hold is unlikely; Account Status is still worth checking).
- **Hush (the two-parter) is held** with its scheduled comments: almost every viewer arrives cold.
- **New format: the short cut, 14-20 s,** built from the existing scripts. It opens close on the joke, with the reason to send it as the big line, and an onset event (something appears or changes, with a sound hit) at about 0.4 s. The turn lands by about 8 s, and the end card lasts 2 s at most.
- **Format test, labelled per Reel:** A = short and silent; B = short with the cartographer's voice; C = second-person POV ("You've just landed on...") with the voice. Rotate A, B, C, about 5 each, judged at 48 h on stranger numbers.
- **Queue order:** funny and awe-inspiring planets first (Max, Bella, Fibb, Thessaly, Cinderwake, Hollow, Pebb, Simon...); wistful ones (Sefe, Fond, Sedge, Summer) wait.
- **No batch 4** until the test picks a winner.


*19 October 2026, from the head of growth*

## The short version
- **The art and the writing are good. How the Reels deliver them is the problem.** The scene barely moves, everything has to be read, there's no voice, and the joke arrives after most people have scrolled away.
- **Instagram may have stopped showing the newest Reels to strangers.** Luna reached 2 people; Ovo had reached 91 by the same age. Please open **Settings → Account Status** in the app today. Only you can see it.
- **I recommend *not* posting more per day yet, which goes against your request.** The reasons are below. I do recommend more motion, but only one kind: something that *starts* moving in the first second.

## What the numbers actually say
Some of the figures we've been using were wrong:
- **Veyra and Ovo, the only Reels strangers saw, were 16 seconds long, not 30-37.** Only Luna and Maren use the long 34-second format, and strangers haven't seen either yet.
- **Ovo is the only Reel with enough viewers to read (118 views).** 73% left within 3 seconds, and the average watch was 3.9 s. That's worse than typical small accounts, which lose about 65%.
- **Veyra's "11 s average watch" includes our own plays.** It showed 75 s when only 2 people had seen it. Strangers watched roughly 2-7 s, so Veyra did not beat the 8.5 s benchmark.
- **With 30-100 viewers per Reel, one Reel's numbers can swing 10-15 points by chance.** Judge patterns over about 5 Reels, at 48 hours, not 3 hours.
- **Zero shares so far is normal at this size** and doesn't tell us anything yet.

## Diagnosis
1. **A possible hold (urgent).** Luna got almost no strangers, and that started about 4 hours *before* the afternoon API block. Day one looked automated: 3 posts in 3.5 minutes, 7 posts in 26 hours. Meta's spam rules name frequent, repetitive posting. This is a hypothesis; Account Status will confirm it or rule it out.
2. **The first second doesn't stop anyone.** Frame 0 is a wide, nearly still scene, and the joke object takes up 3-6% of the screen. Instagram explicitly predicts "watch less than 3 seconds" and counts skips within 2 seconds.
3. **The payoff comes too late.** In the 34-second episodes the twist lands around 25 s, but strangers leave at about 4 s. Instagram compares watch time with Reels of the same length, so long and slow loses.
4. **There's no one to follow and no clear reason to send it.** Every similar account that grew fast had a speaking voice, a recurring character, or a "you are there" angle (Neural Viz, @timetravellerpov, Big Yowie). We have none of those. The line that makes someone think "send this to Bella" is the smallest text on screen, and sends are Instagram's top signal for reaching new people.
5. **Every Reel looks the same:** same layout, sign joke, purple palette and end card. Instagram checks similarity between Reels.

**Not the problem:**
- Posting through the API: no evidence of a penalty.
- Art made by code: original generated art isn't penalised.
- The amount of text: it's 1-3 lines over a soft shade, so it's not at real risk of the "mostly text" penalty.
- The 30-60 s length band in general.

## The plan, in order
1. **Today: check Account Status** (2 minutes). If anything is flagged, request a review, and we pause.
2. **Stop the 8-to-12-a-day ramp.** Post nothing new until 21 Oct, when Luna and Maren have 48-hour numbers. Then post 1 a day, rising to at most 2.
3. **Fix the scoreboard.** Count strangers only, read at 48 hours, and pass a format only if it gets:
   - skip rate of 60% or less;
   - at least 40% of the Reel watched;
   - at least 1 share or save per 100 people reached.
4. **Re-cut to short Reels (14-20 s) that open on the joke.** Open close on the joke, with the whole idea in one big line from the first frame and the payoff by about 8 seconds. We reuse the 39 scripts already written.
5. **Give the cartographer a voice** from second 0, with subtitles. It's mostly built already, as an offline text-to-speech voice in the code. We test it against the silent version. If it sounds robotic, a recorded human voice is the fallback.
6. **Make the "send this to someone" idea the headline,** and lead with funny or awe-inspiring planets rather than wistful ones.
7. **Add one motion event in the first second, tied to the joke** (the kettle boils over, the ball comes home), with a sound on it.
8. **Test three versions over about two weeks, about 5 Reels each:**
   - short and silent;
   - short with the voice;
   - "You've just landed on Kess" with the voice.

   Then put everything into the winner.
9. **Smaller fixes:**
   - vary colours and layouts;
   - fix cut-off signs and the grey smear;
   - put plain keywords in captions and the profile name;
   - drop #luna and #cozy, and the "drop a name below" line on every post;
   - add a short signature sound.
10. **Later:**
    - post the same videos to YouTube Shorts for more test viewers;
    - use trial Reels once we pass 200-1,000 followers;
    - try licensed music only if a Facebook Page is linked.

## Why not more posts a day?
- **The best study stops well short of this rate.** Buffer's study of 2.1M posts only goes up to 10+ posts a *week* and doesn't separate Reels.
- **Instagram's own benchmark is lower still.** Its fastest-growing creators average 10+ Reels a *month*.
- **One creator's daily-Reels test went badly.** Reach per Reel fell about 58%.
- **Meta's spam rules target this pattern.** They name frequent, repetitive posting, and we've already been blocked once.

Eight to twelve near-identical Reels a day is 5-8 times beyond any measured data, on a 2-day-old account. Each post is a test, and right now every test fails in the first second. If 2 a day holds up for a week with no errors and no drop in reach per Reel, we can test more.

## Realistic expectations
Followers on Reels come in jumps from a few breakout videos, not in a steady climb. Big Yowie had a dozen flops, then about 20 posts took it to around 250K once a format clicked; others took years. Expect 2-4 weeks of finding the format before follower numbers move. If none of the new versions passes the lines above after about 30 Reels, we rethink the concept, for example with a recurring character, rather than the posting rate.

## Sources
- Meta, Instagram Reels ranking card (updated 11 Nov 2025): https://transparency.meta.com/features/explaining-ranking/ig-reels-chaining/
- Mosseri on watch time, likes and sends (22 Jan 2025): https://www.socialmediatoday.com/news/instagram-shares-algorithm-insights-2025/738034/
- Mosseri on seconds watched (25 Feb 2025): https://www.socialmediatoday.com/news/instagram-longer-video-watch-time-versus-completion-rate/740916/
- Instagram Ranking Explained (31 May 2023): https://about.instagram.com/blog/announcements/instagram-ranking-explained
- Account Status and recommendations: https://help.instagram.com/653964212890722
- Meta spam policy: https://transparency.meta.com/policies/community-standards/spam/
- Buffer, posting frequency (13 Aug 2025): https://buffer.com/resources/how-often-to-post-on-instagram/
- Daily-Reels test (Bullock, 2026): https://www.lilachbullock.com/how-many-instagram-reels-should-you-post/
- Instagram Creators FAQ: https://creators.instagram.com/faq
- Socialinsider Reels benchmarks (Jun 2026): https://socialinsider.io/blog/instagram-reels-statistics/
- Metricool 2026 study: https://metricool.com/press-release-instagram-study-2026/
- Emplifi, speech in the first 3 s (Facebook data): https://emplifi.io/resources/facebook-reels-data/
- Motion onset and attention (Abrams & Christ 2003): https://pubmed.ncbi.nlm.nih.gov/12930472/
- What gets shared (Berger & Milkman 2012): https://faculty.wharton.upenn.edu/wp-content/uploads/2011/11/Virality.pdf
- Case studies:
  - @timetravellerpov: https://thetab.com/2025/02/18/from-the-titanic-to-the-plague-heres-an-explainer-of-the-pov-wake-up-ai-tiktok-trend
  - Big Yowie: https://www.kapwing.com/resources/what-it-takes-to-make-viral-ai-video-content-we-asked-bigfoot/
  - Neural Viz: https://creatordb.app/creatorstats/neuralviz/
- Instagram Audio API: https://developers.facebook.com/docs/instagram-platform/content-publishing/audio-api/

*Our own data: content/stats_history.jsonl, committed stats snapshots, published.json, and ffprobe durations of the posted files.*