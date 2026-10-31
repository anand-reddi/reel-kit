"""Writes <work>/film/index.html (HyperFrames + GSAP) from the script and the voice timing."""
import json, os, re, shutil, sys
from .cards import CARDS, esc

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(os.path.dirname(HERE))
THEMES = {
    "light": dict(paper="#efece6", ink="#141414", accent="#e5372d", grey="#c9c4ba", mid="#8a857c", card="#1b1b1d",
                  surface="#ffffff", edge="#141414", shadow="#141414", soft="#14141428", vig="#14141418", rays="#14141410",
                  ed="#d7d3cb", ed2="#c4bfb6", ed3="#8f8a81", blend="multiply", glow="transparent"),
    # neutral black (no blue tint); the presenter's red label carries the accent
    "dark":  dict(paper="#0b0b0b", ink="#f2f1ee", accent="#e5372d", grey="#3a3a3a", mid="#8e8d89", card="#000000",
                  surface="#171717", edge="#2b2b2b", shadow="#000000", soft="#00000080", vig="#00000080", rays="#ffffff07",
                  ed="#2a2a2a", ed2="#202020", ed3="#4a4a4a", blend="normal", glow="transparent"),
}
THEME = THEMES["light"]
W, H = 1080, 1920

# Font presets ("fonts" in the script): headline sans, accent italic serif, mono. Files live in assets/fonts.
FONTS = {
    "grotesk":   None,   # Space Grotesk / Instrument Serif / IBM Plex Mono (style.css defaults)
    "bricolage": dict(sans=("Bricolage Grotesque", {500: "bricolage-grotesque-latin-500-normal.woff2", 700: "bricolage-grotesque-latin-700-normal.woff2",
                                                    800: "bricolage-grotesque-latin-800-normal.woff2"}, 700, -2.5),
                      serif=("DM Serif Display", "dm-serif-display-latin-400-italic.woff2", 400),
                      mono=("JetBrains Mono", "jetbrains-mono-latin-500-normal.woff2")),
    "archivo":   dict(sans=("Archivo", {600: "archivo-latin-600-normal.woff2", 800: "archivo-latin-800-normal.woff2"}, 800, -3),
                      serif=("Playfair Display", "playfair-display-latin-600-italic.woff2", 600),
                      mono=("JetBrains Mono", "jetbrains-mono-latin-500-normal.woff2")),
}

