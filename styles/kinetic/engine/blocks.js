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
    s.split(/( )/).forEach(tok => { if (!tok) return; if (tok === ' ') { holder.appendChild(document.createTextNode(' ')); return; }   // a plain space: lines never start with one
    const wd = el('span', 'pw', holder); [...tok].forEach(ch => { const x = el('span', '', wd); x.textContent = ch === ' ' ? ' ' : ch; x.style.opacity = 0; spans.push(x); }); }); });
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

// ================================================================== StyleList: "N styles, one prompt" — a numbered list fills in while a framed card plays each one
// items: [{name, src (clip or image), at, mediaStart}]; title: [word, word] (first word in accent); sub + marks: the tools it works in;
// pin: {src, handle, text} a pinned-comment bar at the bottom (the call to action stays on screen the whole time).
BL.StyleList = (box, c, T, S) => {
  const a = S.start, b = S.end, g = c.ground || 'bg'; K.ground(a, g); const sh = layer(box, a, b); const ink = readable(g);
  const items = c.items || []; const ts = items.map((it, i) => it.at != null ? T(it.at) : a + .4 + i * (b - a - .6) / Math.max(1, items.length));
  const [w1, w2] = c.title || ['Viral', 'Videos'];
  const ti = el('div', 'sltitle', sh, `<span style="color:${col('accent')}">${esc(w1)}</span> ${esc(w2 || '')}`); ti.style.color = ink;
  if (c.enter !== false) tl.fromTo(ti, { y: -60, opacity: 0 }, { y: 0, opacity: 1, duration: .35, ease: 'back.out(1.8)', immediateRender: false }, a);
  if (c.sub) { const sb = el('div', 'slsub', sh); sb.style.color = ink; el('span', '', sb, esc(c.sub));
    (c.marks || []).forEach((m, k) => { if (k) el('span', 'sland', sb, '&amp;'); el('span', 'slbrand', sb, m + (c.names && c.names[k] ? `<b>${esc(c.names[k])}</b>` : '')); });
    if (c.enter !== false) tl.fromTo(sb, { opacity: 0 }, { opacity: 1, duration: .3, immediateRender: false }, a + .12); }
  const list = el('div', 'sllist', sh); const rows = items.map((it, i) => { const r = el('div', 'slrow', list); r.style.color = ink;
    el('span', 'slnum mono', r, (i + 1) + ')'); const nm = el('span', 'slname', r, esc(it.name)); nm.style.opacity = 0; return [r, nm]; });
  if (c.enter !== false) tl.fromTo(list.children, { x: -40, opacity: 0 }, { x: 0, opacity: 1, duration: .25, stagger: .025, ease: 'power3.out', immediateRender: false }, a + .1);
  const card = el('div', 'slcard', sh); if (c.enter !== false) tl.fromTo(card, { x: 300, rotation: 8, opacity: 0 }, { x: 0, rotation: 0, opacity: 1, duration: .45, ease: 'back.out(1.4)', immediateRender: false }, a + .05);
  // intro: images flashed through the card before the first item lands (the hook line plays over it)
  if (c.intro && c.intro.length && ts.length) { const n = c.intro.length, d = Math.max(.08, (ts[0] - a - .15) / n);
    c.intro.forEach((src, k) => { const t0 = a + .15 + k * d; if (t0 >= ts[0]) return; const m = el('img', 'slmedia', card); m.src = src; K.vis(m, t0, Math.min(ts[0], t0 + d));
      tl.fromTo(m, { scale: 1.12 }, { scale: 1, duration: d, ease: 'power2.out', immediateRender: false }, t0); if (k % 2 === 0) sfx(t0, 'pro_pop/tink', -20); }); }
  items.forEach((it, i) => { const t0 = ts[i], t1 = i + 1 < items.length ? ts[i + 1] : b; let m;
    if (/\.(mp4|webm|mov)$/i.test(it.src)) { m = el('video', 'slmedia', card); m.src = it.src; m.muted = true; m.dataset.start = t0; m.dataset.duration = t1 - t0; m.dataset.mediaStart = it.mediaStart || 0; }
    else { m = el('img', 'slmedia', card); m.src = it.src; K.vis(m, t0, t1); }
    tl.fromTo(m, { scale: 1.18, filter: 'brightness(2)' }, { scale: 1, filter: 'brightness(1)', duration: .3, ease: 'expo.out', immediateRender: false }, t0);
    const [r, nm] = rows[i]; tl.set(nm, { opacity: 1 }, t0); tl.set(r, { color: col('accent') }, t0); if (i + 1 < items.length) tl.set(r, { color: ink }, ts[i + 1]);
    tl.fromTo(nm, { x: -30 }, { x: 0, duration: .22, ease: 'power3.out', immediateRender: false }, t0);
    tl.fromTo(card, { rotationY: i % 2 ? -14 : 14 }, { rotationY: 0, duration: .32, ease: 'back.out(2)', immediateRender: false }, t0);
    sfx(t0, ['swish/soft', 'pro_pop/thup', 'whoosh_fast/crisp', 'pro_pop/boop'][i % 4], -15); });
  if (c.pin) { const pb = el('div', 'slpin', sh); if (c.pin.src) el('img', '', pb).src = c.pin.src;
    el('span', 'slpinh', pb, esc(c.pin.handle || '')); el('span', 'slpint', pb, c.pin.text || ''); el('span', 'slpinb mono', pb, esc(c.pin.badge || 'pinned'));
    tl.fromTo(pb, { y: 120, opacity: 0 }, { y: 0, opacity: 1, duration: .35, ease: 'back.out(1.6)', immediateRender: false }, a + .3); }
};

