// kinetic runtime: one GSAP timeline, every frame a pure function of time (no Math.random, no Date, no state
// between frames), so the renderer can seek anywhere. Effects and helpers shared by the blocks (blocks.js).
// Our own code, written for reel-kit (9:16, 1080x1920); the look follows kinetic-type motion design:
// huge words on every beat, ground colour flips, whip pans, 3D type the camera flies through.
'use strict';
const W = 1080, H = 1920;
const tl = gsap.timeline({ paused: true });
const K = window.K = { tl, cues: [], blocks: {}, n: 0 };
const D = window.__DATA;                       // {palette, bpm, scenes: [{start, end, block, times}], hud, subs, fonts}
const P = D.palette, B = 60 / D.bpm;
K.B = B; K.P = P;

// ------------------------------------------------------------------ small helpers
const $ = (s, r = document) => r.querySelector(s);
function el(tag, cls, parent, html) { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; if (parent) parent.appendChild(e); return e; }
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const col = c => (c && P[c]) || c;                       // palette name or a colour
const readable = g => { const c = col(g) || P.bg; const h = c.replace('#', ''); const v = parseInt(h.length === 3 ? h.split('').map(x => x + x).join('') : h, 16);
  const l = (0.3 * (v >> 16 & 255) + 0.59 * (v >> 8 & 255) + 0.11 * (v & 255)); return l > 140 ? P.ink : P.paper; };
function rng(seed) { let s = (seed * 9301 + 49297) % 233280 || 1; return () => (s = (s * 9301 + 49297) % 233280) / 233280; }
function sfx(t, id, gain = -12, opt) { K.cues.push(opt ? [+t.toFixed(3), id, gain, opt] : [+t.toFixed(3), id, gain]); }
K.sfx = sfx;
function uid(p = 'x') { return p + (K.n++); }

// fit an element's text to a box (font-size), measured once on a layout copy (transforms ignored)
function fit(e, maxW, maxH = 99999, cap = 1400) {
  const sp = e.querySelector(':scope > .fitw') || (() => { const s = document.createElement('span'); s.className = 'fitw'; s.style.display = 'inline-block';
    while (e.firstChild) s.appendChild(e.firstChild); e.appendChild(s); return s; })();
  const fs = parseFloat(getComputedStyle(e).fontSize) || 100;
  const k = Math.min(maxW / Math.max(1, sp.offsetWidth), maxH / Math.max(1, sp.offsetHeight));
  e.style.fontSize = Math.min(cap, fs * k) + 'px'; return fs * k;
}
K.fit = fit;
// split text into letter spans
function letters(e, text) { e.innerHTML = ''; return [...String(text)].map(ch => { const s = el('span', 'ch', e); s.textContent = ch === ' ' ? ' ' : ch; return s; }); }

// ------------------------------------------------------------------ the stage
const root = $('#root'), cam = $('#cam'), ground = $('#ground'), fxl = $('#fx');
function setGround(t, g) { tl.set(ground, { backgroundColor: col(g) || P.bg }, t); }
K.ground = setGround;

// visible only between a and b
function window_(e, a, b) { a = Math.max(a, 0.0002); tl.set(e, { visibility: 'hidden' }, 0); tl.set(e, { visibility: 'visible' }, a);   // a set before 0 would lose to the hide at 0
  if (b != null) tl.set(e, { visibility: 'hidden' }, b); }
K.vis = window_;

