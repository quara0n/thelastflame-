"""World 3 (Urheim, dinosaurs) and Tier 4 (big machines and creatures) for The Last Flame prototype.
Applied by build_v2.py on top of the upgrade build."""
from patch import sub

ENGINE_TYPES = r"""
// ===== World 3 – Urheim (wave 21–30): tiden har gått i stykker, og urtidsdyrene er tilbake. =====
// Felles språk: fossilplater som rustning, ravgule øyne, bein som stikker ut. Damp, vulkansk jungel og rav.
Object.assign(TYPES, {
  raptor:      { name: 'Razorclaw', side: 'e', kind: 'dino', role: 'Raptorflokk som går rundt fronten og hopper på skytterne', hp: 160, armor: 1, dmg: 16, interval: 0.7, range: 0.4, speed: 4.4, radius: 0.45, aggro: 12, hunts: 'ranged' },
  hornback:    { name: 'Hornback', side: 'e', kind: 'dino', role: 'Stormer inn og slår fronten bakover', hp: 900, armor: 6, dmg: 36, interval: 1.5, range: 0.7, speed: 2.3, radius: 1.0, aggro: 9, charge: 2.0, knock: 2.0 },
  snapper:     { name: 'Snapper-sverm', side: 'e', kind: 'dino', swarm: true, role: 'Hundrevis av små bitt', hp: 50, armor: 0, dmg: 7, interval: 0.5, range: 0.3, speed: 4.6, radius: 0.3, aggro: 10 },
  clubtail:    { name: 'Clubtail', side: 'e', kind: 'dino', role: 'Tykt panser, halekølla lammer den den treffer', hp: 650, armor: 10, dmg: 24, interval: 1.6, range: 0.8, speed: 1.7, radius: 0.95, aggro: 7, stuns: 1.0 },
  urdragon:    { name: 'Urdrage', side: 'e', kind: 'dragon', flies: true, role: 'Flyr over hæren rett mot porten. Bare skyttere når den i lufta', hp: 650, armor: 3, dmg: 22, interval: 1.3, range: 0.9, speed: 3.2, radius: 1.1, aggro: 8, cleave: true },
  tyrant:      { name: 'Tyrant', side: 'e', kind: 'dino', role: 'Enorm. Brølet skremmer, så units rundt slår svakere en stund', hp: 2200, armor: 6, dmg: 60, interval: 1.4, range: 1.0, speed: 2.2, radius: 1.3, aggro: 9, cleave: true, roar: { every: 8, r: 5, dur: 4, mul: 0.7 } },
  frillspitter:{ name: 'Frillspitter', side: 'e', kind: 'dino', role: 'Spytter fra avstand og blender, så den som treffes slår svakere', hp: 240, armor: 1, dmg: 20, interval: 1.5, range: 7, speed: 2.6, radius: 0.5, aggro: 10, ranged: true, blinds: 3 },
  earthshaker: { name: 'Earthshaker', side: 'e', kind: 'dino', role: 'Kjempestor og treg. Bærer raptorer på ryggen som hopper av ved porten', hp: 3000, armor: 7, dmg: 50, interval: 2.0, range: 1.1, speed: 1.3, radius: 1.6, aggro: 7, cleave: true, knock: 1.5, carries: { type: 'raptor', n: 4 } },
  revenant:    { name: 'Fossil-gjenganger', side: 'e', kind: 'dino', role: 'Et skjelett som setter seg sammen igjen én gang', hp: 380, armor: 3, dmg: 26, interval: 1.0, range: 0.5, speed: 2.6, radius: 0.6, aggro: 8, revive: 0.5 },
  tyrantKing:  { name: 'Tyrant King', side: 'e', kind: 'dino', role: 'Urheims konge, ridd av Urheim Warden. Brøler og kaller raptorer. Boss.', hp: 7000, armor: 9, dmg: 85, interval: 1.2, range: 1.2, speed: 1.9, radius: 1.5, aggro: 9, cleave: true, knock: 2.0, boss: true, roar: { every: 9, r: 6, dur: 4, mul: 0.65 }, summon: { type: 'raptor', n: 3, every: 16 } },
  // Tier 4 – store maskiner og skapninger. Svaret på dinosaurer og drager.
  ironhulk:    { name: 'Ironhulk', side: 'p', tier: 4, role: 'Dampgolem. Tank som drar fiender mot seg', cost: 130, iron: 4, coal: 2, hp: 760, armor: 8, dmg: 30, interval: 1.3, range: 0.6, speed: 1.6, radius: 0.9, aggro: 7, taunt: 5 },
  mammoth:     { name: 'War Mammoth', side: 'p', tier: 4, role: 'Krigsmammut. Tramper gjennom flokker og treffer tre', cost: 140, iron: 3, coal: 2, hp: 960, armor: 6, dmg: 32, interval: 1.1, range: 0.8, speed: 2.4, radius: 1.1, aggro: 8, cleave: true, sweep: 2, knock: 0.8 },
  skyspear:    { name: 'Skyspear', side: 'p', tier: 4, role: 'Kjempe-ballista. Ekstra skade mot flyvere og store dyr', cost: 135, iron: 5, coal: 1, hp: 260, armor: 3, dmg: 110, interval: 2.4, range: 14, speed: 1.6, radius: 0.8, aggro: 15, ranged: true, pierce: 8, bonus: { flies: 2, big: 1.5 } },
  hearthengine:{ name: 'Hearth Engine', side: 'p', tier: 4, role: 'Rullende smie. Reparerer og leger, og allierte rundt slår hardere', cost: 125, iron: 3, coal: 3, hp: 480, armor: 5, dmg: 12, interval: 1.0, range: 5, speed: 1.8, radius: 0.9, aggro: 6, ranged: true, heal: 13, healEvery: 1.2, healRange: 8, aura: 4 },
});
Object.assign(UPGRADES, {
  ironhulk: [
    { name: 'Pansrede kjeler', desc: 'Tykkere plater rundt kjelen. Mye mer helse og rustning.', cost: { gold: 35, iron: 3 }, mod: { hp: 230, armor: 2 } },
    { name: 'Dampstøt', desc: 'Damp fra knyttnevene. Hvert 5. sekund slår han fienden bakover og lammer den.', cost: { gold: 50, iron: 4, coal: 1 }, mod: { hp: 100, bash: 5 } },
    { name: 'Uknuselig', desc: 'Under halv helse låser han leddene og tar halv skade i 6 sekunder.', cost: { gold: 70, iron: 5, coal: 3 }, mod: { hp: 100, brace: 6 } },
  ],
  mammoth: [
    { name: 'Jernkledde støttenner', desc: 'Jern på støttennene. Mye mer skade.', cost: { gold: 35, iron: 3 }, mod: { dmgMul: 1.5 } },
    { name: 'Krigstårn', desc: 'Et tårn av tre og jern på ryggen. Mer helse og rustning.', cost: { gold: 50, iron: 4, coal: 1 }, mod: { hp: 300, armor: 2 } },
    { name: 'Stampede', desc: 'Stormer inn i første kamp og slår alt den treffer langt bakover.', cost: { gold: 70, iron: 5, coal: 3 }, mod: { charge: 1.8, knock: 1.6 } },
  ],
  skyspear: [
    { name: 'Lengre lade', desc: 'Lengre skinne for bolten. Skyter lenger og hardere.', cost: { gold: 35, iron: 3 }, mod: { range: 2, dmgMul: 1.2 } },
    { name: 'Dobbeltlade', desc: 'To bolter på rad. Skyter mye raskere.', cost: { gold: 50, iron: 4, coal: 1 }, mod: { intervalMul: 0.75 } },
    { name: 'Kjedespyd', desc: 'Bolten går tvers gjennom og treffer opptil tre fiender bak målet.', cost: { gold: 70, iron: 5, coal: 3 }, mod: { skewer: 3 } },
  ],
  hearthengine: [
    { name: 'Større ildsted', desc: 'Større smie. Leger mer.', cost: { gold: 35, iron: 3 }, mod: { healMul: 1.4, hp: 100 } },
    { name: 'Varmebølge', desc: 'Varmen når lenger. Større aura og lenger rekkevidde på legingen.', cost: { gold: 50, iron: 4, coal: 1 }, mod: { aura: 2, healRange: 2 } },
    { name: 'Smiens velsignelse', desc: 'Leger to om gangen. Allierte i auraen slår 30 % hardere og gror tilbake.', cost: { gold: 70, iron: 5, coal: 3 }, mod: { twinHeal: true, rally: 6 } },
  ],
});
"""

