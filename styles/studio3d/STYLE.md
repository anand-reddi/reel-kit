# Style: studio3d

One continuous camera through a matte 3D studio (three.js): warm grey floor with a faint grid, soft shadows, charcoal /
white / glass objects, one accent colour per meaning (orange = active, red = problem, blue = the fix, green = OK).
Overlays: a 5-dot state bar with the current state's label, a "Simplified · not to scale" tag, callout labels with
leader lines that follow 3D points, big black titles for the named idea, and a black caption pill at the bottom whose
words turn white as they are spoken. No presenter, no hard cuts. 1080×1920, 30 fps.
Reference: three ~90 s "how does X work" explainers (Kindle e-ink, foldable glass, QR error correction).
Example: `examples/ois.json` + `examples/ois.scene.js` (10 s, optical image stabilization).

## Story shape
Surprising fact → "so how?" → a simple physical model built step by step → the named concept (title) → payoff.
Every transformation happens in place, in one world: the camera travels, objects morph, nothing cuts.

## Script (JSON)
```json
{
  "style": "studio3d", "title": "OIS", "duration": 10,
  "scene": "ois.scene.js",                         // the topic's 3D scene module, next to the script
  "voice": { "name": "am_michael", "speed": 1.08 },
  "music": { "style": "beat", "bpm": 84, "key": "major" }, "levels": { "music": -33, "sfx": -23 },
  "tag": "Simplified · not to scale",
  "states": [ { "label": "Still", "at": "start", "color": "#141518" }, { "label": "Shaking", "at": "word:shakes", "color": "#d93a2b" } ],
  "titles": [ { "text": "Optical image stabilization", "sub": "The lens moves, so the picture doesn't.", "at": "line:3:end+0.35", "until": "end" } ],
  "sfx": [ { "at": "word:magnets", "id": "pro_pop_in/deep", "gain": -8 } ],
  "scenes": [ { "lines": ["Your camera lens hangs on springs.", "When your hand shakes,"] } ],
  "fov": 30, "drift": 0.03
}
```
Use 5 states (the bar has as many dots as states). Times use the usual grammar: seconds, `start`, `end`, `line:N`,
`line:N:end`, `word:text`, each with `+0.2` / `-0.1`. Captions show one line at a time: keep lines under ~9 words.
State changes get a tick and titles a whoosh automatically; add the rest with `sfx`.

## Scene module (JS)
`export default function (S) { ... }` runs once at load. Build objects, then animate them in one of two ways:
GSAP tweens on `S.tl` at `S.at(...)` times, or `S.onFrame(t => ...)` for anything computed from time (shakes, physics,
beams). Both are seekable; never use Math.random (use a seeded generator) or the wall clock.

| API | what it does |
|---|---|
| `S.THREE`, `S.scene`, `S.camera`, `S.tl`, `S.at(spec)`, `S.lines`, `S.duration` | the basics |
| `S.C` | palette: floor grid charcoal dark ink white glass orange red blue green |
| `S.mat(color, {rough, metal, opacity, emissive, unique})` | cached standard material; `unique` for one you will animate |
| `S.box / rbox / cyl / sphere / torus (..., color, [x,y,z], parent, opts)` | meshes with shadows; `rbox(w,h,d,radius,...)` is rounded |
| `S.group([x,y,z], parent)`, `S.spring(radius, length, turns, wire, color, parent)` | groups; a helix spring along +X |
| `S.phone([x,y,z], {w, h, color, screen})` | a phone slab with screen and camera bump |
| `S.cameraPath([{at, pos, look, ease}])` | the one continuous camera move (keys tween in order) |
| `S.label({anchor, title, sub, at, until, dx, dy, color, offset})` | callout that tracks a 3D object/point; kept inside the frame |
| `S.onFrame(fn)` | called every frame with t (seconds) before rendering |

Framing in 9:16: the frame is narrow (≈17° horizontal at fov 30), so keep the camera 2× further back than feels
natural; keep the subject between y≈500 and y≈1400 px (state bar above, caption pill at 1500). Raise the `look`
target to push the subject down when a title is up. Check `--stills` frames for labels off-frame and captions over
the subject.

## Performance
Software WebGL renders about 15 s of wall time per video second at 1080×1920 (shadows on). Use `--quality draft`
while iterating; keep meshes under ~5k and shadow-casting lights to one.