// ================================================================== Route: a dark world map; city dots pop, arcs draw leg by leg with a travelling glow
// src: world map svg (equirectangular, lat 80..-58, 2000 px wide); view: [lonW, latN, lonE, latS] region to frame;
// cities: [[name, lon, lat]]; route: names in order; legs: times per leg (default spread); label: small mono tag top-left.
BL.Route = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b); const MW = 2000, MH = 767;
  const X = lon => (lon + 180) / 360 * MW, Y = lat => (80 - lat) / 360 * MW;
  const [w0, n0, e0, s0] = c.view || [-20, 60, 140, 0]; const vx = X(w0), vy = Y(n0), vw = X(e0) - vx, vh = Y(s0) - vy;
  const sc = 1000 / vw, cy = c.y || 900;   // view fills 1000 px wide, centred at y = cy
  const map = el('div', 'rmap', sh); map.style.width = MW + 'px'; map.style.height = MH + 'px';
  const img = el('img', '', map); img.src = c.src; img.style.width = '100%'; img.style.opacity = .9;
  const NS = 'http://www.w3.org/2000/svg'; const svg = document.createElementNS(NS, 'svg'); svg.setAttribute('viewBox', `0 0 ${MW} ${MH}`); svg.setAttribute('class', 'rsvg'); map.appendChild(svg);
  for (let lo = -180; lo <= 180; lo += 15) { const l = document.createElementNS(NS, 'line'); l.setAttribute('x1', X(lo)); l.setAttribute('x2', X(lo)); l.setAttribute('y1', 0); l.setAttribute('y2', MH); l.setAttribute('class', 'rgrid'); svg.appendChild(l); }
  for (let la = -45; la <= 75; la += 15) { const l = document.createElementNS(NS, 'line'); l.setAttribute('x1', 0); l.setAttribute('x2', MW); l.setAttribute('y1', Y(la)); l.setAttribute('y2', Y(la)); l.setAttribute('class', 'rgrid'); svg.appendChild(l); }
  const pos = (s0x) => `translate(${540 - (vx + vw / 2) * s0x}px, ${cy - (vy + vh / 2) * s0x}px) scale(${s0x})`;
  map.style.transformOrigin = '0 0';
  tl.fromTo(map, { transform: pos(sc * .82), opacity: 0 }, { transform: pos(sc), opacity: 1, duration: Math.min(1.2, b - a), ease: 'power3.out', immediateRender: false }, a);
  tl.to(map, { transform: pos(sc * 1.06), duration: Math.max(.1, b - a - 1.2), ease: 'none' }, a + 1.2);
  const cities = {}; (c.cities || []).forEach(([n, lo, la], i) => { const g = document.createElementNS(NS, 'g'); svg.appendChild(g);
    const ring = document.createElementNS(NS, 'circle'); ring.setAttribute('cx', X(lo)); ring.setAttribute('cy', Y(la)); ring.setAttribute('r', 9 / sc); ring.setAttribute('class', 'rring'); g.appendChild(ring);
    const dot = document.createElementNS(NS, 'circle'); dot.setAttribute('cx', X(lo)); dot.setAttribute('cy', Y(la)); dot.setAttribute('r', 4.5 / sc); dot.setAttribute('class', 'rdot'); g.appendChild(dot);
    const t = document.createElementNS(NS, 'text'); const rgt = X(lo) > vx + vw * .78; t.setAttribute('x', X(lo) + (rgt ? -12 : 12) / sc); t.setAttribute('y', Y(la) - 10 / sc); if (rgt) t.setAttribute('text-anchor', 'end'); t.setAttribute('class', 'rname'); t.setAttribute('font-size', 22 / sc); t.textContent = n.toUpperCase(); g.appendChild(t);
    cities[n] = [X(lo), Y(la)]; tl.fromTo(g, { opacity: 0 }, { opacity: 1, duration: .25, immediateRender: false }, a + .5 + i * .08); });
  const route = c.route || []; const nl = Math.max(1, route.length - 1); const t0 = a + .9, span = b - t0 - .4;
  for (let i = 0; i < route.length - 1; i++) { const [x1, y1] = cities[route[i]], [x2, y2] = cities[route[i + 1]];
    const mx = (x1 + x2) / 2, my = (y1 + y2) / 2, d = Math.hypot(x2 - x1, y2 - y1); const qx = mx, qy = my - d * .32;
    const pth = document.createElementNS(NS, 'path'); pth.setAttribute('d', `M${x1} ${y1} Q${qx} ${qy} ${x2} ${y2}`); pth.setAttribute('class', 'rarc'); pth.setAttribute('stroke-width', 4 / sc); svg.appendChild(pth);
    const L = pth.getTotalLength(); pth.style.strokeDasharray = L; pth.style.strokeDashoffset = L;
    const glow = document.createElementNS(NS, 'circle'); glow.setAttribute('r', 9 / sc); glow.setAttribute('class', 'rglow'); svg.appendChild(glow); glow.style.opacity = 0;
    const ta = c.legs && c.legs[i] != null ? T(c.legs[i]) : t0 + i * span / nl, du = Math.min(1.1, span / nl * .85); const pr = { v: 0 };
    tl.to(pth, { strokeDashoffset: 0, duration: du, ease: 'power2.inOut' }, ta);
    tl.fromTo(pr, { v: 0 }, { v: 1, duration: du, ease: 'power2.inOut', immediateRender: false, onUpdate: () => { const p = pth.getPointAtLength(pr.v * L); glow.setAttribute('cx', p.x); glow.setAttribute('cy', p.y); glow.style.opacity = pr.v > 0 && pr.v < 1 ? 1 : 0; } }, ta);
    sfx(ta, 'whoosh_fast/sleeve', -18); sfx(ta + du, 'pro_pop/tink', -16); }
  if (c.label) { const lb = el('div', 'rlabel mono', sh, esc(c.label)); tl.fromTo(lb, { opacity: 0 }, { opacity: .7, duration: .3, immediateRender: false }, a + .2); }
  if (c.title) { const tt = el('div', 'rtitle', sh, c.title); tl.fromTo(tt, { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: .4, ease: 'power3.out', immediateRender: false }, c.titleAt ? T(c.titleAt) : a + .3); }
};
// ================================================================== SkillCard: icon, "02 / 03 ———— SKILL" rule, a big name and one line (a clean chapter card)
BL.SkillCard = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b); const ink = readable(c.ground || 'bg');
  const w = el('div', 'skc', sh); w.style.color = ink;
  if (c.mark) { const m = el('div', 'skmark', w, c.mark); tl.fromTo(m, { scale: .6, opacity: 0 }, { scale: 1, opacity: 1, duration: .35, ease: 'back.out(2)', immediateRender: false }, a); }
  const row = el('div', 'skrow mono', w); el('span', '', row, esc(c.index || '')); const rl = el('i', 'skrule', row); el('span', '', row, esc(c.kicker || ''));
  tl.fromTo(row, { opacity: 0 }, { opacity: .75, duration: .3, immediateRender: false }, a + .15); tl.fromTo(rl, { scaleX: 0 }, { scaleX: 1, duration: .7, ease: 'power3.inOut', immediateRender: false }, a + .2);
  const nm = el('div', 'skname', w, esc(c.title || '')); const sb = el('div', 'sksub', w, esc(c.sub || ''));
  tl.fromTo(nm, { y: 60, opacity: 0, clipPath: 'inset(0 0 100% 0)' }, { y: 0, opacity: 1, clipPath: 'inset(0 0 0% 0)', duration: .45, ease: 'power4.out', immediateRender: false }, a + .3);
  tl.fromTo(sb, { opacity: 0, y: 14 }, { opacity: .8, y: 0, duration: .35, immediateRender: false }, a + .6); sfx(a + .3, 'swish/soft', -16);
};
// ================================================================== TypeOn: one word types in letter by letter, an underline draws under it
BL.TypeOn = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b); const ink = readable(c.ground || 'bg');
  const wr = el('div', 'tyo', sh); wr.style.color = ink; const tx = String(c.text || ''); const sp = [...tx].map(ch => el('span', '', wr, ch === ' ' ? '&nbsp;' : esc(ch)));
  const per = Math.min(.07, (b - a - .6) / Math.max(1, sp.length)); sp.forEach((s1, i) => { tl.fromTo(s1, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: .08, immediateRender: false }, a + .1 + i * per); if (i % 2 === 0) sfx(a + .1 + i * per, 'pro_pop/tink', -24); });
  const ul = el('i', 'tyul', wr); ul.style.background = col(c.color || 'accent'); tl.fromTo(ul, { scaleX: 0 }, { scaleX: 1, duration: .35, ease: 'power3.out', immediateRender: false }, a + .15 + sp.length * per);
  if (c.sub) { const sb = el('div', 'tyosub mono', sh, esc(c.sub)); sb.style.color = ink; tl.fromTo(sb, { opacity: 0 }, { opacity: .6, duration: .3, immediateRender: false }, a + .3 + sp.length * per); }
};
// ================================================================== Steps: line-icon boxes joined by drawn arrows, then (optional) they turn into a bar chart with a trend line
// steps: [[icon svg, label, at?]]; chart: {at, bars: [[label, value]], title: [bold, light]}
BL.Steps = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b); const ink = readable(c.ground || 'bg');
  const steps = c.steps || []; const wrap = el('div', 'stp', sh); wrap.style.color = ink; const ca = c.chart && c.chart.at ? T(c.chart.at) : b + 1;
  steps.forEach(([ic, lab, at1], i) => { const t = at1 != null ? T(at1) : a + .2 + i * .6;
    if (i) { const ar = el('div', 'stparrow', wrap); tl.fromTo(ar, { scaleY: 0 }, { scaleY: 1, duration: .25, ease: 'power2.out', immediateRender: false }, t - .25); }
    const r = el('div', 'stprow', wrap); const bx = el('div', 'stpbox', r, ic); el('div', 'stplab', r, esc(lab));
    tl.fromTo(r, { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: .3, ease: 'power3.out', immediateRender: false }, t); tl.fromTo(bx, { scale: .7 }, { scale: 1, duration: .35, ease: 'back.out(2.2)', immediateRender: false }, t);
    sfx(t, 'pro_pop_in/round', -15); });
  if (!c.chart) return;
  tl.to(wrap, { opacity: 0, x: -60, duration: .3, ease: 'power2.in' }, ca - .3);
  const ch = el('div', 'stpchart', sh); ch.style.color = ink; K.vis(ch, ca, b); const bars = c.chart.bars || []; const mx = Math.max(...bars.map(x => x[1]));
  const NS = 'http://www.w3.org/2000/svg'; const sv = document.createElementNS(NS, 'svg'); sv.setAttribute('viewBox', '0 0 800 700'); sv.setAttribute('class', 'stpsvg'); ch.appendChild(sv);
  const base = el('i', 'stpbase', ch); tl.fromTo(base, { scaleX: 0 }, { scaleX: 1, duration: .35, ease: 'power3.out', immediateRender: false }, ca);
  const bw = 150, gap = (800 - bars.length * bw) / (bars.length + 1); const tops = [];
  bars.forEach(([lab, v], i) => { const x = gap + i * (bw + gap), h = 600 * v / mx; tops.push([x + bw / 2, 640 - h]);
    const bar = el('div', 'stpbar', ch); bar.style.left = (x / 800 * 100) + '%'; bar.style.width = (bw / 800 * 100) + '%'; bar.style.height = (h / 700 * 100) + '%';
    const lb = el('div', 'stpblab mono', ch, esc(lab)); lb.style.left = ((x + bw / 2) / 800 * 100) + '%';
    tl.fromTo(bar, { scaleY: 0 }, { scaleY: 1, duration: .5, ease: 'power3.out', immediateRender: false }, ca + .25 + i * .18); tl.fromTo(lb, { opacity: 0 }, { opacity: .7, duration: .2, immediateRender: false }, ca + .3 + i * .18);
    sfx(ca + .3 + i * .18, 'pro_pop/thup', -16); });
  const pl = document.createElementNS(NS, 'polyline'); pl.setAttribute('points', tops.map(p => p.join(',')).join(' ')); pl.setAttribute('class', 'stpline'); sv.appendChild(pl);
  const L = tops.reduce((s1, p, i) => i ? s1 + Math.hypot(p[0] - tops[i - 1][0], p[1] - tops[i - 1][1]) : 0, 0); pl.style.strokeDasharray = L; pl.style.strokeDashoffset = L;
  const lt = ca + .35 + bars.length * .18; tl.to(pl, { strokeDashoffset: 0, duration: .6, ease: 'power2.inOut' }, lt);
  tops.forEach(([x, y], i) => { const d = document.createElementNS(NS, 'circle'); d.setAttribute('cx', x); d.setAttribute('cy', y); d.setAttribute('r', 9); d.setAttribute('class', 'stpdot'); sv.appendChild(d);
    tl.fromTo(d, { opacity: 0 }, { opacity: 1, duration: .1, immediateRender: false }, lt + i * .6 / Math.max(1, tops.length - 1)); });
  if (c.chart.title) { const [b1, l1] = c.chart.title; const tt = el('div', 'stptitle', sh, `<b>${esc(b1)}</b><span>${esc(l1 || '')}</span>`); tt.style.color = ink; K.vis(tt, ca, b);
    tl.fromTo(tt, { opacity: 0, y: -20 }, { opacity: 1, y: 0, duration: .4, ease: 'power3.out', immediateRender: false }, ca + .1); }
};

