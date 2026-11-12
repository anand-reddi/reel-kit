// beatreel engine: builds the reel from window.REEL (written by beatreel.py) onto one paused GSAP timeline.
// Every time is in seconds on the reel clock. Items pop in on their word and leave when their beat ends.
(function () {
  const R = window.REEL, st = document.getElementById('stage'), tl = gsap.timeline({ paused: true });
  const $ = (tag, cls, parent, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; (parent || st).appendChild(e); return e; };
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const vis = (el, a, b) => { tl.set(el, { autoAlpha: 0 }, 0); tl.set(el, { autoAlpha: 1 }, a); if (b != null) tl.set(el, { autoAlpha: 0 }, b); };
  st.className = 't-' + (R.theme || 'paper');

  // ---- meta row: slug on the left, a running counter on the right
  const meta = document.getElementById('meta'); const slug = $('span', '', meta), cnt = $('span', '', meta); cnt.id = 'cnt'; slug.style.position = 'relative'; cnt.style.position = 'relative';
  const counter = R.counter || null; let lastVal = null;
  R.beats.forEach((b, k) => {
    const sp = $('span', '', slug, '// ' + esc(b.slug || '')); sp.style.cssText = 'position:absolute;left:0;top:0;white-space:nowrap'; vis(sp, b.t0, b.t1);
    if (counter) { const v = b.count ?? lastVal ?? counter.start ?? ''; const changed = lastVal !== null && v !== lastVal;
      const cp = $('span', '', cnt, esc(counter.label) + ' <b>' + esc(v) + '</b>'); cp.style.cssText = 'position:absolute;right:0;top:0;white-space:nowrap;transform-origin:100% 50%'; vis(cp, b.t0, b.t1);
      if (changed) tl.fromTo(cp, { scale: 1.3 }, { scale: 1, duration: .3, ease: 'back.out(3)', immediateRender: false }, b.t0);
      lastVal = v; }
  });

  // ---- background floods (a beat can turn the page red / black) and halftone wipes
  const flood = document.getElementById('flood');
  R.beats.forEach(b => {
    const col = b.bg === 'red' ? 'var(--accent)' : b.bg === 'black' ? '#0d0d0d' : null;
    if (col) { tl.set(flood, { background: col, opacity: 1 }, b.t0); tl.set(flood, { opacity: 0 }, b.t1);
      tl.set(st, { '--ink': '#fff', '--mute': 'rgba(255,255,255,.4)', '--meta': 'rgba(255,255,255,.7)', '--accent': b.bg === 'red' ? '#111' : 'var(--hi)' }, b.t0);
      tl.set(st, { '--ink': '', '--mute': '', '--meta': '', '--accent': '' }, b.t1); }
    if (b.wipe) { const w = document.getElementById('wipe'); tl.set(w, { '--r': '0px' }, 0);
      tl.to(w, { '--r': '30px', duration: .2, ease: 'power2.in' }, b.t0 - .2); tl.to(w, { '--r': '0px', duration: .22, ease: 'power2.out' }, b.t0); }
  });

  // ---- karaoke caption: one script line at a time; words go from grey to ink (italic serif ones go red)
  const cap = document.getElementById('cap');
  R.lines.forEach((ln, k) => {
    const el = $('div', 'cl', cap); el.innerHTML = ln.words.map(w => `<span class="w${w.it ? ' it' : ''}">${esc(w.w)}</span>`).join('');
    const end = k + 1 < R.lines.length ? R.lines[k + 1].start - .02 : R.dur; vis(el, ln.start - .05, end);
    el.querySelectorAll('.w').forEach((s, j) => { tl.set(s, { attr: { 'data-on': 0 } }, 0); tl.set(s, { attr: { 'data-on': 1 } }, ln.words[j].t); });
    // lines longer than the frame are scaled down once fonts are in
    requestAnimationFrame(() => { const f = Math.min(1, 900 / Math.max(1, el.scrollWidth)); if (f < 1) el.style.transform = `scale(${f})`; });
  });

  // ---- heroes
  const heroes = document.getElementById('heroes'); const fmt = (v, d) => Number(v).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
  const B = {
    card: (o, e) => { e.className += ' card hs'; e.style.width = (o.w || 820) + 'px'; e.innerHTML = (o.label ? `<div class="lbl">${esc(o.label)}</div>` : '') + (o.title ? `<h3>${o.title}</h3>` : '') + (o.text ? `<p>${o.text}</p>` : '') + (o.img ? `<img src="${o.img}" style="width:100%;border-radius:14px;margin-top:18px">` : ''); },
    num: (o, e, t) => { e.className += ' num'; const pre = o.prefix ?? '', suf = o.suffix ?? '', d = o.decimals ?? 0, v = { x: o.from ?? 0 };
      const span = $('span', '', e); $('small', '', e, esc(o.label || '')); const up = () => span.textContent = pre + fmt(v.x, d) + suf; up();
      tl.to(v, { x: o.value, duration: o.count ?? .9, ease: 'power3.out', onUpdate: up }, t + .05); },
    sticker: (o, e) => { e.innerHTML = (o.lines || [o.text]).map((s, k) => `<div class="stk ${o.red && k === (o.redLine ?? 0) ? 'red' : ''}" style="display:block;width:max-content;margin:${k ? 10 : 0}px auto 0">${esc(s)}</div>`).join(''); },
    stamp: (o, e) => { e.innerHTML = `<div class="stamp">${esc(o.text)}</div>`; },
    shot: (o, e, t) => { e.className += ' shot hs'; e.style.width = (o.w || 900) + 'px';
      e.innerHTML = `<div class="bar"><i></i><i></i><i></i><span>${esc(o.label || '')}</span></div><div style="position:relative"><img src="${o.src}">${(o.rings || []).map(r => `<div class="ring" style="left:${r[0]}%;top:${r[1]}%;width:${r[2]}%;height:${r[3]}%"></div>`).join('')}</div>`;
      e.querySelectorAll('.ring').forEach((r, k) => tl.fromTo(r, { scale: 1.6, opacity: 0 }, { scale: 1, opacity: 1, duration: .3, ease: 'back.out(2)', immediateRender: false }, (o.ringAt?.[k] ?? t + .5))); },
    phone: (o, e) => { e.className += ' phone hs'; e.innerHTML = `<div class="scr">${o.src ? `<img src="${o.src}">` : `<div class="pt">${o.title || ''}</div>`}</div>`; if (o.scale) e.style.scale = o.scale; },
    term: (o, e, t) => { e.className += ' term hs'; e.innerHTML = `<div class="tb"><i></i><i></i><i></i><span>${esc(o.title || 'terminal')}</span></div><div class="tx"></div>`;
      const tx = e.querySelector('.tx'), full = (o.lines || []).join('\n'), v = { n: 0 };
      const up = () => { const s = full.slice(0, Math.round(v.n)); tx.innerHTML = esc(s).replace(/\$ /g, '<em>$ </em>') + '<span class="cur"></span>'; }; up();
      tl.to(v, { n: full.length, duration: o.type ?? Math.min(2.2, full.length * .03), ease: 'none', onUpdate: up }, t + .25); },
    logo: (o, e) => { e.className += ' logo'; e.innerHTML = `<div class="mk hs">${o.svg || ''}</div><b>${esc(o.name || '')}</b>`; },
    list: (o, e) => { e.className += ' list card hs'; e.innerHTML = (o.title ? `<div class="lbl">${esc(o.title)}</div>` : '') + (o.items || []).map(s => `<div class="li"><div class="bx"></div><span>${esc(s)}</span></div>`).join('');
      e.querySelectorAll('.li').forEach((li, k) => { const at = o.ticks?.[k]; li.querySelector('.bx').innerHTML = '<span>✓</span>'; tl.set(li, { attr: { 'data-on': 0 } }, 0); if (at == null) return; tl.set(li, { attr: { 'data-on': 1 } }, at);
        tl.fromTo(li.querySelector('.bx'), { scale: 1.5 }, { scale: 1, duration: .25, ease: 'back.out(3)', immediateRender: false }, at); }); },
    grid: (o, e, t) => { e.className += ' grid'; e.style.gridTemplateColumns = `repeat(${o.cols || 6}, 92px)`; for (let k = 0; k < (o.n || 24); k++) $('div', 'p', e);
      const ps = e.querySelectorAll('.p'); tl.fromTo(ps, { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: .25, stagger: .015, ease: 'back.out(2)', immediateRender: false }, t);
      (o.hi || []).forEach((k, j) => { tl.set(ps[k], { attr: { 'data-on': 0 } }, 0); tl.set(ps[k], { attr: { 'data-on': 1 } }, o.hiAt?.[j] ?? t + .6); }); },
    compare: (o, e, t) => { e.className += ' cmp'; e.innerHTML = [['bad', '✕', o.left], ['good', '✓', o.right]].map(([c, m, s]) => `<div class="card hs ${c}"><div class="mark">${m}</div><h3>${s?.title || ''}</h3><p>${s?.text || ''}</p></div>`).join('');
      const cs = e.querySelectorAll('.card'); tl.fromTo(cs[1], { scale: .6, opacity: 0 }, { scale: 1, opacity: 1, duration: .35, ease: 'back.out(2)', immediateRender: false }, o.rightAt ?? t + .6); },
    comment: (o, e) => { e.className += ' cmt card hs'; e.innerHTML = `<div class="who"><i></i><span>${esc(o.who || 'Your comment')}</span></div><div class="kw">${esc(o.keyword || 'SKILL')}</div>`; },
    date: (o, e) => { e.className += ' date hs'; e.innerHTML = `<div class="m">${esc(o.month)}</div><div class="d">${esc(o.day)}</div>`; },
    image: (o, e) => { e.innerHTML = `<img src="${o.src}" style="width:${o.w || 800}px;display:block;border-radius:${o.radius ?? 20}px">`; if (o.shadow !== false) e.firstChild.className = 'hs'; },
    html: (o, e) => { e.innerHTML = o.html; },
  };
  R.items.forEach(o => {
    const e = $('div', 'h', heroes); const t = o.at, u = o.until;
    (B[o.type] || B.card)(o, e, t);
    e.style.left = (o.x ?? 540) + 'px'; e.style.top = (o.y ?? 820) + 'px'; e.style.zIndex = o.z ?? 1;
    gsap.set(e, { xPercent: -50, yPercent: -50, rotation: o.rot || 0 });
    vis(e, t, u);
    const pop = o.type === 'stamp' ? { scale: 2.6, opacity: 0, rotation: (o.rot || 0) - 14 } : { scale: .55, opacity: 0, y: 40, rotation: (o.rot || 0) + (o.type === 'sticker' ? -10 : -4) };
    tl.fromTo(e, pop, { scale: 1, opacity: 1, y: 0, rotation: o.rot || 0, duration: o.type === 'stamp' ? .2 : .42, ease: o.type === 'stamp' ? 'power4.out' : 'back.out(1.8)', immediateRender: false }, t);
    if (o.float !== false && u - t > 1.2) tl.to(e, { y: -10, duration: (u - t) / 2, ease: 'sine.inOut', yoyo: true, repeat: 1 }, t + .45);
    if (o.exit !== 'cut' && u < R.dur) tl.to(e, { scale: .85, opacity: 0, duration: .12, ease: 'power2.in' }, u - .12);
  });

  // ---- presenter: a little bounce on every new beat
  R.beats.forEach((b, k) => { if (k) tl.fromTo('#presin', { scale: .975 }, { scale: 1, duration: .28, ease: 'back.out(3)', immediateRender: false }, b.t0); });

  window.__timelines = window.__timelines || {}; window.__timelines['reel'] = tl;
})();
