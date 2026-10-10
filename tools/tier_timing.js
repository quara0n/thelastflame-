// Usage: node tools/tier_timing.js  – median wave the bot reaches each Barracks tier (20 games).
const G = require('./game_sim.js');
const L = G.load();
const origBuy = L.Econ.prototype.buyBarracks; const hist = [];
let curW = 0; const first = {};
L.Econ.prototype.buyBarracks = function () { const r = origBuy.call(this); if (r) { (first[this.barracks + 1] = first[this.barracks + 1] || []).push(curW); } return r; };
const origBot = G.bot;
for (let i = 0; i < 20; i++) {
  const ec = new L.Econ(), army = []; let t = 45;
  for (let wi = 0; wi < 30; wi++) { curW = wi + 1; ec.tick(t); origBot(L, ec, army, wi);
    const W = L.WAVES[wi]; const sim = new L.Sim(L.withHero(army, ec), { types: ec.types(L.TYPES, W.scale), enemies: L.buildWave(W), gateHp: ec.gateHp, gateMax: ec.gateMax(), archers: L.ARCHERS[ec.archers].count });
    while (!sim.result) sim.step(1 / 15); ec.tick(sim.t); ec.gateHp = sim.gateHp; let b = 0; sim.units.forEach(u => { if (u.side === 'e' && !u.alive) b += L.BOUNTY[u.type] || 0; }); ec.add({ gold: b }); if (sim.result.win) ec.add({ gold: L.waveBonus(W.n) }); L.heroAfterWave(ec, sim, true);
    if (ec.gateHp <= 0) ec.gateHp = ec.gateMax() * 0.5; t = 55; }
}
for (const k in first) { const a = first[k].sort((x, y) => x - y); console.log('Tier', k, 'reached by', a.length, '/20 runs; median wave', a[a.length >> 1], 'range', a[0], '-', a[a.length - 1]); }
