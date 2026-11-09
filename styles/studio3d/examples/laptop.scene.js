// An original 3D laptop (look: "dark") whose screen is a live canvas: a photo library full of copies, a downloads list,
// an empty folder, a big-files list and a GitHub page. Things fly out of the screen in 3D: a warning stamp, three copies
// of one photo, an empty folder, and the copies the app clears. All times are absolute reel seconds (D.T).
import { RoundedBoxGeometry } from "./RoundedBoxGeometry.js";
export default function (S) {
  const { THREE } = S; const D = window.__LAP; const T = D.T; const tl = S.tl;
  const ALU = S.paint("#a7abb1", { rough: .32, metal: .85, coat: .3 }), KEY = S.mat("#1c1d20", { rough: .6 }), PAD = S.paint("#9a9ea4", { rough: .25, metal: .8, coat: .4 }),
    BLACK = S.mat("#060607", { rough: .3 });
  const m = (g, mat, p, parent, r = [0, 0, 0]) => { const o = new THREE.Mesh(g, mat); o.position.set(...p); o.rotation.set(...r); o.castShadow = o.receiveShadow = true; parent.add(o); return o; };
  // ---------- the laptop
  const lap = S.group([0, 0, 0]);
  m(new RoundedBoxGeometry(1.62, .05, 1.1, 4, .022), ALU, [0, .025, 0], lap);
  for (let r = 0; r < 5; r++) for (let k = 0; k < 13; k++) m(new THREE.BoxGeometry(.088, .01, .072), KEY, [-.6 + k * .1, .053, -.44 + r * .085], lap);
  m(new THREE.BoxGeometry(1.26, .01, .072), KEY, [0, .053, -.44 + 5 * .085], lap);   // space-bar row
  m(new RoundedBoxGeometry(.56, .006, .3, 2, .002), PAD, [0, .051, .34], lap);
  const lid = S.group([0, .05, -.54], lap); lid.rotation.x = -.24;
  m(new RoundedBoxGeometry(1.62, 1.04, .032, 4, .02), ALU, [0, .52, -.016], lid);
  m(new THREE.PlaneGeometry(1.58, 1.0), BLACK, [0, .52, .0005], lid);
  const SW = 1.5, SH = .9375, CW = 1600, CH = 1000;
  const scr = S.group([0, .53, .002], lid);   // screen space: x right, y up, z out of the screen
  const cv = document.createElement("canvas"); cv.width = CW; cv.height = CH; const g = cv.getContext("2d");
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(SW, SH), new THREE.MeshBasicMaterial({ map: tex, toneMapped: false })); scr.add(screen);
  const glow = new THREE.PointLight("#9fb8ff", .6, 2.2); glow.position.set(0, 0, .5); scr.add(glow);
  const L = (px, py) => [(px / CW - .5) * SW, (.5 - py / CH) * SH];   // canvas px -> screen space
  // ---------- images
  const img = (src) => { const i = new Image(); i.src = src; return i; };
  const PH = Object.fromEntries(Object.entries(D.photos).map(([k, v]) => [k, img(v)])); const IC = Object.fromEntries(Object.entries(D.icons).map(([k, v]) => [k, img(v)]));
  const GH = img(D.gh);
  window.__lapReady = Promise.all([...Object.values(PH), ...Object.values(IC), GH].map((i) => i.decode())).then(() => document.fonts.load("700 40px Inter")).then(() => document.fonts.load("500 30px 'IBM Plex Mono'"));
  // ---------- canvas helpers
  const RED = "#e5372d", ORANGE = "#ff8a3d", GREEN = "#3ddc84";
  const rr = (x, y, w, h, r) => { g.beginPath(); g.roundRect(x, y, w, h, r); };
  const txt = (s, x, y, size, color, w = 700, al = "left", mono = false) => { g.font = `${w} ${size}px ${mono ? "'IBM Plex Mono'" : "Inter"}`; g.fillStyle = color; g.textAlign = al; g.textBaseline = "middle"; g.fillText(s, x, y); };
  const cover = (im, x, y, w, h) => { const s = Math.max(w / im.width, h / im.height); const sw = w / s, sh = h / s; g.drawImage(im, (im.width - sw) / 2, (im.height - sh) / 2, sw, sh, x, y, w, h); };
  const bar = (title, right) => { g.fillStyle = "#1f1f23"; g.fillRect(0, 0, CW, 74); ["#ff5f57", "#febc2e", "#28c840"].forEach((c, i) => { g.fillStyle = c; g.beginPath(); g.arc(40 + i * 34, 37, 11, 0, 7); g.fill(); });
    txt(title, 160, 38, 30, "#d8d8de", 600); if (right) txt(right, CW - 36, 38, 26, "#8e8e96", 500, "right", true); };
  const ease = (x) => x <= 0 ? 0 : x >= 1 ? 1 : 1 - Math.pow(1 - x, 3);
  // ---------- the photo library
  const LAY = D.lay, cols = 6, gx = 30, gy = 236, gap = 16, tw = (CW - 2 * gx - (cols - 1) * gap) / cols, th = (CH - gy - 24 - 2 * gap) / 3;
  const tilePos = (i) => [gx + (i % cols) * (tw + gap), gy + Math.floor(i / cols) * (th + gap)];
  const groups = {}; LAY.forEach((k, i) => (groups[k] = groups[k] || []).push(i));
  const order = Object.values(groups); const keep = new Set(order.map((gr) => gr[0]));
  const litAt = (i, t0) => { const gi = order.findIndex((gr) => gr.includes(i)); return t0 + gi * .07 + order[gi].indexOf(i) * .04; };
  function library(t, o) {
    g.fillStyle = "#111113"; g.fillRect(0, 0, CW, CH); bar(o.title, o.count);
    const pct = o.pct(t), hot = pct > 80; txt(o.label(t), 36, 128, 30, "#c9c9cf", 600); txt(Math.round(pct) + "%", CW - 36, 126, 54, hot ? RED : GREEN, 700, "right");
    rr(36, 172, CW - 72, 26, 13); g.fillStyle = "#2b2b2f"; g.fill();
    const blink = o.warn && hot && (t % .5) < .25; g.globalAlpha = blink ? .45 : 1; rr(36, 172, (CW - 72) * pct / 100, 26, 13); g.fillStyle = hot ? RED : GREEN; g.fill(); g.globalAlpha = 1;
    LAY.forEach((k, i) => { const [x, y] = tilePos(i); const gone = o.clear != null && !keep.has(i) && t >= o.clear + i * .025;
      if (gone) { g.setLineDash([12, 10]); g.strokeStyle = "#3a3a40"; g.lineWidth = 3; rr(x + 3, y + 3, tw - 6, th - 6, 16); g.stroke(); g.setLineDash([]); return; }
      g.save(); rr(x, y, tw, th, 16); g.clip(); cover(PH[k], x, y, tw, th); g.restore();
      if (o.lit != null && t >= litAt(i, o.lit)) { const first = keep.has(i); g.lineWidth = 9; g.strokeStyle = first ? ORANGE : RED; rr(x + 4, y + 4, tw - 8, th - 8, 14); g.stroke();
        if (!first) { rr(x + tw - 112, y + th - 52, 98, 40, 9); g.fillStyle = RED; g.fill(); txt("COPY", x + tw - 63, y + th - 31, 24, "#fff", 700, "center", true); } } });
    if (o.scan != null && t > o.scan && t < o.scan + .9) { const y = gy + (CH - gy - 24) * ease((t - o.scan) / .9); g.shadowColor = RED; g.shadowBlur = 40; g.fillStyle = RED; g.fillRect(gx, y, CW - 2 * gx, 8); g.shadowBlur = 0; }
  }
  function list(t, o) {
    g.fillStyle = "#111113"; g.fillRect(0, 0, CW, CH); bar(o.title, o.count);
    o.rows.forEach(([ic, nm, sz, b, hot], i) => { const t0 = o.at + i * o.per; if (t < t0) return; const p = ease((t - t0) / .25); const y = 128 + i * 122, x = 40 - (1 - p) * 120;
      g.globalAlpha = p; g.drawImage(IC[ic], x, y - 34, 68, 68); txt(nm, x + 100, o.bars ? y - 14 : y, 44, "#ececf0", 600);
      if (o.bars) { rr(x + 100, y + 22, 1080, 16, 8); g.fillStyle = "#2b2b2f"; g.fill(); rr(x + 100, y + 22, 1080 * b * ease((t - t0 - .05) / .5), 16, 8); g.fillStyle = hot ? RED : "#8a8a92"; g.fill(); }
      txt(sz, CW - 40, y, 38, hot ? RED : "#9a9aa2", 500, "right", true); g.fillStyle = "#26262a"; g.fillRect(40, y + 60, CW - 80, 2); g.globalAlpha = 1; });
  }
  function empty(t) { g.fillStyle = "#111113"; g.fillRect(0, 0, CW, CH); bar("New Folder (3)", "0 items"); }
  function github(t) { g.fillStyle = "#0d1117"; g.fillRect(0, 0, CW, CH); g.fillStyle = "#1f1f23"; g.fillRect(0, 0, CW, 86);
    ["#ff5f57", "#febc2e", "#28c840"].forEach((c, i) => { g.fillStyle = c; g.beginPath(); g.arc(40 + i * 34, 43, 11, 0, 7); g.fill(); });
    rr(200, 18, 1200, 50, 25); g.fillStyle = "#2c2c31"; g.fill(); txt("github.com/qarmin/czkawka", 800, 44, 28, "#d8d8de", 500, "center", true);
    const w = CW, h = GH.height * CW / GH.width; const off = (h - (CH - 86)) * ease((t - T.gh0 - .6) / 2.6); g.drawImage(GH, 0, 86 - Math.max(0, off), w, h); }
  // ---------- what the screen shows when
  const LIB = { title: "Photos", count: "12,408 items", warn: true, pct: () => 98, label: () => "STORAGE", lit: T.copies };
  const CLR = { title: "Czkawka · scanning", count: "12,408 items", lit: 0, scan: T.scan, clear: T.clear, label: (t) => t < T.clear + .1 ? "STORAGE" : "FREED UP",
    pct: (t) => 98 - 57 * ease((t - T.clear - .1) / .9) };
  const DUP = { title: "Czkawka · Duplicates", count: "same file, same hash", pct: () => 86, label: () => "DUPLICATES FOUND", lit: T.dupLit };
  const DL = { title: "Downloads", count: "2019 – 2024", at: T.dl + .05, per: .1, rows: D.dl };
  const BIG = { title: "Czkawka · Big files", count: "biggest first", at: T.big, per: .08, rows: D.big, bars: true };
  S.onFrame((t) => {
    if (t < T.dl) library(t, LIB); else if (t < T.empty) list(t, DL); else if (t < T.name0) empty(t); else if (t < T.feat0) library(t, CLR);
    else if (t < T.big0) library(t, DUP); else if (t < T.gh0) list(t, BIG); else github(t);
    tex.needsUpdate = true;
  });
  // ---------- 3D things that leave the screen
  const plane = (w, h, draw, cw = 600) => { const c = document.createElement("canvas"); c.width = cw; c.height = Math.round(cw * h / w); const x = c.getContext("2d"); const tx = new THREE.CanvasTexture(c); tx.colorSpace = THREE.SRGBColorSpace;
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tx, transparent: true, toneMapped: false, side: THREE.DoubleSide })); mesh.userData.paint = () => { draw(x, c.width, c.height); tx.needsUpdate = true; }; return mesh; };
  const show = (o, a, b) => { o.visible = false; tl.set(o, { visible: true }, a); tl.set(o, { visible: false }, b); };
  const stamp = (text, color, w, h) => plane(w, h, (x, cw, ch) => { x.clearRect(0, 0, cw, ch); x.lineWidth = 16; x.strokeStyle = color; x.fillStyle = "rgba(11,11,11,.88)"; x.beginPath(); x.roundRect(10, 10, cw - 20, ch - 20, 26); x.fill(); x.stroke();
    x.font = `900 ${Math.round(ch * .5)}px Inter`; x.fillStyle = color; x.textAlign = "center"; x.textBaseline = "middle"; x.fillText(text, cw / 2, ch / 2 + 4); }, 900);
  const paints = [];
  // the warning stamp
  const warn = stamp("STORAGE FULL", RED, .95, .2); scr.add(warn); paints.push(warn); show(warn, T.full, T.copies);
  tl.fromTo(warn.position, { z: .01 }, { z: .42, duration: .3, ease: "back.out(2)", immediateRender: false }, T.full); tl.fromTo(warn.scale, { x: .3, y: .3 }, { x: 1, y: 1, duration: .3, ease: "back.out(2)", immediateRender: false }, T.full);
  tl.fromTo(warn.rotation, { z: -.4 }, { z: -.1, duration: .3, ease: "power3.out", immediateRender: false }, T.full);
  // three copies of one photo fly out of the first tile and fan in front of the screen
  const [t0x, t0y] = L(tilePos(0)[0] + tw / 2, tilePos(0)[1] + th / 2);
  D.copies.forEach((nm, i) => { const card = plane(.42, .56, (x, cw, ch) => { x.fillStyle = "#f2f1ee"; x.beginPath(); x.roundRect(0, 0, cw, ch, 24); x.fill();
      x.save(); x.beginPath(); x.roundRect(22, 22, cw - 44, ch - 130, 12); x.clip(); const im = PH.sunset; const s = Math.max((cw - 44) / im.width, (ch - 130) / im.height);
      x.drawImage(im, (im.width - (cw - 44) / s) / 2, (im.height - (ch - 130) / s) / 2, (cw - 44) / s, (ch - 130) / s, 22, 22, cw - 44, ch - 130); x.restore();
      x.font = "500 30px 'IBM Plex Mono'"; x.fillStyle = "#1a1a1a"; x.textAlign = "center"; x.textBaseline = "middle"; x.fillText(nm, cw / 2, ch - 55); });
    scr.add(card); paints.push(card); const a = T.cards[i]; show(card, a, T.dl + .02); card.position.set(t0x, t0y, .01);
    const off = i - 1; const to = { x: off * .4, y: -.02 + Math.abs(off) * -.03, z: .62 - Math.abs(off) * .06 };
    tl.fromTo(card.position, { x: t0x, y: t0y, z: .01 }, { ...to, duration: .5, ease: "back.out(1.4)", immediateRender: false }, a);
    tl.fromTo(card.scale, { x: .4, y: .4 }, { x: 1, y: 1, duration: .5, ease: "back.out(1.4)", immediateRender: false }, a);
    tl.fromTo(card.rotation, { y: 0, z: 0 }, { y: -off * .32, z: -off * .1, duration: .5, ease: "power3.out", immediateRender: false }, a);
    tl.to(card.position, { y: to.y + .04, duration: .9, ease: "sine.inOut" }, a + .5);
    tl.to(card.position, { x: t0x, y: t0y, z: .01, duration: .3, ease: "power3.in" }, T.dl - .32); tl.to(card.scale, { x: .2, y: .2, duration: .3, ease: "power3.in" }, T.dl - .32); });
  const x3 = plane(.3, .19, (x, cw, ch) => { x.fillStyle = RED; x.beginPath(); x.roundRect(0, 0, cw, ch, 36); x.fill(); x.font = `900 ${Math.round(ch * .7)}px Inter`; x.fillStyle = "#fff"; x.textAlign = "center"; x.textBaseline = "middle"; x.fillText("×3", cw / 2, ch / 2 + 6); });
  scr.add(x3); paints.push(x3); show(x3, T.x3, T.dl - .1); x3.position.set(.42, .36, .8);
  tl.fromTo(x3.scale, { x: 2.4, y: 2.4 }, { x: 1, y: 1, duration: .22, ease: "power4.out", immediateRender: false }, T.x3); tl.fromTo(x3.rotation, { z: .5 }, { z: .12, duration: .22, immediateRender: false }, T.x3);
  // an empty folder pops out of the screen
  const FO = S.paint("#f5a524", { rough: .35, coat: .5 }), FO2 = S.paint("#ffc457", { rough: .35, coat: .5 });
  const fold = S.group([0, -.02, .01], scr); m(new RoundedBoxGeometry(.56, .4, .02, 3, .01), FO, [0, 0, 0], fold); m(new RoundedBoxGeometry(.2, .07, .02, 3, .01), FO, [-.17, .22, 0], fold);
  const flap = S.group([0, -.2, .02], fold); m(new RoundedBoxGeometry(.58, .32, .02, 3, .01), FO2, [0, .16, 0], flap); flap.rotation.x = .55;
  const note = plane(.5, .1, (x, cw, ch) => { x.clearRect(0, 0, cw, ch); x.font = `500 ${Math.round(ch * .5)}px 'IBM Plex Mono'`; x.fillStyle = ORANGE; x.textAlign = "center"; x.textBaseline = "middle"; x.fillText("0 ITEMS · 0 BYTES", cw / 2, ch / 2); });
  note.position.set(0, -.33, .0); fold.add(note); paints.push(note);
  show(fold, T.empty, T.name0 + .02);
  tl.fromTo(fold.position, { z: .01 }, { z: .55, duration: .45, ease: "back.out(1.8)", immediateRender: false }, T.empty);
  tl.fromTo(fold.scale, { x: .2, y: .2, z: .2 }, { x: 1, y: 1, z: 1, duration: .45, ease: "back.out(1.8)", immediateRender: false }, T.empty);
  tl.fromTo(fold.rotation, { y: -.9 }, { y: .25, duration: 1.0, ease: "power2.out", immediateRender: false }, T.empty);
  tl.to(flap.rotation, { x: .9, duration: .5, yoyo: true, repeat: 1, ease: "sine.inOut" }, T.empty + .4);
  tl.to(fold.position, { z: .01, duration: .25, ease: "power3.in" }, T.name0 - .26); tl.to(fold.scale, { x: .1, y: .1, z: .1, duration: .25, ease: "power3.in" }, T.name0 - .26);
  // the copies the app clears fly out of the screen and fall away
  let sd = 7; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
  LAY.forEach((k, i) => { if (keep.has(i)) return; const [px, py] = tilePos(i); const [x0, y0] = L(px + tw / 2, py + th / 2);
    const tile = plane(tw / CW * SW, th / CH * SH, (x, cw, ch) => { x.save(); x.beginPath(); x.roundRect(0, 0, cw, ch, 20); x.clip(); const im = PH[k]; const s = Math.max(cw / im.width, ch / im.height);
      x.drawImage(im, (im.width - cw / s) / 2, (im.height - ch / s) / 2, cw / s, ch / s, 0, 0, cw, ch); x.restore(); x.lineWidth = 12; x.strokeStyle = RED; x.beginPath(); x.roundRect(6, 6, cw - 12, ch - 12, 16); x.stroke(); }, 300);
    scr.add(tile); paints.push(tile); const a = T.clear + i * .025; show(tile, a, a + .85); tile.position.set(x0, y0, .01);
    tl.fromTo(tile.position, { x: x0, y: y0, z: .01 }, { x: x0 * 1.3 + (rnd() - .5) * .3, y: y0 - .9 - rnd() * .3, z: .7 + rnd() * .5, duration: .85, ease: "power2.in", immediateRender: false }, a);
    tl.fromTo(tile.rotation, { x: 0, y: 0, z: 0 }, { x: (rnd() - .5) * 3, y: (rnd() - .5) * 3, z: (rnd() - .5) * 2, duration: .85, ease: "power1.in", immediateRender: false }, a);
    tl.fromTo(tile.scale, { x: 1, y: 1 }, { x: .5, y: .5, duration: .85, ease: "power2.in", immediateRender: false }, a); });
  window.__lapReady.then(() => paints.forEach((p) => p.userData.paint()));
  // ---------- the camera
  const k = (at, pos, look, ease) => { look = look || [0, .48, -.35]; const p2 = pos.map((v, i) => look[i] + (v - look[i]) * 1.2); return { at, pos: [p2[0], p2[1] + .14, p2[2]], look: [look[0], look[1] + .14, look[2]], ease }; };
  S.cameraPath([k(0, [.0, .95, 3.55]), k(T.copies, [.22, .9, 3.2], null, "sine.inOut"), k(T.cards[2] + .3, [-.28, .82, 3.0], [0, .5, -.1], "power2.inOut"),
    k(T.dl - .1, [-.28, .84, 3.05], [0, .5, -.1], "none"), k(T.empty, [.32, 1.0, 3.0], null, "power2.inOut"), k(T.name0 - .05, [0, .92, 3.15], [0, .48, -.2], "power2.inOut"),
    k(T.clear, [.3, 1.05, 3.25], null, "power2.inOut"), k(T.feat0 - 1, [-.2, 1.25, 3.7], null, "power2.out"),
    k(T.feat0, [-1.05, 1.0, 2.95]), k(T.big0 - 1, [-.6, .92, 2.75], null, "sine.inOut"),
    k(T.big0, [.85, 1.3, 2.8]), k(T.gh0 - 1, [.55, 1.2, 2.6], null, "sine.inOut"),
    k(T.gh0, [0, .8, 3.7], [0, .5, -.35]), k(T.gh0 + 3.6, [.25, .78, 3.0], [0, .52, -.35], "power2.inOut")]);
  // cuts between the separate shots (features, big files, GitHub): hold each key until the next shot starts
  tl.set({}, {}, T.gh0 + 3.6);
}
