"""Landsbyen etter Runes konseptbilde (11. okt 2026, versjon 29).

Bildet: porten øverst, en lys steinvei med fakler og blå bannere ned mot citadellet,
Longhouse og Barracks til venstre for veien, Forge og Workshop til høyre, og de fem
ressursene langs kanten (gull og tømmer til venstre; jern, stein og kull til høyre).

- Jern og stein bytter plass, så rekkefølgen følger bildet.
- Hus med gavltak, dør og lyse vinduer; gruver med kran, vogner, skinner og stokker;
  belagte plasser under bygningene; fakler med bannere langs veien; røyk fra smia.
- Alt legges i `village`, så sideKit kopierer det til øst, sør og vest. Der får kopien
  sidens farger (VSTYLE) og sidens egne navn på bygningene (SIDE_NAMES).
- Kameraet snur seg etter siden: din side er alltid opp (porten øverst). «Se fra» i
  Landsby-fanen viser landsbyen på hver side slik spilleren der vil se den.
- Større navneskilt med ikon, lesbare på telefon.

Bare utseende og kamera; kampen og balansen er uendret.
"""
from patch import sub


HOUSE_OLD = r"""  function house(x, z, w, d, h, roofMat, bodyMat) {
    const g = new THREE.Group();
    g.add(mesh(new THREE.BoxGeometry(w, h, d), bodyMat || vm.plank, 0, h / 2, 0));
    const roof = mesh(new THREE.ConeGeometry(Math.max(w, d) * 0.75, h * 0.8, 4), roofMat || vm.roof, 0, h + h * 0.4, 0);
    roof.rotation.y = Math.PI / 4; roof.scale.set(w / Math.max(w, d), 1, d / Math.max(w, d));
    g.add(roof); g.position.set(x, 0, z);
    return g;
  }
"""

HOUSE_NEW = r"""  // Materialer som får sidens farge i kopiene (village.py): vkey sier hvilken rolle de har.
  const vtag = (m, k) => { m.userData.vkey = k; return m; };
  vtag(vm.plank, 'plank'); vtag(vm.roof, 'roof'); vtag(vm.banner, 'banner'); vtag(vm.leaf, 'leaf'); vtag(vm.timber, 'wood');
  vm.banner.color.setHex(0x22325a);   // Nord: mørkeblå bannere som på bildet
  const VD = {
    pave: vtag(M(0x887f70, { roughness: 0.95 }), 'pave'), seam: vtag(M(0x5e574d, { roughness: 1 }), 'seam'),
    wood: vtag(M(0x5e4430, { roughness: 0.9 }), 'wood'), woodDark: vtag(M(0x3a291c), 'wood'),
    emblem: vtag(M(0xd9c79a, { roughness: 0.6, emissive: 0x2a2010 }), 'emblem'),
    fire: vtag(new THREE.MeshBasicMaterial({ color: 0xffa23a }), 'fire'), fireCore: new THREE.MeshBasicMaterial({ color: 0xfff0c0 }),
    glow: vtag(new THREE.MeshBasicMaterial({ color: 0xff9a3a, transparent: true, opacity: 0.16, depthWrite: false, blending: THREE.AdditiveBlending }), 'fire'),
    window: vtag(M(0x2a1606, { emissive: 0xffa94a, emissiveIntensity: 1.3 }), 'window'), dark: M(0x0b0908, { roughness: 1 }),
    tarp: vtag(M(0x2e4c78, { side: THREE.DoubleSide }), 'tarp'), canvas: vtag(M(0xd8d0bc, { side: THREE.DoubleSide }), 'canvas'),
    smoke: new THREE.MeshBasicMaterial({ color: 0x8e8c88, transparent: true, opacity: 0.32, depthWrite: false }),
    rail: M(0x3a3a3e, { metalness: 0.5, roughness: 0.5 }), block: vtag(M(0xc9c6bf, { roughness: 0.85 }), 'block'),
    ore: vtag(M(0x5d6470, { roughness: 0.8 }), 'ore'), oreDark: M(0x3c4049, { roughness: 0.8 }), chimney: vtag(M(0x5a5650, { roughness: 0.95 }), 'stone'),
  };
  // Mange små deler slås sammen til én mesh per materiale, så telefonen holder følge (færre tegnekall).
  // Det som beveger seg (røyk, hjul, bannere) holdes utenfor.
  function mergeGroup(root) {
    root.updateMatrixWorld(true);
    const inv = new THREE.Matrix4().copy(root.matrixWorld).invert(), buckets = new Map(), used = [];
    root.traverse(o => {
      if (!o.isMesh || o.isInstancedMesh) return;
      for (let p = o; p && p !== root; p = p.parent) if (p.userData.smoke != null || p.userData.spin || p.userData.wave) return;
      const key = o.material.uuid + (o.castShadow ? '+' : '-');
      if (!buckets.has(key)) buckets.set(key, { mat: o.material, cast: o.castShadow, list: [] });
      buckets.get(key).list.push(o); used.push(o);
    });
    const mtx = new THREE.Matrix4();
    buckets.forEach(b => {
      if (b.list.length < 2) return;
      const pos = [], nor = [];
      b.list.forEach(o => {
        const geo = (o.geometry.index ? o.geometry.toNonIndexed() : o.geometry.clone());
        geo.applyMatrix4(mtx.multiplyMatrices(inv, o.matrixWorld));
        pos.push(geo.attributes.position.array); nor.push(geo.attributes.normal.array);
        o.parent.remove(o);
      });
      const cat = arrs => { const n = arrs.reduce((a, x) => a + x.length, 0), out = new Float32Array(n); let k = 0; arrs.forEach(x => { out.set(x, k); k += x.length; }); return out; };
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(cat(pos), 3)); geo.setAttribute('normal', new THREE.BufferAttribute(cat(nor), 3));
      const m = new THREE.Mesh(geo, b.mat); m.castShadow = b.cast; m.receiveShadow = true; root.add(m);
    });
    return root;
  }
  // Gavltak: en trekant i x-retning, strukket langs z.
  function gable(span, h, len, mat) {
    const sh = new THREE.Shape(); sh.moveTo(-span / 2, 0); sh.lineTo(span / 2, 0); sh.lineTo(0, h); sh.lineTo(-span / 2, 0);
    const geo = new THREE.ExtrudeGeometry(sh, { depth: len, bevelEnabled: false }); geo.translate(0, 0, -len / 2);
    return mesh(geo, mat);
  }
  // Hus som på bildet: gavltak med utstikk langs den lengste siden, dør og lyse vinduer mot kameraet (+z).
  function house(x, z, w, d, h, roofMat, bodyMat) {
    const g = new THREE.Group(), long = d > w;
    g.add(mesh(new THREE.BoxGeometry(w, h, d), bodyMat || vm.plank, 0, h / 2, 0));
    const roof = gable((long ? w : d) + 0.5, h * 0.8, (long ? d : w) + 0.4, roofMat || vm.roof);
    roof.position.y = h; if (!long) roof.rotation.y = Math.PI / 2; g.add(roof);
    g.add(mesh(new THREE.BoxGeometry(w + 0.08, 0.14, d + 0.08), VD.woodDark, 0, 0.07, 0));
    g.add(mesh(new THREE.BoxGeometry(Math.min(0.7, w * 0.22), h * 0.62, 0.06), VD.woodDark, 0, h * 0.31, d / 2 + 0.03));
    [-1, 1].forEach(sd => g.add(mesh(new THREE.BoxGeometry(0.34, 0.3, 0.05), VD.window, sd * w * 0.3, h * 0.58, d / 2 + 0.03)));
    g.position.set(x, 0, z);
    return g;
  }
"""

