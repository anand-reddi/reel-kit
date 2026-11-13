#!/usr/bin/env python3
"""beatreel: talking-avatar explainer reels in the "one idea per beat" paper style.

  python3 beatreel.py make  script.json      voice -> captions -> page -> render -> mix -> <name>.mp4
  python3 beatreel.py board script.json      voice + a frames sheet only (check before rendering)

Voice, pronunciation audit and the sound mix come from reel-kit's core (Kokoro, misaki G2P, earshot sfx);
everything you see is this engine (engine/beats.js + engine/style.css). See SKILL.md for the script format."""
import json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.environ.get("REELKIT", os.path.dirname(HERE))
sys.path.insert(0, KIT)
from core import voice, sound   # noqa: E402

HF_BROWSER = os.environ.get("HYPERFRAMES_BROWSER_PATH", "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell")
r3 = lambda x: round(float(x), 3)
POP = {"stamp": ("pro_impact/air", -13), "num": ("pro_pop_in/deep", -15), "term": ("pro_typing_run/blip", -20)}


def norm(w): return re.sub(r"[^a-z0-9$%'-]", "", w.lower().replace("’", "'"))


def load(path):
    sc = json.load(open(path)); sc["_dir"] = os.path.dirname(os.path.abspath(path))
    sc["_name"] = sc.get("name") or os.path.splitext(os.path.basename(path))[0]
    # the voice module reads "scenes" with "lines": a beat is a scene
    sc["scenes"] = [{"lines": b["lines"], **({"pause_before": b["pause_before"]} if "pause_before" in b else {})} for b in sc["beats"]]
    sc.setdefault("voice", {}).setdefault("name", "am_puck")
    return sc


def speak(sc, work):
    os.makedirs(work, exist_ok=True)
    tj = os.path.join(work, "timing.json")
    key = json.dumps([sc["scenes"], sc["voice"], sc.get("intro")], sort_keys=True)
    kf = os.path.join(work, "voice.key")
    if os.path.exists(tj) and os.path.exists(kf) and open(kf).read() == key:
        return json.load(open(tj))
    tm = voice.speak(sc, work); open(kf, "w").write(key); return tm


def beat_bounds(sc, tm):
    n = len(sc["beats"]); starts = [None] * n
    for l in tm["lines"]:
        if starts[l["scene"]] is None: starts[l["scene"]] = l["start"]
    b = []
    for i in range(n):
        t0 = 0.0 if i == 0 else starts[i] - 0.12
        t1 = (starts[i + 1] - 0.12) if i + 1 < n else tm["duration"]
        b.append([r3(t0), r3(t1)])
    return b


def word_time(tm, i, word, nth=0):
    hits = [w["t"] for l in tm["lines"] if l["scene"] == i for w in l["words"] if norm(w["w"]) == norm(word)]
    if len(hits) <= nth: raise SystemExit(f'beat {i}: word "{word}" (#{nth}) not in its lines')
    return hits[nth]


def at_time(v, tm, i, t0):
    """an item's moment: None (beat start), seconds from the beat start, or "word:xyz" / "word:xyz#2" (+-0.1)."""
    if v is None: return t0 + 0.05
    if isinstance(v, (int, float)): return t0 + v
    m = re.match(r"word:([^#+-]+)(?:#(\d+))?([+-][\d.]+)?$", v)
    if not m: raise SystemExit(f"bad time {v!r}")
    return word_time(tm, i, m.group(1), int(m.group(2) or 1) - 1) - 0.06 + float(m.group(3) or 0)


def icon(name, size=120, color="#111"):
    from core import icons
    return icons.svg(name, size, color)


TIME_LISTS = ("ticks", "hiAt", "ringAt", "ats")
TIME_ONE = ("rightAt", "dropAt", "tapAt", "claudeAt", "outsiderAt", "leaveAt", "endAt", "strikeAt", "checkAt", "answerAt",
            "linkAt", "sortAt", "markAt", "sendAt", "flipAt")


