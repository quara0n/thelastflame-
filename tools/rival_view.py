"""Watch the computer rival live (4 Oct 2026). Applied by build_v2.py after arena.py.
The rival gets his own battlefield to the right of yours (RIVAL_X along x). His wave runs step by step next to yours,
and his army is shown between waves. A minimap in the bottom-right corner shows both bases; tap it to move the camera.
A «Rival» button jumps there. His results (leak gold, what he sends) arrive when his wave actually ends."""
from patch import sub

CSS = """
.hud-sub.rivalhud .pill { border-color: #a35ae0; }
#minimap { position: absolute; right: 12px; bottom: 12px; width: 150px; height: 96px; border: 1px solid var(--line); border-radius: 8px; background: rgba(11, 14, 20, .82); z-index: 4; touch-action: none; cursor: pointer; }
.ordermenu:not([hidden]) ~ #minimap { display: none; }
@media (max-width: 600px) { #minimap { right: 6px; bottom: 6px; width: 120px; height: 78px; } #cam-rival { display: inline-block; } }
"""

UI = r"""
  // ---------- Rivalens slagmark: samme oppsett som din, flyttet til siden ----------
  const RIVAL_X = 90;
  const rivalField = (() => {
    const g = new THREE.Group(); g.position.x = RIVAL_X; scene.add(g);
    const gr = mesh(new THREE.PlaneGeometry(70, 116), mats.ground, 0, 0, 12); gr.rotation.x = -Math.PI / 2; gr.receiveShadow = true; gr.castShadow = false; g.add(gr);
    for (let i = 0; i < 30; i++) { const sd = i % 2 ? 1 : -1, h = 2 + rnd() * 6; const r = mesh(new THREE.ConeGeometry(1.4 + rnd() * 2, h, 6), mats.rock, sd * (16.5 + rnd() * 6), h / 2 - 0.2, -34 + rnd() * 48); g.add(r); }
    const wz = MAP.gateZ + 0.6;
    [-1, 1].forEach(sd => { g.add(mesh(new THREE.BoxGeometry(12, 3.4, 1.4), mats.wall, sd * (MAP.gateHalf + 6.6), 1.7, wz)); g.add(mesh(new THREE.CylinderGeometry(1.25, 1.45, 5.2, 10), mats.wall, sd * (MAP.gateHalf + 0.9), 2.6, wz)); g.add(mesh(new THREE.ConeGeometry(1.5, 1.6, 10), mats.iron, sd * (MAP.gateHalf + 0.9), 6, wz)); });
    const gate = new THREE.Group(); gate.position.z = wz; g.add(gate);
    gate.add(mesh(new THREE.BoxGeometry(MAP.gateHalf * 2, 3.1, 0.5), mats.gate, 0, 1.55, 0));
    [0.7, 1.6, 2.5].forEach(y => gate.add(mesh(new THREE.BoxGeometry(MAP.gateHalf * 2 + 0.05, 0.16, 0.56), mats.gateBand, 0, y, 0)));
    const rubble = new THREE.Group(); rubble.position.z = wz; rubble.visible = false; g.add(rubble);
    for (let i = 0; i < 9; i++) rubble.add(mesh(new THREE.DodecahedronGeometry(0.3 + rnd() * 0.4), mats.gate, (rnd() - 0.5) * 5, 0.25, (rnd() - 0.5) * 1.6));
    const ring = mesh(new THREE.TorusGeometry(3.3, 0.38, 12, 48), mats.portal, 0, 3.6, MAP.portalZ); g.add(ring);
    const vd = new THREE.Mesh(new THREE.CircleGeometry(3.0, 40), mats.portalVoid); vd.position.set(0, 3.6, MAP.portalZ); g.add(vd);
    const road = mesh(new THREE.PlaneGeometry(3.4, 20), M(0x5a4a3c, { roughness: 0.95 }), 0, 0.02, 26); road.rotation.x = -Math.PI / 2; road.castShadow = false; g.add(road);
    [[MAP.flameReach + 1, 0.7], [MAP.flameReach - 1.6, 1.5], [MAP.flameReach - 4.2, 2.5], [MAP.flameReach - 6.4, 3.5]].forEach(([r, h], i) => g.add(mesh(new THREE.CylinderGeometry(r, r + 0.4, h, 32), i % 2 ? mats.warmStone2 : mats.warmStone, 0, h / 2, MAP.flameZ)));
    g.add(mesh(new THREE.CylinderGeometry(1.6, 1.0, 1.2, 16), mats.brass, 0, 4.1, MAP.flameZ));
    const fl = new THREE.Mesh(new THREE.ConeGeometry(1.5, 5.4, 16, 1, true), mats.flame); fl.position.set(0, 7.4, MAP.flameZ); g.add(fl);
    const light = new THREE.PointLight(0xffa23c, 2.2, 40, 1.6); light.position.set(0, 9, MAP.flameZ); g.add(light);
    // Lilla banner på muren, så du ser at det er rivalens.
    [-1, 1].forEach(sd => { g.add(mesh(new THREE.BoxGeometry(0.1, 3, 0.1), mats.iron, sd * 7, 5, wz)); g.add(mesh(new THREE.BoxGeometry(1.2, 1.6, 0.05), M(0x5a2a7a, { side: THREE.DoubleSide }), sd * 7 + sd * 0.6, 5.6, wz)); });
    return { g, gate, rubble, flame: fl };
  })();
  let rivalVis = new Map(), rivalVisSim = null;
  const off = o => ({ x: o.x + RIVAL_X, y: o.y, z: o.z });
  function clearRivalVisuals() { rivalVis.forEach(v => { scene.remove(v.g); scene.remove(v.bar); }); rivalVis = new Map(); }
  function syncRival(dt) {
    const rs = state.versus ? (state.rival.sim || state.rival.view) : null;
    rivalField.g.visible = state.versus;
    if (rs !== rivalVisSim) { clearRivalVisuals(); rivalVisSim = rs; }
    if (!rs) return;
    for (const e of rs.events) {
      if (e.kind === 'shot') addShot(e.from.T ? off(e.from) : off(e.from), off(e.to), e.type);
      else if (e.kind === 'swing') { const v = rivalVis.get(e.from.id); if (v) v.lunge = 0.14; }
    }
    rs.events.length = 0;
    for (const u of rs.units) {
      let v = rivalVis.get(u.id);
      if (!v && u.alive) { v = buildUnit(u); v.bar.visible = false; rivalVis.set(u.id, v); }
      if (!v) continue;
      if (!u.alive) { v.deadT += dt; v.rig.rotation.x = -Math.min(1, v.deadT / 0.4) * Math.PI / 2; v.g.userData.ring.visible = false; if (v.deadT > 2.4) v.g.visible = false; continue; }
      v.g.position.set(u.x + RIVAL_X, 0, u.z);
      let d = u.facing - v.g.rotation.y; d = Math.atan2(Math.sin(d), Math.cos(d)); v.g.rotation.y += d * Math.min(1, dt * 10 || 1);
      if (u.moving && !reduceMotion) { v.bob += dt * 12; v.rig.position.y = Math.abs(Math.sin(v.bob)) * 0.08; } else v.rig.position.y = 0;
      if (u.T.flies) { const ty = u.atGate || rs.gateHp <= 0 ? 0.4 : 4.5; v.fy = v.fy == null ? ty : v.fy + (ty - v.fy) * Math.min(1, dt * 2); v.rig.position.y += v.fy; }
      if (v.lunge > 0) { v.lunge -= dt; v.rig.position.z = Math.sin((v.lunge / 0.14) * Math.PI) * 0.3; } else v.rig.position.z = 0;
      if (v.rig.userData.anim) runAnim(v, animT);
    }
    rivalField.gate.visible = rs.gateHp > 0; rivalField.rubble.visible = rs.gateHp <= 0;
  }
  // Rivalens wave er ferdig: resultatene kommer nå (gull for lekk, det han sender deg, om flammen hans falt).
  function rivalDone() {
    const rr = state.rival.end({ army: state.army, ec: state.econ });
    state.rivalRes = rr;
    if (rr.leakGold) { state.econ.add({ gold: rr.leakGold }); popRes('gold', rr.leakGold); }
    state.incoming = rr.out;
    const h = state.rival.hold;
    toast(rr.lost ? `Rivalens flamme falt på wave ${h.wave}!` : `Rivalen ${h.win ? 'holdt' : 'klarte seg så vidt i'} wave ${h.wave}. ${h.leaked ? `${h.leaked} av dine kom gjennom, +${rr.leakGold} gull. ` : ''}${rr.out.length ? `${state.rival.strike ? 'Stort angrep: ' : ''}han sender deg ${rr.out.length} skapninger${state.rival.why ? ` (${state.rival.why})` : ''}.` : ''}${state.rival.bank > 0 ? ' Han sparer gull til noe større.' : ''}`);
    if (rr.lost && state.phase === 'build') {
      state.phase = 'over'; state.outcome = 'won-vs'; sfx('victory');
      const el = $('#result'); el.hidden = false; el.className = 'result win';
      el.innerHTML = `<div class="r-head"><h2>Seier! Rivalens flamme falt på wave ${h.wave}</h2></div><p class="note">Trykk «Spill igjen» for en ny kamp.</p>`;
    } else if (state.phase === 'build') rebuild();
    renderPanel();
  }
  // Kart nede i hjørnet: begge basene, alle units som prikker, og hvor kameraet er. Trykk for å flytte dit.
  const mm = document.createElement('canvas'); mm.id = 'minimap'; $('.stage').appendChild(mm);
  const MM = { x0: -22, x1: RIVAL_X + 22, z0: -30, z1: 56 };
  const mmCtx = mm.getContext('2d');
  let mmT = 0;
  function drawMinimap(dt) {
    mm.hidden = !state.versus;
    if (!state.versus) return;
    mmT -= dt; if (mmT > 0) return; mmT = 0.1;
    const W = mm.clientWidth, H = mm.clientHeight, dpr = Math.min(2, window.devicePixelRatio || 1);
    if (mm.width !== W * dpr) { mm.width = W * dpr; mm.height = H * dpr; }
    const c = mmCtx; c.setTransform(dpr, 0, 0, dpr, 0, 0); c.clearRect(0, 0, W, H);
    // Kartet ligger på siden: x mot høyre, z (fra portal til flamme) nedover.
    const sx = x => (x - MM.x0) / (MM.x1 - MM.x0) * W, sz = z => (z - MM.z0) / (MM.z1 - MM.z0) * H;
    const field = (ox, col, label) => {
      c.strokeStyle = col; c.lineWidth = 1; c.strokeRect(sx(ox - 15), sz(-28), sx(ox + 15) - sx(ox - 15), sz(54) - sz(-28));
      c.fillStyle = 'rgba(160,160,170,.5)'; c.fillRect(sx(ox - 15), sz(MAP.gateZ), sx(ox + 15) - sx(ox - 15), 1.5);
      c.fillStyle = '#ffc766'; c.beginPath(); c.arc(sx(ox), sz(MAP.flameZ), 2.5, 0, 7); c.fill();
      c.fillStyle = col; c.font = '600 9px system-ui'; c.fillText(label, sx(ox - 14), sz(-24));
    };
    field(0, '#8fb3d6', 'Du'); field(RIVAL_X, '#c99af0', 'Rival');
    const dots = (units, ox) => { for (const u of units) if (u.alive && !u.staged) { c.fillStyle = u.side === 'p' ? '#9fc4de' : (u.sent ? '#c99af0' : '#e0524a'); c.fillRect(sx(u.x + ox) - 1, sz(u.z) - 1, 2, 2); } };
    if (sim) dots(sim.units, 0);
    const rs = state.rival.sim || state.rival.view; if (rs) dots(rs.units, RIVAL_X);
    const half = cam.dist * 0.42;
    c.strokeStyle = 'rgba(255,255,255,.85)'; c.strokeRect(sx(cam.tx - half * 0.8), sz(cam.tz - half), sx(cam.tx + half * 0.8) - sx(cam.tx - half * 0.8), sz(cam.tz + half) - sz(cam.tz - half));
  }
  const mmGo = e => { const r = mm.getBoundingClientRect(); const x = MM.x0 + (e.clientX - r.left) / r.width * (MM.x1 - MM.x0), z = MM.z0 + (e.clientY - r.top) / r.height * (MM.z1 - MM.z0); camAnim = null; cam.tx = clampN(x, -20, RIVAL_X + 20); cam.tz = clampN(z, -30, 55); };
  mm.addEventListener('pointerdown', e => { e.stopPropagation(); mm.setPointerCapture(e.pointerId); mmGo(e); mm._drag = true; });
  mm.addEventListener('pointermove', e => { if (mm._drag) mmGo(e); });
  mm.addEventListener('pointerup', () => { mm._drag = false; });
"""