NODE_OLD_START = "  function nodeModel(k) {\n"
NODE_OLD_END = "    return g;\n  }\n  const nodeVis = {};\n"

NODE_NEW = r"""  // Ressursene som på bildet: gullhaug med kran, tømmerleir med stokker og telt, jerngruve og kullgruve
  // med inngang, skinner og vogner, steinbrudd med blokker og løftekran. Gjerde mot veien.
  function nodeModel(k) {
    const g = new THREE.Group(), add = (geo, mat, x, y, z) => { const m = mesh(geo, mat, x, y, z); g.add(m); return m; };
    const fence = (x0, z0, x1, z1) => {
      const len = Math.hypot(x1 - x0, z1 - z0), a = Math.atan2(x1 - x0, z1 - z0), n = Math.max(2, Math.round(len / 1.1));
      for (let i = 0; i <= n; i++) add(new THREE.BoxGeometry(0.1, 0.6, 0.1), VD.wood, x0 + (x1 - x0) * i / n, 0.3, z0 + (z1 - z0) * i / n);
      [0.22, 0.46].forEach(y => { const r = add(new THREE.BoxGeometry(0.05, 0.06, len), VD.wood, (x0 + x1) / 2, y, (z0 + z1) / 2); r.rotation.y = a; });
    };
    const mine = (x, z) => {   // gruveinngang: to stolper, overligger og mørk åpning, skinner ut
      add(new THREE.BoxGeometry(1.1, 1.0, 0.3), VD.dark, x, 0.5, z);
      [-1, 1].forEach(sd => add(new THREE.BoxGeometry(0.16, 1.2, 0.16), VD.wood, x + sd * 0.62, 0.6, z + 0.12));
      add(new THREE.BoxGeometry(1.5, 0.18, 0.2), VD.wood, x, 1.24, z + 0.12);
      [-1, 1].forEach(sd => add(new THREE.BoxGeometry(0.05, 0.04, 2.2), VD.rail, x + sd * 0.3, 0.03, z + 1.3));
    };
    const cart = (x, z, mat) => {
      add(new THREE.BoxGeometry(0.7, 0.4, 0.9), VD.woodDark, x, 0.36, z);
      add(new THREE.DodecahedronGeometry(0.3), mat, x, 0.6, z).scale.set(1, 0.6, 1.2);
      [-1, 1].forEach(sd => add(new THREE.CylinderGeometry(0.13, 0.13, 0.06, 8), VD.rail, x + sd * 0.36, 0.14, z).rotation.z = Math.PI / 2);
    };
    if (k === 'gold') {
      add(new THREE.DodecahedronGeometry(1.3), mats.rock, 0.2, 0.6, -0.4).scale.set(1.3, 0.85, 1);
      for (let i = 0; i < 7; i++) add(new THREE.OctahedronGeometry(0.22 + (i % 3) * 0.08), vm.gold, Math.cos(i * 1.1) * 1.0, 0.75 + (i % 2) * 0.45, -0.3 + Math.sin(i * 1.1) * 0.6);
      add(new THREE.ConeGeometry(0.8, 0.5, 9), vm.gold, 0.9, 0.25, 0.9);
      // Løftekran av tre.
      [-1, 1].forEach(sd => add(new THREE.BoxGeometry(0.12, 2.6, 0.12), VD.wood, -1.5 + sd * 0.4, 1.25, -0.6).rotation.z = sd * 0.16);
      add(new THREE.BoxGeometry(0.12, 0.12, 2.2), VD.wood, -1.5, 2.45, 0.1);
      add(new THREE.BoxGeometry(0.03, 1.2, 0.03), VD.rail, -1.5, 1.8, 1.1);
      add(new THREE.BoxGeometry(0.4, 0.3, 0.4), VD.woodDark, -1.5, 1.1, 1.1);
      add(new THREE.BoxGeometry(0.5, 0.4, 0.5), vm.crate, -0.6, 0.2, 1.3);
      fence(-2.2, 2.0, 1.8, 2.0);
    }
    if (k === 'timber') {
      for (let i = 0; i < 5; i++) {
        const t = new THREE.Group(), s = 0.85 + (i % 3) * 0.2;
        t.add(mesh(new THREE.CylinderGeometry(0.12, 0.17, 1.0, 6), vm.timber, 0, 0.5, 0), mesh(new THREE.ConeGeometry(0.85, 1.6, 7), vm.leaf, 0, 1.6, 0), mesh(new THREE.ConeGeometry(0.62, 1.3, 7), vm.leaf, 0, 2.4, 0));
        t.scale.setScalar(s); t.position.set(-1.6 + Math.cos(i * 1.9) * 1.1, 0, -1.0 + Math.sin(i * 1.9) * 0.9); g.add(t);
      }
      // Stokker i en stabel, et telt og en kubbe med øks.
      for (let i = 0; i < 6; i++) { const r = i < 3 ? 0 : i < 5 ? 1 : 2, c = i < 3 ? i : i < 5 ? i - 3 : 0; add(new THREE.CylinderGeometry(0.17, 0.17, 1.8, 7), vm.timber, 1.0, 0.18 + r * 0.31, 0.7 + (c - (r === 0 ? 1 : r === 1 ? 0.5 : 0)) * 0.36).rotation.z = Math.PI / 2; }
      const tent = gable(1.4, 0.95, 1.3, VD.canvas); tent.position.set(-0.4, 0, 1.4); g.add(tent);
      add(new THREE.CylinderGeometry(0.24, 0.26, 0.4, 8), vm.timber, 1.9, 0.2, -0.6);
      fence(-2.0, 2.3, 2.0, 2.3);
    }
    if (k === 'iron') {
      add(new THREE.DodecahedronGeometry(1.4), VD.ore, 0, 0.75, -0.9).scale.set(1.35, 0.95, 1);
      add(new THREE.DodecahedronGeometry(0.8), VD.oreDark, 1.3, 0.45, -0.3);
      mine(-0.3, 0.2);
      cart(-0.3, 1.8, VD.oreDark);
      for (let i = 0; i < 4; i++) add(new THREE.DodecahedronGeometry(0.22), VD.oreDark, 1.1 + (i % 2) * 0.35, 0.18, 1.0 + Math.floor(i / 2) * 0.35);
      fence(1.6, 2.4, 1.6, -0.4);
    }
    if (k === 'stone') {
      for (let i = 0; i < 9; i++) { const h = 0.5 + (i % 3) * 0.28; add(new THREE.BoxGeometry(0.75, h, 0.75), VD.block, (i % 3 - 1) * 0.85 - 0.3, h / 2, Math.floor(i / 3) * 0.85 - 1.0).rotation.y = (i % 2) * 0.12; }
      add(new THREE.BoxGeometry(0.7, 0.55, 0.7), VD.block, -0.1, 1.05, -0.6);
      // Løftekran: stolpe, bom og tau.
      add(new THREE.BoxGeometry(0.16, 2.8, 0.16), VD.wood, 1.5, 1.4, 0.6);
      const boom = add(new THREE.BoxGeometry(0.1, 0.1, 2.4), VD.wood, 1.5, 2.5, -0.2); boom.rotation.x = 0.35;
      add(new THREE.BoxGeometry(0.03, 1.4, 0.03), VD.rail, 1.5, 2.0, -1.1);
      add(new THREE.BoxGeometry(0.5, 0.35, 0.5), VD.block, 1.5, 1.2, -1.1);
      fence(-2.0, 1.7, 2.0, 1.7);
    }
    if (k === 'coal') {
      add(new THREE.ConeGeometry(1.4, 1.2, 9), vm.coalHeap, 0.4, 0.6, -0.8);
      add(new THREE.ConeGeometry(0.85, 0.8, 8), vm.coalHeap, 1.6, 0.4, 0.3);
      mine(-0.7, -0.2);
      cart(-0.7, 1.4, vm.coalHeap); cart(0.6, 1.6, vm.coalHeap);
      fence(1.9, 2.4, 1.9, -1.2);
    }
    return mergeGroup(g);
  }
  const nodeVis = {};
"""

