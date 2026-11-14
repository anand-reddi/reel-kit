// The Outlook outage server hall, in 3D: an original diorama of white server racks with live LED rows on a dark
// platform, rendered on a transparent background so it sits on the reel's grid. Everything is a pure function of the
// reel time t (absolute seconds, window.T3 / R3 from times.py), so any frame renders the same in any order.
//   rise     the fleet rises out of the floor
//   scan     a health-check beam sweeps the rows, ticks pop
//   sick     one rack turns red and is pulled out of its row
//   fail     a red wave: most racks fail their checks at once
//   dump     their traffic flies onto the few still running
//   over     those overload (amber, shaking) and fail too
//   restart  everything restarts: lights come back row by row, then a wave of traffic slams in
//   down     ...and they go down again
//   rec      recovery, one stage at a time, with ticks
import * as THREE from "three";
import { RoundedBoxGeometry } from "./RoundedBoxGeometry.js";
import { RoomEnvironment } from "./RoomEnvironment.js";

const T = window.T3, R = window.R3, W = 1080, H = 1280;
const r = new THREE.WebGLRenderer({ canvas: document.getElementById("gl"), antialias: true, alpha: true, preserveDrawingBuffer: true });
r.setPixelRatio(1); r.setSize(W, H, false); r.setClearColor(0x000000, 0);
r.shadowMap.enabled = true; r.shadowMap.type = THREE.PCFSoftShadowMap;
r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = 1.0; r.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
scene.environment = new THREE.PMREMGenerator(r).fromScene(new RoomEnvironment(), 0.04).texture;
const cam = new THREE.PerspectiveCamera(26, W / H, 0.1, 120);

// ---------- light
scene.add(new THREE.HemisphereLight("#ffffff", "#30323a", 0.9));
const key = new THREE.DirectionalLight("#fff4ea", 2.3); key.position.set(-6, 12, 8); key.castShadow = true;
key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7, near: 1, far: 40 });
key.shadow.radius = 4; key.shadow.bias = -0.0005; scene.add(key);
const rim = new THREE.DirectionalLight("#dfe8ff", 0.9); rim.position.set(7, 5, -7); scene.add(rim);

