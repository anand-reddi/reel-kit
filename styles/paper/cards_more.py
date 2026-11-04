"""More centre cards for the paper style (dark and light themes), added for the Lemo-Opuscar reel so reels stop
reusing the same few visuals. Each one has its own sound set. Same contract as cards.py: card(p, cfg, ctx) -> HTML,
animation lines pushed with ctx.A, sounds with ctx.sfx. Times use the `at` grammar.

  spotlight  a real screenshot dimmed, a spotlight glides to each region, a label pin lands beside it (repos, docs)
  tiles      2-4 big icon tiles that flip on, one per spoken word; a code bar sweeps under them ("story, music, voice")
  filmstrip  a film strip of stills or clips runs through a gate; the strip scrubs, a counter ticks (montages, eras)
  wall       a contact-sheet image cut into tiles that land on a tilted wall, a big counter on top ("66 styles")
  polaroid   clips or images drop as tilted instant photos with a written label, one per cue (named examples)
  promptplay a prompt types and sends, a build bar ticks its steps, then the result plays in a frame (input -> output)
  dial       a ring gauge sweeps to a value; centre number, unit, note and an optional badge (time, cost, score)
  stack      2-3 media panels stacked with label pills, popping in on cue (use cases, before/after/after)
  copycmd    commands in chips with a copy button; a finger taps it, a "Copied" toast lands (install steps)
"""
import os, random
from .cards import CARDS, esc, ico, _vidspan, _dur, _spread

VIDEO = (".mp4", ".webm", ".mov", ".m4v")

def _media(x, src, t0, t1, style, ms=0):
    """An image or a video (a video plays from t0 to t1, looping) with the given inline style."""
    a = x.asset(src)
    if src.lower().endswith(VIDEO):
        x.f.uses_video = True
        full = src if os.path.isabs(src) else os.path.join(x.f.sdir, src)
        return _vidspan(a, t0, t1, _dur(full), ms, "", x, style)
    return f'<img src="{esc(a)}" style="{style}"/>'

def _size(x, src):
    from PIL import Image
    return Image.open(os.path.join(x.f.out, x.asset(src))).size

# ------------------------------------------------------------------ spotlight: screenshot, spotlight + label pins
def spotlight(p, c, x):
    """src (image), width (960), height (view px, default fits up to 800), dim (0.74),
    focus: [{at, x, y, w, h (% of the image), label, zoom (default 1.6), side: below|above}], reset_at."""
    W = c.get("width", 960); iw, ih = _size(x, c["src"]); SH = W * ih / iw; VH = c.get("height", min(SH, 800))
    c.setdefault("scale", 1.0); src = x.asset(c["src"]); left = (1080 - W) / 2; dim = c.get("dim", 0.84)
    x.A(f'tl.fromTo("#{p}-fr", {{ opacity: 0, y: 70, rotation: -2 }}, {{ opacity: 1, y: 0, rotation: 0, duration: 0.45, ease: "back.out(1.4)" }}, {x.r(x.start)});')
    x.sfx(x.start + 0.05, "swipe/paper", -15)
    pins = ""
    for i, f in enumerate(c.get("focus", [])):
        t = x.at(f.get("at", "start+0.4"))
        rx, ry, rw, rh = (f[k] / 100 for k in ("x", "y", "w", "h"))
        cx, cy = (rx + rw / 2) * W, (ry + rh / 2) * SH
        k = max(1.0, min(f.get("zoom", 1.6), 0.9 * W / (rw * W), 0.8 * VH / (rh * SH)))
        tx = min(0, max(W - k * W, W / 2 - k * cx)); ty = min(0, max(VH - k * SH, VH / 2 - k * cy)) if k * SH > VH else 0
        # spotlight in image px (the overlay sits inside the camera, so it zooms with the image)
        ex, ey = rw * W / 2 + 26, rh * SH / 2 + 22
        x.A(f'tl.to("#{p}-cam", {{ x: {tx:.1f}, y: {ty:.1f}, scale: {k:.3f}, duration: 0.7, ease: "power3.inOut", transformOrigin: "0px 0px" }}, {x.r(t - 0.3)});')
        x.A(f'tl.to("#{p}-dim", {{ "--cx": "{cx:.0f}px", "--cy": "{cy:.0f}px", "--rx": "{ex:.0f}px", "--ry": "{ey:.0f}px", "--d": {dim}, duration: 0.6, ease: "power3.inOut" }}, {x.r(t - 0.25)});')
        x.sfx(t - 0.25, "whoosh_fast/sleeve", -17); x.sfx(t + 0.05, "tap/glass", -13)
        if f.get("label"):   # the pin sits under (or above) the region as it appears after the zoom, in frame px
            sx, sy0, sy1 = tx + k * cx, ty + k * ry * SH, ty + k * (ry + rh) * SH
            above = f.get("side") == "above" or sy1 + 90 > VH
            py = (sy0 - 78) if above else (sy1 + 18)
            pins += (f'<div id="{p}-pin{i}" class="spin" style="left:{min(max(sx, 170), W - 170):.0f}px;top:{max(8, py):.0f}px">'
                     f'<i></i>{esc(f["label"])}</div>')
            x.A(f'tl.fromTo("#{p}-pin{i}", {{ opacity: 0, y: {(-1 if not above else 1) * 18}, scale: 0.7 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(2.2)", immediateRender: false }}, {x.r(t + 0.35)});')
            x.sfx(t + 0.38, "mallet/marimba", -15)
            nxt = c["focus"][i + 1] if i + 1 < len(c["focus"]) else None
            if nxt: x.A(f'tl.to("#{p}-pin{i}", {{ opacity: 0, duration: 0.15 }}, {x.r(x.at(nxt.get("at")) - 0.35)});')
    if c.get("reset_at"):
        t = x.at(c["reset_at"])
        x.A(f'tl.to("#{p}-cam", {{ x: 0, y: 0, scale: 1, duration: 0.6, ease: "power3.inOut" }}, {x.r(t)});')
        x.A(f'tl.to("#{p}-dim", {{ "--d": 0, duration: 0.4 }}, {x.r(t)});')
        x.A(f'tl.to("#{p} .spin", {{ opacity: 0, duration: 0.15 }}, {x.r(t)});')
    return (f'<div id="{p}-fr" class="spfr" style="left:{left:.0f}px;width:{W}px;height:{VH:.0f}px">'
            f'<div id="{p}-cam" class="spcam" style="width:{W}px;height:{SH:.0f}px"><img src="{esc(src)}"/>'
            f'<div id="{p}-dim" class="spdim"></div></div>{pins}</div>')

