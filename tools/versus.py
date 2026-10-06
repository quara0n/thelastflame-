"""1 v 1 against the computer (4 Oct 2026). Applied by build_v2.py.
The rival is the same bot that game_sim.js uses for balance (its source is copied in at build time). It plays its own
game in the background, one wave at a time, with its own economy, army and Warden. Both sides can send creatures from
the current world; sends join the other side's next wave. A sent creature that breaks through gives the sender half its
price back. Whoever's flame goes out first loses."""
import re
from pathlib import Path
from patch import sub

HERE = Path(__file__).parent

LOGIC = r"""
// ===== 1 mot 1 mot computer (4. okt 2026) =====
// Priser for å sende skapninger (gull). World 2 koster ca. 2 ganger, World 3 ca. 3,5 ganger World 1.
const SEND = { husk: 3, spider: 3, spitter: 5, serpent: 5, brute: 8, beetle: 9, broodmother: 12, stalker: 6, colossus: 30,
  wolf: 6, boar: 16, locust: 5, mantis: 16, thornling: 9, treant: 50, crab: 12, siren: 12, acolyte: 12, seraph: 25,
  raptor: 10, hornback: 30, snapper: 8, clubtail: 28, urdragon: 45, tyrant: 70, frillspitter: 16, earthshaker: 90, revenant: 20 };
const RIVAL_BREAK = 55;
// Knapper for 1 mot 1: hvor mye computeren sender (andel av gullet), hvor sterke portalens egne waves er, og sendeprisene.
const VERSUS = { share: 0.35, wave: 0.5, price: 1, smart: true };
const sendPrice = k => Math.max(1, Math.round(SEND[k] * VERSUS.price));
const versusScale = W => ({ hp: W.scale.hp * VERSUS.wave, dmg: W.scale.dmg * Math.sqrt(VERSUS.wave) });
// Det man kan sende i wave wi: skapninger fra verdenen man er i nå, som allerede har vist seg.
function sendable(wi) {
  const W = WAVES[Math.min(wi, WAVES.length - 1)];
  return Object.keys(SEND).filter(k => FIRST_SEEN[k] && FIRST_SEEN[k] <= W.n && WAVES[FIRST_SEEN[k] - 1].world === W.world);
}
// Sendte skapninger stiller seg bak waven, i rader på åtte.
function placeSent(list, base) {
  if (!list || !list.length) return [];
  const z0 = (base.length ? Math.min(...base.map(e => e.z)) : -15) - 2;
  return list.map((s, i) => {
    const r = Math.floor(i / 8), inRow = Math.min(8, list.length - r * 8), c = i % 8;
    return { type: s.type, x: (c - (inRow - 1) / 2) * 1.7, z: Math.max(MAP.portalZ + 1.5, z0 - r * 1.7), sent: { by: s.by, price: s.price } };
  });
}
// Gull avsenderen får tilbake: halve prisen for hver sendt skapning som kom seg gjennom porten.
function sentLeaks(sim, by) {
  let g = 0;
  for (const u of sim.units) if (u.sent && u.sent.by === by && (u.leaked || u.z > MAP.gateZ + 1.5)) g += u.sent.price / 2;
  return Math.floor(g);
}
__BOT__
// ----- Rivalens sende-hjerne (versjon 19) -----
// Ser på motstanderens hær og velger skapningene den er svakest mot: flyvere når den har få skyttere, tykt skall når
// den slår svakt, raptorer når den har mange skyttere, sverm når den mangler områdeskade. Den husker hvor langt
// det den sendte sist kom, og sparer opp til et stort angrep når porten din er skadet eller en ny art kommer.
function foeProfile(foe) {
  const p = { dps: 0, ranged: 0, splash: 0, hit: 0, pierce: 0, aa: 0, n: 0 };
  if (!foe || !foe.army || !foe.army.length) return null;
  const ft = foe.ec ? foe.ec.types(TYPES) : TYPES;
  for (const a of foe.army) {
    const t = ft[a.type] || TYPES[a.type]; if (!t) continue;
    const m = 1 + 0.2 * (a.level || 0), d = t.dmg * m / (t.interval || 1);
    p.dps += d; p.hit += d * t.dmg * m; p.pierce += d * (t.pierce || 0); p.n++;
    if (t.ranged) p.ranged += d;
    if (t.splash) p.splash += d;
  }
  if (!p.dps) return null;
  const arch = foe.ec ? (ARCHERS[foe.ec.archers] || ARCHERS[0]).count * 12 : 0;
  p.hit /= p.dps; p.pierce /= p.dps;
  p.aa = Math.min(1, (p.ranged + arch) / (p.dps + arch));
  p.rangedShare = p.ranged / p.dps; p.splashShare = p.splash / p.dps;
  p.gate = foe.ec ? foe.ec.gateHp / Math.max(1, foe.ec.gateMax()) : 1;
  return p;
}
// Hvor mye trøbbel én gullbit av skapning k gir denne hæren. Høyere er bedre for den som sender.
function sendValue(k, prof, memo) {
  const t = TYPES[k], price = sendPrice(k);
  if (!prof) return 1 / price;
  const eff = Math.max(1, prof.hit - Math.max(0, (t.armor || 0) - prof.pierce));
  const tough = t.hp * (prof.hit / eff), dps = t.dmg / (t.interval || 1) * (t.cleave ? 1.3 : 1);
  let v = Math.sqrt(tough * dps) / price;
  if (t.flies) v *= 0.7 + 1.6 * (1 - prof.aa);
  if (t.hunts === 'ranged') v *= 0.8 + 0.9 * prof.rangedShare;
  if (t.swarm) v *= 1.15 - 0.9 * prof.splashShare;
  if (t.ranged) v *= 1.1 - 0.4 * prof.rangedShare;
  return v * ((memo && memo[k]) || 1);
}
function pickSends(opts, money, prof, memo) {
  const ranked = opts.map(k => ({ k, v: sendValue(k, prof, memo) * (0.88 + Math.random() * 0.24) })).sort((a, b) => b.v - a.v);
  const out = []; if (!ranked.length) return out;
  // 70 % av pengene på det beste valget, resten på nest beste, og småpenger på det billigste av de to.
  const plan = [[ranked[0].k, money * 0.7], [(ranked[1] || ranked[0]).k, money * 0.3]];
  let left = money;
  for (const [k, part] of plan) { let m = part; const pr = sendPrice(k); while (m >= pr && left >= pr && out.length < 24) { out.push(k); m -= pr; left -= pr; } }
  const cheap = ranked.slice(0, 2).map(r => r.k).sort((a, b) => sendPrice(a) - sendPrice(b))[0];
  while (left >= sendPrice(cheap) && out.length < 24) { out.push(cheap); left -= sendPrice(cheap); }
  return out;
}
const RIVAL_L = { TYPES, BARRACKS, NODES, UPGRADES, MAX_LEVEL, supplyOf, ARCHERS, upgradeSpent, REFUND, WALLS };
class Rival {
  constructor() { this.ec = new Econ(); this.army = []; this.memo = {}; this.bank = 0; this.intent = ''; this.t = 45; this.alive = true; this.hold = null; this.sim = null; this.wi = -1; this.shop(); this.makeView(); }
  // Rivalen handler for pengene sine, men holder av det han vil sende.
  shop() {
    const ec = this.ec, keep = this.wi + 1 >= 2 ? Math.min(Math.floor(ec.res.gold), Math.floor(ec.res.gold * VERSUS.share) + this.bank) : 0;
    ec.res.gold -= keep; rivalBot(RIVAL_L, ec, this.army, Math.min(WAVES.length - 1, this.wi + 1)); ec.res.gold += keep; this.saved = keep;
  }
  // Det som vises av rivalen mellom wavene: hæren hans hjemme.
  makeView() { const ec = this.ec; this.view = new Sim(this.army, { types: ec.types(TYPES), enemies: [], gateHp: ec.gateHp, gateMax: ec.gateMax(), archers: ARCHERS[ec.archers].count }); }
  running() { return !!(this.sim && !this.sim.result); }
  // Waven starter: rivalen samler inn, handler, og kampen bygges. Den kjøres steg for steg (live) eller med end().
  begin(wi, incoming) {
    const ec = this.ec, W = WAVES[wi];
    ec.tick(this.t); this.wi = wi;
    this.budget = wi >= 2 ? Math.min(Math.floor(ec.res.gold), Math.max(this.saved || 0, Math.floor(ec.res.gold * VERSUS.share) + this.bank)) : 0;
    ec.res.gold -= this.budget; rivalBot(RIVAL_L, ec, this.army, wi); ec.res.gold += this.budget;
    const base = buildWave(W); this.incoming = incoming || [];
    this.sim = new Sim(this.army, { types: ec.types(TYPES, versusScale(W)), enemies: base.concat(placeSent(this.incoming, base)), gateHp: ec.gateHp, gateMax: ec.gateMax(), archers: ARCHERS[ec.archers].count });
  }
  // Waven er ferdig (spoles frem om nødvendig). Gir gull for lekk til spilleren og det rivalen sender tilbake.
  end(foe) {
    const ec = this.ec, sim = this.sim, wi = this.wi, W = WAVES[wi];
    while (!sim.result) sim.step(1 / 15);
    ec.tick(sim.t); ec.gateHp = sim.gateHp; this.t = RIVAL_BREAK;
    let bounty = 0; sim.units.forEach(u => { if (u.side === 'e' && !u.alive) bounty += BOUNTY[u.type] || 0; });
    ec.add({ gold: bounty });
    if (sim.result.win) ec.add({ gold: waveBonus(W.n) });
    const lost = sim.result.reason === 'Fienden nådde flammen';
    if (lost) this.alive = false;
    const leaked = sim.units.filter(u => u.sent && u.sent.by === 'p' && (u.leaked || u.z > MAP.gateZ + 1.5)).length;
    this.hold = { wave: W.n, win: sim.result.win, lost, gate: Math.round(sim.gateHp), gateMax: ec.gateMax(), army: this.army.length,
      tier: ec.barracks + 1, got: this.incoming.length, leaked };
    const out = [], opts = sendable(wi);
    let money = Math.min(this.budget, Math.floor(ec.res.gold));
    if (this.smart !== undefined ? this.smart : VERSUS.smart) {
      // Sparer eller slår til: alt når porten din er skadet, en ny art kommer neste wave, eller sparegrisen er full.
      const prof = foeProfile(foe), nx = WAVES[wi + 1];
      this.strike = false;
      // Ny verden neste wave (sterkere skapninger kommer), hæren din har krympet (solgt for ny tier), porten er skadet,
      // eller han har spart i to runder.
      const newWorld = nx && nx.world !== WAVES[wi].world;
      const shrunk = prof && this.foeDps && prof.dps < this.foeDps * 0.85;
      const strike = !prof || prof.gate < 0.6 || newWorld || shrunk || this.bank >= money * 0.45;
      if (prof) this.foeDps = prof.dps;
      const spend = strike ? money : Math.floor(money * 0.5);
      const kinds = pickSends(opts, spend, prof, this.memo);
      kinds.forEach(k => { const pr = sendPrice(k); money -= pr; ec.res.gold -= pr; out.push({ type: k, by: 'r', price: pr }); });
      this.bank = strike ? 0 : Math.max(0, money); this.strike = strike && kinds.length > 0;
      const top = kinds.length ? kinds.reduce((c, k) => (c[k] = (c[k] || 0) + 1, c), {}) : {};
      const main = Object.keys(top).sort((a, b) => top[b] - top[a])[0];
      this.intent = !kinds.length ? 'sparer' : strike ? `stort angrep${main ? ' med ' + TYPES[main].name : ''}` : `sparer litt, sender ${main ? TYPES[main].name : ''}`;
      this.why = main && prof ? (TYPES[main].flies && prof.aa < 0.5 ? 'du har få skyttere' : TYPES[main].hunts === 'ranged' && prof.rangedShare > 0.4 ? 'du har mange skyttere' : TYPES[main].swarm && prof.splashShare < 0.2 ? 'du mangler områdeskade' : (TYPES[main].armor || 0) > prof.hit / 3 ? 'skallet tåler slagene dine' : '') : '';
    } else {
      for (let g = 0; g < 40 && out.length < 24; g++) {
        const can = opts.filter(k => sendPrice(k) <= money);
        if (!can.length) break;
        const k = can[Math.floor(Math.random() * can.length)], pr = sendPrice(k);
        money -= pr; ec.res.gold -= pr; out.push({ type: k, by: 'r', price: pr });
      }
    }
    const leakGold = sentLeaks(sim, 'p');
    this.sim = null;
    if (!lost) { this.shop(); }
    this.makeView();
    return { leakGold, out, lost, sim };
  }
  playWave(wi, incoming, foe) { this.begin(wi, incoming); return this.end(foe); }
  // Etter motstanderens wave: hvor langt kom det han sendte? Godt resultat gir den arten mer vekt neste gang.
  learn(sim, by) {
    const got = {};
    for (const u of sim.units) if (u.sent && u.sent.by === (by || 'r')) {
      const prog = u.leaked || u.z > MAP.gateZ + 1.5 ? 1 : Math.max(0, Math.min(1, (u.z - MAP.portalZ) / (MAP.gateZ - MAP.portalZ)));
      (got[u.type] = got[u.type] || []).push(prog);
    }
    for (const k in got) { const avg = got[k].reduce((a, b) => a + b, 0) / got[k].length; this.memo[k] = 0.6 * (this.memo[k] || 1) + 0.4 * (0.5 + 1.5 * avg); }
  }
}
"""

