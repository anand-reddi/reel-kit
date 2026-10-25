"""Centre cards. Each card function gets (p, cfg, ctx): p is the unique id prefix, cfg the card's JSON,
ctx the scene context (timeline helpers, time resolver, sound cues). It returns the card's inner HTML and
pushes its own animation lines and sound cues. Times in cfg use the `at` grammar (see ctx.at)."""
import html as _h, re

esc = lambda s: _h.escape(str(s))

# ------------------------------------------------------------------ prompt bar that types, then sends
def prompt(p, c, x):
    text = c.get("text", "make a reel")
    chars = "".join(f'<span class="ch">{esc(ch) if ch != " " else "&nbsp;"}</span>' for ch in text)
    tag = c.get("tag", "")
    t0 = x.at(c.get("type_at", "start+0.3")); send = x.at(c.get("send_at", "line:0:end-0.45"))
    step = min(0.045, max(0.015, (send - 0.15 - t0) / max(1, len(text))))
    for i in range(len(text)):
        x.A(f'tl.set("#{p} .ch:nth-child({i + 1})", {{ opacity: 1 }}, {x.r(t0 + i * step)});')
    x.sfx(t0 + 0.05, "pro_typing_run/soft", -15)
    x.A(f'tl.to("#{p}-send", {{ scale: 0.82, duration: 0.07, yoyo: true, repeat: 1 }}, {x.r(send)});')
    x.A(f'tl.to("#{p}-send", {{ backgroundColor: "{x.th["accent"]}", duration: 0.05 }}, {x.r(send)});')
    x.A(f'tl.fromTo("#{p} .spark i", {{ scaleX: 0, opacity: 1 }}, {{ scaleX: 1, opacity: 0, duration: 0.4, ease: "power2.out", stagger: 0.02, immediateRender: false }}, {x.r(send + 0.04)});')
    x.A(f'tl.to("#{p}-bar", {{ y: -10, duration: 0.5, ease: "sine.inOut", yoyo: true, repeat: 1 }}, {x.r(t0 + 0.3)});')
    x.sfx(send, "pro_click/soft", -8)
    if tag:
        x.A(f'tl.fromTo("#{p}-tag", {{ opacity: 0, scale: 0.3, rotation: 20 }}, {{ opacity: 1, scale: 1, rotation: -6, duration: 0.4, ease: "back.out(3)" }}, {x.r(send + 0.13)});')
        x.sfx(send + 0.18, "pro_pop_in/round", -8)
    return f'''<div class="tagline mono">{esc(c.get("label", "// your prompt"))}</div>
  <div id="{p}-bar" class="pbar"><span class="caret-in">›</span><div class="ptxt">{chars}<span class="caret"></span></div>
    <div id="{p}-send" class="send"><svg viewBox="0 0 40 40" width="44" height="44"><path d="M10,22 L20,12 L30,22 M20,12 L20,30" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></div></div>
  {f'<div id="{p}-tag" class="ptag">{esc(tag)}</div>' if tag else ''}
  <div class="spark"><i></i><i></i><i></i><i></i><i></i></div>'''

