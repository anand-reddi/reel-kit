"""Layout QA before rendering: opens the built film (film/index.html) in Chromium, seeks the timeline to the end of every
spoken line (and its middle), and measures what is on screen: the caption, the card, the presenter box and any headline.
It reports a caption that touches a card / the presenter / a headline, and anything that leaves the 1080x1920 frame, and
writes a contact sheet of every checked moment so the frames can be looked at before spending a render on them.

  python3 reel.py layout script.json            # voice + picture (no render), then this check
"""
HEAD = 150   # how far the presenter's head can rise above the camera box (px)
import json, os, sys

JS = r"""
(t) => {
  const tl = window.__timelines && window.__timelines.reel; if (!tl) return {err: "no timeline"};
  tl.seek(t, false);
  const vis = (el) => { let o = 1;
    for (let e = el; e && e !== document.body; e = e.parentElement) {
      const cs = getComputedStyle(e); if (cs.display === "none" || cs.visibility === "hidden") return 0; o *= parseFloat(cs.opacity); }
    return o; };
  const R = (el) => { const r = el.getBoundingClientRect(); return {x: r.left, y: r.top, w: r.width, h: r.height}; };
  const painted = (e) => {      // draws something itself: text, media, or a background / border
    const tag = e.tagName.toLowerCase(); if (["img", "video", "svg", "canvas"].includes(tag)) return true;
    for (const n of e.childNodes) if (n.nodeType === 3 && n.textContent.trim()) return true;
    const cs = getComputedStyle(e);
    return (cs.backgroundColor && !/rgba\(0, 0, 0, 0\)|transparent/.test(cs.backgroundColor)) || cs.backgroundImage !== "none" || parseFloat(cs.borderTopWidth) > 0; };
  const content = (wrap) => {   // the real extent of a card: union of its visible, painted descendants
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9; const W = wrap.getBoundingClientRect();
    wrap.querySelectorAll("*").forEach(e => { if (e.closest("svg") && e.tagName.toLowerCase() !== "svg") return;
      let r = e.getBoundingClientRect(); r = {left: r.left, top: r.top, right: r.right, bottom: r.bottom};
      for (let a = e.parentElement; a && a !== wrap.parentElement; a = a.parentElement) {   // clipped by overflow:hidden
        const cs = getComputedStyle(a); if (cs.overflow === "visible" && cs.overflowX === "visible" && cs.overflowY === "visible") continue;
        const q = a.getBoundingClientRect(); r = {left: Math.max(r.left, q.left), top: Math.max(r.top, q.top), right: Math.min(r.right, q.right), bottom: Math.min(r.bottom, q.bottom)}; }
      r.width = r.right - r.left; r.height = r.bottom - r.top;
      if (r.width < 2 || r.height < 2) return; if (vis(e) < 0.3 || !painted(e)) return;
      if (r.width >= 1079 && r.height >= 1900) return;   // a full-frame backdrop layer
      x0 = Math.min(x0, r.left); y0 = Math.min(y0, r.top); x1 = Math.max(x1, r.right); y1 = Math.max(y1, r.bottom); });
    return x1 > x0 ? {x: x0, y: y0, w: x1 - x0, h: y1 - y0} : null; };
  const out = {caps: [], cards: [], cam: null, heads: []};
  document.querySelectorAll(".cap").forEach(c => { if (vis(c) > 0.5) { // only the words already shown
      let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
      c.querySelectorAll(".w").forEach(w => { if (vis(w) < 0.5) return; const r = w.getBoundingClientRect();
        x0 = Math.min(x0, r.left); y0 = Math.min(y0, r.top); x1 = Math.max(x1, r.right); y1 = Math.max(y1, r.bottom); });
      if (x1 > x0) out.caps.push({id: c.id, x: x0, y: y0, w: x1 - x0, h: y1 - y0}); } });
  document.querySelectorAll(".card-wrap").forEach(c => { if (vis(c) > 0.5 && !c.classList.contains("ins")) { const r = content(c); if (r) out.cards.push({id: c.id, ...r}); } });
  const cam = document.getElementById("cam"); if (cam && vis(cam) > 0.5) { const b = document.getElementById("camback");
    out.box = !!(b && vis(b) > 0.3); out.cam = R(out.box ? b : cam); }
  document.querySelectorAll(".headline").forEach(h => { if (vis(h) > 0.5) out.heads.push(R(h)); });
  return out; }
"""

