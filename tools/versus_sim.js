// Two computer players against each other with sends.
// Usage: node tools/versus_sim.js [matches=20] [knobs JSON] [mode]
//   mode 'mix' (default): A uses the smart send brain, B picks sends at random. Shows if the brain helps.
//   mode 'smart' / 'dumb': both sides the same.
const { load } = require('./game_sim.js');
const N = +(process.argv[2] || 20), knobs = process.argv[3] || '{}', mode = process.argv[4] || 'mix';
const L = load(';Object.assign(VERSUS, ' + knobs + ');');
const ends = [], sentTotals = [], res = { A: 0, B: 0, draw: 0, both: 0 };
for (let m = 0; m < N; m++) {
  const A = new L.Rival(), B = new L.Rival();
  A.smart = mode !== 'dumb'; B.smart = mode === 'smart';
  let toA = [], toB = [], end = 30, winner = 'both';
  for (let wi = 0; wi < 30; wi++) {
    const ra = A.playWave(wi, toA, B), rb = B.playWave(wi, toB, A);
    B.ec.add({ gold: ra.leakGold }); A.ec.add({ gold: rb.leakGold });   // leak gold flows to the sender
    A.learn(rb.sim, 'p'); B.learn(ra.sim, 'p');                          // each side sees how its own sends did
    sentTotals.push(ra.out.length + rb.out.length);
    toA = rb.out.map(s => ({ ...s, by: 'p' })); toB = ra.out.map(s => ({ ...s, by: 'p' }));
    if (ra.lost || rb.lost) { end = wi + 1; winner = ra.lost && rb.lost ? 'draw' : ra.lost ? 'B' : 'A'; break; }
  }
  ends.push(end); res[winner]++;
}
ends.sort((a, b) => a - b);
console.log(`mode ${mode}: A (${mode === 'dumb' ? 'random' : 'smart'}) wins ${res.A}, B (${mode === 'smart' ? 'smart' : 'random'}) wins ${res.B}, draws ${res.draw}, both alive ${res.both}`);
console.log('match ends at wave:', ends.join(' '), '| median', ends[ends.length >> 1], '| avg sends per wave per side', (sentTotals.reduce((a, b) => a + b, 0) / sentTotals.length / 2).toFixed(1));