// ================================================================== Dupes: a photo library window; copies light up with COPY badges, a storage bar runs hot, `clear` sweeps them away
// tiles: [{src, pos, filter}]; groups: [{at, idx: [..]}] (first index of each group is kept on clear); storage: {pct, from, label}; scan: at (a scan line sweeps the grid);
// clear: {at, pct, label}; stamp: {at, text}; enter: false = on screen from frame 1 (a hook)
BL.Dupes = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b);
  const win = el('div', 'dpwin', sh); el('div', 'mbar mono', win, `<i></i><i></i><i></i><span>${esc(c.title || 'Photos')}</span><em>${esc(c.count || '')}</em>`);
  const st = c.storage || {}; const sb = el('div', 'dpstore mono', win); const lab = el('span', 'dplabs', sb); const l1 = el('em', '', lab, esc(st.label || 'STORAGE')); const pc = el('b', '', sb);
  const tr = el('div', 'dptrack', sb); const fill = el('i', '', tr); const v = { p: st.from ?? st.pct ?? 97 };
  const upd = () => { fill.style.width = v.p + '%'; pc.textContent = Math.round(v.p) + '%'; const hot = v.p > 80; fill.style.background = hot ? col('accent') : '#3ddc84'; pc.style.color = hot ? col('accent') : '#3ddc84'; };
  upd(); if (st.from != null) tl.fromTo(v, { p: st.from }, { p: st.pct, duration: 1.1, ease: 'power2.out', onUpdate: upd, immediateRender: false }, a + .1);
  const grid = el('div', 'dpgrid', win); grid.style.gridTemplateColumns = `repeat(${c.cols || 4}, 1fr)`;
  const cells = (c.tiles || []).map((t, i) => { const d = el('div', 'dpcell', grid); const im = el('img', '', d); im.src = t.src; if (t.pos) im.style.objectPosition = t.pos; if (t.filter) im.style.filter = t.filter; if (t.zoom) im.style.transform = `scale(${t.zoom})`;
    const bd = el('div', 'dpbadge mono', d, 'COPY'); bd.style.opacity = 0; return [d, bd]; });
  if (c.enter !== false) tl.fromTo(cells.map(x => x[0]), { scale: .4, opacity: 0 }, { scale: 1, opacity: 1, duration: .3, stagger: .025, ease: 'back.out(1.8)', immediateRender: false }, a);
  if (c.enter !== false) sfx(a, 'pro_pop_in/airy', -15);
  tl.fromTo(win, { scale: c.enter === false ? 1 : .94 }, { scale: 1.04, duration: b - a, ease: 'none', immediateRender: false }, a);
  if (st.warn !== false && v.p > 80) for (let t = a + .2; t < (c.clear ? T(c.clear.at) : b) - .1; t += .5) { tl.set(fill, { opacity: .45 }, t); tl.set(fill, { opacity: 1 }, t + .25); }
  if (c.scan != null) { const ln = el('i', 'dpscan', grid); const t0 = T(c.scan); K.vis(ln, t0, t0 + .9); tl.fromTo(ln, { top: '0%' }, { top: '100%', duration: .9, ease: 'power1.inOut', immediateRender: false }, t0); sfx(t0, 'whoosh_fast/sleeve', -17); }
  const lit = [];
  (c.groups || []).forEach((g, k) => { const t = T(g.at); g.idx.forEach((ix, j) => { const [d, bd] = cells[ix]; if (j) lit.push(d);
      tl.set(d, { boxShadow: `0 0 0 6px ${col(j ? 'accent' : 'hot')}` }, t + j * .06); if (j) tl.fromTo(bd, { opacity: 0, scale: 1.8 }, { opacity: 1, scale: 1, duration: .18, ease: 'back.out(2)', immediateRender: false }, t + j * .06);
      tl.fromTo(d, { scale: 1.1 }, { scale: 1, duration: .25, ease: 'power3.out', immediateRender: false }, t + j * .06); });
    sfx(t, k % 2 ? 'pro_pop/boop' : 'pro_pop/thup', -14); });
  if (c.stamp) { const sp = el('div', 'dpstamp', sh, esc(c.stamp.text)); const t = T(c.stamp.at); K.vis(sp, t, c.stamp.out ? T(c.stamp.out) : b);
    tl.fromTo(sp, { scale: 2.6, opacity: 0, rotation: -14 }, { scale: 1, opacity: 1, rotation: -7, duration: .2, ease: 'power4.out', immediateRender: false }, t); K.fx(t, 'hit'); }
  if (c.clear) { const t = T(c.clear.at); tl.to(lit, { scale: 0, opacity: 0, duration: .3, stagger: .03, ease: 'back.in(1.6)' }, t);
    tl.to(v, { p: c.clear.pct ?? 40, duration: .9, ease: 'power3.inOut', onUpdate: upd }, t + .1); const l2 = el('em', '', lab, esc(c.clear.label || 'FREED UP')); K.vis(l1, a, t + .1); K.vis(l2, t + .1, b);
    sfx(t, 'swish/blade', -14); sfx(t + .5, 'pro_pop_in/round', -15); }
};

// ================================================================== Copies: one photo card multiplies into a fan of copies, each with its file name, then a ×N tag
// src (one picture), names: [file names], ats: [when each copy appears], tag
BL.Copies = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b); const names = c.names || ['IMG.jpg']; const n = names.length;
  const stage = el('div', 'cpstage', sh); const ats = names.map((_, i) => c.ats && c.ats[i] != null ? T(c.ats[i]) : a + .1 + i * .45);
  const cards = names.map((nm, i) => { const d = el('div', 'cpcard', stage); const im = el('img', '', d); im.src = c.src; el('div', 'cpname mono', d, esc(nm)); d.style.zIndex = n - i; return d; });
  const off = i => (i - (n - 1) / 2);
  cards.forEach((d, i) => { const t = ats[i];
    if (!i) tl.fromTo(d, { y: 260, rotation: 0, opacity: 0, scale: .9 }, { y: 0, opacity: 1, scale: 1, duration: .35, ease: 'back.out(1.6)', immediateRender: false }, t);
    else K.vis(d, t, b);
    sfx(t, i ? 'shutter/film' : 'swish/soft', -14);
    // after each copy lands, everyone already shown re-fans
    const shown = i + 1; cards.slice(0, shown).forEach((e, j) => tl.to(e, { x: (j - (shown - 1) / 2) * 225, rotation: (j - (shown - 1) / 2) * 7, y: Math.abs(j - (shown - 1) / 2) * 30, duration: .32, ease: 'back.out(1.5)' }, t + .02)); });
  tl.fromTo(stage, { scale: 1 }, { scale: 1.06, duration: b - a, ease: 'none', immediateRender: false }, a);
  if (c.tag) { const tg = el('div', 'cptag', sh, esc(c.tag)); const t = ats[n - 1] + .25; K.vis(tg, t, b);
    tl.fromTo(tg, { scale: 2.4, opacity: 0, rotation: -12 }, { scale: 1, opacity: 1, rotation: -6, duration: .22, ease: 'power4.out', immediateRender: false }, t); K.fx(t, 'hit'); }
};

