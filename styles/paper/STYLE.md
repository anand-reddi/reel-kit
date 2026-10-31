# Style: paper

Off-white dotted paper, black/white UI cards with one red accent, a mono header (`// 01 · label`) with a live
counter, captions that land word by word with the voice (accent words in red italic serif), and a presenter at the
bottom who changes gesture on every beat. 1080×1920, 30 fps; `"aspect": "16:9"` gives 1920×1080 (below). Reference: a 66 s "AI reels system" explainer reel.
Examples: `examples/one-prompt.json` (10 s, every core card), `examples/card-tour.json` (stat, graph, image),
`examples/cleanyourtv.json` (40 s tool reel: camera layouts, short captions, expressions).

## 1. Write the script (this is the creative part)
Before writing JSON, settle the story with the user when the topic is new: hook (first 2 s must make a claim or a
promise), 3–6 beats, a closing line (follow / comment keyword). Fact-check every claim, number and name with a search
first; never invent figures. Budget: about **2.6 spoken words per second** (10 s ≈ 22 words, 30 s ≈ 70, 60 s ≈ 140).
Keep each line under ~8 words: one line = one caption beat.

```json
{
  "style": "paper", "title": "...", "duration": 10,                    // optional: duration (s); default = voice length + 0.45
  "brand": { "handle": "@techinsixty", "bio": "line 1\nline 2", "avatar": "me.png" },
  "voice": { "name": "am_michael", "speed": 1.18, "say": { "SQL": "sequel" } },
  "music": { "style": "beat", "bpm": 100, "key": "minor" },   // key: minor | major | dark ; style "none" = no music
  "levels": { "music": -31, "sfx": -24 },             // optional loudness of the beds (LUFS)
  "character": "default",                              // a folder (see CHARACTER.md) or "none"
  "theme": "dark",                                     // "light" (default) | "dark" | { "base": "dark", "accent": "#..." }
  "scenes": [
    { "label": "one prompt",                           // header: "// 01 · one prompt"
      "counter": { "name": "PROMPTS", "value": "0", "steps": ["1"] },
      "pose": "up",                                    // or a list (one per beat), or omit to auto-cycle
      "face": "happy",                                 // expression (characters with faces, see CHARACTER.md), or a list per line
      "layout": "full",                                // optional camera layout: "full" (presenter fills the frame, no card)
                                                       // or "box" (presenter in a rounded frame at bottom centre; default once any scene sets a layout)
      "lines": ["This reel was made from one *prompt.*"],   // *word* or *two words* = red serif accent
      "card": { "type": "prompt", "text": "make a 10s reel", "tag": "1 prompt" } }
  ]
}
```
(The `//` notes are annotations; real JSON has no comments.) Counter forms: `{"name","value"}` fixed, `{"name","steps":[...]}` changes on each line, `{"name","from","to","count_for"}` counts up.
Write "AI", "SBI", "API" plainly (no spaces); add `voice.say` only for words Kokoro gets wrong.

## 2. Cards (one per scene; `python3 reel.py cards paper` lists them)
| type | use for | keys |
|---|---|---|
| `prompt` | a prompt / command being typed and sent | `text`, `tag`, `label`, `type_at`, `send_at` |
| `checklist` | steps, features, a stack — ticks per line | `title`, `items: [{label, icon}]` icons: doc wave cc play lock bolt code star dot |
| `code` | code typing in; optional rejected editor | `file`, `lines[]`, `type_at`, `line_step`, `reject: {title, stamp, at, stamp_word_at, stamp_at, cross}` |
| `stat` | a big number counting up + bars | `value`, `from`, `prefix`, `suffix`, `decimals`, `label`, `title`, `tag`, `bars[]` |
| `graph` | growth / "you are here" | `marker` (0–1), `marker_at`, `marker_label`, `x_label`, `y_label` |
| `image` | a real screenshot, with a highlight box | `src` (next to the script), `caption`, `height`, `fit` cover/contain, `highlight: {x,y,w,h,at}` (%) |
| `profile` | the follow CTA (uses `brand`) | `tap_at`, `button`, `done` |
| `figure` | a live isometric line drawing (hairline, 33 objects) that reacts on cue | `name`, `path: [{at, x, y}]` (pointer 0–1 in the figure box; no path = it plays its own tour), `intensity` (0–1), `caption`, `readout` (red live readout, default on), `leave`, `mount_at`, `width`, `colors` |

Any card also takes `"sfx": [{"at", "id", "gain"}]` for extra sound hits, and `"stamp": "TEXT"` or `{"text","at","x","y","rot"}` — a red rubber stamp with a shake and impact sound,
and `"top"` (px) to move it. Times (`at` keys) accept: seconds after scene start, `start`, `end`, `line:N`,
`line:N:end`, `word:follow` — each with an optional `+0.1` / `-0.2`. Lines split across 2–4 caption lines per scene
read best; a checklist with as many items as lines ticks exactly on each line.