// ---------- helpers
const clamp = (x) => Math.max(0, Math.min(1, x));
const eio = (x) => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const eout = (x) => 1 - Math.pow(1 - clamp(x), 3);
const back = (x) => { x = clamp(x); const c1 = 1.7, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const hash = (a, b, c) => { const s = Math.sin(a * 127.1 + b * 311.7 + c * 74.7) * 43758.5453; return s - Math.floor(s); };
const tex = (draw, s = 256) => { const c = document.createElement("canvas"); c.width = c.height = s; draw(c.getContext("2d"), s); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; };
const COL = { green: new THREE.Color("#2fe37f"), red: new THREE.Color("#ff3b30"), amber: new THREE.Color("#ffb21e"), off: new THREE.Color("#2a2c31"), white: new THREE.Color("#ffffff") };

// ---------- the platform (a dark raised floor with tiles)
const plat = new THREE.Mesh(new RoundedBoxGeometry(7.6, .24, 8.8, 4, .08), new THREE.MeshStandardMaterial({ color: "#16171b", roughness: .85, metalness: .1 }));
plat.position.y = -.12; plat.receiveShadow = true; scene.add(plat);
const grid = new THREE.GridHelper(7.2, 12, "#2b2d34", "#24262c"); grid.scale.z = 8.4 / 7.2; grid.position.y = .003; scene.add(grid);
const edge = new THREE.Mesh(new THREE.BoxGeometry(7.62, .012, 8.82), new THREE.MeshBasicMaterial({ color: "#3a3d45" })); edge.position.y = .001; scene.add(edge);

// ---------- racks: 4 rows of 9, all facing the camera (+z). Instanced: body, front panel, 6 units, LED strips, LED dots, top strip
const ROWS = 4, COLS = 9, N = ROWS * COLS, RW = .6, RH = 1.45, RD = .9;
const racks = [];
for (let row = 0; row < ROWS; row++) for (let col = 0; col < COLS; col++) racks.push({ row, col, x: (col - 4) * .66, z: (row - 1.5) * 1.95 });
const idx = (row, col) => row * COLS + col;
const SICK = idx(3, 4);
const SURV = [idx(2, 6), idx(2, 7), idx(2, 8), idx(3, 6), idx(3, 8), idx(1, 7)];   // still running after the wave
const isSurv = (i) => SURV.includes(i);
const WAVE0 = new THREE.Vector2(-3.4, -3.6);
racks.forEach((k, i) => { k.d = Math.hypot(k.x - WAVE0.x, k.z - WAVE0.y); k.c = Math.hypot(k.x, k.z); });
const dMax = Math.max(...racks.map((k) => k.d));

const std = (c, o = {}) => new THREE.MeshStandardMaterial({ color: c, roughness: o.r ?? .5, metalness: o.m ?? 0, envMapIntensity: o.env ?? .6 });
const basic = () => new THREE.MeshBasicMaterial({ color: "#ffffff", toneMapped: false });
const inst = (geo, mat, n, shadow = true) => { const m = new THREE.InstancedMesh(geo, mat, n); m.castShadow = shadow; m.receiveShadow = shadow; m.instanceMatrix.setUsage(THREE.DynamicDrawUsage); scene.add(m); return m; };
const UNITS = 6, uy = (j) => .16 + j * .215;
const body = inst(new RoundedBoxGeometry(RW, RH, RD, 3, .035), std("#ebe9e4", { r: .45 }), N);
const panel = inst(new THREE.BoxGeometry(.5, 1.34, .02), std("#101114", { r: .35, m: .2 }), N, false);
const units = inst(new THREE.BoxGeometry(.46, .16, .026), std("#1e2026", { r: .4, m: .3 }), N * UNITS, false);
const strips = inst(new THREE.BoxGeometry(.22, .028, .012), basic(), N * UNITS, false);
const dots = inst(new THREE.BoxGeometry(.034, .034, .012), basic(), N * UNITS * 2, false);
const tops = inst(new THREE.BoxGeometry(.5, .018, .05), basic(), N, false);
[strips, dots, tops].forEach((m) => { for (let i = 0; i < m.count; i++) m.setColorAt(i, COL.green); });

// floor glow under each rack (additive)
const glowTex = tex((g, s) => { const gr = g.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(.35, "rgba(255,255,255,.35)"); gr.addColorStop(1, "rgba(255,255,255,0)"); g.fillStyle = gr; g.fillRect(0, 0, s, s); });
const glows = new THREE.InstancedMesh(new THREE.PlaneGeometry(1.5, 1.5), new THREE.MeshBasicMaterial({ map: glowTex, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false }), N);
for (let i = 0; i < N; i++) glows.setColorAt(i, new THREE.Color(0, 0, 0)); scene.add(glows);

// marks above racks: tick, cross, alert
const markTex = (kind) => tex((g, s) => {
  const c = { ok: "#2fe37f", x: "#ff3b30", bang: "#ff3b30" }[kind];
  g.fillStyle = c; g.beginPath(); g.arc(s / 2, s / 2, s * .42, 0, 7); g.fill();
  g.strokeStyle = "#ffffff"; g.lineWidth = s * .1; g.lineCap = "round"; g.lineJoin = "round"; g.beginPath();
  if (kind === "ok") { g.moveTo(s * .3, s * .52); g.lineTo(s * .44, s * .66); g.lineTo(s * .71, s * .37); }
  if (kind === "x") { g.moveTo(s * .34, s * .34); g.lineTo(s * .66, s * .66); g.moveTo(s * .66, s * .34); g.lineTo(s * .34, s * .66); }
  if (kind === "bang") { g.moveTo(s * .5, s * .28); g.lineTo(s * .5, s * .58); g.stroke(); g.fillStyle = "#fff"; g.beginPath(); g.arc(s * .5, s * .72, s * .055, 0, 7); g.fill(); return; }
  g.stroke();
}, 128);
const MT = { ok: markTex("ok"), x: markTex("x"), bang: markTex("bang") };
const marks = racks.map(() => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: MT.ok, transparent: true, depthTest: false, toneMapped: false })); s.renderOrder = 10; s.visible = false; scene.add(s); return s; });

