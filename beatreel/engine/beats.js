// beatreel engine: builds the reel from window.REEL (written by beatreel.py) onto one paused GSAP timeline.
// Every time is in seconds on the reel clock. All state changes go through the timeline (tl.set / tweens), never
// through callbacks, so the renderer can seek to any frame in any order.
//
// What the references do, and this file copies:
//  - captions reveal one word at a time (a word fades in grey, then turns ink; key words red italic serif),
//    in short phrase blocks that slide up and out when the next block starts;
//  - each idea gets a hero (often a big panel) that builds up piece by piece on the words, then leaves upward;
//  - numbers roll like an odometer; text can decode; stamps slam; grids assemble and drop away;
//  - the presenter rises in on the first beat, can start big ("cam": "big") and shrink when the hero lands,
//    and reacts with burst lines around the head.
(function () {
  const R = window.REEL, st = document.getElementById('stage'), tl = gsap.timeline({ paused: true });
  const $ = (tag, cls, parent, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; (parent || st).appendChild(e); return e; };
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const vis = (el, a, b) => { tl.set(el, { autoAlpha: 0 }, 0); tl.set(el, { autoAlpha: 1 }, Math.max(0, a)); if (b != null) tl.set(el, { autoAlpha: 0 }, b); };
  const on = (el, t) => { tl.set(el, { attr: { 'data-on': 0 } }, 0); tl.set(el, { attr: { 'data-on': 1 } }, t); };
  // seeded random, so a frame always renders the same
  let seed = 7; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  st.className = 't-' + (R.theme || 'paper');

  // ---- meta row: slug on the left, a running counter on the right
  const meta = document.getElementById('meta'); if (R.meta === false) meta.style.display = 'none'; const slug = $('span', '', meta), cnt = $('span', '', meta); cnt.id = 'cnt'; slug.style.position = 'relative'; cnt.style.position = 'relative';
  const counter = R.counter || null; let lastVal = null;
  R.beats.forEach(b => {
    const sp = $('span', '', slug, '// ' + esc(b.slug || '')); sp.style.cssText = 'position:absolute;left:0;top:0;white-space:nowrap'; vis(sp, b.t0, b.t1);
    if (counter) { const v = b.count ?? lastVal ?? counter.start ?? ''; const changed = lastVal !== null && v !== lastVal;
      const cp = $('span', '', cnt, esc(counter.label) + ' <b>' + esc(v) + '</b>'); cp.style.cssText = 'position:absolute;right:0;top:0;white-space:nowrap;transform-origin:100% 50%'; vis(cp, b.t0, b.t1);
      if (changed) tl.fromTo(cp, { scale: 1.35 }, { scale: 1, duration: .3, ease: 'back.out(3)', immediateRender: false }, b.t0);
      lastVal = v; }
  });

  // ---- background floods (a beat can turn the page red / black) and halftone wipes
  const flood = document.getElementById('flood');
  R.beats.forEach(b => {
    const col = b.bg === 'red' ? (getComputedStyle(st).getPropertyValue('--accent').trim() || '#e8452c') : b.bg === 'black' ? '#0d0d0d' : null;
    if (col) { tl.set(flood, { background: col, opacity: 1 }, b.t0); tl.set(flood, { opacity: 0 }, b.t1);
      tl.set(st, { '--ink': '#fff', '--mute': 'rgba(255,255,255,.4)', '--meta': 'rgba(255,255,255,.7)', '--accent': b.bg === 'red' ? '#111' : 'var(--hi)' }, b.t0);
      tl.set(st, { '--ink': '', '--mute': '', '--meta': '', '--accent': '' }, b.t1); }
    if (b.wipe) { const w = document.getElementById('wipe'); tl.set(w, { '--r': '0px' }, 0);
      tl.to(w, { '--r': '30px', duration: .2, ease: 'power2.in' }, b.t0 - .2); tl.to(w, { '--r': '0px', duration: .22, ease: 'power2.out' }, b.t0); }
  });

  // ---- caption: phrase blocks; each word fades in grey on its time and turns ink a beat later
  const cap = document.getElementById('cap');
  R.lines.forEach((ln, k) => {
    const el = $('div', 'cl', cap); el.innerHTML = ln.words.map(w => `<span class="w${w.it ? ' it' : ''}">${esc(w.w)}</span>`).join('');
    const end = k + 1 < R.lines.length ? R.lines[k + 1].start - .07 : R.dur; vis(el, ln.start - .06, end);
    el.querySelectorAll('.w').forEach((s, j) => { const t = ln.words[j].t;
      tl.fromTo(s, { opacity: 0, y: 12, filter: 'blur(5px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: .16, ease: 'power2.out', immediateRender: true }, t - .06);
      on(s, t + .08); });
    if (k + 1 < R.lines.length) tl.to(el, { y: -26, opacity: 0, duration: .12, ease: 'power2.in' }, end - .12);
    requestAnimationFrame(() => { const f = Math.min(1, 904 / Math.max(1, el.scrollWidth)); if (f < 1) el.style.transform = `scale(${f})`; });
  });

  // ---- heroes
  const heroes = document.getElementById('heroes'); const fmt = (v, d) => Number(v).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
  const CK = '<svg viewBox="0 0 24 24" width="62%" height="62%" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 12.5l5 5L19.5 7"/></svg>';
  const XX = '<svg viewBox="0 0 24 24" width="58%" height="58%" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>';
  const B = {
    card: (o, e) => { e.className += ' card hs'; e.style.width = (o.w || 820) + 'px'; e.innerHTML = (o.label ? `<div class="lbl">${esc(o.label)}</div>` : '') + (o.icon ? `<div class="cic">${o.svg}</div>` : '') + (o.title ? `<h3>${o.title}</h3>` : '') + (o.text ? `<p>${o.text}</p>` : '') + (o.img ? `<img src="${o.img}" style="width:100%;border-radius:14px;margin-top:18px">` : ''); },
    // an odometer: digits roll (random, blurred) and settle left to right
    num: (o, e, t) => { e.className += ' num'; if (o.size) e.style.fontSize = o.size + 'px'; const pre = o.prefix ?? '', suf = o.suffix ?? '', d = o.decimals ?? 0, v = { x: o.from ?? 0, p: 0 };
      const span = $('span', 'nv', e); if (o.label) $('small', '', e, esc(o.label));
      const up = () => { const s = fmt(v.x, d); let out = ''; const n = s.length;
        for (let i = 0; i < n; i++) { const c = s[i]; out += (/\d/.test(c) && v.p < 1 && i / n >= v.p) ? String(Math.floor(((v.x * 7.3 + i * 13) * 97) % 10)) : c; }
        span.textContent = pre + out + suf; span.style.textShadow = v.p < 1 ? `0 -22px 8px var(--ghost), 0 22px 8px var(--ghost)` : 'none'; }; up();
      tl.to(v, { x: o.value, p: 1, duration: o.count ?? .9, ease: 'power3.out', onUpdate: up }, t + .05);
      tl.fromTo(span, { filter: 'blur(3px)' }, { filter: 'blur(0px)', duration: o.count ?? .9, ease: 'power3.in', immediateRender: false }, t + .05); },
    // text that decodes from noise, left to right
    scramble: (o, e, t) => { e.className += ' scr' + (o.red ? ' red' : ''); if (o.size) e.style.fontSize = o.size + 'px'; const txt = String(o.text || ''), v = { p: 0 }, A = '#%&@$0123456789XZ';
      const span = $('span', '', e); const up = () => { let s = ''; for (let i = 0; i < txt.length; i++) s += (i / txt.length < v.p || txt[i] === ' ') ? txt[i] : A[Math.floor((i * 31 + v.p * 977) % A.length)]; span.textContent = s; }; up();
      tl.to(v, { p: 1.001, duration: o.decode ?? .7, ease: 'none', onUpdate: up }, t + .05); if (o.label) $('small', '', e, esc(o.label)); },
    sticker: (o, e) => { e.innerHTML = (o.lines || [o.text]).map((s, k) => `<div class="stk ${o.red && k === (o.redLine ?? 0) ? 'red' : ''}" style="display:block;width:max-content;margin:${k ? 10 : 0}px auto 0${o.size ? `;font-size:${o.size}px` : ''}">${esc(s)}</div>`).join(''); },
    stamp: (o, e) => { e.innerHTML = `<div class="stamp"${o.size ? ` style="font-size:${o.size}px"` : ''}>${esc(o.text)}</div>`; },
    shot: (o, e, t) => { e.className += ' shot hs'; e.style.width = (o.w || 900) + 'px';
      e.innerHTML = `<div class="bar"><i></i><i></i><i></i><span>${esc(o.label || '')}</span></div><div style="position:relative"><img src="${o.src}">${(o.rings || []).map(r => `<div class="ring" style="left:${r[0]}%;top:${r[1]}%;width:${r[2]}%;height:${r[3]}%"></div>`).join('')}</div>`;
      e.querySelectorAll('.ring').forEach((r, k) => { const a = o.ringAt?.[k] ?? t + .5; vis(r, a); tl.fromTo(r, { scale: 1.6, opacity: 0 }, { scale: 1, opacity: 1, duration: .3, ease: 'back.out(2)', immediateRender: false }, a); }); },
    phone: (o, e) => { e.className += ' phone hs'; e.innerHTML = `<div class="scr">${o.src ? `<img src="${o.src}">` : `<div class="pt">${o.title || ''}</div>`}</div>`; if (o.scale) e.style.scale = o.scale; },
    term: (o, e, t) => { e.className += ' term hs'; if (o.w) e.style.width = o.w + 'px'; e.innerHTML = `<div class="tb"><i></i><i></i><i></i><span>${esc(o.title || 'terminal')}</span></div><div class="tx"></div>`;
      const tx = e.querySelector('.tx'), full = (o.lines || []).join('\n'), v = { n: 0 };
      const up = () => { const s = full.slice(0, Math.round(v.n)); tx.innerHTML = esc(s).replace(/\$ /g, '<em>$ </em>') + '<span class="cur"></span>'; }; up();
      tl.to(v, { n: full.length, duration: o.type ?? Math.min(2.2, full.length * .03), ease: 'none', onUpdate: up }, t + .25); },
    logo: (o, e) => { e.className += ' logo'; e.innerHTML = `<div class="mk hs">${o.svg || ''}</div>${o.name ? `<b>${esc(o.name)}</b>` : ''}`; },
    list: (o, e) => { e.className += ' list card hs'; if (o.w) e.style.width = o.w + 'px'; e.innerHTML = (o.title ? `<div class="lbl">${esc(o.title)}</div>` : '') + (o.items || []).map(s => `<div class="li"><div class="bx"><span>${o.mark === 'x' ? XX : CK}</span></div><span>${esc(s)}</span></div>`).join('');
      e.querySelectorAll('.li').forEach((li, k) => { const at = o.ticks?.[k]; if (at == null) return; on(li, at);
        tl.fromTo(li.querySelector('.bx'), { scale: 1.6 }, { scale: 1, duration: .25, ease: 'back.out(3)', immediateRender: false }, at); }); },
    // icon tiles in a row, each landing on its own word
    row: (o, e, t) => { e.className += ' row'; (o.tiles || []).forEach((x, k) => { const c = $('div', 'tile card hs', e, `<div class="ti">${x.svg || ''}</div><b>${esc(x.label || '')}</b>`); const a = o.ats?.[k] ?? t + k * .25;
      vis(c, a); tl.fromTo(c, { y: 60, scale: .5, rotation: k % 2 ? 8 : -8, opacity: 0 }, { y: 0, scale: 1, rotation: 0, opacity: 1, duration: .38, ease: 'back.out(2)', immediateRender: false }, a); }); },
    grid: (o, e, t) => { e.className += ' grid' + (o.shape === 'doc' ? ' docs' : ''); e.style.gridTemplateColumns = `repeat(${o.cols || 6}, ${o.shape === 'doc' ? 74 : 92}px)`; for (let k = 0; k < (o.n || 24); k++) $('div', 'p', e);
      const ps = [...e.querySelectorAll('.p')]; tl.fromTo(ps, { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: .25, stagger: { each: .012, from: 'random' }, ease: 'back.out(2)', immediateRender: false }, t);
      (o.hi || []).forEach((k, j) => on(ps[k], o.hiAt?.[j] ?? t + .6));
      if (o.dropAt != null) tl.to(ps, { y: () => 260 + rnd() * 300, rotation: () => (rnd() - .5) * 160, opacity: 0, duration: .6, ease: 'power2.in', stagger: { each: .01, from: 'random' } }, o.dropAt); },
    compare: (o, e, t) => { e.className += ' cmp'; const sides = o.swap ? [['good', CK, o.left], ['bad', XX, o.right]] : [['bad', XX, o.left], ['good', CK, o.right]]; e.innerHTML = sides.map(([c, m, s]) => `<div class="card hs ${c}"><div class="mark">${m}</div><h3>${s?.title || ''}</h3><p>${s?.text || ''}</p></div>`).join('');
      const cs = e.querySelectorAll('.card'); const a = o.rightAt ?? t + .6; vis(cs[1], a); tl.fromTo(cs[1], { scale: .6, opacity: 0 }, { scale: 1, opacity: 1, duration: .35, ease: 'back.out(2)', immediateRender: false }, a); },
    comment: (o, e) => { e.className += ' cmt card hs'; e.innerHTML = `<div class="who"><i></i><span>${esc(o.who || 'Your comment')}</span></div><div class="kw">${esc(o.keyword || 'SKILL')}</div>`; },
    date: (o, e) => { e.className += ' date hs'; e.innerHTML = `<div class="m">${esc(o.month)}</div><div class="d">${esc(o.day)}</div>`; },
    image: (o, e) => { e.innerHTML = `<img src="${o.src}" style="width:${o.w || 800}px;display:block;border-radius:${o.radius ?? 20}px">`; if (o.shadow !== false) e.firstChild.className = 'hs'; },
    // a browser window; "incognito": true gives the dark private-window look
    browser: (o, e) => { e.className += ' brw hs' + (o.incognito ? ' inc' : ''); e.style.width = (o.w || 900) + 'px'; e.style.height = (o.h || 560) + 'px';
      e.innerHTML = `<div class="bt"><i></i><i></i><i></i><span class="tab">${esc(o.tab || 'New Tab')}</span></div><div class="ub">${esc(o.url || '')}</div><div class="bb">${o.svg ? `<div class="bic">${o.svg}</div>` : ''}${o.title ? `<h3>${o.title}</h3>` : ''}${o.text ? `<p>${o.text}</p>` : ''}</div>`; },
    // a big panel that holds other items; children are placed in panel pixels and land on their own words
    panel: (o, e) => { e.className += ' panel card hs'; e.style.width = (o.w || 920) + 'px'; e.style.height = (o.h || 760) + 'px';
      if (o.label) $('div', 'lbl plbl', e, esc(o.label)); (o.children || []).forEach(ch => place(ch, e, o)); },
    html: (o, e) => { e.innerHTML = o.html; },
    // a playing clip in a browser window (the <video> is made by beatreel.py so the renderer can drive it)
    video: (o, e) => { e.className += ' brw vid hs'; e.style.width = (o.w || 940) + 'px';
      e.innerHTML = `<div class="bt"><i></i><i></i><i></i><span class="tab">${esc(o.tab || '')}</span><span class="vurl">${esc(o.url || '')}</span></div><div class="vb" style="aspect-ratio:${o.aspect || '16/9'}"></div>`;
      const v = document.getElementById(o.vid); if (v) { v.style.cssText = 'width:100%;height:100%;object-fit:' + (o.fit || 'cover') + ';display:block'; e.querySelector('.vb').appendChild(v); }
      (o.words || []).forEach(([at, txt, red]) => { const w = $('div', 'vword' + (red ? ' red' : ''), e, esc(txt)); vis(w, at, o.until);
        tl.fromTo(w, { scale: 1.8, opacity: 0, rotation: -6 }, { scale: 1, opacity: 1, rotation: -3, duration: .22, ease: 'back.out(2.4)', immediateRender: false }, at);
        e.querySelectorAll('.vword').forEach(x => { if (x !== w) tl.set(x, { autoAlpha: 0 }, at); }); }); },
    // the follow card: avatar, handle, a button that gets tapped and turns into "Following"
    follow: (o, e, t) => { e.className += ' fol card hs';
      e.innerHTML = `<img src="${o.img || ''}"><b>${esc(o.handle || '')}</b><span>${esc(o.text || '')}</span><div class="fbtn"><span class="a">Follow</span><span class="b">Following ✓</span></div>`;
      const btn = e.querySelector('.fbtn'), at = o.tapAt ?? t + .6; on(btn, at);
      tl.fromTo(btn, { scale: .86 }, { scale: 1, duration: .3, ease: 'back.out(3)', immediateRender: false }, at); },
  };
  function place(o, parent, owner) {
    const e = $('div', 'h', parent); const t = o.at, u = o.until ?? owner?.until ?? R.dur;
    (B[o.type] || B.card)(o, e, t);
    e.style.left = (o.x ?? (owner ? (owner.w || 920) / 2 : 540)) + 'px'; e.style.top = (o.y ?? (owner ? (owner.h || 760) / 2 : 820)) + 'px'; e.style.zIndex = o.z ?? 1;
    const S1 = o.scale || 1;
    gsap.set(e, { xPercent: -50, yPercent: -50, rotation: o.rot || 0, scale: S1 });
    vis(e, t, u);
    const stamp = o.type === 'stamp', stk = o.type === 'sticker';
    const pop = stamp ? { scale: 2.6, opacity: 0, rotation: (o.rot || 0) - 14 } : { scale: .55, opacity: 0, y: 46, rotation: (o.rot || 0) + (stk ? -12 : -4) };
    pop.scale *= S1; tl.fromTo(e, pop, { scale: S1, opacity: 1, y: 0, rotation: o.rot || 0, duration: stamp ? .2 : .42, ease: stamp ? 'power4.out' : 'back.out(1.8)', immediateRender: false }, t);
    if (!owner && o.float !== false && u - t > 1.4) tl.to(e, { y: -10, duration: (u - t - .5) / 2, ease: 'sine.inOut', yoyo: true, repeat: 1 }, t + .45);
    if (o.exit !== 'cut' && u < R.dur && (!owner || o.until != null)) tl.to(e, { y: owner ? -20 : -70, opacity: 0, duration: .16, ease: 'power2.in' }, u - .16);
    return e;
  }
  R.items.forEach(o => place(o, heroes, null));

  // ---- presenter: rises in, can start big and shrink when the hero lands, bounces on beat changes, reacts
  const pres = document.getElementById('pres'), pin = document.getElementById('presin'); const P = R.presenter || {};
  tl.fromTo(pres, { y: 700 }, { y: 0, duration: .5, ease: 'back.out(1.3)', immediateRender: true }, 0);
  const pbox = document.getElementById('pbox');
  if (pbox) { tl.fromTo(pbox, { y: 700 }, { y: 0, duration: .5, ease: 'back.out(1.1)', immediateRender: true }, 0);
    R.beats.forEach(b => { if (b.pres === false) tl.to(pbox, { y: 900, duration: .4, ease: 'power3.in' }, b.t0 - .05); }); }
  (R.cams || []).forEach(c => { tl.set(pin, { scale: c.scale, y: c.y }, c.t0); if (c.t1 != null) tl.to(pin, { scale: 1, y: 0, duration: .38, ease: 'power3.inOut' }, c.t1); });
  R.beats.forEach(b => { if (b.pres === false) tl.to(pres, { y: 900, duration: .4, ease: 'power3.in' }, b.t0 - .05); });
  R.beats.forEach((b, k) => { if (k) tl.fromTo(pres, { scale: .975 }, { scale: 1, duration: .28, ease: 'back.out(3)', transformOrigin: '50% 100%', immediateRender: false }, b.t0); });
  const hx = (P.headX ?? .517) * 100, hy = (P.headY ?? .31) * 100;
  (R.reacts || []).forEach(t => {
    const bu = $('div', 'burst', pin); bu.style.left = hx + '%'; bu.style.top = hy + '%';
    bu.innerHTML = '<svg viewBox="-100 -100 200 200">' + Array.from({ length: 10 }, (_, i) => { const a = i / 10 * Math.PI * 2 + .2; const r1 = 70, r2 = 92 + (i % 2) * 8;
      return `<line x1="${(Math.cos(a) * r1).toFixed(1)}" y1="${(Math.sin(a) * r1).toFixed(1)}" x2="${(Math.cos(a) * r2).toFixed(1)}" y2="${(Math.sin(a) * r2).toFixed(1)}"/>`; }).join('') + '</svg>';
    vis(bu, t, t + .55); tl.fromTo(bu, { scale: .6, opacity: 1 }, { scale: 1.15, opacity: 0, duration: .55, ease: 'power2.out', immediateRender: false }, t);
    tl.fromTo(pin, { x: -8 }, { x: 0, duration: .3, ease: 'elastic.out(1.2, .3)', immediateRender: false }, t);
  });

  window.__timelines = window.__timelines || {}; window.__timelines['reel'] = tl;
})();
