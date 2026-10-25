// OIS: the camera module rises out of the phone; the hand shakes it; the gyroscope senses it; magnets push the lens
// the opposite way so the light keeps landing on the same spot of the sensor.
export default function (S) {
  const { THREE, C, at, tl } = S;
  const BUMP = [-0.75, 0, -2.45];
  // ---- phone lying on its screen, back up
  const phone = S.group([0, 0, 0]);
  S.rbox(3.2, 0.34, 6.6, 0.3, "#3a3d42", [0, 0.17, 0], phone);
  S.rbox(1.3, 0.12, 1.3, 0.24, "#33363b", [BUMP[0], 0.4, BUMP[2]], phone);
  S.torus(0.32, 0.05, "#1d1f22", [BUMP[0], 0.47, BUMP[2]], phone).rotation.x = Math.PI / 2;
  S.cyl(0.27, 0.27, 0.04, "#1a2230", [BUMP[0], 0.46, BUMP[2]], phone, { rough: 0.2 });
  // gyroscope chip on the back (as if seen through it)
  const gyro = S.group([0.55, 0.36, -1.3], phone);
  S.rbox(0.7, 0.08, 0.7, 0.06, "#2b2d31", [0, 0.04, 0], gyro);
  const gring = S.torus(0.2, 0.025, C.green, [0, 0.14, 0], gyro, { unique: true, emissive: "#000000" }); gring.rotation.x = Math.PI / 2;
  const gring2 = S.torus(0.2, 0.025, C.green, [0, 0.14, 0], gyro, { unique: true });
  // ---- the module, exploded up out of the bump
  const M = S.group([BUMP[0], 0.4, BUMP[2]]);        // rises
  const body = S.group([0, 0, 0], M);                 // shakes with the hand
  const wall = "#5d6168";
  S.box(2.4, 0.08, 2.4, "#2b2d31", [0, -0.42, 0], body);                       // board
  const sensor = S.box(1.0, 0.05, 1.0, "#22324a", [0, -0.36, 0], body, { rough: 0.3 });
  [[0, 0, 1.15, 2.4, 0.12], [0, 0, -1.15, 2.4, 0.12], [1.15, 0, 0, 0.12, 2.4], [-1.15, 0, 0, 0.12, 2.4]].forEach(([x, y, z, w, d]) =>
    S.box(w, 0.7, d, wall, [x, -0.05, z], body, { opacity: 0.55 }));
  const magL = S.box(0.16, 0.4, 0.9, C.red, [-0.98, 0.1, 0], body, { unique: true });
  const magR = S.box(0.16, 0.4, 0.9, C.blue, [0.98, 0.1, 0], body, { unique: true });
  const lens = S.group([0, 0.15, 0], body);
  S.cyl(0.52, 0.52, 0.46, "#2b2d31", [0, 0, 0], lens);
  S.cyl(0.42, 0.42, 0.07, C.glass, [0, 0.25, 0], lens, { opacity: 0.6, rough: 0.1 });
  S.cyl(0.42, 0.42, 0.05, C.glass, [0, 0.05, 0], lens, { opacity: 0.45, rough: 0.1 });
  const coilL = S.torus(0.15, 0.045, C.orange, [-0.56, 0.05, 0], lens, { unique: true }); coilL.rotation.y = Math.PI / 2;
  const coilR = S.torus(0.15, 0.045, C.orange, [0.56, 0.05, 0], lens, { unique: true }); coilR.rotation.y = Math.PI / 2;
  // four springs from the barrel to the frame corners
  const springs = [];
  [45, 135, 225, 315].forEach((deg) => {
    const g = S.group([0, 0.15, 0], body); g.rotation.y = (deg * Math.PI) / 180;
    const sp = S.spring(0.06, 0.95, 7, 0.016, "#b9bdc4", g); sp.position.x = 0.5; springs.push({ g, sp, deg });
  });
  const springAnchor = S.group([0.95, 0.15, -0.95], body);
  // light: a beam from above through the lens to a spot on the sensor
  const beamMat = new THREE.MeshBasicMaterial({ color: "#ffd25a", transparent: true, opacity: 0.85 });
  const beamA = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 1, 12), beamMat); S.scene.add(beamA);
  const beamB = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 1, 12), beamMat); S.scene.add(beamB);
  const spot = S.sphere(0.07, C.red, [0, -0.32, 0], body, { unique: true, emissive: "#000000" });
  const streak = S.box(1, 0.012, 0.12, C.red, [0, -0.33, 0], body, { unique: true, opacity: 0.8 });
  const spotAnchor = S.group([0, -0.3, 0], body);

  // ---- choreography
  const L = S.lines, tShake = at("word:shakes"), tGyro = at("word:gyroscope"), tMag = at("word:magnets"), tEnd = at("line:3:end+0.6");
  M.scale.setScalar(0.25);
  tl.to(M.position, { y: 2.3, duration: 1.4, ease: "power3.inOut" }, 0.35);
  tl.to(M.scale, { x: 1, y: 1, z: 1, duration: 1.4, ease: "power3.inOut" }, 0.35);
  springs.forEach((s, i) => tl.fromTo(s.sp.scale, { x: 0.6 }, { x: 1, duration: 0.5, ease: "elastic.out(1, 0.4)" }, at("word:springs") - 0.05 + i * 0.04));
  tl.to(gring.material.emissive, { r: 0.1, g: 0.6, b: 0.35, duration: 0.2, yoyo: true, repeat: 3 }, tGyro);
  tl.to(magL.material.emissive, { r: 0.45, g: 0.06, b: 0.03, duration: 0.25 }, tMag); tl.to(magR.material.emissive, { r: 0.03, g: 0.1, b: 0.5, duration: 0.25 }, tMag);
  [coilL, coilR].forEach((m) => tl.to(m.material.emissive, { r: 0.5, g: 0.22, b: 0.0, duration: 0.25 }, tMag));

  const A = 0.16, clamp = (x) => Math.max(0, Math.min(1, x));
  const shake = (t) => {
    const env = clamp((t - tShake + 0.1) / 0.3) * clamp((tEnd + 0.6 - t) / 0.6);
    return A * env * (Math.sin(t * 2 * Math.PI * 3.1) + 0.45 * Math.sin(t * 2 * Math.PI * 5.3 + 1.1));
  };
  const red = new THREE.Color(C.red), green = new THREE.Color(C.green);
  const pA = new THREE.Vector3(), pB = new THREE.Vector3(), pC = new THREE.Vector3();
  const place = (m, a, b) => { m.position.copy(a).add(b).multiplyScalar(0.5); const d = b.clone().sub(a); m.scale.set(1, d.length(), 1); m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.normalize()); };
  S.onFrame((t) => {
    const s = shake(t), c = clamp((t - tMag) / 0.35), env = Math.abs(s) > 0 ? 1 : 0;
    phone.position.x = s * 0.5; body.position.x = s;
    lens.position.x = -s * c;                              // the magnets push the lens the other way
    springs.forEach((k) => { const ang = k.g.rotation.y; k.sp.scale.x = 1 + (lens.position.x * Math.cos(ang)) * 0.6; k.sp.position.x = 0.5 + lens.position.x * Math.cos(ang) * 0.3; });
    const rel = -s * (1 - c);                              // where the light lands, relative to the sensor
    spot.position.x = rel;
    const blur = (1 - c) * clamp((t - tShake) / 0.3) * clamp((tEnd + 0.6 - t) / 0.6);
    streak.scale.x = 0.02 + blur * A * 2.6; streak.material.opacity = 0.75 * blur;
    spot.material.color.copy(red).lerp(green, c); spot.material.emissive.copy(spot.material.color).multiplyScalar(0.35);
    gring2.rotation.set(t * 3, t * 2, 0); gring.rotation.set(Math.PI / 2, 0, t * 4);
    // beam: fixed source above the module, through the lens centre, onto the spot
    const vis = clamp((t - 1.2) / 0.4);
    M.updateMatrixWorld(true);
    lens.getWorldPosition(pB); pB.y += 0.25; spot.getWorldPosition(pC);
    const baseX = M.position.x; pA.set(baseX, pB.y + 2.2, M.position.z);
    place(beamA, pA, pB); place(beamB, pB, pC); beamMat.opacity = 0.85 * vis; beamA.visible = beamB.visible = vis > 0.01;
  });

  S.cameraPath([
    { at: 0, pos: [11, 11.5, 16.5], look: [0, 0.6, -0.8] },
    { at: "line:0:end", pos: [6.8, 8.4, 7.6], look: [-0.75, 1.5, -2.3], ease: "power2.inOut" },
    { at: "word:gyroscope", pos: [6.3, 7.6, 6.8], look: [-0.45, 1.3, -2.0] },
    { at: "word:magnets", pos: [5.9, 7.4, 6.0], look: [-0.65, 1.5, -2.35] },
    { at: "line:3:end+0.2", pos: [5.5, 7.0, 5.4], look: [-0.7, 1.6, -2.4] },
    { at: "end", pos: [8.2, 8.0, 9.6], look: [-0.5, 3.3, -1.9], ease: "power1.inOut" },
  ]);

  S.label({ anchor: springAnchor, title: "Springs", sub: "hold the lens", at: "word:springs", until: "word:gyroscope", dx: 150, dy: -170, color: C.orange });
  S.label({ anchor: spotAnchor, title: "Blur", sub: "light smears on the sensor", at: "word:shakes+0.2", until: "word:magnets+0.3", dx: -150, dy: 210, color: C.red });
  S.label({ anchor: gyro, title: "Gyroscope", sub: "senses the shake", at: "word:gyroscope", until: "line:3:end", dx: 190, dy: -150, color: C.green });
  S.label({ anchor: magL, title: "Magnets + coils", sub: "push the lens back", at: "word:magnets", until: "line:3:end+0.3", dx: -160, dy: -190, color: C.blue });
  S.label({ anchor: spotAnchor, title: "Sharp", sub: "same spot, every frame", at: "word:magnets+0.6", until: "end", dx: -150, dy: 210, color: C.green });
}
