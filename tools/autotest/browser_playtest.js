// Automatic playtest in a real browser at phone size (390 × 844, touch), so the whole page is tested:
// graphics, buttons, popups and the game loop, not only the battle logic.
// Each build phase: a "monkey" taps random buttons and the battlefield (like a curious player), then the bot player
// buys an army, and the real «Start wave» button is pressed. The battle runs at high speed.
// Watched all the time: JavaScript errors, NaN/undefined in the text on screen, the page getting wider than the phone,
// buttons off the edge of the screen, a game loop that freezes, waves that never end, and frame rate.
// Screenshots of every wave go into the report folder.
// Usage: node tools/autotest/browser_playtest.js [--html prototype/kamptest-2.html] [--waves 30] [--rich] [--taps 12]
//        [--three path/to/three.min.js] [--out autotest-report] [--headed]
//   --rich gives the bot extra resources every wave, so the run gets through all 30 waves and sees every world.
//   --three serves three.js from a local file and skips the network (when cdnjs is blocked, e.g. in a Claude sandbox).
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');

const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; }, flag = k => args.includes('--' + k);
const ROOT = path.join(__dirname, '..', '..');
const HTML = path.resolve(opt('html', path.join(ROOT, 'prototype', 'kamptest-2.html')));
const OUT = path.resolve(opt('out', path.join(ROOT, 'autotest-report')));
const WAVES = +opt('waves', 30), TAPS = +opt('taps', 12), RICH = flag('rich'), THREE = opt('three', null);
const SPEED = 30, WAVE_LIMIT_MS = 6 * 60 * 1000;
const { bot } = require(path.join(__dirname, '..', 'game_sim.js'));

fs.mkdirSync(OUT, { recursive: true });
const problems = [], waves = [];
let wave = 0;
const problem = (kind, text, extra) => {
  const same = problems.find(p => p.kind === kind && p.text === text);
  if (same) { same.count++; return; }
  problems.push({ kind, text, count: 1, wave, ...(extra || {}) });
  console.log(`  [${kind}] wave ${wave}: ${text}`);
};

// Runs inside the page: the same L object game_sim.js builds, but from the page's own globals.
const PAGE_LIB = `(() => { const o = n => { try { return eval(n); } catch (e) { return null; } };
  return { Sim, Econ, TYPES, WAVES, BARRACKS, NODES, TRACKS, BOUNTY, waveBonus, UPGRADES, MAX_LEVEL, supplyOf, ARCHERS, buildWave, upgradeSpent, REFUND, WALLS,
    heroBot: o('heroBot') || (() => {}), withHero: o('withHero') || (a => a), armyNeed: o('BOT_ARMY_NEED'), workerCap: o('BOT_WORKER_CAP'), heroAfterWave: o('heroAfterWave') || (() => null) }; })()`;

// Checks the page for things a player would see as broken.
async function lookForTrouble(page, when) {
  const r = await page.evaluate(() => {
    const out = { overflow: document.documentElement.scrollWidth - innerWidth, offscreen: [], words: [] };
    for (const b of document.querySelectorAll('button')) {
      if (!b.offsetParent) continue;
      const rc = b.getBoundingClientRect();
      if (rc.width > 0 && (rc.right > innerWidth + 2 || rc.left < -2)) out.offscreen.push((b.id || b.textContent.trim().slice(0, 24)) + ` (${Math.round(rc.left)}–${Math.round(rc.right)} px)`);
    }
    const text = document.body.innerText;
    for (const w of ['NaN', 'undefined', 'null', '[object Object]', 'Infinity']) {
      const m = text.match(new RegExp('.{0,30}\\b' + w.replace(/[[\]]/g, '\\$&') + '\\b.{0,30}'));
      if (m) out.words.push(m[0].replace(/\s+/g, ' ').trim());
    }
    return out;
  });
  if (r.overflow > 2) problem('mobil', `Siden er ${r.overflow} px bredere enn telefonen (${when})`);
  for (const b of r.offscreen.slice(0, 5)) problem('mobil', `Knapp utenfor skjermen: ${b} (${when})`);
  for (const w of r.words) problem('tekst', `Rar tekst på skjermen: «${w}»`);
}