// ------------------------------------------------------------------ camera and transitions
function shake(t, a = 16, d = .22) { tl.to(cam, { keyframes: [{ x: a, y: -a * .5 }, { x: -a * .8, y: a * .4 }, { x: a * .4, y: -a * .2 }, { x: 0, y: 0 }], duration: d, ease: 'none' }, t); }
function bump(t, s = 1.04) { tl.fromTo(cam, { scale: s }, { scale: 1, duration: .25, ease: 'power3.out', immediateRender: false }, t); }
function whip(t, dir = 'x', sign = 1, d = .14) {          // a whip pan into the new shot: the camera lands with motion skew + blur
  const v = dir === 'y' ? { y: sign * 700, skewY: -sign * 6 } : { x: sign * 700, skewX: -sign * 12 };
  tl.fromTo(cam, { ...v, filter: 'blur(14px)' }, { x: 0, y: 0, skewX: 0, skewY: 0, filter: 'blur(0px)', duration: d, ease: 'expo.out', immediateRender: false }, t);
  sfx(t - .05, dir === 'y' ? 'whoosh_fast/tight' : 'whoosh_fast/whip', -11);
}
function whipOut(t, dir = 'x', sign = -1, d = .1) {
  const v = dir === 'y' ? { y: sign * 700, skewY: sign * 6 } : { x: sign * 700, skewX: sign * 12 };
  tl.to(cam, { ...v, filter: 'blur(14px)', duration: d, ease: 'power3.in' }, t - d);
  tl.set(cam, { x: 0, y: 0, skewX: 0, skewY: 0, filter: 'blur(0px)' }, t);
}
function flash(t, c = '#ffffff', d = .14, o = .9) { const f = el('div', 'flash', fxl); f.style.background = col(c);
  tl.fromTo(f, { opacity: o }, { opacity: 0, duration: d, ease: 'power2.out', immediateRender: false }, t); tl.set(f, { opacity: 0 }, 0); }
function drift(e, a, b, k = 1.06, r = .8) { tl.fromTo(e, { scale: 1, rotation: 0 }, { scale: k, rotation: r, duration: Math.max(.2, b - a), ease: 'none', immediateRender: false }, a); }
Object.assign(K, { shake, bump, whip, whipOut, flash, drift });

// ------------------------------------------------------------------ hit effects: rays, ring, sparks
const SVGNS = 'http://www.w3.org/2000/svg';
function svg(parent, cls = 'svgl') { const s = document.createElementNS(SVGNS, 'svg'); s.setAttribute('class', cls); s.setAttribute('viewBox', `0 0 ${W} ${H}`); s.setAttribute('width', W); s.setAttribute('height', H); parent.appendChild(s); return s; }
function sv(tag, attrs, parent) { const e = document.createElementNS(SVGNS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); parent.appendChild(e); return e; }
function rays(t, c = 'accent', cx = W / 2, cy = H / 2, n = 22, seed = 3) {
  const s = svg(fxl), r = rng(seed); tl.set(s, { opacity: 0 }, 0);
  for (let i = 0; i < n; i++) { const a = (i / n) * Math.PI * 2 + r() * .2, l0 = 120 + r() * 80, l1 = 700 + r() * 500;
    const ln = sv('line', { x1: cx + Math.cos(a) * l0, y1: cy + Math.sin(a) * l0, x2: cx + Math.cos(a) * l1, y2: cy + Math.sin(a) * l1, stroke: col(c), 'stroke-width': 6 + r() * 10, 'stroke-linecap': 'round' }, s);
    const L = l1 - l0; ln.setAttribute('stroke-dasharray', `${L} ${L}`);
    tl.fromTo(ln, { attr: { 'stroke-dashoffset': L } }, { attr: { 'stroke-dashoffset': -L }, duration: .32 + r() * .1, ease: 'power2.out', immediateRender: false }, t); }
  tl.set(s, { opacity: 1 }, t); tl.set(s, { opacity: 0 }, t + .5);
}
function ring(t, c = 'paper', cx = W / 2, cy = H / 2, r0 = 60, r1 = 900) {
  const s = svg(fxl); tl.set(s, { opacity: 0 }, 0); const ci = sv('circle', { cx, cy, r: r0, fill: 'none', stroke: col(c), 'stroke-width': 14 }, s);
  tl.set(s, { opacity: 1 }, t); tl.fromTo(ci, { attr: { r: r0, 'stroke-width': 26 } }, { attr: { r: r1, 'stroke-width': 1 }, duration: .45, ease: 'power3.out', immediateRender: false }, t);
  tl.fromTo(ci, { opacity: 1 }, { opacity: 0, duration: .45, ease: 'power1.in', immediateRender: false }, t); tl.set(s, { opacity: 0 }, t + .5);
}
function sparks(t, c = 'accent', cx = W / 2, cy = H / 2, n = 16, seed = 7) {
  const s = svg(fxl), r = rng(seed); tl.set(s, { opacity: 0 }, 0); tl.set(s, { opacity: 1 }, t); tl.set(s, { opacity: 0 }, t + .6);
  for (let i = 0; i < n; i++) { const a = r() * Math.PI * 2, d = 300 + r() * 500, len = 30 + r() * 40;
    const g = sv('g', {}, s); const ln = sv('line', { x1: 0, y1: 0, x2: len, y2: 0, stroke: col(i % 3 ? c : 'paper'), 'stroke-width': 7, 'stroke-linecap': 'round' }, g);
    g.setAttribute('transform', `translate(${cx},${cy}) rotate(${a * 180 / Math.PI})`);
    tl.fromTo(ln, { attr: { x1: 0, x2: len } }, { attr: { x1: d, x2: d + len * .3 }, duration: .5, ease: 'power3.out', immediateRender: false }, t);
    tl.fromTo(ln, { opacity: 1 }, { opacity: 0, duration: .5, ease: 'power2.in', immediateRender: false }, t); }
}
// fx presets on a hit: punch = rays + ring + sparks + flash + shake; hit = flash + shake; beat = shake + bump
function fx(t, kind = 'punch', o = {}) {
  const cx = o.cx ?? W / 2, cy = o.cy ?? H / 2;
  if (kind === 'punch') { rays(t, o.c || 'accent', cx, cy, 22, Math.round(t * 100)); ring(t, 'paper', cx, cy); sparks(t, o.c || 'accent', cx, cy, 16, Math.round(t * 77)); flash(t, '#fff', .1, .5); shake(t, 18); sfx(t, o.big ? 'impact/punch' : 'pro_impact/short', o.big ? -9 : -11); }
  else if (kind === 'hit') { flash(t, '#fff', .1, .6); shake(t, 14); sfx(t, 'cut_hit/punch', -11); }
  else if (kind === 'beat') { shake(t, 8, .16); bump(t, 1.03); sfx(t, 'cut_hit/kick', -12); }
}
Object.assign(K, { svg, sv, rays, ring, sparks, fx });

