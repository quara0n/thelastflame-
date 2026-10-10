"""Bastion med fire sider (10. okt 2026).

Byen er nå et kvadrat rundt flammen med fire like sider: nord (deg), øst, sør og vest.
Hver side har sin portal, sin slagmark, sin port og sitt eget distrikt med landsby,
gruver, Barracks, Forge og Workshop. Mellom distriktene ligger fire hjørnekvartaler
(gamlebyen), og ringveien rundt citadellet binder alt sammen.

Skala: avstanden port -> flamme er den samme som før (35 m), så kampen og balansen er
uendret. Distriktet ditt har samme bredde (35 m). Det som er nytt er at muren nå går
rundt hele byen: et kvadrat på ca. 70 x 70 m (før en stripe på 35 m), og slagmarkene
stråler ut i fire retninger, ca. 170 m fra portal til portal.

Ingen waves på øst, sør og vest ennå: sidene står klare («ledig plass»).
Simuleringen regner alt i sidens egne koordinater (portalen mot -z); sideToWorld()
snur et punkt rundt flammen til riktig side. Det er det flerspilleren skal bruke.
"""
from patch import sub


def cut(s, start, end, repl):
    """Bytter ut alt fra start til og med end (begge må finnes nøyaktig én gang)."""
    assert s.count(start) == 1, f'start not unique: {start[:80]!r}'
    i = s.index(start)
    j = s.index(end, i)
    assert s.count(end) >= 1
    return s[:i] + repl + s[j + len(end):]


SIM = r"""
// Bastion med fire sider (10. okt 2026): nord, øst, sør og vest rundt samme flamme.
// Hver side regnes i egne koordinater (portalen mot -z, flammen på (0, flameZ)). sideToWorld snur et punkt
// rundt flammen til sin side. Nord er deg; øst, sør og vest er ledige plasser (ingen waves ennå).
const BASTION = { half: MAP.flameZ - MAP.gateZ - 0.6, district: 17.6, plaza: 14.6 };
const SIDES = [
  { key: 'nord', name: 'Nord', rot: 0, color: 0x2c4a8a },
  { key: 'ost', name: 'Øst', rot: -Math.PI / 2, color: 0x2f6a3a },
  { key: 'sor', name: 'Sør', rot: Math.PI, color: 0x8a6a1f },
  { key: 'vest', name: 'Vest', rot: Math.PI / 2, color: 0x7a2a24 },
];
function sideToWorld(s, x, z) {
  const r = SIDES[s].rot, c = Math.cos(r), sn = Math.sin(r), dz = z - MAP.flameZ;
  return { x: Math.round((x * c + dz * sn) * 1000) / 1000, z: Math.round((MAP.flameZ - x * sn + dz * c) * 1000) / 1000 };
}
"""