// traffic particles (glowing points)
const NP = 2400, pPos = new Float32Array(NP * 3).fill(-100), pCol = new Float32Array(NP * 3);
const pGeo = new THREE.BufferGeometry(); pGeo.setAttribute("position", new THREE.BufferAttribute(pPos, 3)); pGeo.setAttribute("color", new THREE.BufferAttribute(pCol, 3));
const dotTex = tex((g, s) => { const gr = g.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(.3, "rgba(255,255,255,.8)"); gr.addColorStop(1, "rgba(255,255,255,0)"); g.fillStyle = gr; g.fillRect(0, 0, s, s); }, 64);
const parts = new THREE.Points(pGeo, new THREE.PointsMaterial({ size: .62, map: dotTex, vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false }));
parts.frustumCulled = false; scene.add(parts);

// health-check scanner: a glowing sheet sweeping across the rows
const scanTex = tex((g, s) => { const gr = g.createLinearGradient(0, s, 0, 0); gr.addColorStop(0, "rgba(255,255,255,.9)"); gr.addColorStop(.25, "rgba(255,255,255,.25)"); gr.addColorStop(1, "rgba(255,255,255,0)"); g.fillStyle = gr; g.fillRect(0, 0, s, s); });
const scanner = new THREE.Mesh(new THREE.PlaneGeometry(8.8, 3.2), new THREE.MeshBasicMaterial({ map: scanTex, color: "#2fe37f", transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false, side: THREE.DoubleSide, toneMapped: false }));
scanner.rotation.y = Math.PI / 2; scanner.position.y = 1.6; scanner.renderOrder = 5; scene.add(scanner);
const scanLine = new THREE.Mesh(new THREE.BoxGeometry(.05, .012, 8.6), new THREE.MeshBasicMaterial({ color: "#7dffb2", toneMapped: false })); scanLine.position.y = .01; scene.add(scanLine);

