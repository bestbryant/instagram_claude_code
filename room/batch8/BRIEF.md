# Batch 8 brief: No. 091-102 (written 21 Nov 2026)

Atlas of Elsewhere (@atlas.in.elsewhere) posts invented planets as short narrated Reels: each planet has one
impossible rule, and the rule shows something true about people and someone they love. A stranger scrolling
Reels decides in about 2-3 seconds whether to stay. Twelve new planets are needed for mid-December, two a day.
They post as the entry's `short`, version E (the narrator reads every line on screen).

## What the numbers say (stranger-only, at 48 h; `python -m atlas score`)
- Every breakout (past 300 strangers) skipped 32.5% or less in the first seconds and held 8.7-9.8 s. Of 16
  Reels that skipped more than 34%, none broke out. So the opener (kicker + title + what appears at 0.4 s) decides
  reach. Blind judges could NOT predict skip from the opener (rho -0.23), so treat the table below as the only
  evidence, not as a rule that guarantees anything.
- Follows come from the lengthened shape (three beats, about 14 s) and from relationship stories.
- Skip % by opener (lower is better). Title, then kicker:
  - 25 Fond: "'I love you' only works once here." / "A planet for people who hear 'Take a coat' and know."
  - 26 Simon: "Everyone does what Simon says."
  - 28 Hush: "Shouts take five days to cross the valley." / "...people who reply to texts five days late."
  - 29 Likeness: "Photos here show whoever took them." / "A planet for every mum who's never in the photos."
  - 30 Dibs: "Kim called dibs on sunsets." / "A planet for every big sister who called dibs."
  - 30 Sedge: "The moon came close enough to wave at." / "...people who work while everyone's out."
  - 30 Frank: "Every Frank gets this planet." / sub "Nobody here lies."
  - 31 Ruby: "The sky blushes if you're embarrassed."
  - 32 Tessel: "Winter here lasts a year." / "...the friend who remembers every birthday."
  - 32 Summer: "Nan says she's seen snow." / "A planet for every nan who was right all along."
  - 36 Victoria: "No cake, no Tuesday."
  - 39 Miles: "Next door is ninety miles away."
  - 42 Stead: "Parents here get a moon." / 42 Isla: "Falling out makes islands."
  - 43 Mary: "Mary's bag even has a lamp." / 44 Amber: "Here, the sky's a traffic light."
  - 46 Fret: "Worries here hang in the sky." / 48 Bob: "Bob next door can fix anything."
  - 50 Bill: "Here, you pay with daylight."
- What the low-skip openers share, read loosely: a concrete, impossible rule about something everyone does with
  someone they love (saying I love you, taking the family photo, calling dibs, shouting across a valley), stated
  in plain words in one breath, and a kicker that names a real person the viewer knows ("every mum who's never in
  the photos"). The high-skip ones were abstract (paying with daylight, worries in the sky), not strange enough
  (Bob can fix anything, Mary's bag), or began "Here,". Never start a title with "Here,".

## The shape (docs/HOUSE_RULES.md S1-S4, R1-R4: read them)
- Hook (frame 0, voiced): `kicker` "A planet for ..." (who it's for: the reason to send it) above the `title`
  (2 lines at most, about 8 words or fewer: a specific noun and an impossible verb, no explanation). `sub` is "".
- `onset` at 0.4 s: the picture shows the title's premise happening (R1), a big visible change.
- Three beats, each 12 words or fewer, 1-2 lines. One of them is an escalation before the turn, or a held
  reaction after it that is its own laugh (never padding). The turn by about 7.5 s, visible ON SCREEN (the
  picture changes: an onset on that beat), not only in the words.
- End card: `end` (6 words or fewer: the last laugh), then the sign-off `sign`: "Every name has a planet."
  Also write `end_kicker`, a dedication ("For anyone who ...") that replaces the sign-off if the offer is dropped.
- About 14 s in all (13.5-15.5 s voiced). Check with the preview tool.
- Every beat a new camera or a new scene (R2). People do what the line says (R3). The key subject sits between
  0.38 and 0.72 of the height; nothing that matters below 0.75 (the red line on the preview sheet), where
  Instagram's caption covers it (R4).

## The mix
- 12 planets, No. 091 to 102. At least 5 name planets (a common first name, never one already used: see the
  names in content/*.json) and the rest place planets (an invented one-word name, short, easy to say aloud).
- Spread the relationships: siblings, a parent and a child, a grandparent, best friends, flatmates, work, a
  neighbour, a teacher, a dog and its person, and at most 3 about couples (batch 7, queued ahead of this one, is
  all couples). Every hook leads with a person and someone they love.
- No premise already used: read the registry in docs/HOUSE_RULES.md and the titles in content/*.json.
- Amusement first (S6). Warm, specific, a little dry; British-English everyday detail (Mum, Nan, the kettle, the
  school run) is the house voice. Not "magical", not "whimsical", no cosmic wonder language, no morals. A real
  detail beats an adjective.

## The entry format
Copy the full structure of a same-kind example exactly: content/launch.json id "090" (Vow, a place planet) and
content/names.json id "089" (Sofia, a name planet; name planets also have a top-level `kicker` "Every Sofia gets
this planet."). Every key: id, name, subtitle, story, facts, hook, tags, spec, cover, episode (opener, beats,
end, caption), first_comment, short (version "E", kicker, title, sub, framing, zoom, focus, spec, onset, beats,
end, end_kicker, sign, end_zoom, end_focus, name_y). `hook` = the short's kicker. The caption follows Vow's:
a wry first line; a paragraph with the planet's population, day length and moons and the rule in full; a
first-person traveller line; optionally a true real-world aside in parentheses; it ends on a question.

## The picture
The scenes are drawn by atlas/render.py from the `spec` (the Spec dataclass: palette, terrain, crowd, house,
moons, gag, sign, lamp, etc.) and atlas/props.py. Read them and the existing entries to learn what can be drawn.
Use only what the renderer already draws; never edit the code. If a premise needs something the renderer can't
show, pick another premise. Signs (`sign`) can carry short words on a board when a rule needs text in the world.

## Writing for the ear
The narrator (a TTS voice) reads the kicker, title, beats, end and sign. No abbreviations, numbers that say
easily, names a speech engine pronounces right. Each line must make sense heard once.

## Preview (do this for every entry, more than once)
    python3 tools/short_preview.py --file room/batch8/<your file>.json --out room/batch8/preview
prints the voiced timing (turn, end line, total) and writes a contact sheet per entry to room/batch8/preview/
(look at it with the Read tool): is the text readable over the sky, does the onset visibly show the premise,
is the turn visible, is the subject above the red line? Fix and preview again until it is right.
