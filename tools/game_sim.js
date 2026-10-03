// Simulates whole games of The Last Flame with a sensible bot player, wave by wave.
// Usage: node game_sim.js [runs] [scaleOverrides.json]
const fs = require('fs');
function load(extra) {
  const html = fs.readFileSync(__dirname + '/../prototype/kamptest-2.html', 'utf8');
  const a = html.indexOf('// ===== The Last Flame — kampsimulering'), b = html.indexOf('// ===== The Last Flame — musikk');
  const code = html.slice(a, b).replace(/if \(typeof module !== 'undefined'\) module.exports/g, '//') + (extra || '');
  return new Function(code + ';return { Sim, Econ, TYPES, WAVES, BARRACKS, NODES, TRACKS, BOUNTY, waveBonus, UPGRADES, MAX_LEVEL, supplyOf, ARCHERS, buildWave, upgradeSpent, REFUND, WALLS };')();
}

function bot(L, ec, army, waveIdx) {
  const T = L.TYPES, sup = () => army.reduce((n, a) => n + L.supplyOf(T[a.type]), 0);
  const unitsOf = tier => ({ 1: ['shieldguard', 'stormreaver', 'ironshot', 'longfang'], 2: ['ironwall', 'frostbrand', 'thunderbore', 'hearthkeeper'], 3: ['captain', 'huskarl', 'pyreguard', 'siegebreaker'] })[tier];
  const melee = a => !T[a.type || a].ranged;
  const free = (ranged) => {
    const rows = ranged ? [3, 4, 2, 5] : [0, 1, 2];
    const order = [7, 8, 6, 9, 5, 10, 4, 11, 3, 12, 2, 13, 1, 14, 0, 15];
    for (const r of rows) for (const c of order) if (!army.some(a => a.col === c && a.row === r)) return { col: c, row: r };
    return null;
  };
  const buy = type => {
    const p = ec.unitPrice(T[type]);
    if (!ec.unitUnlocked(type) || sup() + L.supplyOf(T[type]) > ec.supplyCap() || !ec.can(p)) return false;
    const spot = free(T[type].ranged); if (!spot) return false;
    ec.pay(p); army.push({ type, level: 0, ...spot, order: T[type].ranged ? 'follow' : 'advance' }); return true;
  };
  const upgrade = a => {
    if ((a.level || 0) >= L.MAX_LEVEL) return false;
    const c = L.UPGRADES[a.type][a.level || 0].cost;
    if (!ec.can(c)) return false; ec.pay(c); a.level = (a.level || 0) + 1; return true;
  };
  const w = waveIdx + 1;
  for (let guard = 0; guard < 80; guard++) {
    let did = false;
    // Economy first in the early game: gold workers while they are cheap.
    if (w <= 6 && ec.nodes.gold.workers < ec.cap('gold') && ec.workerPrice() <= 9 && ec.res.gold >= ec.workerPrice() + 10) did = ec.addWorker('gold');
    if (!did && w >= 3 && !ec.nodes.iron.unlocked && ec.can(L.NODES.iron.unlock)) did = ec.unlockNode('iron');
    if (!did && ec.nodes.iron.unlocked && ec.nodes.iron.workers < 3 && ec.res.gold >= ec.workerPrice() + 8) did = ec.addWorker('iron');
    if (!did && ec.barracks >= 1 && !ec.nodes.coal.unlocked && ec.can(L.NODES.coal.unlock)) did = ec.unlockNode('coal');
    if (!did && ec.nodes.coal.unlocked && ec.nodes.coal.workers < 2 && ec.res.gold >= ec.workerPrice() + 8) did = ec.addWorker('coal');
    if (!did && ec.nodes.timber.workers < 2 && ec.res.gold >= ec.workerPrice() + 15) did = ec.addWorker('timber');
    if (!did && w >= 4 && ec.barracks === 0 && ec.can(L.BARRACKS[1].cost)) did = ec.buyBarracks();
    if (!did && w >= 9 && ec.barracks === 1 && ec.can(L.BARRACKS[2].cost)) did = ec.buyBarracks();
    if (!did && ec.gateHp < ec.gateMax() * 0.7) did = ec.repair();
    if (!did && w >= 3 && ec.archers === 0) did = ec.buyArchers();
    // Army: keep roughly half melee, half ranged; buy the best tier that is open.
    if (!did && sup() < ec.supplyCap()) {
      const nMel = army.filter(melee).length, wantRanged = nMel > army.length - nMel;
      for (let tier = ec.barracks + 1; tier >= 1 && !did; tier--) {
        const opts = unitsOf(tier).filter(t => !!T[t].ranged === wantRanged);
        const pick = opts[(army.length + w) % opts.length];
        did = buy(pick);
      }
    }
    // Upgrades: cheapest-level units of the highest tier first.
    if (!did) {
      const cand = army.filter(a => (a.level || 0) < L.MAX_LEVEL).sort((a, b) => (T[b.type].tier || 1) - (T[a.type].tier || 1) || (a.level || 0) - (b.level || 0));
      for (const a of cand) if (upgrade(a)) { did = true; break; }
    }
    // Forge when there is iron to spare.
    if (!did && ec.res.iron >= 25) for (const k of ['melee', 'ranged', 'armor']) if (ec.buyTrack(k)) { did = true; break; }
    // Full army of maxed units: swap a maxed lower-tier unit for a higher tier.
    if (!did && sup() >= ec.supplyCap() && ec.barracks >= 1) {
      const old = army.find(a => (T[a.type].tier || 1) <= ec.barracks && (a.level || 0) >= L.MAX_LEVEL);
      if (old) {
        const up = unitsOf(ec.barracks + 1).filter(t => !!T[t].ranged === !!T[old.type].ranged)[0];
        const refund = {}; const p = Object.assign({}, ec.unitPrice(T[old.type])), sp = L.upgradeSpent(old.type, old.level);
        for (const r in sp) p[r] = (p[r] || 0) + sp[r]; for (const r in p) refund[r] = Math.floor(p[r] * L.REFUND);
        const price = ec.unitPrice(T[up]), need = {}; for (const r in price) need[r] = price[r] - (refund[r] || 0);
        const supAfter = sup() - L.supplyOf(T[old.type]) + L.supplyOf(T[up]);
        if (supAfter <= ec.supplyCap() && ec.can(need)) {
          army.splice(army.indexOf(old), 1); ec.add(refund); did = buy(up);
        }
      }
    }
    if (!did) break;
  }
}

