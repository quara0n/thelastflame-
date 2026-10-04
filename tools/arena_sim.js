// Computer-vs-computer arena duels after waves 8, 18, 28. Usage: node tools/arena_sim.js
const L = require('./game_sim.js').load();
for (let m = 0; m < 6; m++) {
  const A = new L.Rival(), B = new L.Rival(); let toA = [], toB = []; const res = [];
  for (let wi = 0; wi < 28; wi++) {
    const ra = A.playWave(wi, toA), rb = B.playWave(wi, toB); toA = rb.out.map(s => ({ ...s, by: 'p' })); toB = ra.out.map(s => ({ ...s, by: 'p' }));
    if (ra.lost || rb.lost) break;
    if ([8, 18, 28].includes(wi + 1)) {
      const sim = L.arenaSim(A.army, A.ec.types(L.TYPES), B); let o = L.arenaOutcome(sim);
      while (!o.done) { sim.step(1 / 15); o = L.arenaOutcome(sim); }
      res.push(`w${wi + 1}: A ${A.army.length}u vs B ${B.army.length}u -> ${o.win ? 'A' : 'B'} wins in ${Math.round(sim.t)}s (${Math.round(o.mine * 100)}% vs ${Math.round(o.theirs * 100)}%)`);
    }
  }
  console.log(res.join(' | '));
}
