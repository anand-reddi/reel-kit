// kinetic blocks: each is (box, cfg, T, S) -> builds its DOM inside `box` and adds its tweens and sounds.
// T(v): a number = beats after the block start; strings ("2.5s", "line:1", "word:code", "end-0.2") were
// resolved by compose.py. S = {start, end, i}. Shots inside a block run until the next shot starts.
'use strict';
(() => {
const { tl, el, esc, col, readable, rng, fit, letters, sfx, B } = { ...K, el: K.el, sfx: K.sfx };
const W = 1080, H = 1920, P = K.P;
const BL = K.blocks;
const shotEnds = (arr, T, S) => arr.map((s, i) => [T(s.at), i + 1 < arr.length ? T(arr[i + 1].at) : S.end]);
const layer = (box, a, b, cls = 'shot') => { const d = el('div', cls, box); K.vis(d, a, b); return d; };
const big = (parent, text, o = {}) => { const e = el('div', 'kw ' + (o.cls || ''), parent); e.textContent = text;
  e.style.color = col(o.color) || readable(o.ground); e.style.fontVariationSettings = `"wdth" ${o.wdth ?? 112}, "wght" ${o.wght ?? 900}`;
  e.style.fontSize = (o.size || 300) + 'px'; e.style.top = (o.y ?? H / 2) + 'px'; if (o.rot) e.style.rotate = o.rot + 'deg'; return e; };
const fitBig = (e, o = {}) => { if (!o.size) fit(e, o.maxW || 980, o.maxH || 760, o.cap || 900); };
function enter(sh, t, how) {          // how a shot arrives
  if (how === 'whipX') K.whip(t, 'x', 1); else if (how === 'whipXr') K.whip(t, 'x', -1); else if (how === 'whipY') K.whip(t, 'y', 1);
}
function extras(sh, word, s, a, b, T) {   // options shared by all Words styles
  if (s.scramble) K.scramble(word, s.text_, a + s.scramble[0] * B, a + s.scramble[1] * B, Math.round(a * 31));
  if (s.glitch) K.glitch(word, a + (s.glitchAt || .5) * B, a + (s.glitchAt || .5) * B + .3, Math.round(a * 13));
  (s.inverts || []).forEach(k => { const t = a + k * B; K.tl.set('#invert', { opacity: 1 }, t); K.tl.set('#invert', { opacity: 0 }, t + 2 / 30); sfx(t, 'cut_hit/air', -15); });
  if (s.flip) { const t = a + s.flip.at * B; K.ground(t, s.flip.ground); if (s.flip.color || s.flip.ground) tl.set(word, { color: col(s.flip.color) || readable(s.flip.ground) }, t); sfx(t, 'cut_hit/kick', -13); }
  if (s.dot) { const sp = word.querySelector('.fitw') || word; const tx = sp.textContent; sp.innerHTML = esc(tx.slice(0, -1)) + `<span style="color:${col(s.dotColor || 'accent')}">${esc(tx.slice(-1))}</span>`; }
  // mark / mark2: brand logos that pop in above the word (a logo whenever a brand is named)
  if (s.mark) { const row = el('div', 'kmarks', sh); row.style.color = col(s.markColor) || readable(s.ground);
    row.style.top = ((s.markY ?? (H / 2 - 430))) + 'px';
    [s.mark, s.mark2].filter(Boolean).forEach((m, k) => { const d = el('div', 'kmark', row, m);
      tl.fromTo(d, { scale: 0, rotation: -25, opacity: 0 }, { scale: 1, rotation: 0, opacity: 1, duration: .28, ease: 'back.out(2.2)', immediateRender: false }, a + .04 + k * .08); });
    sfx(a + .06, 'pro_pop_in/deep', -14); }
  if (s.glyphs) K.glyphBurst(a + .02, W / 2, H / 2, 26, 'paper', Math.round(a * 17));
  if (s.code) K.codeWall(sh, a, b, { c: readable(s.ground), opacity: .1 });
  if (s.note) { const n = el('div', 'knote mono', sh); n.style.color = col(s.noteColor) || readable(s.ground); const t0 = a + (s.noteAt ?? 1) * B;
    const sp = [...s.note].map(ch => { const x = el('span', '', n); x.textContent = ch === ' ' ? ' ' : ch; x.style.opacity = 0; return x; });
    K.typeIn(sp, t0, Math.min(.04, (b - t0 - .2) / Math.max(1, sp.length))); sfx(t0, 'pro_typing_run/tick', -16, { dur: +(sp.length * .035).toFixed(2), align: 'start' }); }
}

// ================================================================== Words: one idea per beat
BL.Words = (box, c, T, S) => {
  const shots = c.shots || []; const ends = shotEnds(shots, T, S);
  if (c.charge && shots.length) {         // a point charges before the first hit
    const a = S.start, b = ends[0][0]; const dot = el('div', 'charge', box); K.vis(dot, a, b);
    tl.fromTo(dot, { scale: .2 }, { scale: 1.6, duration: Math.max(.1, b - a), ease: 'power2.in', immediateRender: false }, a);
    for (let t = a; t < b - .05; t += B / 2) K.ring(t, 'accent', W / 2, H / 2, 20, 260);
    sfx(a, 'riser/snatch', -14, { dur: +Math.max(.3, b - a).toFixed(2) });
  }
  shots.forEach((s, i) => {
    const [a, b] = ends[i]; const sh = layer(box, a, b); s.text_ = Array.isArray(s.text) ? s.text.join(' ') : s.text;
    if (s.ground) K.ground(a, s.ground); else if (i === 0 && c.ground) K.ground(a, c.ground);
    const g = s.ground || c.ground; const style = s.style || 'slam'; const sec = (s.second ?? 1) * B;
    let word;
    if (style === 'slam') {
      if (s.echo !== false) K.ghosts(sh, s.text_, a, b, { c: readable(g), size: 200, gap: 230, rows: 3 });
      word = big(sh, s.text_, { ...s, ground: g }); fitBig(word, s);
      const ls = letters(word.querySelector('.fitw') || word, s.text_); const r = rng(Math.round(a * 50));
      if (s.tumble !== false) ls.forEach((L, k) => tl.fromTo(L, { y: -500 - r() * 300, rotation: (r() - .5) * 120, scale: s.from || 1.6, opacity: 0 },
        { y: 0, rotation: 0, scale: 1, opacity: 1, duration: .22, ease: 'back.out(1.6)', immediateRender: false }, a + k * .025));
      else tl.fromTo(word, { scale: s.from || 2.4, opacity: 0 }, { scale: 1, opacity: 1, duration: .14, ease: 'power4.out', immediateRender: false }, a);
      K.drift(word, a + .25, b, 1.05, -.6);
    } else if (style === 'punch3d') {
      const stage = el('div', 'p3d', sh); const g3 = K.extrude(stage, s.text_, { size: s.size || 210, face: s.color || readable(g), wdth: s.wdth ?? 100, layers: 20, depth: 7 });
      const echoes = [1, 2, 3].map(k => { const e = el('div', 'echo', stage); e.textContent = s.text_; e.style.fontSize = (s.size || 210) + 'px'; e.style.webkitTextStroke = `3px ${readable(g)}`;
        tl.fromTo(e, { z: -400 * k, opacity: 0 }, { z: -150 * k, opacity: .35 / k, duration: .3, ease: 'power3.out', immediateRender: false }, a + .04 * k); return e; });
      tl.fromTo(g3, { z: -2200, rotationX: 35, rotationY: -25 }, { z: 0, rotationX: 0, rotationY: 0, duration: .32, ease: 'expo.out', immediateRender: false }, a);
      tl.to(g3, { rotationY: 14, rotationX: -6, duration: Math.max(.2, b - a - .3), ease: 'sine.inOut' }, a + .3);
      word = g3;
    } else if (style === 'stack') {
      const [k1, w2] = s.text; const kick = big(sh, k1, { ...s, ground: g, size: 120, y: H / 2 - 330, wdth: 125, wght: 800 }); fit(kick, 900, 220, 160);
      word = big(sh, w2, { ...s, ground: g, y: H / 2 + 60 }); fitBig(word, s);
      const bar = el('div', 'kbar', sh); bar.style.background = col(s.bar || 'accent');
      tl.fromTo(kick, { x: -900 }, { x: 0, duration: .18, ease: 'expo.out', immediateRender: false }, a);
      tl.fromTo(word, { scale: 2.6, opacity: 0 }, { scale: 1, opacity: 1, duration: .14, ease: 'power4.out', immediateRender: false }, a + sec);
      tl.fromTo(bar, { scaleX: 0 }, { scaleX: 1, duration: .2, ease: 'expo.out', immediateRender: false }, a + sec + .05);
      sfx(a + sec, 'cut_hit/punch', -12); K.drift(sh, a, b, 1.04, .5);
    } else if (style === 'pair') {
      const [l1, l2] = s.text; const w1 = big(sh, l1, { ...s, ground: g, y: H / 2 - 190 }); fit(w1, 980, 360, 520);
      word = big(sh, l2, { ...s, ground: g, y: H / 2 + 190, color: s.color2 || s.color }); fit(word, 980, 360, 520);
      tl.fromTo(w1, { x: -1300 }, { x: 0, duration: .2, ease: 'expo.out', immediateRender: false }, a);
      tl.fromTo(word, { x: 1300 }, { x: 0, duration: .2, ease: 'expo.out', immediateRender: false }, a + sec);
      sfx(a, 'whoosh_fast/crisp', -13); sfx(a + sec, 'whoosh_fast/crisp', -12); K.drift(sh, a, b, 1.04, -.5);
    } else if (style === 'split') {
      const [sm, bg] = s.text; const w1 = big(sh, sm, { ...s, ground: g, size: 130, y: H / 2 - 360, wdth: 100, wght: 700 }); fit(w1, 900, 200, 150);
      w1.style.textAlign = 'left'; w1.style.left = '60px';
      word = big(sh, bg, { ...s, ground: g, y: H / 2 + 40 }); fitBig(word, s);
      tl.fromTo(w1, { opacity: 0, y: -40 }, { opacity: 1, y: 0, duration: .16, ease: 'power3.out', immediateRender: false }, a);
      tl.fromTo(word, { x: 1400, skewX: -18 }, { x: 0, skewX: 0, duration: .16, ease: 'expo.out', immediateRender: false }, a + sec);
      sfx(a + sec, 'cut_hit/punch', -11); K.drift(sh, a, b, 1.05, .6);
    } else {   // cut: a hard-cut word for runs of beat cuts
      word = big(sh, s.text_, { ...s, ground: g }); fitBig(word, s); if (s.rgb) K.glitch(word, a, a + .2, Math.round(a * 7));
      tl.fromTo(word, { scale: 1.12 }, { scale: 1, duration: .2, ease: 'power3.out', immediateRender: false }, a);
    }
    if (s.dy) word.style.marginTop = s.dy + 'px';
    enter(sh, a, s.in);
    const fxk = s.fx ?? (style === 'cut' ? 'beat' : 'punch');
    if (fxk !== 'none') K.fx(a + (['stack', 'split', 'pair'].includes(style) ? sec : 0), fxk, { big: s.big });
    if (s.cue) sfx(a, s.cue, s.gain ?? -10);
    extras(sh, word, { ...s, ground: g }, a, b, T);
  });
  if (c.exit) { const t = T(c.exit.at); if (c.exit.type === 'flash') K.flash(t, '#fff', .2, 1); else K.whipOut(S.end, 'x', -1); }
};

// ================================================================== Strike: "NO <thing>." over a mock of it, then it dies
function mock(parent, ui = {}) {
  const m = el('div', 'mock', parent); const bar = el('div', 'mbar mono', m, `<i></i><i></i><i></i><span>${esc(ui.title || '')}</span><em>${esc(ui.tag || '')}</em>`); const body = el('div', 'mbody', m);
  if (ui.type === 'timeline') { for (let r = 0; r < 4; r++) { const row = el('div', 'mrow', body); for (let k = 0; k < 6; k++) { const c = el('i', 'mclip', row); c.style.width = (60 + ((r * 7 + k * 13) % 9) * 14) + 'px'; } }
    const pb = el('div', 'mprog', body); el('b', '', pb); }
  else if (ui.type === 'tiles') { const g = el('div', 'mtiles', body); (ui.tiles || [['ONE', '◆', 'v1.0'], ['TWO', '●', 'v2.1'], ['THREE', '▲', 'v3.2'], ['FOUR', '■', 'v1.4']]).forEach(t => el('div', 'mtile', g, `<b>${esc(t[1])}</b><span>${esc(t[0])}</span><em>${esc(t[2] || '')}</em>`)); }
  else if (ui.type === 'rack') { (ui.rows || ['NODE 01', 'NODE 02', 'NODE 03']).forEach(r => el('div', 'mrack mono', body, `<i></i><i></i><span>${esc(r)}</span><b></b>`)); }
  else if (ui.type === 'image' && ui.src) { el('img', 'mimg', body).src = ui.src; }
  else { (ui.lines || ['loading…', 'please wait', 'still loading…']).forEach(l => el('div', 'mline mono', body, esc(l))); }
  return m;
}
BL.Strike = (box, c, T, S) => {
  const its = c.items || []; const ends = shotEnds(its, T, S);
  its.forEach((it, i) => {
    const [a, b] = ends[i]; const sh = layer(box, a, b); const g = it.ground || c.ground || 'bg'; K.ground(a, g);
    const m = mock(sh, it.ui); m.style.top = '360px';
    tl.fromTo(m, { y: 140, opacity: 0, rotation: -3 }, { y: 0, opacity: 1, rotation: 0, duration: .22, ease: 'back.out(1.5)', immediateRender: false }, a);
    const no = big(sh, 'NO', { ground: g, size: 150, y: 1160, wdth: 125, color: 'accent' }); const w = big(sh, it.word, { ground: g, y: 1380 }); fit(w, 980, 280, 300);
    tl.fromTo(no, { scale: 2, opacity: 0 }, { scale: 1, opacity: 1, duration: .12, ease: 'power4.out', immediateRender: false }, a + .1);
    tl.fromTo(w, { x: -1200 }, { x: 0, duration: .16, ease: 'expo.out', immediateRender: false }, a + .14);
    const t1 = a + Math.min((b - a) * .55, 1.6 * B);   // the strike lands, the mock dies
    const sl = el('div', 'strike', sh); sl.style.top = '620px';
    tl.fromTo(sl, { scaleX: 0 }, { scaleX: 1, duration: .12, ease: 'power4.out', immediateRender: false }, t1);
    tl.to(m, { y: 900, rotation: 18, opacity: 0, duration: Math.max(.2, b - t1 - .05), ease: 'power3.in' }, t1 + .08);
    K.glitch(m, t1, t1 + .12, Math.round(a * 19)); K.shake(t1, 16); sfx(t1, 'swish/blade', -10); sfx(t1 + .02, 'glitch/hit', -13); sfx(t1 + .1, 'downlifter/tape', -16, { dur: .6 });
    K.drift(w, a + .3, b, 1.06, -.5);
  });
};

// ================================================================== Graph: comets draw the axes, the camera rides the curve
BL.Graph = (box, c, T, S) => {
  const a = S.start, b = S.end, g = c.ground || 'paper'; K.ground(a, g); const ink = readable(g); const sh = layer(box, a, b);
  const ox = 140, oy = 1420, x1 = 950, y1 = 520; const world = el('div', 'gworld', sh);
  K.comet(world, `M${ox} ${oy} L${ox} ${y1}`, a + .05, .35 * B * 2, ink === P.ink ? 'ink' : 'paper', 6);
  K.comet(world, `M${ox} ${oy} L${x1} ${oy}`, a + .05, .35 * B * 2, ink === P.ink ? 'ink' : 'paper', 6);
  const pts = []; for (let k = 0; k <= 40; k++) { const u = k / 40; pts.push([ox + (x1 - ox) * u, oy - (oy - y1 - 40) * (c.curve === 'linear' ? u : (Math.exp(u * 3.2) - 1) / (Math.exp(3.2) - 1))]); }
  const t0 = a + B * 1.2, dur = Math.max(.5, (b - a) - B * 2.2);
  const cm = K.comet(world, 'M' + pts.map(p => p.join(' ')).join(' L'), t0, dur, 'accent', 12);
  (c.ticks || []).forEach((tk, k, arr) => { const x = ox + (x1 - ox) * (k + 1) / arr.length; const e = el('div', 'gtick mono', world, esc(tk)); e.style.left = (x - 60) + 'px'; e.style.top = (oy + 24) + 'px'; e.style.color = ink;
    tl.fromTo(e, { opacity: 0 }, { opacity: .7, duration: .1, immediateRender: false }, a + .2 + k * .05); });
  const o = { k: 0 }; tl.fromTo(o, { k: 0 }, { k: 1, duration: dur, ease: 'power2.inOut', immediateRender: false, onUpdate: () => {
    const p = cm.at(o.k); world.style.transform = `translate(${(W / 2 - p.x) * .35}px,${(H / 2 - p.y) * .35}px) scale(${1 + o.k * .12})`; } }, t0);
  const num = big(sh, c.number || '0', { ground: g, size: 330, y: 360, wdth: 70 }); const lab = el('div', 'glab', sh, esc(c.label || '')); lab.style.color = ink;
  const sub = el('div', 'gsub mono', sh, esc(c.sub || '')); sub.style.color = ink;
  tl.fromTo(num, { scale: 2, opacity: 0 }, { scale: 1, opacity: 1, duration: .16, ease: 'power4.out', immediateRender: false }, a + .1);
  tl.fromTo([lab, sub], { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .2, stagger: .08, immediateRender: false }, a + .25);
  if (/^\d+$/.test(String(c.number))) { const n = +c.number, cnt = { v: 0 }; tl.fromTo(cnt, { v: 0 }, { v: n, duration: dur, ease: 'power2.in', immediateRender: false,
    onUpdate: () => { num.textContent = Math.round(cnt.v).toLocaleString('en-US'); } }, t0); }
  sfx(t0, 'pro_riser/air_gate', -15, { dur: +dur.toFixed(2) }); K.fx(t0 + dur, 'hit');
  if (c.portal) { tl.to(sh, { scale: 9, opacity: 0, duration: .25, ease: 'power3.in', transformOrigin: '50% 20%' }, b - .25); sfx(b - .25, 'whoosh_big/thump_airy', -12); }
};

// ================================================================== Hero: the title flies out of depth and orbits
BL.Hero = (box, c, T, S) => {
  const a = S.start, b = S.end, g = c.ground || 'bg'; K.ground(a, g); const sh = layer(box, a, b); const ink = readable(g);
  if (c.kicker) { const k = big(sh, c.kicker, { ground: g, size: 90, y: 560, wdth: 125, wght: 700 }); k.style.letterSpacing = '.12em'; fit(k, 820, 140, 110);
    letters(k.querySelector('.fitw') || k, c.kicker).forEach((L, i) => tl.fromTo(L, { rotationX: -90, opacity: 0 }, { rotationX: 0, opacity: 1, duration: .2, ease: 'back.out(2)', immediateRender: false }, a + i * .03)); }
  const sp = []; for (let k = 0; k <= 60; k++) { const u = k / 60, r = 700 * (1 - u), ang = u * Math.PI * 4; sp.push([W / 2 + Math.cos(ang) * r, H / 2 + Math.sin(ang) * r * 1.2]); }
  K.comet(sh, 'M' + sp.map(p => p.map(v => v.toFixed(1)).join(' ')).join(' L'), a + .1, B * 1.6, 'accent', 8, false);
  const stage = el('div', 'p3d', sh); const g3 = K.extrude(stage, c.title, { size: c.size || 230, face: c.color || (ink === P.paper ? 'paper' : 'ink'), wdth: c.wdth ?? 112, layers: 26, depth: 8, glow: g === 'bg' ? 26 : 0 });
  const tf = a + B * 1.6;
  tl.fromTo(g3, { z: -3000, rotationY: 70, rotationX: 20, opacity: 0 }, { z: 0, rotationY: -28, rotationX: 6, opacity: 1, duration: .5, ease: 'expo.out', immediateRender: false }, tf);
  tl.to(g3, { rotationY: 22, rotationX: -8, duration: Math.max(.3, (b - tf) * .5), ease: 'sine.inOut' }, tf + .5);
  tl.to(g3, { rotationY: 0, rotationX: 0, duration: .3, ease: 'power3.out' }, Math.max(tf + .8, b - .9));
  K.fx(tf + .1, 'punch', { big: true }); sfx(tf - .3, 'whoosh_big/swell', -12);
  if (c.landZoom) tl.fromTo(stage, { scale: 1 }, { scale: c.landZoom, duration: .5, ease: 'power3.in', immediateRender: false }, b - .5);
  if (c.sub) { const sb = el('div', 'hsub mono', sh); sb.style.color = ink; const txt = (c.chevron || '') + c.sub;
    const ss = [...txt].map(ch => { const x = el('span', '', sb); x.textContent = ch === ' ' ? ' ' : ch; x.style.opacity = 0; return x; });
    const t0 = tf + .6; K.typeIn(ss, t0, .035); sfx(t0, 'pro_typing_run/glass', -16, { dur: +(ss.length * .035).toFixed(2), align: 'start' }); }
  if (c.whipOut) K.whipOut(b, 'x', -1);
};

// ================================================================== Prompt: a comet draws the box, the brief types, keywords light up
BL.Prompt = (box, c, T, S) => {
  const a = S.start, b = S.end, g = c.ground || 'paper'; K.ground(a, g); const sh = layer(box, a, b); const ink = readable(g);
  const world = el('div', 'pworld', sh); const bx = 70, by = 560, bw = 940, bh = 720, r = 34;
  K.comet(world, `M${bx + r} ${by} H${bx + bw - r} Q${bx + bw} ${by} ${bx + bw} ${by + r} V${by + bh - r} Q${bx + bw} ${by + bh} ${bx + bw - r} ${by + bh} H${bx + r} Q${bx} ${by + bh} ${bx} ${by + bh - r} V${by + r} Q${bx} ${by} ${bx + r} ${by}`,
    a, B * 1.2, ink === P.ink ? 'ink' : 'paper', 5);
  const lab = el('div', 'plab mono', world, esc(c.label || 'BRIEF.md')); lab.style.color = ink;
  const txt = el('div', 'ptxt mono', world); txt.style.color = ink; const spans = []; const kws = [];
  (c.text || []).forEach(([s, kw]) => { const holder = kw ? el('span', 'pkw', txt) : txt; if (kw) { el('b', '', holder); kws.push(holder); }
    s.split(/( )/).forEach(tok => { if (!tok) return; const wd = el('span', 'pw', holder); [...tok].forEach(ch => { const x = el('span', '', wd); x.textContent = ch === ' ' ? ' ' : ch; x.style.opacity = 0; spans.push(x); }); }); });
  const caret = el('i', 'pcaret', txt);
  const t0 = a + B * 1.2, t1 = Math.max(t0 + .5, b - B * 2.2), per = (t1 - t0) / Math.max(1, spans.length);
  K.typeIn(spans, t0, per); sfx(t0, 'pro_typing_run/standard', -15, { dur: +(t1 - t0).toFixed(2), align: 'start' });
  for (let t = a; t < b; t += .25) tl.set(caret, { opacity: Math.round((t - a) / .25) % 2 ? 0 : 1 }, t);
  // the camera follows the caret: the text block slides up as lines fill
  tl.fromTo(world, { y: 120, scale: 1.12 }, { y: -40, scale: 1, duration: t1 - a, ease: 'none', immediateRender: false, transformOrigin: '50% 40%' }, a);
  kws.forEach((k, i) => { const t = t1 + i * B * .5; tl.fromTo(k.querySelector('b'), { scaleX: 0 }, { scaleX: 1, duration: .14, ease: 'power3.out', immediateRender: false }, t);
    tl.set(k, { color: '#fff' }, t + .04); sfx(t, 'mallet/marimba', -12);
    if (c.doodles) { const d = el('i', 'pdoodle', k); tl.fromTo(d, { clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0% 0 0)', duration: .2, immediateRender: false }, t + .1); } });
  if (c.unit) { const u = el('div', 'punit mono', world); u.style.color = ink; const o = { v: 0 };
    tl.fromTo(o, { v: 0 }, { v: spans.length, duration: t1 - t0, ease: 'none', immediateRender: false, onUpdate: () => { u.textContent = Math.round(o.v) + ' ' + c.unit; } }, t0); }
};

// ================================================================== Stretch: a word on the width axis, elastic
BL.Stretch = (box, c, T, S) => {
  const a = S.start, b = S.end, sh = layer(box, a, b); (c.grounds || [[0, c.ground || 'accent']]).forEach(([k, gg]) => { K.ground(a + k * B, gg); });
  const g0 = (c.grounds || [[0, c.ground || 'accent']])[0][1];
  if (c.code) K.codeWall(sh, a, b, { c: readable(g0), opacity: .1 });
  const w = big(sh, c.word, { ground: g0, wdth: 125 }); fit(w, 860, 640, 640); const fs = parseFloat(w.style.fontSize);
  (c.grounds || []).slice(1).forEach(([k, gg]) => tl.set(w, { color: readable(gg) }, a + k * B));
  const seg = (b - a - .2) / 5, v = (wd, wg) => `"wdth" ${wd}, "wght" ${wg}`;
  tl.fromTo(w, { y: -1400, fontVariationSettings: v(62, 900) }, { y: 0, duration: .16, ease: 'power4.in', immediateRender: false }, a); K.fx(a + .16, 'hit'); sfx(a + .16, 'cut_hit/sub', -10);
  tl.to(w, { fontVariationSettings: v(125, 900), duration: seg, ease: 'elastic.out(1, .35)' }, a + .2);             // elastic stretch
  tl.to(w, { fontVariationSettings: v(125, 300), duration: seg * .5, ease: 'power2.inOut', yoyo: true, repeat: 1 }, a + .2 + seg);   // weight dip
  tl.to(w, { fontVariationSettings: v(62, 900), scaleY: 1.25, duration: seg * .6, ease: 'power3.out' }, a + .2 + seg * 2);           // squeeze
  tl.to(w, { fontVariationSettings: v(125, 900), scaleY: 1, duration: seg, ease: 'elastic.out(1, .4)' }, a + .2 + seg * 3);         // stretch
  tl.to(w, { scale: 1.12, duration: seg, ease: 'none' }, a + .2 + seg * 4);
  [1, 2, 3].forEach(k => sfx(a + .2 + seg * k, k === 2 ? 'fit/whoosh.short/bamboo_swish' : 'pro_zip/arc', -14));
};

// ================================================================== Fly: the camera flies through words in portals
BL.Fly = (box, c, T, S) => {
  const a = S.start, b = S.end, sh = layer(box, a, b, 'shot fly'); const ws = c.words || []; const gap = 1800;
  const rig = el('div', 'frig', sh);
  ws.forEach(([w, gg], i) => { const node = el('div', 'fnode', rig); node.style.transform = `translateZ(${-i * gap}px)`;
    const portal = el('div', 'portal', node); portal.style.borderColor = col(gg === 'accent' ? 'paper' : 'accent');
    const g3 = K.extrude(node, w, { size: 210, face: gg === 'accent' ? 'ink' : 'paper', wdth: 112, layers: 16, depth: 8 }); });
  const n = ws.length, per = (b - a) / Math.max(1, n);
  tl.fromTo(rig, { z: -900 }, { z: (n - 1) * gap + 900, duration: b - a, ease: 'none', immediateRender: false }, a);
  tl.fromTo(rig, { rotationZ: -6 }, { rotationZ: 6, duration: per, ease: 'sine.inOut', yoyo: true, repeat: Math.max(0, n * 1 - 1), immediateRender: false }, a);
  ws.forEach(([w, gg], i) => { const t = a + i * per; K.ground(t, gg === 'accent' ? 'accent' : (gg || 'bg')); sfx(t + per * .7, 'whoosh_big/jet', -14); if (i) K.fx(t, 'beat'); });
};

// ================================================================== Notes: notes typed in a panel change the preview
BL.Notes = (box, c, T, S) => {
  const a = S.start, b = S.end, g = c.ground || 'bg'; K.ground(a, g); const sh = layer(box, a, b); const ink = readable(g);
  const prev = el('div', 'nprev', sh); el('div', 'mbar mono', prev, `<i></i><i></i><i></i><span>${esc(c.file || 'preview')}</span><em>${esc(c.tag || 'LIVE')}</em>`);
  const pw = el('div', 'npw', prev); const word = big(pw, c.preview || 'FILM.', { ground: 'accent', size: 200, y: 200 }); fit(word, 760, 300, 260); pw.style.background = col('accent');
  const panel = el('div', 'npanel mono', sh); panel.style.color = ink; el('div', 'nph', panel, esc(c.panel || 'NOTES'));
  const tlx = el('div', 'ntl', sh); const segs = (c.segments || [['INTRO', 220], ['BUILD', 300], ['DROP', 260], ['END', 160]]).map(([nm, wd]) => { const s = el('div', 'nseg mono', tlx, esc(nm)); s.style.width = wd + 'px'; return s; });
  const notes = c.notes || []; const per = (b - a - .4) / Math.max(1, notes.length);
  tl.fromTo([prev, panel, tlx], { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: .25, stagger: .06, ease: 'power3.out', immediateRender: false }, a);
  notes.forEach(([txt, act], i) => { const t0 = a + .3 + i * per; const row = el('div', 'nrow', panel); el('b', '', row, '•');
    const sp = [...txt].map(ch => { const x = el('span', '', row); x.textContent = ch === ' ' ? ' ' : ch; x.style.opacity = 0; return x; });
    const tt = Math.min(per * .5, sp.length * .03); K.typeIn(sp, t0, tt / Math.max(1, sp.length)); sfx(t0, 'pro_typing_run/tick', -16, { dur: +tt.toFixed(2), align: 'start' });
    const ta = t0 + tt + .1; tl.set(row, { color: col('accent') }, ta); sfx(ta, 'ui_pop/step', -13);
    tl.to(sh, { y: i % 2 ? -60 : 40, duration: per * .8, ease: 'power2.inOut' }, t0);   // the camera moves between panel, preview, timeline
    if (act === 'recolor') { tl.to(pw, { backgroundColor: col('hot') || '#ff8a1f', duration: .2 }, ta); tl.set(word, { color: P.ink }, ta); }
    else if (act === 'trim') { tl.to(segs[0], { width: parseFloat(segs[0].style.width) / 2, duration: .3, ease: 'power3.inOut' }, ta); }
    else if (act === 'punch') { tl.fromTo(word, { scale: 1.4 }, { scale: 1, duration: .3, ease: 'back.out(2)', immediateRender: false }, ta); K.fx(ta, 'beat'); }
    else if (act === 'flip') { tl.to(pw, { backgroundColor: P.ink, duration: .15 }, ta); tl.set(word, { color: P.paper }, ta); } });
};

// ================================================================== Counters: giant numbers on slot reels over the source
function slot(parent, value, size) { const wrap = el('div', 'slots', parent); const reels = [];
  [...String(value)].forEach((ch, k) => { const r = el('div', 'reel', wrap); r.style.height = size + 'px'; r.style.width = (/\d/.test(ch) ? size * .56 : size * .3) + 'px';
    const st = el('div', 'strip', r); if (/\d/.test(ch)) { const n = 20 + k * 10 + (+ch); for (let i = 0; i <= n; i++) { const d = el('div', '', st, String(i % 10)); d.style.height = size + 'px'; d.style.lineHeight = size + 'px'; d.style.fontSize = size * .92 + 'px'; } reels.push([st, n]); }
    else { const d = el('div', '', st, esc(ch)); d.style.height = size + 'px'; d.style.lineHeight = size + 'px'; d.style.fontSize = size * .92 + 'px'; } });
  return { wrap, reels }; }
BL.Counters = (box, c, T, S) => {
  const a = S.start, b = S.end, g = c.ground || 'bg'; K.ground(a, g); const sh = layer(box, a, b); const ink = readable(g);
  const plane = el('div', 'cplane mono', sh); plane.textContent = (c.source || D.source || '').split('\n').slice(0, 300).join('\n'); plane.style.color = ink;
  tl.fromTo(plane, { y: 400 }, { y: -1400, duration: b - a, ease: 'none', immediateRender: false }, a);
  if (c.title) { const tt = el('div', 'ctitle mono', sh, esc(c.title)); tt.style.color = ink; tl.fromTo(tt, { opacity: 0 }, { opacity: .8, duration: .2, immediateRender: false }, a); }
  const cs = c.counters || []; const per = (b - a) / Math.max(1, cs.length);
  cs.forEach(([v, lab], i) => { const a1 = a + i * per, b1 = i + 1 < cs.length ? a + (i + 1) * per : b; const grp = el('div', 'cgrp', sh); K.vis(grp, a1, b1);
    const sz = String(v).length > 5 ? 230 : String(v).length > 3 ? 300 : 420; const { wrap, reels } = slot(grp, v, sz); wrap.style.color = col(c.color || 'accent');
    reels.forEach(([st, n], k) => { tl.fromTo(st, { y: 0, filter: 'blur(8px)' }, { y: -n * sz, filter: 'blur(0px)', duration: Math.min(per * .7, .5 + k * .12), ease: 'power3.out', immediateRender: false }, a1); });
    const l = el('div', 'clab', grp, esc(lab)); l.style.color = ink; tl.fromTo(l, { opacity: 0, letterSpacing: '.5em' }, { opacity: 1, letterSpacing: '.08em', duration: .3, immediateRender: false }, a1 + .3);
    sfx(a1, 'pro_riser/roll', -16, { dur: .5 }); sfx(a1 + .55, 'pro_impact/air', -11); K.bump(a1 + .55, 1.04); if (i) K.whip(a1, 'y', 1, .12); });
};

// ================================================================== Progress: a line renders itself, frames ride a conveyor
BL.Progress = (box, c, T, S) => {
  const a = S.start, b = S.end, g = c.ground || 'paper'; K.ground(a, g); const sh = layer(box, a, b); const ink = readable(g);
  const [l1, l2] = c.lines || ['RENDERED', 'IN CODE.'];
  const o1 = big(sh, l1, { ground: g, y: 560, wdth: 112 }); fit(o1, 980, 260, 280); o1.style.color = 'transparent'; o1.style.webkitTextStroke = `3px ${ink}`; o1.style.fontFamily = 'AS';
  const f1 = big(sh, l1, { ground: g, y: 560, wdth: 112 }); f1.style.fontSize = o1.style.fontSize; f1.style.fontFamily = 'AS';
  const scan = el('div', 'scan', sh); scan.style.top = '440px';
  tl.fromTo(o1, { opacity: 0 }, { opacity: 1, duration: .15, immediateRender: false }, a);
  const ts = a + .3, te = a + .3 + B * 2; tl.fromTo(f1, { clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0% 0 0)', duration: te - ts, ease: 'none', immediateRender: false }, ts);
  tl.fromTo(scan, { x: 0, opacity: 1 }, { x: 980, duration: te - ts, ease: 'none', immediateRender: false }, ts); tl.set(scan, { opacity: 0 }, te);
  sfx(ts, 'pro_riser/nblips_hi', -16, { dur: +(te - ts).toFixed(2) });
  const w2 = big(sh, l2, { ground: g, y: 820, color: 'accent' }); fit(w2, 980, 280, 300);
  tl.fromTo(w2, { scale: 2.5, opacity: 0 }, { scale: 1, opacity: 1, duration: .14, ease: 'power4.out', immediateRender: false }, te); K.fx(te, 'punch', { c: 'accent' });
  const belt = el('div', 'belt', sh); (c.cards || [['EVERY', 'bg', 'paper'], ['FRAME', 'accent', 'ink'], ['IS', 'bg', 'paper'], ['CODE.', 'accent', 'ink'], ['EVERY', 'bg', 'paper'], ['FRAME', 'accent', 'ink']]).forEach(([w, bg, fg]) => {
    const cd = el('div', 'bcard', belt, esc(w)); cd.style.background = col(bg); cd.style.color = col(fg); });
  tl.fromTo(belt, { x: 300 }, { x: -1100, duration: b - a, ease: 'none', immediateRender: false }, a);
  const pb = el('div', 'pbar', sh); const fill = el('b', '', pb); const pl = el('div', 'plabel mono', sh); pl.style.color = ink; const pr = el('div', 'pright mono', sh); pr.style.color = ink;
  const o = { v: 0 }; tl.fromTo(o, { v: 0 }, { v: 100, duration: Math.max(.4, b - a - .5), ease: 'power1.inOut', immediateRender: false,
    onUpdate: () => { fill.style.transform = `scaleX(${o.v / 100})`; pr.textContent = Math.round(o.v) + '%'; pl.textContent = o.v >= 99.5 ? (c.doneLabel || 'DONE') : (c.label || 'RENDERING'); if (o.v >= 99.5 && c.doneRight) pr.textContent = c.doneRight; } }, a);
  sfx(b - .45, 'pro_notify/ding_2167', -12);
};

// ================================================================== Chain: three words far apart, the camera rides a comet between them
BL.Chain = (box, c, T, S) => {
  const a = S.start, b = S.end, g = c.ground || 'bg'; K.ground(a, g); const sh = layer(box, a, b); const ink = readable(g);
  const nodes = c.nodes || []; const gap = c.gap || 1500; const world = el('div', 'cworld', sh);
  const pos = nodes.map((n, i) => [i % 2 ? 680 : 400, 900 + i * gap]);
  const d = 'M' + pos.map(p => p.join(' ')).join(' L'); const per = (b - a - .3) / Math.max(1, nodes.length);
  const ts = nodes.map((_, i) => c.at && c.at[i] != null ? T(c.at[i]) : a + .1 + i * per);   // at: when each node lands (on its word)
  const cm = K.comet(world, d, ts[0] + .1, Math.max(.2, ts[ts.length - 1] - ts[0] - .1), 'accent', 10);
  nodes.forEach(([w, sub, cc], i) => { const [x, y] = pos[i]; const n = el('div', 'cnode', world); n.style.left = '0px'; n.style.top = (y - 160) + 'px';
    const ww = big(n, w, { ground: g, color: cc || null, y: 160 }); fit(ww, 900, 260, 280); const sb = el('div', 'csub mono', n, esc(sub || '')); sb.style.color = ink;
    const t = ts[i]; K.vis(n, t - .02, b);
    if (c.marks && c.marks[i]) { const mk = el('div', 'cmark', n, c.marks[i]); mk.style.color = ink; tl.fromTo(mk, { scale: 0, rotation: -30 }, { scale: 1, rotation: 0, duration: .26, ease: 'back.out(2.2)', immediateRender: false }, t + .03); } tl.fromTo(ww, { scale: 2.2, opacity: 0 }, { scale: 1, opacity: 1, duration: .14, ease: 'power4.out', immediateRender: false }, t);
    tl.fromTo(sb, { opacity: 0 }, { opacity: .8, duration: .2, immediateRender: false }, t + .12); K.fx(t, i === nodes.length - 1 ? 'punch' : 'hit'); });
  tl.set(world, { y: 0 }, a); ts.forEach((t, i) => { if (!i) return; const s0 = Math.max(ts[i - 1] + .12, t - .3); tl.to(world, { y: -i * gap, duration: Math.max(.1, t - s0), ease: 'power3.inOut' }, s0); });
  tl.to(world, { y: '-=60', duration: Math.max(.2, b - ts[ts.length - 1]), ease: 'none' }, ts[ts.length - 1] + .05);
};

// ================================================================== Rewind: the film so far plays backwards in a tilting window
// The window's contents are composited at render time (compose.py) from the frames already rendered.
BL.Rewind = (box, c, T, S) => {
  const a = S.start, b = S.end, g = c.ground || 'bg'; K.ground(a, g); const sh = layer(box, a, b);
  const win = el('div', 'rwin', sh); win.id = 'rewind' + S.i; el('div', 'mbar mono', win, `<i></i><i></i><i></i><span>${esc(c.label || 'PLAYBACK')}</span><em>◀◀</em>`);
  const scr = el('div', 'rscr', win); scr.dataset.rewind = JSON.stringify({ a, b, from: c.from ?? a });
  tl.fromTo(win, { scale: .5, rotation: -8, opacity: 0 }, { scale: .82, rotation: 3, opacity: 1, duration: .3, ease: 'back.out(1.5)', immediateRender: false }, a);
  tl.to(win, { rotation: -3, duration: (b - a) * .6, ease: 'sine.inOut' }, a + .3);
  tl.to(win, { scale: 1.9, rotation: 0, duration: .35, ease: 'power3.in' }, b - .35);
  sfx(a, 'reverse_swell/cymbal', -13); sfx(a + .2, 'downlifter/shepard_fall', -18, { dur: +(b - a - .2).toFixed(2) });
};

// ================================================================== Picture: key art or a screenshot, pushed, panned, punched in
const rv0 = c => (c.reveal || 'slash') === 'none';   // on screen from frame 1
BL.Picture = (box, c, T, S) => {
  const a = S.start, b = S.end, sh = layer(box, a, b, 'shot pic'); K.ground(a, c.ground || 'bg');
  // device: "phone" puts the picture on a realistic phone (titanium frame, Dynamic Island, side buttons) floating over a
  // blurred, darkened copy of itself; reveals, push/pan and cut-ins then happen on the phone's screen.
  let host = sh, phone = null;
  if (c.device === 'phone') {
    const bg = el('div', 'pbgblur', sh); bg.style.backgroundImage = `url(${c.poster || c.src})`;
    tl.fromTo(bg, { scale: 1.25 }, { scale: 1.35, duration: b - a, ease: 'none', immediateRender: false }, a);
    phone = el('div', 'phone', sh); const pw = c.phoneWidth || 650; phone.style.width = pw + 'px'; phone.style.height = Math.round(pw * 2.12) + 'px';
    phone.style.left = Math.round((W - pw) / 2) + 'px'; phone.style.top = (c.phoneTop ?? 170) + 'px';
    ['b1', 'b2', 'b3', 'b4'].forEach(k => el('i', 'pbtn ' + k, phone));
    const scr = el('div', 'pscreen', phone); el('div', 'pisland', phone); el('div', 'pglare', phone); host = scr;
    const en = c.enter || 'rise';
    if (en === 'rise') tl.fromTo(phone, { y: 700, rotation: -9, opacity: 0 }, { y: 0, rotation: -2, opacity: 1, duration: .42, ease: 'back.out(1.3)', immediateRender: false }, a);
    else if (en === 'swing') tl.fromTo(phone, { rotationY: -70, x: -300, opacity: 0 }, { rotationY: 0, x: 0, rotation: -2, opacity: 1, duration: .4, ease: 'power3.out', immediateRender: false }, a);
    else tl.set(phone, { rotation: -2 }, a);
    tl.to(phone, { rotation: 1.5, y: -14, duration: Math.max(.3, b - a - .4), ease: 'sine.inOut' }, a + (en === 'keep' || en === 'none' ? 0 : .42));
    if (en !== 'keep' && en !== 'none') sfx(a, 'whoosh_fast/sleeve', -13);
  }
  // device: "browser" puts the clip in a browser window: tabs dot row, a URL pill (`url`), a soft reflection under it
  if (c.device === 'browser') {
    const bg = el('div', 'pbgblur', sh); if (c.poster) bg.style.backgroundImage = `url(${c.poster})`;
    const pw = c.playerWidth || 940, ph = Math.round(pw / (c.aspect || 16 / 9)), top = c.playerTop ?? 380;
    const win = el('div', 'bwin', sh); win.style.width = pw + 'px'; win.style.left = Math.round((W - pw) / 2) + 'px'; win.style.top = top + 'px';
    el('div', 'bbar', win, `<i></i><i></i><i></i><span class="mono">${esc(c.url || 'localhost')}</span>`);
    const scr = el('div', 'plscreen', win); scr.style.height = ph + 'px'; host = scr;
    const en = c.enter || 'none';
    if (en === 'tilt') { tl.fromTo(win, { rotationX: 38, rotationZ: -6, y: 260, opacity: 0 }, { rotationX: 8, rotationZ: 0, y: 0, opacity: 1, duration: .45, ease: 'power4.out', immediateRender: false }, a); sfx(a, 'whoosh_fast/heavy', -12); }
    else tl.set(win, { rotationX: 8 }, a);
    tl.to(win, { rotationX: 2, scale: 1.03, duration: b - a, ease: 'sine.inOut' }, a + (en === 'tilt' ? .45 : 0));
    phone = win; c.wordsY = c.wordsY || (top + ph + 260);
  }
  // device: "player" puts the clip in a desktop video-player window (title bar, controls, a progress bar that runs)
  if (c.device === 'player') {
    const bg = el('div', 'pbgblur', sh); bg.style.backgroundImage = `url(${c.poster || c.src})`;
    tl.fromTo(bg, { scale: 1.25 }, { scale: 1.32, duration: b - a, ease: 'none', immediateRender: false }, a);
    const pw = c.playerWidth || 960, ph = Math.round(pw / (c.aspect || 1)), top = c.playerTop ?? 250;
    const win = el('div', 'player', sh); win.style.width = pw + 'px'; win.style.left = Math.round((W - pw) / 2) + 'px'; win.style.top = top + 'px';
    el('div', 'plbar', win, `<i></i><i></i><i></i><span>${esc(c.title || '')}</span>`);
    const scr = el('div', 'plscreen', win); scr.style.height = ph + 'px'; host = scr;
    const ctl = el('div', 'plctl', win, `<b>❚❚</b><div class="pltrack"><div class="plfill"></div><div class="plknob"></div></div><em class="mono">${esc(c.time || '')}</em>`);
    const fill = ctl.querySelector('.plfill'), knob = ctl.querySelector('.plknob'); const p0 = c.progress || [.08, .62];
    tl.fromTo(fill, { width: p0[0] * 100 + '%' }, { width: p0[1] * 100 + '%', duration: b - a, ease: 'none', immediateRender: false }, a);
    tl.fromTo(knob, { left: p0[0] * 100 + '%' }, { left: p0[1] * 100 + '%', duration: b - a, ease: 'none', immediateRender: false }, a);
    const en = c.enter || 'none';
    if (en === 'rise') { tl.fromTo(win, { y: 500, rotation: -4, opacity: 0 }, { y: 0, rotation: 0, opacity: 1, duration: .4, ease: 'back.out(1.3)', immediateRender: false }, a); sfx(a, 'whoosh_fast/sleeve', -13); }
    tl.fromTo(win, { rotationX: 0 }, { rotationX: 4, y: -10, duration: b - a, ease: 'sine.inOut', immediateRender: false }, a);
    phone = win; c.wordsY = c.wordsY || (top + ph + 230);
  }
  // device: "scope" puts the clip in a round sensor lens: tick ring that turns, crosshair, corner HUD text
  if (c.device === 'scope') {
    const sz = c.scopeSize || 940, top = c.scopeTop ?? 300, sc = el('div', 'scope', sh);
    sc.style.width = sc.style.height = sz + 'px'; sc.style.left = Math.round((W - sz) / 2) + 'px'; sc.style.top = top + 'px';
    const lens = el('div', 'slens', sc); host = lens;
    const ring = el('div', 'sring', sc, `<svg viewBox="0 0 200 200">${Array.from({ length: 72 }, (_, k) => `<line x1="100" y1="${k % 6 ? 3 : 0}" x2="100" y2="${k % 6 ? 7 : 11}" transform="rotate(${k * 5} 100 100)"/>`).join('')}</svg>`);
    el('div', 'scross', sc); const hud = el('div', 'shud mono', sh, esc(c.hud || 'LIVE · TRACKING')); hud.style.top = (top - 70) + 'px'; K.vis(hud, a, b);
    tl.fromTo(ring, { rotation: 0 }, { rotation: 40, duration: b - a, ease: 'none', immediateRender: false }, a);
    if ((c.enter || 'none') === 'iris') { tl.fromTo(sc, { scale: .2, opacity: 0 }, { scale: 1, opacity: 1, duration: .35, ease: 'back.out(1.4)', immediateRender: false }, a); sfx(a, 'whoosh_fast/crisp', -12); }
    phone = sc; c.wordsY = c.wordsY || (top + sz + 170);
  }
  const frame = el('div', 'pframe', host); let m;
  if (/\.(mp4|webm|mov)$/i.test(c.src)) { m = el('video', 'pimg', frame); m.src = c.src; m.muted = true; m.dataset.start = a; m.dataset.duration = b - a; m.dataset.mediaStart = c.mediaStart || 0; }
  else { m = el('img', 'pimg', frame); m.src = c.src; }
  if (c.fit === 'contain') m.style.objectFit = 'contain';
  const tint = el('div', 'ptint', frame); tint.style.background = phone ? 'none' : `linear-gradient(transparent 35%, rgba(0,0,0,${c.tint ?? .55}))`;
  if (phone) tl.fromTo(frame, { scale: c.zoom || 1.04 }, { scale: (c.zoom || 1.04) + .06, duration: b - a, ease: 'none', immediateRender: false }, a);   // a slow push on the screen
  else tl.fromTo(frame, { scale: 1.02, x: -20 }, { scale: 1.16, x: 30, duration: b - a, ease: 'none', immediateRender: false }, a);   // push + pan
  // blur: [px, at] starts out of focus (a backdrop for an overlay) and snaps into focus at `at`
  if (c.blur) { const [px, k] = c.blur, t = T(k); tl.set(m, { filter: `blur(${px}px) brightness(.55)` }, a);
    tl.to(m, { filter: 'blur(0px) brightness(1)', duration: .22, ease: 'power3.out' }, t); K.flash(t, '#fff', .06, .25); sfx(t, 'whoosh_fast/crisp', -12); }
  // overlay: {src, out, width} an image (a title or logo) over the picture: pops in at the start, flicks out fast at `out`
  if (c.overlay) { const o = c.overlay, ov = el('img', 'poverlay', sh); ov.src = o.src; const ow = o.width || 760; ov.style.width = ow + 'px';
    ov.style.left = Math.round((W - ow) / 2) + 'px'; ov.style.top = (o.top ?? 560) + 'px'; const t2 = T(o.out);
    tl.fromTo(ov, { scale: 1.18, opacity: rv0(c) ? 1 : 0 }, { scale: 1, opacity: 1, duration: .16, ease: 'power4.out', immediateRender: false }, a);
    tl.to(ov, { scale: 1.06, rotation: -2, duration: Math.max(.1, t2 - a - .1), ease: 'none' }, a + .16);
    tl.to(ov, { scale: 2.4, opacity: 0, duration: .12, ease: 'power3.in' }, t2); tl.set(ov, { visibility: 'hidden' }, t2 + .12); sfx(t2, 'whoosh_fast/sleeve', -11); }
  // tag: a small mono label under the words (a place, a source), types in after the reveal
  if (c.tag) { const g = el('div', 'ptag mono', sh, esc(c.tag)); g.style.top = ((c.wordsY || (phone ? 1680 : 1450)) + 150) + 'px';
    tl.fromTo(g, { opacity: 0, y: 14 }, { opacity: .9, y: 0, duration: .18, ease: 'power3.out', immediateRender: false }, a + .12); }
  const rv = c.reveal || 'slash';
  if (rv === 'slash') { tl.fromTo(frame, { clipPath: 'polygon(0 0, 0 0, 0 100%, 0 100%)' }, { clipPath: 'polygon(0 0, 120% 0, 100% 100%, -20% 100%)', duration: .22, ease: 'expo.out', immediateRender: false }, a); sfx(a, 'swish/blade', -11); }
  else if (rv === 'iris') { tl.fromTo(frame, { clipPath: 'circle(0% at 50% 50%)' }, { clipPath: 'circle(80% at 50% 50%)', duration: .3, ease: 'power3.out', immediateRender: false }, a); sfx(a, 'whoosh_fast/crisp', -12); }
  else if (rv === 'none') { /* on screen from the first frame (a hook) */ }
  else { tl.fromTo(frame, { clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0% 0)', duration: .25, ease: 'expo.out', immediateRender: false }, a); sfx(a, 'swipe/paper', -12); }
  // subs: [{start, end, words: [[at, word]]}] voice subtitles under the picture, the spoken word lit in an accent box
  (c.subs || []).forEach(L => { const t0 = T(L.start), t1 = T(L.end); const line = el('div', 'psub', sh); line.style.top = (c.subsY || c.wordsY || 1500) + 'px'; K.vis(line, t0, t1);
    const ws = L.words.map(([k, w]) => [T(k), el('span', 'psw', line, esc(w))]);
    ws.forEach(([t, e], i) => { const t2 = i + 1 < ws.length ? ws[i + 1][0] : t1;
      tl.fromTo(e, { opacity: .35 }, { opacity: 1, duration: .06, immediateRender: false }, t);
      tl.set(e, { backgroundColor: col('accent'), color: '#fff' }, t); tl.set(e, { backgroundColor: 'rgba(0,0,0,0)', color: '' }, t2); }); });
  (c.words || []).forEach(([k, w, cc], i, arr) => { const t = T(k), t2 = i + 1 < arr.length ? T(arr[i + 1][0]) : b; const e = big(sh, w, { ground: 'bg', color: cc || 'paper', y: c.wordsY || (phone ? 1680 : 1450) }); e.style.textShadow = '0 8px 30px rgba(0,0,0,.6)'; fit(e, c.wordsWidth || 880, 300, 320); K.vis(e, t, t2);
    tl.fromTo(e, { scale: 2, opacity: 0 }, { scale: 1, opacity: 1, duration: .13, ease: 'power4.out', immediateRender: false }, t);
    tl.fromTo(m, { scale: 1.07 }, { scale: 1, duration: .3, ease: 'power3.out', immediateRender: false }, t); sfx(t, 'cut_hit/punch', -12); K.shake(t, 10, .18); });
  (c.cutIns || []).forEach(([k, z, xy, snd]) => { const t = T(k); const [px, py] = xy || [.5, .5];
    tl.to(m, { scale: z || 1.6, transformOrigin: `${px * 100}% ${py * 100}%`, duration: .18, ease: 'expo.out' }, t); tl.to(m, { scale: 1, duration: .25, ease: 'power3.inOut' }, t + B * 1.2);
    K.flash(t, '#fff', .08, .4); sfx(t, snd || 'shutter/film', -11); });
  if (c.weather) { const s = K.svg(sh, 'svgl wx'); const r = rng(21); const n = c.weather === 'rain' ? 70 : 50;
    for (let i = 0; i < n; i++) { const x = r() * W, y0 = -200 - r() * 600, sp = c.weather === 'rain' ? 2600 : 600, len = c.weather === 'rain' ? 60 : 6;
      const e = c.weather === 'rain' ? K.sv('line', { x1: x, y1: 0, x2: x - 14, y2: len, stroke: 'rgba(255,255,255,.55)', 'stroke-width': 3 }, s) : K.sv('circle', { cx: x, cy: 0, r: c.weather === 'snow' ? 6 : 3, fill: 'rgba(255,255,255,.7)' }, s);
      tl.fromTo(e, { y: y0 }, { y: y0 + sp * (b - a) * (.8 + r() * .4), x: c.weather === 'rain' ? -120 : (r() - .5) * 120, duration: b - a, ease: 'none', immediateRender: false }, a); } }
};

// ================================================================== Logo: a line, a slash and a hit, the mark drops in, the name types
BL.Logo = (box, c, T, S) => {
  const a = S.start, b = S.end, g = c.ground || 'bg'; K.ground(a, g); const sh = layer(box, a, b); const ink = readable(g);
  const ln = el('div', 'lline', sh); ln.style.background = ink; tl.fromTo(ln, { scaleX: 0 }, { scaleX: 1, duration: .2, ease: 'expo.out', immediateRender: false }, a);
  const sl = el('div', 'lslash', sh); tl.fromTo(sl, { scaleY: 0 }, { scaleY: 1, duration: .14, ease: 'power4.out', immediateRender: false }, a + .12); K.fx(a + .14, 'hit'); sfx(a + .14, 'sub_drop/808', -9);
  tl.to([ln, sl], { opacity: 0, duration: .2 }, a + .5);
  if (c.mark) { const mk = el('div', 'lmark', sh, c.mark); if (c.markSize) { const im = mk.querySelector('svg, img'); if (im) { im.style.width = c.markSize + 'px'; im.style.height = 'auto'; } } const parts = mk.querySelectorAll('path, circle, rect, polygon');
    if (parts.length > 1) parts.forEach((p, i) => tl.fromTo(p, { y: -300, opacity: 0 }, { y: 0, opacity: 1, duration: .25, ease: 'back.out(2)', immediateRender: false }, a + .4 + i * .05));
    else tl.fromTo(mk, { y: -400, opacity: 0, rotation: -40 }, { y: 0, opacity: 1, rotation: 0, duration: .35, ease: 'back.out(1.8)', immediateRender: false }, a + .4);
    sfx(a + .45, 'pro_pop_in/deep', -12); }
  if (c.wordmark) { const wm = big(sh, c.wordmark, { ground: g, y: c.mark ? 1110 : 900, wdth: 112, size: 150 }); wm.style.textTransform = c.case === 'upper' ? 'uppercase' : 'none'; fit(wm, c.width || 920, 220, 200);
    const ls = letters(wm.querySelector('.fitw') || wm, c.wordmark); ls.forEach((L, i) => tl.fromTo(L, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: .12, immediateRender: false }, a + .6 + i * .03));
    sfx(a + .6, 'pro_typing_run/blip', -16, { dur: +(ls.length * .03).toFixed(2), align: 'start' }); }
  if (c.tagline) { const tg = el('div', 'ltag', sh, esc(c.tagline)); tg.style.color = ink; tl.fromTo(tg, { opacity: 0 }, { opacity: .85, duration: .3, immediateRender: false }, a + 1.1); }
  if (c.small) { const sm = el('div', 'lsmall mono', sh, esc(c.small)); sm.style.color = ink; tl.fromTo(sm, { opacity: 0 }, { opacity: .6, duration: .3, immediateRender: false }, a + 1.3); }
  sfx(a + .55, 'logo_sting/soft_bloom', -13); K.drift(sh, a + .5, b, 1.04, 0);
};
})();
