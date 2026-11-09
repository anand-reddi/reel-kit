"""kinetic: kinetic-type motion design in 9:16 (huge words on every beat, ground flips, whip pans, 3D type the camera
flies through, slot counters, comets). Our own engine (engine/runtime.js + engine/blocks.js), one page whose every
frame is a pure function of time; frames are captured at 60 fps and pairs are blended into real motion blur.
Script format and blocks: STYLE.md."""
import json, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.dirname(os.path.dirname(HERE))
W, H = 1080, 1920
PALETTE = {"bg": "#0b0b0b", "paper": "#f2f1ee", "accent": "#e5372d", "hot": "#ff8a3d", "ink": "#0b0b0b"}
BLOCKS = ["Words", "Strike", "Graph", "Hero", "Prompt", "Stretch", "Fly", "Notes", "Counters", "Progress", "Chain", "Rewind", "Picture", "Logo", "StyleList", "Route", "SkillCard", "TypeOn", "Steps", "Dupes", "Copies", "Files", "Match", "ToolGrid"]
CARDS = {b: "see STYLE.md" for b in BLOCKS}
TIME = re.compile(r"^(start|end|line:\d+(:end)?|word:[^+\-]+|-?\d+(\.\d+)?s)([+-]\d*\.?\d+)?$")
ASSET_KEYS = {"src"}
ASSET_LISTS = {"intro"}   # lists of image paths

def scene_times(script, timing):
    """[(start, end)] per scene: from the voice lines (a scene starts 0.12 s before its first line), or from
    "beats" per scene when the reel has no voice."""
    sc = script["scenes"]; dur = timing["duration"]
    if timing.get("scenes"): return [tuple(x) for x in timing["scenes"]]
    L = timing["lines"]; starts = []
    for i in range(len(sc)):
        ls = [l for l in L if l["scene"] == i]; starts.append(0.0 if i == 0 else (ls[0]["start"] - 0.12 if ls else None))
    for i in range(len(starts)):           # a scene without lines starts where the previous ends + its beats
        if starts[i] is None: starts[i] = starts[i - 1] + sc[i - 1].get("beats", 4) * 60 / script.get("bpm", 120)
    return [(starts[i], starts[i + 1] if i + 1 < len(starts) else dur) for i in range(len(starts))]

def resolver(timing, i, a, b):
    lines = [l for l in timing["lines"] if l["scene"] == i]
    def at(spec):
        m = re.match(r"^(.*?)([+-]\d*\.?\d+)?$", spec.strip()); base, off = m.group(1), float(m.group(2) or 0)
        if base == "start": t = a
        elif base == "end": t = b
        elif base.endswith("s") and re.match(r"^-?\d+(\.\d+)?s$", base): t = a + float(base[:-1])
        elif base.startswith("line:"):
            p = base.split(":"); ln = lines[min(int(p[1]), len(lines) - 1)] if lines else None
            if not ln: raise SystemExit(f"scene {i + 1}: no voice lines for '{spec}'")
            t = ln["end"] if len(p) > 2 else ln["start"]
        elif base.startswith("word:"):
            want = base[5:].lower(); t = None
            for ln in lines:
                for w in ln["words"]:
                    if re.sub(r"[^a-z0-9%'-]", "", w["w"].lower()) == re.sub(r"[^a-z0-9%'-]", "", want): t = w["t"]; break
                if t is not None: break
            if t is None: raise SystemExit(f"scene {i + 1}: no word '{want}' for timing")
        else: raise SystemExit(f"bad time '{spec}'")
        return round(t + off, 4)
    return at

def _walk(v, fn):
    if isinstance(v, dict): return {k: _walk(x, fn) for k, x in v.items()}
    if isinstance(v, list): return [_walk(x, fn) for x in v]
    return fn(v)