WAVES_W3 = """  // Urheim: oddetall er en mildere ny skapning, partall en tøffere. Wave 25 er flyver-waven (urdrager).
  { style: 'Flokkjakt', groups: [['raptor', 12, 'flank'], ['wolf', 10, 'front'], ['spitter', 6, 'back']], world: 3 },
  { style: 'Horn',      groups: [['hornback', 3, 'front'], ['raptor', 10, 'flank'], ['thornling', 8, 'front']], world: 3 },
  { style: 'Sverm',     groups: [['snapper', 40, 'front'], ['hornback', 2, 'front'], ['raptor', 6, 'flank'], ['spitter', 6, 'back']], world: 3 },
  { style: 'Panser',    groups: [['clubtail', 5, 'front'], ['snapper', 24, 'flank'], ['raptor', 8, 'back']], world: 3 },
  { style: 'Urdrager',  groups: [['urdragon', 4, 'front'], ['raptor', 10, 'flank'], ['clubtail', 3, 'front'], ['snapper', 20, 'flank']], world: 3, flyers: true },
  { style: 'Tyrant',    groups: [['tyrant', 2, 'front'], ['raptor', 12, 'flank'], ['clubtail', 3, 'front']], world: 3, heavy: true },
  { style: 'Spytt',     groups: [['frillspitter', 8, 'back'], ['hornback', 3, 'front'], ['snapper', 24, 'flank'], ['raptor', 6, 'flank']], world: 3 },
  { style: 'Jordskjelv', groups: [['earthshaker', 2, 'front'], ['frillspitter', 6, 'back'], ['raptor', 8, 'flank'], ['clubtail', 2, 'front']], world: 3, heavy: true },
  { style: 'Gjengangere', groups: [['revenant', 10, 'front'], ['tyrant', 1, 'front'], ['frillspitter', 4, 'back'], ['urdragon', 2, 'front']], world: 3 },
  { style: 'Boss',      groups: [['tyrantKing', 1, 'boss'], ['revenant', 4, 'front'], ['raptor', 8, 'flank'], ['frillspitter', 3, 'back']], world: 3, boss: true },
"""

