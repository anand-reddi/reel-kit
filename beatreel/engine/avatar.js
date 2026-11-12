// beatreel avatar: "Kai", an original presenter drawn in code and animated on the reel timeline.
// Drawing manner follows the reference reels: flat fills, NO outlines on the figure (form comes from one darker
// shade per shape), thin lines only on the hands, square-grid halftone shadow, big head on sloped shoulders,
// two-bone arms with a cuff, hands with real fingers. The face is his own: curly dark hair with a fade, no
// glasses, no beard, open zip hoodie over a white tee.
// All motion is state on plain objects tweened by the timeline + one redraw in the timeline's onUpdate,
// so any frame can be rendered in any order.
(function () {
  const R = window.REEL, A = R.avatar; if (!A) return;
  const tl = window.__timelines.reel, NS = 'http://www.w3.org/2000/svg';
  const C = Object.assign({ skin: '#cf9a74', skinSh: '#b57f5b', skinLo: '#a8724f', ear: '#c48d68', line: '#7a4a31',
    hair: '#1f1714', hairHi: '#3b2c25', fade: '#5a4135', brow: '#241a16',
    shirt: '#4d6b5d', shirtSh: '#3c5549', shirtHi: '#5c7c6d', cuff: '#6f8f80', tee: '#f7f4ee', teeSh: '#e2ddd3', cord: '#efe9dc',
    eye: '#ffffff', iris: '#2a1a12', mouth: '#5a1f1c', tongue: '#e2685f', lip: '#9c5a44' }, A.colors || {});
  const W = 1080, H = 900;
  const pres = document.getElementById('pres'), pin = document.getElementById('presin');
  const SC = A.scale ?? 1;
  pres.style.cssText = `left:${540 - W * SC / 2}px;top:${A.top ?? 1060}px;width:${W * SC}px;height:${H * SC}px`;
  const svg = document.createElementNS(NS, 'svg'); svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.setAttribute('width', W * SC); svg.setAttribute('height', H * SC);
  svg.style.overflow = 'visible'; pin.appendChild(svg);
  const el = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); (parent || svg).appendChild(e); return e; };
  const g = (parent, attrs) => el('g', attrs || {}, parent);
  const set = (e, a) => { for (const k in a) e.setAttribute(k, a[k]); };

  const HEAD = 'M432 300 C432 214 472 186 540 186 C608 186 648 214 648 300 L648 372 C648 440 600 478 540 478 C480 478 432 440 432 372 Z';
  const BODY = 'M296 900 C296 770 314 650 350 590 C378 554 440 534 492 522 L588 522 C640 534 702 554 730 590 C766 650 784 770 784 900 Z';
  const HAIR = 'M430 312 C418 250 424 190 462 160 C466 128 504 108 536 122 C560 98 606 104 622 134 C660 144 676 196 660 250 C656 276 652 296 650 312 L640 268 C634 240 618 226 598 232 C578 240 560 222 540 226 C518 232 500 222 480 232 C458 240 446 252 442 272 Z';

  const defs = el('defs', {});
  defs.innerHTML = `
   <pattern id="avdots" width="6" height="6" patternUnits="userSpaceOnUse"><rect x="1.2" y="1.2" width="3.4" height="3.4" rx="1.2" fill="rgba(20,16,14,.42)"/></pattern>
   <clipPath id="avheadclip"><path d="${HEAD}"/></clipPath><clipPath id="avbodyclip"><path d="${BODY}"/></clipPath>
   <clipPath id="avhairclip"><path d="${HAIR}"/></clipPath>
   <clipPath id="aveye0"><ellipse id="aveyec0"/></clipPath><clipPath id="aveye1"><ellipse id="aveyec1"/></clipPath>
   <clipPath id="avmouthclip"><path id="avmclip" d=""/></clipPath>`;

  // ---------- everything sits in one group so the whole figure can lean
  const fig = g(svg, {});
  // halftone shadow: a dotted copy of the silhouette, down and to the right
  const sh = g(fig, { transform: 'translate(15 17)' });
  el('path', { d: BODY, fill: 'url(#avdots)' }, sh);
  const shHead = g(sh, {}); el('path', { d: HEAD, fill: 'url(#avdots)' }, shHead); el('path', { d: HAIR, fill: 'url(#avdots)' }, shHead);
  const shArm = [0, 1].map(() => el('path', { d: '', fill: 'none', stroke: 'url(#avdots)', 'stroke-width': 78, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, sh));
  const shHand = [0, 1].map(() => el('circle', { r: 48, fill: 'url(#avdots)' }, sh));

  // ---------- body: open zip hoodie over a white tee
  const body = g(fig, {});
  el('path', { d: 'M446 560 C428 486 462 450 502 446 L578 446 C618 450 652 486 634 560 C600 528 480 528 446 560 Z', fill: C.shirtSh }, body);   // hood behind the neck
  el('path', { d: BODY, fill: C.shirt }, body);
  const bsh = g(body, { 'clip-path': 'url(#avbodyclip)' });
  el('path', { d: 'M700 540 C760 600 800 760 800 900 L720 900 C730 780 726 640 700 540 Z', fill: C.shirtSh }, bsh);                 // shaded side
  el('path', { d: 'M350 600 C330 680 322 780 322 900 L300 900 L300 600 Z', fill: C.shirtHi, opacity: .6 }, bsh);
  el('path', { d: 'M492 522 L588 522 C600 640 606 780 606 900 L474 900 C474 780 480 640 492 522 Z', fill: C.tee }, body);
  el('path', { d: 'M588 522 C600 640 606 780 606 900 L586 900 C586 780 582 640 572 540 Z', fill: C.teeSh }, body);
  el('path', { d: 'M492 522 C480 640 474 780 474 900', fill: 'none', stroke: C.shirtSh, 'stroke-width': 9 }, body);                 // zip edges
  el('path', { d: 'M588 522 C600 640 606 780 606 900', fill: 'none', stroke: C.shirtSh, 'stroke-width': 9 }, body);
  el('path', { d: 'M452 548 C470 530 488 524 500 528 C494 560 484 590 470 610 C456 596 450 572 452 548 Z', fill: C.shirtHi }, body);  // hood lapels
  el('path', { d: 'M628 548 C610 530 592 524 580 528 C586 560 596 590 610 610 C624 596 630 572 628 548 Z', fill: C.shirtHi }, body);
  el('path', { d: 'M478 600 C476 650 478 690 482 730 M602 600 C604 646 602 680 598 712', fill: 'none', stroke: C.cord, 'stroke-width': 7, 'stroke-linecap': 'round' }, body);  // drawstrings
  el('path', { d: 'M482 724 L483 748 M598 706 L597 730', fill: 'none', stroke: C.shirtSh, 'stroke-width': 9, 'stroke-linecap': 'round' }, body);
  el('path', { d: 'M500 440 L500 520 C516 544 564 544 580 520 L580 440 Z', fill: C.skinSh }, body);                                 // neck
  el('path', { d: 'M500 470 C520 492 560 492 580 470 L580 500 C560 512 520 512 500 500 Z', fill: C.skinLo, opacity: .7 }, body);
  el('path', { d: 'M494 522 C514 548 566 548 586 522', fill: 'none', stroke: C.teeSh, 'stroke-width': 7, 'stroke-linecap': 'round' }, body);

  // ---------- head
  const head = g(fig, {});
  const earL = el('ellipse', { cx: 430, cy: 338, rx: 17, ry: 27, fill: C.ear }, head), earR = el('ellipse', { cx: 650, cy: 338, rx: 17, ry: 27, fill: C.ear }, head);
  el('path', { d: HEAD, fill: C.skin }, head);
  const hsh = g(head, { 'clip-path': 'url(#avheadclip)' });
  el('path', { d: 'M660 180 L660 490 L560 490 C624 452 634 400 630 330 C628 270 624 220 600 180 Z', fill: C.skinSh, opacity: .55 }, hsh);   // shaded side of the face
  el('rect', { x: 428, y: 250, width: 20, height: 76, fill: C.fade, opacity: .75 }, hsh); el('rect', { x: 632, y: 250, width: 20, height: 76, fill: C.fade, opacity: .85 }, hsh);  // fade at the temples
  const feat = g(head, {});
  el('ellipse', { cx: 470, cy: 388, rx: 20, ry: 11, fill: 'rgba(230,110,90,.20)' }, feat); el('ellipse', { cx: 606, cy: 388, rx: 20, ry: 11, fill: 'rgba(230,110,90,.20)' }, feat);
  el('path', { d: 'M544 340 C544 362 554 376 556 384 C552 394 534 394 526 388 C536 388 544 384 544 378 Z', fill: C.skinSh }, feat);   // nose
  const eyes = [[494, 330], [586, 330]].map(([x, y], k) => { const e = g(feat, {});
    const white = el('ellipse', { cx: x, cy: y, fill: C.eye }, e), inner = g(e, { 'clip-path': `url(#aveye${k})` });
    const pupil = el('circle', { r: 10.5, fill: C.iris }, inner), glint = el('circle', { r: 3.2, fill: '#fff' }, inner);
    const lid = el('rect', { fill: C.skinSh }, inner);
    const line = el('path', { d: '', fill: 'none', stroke: C.brow, 'stroke-width': 5.5, 'stroke-linecap': 'round' }, e);
    return { x, y, e, white, pupil, glint, lid, line, clip: document.getElementById('aveyec' + k) }; });
  const brows = [0, 1].map(() => el('path', { d: '', fill: 'none', stroke: C.brow, 'stroke-width': 13, 'stroke-linecap': 'round' }, feat));
  const mouth = g(feat, {});
  const mOpen = el('path', { d: '', fill: C.mouth }, mouth);
  const mIn = g(mouth, { 'clip-path': 'url(#avmouthclip)' });
  const teeth = el('rect', { fill: '#fff', rx: 3 }, mIn), tongue = el('ellipse', { ry: 13, fill: C.tongue }, mIn);
  const mLine = el('path', { d: '', fill: 'none', stroke: C.mouth, 'stroke-width': 6.5, 'stroke-linecap': 'round' }, mouth);
  const mLip = el('path', { d: '', fill: 'none', stroke: C.skinSh, 'stroke-width': 5, 'stroke-linecap': 'round' }, mouth);
  // hair: curly top, drawn over the forehead
  el('path', { d: HAIR, fill: C.hair }, head);
  const hh = g(head, { 'clip-path': 'url(#avhairclip)' });
  el('path', { d: 'M470 176 C482 150 512 140 532 150 M548 140 C572 124 604 134 612 156 M630 170 C648 190 652 220 646 246 M452 214 C462 196 482 190 498 196 M520 190 C540 178 566 180 580 194 M600 200 C614 198 626 208 630 222',
    fill: 'none', stroke: C.hairHi, 'stroke-width': 9, 'stroke-linecap': 'round' }, hh);
  // sweat drops + thought bubble
  const drop = 'M0 -16 C-9 0 -11 10 -4 16 C4 22 14 14 10 2 C8 -4 4 -10 0 -16 Z';
  const sweat = [el('path', { d: drop, fill: '#dff0ff', stroke: '#7fa9cf', 'stroke-width': 2.5, transform: 'translate(424 262)', opacity: 0 }, head),
    el('path', { d: drop, fill: '#dff0ff', stroke: '#7fa9cf', 'stroke-width': 2.5, transform: 'translate(664 300) scale(.8)', opacity: 0 }, head)];
  const qb = g(head, { opacity: 0 });
  el('circle', { cx: 668, cy: 176, r: 9, fill: '#fff' }, qb); el('circle', { cx: 690, cy: 146, r: 14, fill: '#fff' }, qb); el('circle', { cx: 734, cy: 96, r: 44, fill: '#fff' }, qb);
  const qt = el('text', { x: 734, y: 118, 'text-anchor': 'middle', 'font-size': 62, 'font-weight': 800, 'font-family': 'Space Grotesk, sans-serif', fill: '#e8452c' }, qb); qt.textContent = '?';

  // ---------- arms: shoulder → elbow → wrist, cuff, hand
  const arms = g(fig, {});
  const SW = 76, HS = 1.25;
  const mkArm = () => { const a = g(arms, {});
    const lo = el('path', { d: '', fill: 'none', stroke: C.shirtSh, 'stroke-width': SW, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, a);
    const hi = el('path', { d: '', fill: 'none', stroke: C.shirt, 'stroke-width': SW - 12, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, a);
    const hand = g(a, {});
    const fingers = [0, 1, 2, 3].map(() => el('rect', { fill: C.skin, stroke: C.line, 'stroke-width': 2.6 }, hand));
    const thumb = el('rect', { fill: C.skin, stroke: C.line, 'stroke-width': 2.6 }, hand);
    el('rect', { x: -33, y: -30, width: 66, height: 74, rx: 26, fill: C.skin, stroke: C.line, 'stroke-width': 2.6 }, hand);
    el('rect', { x: -28.5, y: -34, width: 57, height: 26, rx: 6, fill: C.skin }, hand);            // fingers run into the palm
    const thumbFill = el('rect', { fill: C.skin }, hand);
    el('path', { d: 'M-14 6 C-6 14 8 14 16 4', fill: 'none', stroke: C.line, 'stroke-width': 2.2, 'stroke-linecap': 'round', opacity: .55 }, hand);
    const cuff = el('path', { d: '', fill: 'none', stroke: C.cuff, 'stroke-width': SW - 2, 'stroke-linecap': 'butt' }, a);
    const cuffL = el('path', { d: '', fill: 'none', stroke: C.shirtSh, 'stroke-width': 3, opacity: .7 }, a);
    return { lo, hi, cuff, cuffL, hand, fingers, thumb, thumbFill }; };
  const ARM = [mkArm(), mkArm()];   // 0 = screen left, 1 = screen right
  const SHO = [[364, 598], [716, 598]], L1 = 165, L2 = 155;

  // ---------- pose library. Per arm: palm centre x/y, r (0 = fingers up), f = [thumb, index, middle, ring, pinky]
  // extension, sp = finger spread, ta = thumb angle, flip, el: -1 = elbow the other way.
  const OPEN = [1, 1, 1, 1, 1], CUP = [.75, .8, .78, .72, .62], POINT = [.3, 1, 0, 0, 0], FIST = [.35, 0, 0, 0, 0], FLAT = [.5, 1, 1, 1, 1];
  const REST = k => ({ x: k ? 772 : 308, y: 990, r: k ? 174 : -174, f: CUP, sp: .3 });
  const UP = k => ({ x: k ? 790 : 290, y: 540, r: k ? 10 : -10, f: CUP, sp: .35 });          // the reference's talking hands
  const LOW = k => ({ x: k ? 742 : 338, y: 800, r: k ? 60 : -60, f: CUP, sp: .5 });
  const P = {
    talk: [UP(0), UP(1)],
    calm: [REST(0), REST(1)],
    smile: [REST(0), REST(1)],
    explain: [{ x: 196, y: 640, r: -62, f: OPEN, sp: 1 }, LOW(1)],
    present: [{ x: 196, y: 640, r: -62, f: OPEN, sp: 1 }, LOW(1)],
    both: [{ x: 196, y: 660, r: -66, f: OPEN, sp: 1 }, { x: 884, y: 660, r: 66, f: OPEN, sp: 1 }],
    hi: [REST(0), { x: 850, y: 350, r: 12, f: OPEN, sp: 1, wv: 1 }],
    wave: [REST(0), { x: 850, y: 350, r: 12, f: OPEN, sp: 1, wv: 1 }],
    point_up: [{ x: 292, y: 420, r: -6, f: POINT, sp: 0 }, REST(1)],
    point_side: [{ x: 132, y: 590, r: -78, f: POINT, sp: 0 }, REST(1)],
    count: [REST(0), { x: 810, y: 440, r: 4, f: [.2, 1, 1, 0, 0], sp: .9 }],
    count3: [REST(0), { x: 810, y: 440, r: 4, f: [.2, 1, 1, 1, 0], sp: .9 }],
    one: [REST(0), { x: 810, y: 440, r: 4, f: POINT, sp: 0 }],
    shrug: [{ x: 170, y: 668, r: -74, f: OPEN, sp: 1 }, { x: 910, y: 668, r: 74, f: OPEN, sp: 1 }],
    shocked: [{ x: 496, y: 424, r: 62, f: FLAT, sp: 0, ta: -20, el: 1 }, { x: 584, y: 430, r: -62, f: FLAT, sp: 0, ta: -20, el: 1 }],
    gasp: [{ x: 224, y: 706, r: -44, f: OPEN, sp: 1 }, { x: 856, y: 706, r: 44, f: OPEN, sp: 1 }],
    oops: [{ x: 408, y: 390, r: 12, f: FLAT, sp: .3 }, { x: 672, y: 390, r: -12, f: FLAT, sp: .3 }],
    excited: [{ x: 236, y: 420, r: -12, f: FIST }, { x: 844, y: 420, r: 12, f: FIST }],
    shh: [REST(0), { x: 556, y: 512, r: -4, f: POINT, sp: 0, ta: -30 }],
    thumbs_up: [REST(0), { x: 810, y: 500, r: 0, f: [1, 0, 0, 0, 0], ta: -8 }],
    think: [REST(0), { x: 580, y: 512, r: -14, f: [.6, .25, 0, 0, 0], ta: -70 }],
    wait: [REST(0), { x: 815, y: 460, r: 0, f: OPEN, sp: .25 }],
    stop: [{ x: 265, y: 460, r: 0, f: OPEN, sp: .25 }, { x: 815, y: 460, r: 0, f: OPEN, sp: .25 }],
    facepalm: [REST(0), { x: 600, y: 300, r: -26, f: FLAT, sp: .35 }],
    clasp: [{ x: 512, y: 740, r: 50, f: [.4, .5, .5, .5, .5] }, { x: 572, y: 744, r: -50, f: [.4, .5, .5, .5, .5] }],
    arms_crossed: [{ x: 640, y: 790, r: 80, f: [.3, .4, .4, .4, .4] }, { x: 440, y: 800, r: -80, f: [.3, .4, .4, .4, .4] }],
  };
  const FACE = {
    talk: { smile: .6 }, calm: { smile: .45 }, smile: { smile: 1, happy: .0, brow: .2 }, explain: { smile: .65, brow: .25, turn: -.5, lookX: -3 },
    present: { smile: .7, brow: .3, turn: -.5, lookX: -3 }, both: { smile: .7, brow: .4 }, hi: { smile: 1, grin: 1, brow: .4 }, wave: { smile: 1, grin: 1, brow: .4 },
    point_up: { smile: .7, brow: .6, lookX: -4, lookY: -5, turn: -.4 }, point_side: { smile: .3, brow: .1, brow2: .6, lookX: -7, lid: .3, turn: -1 },
    count: { smile: .55, brow: .3 }, count3: { smile: .55, brow: .3 }, one: { smile: .55, brow: .4 },
    shrug: { smile: .2, brow: .9, browA: .5, tilt: 5, shrug: 1 }, shocked: { smile: 0, brow: 1, eyes: 1.3, shock: 1 },
    gasp: { smile: 0, brow: 1, eyes: 1.3, shock: 1 }, oops: { smile: -.3, brow: .8, browA: .8, eyes: 1.2, shock: 1, sweat: 1 },
    excited: { smile: 1, grin: 1, brow: .7, happy: 1 }, shh: { smile: .25, brow: .5, lookX: 3 }, thumbs_up: { smile: 1, grin: 1, brow: .3, wink: 1 },
    think: { smile: .1, brow: .1, brow2: .7, lookX: 6, lookY: -7, tilt: -5, q: 1 }, wait: { smile: .15, brow: .5 }, stop: { smile: 0, brow: .6 },
    facepalm: { smile: -.5, brow: -.2, browA: .7, lid: 1, tilt: -6, sweat: 1 }, clasp: { smile: .6 },
    nervous: { smile: .2, brow: .7, browA: .7, sweat: 1 }, stressed: { smile: -.3, brow: .6, browA: .9, sweat: 1 }, sad: { smile: -.7, brow: .2, browA: 1, lid: .3 },
    angry: { smile: -.5, brow: -.4, browA: -1 }, laugh: { smile: 1, grin: 1, happy: 1, brow: .5 }, ok: { smile: .8, wink: 1 },
    bored: { smile: -.1, lid: .5 }, arms_crossed: { smile: .15, brow2: .6, lid: .25 }, skeptical: { smile: .1, brow2: .8, lid: .4, lookX: -6, turn: -.6 },
    cry: { smile: -.9, brow: .5, browA: 1, lid: .6, sweat: 1 }, panic: { smile: -.2, brow: 1, browA: .6, eyes: 1.25, shock: 1, sweat: 1 }, wink: { smile: .9, wink: 1 } };
  const ALIAS = { rest: 'calm', up: 'point_up', card: 'point_side', palms: 'both', thumb: 'thumbs_up', end: 'smile', happy: 'smile', surprised: 'gasp',
    neutral: 'talk', yes: 'thumbs_up', no: 'stop', laugh: 'talk', ok: 'thumbs_up', nervous: 'talk', stressed: 'oops', panic: 'oops', sad: 'calm',
    angry: 'arms_crossed', cry: 'calm', bored: 'calm', skeptical: 'point_side', wink: 'talk', two: 'count', three: 'count3' };
  const pose = n => P[n] || P[ALIAS[n]] || P.talk;
  const face0 = { smile: .55, brow: 0, brow2: 0, browA: 0, eyes: 1, shock: 0, grin: 0, happy: 0, wink: 0, lookX: 0, lookY: 0, tilt: 0, lid: 0, sweat: 0, turn: 0, shrug: 0, q: 0 };
  const arm0 = q => ({ x: q.x, y: q.y, r: q.r, ta: q.ta ?? -58, sp: q.sp ?? .4, flip: q.flip || 0, el: q.el || 0, wv: q.wv || 0, f0: q.f[0], f1: q.f[1], f2: q.f[2], f3: q.f[3], f4: q.f[4] });

  // ---------- state + redraw
  const S = { a: [arm0(REST(0)), arm0(REST(1))], f: Object.assign({ open: 0, blink: 0, nod: 0, wave: 0, bob: 0, sway: 0 }, face0) };
  const FX = [-25.5, -8.5, 8.5, 25.5], FL = [50, 58, 54, 42], FA = [-15, -5, 5, 15];
  function drawArm(k) { const s = S.a[k], a = ARM[k], side = k ? 1 : -1, f = S.f;
    const sx = SHO[k][0], sy = SHO[k][1] - f.shrug * 18;
    const r = s.r + f.wave * s.wv, rad = r * Math.PI / 180, ux = Math.sin(rad), uy = -Math.cos(rad);
    const up = s.y < 880 ? 1 : 0, hx = s.x + f.sway * side * 4 * up, hy = s.y + f.bob * up;
    const wx = hx - ux * 60, wy = hy - uy * 60;
    let dx = wx - sx, dy = wy - sy, d = Math.hypot(dx, dy) || 1; const dd = Math.min(d, L1 + L2 - 2);
    const aa = (L1 * L1 - L2 * L2 + dd * dd) / (2 * dd), h = Math.sqrt(Math.max(L1 * L1 - aa * aa, 0));
    const mx = sx + dx / d * aa, my = sy + dy / d * aa, px = -dy / d, py = dx / d;
    const e1 = [mx + px * h, my + py * h], e2 = [mx - px * h, my - py * h];
    const out = s.el > .5, sc = e => out ? side * e[0] : side * e[0] * .3 + e[1]; const e = sc(e1) > sc(e2) ? e1 : e2;
    const d1 = `M${sx} ${sy} L${e[0]} ${e[1]} L${wx} ${wy}`;
    a.lo.setAttribute('d', d1); a.hi.setAttribute('d', `M${sx - 3} ${sy - 4} L${e[0] - 3} ${e[1] - 4} L${wx - 3} ${wy - 4}`); shArm[k].setAttribute('d', d1);
    let fx = wx - e[0], fy = wy - e[1]; const fl = Math.hypot(fx, fy) || 1; fx /= fl; fy /= fl;
    a.cuff.setAttribute('d', `M${wx - fx * 12} ${wy - fy * 12} L${wx + fx * 14} ${wy + fy * 14}`);
    a.cuffL.setAttribute('d', `M${wx - fx * 12 - fy * 37} ${wy - fy * 12 + fx * 37} L${wx - fx * 12 + fy * 37} ${wy - fy * 12 - fx * 37}`);
    const mir = (k === 0) !== (s.flip > .5);
    a.hand.setAttribute('transform', `translate(${hx} ${hy}) rotate(${r}) scale(${mir ? -HS : HS} ${HS})`);
    set(shHand[k], { cx: hx, cy: hy - 10 });
    const ext = [s.f0, s.f1, s.f2, s.f3, s.f4];
    for (let i = 0; i < 4; i++) { const L = 9 + FL[i] * ext[i + 1];
      set(a.fingers[i], { x: FX[i] - 8.5, y: -26 - L, width: 17, height: L + 14, rx: 8.5, transform: `rotate(${FA[i] * s.sp * ext[i + 1]} ${FX[i]} -22)` }); }
    const TL = 14 + 36 * ext[0], tt = `translate(-27 12) rotate(${s.ta})`;
    set(a.thumb, { x: -10, y: -TL, width: 20, height: TL + 12, rx: 10, transform: tt });
    set(a.thumbFill, { x: -7.5, y: -6, width: 15, height: 18, rx: 6, transform: tt }); }
  function drawFace() { const f = S.f;
    const ht = `rotate(${f.tilt + f.nod * 1.6} 540 500) translate(0 ${f.nod * 5 - f.shrug * 4}) translate(540 500) scale(1.3) translate(-540 -500)`;
    head.setAttribute('transform', ht); shHead.setAttribute('transform', ht);
    feat.setAttribute('transform', `translate(${f.turn * 9} 0)`);
    set(earL, { rx: 17 + f.turn * 4 }); set(earR, { rx: 17 - f.turn * 4 });
    // brows: raise, angle (browA < 0 angry, > 0 worried), brow2 lifts the right one alone
    [0, 1].forEach(k => { const by = 288 - (f.brow + (k ? f.brow2 : 0)) * 14, a = f.browA * 9, s = k ? 1 : -1, cx = k ? 586 : 494;
      brows[k].setAttribute('d', `M${cx + s * 30} ${by + 5 - a} Q${cx + s * 6} ${by - 9} ${cx - s * 26} ${by + a + 1}`); });
    // eyes
    eyes.forEach((E, k) => { const closed = f.happy > .5 || (k === 1 && f.wink > .5), rx = 17.5 * f.eyes, ry = 15.5 * f.eyes, { x, y } = E;
      const lid = Math.max(f.lid, f.blink, f.eyes > 1.1 ? 0 : .14);
      set(E.white, { rx, ry, opacity: closed ? 0 : 1 }); set(E.clip, { cx: x, cy: y, rx, ry });
      set(E.pupil, { cx: x + f.lookX, cy: y + f.lookY + 1, opacity: closed ? 0 : 1 }); set(E.glint, { cx: x + f.lookX - 3.5, cy: y + f.lookY - 3, opacity: closed ? 0 : 1 });
      const cut = y - ry + 2 * ry * lid; set(E.lid, { x: x - rx - 2, y: y - ry - 2, width: rx * 2 + 4, height: Math.max(0, cut - (y - ry) + 2), opacity: closed ? 0 : 1 });
      if (closed) E.line.setAttribute('d', `M${x - 19} ${y + 5} Q${x} ${y - 15} ${x + 19} ${y + 5}`);
      else if (lid < .06) E.line.setAttribute('d', `M${x - rx} ${y - 1} A${rx} ${ry} 0 0 1 ${x + rx} ${y - 1}`);
      else { const q = Math.max(-1, Math.min(1, (cut - y) / ry)), hw = Math.max(rx * Math.sqrt(1 - q * q), rx * .82); E.line.setAttribute('d', `M${x - hw} ${Math.min(cut, y + 6)} Q${x} ${Math.min(cut, y + 6) + (lid > .9 ? 7 : -4 + lid * 6)} ${x + hw} ${Math.min(cut, y + 6)}`); } });
    // mouth
    const sm = f.smile, y0 = 430, o = Math.max(f.open, f.shock ? .6 : 0, f.grin > .5 ? .5 : 0);
    if (o < .12) { mOpen.setAttribute('d', ''); mLine.setAttribute('d', `M${508 - sm * 4} ${y0 - sm * 6} Q540 ${y0 + sm * 18} ${572 + sm * 4} ${y0 - sm * 6}`); mLip.setAttribute('d', `M528 ${y0 + 20 + Math.max(sm, 0) * 4} Q540 ${y0 + 24 + Math.max(sm, 0) * 4} 552 ${y0 + 20 + Math.max(sm, 0) * 4}`); set(teeth, { height: 0 }); set(tongue, { opacity: 0 }); }
    else { mLine.setAttribute('d', '');
      let d;
      if (f.shock > .5) { const w = 19 + o * 6, h = 16 + o * 14; d = `M${540 - w} ${y0 + 4} C${540 - w} ${y0 - h} ${540 + w} ${y0 - h} ${540 + w} ${y0 + 4} C${540 + w} ${y0 + h + 14} ${540 - w} ${y0 + h + 14} ${540 - w} ${y0 + 4} Z`;
        set(teeth, { height: 0 }); set(tongue, { cx: 540, cy: y0 + h + 12, rx: w * .7, opacity: 1 }); mLip.setAttribute('d', ''); }
      else { const sp = Math.max(sm, 0), w = 27 + sp * 9 + f.grin * 7, h = 7 + o * 30, ty = y0 - 9, cy = ty - sp * 5;
        d = `M${540 - w} ${cy} Q540 ${ty + 5} ${540 + w} ${cy} Q${540 + w * .82} ${ty + h + 2} 540 ${ty + h + 5} Q${540 - w * .82} ${ty + h + 2} ${540 - w} ${cy} Z`;
        set(teeth, { x: 540 - w * .72, y: ty - 6, width: w * 1.44, height: 16 + (f.grin > .5 ? 3 : 0) }); set(tongue, { cx: 540, cy: ty + h + 6, rx: w * .55, opacity: 1 });
        mLip.setAttribute('d', `M528 ${ty + h + 15} Q540 ${ty + h + 19} 552 ${ty + h + 15}`); }
      mOpen.setAttribute('d', d); document.getElementById('avmclip').setAttribute('d', d); }
    sweat.forEach(s => s.setAttribute('opacity', f.sweat)); qb.setAttribute('opacity', f.q);
    fig.setAttribute('transform', `rotate(${f.sway * .7} 540 900)`); }
  function redraw() { drawArm(0); drawArm(1); drawFace(); }

  // ---------- timeline: poses per beat, mouth per word, blinks, reactions
  const setPose = (name, t, dur) => { const p = pose(name), fto = Object.assign({}, face0, FACE[name] || FACE[ALIAS[name]] || {});
    p.forEach((q, k) => { const s = S.a[k], to = arm0(q);
      if (t <= 0) { Object.assign(s, to); tl.set(s, to, 0); } else tl.to(s, Object.assign({ duration: dur, ease: 'back.out(1.5)' }, to), t + k * .03); });
    if (t <= 0) { Object.assign(S.f, fto); tl.set(S.f, fto, 0); } else tl.to(S.f, Object.assign({ duration: dur * .7, ease: 'power2.out' }, fto), t);
    if (p.some(q => q.wv)) { for (let k = 0; k < 6; k++) tl.to(S.f, { wave: k % 2 ? -13 : 13, duration: .15, ease: 'sine.inOut' }, t + .2 + k * .15);
      tl.to(S.f, { wave: 0, duration: .15 }, t + .2 + 6 * .15); }
    if (name === 'gasp' || name === 'oops' || name === 'panic') for (let k = 0; k < 6; k++) tl.to(S.f, { bob: k % 2 ? 7 : -7, duration: .06 }, t + .15 + k * .06); };
  A.poses.forEach((b, k) => setPose(b.pose, k ? b.t0 - .08 : 0, .34));
  // mouth on every word (bigger for longer words); the hands and head beat along on the stronger words
  let s = 11; const rnd = () => ((s = (s * 16807) % 2147483647) / 2147483647);
  A.words.forEach((w, i) => { const v = Math.min(.9, .38 + w.n * .055); tl.to(S.f, { open: v, duration: .07, ease: 'power1.out' }, w.t);
    tl.to(S.f, { open: .04, duration: .09, ease: 'power1.in' }, w.t + Math.max(.1, Math.min(w.d * .65, .28)));
    if (w.n > 3) { tl.to(S.f, { bob: -9 - rnd() * 6, duration: .09, ease: 'power2.out' }, w.t); tl.to(S.f, { bob: 0, duration: .2, ease: 'sine.inOut' }, w.t + .1); }
    if (w.n > 5) tl.to(S.f, { nod: 1, duration: .12, yoyo: true, repeat: 1, ease: 'sine.inOut' }, w.t);
    if (i % 5 === 2) tl.to(S.f, { sway: rnd() * 2 - 1, duration: .5, ease: 'sine.inOut' }, w.t); });
  let t = .9; while (t < R.dur - .3) { tl.to(S.f, { blink: 1, duration: .05 }, t); tl.to(S.f, { blink: 0, duration: .08 }, t + .09); t += 2.2 + rnd() * 2.2; }
  (R.reacts || []).forEach(t => tl.to(S.f, { eyes: 1.3, brow: 1, duration: .12, yoyo: true, repeat: 1 }, t));
  window.__avatar = S; redraw(); const prev = tl.eventCallback('onUpdate'); tl.eventCallback('onUpdate', function () { if (prev) prev.apply(this, arguments); redraw(); });
})();
