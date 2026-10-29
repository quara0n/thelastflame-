// Automatic test of the game logic (no graphics). Plays many whole games with the bot player, plus random armies
// against random waves, and watches every step for things that should never happen:
//   crashes, NaN/Infinity, units flying off the map, negative or NaN resources, a gate with more HP than its max,
//   waves that never end, and enemies that stand still for a long time without fighting (stuck).
// It also reports where the bot loses, so a wave that suddenly turns into a wall shows up.
// Usage: node tools/autotest/logic_check.js [--html prototype/kamptest-2.html] [--games 20] [--fuzz 60] [--out report.json]
const fs = require('fs'), path = require('path');

const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const ROOT = path.join(__dirname, '..', '..');
const HTML = path.resolve(opt('html', path.join(ROOT, 'prototype', 'kamptest-2.html')));
const GAMES = +opt('games', 20), FUZZ = +opt('fuzz', 60), OUT = opt('out', null);
const STEP = 1 / 15, MAX_T = 900;

// The bot player lives in game_sim.js next to the other tools.
const { bot } = require(path.join(__dirname, '..', 'game_sim.js'));

function load() {
  const html = fs.readFileSync(HTML, 'utf8');
  const a = html.indexOf('// ===== The Last Flame — kampsimulering'), b = html.indexOf('// ===== The Last Flame — musikk');
  if (a < 0 || b < 0) throw new Error('Fant ikke kampsimulering/musikk-merkene i ' + HTML);
  const opt = n => `typeof ${n} !== "undefined" ? ${n} : null`;
  const code = html.slice(a, b).replace(/if \(typeof module !== 'undefined'\) module.exports/g, '//');
  return new Function(code + `;return { Sim, Econ, TYPES, WAVES, BARRACKS, NODES, TRACKS, BOUNTY, waveBonus, UPGRADES, MAX_LEVEL, supplyOf, ARCHERS, buildWave, upgradeSpent, REFUND, WALLS, MAP,
    heroBot: ${opt('heroBot')} || (() => {}), withHero: ${opt('withHero')} || (a => a), armyNeed: ${opt('BOT_ARMY_NEED')}, workerCap: ${opt('BOT_WORKER_CAP')},
    heroAfterWave: ${opt('heroAfterWave')} || (() => null), Rival: ${opt('Rival')} };`)();
}

const problems = new Map();   // key -> { kind, text, count, example }
function problem(kind, text, example) {
  const key = kind + '|' + text;
  const p = problems.get(key) || { kind, text, count: 0, example };
  p.count++; problems.set(key, p);
}
const bad = v => typeof v !== 'number' || !Number.isFinite(v);