def blocks(tm, max_words=7):
    """caption phrase blocks: a script line split into runs of <= max_words, breaking after punctuation when it can."""
    out = []
    for l in tm["lines"]:
        ws = [{"w": w["w"], "t": w["t"], "it": bool(w.get("italic"))} for w in l["words"]]; cur = []
        for k, w in enumerate(ws):
            cur.append(w); left = len(ws) - k - 1
            punct = w["w"].rstrip("\"'").endswith((",", ".", "?", "!", ":", ";", "—"))
            if left and (len(cur) >= max_words or (punct and len(cur) >= 3 and left >= 2)):
                out.append(cur); cur = []
        if cur: out.append(cur)
    return [{"start": c[0]["t"], "words": c} for c in out]


def build(sc, tm, work):
    bounds = beat_bounds(sc, tm); dur = tm["duration"]; items, beats, cues, cams, reacts = [], [], [], [], []

    def prep(h, i, t0, until, top):
        o = dict(h); o["at"] = r3(at_time(h.get("at"), tm, i, t0))
        if until is not None: o["until"] = until
        elif "until" in h: o["until"] = r3(at_time(h["until"], tm, i, t0))
        for k in TIME_LISTS:
            if k in o: o[k] = [r3(at_time(x, tm, i, t0)) for x in o[k]]
        for k in TIME_ONE:
            if k in o: o[k] = r3(at_time(o[k], tm, i, t0))
        for k in ("src", "img"):
            if o.get(k) and not o[k].startswith(("http", "data:")):
                src = o[k] if os.path.isabs(o[k]) else os.path.join(sc["_dir"], o[k])
                dst = "assets/" + os.path.basename(src); shutil.copy(src, os.path.join(work, "page", dst)); o[k] = dst
        for k in ("words", "speak"):   # [[time, ...], ...]
            if k in o: o[k] = [[r3(at_time(x[0], tm, i, t0))] + list(x[1:]) for x in o[k]]
        if o.get("icon"): o["svg"] = icon(o["icon"], 160, o.get("color", "#111"))
        for k in ("fromIcon", "toIcon"):
            if o.get(k): o[k[:-4] + "Svg"] = icon(o[k], 160, o.get(k[:-4] + "Color", "#fff"))
        if isinstance(o.get("items"), list) and o["items"] and isinstance(o["items"][0], dict):
            o["items"] = [dict(x, svg=icon(x["icon"], 160, x.get("color", "#e5372d")) if x.get("icon") else "") for x in o["items"]]
        if o.get("tiles"): o["tiles"] = [dict(x, svg=icon(x["icon"], 160, x.get("color", "#111")) if x.get("icon") else "") for x in o["tiles"]]
        sid, g = POP.get(o["type"], ("pro_pop/thup", -19))
        if h.get("sfx", True): cues.append([o["at"], h.get("sfx_id", sid), g])
        for a_ in o.get("ats", [])[1:]: cues.append([a_, "pro_pop/thup", -19])
        for a_ in o.get("ticks", []): cues.append([a_, "pro_pop/tink", -18])
        if "dropAt" in o: cues.append([o["dropAt"], "whoosh_fast/crisp", -17])
        if o.get("children"): o["children"] = [prep(c, i, t0, None, False) for c in o["children"]]
        return o

    for i, (b, (t0, t1)) in enumerate(zip(sc["beats"], bounds)):
        beats.append({"t0": t0, "t1": t1, "slug": b.get("slug", f"{i + 1:02d}"), "count": b.get("count"), "bg": b.get("bg"), "wipe": b.get("wipe", False), "pres": b.get("presenter", True)})
        hs = b.get("hero", []); hs = hs if isinstance(hs, list) else [hs]
        for h in hs:
            keep = h.get("keep", 0); until = r3(bounds[min(i + keep, len(bounds) - 1)][1])
            o = prep(h, i, t0, until, True)
            if "until" in h: o["until"] = r3(at_time(h["until"], tm, i, t0))
            items.append(o)
        if b.get("cam") == "big":
            first = min([at_time(h.get("at"), tm, i, t0) for h in hs] or [t1])
            cams.append({"t0": t0, "t1": r3(first) if first < t1 - .05 else None, "scale": b.get("camScale", 1.35), "y": b.get("camY", -150)})
        rs = b.get("react", []); rs = rs if isinstance(rs, list) else [rs]
        for x in rs:
            t = r3(at_time(x, tm, i, t0)); reacts.append(t); cues.append([t, "pro_impact/air", -16])
        if i: cues.append([t0, "swish/soft", -22])
        for s_ in b.get("sfx", []):   # extra sounds: [time|word:xyz, id, gain]
            cues.append([r3(at_time(s_[0], tm, i, t0)), s_[1], s_[2] if len(s_) > 2 else -16])
    lines = blocks(tm, sc.get("caption_words", 7))
    reel = {"dur": dur, "theme": sc.get("theme", "paper"), "counter": sc.get("counter"), "meta": sc.get("meta", True), "beats": beats, "items": items, "lines": lines,
            "cams": cams, "reacts": reacts}
    if sc.get("theme") == "kit" or sc.get("caption_y"): reel["capY"] = sc.get("caption_y", [1150, 1580])
    if sc.get("character", "kai") == "kai":
        ws = [w for l in tm["lines"] for w in l["words"]]
        words = [{"t": w["t"], "d": r3((ws[k + 1]["t"] if k + 1 < len(ws) else w["t"] + .3) - w["t"]), "n": len(re.sub(r"[^A-Za-z0-9]", "", w["w"]))} for k, w in enumerate(ws)]
        reel["avatar"] = {"poses": [{"t0": t0, "pose": b.get("pose", "talk")} for b, (t0, _) in zip(sc["beats"], bounds)], "words": words,
                          "top": sc.get("presenter", {}).get("y", 1060), "scale": sc.get("presenter", {}).get("scale", 1), "colors": sc.get("avatar_colors", {})}
        reel["presenter"] = {"headX": .5, "headY": .31}
    else:
        cdir = sc.get("character") if os.path.isdir(str(sc.get("character"))) else os.path.join(KIT, "characters", sc.get("character"))
        cj = json.load(open(os.path.join(cdir, "character.json")))
        reel["presenter"] = {"headX": cj.get("head_x", .517), "headY": cj.get("head_y", .31)}
    return reel, bounds, cues