# ------------------------------------------------------------------ tiles: icon tiles flipping on per word, a code bar under them
def tiles(p, c, x):
    """items: [{label, icon, at}] (2-4, a 2x2 grid for 3-4), bar: {text, at} (a mono bar that sweeps in under them),
    title (small mono label above)."""
    its = c["items"][:4]; n = len(its); ts = _spread(x, n, "line:0", c.get("until"))
    ts = [x.at(it["at"]) if "at" in it else t for it, t in zip(its, ts)]
    cols = 2 if n >= 3 else n; tw = 400; th = 300 if n >= 3 else 360; gap = 28
    W = cols * tw + (cols - 1) * gap; left = (1080 - W) / 2
    out = f'<div class="tlttl mono" style="left:{left:.0f}px">{esc(c.get("title", ""))}</div>' if c.get("title") else ""
    for i, (it, t) in enumerate(zip(its, ts)):
        r, q = divmod(i, cols); xx = left + q * (tw + gap); yy = 60 + r * (th + gap)
        out += (f'<div id="{p}-t{i}" class="tile" style="left:{xx:.0f}px;top:{yy}px;width:{tw}px;height:{th}px">'
                f'<div class="tic">{ico(it.get("icon", "dot"), 110)}</div><div class="tlab">{esc(it["label"])}</div>'
                f'<em class="tnum mono">{i + 1:02d}</em></div>')
        x.A(f'tl.fromTo("#{p}-t{i}", {{ rotationY: -95, opacity: 0.25 }}, {{ rotationY: 0, opacity: 1, duration: 0.42, ease: "back.out(1.6)", immediateRender: false }}, {x.r(t - 0.12)});')
        x.A(f'tl.set("#{p}-t{i}", {{ className: "tile on" }}, {x.r(t + 0.1)});')
        x.A(f'tl.fromTo("#{p}-t{i} .tic", {{ scale: 0.5 }}, {{ scale: 1, duration: 0.4, ease: "back.out(3)", immediateRender: false }}, {x.r(t)});')
        x.sfx(t - 0.06, "toggle/on", -13)
    b = c.get("bar")
    if b:
        tb = x.at(b.get("at", "line:1")); rows = (n + cols - 1) // cols; by = 60 + rows * (th + gap) + 10
        out += f'<div id="{p}-bar" class="tbar mono" style="left:{left:.0f}px;width:{W}px;top:{by}px"><b>&lt;/&gt;</b><span>{esc(b["text"])}</span></div>'
        x.A(f'tl.fromTo("#{p}-bar", {{ clipPath: "inset(0 100% 0 0)", opacity: 1 }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.45, ease: "power3.out", immediateRender: false }}, {x.r(tb - 0.1)});')
        x.A(f'tl.fromTo("#{p} .tile", {{ borderColor: "{x.th["edge"]}" }}, {{ borderColor: "{x.th["accent"]}", duration: 0.2, stagger: 0.05, immediateRender: false }}, {x.r(tb)});')
        x.sfx(tb - 0.1, "pro_zip/up", -14); x.sfx(tb + 0.3, "shimmer/m2", -17)
    return f'<div class="tiles" style="perspective:1400px">{out}</div>'