# ------------------------------------------------------------------ checklist that ticks off item by item
ICONS = {"doc": '<path d="M12,6 h16 l8,8 v26 h-24 z M16,20 h16 M16,27 h16 M16,34 h10" stroke="currentColor" stroke-width="3.5" fill="none"/>',
         "wave": "".join(f'<rect x="{6 + i * 6}" y="{24 - h}" width="3.5" height="{2 * h}" rx="2" fill="currentColor"/>' for i, h in enumerate([4, 9, 14, 7, 12, 5])),
         "cc": '<rect x="6" y="10" width="36" height="28" rx="6" stroke="currentColor" stroke-width="3.5" fill="none"/><text x="24" y="30" font-size="14" font-weight="700" text-anchor="middle" fill="currentColor" font-family="Space Grotesk">CC</text>',
         "play": '<circle cx="24" cy="24" r="17" stroke="currentColor" stroke-width="3.5" fill="none"/><path d="M20,16 L31,24 L20,32 Z" fill="currentColor"/>',
         "lock": '<rect x="10" y="20" width="28" height="20" rx="4" stroke="currentColor" stroke-width="3.5" fill="none"/><path d="M16,20 v-6 a8,8 0 0 1 16,0 v6" stroke="currentColor" stroke-width="3.5" fill="none"/>',
         "bolt": '<path d="M26,4 L10,27 h12 l-3,17 l17,-24 h-12 z" fill="currentColor"/>',
         "code": '<path d="M17,14 L7,24 L17,34 M31,14 L41,24 L31,34" stroke="currentColor" stroke-width="3.5" fill="none" stroke-linecap="round"/>',
         "star": '<path d="M24,6 l5,12 l13,1 l-10,8 l3,13 l-11,-7 l-11,7 l3,-13 l-10,-8 l13,-1 z" fill="currentColor"/>',
         "dot": '<circle cx="24" cy="24" r="9" fill="currentColor"/>'}
def checklist(p, c, x):
    items = c.get("items", [])
    n = len(items)
    if n == len(x.lines): times = [ln["start"] for ln in x.lines]
    else:
        lo, hi = x.lines[0]["start"], x.lines[-1]["end"] - 0.3
        times = [lo + (hi - lo) * i / max(1, n - 1) for i in range(n)]
    times = [x.at(it["at"]) if isinstance(it, dict) and "at" in it else t for it, t in zip(items, times)]
    rows = ""
    for i, (it, t) in enumerate(zip(items, times)):
        label = it["label"] if isinstance(it, dict) else it; icon = it.get("icon", "dot") if isinstance(it, dict) else "dot"
        rows += f'''<div id="{p}-r{i}" class="row"><div class="ico"><svg viewBox="0 0 48 48" width="56" height="56">{ICONS.get(icon, ICONS["dot"])}</svg></div>
      <div class="rlabel">{esc(label)}</div><div class="rbar"><div id="{p}-f{i}" class="rfill"></div></div>
      <div id="{p}-c{i}" class="chk"><svg viewBox="0 0 40 40" width="40" height="40"><path d="M10,21 L17,28 L31,13" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></div></div>'''
        x.A(f'tl.fromTo("#{p}-r{i}", {{ opacity: 0, x: -60 }}, {{ opacity: 1, x: 0, duration: 0.25, ease: "power3.out" }}, {x.r(t - 0.2)});')
        x.A(f'tl.fromTo("#{p}-f{i}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.4, ease: "power2.out" }}, {x.r(t - 0.05)});')
        x.A(f'tl.fromTo("#{p}-c{i}", {{ scale: 0, backgroundColor: "{x.th["grey"]}" }}, {{ scale: 1, backgroundColor: "{x.th["accent"]}", duration: 0.3, ease: "back.out(3)" }}, {x.r(t + 0.25)});')
        x.A(f'tl.set("#{p}-n", {{ innerText: "{i + 1}/{n}" }}, {x.r(t + 0.25)});')
        x.sfx(t - 0.12, "pro_hover_tick/soft", -16); x.sfx(t + 0.3, ["pro_pop/thup", "pro_pop/boop"][i % 2], -9)
    x.A(f'tl.to("#{p} .sheet", {{ rotation: -2, duration: {x.r(x.end - x.start)}, ease: "sine.inOut" }}, {x.r(x.start)});')
    return f'<div class="sheet"><div class="sheet-h mono"><span>{esc(c.get("title", "checklist"))}</span><span id="{p}-n" class="redt">0/{n}</span></div>{rows}</div>'

