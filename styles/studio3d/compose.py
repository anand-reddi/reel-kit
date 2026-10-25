import json, os, re, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.dirname(os.path.dirname(HERE))
CARDS = {"scene": "a JS module (export default function (S) {...}) that builds the topic's objects, tweens, camera path and labels"}

def _at(spec, timing):
    """Python twin of studio.js at(): used only to time sound cues."""
    if isinstance(spec, (int, float)): return float(spec)
    m = re.match(r"^(.*?)([+-]\d*\.?\d+)?$", str(spec).strip()); base, off = m.group(1), float(m.group(2) or 0); L = timing["lines"]
    if base == "start": t = 0.0
    elif base == "end": t = timing["duration"]
    elif base.startswith("line:"):
        p = base.split(":"); l = L[min(int(p[1]), len(L) - 1)]; t = l["end"] if len(p) > 2 and p[2] == "end" else l["start"]
    elif base.startswith("word:"):
        w = base[5:].lower(); t = next((x["t"] for l in L for x in l["words"] if x["w"].lower().strip(",.!?:;\"'") == w), None)
        if t is None: raise SystemExit(f"no word '{w}' for timing")
    else: raise SystemExit(f"bad time {spec}")
    return t + off

def build(script, timing, work, sdir):
    out = os.path.join(work, "film"); a = os.path.join(out, "assets"); os.makedirs(a, exist_ok=True)
    for f in ["three.module.min.js", "RoundedBoxGeometry.js"]: shutil.copy(os.path.join(KIT, "assets", "vendor", f), a)
    for f in ["inter-500.woff2", "inter-600.woff2", "inter-700.woff2", "plex-500.woff2"]: shutil.copy(os.path.join(KIT, "assets", "fonts", f), a)
    shutil.copy(os.path.join(HERE, "studio.js"), a); shutil.copy(os.path.join(KIT, "assets", "gsap.min.js"), out)
    src = script["scene"]; src = src if os.path.isabs(src) else os.path.join(sdir, src)
    shutil.copy(src, os.path.join(a, "scene.js"))
    dur = timing["duration"]
    cfg = dict(id="reel", width=1080, height=1920, timing=timing, states=script.get("states", []), tag=script.get("tag", ""),
               titles=script.get("titles", []), fov=script.get("fov", 30), drift=script.get("drift", 0.03))
    css = open(os.path.join(HERE, "style.css")).read()
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><title>{script.get("title", "reel")}</title><style>{css}</style>
<script type="importmap">{{ "imports": {{ "three": "./assets/three.module.min.js" }} }}</script>
<script src="gsap.min.js"></script></head>
<body>
<div id="root" data-composition-id="reel" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920" data-fps="{script.get("fps", 30)}">
 <div id="stage3d" class="clip" data-start="0" data-duration="{dur}" data-track-index="1"><canvas id="gl" width="1080" height="1920"></canvas><svg id="leaders"></svg><div id="ov"></div></div>
</div>
<script type="module">
import {{ boot }} from "./assets/studio.js";
import scene from "./assets/scene.js";
window.__timelines = window.__timelines || {{}};
window.__timelines["reel"] = boot({json.dumps(cfg)}, scene);
</script></body></html>'''
    open(os.path.join(out, "index.html"), "w").write(html)
    cues = [(0.05, "swipe/glide", -20)]
    for i, s in enumerate(cfg["states"]):
        if i: cues.append((_at(s["at"], timing), "pro_hover_tick/soft", -14))
    for ti in cfg["titles"]: cues.append((_at(ti["at"], timing), "pro_whoosh_big/long", -18))
    for fx in script.get("sfx", []): cues.append((_at(fx["at"], timing), fx["id"], fx.get("gain", -12)))
    return cues
