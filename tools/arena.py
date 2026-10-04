"""Arena duel against the computer at waves 8, 18 and 28 (4 Oct 2026). Applied by build_v2.py after versus.py.
After the wave, a copy of your army meets a copy of the rival's army on the battlefield for up to 60 seconds. No real
units die. Last army standing wins; at time-out the side with the larger share of health left wins. The winner gets
resources and a Champion flag."""
from patch import sub

def apply(s):
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
    s = sub(s, "  function primaryAction() {\n", "  function primaryAction() {\n    if (state.phase === 'arena') return;\n")
    s = sub(s, "start.textContent = build ? `Start wave ${W.n} nå` : state.phase === 'battle' ?", "start.textContent = build ? `Start wave ${W.n} nå` : state.phase === 'arena' ? 'Arena pågår …' : state.phase === 'battle' ?")
    s = sub(s, "$('#phase').textContent = build ? 'Byggefase' : state.phase === 'battle' ?", "$('#phase').textContent = build ? 'Byggefase' : state.phase === 'arena' ? 'Arena' : state.phase === 'battle' ?")
    s = sub(s, "    } else if (state.phase === 'battle' && !state.paused) {",
               "    } else if (state.phase === 'arena') {\n"
               "      state.acc += dt * state.speed;\n"
               "      let n = 0;\n"
               "      while (state.acc >= STEP && n < 12 && !state.arena.out.done) { sim.step(STEP); state.acc -= STEP; n++; state.arena.out = arenaOutcome(sim); }\n"
               "      handleEvents();\n"
               "      if (state.arena.out.done) finishArena();\n"
               "    } else if (state.phase === 'battle' && !state.paused) {")
    UI = r"""
  // ---------- Arena ----------
  function startArena(n) {
    state.phase = 'arena'; state.acc = 0;
    sim = arenaSim(state.army, state.econ.types(TYPES), state.rival);
    state.arena = { n, out: arenaOutcome(sim) };
    clearVisuals(); clearShots(); sim.units.forEach(u => visuals.set(u.id, buildUnit(u)));
    gridGroup.visible = false; planGroup.visible = false; hover.visible = false;
    Sound.setMode('battle'); sfx('horn');
    camGoto(0, -2, PHONE ? 60 : 46, 0.85);
    toast(`ARENA etter wave ${n}! Hæren din møter rivalens hær. ${ARENA_TIME} sekunder, ingen dør på ekte.`);
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
    toast(o.win ? `Du vant arenaen! +${prize.gold} gull og Champion-flagg.` : 'Rivalen vant arenaen.');
    if (state.incoming.length) setTimeout(() => { if (state.phase === 'build') toast(`Rivalen sender deg ${state.incoming.length} skapninger i wave ${curWave().n}. Se «Neste wave».`); }, 3000);
    state.phase = 'build'; state.arena = null;
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
    s = sub(s, "    state.rival = new Rival(); state.sendQueue = [];", "    state.rival = new Rival(); state.flags = 0; state.rivalFlags = 0; state.arena = null; state.sendQueue = [];")
    return s