# ------------------------------------------------------------------ code editor that types; optional rejected timeline
TOK = re.compile(r'(?P<c>//.*$|#.*$)|(?P<s>"[^"]*"|\'[^\']*\'|`[^`]*`)|(?P<k>\b(?:const|let|var|function|return|import|from|export|await|async|def|class|if|else|for|while|new|true|false|None|null)\b)|(?P<f>\b[A-Za-z_]\w*(?=\())|(?P<n>\b\d+(?:\.\d+)?\b)')
def hl(line):
    out, pos = "", 0
    for m in TOK.finditer(line):
        out += esc(line[pos:m.start()]); g = m.lastgroup; v = esc(m.group())
        out += {"c": f'<i class="c">{v}</i>', "s": f"<s>{v}</s>", "k": f'<b class="k">{v}</b>', "f": f'<b class="f">{v}</b>', "n": f"<u>{v}</u>"}[g]
        pos = m.end()
    return out + esc(line[pos:])
def code(p, c, x):
    lines = c.get("lines", ["// code"]); t0 = x.at(c.get("type_at", "line:0+0.05"))
    step = c.get("line_step", 0.13)
    body = "".join(f'<div class="cl" id="{p}-l{i}"><em>{i + 1}</em>{hl(ln)}</div>' for i, ln in enumerate(lines))
    for i in range(len(lines)):
        x.A(f'tl.fromTo("#{p}-l{i}", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.12 }}, {x.r(t0 + i * step)});')
    x.sfx(t0, "pro_typing_run/tick", -15)
    rej = ""
    if c.get("reject"):
        r = c["reject"]; ta = x.at(r.get("at", "line:1-0.25")); st = x.at(r.get("stamp_at", "line:1:end-0.2"))
        tracks = "".join(f'<div class="trk"><div class="tclip" style="left:{l}%;width:{w}%"></div><div class="tclip" style="left:{l + w + 6}%;width:{w2}%"></div></div>' for l, w, w2 in [(4, 30, 40), (10, 22, 30), (2, 50, 20), (20, 26, 34)])
        rej = f'''<div id="{p}-ed" class="editor"><div class="ed-h mono">{esc(r.get("title", "timeline_final_v7.prproj"))}</div>{tracks}<div class="playhead"></div>
    <div id="{p}-x1" class="xline"></div><div id="{p}-x2" class="xline x2"></div></div>'''
        x.A(f'tl.fromTo("#{p}-ed", {{ opacity: 0, y: 240, rotation: 12 }}, {{ opacity: 1, y: 0, rotation: 5, duration: 0.4, ease: "back.out(1.4)" }}, {x.r(ta)});')
        x.A(f'tl.to("#{p}-code", {{ scale: 0.9, y: -60, opacity: 0.5, duration: 0.3 }}, {x.r(ta)});')
        x.sfx(ta + 0.1, "pro_whoosh_big/long", -15)
        if r.get("stamp", "NOPE"): x.stamp(r.get("stamp", "NOPE"), x.at(r.get("stamp_word_at", "line:1+0.35")), dict(x=260, y=330, rot=-12, big=True))
        if r.get("cross", True):
            x.A(f'tl.fromTo("#{p}-x1", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.14, ease: "power3.out" }}, {x.r(st)});')
            x.A(f'tl.fromTo("#{p}-x2", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.14, ease: "power3.out" }}, {x.r(st + 0.12)});')
            x.A(f'tl.to("#{p}-ed", {{ filter: "grayscale(1)", opacity: 0.55, duration: 0.3 }}, {x.r(st + 0.2)});')
            x.sfx(st + 0.02, "pro_tap/knock", -9); x.sfx(st + 0.14, "pro_tap/knock", -11)
    return f'''<div id="{p}-code" class="code"><div class="dots3"><i></i><i></i><i></i><span class="mono">{esc(c.get("file", "main.js"))}</span></div>{body}</div>{rej}'''

