// Rough strength per wave: sqrt(total HP × total DPS) after the wave factor, armor counted as extra HP.
const { load } = require('./game_sim.js');
const html = process.argv[2];
const L = load();
const ec = new L.Econ();
L.WAVES.forEach((W, i) => {
  const T = ec.types(L.TYPES, W.scale);
  let hp = 0, dps = 0;
  for (const e of L.buildWave(W)) { const t = T[e.type]; hp += t.hp * (1 + (t.armor || 0) / 12); dps += t.dmg / t.interval; }
  console.log(i + 1, W.style.padEnd(13), Math.round(Math.sqrt(hp * dps)));
});