def apply(s):
    s = sub(s, "#om-remove { color: #f0a59d; }", "#om-remove { color: #f0a59d; }" + CSS)
    s = sub(s, '<button type="button" id="cam-field">Slagmark</button>', '<button type="button" id="cam-field">Slagmark</button><button type="button" id="cam-rival">Rival</button>')
    s = sub(s, "  $('#cam-field').onclick = () => camGoto(0, FIELD_TZ, FIELD_DIST, 0.8);",
               "  $('#cam-field').onclick = () => camGoto(0, FIELD_TZ, FIELD_DIST, 0.8);\n  $('#cam-rival').onclick = () => camGoto(RIVAL_X, FIELD_TZ, FIELD_DIST, 0.8);")
    s = sub(s, "    cam.tx = clampN(cam.tx - (dx * cx + dy * sx) * k, -20, 20);", "    cam.tx = clampN(cam.tx - (dx * cx + dy * sx) * k, -20, state.versus ? RIVAL_X + 20 : 20);")
    s = sub(s, "      cam.tx = clampN(cam.tx + (s * cx + f * sx) * sp, -20, 20);", "      cam.tx = clampN(cam.tx + (s * cx + f * sx) * sp, -20, state.versus ? RIVAL_X + 20 : 20);")
    s = sub(s, "  // ---------- 1 mot 1: Send-fanen ----------", UI + "\n  // ---------- 1 mot 1: Send-fanen ----------")
    # Hovedløkken: rivalens wave går live ved siden av din, og kartet tegnes.
    s = sub(s, "    syncVisuals(vdt);", "    syncVisuals(vdt);\n    syncRival(vdt); drawMinimap(dt);\n"
               "    if (state.versus && state.rival.running() && state.phase !== 'over' && !(state.phase === 'battle' && state.paused)) {\n"
               "      state.racc = (state.racc || 0) + dt * (state.phase === 'build' ? 1 : state.speed);\n"
               "      let rn = 0; while (state.racc >= STEP && rn < 12 && state.rival.running()) { state.rival.sim.step(STEP); state.racc -= STEP; rn++; }\n"
               "      if (!state.rival.running()) rivalDone();\n    }")
    # Ved ny kamp: fjern rivalens gamle modeller.
    s = sub(s, "    state.rival = new Rival(); state.flags = 0;", "    clearRivalVisuals(); rivalVisSim = null;\n    state.rival = new Rival(); state.flags = 0;")
    # Knappen vises bare i 1 mot 1.
    s = sub(s, "    $('#hint').hidden = !build;", "    $('#hint').hidden = !build;\n    $('#cam-rival').hidden = !state.versus;")
    # Ser du på rivalen, viser linjen øverst hans tall (lilla).
    s = sub(s, "    $('#h-gatebox').classList.toggle('broken', gr <= 0);\n  }",
               "    $('#h-gatebox').classList.toggle('broken', gr <= 0);\n"
               "    const rs = state.versus && cam.tx > RIVAL_X / 2 ? (state.rival.sim || state.rival.view) : null;\n"
               "    document.querySelector('.hud-sub').classList.toggle('rivalhud', !!rs);\n"
               "    if (rs) {\n"
               "      $('#h-own').textContent = rs.units.filter(u => u.side === 'p' && u.alive && u.type !== 'warden').length;\n"
               "      $('#h-foe').textContent = rs.units.filter(u => u.side === 'e' && u.alive).length;\n"
               "      const rg = rs.gateMax ? rs.gateHp / rs.gateMax : 1;\n"
               "      $('#h-gatefill').style.width = `${rg * 100}%`;\n"
               "      $('#h-gate').textContent = rg > 0 ? `Rival · port ${Math.ceil(rs.gateHp)}` : 'Rivalens port er brutt';\n"
               "    }\n  }")
    return s
