# kinetic

Kinetic-type motion design in 9:16 (1080x1920): huge words on every beat, the ground colour flipping on phrase
changes, whip pans, 3D letters the camera flies through, slot-reel counters, comets that draw lines, a hard drop.
The look follows Scenario's "kinetic film" (the "Just code" launch film) and its open motion library; the engine
here is our own code (`engine/runtime.js`, `engine/blocks.js`), written for reels. Their engine ships without a
licence, so none of it is copied: only the ideas, the block list and the craft rules below.

Every frame is a pure function of time (one GSAP timeline, no `Math.random`, no state between frames), so the
renderer can seek anywhere. `reel.py make` captures 60 fps and blends pairs into real motion blur at 30 fps
(`--quality draft`: 30 fps, no blur). `reel.py board` shows every frame first (three per scene without a voice).

Example: `examples/every-block.json` (50 s, every block, music only).

## Script

```json
{ "style": "kinetic", "bpm": 128, "voice": false,
  "music": {"style": "beat", "bpm": 128, "key": "minor"}, "levels": {"music": -19, "sfx": -16},
  "sfx_set": "cinema", "palette": {"bg": "#0b0b0b", "paper": "#f2f1ee", "accent": "#e5372d", "hot": "#ff8a3d", "ink": "#0b0b0b"},
  "hud": "KRISHEXPLAINZ · KINETIC", "hud_out": 48.0, "captions": "sub",
  "scenes": [ { "beats": 8, "block": { "type": "Words", "shots": [ ... ] } } ] }
```

- **With a voice** (the usual reel): scenes have `lines` like every kit style and the block plays under them; the
  voice lines also run as a small subtitle at the bottom (`"captions": "off"` hides it). **Without** (`"voice": false`):
  each scene lasts `beats` on the `bpm` grid, and the music carries it (raise `levels.music`).
- **Times** inside a block: a number is beats after the block start (`B(k)`); strings work as in the other styles:
  `"1.5s"`, `"line:1"`, `"line:1:end"`, `"word:code"`, `"end-0.2"`.
- **Backdrop** on any block: `"backdrop": {"src", "blur", "dim"}` puts a blurred, darkened image behind it instead of the flat ground (keep text grounds `bg` so the ink stays light).
- **Colours**: palette names (`bg`, `paper`, `accent`, `hot`, `ink`) or hex. Text picks a readable ink on its ground.
- Numbers on screen come from the film or the user, never invented: `{lines}` (lines of engine code), `{frames}`,
  `{seconds}` are filled in.
- The intro sound, the beat, the -14 LUFS mix and the sound sets (`sfx_set`) work as in every style; each block
  places its own sounds on its hits.

## Blocks (14)

| block | what it does | keys |
|---|---|---|
| `Words` | one idea per beat: a run of shots (below); `charge: true` charges a point before the first hit; `exit: {type: flash|whip, at}` | `shots`, `charge`, `ground`, `exit` |
| `Strike` | "NO <thing>." over a mock of the thing, a glowing slash, then the thing falls apart | `items: [{at, word, ground, ui: {type: timeline|tiles|rack|image|lines, title, tag, tiles, rows, src, lines}}]` |
| `Graph` | comets draw the axes, the camera rides the comet drawing the curve, a big number (counts if numeric) | `number`, `label`, `sub`, `ticks: []`, `curve: exp|linear`, `ground`, `portal` (zoom through at the end) |
| `Hero` | the kicker tumbles in, a comet spirals to the centre, an extruded 3D title flies out of depth and orbits | `kicker`, `title`, `sub`, `chevron`, `landZoom`, `whipOut`, `size`, `ground` |
| `Prompt` | a comet draws the box, the brief types while the camera follows the caret, keywords light up | `label`, `text: [[text, keyword?]]`, `unit` (a live count), `doodles` (hand-drawn rings), `ground` |
| `Stretch` | one word on the variable width axis: drop slam, elastic stretch, weight dip, squeeze, stretch | `word`, `grounds: [[beat, ground]]`, `code` (source backdrop) |
| `Fly` | extruded words in depth inside chamfered portals; the camera flies through with a banked roll | `words: [[word, ground]]` |
| `Notes` | notes typed into a panel; each changes the preview (`recolor`, `trim`, `punch`, `flip`) | `preview`, `notes: [[text, action]]`, `segments: [[name, px]]`, `file`, `tag`, `panel` |
| `Counters` | giant numbers on slot reels over the film's own source flying past | `counters: [[value, label]]`, `title`, `source`, `color` |
| `Progress` | line 1 renders itself (outline, a scan line fills it), line 2 slams, cards ride a conveyor, a progress bar | `lines`, `cards: [[word, ground, ink]]`, `label`, `doneLabel`, `doneRight`, `ground` |
| `Chain` | words far apart in one world; the camera rides a comet from node to node, each lands with a hit | `nodes: [[word, sub, colour]]`, `marks` (a brand logo per node), `at` (when each node lands, e.g. on its word), `gap` |
| `Rewind` | the film so far plays backwards inside a tilting playback window, which then fills the screen | `from` (seconds to rewind from), `label` |
| `Picture` | an image or a clip: slash/iris/wipe reveal (`none` = on screen from frame 1, for a hook), push and pan, a punch-in on every word, cut-ins, weather | `src`, `words: [[beat, text, colour]]`, `reveal`, `cutIns: [[beat, zoom, [x, y], sound]]`, `weather: rain|snow|dust`, `tint`, `fit`, `device: browser` (a browser window with a URL pill, `url`, tilting in with `enter: tilt`); `device: scope` (a round sensor lens: turning tick ring, crosshair, a `hud` label; `scopeSize`, `scopeTop`, `enter: iris`); `device: player` (the clip in a desktop video-player window: title bar, controls, a running progress bar; `title`, `time`, `aspect`, `playerWidth`, `playerTop`); `subs: [{start, end, words: [[at, word]]}]` (voice subtitles under it, the spoken word lit in an accent box; `subsY`); `device: phone` (a realistic phone mockup over a blurred copy; `enter: rise|swing|keep|none`, `phoneWidth`, `phoneTop`, `wordsY`, `zoom`); `blur: [px, at]` (starts out of focus, snaps sharp at `at`); `overlay: {src, out, width, top}` (a title or logo over the picture that flicks out fast at `out`); `tag` (a small mono label under the words, e.g. a place) |
| `Logo` | a line, a slash and a hit; the mark drops in, the name types, tagline and small print | `mark` (an .svg, an image or an icon "set:name"), `markSize` (px), `wordmark`, `tagline`, `small`, `case`, `width` |

