"""Writes <work>/film/index.html (HyperFrames + GSAP) from the script and the voice timing."""
import json, os, re, shutil
from .cards import CARDS, esc

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(os.path.dirname(HERE))
THEME = dict(paper="#efece6", ink="#141414", accent="#e5372d", grey="#c9c4ba", mid="#8a857c", card="#1b1b1d")
W, H = 1080, 1920
r3 = lambda v: round(float(v), 3)

class Ctx:
    """Per-scene helpers handed to card functions."""
    def __init__(s, film, si, start, end, lines, p):
        s.f, s.si, s.start, s.end, s.lines, s.p = film, si, start, end, lines, p
        s.A, s.th, s.brand, s.avatar, s.r = film.js.append, film.th, film.brand, film.avatar, r3
    def at(s, spec):
        """Times: a number (seconds after scene start), 'start', 'end', 'line:N', 'line:N:end', 'word:text'
        (first match in the scene, punctuation ignored); any of them can end in +0.2 / -0.1."""
        if isinstance(spec, (int, float)): return s.start + spec
        m = re.match(r"^(.*?)([+-]\d*\.?\d+)?$", str(spec).strip()); base, off = m.group(1), float(m.group(2) or 0)
        if base == "start": t = s.start
        elif base == "end": t = s.end
        elif base.startswith("line:"):
            parts = base.split(":"); ln = s.lines[min(int(parts[1]), len(s.lines) - 1)]
            t = ln["end"] if len(parts) > 2 and parts[2] == "end" else ln["start"]
        elif base.startswith("word:"):
            want = base[5:].lower().strip(); t = None
            for ln in s.lines:
                for w in ln["words"]:
                    if w["w"].lower().strip(",.!?:;\"'") == want: t = w["t"]; break
                if t is not None: break
            if t is None: raise SystemExit(f"scene {s.si + 1}: no word '{want}' for timing")
        else: raise SystemExit(f"bad time '{spec}'")
        return t + off
    def sfx(s, t, sid, gain): s.f.cues.append((round(t, 3), sid, gain))
    def shake(s, t, amt=14):
        s.A(f'tl.to("#stage", {{ keyframes: [{{ x: {amt}, y: {-amt / 2} }}, {{ x: {-amt}, y: {amt / 2} }}, {{ x: {amt / 2}, y: 0 }}, {{ x: 0, y: 0 }}], duration: 0.2, ease: "none" }}, {r3(t)});')
    def stamp(s, text, t, o=None):
        o = o or {}; sid = f"{s.p}-st{len(s.f.stamps)}"; rot = o.get("rot", -8)
        s.f.stamps.append(sid); s.f.stamp_times.append(t)
        s.f.extra[s.p] = s.f.extra.get(s.p, "") + f'<div id="{sid}" class="stamp{" big" if o.get("big") else ""}" style="left:{o.get("x", 300)}px;top:{o.get("y", -120)}px">{esc(text)}</div>'
        s.A(f'tl.fromTo("#{sid}", {{ opacity: 0, scale: 2.6, rotation: {rot - 10} }}, {{ opacity: 1, scale: 1, rotation: {rot}, duration: 0.16, ease: "power4.in" }}, {r3(t - 0.16)});')
        s.shake(t); s.sfx(t, "pro_impact/short", -7 if o.get("big") else -9)
        if o.get("big"): s.sfx(t, "cut_hit/punch", -10)
    def count(s, sel, a, b, t, dur, pre="", suf="", dec=0):
        s.f.counters += 1; k = s.f.counters
        s.A(f'const cnt{k} = {{ v: {a} }}; tl.to(cnt{k}, {{ v: {b}, duration: {r3(dur)}, ease: "power2.out", onUpdate: () => {{ document.querySelector("{sel}").textContent = "{pre}" + fmt(cnt{k}.v, {dec}) + "{suf}"; }} }}, {r3(t)});')
    def asset(s, path): return s.f.asset(path)

