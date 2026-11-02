"""sketchbook: hand-drawn paper UI from Looseleaf (MIT, kevintngo/looseleaf) rendered as a 9:16 reel.

Two looks share this code:
  sketchbook       the original Looseleaf look: sage desk, light paper, yellow highlighter, Stubby the pencil
  sketchbook_dark  the krishexplainz look: near-black dotted page, dark paper, one red accent, a black cat sticker
The page is a small React app (styles/sketchbook/app) built with Vite inside the pinned Looseleaf checkout
(setup.sh installs it at ~/.cache/reelkit/looseleaf), seeked frame by frame in Chromium and encoded with ffmpeg.
"""
import json, os, re, shutil, subprocess, sys, threading, functools, http.server, socketserver

HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.dirname(os.path.dirname(HERE))
LL = os.environ.get("REELKIT_LOOSELEAF", os.path.expanduser("~/.cache/reelkit/looseleaf"))
W, H, FPS = 540, 960, 30          # CSS stage; captured at 2x = 1080x1920

THEMES = {
    "original": dict(buddy="stubby", accent="#df6b3c", hi="#f2dc5d", hi_text="#2a2420"),
    "dark":     dict(buddy="cat",    accent="#e5372d", hi="#e5372d", hi_text="#ffffff"),
}
CARDS = {
    "hook":      "big claim on paper: rows [{text, kind: dim|big|mark, at}], stock graph|paper|kraft, doodle {name, at, x, y, size}",
    "split":     "toggle + slider: title, tabs [a, b], labels [left, right], keys [{at, tab, value 0-100}] (slider eases between keys)",
    "stat":      "index card number: label, value '+44%', sub, at, circle true, stamp {text, at, x, y}, doodle",
    "shot":      "a real screenshot taped on paper: src, chips [{text, at, mark}], doodle",
    "checklist": "ticks per line: title, items [{text, at}]",
    "versus":    "two cards side by side: good {title, text, at}, bad {title, text, at}",
    "note":      "a sticky note: text, sub, color yellow|green|orange|pink|blue, at",
    "follow":    "ending: Polaroid of brand.avatar, handle, Follow -> Following (platform 'youtube' = Subscribe), tap_at; hides the buddy",
}
# reactions of the buddy -> Stubby pose / cat face
REACT = {"idle": ("idle", "idle"), "wow": ("oops", "shocked"), "happy": ("celebrate", "happy"), "smug": ("point", "smug"),
         "love": ("wave", "love"), "think": ("think", "idle"), "point": ("point", "smug"), "shrug": ("shrug", "idle")}

def _norm(w): return re.sub(r"[^a-z0-9%]", "", w.lower())

def resolver(timing):
    lines = timing["lines"]; dur = timing["duration"]
    by = {}
    for ln in lines: by.setdefault(ln["scene"], []).append(ln)
    n = max(by) + 1 if by else 1
    starts = [0.0] + [round(by[i][0]["start"] - 0.3, 3) if i in by else 0 for i in range(1, n)]
    ends = starts[1:] + [dur]
    def at(sc, spec, default="start"):
        spec = default if spec is None else spec
        if isinstance(spec, (int, float)): return round(starts[sc] + spec, 3)
        m = re.match(r"^(.*?)([+-]\d+(?:\.\d+)?)?$", str(spec).strip()); base, off = m.group(1), float(m.group(2) or 0)
        L = by.get(sc, [])
        if base == "start": t = starts[sc]
        elif base == "end": t = ends[sc]
        elif base.startswith("line:"):
            p = base.split(":"); ln = L[int(p[1])]; t = ln["end"] if len(p) > 2 and p[2] == "end" else ln["start"]
        elif base.startswith("word:"):
            want = _norm(base[5:]); t = None
            for ln in L:
                for w in ln["words"]:
                    if _norm(w["w"]).startswith(want): t = w["t"]; break
                if t is not None: break
            if t is None: sys.exit(f"scene {sc}: no word '{base[5:]}' in its lines")
        else: sys.exit(f"scene {sc}: bad time '{spec}'")
        return round(float(t) + off, 3)
    return at, starts, ends

def _asset(src, sdir, dist, used):
    p = src if os.path.isabs(src) else os.path.join(sdir, src)
    if not os.path.exists(p): sys.exit(f"missing file: {p}")
    name = f"a{len(used)}{os.path.splitext(p)[1].lower()}"; shutil.copy(p, os.path.join(dist, name)); used.append(name); return "./" + name