DECOR = r"""
  // ---------- Landsbyen etter konseptbildet (village.py) ----------
  // EMB: steder for sidens merke på bannerne [x, y, z, rotasjon y, størrelse]. Merket bygges per side i sideExtras.
  const EMB = [];
  // Lys steinvei med kantstein fra porten til citadellet, fakler med bannere, belagte plasser under
  // bygningene, bannere på muren, glødepanner ved porten, røyk fra smia og småting rundt husene.
  // Alt havner i `village`, så sideKit kopierer det til de andre sidene.
  {
    const V = new THREE.Group(), add = (geo, mat, x, y, z) => { const m = mesh(geo, mat, x, y, z); V.add(m); return m; };
    const flatV = (w, d, mat, x, z, y) => { const m = mesh(new THREE.PlaneGeometry(w, d), mat, x, y, z); m.rotation.x = -Math.PI / 2; m.castShadow = false; m.receiveShadow = true; V.add(m); return m; };
    const z0 = MAP.gateZ + 1.3, z1 = MAP.roadEnd, roadW = 5;
    flatV(roadW, z1 - z0, VD.pave, 0, (z0 + z1) / 2, 0.026);
    [-1, 1].forEach(sd => add(new THREE.BoxGeometry(0.28, 0.1, z1 - z0), VD.seam, sd * (roadW / 2 + 0.1), 0.05, (z0 + z1) / 2).castShadow = false);
    // Fuger i veien (én InstancedMesh).
    const seams = [];
    for (let z = z0 + 0.6; z < z1; z += 1.05) seams.push([0, 0.03, z]);
    for (let z = z0 + 1.1; z < z1; z += 2.1) [-1.25, 0, 1.25].forEach(x => seams.push([x + (Math.round(z) % 2) * 0.6, 0.031, z, 1]));
    const sGeo = new THREE.PlaneGeometry(1, 1); sGeo.rotateX(-Math.PI / 2);
    const sIm = new THREE.InstancedMesh(sGeo, VD.seam, seams.length), o3 = new THREE.Object3D();
    seams.forEach((p, i) => { o3.position.set(p[0], p[1], p[2]); o3.scale.set(p[3] ? 0.05 : roadW, 1, p[3] ? 1.0 : 0.05); o3.updateMatrix(); sIm.setMatrixAt(i, o3.matrix); });
    sIm.receiveShadow = true; V.add(sIm);
    // Belagte plasser under bygningene.
    [[-6, 21, 7, 7.6], [-6.2, 32.2, 7.6, 6.4], [6, 21.6, 7, 8.6], [6.6, 31.4, 7, 5.6]].forEach(([x, z, w, d]) => {
      flatV(w + 0.4, d + 0.4, VD.seam, x, z, 0.018); flatV(w, d, VD.pave, x, z, 0.022);
    });
    // Fakler langs veien: stolpe, glødepanne med ild, og et banner med sidens merke.
    const torch = (x, z, flag) => {
      add(new THREE.CylinderGeometry(0.08, 0.11, 2.3, 6), mats.iron, x, 1.15, z);
      add(new THREE.CylinderGeometry(0.3, 0.16, 0.26, 10), mats.brass, x, 2.4, z);
      const f = add(new THREE.ConeGeometry(0.2, 0.55, 8), VD.fire, x, 2.75, z); f.castShadow = false; f.userData.flick = 1;
      add(new THREE.ConeGeometry(0.1, 0.3, 6), VD.fireCore, x, 2.66, z).castShadow = false;
      const gl = add(new THREE.SphereGeometry(0.3, 10, 8), VD.glow, x, 2.7, z); gl.castShadow = false;
      if (flag) {
        const sd = Math.sign(x);
        add(new THREE.BoxGeometry(0.5, 0.05, 0.05), mats.iron, x - sd * 0.25, 2.0, z);
        add(new THREE.BoxGeometry(0.04, 1.0, 0.46), vm.banner, x - sd * 0.45, 1.45, z);
        [-1, 1].forEach(f => EMB.push([x - sd * 0.45 + f * 0.03, 1.55, z, f * Math.PI / 2, 0.36]));
      }
    };
    [18.6, 23.8, 29, 34.2].forEach((z, i) => [-1, 1].forEach(sd => torch(sd * 3.0, z, i % 2 === 0)));
    // Glødepanner ved porten og bannere på innsiden av muren.
    [-1, 1].forEach(sd => {
      add(new THREE.CylinderGeometry(0.14, 0.2, 1.1, 8), mats.iron, sd * 3.0, 0.55, 16.4);
      add(new THREE.CylinderGeometry(0.5, 0.28, 0.4, 12), mats.brass, sd * 3.0, 1.25, 16.4);
      const f = add(new THREE.ConeGeometry(0.36, 0.8, 9), VD.fire, sd * 3.0, 1.75, 16.4); f.castShadow = false; f.userData.flick = 1;
      add(new THREE.SphereGeometry(0.65, 10, 8), VD.glow, sd * 3.0, 1.7, 16.4).castShadow = false;
      [7.5, 13].forEach(x => {
        add(new THREE.BoxGeometry(1.3, 2.1, 0.05), vm.banner, sd * x, 2.0, MAP.gateZ + 1.33);
        EMB.push([sd * x, 2.2, MAP.gateZ + 1.38, 0, 0.8]);
        add(new THREE.BoxGeometry(1.45, 0.1, 0.1), mats.brass, sd * x, 3.08, MAP.gateZ + 1.35);
      });
    });
    // Longhouse: banner over døra, benk og tønner.
    add(new THREE.BoxGeometry(0.08, 2.6, 0.08), mats.iron, -3.6, 1.3, 25.4);
    add(new THREE.BoxGeometry(0.6, 0.9, 0.04), vm.banner, -3.25, 2.1, 25.4); EMB.push([-3.25, 2.15, 25.43, 0, 0.42]);
    const barrel = (x, z) => add(new THREE.CylinderGeometry(0.26, 0.26, 0.6, 10), VD.wood, x, 0.3, z);
    barrel(-3.4, 22.2); barrel(-3.5, 21.6); barrel(8.2, 22.6); barrel(-8.9, 26.3);
    const crate = (x, z, s) => add(new THREE.BoxGeometry(s, s, s), vm.crate, x, s / 2, z);
    crate(-8.6, 18.0, 0.55); crate(8.7, 18.4, 0.5); crate(4.0, 33.6, 0.45); crate(-3.4, 18.4, 0.4);
    // Barracks: våpenstativ, telt og øvingsdukke.
    add(new THREE.BoxGeometry(1.6, 0.08, 0.08), VD.wood, -9.4, 1.0, 29.2);
    [-1, 1].forEach(sd => add(new THREE.BoxGeometry(0.08, 1.1, 0.08), VD.wood, -9.4 + sd * 0.75, 0.55, 29.2));
    for (let i = 0; i < 4; i++) add(new THREE.CylinderGeometry(0.025, 0.025, 1.8, 5), mats.steel, -9.95 + i * 0.36, 0.9, 29.3).rotation.z = 0.08;
    const tentB = gable(1.6, 1.1, 1.5, VD.canvas); tentB.position.set(-2.7, 0, 33.6); V.add(tentB);
    add(new THREE.CylinderGeometry(0.06, 0.06, 1.3, 6), VD.wood, -3.4, 0.65, 28.8);
    add(new THREE.BoxGeometry(0.6, 0.08, 0.08), VD.wood, -3.4, 1.0, 28.8);
    add(new THREE.SphereGeometry(0.18, 8, 6), VD.canvas, -3.4, 1.45, 28.8);
    // Forge: høy pipe med røyk, ambolt på kubbe.
    add(new THREE.BoxGeometry(0.95, 4.6, 0.95), VD.chimney, 7.4, 2.3, 24.0);
    add(new THREE.BoxGeometry(1.15, 0.25, 1.15), VD.chimney, 7.4, 4.65, 24.0);
    for (let i = 0; i < 5; i++) { const p = add(new THREE.SphereGeometry(0.4 + i * 0.12, 8, 6), VD.smoke, 7.4, 5.2 + i * 0.8, 24.0); p.castShadow = false; p.userData.smoke = i / 5; }
    add(new THREE.CylinderGeometry(0.28, 0.3, 0.5, 8), vm.timber, 3.3, 0.25, 26.5);
    add(new THREE.BoxGeometry(0.55, 0.22, 0.26), mats.iron, 3.3, 0.6, 26.5);
    // Workshop: blå presenning over arbeidsbenken og et vannhjul med eiker.
    const tarp = mesh(new THREE.PlaneGeometry(2.4, 1.8), VD.tarp, 3.5, 1.7, 31.8); tarp.rotation.set(-Math.PI / 2 + 0.35, 0, 0); V.add(tarp);
    [-1, 1].forEach(sd => [31.0, 32.6].forEach(z => add(new THREE.BoxGeometry(0.08, z < 32 ? 2.0 : 1.4, 0.08), VD.wood, 3.5 + sd * 1.1, z < 32 ? 1.0 : 0.7, z)));
    add(new THREE.BoxGeometry(1.6, 0.1, 0.7), VD.wood, 3.5, 0.75, 31.9);
    const wheel = new THREE.Group(); wheel.position.set(8.55, 1.0, 32.0); wheel.rotation.y = Math.PI / 2; wheel.userData.spin = 1; V.add(wheel);
    wheel.add(mesh(new THREE.TorusGeometry(0.85, 0.08, 6, 16), VD.wood));
    for (let i = 0; i < 4; i++) { const sp = mesh(new THREE.BoxGeometry(1.7, 0.08, 0.08), VD.wood); sp.rotation.z = i * Math.PI / 4; wheel.add(sp); }
    // Furu langs kanten bak tømmerleiren, som på bildet.
    for (let i = 0; i < 7; i++) {
      const t = new THREE.Group(), x = -15.6 + (i % 2) * 1.1, z = 29.5 + i * 1.1;
      t.add(mesh(new THREE.CylinderGeometry(0.12, 0.17, 1.0, 6), vm.timber, 0, 0.5, 0), mesh(new THREE.ConeGeometry(0.9, 1.8, 7), vm.leaf, 0, 1.7, 0), mesh(new THREE.ConeGeometry(0.65, 1.4, 7), vm.leaf, 0, 2.6, 0));
      t.scale.setScalar(0.9 + (i % 3) * 0.15); t.position.set(x, 0, z); V.add(t);
    }
    village.add(mergeGroup(V));
  }
  // Sidens farger på kopiene av landsbyen (øst, sør, vest). Nord beholder verdenens utseende.
  const VSTYLE = [null,
    { plank: 0x5c4630, roof: 0x3f5e2c, banner: 0x1f4a2a, leaf: 0x3d7a30, pave: 0x8a8a70, seam: 0x4a5040, wood: 0x5a4028, tarp: 0x3f6a34, canvas: 0xcfd6b4, stone: 0x5e6656, block: 0xb9bfa8, emblem: 0xe4d9a0 },
    { plank: 0xe4ddcc, roof: 0x2a3f7a, banner: 0x24346a, leaf: 0x9fae70, pave: 0xd9d1bd, seam: 0xa89a74, wood: 0xc4ac78, tarp: 0xf3ead2, canvas: 0xfff6e0, stone: 0xdcd6c8, block: 0xf0ece2, emblem: 0xe2b54a, fire: 0xffe9b0, window: 0xfff0c0 },
    { plank: 0x6a4a30, roof: 0x2b4470, banner: 0x22325a, leaf: 0x3a5a48, pave: 0xa49a84, seam: 0x5a5448, wood: 0x6a5a48, tarp: 0x2b4470, canvas: 0xe6e2d8, stone: 0x5a6670, block: 0xb4b8bc, emblem: 0xe8e2d0 },
  ];
  const vstyleCache = new Map();
  function restyleVillage(root, si) {
    const st = VSTYLE[si]; if (!st) return;
    root.traverse(o => {
      if (!o.isMesh || !o.material || !o.material.userData) return;
      const k = o.material.userData.vkey; if (!k || st[k] == null) return;
      const ck = si + ':' + o.material.uuid;
      if (!vstyleCache.has(ck)) {
        const m = o.material.clone();
        if (k === 'window') m.emissive.setHex(st[k]); else m.color.setHex(st[k]);
        if (si === 2 && k === 'emblem') { m.metalness = 0.6; m.roughness = 0.35; m.emissive = new THREE.Color(0x3a2a08); }
        vstyleCache.set(ck, m);
      }
      o.material = vstyleCache.get(ck);
    });
  }
  // Det som beveger seg i alle landsbyene: røyk, vannhjul, bannere. Samles når sidene er bygget.
  let villageMovers = null;
  function animateVillageDecor(t) {
    if (reduceMotion) return;
    if (!villageMovers) { villageMovers = []; scene.traverse(o => { if (o.userData.smoke != null || o.userData.spin || o.userData.wave) villageMovers.push(o); }); }
    VD.glow.opacity = 0.15 + Math.sin(t * 11) * 0.03 + Math.sin(t * 7.3) * 0.02;
    villageMovers.forEach((o, i) => {
      if (o.userData.smoke != null) { const k = (t * 0.18 + o.userData.smoke) % 1; o.position.y = 5.1 + k * 4.2; o.position.x = 7.4 + Math.sin(k * 3 + i) * 0.3 + k * 0.9; o.scale.setScalar(0.6 + k * 1.2); }
      else if (o.userData.spin) o.rotation.z = t * 0.8;
      else if (o.userData.wave) o.rotation.y = Math.sin(t * 1.8 + i) * 0.12;
    });
  }
"""