def inter(a, b, pad=8):
    w = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"]) + pad
    h = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"]) + pad
    return w > 0 and h > 0

def check(work, out_dir=None):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    film = os.path.join(work, "film", "index.html"); tm = json.load(open(os.path.join(work, "timing.json")))
    out_dir = out_dir or os.path.join(work, "layout"); os.makedirs(out_dir, exist_ok=True)
    pts = []
    for ln in tm["lines"]:
        pts.append((ln["scene"], ln["line"], round((ln["start"] + ln["end"]) / 2, 2)))
        pts.append((ln["scene"], ln["line"], round(ln["end"] - 0.05, 2)))
    probs, shots, fix, lim = [], [], {}, {}
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto("file://" + film); pg.wait_for_timeout(1500)
        pg.evaluate("document.fonts ? document.fonts.ready : null")
        for k, (sc, li, t) in enumerate(pts):
            m = pg.evaluate(JS, t)
            if m.get("err"): sys.exit(m["err"])
            tag = f"scene {sc} line {li} @ {t:.2f}s"
            for c in m["caps"]:
                for cd in m["cards"]:
                    if inter(c, cd): probs.append(f"{tag}: caption {c['id']} overlaps card {cd['id']} (caption y {c['y']:.0f}-{c['y'] + c['h']:.0f}, card y {cd['y']:.0f}-{cd['y'] + cd['h']:.0f})")
                if m["cam"] and m.get("box") and inter(c, m["cam"]): probs.append(f"{tag}: caption {c['id']} overlaps the presenter box (y {m['cam']['y']:.0f})")
                if m["cam"] and m.get("box"):   # the presenter's hair and head rise above the box
                    cm = m["cam"]; hz = {"x": cm["x"] + cm["w"] * .18, "y": cm["y"] - HEAD, "w": cm["w"] * .64, "h": HEAD}
                    if inter(c, hz): probs.append(f"{tag}: caption {c['id']} sits on the presenter's head (caption bottom {c['y'] + c['h']:.0f}, head top {hz['y']:.0f})")
                for h in m["heads"]:
                    if inter(c, h): probs.append(f"{tag}: caption {c['id']} overlaps the headline")
                if c["x"] < 20 or c["x"] + c["w"] > 1060: probs.append(f"{tag}: caption {c['id']} runs off the frame")
            for c in m["caps"]:   # where the caption could go instead: under the lowest card, above the presenter box
                for cd in m["cards"]:
                    if inter(c, cd):
                        need = cd["y"] + cd["h"] + 34
                        fix[sc] = max(fix.get(sc, 0), need)
                        lim[sc] = min(lim.get(sc, 1920), (m["cam"]["y"] - HEAD - 10) if (m["cam"] and m.get("box")) else 1880)
            for cd in m["cards"]:
                if m["cam"] and m.get("box") and inter(cd, m["cam"], pad=-30): probs.append(f"{tag}: card {cd['id']} overlaps the presenter box (card bottom {cd['y'] + cd['h']:.0f}, box top {m['cam']['y']:.0f})")
                if cd["x"] < -2 or cd["x"] + cd["w"] > 1082 or cd["y"] + cd["h"] > 1922: probs.append(f"{tag}: card {cd['id']} runs off the frame")
            f = os.path.join(out_dir, f"{k:03d}.png"); pg.screenshot(path=f); shots.append(f)
        b.close()
    # contact sheet, 6 per row, with the times
    th = [Image.open(f).convert("RGB").resize((216, 384)) for f in shots]
    cols = 6; rows = (len(th) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 216, rows * 384), (40, 40, 40))
    for i, im in enumerate(th): sheet.paste(im, ((i % cols) * 216, (i // cols) * 384))
    sp = os.path.join(out_dir, "sheet.png"); sheet.save(sp)
    seen = []; [seen.append(x) for x in probs if x not in seen]
    print(f"layout: {len(pts)} moments checked, {len(seen)} problem(s); sheet {sp}")
    for x in seen: print("  !", x)
    check.fixes = {sc: round(y) for sc, y in fix.items() if y + 100 <= lim.get(sc, 1920)}
    for sc in fix:
        if sc not in check.fixes: print(f"  ! scene {sc}: no room for the caption under the card (needs y {fix[sc]:.0f}); make the card smaller")
    return seen
