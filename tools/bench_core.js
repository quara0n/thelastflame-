module.exports = function (L) {
  const { Sim, TYPES, WAVES, buildWave } = L;
  const ENEMY_WAVES = [4, 6, 8].map(n => buildWave(WAVES[n - 1]));
const ENEMY_SCALE = [4, 6, 8].map(n => WAVES[n - 1].scale);
function scaled(m, wi) {
  const t = {}; const sc = ENEMY_SCALE[wi];
  for (const k in TYPES) { const T = TYPES[k]; t[k] = T.side === 'e' ? Object.assign({}, T, { hp: Math.round(T.hp * m * sc.hp), dmg: Math.round(T.dmg * m * sc.dmg) }) : T; }
  return t;
}
const melee = k => !TYPES[k].ranged;
function army(test, level, n) {
  const a = [
    { type: 'shieldguard', col: 7, row: 0, order: 'advance' }, { type: 'shieldguard', col: 8, row: 0, order: 'advance' },
    { type: 'ironshot', col: 7, row: 3, order: 'follow' }, { type: 'ironshot', col: 8, row: 3, order: 'follow' },
  ];
  const cols = [6, 9, 5, 10, 4, 11];
  for (let i = 0; i < n; i++) a.push({ type: test, level, col: cols[i], row: melee(test) ? 0 : 3, order: melee(test) ? 'advance' : 'follow' });
  return a;
}
function winRate(arm, m, runs) {
  let w = 0, n = 0;
  for (let wi = 0; wi < ENEMY_WAVES.length; wi++) {
    const types = scaled(m, wi);
    for (let r = 0; r < runs; r++) {
      const sim = new Sim(arm, { types, enemies: ENEMY_WAVES[wi], warden: false, gateHp: 600, gateMax: 600 });
      while (!sim.result) sim.step(1 / 15);
      n++; if (sim.result.win) w++;
    }
  }
  return w / n;
}
function power(arm, runs = 8) {
  let lo = 0.05, hi = 4;
  for (let i = 0; i < 10; i++) { const mid = (lo + hi) / 2; if (winRate(arm, mid, runs) >= 0.5) lo = mid; else hi = mid; }
  return (lo + hi) / 2;
}
  return { army, power, winRate };
};