// ------------------------------------------------------------------ comet: a glowing head drawing a path
function comet(parent, d, t0, dur, c = 'accent', w = 8, keep = true) {
  const s = svg(parent, 'svgl comet'); const glow = sv('path', { d, fill: 'none', stroke: col(c), 'stroke-width': w * 3, 'stroke-linecap': 'round', opacity: .25 }, s);
  const p = sv('path', { d, fill: 'none', stroke: col(c), 'stroke-width': w, 'stroke-linecap': 'round' }, s);
  const head = sv('circle', { r: w * 1.8, fill: '#fff' }, s); const halo = sv('circle', { r: w * 5, fill: col(c), opacity: .35 }, s);
  const L = p.getTotalLength(); [p, glow].forEach(x => { x.setAttribute('stroke-dasharray', `${L} ${L}`); x.setAttribute('stroke-dashoffset', L); });
  const o = { k: 0 };
  const upd = () => { const k = o.k, pt = p.getPointAtLength(L * k); [p, glow].forEach(x => x.setAttribute('stroke-dashoffset', L * (1 - k)));
    head.setAttribute('cx', pt.x); head.setAttribute('cy', pt.y); halo.setAttribute('cx', pt.x); halo.setAttribute('cy', pt.y);
    const on = k > 0 && k < 1; head.style.opacity = on ? 1 : 0; halo.style.opacity = on ? .35 : 0; };
  tl.fromTo(o, { k: 0 }, { k: 1, duration: dur, ease: 'power2.inOut', onUpdate: upd, immediateRender: false }, t0);
  tl.set(o, { k: 0, onComplete: upd }, 0); upd();
  if (!keep) tl.to(s, { opacity: 0, duration: .2 }, t0 + dur);
  sfx(t0, 'pro_zip/up', -16);
  return { s, p, L, at: k => p.getPointAtLength(L * k) };
}
K.comet = comet;