// Taps random visible buttons (not the ones that end the game or change mode), then random spots on the battlefield.
async function monkey(page) {
  for (let i = 0; i < TAPS; i++) {
    const target = await page.evaluate(() => {
      const skip = /btn-new|btn-start|vs-toggle|team-toggle|vs-online|net-|intro|lob-|snd-/;
      const list = [...document.querySelectorAll('button, [role=button], .tab')].filter(b => {
        if (!b.offsetParent || b.disabled || skip.test(b.id || '') || /venn|Ny kamp|online/i.test(b.textContent)) return false;
        const r = b.getBoundingClientRect(); return r.width > 4 && r.height > 4 && r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth;
      });
      if (!list.length || Math.random() < 0.25) return { x: 40 + Math.random() * (innerWidth - 80), y: 120 + Math.random() * 300, what: 'slagmarken' };
      const b = list[Math.floor(Math.random() * list.length)], r = b.getBoundingClientRect();
      return { x: r.left + r.width / 2, y: r.top + r.height / 2, what: b.id || b.textContent.trim().replace(/\s+/g, ' ').slice(0, 30) };
    });
    try { await page.touchscreen.tap(target.x, target.y); } catch (e) { problem('feil', `Trykk feilet på ${target.what}: ${e.message}`); }
    await page.waitForTimeout(150);
    const phase = await page.evaluate(() => __dbg.state.phase);
    if (phase !== 'build') return phase;   // a tap may have started the wave; that is allowed
  }
  // Close whatever popups the monkey opened.
  await page.keyboard.press('Escape').catch(() => {});
  await page.evaluate(() => document.querySelectorAll('#bpop-close, #om-x, .pop-close, [data-close]').forEach(b => b.offsetParent && b.click())).catch(() => {});
  return 'build';
}