def build(script, timing, work, sdir, look="original"):
    """Writes work/sketch/config.json (+ assets) and returns the sound cues; the page is bundled in render()."""
    th = dict(THEMES[look]); th.update({k: v for k, v in (script.get("theme_colors") or {}).items()})
    at, starts, ends = resolver(timing)
    dist = os.path.join(work, "sketch"); os.makedirs(dist, exist_ok=True); used = []
    cues = [(0.1, "pro_pop_in/round", -12)]
    scenes, show = [], []
    buddy = dict(x=318, y=520, size=185); buddy.update(script.get("buddy", {}))
    events = []
    for i, sc in enumerate(script["scenes"]):
        c = dict(sc.get("card") or {"type": "note", "text": ""}); typ = c.get("type", "note")
        if typ not in CARDS: sys.exit(f"scene {i}: unknown card '{typ}' (have: {', '.join(CARDS)})")
        A = lambda spec, d="start": at(i, spec, d)
        if typ == "hook":
            for r in c.get("rows", []):
                if "at" in r: r["at"] = A(r["at"]); cues.append((r["at"], "pro_pop/tink", -10))
        elif typ == "split":
            for k in c.get("keys", []):
                k["at"] = A(k.get("at")); cues.append((k["at"], "pro_click/soft", -10))
        elif typ == "stat":
            c["at"] = A(c.get("at")); cues.append((c["at"], "pro_pop_in/round", -9))
            if c.get("stamp"): c["stamp"]["at"] = A(c["stamp"].get("at", "end-0.6")); cues.append((c["stamp"]["at"], "pro_impact/short", -8))
        elif typ == "shot":
            c["src"] = _asset(c["src"], sdir, dist, used)
            for ch in c.get("chips", []): ch["at"] = A(ch.get("at")); cues.append((ch["at"], "pro_pop_in/double", -10))
        elif typ == "checklist":
            L = [ln for ln in timing["lines"] if ln["scene"] == i]
            for j, it in enumerate(c.get("items", [])):
                it["at"] = A(it.get("at", f"line:{min(j, len(L) - 1)}")); cues.append((it["at"], "pro_pop/tink", -10))
        elif typ == "versus":
            for k in ("good", "bad"):
                if c.get(k): c[k]["at"] = A(c[k].get("at")); cues.append((c[k]["at"], "pro_pop/thup", -11))
        elif typ == "note":
            c["at"] = A(c.get("at")); cues.append((c["at"], "pro_pop/thup", -11))
        elif typ == "follow":
            c["tap_at"] = A(c.get("tap_at", "line:0+0.3")); cues.append((c["tap_at"], "pro_tap/knock", -9))
            b = script.get("brand", {}); c["handle"] = b.get("handle", "@you")
            if b.get("avatar"): c["avatar"] = _asset(b["avatar"], sdir, dist, used)
        if c.get("doodle"): c["doodle"]["at"] = A(c["doodle"].get("at")); cues.append((c["doodle"]["at"], "pro_pop/tink", -12))
        vis = sc.get("buddy", True) is not False and typ != "follow"; show.append(vis)
        if vis:
            for e in (sc.get("react") or []):
                f = REACT.get(e.get("react", "idle"), REACT["idle"])
                events.append(dict(t=A(e.get("at")), pose=e.get("pose", f[0]), face=e.get("face", f[1]), look=e.get("look", 0), jump=bool(e.get("jump"))))
                if e.get("jump"): cues.append((events[-1]["t"], "pro_pop/boop", -11))
        if i > 0: cues.append((starts[i] - 0.2, "swish/soft", -12))
        scenes.append(dict(start=starts[i], end=ends[i], card=c, capY=sc.get("caption_y", 745), top=c.get("top")))
    events.sort(key=lambda e: e["t"])
    lines = [dict(start=ln["start"], end=ln["end"], words=[dict(w=w["w"], t=w["t"], hi=bool(w.get("accent"))) for w in ln["words"]]) for ln in timing["lines"]]
    cfg = dict(look=look, theme=th, dur=timing["duration"], scenes=scenes, lines=lines, show=show, buddy=buddy, events=events)
    json.dump(cfg, open(os.path.join(dist, "config.json"), "w"))
    return cues

