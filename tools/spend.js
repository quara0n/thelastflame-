// Where do the test players' resources go? (version 33). Plays whole games with the balance bot and splits the spending
// per category (army, unit upgrades, Forge, Workshop, Warden, hero, workers, mines, Barracks, wall, wall gear, converters).
// Usage: node spend.js [runs=20] [extra.js]   (extra.js: a skill proxy, e.g. faster or slower gathering)
const fs = require('fs');
const { load, playGame } = require('./game_sim.js');
const runs = +(process.argv[2] || 20);
const L = load(process.argv[3] ? fs.readFileSync(process.argv[3], 'utf8') : '');
L.botSpend.on = true;
const ends = [], owned = [];
const wrap = L.Econ.prototype.tick;
let last = null; L.Econ.prototype.tick = function (dt) { last = this; return wrap.call(this, dt); };
for (let r = 0; r < runs; r++) {
  const log = playGame(L); ends.push(log.length);
  const ec = last;
  owned.push({ forge: ec.up.melee + ec.up.ranged + ec.up.armor, tech: ec.up.tech, tools: ec.tools, warden: ec.warden.sword + ec.warden.shield + ec.warden.armor,
    abil: ec.warden.abil.stun + ec.warden.abil.spin + ec.warden.abil.freeze, wlv: ec.wardenLevel(), oil: ec.wallLv('oil'), ballista: ec.wallLv('ballista'),
    kiln: ec.convLv('kiln'), smelter: ec.convLv('smelter'), hero: ec.hero ? ec.heroLevel() : 0, barracks: ec.barracks });
}
const T = L.botSpend.tot, R = ['gold', 'iron', 'coal', 'timber', 'stone'];
const sum = r => Object.values(T).reduce((s, b) => s + (b[r] || 0), 0);
console.log(`${runs} games, median end wave ${ends.slice().sort((a, b) => a - b)[runs >> 1]}`);
console.log('category'.padEnd(13) + R.map(r => r.padStart(8)).join('') + '   (share of all spending of that resource)');
Object.keys(T).sort((a, b) => (T[b].gold || 0) - (T[a].gold || 0)).forEach(c =>
  console.log(c.padEnd(13) + R.map(r => (Math.round(100 * (T[c][r] || 0) / Math.max(1, sum(r))) + '%').padStart(8)).join('')));
const avg = k => (owned.reduce((s, o) => s + o[k], 0) / runs).toFixed(1);
console.log('owned at the end (average):', Object.keys(owned[0]).map(k => `${k} ${avg(k)}`).join(', '));
