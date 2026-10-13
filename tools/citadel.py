"""Flammeskjoldet og Warden som går dit kampen er (11. okt 2026, versjon 34). Siste steg i build_v2.py.

Rune: «Warden skal kunne gå til hver side der kampen er. Det skal være et skjold over flammen som er der på grunn av
Warden, så fienden ikke bare kan gå til flammen hvis én spiller lekker mens han slåss på sørsiden.»

Regler (valgt her, kan endres):
- **Flammeskjoldet** står over citadellet så lenge Warden lever. På sidene der Warden ikke står (og mens han går),
  stopper fiender ved skjoldet og slår på det. Hvert slag tar like mye av Wardens helse (uten rustning), uansett hvor
  han er. Faller Warden, faller skjoldet. På siden der Warden står, er det han som stopper dem, som før.
  Derfor er spill alene helt som før: der står Warden alltid hjemme. (Et skjold som stoppet fienden også der Warden
  står, gjorde spill alene mye lettere: boten nådde median wave 19 i stedet for 15, uansett hvor mye hvert slag kostet.)
- **Warden går selv (Auto)** langs ringveien til den siden der fienden er nærmest flammen: fiender ved skjoldet teller
  mest, fiender innenfor muren teller mer jo nærmere flammen de er. Han bytter side bare når den andre siden er klart
  verre (1,6 ganger + 2) og han har stått minst 2 s, så han ikke løper fram og tilbake. Ringveien tar ca. 5 s til
  nabosiden og 10 s til motsatt side.
- **Lagkamerater (test):** i Send-fanen kan computeren holde øst, sør og vest med samme waves og samme bot som rivalen.
  Alle fire sidene kjøres i takt, så Warden kan gå mellom dem. Taper én side, taper hele laget.

Logikken (`Citadel`, `Mate`, `teamStep`) ligger i simuleringen og kan kjøres uten grafikk (`node tools/team_sim.js`).
Uten lagkamerater har citadellet bare nord, så Warden står der han alltid har stått; det eneste nye er skjoldet.
"""
from patch import sub