// ---------- the state of one rack at time t
function state(i, t) {
  const k = racks[i], s = { show: 1, rise: 1, dx: 0, dy: 0, dz: 0, rot: 0, col: COL.green, lit: [1, 1, 1, 1, 1, 1], glow: 0, gcol: COL.red, mark: null, ms: 0, busy: .55 };
  // rise out of the floor, in a diagonal wave from the back-left
  const ta = T.rise + .04 + (k.row * 0.6 + k.col) * .045; s.rise = t < ta ? 0 : back((t - ta) / .5);
  // health checks: the beam passes, a tick pops
  const tb = T.scan + (k.x + 4.6) / 9.2 * 1.45 + .03;
  if (t >= tb && t < tb + .9) { s.mark = "ok"; s.ms = back((t - tb) / .25) * (1 - clamp((t - tb - .65) / .25)); }
  // the sick one: red, an alert, pulled out of its row and gone
  if (i === SICK) {
    if (t >= T.one) { s.glow = .35 * clamp((t - T.one) / .3); s.gcol = COL.white; }
    if (t >= T.sick) { s.col = COL.red; s.glow = .9; s.gcol = COL.red; s.mark = "bang"; s.ms = back((t - T.sick) / .25); s.dy = .1 * Math.sin(clamp((t - T.sick) / .3) * Math.PI); }
    if (t >= T.pull) { s.dz = 1.5 * eio((t - T.pull) / .45); s.ms *= 1 - clamp((t - T.pull) / .2); const g = clamp((t - T.pull - .5) / .3); s.dy -= 1.6 * g * g; s.show = 1 - g; }
    if (t >= T.pull + .8) s.show = 0;
  }
  // the wave: every rack except a few fails its checks
  const tf = T.wave + k.d / dMax * .75;
  if (!isSurv(i) && t >= tf) { s.col = COL.red; s.glow = .75; s.gcol = COL.red; s.dy = .12 * Math.sin(clamp((t - tf) / .28) * Math.PI);
    if (t < tf + .75) { s.mark = "x"; s.ms = back((t - tf) / .22) * (1 - clamp((t - tf - .5) / .25)); } }
  // survivors take the dumped traffic: flicker amber, then overload and fail one after another
  const si = SURV.indexOf(i);
  if (si >= 0) {
    if (t >= T.dump + .45) { s.busy = 1; s.col = (Math.floor(t * 9 + si) % 3 === 0) ? COL.amber : COL.green; s.glow = .35; s.gcol = COL.green; }
    if (t >= T.over) { s.col = COL.amber; s.glow = .8; s.gcol = COL.amber; s.dx = .03 * Math.sin(t * 70 + si); s.dz = .02 * Math.cos(t * 63 + si); }
    const t2 = T.fail2 + si * .13;
    if (t >= t2) { s.col = COL.red; s.gcol = COL.red; s.glow = .85; s.dx = 0; s.dz = 0; s.dy = .14 * Math.sin(clamp((t - t2) / .28) * Math.PI);
      if (t < t2 + .8) { s.mark = "x"; s.ms = back((t - t2) / .22) * (1 - clamp((t - t2 - .55) / .25)); } }
  }
  // restart: everything goes dark, then the lights come back unit by unit, bottom to top
  if (t >= T.dark) { s.col = COL.green; s.lit = [0, 0, 0, 0, 0, 0]; s.glow = 0; s.busy = 0; s.mark = null; }
  if (t >= T.back) { const tp = T.back + .05 + k.c / 6.3 * .45; s.lit = s.lit.map((_, j) => t >= tp + j * .05 ? 1 : 0); if (t >= tp + .3) { s.glow = .3 * (1 - clamp((t - tp - .3) / .6)); s.gcol = COL.green; s.busy = .55; } }
  // slammed: a wave of traffic hits from the left
  const th = T.slam + .18 + (k.x + 3) * .04;
  if (t >= th) { s.col = COL.amber; s.gcol = COL.amber; s.glow = .7; s.busy = 1; const q = clamp((t - th) / .35); s.dx = .16 * Math.sin(q * Math.PI) * (1 - q); s.dy = .06 * Math.sin(q * Math.PI); }
  // down again: red, then the units go dark top to bottom
  const td = T.down + .05 + k.c / 6.3 * .35;
  if (t >= td) { s.col = COL.red; s.gcol = COL.red; s.glow = .8; s.busy = 0; s.lit = s.lit.map((_, j) => t >= td + .35 + (5 - j) * .07 ? 0 : 1);
    if (t < td + .7) { s.mark = "x"; s.ms = back((t - td) / .22) * (1 - clamp((t - td - .45) / .25)); }
    s.glow = .8 - .5 * clamp((t - td - .3) / .6); }
  // recovery, one stage at a time (groups of columns, left to right)
  if (t >= T.rec - .3) { s.col = COL.red; s.lit = [0, 0, 0, 0, 0, 0]; s.glow = .3; s.gcol = COL.red; s.mark = null; }
  const grp = k.col < 2 ? 0 : k.col < 4 ? 1 : k.col < 6 ? 2 : 3, tr = T.rec + .22 + grp * .4 + k.row * .04;
  if (t >= tr) { s.col = COL.green; s.gcol = COL.green; s.busy = .55; s.lit = s.lit.map((_, j) => t >= tr + j * .03 ? 1 : 0); s.glow = .7 * (1 - clamp((t - tr - .2) / .8));
    if (t < tr + .95) { s.mark = "ok"; s.ms = back((t - tr) / .22) * (1 - clamp((t - tr - .7) / .25)); } }
  if (i === SICK && t >= T.pull + .8) s.show = 0;
  return s;
}

