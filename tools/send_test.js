// How much trouble do the rival's sends cause? Same army, same base wave, same gold: smart picks vs random picks.
// Score = gold value of defenders killed + gate damage / 10 + leaks × 20. Usage: node tools/send_test.js [runs=8]
const { load } = require('./game_sim.js');
const L = load(';globalThis.__V = { pickSends, foeProfile, sendPrice, placeSent, versusScale, MAP };');
const V = globalThis.__V, R = +(process.argv[2] || 8);
const score = (foe, wi, kinds) => {
  const W = L.WAVES[wi], ec = foe.ec, base = L.buildWave(W);
  const sent = V.placeSent(kinds.map(k => ({ type: k, by: 'r', price: V.sendPrice(k) })), base);
  const sim = new L.Sim(foe.army, { types: ec.types(L.TYPES, V.versusScale(W)), enemies: base.concat(sent), gateHp: ec.gateHp, gateMax: ec.gateMax(), archers: L.ARCHERS[ec.archers].count });
  while (!sim.result) sim.step(1 / 15);
  let s = (ec.gateHp - sim.gateHp) / 10;
  for (const u of sim.units) { if (u.side === 'p' && !u.alive && L.TYPES[u.type]) s += L.TYPES[u.type].cost || 0; if (u.sent && (u.leaked || u.z > V.MAP.gateZ + 1.5)) s += 20; }
  return s;
};
const rand = (opts, money) => { const out = []; for (let g = 0; g < 40 && out.length < 24; g++) { const c = opts.filter(k => V.sendPrice(k) <= money); if (!c.length) break; const k = c[Math.floor(Math.random() * c.length)]; out.push(k); money -= V.sendPrice(k); } return out; };
const rows = {};
for (let r = 0; r < R; r++) {
  const foe = new L.Rival(); foe.smart = false;
  for (let wi = 0; wi < 30; wi++) {
    foe.begin(wi, []);
    if (wi >= 2 && wi % 2 === 0) {
      const money = 30 + 5 * wi, opts = L.sendable(wi), prof = V.foeProfile({ army: foe.army, ec: foe.ec });
      const a = score(foe, wi, V.pickSends(opts, money, prof, {})), b = score(foe, wi, rand(opts, money)), c = score(foe, wi, []);
      (rows[wi + 1] = rows[wi + 1] || []).push([a - c, b - c]);
    }
    const res = foe.end(null); if (res.lost) break;
  }
}
let ts = 0, tr = 0;
for (const w in rows) { const s = rows[w].reduce((x, y) => x + y[0], 0) / rows[w].length, q = rows[w].reduce((x, y) => x + y[1], 0) / rows[w].length; ts += s; tr += q; console.log(`wave ${w}: smart +${s.toFixed(0)}  random +${q.toFixed(0)}`); }
console.log(`total extra trouble: smart ${ts.toFixed(0)}, random ${tr.toFixed(0)} (${(ts / tr * 100 - 100).toFixed(0)} % more)`);