KITS_ANCHOR = "  // ---------- Bastion: fire sider rundt flammen ----------\n  // Hver side bygges i sine egne koordinater"

CSS_OLD = ".lbl { position: absolute; left: 0; top: 0; font-size: 11px;"
CSS_NEW = (".lbl.vl { display: flex; align-items: center; gap: 5px; font-size: 13px; padding: 3px 9px 3px 6px; background: rgba(18, 14, 10, .86); border: 1px solid rgba(226, 181, 74, .55); border-radius: 6px; box-shadow: 0 2px 6px rgba(0, 0, 0, .45); }\n"
           ".lbl.vl i { font-style: normal; font-size: 14px; line-height: 1; }\n"
           ".lbl.vl small { font-size: 11px; font-weight: 500; opacity: .75; margin-left: 2px; }\n"
           "@media (max-width: 600px) { .lbl.vl { font-size: 12px; padding: 2px 7px 2px 5px; gap: 4px; } .lbl.vl i { font-size: 12px; } }\n"
           ".vside { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin: 0 0 12px; }\n"
           ".vside > span { font-size: 12px; opacity: .75; margin-right: 2px; }\n"
           ".vside button { min-height: 34px; padding: 4px 12px; border-radius: 999px; border: 1px solid var(--line); background: transparent; color: var(--fg); font: inherit; font-size: 13px; cursor: pointer; }\n"
           ".vside button.on { border-color: #e2b54a; color: #e2b54a; }\n"
           + CSS_OLD)

