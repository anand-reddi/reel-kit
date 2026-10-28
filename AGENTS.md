# Working rules for this repo (reel-kit, the @techinsixty video tool)

Read `SKILL.md` first (setup, how to make a reel), then `styles/paper/STYLE.md` and `CHARACTER.md`.
Make a reel: `python3 reel.py make script.json -o out.mp4 [--stills] [--quality draft|looks|delivery]`.
Always look at the `--stills` contact sheet before sending a video.

## Standing rules (from the channel owner)
- **Git:** push only to the `techinsixty` branch, never to `main`. Ask before every push.
- **Language:** English by default.
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
- **Voice:** Kokoro `am_puck`, speed 1.0 (natural). Say hard names via `voice.say`.
- **Dark mode:** red glow behind the presenter; bottom box is a dark box with the glow inside (`box_style: glow`).
- **Brand:** handle `@techinsixty`; red accent `#e5372d`; profile pictures in `brand/` (square, edge to edge).
- **Known gap:** lip-sync and expressions come from the footage, so they are approximate.

## Example
`styles/paper/examples/dark-explainer.json` is a self-contained dark-mode reel (no third-party media). Start from it.
