// Plays the bot through 30 waves (gate can't fall) and prints the economy each wave.
const G = require('./game_sim.js'); const L = G.load(process.argv[2] || '');
const ec = new L.Econ(), army = []; let t = 45;
for (let wi = 0; wi < 30; wi++) {
  ec.tick(t); G.bot(L, ec, army, wi);
  const W = L.WAVES[wi];
  const sim = new L.Sim(army, { types: ec.types(L.TYPES, W.scale), enemies: L.buildWave(W), gateHp: 1e5, gateMax: 1e5, archers: L.ARCHERS[ec.archers].count });
  while (!sim.result) sim.step(1 / 15);
  ec.tick(sim.t); let b = 0; sim.units.forEach(u => { if (u.side === 'e' && !u.alive) b += L.BOUNTY[u.type] || 0; }); ec.add({ gold: b + (sim.result.win ? L.waveBonus(W.n) : 0) });
  const nw = ['gold', 'timber', 'stone', 'iron', 'coal'].map(k => ec.nodes[k].workers + '/' + ec.cap(k)).join(' ');
  const r = ec.res; console.log(`w${wi + 1} B${ec.barracks + 1} workers ${nw} | gold ${r.gold|0} tim ${r.timber|0} sto ${r.stone|0} iron ${r.iron|0} coal ${r.coal|0} | army ${army.length} lv ${(army.reduce((s,a)=>s+(a.level||0),0)/Math.max(1,army.length)).toFixed(1)}`);
  t = 55;
}
