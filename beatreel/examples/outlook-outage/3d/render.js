// node render.js stills t1 t2 ...   -> st_<t>.png (debug stills)
// node render.js clips [name ...]   -> ../assets/clips/<name>.webm (VP9 with alpha), one per shot range in times.js
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const HERE = __dirname, OUT = path.join(HERE, '..', 'assets', 'clips'), FPS = 30;
(async () => {
  const [mode, ...rest] = process.argv.slice(2);
  const br = await chromium.launch({ args: ['--allow-file-access-from-files', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pg = await br.newPage({ viewport: { width: 1080, height: 1280 } });
  pg.on('pageerror', e => console.log('pageerror', e.message)); pg.on('console', m => { if (m.type() === 'error') console.log('console', m.text()); });
  await pg.goto('file://' + path.join(HERE, 'index.html')); await pg.waitForFunction('window.__ready === true', null, { timeout: 120000 });
  const shot = async (t, file) => { await pg.evaluate(t => window.__seek(t), t); await pg.screenshot({ path: file, omitBackground: true }); };
  if (mode === 'stills') { for (const t of rest) { await shot(+t, path.join(HERE, 'st_' + t + '.png')); console.log('still', t); } }
  else {
    const R = await pg.evaluate(() => window.R3); fs.mkdirSync(OUT, { recursive: true });
    for (const [name, [a, b]] of Object.entries(R)) { if (rest.length && !rest.includes(name)) continue;
      const fd = path.join(HERE, 'frames', name); fs.rmSync(fd, { recursive: true, force: true }); fs.mkdirSync(fd, { recursive: true });
      const n = Math.ceil((b - a + .1) * FPS), t0 = Date.now();
      for (let i = 0; i < n; i++) await shot(a + i / FPS, path.join(fd, String(i).padStart(5, '0') + '.png'));
      execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', String(FPS), '-i', path.join(fd, '%05d.png'), '-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p', '-b:v', '0', '-crf', '22', '-row-mt', '1', '-auto-alt-ref', '0', path.join(OUT, name + '.webm')]);
      console.log(name, n, 'frames', ((Date.now() - t0) / 1000).toFixed(0) + 's'); }
  }
  await br.close();
})();