KITS = r"""
  // ---------- Bastion: fire sider rundt flammen ----------
  // Hver side bygges i sine egne koordinater og snus rundt flammen. Nord har allerede portal, slagmark,
  // port og landsby fra koden over; her får den distriktet, muren ut til hjørnene og hjørnekvartalet.
  // Øst, sør og vest får alt, med en kopi av landsbyen slik den ser ut ved start.
  const B = BASTION, wallZ2 = MAP.gateZ + 0.6, distZ1 = MAP.gateZ + 1.3;
  const sideMat = SIDES.map(sd => M(sd.color, { roughness: 0.9, side: THREE.DoubleSide }));
  const distFloor = M(0x3a3530, { roughness: 1 }), roadMat2 = M(0x5a4a3c, { roughness: 0.95 });
  const lampMat2 = M(0x2a1a0e, { emissive: 0xffa040, emissiveIntensity: 1.4 });
  const oldWall = M(0x4a4038), oldRoof = M(0x3a2e28);
  const e0 = new Econ();
  const flatIn = (g, geo, mat, x, y, z) => { const m = mesh(geo, mat, x, y, z); m.rotation.x = -Math.PI / 2; m.castShadow = false; m.receiveShadow = true; g.add(m); return m; };
  function sideKit(si) {
    const full = si > 0, pivot = new THREE.Group();
    pivot.position.set(0, 0, MAP.flameZ); pivot.rotation.y = SIDES[si].rot; scene.add(pivot);
    const g = new THREE.Group(); g.position.z = -MAP.flameZ; pivot.add(g);
    const add = (geo, mat, x, y, z) => { const m = mesh(geo, mat, x, y, z); g.add(m); return m; };
    if (full) {
      // Slagmark: fjell på sidene, snøflekker, portalen.
      for (let i = 0; i < 30; i++) { const sd = i % 2 ? 1 : -1, h = 2 + rnd() * 6; add(new THREE.ConeGeometry(1.4 + rnd() * 2.2, h, 6), mats.rock, sd * (16.5 + rnd() * 6), h / 2 - 0.2, -34 + rnd() * 48).rotation.y = rnd() * 6; }
      for (let i = 0; i < 10; i++) flatIn(g, new THREE.CircleGeometry(1.5 + rnd() * 4, 16), mats.snow, (rnd() - 0.5) * 40, 0.01 + i * 0.0005, -30 + rnd() * 42);
      const ring = add(new THREE.TorusGeometry(3.3, 0.38, 12, 48), mats.portal, 0, 3.6, MAP.portalZ);
      const vd = new THREE.Mesh(new THREE.CircleGeometry(3.0, 40), mats.portalVoid); vd.position.set(0, 3.6, MAP.portalZ); g.add(vd);
      for (let i = 0; i < 6; i++) { const a = (i / 6) * Math.PI * 2; add(new THREE.ConeGeometry(0.35, 2.4 + (i % 3), 4), mats.rock, Math.cos(a) * 4.8, Math.sin(a) * 1.4 + 1.2, MAP.portalZ - 0.4); }
      // Porten med tårn, som din.
      [-1, 1].forEach(sd => {
        add(new THREE.BoxGeometry(12, 3.4, 1.4), mats.wall, sd * (MAP.gateHalf + 6.6), 1.7, wallZ2);
        add(new THREE.BoxGeometry(12, 0.3, 1.7), mats.wallTop, sd * (MAP.gateHalf + 6.6), 3.5, wallZ2);
        add(new THREE.CylinderGeometry(1.25, 1.45, 5.2, 10), mats.wall, sd * (MAP.gateHalf + 0.9), 2.6, wallZ2);
        add(new THREE.ConeGeometry(1.5, 1.6, 10), mats.iron, sd * (MAP.gateHalf + 0.9), 6, wallZ2);
      });
      add(new THREE.BoxGeometry(MAP.gateHalf * 2, 3.1, 0.5), mats.gate, 0, 1.55, wallZ2);
      [0.7, 1.6, 2.5].forEach(y => add(new THREE.BoxGeometry(MAP.gateHalf * 2 + 0.05, 0.16, 0.56), mats.gateBand, 0, y, wallZ2));
      // Landsbyen slik den står ved start: gull, tømmer og stein bygget, Barracks I.
      const copy = village.clone(); g.add(copy);
      const twin = o => copy.children[village.children.indexOf(o)];
      Object.keys(nodeVis).forEach(k => {
        const v = nodeVis[k], open = e0.nodes[k].unlocked;
        twin(v.real).visible = open; twin(v.ghost).visible = !open;
        v.workers.forEach(w => { twin(w).visible = false; });
      });
      twin(barracksWing).visible = e0.barracks >= 1; twin(banner).visible = e0.barracks >= 1;
      twin(barracksTower1).visible = e0.barracks >= 2; twin(barracksTower2).visible = e0.barracks >= 3; twin(barracksKeep).visible = e0.barracks >= 4;
      twin(barracksG).scale.setScalar(1 + 0.12 * e0.barracks); twin(cog).visible = false;
    }
    // Muren fortsetter fra porttårnene ut til hjørnet, med et stort tårn der.
    const ext0 = MAP.gateHalf + 12.6, extLen = B.half - ext0;
    [-1, 1].forEach(sd => {
      const cx = sd * (ext0 + extLen / 2);
      add(new THREE.BoxGeometry(extLen, 3.4, 1.4), mats.wall, cx, 1.7, wallZ2).receiveShadow = true;
      add(new THREE.BoxGeometry(extLen, 0.3, 1.7), mats.wallTop, cx, 3.5, wallZ2);
      for (let k = 0; k < extLen; k += 1.2) add(new THREE.BoxGeometry(0.6, 0.5, 0.4), mats.wallTop, cx - extLen / 2 + k + 0.3, 3.9, wallZ2 - 0.6);
    });
    add(new THREE.CylinderGeometry(2, 2.3, 7, 12), mats.wall, B.half, 3.5, wallZ2);
    add(new THREE.ConeGeometry(2.4, 2.4, 12), mats.iron, B.half, 8.2, wallZ2);
    // Sidens farge: to bannere på muren.
    [-1, 1].forEach(sd => { add(new THREE.BoxGeometry(0.1, 3, 0.1), mats.iron, sd * 8, 5, wallZ2); add(new THREE.BoxGeometry(1.2, 1.6, 0.05), sideMat[si], sd * 8 + sd * 0.6, 5.6, wallZ2); });
    // Distriktet: gulv, vei og lykter. Ytterst er det like bredt som før; innerst skrår det inn mot plassen rundt citadellet.
    const D = B.district, dIn = D, zBend = MAP.flameZ - dIn, zIn = MAP.flameZ - B.plaza / Math.SQRT2;
    const sh = new THREE.Shape();
    [[-D + 0.6, distZ1], [D - 0.6, distZ1], [D - 0.6, zBend - 0.6], [B.plaza / Math.SQRT2 - 0.6, zIn], [-B.plaza / Math.SQRT2 + 0.6, zIn], [-D + 0.6, zBend - 0.6]]
      .forEach(([x, z], i) => i ? sh.lineTo(x, -z) : sh.moveTo(x, -z));
    flatIn(g, new THREE.ShapeGeometry(sh), distFloor, 0, 0.012, 0);
    flatIn(g, new THREE.PlaneGeometry(3.4, MAP.roadEnd - distZ1), roadMat2, 0, 0.02, (distZ1 + MAP.roadEnd) / 2);
    for (let z = distZ1 + 4; z < MAP.roadEnd; z += 7) [-1, 1].forEach(sd => {
      add(new THREE.CylinderGeometry(0.07, 0.09, 1.6, 6), mats.iron, sd * 2.2, 0.8, z);
      add(new THREE.BoxGeometry(0.3, 0.3, 0.3), lampMat2, sd * 2.2, 1.7, z);
    });
    // Murer mot nabodistriktene: rett inn fra porten, så på skrå mot plassen (den skrå muren deles med neste side).
    [-1, 1].forEach(sd => {
      const len = zBend - distZ1;
      add(new THREE.BoxGeometry(1.2, 3, len), mats.wall, sd * D, 1.5, distZ1 + len / 2).receiveShadow = true;
      add(new THREE.CylinderGeometry(1, 1.15, 4.2, 8), mats.wall, sd * D, 2.1, zBend);
    });
    const dLen = (D - B.plaza / Math.SQRT2) * Math.SQRT2, dMid = (D + B.plaza / Math.SQRT2) / 2;
    const diag = add(new THREE.BoxGeometry(1.2, 3, dLen), mats.wall, dMid, 1.5, MAP.flameZ - dMid); diag.rotation.y = -Math.PI / 4;
    add(new THREE.CylinderGeometry(0.9, 1.05, 3.8, 8), mats.wall, B.plaza / Math.SQRT2, 1.9, zIn);
    // Hjørnekvartalet til høyre (gamlebyen): hus i et kvadrat mellom to distrikter.
    for (let i = 0; i < 9; i++) {
      const x = D + 2.6 + (i % 3) * 4.8 + rnd() * 1.6, d = D + 2.6 + Math.floor(i / 3) * 4.8 + rnd() * 1.6;
      if (x > B.half - 2 || d > B.half - 2) continue;
      const w = 2 + rnd() * 1.8, h = 1.5 + rnd() * 2;
      add(new THREE.BoxGeometry(w, h, 2.2), oldWall, x, h / 2, MAP.flameZ - d);
      const rf = add(new THREE.ConeGeometry(w * 0.8, 1.2, 4), oldRoof, x, h + 0.6, MAP.flameZ - d); rf.rotation.y = Math.PI / 4;
    }
    return pivot;
  }
  const sideKits = SIDES.map((sd, i) => sideKit(i));
  // Ringveien rundt citadellet binder de fire distriktene sammen.
  { const rr = mesh(new THREE.RingGeometry(MAP.flameReach + 1.6, MAP.flameReach + 4.2, 48), roadMat2, 0, 0.022, MAP.flameZ); rr.rotation.x = -Math.PI / 2; rr.castShadow = false; rr.receiveShadow = true; scene.add(rr); }
"""