CSS = """
.foe.sent { border-color: #6b3a8a; box-shadow: inset 0 0 0 1px #6b3a8a; }
.senttag { position: absolute; top: 12px; left: 12px; font: 700 10px var(--mono); background: #a35ae0; color: #12061c; padding: 1px 6px; border-radius: 4px; }
.rival { display: flex; flex-direction: column; gap: 4px; }
.rival .rv-h { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
.rival .rv-h b { font-family: var(--display); font-size: 15px; }
.rival .rv-h span { font-size: 12px; color: var(--muted); }
.rival .gatebar2 i { background: #a35ae0; }
.sgrid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px; }
.scard { background: var(--panel-2); border: 1px solid var(--line); border-radius: 8px; display: flex; flex-direction: column; align-items: stretch; overflow: hidden; min-width: 0; position: relative; }
.scard img { width: 100%; height: 50px; object-fit: cover; object-position: 50% 35%; background: radial-gradient(circle at 50% 35%, #3a2224, #140e10); }
.scard .sn { font-size: 12px; font-weight: 600; padding: 3px 6px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.scard .sq { position: absolute; top: 4px; right: 4px; font: 600 11px var(--mono); background: #a35ae0; color: #12061c; border-radius: 999px; padding: 0 6px; }
.scard button { border: 0; border-top: 1px solid var(--line); background: none; padding: 6px; font-weight: 600; font-size: 12px; color: #c99af0; display: flex; justify-content: center; align-items: center; gap: 4px; }
.scard button.cant { color: var(--muted); }
.squeue { font-size: 12px; color: var(--fg); display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap; }
.squeue button { background: transparent; border: 1px solid var(--line); border-radius: 6px; padding: 4px 10px; font-size: 12px; }
.vs-tog { display: flex; align-items: center; gap: 6px; font-size: 12px; }
.vs-tog input { accent-color: #a35ae0; }
"""

