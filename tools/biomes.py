"""Hver side av Bastion får sitt eget landskap (10. okt 2026). Brukes etter bastion.py.

Rune (10. okt): trærne på høyre side (øst) skal være grønnere, havet ligger mot vest, og sør er
det guddommelige og himmelske (hvite skyer). Nord beholder dagens utseende (det skifter med verdenen).

- Øst, Grønnlund: gress, skog (furu og løvtrær), grønne åser, enger med blomster, en tjern, ildfluer.
- Sør, Lysheim: hvit marmor med gullinnlegg, søyler langs slagmarken, skyhav, svevende øyer,
  lysstråler fra himmelen, en glorie over porten, gull portal.
- Vest, Havbryn: havet. Sandstrand innenfor muren, en landtunge ut til portalen som står på en
  klippeøy, brygger, båter som gynger, bølger som ruller inn, fyrtårn med lysstråle.

Bare utseende: ingen tall i kampen er endret.
"""
from patch import sub

BIOMES = r"""
  // ---------- Landskap per side (biomes.py) ----------
  // Øst Grønnlund (skog), sør Lysheim (himmelsk), vest Havbryn (hav). Nord beholder verdenens utseende.
  const biomeAnims = [];
  const BM = (c, e, o) => M(c, Object.assign({ roughness: 0.9, emissive: e || 0x000000 }, o || {}));
  const glowMat = (c, op) => new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: op, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide });
  const SIDE_LOOK = [
    {},
    { wall: BM(0x3c4838), wallTop: BM(0x4b5a45), floor: BM(0x34392c, 0, { roughness: 1 }), house: BM(0x4a3e2e), roof: BM(0x2f4a2a) },
    { wall: BM(0xcfc9ba, 0x2a2720), wallTop: BM(0xc9a24e, 0x3a2a08, { metalness: 0.6, roughness: 0.4 }), floor: BM(0x8c887a, 0x1c1a14, { roughness: 1 }),
      house: BM(0xd8d2c2, 0x24221c), roof: BM(0xc9a24e, 0x2a1e06, { metalness: 0.5, roughness: 0.45 }),
      portal: M(0x3a2a08, { emissive: 0xffd27a, emissiveIntensity: 1.6 }),
      portalVoid: new THREE.MeshBasicMaterial({ color: 0xfff1cf, transparent: true, opacity: 0.75, side: THREE.DoubleSide }), rock: BM(0xd8d2c2, 0x2a2720) },
    { wall: BM(0x46505a), wallTop: BM(0x58646e), floor: BM(0x3e3b34, 0, { roughness: 1 }), house: BM(0x55565a), roof: BM(0x2a3e52), rock: BM(0x34383e) },
  ];
  // Mange like ting tegnes i én omgang (InstancedMesh), så telefonen holder følge.
  // Hvert punkt: [x, y, z, skala (tall eller [x, y, z]), rotasjon y].
  const _o = new THREE.Object3D();
  function inst(g, geo, mat, list, colors) {
    const im = new THREE.InstancedMesh(geo, mat, Math.max(1, list.length));
    list.forEach((p, i) => {
      _o.position.set(p[0], p[1], p[2]); _o.rotation.set(0, p[4] || 0, 0);
      if (Array.isArray(p[3])) _o.scale.set(p[3][0], p[3][1], p[3][2]); else _o.scale.setScalar(p[3]);
      _o.updateMatrix(); im.setMatrixAt(i, _o.matrix);
      if (colors) im.setColorAt(i, colors[i % colors.length]);
    });
    if (!list.length) im.visible = false;
    im.castShadow = false; im.receiveShadow = true; g.add(im); return im;
  }
  // Et tilfeldig sted på sidens eget land: utenfor muren, mellom diagonalene, ikke på slagmarken.
  function landSpot(clearX, zMax) {
    for (let k = 0; k < 60; k++) {
      const z = -50 + rnd() * ((zMax == null ? 12 : zMax) + 50), lim = Math.min(96, MAP.flameZ - z - 2), x = (rnd() * 2 - 1) * lim;
      if (Math.abs(x) < clearX && z > -34) continue;
      return { x, z };
    }
    return null;
  }
  // Bakken for sidens land: trapes fra muren ut til kanten, mellom de to diagonalene.
  function wedge(g, mat, y) {
    const sh = new THREE.Shape(), w = MAP.gateZ + 0.6, h = BASTION.half;
    [[-h, w], [h, w], [100, MAP.flameZ - 100], [-100, MAP.flameZ - 100]].forEach(([x, z], i) => i ? sh.lineTo(x, -z) : sh.moveTo(x, -z));
    return flatIn(g, new THREE.ShapeGeometry(sh), mat, 0, y, 0);
  }
  const polyFlat = (g, pts, mat, y) => { const sh = new THREE.Shape(); pts.forEach(([x, z], i) => i ? sh.lineTo(x, -z) : sh.moveTo(x, -z)); return flatIn(g, new THREE.ShapeGeometry(sh), mat, 0, y, 0); };
  function sparkPoints(g, n, color, size, spot) {
    const pos = new Float32Array(n * 3), base = [];
    for (let i = 0; i < n; i++) { const p = spot(i); base.push(p); pos.set([p[0], p[1], p[2]], i * 3); }
    const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const pts = new THREE.Points(geo, new THREE.PointsMaterial({ color, size, transparent: true, opacity: 0.9, depthWrite: false, blending: THREE.AdditiveBlending }));
    g.add(pts); return { pts, pos, base, geo };
  }

  // Øst, Grønnlund: skog, åser og enger.
  function eastBuild(g, add) {
    wedge(g, BM(0x2b4c25, 0x07140a), 0.03);
    const meadow = BM(0x3e6a30, 0x0a1a06);
    for (let i = 0; i < 14; i++) flatIn(g, new THREE.CircleGeometry(1.5 + rnd() * 4, 16), meadow, (rnd() - 0.5) * 36, 0.06 + i * 0.003, -30 + rnd() * 42);
    // Grønne åser langs slagmarken, der nord har svarte fjell.
    const hills = [];
    for (let i = 0; i < 26; i++) { const sd = i % 2 ? 1 : -1; hills.push([sd * (18.5 + rnd() * 7), -0.5, -34 + rnd() * 48, [2.6 + rnd() * 3, 1.3 + rnd() * 2.6, 2.6 + rnd() * 3], rnd() * 6]); }
    for (let i = 0; i < 18; i++) { const p = landSpot(30, -20); if (p) hills.push([p.x, -1, p.z, [5 + rnd() * 7, 2 + rnd() * 4, 5 + rnd() * 7], rnd() * 6]); }
    inst(g, new THREE.SphereGeometry(1, 12, 8), BM(0x325a2a, 0x081606), hills);
    // Skog: furu og løvtrær, tettest langt ute, en rad langs slagmarken.
    const pines = [], leafy = [];
    const plant = (x, z) => (rnd() < 0.5 ? pines : leafy).push([x, 0, z, 0.75 + rnd() * 0.9, rnd() * 6]);
    for (let i = 0; i < 46; i++) { const sd = i % 2 ? 1 : -1; plant(sd * (17 + rnd() * 9), -36 + rnd() * 48); }
    for (let i = 0; i < 190; i++) { const p = landSpot(27); if (p) plant(p.x, p.z); }
    const greens = [0x1f4a22, 0x24572a, 0x2c6a2e, 0x1a3f1f].map(c => new THREE.Color(c));
    const leaves = [0x3c7a30, 0x4a8a34, 0x5a9a3a, 0x356e2b, 0x6a9a34].map(c => new THREE.Color(c));
    const bark = BM(0x4a3524), white = c => BM(0xffffff, c);
    inst(g, new THREE.CylinderGeometry(0.15, 0.22, 1.2, 6).translate(0, 0.6, 0), bark, pines);
    inst(g, new THREE.ConeGeometry(1.4, 2.5, 7).translate(0, 2.1, 0), white(0x061206), pines, greens);
    inst(g, new THREE.ConeGeometry(1.0, 2.0, 7).translate(0, 3.4, 0), white(0x061206), pines, greens);
    inst(g, new THREE.CylinderGeometry(0.18, 0.26, 1.6, 6).translate(0, 0.8, 0), bark, leafy);
    inst(g, new THREE.IcosahedronGeometry(1.3, 0).translate(0, 2.4, 0), white(0x0a1a06), leafy, leaves);
    inst(g, new THREE.IcosahedronGeometry(0.95, 0).translate(0.7, 3.0, 0.3), white(0x0a1a06), leafy, leaves.slice(1));
    inst(g, new THREE.IcosahedronGeometry(0.85, 0).translate(-0.6, 2.9, -0.4), white(0x0a1a06), leafy, leaves.slice(2));
    // Busker langs kanten av slagmarken.
    const bushes = [];
    for (let i = 0; i < 40; i++) { const sd = i % 2 ? 1 : -1; bushes.push([sd * (14 + rnd() * 3), 0.2, -32 + rnd() * 44, [0.6 + rnd() * 0.6, 0.45 + rnd() * 0.3, 0.6 + rnd() * 0.6], rnd() * 6]); }
    inst(g, new THREE.IcosahedronGeometry(1, 0), white(0x0a1a06), bushes, leaves);
    // Tjern med nøkkeroser.
    const pond = flatIn(g, new THREE.CircleGeometry(5, 24), BM(0x16384a, 0x05182a, { roughness: 0.2, metalness: 0.3 }), -30, 0.07, -10); pond.scale.set(1.4, 1, 1);
    const pads = []; for (let i = 0; i < 9; i++) pads.push([-30 + (rnd() - 0.5) * 11, 0.09, -10 + (rnd() - 0.5) * 7, [0.5 + rnd() * 0.3, 0.05, 0.5 + rnd() * 0.3], 0]);
    inst(g, new THREE.CylinderGeometry(1, 1, 1, 10), BM(0x3e7a2e, 0x0a1a06), pads);
    // Blomster på engene og ildfluer som svever i skumringen.
    const fl = sparkPoints(g, 160, 0xffffff, 0.32, () => { const sd = rnd() < 0.5 ? 1 : -1; return [rnd() < 0.6 ? sd * (12 + rnd() * 10) : (rnd() - 0.5) * 30, 0.12, -32 + rnd() * 44]; });
    const fc = new Float32Array(160 * 3), fcol = [0xfff3a0, 0xff9ad0, 0xffffff, 0xb0c8ff].map(c => new THREE.Color(c));
    for (let i = 0; i < 160; i++) { const c = fcol[i % 4]; fc.set([c.r, c.g, c.b], i * 3); }
    fl.geo.setAttribute('color', new THREE.BufferAttribute(fc, 3)); fl.pts.material.vertexColors = true; fl.pts.material.blending = THREE.NormalBlending;
    const ff = sparkPoints(g, 80, 0xd8ff7a, 0.4, () => { const p = landSpot(15, 10) || { x: 20, z: 0 }; return [p.x, 0.6 + rnd() * 2.2, p.z, rnd() * 6]; });
    biomeAnims.push(t => {
      for (let i = 0; i < ff.base.length; i++) { const b = ff.base[i]; ff.pos[i * 3] = b[0] + Math.sin(t * 0.5 + b[3]) * 1.2; ff.pos[i * 3 + 1] = b[1] + Math.sin(t * 1.3 + b[3] * 2) * 0.5; ff.pos[i * 3 + 2] = b[2] + Math.cos(t * 0.4 + b[3]) * 1.2; }
      ff.geo.attributes.position.needsUpdate = true; ff.pts.material.opacity = 0.65 + Math.sin(t * 2.1) * 0.25;
    });
  }

  // Sør, Lysheim: hvit marmor, gull, skyer og lys fra himmelen.
  function southBuild(g, add) {
    const L = SIDE_LOOK[2], gold = BM(0xd9b25a, 0x5a3e0a, { metalness: 0.6, roughness: 0.35 });
    wedge(g, BM(0xb9b3a4, 0x1c1a14), 0.03);
    // Gullinnlegg langs slagmarken og en gullsirkel rundt portalen.
    [-1, 1].forEach(sd => flatIn(g, new THREE.PlaneGeometry(0.35, 44), gold, sd * 15.6, 0.06, -8));
    flatIn(g, new THREE.RingGeometry(7.4, 7.9, 48), gold, 0, 0.06, MAP.portalZ);
    for (let z = -20; z < 13; z += 6) flatIn(g, new THREE.PlaneGeometry(31, 0.12), BM(0x9a9484, 0x14120e), 0, 0.055, z);
    // Søyler langs slagmarken og en halvsirkel bak portalen.
    const cols = [];
    for (let z = -28; z <= 10; z += 5.5) [-1, 1].forEach(sd => cols.push([sd * 17.6, 0, z, 1, 0]));
    for (let i = 0; i < 7; i++) { const a = Math.PI * (0.1 + 0.8 * i / 6); cols.push([Math.cos(a) * 9, 0, MAP.portalZ - Math.sin(a) * 9, 0.9, 0]); }
    inst(g, new THREE.CylinderGeometry(0.55, 0.65, 6, 12).translate(0, 3.3, 0), L.wall, cols);
    inst(g, new THREE.BoxGeometry(1.7, 0.4, 1.7).translate(0, 0.2, 0), L.wall, cols);
    inst(g, new THREE.BoxGeometry(1.6, 0.5, 1.6).translate(0, 6.5, 0), gold, cols);
    // Skyhav: tre lag med skyer som driver sakte.
    const puff = new THREE.SphereGeometry(1, 12, 8), cloudMat = BM(0xf4f6fb, 0x454b5e, { roughness: 1 });
    for (let layer = 0; layer < 3; layer++) {
      const list = [];
      for (let c = 0; c < 22; c++) {
        const p = landSpot(19); if (!p) continue;
        const n = 3 + Math.floor(rnd() * 4), big = 1.6 + rnd() * 2.4;
        for (let k = 0; k < n; k++) { const s = big * (0.6 + rnd() * 0.6); list.push([p.x + (rnd() - 0.5) * big * 2.6, 0.3 + rnd() * 1.6 + layer * 0.4, p.z + (rnd() - 0.5) * big * 1.6, [s, s * 0.6, s], 0]); }
      }
      const im = inst(g, puff, cloudMat, list), ph = layer * 2.1, sp = 0.05 + layer * 0.03;
      biomeAnims.push(t => { im.position.x = Math.sin(t * sp + ph) * 2.5; im.position.z = Math.cos(t * sp * 0.7 + ph) * 1.2; });
    }
    // Høye skyer over slagmarken.
    const high = [];
    for (let c = 0; c < 10; c++) { const x = (rnd() - 0.5) * 120, z = -48 + rnd() * 40, n = 4 + Math.floor(rnd() * 3); for (let k = 0; k < n; k++) { const s = 2.5 + rnd() * 2.5; high.push([x + (rnd() - 0.5) * 10, 16 + rnd() * 6, z + (rnd() - 0.5) * 5, [s, s * 0.5, s], 0]); } }
    const hi = inst(g, puff, cloudMat, high); biomeAnims.push(t => { hi.position.x = Math.sin(t * 0.03) * 6; });
    // Svevende øyer med små templer.
    [[-32, -18, 9], [34, -24, 11], [0, -46, 14], [-56, -36, 12], [58, -12, 8]].forEach(([x, z, y], i) => {
      const isl = new THREE.Group(); isl.position.set(x, y, z); g.add(isl);
      const r = 3 + (i % 3);
      const base = mesh(new THREE.ConeGeometry(r, r * 1.8, 8), BM(0x8a8070, 0x1a1810), 0, -r * 0.9, 0); base.rotation.x = Math.PI; isl.add(base);
      isl.add(mesh(new THREE.CylinderGeometry(r, r, 0.4, 16), L.wall, 0, 0.2, 0));
      for (let k = 0; k < 4; k++) { const a = k / 4 * Math.PI * 2 + 0.4; isl.add(mesh(new THREE.CylinderGeometry(0.18, 0.2, 2, 8), L.wall, Math.cos(a) * r * 0.5, 1.4, Math.sin(a) * r * 0.5)); }
      const roof = mesh(new THREE.ConeGeometry(r * 0.8, 1, 4), gold, 0, 2.9, 0); roof.rotation.y = Math.PI / 4; isl.add(roof);
      biomeAnims.push(t => { isl.position.y = y + Math.sin(t * 0.6 + i * 1.7) * 0.6; isl.rotation.y = t * 0.03 * (i % 2 ? 1 : -1); });
    });
    // Lysstråler fra himmelen.
    const rayMat = glowMat(0xfff0c8, 0.09);
    [[-24, -12], [26, -30], [-8, -40], [44, -42], [-48, -22], [10, 4]].forEach(([x, z], i) => {
      const ray = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 3.2, 44, 16, 1, true), rayMat); ray.position.set(x, 22, z); ray.rotation.z = 0.12; g.add(ray);
    });
    biomeAnims.push(t => { rayMat.opacity = 0.075 + Math.sin(t * 0.8) * 0.03; });
    // Glorie over porten.
    const halo = mesh(new THREE.TorusGeometry(4.2, 0.16, 8, 48), BM(0xffe2a0, 0xffc860), 0, 9.5, MAP.gateZ + 0.6); halo.rotation.x = Math.PI / 2; halo.castShadow = false; g.add(halo);
    biomeAnims.push(t => { halo.position.y = 9.5 + Math.sin(t * 1.1) * 0.25; });
    // Gullstøv som stiger sakte.
    const dust = sparkPoints(g, 120, 0xffe3a0, 0.3, () => { const p = landSpot(4, 12) || { x: 0, z: 0 }; return [p.x, rnd() * 8, p.z]; });
    biomeAnims.push((t, dt) => {
      for (let i = 0; i < dust.base.length; i++) { let y = dust.pos[i * 3 + 1] + dt * 0.6; if (y > 9) y = 0; dust.pos[i * 3 + 1] = y; }
      dust.geo.attributes.position.needsUpdate = true;
    });
  }

  // Vest, Havbryn: havet, en landtunge ut til portalen, brygger, båter og fyrtårn.
  function westBuild(g, add) {
    const L = SIDE_LOOK[3];
    const water = BM(0x0f3550, 0x062238, { roughness: 0.25, metalness: 0.35 });
    wedge(g, water, 0.03);
    biomeAnims.push(t => { water.emissiveIntensity = 0.85 + Math.sin(t * 0.9) * 0.15; });
    // Strand innenfor muren og en landtunge ut til klippeøya med portalen.
    const wz = MAP.gateZ + 0.6, R = 15.5, pz = MAP.portalZ - 1, right = [], island = [];
    for (let z = 6; z >= -14; z -= 4) right.push([17 + rnd() * 2.5 + (z > 2 ? (z - 2) * 3 : 0), z]);
    for (let a = -0.35; a <= Math.PI + 0.36; a += 0.22) island.push([Math.cos(a) * R * (0.94 + rnd() * 0.12), pz - Math.sin(a) * R * (0.94 + rnd() * 0.12)]);
    const left = right.map(([x, z]) => [-x - rnd() * 1.5, z]).reverse();
    const shore = [[42, 9], ...right, ...island, ...left, [-42, 9]];
    const out = (p, k) => { const [x, z] = p, isl = z < -14; if (isl) { const dx = x, dz = z - pz, d = Math.hypot(dx, dz) || 1; return [x + dx / d * k, z + dz / d * k]; } return [x + Math.sign(x) * k, z - (Math.abs(x) > 30 ? k : 0)]; };
    const foamMat = glowMat(0xdff4ff, 0.3);
    polyFlat(g, [[-BASTION.half, wz], [BASTION.half, wz], ...shore.map(p => out(p, 1.4))], foamMat, 0.045);
    polyFlat(g, [[-BASTION.half, wz], [BASTION.half, wz], ...shore], BM(0x7d6c4e, 0x1a140a), 0.06);
    biomeAnims.push(t => { foamMat.opacity = 0.22 + Math.sin(t * 1.6) * 0.12; });
    // Klipper langs kanten av øya og steiner i vannet.
    const stones = [];
    island.forEach(([x, z], i) => { if (i % 2) return; const p = out([x, z], 0.4); stones.push([p[0], 0.2, p[1], [1 + rnd() * 1.4, 0.8 + rnd() * 1.6, 1 + rnd() * 1.4], rnd() * 6]); });
    for (let i = 0; i < 26; i++) { const p = landSpot(30); if (p) stones.push([p.x, -0.2, p.z, [0.8 + rnd() * 2, 0.6 + rnd() * 1.6, 0.8 + rnd() * 2], rnd() * 6]); }
    for (let i = 0; i < 12; i++) { const sd = i % 2 ? 1 : -1; stones.push([sd * (18 + rnd() * 3), 0.1, -12 + rnd() * 16, [0.8 + rnd(), 0.5 + rnd(), 0.8 + rnd()], rnd() * 6]); }
    inst(g, new THREE.DodecahedronGeometry(1, 0), L.rock, stones);
    // Brygger fra stranda.
    const plank = BM(0x5a4230);
    [-27, 27].forEach(x => {
      add(new THREE.BoxGeometry(1.8, 0.15, 11), plank, x, 0.45, 3);
      for (let z = -2; z <= 8; z += 2.5) [-0.8, 0.8].forEach(dx => add(new THREE.CylinderGeometry(0.1, 0.1, 1.2, 6), plank, x + dx, 0.1, z));
    });
    // Båter som gynger på bølgene.
    const hull = BM(0x4a3020), sail = BM(0xe8e2d0, 0x2a2822, { side: THREE.DoubleSide });
    [[-27, -5, 0.4], [31, -4, -0.3], [-44, -30, 1.2], [40, -38, 2.4], [-62, -8, 0.9], [66, -22, -1.1]].forEach(([x, z, ry], i) => {
      const b = new THREE.Group(); b.position.set(x, 0.1, z); b.rotation.y = ry; g.add(b);
      b.add(mesh(new THREE.BoxGeometry(1.3, 0.6, 3.4), hull, 0, 0.2, 0));
      const bow = mesh(new THREE.ConeGeometry(0.65, 1.2, 4), hull, 0, 0.2, -2.2); bow.rotation.x = -Math.PI / 2; bow.rotation.y = Math.PI / 4; bow.scale.set(1, 1, 0.45); b.add(bow);
      b.add(mesh(new THREE.CylinderGeometry(0.06, 0.06, 3.2, 6), hull, 0, 2, 0));
      const sh = new THREE.Shape(); sh.moveTo(0, 0); sh.lineTo(0, 2.6); sh.lineTo(1.6, 0); sh.lineTo(0, 0);
      const s = new THREE.Mesh(new THREE.ShapeGeometry(sh), sail); s.position.set(0, 0.6, 0.1); s.rotation.y = Math.PI / 2; b.add(s);
      biomeAnims.push(t => { b.position.y = 0.1 + Math.sin(t * 1.2 + i) * 0.12; b.rotation.z = Math.sin(t * 0.9 + i * 2) * 0.06; b.rotation.x = Math.cos(t * 0.8 + i) * 0.04; });
    });
    // Bølger som ruller inn mot land.
    const waveMat = new THREE.MeshBasicMaterial({ color: 0xdff4ff, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide });
    for (let i = 0; i < 14; i++) {
      const sd = i % 2 ? 1 : -1, x = sd * (26 + rnd() * 50), z1 = Math.min(5, MAP.flameZ - Math.abs(x) - 8), z0 = -50, ph = rnd(), m = waveMat.clone();
      const w = flatIn(g, new THREE.PlaneGeometry(7 + rnd() * 6, 0.35), m, x, 0.05, z0);
      biomeAnims.push(t => { const k = (t * 0.05 + ph) % 1; w.position.z = z0 + (z1 - z0) * k; m.opacity = Math.sin(k * Math.PI) * 0.4; });
    }
    // Fyrtårn på en klippe ute i vannet, med lys som sveiper over havet.
    const lh = new THREE.Group(); lh.position.set(-36, 0, -16); g.add(lh);
    lh.add(mesh(new THREE.CylinderGeometry(3, 4, 1.6, 10), L.rock, 0, 0.6, 0));
    lh.add(mesh(new THREE.CylinderGeometry(0.9, 1.3, 9, 12), BM(0xe8e4dc, 0x1a1a1a), 0, 6, 0));
    [3.5, 7].forEach(y => lh.add(mesh(new THREE.CylinderGeometry(1.05 - y * 0.03, 1.12 - y * 0.03, 1, 12), BM(0x9a2a22), 0, y, 0)));
    lh.add(mesh(new THREE.CylinderGeometry(0.75, 0.75, 1.1, 10), BM(0x3a2a0a, 0xffd27a), 0, 11, 0));
    lh.add(mesh(new THREE.ConeGeometry(1.1, 1.2, 10), mats.iron, 0, 12.2, 0));
    const beam = new THREE.Group(); beam.position.y = 11; lh.add(beam);
    const cone = new THREE.Mesh(new THREE.ConeGeometry(2.6, 22, 16, 1, true).translate(0, -11, 0), glowMat(0xfff0b0, 0.12)); cone.rotation.z = Math.PI / 2 + 0.08; beam.add(cone);
    biomeAnims.push(t => { beam.rotation.y = t * 0.7; });
  }
  const BIOME_BUILD = [null, eastBuild, southBuild, westBuild];
  const sidePortals = [];
  function animateBiomes(t, dt) {
    if (reduceMotion) return;
    biomeAnims.forEach(f => f(t, dt));
    sidePortals.forEach(([r, v], i) => { r.rotation.z = t * 0.4 + i; v.rotation.z = -t * 0.7; });
  }
"""


