// beatreel avatar: an original flat-vector presenter ("Kai"), drawn in code, animated on the reel timeline.
// Style matches the references (flat colour, thin dark outline, dotted halftone shadow, chest-up, gestures every
// beat, mouth moving on every word, blinks), but it is its own character: wavy side-swept hair, rectangular
// glasses, light stubble, navy overshirt over a white tee, orange headphones round the neck.
// All motion is state on plain objects tweened by the timeline + one redraw in the timeline's onUpdate,
// so any frame can be rendered in any order.
(function () {
  const R = window.REEL, A = R.avatar; if (!A) return;
  const tl = window.__timelines.reel, NS = 'http://www.w3.org/2000/svg';
  const C = Object.assign({ skin: '#e9b48e', skinHi: '#f6cfae', skinLo: '#cf9470', line: '#3a271d', hair: '#2a1c16', hairHi: '#4a3328',
    shirt: '#2d3a55', shirtLo: '#222c42', tee: '#f6f2ea', phones: '#ff7a3d', phonesLo: '#d95c22', iris: '#4b2e1d', lens: 'rgba(255,255,255,.10)',
    mouth: '#6b2320', tongue: '#e0706a', glasses: '#1c1c1c' }, A.colors || {});
  const W = 1080, H = 900;
  const pres = document.getElementById('pres'), pin = document.getElementById('presin');
  const SC = A.scale ?? 1.15;   // the whole presenter: head centre lands at about y 1340 on the frame
  pres.style.cssText = `left:${540 - W * SC / 2}px;top:${A.top ?? 954}px;width:${W * SC}px;height:${H * SC}px`;
  const svg = document.createElementNS(NS, 'svg'); svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.setAttribute('width', W * SC); svg.setAttribute('height', H * SC);
  svg.style.overflow = 'visible'; pin.appendChild(svg);
  const el = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); (parent || svg).appendChild(e); return e; };
  const g = (parent, attrs) => el('g', attrs || {}, parent);
  const OL = { stroke: C.line, 'stroke-width': 3.5, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' };

  // ---------- defs: halftone dots + soft gradients
  const defs = el('defs', {});
  defs.innerHTML = `
   <pattern id="avdots" width="7" height="7" patternUnits="userSpaceOnUse"><circle cx="3.5" cy="3.5" r="1.7" fill="rgba(0,0,0,.30)"/></pattern>
   <radialGradient id="avskin" cx=".42" cy=".38" r=".75"><stop offset="0" stop-color="${C.skinHi}"/><stop offset=".65" stop-color="${C.skin}"/><stop offset="1" stop-color="${C.skinLo}"/></radialGradient>
   <linearGradient id="avshirt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${C.shirt}"/><stop offset="1" stop-color="${C.shirtLo}"/></linearGradient>
   <linearGradient id="avhair" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${C.hairHi}"/><stop offset=".5" stop-color="${C.hair}"/></linearGradient>
   <clipPath id="avmouthclip"><path id="avmclip" d=""/></clipPath>`;

  // ---------- shapes (head centre 540, 318)
  const HEAD = 'M540 178 C612 178 655 228 657 300 C659 380 628 448 586 474 C566 486 552 490 540 490 C528 490 514 486 494 474 C452 448 421 380 423 300 C425 228 468 178 540 178 Z';
  const BODY = 'M118 900 C122 760 168 668 262 628 C318 604 382 590 452 578 L628 578 C698 590 762 604 818 628 C912 668 958 760 962 900 Z';
  const NECK = 'M494 430 L494 548 C510 566 570 566 586 548 L586 430 Z';
  const HAIR = 'M418 322 C404 262 420 200 462 172 C470 148 500 136 526 146 C542 126 576 126 592 144 C618 134 648 152 654 180 C678 200 682 250 666 300 C662 318 660 326 656 334 C650 300 638 276 620 262 C592 274 556 270 530 254 C506 270 474 276 448 272 C436 288 426 306 418 322 Z';
  const FRINGE = 'M448 272 C470 226 520 198 574 204 C614 208 642 230 656 262 C628 244 592 236 558 242 C530 248 506 258 488 270 C474 278 458 280 448 272 Z';

  // shadow (halftone copy of the silhouette, offset)
  const sh = g(svg, { transform: 'translate(16 18)' });
  el('path', { d: BODY, fill: 'url(#avdots)' }, sh); el('path', { d: HEAD, fill: 'url(#avdots)' }, sh); el('path', { d: HAIR, fill: 'url(#avdots)' }, sh);

  const body = g(svg, {});
  el('path', { d: BODY, fill: 'url(#avshirt)', ...OL }, body);
  // tee + open overshirt placket
  el('path', { d: 'M452 578 L628 578 C640 680 642 800 640 900 L440 900 C438 800 440 680 452 578 Z', fill: C.tee, ...OL }, body);
  el('path', { d: 'M452 578 C470 650 470 760 452 900 L404 900 C410 780 416 670 430 598 Z', fill: C.shirt, ...OL }, body);
  el('path', { d: 'M628 578 C610 650 610 760 628 900 L676 900 C670 780 664 670 650 598 Z', fill: C.shirt, ...OL }, body);
  el('circle', { cx: 448, cy: 700, r: 6, fill: C.line }, body); el('circle', { cx: 452, cy: 790, r: 6, fill: C.line }, body);
  el('path', { d: 'M300 700 L392 700 L392 770 L300 770 Z', fill: 'none', stroke: C.shirtLo, 'stroke-width': 5, 'stroke-linejoin': 'round' }, body);  // pocket
  const neck = el('path', { d: NECK, fill: C.skinLo, ...OL }, body);
  el('path', { d: 'M494 520 C520 540 560 540 586 520 L586 548 C570 566 510 566 494 548 Z', fill: 'rgba(0,0,0,.12)' }, body);
  el('path', { d: 'M470 576 C500 600 580 600 610 576', fill: 'none', ...OL, stroke: C.tee, 'stroke-width': 16 }, body);   // tee collar
  el('path', { d: 'M470 576 C500 600 580 600 610 576', fill: 'none', ...OL }, body);
  // headphones round the neck
  const ph = g(body, {});
  el('path', { d: 'M452 560 C470 640 610 640 628 560', fill: 'none', stroke: C.phonesLo, 'stroke-width': 22, 'stroke-linecap': 'round' }, ph);
  el('path', { d: 'M452 560 C470 640 610 640 628 560', fill: 'none', stroke: C.phones, 'stroke-width': 14, 'stroke-linecap': 'round' }, ph);
  el('rect', { x: 412, y: 540, width: 64, height: 88, rx: 26, fill: C.phones, ...OL, transform: 'rotate(-18 444 584)' }, ph);
  el('rect', { x: 604, y: 540, width: 64, height: 88, rx: 26, fill: C.phones, ...OL, transform: 'rotate(18 636 584)' }, ph);
  el('rect', { x: 424, y: 552, width: 40, height: 64, rx: 16, fill: C.phonesLo, transform: 'rotate(-18 444 584)' }, ph);
  el('rect', { x: 616, y: 552, width: 40, height: 64, rx: 16, fill: C.phonesLo, transform: 'rotate(18 636 584)' }, ph);

  // ---------- head (rotates around the neck)
  const head = g(svg, {});
  el('ellipse', { cx: 424, cy: 330, rx: 24, ry: 38, fill: C.skin, ...OL }, head); el('ellipse', { cx: 656, cy: 330, rx: 24, ry: 38, fill: C.skin, ...OL }, head);
  el('ellipse', { cx: 428, cy: 332, rx: 10, ry: 20, fill: C.skinLo }, head); el('ellipse', { cx: 652, cy: 332, rx: 10, ry: 20, fill: C.skinLo }, head);
  el('path', { d: HEAD, fill: 'url(#avskin)', ...OL }, head);
  el('path', { d: 'M446 408 C470 462 510 484 540 484 C570 484 610 462 634 408 C622 452 588 480 540 482 C492 480 458 452 446 408 Z', fill: 'rgba(58,39,29,.16)' }, head);  // stubble
  el('path', { d: 'M500 410 C520 402 560 402 580 410 C562 406 518 406 500 410 Z', fill: 'rgba(58,39,29,.35)', stroke: 'rgba(58,39,29,.35)', 'stroke-width': 8, 'stroke-linecap': 'round' }, head); // light moustache
  el('ellipse', { cx: 466, cy: 380, rx: 22, ry: 13, fill: 'rgba(255,110,90,.16)' }, head); el('ellipse', { cx: 614, cy: 380, rx: 22, ry: 13, fill: 'rgba(255,110,90,.16)' }, head);
  el('path', { d: 'M540 330 C536 352 528 368 522 376 C532 384 548 384 558 376', fill: 'none', stroke: C.skinLo, 'stroke-width': 6, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, head);  // nose
  // eyes
  const eyes = [], lids = [];
  [[492, 322], [588, 322]].forEach(([x, y]) => { const e = g(head, {});
    el('ellipse', { cx: x, cy: y, rx: 21, ry: 23, fill: '#fff', ...OL, 'stroke-width': 2.5 }, e);
    const ir = g(e, {}); el('circle', { cx: x, cy: y + 2, r: 12.5, fill: C.iris }, ir); el('circle', { cx: x, cy: y + 2, r: 6, fill: '#120c09' }, ir); el('circle', { cx: x - 4, cy: y - 3, r: 3.6, fill: '#fff' }, ir);
    eyes.push(ir); lids.push(el('path', { d: '', fill: C.skin, stroke: C.line, 'stroke-width': 2.5 }, e)); });
  // brows
  const browL = el('path', { d: '', fill: 'none', stroke: C.hair, 'stroke-width': 11, 'stroke-linecap': 'round' }, head);
  const browR = el('path', { d: '', fill: 'none', stroke: C.hair, 'stroke-width': 11, 'stroke-linecap': 'round' }, head);
  // glasses (rectangular)
  const gl = g(head, {});
  el('rect', { x: 452, y: 292, width: 80, height: 60, rx: 14, fill: C.lens, stroke: C.glasses, 'stroke-width': 7 }, gl);
  el('rect', { x: 548, y: 292, width: 80, height: 60, rx: 14, fill: C.lens, stroke: C.glasses, 'stroke-width': 7 }, gl);
  el('path', { d: 'M532 316 C536 310 544 310 548 316', fill: 'none', stroke: C.glasses, 'stroke-width': 7, 'stroke-linecap': 'round' }, gl);
  el('path', { d: 'M452 312 L428 318 M628 312 L652 318', fill: 'none', stroke: C.glasses, 'stroke-width': 7, 'stroke-linecap': 'round' }, gl);
  el('path', { d: 'M462 300 L478 300 M558 300 L574 300', stroke: 'rgba(255,255,255,.55)', 'stroke-width': 5, 'stroke-linecap': 'round' }, gl);
  // mouth: closed smile line + an open mouth that grows
  const mouth = g(head, {});
  const mOpen = el('path', { d: '', fill: C.mouth, ...OL, 'stroke-width': 3 }, mouth);
  const mIn = g(mouth, { 'clip-path': 'url(#avmouthclip)' });
  const teeth = el('rect', { x: 500, y: 418, width: 80, height: 14, fill: '#fff' }, mIn);
  const tongue = el('ellipse', { cx: 540, cy: 470, rx: 26, ry: 14, fill: C.tongue }, mIn);
  const mLine = el('path', { d: '', fill: 'none', stroke: C.line, 'stroke-width': 6, 'stroke-linecap': 'round' }, mouth);
  // hair on top
  el('path', { d: HAIR, fill: 'url(#avhair)', ...OL }, head);
  el('path', { d: FRINGE, fill: C.hair, ...OL }, head);
  el('path', { d: 'M470 196 C496 170 532 164 560 170 M580 160 C606 158 630 170 640 190 M500 226 C528 214 566 212 602 222', fill: 'none', stroke: 'rgba(255,255,255,.17)', 'stroke-width': 7, 'stroke-linecap': 'round' }, head);
  el('path', { d: 'M424 316 C426 336 428 350 432 362 M656 316 C654 336 652 350 648 362', fill: 'none', stroke: C.hair, 'stroke-width': 9, 'stroke-linecap': 'round' }, head);   // sideburns
  // sweat drop (for "nervous"/"stressed")
  const sweat = el('path', { d: 'M418 250 C410 266 408 276 416 282 C424 288 434 280 430 268 C428 262 424 256 418 250 Z', fill: '#cfe8ff', stroke: '#6a9cc8', 'stroke-width': 3, opacity: 0 }, head);

  // ---------- arms + hands (drawn over the body and the face)
  const arms = g(svg, {});
  const mkArm = () => { const a = g(arms, {}); const o = el('path', { d: '', fill: 'none', stroke: C.line, 'stroke-width': 104, 'stroke-linecap': 'round' }, a);
    const f = el('path', { d: '', fill: 'none', stroke: 'url(#avshirt)', 'stroke-width': 96, 'stroke-linecap': 'round' }, a);
    const cuff = el('ellipse', { rx: 44, ry: 18, fill: C.shirtLo, ...OL }, a);
    const hand = g(a, {}); const fingers = [];
    for (let i = 0; i < 5; i++) fingers.push(el('rect', { x: -12, y: 0, width: 24, height: 10, rx: 12, fill: C.skin, ...OL, 'stroke-width': 3 }, hand));
    el('rect', { x: -38, y: -42, width: 76, height: 84, rx: 30, fill: C.skin, ...OL, 'stroke-width': 3 }, hand);
    const thumb = el('rect', { x: -13, y: 0, width: 26, height: 10, rx: 13, fill: C.skin, ...OL, 'stroke-width': 3 }, hand);
    return { o, f, cuff, hand, fingers, thumb }; };
  const ARM = [mkArm(), mkArm()];   // 0 = screen left, 1 = screen right
  const SHOULDER = [[262, 640], [818, 640]];

  // ---------- pose library: hand centre x/y, rotation, finger extension [thumb, index, middle, ring, pinky], thumb angle
  const OPEN = [.8, 1, 1, 1, .9], POINT = [.25, 1, 0, 0, 0], FIST = [.3, 0, 0, 0, 0];
  const HID = (s) => ({ x: s ? 820 : 260, y: 1060, r: 0, f: OPEN, ta: -40 });
  const P = {
    talk: [HID(0), { x: 760, y: 760, r: -18, f: [.6, .9, .9, .85, .8], ta: -40 }],
    calm: [HID(0), HID(1)],
    smile: [HID(0), HID(1)],
    explain: [HID(0), { x: 800, y: 560, r: 14, f: OPEN, ta: -45 }],
    hi: [HID(0), { x: 820, y: 400, r: 16, f: OPEN, ta: -50, wave: 1 }],
    wave: [HID(0), { x: 820, y: 400, r: 16, f: OPEN, ta: -50, wave: 1 }],
    point_up: [HID(0), { x: 790, y: 470, r: -6, f: POINT, ta: -30 }],
    point_side: [{ x: 235, y: 610, r: -92, f: POINT, ta: -30 }, HID(1)],
    count: [HID(0), { x: 800, y: 500, r: -4, f: [0, 1, 1, 0, 0], ta: -10 }],
    count3: [HID(0), { x: 800, y: 500, r: -4, f: [0, 1, 1, 1, 0], ta: -10 }],
    shrug: [{ x: 210, y: 640, r: -62, f: OPEN, ta: -45, flip: 1 }, { x: 870, y: 640, r: 62, f: OPEN, ta: -45 }],
    shocked: [{ x: 400, y: 420, r: 18, f: OPEN, ta: -45, flip: 1 }, { x: 680, y: 420, r: -18, f: OPEN, ta: -45 }],
    excited: [{ x: 230, y: 380, r: -10, f: FIST, ta: -20, flip: 1 }, { x: 850, y: 380, r: 10, f: FIST, ta: -20 }],
    shh: [HID(0), { x: 548, y: 470, r: -10, f: POINT, ta: -20 }],
    thumbs_up: [HID(0), { x: 800, y: 520, r: 0, f: [1, 0, 0, 0, 0], ta: 10 }],
    think: [HID(0), { x: 560, y: 520, r: 8, f: [.2, .35, 0, 0, 0], ta: -30 }],
    wait: [HID(0), { x: 800, y: 520, r: 0, f: [.7, 1, 1, 1, 1], ta: -60 }],
    facepalm: [HID(0), { x: 520, y: 250, r: -20, f: OPEN, ta: -40 }],
    clasp: [{ x: 500, y: 700, r: 30, f: [.4, .5, .5, .5, .5], ta: -20, flip: 1 }, { x: 580, y: 700, r: -30, f: [.4, .5, .5, .5, .5], ta: -20 }],
  };
  const FACE = { talk: { smile: .55 }, calm: { smile: .4 }, smile: { smile: 1 }, explain: { smile: .6, brow: .2 }, hi: { smile: 1, brow: .3 },
    wave: { smile: 1 }, point_up: { smile: .7, brow: .5 }, point_side: { smile: .6, brow: .2, lookX: -6 }, count: { smile: .5 }, count3: { smile: .5 },
    shrug: { smile: .3, brow: .9, tilt: 6 }, shocked: { smile: 0, brow: 1, eyes: 1.25, shock: 1 }, excited: { smile: 1, brow: .6 },
    shh: { smile: .2, brow: .4, lookX: 4 }, thumbs_up: { smile: 1, brow: .3 }, think: { smile: .2, brow: -.4, lookX: 6, lookY: -6, tilt: -5 },
    wait: { smile: .3, brow: .4 }, facepalm: { smile: 0, brow: -.6, lid: .9, tilt: -6 }, clasp: { smile: .6 }, nervous: { smile: .2, brow: .7, sweat: 1 },
    stressed: { smile: 0, brow: .8, sweat: 1 }, sad: { smile: -.6, brow: -.2 }, angry: { smile: -.4, brow: -1 }, laugh: { smile: 1, brow: .4 },
    ok: { smile: .7 }, bored: { smile: 0, lid: .45 }, arms_crossed: { smile: .2 }, cry: { smile: -.8, brow: .6 }, panic: { smile: -.2, brow: 1, eyes: 1.2, sweat: 1 } };
  const ALIAS = { rest: 'calm', up: 'point_up', card: 'point_side', palms: 'explain', thumb: 'thumbs_up', end: 'smile', happy: 'smile', surprised: 'shocked',
    neutral: 'talk', yes: 'thumbs_up', no: 'wait', laugh: 'smile', ok: 'thumbs_up', nervous: 'shrug', stressed: 'shrug', panic: 'shocked', sad: 'calm',
    angry: 'wait', cry: 'calm', bored: 'calm', arms_crossed: 'clasp' };
  const pose = n => P[n] || P[ALIAS[n]] || P.talk;
  const face0 = { smile: .55, brow: 0, eyes: 1, shock: 0, lookX: 0, lookY: 0, tilt: 0, lid: 0, sweat: 0 };

  // ---------- state + redraw
  const S = { a: [Object.assign({}, HID(0)), Object.assign({}, HID(1))], f: Object.assign({ open: 0, blink: 0, nod: 0, wave: 0 }, face0) };
  S.a.forEach(a => { a.f0 = a.f[0]; a.f1 = a.f[1]; a.f2 = a.f[2]; a.f3 = a.f[3]; a.f4 = a.f[4]; a.flip = a.flip || 0; });
  function drawArm(k) { const s = S.a[k], A_ = ARM[k], [sx, sy] = SHOULDER[k], side = k ? 1 : -1;
    const r = (s.r + (k ? s.wave || 0 : 0) * 0 + (k === 1 ? S.f.wave : 0));
    const rad = r * Math.PI / 180, wx = s.x - Math.sin(rad) * -48, wy = s.y + Math.cos(rad) * 48;   // wrist just below the palm
    const out = s.y > 880 ? 18 : 70, mx = (sx + wx) / 2 + side * out, my = Math.max(sy, wy) + (s.y > 880 ? 20 : 70);   // elbow out and down (hugs the body at rest)
    const d = `M${sx} ${sy} Q${mx} ${my} ${wx} ${wy}`; A_.o.setAttribute('d', d); A_.f.setAttribute('d', d);
    A_.cuff.setAttribute('cx', wx); A_.cuff.setAttribute('cy', wy); A_.cuff.setAttribute('transform', `rotate(${r} ${wx} ${wy})`);
    A_.hand.setAttribute('transform', `translate(${s.x} ${s.y}) rotate(${r}) scale(${s.flip > .5 ? -1 : 1} 1)`);
    const ext = [s.f0, s.f1, s.f2, s.f3, s.f4], X = [0, -27, -9, 9, 26], LEN = [0, 62, 68, 62, 50];
    for (let i = 1; i < 5; i++) { const L = 12 + LEN[i] * ext[i]; const fi = A_.fingers[i - 1];
      fi.setAttribute('x', X[i] - 11); fi.setAttribute('y', -36 - L); fi.setAttribute('width', 22); fi.setAttribute('height', L + 14); fi.setAttribute('rx', 11); }
    A_.fingers[4].setAttribute('opacity', 0);
    const TL = 14 + 46 * ext[0]; A_.thumb.setAttribute('x', -13); A_.thumb.setAttribute('y', -TL); A_.thumb.setAttribute('height', TL + 10);
    A_.thumb.setAttribute('transform', `translate(-30 6) rotate(${s.ta ?? -40})`); }
  function drawFace() { const f = S.f;
    head.setAttribute('transform', `rotate(${f.tilt + f.nod * 2} 540 470) translate(0 18) translate(540 470) scale(1.08) translate(-540 -470)`);
    // brows: raise (+) / frown (-)
    const by = 282 - f.brow * 12, bk = f.brow < 0 ? -f.brow * 8 : 0;
    browL.setAttribute('d', `M462 ${by + 6 + bk} Q490 ${by - 8} 518 ${by + 2 - bk}`); browR.setAttribute('d', `M562 ${by + 2 - bk} Q590 ${by - 8} 618 ${by + 6 + bk}`);
    eyes.forEach((e, k) => e.setAttribute('transform', `translate(${f.lookX} ${f.lookY}) scale(${f.eyes}) translate(${(1 - f.eyes) * (k ? 588 : 492) / f.eyes} ${(1 - f.eyes) * 324 / f.eyes})`));
    const lid = Math.max(f.lid, f.blink);
    [[492, 322], [588, 322]].forEach(([x, y], k) => { const top = y - 23, cut = top + 46 * lid;
      lids[k].setAttribute('d', lid < .02 ? '' : `M${x - 22} ${top - 2} L${x + 22} ${top - 2} L${x + 22} ${cut} Q${x} ${cut + 6} ${x - 22} ${cut} Z`); });
    // mouth
    const o = f.shock ? Math.max(.55, f.open) : f.open, sm = f.smile, y0 = 430;
    if (o < .12) { mOpen.setAttribute('d', ''); mLine.setAttribute('d', `M505 ${y0 - sm * 4} Q540 ${y0 + 12 + sm * 14} 575 ${y0 - sm * 4}`); }
    else { mLine.setAttribute('d', '');
      const w = f.shock ? 20 + o * 8 : 30 + sm * 7, h = 6 + o * 32;
      const d = f.shock ? `M${540 - w} ${y0 + h / 2} C${540 - w} ${y0 - 6} ${540 + w} ${y0 - 6} ${540 + w} ${y0 + h / 2} C${540 + w} ${y0 + h + 8} ${540 - w} ${y0 + h + 8} ${540 - w} ${y0 + h / 2} Z`
        : `M${540 - w} ${y0 - sm * 4} Q540 ${y0 - 4} ${540 + w} ${y0 - sm * 4} Q${540 + w * .8} ${y0 + h} 540 ${y0 + h + 4} Q${540 - w * .8} ${y0 + h} ${540 - w} ${y0 - sm * 4} Z`;
      mOpen.setAttribute('d', d); document.getElementById('avmclip').setAttribute('d', d);
      teeth.setAttribute('y', y0 - 8); teeth.setAttribute('x', 540 - w); teeth.setAttribute('width', w * 2); teeth.setAttribute('height', f.shock ? 0 : 12);
      tongue.setAttribute('cy', y0 + h); tongue.setAttribute('rx', w * .6); }
    sweat.setAttribute('opacity', f.sweat); }
  function redraw() { drawArm(0); drawArm(1); drawFace(); }

  // ---------- timeline: poses per beat, mouth per word, blinks, reactions
  const setPose = (name, t, dur) => { const p = pose(name), fc = Object.assign({}, face0, FACE[name] || FACE[ALIAS[name]] || {});
    p.forEach((q, k) => { const s = S.a[k]; const to = { x: q.x, y: q.y, r: q.r, ta: q.ta ?? -40, flip: q.flip || 0, f0: q.f[0], f1: q.f[1], f2: q.f[2], f3: q.f[3], f4: q.f[4] };
      if (t <= 0) { Object.assign(s, to); tl.set(s, to, 0); } else tl.to(s, Object.assign({ duration: dur, ease: 'back.out(1.4)' }, to), t); });
    const fto = { smile: fc.smile, brow: fc.brow, eyes: fc.eyes, shock: fc.shock, lookX: fc.lookX, lookY: fc.lookY, tilt: fc.tilt, lid: fc.lid, sweat: fc.sweat };
    if (t <= 0) { Object.assign(S.f, fto); tl.set(S.f, fto, 0); } else tl.to(S.f, Object.assign({ duration: dur * .8, ease: 'power2.out' }, fto), t);
    if (pose(name)[1].wave) for (let k = 0; k < 6; k++) tl.to(S.f, { wave: k % 2 ? -12 : 12, duration: .16, ease: 'sine.inOut' }, t + .2 + k * .16);
    if (pose(name)[1].wave) tl.to(S.f, { wave: 0, duration: .16 }, t + .2 + 6 * .16); };
  A.poses.forEach((b, k) => setPose(b.pose, k ? b.t0 - .08 : 0, .32));
  // mouth: open on every word, close between; bigger for longer words
  A.words.forEach(w => { const v = Math.min(.85, .35 + w.n * .05); tl.to(S.f, { open: v, duration: .07, ease: 'power1.out' }, w.t);
    tl.to(S.f, { open: .05, duration: .09, ease: 'power1.in' }, w.t + Math.max(.1, Math.min(w.d * .65, .28)));
    if (w.n > 5) tl.to(S.f, { nod: 1, duration: .12, yoyo: true, repeat: 1, ease: 'sine.inOut' }, w.t); });
  // blinks, seeded
  let s = 11, t = .9; const rnd = () => ((s = (s * 16807) % 2147483647) / 2147483647);
  while (t < R.dur - .3) { tl.to(S.f, { blink: 1, duration: .06 }, t); tl.to(S.f, { blink: 0, duration: .09 }, t + .1); t += 2.2 + rnd() * 2.2; }
  (R.reacts || []).forEach(t => tl.to(S.f, { eyes: 1.25, brow: 1, duration: .12, yoyo: true, repeat: 1 }, t));
  redraw(); const prev = tl.eventCallback('onUpdate'); tl.eventCallback('onUpdate', function () { if (prev) prev.apply(this, arguments); redraw(); });
})();