# ------------------------------------------------------------------ profile card with a Follow tap
def profile(p, c, x):
    b = x.brand; tap = x.at(c.get("tap_at", "line:0+0.15"))
    av = f'<img src="{esc(x.avatar)}" width="150" height="150"/>' if x.avatar else ""
    x.A(f'tl.fromTo("#{p}-rays", {{ opacity: 0, rotation: 0, scale: 0.6 }}, {{ opacity: 1, rotation: 40, scale: 1, duration: 1.8, ease: "power2.out" }}, {x.r(x.start)});')
    x.A(f'tl.fromTo("#{p}-tap", {{ opacity: 0, x: 160, y: 200 }}, {{ opacity: 1, x: 0, y: 0, duration: 0.35, ease: "power3.out" }}, {x.r(max(x.start + 0.1, tap - 0.45))});')
    x.A(f'tl.to("#{p}-tap", {{ scale: 0.86, duration: 0.07, yoyo: true, repeat: 1 }}, {x.r(tap)});')
    x.A(f'tl.to("#{p}-btn", {{ scale: 0.92, duration: 0.07, yoyo: true, repeat: 1 }}, {x.r(tap)});')
    x.A(f'tl.set("#{p}-fa", {{ display: "none" }}, {x.r(tap + 0.07)});'); x.A(f'tl.set("#{p}-fb", {{ display: "inline" }}, {x.r(tap + 0.07)});')
    x.A(f'tl.set("#{p}-btn", {{ backgroundColor: "#2b2b2f" }}, {x.r(tap + 0.07)});')
    x.A(f'tl.fromTo("#{p}-ring", {{ opacity: 1, scale: 0.2 }}, {{ opacity: 0, scale: 1.6, duration: 0.5, ease: "power2.out", immediateRender: false }}, {x.r(tap + 0.05)});')
    x.A(f'tl.fromTo("#{p}-hearts b", {{ opacity: 0, y: 0 }}, {{ opacity: 1, y: -90, duration: 0.5, ease: "power2.out", stagger: 0.04 }}, {x.r(tap + 0.1)});')
    x.A(f'tl.to("#{p}-hearts b", {{ opacity: 0, duration: 0.3, stagger: 0.04 }}, {x.r(tap + 0.6)});')
    x.A(f'tl.to("#{p}-tap", {{ opacity: 0, x: 120, y: 160, duration: 0.3, ease: "power2.in" }}, {x.r(tap + 0.5)});')
    x.A(f'tl.to("#{p}-prof", {{ scale: 1.04, duration: 1.2, ease: "sine.inOut" }}, {x.r(tap + 0.3)});')
    x.sfx(tap, "pro_click/soft", -6); x.sfx(tap + 0.1, "pro_notify/ding_2045", -12)
    hearts = "".join(f'<b style="left:{a}px;top:{bb}px;transform:scale({s})">♥</b>' for a, bb, s in [(0, 0, 1), (-70, 40, .7), (80, 30, .8), (-30, -60, .6), (50, -50, .9), (110, -10, .55)])
    ver = '<span class="ver"><svg viewBox="0 0 24 24" width="34" height="34"><circle cx="12" cy="12" r="11" fill="#2f7bf6"/><path d="M7,12.5 L10.5,16 L17,9" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round"/></svg></span>' if b.get("verified", True) else ""
    bio = "<br>".join(esc(l) for l in b.get("bio", "").split("\n"))
    return f'''<div id="{p}-rays" class="rays">{"".join(f'<i style="transform:rotate({i * 22.5}deg)"></i>' for i in range(16))}</div>
  <div id="{p}-prof" class="prof">
    <div class="ph mono"><span>{esc(b.get("handle", "@you").lstrip("@"))}</span><span>≡</span></div>
    <div class="prow"><div class="pav">{av}</div><div class="pname">{esc(b.get("handle", "@you"))} {ver}<div class="pbio">{bio}</div></div></div>
    <div id="{p}-btn" class="fbtn"><span id="{p}-fa">{esc(c.get("button", "Follow"))}</span><span id="{p}-fb" class="fb">{esc(c.get("done", "Following ✓"))}</span></div>
  </div>
  <div id="{p}-tap" class="tap"><svg viewBox="0 0 80 100" width="110" height="138"><path d="M30,8 c0,-8 14,-8 14,0 v40 l4,-2 c6,-3 12,0 12,6 l2,0 c6,-2 11,2 11,8 c6,-1 9,3 9,9 v14 c0,14 -10,22 -24,22 h-12 c-10,0 -16,-6 -22,-14 l-14,-22 c-4,-6 4,-12 10,-6 l10,10 z" fill="#fff" stroke="#141414" stroke-width="5" stroke-linejoin="round"/></svg></div>
  <div id="{p}-ring" class="ring"></div>
  <div id="{p}-hearts" class="hearts">{hearts}</div>'''