// ================================================================== Files: a file-list window (rows drop in, optional size bars), then an empty folder
// title, rows: [[icon svg, name, size, bar 0..1, hot]], at (rows start), bars: true; empty: {at, name, note, icon}
BL.Files = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b); const ea = c.empty ? T(c.empty.at) : b + 1;
  const win = el('div', 'flwin', sh); el('div', 'mbar mono', win, `<i></i><i></i><i></i><span>${esc(c.title || 'Downloads')}</span><em>${esc(c.count || '')}</em>`);
  const list = el('div', 'fllist', win); const t0 = c.at != null ? T(c.at) : a + .1; const rows = c.rows || []; const per = Math.min(.14, (ea - t0 - .3) / Math.max(1, rows.length));
  tl.fromTo(win, { y: 120, opacity: 0, rotationX: 18 }, { y: 0, opacity: 1, rotationX: 0, duration: .4, ease: 'power3.out', immediateRender: false }, a);
  rows.forEach(([ic, nm, sz, bar, hot], i) => { const r = el('div', 'flrow', list); el('span', 'flic', r, ic || ''); const tx = el('div', 'fltx', r); el('span', 'flnm', tx, esc(nm));
    if (c.bars) { const tk = el('div', 'flbar', tx); const f = el('i', '', tk); f.style.background = hot ? col('accent') : '#8a8a92'; tl.fromTo(f, { width: '0%' }, { width: (bar * 100) + '%', duration: .5, ease: 'power3.out', immediateRender: false }, t0 + i * per + .1); }
    const s = el('span', 'flsz mono', r, esc(sz || '')); if (hot) s.style.color = col('accent');
    tl.fromTo(r, { x: -80, opacity: 0 }, { x: 0, opacity: 1, duration: .25, ease: 'power3.out', immediateRender: false }, t0 + i * per); if (i % 2 === 0) sfx(t0 + i * per, 'pro_pop/tink', -20); });
  tl.to(list, { y: -40, duration: Math.max(.1, ea - t0), ease: 'none' }, t0);
  if (!c.empty) return;
  tl.to(win, { x: -1100, rotation: -6, duration: .35, ease: 'power3.in' }, ea - .3); sfx(ea - .3, 'whoosh_fast/crisp', -15);
  const em = el('div', 'flempty', sh); K.vis(em, ea, b); const fo = el('div', 'flfold', em, c.empty.icon || ''); el('div', 'flename', em, esc(c.empty.name || 'New Folder'));
  const nt = el('div', 'flenote mono', em, esc(c.empty.note || '0 items')); nt.style.color = col('accent');
  tl.fromTo(fo, { scale: .3, rotation: -20, opacity: 0 }, { scale: 1, rotation: 0, opacity: 1, duration: .4, ease: 'back.out(2)', immediateRender: false }, ea);
  tl.fromTo(nt, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .25, immediateRender: false }, ea + .25); tl.to(fo, { y: -14, duration: .5, yoyo: true, repeat: 5, ease: 'sine.inOut' }, ea + .4);
  sfx(ea, 'pro_pop_in/round', -14);
};

// ================================================================== Match: two pictures side by side; scan lines run down both, a percentage ticks up, a stamp lands
// left / right: {src, name, css (a CSS filter), crop (zoom), wave: true (an audio file: waveform instead of a picture)}; pct, at (scan start), stamp, label
BL.Match = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b); const t0 = c.at != null ? T(c.at) : a + .35;
  const mk = (o, k) => { const d = el('div', 'mtcard ' + (k ? 'mtr' : 'mtl'), sh); const fr = el('div', 'mtpic', d);
    if (o.wave) { fr.classList.add('mtwave'); el('div', 'mtnote', fr, o.icon || ''); const wv = el('div', 'mtbars', fr); const r = rng(7); for (let i = 0; i < 28; i++) { const bb = el('i', '', wv); bb.style.height = (18 + r() * 82) + '%'; } }
    else { const im = el('img', '', fr); im.src = o.src; if (o.css) im.style.filter = o.css; if (o.crop) { im.style.transform = `scale(${o.crop})`; im.style.transformOrigin = o.origin || '50% 40%'; } if (o.wm) el('div', 'mtwm', fr, esc(o.wm)); if (o.res) el('div', 'mtres mono', fr, esc(o.res)); }
    el('div', 'mtname mono', d, esc(o.name || '')); const sc = el('i', 'mtscan', fr); K.vis(sc, t0, t0 + 1); tl.fromTo(sc, { top: '0%' }, { top: '100%', duration: 1, ease: 'power1.inOut', immediateRender: false }, t0);
    tl.fromTo(d, { x: k ? 600 : -600, rotation: k ? 10 : -10 }, { x: 0, rotation: k ? 3 : -3, duration: .4, ease: 'back.out(1.4)', immediateRender: false }, a + k * .08); return d; };
  const L = mk(c.left || {}, 0), R = mk(c.right || {}, 1); sfx(a, 'swish/cane', -15); sfx(t0, 'whoosh_fast/sleeve', -18);
  const link = el('i', 'mtlink', sh); tl.fromTo(link, { scaleX: 0 }, { scaleX: 1, duration: .5, ease: 'power3.inOut', immediateRender: false }, t0 + .2);
  const pc = el('div', 'mtpct', sh); const v = { p: 0 }; const goal = c.pct ?? 96; const upd = () => { pc.innerHTML = `${Math.round(v.p)}<small>%</small> <span>${esc(c.label || 'MATCH')}</span>`; }; upd();
  tl.fromTo(pc, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: .25, immediateRender: false }, t0 + .1);
  tl.fromTo(v, { p: 0 }, { p: goal, duration: 1, ease: 'power2.out', onUpdate: upd, immediateRender: false }, t0 + .15);
  for (let k = 0; k < 6; k++) sfx(t0 + .15 + k * .14, 'pro_pop/tink', -24);
  if (c.stamp) { const sp = el('div', 'dpstamp mtstamp', sh, esc(c.stamp)); const t = c.stampAt != null ? T(c.stampAt) : t0 + 1.2; K.vis(sp, t, b);
    tl.fromTo(sp, { scale: 2.6, opacity: 0, rotation: -14 }, { scale: 1, opacity: 1, rotation: -7, duration: .2, ease: 'power4.out', immediateRender: false }, t);
    tl.set([L, R], { boxShadow: `0 0 0 6px ${col('accent')}, 0 40px 100px rgba(0,0,0,.6)` }, t); K.fx(t, 'hit'); }
  tl.to([L, R], { y: -24, duration: Math.max(.2, b - a - .4), ease: 'none' }, a + .4);
};

// ================================================================== ToolGrid: icon tiles fill a grid fast, then a big number slams over them
// items: [[icon svg, label]], at (fill start), per (seconds per tile), number, label, numAt
BL.ToolGrid = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b); const it = c.items || []; const t0 = c.at != null ? T(c.at) : a + .05; const per = c.per || .05;
  const g = el('div', 'tggrid', sh); const tiles = it.map(([ic, lb]) => { const d = el('div', 'tgtile', g); el('div', 'tgic', d, ic); el('div', 'tglb mono', d, esc(lb)); return d; });
  tl.fromTo(tiles, { scale: 0, opacity: 0, rotation: -12 }, { scale: 1, opacity: 1, rotation: 0, duration: .25, stagger: per, ease: 'back.out(2)', immediateRender: false }, t0);
  tiles.forEach((_, i) => { if (i % 3 === 0) sfx(t0 + i * per, 'pro_pop/tink', -21); });
  tl.fromTo(g, { scale: 1.08 }, { scale: .96, duration: b - a, ease: 'none', immediateRender: false }, a);
  if (c.number != null) { const na = c.numAt != null ? T(c.numAt) : t0 + it.length * per + .1; const nb = el('div', 'tgnum', sh, `${esc(String(c.number))}<span>${esc(c.label || '')}</span>`); K.vis(nb, na, b);
    tl.to(tiles, { opacity: .22, duration: .2 }, na); tl.fromTo(nb, { scale: 2.8, opacity: 0 }, { scale: 1, opacity: 1, duration: .2, ease: 'power4.out', immediateRender: false }, na); K.fx(na, 'punch'); }
};