// ------------------------------------------------------------------ text effects
// glyph scramble: the word resolves from random glyphs between a and b (seeded, so seeks are exact)
const GLYPHS = '#%&@$*+=<>/\\|{}[]01ABCDEFGHJKLMNPQRSTUVWXYZ';
function scramble(e, text, a, b, seed = 5) {
  const o = { k: 0 }, n = text.length;
  const upd = () => { const r = rng(seed + Math.floor(o.k * 40)); let s = '';
    for (let i = 0; i < n; i++) s += (text[i] === ' ' || o.k >= (i + 1) / n) ? text[i] : GLYPHS[Math.floor(r() * GLYPHS.length)];
    const sp = e.querySelector('.fitw') || e; sp.textContent = s; };
  tl.fromTo(o, { k: 0 }, { k: 1, duration: Math.max(.1, b - a), ease: 'none', onUpdate: upd, immediateRender: false }, a);
  tl.set(o, { k: 1, onComplete: upd }, b);
}
// RGB glitch: two coloured copies jitter around the word (no blend modes: they stall headless capture)
function glitch(e, a, b, seed = 9) {
  const r = rng(seed); const c1 = e.cloneNode(true), c2 = e.cloneNode(true);
  [c1, c2].forEach((c, i) => { c.removeAttribute('id'); c.classList.add('gl'); c.style.color = i ? '#00e5ff' : col('accent'); c.style.opacity = 0; e.parentNode.insertBefore(c, e); });
  for (let t = a; t < b; t += 1 / 30) { const dx = (r() - .5) * 40, dy = (r() - .5) * 10, on = r() > .35;
    tl.set(c1, { x: dx, y: dy, opacity: on ? .85 : 0 }, t); tl.set(c2, { x: -dx, y: -dy, opacity: on ? .85 : 0 }, t);
    tl.set(e, { x: on ? (r() - .5) * 14 : 0 }, t); }
  tl.set([c1, c2], { opacity: 0 }, b); tl.set(e, { x: 0 }, b); sfx(a, 'glitch/stutter', -15);
}
// invert flash: ground and ink swap for 2 frames
function invert(t, inkEls) { const g = $('#ground'); const keep = getComputedStyle(g).backgroundColor;
  tl.set('#invert', { opacity: 1 }, t); tl.set('#invert', { opacity: 0 }, t + 2 / 30); }