// ---------- particles at time t
function particles(t) {
  let n = 0; const put = (x, y, z, c) => { if (n >= NP) return; pPos.set([x, y, z], n * 3); pCol.set([c.r, c.g, c.b], n * 3); n++; };
  const top = (i) => { const k = racks[i]; return new THREE.Vector3(k.x, RH + .12, k.z); };
  const arc = (a, b, h, q) => { const p = a.clone().lerp(b, q); p.y += Math.sin(q * Math.PI) * h; return p; };
  const blue = new THREE.Color("#5fd0ff"), TR = [1, .55, .3, .16];
  // dump: from the failed racks onto the survivors
  if (t > T.dump - .1 && t < T.over + .6) {
    const src = racks.map((_, i) => i).filter((i) => i !== SICK && !isSurv(i));
    for (let p = 0; p < 220; p++) { const st = T.dump + .05 + (p / 220) * 1.6, q = (t - st) / .6; if (q < 0 || q > 1) continue;
      const a = top(src[(p * 7) % src.length]), b = top(SURV[p % SURV.length]), h = 1.4 + hash(p, 1, 2) * .8;
      TR.forEach((f, j) => { const qq = q - j * .05; if (qq < 0) return; const v = arc(a, b, h, eio(qq)); put(v.x, v.y, v.z, blue.clone().multiplyScalar(f)); }); }
  }
  // slam: a flood of traffic from the left onto every rack
  if (t > T.slam - .3 && t < T.slam + 1) {
    racks.forEach((k, i) => { if (i === SICK) return; const th = T.slam + .18 + (k.x + 3) * .04;
      for (let j = 0; j < 5; j++) { const st = th - .4 + j * .035, q = (t - st) / .4; if (q < 0 || q > 1) continue;
        const a = new THREE.Vector3(-6.5, 2.2 + hash(i, j, 3) * 1.5, k.z + (hash(i, j, 4) - .5) * 1.2), b = new THREE.Vector3(k.x, .4 + j * .2, k.z + .5);
        TR.forEach((f, jj) => { const qq = q - jj * .06; if (qq < 0) return; const v = a.clone().lerp(b, eout(qq)); put(v.x, v.y, v.z, COL.amber.clone().multiplyScalar(f)); }); } });
  }
  for (let i = n; i < NP; i++) pPos.set([0, -100, 0], i * 3);
  pGeo.attributes.position.needsUpdate = true; pGeo.attributes.color.needsUpdate = true;
}

// ---------- cameras: one move per shot
const SHOT = {
  rise: [[15, 17, 20.5], [0, -.3, .4], [12.5, 13.5, 17.5], [0, 0, .4]],
  scan: [[-7.6, 4.3, 11.2], [-1.8, .8, .8], [6.2, 4.1, 11.6], [2, .8, .8]],
  sick: [[4.2, 3.5, 10.8], [0, 1.1, 2.4], [2.9, 2.9, 10], [0, .9, 3]],
  fail: [[-9, 16, 12], [0, 0, .3], [-4, 17.5, 14.5], [0, 0, .3]],
  dump: [[14, 11, 10], [1.2, .5, 0], [12, 10, 13], [1.6, .5, .6]],
  over: [[11.5, 5.2, 11.5], [3.2, .9, 1.6], [10, 4.5, 12.4], [3.2, .9, 1.9]],
  restart: [[0, 10, 20.5], [0, .4, 0], [0, 8.6, 18.5], [0, .5, .2]],
  down: [[-13, 8, 15], [-.3, 1.5, .6], [-11.5, 7, 13.5], [-.4, 1.5, .9]],
  rec: [[9.5, 13.5, 14], [0, 0, 0], [-6, 12.5, 16], [0, 0, 0]],
};
const v3 = (a) => new THREE.Vector3(...a);
function camera(t) {
  let name = Object.keys(R).find((n) => t >= R[n][0] - .001 && t <= R[n][1] + .001) || "rise";
  const [a, b] = R[name], q = eio((t - a) / Math.max(.1, b - a)) * .85 + clamp((t - a) / Math.max(.1, b - a)) * .15, S = SHOT[name];
  cam.position.copy(v3(S[0]).lerp(v3(S[2]), q)); cam.lookAt(v3(S[1]).lerp(v3(S[3]), q)); cam.updateMatrixWorld();
  return name;
}

