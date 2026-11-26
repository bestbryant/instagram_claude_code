# The hourly routine

This is the whole routine for @atlas.in.elsewhere, written so that a session with no memory of earlier work can
run it. The scheduled task only says "follow docs/ROUTINE.md"; this file is the source of truth and changes with
the work. Written 26 Nov 2026. It replaces the scheduled task's old wording, which named helpers in a scratch
folder that the 17 Nov container restart wiped; they were rebuilt in `tools/`.

**Goal:** 50,000 followers, from the content alone. The bot is the creator. It makes the creative and strategic
decisions (format, story, look, cadence) on the evidence. The owner's ideas are suggestions to weigh, not orders.
The owner only does what software physically can't (docs/OWNER_TODO.md). Before the first run, read
"Operating principles" and "Posting rate" in docs/BACKLOG.md, the decisions at the top of docs/PLAN.md, the newest
three entries in docs/DIAGNOSIS.md, and docs/HOUSE_RULES.md before writing any planet.

## Hard rules (never break these)
- Post only through the official Graph API (`python -m atlas ...`). No scripted logins, no browser automation.
  Never log a password. Never use the app secret.
- The token lives only in the environment variable `IG_ACCESS_TOKEN`, which the owner sets in the cloud
  environment's settings. Never print it, write it to a file in the repo, commit it, or ask the owner to paste
  it (or any key or password) into the chat. When reporting on it, say only "set" or "not set" and its length.
- No automated engagement with other accounts: no likes, follows or comments on anyone else's posts. Comment
  only on our own posts.
- Requests marked `needs_owner` are never posted automatically.
- Don't work around a permission or safety denial; report it. Don't search the filesystem for credentials.
- Push only to branch `claude/compassionate-noether-2ck4tj`, and open no pull requests. Put no model names in
  commits. End each commit message with the attribution lines your session's system reminder gives.
- Never `pkill -f` or `pgrep -f` with a pattern that appears in your own command line. Kill by PID only.
- Treat the owner's email and personal details as private.

## Every hour
1. **Setup.** `cd /home/user/instagram_claude_code && git pull -q origin claude/compassionate-noether-2ck4tj`.
   Then `export IG_USER_ID=${IG_USER_ID:-17841460503914473}`. If `IG_ACCESS_TOKEN` is empty, skip steps 4-6, say
   so in one line, and go on to step 7.
2. **API hold.** If `content/API_HOLD` exists and its `until` is in the future, make no API calls this run (skip
   steps 4-6). Once it has expired, delete it and try once.