LOGIC = r"""
// Flammeskjoldet og Warden som går dit kampen er (11. okt 2026, versjon 34).
// Warden er lagets felles konge. Så lenge han lever, står et skjold av hans kraft over flammen: fiender som når
// citadellet på en side der Warden ikke står, må slå seg gjennom det, og hvert slag tar av Wardens helse. Faller Warden,
// faller skjoldet. Der Warden står, er det han som stopper fienden (som før). Warden går selv langs ringveien til den siden der fienden er nærmest flammen.
// Hver side har sin egen simulering i egne koordinater; Citadel deler Warden og skjoldet mellom dem.
const CITADEL = { ring: MAP.flameReach + 2, shieldR: MAP.flameReach + 1.5, share: 1, pace: 1.4, minStay: 2, grace: 4, switchMul: 1.6, switchAdd: 2, shield: true, roam: true };
class Citadel {
  constructor() { this.sims = []; this.post = 0; this.warden = null; this.trip = null; this.t = 0; this.since = 0; this.hits = [0, 0, 0, 0]; this.moves = []; }
  attach(sim, si) {
    this.sims[si] = sim;
    if (sim.warden && !this.warden) { this.warden = sim.warden; this.post = si; }
  }
  shieldUp() { return CITADEL.shield && !!(this.warden && this.warden.alive); }
  // Skjoldet stopper fienden på sidene der Warden ikke står. Der han står, er det han som stopper dem (som før);
  // når han nettopp har kommet, holder skjoldet der også et par sekunder til han har fått tatt opp kampen.
  blocks(sim) { return this.shieldUp() && (!!this.trip || this.post !== sim.si || this.t - this.since < CITADEL.grace); }
  // Simuleringen der Warden står nå (null mens han går mellom sidene).
  simOf() { return this.trip ? null : this.sims[this.post] || null; }
  // Kalles fra hver sides step(); citadellet regnes én gang per tidssteg, uansett hvor mange sider som kjører.
  tick(sim) {
    if (sim.t <= this.t + 1e-9) return;
    const dt = sim.t - this.t; this.t = sim.t;
    this.update(dt);
  }
  // Hvor ille det står til på en side: fiender ved skjoldet teller mest, fiender innenfor muren mer jo nærmere flammen.
  threat(s) {
    if (!s || s.result) return 0;
    let k = 0;
    for (const e of s.units) if (e.alive && e.side === 'e') {
      if (e.atShield) k += 4;
      else if (e.z > MAP.gateZ + 1.5) k += 1 + 2 * Math.min(1, (e.z - MAP.gateZ) / (MAP.flameZ - MAP.gateZ));
      else if (s.gateHp <= 0) k += 0.3;
    }
    return k;
  }
  update(dt) {
    const w = this.warden;
    if (!w || !w.alive) { this.trip = null; return; }
    if (this.trip) { this.trip.t += dt; if (this.trip.t >= this.trip.dur) this._arrive(); return; }
    if (!CITADEL.roam) return;
    const sc = [0, 1, 2, 3].map(i => this.threat(this.sims[i]));
    let best = this.post;
    for (let i = 0; i < 4; i++) if (sc[i] > sc[best]) best = i;
    if (best === this.post || !(sc[best] > 0) || this.t - this.since < CITADEL.minStay) return;
    const cur = sc[this.post];
    if (cur > 0 && sc[best] < cur * CITADEL.switchMul + CITADEL.switchAdd) return;
    this._go(best);
  }
  // Warden forlater siden han står på og går langs ringveien rundt citadellet.
  _go(si) {
    const w = this.warden, from = this.sims[this.post];
    const p = sideToWorld(this.post, w.x, w.z), q = sideToWorld(si, 0, MAP.flameZ - CITADEL.ring);
    if (from) {
      const i = from.units.indexOf(w); if (i >= 0) from.units.splice(i, 1);
      for (const u of from.units) if (u.target === w) u.target = null;
    }
    const a0 = Math.atan2(p.x, p.z - MAP.flameZ), a1 = Math.atan2(q.x, q.z - MAP.flameZ), r0 = Math.hypot(p.x, p.z - MAP.flameZ);
    const da = Math.atan2(Math.sin(a1 - a0), Math.cos(a1 - a0));
    const dur = (Math.abs(da) * CITADEL.ring + Math.abs(r0 - CITADEL.ring)) / (w.T.speed * CITADEL.pace);
    this.trip = { from: this.post, to: si, a0, da, r0, t: 0, dur: Math.max(0.5, dur) };
    this.moves.push({ from: this.post, to: si, t: this.t });
    this.post = si; w.target = null; w.moving = true;
  }
  _arrive() {
    const tr = this.trip, s = this.sims[tr.to], w = this.warden;
    this.trip = null; this.since = this.t;
    w.x = w.homeX = 0; w.z = w.homeZ = MAP.flameZ - CITADEL.ring; w.facing = 0; w.target = null; w.moving = false;
    if (s && !s.units.includes(w)) { s.units.push(w); s.warden = w; }
  }
  // Hvor Warden er i verden mens han går (for tegningen).
  tripPos() {
    const tr = this.trip, k = Math.min(1, tr.t / tr.dur), r = tr.r0 + (CITADEL.ring - tr.r0) * Math.min(1, k * 3), a = tr.a0 + tr.da * k;
    const sg = tr.da >= 0 ? 1 : -1;
    return { x: Math.sin(a) * r, z: MAP.flameZ + Math.cos(a) * r, facing: Math.atan2(Math.cos(a) * sg, -Math.sin(a) * sg) };
  }
  // En fiende slår på skjoldet: Warden betaler med helsen sin.
  hit(sim, u) {
    const w = this.warden;
    if (!w || !w.alive) return;
    this.hits[sim.si] = (this.hits[sim.si] || 0) + 1;
    sim._hurt(w, u.T.dmg * CITADEL.share, u.type);
    sim.events.push({ kind: 'shield', from: u, fell: !w.alive });
  }
}
// Lagspill (versjon 36, Runes valg): wavene er svakere når fire sider deler én Warden. Hver side får fiender med
// HP × k og skade × √k. Alene holder du de første wavene fordi Warden dreper det som slipper gjennom porten; i lag må
// han dele seg på fire, så de første wavene trenger mest hjelp (early til og med wave `until`, late etter).
const TEAM = { early: 0.45, late: 0.75, until: 5 };
const teamK = n => n <= TEAM.until ? TEAM.early : TEAM.late;
const teamScale = (sc, n) => { const k = teamK(n); return Object.assign({}, sc, { hp: sc.hp * k, dmg: sc.dmg * Math.sqrt(k) }); };
// Lagets wave: alle sidene kjøres i takt, så Warden kan gå mellom dem. Når fienden når flammen på én side, taper hele laget.
// Returnerer true når alle sidene er ferdige.
function teamStep(sims, dt) {
  for (const s of sims) if (s && !s.result) s.step(dt);
  const lost = sims.find(s => s && s.result && s.result.reason === 'Fienden nådde flammen' && !s.result.team);
  if (lost) sims.forEach(s => { if (s && !s.result) s.result = { win: false, reason: 'Fienden nådde flammen', team: true, from: lost.si }; else if (s && s !== lost && s.result.win) s.result = { win: false, reason: 'Fienden nådde flammen', team: true, from: lost.si }; });
  return !sims.some(s => s && !s.result);
}
"""

