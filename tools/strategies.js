// Play styles for the test player (version 33, Rune: «everything should be used, at least portions of it,
// but some might focus on other parts and still get the job done»). Each style is code appended to the game logic
// (game_sim.js load(extra)) that replaces wardenBot, the bot's spending on everything beyond army, workers and Barracks.
// Usage: node strategies.js [games per style=24] [style …]  (runs the styles side by side and compares them)
const PARTS = `
const _sp = (ec, c, g, i) => c && ec.can(c) && ec.res.gold >= (c.gold || 0) + g && (ec.res.iron || 0) >= (c.iron || 0) + i;
const BOTP = {
  tools(ec, w, early) { const t = TOOLS[ec.tools]; return !!t && (early ? w >= 3 : ec.barracks > ec.tools) && (ec.res.timber || 0) >= t.cost.timber + (early ? 15 : 40) && _sp(ec, t.cost, 15, 5) && ec.buyTools(); },
  forge(ec, w) { if (w < 4) return false; for (const k of ['melee', 'ranged', 'armor']) { const lv = TRACKS[k].levels[ec.up[k]]; if (lv && !ec.trackLocked(k) && _sp(ec, lv.cost, 20, 5) && ec.buyTrack(k)) return true; } return false; },
  tech(ec, w) { const lv = TRACKS.tech.levels[ec.up.tech]; return w >= 6 && !!lv && (ec.res.coal || 0) >= (lv.cost.coal || 0) + 8 && _sp(ec, lv.cost, 20, 8) && ec.buyTrack('tech'); },
  wgear(ec, w, g, i) { const k = Object.keys(WARDEN_GEAR).sort((a, b) => ec.warden[a] - ec.warden[b])[0], lv = WARDEN_GEAR[k].levels[ec.warden[k]]; return !!lv && _sp(ec, lv.cost, g, i) && ec.buyWardenGear(k); },
  wabil(ec, w, g, i) { for (const k of ['stun', 'spin', 'freeze']) { const lv = WARDEN_ABIL[k].levels[ec.warden.abil[k]]; if (lv && _sp(ec, lv.cost, g, i) && ec.buyWardenAbility(k)) return true; } return false; },
  hgear(ec, w, g, i) { if (!ec.hero) return false; const k = Object.keys(HERO_GEAR).sort((a, b) => ec.heroGearLevel(a) - ec.heroGearLevel(b))[0], c = ec.heroGearCost(k); return !!c && _sp(ec, c, g, i) && ec.buyHeroGear(k); },
  wall(ec, w) { for (const k of ['ballista', 'oil']) { const n = ec.wallNext(k); if (n && _sp(ec, n.cost, 15, 5) && ec.buyWallGear(k)) return true; }
    const a = ARCHERS[ec.archers + 1]; if (a && _sp(ec, a.cost, 10, 0) && ec.buyArchers()) return true; return false; },
  conv(ec, w) { for (const k of ['smelter', 'kiln']) { const n = ec.convNext(k); if (n && _sp(ec, n.cost, 15, 0) && ec.buyConv(k)) return true; } return false; },
};
const _heal = ec => { if (ec.wardenHp != null && ec.wardenHp < 0.6) { const c = ec.wardenHealCost(); if (c && ec.res.gold >= c.gold + 20) ec.healWarden(); } };
const _style = steps => function (ec, w) { _heal(ec); for (let g = 0; g < 6; g++) if (!steps.some(f => f(ec, w))) break; };
// The balanced player's spending (same pace as wardenBot): a little Warden every third wave, tech every eighth.
const _gearN = ec => ec.warden.sword + ec.warden.shield + ec.warden.armor, _abilN = ec => ec.warden.abil.stun + ec.warden.abil.spin + ec.warden.abil.freeze;
const _hgN = ec => ec.hero ? Object.keys(HERO_GEAR).reduce((n, k) => n + ec.heroGearLevel(k), 0) : 0, _wallN = ec => ec.wallLv('ballista') + ec.wallLv('oil') + ec.archers;
const MIX = [(ec, w) => BOTP.tools(ec, w), BOTP.forge, (ec, w) => w >= 4 && _gearN(ec) < Math.floor(w / 3) && BOTP.wgear(ec, w, 50, 25),
  (ec, w) => w >= 6 && _abilN(ec) < Math.floor((w - 2) / 4) && BOTP.wabil(ec, w, 50, 25), (ec, w) => w >= 8 && ec.up.tech < Math.floor(w / 8) && BOTP.tech(ec, w)];
`;
const off = (...m) => m.map(k => `Econ.prototype.${k} = () => false;`).join(' ');
const STYLES = {
  // The default test player: a bit of everything (wardenBot in botplay.py as it is).
  balanced: '',
  // Leaning styles: one area first and early, then the same mix as the balanced player.
  army: PARTS + `wardenBot = _style([BOTP.forge, ...MIX]);`,
  // Economy: more workers (accepts dearer ones) and worker tools before the Barracks asks for them.
  economy: PARTS + `const BOT_WORKER_CAP = w => 22 + 5 * w; wardenBot = _style([(ec, w) => BOTP.tools(ec, w, true), ...MIX]);`,
  // Warden: about twice the balanced pace of gear and abilities.
  warden: PARTS + `wardenBot = _style([(ec, w) => w >= 3 && _gearN(ec) < Math.floor(w / 1.5) && BOTP.wgear(ec, w, 30, 10), (ec, w) => w >= 4 && _abilN(ec) < Math.floor(w / 2.5) && BOTP.wabil(ec, w, 30, 10), ...MIX]);`,
  // Hero: hero gear about one piece every third wave from wave 3.
  hero: PARTS + `wardenBot = _style([(ec, w) => w >= 3 && _hgN(ec) < Math.floor(w / 3) && BOTP.hgear(ec, w, 30, 10), ...MIX]);`,
  // Defence: wall gear and wall archers about one step every third wave, plus tech for the shooters.
  defence: PARTS + `wardenBot = _style([(ec, w) => w >= 4 && _wallN(ec) < Math.floor(w / 3) && BOTP.wall(ec, w), BOTP.tech, ...MIX]);`,
  // One-trick checks: everything beyond army and workers goes into one thing. These should NOT beat the mixed styles.
  onlyWarden: PARTS + `wardenBot = _style([(ec, w) => w >= 3 && BOTP.wgear(ec, w, 10, 3), (ec, w) => w >= 4 && BOTP.wabil(ec, w, 10, 3)]); ${off('buyWallGear', 'buyConv', 'buyHeroGear', 'buyTrack', 'buyTools')}`,
  onlyHero: PARTS + `wardenBot = _style([(ec, w) => w >= 3 && BOTP.hgear(ec, w, 10, 3)]); ${off('buyWallGear', 'buyConv', 'buyWardenGear', 'buyWardenAbility', 'buyTrack', 'buyTools')}`,
  onlyWall: PARTS + `wardenBot = _style([(ec, w) => w >= 4 && BOTP.wall(ec, w)]); ${off('buyConv', 'buyHeroGear', 'buyWardenGear', 'buyWardenAbility', 'buyTrack', 'buyTools')}`,
  onlyForge: PARTS + `wardenBot = _style([BOTP.forge]); ${off('buyWallGear', 'buyConv', 'buyHeroGear', 'buyWardenGear', 'buyWardenAbility', 'buyTools')}`,
  // Rune: surviving on Tier 1–2 is not an option. The balanced player who stops at Barracks II should fail in the later waves.
  lowTier: `{ const _bb = Econ.prototype.buyBarracks; Econ.prototype.buyBarracks = function () { return this.barracks >= 1 ? false : _bb.call(this); }; }`,
  // The balanced player who never buys the Forge (does the Forge alone decide the game?).
  noForge: off('buyTrack'),
};
module.exports = { STYLES };

