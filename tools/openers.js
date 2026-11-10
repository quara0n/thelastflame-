// Opening choices (version 34, Rune: «hard choices at the start about where the money goes: production, army, gate»).
// Plays whole games with the balanced test player but a different opening, and shows how many fall in the first waves.
// Usage: node openers.js [games=24]
const { spawn } = require('child_process');
const OPENERS = {
  balanced: '',
  // Workers first: hires every worker it can afford and keeps only a token army.
  greedy: 'const BOT_WORKER_CAP = w => 99; const BOT_ARMY_NEED = w => 4;',
  // Army first: never hires extra workers in the first five waves.
  armyOnly: 'const BOT_WORKER_CAP = w => w <= 5 ? 0 : 16 + 3 * w; const BOT_ARMY_NEED = w => 99;',
  // Never repairs the gate.
  noRepair: 'Econ.prototype.repair = () => false;',
};
const games = +(process.argv[2] || 24);
if (process.env.OPENER) {
  const { load, playGame } = require('./game_sim.js');
  const L = load(OPENERS[process.env.OPENER]);
  const ends = []; for (let r = 0; r < games; r++) ends.push(playGame(L).length);
  console.log(JSON.stringify(ends));
} else {
  const names = Object.keys(OPENERS), out = {};
  let left = names.length;
  for (const n of names) {
    let buf = ''; const p = spawn(process.execPath, [__filename, String(games)], { env: { ...process.env, OPENER: n } });
    p.stdout.on('data', d => buf += d); p.stderr.on('data', d => process.stderr.write(d));
    p.on('close', () => { out[n] = JSON.parse(buf.trim().split('\n').pop()); if (--left) return;
      for (const k of names) { const e = out[k].slice().sort((a, b) => a - b);
        console.log(`${k.padEnd(9)} lost by wave 5: ${e.filter(x => x <= 5).length}/${e.length}  by wave 10: ${e.filter(x => x <= 10).length}  median ${e[e.length >> 1]}  win 30: ${e.filter(x => x >= 30).length}`); } });
  }
}