MATE = r"""
// Lagkamerat styrt av computeren (versjon 34, test av lagspill). Han holder én side av Bastionen (si = 1 øst, 2 sør,
// 3 vest) med samme waves og den samme fornuftige boten som rivalen, men sender ingenting.
class Mate {
  constructor(si) { this.si = si; this.ec = new Econ(); this.army = []; this.t = 45; this.alive = true; this.sim = null; this.wi = -1; this.hold = null; rivalBot(RIVAL_L, this.ec, this.army, 0); this.makeView(); }
  makeView() { const ec = this.ec; this.view = new Sim(withHero(this.army, ec), { types: ec.types(TYPES), enemies: [], gateHp: ec.gateHp, gateMax: ec.gateMax(), archers: ARCHERS[ec.archers].count, wallgear: ec.wallgear, warden: false, si: this.si }); }
  running() { return !!(this.sim && !this.sim.result); }
  begin(wi, citadel) {
    const ec = this.ec, W = WAVES[wi];
    ec.tick(this.t); this.wi = wi;
    rivalBot(RIVAL_L, ec, this.army, wi);
    this.sim = new Sim(withHero(this.army, ec), { types: ec.types(TYPES, teamScale(W.scale, W.n)), enemies: buildWave(W), gateHp: ec.gateHp, gateMax: ec.gateMax(), archers: ARCHERS[ec.archers].count, wallgear: ec.wallgear, warden: false, citadel, si: this.si });
  }
  end() {
    const ec = this.ec, sim = this.sim, W = WAVES[this.wi];
    if (!sim) return this.hold;
    ec.tick(sim.t); ec.gateHp = sim.gateHp; this.t = RIVAL_BREAK;
    let bounty = 0; sim.units.forEach(u => { if (u.side === 'e' && !u.alive) bounty += BOUNTY[u.type] || 0; });
    ec.add({ gold: bounty });
    const win = !!(sim.result && sim.result.win);
    if (win) ec.add({ gold: waveBonus(W.n) });
    const lost = !!(sim.result && sim.result.reason === 'Fienden nådde flammen' && !sim.result.team);
    this.hold = { wave: W.n, win, lost, gate: Math.round(sim.gateHp), gateMax: ec.gateMax(), army: this.army.length, tier: ec.barracks + 1, leaks: sim.leaks };
    this.sim = null;
    if (!(sim.result && sim.result.reason === 'Fienden nådde flammen')) rivalBot(RIVAL_L, ec, this.army, Math.min(WAVES.length - 1, this.wi + 1));
    this.makeView();
    return this.hold;
  }
}
"""