GFX_MATS = r"""  // Urheim: oliven og brun hud, fossilplater, ravgule øyne. Tier 4: jern, tre og varm smieglød.
  Object.assign(mats, {
    dnHide: M(0x4a4630, { roughness: 0.85 }), dnHide2: M(0x5d4a33, { roughness: 0.8 }), dnBelly: M(0x7a6a4a, { roughness: 0.9 }),
    dnFossil: M(0xcdbd98, { roughness: 0.7 }), dnBone: M(0xd9cfb5, { roughness: 0.75 }),
    dnAmber: M(0x3a2204, { emissive: 0xffa21f, emissiveIntensity: 1.6 }), dnEye: new THREE.MeshBasicMaterial({ color: 0xffb020 }),
    dnTeal: M(0x1f4a44, { roughness: 0.6 }), dnWing: new THREE.MeshStandardMaterial({ color: 0x6b4a2a, roughness: 0.9, side: THREE.DoubleSide }),
    dnFeather: M(0x8a3a1a, { roughness: 0.9 }), wood: M(0x5a3d22, { roughness: 0.9 }), mFur: M(0x5a3e28, { roughness: 1 }),
  });
  // To bein og hale (raptor, tyrant, spytter, gjenganger). Kroppen henger frem, halen balanserer.
  function theropod(rig, o) {
    const ar = o.animRig || rig;
    const hide = o.hide || mats.dnHide, s = o.s || 1, g = new THREE.Group(); g.scale.setScalar(s); rig.add(g);
    const body = mesh(new THREE.SphereGeometry(0.42, 12, 10), hide, 0, 1.05, 0); body.scale.set(0.85, 0.8, 1.45); body.rotation.x = -0.12; g.add(body);
    if (!o.bones) g.add(mesh(new THREE.SphereGeometry(0.3, 10, 8), mats.dnBelly, 0, 0.92, 0.12).translateY(-0.02));
    for (let i = 0; i < 4; i++) { const t = mesh(new THREE.ConeGeometry(0.26 - i * 0.05, 0.55, 8), hide, 0, 1.1 - i * 0.04, -0.62 - i * 0.42); t.rotation.x = -Math.PI / 2 - 0.08; g.add(t); }
    const neck = mesh(new THREE.CylinderGeometry(0.14, 0.2, 0.5, 8), hide, 0, 1.38, 0.5); neck.rotation.x = 0.7; g.add(neck);
    const head = new THREE.Group(); head.position.set(0, 1.6, 0.75); g.add(head);
    head.add(mesh(new THREE.BoxGeometry(0.3, 0.26, 0.5), hide, 0, 0, 0.1));
    const jaw = mesh(new THREE.BoxGeometry(0.26, 0.08, 0.44), o.bones ? mats.dnBone : mats.dnHide2, 0, -0.14, 0.12); head.add(jaw); anim(ar, jaw, 'jaw', 7);
    for (let k = -1; k <= 1; k += 2) for (let j = 0; j < 3; j++) head.add(mesh(new THREE.ConeGeometry(0.018, 0.08, 4), mats.dnBone, k * 0.1, -0.1, 0.18 + j * 0.1));
    [-1, 1].forEach(k => head.add(mesh(new THREE.SphereGeometry(0.045, 8, 6), mats.dnEye, k * 0.15, 0.06, 0.12)));
    for (let i = 0; i < 6; i++) { const p = mesh(new THREE.ConeGeometry(0.07, 0.24, 4), o.bones ? mats.dnAmber : mats.dnFossil, 0, 1.38 - Math.abs(i - 2) * 0.03, 0.4 - i * 0.28); p.rotation.x = -0.3; g.add(p); }
    [-1, 1].forEach(k => {
      const th = mesh(new THREE.CylinderGeometry(0.13, 0.09, 0.55, 8), hide, k * 0.22, 0.72, -0.05); th.rotation.x = 0.35; g.add(th);
      const sh = mesh(new THREE.CylinderGeometry(0.07, 0.05, 0.5, 6), o.bones ? mats.dnBone : mats.dnHide2, k * 0.22, 0.3, -0.12); sh.rotation.x = -0.3; g.add(sh);
      g.add(mesh(new THREE.BoxGeometry(0.16, 0.06, 0.3), mats.dnHide2, k * 0.22, 0.04, 0.02));
      if (o.arms !== false) { const a = mesh(new THREE.BoxGeometry(0.05, 0.28, 0.05), hide, k * 0.2, 1.12, 0.5); a.rotation.x = -0.9; g.add(a); }
    });
    if (o.bones) { const core = mesh(new THREE.SphereGeometry(0.16, 10, 8), mats.dnAmber, 0, 1.05, 0.05); g.add(core); anim(ar, core, 'pulse', 3); }
    return { g, head, h: 1.8 * s };
  }
  // Fire bein (hornback, clubtail, earthshaker, mammut).
  function quadruped(rig, o) {
    const hide = o.hide || mats.dnHide, s = o.s || 1, g = new THREE.Group(); g.scale.setScalar(s); rig.add(g);
    const body = mesh(new THREE.SphereGeometry(0.7, 14, 10), hide, 0, 1.05, 0); body.scale.set(0.95, 0.75, 1.35); g.add(body);
    [[-1, 1], [1, 1], [-1, -1], [1, -1]].forEach(([sx, sz]) => g.add(mesh(new THREE.CylinderGeometry(0.17, 0.15, 0.75, 8), mats.dnHide2, sx * 0.42, 0.37, sz * 0.55)));
    return { g, h: 1.9 * s };
  }
"""