# ------------------------------------------------------------------ big number that counts up
def stat(p, c, x):
    t0 = x.at(c.get("at", "line:0")); dur = c.get("count_for", 1.0)
    x.count(f"#{p}-v", c.get("from", 0), c["value"], t0, dur, c.get("prefix", ""), c.get("suffix", ""), c.get("decimals", 0))
    bars = c.get("bars", [12, 18, 15, 26, 34, 30, 52, 78, 100])
    bh = "".join(f'<i id="{p}-b{i}" style="height:{h}%"></i>' for i, h in enumerate(bars))
    x.A(f'tl.fromTo("#{p} .bars i", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.35, ease: "back.out(2)", stagger: {x.r(dur / len(bars))} }}, {x.r(t0)});')
    x.sfx(t0, "pro_riser/nblips", -18); x.sfx(t0 + dur, "pro_pop_in/round", -9)
    return f'''<div class="sheet stat"><div class="sheet-h mono"><span>{esc(c.get("title", "the numbers"))}</span><span class="redt">{esc(c.get("tag", "live"))}</span></div>
    <div class="sv"><span id="{p}-v">{esc(c.get("prefix", ""))}0{esc(c.get("suffix", ""))}</span></div><div class="sl">{esc(c.get("label", ""))}</div>
    <div class="bars">{bh}</div></div>'''

# ------------------------------------------------------------------ growth graph that draws itself, with a marker
def graph(p, c, x):
    t0 = x.at(c.get("at", "line:0")); mk = x.at(c.get("marker_at", "line:0:end-0.3"))
    pos = c.get("marker", 0.15)   # 0..1 along x
    mx, my = 120 + pos * 560, 520 - (pos ** 2.4) * 420
    x.A(f'tl.fromTo("#{p}-curve", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: {c.get("draw_for", 1.2)}, ease: "power1.inOut" }}, {x.r(t0)});')
    x.A(f'tl.fromTo("#{p}-mk", {{ opacity: 0, scale: 2.5 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(3)", svgOrigin: "{mx:.0f} {my:.0f}" }}, {x.r(mk)});')
    x.A(f'tl.fromTo("#{p}-vl", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, {x.r(mk)});')
    x.sfx(t0, "swipe/glide", -16); x.sfx(mk, "pro_pop/tink", -10)
    path = "M120,520 " + " ".join(f"L{120 + i / 40 * 600:.0f},{520 - (i / 40) ** 2.4 * 440:.0f}" for i in range(1, 41))
    return f'''<div class="sheet graph"><svg viewBox="40 40 720 560" width="100%" height="470">
    <g stroke="#e3dfd7" stroke-width="2">{"".join(f'<path d="M{120 + i * 75},80 V520"/>' for i in range(9))}{"".join(f'<path d="M120,{80 + i * 55} H720"/>' for i in range(9))}</g>
    <path d="M120,60 V520 H740" stroke="#141414" stroke-width="5" fill="none"/><path d="M110,72 L120,56 L130,72 M728,510 L744,520 L728,530" stroke="#141414" stroke-width="5" fill="none"/>
    <text x="96" y="300" transform="rotate(-90 96 300)" class="gl">{esc(c.get("y_label", "reach"))}</text><text x="700" y="560" class="gl">{esc(c.get("x_label", "time"))}</text>
    <path id="{p}-curve" d="{path}" stroke="{x.th["mid"]}" stroke-width="5" stroke-dasharray="1" pathLength="1" fill="none"/>
    <path id="{p}-vl" d="M{mx:.0f},100 V520" stroke="{x.th["accent"]}" stroke-width="4" stroke-dasharray="12 10"/>
    <g id="{p}-mk"><circle cx="{mx:.0f}" cy="{my:.0f}" r="26" stroke="{x.th["accent"]}" stroke-width="5" fill="none"/>
      <rect x="{mx - 80:.0f}" y="545" width="160" height="40" rx="20" fill="{x.th["accent"]}"/><text x="{mx:.0f}" y="573" text-anchor="middle" class="gm">{esc(c.get("marker_label", "you are here"))}</text></g>
    </svg></div>'''

