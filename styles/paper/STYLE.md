# Style: paper

Off-white dotted paper, black/white UI cards with one red accent, a mono header (`// 01 · label`) with a live
counter, captions that land word by word with the voice (accent words in red italic serif), and a presenter at the
bottom who changes gesture on every beat. 1080×1920, 30 fps. Reference: a 66 s "AI reels system" explainer reel.
Examples: `examples/one-prompt.json` (10 s, every core card), `examples/card-tour.json` (stat, graph, image).

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
