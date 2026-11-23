# Your to-do list

Only things the bot can't do, kept as short as possible. Growth comes mainly from the Reels; these help the visitors we already get to follow.

## Urgent: posting is stopped until this is done (since 17 Nov, 17:10 UTC; checked again 23 Nov)
- [ ] **Store the Instagram access token in the environment settings, then tell me in chat that it's done.** The cloud container restarted on 17 Nov and wiped my scratch folder, where the token was kept, so I can't post or read stats. As of 23 Nov 12:10 UTC it is still not set: I checked from a brand-new session in this environment, which is where new settings show up. Please add an environment variable named `IG_ACCESS_TOKEN` in the cloud environment's settings: open the environment menu in this session's title bar, then Edit, and add it as an environment variable (a Network secret won't work here, because the code sends the token itself). Use the same long-lived token as before, or a fresh one from the Meta app dashboard (docs/PUBLISHING.md, step 2). Please don't paste it into the chat.
  - **Then send me a short message** (for example "token added"). Settings only reach *new* sessions, and my hourly run resumes this one, so a message lets me pick it up from a fresh session straight away instead of within 6 hours. The queue (59 Reels, checked, to 17 Dec) then moves forward by however many days were missed and posting resumes from the next slot, with no catch-up.

## Now, please (2 minutes, in the app; 13 Nov)
- [ ] **Selk wasn't shown to anyone.** The Reel posted 12 Nov 20:10 UTC (https://www.instagram.com/reel/Dfp4bwQCeUc/) has 0 views after 12 hours; no Reel before has gone more than 4 hours without a view. Please open it in the app and tell me if it shows any notice (for example 'can't be recommended', 'under review', a music or copyright note), and check Profile > menu > Settings > Account Status for anything new. The API can't see either.

## Please, when you can (5 minutes, in the app)
Three Reels have now passed 1,000 strangers each (Summer, Fond, Hush), but only 2 of those viewers followed (1 Nov). The grid itself looks good (a run of illustrated cards), so the bio and pins are what a visitor has left to judge by. These three make the profile convert the visitors we now get.
- [ ] **Bio** (Edit profile > Bio): replace it with
  `Invented planets. Leave any first name under a Reel and I'll find its planet.`
  (The current one says "One a day", which is no longer true.)
- [ ] **Name** (Edit profile > Name): `Atlas of Elsewhere | invented planets` (Instagram search matches the name field).
- [ ] **Pin 3 posts** to the top of the grid (open the post > ... > Pin to your profile). These are our three biggest Reels so far (1 Nov):
  1. Hush: https://www.instagram.com/reel/DfHxlp7ExYh/ (1,138 strangers, 20 likes, 2 saves; part two posts 1 Nov)
  2. Summer: https://www.instagram.com/reel/De644BXFNuB/ (1,103 strangers)
  3. Fond: https://www.instagram.com/reel/DfFPZaljptx/ (1,039 strangers, the lowest skip rate)
- [ ] **Check Account Status** (Profile > menu > Settings > Account Status): does it say the account can be recommended to non-followers? Summer's reach suggests yes, but it's worth a look.

## Optional
- [ ] **Pin a comment** when the bot asks (the API can post comments but not pin them). Nothing to pin right now.