// ---------- draw one frame
const M = new THREE.Matrix4(), M2 = new THREE.Matrix4(), Q = new THREE.Quaternion(), P = new THREE.Vector3(), Sc = new THREE.Vector3(), C = new THREE.Color();
function frame(t) {
  const shot = camera(t);
  racks.forEach((k, i) => {
    const s = state(i, t), sy = Math.max(.001, s.rise) * Math.max(.001, s.show);
    Q.setFromAxisAngle(new THREE.Vector3(0, 1, 0), s.rot); P.set(k.x + s.dx, s.dy, k.z + s.dz); Sc.set(Math.max(.001, s.show), sy, Math.max(.001, s.show));
    M.compose(P, Q, Sc);   // the rack's frame (origin at its foot)
    const L = (x, y, z) => M2.copy(M).multiply(new THREE.Matrix4().makeTranslation(x, y, z));
    body.setMatrixAt(i, L(0, RH / 2, 0)); panel.setMatrixAt(i, L(0, RH / 2 + .01, RD / 2 + .002)); tops.setMatrixAt(i, L(0, RH + .002, RD / 2 - .06));
    tops.setColorAt(i, s.lit.some((x) => x) ? s.col : COL.off);
    for (let j = 0; j < UNITS; j++) { const u = i * UNITS + j, on = s.lit[j];
      units.setMatrixAt(u, L(0, uy(j), RD / 2 + .014)); strips.setMatrixAt(u, L(-.08, uy(j), RD / 2 + .03));
      const pulse = on ? (s.busy > .9 ? .65 + .35 * (hash(i, j, Math.floor(t * 14)) > .4 ? 1 : 0) : 1) : 0;
      C.copy(on ? s.col : COL.off).multiplyScalar(on ? pulse : 1); strips.setColorAt(u, C);
      for (let d = 0; d < 2; d++) { const dd = u * 2 + d; dots.setMatrixAt(dd, L(.12 + d * .06, uy(j), RD / 2 + .03));
        const blink = on && hash(i * 7 + d, j, Math.floor(t * (6 + d * 3))) < s.busy; dots.setColorAt(dd, blink ? s.col : COL.off); } }
    glows.setMatrixAt(i, new THREE.Matrix4().compose(new THREE.Vector3(k.x + s.dx, .012, k.z + s.dz + .35), new THREE.Quaternion().setFromEuler(new THREE.Euler(-Math.PI / 2, 0, 0)), new THREE.Vector3(1, 1, 1)));
    glows.setColorAt(i, C.copy(s.gcol).multiplyScalar(s.glow * Math.min(1, s.rise) * s.show));
    const mk = marks[i]; mk.visible = !!s.mark && s.ms > .01 && s.show > .05;
    if (mk.visible) { mk.material.map = MT[s.mark]; mk.position.set(k.x + s.dx, RH + .55 + s.dy, k.z + s.dz + .1); mk.scale.setScalar(.5 * s.ms); }
  });
  [body, panel, units, strips, dots, tops, glows].forEach((m) => { m.instanceMatrix.needsUpdate = true; if (m.instanceColor) m.instanceColor.needsUpdate = true; });
  // the scanner
  const sq = (t - T.scan) / 1.45; scanner.visible = scanLine.visible = sq > 0 && sq < 1;
  if (scanner.visible) { const x = -4.6 + 9.2 * sq; scanner.position.x = x; scanLine.position.x = x; scanner.material.opacity = Math.sin(sq * Math.PI) * .45 + .25; }
  particles(t);
  r.render(scene, cam);
  return shot;
}
window.__seek = (t) => frame(t);
window.__ready = true;
frame(R.rise[0] + .8);