LABELS_OLD = r"""    { text: 'Longhouse', x: -5.2, y: 3.6, z: 23.4 },
    ...Object.keys(NODE_POS).map(k => ({ node: k, text: NODES[k].name, x: NODE_POS[k].x, y: 2.8, z: NODE_POS[k].z })),
    { text: 'Barracks', x: -6, y: 4, z: 31 }, { text: 'Forge', x: 5.6, y: 4.2, z: 24.6 }, { text: 'Workshop', x: 6.4, y: 4, z: 31 },
"""
LABELS_NEW = r"""    // Landsbyskilt for alle fire sider, med sidens egne navn på bygningene (village.py).
    ...SIDES.flatMap((sd, si) => [
      ...VBUILD.map(b => Object.assign({ vl: true, si, icon: b.icon, text: SIDE_NAMES[si][b.key], y: b.y }, sideToWorld(si, b.x, b.z))),
      ...Object.keys(NODE_POS).map(k => Object.assign({ vl: true, si, node: si ? null : k, icon: NODE_ICON[k], text: NODES[k].name, y: 3.0 }, sideToWorld(si, NODE_POS[k].x, NODE_POS[k].z))),
    ]),
"""
NAMES = r"""  // Longhouse heter noe eget på hver side (Runes bilder 11. okt): Roothall, Sanctum, Tidehall. Resten heter det samme.
  const SIDE_NAMES = [
    { longhouse: 'Longhouse', barracks: 'Barracks', forge: 'Forge', workshop: 'Workshop' },
    { longhouse: 'Roothall', barracks: 'Barracks', forge: 'Forge', workshop: 'Workshop' },
    { longhouse: 'Sanctum', barracks: 'Barracks', forge: 'Forge', workshop: 'Workshop' },
    { longhouse: 'Tidehall', barracks: 'Barracks', forge: 'Forge', workshop: 'Workshop' },
  ];
  const VBUILD = [
    { key: 'longhouse', icon: '🏠', x: -5.2, y: 4.4, z: 23.4 }, { key: 'barracks', icon: '⚔️', x: -6, y: 4.4, z: 31 },
    { key: 'forge', icon: '⚒️', x: 5.6, y: 4.6, z: 24.6 }, { key: 'workshop', icon: '⚙️', x: 6.4, y: 4.2, z: 31 },
  ];
  const NODE_ICON = { gold: '🪙', timber: '🌲', stone: '🧱', iron: '⛏️', coal: '⚫' };
  // Hvilken side kameraet ser på nå (nærmeste distrikt).
  function camSide() {
    let best = 0, bd = 1e9;
    SIDES.forEach((sd, i) => { const p = sideToWorld(i, 0, 26); const d = Math.hypot(p.x - cam.tx, p.z - cam.tz); if (d < bd) { bd = d; best = i; } });
    return best;
  }
  // Sidens merke, fakler og statuer (Runes referansebilder 11. okt): hjort i nord, tre i øst, stjerne i sør, anker i vest.
  // Hvert merke er noen flate deler i xy-planet, ca. 1 x 1 stort; [geometri, x, y, rotasjon z, rotasjon x].
  function sideExtras(si, g) {
    const EMBLEM = [
      () => [[new THREE.BoxGeometry(0.2, 0.3, 0.05), 0, -0.2], [new THREE.BoxGeometry(0.12, 0.16, 0.05), 0, -0.4],
        ...[-1, 1].flatMap(s => [[new THREE.BoxGeometry(0.06, 0.5, 0.05), s * 0.2, 0.12, -s * 0.5], [new THREE.BoxGeometry(0.05, 0.24, 0.05), s * 0.13, 0.22, s * 0.3],
          [new THREE.BoxGeometry(0.05, 0.24, 0.05), s * 0.36, 0.34, -s * 1.0], [new THREE.BoxGeometry(0.05, 0.2, 0.05), s * 0.3, 0.42, -s * 0.1], [new THREE.BoxGeometry(0.14, 0.06, 0.05), s * 0.15, -0.08, 0]])],
      () => [[new THREE.BoxGeometry(0.08, 0.42, 0.05), 0, -0.24], [new THREE.CylinderGeometry(0.3, 0.3, 0.05, 18), 0, 0.14, 0, Math.PI / 2],
        ...[-1, 1].map(s => [new THREE.BoxGeometry(0.05, 0.24, 0.05), s * 0.1, -0.4, s * 0.7])],
      () => [[new THREE.BoxGeometry(0.09, 0.9, 0.05), 0, 0], [new THREE.BoxGeometry(0.9, 0.09, 0.05), 0, 0], [new THREE.BoxGeometry(0.06, 0.5, 0.05), 0, 0, Math.PI / 4],
        [new THREE.BoxGeometry(0.06, 0.5, 0.05), 0, 0, -Math.PI / 4], [new THREE.TorusGeometry(0.2, 0.03, 6, 20), 0, 0]],
      () => [[new THREE.BoxGeometry(0.07, 0.62, 0.05), 0, -0.02], [new THREE.BoxGeometry(0.36, 0.06, 0.05), 0, 0.18], [new THREE.TorusGeometry(0.07, 0.025, 6, 12), 0, 0.36],
        [new THREE.TorusGeometry(0.24, 0.035, 6, 16, Math.PI), 0, -0.1, Math.PI], ...[-1, 1].map(s => [new THREE.BoxGeometry(0.1, 0.05, 0.05), s * 0.25, -0.06, -s * 0.7])],
    ];
    const G = new THREE.Group(), add = (geo, mat, x, y, z) => { const m = mesh(geo, mat, x, y, z); G.add(m); return m; };
    const putEmblem = (x, y, z, ry, size) => {
      const e = new THREE.Group(); e.position.set(x, y, z); e.rotation.y = ry; e.scale.setScalar(size); G.add(e);
      EMBLEM[si]().forEach(([geo, ex, ey, rz, rx]) => { const m = mesh(geo, VD.emblem, ex, ey, 0.02); m.rotation.set(rx || 0, 0, rz || 0); m.castShadow = false; e.add(m); });
    };
    EMB.forEach(p => putEmblem(...p));
    const wz = MAP.gateZ + 0.6, tx = MAP.gateHalf + 0.9;
    const fire = (x, y, z, r) => {
      add(new THREE.CylinderGeometry(r, r * 0.55, r * 0.8, 10), mats.brass, x, y, z);
      add(new THREE.ConeGeometry(r * 0.7, r * 1.7, 8), VD.fire, x, y + r * 1.1, z).castShadow = false;
      add(new THREE.SphereGeometry(r * 1.3, 8, 6), VD.glow, x, y + r, z).castShadow = false;
    };
    // Porttårnene: banner med merket mot slagmarken og mot landsbyen, glødepanner på muren.
    [-1, 1].forEach(sd => {
      [-1, 1].forEach(f => {
        add(new THREE.BoxGeometry(1.0, 2.2, 0.05), vm.banner, sd * tx, 3.0, wz + f * 1.42);
        putEmblem(sd * tx, 3.1, wz + f * 1.46, f > 0 ? 0 : Math.PI, 0.7);
      });
      [5.6, 15.5].forEach(x => fire(sd * x, 3.9, wz, 0.42));
    });
    // Fakler med gjerde langs kantene av slagmarken, som på bildet av nord.
    [-26, -16, -6, 4].forEach(z => [-1, 1].forEach(sd => {
      const x = sd * 15.2;
      add(new THREE.CylinderGeometry(0.1, 0.13, 1.5, 6), mats.iron, x, 0.75, z);
      fire(x, 1.6, z, 0.32);
      add(new THREE.BoxGeometry(0.06, 0.06, 2.4), VD.wood, x + sd * 0.3, 0.55, z + 2.2);
      add(new THREE.BoxGeometry(0.06, 0.06, 2.4), VD.wood, x + sd * 0.3, 0.25, z + 2.2);
      [1.0, 3.4].forEach(dz => add(new THREE.BoxGeometry(0.1, 0.7, 0.1), VD.wood, x + sd * 0.3, 0.35, z + dz));
    }));
    // Lysheim: engler på porttårnene og ved enden av veien mot citadellet.
    if (si === 2) {
      const marble = M(0xeeeae0, { roughness: 0.5, emissive: 0x2a2820 });
      const angel = (x, y, z, s, ry) => {
        const a = new THREE.Group(); a.position.set(x, y, z); a.scale.setScalar(s); a.rotation.y = ry; G.add(a);
        a.add(mesh(new THREE.BoxGeometry(0.9, 0.4, 0.9), marble, 0, 0.2, 0), mesh(new THREE.ConeGeometry(0.42, 1.7, 10), marble, 0, 1.25, 0), mesh(new THREE.SphereGeometry(0.2, 10, 8), marble, 0, 2.25, 0));
        const halo = mesh(new THREE.TorusGeometry(0.22, 0.03, 6, 18), vm.gold, 0, 2.6, -0.05); a.add(halo);
        [-1, 1].forEach(sd => { const w = mesh(new THREE.BoxGeometry(0.08, 1.4, 0.55), vm.gold, sd * 0.36, 1.8, -0.25); w.rotation.set(-0.3, 0, -sd * 0.35); a.add(w); });
        a.add(mesh(new THREE.CylinderGeometry(0.03, 0.03, 2.4, 6), vm.gold, 0.4, 1.4, 0.2));
      };
      [-1, 1].forEach(sd => angel(sd * tx, 5.6, wz, 0.9, Math.PI));
      [-1, 1].forEach(sd => angel(sd * 3.4, 0, MAP.roadEnd - 0.3, 1.1, 0));
    }
    restyleVillage(G, si);
    g.add(mergeGroup(G));
  }
  // Navneskilt i landsbyen, vises når kameraet er der.
"""


