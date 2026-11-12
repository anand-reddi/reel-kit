import sys, subprocess, json
sys.path.insert(0, '/root/reelkit')
from core import icons
import base64
b64=lambda f: 'data:font/woff2;base64,'+base64.b64encode(open(f,'rb').read()).decode()
F = b64('/root/reelkit/assets/fonts/archivo-latin-800-normal.woff2'); M = b64('/root/reelkit/assets/fonts/inter-700.woff2')
el = icons.svg('simple-icons:electron', 64, '#9feaf9'); ru = icons.svg('simple-icons:rust', 64, '#ffffff'); dc = icons.svg('simple-icons:discord', 56, '#5865f2')
ck = icons.svg('lucide:check', 44, '#0b0b0b'); ld = icons.svg('lucide:loader', 44, '#fff'); mp = icons.svg('lucide:mouse-pointer-click', 44, '#0b0b0b')
css = f'''@font-face{{font-family:AV;src:url({F})}}@font-face{{font-family:IN;src:url({M})}}
html,body{{margin:0;background:transparent;width:1080px;height:1920px;overflow:hidden}}
.pill{{position:absolute;left:36px;display:flex;align-items:center;gap:18px;padding:16px 30px 16px 20px;border-radius:999px;background:rgba(11,11,11,.82);border:2px solid rgba(255,255,255,.15);font:900 46px AV;color:#fff;letter-spacing:-1px}}
.pill small{{font:700 26px IN;letter-spacing:4px;color:rgba(255,255,255,.6);text-transform:uppercase}}
.band{{position:absolute;left:0;right:0;top:860px;height:200px;background:#0b0b0b;background-image:radial-gradient(rgba(255,255,255,.09) 1.5px,transparent 1.6px);background-size:26px 26px;border-top:4px solid #e5372d;border-bottom:4px solid #e5372d}}
.badge{{position:absolute;right:36px;display:flex;align-items:center;gap:14px;padding:16px 30px;border-radius:22px;font:900 44px AV;letter-spacing:-.5px}}
.ok{{background:#3ddc84;color:#0b0b0b}} .wait{{background:rgba(11,11,11,.85);color:#fff;border:2px solid rgba(255,255,255,.25)}} .clk{{background:#fff;color:#0b0b0b}}
'''
def page(body): return f'<!doctype html><html><head><meta charset=utf-8><style>{css}</style></head><body>{body}</body></html>'
P = {
 'base': f'<div style="position:absolute;left:0;right:0;top:0;height:150px;background:linear-gradient(#0b0b0b 35%,transparent)"></div><div style="position:absolute;left:0;right:0;top:1060px;height:150px;background:linear-gradient(#0b0b0b 35%,transparent)"></div><div class="band"></div><div class="pill" style="top:40px">{dc}{el}<span>Electron</span><small>today</small></div><div class="pill" style="top:1100px">{dc}{ru}<span>Rust</span><small>new</small></div>',
 'e_clk': f'<div class="badge clk" style="top:40px">{mp}OPENED FIRST</div>',
 'e_wait': f'<div class="badge wait" style="top:40px">{ld}STILL LOADING…</div>',
 'e_ok': f'<div class="badge ok" style="top:40px">{ck}READY</div>',
 'r_clk': f'<div class="badge clk" style="top:1100px">{mp}OPENED LATER</div>',
 'r_ok': f'<div class="badge ok" style="top:1100px">{ck}READY FIRST</div>',
}
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
    for k, v in P.items():
        pg.set_content(page(v)); pg.wait_for_timeout(250); pg.screenshot(path=f'race/{k}.png', omit_background=True)
    b.close()
MODE = sys.argv[1] if len(sys.argv) > 1 else 'race'
S0, S1, SP = (5.6, 12.1, 1.3) if MODE == 'race' else (13.2, 16.1, 1.0)
o = lambda t: round((t - S0) / SP, 3)
ev = dict(eclk=o(6.0), rclk=o(8.7), rok=o(10.0), eok=o(11.7))
D = round((S1 - S0) / SP, 3)
ov = [] if MODE != 'race' else [('e_clk', ev['eclk'], ev['rclk']), ('e_wait', ev['rclk'], ev['eok']), ('e_ok', ev['eok'], 99), ('r_clk', ev['rclk'], ev['rok']), ('r_ok', ev['rok'], 99)]
inputs = ['-ss', str(S0), '-t', str(S1 - S0), '-i', 'race-src.mp4', '-i', 'race/base.png'] + sum([['-i', f'race/{k}.png'] for k, _, _ in ov], [])
fc = (f'[0:v]setpts=PTS/{SP},split[a][b];[a]crop=540:430:0:112,scale=1080:860:flags=lanczos,eq=saturation=1.1[t];[b]crop=540:430:540:112,scale=1080:860:flags=lanczos,eq=saturation=1.1[u];'
      f'color=c=0x0b0b0b:s=1080x1920:d={D}[bg];[bg][t]overlay=0:0[x0];[x0][u]overlay=0:1060[x1];[x1][1:v]overlay=0:0[y0]')
last = 'y0'
for n, (k, a, z) in enumerate(ov):
    fc += f";[{last}][{n+2}:v]overlay=0:0:enable='between(t,{a},{z})'[z{n}]"; last = f'z{n}'
fc += f';[{last}]fps=30,format=yuv420p[out]'
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', fc, '-map', '[out]', '-t', str(D), '-c:v', 'libx264', '-crf', '16', f'reel/assets/{MODE}.mp4'], check=True)
json.dump(ev | {'dur': D}, open(f'race/{MODE}.json', 'w')); print(ev, D)
