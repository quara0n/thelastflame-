const { army, power } = require('./bench.js');
const groups = (process.argv[2] || 'shieldguard>ironwall,stormreaver>frostbrand,ironshot>thunderbore,longfang>thunderbore').split(',');
const base = power(army('shieldguard', 0, 0), 12);
console.log('core', base.toFixed(3));
for (const g of groups) {
  const [a, b] = g.split('>');
  const r = {};
  for (const [k, ls] of [[a, [0, 3]], [b, [0, 1, 3]]]) for (const l of ls) r[k + l] = power(army(k, l, 3), 12) - base;
  const ref = r[a + 3];
  console.log(g.padEnd(26), Object.entries(r).map(([k, v]) => `${k}=${v.toFixed(3)} (${(v / ref * 100).toFixed(0)}%)`).join('  '));
}