UI = r"""
  // ---------- Flammeskjoldet og Warden mellom sidene (versjon 34) ----------
  const shieldMat = new THREE.MeshBasicMaterial({ color: 0xffcf5a, transparent: true, opacity: 0.14, side: THREE.DoubleSide, depthWrite: false });
  const shieldDome = new THREE.Mesh(new THREE.SphereGeometry(CITADEL.shieldR, 40, 14, 0, Math.PI * 2, 0, Math.PI / 2), shieldMat);
  shieldDome.position.set(0, 0, MAP.flameZ); shieldDome.scale.y = 1.15; shieldDome.castShadow = false; shieldDome.renderOrder = 5; scene.add(shieldDome);
  const shieldRing = new THREE.Mesh(new THREE.RingGeometry(CITADEL.shieldR - 0.25, CITADEL.shieldR + 0.1, 64), new THREE.MeshBasicMaterial({ color: 0xffd27a, transparent: true, opacity: 0.5, side: THREE.DoubleSide, depthWrite: false }));
  shieldRing.rotation.x = -Math.PI / 2; shieldRing.position.set(0, 0.06, MAP.flameZ); scene.add(shieldRing);
  let shieldFlash = 0;
  const sideName = i => i ? SIDES[i].name : 'Nord (din side)';
  // Warden tegnes her når han står på en annen side eller går langs ringveien.
  function syncWarden(dt) {
    const C = sim && sim.citadel, w = C && C.warden;
    const up = !!(C && C.shieldUp());
    shieldDome.visible = up; shieldRing.visible = up;
    shieldFlash = Math.max(0, shieldFlash - dt * 1.6);
    shieldMat.opacity = 0.13 + shieldFlash * 0.22 + (reduceMotion ? 0 : Math.sin(animT * 2.2) * 0.03);
    shieldRing.material.opacity = 0.55 + shieldFlash * 0.45;
    if (!C || !w) return;
    // Meldinger: Warden bytter side, skjoldet tar slag, Warden faller.
    C.told = C.told || { moves: 0, hits: [0, 0, 0, 0], fell: false };
    if (C.moves.length > C.told.moves) {
      const m = C.moves[C.moves.length - 1]; C.told.moves = C.moves.length;
      toast(m.to ? `Warden løper langs ringveien til ${SIDES[m.to].name}. Fienden er inne ved flammen der.` : 'Warden kommer tilbake til din side.');
    }
    for (let i = 0; i < 4; i++) if (C.hits[i] && !C.told.hits[i]) {
      C.told.hits[i] = 1;
      toast(`Fiender slår på flammeskjoldet fra ${sideName(i)}. Hvert slag tar av Wardens helse${C.post === i && !C.trip ? '.' : ', og han er på vei.'}`);
    }
    if (!w.alive && !C.told.fell && state.phase === 'battle') { C.told.fell = true; toast('Warden falt. Flammeskjoldet er borte, og flammen står åpen!'); }
    if (sim.units.includes(w)) return;
    const v = visuals.get(w.id); if (!v) return;
    let p, f;
    if (C.trip) { p = C.tripPos(); f = p.facing; } else { p = sideToWorld(C.post, w.x, w.z); f = w.facing + SIDES[C.post].rot; }
    if (!w.alive) {
      v.deadT += dt; v.rig.rotation.x = -Math.min(1, v.deadT / 0.4) * Math.PI / 2; v.g.userData.ring.visible = false; v.bar.visible = false;
      if (v.deadT > 2.4) v.g.visible = false;
      return;
    }
    v.g.visible = true; v.g.userData.ring.visible = true; v.rig.rotation.x = 0;
    v.g.position.set(p.x, 0, p.z);
    let d = f - v.g.rotation.y; d = Math.atan2(Math.sin(d), Math.cos(d)); v.g.rotation.y += d * Math.min(1, dt * 10 || 1);
    if ((C.trip || w.moving) && !reduceMotion) { v.bob += dt * 12; v.rig.position.y = Math.abs(Math.sin(v.bob)) * 0.08; } else v.rig.position.y = 0;
    if (v.lunge > 0) { v.lunge -= dt; v.rig.position.z = Math.sin((v.lunge / 0.14) * Math.PI) * 0.3; } else v.rig.position.z = 0;
    if (v.rig.userData.anim) runAnim(v, animT);
    const ratio = Math.max(0, w.hp / w.maxHp);
    v.bar.visible = ratio < 0.999;
    if (v.bar.visible) { v.bar.position.set(p.x, v.height + 0.35, p.z); v.bar.quaternion.copy(camera.quaternion); v.fill.scale.x = Math.max(0.001, ratio); }
  }
  // Lagkameratene på øst, sør og vest: hver side tegnes i sine egne koordinater, snudd rundt flammen.
  let mateVis = [null, new Map(), new Map(), new Map()], mateVisSim = [];
  let sideGates = null;
  function clearMate(i) { mateVis[i].forEach(v => { scene.remove(v.g); scene.remove(v.bar); }); mateVis[i] = new Map(); }
  function clearMates() { for (let i = 1; i < 4; i++) { clearMate(i); mateVisSim[i] = null; } }
  const matesRunning = () => state.team && state.mates.some(m => m && m.running());
  function syncMates(dt) {
    if (!sideGates && typeof sideKits !== 'undefined') sideGates = sideKits.map(k => { const a = []; k.traverse(o => { if (o.isMesh && (o.material === mats.gate || o.material === mats.gateBand)) a.push(o); }); return a; });
    const w = sim && sim.citadel && sim.citadel.warden;
    for (let i = 1; i < 4; i++) {
      const m = state.team ? state.mates[i] : null, s = m ? (m.sim || m.view) : null;
      if (s !== mateVisSim[i]) { clearMate(i); mateVisSim[i] = s; }
      if (sideGates && sideGates[i]) sideGates[i].forEach(o => { o.visible = !s || s.gateHp > 0; });
      if (!s) continue;
      const rot = SIDES[i].rot, o3 = o => { const p = sideToWorld(i, o.x, o.z); return { x: p.x, y: o.y, z: p.z }; };
      for (const e of s.events) {
        if (e.kind === 'shot') addShot(o3(e.from), o3(e.to), e.type);
        else if (e.kind === 'swing') { const v = e.from === w ? visuals.get(w.id) : mateVis[i].get(e.from.id); if (v) v.lunge = 0.14; }
        else if (e.kind === 'shield') { shieldFlash = 1; if (Math.random() < 0.4) sfx('gate'); }
      }
      s.events.length = 0;
      for (const u of s.units) {
        if (u === w) continue;
        let v = mateVis[i].get(u.id);
        if (!v && u.alive) { v = buildUnit(u); v.bar.visible = false; mateVis[i].set(u.id, v); }
        if (!v) continue;
        if (!u.alive) { v.deadT += dt; v.rig.rotation.x = -Math.min(1, v.deadT / 0.4) * Math.PI / 2; v.g.userData.ring.visible = false; if (v.deadT > 2.4) v.g.visible = false; continue; }
        const p = sideToWorld(i, u.x, u.z);
        v.g.position.set(p.x, 0, p.z);
        let d = u.facing + rot - v.g.rotation.y; d = Math.atan2(Math.sin(d), Math.cos(d)); v.g.rotation.y += d * Math.min(1, dt * 10 || 1);
        if (u.moving && !reduceMotion) { v.bob += dt * 12; v.rig.position.y = Math.abs(Math.sin(v.bob)) * 0.08; } else v.rig.position.y = 0;
        if (u.T.flies) { const ty = u.atGate || s.gateHp <= 0 ? 0.4 : 4.5; v.fy = v.fy == null ? ty : v.fy + (ty - v.fy) * Math.min(1, dt * 2); v.rig.position.y += v.fy; }
        if (v.lunge > 0) { v.lunge -= dt; v.rig.position.z = Math.sin((v.lunge / 0.14) * Math.PI) * 0.3; } else v.rig.position.z = 0;
        if (v.rig.userData.anim) runAnim(v, animT);
      }
    }
  }
  function teamHtml() {
    const st = i => { const m = state.mates[i]; if (!m) return ''; const h = m.hold; return `<span>${SIDES[i].name}: ${m.running() ? 'kjemper' : h ? `wave ${h.wave} ${h.lost ? 'tapt' : h.win ? 'holdt' : 'porten tok skade'}${h.leaks ? `, ${h.leaks} lekket` : ''}` : 'klar'} · ${m.army.length} soldater</span>`; };
    return `<section class="rival"><label class="vs-tog"><input type="checkbox" id="team-toggle" ${state.team ? 'checked' : ''}> Lagkamerater på øst, sør og vest (computer) ${tipIcon('Test av lagspill: computeren holder de tre andre sidene av Bastionen med de samme wavene. Lekker en side, går fienden mot den felles flammen. Flammeskjoldet stopper dem, men hvert slag tar av Wardens helse, og Warden løper langs ringveien dit kampen er. Taper én side, taper hele laget. Wavene er svakere i lag (wave 1–5 på 45 %, resten på 75 %), fordi fire sider deler én Warden. Kan bare slås av eller på før første wave.')}</label>
      ${state.team ? `<div class="rv-h" style="flex-direction:column;align-items:flex-start;gap:2px">${[1, 2, 3].map(st).join('')}</div><p class="note">Trykk «Bastion» for å se hele byen og Warden som går mellom sidene.</p>` : ''}</section>`;
  }
"""


