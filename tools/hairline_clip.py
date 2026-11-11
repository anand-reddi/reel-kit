"""Render one Hairline figure (lucasmarkes/hairline, MIT, vendored in assets/vendor/hairline) as a 1080x1920 clip in
the reel theme: white lines, dark fills, red on the moving part. The figure answers a pointer, so motion is timed by
moving a real pointer along keys you give (in the figure's own 400x320 coordinates); time runs on a virtual clock, so
the clip is frame-accurate at any render speed.

usage: python3 tools/hairline_clip.py spec.json out.mp4
spec:  {"fig": "padlock", "dur": 2.5, "fps": 30, "keys": [[0, null], [0.4, 200, 120], [1.2, 230, 90]],
        "play": false, "y": 330, "width": 1540, "accent": "#e5372d"}
keys:  [t, x, y] moves the pointer there (eased from the previous key); [t, null] takes the pointer away.
       Leave keys out and set "play": true to use the figure's own built-in loop instead.
figures: basket branches cabinet dish drawer elevator exploded format hub keyboard laptop lockers loupe padlock patch
         phone phosphor plot plug query rail rebuild relay riffle router settle sieve slow stack terminal terrain
         turntable vault"""
import json, os, shutil, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INIT = r"""
(() => { let now = 0; const q = new Map(); let id = 0;
  window.requestAnimationFrame = (cb) => { q.set(++id, cb); return id; }; window.cancelAnimationFrame = (i) => q.delete(i);
  performance.now = () => now; const d0 = Date.now(); Date.now = () => d0 + now;
  const rt = window.setTimeout.bind(window); const timers = new Map(); let tid = 0;
  window.setTimeout = (fn, ms = 0, ...a) => { timers.set(++tid, { at: now + (ms || 0), fn: () => fn(...a) }); return tid; };
  window.clearTimeout = (i) => timers.delete(i);
  window.IntersectionObserver = class { constructor(cb) { this.cb = cb; } observe(el) { rt(() => this.cb([{ isIntersecting: true, target: el, intersectionRatio: 1 }], this), 0); } unobserve() {} disconnect() {} takeRecords() { return []; } };
  const fire = () => { for (const [i, t] of [...timers]) if (t.at <= now) { timers.delete(i); try { t.fn(); } catch (e) { console.error(e); } } };
  window.__step = (ms) => { const n = Math.max(1, Math.round(ms / (1000 / 120))); for (let k = 0; k < n; k++) { now += ms / n; const cbs = [...q.values()]; q.clear(); cbs.forEach((cb) => { try { cb(now); } catch (e) { console.error(e); } }); fire(); } };
})();"""
PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:1080px;height:1920px;background:transparent;overflow:hidden}
#fig{position:absolute;left:LEFTpx;top:TOPpx;width:WIDTHpx;--hl-sw:3.2px;--hl-edge:#f2f1ee;--hl-mid:#b4b4ba;--hl-lo:#5e5e66;--hl-hi:ACCENT;--hl-plate:#151518}
</style></head><body><div id="fig"></div>
<script type="module">import * as H from "./hairline.js"; window.__fig = H["FIG"](document.getElementById("fig"), { theme: "dark", play: PLAY, intensity: 1 }); window.__ready = 1;</script>
</body></html>"""
def ease(k): return k * k * (3 - 2 * k)
def pointer(keys, t):
    prev = None
    for k in keys:
        if k[0] > t: break
        prev = k
    if prev is None or prev[1] is None: return None
    i = keys.index(prev); nxt = keys[i + 1] if i + 1 < len(keys) else None
    if nxt is None or nxt[1] is None or len(prev) < 3: return prev[1:3]
    u = ease(min(1, (t - prev[0]) / max(1e-6, nxt[0] - prev[0])))
    return [prev[1] + (nxt[1] - prev[1]) * u, prev[2] + (nxt[2] - prev[2]) * u]
def render(spec, out):
    w = spec.get('width', 1540); left = (1080 - w) / 2; top = spec.get('y', 330); h = w * 320 / 400
    tmp = tempfile.mkdtemp(); shutil.copy(os.path.join(KIT, 'assets/vendor/hairline/hairline.js'), tmp)
    page = PAGE.replace('LEFT', str(left)).replace('TOP', str(top)).replace('WIDTH', str(w)).replace('ACCENT', spec.get('accent', '#e5372d')) \
               .replace('FIG', spec['fig']).replace('PLAY', 'true' if spec.get('play') else 'false')
    open(os.path.join(tmp, 'index.html'), 'w').write(page); fd = os.path.join(tmp, 'f'); os.makedirs(fd)
    fps = spec.get('fps', 30); n = int(round(spec['dur'] * fps)); keys = spec.get('keys', [])
    with sync_playwright() as p:
        br = p.chromium.launch(args=['--allow-file-access-from-files']); pg = br.new_page(viewport={'width': 1080, 'height': 1920}); pg.add_init_script(INIT)
        pg.goto('file://' + os.path.join(tmp, 'index.html')); pg.wait_for_function('window.__ready === 1'); pg.mouse.move(1070, 1910)
        for i in range(n):
            t = i / fps; at = pointer(keys, t)
            if at: pg.mouse.move(left + at[0] / 400 * w, top + at[1] / 320 * h)
            else: pg.mouse.move(1070, 1910)
            pg.evaluate(f'window.__step({1000 / fps})'); pg.screenshot(path=os.path.join(fd, f'{i:05d}.png'), omit_background=True)
        br.close()
    bg = spec.get('bg', '#0b0b0b')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color={bg}:s=1080x1920:r={fps}', '-framerate', str(fps), '-i', os.path.join(fd, '%05d.png'),
                    '-filter_complex', '[0][1]overlay=shortest=1', '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p', out], check=True)
    shutil.rmtree(tmp)
if __name__ == '__main__':
    render(json.load(open(sys.argv[1])), sys.argv[2]); print('ok', sys.argv[2])