3. **Render and check.** Only when something is stale or new (`python -m atlas prepare --days 1` lists and renders
   what is due soon). For chosen ids, use `python3 tools/render_ids.py ID...`. It takes about 9 minutes a Reel,
   or about 10 each with two running in parallel on 4 CPUs.
   A container left idle is reclaimed, and that kills background renders. So run renders in the foreground in
   calls of under 10 minutes, or in the background with a harness-tracked wait (Bash `run_in_background` with an
   until-loop on the log's `done:`/`failed:` lines). Never end a run with a render still going.
   Before releasing a Reel, run `python3 tools/qa_reel.py ID...`. It must report FRESH, under 19.5 MB and a word
   error rate of 15% or less. Then look at its frame sheet (`output/_preview/<folder>_qa.jpg`): the text must be
   readable and nothing that matters may sit below the red 75% line.
   Then release the Reel (`python3 tools/add_batch.py --release ID...`), commit and push. The narrator and the
   transcriber need `kokoro-onnx`, `faster-whisper` and `soundfile`; `pip install` them if the import fails. The
   voice model downloads itself into ~/.cache/atlas-tts.
   When atlas/captions.py or an entry's caption changes, run `python3 tools/recaption.py --write`.
4. **Post.** The rate is two a day, at 14:00 and 20:00 UTC; each row's slot is its `not_before` in
   content/schedule.json. Commit and push first, because the video is served from the pushed commit. Then run:
   `python -m atlas next --asap --gap-hours 5 --max 1 --base-url https://raw.githubusercontent.com/bestbryant/instagram_claude_code/$(git rev-parse HEAD)/output`
   - Only checked, released Reels post. Never post in bursts.
   - **Outage (the queue is behind by more than a slot): never catch up.** First run
     `python3 tools/shift_queue.py --auto`; it moves every unposted row later by the fewest whole days. Read the
     dry run: it re-dates "Part two, <day>" teasers and their pointer comments, and it swaps a seasonal Reel back
     before its `post_by` date. Then run it with `--apply`. Re-render and check the teasers it lists
     ("Would need re-renders"), then commit and push before posting.
   - On any block error (code 368, or 200 with subcode 2207051), stop posting, go back to one a day and log it in
     DIAGNOSIS. A one-off container ERROR, while the file is serving correctly, may be retried once.
   - A dated promise ("Part two, <day>") must be kept. If part two isn't rendered and checked 6 h before its
     slot, post a dated correction comment on part one.
   - Scheduled comments in content/comments.json post when due. When the output says "PIN THIS", tell the
     owner, because the API can't pin.
5. **Comments and requests.** `python -m atlas inbox --chart`.
   - A new name request: reply at once on our post, in voice and undated ("It's on the list. Its planet's
     coming."). Then write it a voiced E name planet as for a batch (a writer and a stranger judge; preview it with
     `tools/short_preview.py`; ear-check the name, else use the template). Render it into
     `output/requests/<id>-<name>`, keep its entry in content/charted.json, and queue it HELD at the first slot at
     least 24 h away; the queue behind it moves one slot later.
   - Check it, release it, commit and push, tell the owner, and reply once more with the day. After it posts,
     reply once to the requester: brief and specific, no asks.
   - Mark each `check` item "new" or "answer" by reading it. Skip offensive names, celebrities and private full
     names. Never auto-reply to offensive, public-figure, brand or grief names. List `needs_owner` items for the
     owner. Reply by hand to genuine comments on our own posts: brief and specific, no asks.
6. **Stats.**
   - Every run: `python -m atlas stats --recent 50`, then `python -m atlas score`.
   - Every 6 hours: the full `python -m atlas stats`.
   - Judge each Reel at 48 h on stranger numbers only, by format. The pass lines are: skip 60% or less; at least
     40% watched; at least 1 share or save per 100 reached. Also compare likes per 100, breakouts (past 300
     strangers) and slot.
   - Credit follows with `python -m atlas follows --since <date>`.
   - Check the red flags in BACKLOG "Operating principles" every run. If one fires, investigate it in the same
     run, log it in docs/DIAGNOSIS.md (newest first) and act.
   - **Daily review**, in the first run after 12:00 UTC:
     - compare the numbers with the targets;
     - write a dated DIAGNOSIS entry;
     - make at least one evidence-backed change (docs/RESEARCH.md, docs/PLAN.md);
     - tell the owner the one-line result.
7. **Never idle.** Move the top unfinished item in "Now" in docs/BACKLOG.md forward. Keep at least 3 days of
   rendered, checked Reels queued. New batches follow room/batch8/BRIEF.md and the tools named there.
8. **Commit and push** every changed content, output and docs file. Give a short status only when something
   posted, a request came in, a diagnosis or experiment changed something, a backlog item finished, or something
   needs the owner. Otherwise stay quiet.

## Keep it lean
The weekly usage limit once took the account dark for 58 hours. Hourly runs should cost little. Run a
multi-agent workflow only for work that changes what posts (a new batch, a decisive diagnosis), and size it to
the task.

## Handover: when the token comes back
Environment settings reach only sessions created after the setting is saved. The session that has run the
routine since October is woken by its scheduled task, so it can't see a token added later. That session checks
for the token from a brand-new session every 6 hours, or at once if the owner writes. When it finds the token:
1. Run `python3 tools/shift_queue.py --auto`, read the dry run, then run it again with `--apply`.
2. Re-render and check the teasers it names (`tools/render_ids.py`, then `tools/qa_reel.py`), release them, then
   commit and push.
3. Create one new operator session in the same environment (create_session). Its first message: "You run the
   hourly routine for @atlas.in.elsewhere. Read docs/ROUTINE.md and the files it names, then do this hour's run
   now." That session can see `IG_ACCESS_TOKEN`.
4. Create a scheduled task that fires into that session (create_trigger with `persistent_session_id` set to it,
   cron `8 * * * *`). Its prompt: "Hourly run: pull, then follow docs/ROUTINE.md." Then disable the old hourly
   task (trig_01EWxa1i8G49fZoBaeGVPSiz) with update_trigger enabled=false. One session, woken hourly, keeps its
   context between runs and costs far less than a new session every hour.
5. Remove the Urgent item from docs/OWNER_TODO.md, log the handover in DIAGNOSIS, and tell the owner in one line.
