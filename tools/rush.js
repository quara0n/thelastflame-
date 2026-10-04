// Greedy economy player: workers everywhere, then Barracks as soon as affordable. Army costs approximated by
// spending ARMYFRAC of each wave's gold on soldiers. Prints the wave each Barracks level is reached.
const { load } = require('./game_sim.js');
const L = load();
const BUILD = +(process.argv[3] || 55), BATTLE = 60, ARMYFRAC = +(process.argv[4] || 0.5);
const ec = new L.Econ(); const got = {}; let t = 45;
for (let w = 1; w <= 30; w++) {
  ec.tick(t + BATTLE);
  // bounty + bonus
  const W = L.WAVES[w - 1]; let b = 0; L.buildWave(W).forEach(e => b += L.BOUNTY[e.type] || 0);
  const goldIn = b + L.waveBonus(w); ec.add({ gold: Math.round(goldIn * (1 - ARMYFRAC)) });
  for (let g = 0; g < 200; g++) {
    let did = false;
    if (ec.buyBarracks()) { did = true; got[ec.barracks + 1] = got[ec.barracks + 1] || w; continue; }
    for (const k of ['iron', 'coal']) if (!did && !ec.nodes[k].unlocked && ec.unlockNode(k)) did = true;
    for (const k of ['timber', 'stone', 'iron', 'coal', 'gold']) if (!did && ec.nodes[k].unlocked && ec.nodes[k].workers < ec.cap(k) && ec.res.gold >= ec.workerPrice()) did = ec.addWorker(k);
    if (!did && ec.tools < 3 && ec.buyTools()) did = true;
    for (const k of ['timber', 'stone', 'iron', 'coal']) if (!did && ec.nodes[k].unlocked && !ec.nodes[k].expanded && ec.res.gold > 30 && ec.expandNode(k)) did = true;
    if (!did) break;
  }
  t = BUILD;
}
console.log('BUILD', BUILD, 'armyfrac', ARMYFRAC, 'Barracks tier reached at wave:', JSON.stringify(got), 'res now', JSON.stringify(Object.fromEntries(Object.entries(ec.res).map(([k,v])=>[k,Math.round(v)]))));