# ------------------------------------------------------------------ screenshot / image with optional highlight box
def image(p, c, x):
    src = x.asset(c["src"]); hl_ = c.get("highlight")
    box = ""
    if hl_:
        t = x.at(hl_.get("at", "line:0:end-0.3"))
        box = f'<div id="{p}-hl" class="hlbox" style="left:{hl_["x"]}%;top:{hl_["y"]}%;width:{hl_["w"]}%;height:{hl_["h"]}%"></div>'
        x.A(f'tl.fromTo("#{p}-hl", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2)" }}, {x.r(t)});')
        x.sfx(t, "pro_pop/tink", -10)
    x.A(f'tl.fromTo("#{p} .imin", {{ scale: 1 }}, {{ scale: 1.05, duration: {x.r(x.end - x.start)}, ease: "none" }}, {x.r(x.start)});')
    cap = f'<div class="imcap mono">{esc(c["caption"])}</div>' if c.get("caption") else ""
    return f'''<div class="imframe" style="height:{c.get("height", 520)}px"><div class="imin"><img id="{p}-img" src="{esc(src)}" style="object-fit:{c.get("fit", "cover")}"/>{box}</div></div>{cap}'''

# ------------------------------------------------------------------ hairline figure (live isometric line drawing)
FIGURES = ["riffle", "terrain", "exploded", "phosphor", "slow", "turntable", "keyboard", "elevator", "phone", "laptop", "terminal",
           "cabinet", "branches", "vault", "lockers", "padlock", "patch", "dish", "router", "loupe", "sieve", "rail", "plug", "query",
           "drawer", "basket", "plot", "hub", "relay", "settle", "format", "rebuild", "stack"]
def figure(p, c, x):
    name = c.get("name", "terminal")
    if name not in FIGURES: raise SystemExit(f"figure '{name}' unknown; have: {', '.join(FIGURES)}")
    x.f.uses_figures = True
    start = x.at(c.get("mount_at", "start"))
    path = [[round(x.at(k.get("at", "start")), 3), k.get("x", 0.5), k.get("y", 0.5)] for k in c.get("path", [])]
    opts = {"intensity": c.get("intensity", 0.8)}
    if not path: opts["play"] = True
    import json as _j
    x.A(f'window.__figs.push({{ el: document.getElementById("{p}-fig"), name: "{name}", start: {x.r(start)}, opts: {_j.dumps(opts)}, path: {_j.dumps(path)}, leave: {"true" if c.get("leave", True) else "false"} }});')
    for k in path[1:]: x.sfx(k[0], c.get("move_sfx", "pro_hover_tick/soft"), -17)
    w = c.get("width", 700)
    cap = f'<div class="figcap mono">{esc(c.get("caption", ""))}</div>'
    read = '<div class="figread mono"></div>' if c.get("readout", True) else ""
    col = c.get("colors", {})
    style = "".join(f"--hairline-{k}:{v};" for k, v in col.items())
    return f'<div class="figwrap" style="width:{w}px;margin-left:{(1080 - w) // 2}px;{style}">{cap}<div id="{p}-fig" class="fig"></div>{read}</div>'

CARDS = dict(prompt=prompt, checklist=checklist, code=code, profile=profile, stat=stat, graph=graph, image=image, figure=figure)