// ================================================================== Stack: full-width cards drop in one per name (works-with lists), a heading on top
// head, sub, items: [{mark (svg), title, sub, at, color}]; each card lands at its own `at`, earlier cards dim a little
BL.Stack = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b); const it = c.items || [];
  const hd = el('div', 'stkhead', sh, `<b>${esc(c.head || '')}</b><span class="mono">${esc(c.sub || '')}</span>`);
  tl.fromTo(hd, { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: .25, ease: 'power3.out', immediateRender: false }, a);
  const h = c.h || 370, gap = 50, top0 = c.top ?? 560;
  const cards = it.map((o, k) => { const d = el('div', 'stkcard', sh); d.style.top = (top0 + k * (h + gap)) + 'px'; d.style.height = h + 'px'; if (o.color) d.style.setProperty('--sc', o.color);
    el('div', 'stkmk', d, o.mark || ''); el('div', 'stktx', d, `<b>${esc(o.title)}</b><span class="mono">${esc(o.sub || '')}</span>`); el('div', 'stkok', d, c.check || '');
    const t = o.at != null ? T(o.at) : a + .1 + k * .3; tl.set(d, { x: k % 2 ? 1100 : -1100 }, a);
    tl.fromTo(d, { x: k % 2 ? 1100 : -1100, rotation: k % 2 ? 6 : -6, opacity: 1 }, { x: 0, rotation: 0, duration: .32, ease: 'back.out(1.4)', immediateRender: false }, t);
    tl.fromTo(d.querySelector('.stkok'), { scale: 0 }, { scale: 1, duration: .2, ease: 'back.out(3)', immediateRender: false }, t + .3);
    sfx(t, 'whoosh_fast/crisp', -14); sfx(t + .3, 'pro_pop/thup', -14); return [d, t]; });
  cards.forEach(([d], k) => { if (k + 1 < cards.length) tl.to(d, { opacity: .45, duration: .2 }, cards[k + 1][1]); });
};

// ================================================================== TaskMgr: a task-manager window; one process row lands and its memory counts up over a live graph, then a compare strip and a badge
// title, row: {mark (svg), name, mem (MB), sub, subAt}, at, compare: {at, rows: [[label, value, color, text]], max}, badge: {text, at}
BL.TaskMgr = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b); const t0 = c.at != null ? T(c.at) : a + .15; const rw = c.row || {};
  const win = el('div', 'tmwin', sh); el('div', 'mbar mono', win, `<i></i><i></i><i></i><span>${esc(c.title || 'Task Manager')}</span><em>Processes</em>`);
  el('div', 'tmhead mono', win, '<span>Name</span><span>Memory</span>');
  const r = el('div', 'tmrow', win); el('div', 'tmmk', r, rw.mark || ''); const nm = el('div', 'tmnm', r, `<b>${esc(rw.name || '')}</b><span class="mono">${esc(rw.sub || '')}</span>`);
  const mem = el('div', 'tmmem', r); const o = { v: 0 }; const up = () => { mem.textContent = o.v.toFixed(1) + ' MB'; }; up();
  tl.fromTo(win, { y: 120, opacity: 0, scale: .94 }, { y: 0, opacity: 1, scale: 1, duration: .35, ease: 'power3.out', immediateRender: false }, a);
  tl.fromTo(r, { x: -160, opacity: 0 }, { x: 0, opacity: 1, duration: .3, ease: 'back.out(1.5)', immediateRender: false }, t0); sfx(t0, 'pro_pop_in/deep', -13);
  tl.fromTo(o, { v: 0 }, { v: rw.mem || 0, duration: 1.0, ease: 'power3.out', onUpdate: up, immediateRender: false }, t0 + .1); sfx(t0 + .1, 'pro_typing_run/blip', -17);
  const sb = nm.querySelector('span'); if (rw.subAt) { K.vis(sb, T(rw.subAt), b); tl.fromTo(sb, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .25, immediateRender: false }, T(rw.subAt)); sfx(T(rw.subAt), 'pro_pop/thup', -14); }
  // live memory graph: a flat line that draws across
  const gw = el('div', 'tmgraph', win); const pts = []; for (let i = 0; i <= 40; i++) pts.push(`${i * 22},${150 - 30 - 12 * Math.sin(i * .9) - (i % 7 === 0 ? 10 : 0)}`);
  gw.innerHTML = `<svg viewBox="0 0 880 200" preserveAspectRatio="none"><polyline points="${pts.join(' ')}" fill="none" stroke="var(--accent,#e5372d)" stroke-width="5"/><polyline points="0,200 ${pts.join(' ')} 880,200" fill="rgba(229,55,45,.15)" stroke="none"/></svg><span class="mono">memory · live</span>`;
  const pl = gw.querySelector('polyline'); const L = 1400; pl.style.strokeDasharray = L; tl.fromTo(pl, { strokeDashoffset: L }, { strokeDashoffset: 0, duration: 1.6, ease: 'none', immediateRender: false }, t0);
  if (c.compare) { const cp = c.compare, ct = T(cp.at), mx = cp.max || 1;
    (cp.rows || []).forEach(([lb, v, col, tx], k) => { const rr = el('div', 'tmcmp', sh); rr.style.top = (1180 + k * 190) + 'px';
      el('div', 'tmcl mono', rr, esc(lb)); const tr = el('div', 'tmtr', rr); const f = el('i', '', tr); f.style.background = col; el('b', '', tr, esc(tx));
      const t = ct + k * .25; tl.fromTo(rr, { opacity: 0, x: -120 }, { opacity: 1, x: 0, duration: .25, ease: 'power3.out', immediateRender: false }, t);
      tl.fromTo(f, { width: '0%' }, { width: (v / mx * 100) + '%', duration: .6, ease: 'power3.out', immediateRender: false }, t + .05); sfx(t, 'swish/soft', -16); }); }
  if (c.badge) { const bd = el('div', 'bbadge', sh, esc(c.badge.text)); bd.style.top = '1610px'; const t = T(c.badge.at); K.vis(bd, t, b); tl.fromTo(bd, { scale: 2.4, opacity: 0, rotation: -12 }, { scale: 1, opacity: 1, rotation: -5, duration: .22, ease: 'power4.out', immediateRender: false }, t); K.fx(t, 'hit'); }
};

// ================================================================== Shot: a screenshot in a window; the camera zooms to one area at a time, a ring draws round it, a cursor taps
// src, iw, ih (the image's pixel size), logo (svg) + brand (text) above the window, view: {top, height},
// steps: [{at, rect: [x, y, w, h] (image px; omit for the whole image), ring: true, tap: true, label}]
BL.Shot = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b);
  const vw = 1000, vt = c.view?.top ?? 330, vh = c.view?.height ?? 1080, iw = c.iw, ih = c.ih;
  if (c.logo || c.brand) { const hd = el('div', 'shbrand', sh, `${c.logo || ''}<b>${esc(c.brand || '')}</b>`); hd.style.top = (vt - 190) + 'px';
    tl.fromTo(hd, { opacity: 0, y: -24 }, { opacity: 1, y: 0, duration: .25, ease: 'power3.out', immediateRender: false }, a); }
  const view = el('div', 'shview', sh); view.style.top = vt + 'px'; view.style.height = vh + 'px';
  const cam = el('div', 'shcam', view); cam.style.width = iw + 'px'; cam.style.height = ih + 'px';
  const im = el('img', '', cam); im.src = c.src; im.style.width = iw + 'px'; im.style.height = ih + 'px'; if (c.bright) im.style.filter = `brightness(${c.bright}) contrast(1.06)`;
  const fit = r => { const [x, y, w, h] = r || [0, 0, iw, ih]; const sc = Math.min(vw * .92 / w, vh * .8 / h, c.maxZoom || 2.4); return { scale: sc, x: vw / 2 - (x + w / 2) * sc, y: vh / 2 - (y + h / 2) * sc }; };
  const f0 = fit(null); gsap.set(cam, { transformOrigin: '0 0', ...f0 });
  tl.fromTo(view, { y: 140, opacity: 0, scale: .95 }, { y: 0, opacity: 1, scale: 1, duration: .35, ease: 'power3.out', immediateRender: false }, a);
  const cur = el('div', 'shcur', cam, '<svg viewBox="0 0 24 24"><path d="M4 2 L4 19 L8.5 15 L11.5 22 L14.5 20.6 L11.6 14 L18 14 Z" fill="#fff" stroke="#0b0b0b" stroke-width="1.4" stroke-linejoin="round"/></svg>');
  let cx = iw * .7, cy = ih * .8; gsap.set(cur, { x: cx, y: cy, opacity: 0 });
  const sts = c.steps || []; sts.forEach((st, k) => { if (st.until == null && sts[k + 1] && sts[k + 1].at != null) st.until = sts[k + 1].at; });
  sts.forEach(st => { const t = st.at != null ? T(st.at) : a; const f = fit(st.rect);
    tl.to(cam, { ...f, duration: .5, ease: 'power3.inOut' }, t); sfx(t, 'swish/soft', -17);
    if (st.rect && st.ring) { const [x, y, w, h] = st.rect, rg = el('div', 'shring', cam); const p = (c.pad ?? 8) / f.scale;   // one ring at a time: it fades out before the next step's ring lands
      Object.assign(rg.style, { left: (x - p) + 'px', top: (y - p) + 'px', width: (w + 2 * p) + 'px', height: (h + 2 * p) + 'px', borderWidth: (6 / f.scale) + 'px', borderRadius: (14 / f.scale) + 'px' });
      const t1 = t + .45, t2 = Math.max(t1 + .3, (st.until != null ? T(st.until) : t + 2.2) - .05);
      tl.set(rg, { opacity: 0 }, a); tl.fromTo(rg, { opacity: 0, scale: 1.15 }, { opacity: 1, scale: 1, duration: .22, ease: 'back.out(2)', immediateRender: false }, t1);
      tl.fromTo(rg, { opacity: 1 }, { opacity: 0, duration: .12, immediateRender: false }, t2); }
    if (st.rect && st.tap) { const [x, y, w, h] = st.rect; const tx = x + w / 2, ty = y + h / 2; const cs = 1 / f.scale * 2.2;
      tl.set(cur, { opacity: 1 }, t); tl.fromTo(cur, { x: cx, y: cy, scale: cs }, { x: tx, y: ty, scale: cs, duration: .45, ease: 'power2.inOut', immediateRender: false }, t + .2);
      tl.to(cur, { scale: cs * .8, duration: .08, yoyo: true, repeat: 1 }, t + .68); cx = tx; cy = ty;
      const rp = el('div', 'shrip', cam); Object.assign(rp.style, { left: tx + 'px', top: ty + 'px' });
      tl.fromTo(rp, { scale: 0, opacity: .8 }, { scale: 3 / f.scale * 2, opacity: 0, duration: .45, ease: 'power2.out', immediateRender: false }, t + .7); sfx(t + .7, 'pro_pop/thup', -13); }
    if (st.label) { const lb = el('div', 'shlabel', sh, esc(st.label)); lb.style.top = (vt + vh + 60) + 'px'; K.vis(lb, t + .3, st.until != null ? T(st.until) : b);
      tl.fromTo(lb, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .2, immediateRender: false }, t + .3); } });
};

