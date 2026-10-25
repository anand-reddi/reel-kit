# Plugging in a presenter character

A character is a folder with a `character.json`. Point a script at it with `"character": "characters/goku"` (relative to the
script or the kit) or `"character": "none"` for no presenter (cards then sit lower). `characters/default/` is the
placeholder.

## Option A: SVG (full lip sync, blinks, gestures). Best result.

`character.json`
```json
{ "type": "svg", "file": "character.svg", "x": -60, "y": 1130, "width": 1200,
  "head_origin": "600 480", "wave_origin": "800 560", "avatar_view": "395 70 410 410",
  "poses": ["up", "palms", "card", "thumb", "shrug", "wave"] }
```
`character.svg` must use these ids (any drawing style; viewBox is yours, `x`/`y`/`width` place it on the 1080×1920 frame):

| id | what it is | default visibility |
|---|---|---|
| `pres-body` | group wrapping everything (bounces on each pose change) | visible |
| `head` | head group (tilts around `head_origin`) | visible |
| `pose-<name>` | one group per pose: the arms/hands for that gesture | `opacity="0"` |
| `m-closed`, `m-o`, `m-smile` | mouth shapes: closed, open (talking), smile (end) | only `m-smile` visible |
| `eyes-open`, `eyes-shut` | eyes and the blink | `eyes-shut` `opacity="0"` |

Pose names are free; the script's `pose` / `pose_cycle` use them. Built-in scripts expect `up` (point up), `palms` (open hands),
`card` (point at the card), `thumb` (at chest), `shrug`, `wave`. `avatar_view` is the crop used for the profile-card avatar.
The default's generator (`characters/default/make.py`) is a working template.

### Secondary motion (both options)
Optional keys in `character.json`, all tied to the timeline:
`"idle": [{"sel": "#tail", "rot": 12, "period": 1.7, "origin": "930 600"}]` continuous sway;
`"twitch": [{"sel": "#cat-ear", "rot": 14, "every": 2.6, "offset": 0.9, "origin": "896 410"}]` a quick flick every few seconds;
`"blink2": [{"open": "#cat-eyes-open", "shut": "#cat-eyes-shut", "every": 3.3}]` a second set of eyes (a pet);
`"react": {"sel": "#cat", "y": -34, "rot": -6, "origin": "880 610"}` a hop whenever a stamp lands.

## Option B: PNG poses (fastest from an existing avatar app or drawing)

```json
{ "type": "png", "x": 140, "y": 1180, "width": 800, "height": 740, "avatar": "head.png",
  "poses": { "up": "up.png", "palms": "palms.png", "card": "card.png", "shrug": "shrug.png", "wave": "wave.png" } }
```
Transparent PNGs, same canvas size, bottom-aligned (waist up). The kit swaps them per beat, bounces and tilts (`tilt`,
degrees). Optional overlays on the same canvas: `"talk": ["talk.png", "talk2.png"]` (open-mouth frames, flapped while
the voice speaks) and `"blink": "blink.png"` (closed eyes, every ~3 s). Without `talk` it bobs while talking instead.
Extra PNG keys: `"layers": [{"id", "src", "z", "hidden"}]` (z < 0 = behind the body; `hidden` starts invisible),
`"talk_order"` (sequence of talk-frame indexes; index len(talk) = mouth closed), `"end"` (face after the last line),
`"canvas": [w, h]` (so rig origins can be given in canvas pixels).

## Making one from a photo
Ask Claude: "make my character from this photo" — it draws Option A in the same flat style, keeping the ids above, and checks
it with `python3 reel.py make styles/paper/examples/one-prompt.json --stills`.
