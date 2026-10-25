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

## Option B: PNG poses (fastest from an existing avatar app or drawing)

```json
{ "type": "png", "x": 140, "y": 1180, "width": 800, "height": 740, "avatar": "head.png",
  "poses": { "up": "up.png", "palms": "palms.png", "card": "card.png", "shrug": "shrug.png", "wave": "wave.png" } }
```
Transparent PNGs, same canvas size, bottom-aligned (waist up). The kit swaps them per beat, bounces, and bobs while talking;
there is no mouth movement (use Option A for that).

## Making one from a photo
Ask Claude: "make my character from this photo" — it draws Option A in the same flat style, keeping the ids above, and checks
it with `python3 reel.py make examples/one-prompt.json --stills`.