// Checks one battle while it runs. ctx says which game and wave, for the report.
function watchBattle(L, sim, ctx) {
  const still = new Map();   // enemy id -> { x, z, since }
  let lastCheck = 0;
  try {
    while (!sim.result) {
      sim.step(STEP);
      if (sim.t - lastCheck < 1) continue;
      lastCheck = sim.t;
      for (const u of sim.units) {
        if (!u.alive) continue;
        if (bad(u.x) || bad(u.z) || bad(u.hp)) { problem('feil', `${u.type} fikk ugyldig posisjon eller HP (NaN/uendelig)`, { ...ctx, t: +sim.t.toFixed(1) }); u.alive = false; continue; }
        if (Math.abs(u.x) > 120 || u.z < -80 || u.z > 140) problem('feil', `${u.type} havnet langt utenfor kartet`, { ...ctx, x: +u.x.toFixed(1), z: +u.z.toFixed(1) });
        if (u.hp > u.maxHp * 1.01 + 1) problem('feil', `${u.type} har mer HP enn maks`, { ...ctx, hp: Math.round(u.hp), max: Math.round(u.maxHp) });
        if (u.side === 'e' && !u.T.flies && !u.T.heal) {   // healers may hang back on purpose
          const s = still.get(u.id);
          // Moving, attacking (its cooldown was reset since the last look) or hitting the gate all count as doing something.
          const busy = s && (u.cd > s.cd + 0.01 || u.atGate);
          if (s) s.cd = u.cd;
          if (!s || busy || Math.hypot(s.x - u.x, s.z - u.z) > 0.3) still.set(u.id, { x: u.x, z: u.z, since: sim.t, cd: u.cd });
          else if (sim.t - s.since > 45) { problem('fast', `${u.type} står stille i over 45 s uten å slåss`, { ...ctx, x: +u.x.toFixed(1), z: +u.z.toFixed(1) }); s.since = sim.t; }
        }
      }
      if (bad(sim.gateHp) || sim.gateHp > sim.gateMax + 1) problem('feil', 'Porten har ugyldig HP', { ...ctx, gate: sim.gateHp, max: sim.gateMax });
      if (sim.t > MAX_T) { problem('fast', `Waven tok slutt aldri (over ${MAX_T} s)`, { ...ctx, left: sim.units.filter(u => u.alive && u.side === 'e').map(u => u.type).slice(0, 6) }); return false; }
    }
  } catch (e) { problem('krasj', `Kampen krasjet: ${e.message}`, { ...ctx, stack: String(e.stack).split('\n').slice(0, 4).join(' | ') }); return false; }
  return true;
}

function checkEcon(ec, ctx) {
  for (const [r, v] of Object.entries(ec.res)) {
    if (bad(v)) problem('feil', `Ressursen ${r} ble NaN/uendelig`, ctx);
    else if (v < -0.5) problem('feil', `Ressursen ${r} gikk under null`, { ...ctx, value: v });
  }
  if (bad(ec.gateHp)) problem('feil', 'Portens HP i økonomien ble NaN', ctx);
}

// Whole games with the bot, the same way game_sim.js plays them, but watched.
function playWatched(L, g) {
  const ec = new L.Econ(), army = [], log = [];
  let t = 45;
  for (let wi = 0; wi < L.WAVES.length; wi++) {
    const W = L.WAVES[wi], ctx = { game: g, wave: W.n };
    try { ec.tick(t); bot(L, ec, army, wi); } catch (e) { problem('krasj', `Kjøp/økonomi krasjet: ${e.message}`, { ...ctx, stack: String(e.stack).split('\n').slice(0, 4).join(' | ') }); break; }
    checkEcon(ec, ctx);
    let sim;
    try { sim = new L.Sim(L.withHero(army, ec), { types: ec.types(L.TYPES, W.scale), enemies: L.buildWave(W), gateHp: ec.gateHp, gateMax: ec.gateMax(), archers: L.ARCHERS[ec.archers].count, wallgear: ec.wallgear, bot: ec }); }
    catch (e) { problem('krasj', `Kunne ikke starte waven: ${e.message}`, { ...ctx, stack: String(e.stack).split('\n').slice(0, 4).join(' | ') }); break; }
    if (!watchBattle(L, sim, ctx)) break;
    try {
      ec.tick(sim.t); ec.gateHp = sim.gateHp;
      let bounty = 0; sim.units.forEach(u => { if (u.side === 'e' && !u.alive) bounty += L.BOUNTY[u.type] || 0; });
      ec.add({ gold: bounty }); if (sim.result.win) ec.add({ gold: L.waveBonus(W.n) });
      L.heroAfterWave(ec, sim, true);
    } catch (e) { problem('krasj', `Etter waven krasjet: ${e.message}`, { ...ctx, stack: String(e.stack).split('\n').slice(0, 4).join(' | ') }); break; }
    checkEcon(ec, ctx);
    const lost = sim.result.reason === 'Fienden nådde flammen';
    log.push({ w: W.n, win: !!sim.result.win, lost, t: Math.round(sim.t), army: army.length, tier: Math.max(1, ...army.map(a => L.TYPES[a.type].tier || 1)) });
    if (lost) break;
    t = 55;
  }
  return log;
}