(async () => {
  const t0 = Date.now();
  const browser = await chromium.launch({ headless: !flag('headed'), args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 1 });   // 1 keeps the software renderer fast enough
  const page = await ctx.newPage();
  // With --three the run is offline: three.js comes from the local file and everything else on the net is skipped.
  if (THREE) await page.route('**/*', r => { const u = r.request().url();
    if (/three(\.min)?\.js$/.test(u)) return r.fulfill({ path: path.resolve(THREE), contentType: 'text/javascript' });
    return u.startsWith('file:') ? r.continue() : r.abort(); });
  page.on('pageerror', e => problem('krasj', `JavaScript-feil: ${e.message}`, { stack: String(e.stack || '').split('\n').slice(0, 3).join(' | ') }));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource|fonts\.g/.test(m.text())) problem('konsoll', m.text().slice(0, 200)); });
  page.on('crash', () => problem('krasj', 'Fanen krasjet (for lite minne eller GPU-feil)'));

  await page.goto('file://' + HTML + '#dbg');
  await page.waitForFunction(() => window.__dbg && __dbg.state, null, { timeout: 30000 });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(OUT, '00-start.png') });
  await lookForTrouble(page, 'startskjermen');
  const go = await page.$('#intro-go'); if (go && await go.isVisible()) await go.tap();
  await page.waitForTimeout(800);
  await page.evaluate(`window.__bot = ${bot.toString()}; window.__L = ${PAGE_LIB};`);
  await page.evaluate(() => { window.__frames = 0; const f = () => { window.__frames++; requestAnimationFrame(f); }; requestAnimationFrame(f); });

  let outcome = null;
  for (wave = 1; wave <= WAVES; wave++) {
    const s0 = await page.evaluate(() => ({ phase: __dbg.state.phase, wave: __dbg.state.wave }));
    if (s0.phase === 'over') { outcome = await page.evaluate(() => __dbg.state.outcome); break; }
    if (s0.phase.startsWith('arena')) {   // arena duel after waves 8/18/28 (only against the computer)
      await page.evaluate(() => { __dbg.state.speed = 30; }); await page.tap('#btn-start').catch(() => {});
      await page.waitForFunction(() => !__dbg.state.phase.startsWith('arena'), null, { timeout: WAVE_LIMIT_MS }).catch(() => problem('fast', 'Arenaen ble aldri ferdig'));
    }
    let phase = await monkey(page);
    await lookForTrouble(page, `byggefase wave ${wave}`);
    if (phase === 'build') {
      const bought = await page.evaluate(([rich]) => {
        const st = __dbg.state, ec = st.econ;
        if (rich) ec.add({ gold: 250 + 40 * st.wave, timber: 120, stone: 120, iron: 60, coal: 40 });
        const before = st.army.length;
        try { __bot(__L, ec, st.army, st.wave); } catch (e) { return { error: e.message }; }
        return { army: st.army.length, before, gold: Math.round(ec.res.gold) };
      }, [RICH]);
      if (bought.error) problem('krasj', `Boten krasjet i byggefasen: ${bought.error}`);
      await page.screenshot({ path: path.join(OUT, `w${String(wave).padStart(2, '0')}-bygg.png`) });
      await page.evaluate(() => window.scrollTo(0, 0));
      const start = await page.$('#btn-start');
      if (!start || !(await start.isVisible())) { problem('feil', '«Start wave»-knappen er ikke synlig'); await page.evaluate(() => __dbg.state.buildLeft = 0); }
      else await start.tap();
    }
    // The battle: high speed, count frames to catch a frozen loop.
    const f0 = await page.evaluate(sp => { __dbg.state.speed = sp; return window.__frames; }, SPEED);
    const tw = Date.now();
    let shot = false, ok = true, lastT = -1, sameSince = Date.now();
    while (true) {
      const s = await page.evaluate(() => ({ phase: __dbg.state.phase, paused: __dbg.state.paused, t: __dbg.sim ? __dbg.sim.t : 0 }));
      if (s.phase !== 'battle') break;
      // A monkey tap may have paused the battle; that is the player's choice, not a bug.
      if (s.paused) { await page.evaluate(() => { __dbg.state.paused = false; }); sameSince = Date.now(); }
      if (!shot && s.t > 8) { await page.evaluate(() => window.scrollTo(0, 0)); await page.screenshot({ path: path.join(OUT, `w${String(wave).padStart(2, '0')}-kamp.png`) }); shot = true; }
      // The battle clock must move. If it stands still for 15 s while the page still draws, the game loop has died.
      if (s.t !== lastT) { lastT = s.t; sameSince = Date.now(); }
      else if (Date.now() - sameSince > 15000) {
        const diag = await page.evaluate(async () => { const st = __dbg.state, a0 = st.acc; await new Promise(r => setTimeout(r, 500));
          return { paused: st.paused, speed: st.speed, acc0: a0, acc1: st.acc, tab: st.tab, result: __dbg.sim && __dbg.sim.result, units: __dbg.sim && __dbg.sim.units.length, versus: !!st.versus, team: !!st.team }; });
        problem('fast', `Spillet frøs midt i wave ${wave}: kampklokka sto stille på ${s.t.toFixed(1)} s`, { diag });
        await page.screenshot({ path: path.join(OUT, `w${String(wave).padStart(2, '0')}-frosset.png`) }); ok = false; break;
      }
      if (Date.now() - tw > WAVE_LIMIT_MS) { problem('fast', `Wave ${wave} ble aldri ferdig (${Math.round(s.t)} s spilltid)`); ok = false; break; }
      await page.waitForTimeout(1000);
    }
    const secs = (Date.now() - tw) / 1000;
    const r = await page.evaluate(() => { const st = __dbg.state, rep = st.lastReport || {}; return { win: rep.win, reason: rep.reason, simT: Math.round(rep.t || 0), army: st.army.length, gate: Math.round(st.econ.gateHp), phase: st.phase, outcome: st.outcome, frames: window.__frames }; });
    r.frames -= f0;
    waves.push({ wave, ...r, fps: Math.round(r.frames / Math.max(1, secs)), realSeconds: Math.round(secs) });
    console.log(`wave ${wave}: ${r.win ? 'holdt' : 'tapt'}${r.reason ? ' (' + r.reason + ')' : ''}, hær ${r.army}, port ${r.gate}, ${Math.round(r.frames / Math.max(1, secs))} fps`);
    await page.waitForTimeout(400);
    await lookForTrouble(page, `etter wave ${wave}`);
    if (!ok || r.phase === 'over') { outcome = r.outcome; await page.screenshot({ path: path.join(OUT, 'slutt.png') }); break; }
  }
  await browser.close();
  const report = { html: path.relative(ROOT, HTML), rich: RICH, minutes: +((Date.now() - t0) / 60000).toFixed(1), reached: waves.length, outcome, waves, problems };
  fs.writeFileSync(path.join(OUT, 'browser.json'), JSON.stringify(report, null, 2));
  console.log(`Nettlesertest: ${waves.length} waves på ${report.minutes} min, utfall: ${outcome || 'ikke ferdig'}. ${problems.length} problemtyper.`);
  process.exitCode = problems.some(p => p.kind === 'krasj') ? 1 : 0;
})().catch(e => { console.error('Testen selv feilet:', e); process.exitCode = 2; });
