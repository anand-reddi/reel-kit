# Style: sketchbook (and sketchbook_dark)

Hand-drawn paper UI from [Looseleaf](https://github.com/kevintngo/looseleaf) (MIT: code, art and the Kevin Sans font):
paper cards with tape, real toggles and sliders, index cards circled in pen, rubber stamps, doodles, Polaroids,
handwritten captions. Two separate looks share one renderer:

| style | look | buddy |
|---|---|---|
| `sketchbook` | the original Looseleaf look: sage desk, light paper, yellow highlighter, orange marker | Stubby the pencil (Looseleaf's mascot, poses) |
| `sketchbook_dark` | the krishexplainz look: near-black dotted page with a soft red glow, dark paper, off-white ink, one red accent (highlights are red boxes) | an original black cat sticker that reacts with expressions; it never talks |

Examples: `examples/backburner-original.json`, `examples/backburner-dark.json` (the same 15 s script in both looks).

```bash
python3 reel.py make styles/sketchbook/examples/backburner-dark.json -o out.mp4
python3 reel.py cards sketchbook                      # card types and keys
```

## Script
Same top level as paper (`brand`, `voice`, `music`, `intro`, `scenes[].lines`, `*accent*` words, `pause_before`).
Per scene: `card` (below), `react` (the buddy), `buddy: false` (hide it for that scene), `caption_y` (default 745 on a
540x960 stage; the video is rendered at 2x = 1080x1920). Top level `buddy: {x, y, size}` moves the buddy (default
318, 520, 185). Colours: `theme_colors: {accent, hi, hi_text}` override the look's accent / highlighter.

Times (`at` keys): seconds after the scene start, `start`, `end`, `line:N`, `line:N:end`, `word:follow`, each with an
optional `+0.1` / `-0.2`, exactly like paper.

## Cards
| type | use for | keys |
|---|---|---|
| `hook` | the claim, big type on graph paper | `rows: [{text, kind: dim\|big\|mark, at, size}]`, `stock` graph\|paper\|kraft |
| `split` | a real toggle + slider that moves on cue (who does what, before/after, a setting) | `title`, `tabs: [a, b]`, `labels: [left, right]`, `keys: [{at, tab, value 0-100}]` |
| `stat` | a number circled in pen on an index card, optional rubber stamp | `label`, `value`, `sub`, `at`, `circle` (default true), `stamp: {text, at, x, y}`, `size` |
| `shot` | a real screenshot taped to paper (crop personal info first) | `src`, `chips: [{text, at, mark, dim}]`, `height` |
| `checklist` | requirements, steps: boxes tick on each line | `title`, `items: [{text, at}]` |
| `versus` | good vs bad, two index cards | `good: {title, text, at}`, `bad: {title, text, at}` |
| `note` | one statement on a sticky note | `text`, `sub`, `color` yellow\|green\|orange\|pink\|blue, `at`, `size` |
| `follow` | the ending: Polaroid of `brand.avatar`, handle, Follow → Following; `"platform": "youtube"` = Subscribe → Subscribed | `tap_at`, `platform` |

Any card takes `top` (px on the 540x960 stage) and `doodle: {name, at, x, y, size}`. Doodles: spiral confetti swirl star
sparkle sun moon cloud lightning flower leaf tulip tree mushroom sprout feather wave heart cup key crown smiley house
balloon pencil eye umbrella fish book.

## The buddy (`react`)
`"react": [{"at": "word:GPU", "react": "wow", "jump": true}, ...]` — reactions: `idle`, `wow`, `happy`, `smug`, `love`,
`think`, `point`, `shrug`. Stubby maps them to poses (oops, celebrate, point, wave, think, shrug), the cat to faces
(shocked, happy, smug, love; `look: -1..1` moves its eyes). Raw `pose` (Stubby) or `face` (cat) override the mapping.
It breathes, blinks and swishes its tail on its own, and leaves before the `follow` card (one character on the ending:
the avatar).

## Rules that still apply
Intro sound, natural lines, Puck at speed 1.0, two cuts (Instagram "Follow", YouTube "Subscribe"), fact-checked claims,
captions never covering a card: the render checks every line's middle and end and prints `!` lines for any caption that
touches a card, stamp, doodle, button or the buddy. Move the card (`top`), the doodle (`x`, `y`) or `caption_y` and
render again.

## How it renders
`setup.sh` installs Looseleaf at a pinned commit in `~/.cache/reelkit/looseleaf` (`REELKIT_LOOSELEAF` overrides).
`make` copies `app/` into it, bundles one page with Vite, writes `config.json` (resolved times) next to it, seeks the
page frame by frame in Chromium (GSAP timeline + React state as a function of time) and encodes with ffmpeg; the usual
voice / music / SFX mix is added by `reel.py`.
