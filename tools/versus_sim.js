// Two computer players against each other with sends. Usage: node tools/versus_sim.js [matches=20] [sendShare]
const { load } = require('./game_sim.js');
const N = +(process.argv[2] || 20), knobs = process.argv[3] || '{}';
const extra = ';Object.assign(VERSUS, ' + knobs + ');';
const L = load(extra);
const ends = [], sentTotals = [];
for (let m = 0; m < N; m++) {
  const A = new L.Rival(), B = new L.Rival();
  let toA = [], toB = [], end = 30, winner = 'both';
  for (let wi = 0; wi < 30; wi++) {
    const ra = A.playWave(wi, toA), rb = B.playWave(wi, toB);
    A.ec.add({ gold: ra.leakGold ? 0 : 0 }); // leak gold flows to the sender
    B.ec.add({ gold: ra.leakGold }); A.ec.add({ gold: rb.leakGold });
    sentTotals.push(ra.out.length + rb.out.length);
    toA = rb.out.map(s => ({ ...s, by: 'p' })); toB = ra.out.map(s => ({ ...s, by: 'p' }));
    if (ra.lost || rb.lost) { end = wi + 1; winner = ra.lost && rb.lost ? 'draw' : ra.lost ? 'B' : 'A'; break; }
  }
  ends.push(end);
}
ends.sort((a, b) => a - b);
console.log('match ends at wave:', ends.join(' '), '| median', ends[ends.length >> 1], '| avg sends per wave per side', (sentTotals.reduce((a, b) => a + b, 0) / sentTotals.length / 2).toFixed(1));