def apply(s):
    # Logikk: sidene og sideToWorld, rett etter MAP.
    s = sub(s, "function cellCenter(col, row) {", SIM.lstrip() + "\nfunction cellCenter(col, row) {")

    # Bakken dekker hele byen og alle fire slagmarker.
    s = sub(s, "const ground = mesh(new THREE.PlaneGeometry(70, 116), mats.ground, 0, 0, 12);",
               "const ground = mesh(new THREE.PlaneGeometry(210, 210), mats.ground, 0, 0, MAP.flameZ);")

    # Det gamle distriktet (rett stripe) og den rette ringveien bygges nå av sideKit.
    s = cut(s, "  flat(34, ringZ - distZ0, 0, (distZ0 + ringZ) / 2, M(0x3a3530, { roughness: 1 }), 0.012);",
               "    scene.add(mesh(new THREE.BoxGeometry(0.3, 0.3, 0.3), lampMat, sd * 2.2, 1.7, z));\n  });\n",
               "  // Distriktet, ringveien og murene mot naboene bygges av sideKit (Bastion med fire sider).\n")
    # Husene bak citadellet står nå der sør-distriktet er; hjørnekvartalene tar over.
    s = cut(s, "  // Resten av byen bak citadellet.\n",
               "    const rf = mesh(new THREE.ConeGeometry(w * 0.8, 1.2, 4), farRoof, x, h + 0.6, z); rf.rotation.y = Math.PI / 4; scene.add(rf);\n  }\n",
               "")

    # Sidene bygges når landsbyen finnes (øst, sør og vest får en kopi av den).
    s = sub(s, "  // Navneskilt i landsbyen, vises når kameraet er der.\n", KITS + "\n  // Navneskilt i landsbyen, vises når kameraet er der.\n")

    # Skilt over hver port. Landsbyskiltene skjules når man ser hele byen ovenfra.
    s = sub(s, "    { text: 'Gatehouse', x: 0, y: 6.2, z: MAP.gateZ + 0.6 },",
               "    ...SIDES.map((sd, i) => Object.assign({ side: true, far: !i, text: i ? `${sd.name} · ledig plass` : `${sd.name} · deg`, y: 8 }, sideToWorld(i, 0, MAP.gateZ + 0.6))),\n"
               "    { text: 'Gatehouse', x: 0, y: 6.2, z: MAP.gateZ + 0.6 },")
    s = sub(s, "    const show = cam.tz > 10;", "    const show = cam.tz > 10 || cam.dist > 100 || Math.abs(cam.tx) > 25;")
    s = sub(s, "      const vis = lv.z < 1 && Math.abs(lv.x) < 1.1 && Math.abs(lv.y) < 1.1;",
               "      const vis = lv.z < 1 && Math.abs(lv.x) < 1.1 && Math.abs(lv.y) < 1.1 && (L.side ? !L.far || cam.dist > 100 : cam.dist < 100);")

    # Kamera: kan flyttes rundt hele byen, zoome langt ut, og «Bastion»-knappen viser alt ovenfra.
    for old in ["cam.tx = clampN(cam.tx - (dx * cx + dy * sx) * k, -20, state.versus ? RIVAL_X + 20 : 20);",
                "cam.tx = clampN(cam.tx + (s * cx + f * sx) * sp, -20, state.versus ? RIVAL_X + 20 : 20);"]:
        s = sub(s, old, old.replace("-20, state.versus ? RIVAL_X + 20 : 20", "-95, state.versus ? RIVAL_X + 20 : 95"))
    s = sub(s, "cam.tz = clampN(cam.tz - (-dx * sx + dy * cx) * k, -30, 55);", "cam.tz = clampN(cam.tz - (-dx * sx + dy * cx) * k, -35, MAP.flameZ + 90);")
    s = sub(s, "cam.tz = clampN(cam.tz + (-s * sx + f * cx) * sp, -30, 55);", "cam.tz = clampN(cam.tz + (-s * sx + f * cx) * sp, -35, MAP.flameZ + 90);")
    s = sub(s, "cam.dist = clampN(pinch.dist * pinch.d / Math.max(20, Math.hypot(a.x - b.x, a.y - b.y)), 24, 95);",
               "cam.dist = clampN(pinch.dist * pinch.d / Math.max(20, Math.hypot(a.x - b.x, a.y - b.y)), 24, 190);")
    s = sub(s, "cam.dist = clampN(cam.dist * (1 + e.deltaY * 0.001), 24, 95);", "cam.dist = clampN(cam.dist * (1 + e.deltaY * 0.001), 24, 190);")
    s = sub(s, '<button type="button" id="cam-rival">Rival</button>', '<button type="button" id="cam-rival">Rival</button><button type="button" id="cam-bastion">Bastion</button>')
    s = sub(s, "  $('#cam-flame').onclick = () => camGoto(0, 42, 52, 0.62);",
               "  $('#cam-flame').onclick = () => camGoto(0, 42, 52, 0.62);\n"
               "  $('#cam-bastion').onclick = () => camGoto(0, MAP.flameZ, PHONE ? 205 : 165, 1.2);")
    # Tåken flytter seg med kameraet, så byen ikke forsvinner når man ser den ovenfra.
    s = sub(s, "    updateCamera();\n", "    updateCamera();\n    scene.fog.near = 60 + Math.max(0, cam.dist - 72); scene.fog.far = 120 + Math.max(0, cam.dist - 72) * 1.8;\n")
    return s