## 3. Render and check
```bash
python3 reel.py make my-reel.json -o out/my-reel.mp4 --stills
```
`--stills` writes `out/my-reel-frames.png` (one frame per line). Look at it before sending: captions inside the
frame, no card overlapping the presenter's head, stamps readable. `--quality draft` renders faster while iterating.
The voice must fit: if it overruns, the kit stops and says so (cut words or raise `voice.speed` up to ~1.25).
Build files go to `build/<name>/` next to the script (`film/index.html` is a normal HyperFrames composition).

## 4. Extending
New card: add a function to `styles/paper/cards.py` (`fn(p, cfg, ctx) -> html`, animate with `ctx.A(...)`, time with
`ctx.at(...)`, sound with `ctx.sfx(t, earshot_id, gain_db)`), register it in `CARDS`, style it in `styles/paper/style.css`.
Sound ids come from `earshot sfx list`. Presenter: see `CHARACTER.md`.


## Figures (the `figure` card)
Live drawings from [hairline](https://github.com/lucasmarkes/hairline) (MIT, vendored in `assets/vendor/`), recoloured
to the paper palette. They run on a virtual clock tied to the timeline (`core/clock.js`), so renders are frame-exact.
Names: riffle terrain exploded phosphor slow turntable keyboard elevator phone laptop terminal cabinet branches vault
lockers padlock patch dish router loupe sieve rail plug query drawer basket plot hub relay settle format rebuild stack.
What the pointer does per figure (from hairline's docs): height picks a floor/layer/drawer/frame (`elevator`, `exploded`,
`phone`, `drawer`, `stack`, `sieve`, `cabinet`, `terminal` scrolls, `laptop` lid); nearness opens `padlock`, lifts
`terrain` and `keyboard`; circling the dial turns `vault` (readout "dial NN"); a `path` that ends on a word lands the
reaction on that word. Without a path the figure plays its own tour (slow to start: give it 3 s or more).
Recipes: vault dial = 9 points on a circle centred (0.42, 0.5), radius 0.22, 0.22 s apart; padlock opens = from
(0.1, 0.95) to (0.55, 0.22) ending on the word; terminal scroll = y 0.25 → 0.8 across the scene.
Example: `examples/figures.json`.

## Camera layouts
Setting `"layout"` on any scene turns on the presenter camera: the character sits in a backdrop that hard-cuts per scene
between `"box"` (a rounded frame at the bottom centre; head and hands break out over its top and sides, and the box stacks above
cards and captions) and `"full"` (a close-up filling the frame, for the
hook, opinions and punchlines; give those scenes no card). Tune per character in `character.json` with
`"camera": {"top_y": 78, "box_scale": 0.82, "box_pop": -90, "full_scale": 1.55, "full_top": 600, "backdrop": "<css background>"}`.
SVG characters only. Without any `"layout"` the presenter stays at the bottom as before.

## Fonts
`"fonts"` in the script picks a preset: `"grotesk"` (default: Space Grotesk, Instrument Serif accents, IBM Plex Mono),
`"bricolage"` (Bricolage Grotesque bold, DM Serif Display accents, JetBrains Mono) or `"archivo"` (Archivo extra-bold,
Playfair Display accents, JetBrains Mono; the heavy look of big explainer reels). All OFL, vendored in `assets/fonts/`.

## Header
`"header": "chips"` swaps the mono `// 02 · label   NAME 1/3` header for a red number tag, a bold uppercase label in the
caption font, and the counter in an outlined pill.
`"header": "none"` removes the top header entirely.

## Short captions, headline, presenter-off shots
`"captions": "short"` shows one short phrase at a time (write lines of 1–4 words), centred: just above the presenter's
head in `"box"` scenes, under the card in `"layout": "none"` scenes (presenter off screen, card zoomed up), near the
top in `"full"` scenes. Cards cut in and out with a zoom-blur and a swish; accent words get a soft pop. Move rows with
`"caption_y": {"box": 850, "none": 1260, "full": 200}`. A scene's `"headline": ["bold line", "accent block line"]`
puts a title at the top. The script's `"camera"` overrides the character's (e.g. `"box": [x, y, w, h]`, `box_scale`).
New cards: `post` (a quoted social post, `[[phrase]]` highlights at `highlight_at`), `terminal` (typed `lines`,
a `progress` list that strikes items off with a counter and badge, a `done` check overlay) and `repo` (owner/name,
description with `[[highlight]]`, topics, stats row). Example: `examples/cleanyourtv.json`, a 40 s tool reel in this
format with no music, voice + SFX only (screenshots from the MIT-licensed cleanyourtv repo, credited in the file).

## Captions, cuts and cards added for tool reels
- **Captions** (`"captions": "short"`): words blur in one at a time and the line re-centres as it grows (transform
  only); plain words are dimmed; `*word*` = a red text-selection box (Poppins bold, bar grows with the words,
  handles with knobs, no sound); `_word_` = italic serif; lines blur out. `"accent_style": "italic"` keeps the old
  red italic accent. Per scene: `"caption_y"`, `"captions": "off"`.
- **Cuts** (`"cut"` per scene, the card leaves the way the next scene arrives): `zoom` (default), `whip`, `flash`,
  `impact` (2-frame ink frame, speed lines on ones, smear-in; use once), `glitch`, `dip`, `hard`; each has its own sound.
- **Scene fx** (`"fx": [{"type", "at"}]`): `confetti`, `ping` (alert ring + ding at x,y), `shake`, `speed`, `flash`,
  `riser` (peak on "at"), `sfx` (any earshot id). `"punch": true` jumps the frame in on accent words in `full` shots.
- **Cards**: `clips` (a product's own clips in an app window, one per line, label pills, optional `url` bar that
  types in), `lineup` (transparent character clips popping in), `kinetic` (full-frame type pages: word slam, number
  page on an accent wipe), `flow` (nodes + arrows + a signal dot + a speech bubble), `insert` (a full-frame clip).
- **Presenter**: gestures can land on a word (`"face": [{"face": "facepalm", "at": "word:staring"}]`); clips skip their
  wind-up so the gesture peaks on the word. Full-screen shots sit on the plain page background.
- **Voice**: each sentence is read in one go (default voice `am_puck`, speed 1.0); lines are found inside it.

### Presenter glow and box style
Dark theme puts a soft accent (red) glow behind the presenter, like the profile picture. Full shots: the glow sits
behind the head on the plain page. Box shots (`box_style`, default `glow` in dark, `studio` in light): `glow` = a dark
box with the glow clipped inside it (the head still breaks out over the top), `studio` = the lit studio wall,
`open` = no box, glow on the page. Override with `"camera": {"glow": false | "#hex", "box_style": "..."}`.

### Icons: always from the icon library
Every icon comes from `core/icons.py` (Iconify sets, about 17,000 icons, free licences). Never use emoji or text glyphs as
icons. Name them `"set:name"` and find names with `python3 reel.py icons <word>`:
- **Companies, AI tools, apps:** `logos:` (full colour, e.g. `logos:openai-icon`, `logos:claude-icon`, `logos:cursor`) or
  `simple-icons:` (one colour, 3,700 brands, e.g. `simple-icons:github`; best on dark cards).
- **Languages and dev tools:** `devicon:` (full colour, e.g. `devicon:python`, `devicon:docker`).
- **UI ideas (key, server, lock, user, file):** `lucide:` first, `tabler:` when lucide lacks it.
- **Friendly colour objects (key, rocket, money):** `fluent-emoji-flat:`.
Where: flow nodes `"icon"`, checklist items `"icon"`, kinetic pages `"icon"`; add `"color": "#hex"` for one-colour sets.
A logo of a dark brand (GitHub, Vercel) disappears on black: use its `simple-icons:` version, which takes the text colour.

### Intro slides (kinetic)
The opening pages use the video's own look: theme background with the dot grid (and the red glow in dark), the caption
font, and the accent as the same red selection box the captions use (`"accent": true`). Words blur in like captions; no
full-colour slabs, no sound on the red box.

### Presenter: only when the gesture matches the line
Show him (`layout` box or full) only when a clip fits what is being said; otherwise `"layout": "none"` (visuals only).
Every visible scene names its clips in `"face"`, timed onto the word they belong to (`{"face": "shh", "at": "word:password"}`);
he holds `calm` until the first one lands. `reel.py make` warns about a visible scene with no gesture.

| the line is... | clip |
|---|---|
| a definition, plain explanation | `talk` (open hand), `explain` (serious, both hands) |
| a tip, the key point, "remember" | `point_up` |
| about the card / "look at this" | `point_side` |
| a list, steps, "two things" | `count` |
| "don't", "never", "stop" | `wait` (palms out) |
| a secret, password, private | `shh` |
| a question, "how does it..." | `think` |
| a problem, pain, "we've all done this" | `facepalm`, `stressed`, `nervous`, `bored` |
| a surprise, a big number | `shocked` |
| good news, "it works", "free" | `thumbs_up`, `ok`, `excited` |
| a shrug, "who knows", "it depends" | `shrug` |
| skeptical, "not convinced" | `arms_crossed` |
| hello / follow / end | `hi`, `wave`, `point_up` on "follow", `smile` |

### Captions always fit the frame
A spoken line wider than the frame is split into caption chunks between words, on the voice timing (a red selection run
is never split; no orphan last word). A chunk that is still slightly too wide is scaled down to the safe width, measured
in the browser with the real fonts (`capfit`); kinetic words do the same (`kfit`). Keep red runs to 1-2 short words.
`"caption_width"` (default 1040, estimated px) sets when a line splits.


## 16:9 (`"aspect": "16:9"`)
1920×1080. The 9:16 column (header, captions, cards) keeps its 1080-wide coordinates on the left
(`"column": {"x": 60, "y": -70, "scale": 1.0}`), the presenter stands on the right, bottom on the frame edge
(`"presenter": {"x", "y", "width"}` overrides). Use the default caption style and normal cards; camera layouts
(`box`/`full`), `kinetic` and full-frame inserts are still 9:16-only. Keep a scene to 3 caption lines so the card is not
pushed to the bottom edge. Example: a 25 s five-step how-to (checklist per step, profile card at the end).
