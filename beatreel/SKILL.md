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
2. **Caption** (top-left, y≈170): short phrase blocks (≤7 words, split after punctuation), bold grotesk.
   **Nothing is shown before it is said**: each word fades in grey (with a little blur and lift) on its time and
   turns ink ~0.1 s later. When the next block starts, the old one slides up and fades in ~0.1 s. **One or two key
   words per line are red italic serif** (`_word_` in the script). Never centred, never at the bottom.
3. **Hero** (middle, y≈450–1150): one idea at a time, shown literally, and it **builds up on the words**: an idea
   usually lives 2–4 s as a big panel or object, and pieces land inside it as they are named (a pin drops on
   "you are here", a curve draws, a stamp slams on the verdict word, a label counts up). When the idea changes the
   whole thing leaves upward fast and the next one pops in. Objects carry a **halftone dot drop-shadow** and sit
   close to the presenter's head (they may overlap it slightly). What the references use, most common first:
   UI cards / browser windows / screenshots with a red ring on the one thing that matters · a huge red number that
   **rolls like an odometer** (digits blur and settle left to right) · condensed black/red sticker labels
   (`ONE RULE`, `WIDE OPEN`) · red outlined stamps (`SEALED`, `SETTLED`) · phones · terminals typing · checklists
   that tick on the word · rows of icon tiles landing one per word · grids (people, files) that assemble, highlight
   one, or fall away · ✕ vs ✓ cards · calendar pages · text that decodes from noise · the comment-bubble CTA.
4. **Presenter** (bottom, chest-up, head ≈ y 1180–1650): **rises in from below in the first 0.5 s**, and in the
   reference openings is **big and centred for ~1–1.5 s** before the first hero lands (`"cam": "big"`), then
   settles low. Gesture changes every beat to match the line (point up for a reveal, shrug for "but", shh for a
   secret, shocked for a twist, count for numbers), with a small bounce on each beat change. On a surprise it
   **reacts with burst lines** around the head (`"react": "word:x"`).

Rhythm: hero changes every ~2–3 s (median 2.1 s across the 25), 15–25 beats per minute-long video; a 25 s video is
7–9 beats. Voice only, **no music bed** (measured: the non-voice stem sits ~30 dB under the voice); soft pops
when things land, a swish on beat changes, impacts on stamps and reactions. Accents: a beat can flood red or black
for the punchline (`"bg": "red" | "black"`), a halftone dot wipe marks a chapter change (`"wipe": true`). The last
beat is always the CTA (comment a keyword / send to a friend / follow).