# ------------------------------------------------------------------ filmstrip: a strip runs through a gate
def filmstrip(p, c, x):
    """items: [{src (image or clip), label, sub}] (stills or clips), at / until (when the strip runs), counter:
    {to, from, label} (a number ticking with the strip), title. The strip slides frame to frame (eased steps)
    and the frame in the gate is lit; the rest sit dimmed."""
    c.setdefault("scale", 1.0)
    its = c["items"]; n = len(its); fw, fh, gap = 700, 394, 34; step = fw + gap
    ts = _spread(x, n, c.get("at", "start+0.3"), c.get("until"))
    frames = ""
    for i, it in enumerate(its):
        st = "position:absolute;inset:0;width:100%;height:100%;object-fit:cover"
        m = _media(x, it["src"], x.start, x.end + 0.4, st)
        lab = (f'<div class="fslab"><b>{esc(it["label"])}</b>{"<span>" + esc(it["sub"]) + "</span>" if it.get("sub") else ""}</div>') if it.get("label") else ""
        frames += f'<div id="{p}-f{i}" class="fsf" style="left:{i * step}px;width:{fw}px;height:{fh}px">{m}{lab}</div>'
    holes = "".join(f'<i style="left:{k * 44}px"></i>' for k in range(int((n * step + 1200) / 44)))
    base = (1080 - fw) / 2
    x.A(f'tl.set("#{p}-reel", {{ x: {base:.0f} }}, {x.r(x.start)});')
    x.A(f'tl.set("#{p}-f0", {{ className: "fsf on" }}, {x.r(x.start)});')
    for i in range(1, n):
        t = ts[i]; d = min(0.35, max(0.12, (ts[i] - ts[i - 1]) * 0.7))
        x.A(f'tl.to("#{p}-reel", {{ x: {base - i * step:.0f}, duration: {d:.2f}, ease: "power3.inOut" }}, {x.r(t - d)});')
        x.A(f'tl.set("#{p}-f{i - 1}", {{ className: "fsf" }}, {x.r(t - d / 2)}); tl.set("#{p}-f{i}", {{ className: "fsf on" }}, {x.r(t - d / 2)});')
        x.sfx(t - d * 0.6, "shutter/film" if i % 3 == 0 else "fit/tick/domino", -16 if i % 3 else -14)
    cnt = c.get("counter")
    hud = ""
    if cnt:
        hud = (f'<div class="fshud"><span class="mono">{esc(cnt.get("label", ""))}</span><b id="{p}-n">{cnt.get("from", 1)}</b>'
               f'<small>/ {cnt["to"]}</small></div>')
        x.count(f"#{p}-n", cnt.get("from", 1), cnt["to"], ts[0], max(0.5, ts[-1] - ts[0]))
        x.sfx(ts[-1] + 0.05, "notify/mid_tine", -13)
    ttl = f'<div class="fsttl mono">{esc(c.get("title", ""))}</div>' if c.get("title") else ""
    x.A(f'tl.fromTo("#{p}-strip", {{ opacity: 0, scaleY: 0.6 }}, {{ opacity: 1, scaleY: 1, duration: 0.35, ease: "power3.out" }}, {x.r(x.start)});')
    x.sfx(x.start + 0.02, "pro_whoosh_big/tonal", -18)
    return (f'{ttl}<div id="{p}-strip" class="fstrip"><div class="fsh top">{holes}</div><div class="fsh bot">{holes}</div>'
            f'<div id="{p}-reel" class="fsreel">{frames}</div><div class="fsgate" style="left:{base - 8:.0f}px;width:{fw + 16}px;height:{fh + 16}px"></div></div>{hud}')

