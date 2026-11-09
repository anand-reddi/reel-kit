"""Renders the 3D laptop shots for the Czkawka reel: one film, several time ranges (absolute reel seconds)."""
import json, os, sys, shutil, subprocess, base64
sys.path.insert(0, '/root/reelkit')
from core import icons
from styles.studio3d import compose as C3
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, '..', 'reel'); A = os.path.join(R, 'assets')
tm = json.load(open(os.path.join(R, 'build/cz-ig/timing.json')))
T = dict(full=1.32, copies=2.25, cards=[3.08, 3.34, 3.63], x3=3.9, dl=4.38, empty=5.18, name0=6.27, scan=6.65, clear=7.13,
         feat0=10.42, dupLit=11.07, big0=16.89, big=16.66, gh0=27.22)
RANGES = {'lap-a': (0.0, 7.71), 'lap-dup': (10.42, 11.99), 'lap-big': (16.89, 17.79), 'lap-gh': (27.22, 30.74)}
LAY = ['sunset', 'lake', 'sunset', 'city', 'beach', 'night', 'lake', 'sunset', 'dunes', 'beach', 'city', 'night', 'lake', 'dunes', 'sunset', 'beach', 'city', 'night']
work = os.path.join(HERE, 'build'); film = os.path.join(work, 'film'); fa = os.path.join(film, 'assets')
script = {'scene': os.path.join(HERE, 'laptop.scene.js'), 'look': 'dark', 'fov': 38, 'drift': 0.008, 'scale': .8, 'captions': False, 'fog': [6, 14]}
C3.build(script, tm, work, HERE)
photos = {}
for k in set(LAY): shutil.copy(f'{A}/photo-{k}.png', fa); photos[k] = f'assets/photo-{k}.png'
shutil.copy(f'{A}/gh-czkawka.jpg', fa)
ics = {k: 'data:image/svg+xml;base64,' + base64.b64encode(icons.svg('lucide:' + k, 96, '#d8d8de').encode()).decode() for k in ['package', 'file-video', 'file-text', 'file-archive']}
data = dict(T=T, lay=LAY, photos=photos, icons=ics, gh='assets/gh-czkawka.jpg', copies=['IMG_2041.jpg', 'IMG_2041 (1).jpg', 'IMG_2041 copy.jpg'],
    dl=[['package', 'setup.exe', '212 MB'], ['package', 'setup (1).exe', '212 MB', 0, 1], ['file-video', 'trip_video.mp4', '1.4 GB'], ['file-video', 'trip_video (2).mp4', '1.4 GB', 0, 1],
        ['file-text', 'invoice.pdf', '88 KB'], ['file-text', 'invoice (1).pdf', '88 KB', 0, 1], ['file-archive', 'wallpapers.zip', '640 MB']],
    big=[['file-video', 'wedding_full.mov', '14.2 GB', 1, 1], ['file-archive', 'backup_2021.zip', '9.8 GB', .69, 1], ['file-video', 'screen_rec.mp4', '6.1 GB', .43],
         ['package', 'game_installer.iso', '4.7 GB', .33], ['file-video', 'lecture_03.mkv', '2.2 GB', .15], ['file-video', 'old_reel_raw.mov', '1.9 GB', .13]])
open(os.path.join(fa, 'lapdata.js'), 'w').write('window.__LAP = ' + json.dumps(data) + ';')
h = open(os.path.join(film, 'index.html')).read(); h = h.replace('<script type="module">', '<script src="assets/lapdata.js"></script>\n<script type="module">', 1)
open(os.path.join(film, 'index.html'), 'w').write(h)
only = [a for a in sys.argv[1:] if not a.startswith('--')]; stills = '--stills' in sys.argv
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    br = p.chromium.launch(args=['--allow-file-access-from-files', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    pg = br.new_page(viewport={'width': 1080, 'height': 1920}); pg.on('console', lambda m: print('console:', m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: print('pageerror:', e))
    pg.goto('file://' + os.path.join(film, 'index.html')); pg.wait_for_function('window.__timelines && window.__timelines.reel && window.__lapReady', timeout=120000)
    pg.evaluate('window.__lapReady.then(() => { window.__ok = 1; })'); pg.wait_for_function('window.__ok === 1', timeout=60000)
    for name, (a, b) in RANGES.items():
        if only and name not in only: continue
        if stills:
            for t in [a + .05, (a + b) / 2, b - .05] if name != 'lap-a' else [0.05, 1.6, 2.5, 3.5, 4.2, 4.9, 5.7, 6.5, 7.35, 7.65]:
                pg.evaluate(f'(() => {{ window.__timelines.reel.seek({t}, false); }})()'); pg.screenshot(path=os.path.join(work, f'st_{name}_{t:.2f}.jpg'), type='jpeg', quality=85)
            continue
        fd = os.path.join(work, name); shutil.rmtree(fd, ignore_errors=True); os.makedirs(fd)
        n = int(round((b - a) * 30))
        for i in range(n):
            pg.evaluate(f'(() => {{ window.__timelines.reel.seek({a + i / 30:.4f}, false); }})()'); pg.screenshot(path=os.path.join(fd, f'{i:05d}.jpg'), type='jpeg', quality=93)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-i', os.path.join(fd, '%05d.jpg'), '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', os.path.join(A, f'{name}.mp4')], check=True)
        print(name, n, 'frames')
    br.close()