def apply(s):
    gs = (HERE / 'game_sim.js').read_text()
    a = gs.index('function bot(L, ec, army, waveIdx) {'); b = gs.index('\nfunction playGame')
    bot = gs[a:b].replace('function bot(L, ec, army, waveIdx) {', '// Rivalens hjerne: den samme fornuftige spilleren som game_sim.js bruker til balansen.\nfunction rivalBot(L, ec, army, waveIdx) {', 1)
    s = sub(s, "if (typeof module !== 'undefined') module.exports = { supplyOf, WARDEN_GEAR,", LOGIC.replace('__BOT__', bot) + "\nif (typeof module !== 'undefined') module.exports = { supplyOf, WARDEN_GEAR,")
    # Sim husker hvem som sendte en skapning.
    s = sub(s, "    for (const e of enemies) this.units.push(this._make(id++, e.type, e.x, e.z, null));",
               "    for (const e of enemies) { const m = this._make(id++, e.type, e.x, e.z, null); if (e.sent) m.sent = e.sent; this.units.push(m); }")
    s = sub(s, "#om-remove { color: #f0a59d; }", "#om-remove { color: #f0a59d; }" + CSS)
    # Fane og panel.
    # Send-fanen står helt til høyre (etter Testbenk), 4 Oct.
    s = sub(s, '<button type="button" role="tab" id="tab-test" data-tab="test">Testbenk</button>',
               '<button type="button" role="tab" id="tab-test" data-tab="test">Testbenk</button>\n      <button type="button" role="tab" id="tab-send" data-tab="send">Send</button>')
    s = sub(s, '<div class="tabpane" id="pane-test" hidden></div>', '<div class="tabpane" id="pane-test" hidden></div>\n    <div class="tabpane" id="pane-send" hidden></div>')
    s = sub(s, "['army', 'village', 'build', 'test'].forEach(t => $('#pane-' + t).hidden = state.tab !== t);\n    if (state.tab === 'test') renderBench();",
               "['army', 'village', 'build', 'test', 'send'].forEach(t => $('#pane-' + t).hidden = state.tab !== t);\n    if (state.tab === 'test') renderBench();\n    if (state.tab === 'send') renderSend();")
    # Tilstand.
    s = sub(s, "    tool: null, together: true, nextSquad: 10,", "    versus: true, rival: new Rival(), sendQueue: [], incoming: [], rivalRes: null,\n    tool: null, together: true, nextSquad: 10,")
    # Wavene får med det rivalen sendte.
    s = sub(s, "      types: ec.types(TYPES, W.scale),\n      enemies: buildWave(W),\n      gateHp: ec.gateHp,", "      types: ec.types(TYPES, state.versus ? versusScale(W) : W.scale),\n      enemies: withSends(buildWave(W)),\n      gateHp: ec.gateHp,")
    s = sub(s, "  function startWave() {\n    if (state.phase !== 'build') return;\n    clearSelection(true);\n    state.tool = null;\n    rebuild();",
               "  const withSends = base => state.versus ? base.concat(placeSent(state.incoming, base)) : base;\n"
               "  function startWave() {\n    if (state.phase !== 'build') return;\n    clearSelection(true);\n    state.tool = null;\n"
               "    // Er rivalen fortsatt i sin forrige wave, spoles den ferdig først (så vi vet hva han sender).\n"
               "    if (state.versus && state.rival.running()) rivalDone();\n    if (state.phase !== 'build') return;\n"
               "    rebuild();\n"
               "    // Rivalen starter sin wave samtidig og kjemper live på sin egen slagmark.\n"
               "    if (state.versus && state.rival.alive) { state.rival.begin(state.wave, state.sendQueue); state.sentLast = state.sendQueue; state.sendQueue = []; state.racc = 0; }\n"
               "    state.incoming = [];   // de er nå med i waven din")
    s = sub(s, "    if (lostFlame) { state.phase = 'over'; state.outcome = 'lost'; }\n    else if (state.wave >= WAVES.length - 1) { state.phase = 'over'; state.outcome = 'won'; }",
               "    if (state.versus) {\n"
               "      const back = sentLeaks(sim, 'r'); if (back) state.rival.ec.add({ gold: back });\n      state.rival.learn(sim, 'r');\n"
                              "      report.rival = state.rival.running() ? { pending: true } : Object.assign({}, state.rival.hold, { sent: (state.sentLast || []).length, leakGold: state.rivalRes ? state.rivalRes.leakGold : 0 });\n"
               "    }\n"
               "    const rivalDown = state.versus && !state.rival.alive;\n"
               "    if (lostFlame || rivalDown) { state.phase = 'over'; state.outcome = lostFlame ? (rivalDown ? 'draw' : 'lost') : 'won-vs'; if (rivalDown && !lostFlame) sfx('victory'); }\n"
               "    else if (state.wave >= WAVES.length - 1) { state.phase = 'over'; state.outcome = state.versus && state.rival.alive ? 'draw-alive' : 'won'; }")
    s = sub(s, "      rebuild();\n    }\n    renderPanel(); showResult();\n  }",
               "      rebuild();\n      if (state.versus && state.incoming.length) setTimeout(() => toast(`Rivalen sender deg ${state.incoming.length} skapninger i wave ${curWave().n}. Se «Neste wave».`), 2800);\n    }\n    renderPanel(); showResult();\n  }")
    s = sub(s, "    state.phase = 'build'; state.paused = false; state.lastReport = null; state.outcome = null; state.summonTold = false;",
               "    state.phase = 'build'; state.paused = false; state.lastReport = null; state.outcome = null; state.summonTold = false;\n"
               "    state.rival = new Rival(); state.sendQueue = []; state.incoming = []; state.rivalRes = null; state.sentLast = [];")
    # Resultat.
    s = sub(s, "    const head = over ? (state.outcome === 'won' ? 'Flammen brenner fortsatt' : `Flammen falt på wave ${r.wave}`)",
               "    if (r.rival && r.rival.pending) why.push('Rivalen kjemper fortsatt sin wave. Se ham med «Rival»-knappen eller kartet.');\n"
               "    else if (r.rival) why.push(`Rivalen: ${r.rival.lost ? 'flammen falt' : r.rival.win ? 'holdt' : 'porten tok skade'} (port ${r.rival.gate}/${r.rival.gateMax}, ${r.rival.army} soldater, Tier ${r.rival.tier}). Du sendte ${r.rival.sent}, ${r.rival.leaked} kom gjennom${r.rival.leakGold ? `, +${r.rival.leakGold} gull` : ''}.`);\n"
               "    const head = over && state.outcome === 'won-vs' ? `Seier! Rivalens flamme falt på wave ${r.wave}` : over && state.outcome === 'draw' ? 'Begge flammene falt. Uavgjort.' : over && state.outcome === 'draw-alive' ? 'Begge flammene brenner etter wave 30. Uavgjort.' : over ? (state.outcome === 'won' ? 'Flammen brenner fortsatt' : `Flammen falt på wave ${r.wave}`)")
    # Neste wave viser det rivalen sender.
    s = sub(s, "        ${isNew ? '<span class=\"newtag\">NY</span>' : ''}<span class=\"u-role\">${T.role}</span></div>`;\n    }).join('');",
               "        ${isNew ? '<span class=\"newtag\">NY</span>' : ''}<span class=\"u-role\">${T.role}</span></div>`;\n    }).join('') + (state.versus ? sentChips(state.incoming, et) : '');")
    s = sub(s, "  function onUiClick(e) {\n",
               "  function onUiClick(e) {\n"
               "    const sd = e.target.closest('[data-send]'); if (sd) { sendOne(sd.dataset.send); return; }\n"
               "    if (e.target.closest('[data-unsend]')) { unsendLast(); return; }\n"
               "    const vt = e.target.closest('#vs-toggle'); if (vt) { if (state.wave === 0 && state.phase === 'build') { state.versus = vt.checked; refundQueue(); rebuild(); renderPanel(); } else { vt.checked = state.versus; toast('Kan bare endres før første wave. Start en ny kamp for å bytte.'); } return; }\n")
    UI = r"""
  // ---------- 1 mot 1: Send-fanen ----------
  function sentChips(list, et) {
    if (!list || !list.length) return '';
    const c = {}; list.forEach(s => c[s.type] = (c[s.type] || 0) + 1);
    return Object.entries(c).map(([k, n]) => `<div class="foe sent" data-tip="Sendt av rivalen. ${et[k].role}.">
        <img alt="" src="${portraits[k] || ''}"><div class="u-top"><span class="u-name">${et[k].name}</span><span class="u-count">×${n}</span></div>
        <span class="senttag">SENDT</span><span class="u-role">Fra rivalen</span></div>`).join('');
  }
  function sendOne(k) {
    const ec = state.econ;
    if (!state.versus) { toast('Slå på 1 mot 1 før første wave for å sende.'); return; }
    if (state.phase !== 'build') { toast('Du sender i byggefasen. De kommer med rivalens neste wave.'); return; }
    if (!state.rival.alive) { toast('Rivalens flamme har falt.'); return; }
    if (state.sendQueue.length >= 24) { toast('Maks 24 sendte per wave.'); return; }
    const cost = { gold: sendPrice(k) };
    if (!ec.can(cost)) { explainMissing(cost); return; }
    ec.pay(cost); state.sendQueue.push({ type: k, by: 'p', price: sendPrice(k) }); sfx('coin'); renderPanel();
  }
  function unsendLast() { const s = state.sendQueue.pop(); if (s) { state.econ.add({ gold: s.price }); renderPanel(); } }
  function refundQueue() { state.sendQueue.forEach(s => state.econ.add({ gold: s.price })); state.sendQueue = []; }
  function renderSend() {
    const ec = state.econ, r = state.rival, h = r.hold, build = state.phase === 'build', opts = sendable(state.wave), W = curWave();
    const count = {}; state.sendQueue.forEach(s => count[s.type] = (count[s.type] || 0) + 1);
    const spent = state.sendQueue.reduce((a, s) => a + s.price, 0);
    const status = !state.versus ? 'Av. Du spiller alene.' : !r.alive ? 'Rivalens flamme har falt.' : h ? `Wave ${h.wave}: ${h.win ? 'holdt' : 'porten tok skade'} · ${h.army} soldater · Tier ${h.tier}` : 'Har ikke kjempet ennå.';
    const gp = h ? Math.max(0, h.gate / h.gateMax * 100) : 100;
    $('#pane-send').innerHTML = `<section class="rival"><div class="rv-h"><b>Rival: computer</b><span>${status}</span></div>
        <div class="gatebar2" data-tip="Rivalens port"><i style="width:${gp}%"></i></div>
        <label class="vs-tog"><input type="checkbox" id="vs-toggle" ${state.versus ? 'checked' : ''}> 1 mot 1 mot computer ${tipIcon('Rivalen spiller sitt eget spill samtidig, med samme waves. Dere kan sende skapninger til hverandre. Den som mister flammen først, taper. Kan bare slås av eller på før første wave.')}</label></section>
      ${state.versus ? `<section><h2>Send til rivalen ${tipIcon(`Skapningene kommer med rivalens wave ${W.n}. Bryter en gjennom porten hans, får du halve prisen tilbake. Du kan sende skapninger fra ${WORLDS[W.world].name} som allerede har dukket opp.`)}</h2>
        <div class="sgrid">${opts.map(k => `<div class="scard"><img alt="" src="${portraits[k] || ''}">${count[k] ? `<span class="sq">${count[k]}</span>` : ''}<span class="sn">${TYPES[k].name}</span>
          <button type="button" data-send="${k}" class="${!build || ec.res.gold < sendPrice(k) ? 'cant' : ''}">${icon('gold', 13)}${sendPrice(k)}</button></div>`).join('')}</div>
        <div class="squeue"><span>${state.sendQueue.length ? `Sendes med wave ${W.n}: ${Object.entries(count).map(([k, n]) => `${n} ${TYPES[k].name}`).join(', ')} (${spent} gull)` : 'Ingen sendt ennå denne waven.'}</span>
          ${state.sendQueue.length && build ? '<button type="button" data-unsend="1">Angre siste</button>' : ''}</div>
        <p class="note">${state.incoming.length ? `Rivalen sender deg ${state.incoming.length} skapninger i wave ${W.n}${r.strike ? ' – et stort angrep' : ''}. De står i «Neste wave» i Hær-fanen.` : 'Rivalen har ikke sendt deg noe til neste wave.'}${r.why && state.incoming.length ? ` Han valgte dem fordi ${r.why}.` : ''}${r.bank > 0 ? ' Han sparer gull til et større angrep – pass på når porten din er skadet, eller når du selger units for å bytte tier.' : ''}</p></section>` : ''}`;
  }
"""
    s = sub(s, "  // ---------- Statkort for units i Hær-fanen ----------", UI + "\n  // ---------- Statkort for units i Hær-fanen ----------")
    return s
