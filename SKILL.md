---
name: reel-kit
description: Make 9:16 explainer reels from a short script: voice, word-synced captions, animated UI cards, a gesturing presenter, beat and SFX. Paper + red style.
---

# reel-kit

Short vertical explainer reels in one look: off-white dotted paper, black/white UI cards with one red accent, a mono
header with a live counter, captions that land word by word with the voice (key words in red italic serif), and a
cartoon presenter at the bottom who changes gesture on every beat. Sound is a deep male voice (Kokoro `am_michael`),
a quiet code-made beat and a sound effect on every card move. Output: 1080×1920, 30 fps MP4 at -14 LUFS.

## 0. Setup (once per session)
```bash
[ -f ~/reel-kit/reel.py ] || git clone -q --depth 1 -b techinsixty https://github.com/anand-reddi/reel-kit ~/reel-kit
bash ~/reel-kit/setup.sh          # deps, Kokoro voice model (cached), earshot SFX; idempotent
cd ~/reel-kit
```
Everything below runs in `~/reel-kit`. Read `CHARACTER.md` there before adding or changing a presenter.

## 1. Write the script (this is the creative part)
Before writing JSON, settle the story with the user when the topic is new: hook (first 2 s must make a claim or a
promise), 3–6 beats, a closing line (follow / comment keyword). Fact-check every claim, number and name with a search
first; never invent figures. Budget: about **2.6 spoken words per second** (10 s ≈ 22 words, 30 s ≈ 70, 60 s ≈ 140).
Keep each line under ~8 words: one line = one caption beat.

```json
{
  "title": "...", "duration": 10,                    // optional: duration (s); default = voice length + 0.45
  "brand": { "handle": "@techinsixty", "bio": "line 1\nline 2", "avatar": "me.png" },
  "voice": { "name": "am_michael", "speed": 1.18, "say": { "SQL": "sequel" } },
  "music": { "style": "beat", "bpm": 100, "key": "minor" },   // key: minor | major | dark ; style "none" = no music
  "levels": { "music": -31, "sfx": -24 },             // optional loudness of the beds (LUFS)
  "character": "default",                              // a folder (see CHARACTER.md) or "none"
  "theme": { "accent": "#e5372d" },                    // optional: paper, ink, accent, grey, mid, card
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

## 2. Cards (one per scene; `python3 reel.py cards` lists them)
| type | use for | keys |
|---|---|---|
| `prompt` | a prompt / command being typed and sent | `text`, `tag`, `label`, `type_at`, `send_at` |
| `checklist` | steps, features, a stack — ticks per line | `title`, `items: [{label, icon}]` icons: doc wave cc play lock bolt code star dot |
| `code` | code typing in; optional rejected editor | `file`, `lines[]`, `type_at`, `line_step`, `reject: {title, stamp, at, stamp_word_at, stamp_at, cross}` |
| `stat` | a big number counting up + bars | `value`, `from`, `prefix`, `suffix`, `decimals`, `label`, `title`, `tag`, `bars[]` |
| `graph` | growth / "you are here" | `marker` (0–1), `marker_at`, `marker_label`, `x_label`, `y_label` |
| `image` | a real screenshot, with a highlight box | `src` (next to the script), `caption`, `height`, `fit` cover/contain, `highlight: {x,y,w,h,at}` (%) |
| `profile` | the follow CTA (uses `brand`) | `tap_at`, `button`, `done` |

Any card takes `"stamp": "TEXT"` or `{"text","at","x","y","rot"}` — a red rubber stamp with a shake and impact sound,
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
New card: add a function to `kit/cards.py` (`fn(p, cfg, ctx) -> html`, animate with `ctx.A(...)`, time with
`ctx.at(...)`, sound with `ctx.sfx(t, earshot_id, gain_db)`), register it in `CARDS`, style it in `kit/reel.css`.
Sound ids come from `earshot sfx list`. Presenter: see `CHARACTER.md`.

## Notes
- Fonts (Space Grotesk, Instrument Serif, IBM Plex Mono) and GSAP are vendored: renders need no network.
- Rendering needs Node (npx hyperframes), ffmpeg and a headless Chrome (`HYPERFRAMES_BROWSER_PATH` is auto-detected
  from Playwright's folders).
- Examples: `examples/one-prompt.json` (10 s, every core card), `examples/card-tour.json` (stat, graph, image).
