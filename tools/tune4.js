// Measures Tier 4 against fully upgraded Tier 3 (same rule as before: fresh ≈ 90 %, after first upgrade ≈ 120 %).
// usage: node tune4.js '<json TYPES overrides>' '<json UPGRADES mod overrides>'
const fs = require('fs');
const { load } = require('./game_sim.js');
const ov = JSON.parse(process.argv[2] || '{}'), uov = JSON.parse(process.argv[3] || '{}');
const extra = `\nfor (const k in ${JSON.stringify(ov)}) Object.assign(TYPES[k], ${JSON.stringify(ov)}[k]);\nconst __u = ${JSON.stringify(uov)}; for (const k in __u) __u[k].forEach((m, i) => { if (m) UPGRADES[k][i].mod = m; });\n`;
const L = load(extra);
const WV = [22, 24, 26].map(n => L.WAVES[n - 1]);
const ENEM = WV.map(W => L.buildWave(W));
function types(m, wi) { const t = {}, sc = WV[wi].scale; for (const k in L.TYPES) { const T = L.TYPES[k]; t[k] = T.side === 'e' ? Object.assign({}, T, { hp: Math.round(T.hp * m * sc.hp), dmg: Math.round(T.dmg * m * sc.dmg) }) : T; } return t; }
function army(test, level, n) {
  const a = [['huskarl', 6, 0], ['huskarl', 9, 0], ['captain', 7, 0], ['siegebreaker', 7, 3], ['pyreguard', 8, 3], ['siegebreaker', 9, 3]].map(([type, col, row]) => ({ type, level: 3, col, row, order: L.TYPES[type].ranged ? 'follow' : 'advance' }));
  const cols = [5, 10, 4, 11];
  for (let i = 0; i < n; i++) a.push({ type: test, level, col: cols[i], row: L.TYPES[test].ranged ? 3 : 0, order: L.TYPES[test].ranged ? 'follow' : 'advance' });
  return a;
}
function win(arm, m, runs) { let w = 0, n = 0; for (let wi = 0; wi < WV.length; wi++) { const t = types(m, wi); for (let r = 0; r < runs; r++) { const s = new L.Sim(arm, { types: t, enemies: ENEM[wi], warden: false, gateHp: 600, gateMax: 600 }); while (!s.result) s.step(1 / 15); n++; if (s.result.win) w++; } } return w / n; }
function power(arm) { let lo = 0.02, hi = 3; for (let i = 0; i < 10; i++) { const mid = (lo + hi) / 2; if (win(arm, mid, 8) >= 0.5) lo = mid; else hi = mid; } return (lo + hi) / 2; }
const base = power(army('huskarl', 3, 0));
const pairs = [['captain', 'ironhulk'], ['huskarl', 'mammoth'], ['siegebreaker', 'skyspear'], ['captain', 'hearthengine']];
for (const [a, b] of pairs) {
  const ref = power(army(a, 3, 2)) - base;
  const r0 = power(army(b, 0, 2)) - base, r1 = power(army(b, 1, 2)) - base;
  console.log(`${b.padEnd(13)} fresh ${(r0 / ref * 100).toFixed(0)}%  after 1st ${(r1 / ref * 100).toFixed(0)}%   (vs maxed ${a})`);
}