def apply(s):
    # Logikk: Citadel før Sim brukes, Mate etter rivalens hjelpere.
    s = sub(s, "class Rival {", LOGIC + MATE + "class Rival {")
    s = sub(s, "      this.units.push(w); this.warden = w;\n    }\n",
            "      this.units.push(w); this.warden = w;\n    }\n"
            "    // Flammeskjoldet og Warden mellom sidene (versjon 34): alle sider med samme citadell deler Warden og skjoldet.\n"
            "    this.si = cfg.si || 0;\n"
            "    this.citadel = cfg.citadel || (this.warden ? new Citadel() : null);\n"
            "    if (this.citadel) this.citadel.attach(this, this.si);\n")
    s = sub(s, "    this.t += dt;\n    const players = this.alive('p'), enemies = this.alive('e');",
            "    this.t += dt;\n    if (this.citadel) this.citadel.tick(this);\n    const players = this.alive('p'), enemies = this.alive('e');")
    s = sub(s, "    } else {\n      u.atGate = false;\n      this._moveTo(u, clamp(u.x, -2, 2), MAP.flameZ, dt);",
            "    } else {\n      u.atGate = false;\n"
            "      // Flammeskjoldet: så lenge Warden lever, stopper fienden ved citadellet og slår på skjoldet.\n"
            "      // De sprer seg langs skjoldet foran citadellet i stedet for å stå i én klump.\n"
            "      const C = this.citadel;\n"
            "      if (C && C.blocks(this)) {\n"
            "        const R = CITADEL.shieldR + 0.3 + (u.T.radius || 0.4), dz = u.z - MAP.flameZ;\n"
            "        if (Math.hypot(u.x, dz) <= R + 0.2) { u.atShield = true; u.facing = Math.atan2(-u.x, -dz); if (u.cd <= 0) { u.cd = u.T.interval; C.hit(this, u); } return; }\n"
            "        const tx = clamp(u.x, -R * 0.6, R * 0.6);\n"
            "        u.atShield = false; this._moveTo(u, tx, MAP.flameZ - Math.sqrt(R * R - tx * tx), dt); return;\n"
            "      }\n"
            "      u.atShield = false;\n"
            "      this._moveTo(u, clamp(u.x, -2, 2), MAP.flameZ, dt);")
    # Evnene virker bare der Warden står.
    s = sub(s, "    const w = this.warden; if (!w || !w.alive || !lv) return -1;",
            "    const w = this.warden; if (!w || !w.alive || !lv || !this.units.includes(w)) return -1;")

    # ---------- UI ----------
    s = sub(s, "      types: ec.types(TYPES, state.versus ? versusScale(W) : W.scale),",
            "      types: ec.types(TYPES, state.team ? teamScale(state.versus ? versusScale(W) : W.scale, W.n) : state.versus ? versusScale(W) : W.scale),")
    s = sub(s, "versus: true, flags: 0,", "versus: true, team: false, mates: [], flags: 0,")
    s = sub(s, "  // ---------- 1 mot 1: Send-fanen ----------", UI + "\n  // ---------- 1 mot 1: Send-fanen ----------")
    # Evnene brukes der Warden står, også på en annen side.
    s = sub(s, "    const n = sim.wardenAbility(k, lv);",
            "    const n = ((sim.citadel && sim.citadel.simOf()) || sim).wardenAbility(k, lv);")
    # Kampen: alle sidene i takt. Waven er over når hele laget er ferdig.
    s = sub(s, "      while (state.acc >= STEP && n < 12 && !sim.result) { sim.step(STEP); state.econ.tick(STEP); state.acc -= STEP; n++; }\n"
               "      handleEvents();\n      if (sim.result) finish();",
            "      while (state.acc >= STEP && n < 12 && (!sim.result || matesRunning())) {\n"
            "        if (!sim.result) state.econ.tick(STEP);\n"
            "        if (state.team) teamStep([sim].concat(state.mates.slice(1).map(m => m && m.sim)), STEP); else sim.step(STEP);\n"
            "        state.acc -= STEP; n++;\n      }\n"
            "      handleEvents();\n"
            "      if (sim.result && sim.result.win && matesRunning() && !state.mateWaitTold) { state.mateWaitTold = true; toast('Du holdt! Lagkameratene kjemper fortsatt, og waven er over når hele laget er ferdig.'); }\n"
            "      if (sim.result && !matesRunning()) finish();")
    s = sub(s, "  function finish() {\n    const r = sim.result, W = curWave(), ec = state.econ;",
            "  function finish() {\n"
            "    if (state.team) state.mates.forEach(m => { if (m && m.sim) m.end(); });\n"
            "    state.mateWaitTold = false;\n"
            "    if (sim.result && sim.result.team && sim.result.from) setTimeout(() => toast(`Fienden nådde flammen fra ${SIDES[sim.result.from].name}. Hele laget taper.`), 300);\n"
            "    const r = sim.result, W = curWave(), ec = state.econ;")
    s = sub(s, "    if (state.versus && state.rival.alive) { state.rival.begin(state.wave, state.sendQueue);",
            "    if (state.team) state.mates.forEach(m => { if (m) m.begin(state.wave, sim.citadel); });\n"
            "    if (state.versus && state.rival.alive) { state.rival.begin(state.wave, state.sendQueue);")
    s = sub(s, "    state.rival = new Rival(); state.flags = 0;",
            "    clearMates(); state.mates = state.team ? [null, new Mate(1), new Mate(2), new Mate(3)] : [];\n"
            "    state.rival = new Rival(); state.flags = 0;")
    s = sub(s, "    $('#pane-send').innerHTML = onlineHtml() + ", "    $('#pane-send').innerHTML = onlineHtml() + teamHtml() + ")
    s = sub(s, "    const vt = e.target.closest('#vs-toggle');",
            "    const tt = e.target.closest('#team-toggle'); if (tt) { if (state.wave === 0 && state.phase === 'build') { state.team = tt.checked; clearMates(); state.mates = state.team ? [null, new Mate(1), new Mate(2), new Mate(3)] : []; rebuild(); renderPanel(); } else { tt.checked = state.team; toast('Kan bare endres før første wave. Start en ny kamp for å bytte.'); } return; }\n"
            "    const vt = e.target.closest('#vs-toggle');")
    s = sub(s, "    syncRival(vdt); drawMinimap(dt);", "    syncRival(vdt); syncWarden(vdt); syncMates(vdt); drawMinimap(dt);")
    s = sub(s, "      else if (e.kind === 'gate') { gateFlash = 0.15; sfx('gate'); }",
            "      else if (e.kind === 'gate') { gateFlash = 0.15; sfx('gate'); }\n"
            "      else if (e.kind === 'shield') { shieldFlash = 1; if (Math.random() < 0.4) sfx('gate'); }")
    return s
