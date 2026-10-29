import os
"""Centre cards. Each card function gets (p, cfg, ctx): p is the unique id prefix, cfg the card's JSON,
ctx the scene context (timeline helpers, time resolver, sound cues). It returns the card's inner HTML and
pushes its own animation lines and sound cues. Times in cfg use the `at` grammar (see ctx.at)."""
import html as _h, re, sys
from core import icons as _icons

esc = lambda s: _h.escape(str(s))
_EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF]")

def ico(spec, size, color=None):
    """An icon from the library ("set:name", see core/icons.py) or a built-in line icon (ICONS key)."""
    if spec and ":" in spec: return _icons.svg(spec, size, color)
    return f'<svg viewBox="0 0 48 48" width="{size}" height="{size}">{ICONS.get(spec or "dot", ICONS["dot"])}</svg>'

def no_emoji(text, where):
    if _EMOJI.search(str(text)):
        print(f"    WARN {where}: emoji '{text}' used as an icon; use an icon from the library (python3 reel.py icons <word>)", file=sys.stderr)

# ------------------------------------------------------------------ prompt bar that types, then sends
def prompt(p, c, x):
    text = c.get("text", "make a reel")
    chars = "".join(f'<span class="ch">{esc(ch) if ch != " " else "&nbsp;"}</span>' for ch in text)
    tag = c.get("tag", "")
    t0 = x.at(c.get("type_at", "start+0.3")); send = x.at(c.get("send_at", "line:0:end-0.45"))
    step = min(0.045, max(0.015, (send - 0.15 - t0) / max(1, len(text))))
    for i in range(len(text)):
        x.A(f'tl.set("#{p} .ch:nth-child({i + 1})", {{ opacity: 1 }}, {x.r(t0 + i * step)});')
    x.typing(t0, len(text) * step)
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
        lo = x.lines[0]["start"]; hi = lo + (x.lines[-1]["end"] - 0.3 - lo) * 0.75   # all items in before the line ends
        times = [lo + (hi - lo) * i / max(1, n - 1) for i in range(n)]
    times = [x.at(it["at"]) if isinstance(it, dict) and "at" in it else t for it, t in zip(items, times)]
    rows = ""
    for i, (it, t) in enumerate(zip(items, times)):
        label = it["label"] if isinstance(it, dict) else it; icon = it.get("icon", "dot") if isinstance(it, dict) else "dot"
        col = it.get("color") if isinstance(it, dict) else None
        rows += f'''<div id="{p}-r{i}" class="row"><div class="ico">{ico(icon, 50 if ":" in icon else 56, col)}</div>
      <div class="rlabel" style="font-size:{min(50, round(440 / (max(1, len(label)) * 0.56)))}px">{esc(label)}</div><div class="rbar"><div id="{p}-f{i}" class="rfill"></div></div>
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
    if len(lines) == 1: x.typing(t0, 0.3, -16, "pro_typing_run/tick")
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
    x.A(f'tl.set("#{p}-btn", {{ backgroundColor: "{x.th["edge"]}" }}, {x.r(tap + 0.07)});')
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
    <g stroke="{x.th["grey"]}" stroke-width="2" opacity="0.6">{"".join(f'<path d="M{120 + i * 75},80 V520"/>' for i in range(9))}{"".join(f'<path d="M120,{80 + i * 55} H720"/>' for i in range(9))}</g>
    <path d="M120,60 V520 H740" stroke="{x.th["ink"]}" stroke-width="5" fill="none"/><path d="M110,72 L120,56 L130,72 M728,510 L744,520 L728,530" stroke="{x.th["ink"]}" stroke-width="5" fill="none"/>
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


# ------------------------------------------------------------------ social post (a real post you are quoting), [[phrase]] gets highlighted
def _marks(text, p, x, at):
    out, k = "", 0
    for i, part in enumerate(re.split(r"\[\[(.*?)\]\]", text)):
        if i % 2:
            out += f'<mark id="{p}-mk{k}">{esc(part)}</mark>'
            x.A(f'tl.to("#{p}-mk{k}", {{ backgroundSize: "100% 100%", duration: 0.35, ease: "power2.out" }}, {x.r(at + k * 0.25)});')
            x.sfx(at + k * 0.25, "pro_hover_tick/soft", -14); k += 1
        else: out += esc(part)
    return out
def post(p, c, x):
    body = _marks(c.get("text", ""), p, x, x.at(c.get("highlight_at", "line:1")))
    img = f'<div class="post-img"><img src="{esc(x.asset(c["image"]))}"/></div>' if c.get("image") else ""
    foot = "".join(f"<span>{esc(f)}</span>" if i else f"<span><b>{esc(f)}</b></span>" for i, f in enumerate(c.get("footer", [])))
    x.A(f'tl.to("#{p} .post", {{ y: -14, duration: {x.r(x.end - x.start)}, ease: "sine.inOut" }}, {x.r(x.start)});')
    who = f'<div class="post-u">{esc(c.get("handle", ""))}{" · " + esc(c["date"]) if c.get("date") else ""}</div>'
    return (f'<div class="post"><div class="post-h"><div class="post-av">{esc(c.get("name", "?")[:1])}</div><div><div class="post-n">{esc(c.get("name", ""))}</div>'
            f'{who}</div></div><div class="post-t">{body}</div>{img}<div class="post-f">{foot}</div></div>')

# ------------------------------------------------------------------ terminal: typed lines, a progress list that strikes items off, a done overlay
def _tline(s):
    s = esc(s)
    if s.startswith("$ "): return f'<span class="pr">$</span> {s[2:]}'
    if s.startswith("✓ "): return f'<span class="ok">✓</span> {s[2:]}'
    if s.startswith("# "): return f'<span class="dim">{s}</span>'
    return s
def terminal(p, c, x):
    lines = c.get("lines", []); t0 = x.at(c.get("type_at", "start+0.15")); step = c.get("line_step", 0.32)
    body = "".join(f'<div class="tl" id="{p}-l{i}">{_tline(l)}</div>' for i, l in enumerate(lines))
    for i in range(len(lines)):
        x.A(f'tl.fromTo("#{p}-l{i}", {{ opacity: 0, clipPath: "inset(0 100% 0 0)" }}, {{ opacity: 1, clipPath: "inset(0 0% 0 0)", duration: 0.22, ease: "none" }}, {x.r(t0 + i * step)});')
        if len(lines) == 1: x.typing(t0, 0.25, -16, "pro_typing_run/tick")
    pr = c.get("progress")
    if pr:
        ta = x.at(pr.get("at", "line:1")); items = pr.get("items", []); total = pr.get("total", len(items)); dur = pr.get("for", 2.0)
        ev = dur / max(1, len(items))
        body += f'<div id="{p}-pg" class="tprog"><span>{esc(pr.get("label", "Working"))}</span><b id="{p}-pn">0/{total}</b></div>'
        x.A(f'tl.to("#{p}-pg", {{ opacity: 1, duration: 0.15 }}, {x.r(ta)});')
        x.f.counters += 1; k = x.f.counters
        x.A(f'const cnt{k} = {{ v: 0 }}; tl.to(cnt{k}, {{ v: {total}, duration: {x.r(dur)}, ease: "none", onUpdate: () => {{ document.querySelector("#{p}-pn").textContent = Math.round(cnt{k}.v) + "/{total}"; }} }}, {x.r(ta)});')
        for i, it in enumerate(items):
            ti = ta + i * ev
            body += f'<div class="tpk" id="{p}-k{i}"><i>✕</i><s id="{p}-s{i}">{esc(it)}</s></div>'
            x.A(f'tl.fromTo("#{p}-k{i}", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.12 }}, {x.r(ti)});')
            x.A(f'tl.fromTo("#{p}-s{i}", {{ "--k": 0, color: "#e9e6df" }}, {{ "--k": 1, color: "#8d8a84", duration: 0.18 }}, {x.r(ti + 0.12)});')
            x.sfx(ti + 0.12, "pro_hover_tick/glass", -15)
        if pr.get("badge"):
            body += f'<div id="{p}-bd" class="tbadge">✓ {esc(pr["badge"])}</div>'
            x.A(f'tl.fromTo("#{p}-bd", {{ opacity: 0, scale: 0.5 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(3)" }}, {x.r(ta + dur + 0.05)});')
            x.sfx(ta + dur + 0.08, "pro_pop_in/round", -9)
    dn = c.get("done")
    if dn:
        td = x.at(dn.get("at", "line:1"))
        body += (f'<div id="{p}-dn" class="tdone"><div class="ck"><svg viewBox="0 0 40 40" width="100" height="100"><path d="M9,21 L17,29 L32,12" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
                 f'<div>{esc(dn.get("text", "Done"))}</div></div>')
        x.A(f'tl.fromTo("#{p}-dn", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.6)" }}, {x.r(td)});')
        x.A(f'tl.to("#{p} .tl, #{p} .tpk", {{ opacity: 0.25, duration: 0.25 }}, {x.r(td)});')
        x.sfx(td + 0.05, "pro_pop_in/round", -8)
    return f'<div class="term"><div class="dots3"><i></i><i></i><i></i><span class="mono">{esc(c.get("title", "terminal"))}</span></div>{body}</div>'

# ------------------------------------------------------------------ repository card: name, description ([[phrase]] highlighted), topics, a stats row
def repo(p, c, x):
    desc = _marks(c.get("description", ""), p, x, x.at(c.get("highlight_at", "line:1")))
    topics = "".join(f"<span>{esc(tp)}</span>" for tp in c.get("topics", []))
    stats = "".join(f"<span>{esc(s)}</span>" if i else f"<span><b>{esc(s)}</b></span>" for i, s in enumerate(c.get("stats", [])))
    icon = '<svg viewBox="0 0 24 24" width="40" height="40"><path d="M5,3 h12 a2,2 0 0 1 2,2 v14 h-12 a2,2 0 0 0 -2,2 z M5,19 a2,2 0 0 1 2,-2 h12" stroke="currentColor" stroke-width="2" fill="none"/></svg>'
    x.A(f'tl.fromTo("#{p} .repo-s span", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.25, stagger: 0.12 }}, {x.r(x.at(c.get("stats_at", "line:1")))});')
    return (f'<div class="repo"><div class="repo-n">{icon}<span>{esc(c.get("owner", ""))} / <b>{esc(c.get("name", ""))}</b></span><span class="pub">Public</span></div>'
            f'<div class="repo-d">{desc}</div><div class="repo-t">{topics}</div><div class="repo-s">{stats}</div></div>')

# ------------------------------------------------------------------ video clips (a product's own short clips) in an app window, one per beat
def _vidspan(src, t0, t1, L, ms, cls, x, style):
    out, tt, k = "", t0, 0
    while tt < t1 - 0.02:
        d = min(L - ms if k == 0 else L, t1 - tt)
        a = ms if k == 0 else 0
        x.f.vid_n = getattr(x.f, "vid_n", 0) + 1
        out += (f'<video id="cv{x.f.vid_n}" class="clip {cls}" src="{esc(src)}" muted playsinline data-start="{x.r(tt)}" data-duration="{x.r(d)}" '
                f'data-media-start="{x.r(a)}" data-track-index="{4 + x.f.vid_track}" style="{style}"></video>')
        x.f.vid_track = (x.f.vid_track + 1) % 6
        tt += d; k += 1
    return out
def _dur(path):
    import subprocess
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip() or 3)
def clips(p, c, x):
    """items: [{src, at, label, media_start}] -- each clip plays (looping) from its `at` until the next one."""
    x.f.uses_video = True
    its = c["items"]; ts = [x.at(it.get("at", "start" if i == 0 else f"line:{i}")) for i, it in enumerate(its)]
    h = c.get("height", 640); w = c.get("width", 820); zoom = c.get("zoom", 1.0)
    vids, pills = "", ""
    for i, it in enumerate(its):
        src = x.asset(it["src"]); full = src if os.path.isabs(it["src"]) else os.path.join(x.f.sdir, it["src"])
        t0 = max(x.start, ts[i] - 0.05); t1 = ts[i + 1] if i + 1 < len(its) else x.end + 0.4
        st = f"position:absolute;left:50%;top:50%;height:{100 * zoom}%;transform:translate(-50%,-50%)"
        vids += _vidspan(src, t0, t1, _dur(full), it.get("media_start", 0), "", x, st)
        if it.get("label"):
            pills += f'<div id="{p}-pl{i}" class="clipl mono"><i></i>{esc(it["label"])}</div>'
            x.A(f'tl.fromTo("#{p}-pl{i}", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.22, ease: "back.out(2)", immediateRender: false }}, {x.r(ts[i])});')
            if i + 1 < len(its): x.A(f'tl.to("#{p}-pl{i}", {{ opacity: 0, duration: 0.08 }}, {x.r(ts[i + 1] - 0.08)});')
            if i: x.sfx(ts[i], "pro_pop/round", -12)
    if c.get("url"):   # a browser bar: the address types in, then gets a red underline
        u = c["url"]; tu = x.at(c.get("url_at", "start+0.1")); per = 0.055
        chars = "".join(f'<span id="{p}-u{j}" style="opacity:0">{esc(ch)}</span>' for j, ch in enumerate(u))
        for j in range(len(u)): x.A(f'tl.set("#{p}-u{j}", {{ opacity: 1 }}, {x.r(tu + j * per)});')
        x.typing(tu, len(u) * per, -16, "pro_typing_run/tick")
        hl = x.at(c.get("url_hl", "line:1"))
        x.A(f'tl.fromTo("#{p}-ul", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.3, ease: "power3.out", immediateRender: false }}, {x.r(hl)});')
        x.A(f'tl.fromTo("#{p}-url", {{ scale: 1 }}, {{ scale: 1.08, duration: 0.25, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }}, {x.r(hl)});')
        x.sfx(hl, "pro_pop/tink", -11)
        title = (f'<div class="clipbar"><b></b><b></b><b></b><div id="{p}-url" class="urlbar mono"><i class="lk"></i>'
                 f'<span class="ut">{chars}<em id="{p}-ul" class="ul"></em></span></div></div>')
    else:
        title = f'<div class="clipbar"><b></b><b></b><b></b><span class="mono">{esc(c.get("title", ""))}</span></div>'
    tag = ""
    if c.get("tagline"):
        tag = f'<div id="{p}-tg" class="cliptag">{esc(c["tagline"])}{"<small class=mono>" + esc(c["sub"]) + "</small>" if c.get("sub") else ""}</div>'
        x.A(f'tl.fromTo("#{p}-tg", {{ opacity: 0, y: -20 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power3.out", immediateRender: false }}, {x.r(x.at(c.get("tagline_at", "start+0.3")))});')
    return f'<div class="clipwin" style="width:{w}px;margin-left:{(1080 - w) // 2}px">{title}<div class="clipin" style="height:{h}px">{vids}{tag}{pills}</div></div>'

# ------------------------------------------------------------------ lineup: a row of transparent character clips popping in
def lineup(p, c, x):
    x.f.uses_video = True
    its = c["items"]; n = len(its); h = c.get("height", 520); t0 = x.at(c.get("at", "start+0.15"))
    out = ""
    for i, it in enumerate(its):
        src = x.asset(it["src"]); full = src if os.path.isabs(it["src"]) else os.path.join(x.f.sdir, it["src"])
        t = t0 + i * c.get("step", 0.16)
        st = "position:absolute;left:0;bottom:0;width:100%;height:100%;object-fit:contain;object-position:50% 100%"
        v = _vidspan(src, x.start, x.end + 0.4, _dur(full), 0, "", x, st)
        tag = f'<div class="lutag mono{" free" if it.get("free") else ""}">{esc(it.get("tag", ""))}</div>' if it.get("tag") else ""
        out += f'<div id="{p}-c{i}" class="lucell" style="height:{h}px">{v}{tag}</div>'
        x.A(f'tl.fromTo("#{p}-c{i}", {{ opacity: 0, y: 60, scale: 0.8 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(2)", immediateRender: false }}, {x.r(t)});')
        x.sfx(t, "pro_pop/round", -15)
    if c.get("highlight") is not None:
        k = c["highlight"]; t = x.at(c.get("highlight_at", "line:1"))
        x.A(f'tl.fromTo("#{p}-c{k}", {{ scale: 1 }}, {{ scale: 1.12, duration: 0.3, ease: "back.out(3)", immediateRender: false }}, {x.r(t)});')
        x.A(f'tl.to("#{p} .lucell:not(#{p}-c{k})", {{ opacity: 0.35, duration: 0.25 }}, {x.r(t)});')
        x.sfx(t, "pro_pop/tink", -10)
    return f'<div class="lineup">{out}</div>'

# ------------------------------------------------------------------ insert: a full-frame clip made elsewhere (another skill's render), played once
def insert(p, c, x):
    x.f.uses_video = True
    src = x.asset(c["src"]); full = src if os.path.isabs(c["src"]) else os.path.join(x.f.sdir, c["src"])
    L = _dur(full); t0 = x.start; t1 = x.end + 0.3
    # zoom (crop around "origin", in source px) is baked into a copy with ffmpeg, so the clip stays sharp and the
    # page needs no transforms around the video
    z = c.get("zoom", 1)
    if z != 1:
        import subprocess
        o = c.get("origin", [540, 960]); w, h = round(1080 / z / 2) * 2, round(1920 / z / 2) * 2
        cx, cy = min(max(0, o[0] - w // 2), 1080 - w), min(max(0, o[1] - h // 2), 1920 - h)
        name = os.path.splitext(os.path.basename(src))[0] + f"-z{int(z * 100)}.mp4"; out = os.path.join(x.f.out, "assets", name)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", full, "-vf", f"crop={w}:{h}:{cx}:{cy},scale=1080:1920:flags=lanczos",
                        "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", "-an", out], check=True)
        src = "assets/" + name
    st = "position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover"
    return f'<div class="insert">{_vidspan(src, t0, t1, L, c.get("media_start", 0), "", x, st)}</div>'

# ------------------------------------------------------------------ kinetic: full-frame type pages in the paper UI (word slams, number pages)
def kinetic(p, c, x):
    """pages: [{at, word, sub, label, icon, accent}] or [{at, number, from, suffix, sub, accent}]. Intro slides in the
    video's own look: the theme background (paper + dots, and the red glow in dark), the caption font, and the accent
    as the same red selection box the captions use (`"accent": true`, or the old `"bg": "accent"`). Words blur-build in
    like captions; each page blurs out as the next arrives. No sound on the accent box (the house rule for red words).
    `icon`: "set:name" from the icon library, shown above the word. Use with "layout": "none" and "captions": "off"."""
    out = ""; th = x.th; pages = c["pages"]; dark = th["paper"].lower() in ("#0b0b0b", "#000000")
    glow = (f'<div class="kglow" style="background:radial-gradient(circle, {th["accent"]}59 0%, {th["accent"]}26 32%, transparent 68%)"></div>'
            if dark and c.get("glow", True) else "")
    ts = [x.at(pg.get("at", "start+0.1")) for pg in pages]
    for i, pg in enumerate(pages):
        t = ts[i]; q = f"{p}-pg{i}"; acc = pg.get("accent") or pg.get("bg") == "accent"
        if "number" in pg:
            txt = f'{pg["number"]}{pg.get("suffix", "")}'
            inner = f'<span id="{q}-n">{pg.get("from", 0)}</span><small>{esc(pg.get("suffix", ""))}</small>'
            x.count(f"#{q}-n", pg.get("from", 0), pg["number"], t - 0.5, 0.5)
            for k in range(5): x.sfx(t - 0.5 + k * 0.1, "pro_hover_tick/soft", -21)
        else:
            txt = pg["word"]; inner = esc(txt)
        n = max(3, len(txt)); fs = min(250 if acc else 270, round((860 if acc else 960) / (n * 0.56)))
        if acc:   # the caption selection box: translucent red bar with a red border, handles with round knobs
            main = (f'<span class="ksel"><b class="kselbg"></b><i class="khd khl"></i><i class="khd khr"></i>'
                    f'<span class="ksw">{inner}</span></span>')
            x.A(f'tl.fromTo("#{q} .kselbg", {{ scaleX: 0, opacity: 1 }}, {{ scaleX: 1, duration: 0.3, ease: "power3.out", immediateRender: false }}, {x.r(t)});')
            x.A(f'tl.fromTo("#{q} .khl", {{ scaleY: 0, opacity: 1 }}, {{ scaleY: 1, duration: 0.22, ease: "back.out(2.5)", immediateRender: false }}, {x.r(t)});')
            x.A(f'tl.fromTo("#{q} .khr", {{ scaleY: 0, opacity: 1 }}, {{ scaleY: 1, duration: 0.22, ease: "back.out(2.5)", immediateRender: false }}, {x.r(t + 0.24)});')
        else:
            main = inner; x.sfx(t, "cut_hit/kick", -14)
        x.A(f'tl.fromTo("#{q} .kmain", {{ opacity: 0, y: 34, scale: () => 1.08 * kfit("#{q} .kmain"), filter: "blur(14px)" }}, {{ opacity: 1, y: 0, scale: () => kfit("#{q} .kmain"), filter: "blur(0px)", duration: 0.34, ease: "power3.out", immediateRender: false }}, {x.r(t)});')
        lab = f'<div class="klab mono"><i></i>{esc(pg["label"])}</div>' if pg.get("label") else ""
        icn = f'<div class="kicon">{ico(pg["icon"], 170, pg.get("color", th["ink"]))}</div>' if pg.get("icon") else ""
        sub = f'<div class="ksub"><span>{esc(pg["sub"])}</span></div>' if pg.get("sub") else ""
        out += (f'<div id="{q}" class="kpage">{icn}{lab}<div class="kmain{" kacc" if acc else ""}" style="font-size:{fs}px">{main}</div>{sub}</div>')
        x.A(f'tl.set("#{q}", {{ opacity: 1 }}, {x.r(t - 0.02 if i else x.start)});')
        if pg.get("icon"):
            x.A(f'tl.fromTo("#{q} .kicon", {{ opacity: 0, scale: 0.5, y: 30 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.36, ease: "back.out(2.2)", immediateRender: false }}, {x.r(t - 0.12)});')
        if pg.get("sub"): x.A(f'tl.fromTo("#{q} .ksub span", {{ opacity: 0, y: 26, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.3, ease: "power3.out", immediateRender: false }}, {x.r(t + 0.2)});')
        if pg.get("label"): x.A(f'tl.fromTo("#{q} .klab", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.25, ease: "power3.out", immediateRender: false }}, {x.r(t + 0.3)});')
        if i + 1 < len(pages):   # blur out just before the next page
            x.A(f'tl.to("#{q}", {{ opacity: 0, filter: "blur(12px)", scale: 0.96, duration: 0.14, ease: "power2.in" }}, {x.r(ts[i + 1] - 0.16)});')
    return f'<div class="kin">{glow}{out}</div>'

# ------------------------------------------------------------------ flow: how something works, as nodes joined by arrows with a signal running along
def flow(p, c, x):
    """nodes: [{label, img | glyph, at}] in a row; arrows draw in before each node; `signal_at` sends a red dot along
    every arrow in turn (a ping on each node); `bubble`: {text, at} pops a speech bubble over the last node."""
    nodes = c["nodes"]; n = len(nodes); out = ""; th = x.th
    nw, gap = c.get("node", 250), c.get("gap", 70); W0 = n * nw + (n - 1) * gap; x0 = (1080 - W0) // 2
    ts = [x.at(nd.get("at", "start+0.1" if i == 0 else f"line:{min(i, len(x.lines) - 1)}")) for i, nd in enumerate(nodes)]
    for i, nd in enumerate(nodes):
        left = x0 + i * (nw + gap); q = f"{p}-n{i}"
        if nd.get("img"): face = f'<img src="{esc(x.asset(nd["img"]))}" style="width:100%;height:100%;object-fit:contain"/>'
        elif nd.get("svg"): face = nd["svg"]   # inline drawing (trusted: written in the script)
        elif nd.get("icon"): face = f'<div class="ficon">{ico(nd["icon"], round(nw * 0.5), nd.get("color"))}</div>'
        else:
            no_emoji(nd.get("glyph", ""), "flow node"); face = f'<div class="fglyph mono">{esc(nd.get("glyph", "•"))}</div>'
        out += (f'<div id="{q}" class="fnode{" hot" if nd.get("hot") else ""}" style="left:{left}px;width:{nw}px">'
                f'<div class="fface" style="height:{nw}px">{face}</div><div class="flab">{esc(nd["label"])}</div></div>')
        x.A(f'tl.fromTo("#{q}", {{ opacity: 0, scale: 0.6, y: 40 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.36, ease: "back.out(2.2)", immediateRender: false }}, {x.r(ts[i])});')
        x.sfx(ts[i], "pro_pop_in/round", -14)
        if i:
            ax = left - gap + 8; aw = gap - 16; a = f"{p}-a{i}"
            out += (f'<svg id="{a}" class="farrow" style="left:{ax}px;top:{nw // 2 - 20}px" width="{aw}" height="40" viewBox="0 0 {aw} 40">'
                    f'<path d="M2 20 H{aw - 14}" stroke="{th["ink"]}" stroke-width="6" stroke-linecap="round" fill="none" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
                    f'<path d="M{aw - 20} 9 L{aw - 4} 20 L{aw - 20} 31" stroke="{th["ink"]}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0"/></svg>')
            x.A(f'tl.to("#{a} path:first-child", {{ strokeDashoffset: 0, duration: 0.22, ease: "power2.out" }}, {x.r(ts[i] - 0.25)});')
            x.A(f'tl.set("#{a} path:last-child", {{ opacity: 1 }}, {x.r(ts[i] - 0.05)});')
            x.sfx(ts[i] - 0.25, "swipe/flick", -19)
    if c.get("signal_at"):
        t = x.at(c["signal_at"]); dot = f"{p}-sig"; out += f'<i id="{dot}" class="fsig"></i>'
        for i in range(1, n):
            xa = x0 + (i - 1) * (nw + gap) + nw - 10; xb = x0 + i * (nw + gap) + 10; tt = t + (i - 1) * 0.42
            x.A(f'tl.fromTo("#{dot}", {{ opacity: 1, x: {xa}, y: {nw // 2 - 14} }}, {{ x: {xb}, duration: 0.3, ease: "power2.inOut", immediateRender: false }}, {x.r(tt)});')
            x.A(f'tl.fromTo("#{p}-n{i} .fface", {{ boxShadow: "0 0 0 0px {th["accent"]}" }}, {{ boxShadow: "0 0 0 10px {th["accent"]}", duration: 0.12, yoyo: true, repeat: 1, immediateRender: false }}, {x.r(tt + 0.3)});')
            x.sfx(tt + 0.3, "pro_hover_tick/ping", -13)
        x.A(f'tl.set("#{dot}", {{ opacity: 0 }}, {x.r(t + (n - 1) * 0.42)});')
    if c.get("bubble"):
        b = c["bubble"]; t = x.at(b.get("at", "line:2")); right = 1080 - (x0 + n * nw + (n - 1) * gap)   # right-aligned to the last node
        out += f'<div id="{p}-bub" class="fbub mono" style="right:{right}px">{esc(b["text"])}</div>'
        x.A(f'tl.fromTo("#{p}-bub", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.6)", immediateRender: false }}, {x.r(t)});')
        x.sfx(t, "pro_pop/bloop", -12)
    return f'<div class="flow" style="height:{nw + 90}px">{out}</div>'

CARDS = dict(prompt=prompt, checklist=checklist, code=code, profile=profile, stat=stat, graph=graph, image=image, figure=figure, post=post, terminal=terminal, repo=repo, clips=clips, lineup=lineup, insert=insert, kinetic=kinetic, flow=flow)