// ghost rows: outlined copies of a word scrolling above and below it
function ghosts(parent, text, a, b, o = {}) {
  const wrap = el('div', 'ghosts', parent); const rows = o.rows || 3, gap = o.gap || 250, size = o.size || 220, c = col(o.c || 'paper');
  for (let i = -rows; i <= rows; i++) { if (!i) continue; const row = el('div', 'ghost', wrap); row.textContent = (text + '  ').repeat(4);
    row.style.top = (H / 2 + i * gap - size / 2 + (o.dy || 0)) + 'px'; row.style.fontSize = size + 'px'; row.style.webkitTextStroke = `3px ${c}`;
    const dir = i % 2 ? 1 : -1; tl.fromTo(row, { x: dir * -300 - 400 }, { x: dir * 300 - 400, duration: Math.max(.3, b - a), ease: 'none', immediateRender: false }, a);
    tl.fromTo(row, { opacity: 0 }, { opacity: .5 - Math.abs(i) * .1, duration: .15, immediateRender: false }, a); }
  window_(wrap, a, b); return wrap;
}
// typed text: spans appear one by one; keyword spans can light up
function typeIn(spans, t0, per) { spans.forEach((s, i) => tl.set(s, { opacity: 1 }, t0 + i * per)); }
// code backdrop: the film's own engine source (or given text) scrolling faintly
function codeWall(parent, a, b, o = {}) {
  const w = el('div', 'codewall', parent); const src = (o.text || D.source || '').split('\n').slice(0, 260).join('\n'); w.textContent = src;
  w.style.color = col(o.c || 'paper'); w.style.opacity = o.opacity ?? .12;
  tl.fromTo(w, { y: 0 }, { y: -(o.speed || 900), duration: Math.max(.3, b - a), ease: 'none', immediateRender: false }, a); window_(w, a, b); return w;
}
// a burst of code glyphs flying out of a point
function glyphBurst(t, cx = W / 2, cy = H / 2, n = 26, c = 'paper', seed = 11) {
  const r = rng(seed); const wrap = el('div', 'gburst', fxl);
  for (let i = 0; i < n; i++) { const g = el('span', 'gb', wrap); g.textContent = GLYPHS[Math.floor(r() * GLYPHS.length)]; g.style.color = col(i % 4 ? c : 'accent');
    g.style.left = cx + 'px'; g.style.top = cy + 'px'; g.style.fontSize = (30 + r() * 50) + 'px';
    const a = r() * Math.PI * 2, d = 250 + r() * 550;
    tl.fromTo(g, { x: 0, y: 0, opacity: 1, rotation: 0 }, { x: Math.cos(a) * d, y: Math.sin(a) * d, opacity: 0, rotation: (r() - .5) * 360, duration: .7, ease: 'power3.out', immediateRender: false }, t); }
  tl.set(wrap, { opacity: 0 }, 0); tl.set(wrap, { opacity: 1 }, t); tl.set(wrap, { opacity: 0 }, t + .8); sfx(t, 'glitch/data', -16);
}
Object.assign(K, { scramble, glitch, invert, ghosts, typeIn, codeWall, glyphBurst, letters, el, esc, col, readable, rng, uid, window_, $ });

// ------------------------------------------------------------------ extruded 3D text
// layers stacked in depth; front face in `face`, sides darkening; returns the group (preserve-3d)
function extrude(parent, text, o = {}) {
  const g = el('div', 'ex3', parent); const n = o.layers || 22, depth = o.depth || 6, size = o.size || 260;
  const face = col(o.face || 'ink'), side = o.side || null;
  for (let i = n; i >= 0; i--) { const d = el('div', 'exl', g); d.textContent = text; d.style.fontSize = size + 'px'; d.style.fontVariationSettings = `"wdth" ${o.wdth || 100}, "wght" 900`;
    d.style.transform = `translate(-50%,-50%) translateZ(${-i * depth}px)`;
    d.style.color = i === 0 ? face : (side || `rgba(0,0,0,${.55 + i / n * .35})`);
    if (i === 0 && o.glow) d.style.textShadow = `0 0 ${o.glow}px ${col('accent')}`; }
  const front = g.lastChild, mw = o.maxW || 940; if (front.offsetWidth > mw) { const k = mw / front.offsetWidth; g.querySelectorAll('.exl').forEach(d => d.style.fontSize = (size * k) + 'px'); }
  return g;
}
K.extrude = extrude;

// ------------------------------------------------------------------ hud and subtitles
if (D.hud) {
  const h = el('div', 'hud mono', root); const l = el('span', '', h, esc(D.hud)); const r = el('span', 'hudr', h);
  const o = { t: 0 }; const fmt = t => { const f = Math.floor(t * 30) % 30, s = Math.floor(t) % 60, m = Math.floor(t / 60); return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}:${String(f).padStart(2, '0')}`; };
  tl.fromTo(o, { t: 0 }, { t: D.duration, duration: D.duration, ease: 'none', onUpdate: () => { r.textContent = fmt(o.t) + '  ·  BEAT ' + String(Math.floor(o.t / B) + 1).padStart(3, '0'); } }, 0);
  if (D.hudOut) { tl.to(h, { opacity: 0, duration: .2 }, D.hudOut); }
}
(D.subs || []).forEach(s => { const e = el('div', 'sub mono', root, esc(s.text)); tl.set(e, { opacity: 0 }, 0); tl.set(e, { opacity: 1 }, s.start); tl.set(e, { opacity: 0 }, s.end); });