# ------------------------------------------------------------------ wall: contact-sheet tiles landing on a tilted wall + a counter
def wall(p, c, x):
    """src (a contact-sheet image), grid: [cols, rows] of the source sheet, show: columns on the wall (6),
    count: {to, label, at}, land: [from, until] (when the tiles land), tilt (deg, 16), skip: [tile indexes to leave out]."""
    c.setdefault("scale", 1.0)
    sc_, sr = c["grid"]; iw, ih = _size(x, c["src"]); src = x.asset(c["src"])
    skip = set(c.get("skip", [])); idx = [k for k in range(sc_ * sr) if k not in skip]
    cols = c.get("show", 6); tw = 1180 / cols; th_ = tw * (ih / sr) / (iw / sc_); rows = (len(idx) + cols - 1) // cols
    t0 = x.at(c.get("land", ["start+0.1"])[0]); t1 = x.at(c["land"][1]) if len(c.get("land", [])) > 1 else min(x.end - 0.6, t0 + 1.6)
    rnd = random.Random(7); order = list(range(len(idx))); rnd.shuffle(order)
    tiles_ = ""
    for j, k in enumerate(idx):
        r, q = divmod(j, cols); sx, sy = k % sc_, k // sc_
        tiles_ += (f'<div id="{p}-w{j}" class="wtile" style="left:{q * tw:.1f}px;top:{r * th_:.1f}px;width:{tw - 6:.1f}px;height:{th_ - 6:.1f}px;'
                   f'background-image:url({esc(src)});background-size:{sc_ * 100}% {sr * 100}%;background-position:{sx * 100 / max(1, sc_ - 1):.3f}% {sy * 100 / max(1, sr - 1):.3f}%"></div>')
    for rank, j in enumerate(order):
        t = t0 + (t1 - t0) * rank / max(1, len(order) - 1)
        x.A(f'tl.fromTo("#{p}-w{j}", {{ opacity: 0, scale: 1.8, z: 300 }}, {{ opacity: 1, scale: 1, z: 0, duration: 0.25, ease: "power3.out", immediateRender: false }}, {x.r(t)});')
        if rank % 6 == 0: x.sfx(t + 0.2, "pro_hover_tick/glass", -20)
    H = rows * th_; tilt = c.get("tilt", 16)
    x.A(f'tl.fromTo("#{p}-wall", {{ y: 80 }}, {{ y: {-(H - 700) * 0.6 - 60:.0f}, duration: {x.r(max(1, x.end - x.start))}, ease: "none" }}, {x.r(x.start)});')
    cn = c.get("count"); badge = ""
    if cn:
        ta = x.at(cn.get("at", "line:0"))
        badge = f'<div id="{p}-bd" class="wbadge"><b id="{p}-wn">0</b><span>{esc(cn.get("label", ""))}</span></div>'
        x.count(f"#{p}-wn", 0, cn["to"], ta - 0.6, 0.6)
        x.A(f'tl.fromTo("#{p}-bd", {{ opacity: 0, scale: 0.4, rotation: -8 }}, {{ opacity: 1, scale: 1, rotation: -3, duration: 0.4, ease: "back.out(2.5)", immediateRender: false }}, {x.r(ta - 0.65)});')
        x.sfx(ta - 0.6, "pro_riser/nblips", -16); x.sfx(ta, "pro_impact/air", -12)
    return (f'<div class="wview"><div style="position:absolute;left:{(1080 - 1180) / 2:.0f}px;top:0;width:1180px;transform:perspective(1600px) rotateX({tilt}deg) rotateZ(-4deg);transform-origin:50% 0">'
            f'<div id="{p}-wall" class="wwall" style="height:{H:.0f}px">{tiles_}</div></div></div>{badge}')