GFX_MODELS = r"""      // ---------- Urheim (World 3) ----------
      case 'raptor': { const t = theropod(rig, { s: 0.75, hide: mats.dnHide2 }); [-1, 1].forEach(k => { const c = mesh(new THREE.ConeGeometry(0.03, 0.22, 4), mats.dnBone, k * 0.16, 0.12, 0.25); c.rotation.x = 1.2; t.g.add(c); });
        for (let i = 0; i < 4; i++) { const f = mesh(new THREE.BoxGeometry(0.03, 0.22, 0.1), mats.dnFeather, 0, 1.45 + i * 0.02, 0.3 - i * 0.18); f.rotation.x = -0.4; t.g.add(f); }
        height = t.h; break; }
      case 'snapper': { const t = theropod(rig, { s: 0.38, arms: false }); height = t.h; break; }
      case 'frillspitter': { const t = theropod(rig, { s: 0.85, hide: mats.dnTeal });
        const fr = new THREE.Mesh(new THREE.CircleGeometry(0.42, 16), mats.dnAmber); fr.position.set(0, -0.02, -0.1); t.head.add(fr); anim(rig, fr, 'pulse', 2.5);
        height = t.h; break; }
      case 'revenant': { const t = theropod(rig, { s: 0.95, hide: mats.dnBone, bones: true }); height = t.h; break; }
      case 'tyrant': case 'tyrantKing': {
        const king = u.type === 'tyrantKing', t = theropod(rig, { s: king ? 2.7 : 2.1, hide: king ? mats.dnHide2 : mats.dnHide, arms: true });
        for (let i = 0; i < 5; i++) { const p = mesh(new THREE.ConeGeometry(0.1, 0.35, 4), mats.dnFossil, 0, 1.5, 0.3 - i * 0.25); t.g.add(p); }
        if (king) {
          const rider = new THREE.Group(); rider.position.set(0, 1.42, 0.15); rider.scale.setScalar(0.42); t.g.add(rider);
          humanoid(rider, mats.fallen); const halo = mesh(new THREE.TorusGeometry(0.28, 0.03, 6, 20), mats.dnAmber, 0, 1.9, 0); halo.rotation.x = Math.PI / 2; rider.add(halo);
          const sp = mesh(new THREE.CylinderGeometry(0.03, 0.03, 2.2, 6), mats.iron, 0.35, 1.3, 0.2); sp.rotation.x = -0.5; rider.add(sp);
          const crown = mesh(new THREE.TorusGeometry(0.22, 0.04, 6, 16), mats.dnAmber, 0, 0.25, 0.1); crown.rotation.x = Math.PI / 2; t.head.add(crown);
        }
        height = t.h; break; }
      case 'hornback': { const q = quadruped(rig, { s: 1.05 });
        const head = new THREE.Group(); head.position.set(0, 1.0, 1.0); q.g.add(head);
        head.add(mesh(new THREE.BoxGeometry(0.55, 0.45, 0.6), mats.dnHide, 0, 0, 0.1));
        const frill = new THREE.Mesh(new THREE.CircleGeometry(0.55, 18, 0, Math.PI), mats.dnHide2); frill.position.set(0, 0.15, -0.2); frill.rotation.x = -0.35; head.add(frill);
        [[-0.2, 0.35, 0.7], [0.2, 0.35, 0.7], [0, 0, 0.75]].forEach(([x, y, l]) => { const h = mesh(new THREE.ConeGeometry(0.07, l, 6), mats.dnBone, x, y * 0.4, 0.4 + l * 0.3); h.rotation.x = Math.PI / 2 - 0.3; head.add(h); });
        [-1, 1].forEach(k => head.add(mesh(new THREE.SphereGeometry(0.05, 8, 6), mats.dnEye, k * 0.24, 0.08, 0.3)));
        height = q.h; break; }
      case 'clubtail': { const q = quadruped(rig, { s: 0.95, hide: mats.dnHide2 });
        for (let r = 0; r < 3; r++) for (let i = 0; i < 4; i++) { const p = mesh(new THREE.ConeGeometry(0.1, 0.22, 4), mats.dnFossil, (r - 1) * 0.35, 1.5 - Math.abs(r - 1) * 0.15, 0.6 - i * 0.4); q.g.add(p); }
        const tail = new THREE.Group(); tail.position.set(0, 0.95, -0.9); q.g.add(tail); anim(rig, tail, 'wave', 2.5);
        const tl = mesh(new THREE.CylinderGeometry(0.08, 0.2, 1.0, 8), mats.dnHide2, 0, 0, -0.5); tl.rotation.x = Math.PI / 2; tail.add(tl);
        tail.add(mesh(new THREE.DodecahedronGeometry(0.28, 0), mats.dnFossil, 0, 0, -1.05));
        q.g.add(mesh(new THREE.BoxGeometry(0.4, 0.32, 0.45), mats.dnHide, 0, 0.85, 1.0));
        [-1, 1].forEach(k => q.g.add(mesh(new THREE.SphereGeometry(0.045, 8, 6), mats.dnEye, k * 0.17, 0.92, 1.2)));
        height = q.h; break; }
      case 'earthshaker': { const q = quadruped(rig, { s: 1.7, hide: mats.dnHide });
        const neck = mesh(new THREE.CylinderGeometry(0.16, 0.3, 1.8, 10), mats.dnHide, 0, 1.9, 1.15); neck.rotation.x = 0.5; q.g.add(neck);
        q.g.add(mesh(new THREE.BoxGeometry(0.3, 0.25, 0.45), mats.dnHide2, 0, 2.7, 1.6));
        [-1, 1].forEach(k => q.g.add(mesh(new THREE.SphereGeometry(0.04, 8, 6), mats.dnEye, k * 0.13, 2.75, 1.78)));
        const tl = mesh(new THREE.ConeGeometry(0.28, 1.8, 8), mats.dnHide, 0, 0.95, -1.6); tl.rotation.x = -Math.PI / 2 + 0.15; q.g.add(tl);
        // raptorer på ryggen
        [-0.3, 0.3].forEach(x => { const r = new THREE.Group(); r.position.set(x, 1.45, -0.2); r.scale.setScalar(0.32); q.g.add(r); theropod(r, { hide: mats.dnHide2 }); });
        height = q.h + 1; break; }
      case 'urdragon': {
        const fl = new THREE.Group(); rig.add(fl); anim(rig, fl, 'float', 2.2, 0.25);
        const t = theropod(fl, { s: 1.15, hide: mats.dnFeather, arms: false, animRig: rig });
        [-1, 1].forEach(k => { const w = new THREE.Group(); w.position.set(k * 0.35, 1.3, 0.1);
          const p = new THREE.Mesh(new THREE.PlaneGeometry(2.2, 1.1), mats.dnWing); p.position.x = k * 1.1; p.rotation.x = -Math.PI / 2 + 0.1; w.add(p);
          const spar = mesh(new THREE.CylinderGeometry(0.04, 0.03, 2.2, 5), mats.dnBone, k * 1.1, 0.02, 0.5); spar.rotation.z = Math.PI / 2; w.add(spar);
          t.g.add(w); anim(rig, w, 'flap', 5, k); });
        [-1, 1].forEach(k => { const h = mesh(new THREE.ConeGeometry(0.04, 0.35, 5), mats.dnBone, k * 0.1, 0.2, -0.1); h.rotation.x = -0.9; t.head.add(h); });
        height = t.h; break; }
      // ---------- Tier 4 ----------
      case 'ironhulk': {
        rig.add(mesh(new THREE.BoxGeometry(1.1, 1.2, 0.85), mats.iron, 0, 1.45, 0), mesh(new THREE.BoxGeometry(0.7, 0.5, 0.05), mats.ember, 0, 1.5, 0.44));
        rig.add(mesh(new THREE.BoxGeometry(0.5, 0.4, 0.5), mats.steel, 0, 2.25, 0.05));
        [-1, 1].forEach(k => rig.add(mesh(new THREE.SphereGeometry(0.05, 8, 6), mats.pilot, k * 0.12, 2.28, 0.31)));
        const ch = mesh(new THREE.CylinderGeometry(0.12, 0.14, 0.7, 8), mats.iron, 0.3, 2.3, -0.3); rig.add(ch);
        rig.add(mesh(new THREE.ConeGeometry(0.1, 0.25, 6), mats.pilot, 0.3, 2.75, -0.3));
        [-1, 1].forEach(k => { rig.add(mesh(new THREE.SphereGeometry(0.3, 10, 8), mats.steel, k * 0.75, 1.85, 0)); rig.add(mesh(new THREE.CylinderGeometry(0.2, 0.26, 1.1, 8), mats.iron, k * 0.8, 1.2, 0.05)); rig.add(mesh(new THREE.BoxGeometry(0.45, 0.4, 0.45), mats.steel, k * 0.82, 0.55, 0.1)); });
        [-1, 1].forEach(k => rig.add(mesh(new THREE.BoxGeometry(0.35, 0.85, 0.45), mats.iron, k * 0.3, 0.42, 0)));
        height = 2.9; break; }
      case 'mammoth': { const q = quadruped(rig, { s: 1.25, hide: mats.mFur });
        q.g.add(mesh(new THREE.SphereGeometry(0.42, 10, 8), mats.mFur, 0, 1.3, 1.0));
        const tr = mesh(new THREE.CylinderGeometry(0.06, 0.12, 0.9, 8), mats.mFur, 0, 0.75, 1.35); tr.rotation.x = 0.25; q.g.add(tr); anim(rig, tr, 'creak', 2);
        [-1, 1].forEach(k => { const t = mesh(new THREE.TorusGeometry(0.42, 0.05, 6, 12, Math.PI * 0.9), mats.dnBone, k * 0.22, 0.95, 1.35); t.rotation.set(0, Math.PI / 2, k > 0 ? 0.5 : Math.PI - 0.5); q.g.add(t); });
        q.g.add(mesh(new THREE.BoxGeometry(0.85, 0.5, 0.9), mats.wood, 0, 1.85, -0.05), mesh(new THREE.BoxGeometry(0.95, 0.06, 1.0), mats.flag, 0, 1.62, -0.05));
        const r = new THREE.Group(); r.position.set(0, 2.05, 0); r.scale.setScalar(0.38); humanoid(r, mats.cloth); q.g.add(r);
        height = q.h + 0.8; break; }
      case 'skyspear': {
        rig.add(mesh(new THREE.BoxGeometry(1.0, 0.25, 1.6), mats.wood, 0, 0.55, 0));
        [[-1, 1], [1, 1], [-1, -1], [1, -1]].forEach(([x, z]) => { const w = mesh(new THREE.CylinderGeometry(0.3, 0.3, 0.12, 12), mats.wood, x * 0.55, 0.3, z * 0.55); w.rotation.z = Math.PI / 2; rig.add(w); });
        rig.add(mesh(new THREE.BoxGeometry(0.2, 0.7, 0.2), mats.wood, 0, 0.95, 0));
        const bow = new THREE.Group(); bow.position.set(0, 1.35, 0.1); bow.rotation.x = -0.15; rig.add(bow);
        bow.add(mesh(new THREE.BoxGeometry(0.16, 0.16, 2.0), mats.wood, 0, 0, 0.1));
        [-1, 1].forEach(k => { const a = mesh(new THREE.BoxGeometry(1.1, 0.1, 0.12), mats.iron, k * 0.55, 0, 0.75); a.rotation.y = -k * 0.35; bow.add(a); });
        const bolt = mesh(new THREE.CylinderGeometry(0.04, 0.04, 1.9, 6), mats.steelLight, 0, 0.12, 0.3); bolt.rotation.x = Math.PI / 2; bow.add(bolt);
        const tip = mesh(new THREE.ConeGeometry(0.09, 0.3, 6), mats.steelLight, 0, 0.12, 1.35); tip.rotation.x = Math.PI / 2; bow.add(tip);
        const c = new THREE.Group(); c.position.set(0.7, 0, -0.7); c.scale.setScalar(0.75); humanoid(c, mats.steel); rig.add(c);
        height = 2.0; break; }
      case 'hearthengine': {
        rig.add(mesh(new THREE.BoxGeometry(1.1, 0.4, 1.6), mats.wood, 0, 0.6, 0));
        [[-1, 1], [1, 1], [-1, -1], [1, -1]].forEach(([x, z]) => { const w = mesh(new THREE.CylinderGeometry(0.34, 0.34, 0.14, 12), mats.iron, x * 0.62, 0.34, z * 0.55); w.rotation.z = Math.PI / 2; rig.add(w); });
        rig.add(mesh(new THREE.CylinderGeometry(0.45, 0.5, 0.9, 10), mats.iron, 0, 1.25, -0.1));
        const fire = mesh(new THREE.BoxGeometry(0.4, 0.35, 0.05), mats.lantern, 0, 1.15, 0.42); rig.add(fire); anim(rig, fire, 'pulse', 6);
        rig.add(mesh(new THREE.CylinderGeometry(0.1, 0.12, 0.8, 8), mats.iron, 0, 2.05, -0.2), mesh(new THREE.ConeGeometry(0.12, 0.3, 6), mats.pilot, 0, 2.55, -0.2));
        rig.add(mesh(new THREE.BoxGeometry(0.5, 0.12, 0.3), mats.steel, 0.3, 0.92, 0.6));
        const sm = new THREE.Group(); sm.position.set(-0.6, 0, 0.6); sm.scale.setScalar(0.7); humanoid(sm, mats.fur); rig.add(sm);
        height = 2.6; break; }
"""

