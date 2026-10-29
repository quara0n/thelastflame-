// Runs the whole automatic test and writes one short report: autotest-report/RAPPORT.md (plus screenshots).
//   1. logic_check.js: whole bot games and random armies, no graphics (about 2 minutes).
//   2. browser_playtest.js: the real page at phone size through 30 waves with extra resources (20–40 minutes).
// Usage: node tools/autotest/run.js [--html prototype/kamptest-2.html] [--quick] [--three path/to/three.min.js]
//   --quick: fewer games and only 5 waves in the browser (a few minutes), for a fast check after a change.
const fs = require('fs'), path = require('path'), { spawnSync } = require('child_process');

const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const ROOT = path.join(__dirname, '..', '..'), OUT = path.join(ROOT, 'autotest-report');
const html = path.resolve(opt('html', path.join(ROOT, 'prototype', 'kamptest-2.html'))), quick = args.includes('--quick'), three = opt('three', null);
fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT, { recursive: true });

const run = (file, extra) => spawnSync(process.execPath, [path.join(__dirname, file), '--html', html, ...extra], { stdio: 'inherit' }).status;
const logicCode = run('logic_check.js', ['--games', quick ? '8' : '40', '--fuzz', quick ? '60' : '300', '--out', path.join(OUT, 'logic.json')]);
const browserCode = run('browser_playtest.js', ['--waves', quick ? '5' : '30', '--rich', '--out', OUT, ...(three ? ['--three', three] : [])]);

const read = f => { try { return JSON.parse(fs.readFileSync(path.join(OUT, f), 'utf8')); } catch (e) { return null; } };
const L = read('logic.json'), B = read('browser.json');
const icon = { krasj: '🔴', feil: '🟠', fast: '🟡', mobil: '📱', tekst: '🔤', konsoll: '⚪' };
const lines = [`# Automatisk test – ${new Date().toISOString().slice(0, 16).replace('T', ' ')}`, '', `Side: \`${path.relative(ROOT, html)}\``, ''];
const all = [...(L ? L.problems : []).map(p => ({ ...p, where: 'logikk' })), ...(B ? B.problems : []).map(p => ({ ...p, where: 'nettleser' }))];
lines.push(all.length ? `## ${all.length} problemer funnet` : '## Ingen problemer funnet', '');
for (const p of all) lines.push(`- ${icon[p.kind] || '•'} **${p.kind}** (${p.where}${p.wave ? ', wave ' + p.wave : ''}, ${p.count}×): ${p.text}`);
if (L) {
  lines.push('', '## Balanse (testspilleren, uten ekstra ressurser)', '', `Kom til wave ${L.reachedWave.median} i snitt (median av ${L.games} spill).`);
  if (L.walls.length) lines.push(`Brå hopp i vanskelighet: wave ${L.walls.join(', ')}.`);
  lines.push('', 'Holdt per wave: ' + L.waves.map(w => `${w.wave}: ${w.held} %`).join(' · '));
}
if (B) {
  lines.push('', '## Nettleser (telefon, 390 px)', '', `${B.reached} waves spilt på ${B.minutes} min. Utfall: ${B.outcome || 'ikke ferdig'}.`,
    'Lavest bildefrekvens: ' + (B.waves.length ? B.waves.slice().sort((a, b) => a.fps - b.fps).slice(0, 3).map(w => `wave ${w.wave} (${w.fps} fps)`).join(', ') : '–') + ' (i en testmaskin uten skjermkort; en telefon er raskere).',
    '', 'Skjermbilder av hver wave ligger i samme mappe.');
}
fs.writeFileSync(path.join(OUT, 'RAPPORT.md'), lines.join('\n') + '\n');
console.log('\n' + lines.join('\n'));
process.exitCode = logicCode || browserCode ? 1 : 0;
