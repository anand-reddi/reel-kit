// Exploded-view showcase (look: "dark"): an original retro Indian step-through scooter built from simple solids,
// a slow three-quarter orbit, then the parts fly apart with labels and snap back together.
import { RoundedBoxGeometry } from "./RoundedBoxGeometry.js";
export default function (S) {
  const { THREE } = S;
  const P = S.paint("#1f8f8a"), CREAM = S.paint("#f1e6cf", { coat: .6, rough: .35 }), LAMP = S.paint("#fff6d8", { emissive: "#ffe9a8", glow: 1.6, rough: .05 });
  const CHROME = new THREE.MeshStandardMaterial({ color: "#ffffff", roughness: .08, metalness: 1 }), TYRE = S.mat("#151515", { rough: .9 }),
    RIM = S.mat("#bfc3c7", { rough: .3, metal: .9 }), SEAT = S.mat("#3a2418", { rough: .7 }), DARK = S.mat("#2a2a2a", { rough: .5, metal: .6 }), RED = S.mat("#e5372d", { rough: .4, metal: .3 });
  const m = (g, mat, p, r = [0, 0, 0], s = [1, 1, 1], parent) => { const o = new THREE.Mesh(g, mat); o.position.set(...p); o.rotation.set(...r); o.scale.set(...s); o.castShadow = o.receiveShadow = true; parent.add(o); return o; };
  const part = () => S.group([0, 0, 0]);
  const wheel = (g, x) => { m(new THREE.TorusGeometry(.19, .07, 20, 48), TYRE, [x, .26, 0], [0, 0, 0], [1, 1, 1], g);
    m(new THREE.CylinderGeometry(.15, .15, .1, 32), RIM, [x, .26, 0], [Math.PI / 2, 0, 0], [1, 1, 1], g);
    m(new THREE.CylinderGeometry(.05, .05, .14, 16), CHROME, [x, .26, 0], [Math.PI / 2, 0, 0], [1, 1, 1], g); };
  const fw = part(); wheel(fw, .72); m(new THREE.TorusGeometry(.29, .05, 12, 40, Math.PI * .95), P, [.72, .27, 0], [0, 0, Math.PI * .05], [1, 1, 1], fw);
  const rw = part(); wheel(rw, -.66);
  const fb = part(); m(new RoundedBoxGeometry(.85, .06, .44, 4, .02), DARK, [.02, .34, 0], [0, 0, 0], [1, 1, 1], fb);
  [-.15, 0, .15].forEach((z) => m(new THREE.BoxGeometry(.8, .012, .03), CHROME, [.02, .375, z], [0, 0, 0], [1, 1, 1], fb));
  const ls = part(); const sh = m(new THREE.CylinderGeometry(.34, .26, .75, 40, 1, true, -Math.PI * .42, Math.PI * .84), P, [.36, .72, 0], [0, -Math.PI / 2, -.18], [1, 1, 1], ls); sh.material = P.clone(); sh.material.side = THREE.DoubleSide;
  const hl = part(); m(new THREE.CylinderGeometry(.025, .03, .75, 16), CHROME, [.62, .78, 0], [0, 0, -.18], [1, 1, 1], hl);
  m(new RoundedBoxGeometry(.2, .14, .7, 4, .06), P, [.69, 1.15, 0], [0, 0, 0], [1, 1, 1], hl);
  m(new THREE.CylinderGeometry(.075, .075, .05, 32), LAMP, [.79, 1.15, 0], [0, 0, Math.PI / 2], [1, 1, 1], hl);
  m(new THREE.TorusGeometry(.078, .012, 10, 32), CHROME, [.815, 1.15, 0], [0, Math.PI / 2, 0], [1, 1, 1], hl);
  [-.42, .42].forEach((z) => m(new THREE.CylinderGeometry(.022, .022, .16, 12), DARK, [.69, 1.16, z], [Math.PI / 2, 0, 0], [1, 1, 1], hl));
  const bs = part(); m(new THREE.SphereGeometry(1, 48, 32), P, [-.45, .58, 0], [0, 0, .08], [.5, .3, .29], bs);
  m(new THREE.TorusGeometry(.29, .01, 8, 48), CHROME, [-.45, .58, 0], [Math.PI / 2, 0, 0], [1.7, 1, 1], bs); m(new THREE.BoxGeometry(.05, .06, .12), RED, [-.94, .62, 0], [0, 0, 0], [1, 1, 1], bs);
  const st = part(); m(new RoundedBoxGeometry(.62, .1, .3, 6, .05), SEAT, [-.32, .92, 0], [0, 0, 0], [1, 1, 1], st); m(new THREE.BoxGeometry(.5, .03, .26), DARK, [-.32, .86, 0], [0, 0, 0], [1, 1, 1], st);
  const ft = part(); m(new RoundedBoxGeometry(.36, .2, .24, 4, .05), CREAM, [-.3, .72, 0], [0, 0, 0], [1, 1, 1], ft); m(new THREE.CylinderGeometry(.04, .04, .05, 20), CHROME, [-.3, .84, 0], [0, 0, 0], [1, 1, 1], ft);
  const en = part(); m(new RoundedBoxGeometry(.34, .2, .2, 4, .04), DARK, [-.5, .38, .05], [0, 0, 0], [1, 1, 1], en);
  for (let i = 0; i < 6; i++) m(new THREE.BoxGeometry(.012, .2, .26), RIM, [-.62 + i * .045, .42, .05], [0, 0, 0], [1, 1, 1], en);

  // the camera: a slow three-quarter orbit, pulled back while exploded
  const orbit = (deg, d, y, ly) => { const a = THREE.MathUtils.degToRad(deg); return { pos: [Math.sin(a) * d, y, Math.cos(a) * d], look: [0, ly, 0] }; };
  S.cameraPath([{ at: "start", ...orbit(22, 7.8, 2.0, .62) }, { at: "line:1-0.2", ...orbit(36, 6.4, 2.0, .62) },
    { at: "word:apart+0.9", ...orbit(46, 8.8, 2.6, .92), ease: "power2.inOut" }, { at: "line:2:end", ...orbit(52, 8.8, 2.6, .92) },
    { at: "end", ...orbit(60, 6.4, 2.0, .62), ease: "power2.inOut" }]);
  S.explode([{ obj: fw, off: [.6, 0, 0] }, { obj: rw, off: [-.55, 0, 0] }, { obj: fb, off: [0, -.25, .55] }, { obj: ls, off: [.55, .25, 0] },
    { obj: hl, off: [.6, .75, 0] }, { obj: bs, off: [-.35, .7, 0] }, { obj: st, off: [0, 1.15, 0] }, { obj: ft, off: [.05, .2, .95] }, { obj: en, off: [-.2, -.05, .95] }],
    { at: "word:apart", back: "line:2:end+0.1" });
  const L = (obj, title, at, dx, off) => S.label({ anchor: obj, offset: off, title, at, until: "line:2:end", dx, dy: 0 });
  L(en, "2-stroke engine", "word:two-stroke", -170, [-.5, .38, .1]); L(bs, "Steel body shell", "word:steel", -170, [-.62, .7, .2]);
  L(fw, '10" wheels', "word:ten-inch", 150, [.72, .26, .1]); L(st, "Seat", "word:apart+0.5", 150, [-.3, 1.0, 0]);
  L(hl, "Headlamp", "word:apart+0.7", -150, [.78, 1.16, 0]); L(ls, "Leg shield", "word:apart+0.9", 150, [.5, .7, .2]);
}