SOUNDS = r"""    dino: t => { voice(t, { type: 'sawtooth', f: [[0, 70], [0.35, 52], [1.1, 40]], dur: 1.15, v: 0.2, bp: 380, q: 2.5, a: 0.08, trem: [18, 0.5] }); voice(t + 0.05, { f: [[0, 140], [0.4, 104], [1.0, 80]], dur: 1.0, v: 0.08, bp: 700, q: 3, a: 0.1 }); noise(sfxBus, t, 0.8, { ftype: 'lowpass', f: 420, v: 0.12 }); },
    dragon: t => { voice(t, { f: [[0, 900], [0.25, 1700], [0.9, 600]], dur: 0.95, v: 0.14, bp: 1600, q: 2, a: 0.03, vib: [11, 40] }); noise(sfxBus, t + 0.1, 0.7, { ftype: 'bandpass', f: 1200, q: 1, v: 0.1 }); },
"""
SOUNDS_DIE = r"""    dino: t => { voice(t, { type: 'sawtooth', f: [[0, 90], [0.7, 30]], dur: 0.75, v: 0.18, bp: 300, q: 2 }); drum(sfxBus, t + 0.15, 38, 0.5, 0.5); },
    dragon: t => { voice(t, { f: [[0, 1400], [0.9, 200]], dur: 0.95, v: 0.14, bp: 1400, q: 2, vib: [8, 50] }); drum(sfxBus, t + 0.5, 42, 0.5, 0.5); },
"""


