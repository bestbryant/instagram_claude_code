# What makes a Reel grow an account (research, 19-20 Oct 2026)

Four researchers (ranking, retention, comparable accounts, cold start), then a critic who checked every claim against our own files and numbers. Sources are in the workflow transcript; the main ones are linked below. "Official" means Instagram or Meta said it; "measured" means a study with data; the rest is practitioner lore and is marked as such.

## What Instagram ranks on
- **Watch time, likes per reach and sends per reach** are the top three signals (Mosseri, Jan 2025). Sends (DM shares) count most with people who don't follow you. With one follower, almost all our reach is non-followers, so **sends per reach is the number to design for**. (official)
- **The first 2-3 seconds decide distribution.** Meta's Reels ranking card models the chance a viewer leaves within 3 s and uses skips within 2 s as an input. (official: transparency.meta.com/features/explaining-ranking/ig-reels-chaining)
- **Seconds watched matter more than finishing** (Mosseri, Feb 2025). A long Reel isn't penalised for a lower completion rate, but a payoff at 25 s is invisible to the 75% who left at 3 s. (official)
- Instagram shows fewer Reels that are mostly text, bordered, muted, low-resolution or watermarked, and uses "similarity to other reels" in ranking. Meta's spam policy names high-frequency posting and repetitive content. (official)
- Posting through the API is not ranked differently from posting in the app. (official + independent tests)

## Benchmarks to judge each Reel against
- Skip rate (leaves before 3 s): about 65% for small accounts (Socialinsider, 140K Reels, H1 2026).
- Average watch: about 8.5 s (Metricool, 24M posts, 2026).
- Judge at **48 h**, not 3-12 h: new accounts are tested on small non-follower audiences over the first 1-2 days.
- Self-views pollute the numbers at our size: the owner's and our own plays add watch time without adding reach. Read watch time only where reach is 20+.

## Levers, strongest evidence first
1. **A premise someone would send to a specific person, visible in frame 1.** Identity hooks ("A planet for people who...") and name planets ("Every Luna gets this planet") are the right mechanic, but the identity line must be the big line, not a small kicker. (official signal + case studies)
2. **Speech in the first 3 seconds:** +12% 3-s and +25% 10-s retention (Emplifi, brand Facebook Reels, correlational). Every fast-growing comparable account had a spoken voice, a recurring named character or a "POV: you..." frame (Neural Viz ~870K, @timetravellerpov ~500K in weeks, Big Yowie ~280K in 2 months, Strange Planet 2M in 3 months). (measured + cases)
3. **Something starts moving or changes in the first second.** Motion onset grabs attention; ongoing slow drift doesn't (everything in the feed already moves). A figure starts walking, a moon cracks, a sign flips: an event tied to the line. No study isolates "more animation" on its own. (measured, attention research)
4. **Concrete openers.** A specific noun and an impossible verb, no explanation ("Umbrellas go on your feet."). Too vague loses (Upworthy meta-analysis, 9K A/B tests). (measured)
5. **High-arousal emotion gets shared:** awe +30% share odds, amusement and recognition high; sadness lowers sharing (Berger & Milkman, 7K NYT articles). Keep the art; push the ideas toward wonder and recognition, away from wistful. (measured)
6. **Length:** 30-60 s is the best measured band, but only if people stay; loops only measurably help at 7 s or less. Our only Reels with stranger distribution were 15-16 s postcards. (measured, brand data)

## What doesn't hold up
- **Posting many times a day.** Measured data covers up to about 10 posts a week (more posts, more total reach, diminishing returns). Nothing measures 3+ a day, and one creator's daily test lost per-post reach. On a 2-day-old automated account that was API-blocked, high frequency plus a repeated template matches Meta's spam pattern.
- **Word-by-word captions** beating static text: no independent evidence. Only worth it to sync with a voice.
- **Trending music** as a ranking boost: no primary source. (The Audio API can attach library music since June 2026, but only with Facebook Login.)
- **"AI penalty":** none for generated art. The only enforced AI rule is for profiles built around an unlabelled AI person.

## Our own numbers, honestly read (critic, 19 Oct)
- Veyra (15.6 s postcard, identity hook on screen): reach 34, skip 58%: at or better than benchmark.
- Ovo (15.9 s, vague opener "One of everything."): reach 100, skip 73%, 3.9 s watch: worse than benchmark.
- Luna (34 s story): reach 2, stalled at 9-11 h old, with no stranger test showing at all, and it posted **before** the API block. That looks like an account-level distribution hold, not weak craft. Only Settings > Account Status in the app can confirm it.
- The 34 s story format has no stranger data yet.
- Template sameness is real: the same text position, sign-board gag, end card and palette family on every Reel.
- Craft defects: a grey mist band in the upper third behind the text; sign boards cut off at the frame edge; tiny gag objects; signs drifting into the bottom UI zone.
