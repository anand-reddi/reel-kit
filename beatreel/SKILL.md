---
name: beatreel
description: Talking-avatar explainer reels in the "one idea per beat" paper style (karaoke caption top-left, one hero object per beat, presenter at the bottom). Separate from reel-kit.
---

# beatreel

Vertical explainer reels (1080x1920, 30 fps, 30–70 s) in the style of the 25 reference reels in the user's
"Explainer reels" folder. It is **not** reel-kit: different look, different engine. It only borrows reel-kit's
voice (Kokoro + pronunciation audit), sound mixer (earshot SFX) and the user's presenter character.

## The style (learned from the 25 references)

Every frame has the same four layers, top to bottom:

1. **Meta row** (y≈82): tiny mono slug on the left, `// 03 — the catch`, changes every beat. A running counter on
   the right, `LIABILITY $53,000` / `RESETS 1` / `FOLLOWERS 40K`, whose value (in the accent colour) changes when the
   story moves it. The counter is the video's spine: pick one number the story is about.
2. **Karaoke caption** (top-left, y≈170): one script line at a time, 2 lines max, bold grotesk. Words not yet
   spoken sit in light grey and slightly blurred; each turns ink as it is said. **One or two key words per line are
   set in red italic serif** (`_word_` in the script). Never a centred caption, never at the bottom.
3. **Hero** (middle, y≈600–1100): exactly **one idea per beat**, shown literally. A new beat = a new object that
   springs in (back-out pop, small tilt), floats slightly, and leaves when the beat ends. Objects carry a
   **halftone dot drop-shadow**. What the references use, roughly in order of frequency:
   UI cards and screenshots with a red ring on the one thing that matters · a huge red number that counts ·
   condensed black/red sticker labels (`ONE RULE`, `THE EASY PART`) · red outlined stamps (`SEALED`, `TUNED`) ·
   phones · terminals typing · checklists that tick on the word · a grid of people with one highlighted ·
   ✕ vs ✓ comparison cards · calendar pages · the comment-bubble CTA with the keyword huge.
4. **Presenter** (bottom, chest-up, centred): the avatar changes gesture on every beat to match the line
   (point up for a reveal, shrug for "but", shh for a secret, facepalm for a mistake, count for numbers).

Rhythm: a beat is one short line (5–10 words, ~1.5–3.5 s). 15–25 beats per video. Voice only, **no music bed**;
soft pops when objects land, a swish on beat changes, an impact on stamps. Accents: a beat can flood the page red
or black for the punchline (`"bg": "red" | "black"`), and a halftone dot wipe can mark a chapter change
(`"wipe": true`). The last beat is always the CTA (comment a keyword / send to a friend / follow).

Themes: `paper` (off-white #efece6, ink, red #e8452c — most references), `ink` (dark navy, agents/dashboards),
`neon` (near-black, lime #c8f53c + pink glow, launches/AI video tools). The illustrated desk-room look seen in
two references is not built yet.

## Workflow (the user's standing rules apply)

1. Research and fact-check. Show options first: 3–4 hooks scored /50, share angle, follow angle, length.
2. Write the script as beats (below). Keep every line literal: the hero must *show* what the line *says*. If you
   can't name the object for a line, rewrite the line.
3. `python3 beatreel.py board script.json` → voice, pronunciation report (`build/<name>/pronounce.txt`, fix with
   `voice.say`), a frames sheet `<name>-frames.jpg` (middle of each beat). Send the sheet; wait for approval.
4. `python3 beatreel.py make script.json` → `<name>.mp4` (-14 LUFS). Check frames, send.
5. Brand named → brand logo (`"type": "logo", "icon": "simple-icons:<brand>"`). Icons come from the kit, never emoji.
   The repulsor intro sound plays by default (`"intro": false` turns it off).

## Script format

```json
{
 "name": "claude-reset", "theme": "paper",
 "counter": {"label": "RESETS", "start": "0"},
 "voice": {"name": "am_puck", "speed": 1.12, "say": {"US": "U S"}},
 "presenter": {"width": 1500, "y": 1150},
 "beats": [
  {"slug": "01 — hook", "pose": "shh", "count": "1",
   "lines": ["Claude hid a _free_ reset button in your settings."],
   "hero": [{"type": "shot", "src": "usage.png", "label": "settings → usage", "rings": [[85.5, 63.5, 12.5, 7]], "ringAt": ["word:button"]}]},
  {"slug": "04 — the catch", "pose": "wait", "bg": "black",
   "lines": ["But there's no undo."],
   "hero": {"type": "sticker", "lines": ["NO UNDO"], "red": true, "rot": -4}}
 ]
}
```

Beat keys: `slug`, `lines` (usually one; `_x_` = red italic serif), `pose` (presenter clip: talk, explain, calm,
laugh, hi, shrug, smile, think, clasp, wait, ok, shh, arms_crossed, facepalm, excited, stressed, shocked, angry,
sad, cry, panic, nervous, thumbs_up, point_up, point_side, count, wave, bored), `count` (new counter value),
`bg`, `wipe`, `pause_before`, `sfx` ([[time|"word:x", id, gain]]), `hero` (one item or a list).

Every hero item: `type`, `at` (`"word:xyz"`, `"word:xyz#2"`, `"word:xyz+0.2"`, seconds into the beat, or omitted =
beat start), `keep` (stay N more beats), `x`, `y` (centre, px), `rot`, `z`, `sfx` (false = silent),
`sfx_id`, `float` (false = no drift), `exit` ("cut" = no fade).

| type | keys |
|---|---|
| `card` | label, title (html ok), text, img, w |
| `num` | value, from, prefix, suffix, decimals, label, count (seconds) |
| `sticker` | lines [..], red, redLine, or text |
| `stamp` | text |
| `shot` | src, label, w, rings [[x%, y%, w%, h%]], ringAt [times] |
| `phone` | src or title, scale |
| `term` | title, lines [..] (types out; `$ ` turns accent), type (seconds) |
| `logo` | icon (e.g. simple-icons:claude), color, name |
| `list` | title, items [..], ticks [times] |
| `grid` | n, cols, hi [indexes], hiAt [times] |
| `compare` | left {title, text}, right {title, text}, rightAt |
| `comment` | who, keyword |
| `date` | month, day |
| `image` | src, w, radius, shadow |
| `html` | html (escape hatch) |

## Files

`beatreel.py` (CLI: voice → page → HyperFrames render → mix), `engine/beats.js` (all animation, one GSAP
timeline, seek-safe), `engine/style.css` (themes + components), `engine/fonts/` (Space Grotesk, Instrument Serif
italic, JetBrains Mono, Archivo variable for stickers). Lives in reel-kit/beatreel/ and uses the parent reel-kit (or `$REELKIT`)
for voice, sound and the character; HyperFrames + a headless Chromium (`HYPERFRAMES_BROWSER_PATH`).
Example: `examples/claude-reset/`.

## Adding a hero type

Add a builder to `B` in `engine/beats.js` (`(o, el, t) => {...}`; use `tl.set(el, {attr: {'data-on': 1}}, t)`
for state changes so seeking backwards works) and its CSS in `style.css`. Add any time keys it takes to the
list in `build()` in `beatreel.py` so `"word:x"` resolves. Then add it to the table above.
