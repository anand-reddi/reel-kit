"""Storyboard of a built (unrendered) reel: one frame at the end of every spoken line (plus the first frame), with the
timeline AND every <video> seeked to that moment, on one labelled sheet. For showing the owner every frame before a render.

  python3 reel.py board script.json      # voice + picture (no render), then build/<name>/board/board.jpg
"""
import json, os, sys, textwrap

def main(work, out, times=None):
    from playwright.sync_api import sync_playwright
    from PIL import Image, ImageDraw, ImageFont
    tm = json.load(open(os.path.join(work, "timing.json")))
    pts = [(t, 0, "") for t in times] if times else [(0.2, 0, "(first frame)")]
    for ln in ([] if times else tm["lines"]):
        pts.append((round(ln["end"] - 0.08, 2), ln["scene"], ln.get("text", "")))
    SEEK = r"""async (t) => {
      window.__timelines.reel.seek(t, false);
      const vs = [...document.querySelectorAll('video[data-start]')]; const ps = [];
      for (const v of vs) { const s = +v.dataset.start, d = +v.dataset.duration, m = +(v.dataset.mediaStart || 0);
        const on = t >= s && t < s + d; v.style.visibility = on ? 'visible' : 'hidden';
        if (on) { ps.push(new Promise(r => { v.addEventListener('seeked', r, {once: true}); setTimeout(r, 3000); })); v.currentTime = m + (t - s); } }
      await Promise.all(ps); return vs.length; }"""
    shots = []
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto("file://" + os.path.join(work, "film", "index.html")); pg.wait_for_timeout(2000)
        pg.evaluate("document.fonts.ready")
        for i, (t, sc, txt) in enumerate(pts):
            pg.evaluate(SEEK, t); pg.wait_for_timeout(120)
            f = os.path.join(out, f"f{i:03d}.png"); pg.screenshot(path=f); shots.append((f, t, sc, txt))
        b.close()
    W, H, LB, cols = 360, 640, 70, 6
    rows = (len(shots) + cols - 1) // cols
    S = Image.new("RGB", (cols * W, rows * (H + LB)), (24, 24, 24)); d = ImageDraw.Draw(S)
    try: fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
    except Exception: fnt = ImageFont.load_default()
    for i, (f, t, sc, txt) in enumerate(shots):
        x, y = (i % cols) * W, (i // cols) * (H + LB)
        S.paste(Image.open(f).resize((W, H)), (x, y))
        d.text((x + 8, y + H + 6), f"#{i+1}  {t:.1f}s  scene {sc+1}", fill=(229, 55, 45), font=fnt)
        d.text((x + 8, y + H + 28), "\n".join(textwrap.wrap(txt.replace('*', ''), 36)[:2]), fill=(220, 220, 220), font=fnt)
    S.save(os.path.join(out, "board.jpg"), quality=88); print(f"board: {len(shots)} frames, {os.path.join(out, 'board.jpg')}"); return os.path.join(out, "board.jpg")


if __name__ == "__main__": main(sys.argv[1], sys.argv[2])
