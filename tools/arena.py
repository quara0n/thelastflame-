"""Arena duel against the computer at waves 8, 18 and 28 (4 Oct 2026). Applied by build_v2.py after versus.py.
After the wave, a copy of your army meets a copy of the rival's army on the battlefield for up to 60 seconds. No real
units die. Last army standing wins; at time-out the side with the larger share of health left wins. The winner gets
resources and a Champion flag."""
from patch import sub

CSS = """
.arenacard { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); width: min(380px, calc(100% - 20px)); max-height: calc(100% - 20px); overflow-y: auto; z-index: 15;
  background: linear-gradient(180deg, rgba(42, 26, 8, .97), rgba(18, 14, 10, .97)); border: 1px solid #e9a23b; border-radius: 14px; padding: 16px; text-align: center; box-shadow: 0 20px 50px rgba(0, 0, 0, .6); display: flex; flex-direction: column; gap: 8px; }
.arenacard.lost { border-color: #8a3a34; }
.arenacard .ac-eyebrow { font: 600 11px var(--body); letter-spacing: .16em; text-transform: uppercase; color: var(--flame); }
.arenacard h2 { font-family: var(--display); font-size: 24px; letter-spacing: .04em; text-transform: none; color: var(--fg); margin: 0; }
.ac-vs { display: grid; grid-template-columns: 1fr auto 1fr; gap: 8px; align-items: center; }
.ac-side { display: flex; flex-direction: column; gap: 2px; background: rgba(143, 179, 214, .08); border: 1px solid #3a4a5c; border-radius: 10px; padding: 8px 6px; font-size: 12px; color: var(--muted); }
.ac-side b { color: #9fc4de; font-family: var(--display); font-size: 15px; }
.ac-side em { font-style: normal; color: var(--fg); font-weight: 600; }
.ac-side.foe { background: rgba(163, 90, 224, .08); border-color: #5a3a7a; }
.ac-side.foe b { color: #c99af0; }
.ac-vote { color: var(--flame); }
.ac-mid { font-family: var(--display); font-size: 22px; color: var(--flame); }
.ac-note { font-size: 12px; color: var(--muted); margin: 0; }
.ac-prize { font: 600 12.5px var(--body); color: #ffd76a; }
.ac-flags { font-size: 12px; color: var(--fg); }
.ac-go { align-self: center; background: var(--flame); color: var(--flame-ink); border: 0; border-radius: 8px; padding: 10px 22px; font-weight: 700; font-size: 15px; }
.ac-go span { font-family: var(--mono); margin-left: 6px; }
"""

