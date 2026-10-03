// Tunes one strength factor per wave so a sensible bot player holds each wave at a target rate.
// "Holds" = wave won and the gate still standing.
const { load } = require('./game_sim.js');
const fs = require('fs');
const L = load();
const R = +(process.argv[2] || 16);
const TARGET = w => w <= 4 ? 1.0 : w <= 8 ? 0.94 : w === 9 ? 0.88 : w === 10 ? 0.75 : w <= 15 ? 0.88 : w <= 19 ? 0.8 : 0.6;
const GRID = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.25, 1.4, 1.6];

// Pull the bot out of game_sim by re-loading it with access to its internals.

const botFn = require('./game_sim.js').bot;

const cloneEcon = ec => { const c = Object.assign(Object.create(Object.getPrototypeOf(ec)), JSON.parse(JSON.stringify(ec))); return c; };
const runWave = (st, wi, k) => {
  const W = L.WAVES[wi], ec = st.ec;
  const scale = { hp: W.scale.hp * k, dmg: W.scale.dmg * Math.sqrt(k) };
  const sim = new L.Sim(st.army, { types: ec.types(L.TYPES, scale), enemies: L.buildWave(W), gateHp: ec.gateHp, gateMax: ec.gateMax(), archers: L.ARCHERS[ec.archers].count });
  while (!sim.result) sim.step(1 / 15);
  return sim;
};
let states = Array.from({ length: R }, () => ({ ec: new L.Econ(), army: [], t: 45 }));
const K = [];
for (let wi = 0; wi < L.WAVES.length; wi++) {
  states.forEach(st => { st.ec.tick(st.t); botFn(L, st.ec, st.army, wi); });
  const held = k => {
    let ok = 0;
    for (const st of states) { const s = runWave({ ec: cloneEcon(st.ec), army: st.army }, wi, k); if (s.result.win && s.gateHp > 0) ok++; }
    return ok / states.length;
  };
  let best = GRID[0];
  for (const k of GRID) { if (held(k) >= TARGET(wi + 1)) best = k; else break; }
  K.push(best);
  // Play the wave for real with the chosen factor and move every run forward.
  states.forEach(st => {
    const sim = runWave(st, wi, best), ec = st.ec;
    ec.tick(sim.t); ec.gateHp = sim.gateHp;
    let bounty = 0; sim.units.forEach(u => { if (u.side === 'e' && !u.alive) bounty += L.BOUNTY[u.type] || 0; });
    ec.add({ gold: bounty }); if (sim.result.win) ec.add({ gold: L.waveBonus(wi + 1) });
    if (ec.gateHp <= 0) ec.gateHp = ec.gateMax() * 0.5;   // in the real game the player repairs; keep runs alive
    st.t = 30;
  });
  const a = states[0].army;
  console.log(`wave ${wi + 1}: factor ${best}  target ${TARGET(wi + 1)}  army ${a.length} units, avg level ${(a.reduce((s, x) => s + x.level, 0) / a.length).toFixed(1)}`);
}
fs.writeFileSync(__dirname + '/wave_factors.json', JSON.stringify(K));
console.log(JSON.stringify(K));
