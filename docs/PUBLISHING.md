# Publishing

There are two ways to post. **Start with manual posting.** It's the safest choice for a brand-new account, and in-app posting lets you add trending audio to Reels. Switch on the API publisher once the account is a couple of weeks old.

> This project never uses your Instagram password. Scripted password logins from servers are a common reason new accounts get flagged or disabled, and they break Instagram's terms. The only automation here goes through Meta's official Graph API.

---

## A. Manual posting (recommended for the first 2–4 weeks)

Each folder in `output/launch/<id>-<name>/` contains:

| File | Use |
|---|---|
| `1-cover.jpg`, `2-notes.jpg` | Carousel slides (1080×1350, 4:5) |
| `caption-carousel.txt` | Carousel caption |
| `reel.mp4`, `reel-cover.jpg` | Reel (1080×1920, 13 s, H.264/AAC) and its cover |
| `caption-reel.txt` | Reel caption |
| `alt-text.txt` | Accessibility text (Advanced settings → Accessibility) |

To get the files onto your phone: open this repo on GitHub in your phone's browser, tap a file, then *Download*. Or sync the `output/` folder with any cloud drive.

---

## B. Automatic posting with the official Instagram API

### 1. Make the account Professional
In the app: Settings → *Account type and tools* → *Switch to professional account* → **Creator**.

### 2. Create a Meta app and get a token
1. Go to <https://developers.facebook.com/apps> → **Create app** → use case **"Manage messaging & content on Instagram"**.
2. In the app, open **Instagram → API setup with Instagram login**.
3. Under *Generate access tokens*, **add your Instagram account**, then log in and approve it in the Instagram popup. That is Meta's official login page, not this code.
4. Grant `instagram_business_basic`, `instagram_business_content_publish` and `instagram_business_manage_comments`.
5. Copy the **access token** and the **Instagram user ID** shown there. Tokens generated here are long-lived (about 60 days). Refresh one before it expires with:
   ```
   GET https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=<TOKEN>
   ```
   An app in *development mode* can publish to accounts that have a role on the app (yours does), so you don't need App Review.

### 3. Host the media at public URLs
Instagram fetches media from a URL; it can't take uploads directly. The easiest free option is **GitHub Pages** for this repo:

1. Make the repo public, or use a plan that allows Pages on private repos.
2. Repo → Settings → Pages → *Deploy from a branch* → `main`, folder `/ (root)`.
3. Your base URL becomes: `https://bestbryant.github.io/instagram_claude_code/output`

Any static host works too (Cloudflare R2, S3, Netlify). Images must be **JPEG**, which the renderer already outputs.

### 4. Post
```bash
export IG_USER_ID=1784...           # from step 2
export IG_ACCESS_TOKEN=IGAA...      # from step 2 (never commit this)
BASE=https://bestbryant.github.io/instagram_claude_code/output

# check what would be sent
python -m atlas next --base-url $BASE --dry-run

# post the next item in content/schedule.json (logged to content/published.json)
python -m atlas next --base-url $BASE

# or post a specific folder
python -m atlas publish output/requests/biscuit --kind reel --base-url $BASE
```

If you used **Facebook Login** for the token instead (an Instagram account linked to a Facebook Page), also set `IG_GRAPH_HOST=graph.facebook.com`.

### 5. Collect name requests from comments
```bash
python -m atlas inbox            # scans your 10 most recent posts, queues requests in content/requests.json
python -m atlas inbox --chart    # …and renders a planet (carousel + Reel) for each new one
```
The parser keeps short name-like comments ("Biscuit!", "do my dog Pepper", "my cat's name is Toast") and skips compliments, links and friend-tags. **Glance over the queue before you post**: skip anything offensive or any private person's full name.

### 6. Optional: post daily from GitHub Actions
`.github/workflows/daily-post.yml` runs `python -m atlas next` once a day.

1. Add repository secrets `IG_USER_ID` and `IG_ACCESS_TOKEN` (Settings → Secrets and variables → Actions).
2. Add a repository *variable* `MEDIA_BASE_URL` (e.g. the GitHub Pages URL above).
3. Merge to the default branch. Scheduled workflows only run from there.

Until the secrets exist, the workflow skips itself and does nothing.

### Limits worth knowing
- Meta caps how many posts an account can publish through the API in 24 hours. The current number is in Meta's *Content Publishing* docs, and it's far more than this plan needs.
- Reels must be 3 s to 15 min, 9:16, H.264 + AAC. The generated files meet this.
- With Instagram Login the API only takes Reels by `video_url`. The publisher serves each video from this public repo through jsDelivr at the exact commit, which sends `video/mp4`. raw.githubusercontent sends `application/octet-stream`. Push before posting, or the URL check fails. Since 27 Oct jsDelivr sometimes answers 403 "Package size exceeded the configured limit of 50 MB" (the repo is large); the publisher then falls back to raw.githubusercontent at the same commit. Checked 27 Oct 14:40 UTC: an unpublished Reels container made from the raw URL (Charlie) reached FINISHED, so Instagram accepts octet-stream. If that ever changes (container status ERROR), the next options are a GitHub release asset or Pages.
- The API can't add trending audio. That's one reason to keep posting some Reels by hand.

**One-off container ERROR (29 Oct 14:37 UTC):** Fond's first container came back `status_code ERROR` with no detail, although the raw.githubusercontent URL served the right 8.55 MB file and the encode matched Reels that had posted (h264 High 1080x1920 30 fps, AAC 48 kHz stereo). A retry a minute later posted it (18145384876716242). Read as a transient fetch failure on Instagram's side. If it happens twice in a row on the same Reel, check the hosting (raw.githubusercontent throttling) before retrying again.