# ------------------------------------------------------------------ polaroid: instant photos dropping onto a pile
def polaroid(p, c, x):
    """items: [{src (image or clip), label, at}] (2-5). Each drops in on its cue, tilted, the newest on top;
    the label is written in the white strip."""
    c.setdefault("scale", 1.0)
    its = c["items"]; n = len(its); ts = _spread(x, n, "line:0", c.get("until"))
    ts = [x.at(it["at"]) if "at" in it else t for it, t in zip(its, ts)]
    rot = [-7, 5, -3, 8, -5]; dx = [-150, 120, -60, 160, -110]; dy = [0, 70, 150, 40, 120]
    out = ""
    for i, (it, t) in enumerate(zip(its, ts)):
        st = "position:absolute;inset:0;width:100%;height:100%;object-fit:cover"
        m = _media(x, it["src"], t - 0.1, x.end + 0.4, st)
        out += (f'<div id="{p}-p{i}" class="pola" style="left:{540 - 290 + dx[i % 5]}px;top:{40 + dy[i % 5]}px;z-index:{i + 1}">'
                f'<div class="polimg">{m}</div><div class="polcap">{esc(it.get("label", ""))}</div></div>')
        x.A(f'tl.fromTo("#{p}-p{i}", {{ opacity: 0, y: -700, rotation: {rot[i % 5] * 4}, scale: 1.15 }}, {{ opacity: 1, y: 0, rotation: {rot[i % 5]}, scale: 1, duration: 0.42, ease: "back.out(1.3)", immediateRender: false }}, {x.r(t - 0.3)});')
        x.sfx(t - 0.3, "swipe/flick", -15); x.sfx(t + 0.08, "knock/desk", -12)
        if i: x.A(f'tl.to("#{p}-p{i - 1}", {{ filter: "brightness(0.55)", duration: 0.25 }}, {x.r(t)});')
    return f'<div class="polas">{out}</div>'

# ------------------------------------------------------------------ promptplay: prompt -> build steps -> result in a frame
def promptplay(p, c, x):
    """text (the prompt), label (small mono label), send_at, steps: [{label, at}] (a build bar ticking each one),
    result: {src (clip/image), title, at}."""
    c.setdefault("scale", 1.0)
    text = c["text"]; t0 = x.at(c.get("type_at", "start+0.3")); send = x.at(c.get("send_at", "line:0:end"))
    per = min(0.05, max(0.02, (send - 0.2 - t0) / max(1, len(text))))
    chars = "".join(f'<span id="{p}-c{i}" style="opacity:0">{esc(ch) if ch != " " else "&nbsp;"}</span>' for i, ch in enumerate(text))
    for i in range(len(text)): x.A(f'tl.set("#{p}-c{i}", {{ opacity: 1 }}, {x.r(t0 + i * per)});')
    x.typing(t0, len(text) * per, -15, "pro_typing_run/glass")
    x.A(f'tl.fromTo("#{p}-go", {{ scale: 1 }}, {{ scale: 0.8, backgroundColor: "{x.th["accent"]}", duration: 0.1, yoyo: true, repeat: 1, immediateRender: false }}, {x.r(send)});')
    x.sfx(send, "toggle/on", -11)
    x.A(f'tl.to("#{p}-bar", {{ y: -40, scale: 0.86, duration: 0.4, ease: "power3.inOut" }}, {x.r(send + 0.15)});')
    steps = c.get("steps", []); ss = ""
    for i, s_ in enumerate(steps):
        ts_ = x.at(s_.get("at", f"line:{i}"))
        ss += f'<div id="{p}-s{i}" class="ppst"><i></i><span>{esc(s_["label"])}</span></div>'
        x.A(f'tl.fromTo("#{p}-s{i}", {{ opacity: 0.25 }}, {{ opacity: 1, duration: 0.15, immediateRender: false }}, {x.r(ts_)});')
        x.A(f'tl.set("#{p}-s{i}", {{ className: "ppst on" }}, {x.r(ts_)});')
        x.sfx(ts_, "ui_pop/step", -15)
    if steps:
        a, b = x.at(steps[0].get("at", "line:0")), x.at(steps[-1].get("at", "line:0"))
        x.A(f'tl.fromTo("#{p}-steps", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power3.out", immediateRender: false }}, {x.r(send + 0.3)});')
        x.A(f'tl.fromTo("#{p}-prog", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {x.r(max(0.4, b - send))}, ease: "none", immediateRender: false }}, {x.r(send + 0.3)});')
        x.sfx(send + 0.3, "pro_riser/nblips", -19)
    r = c.get("result"); res = ""
    if r:
        tr = x.at(r.get("at", "end-2"))
        st = "position:absolute;inset:0;width:100%;height:100%;object-fit:cover"
        m = _media(x, r["src"], tr - 0.1, x.end + 0.4, st)
        res = (f'<div id="{p}-res" class="ppres"><div class="pprbar mono"><b></b><b></b><b></b><span>{esc(r.get("title", ""))}</span></div>'
               f'<div class="pprin">{m}</div></div>')
        x.A(f'tl.fromTo("#{p}-res", {{ opacity: 0, scale: 0.6, y: 120 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.45, ease: "back.out(1.5)", immediateRender: false }}, {x.r(tr - 0.2)});')
        x.sfx(tr - 0.2, "logo_sting/spark", -15)
    return (f'<div id="{p}-bar" class="ppbar"><div class="pplab mono">{esc(c.get("label", ""))}</div>'
            f'<div class="ppin"><span class="pr">&gt;</span><span class="ppt">{chars}</span><b id="{p}-go" class="ppgo">↑</b></div></div>'
            f'<div id="{p}-steps" class="ppsteps"><div class="ppprog"><b id="{p}-prog"></b></div>{ss}</div>{res}')