def apply(s):
    # --- Engine: creatures, Tier 4 and their upgrades ---
    s = sub(s, "\nconst ARCHER = {", ENGINE_TYPES + "\nconst ARCHER = {")
    s = sub(s, "].map((w, i) => Object.assign(w, { n: i + 1, world: w.world || 1,", WAVES_W3 + "].map((w, i) => Object.assign(w, { n: i + 1, world: w.world || 1,")
    s = sub(s, "scale: i < 10 ? { hp: 1 + 0.08 * i, dmg: 1 + 0.05 * i } : { hp: +(2.6 + 0.12 * (i - 10)).toFixed(2), dmg: +(1.75 + 0.05 * (i - 10)).toFixed(2) } }));",
               "scale: i < 10 ? { hp: 1 + 0.08 * i, dmg: 1 + 0.05 * i } : i < 20 ? { hp: +(2.6 + 0.12 * (i - 10)).toFixed(2), dmg: +(1.75 + 0.05 * (i - 10)).toFixed(2) } : { hp: +(3.4 + 0.12 * (i - 20)).toFixed(2), dmg: +(2.0 + 0.05 * (i - 20)).toFixed(2) } }));")
    s = sub(s, "2: { name: 'Vrangheim', desc: 'en vridd verden der alt levende er blitt vilt' } };",
               "2: { name: 'Vrangheim', desc: 'en vridd verden der alt levende er blitt vilt' }, 3: { name: 'Urheim', desc: 'en urtid der tiden har gått i stykker, og dinosaurene er tilbake' } };")
    # Flyers: ignore the army on the way, only ranged units reach them until they hover at the gate.
    s = sub(s, "    if (!u.atGate && this._engage(u, players, attackers, dt, u.T.aggro)) return;",
               "    if (!u.atGate && !u.T.flies && this._engage(u, players, attackers, dt, u.T.aggro)) return;")
    s = sub(s, """    for (const f of foes) {
      const d = dist(u, f);
      if (d > maxRange) continue;""", """    for (const f of foes) {
      const d = dist(u, f);
      if (d > maxRange) continue;
      if (f.T.flies && !f.atGate && this.gateHp > 0 && u.side === 'p' && !u.T.ranged) continue;""")
    s = sub(s, """      if (!o.alive || o === u || o === ignore) continue;
      const rx = o.x - u.x, rz = o.z - u.z;""", """      if (!o.alive || o === u || o === ignore || (u.T.flies && o.side !== u.side)) continue;
      const rx = o.x - u.x, rz = o.z - u.z;""")
    s = sub(s, """      const min = p.T.radius + q.T.radius;""", """      if (p.side !== q.side && ((p.T.flies && !p.atGate) || (q.T.flies && !q.atGate))) continue;
      const min = p.T.radius + q.T.radius;""")
    # Roar, carriers.
    s = sub(s, "    for (const e of enemies) if (e.T.summon && this.contact) {", """    for (const e of enemies) if (e.T.roar && this.contact) {
      e.rcd = (e.rcd == null ? 2 : e.rcd) - dt;
      if (e.rcd > 0) continue;
      const near = players.filter(p => dist(p, e) < e.T.roar.r);
      if (!near.length) continue;
      e.rcd = e.T.roar.every;
      near.forEach(p => { if (!this._steady(p)) { p.weakUntil = this.t + e.T.roar.dur; p.weakMul = e.T.roar.mul; } });
      this.events.push({ kind: 'roar', from: e });
    }
    for (const e of enemies) if (e.T.carries && !e.dropped && e.z > 4) this._drop(e);
    for (const e of enemies) if (e.T.summon && this.contact) {""")
    # Damage: bonus vs flyers and big targets, weakness, stun, blind, revive, carriers on death.
    s = sub(s, "    if (B) mult *= (B[t.T.kind] || 1) * (t.T.swarm && B.swarm ? B.swarm : 1);",
               "    if (B) mult *= (B[t.T.kind] || 1) * (t.T.swarm && B.swarm ? B.swarm : 1) * (t.T.flies && B.flies ? B.flies : 1) * (t.T.radius >= 1 && B.big ? B.big : 1);\n    if (u.weakUntil > this.t) mult *= u.weakMul || 0.7;\n    if (u.T.stuns && t.alive && !t.T.boss && t.type !== 'warden') t.stunUntil = this.t + u.T.stuns;\n    if (u.T.blinds && t.alive) { t.weakUntil = this.t + u.T.blinds; t.weakMul = 0.6; }")
    revive = "    if (t.hp <= 0 && t.alive && t.T.revive && !t.revived) { t.revived = true; t.hp = t.maxHp * t.T.revive; t.stunUntil = this.t + 1.5; this.events.push({ kind: 'revive', unit: t }); }\n"
    s = sub(s, "    if (t.hp <= 0 && t.alive) {\n      t.alive = false; t.target = null;\n      this.stats[u.type].kills++;",
               revive + "    if (t.hp <= 0 && t.alive) {\n      if (t.T.carries && !t.dropped) this._drop(t);\n      t.alive = false; t.target = null;\n      this.stats[u.type].kills++;")
    s = sub(s, "    t.hp -= amt;\n    if (byType && this.stats[byType]) this.stats[byType].dmg += dealt;\n    if (t.hp <= 0) {",
               "    t.hp -= amt;\n    if (byType && this.stats[byType]) this.stats[byType].dmg += dealt;\n    if (t.hp <= 0 && t.T.revive && !t.revived) { t.revived = true; t.hp = t.maxHp * t.T.revive; t.stunUntil = this.t + 1.5; this.events.push({ kind: 'revive', unit: t }); return; }\n    if (t.hp <= 0) {\n      if (t.T.carries && !t.dropped) this._drop(t);")
    s = sub(s, "  _sheltered(t) {", """  _drop(e) {
    e.dropped = true;
    for (let i = 0; i < e.T.carries.n; i++) {
      const a = i / e.T.carries.n * Math.PI * 2;
      const c = this._make(this.nextId++, e.T.carries.type, e.x + Math.cos(a) * 1.4, e.z + Math.sin(a) * 1.4, null);
      this.units.push(c); this.stats[c.type].count++;
    }
    this.events.push({ kind: 'drop', from: e });
  }
  _sheltered(t) {""")
    s = sub(s, "Object.keys(TYPES).concat(['archer']).forEach(k => this.stats[k] = { dmg: 0, kills: 0, deaths: 0, count: 0 });",
               "Object.keys(TYPES).concat(['archer']).forEach(k => this.stats[k] = { dmg: 0, kills: 0, deaths: 0, count: 0 });")
    # --- Economy: bounties, Barracks IV opens Tier 4 ---
    s = sub(s, "const WARDEN_KILL_XP = BOUNTY;", "Object.assign(BOUNTY, { raptor: 2, hornback: 4, snapper: 1, clubtail: 4, urdragon: 8, tyrant: 10, frillspitter: 3, earthshaker: 12, revenant: 3, tyrantKing: 40 });\nconst WARDEN_KILL_XP = BOUNTY;")
    s = sub(s, "{ name: 'Barracks IV',  tier: 4, supply: 50, unlocks: [], cost: { timber: 90, stone: 60, iron: 35, coal: 15 }, future: true },",
               "{ name: 'Barracks IV',  tier: 4, supply: 50, unlocks: ['ironhulk', 'mammoth', 'skyspear', 'hearthengine'], cost: { timber: 90, stone: 60, iron: 35, coal: 15 } },")
    s = sub(s, "toast('Tier 4–5 er ikke designet ennå. Barracks IV–V åpnes når de er klare.')", "toast('Tier 5 er ikke designet ennå. Barracks V åpnes når den er klar, og kan da kjøpes så snart dere har råd, også i World 3.')")
    # --- Graphics: roster, world look, models, flying, events, sounds ---
    s = sub(s, "'pyreguard', 'siegebreaker', 'captain', 'huskarl'];\n  const RES_HEX", "'pyreguard', 'siegebreaker', 'captain', 'huskarl', 'ironhulk', 'mammoth', 'skyspear', 'hearthengine'];\n  const RES_HEX")
    s = sub(s, "    { tier: 4, name: 'Store maskiner og skapninger', need: 'Barracks IV' },",
               "    { tier: 4, name: 'Store maskiner og skapninger', units: ['ironhulk', 'mammoth', 'skyspear', 'hearthengine'], need: 'Barracks IV' },")
    s = sub(s, "collapsed: new Set([4, 5])", "collapsed: new Set([5])")
    s = sub(s, "    2: { portal: 0xff2fd0, void: 0x24062e, light: 0xd94aff, sky: 0x0f0a17, ground: 0x1c1622, snow: 0x241a2c, rock: 0x130c18 },",
               "    2: { portal: 0xff2fd0, void: 0x24062e, light: 0xd94aff, sky: 0x0f0a17, ground: 0x1c1622, snow: 0x241a2c, rock: 0x130c18 },\n    3: { portal: 0xffa21f, void: 0x2e1a04, light: 0xffb347, sky: 0x0d0f09, ground: 0x23261a, snow: 0x3a3b25, rock: 0x16170f },")
    s = sub(s, "  // Hjelpere for vridde skapninger.\n", GFX_MATS + "  // Hjelpere for vridde skapninger.\n")
    s = sub(s, "        rig.scale.setScalar(1.8); height = 4.6; break;\n      }\n    }\n",
               "        rig.scale.setScalar(1.8); height = 4.6; break;\n      }\n" + GFX_MODELS + "    }\n")
    s = sub(s, "      else v.rig.position.y = 0;\n", """      else v.rig.position.y = 0;
      if (u.T.flies) { const ty = u.atGate || sim.gateHp <= 0 ? 0.4 : 4.5; v.fy = v.fy == null ? ty : v.fy + (ty - v.fy) * Math.min(1, dt * 2); v.rig.position.y += v.fy; }
""")
    s = sub(s, "        v.bar.position.set(u.x, v.height + 0.35, u.z);", "        v.bar.position.set(u.x, v.height + 0.35 + (v.fy || 0), u.z);")
    s = sub(s, "      else if (e.kind === 'knock') {", """      else if (e.kind === 'roar') { addBlast(e.from.x, e.from.z, e.from.T.roar.r * 0.6, 0xffa21f); sfx('call_dino'); }
      else if (e.kind === 'revive') { addBlast(e.unit.x, e.unit.z, 0.9, 0xd9cfb5); sfx('thud'); }
      else if (e.kind === 'drop') { addBlast(e.from.x, e.from.z, 1.6, 0xffa21f); sfx('charge'); toast(`${e.from.T.name} slipper ${e.from.T.carries.n} ${TYPES[e.from.T.carries.type].name} løs!`); }
      else if (e.kind === 'knock') {""")
    s = sub(s, "    divine: t => { [1, 1.414, 2, 2.52]", SOUNDS + "    divine: t => { [1, 1.414, 2, 2.52]")
    s = sub(s, "    divine: t => { [1, 1.5, 2].forEach", SOUNDS_DIE + "    divine: t => { [1, 1.5, 2].forEach")
    return s