def apply(s):
    s = sub(s, HOUSE_OLD, HOUSE_NEW)
    i = s.index(NODE_OLD_START); j = s.index(NODE_OLD_END, i)
    assert s.count(NODE_OLD_START) == 1
    s = s[:i] + NODE_NEW + s[j + len(NODE_OLD_END):]
    # Jern og stein bytter plass: jern øverst til høyre ved porten, stein i midten, som på bildet.
    s = sub(s, "stone:  { x: 13.4, z: 19.8, store: 'R' }, iron: { x: 13, z: 27, store: 'R' },",
               "iron:   { x: 13.4, z: 19.8, store: 'R' }, stone: { x: 13, z: 27, store: 'R' },")
    s = sub(s, KITS_ANCHOR, DECOR.lstrip('\n') + "\n" + KITS_ANCHOR)
    # Nord får varm, tråkket jord som på bildet.
    s = sub(s, "  const SIDE_LOOK = [\n    {},\n", "  const SIDE_LOOK = [\n    { floor: BM(0x4a3f31, 0, { roughness: 1 }) },\n")
    # Kopiene på de andre sidene får sidens farger.
    s = sub(s, "const copy = village.clone(); g.add(copy);", "const copy = village.clone(); g.add(copy); restyleVillage(copy, si);")
    # De gamle lyktene langs veien er byttet ut med faklene over.
    s = sub(s, "for (let z = distZ1 + 4; z < MAP.roadEnd; z += 7) [-1, 1].forEach(sd => {",
               "for (let z = MAP.roadEnd; z < MAP.roadEnd; z += 7) [-1, 1].forEach(sd => {   // fakler fra village.py i stedet")
    s = sub(s, "    animateBiomes(now / 1000, dt);\n", "    animateBiomes(now / 1000, dt);\n    animateVillageDecor(now / 1000);\n")
    # Skiltene.
    s = sub(s, CSS_OLD, CSS_NEW)
    s = sub(s, "  // Navneskilt i landsbyen, vises når kameraet er der.\n", NAMES)
    s = sub(s, LABELS_OLD, LABELS_NEW)
    s = sub(s, "LABELS.forEach(L => { L.el = document.createElement('span'); L.el.className = 'lbl';",
               "LABELS.forEach(L => { L.el = document.createElement('span'); L.el.className = L.vl ? 'lbl vl' : 'lbl';")
    s = sub(s, """    const rect = canvas.getBoundingClientRect(), ec = state.econ;
    LABELS.forEach(L => {
      let t = L.text;
      if (L.node) { const n = ec.nodes[L.node]; t += n.unlocked ? ` · ${n.workers}/${ec.cap(L.node)}` : ' · ikke bygget'; }
      if (L.el.textContent !== t) L.el.textContent = t;
""", """    const rect = canvas.getBoundingClientRect(), ec = state.econ, cs = camSide();
    LABELS.forEach(L => {
      let t = L.text, small = '';
      if (L.node) { const n = ec.nodes[L.node]; small = n.unlocked ? `${n.workers}/${ec.cap(L.node)}` : PHONE ? '🔒' : 'ikke bygget'; }
      const key = t + '|' + small;
      if (L.key !== key) { L.key = key; if (L.vl) L.el.innerHTML = `<i>${L.icon}</i><b>${t}</b>${small ? `<small>${small}</small>` : ''}`; else L.el.textContent = t; }
      if (L.vl && L.si !== cs) { L.el.style.display = 'none'; return; }
""")
    # Kameraet: din side er alltid opp. camGoto snur kameraet til sidens retning (yaw) med mindre noe annet er gitt.
    s = sub(s, "  let camAnim = null;\n  function camGoto(tx, tz, dist, pitch) { camAnim = { tx, tz, dist, pitch }; }\n",
               """  let camAnim = null;
  // Din side (0 = nord). Kameraet snur seg så din port alltid er øverst, uansett side.
  let MY_SIDE = 0;
  function camGoto(tx, tz, dist, pitch, yaw) { camAnim = { tx, tz, dist, pitch, yaw: yaw == null ? SIDES[MY_SIDE].rot : yaw }; }
  // Landsbyen sett fra en side: porten øverst, citadellet nederst, hele distriktet i bildet også på telefon.
  function villageDist() {
    const a = Math.max(0.3, camera.aspect || 1), fit = 19 / (Math.tan(camera.fov * Math.PI / 360) * a);
    return Math.max(46, Math.min(95, fit * 0.98));
  }
  function viewVillage(si) {
    const p = sideToWorld(si, 0, PHONE ? 23.5 : 26.5);
    camGoto(p.x, p.z, villageDist(), PHONE ? 1.18 : 0.98, SIDES[si].rot);
    document.querySelectorAll('#vside button').forEach(b => b.classList.toggle('on', +b.dataset.vs === si));
  }
  document.querySelectorAll('#vside button').forEach(b => b.onclick = () => viewVillage(+b.dataset.vs));
""")
    s = sub(s, "  $('#cam-village').onclick = () => camGoto(0, 25.5, 46, 0.95);", "  $('#cam-village').onclick = () => viewVillage(MY_SIDE);")
    s = sub(s, """      ['tx', 'tz', 'dist', 'pitch'].forEach(p => cam[p] += (camAnim[p] - cam[p]) * k);
      if (Math.abs(cam.tz - camAnim.tz) < 0.05 && Math.abs(cam.dist - camAnim.dist) < 0.05) camAnim = null;""",
               """      ['tx', 'tz', 'dist', 'pitch'].forEach(p => cam[p] += (camAnim[p] - cam[p]) * k);
      const dy = Math.atan2(Math.sin(camAnim.yaw - cam.yaw), Math.cos(camAnim.yaw - cam.yaw)); cam.yaw += dy * k;
      if (Math.abs(cam.tz - camAnim.tz) < 0.05 && Math.abs(cam.tx - camAnim.tx) < 0.05 && Math.abs(cam.dist - camAnim.dist) < 0.05 && Math.abs(dy) < 0.003) { cam.yaw = camAnim.yaw; camAnim = null; }""")
    # «Se fra» øverst i Landsby-fanen.
    s = sub(s, '      <div id="longhouse"></div>\n',
               '      <div class="vside" id="vside"><span>Se landsbyen fra</span>'
               '<button type="button" data-vs="0" class="on">Nord</button><button type="button" data-vs="1">Øst</button>'
               '<button type="button" data-vs="2">Sør</button><button type="button" data-vs="3">Vest</button></div>\n'
               '      <div id="longhouse"></div>\n')
    s = sub(s, "    return pivot;\n  }\n  const sideKits", "    sideExtras(si, g);\n    return pivot;\n  }\n  const sideKits")
    s = sub(s, "      if (vis && L.side) { const hw = L.el.offsetWidth / 2 + 4;", "      if (vis && (L.side || L.vl)) { const hw = L.el.offsetWidth / 2 + 4;")
    return s