# ------------------------------------------------------------------ dial: a ring gauge
def dial(p, c, x):
    """value (0-100 of the ring), number (text shown, counts if numeric), unit, note, badge: {text, at}, at, title."""
    t = x.at(c.get("at", "line:0+0.2")); R = 230; L = 2 * 3.14159 * R; v = c.get("value", 60) / 100
    num = c.get("number", c.get("value", 60))
    x.A(f'tl.fromTo("#{p}-arc", {{ strokeDashoffset: {L:.1f} }}, {{ strokeDashoffset: {L * (1 - v):.1f}, duration: 1.1, ease: "power2.out", immediateRender: false }}, {x.r(t)});')
    x.A(f'tl.fromTo("#{p}-dot", {{ rotation: -90 }}, {{ rotation: {-90 + 360 * v:.1f}, duration: 1.1, ease: "power2.out", transformOrigin: "260px 260px", immediateRender: false }}, {x.r(t)});')
    x.sfx(t, "pro_riser/roll", -18); x.sfx(t + 1.05, "notify/mid_tine", -13)
    if isinstance(num, (int, float)): x.count(f"#{p}-num", 0, num, t, 1.1)
    ticks = "".join(f'<line x1="260" y1="{260 - R - 34}" x2="260" y2="{260 - R - (46 if k % 5 == 0 else 40)}" transform="rotate({k * 6} 260 260)"/>' for k in range(60))
    bd = c.get("badge"); badge = ""
    if bd:
        tb = x.at(bd.get("at", "line:2"))
        badge = f'<div id="{p}-bd" class="dbadge">{esc(bd["text"])}</div>'
        x.A(f'tl.fromTo("#{p}-bd", {{ opacity: 0, scale: 2.2, rotation: 12 }}, {{ opacity: 1, scale: 1, rotation: 6, duration: 0.2, ease: "power4.in", immediateRender: false }}, {x.r(tb - 0.2)});')
        x.sfx(tb, "cut_hit/kick", -12); x.shake(tb, 8)
    ttl = f'<div class="dttl mono">{esc(c["title"])}</div>' if c.get("title") else ""
    return (f'<div class="dial">{ttl}<svg viewBox="0 0 520 520" width="520" height="520">'
            f'<g class="dtk">{ticks}</g><circle cx="260" cy="260" r="{R}" class="dtrack"/>'
            f'<circle id="{p}-arc" cx="260" cy="260" r="{R}" class="darc" style="stroke-dasharray:{L:.1f};stroke-dashoffset:{L:.1f}" transform="rotate(-90 260 260)"/>'
            f'<g id="{p}-dot"><circle cx="{260 + R}" cy="260" r="16" class="ddot"/></g></svg>'
            f'<div class="dmid"><b id="{p}-num">{esc(num)}</b><span>{esc(c.get("unit", ""))}</span><em>{esc(c.get("note", ""))}</em></div>{badge}</div>')