def build(script, timing, work, sdir):
    out = os.path.join(work, "film"); os.makedirs(os.path.join(out, "assets"), exist_ok=True)
    for f in ("archivo-var-latin.woff2", "archivo-latin-800-normal.woff2", "jetbrains-mono-latin-500-normal.woff2"):
        shutil.copy(os.path.join(KIT, "assets", "fonts", f), os.path.join(out, "assets", f))
    shutil.copy(os.path.join(KIT, "assets", "gsap.min.js"), os.path.join(out, "gsap.min.js"))
    eng = os.path.join(HERE, "engine"); runtime = open(os.path.join(eng, "runtime.js")).read(); blocks = open(os.path.join(eng, "blocks.js")).read()
    source = runtime + "\n" + blocks; dur = timing["duration"]
    nums = {"{lines}": f'{len(source.splitlines()):,}', "{frames}": f"{int(dur * 30):,}", "{seconds}": f"{dur:.0f}"}
    used = {}
    def asset(p):
        src = p if os.path.isabs(p) else os.path.join(sdir, p)
        if not os.path.exists(src): raise SystemExit(f"missing file {p}")
        name = used.setdefault(src, f"a{len(used)}_{os.path.basename(src)}"); shutil.copy(src, os.path.join(out, "assets", name)); return "assets/" + name
    def mark(v):          # a logo mark: an inline SVG file, an icon from the library ("set:name"), or an image
        if not isinstance(v, str): return v
        if v.endswith(".svg"): return open(v if os.path.isabs(v) else os.path.join(sdir, v)).read()
        if ":" in v and not os.path.exists(os.path.join(sdir, v)):
            sys.path.insert(0, KIT); from core import icons; return icons.svg(v, 280)
        return f'<img src="{asset(v)}"/>'
    scenes = []; spans = scene_times(script, timing)
    for i, sc in enumerate(script["scenes"]):
        a, b = spans[i]; at = resolver(timing, i, a, b); blk = dict(sc.get("block") or {}); typ = blk.pop("type", "Words")
        if typ not in BLOCKS: raise SystemExit(f"scene {i + 1}: unknown block {typ}; have {BLOCKS}")
        times = {}
        def fix(v):
            if isinstance(v, str):
                for k, x in nums.items(): v = v.replace(k, x)
                if TIME.match(v.strip()): times[v] = at(v)
            return v
        blk = _walk(blk, fix)
        def assets_in(d):
            if isinstance(d, dict):
                return {k: (asset(x) if k in ASSET_KEYS and isinstance(x, str) and not x.startswith("http") else
                            [asset(y) for y in x] if k in ASSET_LISTS and isinstance(x, list) else mark(x) if k in ("mark", "mark2") else [mark(y) for y in x] if k == "marks" and isinstance(x, list) else assets_in(x)) for k, x in d.items()}
            if isinstance(d, list): return [assets_in(x) for x in d]
            return d
        blk = assets_in(blk)
        scenes.append({"start": round(a, 4), "end": round(b, 4), "type": typ, "block": blk, "times": times})
    pal = {**PALETTE, **script.get("palette", {})}
    subs = [] if script.get("captions", "sub") == "off" else [{"text": l["text"].replace("*", "").replace("_", ""), "start": l["start"], "end": l["end"]} for l in timing["lines"]]
    data = {"palette": pal, "bpm": script.get("bpm", script.get("music", {}).get("bpm", 120)), "duration": dur, "scenes": scenes,
            "hud": script.get("hud"), "hudOut": script.get("hud_out"), "subs": subs, "source": source}
    css = open(os.path.join(eng, "kinetic.css")).read()
    for k, v in pal.items(): css = css.replace("{" + k + "}", v)
    boot = """
Promise.all(['900 100px AV', '400 100px AS', '400 40px MO'].map(f => document.fonts.load(f))).then(() => document.fonts.ready).then(() => {
  const D = window.__DATA, cam = document.getElementById('cam');
  D.scenes.forEach((s, i) => {
    const box = K.el('div', 'blk', cam); K.vis(box, s.start, i + 1 < D.scenes.length ? D.scenes[i + 1].start : null);
    const T = v => typeof v === 'number' ? s.start + v * K.B : (v in s.times ? s.times[v] : s.start);
    const bd = s.block.backdrop;   // backdrop: {src, blur, dim} an image behind any block (instead of a flat ground)
    if (bd) { const d = K.el('div', 'kbackdrop', box); d.style.backgroundImage = `url(${bd.src})`;
      d.style.filter = `blur(${bd.blur ?? 14}px) brightness(${1 - (bd.dim ?? .55)})`;
      K.tl.fromTo(d, { scale: 1.08 }, { scale: 1.16, duration: s.end - s.start, ease: 'none', immediateRender: false }, s.start); }
    K.blocks[s.type](box, s.block, T, { start: s.start, end: s.end, i });
  });
  K.tl.set({}, {}, D.duration);
  window.__timelines = { reel: K.tl }; window.__cues = K.cues; window.__ready = true;
});"""
    html = (f'<!doctype html><html><head><meta charset="utf-8"><title>{script.get("title", "kinetic")}</title><style>{css}</style>'
            f'<script src="gsap.min.js"></script></head><body><div id="root"><div id="ground"></div><div id="cam"><div id="fx"></div></div><div id="invert"></div></div>'
            f'<script>window.__DATA = {json.dumps(data)};</script><script>{runtime}</script><script>{blocks}</script><script>{boot}</script></body></html>')
    open(os.path.join(out, "index.html"), "w").write(html)
    # run the page once: it reports its own sound cues and any script error
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch(); pg = br.new_page(viewport={"width": W, "height": H}); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("file://" + os.path.join(out, "index.html"))
        try: pg.wait_for_function("window.__ready === true", timeout=60000)
        except Exception: sys.exit("kinetic page did not start: " + "; ".join(errs[:3]))
        if errs: sys.exit("kinetic page error: " + "; ".join(errs[:3]))
        cues = [tuple(c) for c in pg.evaluate("window.__cues.map(c => c.slice())")]
        br.close()
    return cues