// ================================================================== Usage: a usage-limits panel; bars sit full, then each one empties at its own time (a reset)
// title, plan, rows: [{name, sub, pct, at (when it empties), num: false hides the % text}], button: {label, sub, at (pressed)}, stamp: {text, at}
BL.Usage = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b);
  if (c.head) { const hd = el('div', 'stkhead', sh, `<b>${esc(c.head)}</b><span class="mono">${esc(c.sub || '')}</span>`); tl.fromTo(hd, { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: .25, ease: 'power3.out', immediateRender: false }, a); }
  const p = el('div', 'uspanel', sh); p.style.top = (c.top ?? 330) + 'px'; el('div', 'ushead', p, `<b>${esc(c.title || 'Your usage limits')}</b><span>${esc(c.plan || '')}</span>`);
  tl.fromTo(p, { y: 140, opacity: 0 }, { y: 0, opacity: 1, duration: .35, ease: 'power3.out', immediateRender: false }, a);
  (c.rows || []).forEach(r => { const row = el('div', 'usrow', p); el('div', 'usnm', row, `<b>${esc(r.name)}</b><span>${esc(r.sub || '')}</span>`);
    const tr = el('div', 'ustr', row); const f = el('i', '', tr); const num = el('div', 'usnum', row); const o = { v: r.pct };
    const up = () => { f.style.width = o.v + '%'; num.textContent = r.num === false ? '' : Math.round(o.v) + '% used'; f.style.background = o.v > 90 ? '#e5372d' : '#2c84db'; }; up();
    tl.fromTo(o, { v: r.from ?? r.pct }, { v: r.pct, duration: .6, ease: 'power2.out', onUpdate: up, immediateRender: false }, a + .2);
    if (r.at != null) { const t = T(r.at); tl.to(o, { v: 0, duration: .55, ease: 'power3.inOut', onUpdate: up }, t); sfx(t, 'pro_riser/air_gate', -20); sfx(t + .5, 'pro_pop/tink', -16); } });
  if (c.button) { const bt = c.button, row = el('div', 'usbtnrow', p); el('div', 'usnm', row, `<b>${esc(bt.label || 'Full reset')}</b><span>${esc(bt.sub || '')}</span>`); const btn = el('div', 'usbtn', row, 'Reset for free');
    if (bt.at != null) { const t = T(bt.at); tl.to(btn, { scale: .9, duration: .08, yoyo: true, repeat: 1 }, t); tl.to(btn, { backgroundColor: '#3ddc84', color: '#0b0b0b', duration: .15 }, t + .1); sfx(t, 'pro_pop/thup', -12); K.fx(t, 'hit'); } }
  if (c.stamp) { const sp = el('div', 'bbadge', sh, esc(c.stamp.text)); sp.style.top = (c.stamp.top ?? 1560) + 'px'; sp.style.borderColor = '#3ddc84'; sp.style.color = '#3ddc84'; const t = T(c.stamp.at); K.vis(sp, t, b);
    tl.fromTo(sp, { scale: 2.4, opacity: 0, rotation: -12 }, { scale: 1, opacity: 1, rotation: -4, duration: .22, ease: 'power4.out', immediateRender: false }, t); K.fx(t, 'hit'); }
};

// ================================================================== Week: seven day tiles; one is the weekly refill day; marks land under days (bad / good)
// head, sub, refill (day index 0-6), refillLabel, marks: [{day, at, kind: 'bad'|'good', text}]
BL.Week = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b); const days = c.days || ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
  const hd = el('div', 'stkhead', sh, `<b>${esc(c.head || '')}</b><span class="mono">${esc(c.sub || '')}</span>`);
  tl.fromTo(hd, { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: .25, ease: 'power3.out', immediateRender: false }, a);
  const row = el('div', 'wkrow', sh); const tiles = days.map((d, k) => { const t = el('div', 'wkday' + (k === c.refill ? ' wkref' : ''), row, `<b>${d}</b>`);
    tl.fromTo(t, { y: 80, opacity: 0 }, { y: 0, opacity: 1, duration: .25, ease: 'back.out(1.6)', immediateRender: false }, a + .1 + k * .05); return t; });
  if (c.refill != null) { const rl = el('div', 'wkreflbl mono', sh, esc(c.refillLabel || 'week refills')); const tr = tiles[c.refill]; rl.style.left = (60 + c.refill * 140 + 62) + 'px';
    tl.fromTo(rl, { opacity: 0, y: -10 }, { opacity: 1, y: 0, duration: .25, immediateRender: false }, a + .5); }
  if (c.note) { const nt = el('div', 'wknote', sh, esc(c.note.text)); const t = T(c.note.at); K.vis(nt, t, b); tl.fromTo(nt, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: .25, ease: 'power3.out', immediateRender: false }, t); }
  (c.marks || []).forEach(m => { const t = T(m.at); const tile = tiles[m.day]; const ok = m.kind === 'good';
    const pin = el('div', 'wkpin ' + (ok ? 'ok' : 'bad'), sh, `<i>${ok ? '✓' : '✕'}</i><b>${esc(m.text || '')}</b>`); pin.style.left = (60 + m.day * 140 + 62) + 'px';
    K.vis(pin, t, b); tl.fromTo(pin, { y: 60, opacity: 0, scale: .6 }, { y: 0, opacity: 1, scale: 1, duration: .3, ease: 'back.out(2)', immediateRender: false }, t);
    tl.to(tile, { backgroundColor: ok ? 'rgba(61,220,132,.25)' : 'rgba(229,55,45,.3)', borderColor: ok ? '#3ddc84' : '#e5372d', duration: .2 }, t); sfx(t, ok ? 'pro_pop/tink' : 'pro_impact/air', -13); });
};

