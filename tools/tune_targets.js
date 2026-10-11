// Tunes one strength factor per wave against survival targets (version 33, 11 Oct 2026).
// Unlike tune_waves.js, runs that lose are replaced by copies of runs that held, so every wave is tuned on players who
// really got there (tune_waves.js kept losing runs alive, their armies shrank and late waves came out far too easy).
// Targets: the average bot should lose around wave 22–25, waves 1–5 are gentle, and few reach wave 30.
// Usage: node tune_targets.js [runs=40] [from=1]
const { load, bot } = require('./game_sim.js');
const fs = require('fs');
const L = load();
const R = +(process.argv[2] || 40), FROM = +(process.argv[3] || 1);
// Share of the players who start a wave that should come through it (the flame not reached).
const TARGET = w => w <= 5 ? 0.99 : w <= 9 ? 0.96 : w === 10 ? 0.93 : w <= 19 ? 0.97 : w === 20 ? 0.92 : w <= 22 ? 0.95 : w <= 29 ? 0.72 : 0.6;
const GRID = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.35, 1.5, 1.7, 2, 2.4, 3];
// Waves 1–5 should stay gentle for new players, so they are never made more than 20 % harder than now.
const CAP = w => w <= 5 ? 1.2 : Infinity;
const LOST = 'Fienden nådde flammen';
const clone = st => ({ ec: Object.assign(Object.create(Object.getPrototypeOf(st.ec)), JSON.parse(JSON.stringify(st.ec))), army: JSON.parse(JSON.stringify(st.army)), t: st.t });
const runWave = (st, wi, k) => {
  const W = L.WAVES[wi], ec = st.ec;
  const scale = { ...W.scale, hp: W.scale.hp * k, dmg: W.scale.dmg * Math.sqrt(k) };
  const sim = new L.Sim(L.withHero(st.army, ec), { types: ec.types(L.TYPES, scale), enemies: L.buildWave(W), gateHp: ec.gateHp, gateMax: ec.gateMax(), archers: L.ARCHERS[ec.archers].count, wallgear: ec.wallgear, bot: ec });
  while (!sim.result) sim.step(1 / 15);
  return sim;
};
let states = Array.from({ length: R }, () => ({ ec: new L.Econ(), army: [], t: 45 }));
const K = [];
for (let wi = 0; wi < L.WAVES.length; wi++) {
  states.forEach(st => { st.ec.tick(st.t); bot(L, st.ec, st.army, wi); });
  const held = k => states.filter(st => runWave(clone(st), wi, k).result.reason !== LOST).length / states.length;
  let best = 1;
  if (wi + 1 >= FROM) {
    // Largest factor that still lets the target share through (held falls as k rises).
    let lo = 0, hi = GRID.length - 1;
    if (held(GRID[lo]) < TARGET(wi + 1)) best = GRID[lo];
    else { while (hi - lo > 1) { const m = (lo + hi) >> 1; if (held(GRID[m]) >= TARGET(wi + 1)) lo = m; else hi = m; } best = held(GRID[hi]) >= TARGET(wi + 1) ? GRID[hi] : GRID[lo]; }
    best = Math.min(best, CAP(wi + 1));
  }
  K.push(best);
  const next = [];
  states.forEach(st => {
    const sim = runWave(st, wi, best), ec = st.ec;
    ec.tick(sim.t); ec.gateHp = sim.gateHp;
    let bounty = 0; sim.units.forEach(u => { if (u.side === 'e' && !u.alive) bounty += L.BOUNTY[u.type] || 0; });
    ec.add({ gold: bounty }); if (sim.result.win) ec.add({ gold: L.waveBonus(wi + 1) });
    L.heroAfterWave(ec, sim, true);
    st.t = 55;
    if (sim.result.reason !== LOST) next.push(st);
  });
  const survived = next.length;
  // Replace the runs that lost with copies of runs that held, so the next wave is tuned on real survivors.
  while (next.length && next.length < R) next.push(clone(next[Math.floor(Math.random() * survived)]));
  states = next.length ? next : states;
  const a = states[0].army;
  console.log(`wave ${wi + 1}: factor ${best}  target ${TARGET(wi + 1)}  held ${survived}/${R}  army ${a.length}`);
}
const prev = JSON.parse(fs.readFileSync(__dirname + '/wave_factors.json', 'utf8'));
const out = K.map((k, i) => +((prev[i] || 1) * k).toFixed(3));
fs.writeFileSync(__dirname + '/wave_factors.json', JSON.stringify(out));
console.log('combined:', JSON.stringify(out));
console.log(JSON.stringify(K));
