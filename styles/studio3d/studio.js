// studio3d runtime: a warm studio floor, soft shadows, one continuous camera, and HTML overlays (state bar, tag,
// callout labels, titles, caption pill). A topic's scene module gets the API `S` and builds its objects on top.
// Everything is a pure function of timeline time, so HyperFrames can seek any frame.
import * as THREE from "three";
import { RoundedBoxGeometry } from "./RoundedBoxGeometry.js";

export const C = { floor: "#e6e2db", grid: "#d6d1c8", charcoal: "#55595f", dark: "#2b2d31", ink: "#141518", white: "#f4f2ee",
  glass: "#cfe3ea", orange: "#e0731f", red: "#d93a2b", blue: "#2457e6", green: "#1f9d6b" };

export function boot(cfg, build) {
  const W = cfg.width, H = cfg.height, T = cfg.timing, lines = T.lines;
  const canvas = document.getElementById("gl");
  const r = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  r.setPixelRatio(1); r.setSize(W, H, false);
  r.shadowMap.enabled = true; r.shadowMap.type = THREE.PCFSoftShadowMap;
  r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = 1.05; r.outputColorSpace = THREE.SRGBColorSpace;
  const scene = new THREE.Scene(); scene.background = new THREE.Color(C.floor); scene.fog = new THREE.Fog(C.floor, 18, 46);
  const cam = new THREE.PerspectiveCamera(cfg.fov || 30, W / H, 0.05, 200);
  scene.add(new THREE.HemisphereLight("#ffffff", "#c9c2b6", 1.5));
  const sun = new THREE.DirectionalLight("#ffffff", 2.3); sun.position.set(-6, 14, 8); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, { left: -10, right: 10, top: 10, bottom: -10, near: 1, far: 40 });
  sun.shadow.radius = 5; sun.shadow.bias = -0.0004; scene.add(sun);
  const fill = new THREE.DirectionalLight("#fff6ea", 0.5); fill.position.set(8, 5, -4); scene.add(fill);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), new THREE.MeshStandardMaterial({ color: C.floor, roughness: 1 }));
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
  const grid = new THREE.GridHelper(120, 60, C.grid, C.grid); grid.position.y = 0.003; grid.material.transparent = true; grid.material.opacity = 0.55; scene.add(grid);

  // ---------- time grammar: seconds | "start" | "end" | "line:N" | "line:N:end" | "word:text" (+/- offset)
  const words = lines.flatMap((l) => l.words);
  function at(spec) {
    if (typeof spec === "number") return spec;
    const m = String(spec).trim().match(/^(.*?)([+-]\d*\.?\d+)?$/); const base = m[1]; const off = parseFloat(m[2] || 0);
    let t;
    if (base === "start") t = 0; else if (base === "end") t = T.duration;
    else if (base.startsWith("line:")) { const p = base.split(":"); const l = lines[Math.min(+p[1], lines.length - 1)]; t = p[2] === "end" ? l.end : l.start; }
    else if (base.startsWith("word:")) { const w = base.slice(5).toLowerCase(); const hit = words.find((x) => x.w.toLowerCase().replace(/[,.!?:;"']/g, "") === w); if (!hit) throw new Error("no word " + w); t = hit.t; }
    else throw new Error("bad time " + spec);
    return t + off;
  }

  // ---------- materials and primitives
  const mats = {};
  const mat = (color, o = {}) => {
    const k = color + JSON.stringify(o);
    if (!mats[k]) mats[k] = new THREE.MeshStandardMaterial({ color, roughness: o.rough ?? 0.72, metalness: o.metal ?? 0, transparent: o.opacity != null, opacity: o.opacity ?? 1, emissive: o.emissive || "#000000", depthWrite: o.opacity == null || o.opacity > 0.6 });
    return o.unique ? mats[k].clone() : mats[k];
  };
  const prep = (m, pos, parent) => { m.castShadow = m.receiveShadow = true; if (pos) m.position.set(...pos); (parent || scene).add(m); return m; };
  const S = {
    THREE, scene, camera: cam, C, at, mat, words, lines, duration: T.duration,
    tl: null, frames: [],
    box: (w, h, d, color, pos, parent, o) => prep(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat(color, o)), pos, parent),
    rbox: (w, h, d, rad, color, pos, parent, o) => prep(new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 4, rad), mat(color, o)), pos, parent),
    cyl: (rt, rb, h, color, pos, parent, o) => prep(new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, 48), mat(color, o)), pos, parent),
    sphere: (rad, color, pos, parent, o) => prep(new THREE.Mesh(new THREE.SphereGeometry(rad, 32, 20), mat(color, o)), pos, parent),
    torus: (rad, tube, color, pos, parent, o) => prep(new THREE.Mesh(new THREE.TorusGeometry(rad, tube, 16, 64), mat(color, o)), pos, parent),
    group: (pos, parent) => { const g = new THREE.Group(); if (pos) g.position.set(...pos); (parent || scene).add(g); return g; },
    spring: (rad, len, turns, wire, color, parent) => {   // a helix along +X, starting at the origin
      const pts = []; for (let i = 0; i <= turns * 24; i++) { const a = (i / 24) * Math.PI * 2; pts.push(new THREE.Vector3((i / (turns * 24)) * len, Math.sin(a) * rad, Math.cos(a) * rad)); }
      return prep(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), turns * 24, wire, 8), mat(color, { rough: 0.35, metal: 0.6 })), null, parent);
    },
    // a phone: rounded slab with screen and camera bump. Returns {g, body, screen, bump}
    phone: (pos, o = {}) => {
      const g = S.group(pos); const w = o.w || 3.2, h = o.h || 6.6, d = 0.34;
      const body = S.rbox(w, d, h, 0.3, o.color || C.dark, [0, d / 2, 0], g);
      const screen = S.rbox(w - 0.2, 0.02, h - 0.2, 0.22, o.screen || "#1c2433", [0, d + 0.005, 0], g, { rough: 0.25 });
      const bump = S.rbox(1.3, 0.12, 1.3, 0.25, o.color || C.dark, [-w / 2 + 0.85, -0.04, -h / 2 + 0.85], g);
      return { g, body, screen, bump };
    },
    onFrame: (fn) => S.frames.push(fn),
  };

  // ---------- camera rig: keys [{at, pos:[x,y,z], look:[x,y,z], ease}] tweened in order, plus a tiny handheld drift
  const rig = { x: 0, y: 6, z: 14, lx: 0, ly: 0, lz: 0, drift: cfg.drift ?? 0.03 };
  S.cameraPath = (keys) => {
    const k0 = keys[0]; Object.assign(rig, { x: k0.pos[0], y: k0.pos[1], z: k0.pos[2], lx: k0.look[0], ly: k0.look[1], lz: k0.look[2] });
    for (let i = 1; i < keys.length; i++) {
      const a = at(keys[i - 1].at), b = at(keys[i].at), k = keys[i];
      S.tl.to(rig, { x: k.pos[0], y: k.pos[1], z: k.pos[2], lx: k.look[0], ly: k.look[1], lz: k.look[2], duration: Math.max(0.05, b - a), ease: k.ease || "power2.inOut" }, a);
    }
  };

  // ---------- overlays
  const ov = document.getElementById("ov");
  const el = (cls, html, parent) => { const d = document.createElement("div"); d.className = cls; d.innerHTML = html; (parent || ov).appendChild(d); return d; };
  const tl = gsap.timeline({ paused: true, onUpdate: () => frame(tl.time()) }); S.tl = tl;
  // state bar
  if (cfg.states && cfg.states.length) {
    const bar = el("sbar", `<div class="sline"></div>`); const n = cfg.states.length;
    const lab = el("slabel", "", bar);
    cfg.states.forEach((s, i) => {
      const x = (i / (n - 1)) * 100; const dot = el("sdot", "", bar); dot.style.left = x + "%";
      const t = at(s.at); const next = i + 1 < n ? at(cfg.states[i + 1].at) : T.duration + 1;
      tl.set(dot, { backgroundColor: s.color || C.ink, borderColor: s.color || C.ink, width: 34, borderRadius: 7 }, t);
      if (i + 1 < n) tl.set(dot, { backgroundColor: "#efece6", borderColor: "#8d8981", width: 14, borderRadius: 7 }, next);
      tl.set(lab, { innerText: s.label, left: x + "%", xPercent: i === 0 ? 0 : i === n - 1 ? -100 : -50 }, t);
    });
  }
  if (cfg.tag) el("tag", "• " + cfg.tag);
  // titles
  (cfg.titles || []).forEach((ti) => {
    const d = el("title", `<b>${ti.text}</b>${ti.sub ? `<span>${ti.sub}</span>` : ""}`);
    const a = at(ti.at), b = ti.until ? at(ti.until) : T.duration;
    tl.fromTo(d, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }, a);
    if (b < T.duration) tl.to(d, { opacity: 0, y: -20, duration: 0.25 }, b - 0.25);
  });
  // labels anchored to 3D points: S.label({anchor: Object3D | [x,y,z], title, sub, at, until, dx, dy, color})
  const labels = []; const svg = document.getElementById("leaders");
  S.label = (o) => {
    const d = el("label", `<b>${o.title}</b>${o.sub ? `<span>${o.sub}</span>` : ""}`);
    if (o.color) d.style.setProperty("--lc", o.color);
    const ln = document.createElementNS("http://www.w3.org/2000/svg", "line"); ln.setAttribute("stroke", o.color || C.ink); ln.setAttribute("stroke-width", "2.5"); svg.appendChild(ln);
    const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle"); dot.setAttribute("r", "6"); dot.setAttribute("fill", o.color || C.ink); svg.appendChild(dot);
    const L = { o, d, ln, dot, vis: { v: 0 } }; labels.push(L);
    const a = at(o.at), b = o.until ? at(o.until) : T.duration;
    tl.fromTo(L.vis, { v: 0 }, { v: 1, duration: 0.3, ease: "power2.out" }, a);
    if (b < T.duration) tl.to(L.vis, { v: 0, duration: 0.2 }, b - 0.2);
    return L;
  };
  // caption pill: one line at a time, words grey until spoken
  lines.forEach((l, i) => {
    const pill = el("cap", l.words.map((w) => `<i>${w.w}</i>`).join(" "));
    const a = Math.max(0, l.start - 0.08), b = i + 1 < lines.length ? lines[i + 1].start - 0.08 : Math.min(T.duration, l.end + 0.7);
    tl.set(pill, { opacity: 1 }, a); if (b < T.duration) tl.to(pill, { opacity: 0, duration: i + 1 < lines.length ? 0.01 : 0.25 }, b);
    tl.fromTo(pill, { scale: 0.92 }, { scale: 1, duration: 0.18, ease: "back.out(2)" }, a);
    [...pill.children].forEach((sp, j) => tl.set(sp, { color: "#ffffff" }, l.words[j].t));
  });

  build(S);   // the topic's scene: objects, tweens, camera path, labels

  const v = new THREE.Vector3();
  function project(p) { v.copy(p).project(cam); return [(v.x * 0.5 + 0.5) * W, (-v.y * 0.5 + 0.5) * H, v.z]; }
  function frame(t) {
    S.frames.forEach((fn) => fn(t));
    const dr = rig.drift;
    cam.position.set(rig.x + Math.sin(t * 0.7) * dr, rig.y + Math.sin(t * 0.9 + 1) * dr, rig.z);
    cam.lookAt(rig.lx, rig.ly, rig.lz); cam.updateMatrixWorld();
    labels.forEach((L) => {
      const o = L.o; const wp = o.anchor.isObject3D ? o.anchor.getWorldPosition(new THREE.Vector3()) : new THREE.Vector3(...o.anchor);
      if (o.offset) wp.add(new THREE.Vector3(...o.offset));
      const [x, y, z] = project(wp); const right = (o.dx ?? 160) >= 0, lw = L.d.offsetWidth || 300, lh = L.d.offsetHeight || 80;
      let lx = x + (o.dx ?? 160), ly = y + (o.dy ?? -140);
      if (right) lx = Math.min(lx, W - 40 - lw); else lx = Math.max(lx, 40 + lw);   // keep labels inside the frame
      ly = Math.max(380 + lh / 2, Math.min(ly, 1440 - lh / 2));                      // clear of the state bar and the captions
      const vis = z < 1 ? L.vis.v : 0;
      L.d.style.opacity = vis; L.d.style.transform = `translate(${lx}px, ${ly}px) translate(${right ? "0" : "-100%"}, -50%) scale(${0.9 + 0.1 * vis})`;
      L.ln.setAttribute("x1", x); L.ln.setAttribute("y1", y); L.ln.setAttribute("x2", lx); L.ln.setAttribute("y2", ly); L.ln.setAttribute("opacity", vis);
      L.dot.setAttribute("cx", x); L.dot.setAttribute("cy", y); L.dot.setAttribute("opacity", vis);
    });
    r.render(scene, cam);
  }
  tl.to({}, { duration: T.duration }, 0);
  frame(0);
  return tl;
}