Themes: `paper` (off-white #efece6, ink, red #e8452c — most references), `ink` (dark navy, agents/dashboards),
`neon` (near-black, lime #c8f53c + pink glow, launches/AI video tools). `kit` mixes in reel-kit's look: its black grid background, Archivo
type, red #e5372d, red halftone shadows, and the presenter (use `"character": "otaku"` for Krish) rising out of a
rounded box with a red glow, like reel-kit's character box. Example: `examples/claude-meetings-kit/`. In `kit` the caption sits **under** the visuals, centred
(`caption_y` [with presenter, without], default [1150, 1580]); show the presenter only on beats where a gesture
fits (`"presenter": false` on the rest gives the visuals the whole frame), and explain every line with a scene that
acts it out (the explainer scenes below), not a static card. `"pop": false` on a hero makes it appear without the
pop, to continue the same object from the previous beat. The illustrated desk-room look seen in
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

Top-level keys: `name`, `theme`, `counter` {label, start}, `meta` (false = no slug/counter row at the top), `voice` (reel-kit voice block), `presenter` {scale, y}
(default 1 / 1060: head centre ≈ y 1340), `caption_words` (block size, default 7), `intro`, `sfx_level`,
`character` ("kai" default; or a reel-kit video character folder such as "otaku"), `avatar_colors` (override
Kai's palette: skin, skinSh, hair, shirt, shirtSh, cuff, tee, iris, …).

### The presenter: Kai (engine/avatar.js)

An **original** presenter drawn the way the references draw theirs, with his own face (the reference avatar is
the creator's likeness, so never copy it): flat fills and **no outlines** (form comes from one darker shade per
shape), thin lines only on the hands, square-dot halftone shadow, big head on sloped shoulders, two-bone arms
with a cuff, hands with real fingers. Curly dark hair with a fade, no glasses, no beard, open green zip hoodie
over a white tee. Drawn in code, so it animates on the reel clock: rises in, mouth opens on every word (bigger
for longer words), hands and head beat along on the stronger words, blinks every 2-4 s, slight body sway, new
pose every beat, waves on `hi`, shakes on `gasp`, sweats when nervous, thought bubble on `think`.

Poses (arms + face): talk (both hands raised, the references' default), calm, smile, explain/present (open palm
out to the side), both, hi/wave, point_up, point_side, one, count, count3, shrug, shocked (both hands over the
mouth), gasp (O mouth, hands out), oops (hands on cheeks), excited, shh, thumbs_up (with a wink), think, wait,
stop, facepalm, clasp, arms_crossed. Face-only moods on the talk/calm arms: laugh, nervous, stressed, sad,
angry, bored, skeptical, wink, cry, panic. Per arm a pose sets palm x/y, rotation, finger extension, finger
spread, thumb angle and `el: 1` (elbow outward instead of down). Redraws run in the timeline's onUpdate, so
seek with events on (`tl.seek(t, false)`) when screenshotting pages by hand. Every pose and expression is
shown in `engine/kai-poses.jpg`. Default placement: `presenter`
{scale 1, y 1060} (head centre about y 1340).

Beat keys: `presenter` (false = the presenter drops out, e.g. the Follow beat), `slug`, `lines` (usually one; `_x_` = red italic serif), `cam` ("big" = presenter starts large until
the beat's first hero lands), `react` (word or list of words: burst lines + impact), `pose` (presenter clip: talk, explain, calm,
laugh, hi, shrug, smile, think, clasp, wait, ok, shh, arms_crossed, facepalm, excited, stressed, shocked, angry,
sad, cry, panic, nervous, thumbs_up, point_up, point_side, count, wave, bored), `count` (new counter value),
`bg`, `wipe`, `pause_before`, `sfx` ([[time|"word:x", id, gain]]), `hero` (one item or a list).

Every hero item: `type`, `tilt` [rx, ry] (starts tilted in 3D and settles), `push` (slow zoom to this scale), `at` (`"word:xyz"`, `"word:xyz#2"`, `"word:xyz+0.2"`, seconds into the beat, or omitted =
beat start), `until` (a word: leave early), `keep` (stay N more beats), `x`, `y` (centre, px), `rot`, `z`,
`scale` (size multiplier), `sfx` (false = silent), `sfx_id`, `float` (false = no drift), `exit` ("cut" = no fade). Any item can take
`icon` (+ `color`) where it shows one.

| type | keys |
|---|---|
| `card` | label, icon, title (html ok), text, img, w |
| `panel` | w, h, label, children [items placed in panel px, each with its own `at`] |
| `browser` | tab, url, icon, title, text, w, h, incognito |
| `num` | value, from, prefix, suffix, decimals, label, count (seconds), size — rolls like an odometer |
| `scramble` | text, red, size, decode (seconds), label — decodes from noise |
| `sticker` | lines [..], red, redLine, or text, size |
| `stamp` | text, size |
| `shot` | src, label, w, rings [[x%, y%, w%, h%]], ringAt [times] |
| `phone` | src or title, scale |
| `term` | title, lines [..] (types out; `$ ` turns accent; verdict words are coloured), typeDur (seconds) |
| `logo` | icon (e.g. simple-icons:claude), color, name |
| `list` | title, items [..], ticks [times], mark ("x" for crosses), w |
| `row` | tiles [{icon, label}], ats [times] — icon tiles landing one per word |
| `grid` | n, cols, shape ("doc" for files), hi [indexes], hiAt [times], dropAt (all fall away) |
| `compare` | left {title, text}, right {title, text}, rightAt, swap (left is the ✓ side) |
| `comment` | who, keyword |
| `date` | month, day |
| `image` | src, w, radius, shadow |
| `html` | html (escape hatch) |
| `video` | src (mp4), media (start second in the clip), url, tab, w, aspect, fit, words [[time, text, red]] — a clip playing in a browser window, with pop-on labels |
| `meet` | people [{n, c}], title, url, icon (Claude logo), claudeAt, speak [[time, tile]], typing [[from, to]], outsiderAt, outsider, leaveAt, endAt — a video call acted out |
| `doc` | title, by, icon, lines ["# heading", "line", ...], ats or step — a doc writing itself |
| `speak` | who, c, text, dur — someone speaking: live waveform + words typing |
| `sort` | title, sub, icon, empty, notes [{t, col, c}], ats, sortAt, cols, hi, hiAt, w, h — sticky notes fly in, then sort into columns |
| `answer` | who, q, docs [..], hit, a, link, icon, checkAt, answerAt, linkAt — question, docs scanned, answer with its source |
| `mpage` | title, sub, icon, items [{icon, title, sub}], ats — a page whose rows land one per word |
| `wave` | label, strikeAt — an audio waveform that gets struck out |
| `plans` | items [{t, ok}], markAt — plan cards; the ones left out grey and cross, the rest light up |
| `flip` | pages [{m, d, y}], flipAt, dur — calendar pages flipping to a date |
| `send` | from, fromIcon, to, toIcon, c, sendAt — a paper plane flies to a person |
| `code` | file, tag, lines [..], lang ("md" or "py"), start, rows, lh, fs, first, scroll [[time, line]], marks [{line, to, at, until, tag, color: "green"}], scanAt, scanDur — a file viewer that scrolls, boxes lines and scans |
| `hub` | icon, label, plug + fromIcon, plugAt, items [{icon, title, a (angle)}], ats, r, cy, w, h — one thing reaching out to others |
| `pile` | items [..], hi [indexes], dropAt, each, fs, w, h — labels rain down and pile up |
| `gauge` | title, value, verdict, at2, count — a 0-100 dial (green / amber / red) with the verdict |
| `dots` | n, cols, cell, hi, hi2, redAt, darkAt, legend [[time, text, "r1"/"r2"]] — a 10 x 10 share grid |
| `profile` | img, handle, cat, bio, covers [paths], tapAt, gridAt — the follow end card: avatar ring, Follow button tapped (hearts), grid of earlier reel covers |
| `follow` | img, handle, text, tapAt — the follow card; the button turns to "Following" on tapAt |

### Fast-cut, visual-first reels (the user's current standard)

- **Each visual stays up to about 2.5 s** (1.5 s felt too fast). Write each beat as `"shots"`: a list of shots, each one item
  or a list of items shown together; a shot lasts until the next shot's `at` (the last until the beat ends). Set
  top-level `"max_hold": 2.6` and the build prints every item that stays longer. Vary the entrances with `"in"`
  (zoom, left, right, up, down, flip, drop, swing) and exits with `"out"` (left, right, zoom, down, shrink).
- **Show the source** whenever there is one (screenshots, the real file, the real command output); explain the rest
  with animated scenes (code, hub, pile, gauge, dots, send, meet, sort, answer...).
- **Presenter:** only on the "send this to a friend" frame. Put `"presenter": false` on every beatreel beat and end
  with `"outro": "outro.json"`, a reel-kit script holding the share scene (Krish in his box + the share sheet) and the
  follow card; beatreel renders it with reel-kit and appends it, then one music bed and one mix run over the whole.
  (`"flash"` cutaways still exist for other uses.) `"sfx": false` drops every sound effect except the intro.
- **Instagram-safe captions:** `"caption_y": [1420, 1420]` keeps the caption above the profile row; the kit caption box runs
  x 130-950. Keep visuals centred (x 540), at most ~880 px wide, in y 120-1380.
- **Music:** `"music": {"style": "curious", "bpm": 120, "level": -33, "duck_db": 3}` is a quiet code-made curiosity bed
  (plucked D Lydian arpeggio with echo, ticks, soft pad, a sub and kick lift in the middle third, a bell every fourth
  bar), built from the measured shape of the user's reference reel (120 BPM, D major colour, sparse bed under the voice).
  It sits about 18 dB under the voice and dips 3 dB more while he speaks.
- End with the reel-kit share and follow scenes via `outro` (the `profile` card is an alternative).
- Example: `examples/skillspector/`.

## Files

`beatreel.py` (CLI: voice → page → HyperFrames render → mix), `engine/beats.js` (all animation, one GSAP
timeline, seek-safe), `engine/style.css` (themes + components), `engine/fonts/` (Space Grotesk, Instrument Serif
italic, JetBrains Mono, Archivo variable for stickers). Lives in reel-kit/beatreel/ and uses the parent reel-kit (or `$REELKIT`)
for voice, sound and the character; HyperFrames + a headless Chromium (`HYPERFRAMES_BROWSER_PATH`).
Examples: `examples/incognito/` (24 s, every v2 feature) and `examples/claude-reset/`.

## Adding a hero type

Add a builder to `B` in `engine/beats.js` (`(o, el, t) => {...}`; use `tl.set(el, {attr: {'data-on': 1}}, t)`
for state changes so seeking backwards works) and its CSS in `style.css`. Add any time keys it takes to the
list in `build()` in `beatreel.py` so `"word:x"` resolves. Then add it to the table above.