def apply(s):
    s = sub(s, "#om-remove { color: #f0a59d; }", "#om-remove { color: #f0a59d; }" + CSS)
    s = sub(s, "const RIVAL_BREAK = 55;", """const RIVAL_BREAK = 55;
// Arena: etter disse wavene møtes hærene. Premien vokser for hver arena.
const ARENA_WAVES = [8, 18, 28], ARENA_TIME = 60;
const arenaPrize = n => { const k = ARENA_WAVES.indexOf(n) + 1; return { gold: 40 * k, timber: 20 * k, stone: 20 * k, coal: 10 * k }; };
// Bygger arenakampen: din hær (kopi) mot rivalens hær (kopi), speilvendt på andre siden av slagmarken.
function arenaSim(playerArmy, playerTypes, rival) {
  const rt = rival.ec.types(TYPES);
  const foes = rival.army.map(a => {
    const T = Object.assign({}, levelType(rt[a.type], a.type, a.level || 0), { side: 'e', aggro: 60 });
    const c = cellCenter(a.col, a.row);
    return { type: a.type, x: -c.x, z: -(c.z - MAP.gridZ0) - 4, T };
  });
  const army = playerArmy.map(a => Object.assign({}, a, { order: TYPES[a.type].ranged ? 'follow' : 'advance', squad: null, delay: 0 }));
  return new Sim(army, { types: playerTypes, enemies: foes, warden: false, gateHp: 1e6, gateMax: 1e6, archers: 0 });
}
function arenaOutcome(sim) {
  const p = sim.units.filter(u => u.side === 'p'), e = sim.units.filter(u => u.side === 'e');
  const share = l => l.reduce((a, u) => a + Math.max(0, u.alive ? u.hp : 0), 0) / Math.max(1, l.reduce((a, u) => a + u.maxHp, 0));
  const pa = p.some(u => u.alive), ea = e.some(u => u.alive);
  const done = !pa || !ea || sim.t >= ARENA_TIME;
  return { done, win: ea ? (pa ? share(p) >= share(e) : false) : true, mine: share(p), theirs: share(e) };
}""")
    # Sim: en fiende kan ha sine egne tall (rivalens soldater).
    s = sub(s, "if (e.sent) m.sent = e.sent; this.units.push(m); }", "if (e.sent) m.sent = e.sent; if (e.T) { m.T = e.T; m.side = 'e'; m.hp = m.maxHp = e.T.hp; m.facing = 0; } this.units.push(m); }")
    # Auraen til Warbanner Captain virker også for rivalens kapteiner i arenaen.
    s = sub(s, "    this.captains = players.filter(u => u.T.aura);", "    this.captains = players.filter(u => u.T.aura);\n    this.foeCaptains = enemies.filter(u => u.T.aura && u.T.side === 'e' && u.T.ranged !== true && TYPES[u.type] && TYPES[u.type].side === 'p');")
    s = sub(s, "    if (u.side === 'p' && this.captains) {", "    if (u.side === 'e' && this.foeCaptains && this.foeCaptains.length) {\n      const fc = this.foeCaptains.filter(c => c.alive && c !== u && dist(c, u) < c.T.aura);\n      if (fc.length) mult *= fc.some(c => c.T.rally) ? 1.3 : 1.2;\n    }\n    if (u.side === 'p' && this.captains) {")
    # Taunt og skjoldmur virker for begge sider (betyr noe i arenaen, der rivalens soldater er fiender).
    s = sub(s, "if (f.T.taunt && u.side === 'e' && d < f.T.taunt && !u.T.hunts) pref -= 6;", "if (f.T.taunt && u.side !== f.side && d < f.T.taunt && !u.T.hunts) pref -= 6;")
    s = sub(s, "if (u.T.ranged && t.side === 'p' && u.side === 'e' && this._sheltered(t)) mult *= 0.75;", "if (u.T.ranged && t.side !== u.side && this._sheltered(t)) mult *= 0.75;")
    s = sub(s, "return this.units.some(a => a.alive && a !== t && a.side === 'p' && a.T.shieldwall && a.z < t.z && t.z - a.z < 2.6 && Math.abs(a.x - t.x) < 1.3);",
               "const f = t.side === 'p' ? 1 : -1;   // spillerens front er mot lavere z, rivalens mot høyere\n    return this.units.some(a => a.alive && a !== t && a.side === t.side && a.T.shieldwall && f * (t.z - a.z) > 0 && f * (t.z - a.z) < 2.6 && Math.abs(a.x - t.x) < 1.3);")
    s = sub(s, "    versus: true, rival: new Rival(),", "    versus: true, flags: 0, rivalFlags: 0, rival: new Rival(),")
    # Etter wave 8, 18 og 28: arenaen starter før byggefasen.
    s = sub(s, "      if (state.versus && state.incoming.length) setTimeout(() => toast(`Rivalen sender deg ${state.incoming.length} skapninger i wave ${curWave().n}. Se «Neste wave».`), 2800);",
               "      if (state.versus && state.incoming.length) setTimeout(() => toast(`Rivalen sender deg ${state.incoming.length} skapninger i wave ${curWave().n}. Se «Neste wave».`), 2800);\n"
               "      if (state.versus && state.rival.alive && ARENA_WAVES.includes(W.n) && state.army.length && state.rival.army.length) startArena(W.n);")
    s = sub(s, "    $('#h-gate').textContent = gr > 0 ? `Port ${Math.ceil(sim.gateHp)}` : 'Porten er brutt';",
               "    $('#h-gate').textContent = state.phase === 'arena' ? `Arena ${Math.max(0, Math.ceil(ARENA_TIME - sim.t))} s` : gr > 0 ? `Port ${Math.ceil(sim.gateHp)}` : 'Porten er brutt';")
    s = sub(s, "setTimeout(() => toast(`Rivalen sender deg ${state.incoming.length} skapninger i wave ${curWave().n}. Se «Neste wave».`), 2800);",
               "setTimeout(() => { if (state.phase !== 'arena') toast(`Rivalen sender deg ${state.incoming.length} skapninger i wave ${curWave().n}. Se «Neste wave».`); }, 2800);")
    s = sub(s, "  function primaryAction() {\n", "  function primaryAction() {\n    if (state.phase === 'arena-intro') { beginDuel(state.arenaN); return; }\n    if (state.phase === 'arena') return;\n")
    s = sub(s, "start.textContent = build ? `Start wave ${W.n} nå` : state.phase === 'battle' ?", "start.textContent = build ? `Start wave ${W.n} nå` : state.phase === 'arena-intro' ? 'Til kamp!' : state.phase === 'arena' ? 'Arena pågår …' : state.phase === 'battle' ?")
    s = sub(s, "$('#phase').textContent = build ? 'Byggefase' : state.phase === 'battle' ?", "$('#phase').textContent = build ? 'Byggefase' : state.phase === 'arena' || state.phase === 'arena-intro' ? 'Arena' : state.phase === 'battle' ?")
    s = sub(s, "    } else if (state.phase === 'battle' && !state.paused) {",
               "    } else if (state.phase === 'arena-intro') {\n      arenaIntroTick(dt);\n"
               "    } else if (state.phase === 'arena') {\n"
               "      state.acc += dt * state.speed;\n"
               "      let n = 0;\n"
               "      while (state.acc >= STEP && n < 12 && !state.arena.out.done) { sim.step(STEP); state.acc -= STEP; n++; state.arena.out = arenaOutcome(sim); }\n"
               "      handleEvents();\n"
               "      if (state.arena.out.done) finishArena();\n"
               "    } else if (state.phase === 'battle' && !state.paused) {")
    UI = r"""

  // ---------- Arena: seremonien før og etter duellen ----------
  const arenaRing = new THREE.Group(); arenaRing.visible = false; scene.add(arenaRing);
  (() => {
    const cz = -2, R = 13.5;
    const gl = new THREE.Mesh(new THREE.RingGeometry(R - 0.5, R + 0.5, 64), new THREE.MeshBasicMaterial({ color: 0xe9a23b, transparent: true, opacity: 0.55, side: THREE.DoubleSide }));
    gl.rotation.x = -Math.PI / 2; gl.position.set(0, 0.05, cz); arenaRing.add(gl);
    for (let i = 0; i < 18; i++) {
      const a = i / 18 * Math.PI * 2, x = Math.cos(a) * (R + 1), z = cz + Math.sin(a) * (R + 1);
      arenaRing.add(mesh(new THREE.CylinderGeometry(0.12, 0.16, 2.2, 6), mats.iron, x, 1.1, z));
      arenaRing.add(mesh(new THREE.ConeGeometry(0.28, 0.7, 8), mats.lantern, x, 2.5, z));
    }
  })();
  const arenaCard = document.createElement('div'); arenaCard.className = 'arenacard'; arenaCard.hidden = true; $('.stage').appendChild(arenaCard);
  function hideArenaCard() { arenaCard.hidden = true; }
  // Arenaen kalles inn: kort med lagets champion (stemmes frem; mot computeren er det deg), motstanderen, premien og nedtelling.
  function startArena(n) {
    const prize = arenaPrize(n), r = state.rival;
    state.phase = 'arena-intro'; state.arenaN = n; state.arenaCount = 10;
    arenaRing.visible = true; camGoto(0, -2, PHONE ? 60 : 46, 0.85);
    Sound.setMode('battle'); sfx('horn');
    arenaCard.className = 'arenacard'; arenaCard.hidden = false;
    arenaCard.innerHTML = `<div class="ac-eyebrow">Arena · etter wave ${n}</div><h2>Duell om flagget</h2>
      <div class="ac-vs"><div class="ac-side"><b>Ditt lag</b><span>Champion: <em>Du</em></span><span class="ac-vote">Stemmer: Du 1/1</span><span>${state.army.length} soldater</span></div>
        <div class="ac-mid">VS</div>
        <div class="ac-side foe"><b>Rivalen</b><span>Champion: <em>Computer</em></span><span class="ac-vote">Stemmer: 1/1</span><span>${r.army.length} soldater</span></div></div>
      <p class="ac-note">En kopi av hæren din møter en kopi av hans i ringen. Ingen dør på ekte. Siste hær som står, vinner; etter ${ARENA_TIME} sekunder vinner den med mest helse igjen.</p>
      <div class="ac-prize">Premie: +${prize.gold} gull, +${prize.timber} tømmer, +${prize.stone} stein, +${prize.coal} kull og Champion-flagg</div>
      <div class="ac-flags">Champion-flagg: du ${state.flags}, rivalen ${state.rivalFlags}</div>
      <button type="button" class="ac-go" id="ac-go">Til kamp! <span id="ac-count">10</span></button>`;
    $('#ac-go').onclick = () => { if (state.phase === 'arena-intro') beginDuel(n); };
    renderPanel();
  }
  function arenaIntroTick(dt) {
    const before = Math.ceil(state.arenaCount); state.arenaCount -= dt;
    const now = Math.ceil(Math.max(0, state.arenaCount));
    if (now !== before) { const c = document.getElementById('ac-count'); if (c) c.textContent = now; if (now > 0) sfx('gate'); }
    if (state.arenaCount <= 0) beginDuel(state.arenaN);
  }
  // ---------- Arena ----------
  function beginDuel(n) {
    hideArenaCard();
    state.phase = 'arena'; state.acc = 0; arenaRing.visible = true;
    sim = arenaSim(state.army, state.econ.types(TYPES), state.rival);
    state.arena = { n, out: arenaOutcome(sim) };
    clearVisuals(); clearShots(); sim.units.forEach(u => visuals.set(u.id, buildUnit(u)));
    gridGroup.visible = false; planGroup.visible = false; hover.visible = false;
    Sound.setMode('battle'); sfx('horn');
    camGoto(0, -2, PHONE ? 60 : 46, 0.85);
    renderPanel();
  }
  function finishArena() {
    const a = state.arena, o = a.out, prize = arenaPrize(a.n);
    if (o.win) { state.econ.add(prize); state.flags++; Object.keys(prize).forEach(r => popRes(r, prize[r])); sfx('victory'); }
    else { state.rival.ec.add(prize); state.rivalFlags++; sfx('defeat'); }
    const el = $('#result'); el.hidden = false; el.className = 'result ' + (o.win ? 'win' : 'loss');
    el.innerHTML = `<div class="r-head"><h2>${o.win ? 'Arena: du vant!' : 'Arena: rivalen vant'}</h2><span>${fmtTime(sim.t)}</span></div>
      <p class="bonus">${o.win ? `+${prize.gold} gull, +${prize.timber} tømmer, +${prize.stone} stein, +${prize.coal} kull · Champion-flagg` : `Rivalen fikk ${prize.gold} gull og mer.`}</p>
      <p class="why">Igjen av hæren: din ${Math.round(o.mine * 100)} %, rivalens ${Math.round(o.theirs * 100)} %. Champion-flagg: du ${state.flags}, rivalen ${state.rivalFlags}.</p>
      <p class="note">Ingen units døde på ekte. Byggefasen er i gang.</p>`;
    arenaCard.className = 'arenacard ' + (o.win ? 'won' : 'lost'); arenaCard.hidden = false;
    arenaCard.innerHTML = `<div class="ac-eyebrow">Arena · etter wave ${a.n}</div><h2>${o.win ? 'Du vant duellen!' : 'Rivalen vant duellen'}</h2>
      <p class="ac-note">Igjen av hæren: din ${Math.round(o.mine * 100)} %, rivalens ${Math.round(o.theirs * 100)} %.</p>
      <div class="ac-prize">${o.win ? `+${prize.gold} gull, +${prize.timber} tømmer, +${prize.stone} stein, +${prize.coal} kull · Champion-flagg` : `Rivalen tar premien og flagget.`}</div>
      <div class="ac-flags">Champion-flagg: du ${state.flags}, rivalen ${state.rivalFlags}</div>
      <button type="button" class="ac-go" id="ac-go">Tilbake til byggingen</button>`;
    $('#ac-go').onclick = hideArenaCard; setTimeout(hideArenaCard, 7000);
    if (state.incoming.length) setTimeout(() => { if (state.phase === 'build') toast(`Rivalen sender deg ${state.incoming.length} skapninger i wave ${curWave().n}. Se «Neste wave».`); }, 3000);
    state.phase = 'build'; state.arena = null; arenaRing.visible = false;
    gridGroup.visible = true; planGroup.visible = true;
    Sound.setMode('build');
    camGoto(0, FIELD_TZ, FIELD_DIST, 0.8);
    rebuild(); renderPanel();
  }
"""
    s = sub(s, "  // ---------- 1 mot 1: Send-fanen ----------", UI + "\n  // ---------- 1 mot 1: Send-fanen ----------")
    # Send-fanen viser flaggene og når neste arena kommer.
    s = sub(s, "        <label class=\"vs-tog\"><input type=\"checkbox\" id=\"vs-toggle\"",
               "        <p class=\"note\">Champion-flagg: du ${state.flags}, rivalen ${state.rivalFlags}. ${(() => { const nx = ARENA_WAVES.find(w => w >= W.n); return nx ? `Neste arena: etter wave ${nx}.` : 'Ingen flere arenaer.'; })()}</p>\n"
               "        <label class=\"vs-tog\"><input type=\"checkbox\" id=\"vs-toggle\"")
    s = sub(s, "    state.rival = new Rival(); state.sendQueue = [];", "    state.rival = new Rival(); state.flags = 0; state.rivalFlags = 0; state.arena = null; hideArenaCard(); arenaRing.visible = false; state.sendQueue = [];")
    return s