def fonts_css(name):
    f = FONTS.get(name)
    if not f: return ""
    (sn, files, cap_w, ls), (se, sef, sew), (mn, mf) = f["sans"], f["serif"], f["mono"]
    css = "".join(f'@font-face {{ font-family: "{sn}"; src: url("assets/{fn}"); font-weight: {w}; }}' for w, fn in files.items())
    css += f'@font-face {{ font-family: "{se}"; src: url("assets/{sef}"); font-style: italic; font-weight: {sew}; }}'
    css += f'@font-face {{ font-family: "{mn}"; src: url("assets/{mf}"); font-weight: 500; }}'
    css += (f'#root {{ font-family: "{sn}", sans-serif; }} .cap {{ font-weight: {cap_w}; letter-spacing: {ls}px; }}'
            f'.acc {{ font-family: "{se}", serif; font-weight: {sew}; letter-spacing: -1px; }} .sv {{ font-family: "{se}", serif; }} .cap.short .w.it {{ font-family: "{se}", serif; font-weight: {sew}; }}'
            f'.mono, .ptxt, .code, .gl, .gm {{ font-family: "{mn}", monospace; }}')
    return css
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
    def typing(s, t, dur, gain=-15, sid="pro_typing_run/soft"):
        """Typing sound that starts with the first letter and lasts exactly as long as the text types in. Only for a
        single line of text: several lines typing at once never stay in sync, so cards skip it there."""
        s.f.cues.append((round(t, 3), sid, gain, {"dur": round(max(0.2, dur), 3), "align": "start"}))
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
        th = script.get("theme", {}); th = {"base": th} if isinstance(th, str) else th
        s.th = {**THEMES[th.get("base", "light")], **{k: v for k, v in th.items() if k != "base"}}; s.brand = script.get("brand", {})
        s.js, s.cues, s.stamps, s.extra, s.counters, s.uses_figures, s.stamp_times = [], [], [], {}, 0, False, []
        s.uses_video, s.vid_track = False, 0
        s.fx_used, s.fx_html = set(), ""
        s.out = os.path.join(work, "film"); os.makedirs(os.path.join(s.out, "assets"), exist_ok=True)
        s.char = s.load_character(script.get("character", "default"))
        # "aspect": "16:9" -> 1920x1080: the 9:16 column (header, captions, cards) keeps its own 1080-wide coordinates on
        # the left, scaled by "column.scale"; the presenter stands on the right ("presenter": {x, y, width} overrides)
        s.wide = script.get("aspect") == "16:9"
        s.W, s.H = (1920, 1080) if s.wide else (W, H)
        if s.wide and s.char:
            c = s.char
            if c["type"] == "svg":
                pw = 1150; pos = {"x": 1510 - pw / 2, "y": 1080 - (1920 - 1290) * pw / 960 + 40, "width": pw}
            else:   # video / rig: full canvas, head at canvas centre, bottom on the frame's bottom edge
                cw, ch = c.get("canvas", [1200, 720]); pw = 1500 if c["type"] == "video" else 1000
                pos = {"x": 1590 - pw / 2, "y": 1080 - pw * ch / cw + 20, "width": pw, "height": pw * ch / cw}
            c.update(pos); c.update(script.get("presenter", {}))
        s.avatar = s.asset(s.brand["avatar"]) if s.brand.get("avatar") else s.char_avatar()
    def asset(s, path):
        src = path if os.path.isabs(path) else os.path.join(s.sdir, path)
        if not os.path.exists(src): raise SystemExit(f"missing file {path}")
        name = "assets/" + os.path.basename(src); shutil.copy(src, os.path.join(s.out, name)); return name
    def load_character(s, ch):
        if ch in (None, "none", False): return None
        d = ch if os.path.isdir(str(ch)) else (os.path.join(s.sdir, ch) if os.path.isdir(os.path.join(s.sdir, str(ch))) else os.path.join(KIT, "characters", ch))
        cfg = json.load(open(os.path.join(d, "character.json"))); cfg["dir"] = d
        if cfg["type"] == "rig":
            for part in cfg["parts"]:
                if part.get("src"): shutil.copy(os.path.join(d, part["src"]), os.path.join(s.out, "assets", part["src"]))
            if cfg.get("avatar"): shutil.copy(os.path.join(d, cfg["avatar"]), os.path.join(s.out, "assets", cfg["avatar"]))
            return cfg
        if cfg["type"] == "video":
            for f in {cfg["file"], cfg.get("avatar")} - {None}: shutil.copy(os.path.join(d, f), os.path.join(s.out, "assets", f))
            return cfg
        if cfg["type"] == "svg":
            svg = open(os.path.join(d, cfg["file"])).read()
            shutil.copy(os.path.join(d, cfg["file"]), os.path.join(s.out, "assets", "character.svg")); cfg["svg"] = svg
        else:
            talk = cfg.get("talk", []); talk = [talk] if isinstance(talk, str) else talk
            files = set(cfg["poses"].values()) | set(talk) | {cfg[k] for k in ("blink", "avatar", "end") if cfg.get(k)} | {L["src"] for L in cfg.get("layers", [])}
            for f in files: shutil.copy(os.path.join(d, f), os.path.join(s.out, "assets", f))
        return cfg
    def char_avatar(s):
        c = s.char
        if not c: return ""
        if c["type"] == "rig": return "assets/" + c["avatar"] if c.get("avatar") else ""
        if c["type"] == "svg": return f'assets/character.svg#svgView(viewBox({c.get("avatar_view", "395 70 410 410").replace(" ", ",")}))'
        if c["type"] == "video": return "assets/" + c["avatar"] if c.get("avatar") else ""
        return "assets/" + c.get("avatar", list(c["poses"].values())[0])

    # -------------------------------------------------------------------------------------------
    def build(s):
        L, dur, A, th = s.tm["lines"], s.tm["duration"], s.js.append, s.th
        scenes = s.sc["scenes"]; n = len(scenes)
        short_cap = s.sc.get("captions") == "short"
        cut_of = lambda k: scenes[k].get("cut", "zoom" if short_cap else "slide")
        lines_of = [[ln for ln in L if ln["scene"] == i] for i in range(n)]
        start = [0.0] + [lines_of[i][0]["start"] - 0.12 for i in range(1, n)]; end = start[1:] + [dur]
        hdr, caps, cards = "", "", ""
        for i, sc in enumerate(scenes):
            st, en, lns, p = start[i], end[i], lines_of[i], f"k{i}"
            # header
            cnt = sc.get("counter") or {}
            cid = f"hv{i}"; cv = cnt.get("value", cnt.get("from", ""))
            right = f'{esc(cnt.get("name", ""))} <b id="{cid}" class="redt">{esc(cv)}</b>' if cnt else ""
            if s.sc.get("header") == "none":   # no top header at all (hidden node keeps counter ids valid)
                hdr += f'<div id="hd{i}" class="hdr" style="display:none"><b id="{cid}"></b></div>'
            elif s.sc.get("header") == "chips":   # red number tag + bold uppercase label, counter in an outlined pill
                pill = f'<span class="hcnt">{esc(cnt.get("name", ""))} <b id="{cid}">{esc(cv)}</b></span>' if cnt else ""
                hdr += (f'<div id="hd{i}" class="hdr chips"><span class="hl"><span class="hnum">{i + 1:02d}</span>'
                        f'<span class="hlab">{esc(sc.get("label", ""))}</span></span>{pill}</div>')
            else:
                hdr += f'<div id="hd{i}" class="hdr mono"><span>// {i + 1:02d} · {esc(sc.get("label", ""))}</span><span>{right}</span></div>'
            A(f'tl.set("#hd{i}", {{ opacity: 1 }}, {r3(st)});')
            if i < n - 1: A(f'tl.set("#hd{i}", {{ opacity: 0 }}, {r3(en)});')
            ctx = Ctx(s, i, st, en, lns, p)
            if "to" in cnt: ctx.count(f"#{cid}", cnt.get("from", 0), cnt["to"], ctx.at(cnt.get("at", "line:0")), cnt.get("count_for", en - st - 0.4), cnt.get("prefix", ""), cnt.get("suffix", ""))
            for k, v in enumerate(cnt.get("steps", [])):
                A(f'tl.set("#{cid}", {{ innerText: "{esc(v)}" }}, {r3(lns[min(k, len(lns) - 1)]["start"] + 0.05)});')
            # caption: every word shows grey just before it is said, then ink (accent words red serif with a pop)
            short = s.sc.get("captions") == "short"   # reference-reel captions: one short phrase at a time, centred
            lay_i = sc.get("layout", "box") if any(x.get("layout") for x in scenes) else None
            if short:
                cy = sc.get("caption_y", {"box": 850, "none": 1260, "full": 200, None: 980, **s.sc.get("caption_y", {})}[lay_i])
                # a spoken line too wide for the frame becomes two (or more) caption chunks, split between words on the
                # voice timing (never inside a red selection run), so captions stay big; capfit() shrinks any remainder
                est = lambda w: len(w["w"]) * (53 if w["accent"] else 43) + 24
                cw = s.sc.get("caption_width", 1040); chunks = []   # up to ~12% over is shrunk by capfit; wider lines split
                for ln in ([] if sc.get("captions") == "off" else lns):
                    ws_ = ln["words"]; units = []   # a red selection run is one unit (never split)
                    for j, w in enumerate(ws_):
                        if units and w["accent"] and ws_[j - 1]["accent"]: units[-1].append(j)
                        else: units.append([j])
                    parts, width = [[]], 0
                    for u in units:
                        uw = sum(est(ws_[j]) for j in u)
                        if parts[-1] and width + uw > cw: parts.append([]); width = 0
                        parts[-1] += u; width += uw
                    if len(parts) > 1 and sum(est(ws_[j]) for j in parts[-1]) + sum(est(ws_[j]) for j in parts[-2]) <= cw * 1.08:
                        last_ = parts.pop(); parts[-1] += last_   # no orphan word at the end
                    for c_, js in enumerate(parts):
                        chunks.append(dict(line=ln["line"], js=js, words=[ws_[j] for j in js],
                                           start=ln["start"] if c_ == 0 else ws_[js[0]]["t"] - 0.12))
                for k, ln in enumerate(chunks):
                    # words grow into the line one by one (width 0 -> its own width, blur 10px -> 0), so the
                    # centred line re-centres as it builds; plain words dim, *x* = selection box, _x_ = italic serif
                    spans = []; sel = s.sc.get("accent_style", "select") == "select"; run = None
                    for j, w in enumerate(ln["words"]):
                        wid = f"w{i}_{ln['line']}_{ln['js'][j]}"; t_in = max(st, w["t"] - 0.1)
                        A(f'tl.fromTo("#{wid}", {{ opacity: 0, x: 26, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.24, ease: "power3.out" }}, {r3(t_in)});')
                        # the line slides so the words shown so far stay centred (transform only; measured once fonts are in)
                        xfn = f'() => capx("cap{i}_{k}", {j})'
                        if j == 0: A(f'tl.set("#cap{i}_{k}", {{ x: {xfn}, scale: () => capfit("cap{i}_{k}") }}, {r3(st if k == 0 else ln["start"] - 0.1)});')
                        else: A(f'tl.to("#cap{i}_{k}", {{ x: {xfn}, duration: 0.24, ease: "power3.out" }}, {r3(t_in)});')
                        if sel and w["accent"]:
                            word = f'<span id="{wid}" class="w sw">{esc(w["w"])}</span>'
                            if run is None:
                                run = f"sel{i}_{ln['line']}_{ln['js'][j]}"; spans.append(f'<span id="{run}" class="sel"><b class="selbg"></b><i class="hd hl"></i><i class="hd hr"></i>{word}')
                                last = j
                                while last + 1 < len(ln["words"]) and ln["words"][last + 1]["accent"]: last += 1
                                t_end = ln["words"][last]["t"] + 0.14   # the box grows with the words, the right handle lands on the last one
                                A(f'tl.fromTo("#{run} .selbg", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {r3(max(0.3, t_end - t_in))}, ease: "power2.out", immediateRender: false }}, {r3(t_in)});')
                                A(f'tl.fromTo("#{run} .hl", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.22, ease: "back.out(2.5)", immediateRender: false }}, {r3(t_in)});')
                                A(f'tl.fromTo("#{run} .hr", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.22, ease: "back.out(2.5)", immediateRender: false }}, {r3(t_end)});')
                                A(f'tl.set("#{run} .selbg, #{run} .hd", {{ opacity: 1 }}, {r3(t_in)});')
                            else: spans[-1] += " " + word
                            nxt = ln["words"][j + 1] if j + 1 < len(ln["words"]) else None
                            if not (nxt and nxt["accent"]): spans[-1] += "</span>"; run = None
                            continue
                        cls = "w" + (" acc" if w["accent"] else "") + (" it" if w.get("italic") else "") + ("" if (w["accent"] or w.get("italic")) else " dim")
                        spans.append(f'<span id="{wid}" class="{cls}">{esc(w["w"])}</span>')
                    cid = f"cap{i}_{k}"
                    caps += f'<div id="{cid}" class="cap short" style="top:{cy}px">{" ".join(spans)}</div>'
                    on = st if k == 0 else ln["start"] - 0.1
                    A(f'tl.set("#{cid}", {{ opacity: 1 }}, {r3(on)});')
                    off = chunks[k + 1]["start"] - 0.1 if k + 1 < len(chunks) else (en if i < n - 1 else None)
                    if off is not None: A(f'tl.to("#{cid}", {{ opacity: 0, filter: "blur(12px)", duration: 0.14, ease: "power2.in" }}, {r3(off - 0.14)});')
            hl_ = sc.get("headline")
            if hl_:   # a title at the top: a bold line and a line in an accent block
                hl_ = [hl_] if isinstance(hl_, str) else hl_
                caps += (f'<div id="hl{i}" class="headline"><div class="h1">{esc(hl_[0])}</div>'
                         + (f'<div class="h2"><span>{esc(hl_[1])}</span></div>' if len(hl_) > 1 else "") + "</div>")
                A(f'tl.fromTo("#hl{i} .h1", {{ opacity: 0, y: -30 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }}, {r3(st)});')
                A(f'tl.fromTo("#hl{i} .h2 span", {{ opacity: 0, scale: 0.6, rotation: -3 }}, {{ opacity: 1, scale: 1, rotation: -2, duration: 0.35, ease: "back.out(2.4)" }}, {r3(st + 0.15)});')
                s.cues.append((round(st + 0.2, 3), "pro_pop_in/round", -12))
                if i < n - 1: A(f'tl.to("#hl{i}", {{ opacity: 0, duration: 0.12 }}, {r3(en - 0.12)});')
            spans = []
            for ln in ([] if short else lns):
                for j, w in enumerate(ln["words"]):
                    wid = f"w{i}_{ln['line']}_{j}"; spans.append(f'<span id="{wid}" class="w{" acc" if w["accent"] else ""}">{esc(w["w"])}</span>')
                    A(f'tl.fromTo("#{wid}", {{ opacity: 0, y: 22 }}, {{ opacity: 1, y: 0, duration: 0.16, ease: "power3.out" }}, {r3(max(st, w["t"] - 0.16))});')
                    A(f'tl.to("#{wid}", {{ color: "{th["accent"] if w["accent"] else th["ink"]}", duration: 0.06 }}, {r3(w["t"])});')
                    if w["accent"]: A(f'tl.fromTo("#{wid}", {{ scale: 1.25 }}, {{ scale: 1, duration: 0.35, ease: "back.out(3)" }}, {r3(w["t"])});')
            if not short:
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
                if short:   # cards cut in and out with the scene's cut (default: zoom-blur); sized up when the presenter is off screen
                    full = card["type"] in ("insert", "kinetic")
                    top = card.get("top", 0 if full else {"none": 360}.get(lay_i, 290 + (150 if hl_ else 0)))
                    k = card.get("scale", 1.0 if full else (1.14 if lay_i == "none" else 1.0))
                    cards += (f'<div id="{p}" class="card-wrap{" ins" if full else ""}" style="top:{top}px"><div style="position:absolute;inset:0;transform:scale({k});transform-origin:50% 0">'
                              f'{inner}@@EXTRA_{p}@@</div></div>')
                    s.card_in(p, cut_of(i), st + (0.05 if i == 0 else 0))
                    if i < n - 1: s.card_out(p, cut_of(i + 1), en)
                else:
                    big = lay_i == "none" and not s.wide   # 9:16, presenter off screen: the card grows into the free space
                    top = card.get("top", 700 if big else ((510 if card["type"] == "figure" else 600) if s.char else 720))
                    k = card.get("scale", 1.22 if big else 1.0)
                    inner_ = f'<div style="position:absolute;inset:0;transform:scale({k});transform-origin:50% 0">{inner}@@EXTRA_{p}@@</div>' if k != 1 else f'{inner}@@EXTRA_{p}@@'
                    cards += f'<div id="{p}" class="card-wrap" style="top:{top}px">{inner_}</div>'
                    rot = [-4, 4, -3, 3][i % 4]
                    A(f'tl.fromTo("#{p}", {{ opacity: 0, y: 80, rotation: {rot}, scale: 0.88 }}, {{ opacity: 1, y: 0, rotation: 0, scale: 1, duration: 0.45, ease: "back.out(1.6)" }}, {r3(st + (0.05 if i == 0 else 0))});')
                    if i < n - 1: A(f'tl.to("#{p}", {{ opacity: 0, y: -70, scale: 0.92, duration: 0.18, ease: "power2.in" }}, {r3(en - 0.18)});')
            if i: s.cut(cut_of(i), st)
            for fx in sc.get("fx", []): s.fx(fx, ctx, i)
            if sc.get("punch", s.sc.get("punch")) and lay_i == "full":   # close-ups punch in on accent words
                for ln in lns:
                    for w in ln["words"]:
                        if w["accent"]: A(f'tl.fromTo("#stage", {{ scale: 1.045 }}, {{ scale: 1, duration: 0.35, ease: "power3.out", immediateRender: false }}, {r3(w["t"])});')
        cards += s.fx_layer()
        for p, h in s.extra.items(): cards = cards.replace(f"@@EXTRA_{p}@@", h)
        cards = re.sub(r"@@EXTRA_k\d+@@", "", cards)
        pres = s.presenter(scenes, lines_of, start, dur)
        A(f'tl.to("#paperdots", {{ x: -6, y: -40, duration: {dur}, ease: "none" }}, 0);')
        A(f'tl.to("#stage", {{ opacity: 0, duration: 0.2, ease: "power1.in" }}, {r3(dur - 0.2)});')
        s.write(hdr, caps, cards, pres, dur)
        return s.cues

    # ------------------------------------------------------------------ cuts and effects
    # A scene's "cut" sets how it arrives: zoom (zoom-blur, default) | whip (fast sideways push with motion skew) |
    # flash (white frame) | impact (anime: a 2-frame ink frame, straight speed lines on ones, a smear-in) |
    # glitch (slice jitter) | dip (a one-colour dip, from html-anime's cut). Cards leave the way the next scene arrives.
    CUT_SFX = {"zoom": [("swish/soft", -13, 0)], "whip": [("whoosh_fast/whip", -11, -0.04)],
               "flash": [("shutter/quick", -13, 0), ("pro_impact/short", -17, 0)],
               "impact": [("cut_hit/punch", -9, 0), ("whoosh_fast/crisp", -14, -0.06)],
               "glitch": [("pro_glitch/standard", -13, 0)], "dip": [("swipe/velvet", -13, 0)], "slide": [("swipe/glide", -17, 0)], "hard": []}
    def card_in(s, p, cut, t):
        A = s.js.append
        if cut == "whip":
            A(f'tl.fromTo("#{p}", {{ x: 1000, skewX: -14, filter: "blur(10px)" }}, {{ x: 0, skewX: 0, filter: "blur(0px)", duration: 0.3, ease: "expo.out", immediateRender: false }}, {r3(t)});')
            A(f'tl.set("#{p}", {{ opacity: 1 }}, {r3(t)});')
        elif cut == "impact":   # smear in: stretched along the travel, settling on twos
            A(f'tl.set("#{p}", {{ opacity: 1, scaleX: 0.7, scaleY: 1.35, y: 120 }}, {r3(t + 0.067)});')
            A(f'tl.set("#{p}", {{ scaleX: 1.12, scaleY: 0.9, y: -20 }}, {r3(t + 0.133)});')
            A(f'tl.set("#{p}", {{ scaleX: 0.97, scaleY: 1.03, y: 6 }}, {r3(t + 0.2)});')
            A(f'tl.set("#{p}", {{ scaleX: 1, scaleY: 1, y: 0 }}, {r3(t + 0.267)});')
        elif cut == "hard":
            A(f'tl.set("#{p}", {{ opacity: 1 }}, {r3(t)});')
        elif cut in ("flash", "dip", "glitch"):
            A(f'tl.fromTo("#{p}", {{ opacity: 0, scale: 1.06 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power3.out", immediateRender: false }}, {r3(t)});')
            A(f'tl.set("#{p}", {{ opacity: 1 }}, {r3(t)});')
        else:
            A(f'tl.fromTo("#{p}", {{ opacity: 0, scale: 1.2, filter: "blur(16px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.32, ease: "power3.out" }}, {r3(t)});')
    def card_out(s, p, cut, en):
        A = s.js.append
        if cut == "whip":
            A(f'tl.to("#{p}", {{ x: -1000, skewX: 14, filter: "blur(10px)", duration: 0.16, ease: "power3.in" }}, {r3(en - 0.16)});')
            A(f'tl.set("#{p}", {{ opacity: 0 }}, {r3(en)});')
        elif cut in ("impact", "flash", "dip", "hard", "glitch"):
            A(f'tl.set("#{p}", {{ opacity: 0 }}, {r3(en)});')
        else:
            A(f'tl.to("#{p}", {{ opacity: 0, scale: 0.9, filter: "blur(12px)", duration: 0.16, ease: "power2.in" }}, {r3(en - 0.16)});')
    def cut(s, cut, t):
        A = s.js.append; s.fx_used.add(cut)
        for sid, g, off in s.CUT_SFX.get(cut, s.CUT_SFX["zoom"]): s.cues.append((round(t + off, 3), sid, g))
        if cut == "flash":
            A(f'tl.fromTo("#fxflash", {{ opacity: 0.95 }}, {{ opacity: 0, duration: 0.22, ease: "power2.out", immediateRender: false }}, {r3(t)});')
        elif cut == "dip":
            A(f'tl.fromTo("#fxdip", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.18, ease: "power1.in", immediateRender: false }}, {r3(t + 0.05)});')
            A(f'tl.set("#fxdip", {{ opacity: 1 }}, {r3(t - 0.05)});')
        elif cut == "impact":
            A(f'tl.set("#fxink", {{ opacity: 1 }}, {r3(t)});'); A(f'tl.set("#fxink", {{ opacity: 0 }}, {r3(t + 0.067)});')
            s.speed(t + 0.067, 0.55)
            A(f'tl.to("#stage", {{ keyframes: [{{ x: 16, y: -8 }}, {{ x: -12, y: 6 }}, {{ x: 6, y: -2 }}, {{ x: 0, y: 0 }}], duration: 0.2, ease: "none" }}, {r3(t + 0.067)});')
        elif cut == "glitch":
            for j, (dx, sk) in enumerate([(-28, 8), (22, -6), (-10, 3), (0, 0)]):
                A(f'tl.set("#stage", {{ x: {dx}, skewX: {sk} }}, {r3(t + j * 0.04)});')
            A(f'tl.set("#fxglitch", {{ opacity: 1 }}, {r3(t)});'); A(f'tl.set("#fxglitch", {{ opacity: 0 }}, {r3(t + 0.16)});')
    def speed(s, t, dur):
        """Straight focus lines on ones (two drawings swapping every frame), then gone. html-anime: few, straight, one shot."""
        A = s.js.append; s.fx_used.add("impact")
        f = 1 / 30; k = 0
        while k * f < dur:
            A(f'tl.set("#fxspeedA", {{ opacity: {1 if k % 2 == 0 else 0} }}, {r3(t + k * f)});')
            A(f'tl.set("#fxspeedB", {{ opacity: {0 if k % 2 == 0 else 1} }}, {r3(t + k * f)});'); k += 1
        A(f'tl.set("#fxspeedA, #fxspeedB", {{ opacity: 0 }}, {r3(t + dur)});')
    def fx(s, fx, ctx, i):
        """Scene "fx": [{"type": "confetti" | "ping" | "shake" | "speed" | "flash" | "riser", "at": time, ...}]."""
        A = s.js.append; t = ctx.at(fx.get("at", "start")); kind = fx["type"]; s.fx_used.add(kind)
        if kind == "confetti":
            import random; rnd = random.Random(7 + i); n = fx.get("count", 42); cx, cy = fx.get("x", 540), fx.get("y", 760)
            cols = [s.th["accent"], s.th["ink"], "#ffffff", s.th["accent"], s.th["mid"]]
            html = ""
            for j in range(n):
                cid = f"cf{i}_{j}"; w, h = rnd.randint(14, 24), rnd.randint(8, 14)
                html += f'<i id="{cid}" class="conf" style="left:{cx}px;top:{cy}px;width:{w}px;height:{h}px;background:{cols[j % len(cols)]}"></i>'
                dx, dy = rnd.uniform(-520, 520), rnd.uniform(-720, -260); r = rnd.uniform(-540, 540); fall = rnd.uniform(700, 1200)
                A(f'tl.fromTo("#{cid}", {{ opacity: 1, x: 0, y: 0, rotation: 0 }}, {{ x: {dx:.0f}, y: {dy:.0f}, rotation: {r / 2:.0f}, duration: 0.42, ease: "power3.out", immediateRender: false }}, {r3(t)});')
                A(f'tl.to("#{cid}", {{ x: {dx * 1.25:.0f}, y: {dy + fall:.0f}, rotation: {r:.0f}, opacity: 0, duration: 1.3, ease: "power1.in" }}, {r3(t + 0.42)});')
            s.fx_html += f'<div class="conflayer">{html}</div>'
            s.cues += [(round(t, 3), "pro_pop/double", -12), (round(t + 0.05, 3), "pro_shimmer/m2", -17)]
        elif kind == "ping":
            x, y = fx.get("x", 540), fx.get("y", 700)
            for j in range(2):
                pid = f"pg{i}_{len(s.fx_html)}_{j}"
                s.fx_html += f'<i id="{pid}" class="ping" style="left:{x - 60}px;top:{y - 60}px"></i>'
                A(f'tl.fromTo("#{pid}", {{ opacity: 1, scale: 0.3 }}, {{ opacity: 0, scale: 2.6, duration: 0.7, ease: "power2.out", immediateRender: false }}, {r3(t + j * 0.22)});')
            s.cues.append((round(t, 3), fx.get("sfx", "pro_notify/ding_2045"), -12))
        elif kind == "shake":
            ctx.shake(t, fx.get("amt", 14)); s.cues.append((round(t, 3), fx.get("sfx", "cut_hit/punch"), -12))
        elif kind == "speed":
            s.speed(t, fx.get("for", 0.6))
        elif kind == "flash":
            A(f'tl.fromTo("#fxflash", {{ opacity: 0.9 }}, {{ opacity: 0, duration: 0.22, ease: "power2.out", immediateRender: false }}, {r3(t)});')
        elif kind == "sfx":     # any earshot sound, its peak on "at"
            s.cues.append((round(t, 3), fx["id"], fx.get("gain", -14)))
        elif kind == "riser":   # a riser whose peak lands on "at" (a reveal), plus a hit there
            s.cues.append((round(t, 3), fx.get("sfx", "riser/build"), fx.get("gain", -18)))
            if fx.get("hit", True): s.cues.append((round(t, 3), "pro_impact/short", -15))
    def fx_layer(s):
        th = s.th; out = s.fx_html
        if "flash" in s.fx_used: out += '<div id="fxflash" class="fxfull" style="background:#fff"></div>'
        if "dip" in s.fx_used: out += f'<div id="fxdip" class="fxfull" style="background:{th["accent"]}"></div>'
        if "impact" in s.fx_used:
            import random, math
            def lines(seed):
                rnd = random.Random(seed); ps = ""
                for _ in range(26):
                    a = rnd.uniform(0, 2 * math.pi); w = rnd.uniform(0.012, 0.03); r0 = rnd.uniform(560, 760)
                    x1, y1 = 540 + math.cos(a) * 1500, 960 + math.sin(a) * 1500
                    x2, y2 = 540 + math.cos(a - w) * 1500, 960 + math.sin(a - w) * 1500
                    x3, y3 = 540 + math.cos(a - w / 2) * r0, 960 + math.sin(a - w / 2) * r0 * 1.5
                    ps += f'<path d="M{x1:.0f} {y1:.0f}L{x2:.0f} {y2:.0f}L{x3:.0f} {y3:.0f}Z"/>'
                return ps
            for nm, sd in (("A", 3), ("B", 11)):
                out += f'<svg id="fxspeed{nm}" class="fxfull speed" viewBox="0 0 1080 1920"><g fill="{th["ink"]}">{lines(sd)}</g></svg>'
            out += f'<div id="fxink" class="fxfull" style="background:{th["ink"]}"></div>'
        if "glitch" in s.fx_used:
            out += '<div id="fxglitch" class="fxfull glitch"></div>'
        return out

    @staticmethod
    def beat_at(spec, lns, dflt):
        """'line:N' or 'word:text' (+/- offset) inside one scene; gestures start a little before the word."""
        if spec is None: return dflt
        m = re.match(r"^(.*?)([+-]\d*\.?\d+)?$", str(spec).strip()); base, off = m.group(1), float(m.group(2) or 0)
        if base.startswith("line:"): return lns[min(int(base[5:]), len(lns) - 1)]["start"] - 0.1 + off
        if base.startswith("word:"):
            want = base[5:].lower()
            for ln in lns:
                for w in ln["words"]:
                    if w["w"].lower().strip(",.!?:;\"'") == want: return w["t"] - 0.15 + off
            raise SystemExit(f"no word '{want}' for a gesture")
        return dflt
    def presenter(s, scenes, lines_of, start, dur):
        c, A = s.char, s.js.append
        if not c: return ""
        names = c["poses"] if isinstance(c["poses"], list) else list(c["poses"])
        cycle = s.sc.get("pose_cycle", c.get("pose_cycle", ["up", "palms", "card", "thumb", "shrug", "wave"]))
        beats = []
        for i, sc in enumerate(scenes):
            want = sc.get("pose")
            if c["type"] == "video" and sc.get("face"): want = sc["face"]   # video characters: a face is a clip too
            if c["type"] == "video" and not want and sc.get("layout", "box") != "none":
                print(f'    WARN scene {i} "{sc.get("label", "")}": presenter on screen with no chosen gesture. Pick a "face" '
                      f'that matches the line, or use "layout": "none" (visuals only).', file=sys.stderr)
            if c["type"] == "video" and not want and sc.get("layout", "box") == "none" and any(x.get("layout") for x in scenes):
                want = ["rest"]   # off screen: hold a neutral clip (no random gestures carried into the next shot)
            per_line = want if isinstance(want, list) else ([want] if want else [cycle[(len(beats)) % len(cycle)] for _ in range(max(1, len(lines_of[i]) // 2))])
            if c["type"] == "video" and isinstance(per_line[0], dict) and per_line[0].get("at") and "rest" in names:
                per_line = ["rest"] + per_line   # neutral until the first gesture lands on its word
            for k, name in enumerate(per_line):
                ln = lines_of[i][min(k * max(1, len(lines_of[i]) // len(per_line)), len(lines_of[i]) - 1)]
                t = 0.0 if not beats else ln["start"] - 0.1
                if isinstance(name, dict):   # {"face": "facepalm", "at": "word:staring"} lands a gesture on a word or line
                    t = 0.0 if not beats else s.beat_at(name.get("at"), lines_of[i], t)
                    name = name.get("face") or name.get("pose")
                if name not in names and name not in c.get("aliases", {}):
                    print(f'    WARN scene {i}: no gesture "{name}" (has: {", ".join(names)})', file=sys.stderr)
                beats.append((t, name if name in names else names[0]))
        if c["type"] == "video":
            body = s.video_presenter(c, beats, dur)
        elif c["type"] == "rig":
            body = s.rig_presenter(c, beats, dur)
        elif c["type"] == "svg":
            ho, wo = c.get("head_origin", "600 480"), c.get("wave_origin", "800 560")
            arms = c.get("arms")
            if arms:   # two-bone arms: upper arm rotates at the shoulder (u), forearm bends at the elbow (f); hands swap mid-swing
                state = {}
                A("const ARMS = {};")
                for a in arms:
                    r0 = a["poses"]["rest"]; state[a["id"]] = [r0["u"], r0["f"], r0.get("hand")]
                    A(f'ARMS.{a["id"]} = {{ u: {r0["u"]}, f: {r0["f"]}, sx: {a["shoulder"][0]}, sy: {a["shoulder"][1]}, U: {a["upper"]} }};')
                    for h in a["hands"]: A(f'tl.set("#{a["id"]}-{h}", {{ opacity: {1 if h == r0.get("hand") else 0} }}, 0);')
                A('window.__hooks.push(() => { for (const id in ARMS) { const a = ARMS[id], el = document.getElementById(id); if (!el) continue; '
                  'el.setAttribute("transform", `rotate(${a.u} ${a.sx} ${a.sy})`); '
                  'el.querySelectorAll(".fore").forEach((g) => g.setAttribute("transform", `rotate(${a.f} ${a.U} 0)`)); } });')
            for k, (t, name) in enumerate(beats):
                if arms:
                    for a in arms:
                        p = a["poses"].get(name, a["poses"]["rest"]); cu, cf, ch = state[a["id"]]
                        tu, tf = p["u"], p["f"]; du, df = tu - cu, tf - cf
                        if abs(du) + abs(df) > 1:
                            if abs(du) + abs(df) > 25:
                                A(f'tl.to(ARMS.{a["id"]}, {{ u: {round(cu - 4 * (1 if du > 0 else -1), 2)}, f: {round(cf - 8 * (1 if df > 0 else -1), 2)}, duration: 0.08, ease: "power1.in" }}, {r3(t)});')
                            A(f'tl.to(ARMS.{a["id"]}, {{ u: {tu}, f: {tf}, duration: 0.46, ease: "back.out(1.3)" }}, {r3(t + 0.08)});')
                        h = p.get("hand", ch)
                        if h != ch:
                            sw = t + 0.2
                            if ch: A(f'tl.set("#{a["id"]}-{ch}", {{ opacity: 0 }}, {r3(sw)});')
                            A(f'tl.set("#{a["id"]}-{h}", {{ opacity: 1 }}, {r3(sw)});')
                        if p.get("wave"):
                            A(f'tl.to(ARMS.{a["id"]}, {{ f: {tf + (14 if a["id"].endswith("L") else -14)}, duration: 0.17, yoyo: true, repeat: 5, ease: "sine.inOut" }}, {r3(t + 0.56)});')
                        state[a["id"]] = [tu, tf, h]
                else:
                    A(f'tl.set("#pose-{name}", {{ opacity: 1 }}, {r3(t)});')
                    if k + 1 < len(beats) and beats[k + 1][1] != name: A(f'tl.set("#pose-{name}", {{ opacity: 0 }}, {r3(beats[k + 1][0])});')
                if k: A(f'tl.fromTo("#pres-body", {{ scaleY: 0.965, y: 16 }}, {{ scaleY: 1, y: 0, duration: 0.35, ease: "back.out(3)", svgOrigin: "600 1000" }}, {r3(t)});')
                A(f'tl.to("#head", {{ rotation: {round([-4, 3, -3, 4, -6, 3][k % 6] * c.get("head_tilt", 1), 2)}, duration: 0.3, ease: "power2.out", svgOrigin: "{ho}" }}, {r3(t)});')
                if name == "wave" and not arms: A(f'tl.to("#pose-wave", {{ rotation: 6, svgOrigin: "{wo}", duration: 0.18, yoyo: true, repeat: 5, ease: "sine.inOut" }}, {r3(t + 0.1)});')
            br = c.get("brows")
            if br:
                ups = sorted({round(w["t"], 2) for ln in s.tm["lines"] for w in ln["words"] if w.get("accent")} | {round(t, 2) for t, n in beats if n in ("shrug", "palms")})
                last = -9
                for t in ups:
                    if t - last < 0.7: continue
                    A(f'tl.to("{br["sel"]}", {{ y: {br.get("raise", -9)}, duration: 0.12, ease: "power2.out" }}, {r3(t - 0.06)}); tl.to("{br["sel"]}", {{ y: 0, duration: 0.3, ease: "power2.inOut" }}, {r3(t + 0.42)});')
                    last = t
                if br.get("end"): A(f'tl.to("{br["end"]}", {{ y: {br.get("raise", -9)}, rotation: -4, duration: 0.2, ease: "power2.out" }}, {r3(s.tm["lines"][-1]["end"] + 0.05)});')
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
            fc = c.get("faces")
            face_at = s.faces(c, fc, scenes, lines_of, start, beats) if fc else None
            b = 1.95
            while b < dur - 0.3:
                if not fc:
                    A(f'tl.set("#eyes-open", {{ opacity: 0 }}, {r3(b)}); tl.set("#eyes-shut", {{ opacity: 1 }}, {r3(b)}); tl.set("#eyes-open", {{ opacity: 1 }}, {r3(b + 0.1)}); tl.set("#eyes-shut", {{ opacity: 0 }}, {r3(b + 0.1)});')
                elif face_at(b) not in ("content", "angel", "wink", "bored"):   # blink = a quick squash of whatever eyes are showing
                    A(f'tl.to("#eyes-all", {{ scaleY: 0.12, duration: 0.05, yoyo: true, repeat: 1, ease: "power1.in", svgOrigin: "{fc.get("origin", "600 320")}" }}, {r3(b)});')
                b += 3.0
            body = re.sub(r"<\?xml[^>]*>", "", c["svg"])
            body = re.sub(r"<svg\b", f'<svg id="pres" style="position:absolute;left:{c.get("x", -60)}px;top:{c.get("y", 1130)}px;width:{c.get("width", 1200)}px;height:auto"', body, count=1)
        else:   # PNG poses: swap per beat, bounce + tilt on each change; optional talk/blink overlays (same canvas)
            box = "position:absolute;left:0;top:0;width:100%;height:100%;object-fit:contain;object-position:bottom"
            layer = lambda L: f'<img id="{L["id"]}" src="assets/{L["src"]}" style="{box}{";opacity:0" if L.get("hidden") else ""}"/>'
            imgs = "".join(layer(L) for L in c.get("layers", []) if L.get("z", 1) < 0)
            imgs += "".join(f'<img id="pose-{n}" class="pose" src="assets/{f}" style="{box};opacity:0"/>' for n, f in c["poses"].items())
            talk = c.get("talk", []); talk = [talk] if isinstance(talk, str) else talk
            imgs += "".join(f'<img id="talk{i}" src="assets/{f}" style="{box};opacity:0"/>' for i, f in enumerate(talk))
            if c.get("blink"): imgs += f'<img id="blink" src="assets/{c["blink"]}" style="{box};opacity:0"/>'
            if c.get("end"): imgs += f'<img id="endface" src="assets/{c["end"]}" style="{box};opacity:0"/>'
            imgs += "".join(layer(L) for L in c.get("layers", []) if L.get("z", 1) >= 0)
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
                        seq = c.get("talk_order") or list(range(len(talk))) + [len(talk)]
                        which = seq[k % len(seq)]
                        for i in range(len(talk)): A(f'tl.set("#talk{i}", {{ opacity: {1 if which == i else 0} }}, {r3(t)});')
                        t += 0.09 + (0.03 if k % 3 == 2 else 0); k += 1
                    for i in range(len(talk)): A(f'tl.set("#talk{i}", {{ opacity: 0 }}, {r3(ln["end"])});')
            else:
                for ln in s.tm["lines"]:
                    A(f'tl.to("#presin", {{ y: -6, duration: 0.12, yoyo: true, repeat: {max(1, int((ln["end"] - ln["start"]) / 0.24) * 2 - 1)}, ease: "sine.inOut" }}, {r3(ln["start"])});')
            if c.get("end"):
                A(f'tl.set("#endface", {{ opacity: 1 }}, {r3(s.tm["lines"][-1]["end"] + 0.05)});')
            if c.get("blink"):
                bt = 1.7
                while bt < dur - 0.3:
                    A(f'tl.set("#blink", {{ opacity: 1 }}, {r3(bt)}); tl.set("#blink", {{ opacity: 0 }}, {r3(bt + 0.1)});'); bt += 2.9
            body = (f'<div id="pres" style="position:absolute;left:{c.get("x", 140)}px;top:{c.get("y", 1180)}px;width:{c.get("width", 800)}px;height:{c.get("height", 740)}px">'
                    f'<div id="presin" style="position:absolute;inset:0;transform-origin:50% 100%">{imgs}</div></div>')
        s.rigs(c, dur)
        A(f'tl.fromTo("#pres", {{ y: 260 }}, {{ y: 0, duration: 0.5, ease: "back.out(1.4)" }}, 0);')
        if s.wide and any(sc.get("layout") for sc in scenes):   # 16:9 layouts are applied in write() (#wcam / #col)
            s.wide_lay = [(0 if i == 0 else start[i], sc.get("layout", "box")) for i, sc in enumerate(scenes)]
        elif c["type"] in ("svg", "video") and any(sc.get("layout") for sc in scenes):
            body = s.camera(body, c, scenes, start)
        return body

    def faces(s, c, fc, scenes, lines_of, start, beats):
        """Expression faces (character.json "faces"): groups #face-<name> swapped with a squash-pop. A scene's "face" (a name,
        or a list: one per line) sets them; otherwise the pose picks one (by_pose), the first beat uses "start", a stamp
        flashes "stamp" for 0.9 s, and the end of the voice shows "end" then "happy". Returns face_at(t)."""
        A, names = s.js.append, fc["names"]; org = fc.get("origin", "600 320"); dflt = fc.get("default", "neutral")
        base = []
        for i, sc in enumerate(scenes):
            want, lns = sc.get("face"), lines_of[i]
            if want:
                for k, f in enumerate(want if isinstance(want, list) else [want]):
                    if f not in names: raise SystemExit(f"scene {i + 1}: face '{f}' unknown; have: {', '.join(names)}")
                    base.append((0.0 if i == 0 and k == 0 else lns[min(k, len(lns) - 1)]["start"] - 0.08, f))
            else:
                for t, pose in beats:
                    j = max([k for k in range(len(scenes)) if start[k] <= t + 0.15] or [0])
                    if j == i: base.append((t, fc["by_pose"].get(pose, dflt) if fc.get("by_pose") else dflt))
        if base and base[0][0] > 0.01 or not base: base.insert(0, (0.0, dflt))
        if not scenes[0].get("face") and fc.get("start"): base[0] = (0.0, fc["start"])
        end = s.tm["lines"][-1]["end"] + 0.05
        if fc.get("end"): base += [(end, fc["end"]), (end + 0.8, "happy" if "happy" in names else fc["end"])]
        base.sort(key=lambda e: e[0])
        at = lambda T, ev: ([f for t, f in ev if t <= T + 1e-6] or [dflt])[-1]
        seq = list(base)
        if fc.get("stamp"):
            for t in s.stamp_times:
                seq += [(t - 0.05, fc["stamp"]), (t + 0.9, at(t + 0.9, base))]
        seq.sort(key=lambda e: e[0])
        # the opening face is baked into the svg (sets at time 0 do not survive the renderer's seek back to frame 0)
        cur = seq[0][1]; seq = seq[1:]
        c["svg"] = re.sub(r'(<g id="face-([a-z]+)" opacity=")[01](")', lambda m: m.group(1) + ("1" if m.group(2) == cur else "0") + m.group(3), c["svg"])
        for t, f in seq:
            if f == cur: continue
            if cur: A(f'tl.set("#face-{cur}", {{ opacity: 0 }}, {r3(t)});')
            A(f'tl.set("#face-{f}", {{ opacity: 1 }}, {r3(t)});')
            if cur: A(f'tl.fromTo("#face-{f}", {{ scaleY: 0.3, scaleX: 1.15, svgOrigin: "{org}" }}, {{ scaleY: 1, scaleX: 1, duration: 0.24, ease: "back.out(2.5)", svgOrigin: "{org}", immediateRender: false }}, {r3(t)});')
            cur = f
        return lambda T: at(T, seq)

    def camera(s, body, c, scenes, start):
        """Camera layouts (opt-in: any scene sets "layout"). The presenter lives in a backdrop "camera" (#cam) that
        hard-cuts per scene between "box" (a rounded frame at bottom centre under the cards; the default) and "full"
        (the presenter fills the frame, close-up, for hooks and opinions; give those scenes no card)."""
        A, th = s.js.append, s.th
        cv = {**c.get("camera", {}), **s.sc.get("camera", {})}
        hat = cv.get("top_y", 78)                 # svg y of the top of the character (hat / hair)
        k_box, k_full = cv.get("box_scale", 0.82), cv.get("full_scale", 1.55)
        bx, by, bw, bh = cv.get("box", [150, 1330, 780, 500])
        lay = {
            # box: head and hands break out over the top and sides (only the bottom edge clips), and the box sits above all
            "box":  dict(cam=dict(left=bx, top=by, width=bw, height=bh, zIndex=10, autoAlpha=1),
                         back=dict(borderRadius=28, borderWidth=3, opacity=1), clip=dict(clipPath='"inset(-900px -600px 0px -600px)"'),
                         svg=dict(left=bw / 2 - 600 * k_box, top=cv.get("box_pop", -90) - hat * k_box, width=1200 * k_box)),
            "full": dict(cam=dict(left=0, top=0, width=s.W, height=s.H, zIndex=1, autoAlpha=1),
                         back=dict(borderRadius=0, borderWidth=0, opacity=0), clip=dict(clipPath='"inset(0px 0px 0px 0px)"'),
                         svg=dict(left=s.W / 2 - 600 * k_full, top=cv.get("full_top", 600) - hat * k_full, width=1200 * k_full)),
        }
        # a soft accent glow behind the head (dark theme by default; "camera": {"glow": false | "#hex", "glow_y": svg y of the head})
        dark = s.sc.get("theme") == "dark"
        gcol = cv.get("glow", th["accent"] if dark else False)
        gy, gr = cv.get("glow_y", 250), cv.get("glow_r", 560)
        if gcol:
            bstyle = cv.get("box_style", "glow" if dark else "studio")   # studio | glow (dark box, glow inside) | open (no box)
            for L, k, ox, oy, op in (("box", k_box, bw / 2, lay["box"]["svg"]["top"], 0 if bstyle == "studio" else 1), ("full", k_full, s.W / 2, lay["full"]["svg"]["top"], 1)):
                R = gr * k / k_full * (1 if L == "full" else 1.3)
                lay[L]["glow"] = dict(left=ox - R, top=oy + gy * k - R, width=2 * R, height=2 * R, opacity=op)
        else: bstyle = cv.get("box_style", "studio")
        if bstyle == "open": lay["box"]["back"] = {**lay["box"]["back"], "opacity": 0}
        if bstyle == "glow":   # the glow lives inside the box: clip it to the box (head still breaks out over the top)
            lay["box"]["glowclip"] = dict(clipPath='"inset(0px 0px 0px 0px round 28px)"')
            lay["full"]["glowclip"] = dict(clipPath='"inset(-2000px -2000px -2000px -2000px)"')
            R = bw * 0.6   # centred in the box, so the whole glow reads inside it
            lay["box"]["glow"] = dict(left=bw / 2 - R, top=bh * 0.42 - R, width=2 * R, height=2 * R, opacity=1)
        lay["none"] = {**lay["box"], "cam": {**lay["box"]["cam"], "autoAlpha": 0}, "back": {**lay["box"]["back"], "opacity": 0}}   # presenter off screen (visual-only shots)
        js = lambda d: ", ".join(f"{k}: {round(v, 1) if isinstance(v, float) else v}" for k, v in d.items())
        cur = None
        for i, sc in enumerate(scenes):
            L = sc.get("layout", "box"); L = L if L in lay else "box"
            if L == cur: continue
            t = 0 if i == 0 else start[i]
            for sel, key in (("#cam", "cam"), ("#camback", "back"), ("#camclip", "clip"), ("#pres", "svg"), ("#camglow", "glow"), ("#glowclip", "glowclip")):
                if key not in lay[L]: continue
                A(f'tl.set("{sel}", {{ {js(lay[L][key])} }}, {r3(t)});')
            if i: A(f'tl.fromTo("#cam", {{ scale: 1.04 }}, {{ scale: 1, duration: 0.3, ease: "power2.out" }}, {r3(t)});')
            cur = L
        if bstyle == "glow": wall = cv.get("backdrop") or "#0d0d0d"
        else: wall = cv.get("backdrop") or ("radial-gradient(120% 80% at 50% 30%, #4b5260 0%, #2c3039 55%, #1a1c22 100%)" if dark
                                      else "radial-gradient(120% 80% at 50% 30%, #f4efe6 0%, #e2dacb 60%, #cfc6b5 100%)")
        lights = "" if bstyle == "glow" else "".join(f'<div style="position:absolute;left:{x}%;top:{y}%;width:{r}px;height:{r}px;border-radius:50%;background:{col};filter:blur({r // 3}px);opacity:{o}"></div>'
                         for x, y, r, col, o in ((8, 18, 160, "#ffb46b", 0.35), (78, 12, 200, "#6b8cff", 0.25), (86, 52, 120, "#ffd59a", 0.25)))
        L0 = scenes[0].get("layout", "box") if scenes else "box"
        first_back = lay[L0 if L0 in lay else "box"]["back"]["opacity"]
        glow = (f'<div id="camglow" style="position:absolute;border-radius:50%;pointer-events:none;'
                f'background:radial-gradient(circle, {gcol}8c 0%, {gcol}4d 28%, {gcol}1a 52%, transparent 70%)"></div>') if gcol else ""
        return (f'<div id="cam" style="position:absolute;transform-origin:50% 50%">'
                f'<div id="camback" style="position:absolute;inset:0;overflow:hidden;opacity:{first_back};background:{wall};border:0 solid {th["edge"]};'
                f'box-shadow:0 18px 50px rgba(0,0,0,0.35)">{lights}</div>'
                f'<div id="camclip" style="position:absolute;inset:0"><div id="glowclip" style="position:absolute;inset:0">{glow}</div>{body}</div></div>')

    def video_presenter(s, c, beats, dur):
        """A filmed/animated character: one transparent video holding gesture loops ("clips": name -> [start, end] s,
        each cut forward-then-backward so it loops cleanly). Every beat plays its gesture (pose names map through
        "aliases"), looping for as long as the beat lasts; after the voice ends it plays "end". Canvas: "canvas" [w, h]
        with the head centred at x = w/2, like the SVG characters, so the camera layouts work unchanged."""
        A = s.js.append; clips, alias = c["clips"], c.get("aliases", {}); dflt = c.get("default", next(iter(clips)))
        cw, ch = c.get("canvas", [1200, 720]); src = "assets/" + c["file"]
        last = s.tm["lines"][-1]["end"] + 0.1
        bts = [(t, n) for t, n in beats if t < last] + ([(last, "end")] if last < dur - 0.3 else [])
        vids, k = "", 0
        for b, (t, name) in enumerate(bts):
            t_end = bts[b + 1][0] if b + 1 < len(bts) else dur
            clip = alias.get(name, name); clip = clip if clip in clips else dflt
            a, z = clips[clip]; L = z - a; tt = t
            # skip the slow wind-up so the gesture peaks on the words, not a second after them
            lead = 0.0 if (b == 0 or name == "end") else min(L * c.get("lead", 0.3), 0.5)
            first = True
            while tt < t_end - 0.02:
                ms = a + (lead if first else 0); d = min(z - ms, t_end - tt)
                vids += (f'<video id="pv{k}" class="clip" src="{src}" muted playsinline data-start="{r3(tt)}" data-duration="{r3(d)}" '
                         f'data-media-start="{r3(ms)}" data-track-index="3" style="position:absolute;left:0;top:0;width:100%;height:100%"></video>')
                tt += d; k += 1; first = False
            if b: A(f'tl.fromTo("#presin", {{ scale: 0.985 }}, {{ scale: 1, duration: 0.25, ease: "back.out(3)", immediateRender: false }}, {r3(t)});')
        return (f'<div id="pres" style="position:absolute;left:{c.get("x", -60)}px;top:{c.get("y", 1130)}px;width:{c.get("width", 1200)}px;aspect-ratio:{cw}/{ch}">'
                f'<div id="presin" style="position:absolute;inset:0;transform-origin:50% 100%">{vids}</div></div>')

    def rig_presenter(s, c, beats, dur):
        """A cut-out rig: nested full-canvas parts with pivots (character.json "parts"), a pose library ("poses": part ->
        {rotation, x, y, scale} in canvas px), lip sync from mouth layers, blinks, nods on accented words, end face."""
        A = s.js.append; cw, ch = c["canvas"]
        kids = {}
        for part in c["parts"]: kids.setdefault(part.get("parent"), []).append(part)
        def build(pid):
            out = ""
            for part in kids.get(pid, []):
                ox, oy = part.get("origin", [cw / 2, ch / 2])
                img = f'<img src="assets/{part["src"]}" style="position:absolute;inset:0;width:100%;height:100%"/>' if part.get("src") else ""
                out += (f'<div id="{part["id"]}" style="position:absolute;inset:0;transform-origin:{ox / cw * 100:.2f}% {oy / ch * 100:.2f}%'
                        f'{";opacity:0" if part.get("hidden") else ""}">{img}{build(part["id"])}</div>')
            return out
        # poses: anticipation -> action (overshoot) -> hold, per the pose library
        poses = c.get("poses", {}); moved = sorted({p for v in poses.values() for p in v})
        def vals(pose, part):
            v = poses.get(pose, {}).get(part, {})
            return {"rotation": v.get("rotation", 0), "xPercent": round(v.get("x", 0) / cw * 100, 3), "yPercent": round(v.get("y", 0) / ch * 100, 3), "scale": v.get("scale", 1)}
        for k, (t, name) in enumerate(beats):
            for part in moved:
                v = vals(name, part)
                if k and abs(v["rotation"]) > 0.5:
                    A(f'tl.to("#{part}", {{ rotation: {round(-v["rotation"] * 0.3, 2)}, duration: 0.09, ease: "power1.in" }}, {r3(t)});')
                A(f'tl.to("#{part}", {{ rotation: {v["rotation"]}, xPercent: {v["xPercent"]}, yPercent: {v["yPercent"]}, scale: {v["scale"]}, duration: 0.45, ease: "back.out(1.8)" }}, {r3(t + (0.09 if k else 0))});')
        # lip sync
        talk = c.get("talk", []); seq = c.get("talk_order") or list(range(len(talk))) + [len(talk)]
        for ln in s.tm["lines"]:
            t, k, cur = ln["start"], 0, None
            while t < ln["end"] - 0.06:
                which = seq[k % len(seq)]
                if which != cur:
                    for i, m in enumerate(talk): A(f'tl.set("#{m}", {{ opacity: {1 if which == i else 0} }}, {r3(t)});')
                    cur = which
                t += 0.085 + (0.035 if k % 3 == 2 else 0); k += 1
            for m in talk: A(f'tl.set("#{m}", {{ opacity: 0 }}, {r3(ln["end"])});')
        if c.get("end"): A(f'tl.set("#{c["end"]}", {{ opacity: 1 }}, {r3(s.tm["lines"][-1]["end"] + 0.05)});')
        if c.get("blink"):
            bt = 1.6
            while bt < dur - 0.3:
                A(f'tl.set("#{c["blink"]}", {{ opacity: 1 }}, {r3(bt)}); tl.set("#{c["blink"]}", {{ opacity: 0 }}, {r3(bt + 0.11)});'); bt += 2.9 + (0.6 if int(bt) % 2 else 0)
        nod = c.get("talk_nod")
        if nod:   # a small nod on every line start and every accented word
            hits = [ln["start"] for ln in s.tm["lines"]] + [w["t"] for ln in s.tm["lines"] for w in ln["words"] if w.get("accent")]
            for t in sorted(set(round(h, 2) for h in hits)):
                A(f'tl.fromTo("#{nod["sel"].lstrip("#")}", {{ rotation: 0, yPercent: 0 }}, {{ rotation: {nod.get("rot", 1.2)}, yPercent: {round(nod.get("y", 3) / ch * 100, 3)}, duration: 0.14, ease: "power1.out", yoyo: true, repeat: 1, immediateRender: false }}, {r3(t)});')
        return (f'<div id="pres" style="position:absolute;left:{c.get("x", 114)}px;top:{c.get("y", 1165)}px;width:{c.get("width", 853)}px;'
                f'height:{c.get("height", 853)}px">{build(None)}</div>')

    def rigs(s, c, dur):
        """Optional secondary motion from character.json (all seekable tweens):
        idle:   [{sel, rot, period, origin, y}]   continuous sway (a tail, an antenna)
        twitch: [{sel, rot, every, offset, origin}]  a quick flick every few seconds (an ear)
        blink2: [{open, shut, every, offset}]     a second pair of eyes that blinks on its own clock (a pet)
        react:  {sel, y, rot, origin}             a hop whenever a stamp lands"""
        A = s.js.append
        cw, ch = c.get("canvas", [1, 1])
        def origin(o):
            if not o: return ""
            if c["type"] == "svg": return f', svgOrigin: "{o}"'
            x, y = (float(v) for v in o.split()); return f', transformOrigin: "{x / cw * 100:.2f}% {y / ch * 100:.2f}%"'
        for it in c.get("idle", []):
            half = it.get("period", 1.6) / 2; n = int(dur / half) + 1; o = origin(it.get("origin"))
            if it.get("rot"): A(f'tl.fromTo("{it["sel"]}", {{ rotation: {-it["rot"]} }}, {{ rotation: {it["rot"]}, duration: {r3(half)}, yoyo: true, repeat: {n}, ease: "sine.inOut"{o} }}, 0);')
            if it.get("y"): A(f'tl.fromTo("{it["sel"]}", {{ y: 0 }}, {{ y: {it["y"]}, duration: {r3(half)}, yoyo: true, repeat: {n}, ease: "sine.inOut" }}, 0);')
        for it in c.get("twitch", []):
            t = it.get("offset", 1.0); o = origin(it.get("origin"))
            while t < dur - 0.3:
                A(f'tl.to("{it["sel"]}", {{ rotation: {it.get("rot", 12)}, duration: 0.07, yoyo: true, repeat: 3, ease: "sine.inOut"{o} }}, {r3(t)});'); t += it.get("every", 3.0)
        for it in c.get("blink2", []):
            t = it.get("offset", 1.2)
            while t < dur - 0.3:
                if it.get("open"): A(f'tl.set("{it["open"]}", {{ opacity: 0 }}, {r3(t)}); tl.set("{it["open"]}", {{ opacity: 1 }}, {r3(t + 0.12)});')
                A(f'tl.set("{it["shut"]}", {{ opacity: 1 }}, {r3(t)}); tl.set("{it["shut"]}", {{ opacity: 0 }}, {r3(t + 0.12)});')
                t += it.get("every", 3.4)
        rc = c.get("react")
        if rc:
            o = origin(rc.get("origin"))
            for t in s.stamp_times:
                A(f'tl.to("{rc["sel"]}", {{ y: {rc.get("y", -30)}, rotation: {rc.get("rot", 0)}, duration: 0.14, ease: "power2.out", yoyo: true, repeat: 1{o} }}, {r3(t - 0.02)});')

    def write(s, hdr, caps, cards, pres, dur):
        th = s.th; css = open(os.path.join(HERE, "style.css")).read() + fonts_css(s.sc.get("fonts", "grotesk"))
        for k, v in th.items(): css = css.replace("{" + k + "}", v)
        if s.wide: css = css.replace("#root { position: relative; width: 1080px; height: 1920px;", "#root { position: relative; width: 1920px; height: 1080px;")
        for f in os.listdir(os.path.join(KIT, "assets", "fonts")): shutil.copy(os.path.join(KIT, "assets", "fonts", f), os.path.join(s.out, "assets", f))
        shutil.copy(os.path.join(KIT, "assets", "gsap.min.js"), os.path.join(s.out, "gsap.min.js"))
        head_extra, mod, upd = "", "", ""
        if s.uses_figures:
            shutil.copy(os.path.join(KIT, "assets", "vendor", "hairline.js"), os.path.join(s.out, "assets", "hairline.js"))
            head_extra = "<script>" + open(os.path.join(KIT, "core", "clock.js")).read() + "</script>"
            mod = '<script type="module">import * as H from "./assets/hairline.js"; window.__hairline = H;</script>'
            upd = "window.__advance(tl.time() * 1000);"
        js = "\n".join(s.js)
        # a video presenter's clips carry their own timing, so the stage wrapper must not be timed as well
        wrap = "" if (s.uses_video or (s.char and s.char["type"] == "video")) else f' class="clip" data-start="0" data-duration="{dur}" data-track-index="1"'
        col = hdr + caps + cards + pres
        if s.wide:
            cc = s.sc.get("column", {}); k = cc.get("scale", 0.94)
            col = (f'<div id="col" style="position:absolute;left:{cc.get("x", 50)}px;top:{cc.get("y", -60)}px;width:1080px;height:1920px;'
                   f'transform:scale({k});transform-origin:0 0">{hdr}{caps}{cards}</div>{pres}')
            # dark theme: an accent glow behind the presenter's head ("camera": {"glow": false | "#hex"} to change)
            gcol = s.sc.get("camera", {}).get("glow", th["accent"] if s.sc.get("theme") == "dark" else False)
            glow = ""
            if s.char:
                c = s.char; cx = c["x"] + c["width"] / 2; cy = c["y"] + c.get("height", c["width"] * 0.6) * 0.42; R = 520
                if gcol:
                    glow = (f'<div id="presglow" style="position:absolute;left:{cx - R:.0f}px;top:{cy - R:.0f}px;width:{2 * R}px;height:{2 * R}px;border-radius:50%;'
                            f'background:radial-gradient(circle, {gcol}80 0%, {gcol}40 30%, {gcol}14 55%, transparent 70%)"></div>')
                # layouts in 16:9: box = presenter on the right (default) | none = presenter off, the column moves to the
                # centre | full = presenter close-up (scaled round the head, moved toward the centre), no card
                cam = s.sc.get("camera", {}); kf = cam.get("full_scale", 1.55); fx = cam.get("full_x", -330)
                colc = (s.W - 1080 * k) / 2 - cc.get("x", 50)
                for t, L in getattr(s, "wide_lay", []):
                    pw = {"none": "autoAlpha: 0, scale: 1, x: 0", "full": f"autoAlpha: 1, scale: {kf}, x: {fx}"}.get(L, "autoAlpha: 1, scale: 1, x: 0")
                    s.js.append(f'tl.set("#wcam", {{ {pw} }}, {r3(t)});')
                    s.js.append(f'tl.set("#col", {{ x: {r3(colc) if L == "none" else 0} }}, {r3(t)});')
                    if t > 0 and L != "none": s.js.append(f'tl.fromTo("#wcam", {{ y: 30 }}, {{ y: 0, duration: 0.3, ease: "power2.out", immediateRender: false }}, {r3(t)});')
                col = col.replace(pres, "")
                col = (f'<div id="wcam" style="position:absolute;inset:0;transform-origin:{cx:.0f}px {cy:.0f}px">{glow}{pres}</div>') + col
        js = "\n".join(s.js)   # again: the 16:9 layouts above add timeline sets
        html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><title>{esc(s.sc.get("title", "reel"))}</title><style>{css}</style>{head_extra}<script src="gsap.min.js"></script>{mod}</head>
<body>
<div id="root" data-composition-id="reel" data-start="0" data-duration="{dur}" data-width="{s.W}" data-height="{s.H}" data-fps="{s.sc.get("fps", 30)}">
 <div id="stagewrap"{wrap}>
  <div id="stage">
   <div id="paperdots"></div><div id="vig"></div>
   {col}
  </div>
 </div>
</div>
<script>
// captions: a line that would run past the safe margins is scaled down to fit (measured with the real fonts, once)
function capoff(line, el) {{ let x = 0; while (el && el !== line) {{ x += el.offsetLeft; el = el.offsetParent; }} return x; }}
function capfit(id) {{ const line = document.getElementById(id); if (line.dataset.fit) return +line.dataset.fit;
  const ws = line.querySelectorAll(".w"), a = ws[0], b = ws[ws.length - 1];
  const w = capoff(line, b) + b.offsetWidth - capoff(line, a) + (line.querySelector(".sel") ? 70 : 20);
  const f = Math.min(1, (line.clientWidth - 30) / w); line.dataset.fit = f; return f; }}
// the line slides so the words shown so far stay centred on the frame (x is applied before the fit scale)
function capx(id, k) {{ const line = document.getElementById(id); const ws = line.querySelectorAll(".w");
  const vis = (capoff(line, ws[0]) + capoff(line, ws[k]) + ws[k].offsetWidth) / 2;
  return capfit(id) * (line.clientWidth / 2 - vis); }}
// kinetic words: scale down a word wider than the frame's safe width
function kfit(el) {{ el = typeof el === "string" ? document.querySelector(el) : el; return Math.min(1, 940 / Math.max(1, el.offsetWidth)); }}
const fmt = (v, d) => Number(v).toLocaleString("en-US", {{ minimumFractionDigits: d, maximumFractionDigits: d }});
window.__hooks = window.__hooks || [];
const tl = gsap.timeline({{ paused: true, onUpdate() {{ {upd} window.__hooks.forEach((f) => f()); }} }});
{js}
window.__timelines = window.__timelines || {{}};
window.__timelines["reel"] = tl;
</script></body></html>'''
        open(os.path.join(s.out, "index.html"), "w").write(html)