### Words shots

`{at, style, text, ground, color, size, wdth, in, fx, ...}`: each shot runs until the next one starts.

| style | look |
|---|---|
| `slam` | letters tumble in, outlined ghost rows scroll above and below (`echo: false` off, `tumble: false` for a straight slam, `from` = start scale) |
| `punch3d` | an extruded word flies out of depth with an echo trail, then turns slowly |
| `stack` | `[kicker, word]`: the kicker slides in, the word slams `second` beats later on an accent bar |
| `pair` | `[line1, line2]`: from the left and the right |
| `split` | `[small, big]`: the small line first, the big word slams in from the right `second` beats later |
| `cut` | a hard-cut word for runs of beat cuts (`size`, `rot`, `rgb` for an RGB split) |

Extras on any shot: `mark` / `mark2` (brand logos, an icon "set:name", .svg or image, that pop in above the word; show the logo whenever a brand is named; `markY`, `markColor`); `in: cut|whipX|whipXr|whipY`; `fx: punch|hit|beat|none` (`big` = the heavier impact, `cue`/`gain`
= an extra sound); `scramble: [a, b]` (glyphs resolve between beats a and b of the shot); `glitch` (`glitchAt`);
`inverts: [beats]` (2-frame invert flashes); `flip: {at, ground, color}` (ground flips mid-shot); `dot` (accent the
last character); `glyphs` (a burst of code glyphs); `code` (the film's source as a backdrop); `note` + `noteAt` (a mono
line typed under the word); `dy` (nudge).

## Craft (what keeps it reading as motion design, not a slideshow)

- One idea per beat or half beat; one or two words filling the width. Function words stay small.
- Nothing parks: no still stretch over about 0.6 s before the end card. Every block drifts, scrolls or orbits
  between hits; check the render with `reel.py check` (freezes) and by eye on the board.
- Transitions are moves (whips, a zoom through a word, a collapse), never fades. Flip the ground on phrase changes.
- Never the same treatment on two shots in a row; vary scale and density (poster slams, mid phrases, mono notes).
- Glow only on dark grounds; flat grounds stay flat.
- Words are measured and fitted to the frame after the fonts load (the page waits for them).
- Headless capture: no `mix-blend-mode` layers (they stall Chromium's capture with 3D type on the page), and
  `window.seek` style helpers must not return the timeline object (serialising it hangs the capture).

## Clean explainer blocks (Remotion / GSAP-skill looks)
Minimal, grey-on-black chapters for tool rundowns and data beats. All seekable, all on the dotted paper backdrop.
- `StyleList` — "N styles, one prompt": title + brand row, a numbered list that fills in while a framed card plays
  each item (`items: [{name, src, at, mediaStart}]`, `marks`, `names`, `enter: false` for a full first frame).
- `Route` — a dark world map (`src: assets/maps/world.svg`), city dots pop and red arcs draw leg by leg with a
  travelling glow (`view: [lonW, latN, lonE, latS]`, `cities: [[name, lon, lat]]`, `route`, `legs`, `label`, `title`).
- `SkillCard` — chapter card: icon, "02 / 03 ——— SKILL" rule, a huge name and one line (`mark, index, kicker, title, sub`).
- `TypeOn` — one word types in with an accent underline (`text, sub, color`).
- `Steps` — line-icon boxes joined by drawn arrows (`steps: [[svg, label, at]]`), then optionally a bar chart with a
  trend line and a bold/light title (`chart: {at, bars: [[label, value]], title: [bold, light]}`).
