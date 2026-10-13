// Team of four bots around one flame (version 34): north, east, south and west play the same wave in lockstep and
// share the Warden and the flame shield. The team loses when an enemy reaches the flame on any side.
// Usage: node team_sim.js [runs] [variant] ['{"early":0.45,"late":0.8}']   (overrides TEAM, the team-play wave factors)
//   variant: roam (default) | fixed (Warden stays north) | old (fixed, no shield)
const G = require('./game_sim.js'), { bot } = G;

// Same loader as game_sim.js (so the bot gets everything it uses there), plus the team pieces.
function load(extra) {
  const L = G.load((extra || '') + ';globalThis.__team = { Citadel, CITADEL, teamStep, teamScale, TEAM };');
  return Object.assign(L, globalThis.__team);
}

function playTeam(L) {
  const P = [0, 1, 2, 3].map(() => ({ ec: new L.Econ(), army: [] }));
  const log = [];
  let t = 45;
  for (let wi = 0; wi < L.WAVES.length; wi++) {
    const W = L.WAVES[wi];
    P.forEach(p => { p.ec.tick(t); bot(L, p.ec, p.army, wi); });
    const cit = new L.Citadel();
    const sims = P.map((p, si) => new L.Sim(L.withHero(p.army, p.ec), { types: p.ec.types(L.TYPES, L.teamScale(W.scale, W.n)), enemies: L.buildWave(W), gateHp: p.ec.gateHp, gateMax: p.ec.gateMax(), archers: L.ARCHERS[p.ec.archers].count, wallgear: p.ec.wallgear, warden: si === 0, citadel: cit, si, bot: si === 0 ? p.ec : undefined }));
    while (!L.teamStep(sims, 1 / 15)) {}
    P.forEach((p, si) => {
      const sim = sims[si];
      p.ec.tick(sim.t); p.ec.gateHp = sim.gateHp;
      let bounty = 0; sim.units.forEach(u => { if (u.side === 'e' && !u.alive) bounty += L.BOUNTY[u.type] || 0; });
      p.ec.add({ gold: bounty });
      if (sim.result.win) p.ec.add({ gold: L.waveBonus(W.n) });
      L.heroAfterWave(p.ec, sim, true);
    });
    const lost = sims.find(s => s.result.reason === 'Fienden nådde flammen' && !s.result.team);
    log.push({ w: W.n, moves: cit.moves.length, shieldHits: cit.hits.reduce((a, b) => a + b, 0), wardenAlive: cit.warden.alive, lostFrom: lost ? lost.si : null, leakSides: sims.filter(s => s.leaks).length });
    if (lost) break;
    t = 55;
  }
  return log;
}

module.exports = { load, playTeam };
if (require.main === module) {
  const runs = +(process.argv[2] || 10), variant = process.argv[3] || 'roam';
  const extra = (process.argv[4] ? `;Object.assign(TEAM, ${process.argv[4]});` : '') + (variant === 'fixed' ? ';CITADEL.roam = false;' : variant === 'old' ? ';CITADEL.roam = false; CITADEL.shield = false;' : '');
  const L = load(extra);
  const ends = [], from = [0, 0, 0, 0];
  let moves = 0, hits = 0, waves = 0;
  for (let r = 0; r < runs; r++) {
    const log = playTeam(L);
    ends.push(log.length);
    log.forEach(x => { moves += x.moves; hits += x.shieldHits; waves++; });
    const last = log[log.length - 1]; if (last.lostFrom != null) from[last.lostFrom]++;
  }
  ends.sort((a, b) => a - b);
  console.log(`${variant}: team reached waves`, ends.join(' '));
  console.log(`median ${ends[Math.floor(ends.length / 2)]}, mean ${(ends.reduce((a, b) => a + b, 0) / ends.length).toFixed(1)}, reached 20: ${ends.filter(e => e >= 20).length}/${runs}, reached 30: ${ends.filter(e => e >= 30).length}/${runs}`);
  console.log(`lost from north/east/south/west: ${from.join('/')}; Warden moves per wave ${(moves / waves).toFixed(2)}, shield hits per wave ${(hits / waves).toFixed(1)}`);
}
