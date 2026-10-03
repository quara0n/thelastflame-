// Logikken fra Kamptest 1 med oppgraderinger lagt på (brukes til å måle styrken til enkelt-units).
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const html = fs.readFileSync(path.join(__dirname, '../prototype/kamptest-1.html'), 'utf8');
const a = html.indexOf('// ===== The Last Flame — kampsimulering'), b = html.indexOf('// ===== The Last Flame — musikk');
module.exports = execFileSync('python3', ['-c', 'import sys; sys.path.insert(0, sys.argv[1]); from patch import patch; print(patch(sys.stdin.read()))', __dirname], { input: html.slice(a, b), maxBuffer: 1 << 26 }).toString();
