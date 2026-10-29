---
name: reel-kit
description: Make short videos and reels from a script in the user's saved styles (paper explainer, 3D studio explainer): voice, synced captions, animation, music, SFX.
---

# reel-kit

One repo for every video style the user builds from reference videos. All styles share the same core: Kokoro voice
(`am_michael` by default) with word timings, a code-made music bed, earshot sound effects placed on their peaks, a
swappable presenter character, HyperFrames rendering and a -14 LUFS mix. Each style lives in `styles/<name>/` with
its own `STYLE.md`; a reel is one JSON script with `"style": "<name>"`.

## 0. Setup (once per session)
```bash
[ -f ~/reel-kit/reel.py ] || git clone -q --depth 1 -b techinsixty https://github.com/anand-reddi/reel-kit ~/reel-kit
git -C ~/reel-kit pull -q || true   # pick up styles added since the last clone
bash ~/reel-kit/setup.sh          # deps, Kokoro voice model (cached), earshot SFX; idempotent
cd ~/reel-kit && python3 reel.py styles
```

## 1. Making a video
1. Pick the style (ask if the user didn't say and more than one fits) and read `styles/<style>/STYLE.md` in full.
2. Settle the story: hook in the first 2 s, 3–6 beats, a closing line. Fact-check every claim, number and name with a
   search first; never invent figures. About 2.6 spoken words per second (10 s ≈ 22 words, 60 s ≈ 140).
3. Write the script JSON (format in the style's STYLE.md), then:
   ```bash
   python3 reel.py make my-reel.json -o out/my-reel.mp4 --stills    # --quality draft while iterating
   ```
4. Icons: always from the icon library (`python3 reel.py icons <word>`), never emoji. Presenter only where a clip matches
   the line (clip table in the style's STYLE.md), else visuals only.
5. Read the pronunciation report (`pronounce.txt` in the work folder; guessed words are also printed) and fix wrong
   words in `core/lexicon.json` or `voice.say` (`python3 reel.py say "text"` to check).
6. Look at `out/my-reel-frames.png` before sending. Send the MP4 with a one-line summary.

Styles: `paper` — off-white dotted paper, black/white UI cards with a red accent, live hairline line figures,
word-synced captions, presenter
(see `styles/paper/STYLE.md`).
`studio3d` — one continuous camera through a matte 3D studio (three.js), state bar, callout labels, titles, caption
pill; each video brings its own scene module (see `styles/studio3d/STYLE.md`). `python3 reel.py styles` lists what the repo has now.

## 2. Adding a new style from a reference video
When the user shares a reference video and wants "videos like this":
1. Analyse it: duration, aspect, fps (`ffprobe`); a tiled contact sheet (`ffmpeg -vf "fps=0.5,scale=180:-1,tile=11x3"`)
   and a 10 fps strip of the first 12 s; 2–3 full-res frames; `earshot measure` for loudness and band balance.
   Write down: palette (hex), type (families, sizes, accent treatment), layout zones, caption mechanics, the
   recurring visual devices, cut rhythm, presenter, sound (voice / music / SFX roles).
2. Tell the user the breakdown and the plan for a 10 s test before building.
3. Build `styles/<name>/` with the same interface as `styles/paper/`: `__init__.py` exposing
   `build(script, timing, work, script_dir) -> cues`, `CARDS` (its building blocks) and `SIZE`; its own CSS/assets;
   `STYLE.md` (look, script format, blocks, timing grammar); `examples/` with the 10 s test script. Reuse
   `core/voice.py`, `core/sound.py` and `core/clock.js` as they are; put new shared helpers in `core/`, never copy them into a style.
   Fonts go in `assets/fonts/` (vendored from npm `@fontsource/*`, jsDelivr is blocked in the browser).
4. Draw only original characters and artwork; never copy the reference creator's avatar, logo or branding.
5. Render the example, check the frames, send it. After the user approves, add the style to the list in section 1,
   commit on branch `techinsixty` and ask before pushing (never push to `main`).

## 3. Characters
`characters/<name>/` + `character.json`; a script picks one with `"character"`. Format and required ids:
`CHARACTER.md`. `default` is the @techinsixty presenter (black face, fedora, blue LED expression faces, overshirt, 60 chain).

## Notes
- Fonts and GSAP are vendored: renders need no network. Rendering needs Node (npx hyperframes), ffmpeg and a headless
  Chrome (auto-detected from Playwright's folders, or `HYPERFRAMES_BROWSER_PATH`).
- Write "AI", "SBI", "API" plainly (no spaces); use the script's `voice.say` map only for words Kokoro gets wrong.
- The voice must fit the duration: the kit stops and says so if it overruns (cut words or raise `voice.speed`, max ~1.25).
- Build files go to `build/<name>/` next to the script; `film/index.html` is a normal HyperFrames composition.