def presenter(sc, bounds, dur):
    """the avatar at the bottom. Default "kai": the engine's own code-drawn presenter (engine/avatar.js), posed per
    beat. Any other value is a reel-kit video character folder (one transparent gesture clip per beat, looped)."""
    if sc.get("character", "kai") == "kai":
        return None, '<div id="pres"><div id="presin"></div></div>'
    cdir = sc.get("character") if os.path.isdir(str(sc.get("character"))) else os.path.join(KIT, "characters", sc.get("character"))
    c = json.load(open(os.path.join(cdir, "character.json"))); clips, alias = c["clips"], c.get("aliases", {})
    cw, ch = c.get("canvas", [1800, 1080]); P = sc.get("presenter", {})
    W = P.get("width", 1500); x = P.get("x", 540 - W / 2); y = P.get("y", 1150)
    vids, k = "", 0
    for i, ((t0, t1), b) in enumerate(zip(bounds, sc["beats"])):
        name = b.get("pose", "talk"); name = alias.get(name, name); name = name if name in clips else c.get("default", "talk")
        a, z = clips[name]; tt, first = t0, True
        while tt < t1 - 0.02:
            ms = a + (min((z - a) * 0.3, 0.4) if first and i else 0); d = min(z - ms, t1 - tt)
            vids += (f'<video class="clip" src="assets/{c["file"]}" muted playsinline data-start="{r3(tt)}" data-duration="{r3(d)}" '
                     f'data-media-start="{r3(ms)}" data-track-index="3" style="position:absolute;left:0;top:0;width:100%;height:100%"></video>')
            tt += d; k += 1; first = False
    return os.path.join(cdir, c["file"]), (f'<div id="pres" style="left:{x}px;top:{y}px;width:{W}px;aspect-ratio:{cw}/{ch}">'
                                           f'<div id="presin">{vids}</div></div>')