SEEK = r"""async (t) => {
  window.__timelines.reel.seek(Math.max(t, 0.0005), false);   // past 0, so sets placed at 0 have rendered
  const ps = [];
  for (const v of document.querySelectorAll('video[data-start]')) { const s = +v.dataset.start, d = +v.dataset.duration, m = +(v.dataset.mediaStart || 0);
    const on = t >= s && t < s + d; v.style.visibility = on ? 'visible' : 'hidden';
    if (on) { ps.push(new Promise(r => { v.addEventListener('seeked', r, { once: true }); setTimeout(r, 3000); })); v.currentTime = m + (t - s); } }
  await Promise.all(ps);
  const out = [];   // rewind windows on screen: where to paste the film so far, played backwards
  for (const e of document.querySelectorAll('[data-rewind]')) { const blk = e.closest('.shot'); if (getComputedStyle(blk).visibility !== 'visible') continue;
    const r = JSON.parse(e.dataset.rewind); if (t < r.a || t >= r.b) continue; const q = e.getBoundingClientRect(); const win = e.parentElement;
    const m = new DOMMatrix(getComputedStyle(win).transform); const sc = Math.hypot(m.a, m.b), ang = Math.atan2(m.b, m.a) * 180 / Math.PI;
    out.push({ cx: q.left + q.width / 2, cy: q.top + q.height / 2, w: e.offsetWidth * sc, h: e.offsetHeight * sc, ang, src: r.from * (1 - (t - r.a) / (r.b - r.a)) }); }
  return out; }"""

def render(script, timing, work, sdir, quality="looks"):
    """Captures every frame (60 fps, blended in pairs into motion blur at 30 fps; draft = 30 fps, no blur), pastes
    the Rewind windows from frames already rendered, and writes work/video.mp4 (no audio)."""
    from playwright.sync_api import sync_playwright
    from PIL import Image
    fps = 30 if quality == "draft" else 60; fdir = os.path.join(work, "kin-frames"); shutil.rmtree(fdir, ignore_errors=True); os.makedirs(fdir)
    n = int(round(timing["duration"] * fps)); rew = 0
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--run-all-compositor-stages-before-draw"]); pg = br.new_page(viewport={"width": W, "height": H})
        pg.goto("file://" + os.path.join(work, "film", "index.html")); pg.wait_for_function("window.__ready === true", timeout=60000)
        for k in range(n):
            wins = pg.evaluate(SEEK, k / fps); f = os.path.join(fdir, f"{k:05d}.jpg")
            pg.screenshot(path=f, type="jpeg", quality=93)
            for w in wins:          # the film so far, played backwards inside the window
                src = os.path.join(fdir, f"{max(0, min(k - 1, int(w['src'] * fps))):05d}.jpg")
                if not os.path.exists(src): continue
                im = Image.open(f).convert("RGB"); s = Image.open(src).convert("RGB").resize((max(2, int(w["w"])), max(2, int(w["h"]))))
                s = s.rotate(-w["ang"], expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0)); mk = Image.new("L", s.size, 0)
                mk.paste(255, (0, 0, s.size[0], s.size[1])); mask = Image.new("L", (max(2, int(w["w"])), max(2, int(w["h"]))), 255).rotate(-w["ang"], expand=True)
                im.paste(s, (int(w["cx"] - s.size[0] / 2), int(w["cy"] - s.size[1] / 2)), mask); im.save(f, quality=93); rew += 1
        br.close()
    vf = "tmix=frames=2:weights='1 1',fps=30,format=yuv420p" if fps == 60 else "format=yuv420p"
    crf = {"draft": "23", "looks": "17", "delivery": "14"}.get(quality, "17")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", os.path.join(fdir, "%05d.jpg"), "-vf", vf, "-c:v", "libx264", "-crf", crf,
                        "-preset", "veryfast" if quality == "draft" else "medium", os.path.join(work, "video.mp4")], capture_output=True, text=True)
    if r.returncode: sys.exit("ffmpeg failed: " + r.stderr[-800:])
    shutil.rmtree(fdir, ignore_errors=True)
    print(f"    {n} frames at {fps} fps{' (motion blur)' if fps == 60 else ''}{f', {rew} rewind frames composited' if rew else ''}")
    return []