class Film:
    def __init__(s, script, timing, work, script_dir):
        s.sc, s.tm, s.work, s.sdir = script, timing, work, script_dir
        s.th = {**THEME, **script.get("theme", {})}; s.brand = script.get("brand", {})
        s.js, s.cues, s.stamps, s.extra, s.counters, s.uses_figures, s.stamp_times = [], [], [], {}, 0, False, []
        s.out = os.path.join(work, "film"); os.makedirs(os.path.join(s.out, "assets"), exist_ok=True)
        s.char = s.load_character(script.get("character", "default"))
        s.avatar = s.asset(s.brand["avatar"]) if s.brand.get("avatar") else s.char_avatar()
    def asset(s, path):
        src = path if os.path.isabs(path) else os.path.join(s.sdir, path)
        if not os.path.exists(src): raise SystemExit(f"missing file {path}")
        name = "assets/" + os.path.basename(src); shutil.copy(src, os.path.join(s.out, name)); return name
    def load_character(s, ch):
        if ch in (None, "none", False): return None
        d = ch if os.path.isdir(str(ch)) else (os.path.join(s.sdir, ch) if os.path.isdir(os.path.join(s.sdir, str(ch))) else os.path.join(KIT, "characters", ch))
        cfg = json.load(open(os.path.join(d, "character.json"))); cfg["dir"] = d
        if cfg["type"] == "svg":
            svg = open(os.path.join(d, cfg["file"])).read()
            shutil.copy(os.path.join(d, cfg["file"]), os.path.join(s.out, "assets", "character.svg")); cfg["svg"] = svg
        else:
            talk = cfg.get("talk", []); talk = [talk] if isinstance(talk, str) else talk
            files = set(cfg["poses"].values()) | set(talk) | {cfg[k] for k in ("blink", "avatar") if cfg.get(k)}
            for f in files: shutil.copy(os.path.join(d, f), os.path.join(s.out, "assets", f))
        return cfg
    def char_avatar(s):
        c = s.char
        if not c: return ""
        if c["type"] == "svg": return f'assets/character.svg#svgView(viewBox({c.get("avatar_view", "395 70 410 410").replace(" ", ",")}))'
        return "assets/" + c.get("avatar", list(c["poses"].values())[0])

    # -------------------------------------------------------------------------------------------
    def build(s):
        L, dur, A, th = s.tm["lines"], s.tm["duration"], s.js.append, s.th
        scenes = s.sc["scenes"]; n = len(scenes)
        lines_of = [[ln for ln in L if ln["scene"] == i] for i in range(n)]
        start = [0.0] + [lines_of[i][0]["start"] - 0.12 for i in range(1, n)]; end = start[1:] + [dur]
        hdr, caps, cards = "", "", ""
        for i, sc in enumerate(scenes):
            st, en, lns, p = start[i], end[i], lines_of[i], f"k{i}"
            # header
            cnt = sc.get("counter") or {}
            cid = f"hv{i}"; cv = cnt.get("value", cnt.get("from", ""))
            right = f'{esc(cnt.get("name", ""))} <b id="{cid}" class="redt">{esc(cv)}</b>' if cnt else ""
            hdr += f'<div id="hd{i}" class="hdr mono"><span>// {i + 1:02d} · {esc(sc.get("label", ""))}</span><span>{right}</span></div>'
            A(f'tl.set("#hd{i}", {{ opacity: 1 }}, {r3(st)});')
            if i < n - 1: A(f'tl.set("#hd{i}", {{ opacity: 0 }}, {r3(en)});')
            ctx = Ctx(s, i, st, en, lns, p)
            if "to" in cnt: ctx.count(f"#{cid}", cnt.get("from", 0), cnt["to"], ctx.at(cnt.get("at", "line:0")), cnt.get("count_for", en - st - 0.4), cnt.get("prefix", ""), cnt.get("suffix", ""))
            for k, v in enumerate(cnt.get("steps", [])):
                A(f'tl.set("#{cid}", {{ innerText: "{esc(v)}" }}, {r3(lns[min(k, len(lns) - 1)]["start"] + 0.05)});')
            # caption: every word shows grey just before it is said, then ink (accent words red serif with a pop)
            spans = []
            for ln in lns:
                for j, w in enumerate(ln["words"]):
                    wid = f"w{i}_{ln['line']}_{j}"; spans.append(f'<span id="{wid}" class="w{" acc" if w["accent"] else ""}">{esc(w["w"])}</span>')
                    A(f'tl.fromTo("#{wid}", {{ opacity: 0, y: 22 }}, {{ opacity: 1, y: 0, duration: 0.16, ease: "power3.out" }}, {r3(max(st, w["t"] - 0.16))});')
                    A(f'tl.to("#{wid}", {{ color: "{th["accent"] if w["accent"] else th["ink"]}", duration: 0.06 }}, {r3(w["t"])});')
                    if w["accent"]: A(f'tl.fromTo("#{wid}", {{ scale: 1.25 }}, {{ scale: 1, duration: 0.35, ease: "back.out(3)" }}, {r3(w["t"])});')
            caps += f'<div id="cap{i}" class="cap{" small" if sum(len(l["text"]) for l in lns) > 60 else ""}">{" ".join(spans)}</div>'
            A(f'tl.set("#cap{i}", {{ opacity: 1 }}, {r3(st)});')
            if i < n - 1: A(f'tl.to("#cap{i}", {{ opacity: 0, y: -30, duration: 0.14, ease: "power2.in" }}, {r3(en - 0.14)});')
            # card
            card = sc.get("card")
            if card:
                fn = CARDS.get(card["type"]) or (_ for _ in ()).throw(SystemExit(f"unknown card type {card['type']}; have {list(CARDS)}"))
                inner = fn(p, card, ctx)
                for fx in card.get("sfx", []): ctx.sfx(ctx.at(fx.get("at", "start")), fx["id"], fx.get("gain", -10))
                if card.get("stamp"):
                    stp = card["stamp"]; stp = {"text": stp} if isinstance(stp, str) else stp
                    ctx.stamp(stp["text"], ctx.at(stp.get("at", "end-0.45")), stp)
                top = card.get("top", (510 if card["type"] == "figure" else 600) if s.char else 720)
                cards += f'<div id="{p}" class="card-wrap" style="top:{top}px">{inner}@@EXTRA_{p}@@</div>'
                rot = [-4, 4, -3, 3][i % 4]
                A(f'tl.fromTo("#{p}", {{ opacity: 0, y: 80, rotation: {rot}, scale: 0.88 }}, {{ opacity: 1, y: 0, rotation: 0, scale: 1, duration: 0.45, ease: "back.out(1.6)" }}, {r3(st + (0.05 if i == 0 else 0))});')
                if i < n - 1: A(f'tl.to("#{p}", {{ opacity: 0, y: -70, scale: 0.92, duration: 0.18, ease: "power2.in" }}, {r3(en - 0.18)});')
            if i: s.cues.append((round(st, 3), "swipe/glide", -17))
        for p, h in s.extra.items(): cards = cards.replace(f"@@EXTRA_{p}@@", h)
        cards = re.sub(r"@@EXTRA_k\d+@@", "", cards)
        pres = s.presenter(scenes, lines_of, start, dur)
        A(f'tl.to("#paperdots", {{ x: -6, y: -40, duration: {dur}, ease: "none" }}, 0);')
        A(f'tl.to("#stage", {{ opacity: 0, duration: 0.2, ease: "power1.in" }}, {r3(dur - 0.2)});')
        s.write(hdr, caps, cards, pres, dur)
        return s.cues

    def presenter(s, scenes, lines_of, start, dur):
        c, A = s.char, s.js.append
        if not c: return ""
        names = c["poses"] if isinstance(c["poses"], list) else list(c["poses"])
        cycle = s.sc.get("pose_cycle", ["up", "palms", "card", "thumb", "shrug", "wave"])
        beats = []
        for i, sc in enumerate(scenes):
            want = sc.get("pose")
            per_line = want if isinstance(want, list) else ([want] if want else [cycle[(len(beats)) % len(cycle)] for _ in range(max(1, len(lines_of[i]) // 2))])
            for k, name in enumerate(per_line):
                ln = lines_of[i][min(k * max(1, len(lines_of[i]) // len(per_line)), len(lines_of[i]) - 1)]
                t = 0.0 if not beats else ln["start"] - 0.1
                beats.append((t, name if name in names else names[0]))
        if c["type"] == "svg":
            ho, wo = c.get("head_origin", "600 480"), c.get("wave_origin", "800 560")
            for k, (t, name) in enumerate(beats):
                A(f'tl.set("#pose-{name}", {{ opacity: 1 }}, {r3(t)});')
                if k + 1 < len(beats) and beats[k + 1][1] != name: A(f'tl.set("#pose-{name}", {{ opacity: 0 }}, {r3(beats[k + 1][0])});')
                if k: A(f'tl.fromTo("#pres-body", {{ scaleY: 0.965, y: 16 }}, {{ scaleY: 1, y: 0, duration: 0.35, ease: "back.out(3)", svgOrigin: "600 1000" }}, {r3(t)});')
                A(f'tl.to("#head", {{ rotation: {[-4, 3, -3, 4, -6, 3][k % 6]}, duration: 0.3, ease: "power2.out", svgOrigin: "{ho}" }}, {r3(t)});')
                if name == "wave": A(f'tl.to("#pose-wave", {{ rotation: 6, svgOrigin: "{wo}", duration: 0.18, yoyo: true, repeat: 5, ease: "sine.inOut" }}, {r3(t + 0.1)});')
            # lip flap while each line plays, a smile at the end, blinks every ~3 s
            A('tl.set("#m-smile", { opacity: 0 }, 0); tl.set("#m-closed", { opacity: 1 }, 0);')
            cur = "closed"
            for ln in s.tm["lines"]:
                t, k = ln["start"], 0
                while t < ln["end"] - 0.06:
                    m = "o" if k % 2 == 0 else "closed"
                    if m != cur: A(f'tl.set("#m-{cur}", {{ opacity: 0 }}, {r3(t)}); tl.set("#m-{m}", {{ opacity: 1 }}, {r3(t)});'); cur = m
                    t += 0.09 + (0.03 if k % 3 == 2 else 0); k += 1
                if cur != "closed": A(f'tl.set("#m-{cur}", {{ opacity: 0 }}, {r3(ln["end"])}); tl.set("#m-closed", {{ opacity: 1 }}, {r3(ln["end"])});'); cur = "closed"
            A(f'tl.set("#m-closed", {{ opacity: 0 }}, {r3(s.tm["lines"][-1]["end"] + 0.05)}); tl.set("#m-smile", {{ opacity: 1 }}, {r3(s.tm["lines"][-1]["end"] + 0.05)});')
            b = 1.95
            while b < dur - 0.3:
                A(f'tl.set("#eyes-open", {{ opacity: 0 }}, {r3(b)}); tl.set("#eyes-shut", {{ opacity: 1 }}, {r3(b)}); tl.set("#eyes-open", {{ opacity: 1 }}, {r3(b + 0.1)}); tl.set("#eyes-shut", {{ opacity: 0 }}, {r3(b + 0.1)});')
                b += 3.0
            body = re.sub(r"<\?xml[^>]*>", "", c["svg"])
            body = re.sub(r"<svg\b", f'<svg id="pres" style="position:absolute;left:{c.get("x", -60)}px;top:{c.get("y", 1130)}px;width:{c.get("width", 1200)}px;height:auto"', body, count=1)
        else:   # PNG poses: swap per beat, bounce + tilt on each change; optional talk/blink overlays (same canvas)
            box = "position:absolute;left:0;top:0;width:100%;height:100%;object-fit:contain;object-position:bottom"
            imgs = "".join(f'<img id="pose-{n}" class="pose" src="assets/{f}" style="{box};opacity:0"/>' for n, f in c["poses"].items())
            talk = c.get("talk", []); talk = [talk] if isinstance(talk, str) else talk
            imgs += "".join(f'<img id="talk{i}" src="assets/{f}" style="{box};opacity:0"/>' for i, f in enumerate(talk))
            if c.get("blink"): imgs += f'<img id="blink" src="assets/{c["blink"]}" style="{box};opacity:0"/>'
            tilt = c.get("tilt", 2.0)
            for k, (t, name) in enumerate(beats):
                A(f'tl.set("#pose-{name}", {{ opacity: 1 }}, {r3(t)});')
                if k + 1 < len(beats) and beats[k + 1][1] != name: A(f'tl.set("#pose-{name}", {{ opacity: 0 }}, {r3(beats[k + 1][0])});')
                if k: A(f'tl.fromTo("#presin", {{ scaleY: 0.97, y: 14 }}, {{ scaleY: 1, y: 0, duration: 0.35, ease: "back.out(3)" }}, {r3(t)});')
                A(f'tl.to("#presin", {{ rotation: {[0, tilt, -tilt * 0.7, tilt * 0.6, -tilt, tilt * 0.4][k % 6]}, duration: 0.45, ease: "power2.out" }}, {r3(t)});')
            if talk:   # lip flap, alternating openings, closed between lines
                for ln in s.tm["lines"]:
                    t, k = ln["start"], 0
                    while t < ln["end"] - 0.06:
                        which = k % (len(talk) + 1)
                        for i in range(len(talk)): A(f'tl.set("#talk{i}", {{ opacity: {1 if which == i else 0} }}, {r3(t)});')
                        t += 0.09 + (0.03 if k % 3 == 2 else 0); k += 1
                    for i in range(len(talk)): A(f'tl.set("#talk{i}", {{ opacity: 0 }}, {r3(ln["end"])});')
            else:
                for ln in s.tm["lines"]:
                    A(f'tl.to("#presin", {{ y: -6, duration: 0.12, yoyo: true, repeat: {max(1, int((ln["end"] - ln["start"]) / 0.24) * 2 - 1)}, ease: "sine.inOut" }}, {r3(ln["start"])});')
            if c.get("blink"):
                bt = 1.7
                while bt < dur - 0.3:
                    A(f'tl.set("#blink", {{ opacity: 1 }}, {r3(bt)}); tl.set("#blink", {{ opacity: 0 }}, {r3(bt + 0.1)});'); bt += 2.9
            body = (f'<div id="pres" style="position:absolute;left:{c.get("x", 140)}px;top:{c.get("y", 1180)}px;width:{c.get("width", 800)}px;height:{c.get("height", 740)}px">'
                    f'<div id="presin" style="position:absolute;inset:0;transform-origin:50% 100%">{imgs}</div></div>')
        s.rigs(c, dur)
        A(f'tl.fromTo("#pres", {{ y: 260 }}, {{ y: 0, duration: 0.5, ease: "back.out(1.4)" }}, 0);')
        return body

    def rigs(s, c, dur):
        """Optional secondary motion from character.json (all seekable tweens):
        idle:   [{sel, rot, period, origin, y}]   continuous sway (a tail, an antenna)
        twitch: [{sel, rot, every, offset, origin}]  a quick flick every few seconds (an ear)
        blink2: [{open, shut, every, offset}]     a second pair of eyes that blinks on its own clock (a pet)
        react:  {sel, y, rot, origin}             a hop whenever a stamp lands"""
        A = s.js.append
        for it in c.get("idle", []):
            half = it.get("period", 1.6) / 2; n = int(dur / half) + 1; o = f', svgOrigin: "{it["origin"]}"' if it.get("origin") else ""
            if it.get("rot"): A(f'tl.fromTo("{it["sel"]}", {{ rotation: {-it["rot"]} }}, {{ rotation: {it["rot"]}, duration: {r3(half)}, yoyo: true, repeat: {n}, ease: "sine.inOut"{o} }}, 0);')
            if it.get("y"): A(f'tl.fromTo("{it["sel"]}", {{ y: 0 }}, {{ y: {it["y"]}, duration: {r3(half)}, yoyo: true, repeat: {n}, ease: "sine.inOut" }}, 0);')
        for it in c.get("twitch", []):
            t = it.get("offset", 1.0); o = f', svgOrigin: "{it["origin"]}"' if it.get("origin") else ""
            while t < dur - 0.3:
                A(f'tl.to("{it["sel"]}", {{ rotation: {it.get("rot", 12)}, duration: 0.07, yoyo: true, repeat: 3, ease: "sine.inOut"{o} }}, {r3(t)});'); t += it.get("every", 3.0)
        for it in c.get("blink2", []):
            t = it.get("offset", 1.2)
            while t < dur - 0.3:
                A(f'tl.set("{it["open"]}", {{ opacity: 0 }}, {r3(t)}); tl.set("{it["shut"]}", {{ opacity: 1 }}, {r3(t)}); tl.set("{it["open"]}", {{ opacity: 1 }}, {r3(t + 0.12)}); tl.set("{it["shut"]}", {{ opacity: 0 }}, {r3(t + 0.12)});')
                t += it.get("every", 3.4)
        rc = c.get("react")
        if rc:
            o = f', svgOrigin: "{rc["origin"]}"' if rc.get("origin") else ""
            for t in s.stamp_times:
                A(f'tl.to("{rc["sel"]}", {{ y: {rc.get("y", -30)}, rotation: {rc.get("rot", 0)}, duration: 0.14, ease: "power2.out", yoyo: true, repeat: 1{o} }}, {r3(t - 0.02)});')

    def write(s, hdr, caps, cards, pres, dur):
        th = s.th; css = open(os.path.join(HERE, "style.css")).read()
        for k, v in th.items(): css = css.replace("{" + k + "}", v)
        for f in os.listdir(os.path.join(KIT, "assets", "fonts")): shutil.copy(os.path.join(KIT, "assets", "fonts", f), os.path.join(s.out, "assets", f))
        shutil.copy(os.path.join(KIT, "assets", "gsap.min.js"), os.path.join(s.out, "gsap.min.js"))
        head_extra, mod, upd = "", "", ""
        if s.uses_figures:
            shutil.copy(os.path.join(KIT, "assets", "vendor", "hairline.js"), os.path.join(s.out, "assets", "hairline.js"))
            head_extra = "<script>" + open(os.path.join(KIT, "core", "clock.js")).read() + "</script>"
            mod = '<script type="module">import * as H from "./assets/hairline.js"; window.__hairline = H;</script>'
            upd = ", onUpdate() { window.__advance(tl.time() * 1000); }"
        js = "\n".join(s.js)
        html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><title>{esc(s.sc.get("title", "reel"))}</title><style>{css}</style>{head_extra}<script src="gsap.min.js"></script>{mod}</head>
<body>
<div id="root" data-composition-id="reel" data-start="0" data-duration="{dur}" data-width="{W}" data-height="{H}" data-fps="{s.sc.get("fps", 30)}">
 <div id="stagewrap" class="clip" data-start="0" data-duration="{dur}" data-track-index="1">
  <div id="stage">
   <div id="paperdots"></div><div id="vig"></div>
   {hdr}{caps}{cards}{pres}
  </div>
 </div>
</div>
<script>
const fmt = (v, d) => Number(v).toLocaleString("en-US", {{ minimumFractionDigits: d, maximumFractionDigits: d }});
const tl = gsap.timeline({{ paused: true{upd} }});
{js}
window.__timelines = window.__timelines || {{}};
window.__timelines["reel"] = tl;
</script></body></html>'''
        open(os.path.join(s.out, "index.html"), "w").write(html)
