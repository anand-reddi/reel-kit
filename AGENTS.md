# Working rules for this repo (reel-kit, the @techinsixty video tool)

Read `SKILL.md` first (setup, how to make a reel), then `styles/paper/STYLE.md` and `CHARACTER.md`.
Make a reel: `python3 reel.py make script.json -o out.mp4 [--stills] [--quality draft|looks|delivery]`.
Always look at the `--stills` contact sheet before sending a video.

## Standing rules (from the channel owner)
- **Git:** push only to the `techinsixty` branch, never to `main`. Ask before every push.
- **Language:** English by default.
- **Write for shares, not likes or comments:** the reel's job is to make the viewer feel smart, so they forward it
  to a friend ("bro, how did you not know this?"). Every script needs one surprising, useful takeaway someone would
  send on. Prefer a "send this to someone who…" or "save this" ending over "comment below". Judge a script by:
  would someone share this?
- **Facts:** fact-check every claim, number and name with a search before writing the script. Never invent figures.
  If a site or its media is blocked from the workspace, say so and ask the owner to send the clips.
- **Characters:** original characters only (the `otaku` presenter is the channel face). Third-party art/clips are used
  only when the owner supplies them, with a `credits` line in the script.
- **Style:** paper style only (dark theme by default for new videos). Do not mix in other video styles or skills
  unless asked.
- **Captions:** blur-build words, accent words in the red selection box. **No sound effect on the red words.**
  Text must never be cut by the frame: long lines split automatically; still check every caption in the stills.
- **Presenter:** use the character only where the gesture/expression matches the line (see the clip table in
  `styles/paper/STYLE.md`); if no clip fits, show visuals only (`"layout": "none"`). Time each gesture onto its word.
  Fix every "WARN ... no chosen gesture" from `reel.py make`. Keep him smaller in full and bottom shots.
- **Icons:** always from the icon library (`python3 reel.py icons <word>`: logos, simple-icons, devicon, lucide, tabler,
  fluent-emoji-flat). Never emoji or text glyphs as icons. Company and tool logos use their real logo.
- **Intro slides:** the opening kinetic pages match the rest of the video: theme background, caption font, red
  selection box for the accent word (`"accent": true`). No full red slabs.
- **Voice:** Kokoro `am_puck`, speed 1.0 (natural). Words go through `core/pronounce.py` (misaki dictionaries, the
  phonemes Kokoro was trained on; tech words in `core/lexicon.json`). Every render writes `pronounce.txt` and warns
  about guessed words: read it, and fix any wrong one in `core/lexicon.json` (permanent) or `voice.say` (this video).
  Check text any time with `python3 reel.py say "..."`. Prices, 10x, 8.1k, %, domains (cindy.app) are read out properly.
- **Dark mode:** red glow behind the presenter; bottom box is a dark box with the glow inside (`box_style: glow`).
- **Brand:** handle `@techinsixty`; red accent `#e5372d`; profile pictures in `brand/` (square, edge to edge).
- **Known gap:** lip-sync and expressions come from the footage, so they are approximate.

## Example
`styles/paper/examples/dark-explainer.json` is a self-contained dark-mode reel (no third-party media). Start from it.