def _bundle(dist):
    if not os.path.isdir(os.path.join(LL, "node_modules")): sys.exit(f"Looseleaf is not installed at {LL}: run setup.sh")
    app = os.path.join(LL, "src", "reelkit"); shutil.rmtree(app, ignore_errors=True); shutil.copytree(os.path.join(HERE, "app"), app)
    shutil.copy(os.path.join(HERE, "app", "index.html"), os.path.join(LL, "reelkit.html"))
    out = os.path.join(dist, "_page"); pub = os.path.join(LL, "reelkit-public")
    if not os.path.isdir(os.path.join(pub, "fonts")): shutil.copytree(os.path.join(LL, "public", "fonts"), os.path.join(pub, "fonts"), dirs_exist_ok=True)
    cfg = os.path.join(LL, "vite.reelkit.config.ts")
    open(cfg, "w").write(f'''import path from "node:path"
import {{ defineConfig }} from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"
export default defineConfig({{ base: "./", publicDir: "reelkit-public", plugins: [react(), tailwindcss()],
  resolve: {{ alias: {{ "@": path.resolve(import.meta.dirname, "src") }} }},
  build: {{ outDir: {json.dumps(out)}, emptyOutDir: true, chunkSizeWarningLimit: 99999, rollupOptions: {{ input: path.resolve(import.meta.dirname, "reelkit.html") }} }} }})
''')
    r = subprocess.run(["npx", "vite", "build", "-c", cfg, "--logLevel", "error"], cwd=LL, capture_output=True, text=True)
    if r.returncode: sys.exit("vite build failed:\n" + (r.stdout + r.stderr)[-2000:])
    shutil.copytree(out, dist, dirs_exist_ok=True); shutil.rmtree(out, ignore_errors=True)
    shutil.copy(os.path.join(KIT, "assets", "gsap.min.js"), dist)

class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

def _serve(d):
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(_Quiet, directory=d)); srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start(); return srv

QA_JS = r"""() => {
  const vis = (el) => { for (let e = el; e && e.id !== "stage"; e = e.parentElement) { const s = getComputedStyle(e); if (s.display === "none" || parseFloat(s.opacity) < 0.3) return false } return true };
  const R = (el) => el.getBoundingClientRect();
  const caps = [...document.querySelectorAll(".cap .w")].filter(w => vis(w) && R(w).width > 0).map(R);
  const blocks = [...document.querySelectorAll("[data-qa]")].filter(vis).map(e => ({ n: e.dataset.qa, r: R(e) }))
    .filter(b => b.r.right > 0 && b.r.left < 540 && b.r.width > 0);   // scenes parked off stage between cuts are not on screen
  const hit = (a, b) => Math.min(a.right, b.right) - Math.max(a.left, b.left) > 4 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 4;
  const out = [];
  for (const c of caps) { for (const b of blocks) if (hit(c, b.r)) out.push("caption overlaps " + b.n);
    if (c.left < 8 || c.right > 532 || c.bottom > 952) out.push("caption runs off the frame") }
  for (const b of blocks) if (b.r.left < -4 || b.r.right > 544 || b.r.bottom > 964) out.push(b.n + " runs off the frame");
  return [...new Set(out)] }"""

def render(script, timing, work, sdir, quality="looks"):
    """Bundles the page, captures every frame at 1080x1920, runs a caption QA, writes work/video.mp4 (no audio)."""
    from playwright.sync_api import sync_playwright
    dist = os.path.join(work, "sketch"); _bundle(dist)
    fdir = os.path.join(work, "sketch-frames"); shutil.rmtree(fdir, ignore_errors=True); os.makedirs(fdir)
    dur = timing["duration"]; n = int(round(dur * FPS)); srv = _serve(dist); probs = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
            errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(f"http://127.0.0.1:{srv.server_address[1]}/reelkit.html")
            try: pg.wait_for_function("window.__ready === true", timeout=30000)
            except Exception: sys.exit("sketchbook page did not start: " + "; ".join(errs[:3]))
            pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(400)
            checks = sorted({round(ln["end"] - 0.06, 2) for ln in timing["lines"]} | {round((ln["start"] + ln["end"]) / 2, 2) for ln in timing["lines"]})
            for t in checks:
                pg.evaluate(f"window.__seek({t})"); pg.evaluate("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
                probs += [f"@ {t:.2f}s: {x}" for x in pg.evaluate(QA_JS)]
            stage = pg.locator("#stage")
            for k in range(n):
                pg.evaluate(f"window.__seek({k / FPS:.4f})"); pg.evaluate("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
                stage.screenshot(path=os.path.join(fdir, f"{k:05d}.png"))
            b.close()
    finally: srv.shutdown()
    print(f"    layout: {len(checks)} moments checked, {len(probs)} problem(s)")
    for x in probs: print("  !", x)
    crf = {"draft": "23", "looks": "17", "delivery": "14"}.get(quality, "17")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(fdir, "%05d.png"), "-c:v", "libx264", "-crf", crf,
                        "-preset", "veryfast" if quality == "draft" else "medium", "-pix_fmt", "yuv420p", os.path.join(work, "video.mp4")], capture_output=True, text=True)
    if r.returncode: sys.exit("ffmpeg failed: " + r.stderr[-800:])
    shutil.rmtree(fdir, ignore_errors=True)
    return probs