# ------------------------------------------------------------------ stack: media panels stacked with label pills
def stack(p, c, x):
    """items: [{src, label, at}] (2-3 images or clips). Panels pop in alternately from the left and the right."""
    c.setdefault("scale", 1.0)
    its = c["items"][:3]; n = len(its); ts = _spread(x, n, "line:0", c.get("until"))
    ts = [x.at(it["at"]) if "at" in it else t for it, t in zip(its, ts)]
    W = c.get("width", 820); H = round(W * 9 / 16); gap = 26; top0 = 0
    out = ""
    for i, (it, t) in enumerate(zip(its, ts)):
        st = "position:absolute;inset:0;width:100%;height:100%;object-fit:cover"
        m = _media(x, it["src"], t - 0.1, x.end + 0.4, st)
        side = -1 if i % 2 == 0 else 1
        out += (f'<div id="{p}-s{i}" class="stk" style="left:{(1080 - W) / 2 + side * 20:.0f}px;top:{top0 + i * (H * 0.62 + gap):.0f}px;width:{W}px;height:{H}px;z-index:{i + 1};transform:rotate({side * 1.6}deg)">'
                f'{m}<div class="stklab"><i></i>{esc(it.get("label", ""))}</div></div>')
        x.A(f'tl.fromTo("#{p}-s{i}", {{ opacity: 0, x: {side * 700} }}, {{ opacity: 1, x: 0, duration: 0.38, ease: "expo.out", immediateRender: false }}, {x.r(t - 0.15)});')
        x.sfx(t - 0.15, "whoosh_fast/tight", -15); x.sfx(t + 0.05, "ui_pop/wide", -14)
    return f'<div class="stks">{out}</div>'

# ------------------------------------------------------------------ copycmd: command chips, a tap on copy, a toast
def copycmd(p, c, x):
    """lines: [command strings] (each in its own chip), title, tap_at (when the copy button is tapped), toast."""
    c.setdefault("scale", 1.0)
    ls = c["lines"]; ts = _spread(x, len(ls), c.get("at", "start+0.2"), c.get("until", "line:0:end"))
    chips = ""
    for i, (l, t) in enumerate(zip(ls, ts)):
        chips += f'<div id="{p}-l{i}" class="ccl mono"><span class="pr">$</span>{esc(l)}</div>'
        x.A(f'tl.fromTo("#{p}-l{i}", {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.3, ease: "power3.out", immediateRender: false }}, {x.r(t)});')
        x.sfx(t, "fit/key/thock", -15)
    tt = x.at(c.get("tap_at", "line:1"))
    x.A(f'tl.fromTo("#{p}-fg", {{ opacity: 0, x: 160, y: 160 }}, {{ opacity: 1, x: 0, y: 0, duration: 0.35, ease: "power3.out", immediateRender: false }}, {x.r(tt - 0.45)});')
    x.A(f'tl.fromTo("#{p}-cp", {{ scale: 1 }}, {{ scale: 0.82, duration: 0.08, yoyo: true, repeat: 1, immediateRender: false }}, {x.r(tt)});')
    x.A(f'tl.set("#{p}-cp", {{ className: "ccbtn on" }}, {x.r(tt + 0.05)});')
    x.A(f'tl.fromTo("#{p}-ts", {{ opacity: 0, y: 30, scale: 0.8 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(2)", immediateRender: false }}, {x.r(tt + 0.1)});')
    x.A(f'tl.to("#{p}-fg", {{ opacity: 0, duration: 0.2 }}, {x.r(tt + 0.5)});')
    x.sfx(tt, "tap/finger", -10); x.sfx(tt + 0.1, "pro_notify/ding_2045", -14)
    hand = '<svg viewBox="0 0 24 24" width="90" height="90"><path d="M9 11V5.5a1.5 1.5 0 0 1 3 0V10m0-1.5a1.5 1.5 0 0 1 3 0V11m0-1a1.5 1.5 0 0 1 3 0v4.5a6 6 0 0 1-6 6h-1.2a5 5 0 0 1-3.9-1.9L4.4 15a1.6 1.6 0 0 1 2.5-2L9 15" fill="#f2f1ee" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>'
    return (f'<div class="ccw"><div class="ccbar mono"><span>{esc(c.get("title", "terminal"))}</span>'
            f'<b id="{p}-cp" class="ccbtn">{ico("lucide:copy", 30)}<em>Copy</em></b></div><div class="ccbody">{chips}</div>'
            f'<div id="{p}-fg" class="ccfg">{hand}</div>'
            f'<div id="{p}-ts" class="cctoast">{ico("lucide:check", 34)}{esc(c.get("toast", "Copied"))}</div></div>')

CARDS.update(spotlight=spotlight, tiles=tiles, filmstrip=filmstrip, wall=wall, polaroid=polaroid,
             promptplay=promptplay, dial=dial, stack=stack, copycmd=copycmd)