def apply(s):
    # Navn på landene og havblått banner for vest.
    s = sub(s, "{ key: 'ost', name: 'Øst', rot: -Math.PI / 2, color: 0x2f6a3a },", "{ key: 'ost', name: 'Øst', land: 'Grønnlund', rot: -Math.PI / 2, color: 0x2f6a3a },")
    s = sub(s, "{ key: 'sor', name: 'Sør', rot: Math.PI, color: 0x8a6a1f },", "{ key: 'sor', name: 'Sør', land: 'Lysheim', rot: Math.PI, color: 0xc9a24e },")
    s = sub(s, "{ key: 'vest', name: 'Vest', rot: Math.PI / 2, color: 0x7a2a24 },", "{ key: 'vest', name: 'Vest', land: 'Havbryn', rot: Math.PI / 2, color: 0x1f6a7a },")
    s = sub(s, "text: i ? `${sd.name} · ledig plass` : `${sd.name} · deg`", "text: i ? `${sd.name} · ${sd.land} · ledig plass` : `${sd.name} · deg`")

    s = sub(s, "  function sideKit(si) {\n", BIOMES.lstrip('\n') + "  function sideKit(si) {\n")
    # Slagmarken: landskapet kommer fra BIOME_BUILD i stedet for svarte fjell og snø.
    s = sub(s, "      // Slagmark: fjell på sidene, snøflekker, portalen.\n"
               "      for (let i = 0; i < 30; i++) { const sd = i % 2 ? 1 : -1, h = 2 + rnd() * 6; add(new THREE.ConeGeometry(1.4 + rnd() * 2.2, h, 6), mats.rock, sd * (16.5 + rnd() * 6), h / 2 - 0.2, -34 + rnd() * 48).rotation.y = rnd() * 6; }\n"
               "      for (let i = 0; i < 10; i++) flatIn(g, new THREE.CircleGeometry(1.5 + rnd() * 4, 16), mats.snow, (rnd() - 0.5) * 40, 0.01 + i * 0.0005, -30 + rnd() * 42);\n"
               "      const ring = add(new THREE.TorusGeometry(3.3, 0.38, 12, 48), mats.portal, 0, 3.6, MAP.portalZ);\n"
               "      const vd = new THREE.Mesh(new THREE.CircleGeometry(3.0, 40), mats.portalVoid); vd.position.set(0, 3.6, MAP.portalZ); g.add(vd);\n"
               "      for (let i = 0; i < 6; i++) { const a = (i / 6) * Math.PI * 2; add(new THREE.ConeGeometry(0.35, 2.4 + (i % 3), 4), mats.rock,",
               "      // Slagmark: hver side har sitt eget landskap (biomes.py), så portalen.\n"
               "      BIOME_BUILD[si](g, add);\n"
               "      const ring = add(new THREE.TorusGeometry(3.3, 0.38, 12, 48), LOOK.portal || mats.portal, 0, 3.6, MAP.portalZ);\n"
               "      const vd = new THREE.Mesh(new THREE.CircleGeometry(3.0, 40), LOOK.portalVoid || mats.portalVoid); vd.position.set(0, 3.6, MAP.portalZ); g.add(vd);\n"
               "      sidePortals.push([ring, vd]);\n"
               "      for (let i = 0; i < 6; i++) { const a = (i / 6) * Math.PI * 2; add(new THREE.ConeGeometry(0.35, 2.4 + (i % 3), 4), LOOK.rock || mats.rock,")
    # Murene og distriktet i sidens egne farger (nord uendret).
    i = s.index("  function sideKit(si) {\n"); j = s.index("  const sideKits = SIDES.map", i)
    body = s[i:j]
    body = body.replace("mats.wall, ", "wm, ").replace("mats.wallTop, ", "wtm, ")
    body = sub(body, "flatIn(g, new THREE.ShapeGeometry(sh), distFloor, 0, 0.012, 0);", "flatIn(g, new THREE.ShapeGeometry(sh), LOOK.floor || distFloor, 0, 0.012, 0);")
    body = sub(body, "add(new THREE.BoxGeometry(w, h, 2.2), oldWall,", "add(new THREE.BoxGeometry(w, h, 2.2), LOOK.house || oldWall,")
    body = sub(body, "add(new THREE.ConeGeometry(w * 0.8, 1.2, 4), oldRoof,", "add(new THREE.ConeGeometry(w * 0.8, 1.2, 4), LOOK.roof || oldRoof,")
    body = body.replace("  function sideKit(si) {\n", "  function sideKit(si) {\n    const LOOK = SIDE_LOOK[si], wm = LOOK.wall || mats.wall, wtm = LOOK.wallTop || mats.wallTop;\n", 1)
    s = s[:i] + body + s[j:]
    # Skiltene over sideportene holdes innenfor skjermen (telefon).
    s = sub(s, "      if (vis) L.el.style.transform = `translate(${(lv.x + 1) / 2 * rect.width}px, ${(1 - lv.y) / 2 * rect.height}px) translate(-50%, -100%)`;",
               "      let px = (lv.x + 1) / 2 * rect.width;\n"
               "      if (vis && L.side) { const hw = L.el.offsetWidth / 2 + 4; px = Math.max(hw, Math.min(rect.width - hw, px)); }\n"
               "      if (vis) L.el.style.transform = `translate(${px}px, ${(1 - lv.y) / 2 * rect.height}px) translate(-50%, -100%)`;")
    # Vind, bølger, skyer og ildfluer beveger seg.
    s = sub(s, "    animateVillage(now / 1000, dt);\n", "    animateVillage(now / 1000, dt);\n    animateBiomes(now / 1000, dt);\n")
    return s