// ================================================================== Clock: a calendar page and an analog clock side by side; each item flips the page and spins the hands to a time
// items: [{at, place, month, day, h (0-23), m, label}], chip: {text, at}
BL.Clock = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b); const it = c.items || [];
  const pl = el('div', 'ckplace', sh); const cal = el('div', 'ckcal', sh, '<div class="ckmon"></div><div class="ckday"></div><div class="ckdow mono"></div>');
  const face = el('div', 'ckface', sh); let ticks = ''; for (let k = 0; k < 60; k++) ticks += `<line x1="100" y1="${k % 5 ? 8 : 6}" x2="100" y2="${k % 5 ? 13 : 22}" stroke-width="${k % 5 ? 1.5 : 4}" transform="rotate(${k * 6} 100 100)"/>`;
  face.innerHTML = `<svg viewBox="0 0 200 200"><circle cx="100" cy="100" r="96" class="ckrim"/>${ticks}<line class="ckh" x1="100" y1="100" x2="100" y2="52"/><line class="ckm" x1="100" y1="100" x2="100" y2="28"/><circle cx="100" cy="100" r="7" fill="#e5372d"/></svg>`;
  const hh = face.querySelector('.ckh'), mm = face.querySelector('.ckm'); const dig = el('div', 'ckdig', sh);
  tl.fromTo([cal, face], { y: 120, opacity: 0 }, { y: 0, opacity: 1, duration: .35, ease: 'back.out(1.4)', stagger: .08, immediateRender: false }, a);
  let H = 0, M = 0;
  it.forEach((o, k) => { const t = o.at != null ? T(o.at) : a + .05; const nh = (o.h % 12) * 30 + o.m * .5, nm = o.m * 6;
    let th = nh, tm = nm; if (k > 0) { while (th <= H) th += 360; tm = nm + 360 * Math.round((th - H) / 360 * 3 + 2); }
    const setTxt = () => { pl.textContent = o.place || ''; cal.querySelector('.ckmon').textContent = o.month; cal.querySelector('.ckday').textContent = o.day; cal.querySelector('.ckdow').textContent = o.dow || ''; dig.textContent = o.label || ''; };
    if (k === 0) { tl.call(setTxt, null, a); tl.set(hh, { rotation: th, svgOrigin: '100 100' }, a); tl.set(mm, { rotation: tm, svgOrigin: '100 100' }, a); }
    else { tl.to(cal, { rotationX: 90, duration: .16, ease: 'power2.in' }, t); tl.call(setTxt, null, t + .16); tl.to(cal, { rotationX: 0, duration: .2, ease: 'power2.out' }, t + .16);
      tl.fromTo(hh, { rotation: H, svgOrigin: '100 100' }, { rotation: th, duration: 1.0, ease: 'power3.inOut', immediateRender: false }, t);
      tl.fromTo(mm, { rotation: M, svgOrigin: '100 100' }, { rotation: tm, duration: 1.0, ease: 'power3.inOut', immediateRender: false }, t);
      tl.fromTo(dig, { opacity: 0 }, { opacity: 1, duration: .2, immediateRender: false }, t + .9); sfx(t, 'swipe/paper', -15); sfx(t + .1, 'pro_riser/air_gate', -19); sfx(t + 1, 'pro_pop/thup', -13); }
    H = th; M = tm; });
  if (c.chip) { const ch = el('div', 'bbadge', sh, esc(c.chip.text)); ch.style.top = '1560px'; const t = T(c.chip.at); K.vis(ch, t, b); tl.fromTo(ch, { scale: 2.2, opacity: 0, rotation: -10 }, { scale: 1, opacity: 1, rotation: -4, duration: .22, ease: 'power4.out', immediateRender: false }, t); }
};

// ================================================================== Duo: two tall cards (two products, two models) land one by one, then a link joins them
// cards: [{logo (svg), title, sub, chip, chipIcon (svg), at, color}], link: {text, at}
BL.Duo = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b); const cs = c.cards || [];
  cs.forEach((o, k) => { const d = el('div', 'duocard ' + (k ? 'duor' : 'duol'), sh); if (o.color) d.style.setProperty('--dc', o.color);
    el('div', 'duologo', d, o.logo || ''); const fit = (e, txt, big) => { const L = Math.max(...String(txt).split(' ').map(w => w.length)); if (L > 7 || String(txt).length > 9) e.style.fontSize = Math.round(big * Math.min(1, 7.5 / Math.max(L, 9))) + 'px'; };
    fit(el('div', 'duotitle', d, esc(o.title || '')), o.title || '', 82); fit(el('div', 'duosub', d, esc(o.sub || '')), o.sub || '', 74);
    const ch = el('div', 'duochip mono', d, (o.chipIcon || '') + `<span>${esc(o.chip || '')}</span>`);
    const t = o.at != null ? T(o.at) : a + .1 + k * .5;
    tl.fromTo(d, { y: 900, rotation: k ? 14 : -14, opacity: 0 }, { y: 0, rotation: k ? 4 : -4, opacity: 1, duration: .5, ease: 'back.out(1.5)', immediateRender: false }, t);
    tl.fromTo(ch, { scale: 0 }, { scale: 1, duration: .25, ease: 'back.out(2.4)', immediateRender: false }, t + .35);
    tl.to(d, { y: -18, duration: Math.max(.3, b - t - .5), ease: 'sine.inOut' }, t + .5);
    sfx(t, k ? 'swish/cane' : 'swish/soft', -13); sfx(t + .35, 'pro_pop/boop', -18); });
  if (c.link) { const t = T(c.link.at); const ln = el('div', 'duolink mono', sh, `<i></i><span>${esc(c.link.text)}</span><i></i>`); K.vis(ln, t, b);
    tl.fromTo(ln, { scaleX: 0 }, { scaleX: 1, duration: .35, ease: 'power3.out', immediateRender: false }, t); sfx(t, 'whoosh_fast/crisp', -15); }
};