if (require.main === module) {
  const { execFileSync, spawn } = require('child_process');
  const games = +(process.argv[2] || 24), names = process.argv.slice(3).length ? process.argv.slice(3) : Object.keys(STYLES);
  if (process.env.STYLE_CHILD) {
    // Child: play the games for one style and print the end waves.
    const { load, playGame } = require('./game_sim.js');
    if (!(process.env.STYLE_CHILD in STYLES)) throw new Error('unknown style ' + process.env.STYLE_CHILD);
    const L = load(STYLES[process.env.STYLE_CHILD]);
    const ends = []; for (let r = 0; r < games; r++) ends.push(playGame(L).length);
    console.log(JSON.stringify(ends));
  } else {
    const out = {}; let running = 0, i = 0;
    const next = () => {
      if (i >= names.length) { if (!running) report(); return; }
      const n = names[i++]; running++;
      let buf = ''; const p = spawn(process.execPath, [__filename, String(games)], { env: { ...process.env, STYLE_CHILD: n } });
      p.stdout.on('data', d => buf += d); p.stderr.on('data', d => process.stderr.write(d));
      p.on('close', () => { out[n] = JSON.parse(buf.trim().split('\n').pop()); running--; next(); });
    };
    const report = () => {
      for (const n of names) { const e = out[n].slice().sort((a, b) => a - b), med = e[e.length >> 1];
        console.log(`${n.padEnd(9)} median ${String(med).padStart(2)}  reach 10: ${e.filter(x => x >= 10).length}/${e.length}  reach 20: ${e.filter(x => x >= 20).length}  win 30: ${e.filter(x => x >= 30).length}`); }
    };
    for (let k = 0; k < 4; k++) next();
  }
}