def page(sc, tm, work):
    pg = os.path.join(work, "page"); shutil.rmtree(pg, ignore_errors=True); os.makedirs(os.path.join(pg, "assets"))
    shutil.copytree(os.path.join(HERE, "engine", "fonts"), os.path.join(pg, "fonts"))
    for f in ("gsap.min.js", "beats.js", "avatar.js", "style.css", "kit-bg.png"): shutil.copy(os.path.join(HERE, "engine", f), pg)
    reel, bounds, cues = build(sc, tm, work)
    src, pres = presenter(sc, bounds, tm["duration"])
    vids = ""
    for k, o in enumerate([o for o in reel["items"] if o["type"] == "video"]):
        o["vid"] = f"hv{k}"; d = r3(o.get("until", tm["duration"]) - o["at"] + 0.2)
        vids += (f'<video class="clip" id="hv{k}" src="{o["src"]}" muted playsinline data-start="{r3(o["at"] - 0.2)}" data-duration="{d}" '
                 f'data-media-start="{r3(max(0, o.get("media", 0) - 0.2))}" data-track-index="{4 + k}"></video>')
    box = '<div id="pbox"></div>' if sc.get("theme") == "kit" else ""
    if src: shutil.copy(src, os.path.join(pg, "assets", os.path.basename(src)))
    dur = tm["duration"]
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"/><title>{sc["_name"]}</title>
<link rel="stylesheet" href="style.css"/><script src="gsap.min.js"></script></head><body>
<div id="root" data-composition-id="reel" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920" data-fps="30">
 <div id="stage"><div id="dots"></div><div id="glow"></div><div id="flood"></div>
  <div id="meta"></div><div id="cap"></div><div id="heroes"></div>{box}{pres}<div id="wipe"></div></div>
 <div id="vids" style="display:none">{vids}</div>
</div>
<script>window.REEL = {json.dumps(reel)};</script><script src="beats.js"></script><script src="avatar.js"></script></body></html>'''
    open(os.path.join(pg, "index.html"), "w").write(html)
    return bounds, cues


def render(work, out):
    pg = os.path.join(work, "page"); env = dict(os.environ, HYPERFRAMES_BROWSER_PATH=HF_BROWSER)
    shutil.rmtree("/tmp/hyperframes-extract-cache-0", ignore_errors=True)
    r = subprocess.run(["npx", "hyperframes", "render", ".", "-o", out], cwd=pg, env=env, capture_output=True, text=True)
    if r.returncode or not os.path.exists(out): print(r.stdout[-1500:], r.stderr[-1500:]); raise SystemExit("render failed")


def board(work, bounds, out):
    """frames sheet: the middle of every beat."""
    from PIL import Image
    vid = os.path.join(work, "silent.mp4"); tiles = []
    for t0, t1 in bounds:
        p = os.path.join(work, "b.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{(t0 + t1) / 2:.2f}", "-i", vid, "-frames:v", "1", "-vf", "scale=270:480", p])
        tiles.append(Image.open(p).convert("RGB"))
    cols = min(8, len(tiles)); rows = (len(tiles) + cols - 1) // cols
    S = Image.new("RGB", (cols * 270, rows * 480), "white")
    for k, t in enumerate(tiles): S.paste(t, ((k % cols) * 270, (k // cols) * 480))
    S.save(out, quality=88)


def main():
    if len(sys.argv) < 3: print(__doc__); sys.exit(1)
    cmd, path = sys.argv[1], sys.argv[2]; sc = load(path)
    work = os.path.join(sc["_dir"], "build", sc["_name"]); os.makedirs(work, exist_ok=True)
    print("voice ..."); tm = speak(sc, work)
    print(f"  {tm['duration']} s, {len(tm['lines'])} lines")
    bounds, cues = page(sc, tm, work)
    intro = voice.intro(sc)
    if intro: cues.insert(0, [0.0, "file:" + intro["sound"], intro["gain"]])
    print("render ..."); render(work, os.path.join(work, "silent.mp4"))
    if cmd == "board":
        out = os.path.join(sc["_dir"], sc["_name"] + "-frames.jpg"); board(work, bounds, out); print("frames:", out); return
    print("mix ..."); lufs, n = sound.mix(work, cues, tm["duration"], {"music": {"style": "none"}, "levels": {"sfx": sc.get("sfx_level", -26)}})
    out = os.path.join(sc["_dir"], sc["_name"] + ".mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(work, "silent.mp4"), "-i", os.path.join(work, "mix.wav"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    print(f"done: {out}  ({lufs:.1f} LUFS, {n} sounds)")


if __name__ == "__main__":
    main()