// ================================================================== Race: two step lines race across a chart (a progress-over-time chart); end labels land
// title, sub, xmax, xunit, ticks: [x], series: [{name, color, logo, pts: [[x, y 0..1]], end}], at, dur, mark: {x, label} (a dashed line)
BL.Race = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b);
  const ox = 130, oy = 1330, w = 830, h = 720, X = x => ox + w * x / (c.xmax || 1), Y = y => oy - h * y;
  el('div', 'rctitle', sh, esc(c.title || '')); el('div', 'rcsub mono', sh, esc(c.sub || ''));
  const t0 = c.at != null ? T(c.at) : a + .3, dur = c.dur || Math.max(.8, b - t0 - .6);
  const ns = 'http://www.w3.org/2000/svg'; const svg = document.createElementNS(ns, 'svg'); svg.setAttribute('class', 'rcsvg'); svg.setAttribute('viewBox', `0 0 ${W} ${H}`); sh.appendChild(svg);
  const mk = (tag, at) => { const e = document.createElementNS(ns, tag); for (const k in at) e.setAttribute(k, at[k]); svg.appendChild(e); return e; };
  [0, .25, .5, .75, 1].forEach(v => { mk('line', { x1: ox, x2: ox + w, y1: Y(v), y2: Y(v), stroke: '#ffffff1c', 'stroke-width': 2 }); const lb = el('div', 'rcy mono', sh, Math.round(v * 100) + '%'); lb.style.top = (Y(v) - 16) + 'px'; });
  (c.ticks || []).forEach(x => { const lb = el('div', 'rcx mono', sh, esc(String(x))); lb.style.left = (X(x) - 40) + 'px'; });
  el('div', 'rcxu mono', sh, esc(c.xunit || ''));
  mk('line', { x1: ox, x2: ox + w, y1: oy, y2: oy, stroke: '#f2f1ee', 'stroke-width': 4 });
  const clock = el('div', 'rcclock', sh); const cv = { x: 0 }; const upd = () => { clock.innerHTML = `${Math.round(cv.x)}<small> ${esc(c.xunit || '')}</small>`; }; upd();
  tl.fromTo(cv, { x: 0 }, { x: c.xmax || 1, duration: dur, ease: 'none', onUpdate: upd, immediateRender: false }, t0);
  if (c.mark) { const l = mk('line', { x1: X(c.mark.x), x2: X(c.mark.x), y1: oy, y2: oy - h - 20, stroke: '#ffffff66', 'stroke-width': 3, 'stroke-dasharray': '10 10' }); }
  (c.series || []).forEach((s, k) => { const pts = s.pts; let d = `M${X(0)} ${Y(0)}`; let py = 0; pts.forEach(([x, y]) => { d += ` L${X(x)} ${Y(py)} L${X(x)} ${Y(y)}`; py = y; }); d += ` L${X(c.xmax)} ${Y(py)}`;
    const p = mk('path', { d, fill: 'none', stroke: s.color, 'stroke-width': 12, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' }); const L = p.getTotalLength();
    p.style.strokeDasharray = L; tl.fromTo(p, { strokeDashoffset: L }, { strokeDashoffset: 0, duration: dur, ease: 'none', immediateRender: false }, t0);
    const dot = mk('circle', { r: 20, fill: s.color, stroke: '#0b0b0b', 'stroke-width': 5 }); const o = { u: 0 };
    tl.fromTo(o, { u: 0 }, { u: 1, duration: dur, ease: 'none', immediateRender: false, onUpdate: () => { const q = p.getPointAtLength(L * o.u); dot.setAttribute('cx', q.x); dot.setAttribute('cy', q.y); } }, t0);
    const lg = el('div', 'rcleg', sh, `${s.logo || ''}<span>${esc(s.name)}</span>`); lg.style.top = (320 + k * 64) + 'px'; lg.style.setProperty('--sc', s.color);
    if (s.end) { const e = el('div', 'rcend', sh, esc(s.end)); e.style.left = (X(c.xmax) - 250) + 'px'; e.style.top = (Y(py) + (py > .5 ? 30 : -150)) + 'px'; e.style.color = s.color;
      const te = s.endAt != null ? T(s.endAt) : t0 + dur; K.vis(e, te, b); tl.fromTo(e, { scale: 2.4, opacity: 0 }, { scale: 1, opacity: 1, duration: .2, ease: 'power4.out', immediateRender: false }, te); K.fx(te, 'hit'); } });
  sfx(t0, 'pro_riser/air_gate', -16, { dur: +dur.toFixed(2) });
};

// ================================================================== Bars: a ranked bar chart; bars grow and their numbers count up, the winner glows
// title, sub, rows: [[logo svg, name, value, color, win]], max, at, stagger, unit
BL.Bars = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b);
  if (c.ghost) { const gh = el('div', 'bghost', sh, esc(c.ghost)); tl.fromTo(gh, { scale: 1.15, opacity: 0 }, { scale: 1, opacity: 1, duration: .6, ease: 'power3.out', immediateRender: false }, a); }
  el('div', 'rctitle', sh, esc(c.title || '')); el('div', 'rcsub mono', sh, esc(c.sub || ''));
  const t0 = c.at != null ? T(c.at) : a + .2, st = c.stagger ?? .18, mx = c.max || 100;
  (c.rows || []).forEach(([lg, nm, v, colr, win], k) => { const r = el('div', 'brow' + (win ? ' bwin' : ''), sh); r.style.top = ((c.top || 430) + k * (c.gap || 220)) + 'px';
    el('div', 'blogo', r, lg || ''); el('div', 'bname', r, esc(nm)); const tr = el('div', 'btrack', r); const f = el('i', '', tr); f.style.background = colr;
    const num = el('div', 'bnum', r); const o = { v: 0 }; const upd = () => { num.textContent = o.v.toFixed(1) + (c.unit ?? '%'); }; upd(); const t = t0 + k * st;
    tl.fromTo(r, { x: -200, opacity: 0 }, { x: 0, opacity: 1, duration: .3, ease: 'power3.out', immediateRender: false }, t);
    tl.fromTo(f, { width: '0%' }, { width: (v / mx * 100) + '%', duration: .8, ease: 'power3.out', immediateRender: false }, t + .1);
    tl.fromTo(o, { v: 0 }, { v, duration: .8, ease: 'power3.out', onUpdate: upd, immediateRender: false }, t + .1); sfx(t, 'pro_pop/tink', -18);
    if (win) { tl.fromTo(r, { scale: 1 }, { scale: 1.05, duration: .25, yoyo: true, repeat: 1, ease: 'power2.out', immediateRender: false }, t0 + (c.rows.length) * st + .7); K.fx(t0 + c.rows.length * st + .7, 'hit'); } });
  if (c.badge) { const bd = el('div', 'bbadge', sh, esc(c.badge.text)); const t = T(c.badge.at); K.vis(bd, t, b); tl.fromTo(bd, { scale: 2.4, opacity: 0, rotation: -12 }, { scale: 1, opacity: 1, rotation: -5, duration: .22, ease: 'power4.out', immediateRender: false }, t); K.fx(t, 'hit'); }
};

// ================================================================== Price: old prices get struck through and the new ones slam in, then a discount tag
// title, rows: [[label, old, new]], unit, at, tag, tagAt
BL.Price = (box, c, T, S) => {
  const a = S.start, b = S.end; K.ground(a, c.ground || 'bg'); const sh = layer(box, a, b); const t0 = c.at != null ? T(c.at) : a + .2;
  const card = el('div', 'prcard', sh); el('div', 'prhead', card, (c.logo || '') + `<span>${esc(c.title || '')}</span>`);
  tl.fromTo(card, { y: 500, opacity: 0, rotation: -5 }, { y: 0, opacity: 1, rotation: -1.5, duration: .45, ease: 'back.out(1.4)', immediateRender: false }, a); sfx(a, 'swish/soft', -14);
  (c.rows || []).forEach(([lb, o, n], k) => { const r = el('div', 'prrow', card); el('div', 'prlab mono', r, esc(lb)); const od = el('div', 'prold', r, esc(o)); const ln = el('i', 'prline', od); const nw = el('div', 'prnew', r, esc(n));
    const t = t0 + .3 + k * .35; tl.fromTo(ln, { scaleX: 0 }, { scaleX: 1, duration: .2, ease: 'power3.out', immediateRender: false }, t); tl.to(od, { opacity: .45, duration: .2 }, t + .1);
    tl.fromTo(nw, { scale: 2.2, opacity: 0 }, { scale: 1, opacity: 1, duration: .22, ease: 'power4.out', immediateRender: false }, t + .15); sfx(t, 'swish/blade', -15); sfx(t + .15, 'pro_pop/thup', -15); });
  el('div', 'prunit mono', card, esc(c.unit || ''));
  if (c.tag) { const tg = el('div', 'prtag', sh, esc(c.tag)); const t = c.tagAt != null ? T(c.tagAt) : t0 + 1.2; K.vis(tg, t, b);
    tl.fromTo(tg, { scale: 2.6, opacity: 0, rotation: 14 }, { scale: 1, opacity: 1, rotation: 8, duration: .22, ease: 'power4.out', immediateRender: false }, t); K.fx(t, 'punch'); }
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
  else if (c.push !== false) tl.fromTo(frame, { scale: 1.02, x: -20 }, { scale: 1.16, x: 30, duration: b - a, ease: 'none', immediateRender: false }, a);   // push + pan (push: false for a clip with its own camera move)
  // blur: [px, at] starts out of focus (a backdrop for an overlay) and snaps into focus at `at`
  if (c.blur) { const [px, k] = c.blur, t = T(k); tl.set(m, { filter: `blur(${px}px) brightness(.55)` }, a);
    tl.to(m, { filter: 'blur(0px) brightness(1)', duration: .22, ease: 'power3.out' }, t); K.flash(t, '#fff', .06, .25); sfx(t, 'whoosh_fast/crisp', -12); }
  // overlay: {src, out, width} an image (a title or logo) over the picture: pops in at the start, flicks out fast at `out`
  if (c.overlay) { const o = c.overlay, ov = el('img', 'poverlay', sh); ov.src = o.src; const ow = o.width || 760; ov.style.width = ow + 'px';
    ov.style.left = Math.round((W - ow) / 2) + 'px'; ov.style.top = (o.top ?? 560) + 'px'; const t2 = T(o.out);
    tl.fromTo(ov, { scale: 1.18, opacity: rv0(c) ? 1 : 0 }, { scale: 1, opacity: 1, duration: .16, ease: 'power4.out', immediateRender: false }, a);
    tl.to(ov, { scale: 1.06, rotation: -2, duration: Math.max(.1, t2 - a - .1), ease: 'none' }, a + .16);
    tl.to(ov, { scale: 2.4, opacity: 0, duration: .12, ease: 'power3.in' }, t2); tl.set(ov, { visibility: 'hidden' }, t2 + .12); sfx(t2, 'whoosh_fast/sleeve', -11); }
  // head: {text, sub, top} a heading in the empty top of a landscape clip
  if (c.head) { const hh = el('div', 'stkhead', sh, `<b>${esc(c.head.text)}</b><span class="mono">${esc(c.head.sub || '')}</span>`); hh.style.top = (c.head.top ?? 170) + 'px';
    tl.fromTo(hh, { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: .25, ease: 'power3.out', immediateRender: false }, a + .05); }
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
  if (c.line !== false) {   // line: false drops the opening line and slash (the mark and name land on a clean ground)
    const ln = el('div', 'lline', sh); ln.style.background = ink; tl.fromTo(ln, { scaleX: 0 }, { scaleX: 1, duration: .2, ease: 'expo.out', immediateRender: false }, a);
    const sl = el('div', 'lslash', sh); tl.fromTo(sl, { scaleY: 0 }, { scaleY: 1, duration: .14, ease: 'power4.out', immediateRender: false }, a + .12); K.fx(a + .14, 'hit'); sfx(a + .14, 'sub_drop/808', -9);
    tl.to([ln, sl], { opacity: 0, duration: .2 }, a + .5); }
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