// Random armies against random waves: odd mixes of units, levels and orders the bot never tries.
function fuzz(L, i) {
  const rnd = n => Math.floor(Math.random() * n);
  const own = Object.keys(L.TYPES).filter(k => L.TYPES[k].side === 'p' && k !== 'warden' && L.UPGRADES[k]);
  const orders = ['hold', 'advance', 'follow', 'flankL', 'flankR'];
  const army = [], used = new Set(), n = 3 + rnd(22);
  for (let k = 0; k < n; k++) {
    const col = rnd(L.MAP.cols), row = rnd(L.MAP.rows); if (used.has(col + ':' + row)) continue; used.add(col + ':' + row);
    army.push({ type: own[rnd(own.length)], level: rnd(L.MAX_LEVEL + 1), col, row, order: orders[rnd(orders.length)], squad: Math.random() < 0.4 ? rnd(3) : null });
  }
  const W = L.WAVES[rnd(L.WAVES.length)], ctx = { fuzz: i, wave: W.n, army: army.map(a => `${a.type}${a.level}/${a.order}`).join(' ') };
  let sim;
  try { sim = new L.Sim(army, { types: L.TYPES, enemies: L.buildWave(W), gateHp: 600, gateMax: 600, archers: rnd(6) }); }
  catch (e) { problem('krasj', `Tilfeldig hær: kunne ikke starte waven: ${e.message}`, ctx); return; }
  watchBattle(L, sim, ctx);
}

const t0 = Date.now();
const L = load();
const per = {}, ends = [];
for (let g = 0; g < GAMES; g++) {
  const log = playWatched(L, g + 1);
  ends.push(log.length ? log[log.length - 1].w : 0);
  log.forEach(x => { const p = per[x.w] || (per[x.w] = { n: 0, win: 0, t: 0 }); p.n++; p.t += x.t; if (x.win) p.win++; });
}
for (let i = 0; i < FUZZ; i++) fuzz(L, i + 1);

// Balance: a wave the bot reaches but rarely holds, after one it held easily, is a "wall".
const waves = Object.entries(per).map(([w, p]) => ({ wave: +w, reached: p.n, held: Math.round(p.win / p.n * 100), avgSeconds: Math.round(p.t / p.n) }));
const walls = waves.filter((x, i) => i > 0 && x.reached >= 3 && waves[i - 1].held - x.held >= 40);
const report = {
  html: path.relative(ROOT, HTML), games: GAMES, fuzz: FUZZ, seconds: Math.round((Date.now() - t0) / 1000),
  reachedWave: { median: ends.slice().sort((a, b) => a - b)[Math.floor(ends.length / 2)], all: ends },
  waves, walls: walls.map(x => x.wave),
  problems: [...problems.values()].sort((a, b) => ({ krasj: 0, feil: 1, fast: 2 }[a.kind] - { krasj: 0, feil: 1, fast: 2 }[b.kind]) || b.count - a.count),
};
if (OUT) fs.writeFileSync(OUT, JSON.stringify(report, null, 2));
console.log(`Logikktest: ${GAMES} hele spill + ${FUZZ} tilfeldige hærer på ${report.seconds} s (${report.html})`);
console.log(`Boten kom til wave (median) ${report.reachedWave.median}; alle: ${ends.join(' ')}`);
console.log('Holdt per wave: ' + waves.map(x => `${x.wave}:${x.held}%`).join(' '));
if (report.walls.length) console.log('Mulige vegger (brå hopp i vanskelighet): wave ' + report.walls.join(', '));
console.log(report.problems.length ? `${report.problems.length} problemtyper:` : 'Ingen feil funnet.');
for (const p of report.problems) console.log(`  [${p.kind}] ${p.text} (${p.count}×) ${JSON.stringify(p.example).slice(0, 300)}`);
process.exitCode = report.problems.some(p => p.kind !== 'fast') ? 1 : 0;
