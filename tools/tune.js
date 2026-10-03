// usage: node tune.js '<json overrides of TYPES>' '<json overrides of UPGRADES mods: {"ironwall":[{..},..]}>' a>b ...
const fs = require('fs');
let code = require('./logic_up.js');
const ov = JSON.parse(process.argv[2] || '{}'), uov = JSON.parse(process.argv[3] || '{}');
code = code.replace('const ARCHER = {', `const __ov = ${JSON.stringify(ov)}, __uov = ${JSON.stringify(uov)};
for (const k in __ov) Object.assign(TYPES[k], __ov[k]);
for (const k in __uov) __uov[k].forEach((m, i) => { if (m) UPGRADES[k][i].mod = m; });
const ARCHER = {`);
const L = new Function(code + '; return { Sim, TYPES, WAVES, buildWave };')();
// reuse bench functions with this logic
const B = require('./bench_core.js')(L);
const base = B.power(B.army('shieldguard', 0, 0), 12);
for (const g of process.argv.slice(4)) {
  const [a, b, lv] = g.split('>');
  const ref = B.power(B.army(a, 3, 3), 12) - base;
  const out = [`${a}3=${ref.toFixed(3)}`];
  for (const l of (lv || '0,1').split('.').join(',').split(',').map(Number)) { const v = B.power(B.army(b, l, 3), 12) - base; out.push(`${b}${l}=${(v / ref * 100).toFixed(0)}%`); }
  console.log(out.join('  '));
}