function playGame(L, opts) {
  const ec = new L.Econ(), army = [], log = [];
  let t = 45;
  for (let wi = 0; wi < L.WAVES.length; wi++) {
    ec.tick(t);
    bot(L, ec, army, wi);
    const W = L.WAVES[wi];
    const sim = new L.Sim(army, { types: ec.types(L.TYPES, W.scale), enemies: L.buildWave(W), gateHp: ec.gateHp, gateMax: ec.gateMax(), archers: L.ARCHERS[ec.archers].count });
    while (!sim.result) sim.step(1 / 15);
    ec.tick(sim.t);
    ec.gateHp = sim.gateHp;
    let bounty = 0; sim.units.forEach(u => { if (u.side === 'e' && !u.alive) bounty += L.BOUNTY[u.type] || 0; });
    ec.add({ gold: bounty });
    if (sim.result.win) ec.add({ gold: L.waveBonus(W.n) });
    const value = army.reduce((s, a) => s + (L.TYPES[a.type].cost || 0) + (L.upgradeSpent(a.type, a.level).gold || 0), 0);
    log.push({ w: W.n, win: sim.result.win, flame: sim.result.reason === 'Fienden nådde flammen', gate: Math.round(sim.gateHp), army: army.length, value, lv: +(army.reduce((s, a) => s + (a.level || 0), 0) / Math.max(1, army.length)).toFixed(1), tiers: [1, 2, 3].map(k => army.filter(a => (L.TYPES[a.type].tier || 1) === k).length).join('/'), gold: Math.round(ec.res.gold) });
    if (sim.result.reason === 'Fienden nådde flammen') break;
    t = 30;
  }
  return log;
}

module.exports = { load, playGame, bot };
if (require.main === module) {
  const runs = +(process.argv[2] || 10);
  const extra = process.argv[3] ? fs.readFileSync(process.argv[3], 'utf8') : '';
  const L = load(extra);
  const per = {}; const ends = [];
  let sample;
  for (let r = 0; r < runs; r++) {
    const log = playGame(L); if (!sample) sample = log;
    ends.push(log.length);
    log.forEach(x => { const p = per[x.w] || (per[x.w] = { n: 0, win: 0 }); p.n++; if (x.win) p.win++; });
  }
  console.log('waves reached:', ends.join(' '));
  console.log('win% per wave:', Object.entries(per).map(([w, p]) => `${w}:${Math.round(p.win / p.n * 100)}`).join(' '));
  console.log('sample run:'); sample.forEach(x => console.log(JSON.stringify(x)));
}
