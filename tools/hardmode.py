"""Version 28 (11 Oct 2026), Rune's feedback after playing version 27: harder waves, scarcer gold, coal that is reachable.
- Gate bug: big creatures (Colossus, Treant, Hornback, Clubtail, Tyrant, Earthshaker) stopped a little short of the gate
  because of their size and never started hitting it. Now a creature counts as at the gate when its body touches it.
- Ranged units reach less far: everything past 6 m is cut by 40 % (Longfang 12 → 9.6 m, Skyspear 14 → 10.8 m), and
  range upgrades give +1 m instead of +2.
- The Gatehouse gets two new defences: boiling oil (coal; burns everything at the gate) and ballistae (heavy bolts that go
  through armour, good against giants).
- Two new village buildings turn the timber and stone that pile up into what is scarce: the charcoal kiln (timber → coal)
  and the smelter (stone → iron).
Numbers for workers, Barracks coal and wave size live in economy.json and waves30.py. Applied by build_v2.py after ui_tidy.py."""
from patch import sub

LOGIC = r"""
// ===== Versjon 28: kortere rekkevidde, forsvar på muren, kullmile og smelteovn =====
// Skyttere: alt over 6 m kortes ned med 40 %. Rekkevidde-oppgraderinger gir +1 m i stedet for +2.
(() => {
  for (const k in TYPES) { const t = TYPES[k]; if (t.side !== 'p' || !t.ranged || t.range <= 6) continue;
    const r = +(6 + (t.range - 6) * 0.6).toFixed(1); t.aggro = +(t.aggro - (t.range - r)).toFixed(1); t.range = r; }
  for (const k in UPGRADES) for (const u of UPGRADES[k]) if (u.mod && u.mod.range > 1) u.mod.range = 1;
})();
// Kull: Barracks IV og V krevde 105 og 174 kull, det tok mange waves med tre kullarbeidere. Nå 40 % av det.
for (const i of [3, 4]) if (BARRACKS[i].cost.coal) BARRACKS[i].cost.coal = Math.round(BARRACKS[i].cost.coal * 0.4);
// Forsvar på muren. Kokende olje: hvert 5. sekund brenner alle fiender ved porten. Ballista: tunge bolter mot de største.
const WALL_OIL = [
  { dmg: 0 },
  { dmg: 35, cost: { gold: 30, iron: 10, coal: 8 } },
  { dmg: 70, cost: { gold: 50, iron: 18, coal: 16 } },
  { dmg: 120, cost: { gold: 80, iron: 28, coal: 28 } },
];
const WALL_BALLISTA = [
  { count: 0 },
  { count: 1, cost: { gold: 35, timber: 60, iron: 15 } },
  { count: 2, cost: { gold: 60, timber: 90, iron: 30, coal: 8 } },
  { count: 3, cost: { gold: 90, timber: 120, iron: 45, coal: 16 } },
];
const BALLISTA = { name: 'Ballista', dmg: 90, interval: 3.4, range: 17, radius: 0.3, pierce: 12, bonus: { big: 1.6 } };
const OIL = { name: 'Kokende olje', dmg: 0, interval: 5, radius: 0.3 };
// Omformere i landsbyen: gjør tømmer og stein (som hoper seg opp) om til kull og jern. Hvert nivå én omgang til per runde.
const CONVERT = {
  kiln:    { name: 'Kullmile',   from: 'timber', to: 'coal', take: 6, give: 1, every: 15, levels: [
    { cost: { gold: 40, stone: 40 } }, { cost: { gold: 70, stone: 70, iron: 10 } }, { cost: { gold: 110, stone: 110, iron: 20 } }] },
  smelter: { name: 'Smelteovn',  from: 'stone',  to: 'iron', take: 5, give: 1, every: 15, levels: [
    { cost: { gold: 40, timber: 40 } }, { cost: { gold: 70, timber: 70, coal: 5 } }, { cost: { gold: 110, timber: 110, coal: 10 } }] },
};
Object.assign(Econ.prototype, {
  wallLv(k) { return (this.wallgear || {})[k] || 0; },
  wallNext(k) { const t = k === 'oil' ? WALL_OIL : WALL_BALLISTA; return t[this.wallLv(k) + 1] || null; },
  buyWallGear(k) { const n = this.wallNext(k); if (!n || !this.pay(n.cost)) return false; (this.wallgear = this.wallgear || {})[k] = this.wallLv(k) + 1; return true; },
  convLv(k) { return (this.conv || {})[k] || 0; },
  convNext(k) { return CONVERT[k].levels[this.convLv(k)] || null; },
  buyConv(k) { const n = this.convNext(k); if (!n || !this.pay(n.cost)) return false; (this.conv = this.conv || {})[k] = this.convLv(k) + 1; return true; },
  // Per minutt ved fullt lager: hvor mye den gjør om.
  convRate(k) { const c = CONVERT[k], l = this.convLv(k); return { from: c.take * l * 60 / c.every, to: c.give * l * 60 / c.every }; },
});
{
  const tick0 = Econ.prototype.tick;
  Econ.prototype.tick = function (dt) {
    tick0.call(this, dt);
    if (!this.conv) return;
    this.convT = this.convT || {};
    for (const k in CONVERT) {
      const l = this.convLv(k); if (!l) continue;
      const c = CONVERT[k];
      this.convT[k] = (this.convT[k] || 0) + dt;
      while (this.convT[k] >= c.every) {
        this.convT[k] -= c.every;
        const n = Math.min(l, Math.floor((this.res[c.from] || 0) / c.take));
        if (n > 0) { this.res[c.from] -= n * c.take; this.add({ [c.to]: n * c.give }); if (this.deliveries.length < 300) this.deliveries.push({ node: c.to, res: c.to, amount: n * c.give, conv: k }); }
      }
    }
  };
}
// Boten og rivalen: bygger omformere og murforsvar når de har mye til overs.
function extrasBot(ec, w) {
  for (let g = 0; g < 4; g++) {
    let did = false;
    if (w >= 7 && ec.res.timber >= 120 && ec.convNext('kiln') && ec.can(ec.convNext('kiln').cost) && ec.res.gold >= ec.convNext('kiln').cost.gold + 40) did = ec.buyConv('kiln');
    if (!did && w >= 6 && ec.res.stone >= 120 && ec.convNext('smelter') && ec.can(ec.convNext('smelter').cost) && ec.res.gold >= ec.convNext('smelter').cost.gold + 40) did = ec.buyConv('smelter');
    if (!did && w >= 10 && ec.wallNext('ballista') && ec.res.iron >= ec.wallNext('ballista').cost.iron + 25 && ec.res.gold >= ec.wallNext('ballista').cost.gold + 50 && ec.can(ec.wallNext('ballista').cost)) did = ec.buyWallGear('ballista');
    if (!did && w >= 12 && ec.wallNext('oil') && ec.res.coal >= ec.wallNext('oil').cost.coal + 20 && ec.res.gold >= ec.wallNext('oil').cost.gold + 50 && ec.can(ec.wallNext('oil').cost)) did = ec.buyWallGear('oil');
    if (!did) break;
  }
}
"""

SIM_INIT = """    // Forsvar på muren (versjon 28): ballistaer og kokende olje.
    const wg = cfg.wallgear || {};
    this.ballistae = [];
    for (let i = 0; i < (WALL_BALLISTA[wg.ballista || 0] || WALL_BALLISTA[0]).count; i++) {
      const side = i % 2 ? 1 : -1;
      this.ballistae.push({ x: side * (MAP.gateHalf + 1.2) + (i === 2 ? 0.01 : 0), z: MAP.gateZ + 0.6, cd: 1 + i, T: BALLISTA, type: 'archer', side: 'p' });
    }
    this.oil = (WALL_OIL[wg.oil || 0] || WALL_OIL[0]).dmg; this.oilCd = 3;
    this.units = []; let id = 0;"""

SIM_STEP = """    for (const a of this.ballistae || []) {
      a.cd -= dt;
      if (a.cd > 0) continue;
      let best = null, bs = -1;
      for (const e of enemies) { const d = Math.hypot(e.x - a.x, e.z - a.z); if (e.alive && d < a.T.range && e.maxHp > bs) { bs = e.maxHp; best = e; } }
      if (!best) continue;
      a.cd = a.T.interval;
      this._damage(a, best);
      this.events.push({ kind: 'shot', from: { x: a.x, z: a.z, y: 3.8 }, to: best, type: 'siegebreaker' });
    }
    if (this.oil) {
      this.oilCd -= dt;
      if (this.oilCd <= 0) {
        const hit = enemies.filter(e => e.alive && !e.T.flies && e.z > MAP.gateZ - 3.2 && Math.abs(e.x) < MAP.gateHalf + 1.5);
        if (hit.length) {
          this.oilCd = OIL.interval;
          const src = { T: Object.assign({}, OIL, { dmg: this.oil, pierce: 99 }), type: 'archer', side: 'p', x: 0, z: MAP.gateZ + 0.5 };
          hit.forEach(e => this._damage(src, e));
          this.events.push({ kind: 'oil', at: { x: 0, z: MAP.gateZ - 1.2 } });
        } else this.oilCd = 0.5;
      }
    }
    for (const u of this.units) { u.px = u.x; u.pz = u.z; }"""

UI = r"""
  // ---------- Versjon 28: murforsvar og omformere ----------
  Object.assign(UP_PIC, {
    oil: '<path d="M8 12 H32 L29 30 Q20 35 11 30 Z" fill="#3b3631" stroke="#1d1a17" stroke-width="1.4"/><path d="M12 12 Q20 6 28 12" fill="none" stroke="#5a5550" stroke-width="2"/><path d="M14 18 Q20 22 26 18" stroke="#ffb03a" stroke-width="2.4" fill="none"/><path d="M17 8 Q15 4 18 1 M23 8 Q25 4 22 1" stroke="#c9d3dd" stroke-width="1.2" fill="none" opacity=".7"/>',
    ballista: '<path d="M6 14 Q20 26 34 14" fill="none" stroke="#7a5230" stroke-width="3"/><path d="M6 14 L20 24 L34 14" fill="none" stroke="#d8d0c0" stroke-width="1"/><path d="M20 30 V6" stroke="#5a3d24" stroke-width="3"/><path d="M20 4 L17 9 H23 Z" fill="#c9d3dd"/><path d="M12 36 L20 28 L28 36" stroke="#5a3d24" stroke-width="2.4" fill="none"/>',
    kiln: '<path d="M8 34 Q8 14 20 8 Q32 14 32 34 Z" fill="#5a4636" stroke="#2a1f16" stroke-width="1.4"/><path d="M15 34 V26 Q20 21 25 26 V34 Z" fill="#ff8a2a"/><path d="M18 8 Q16 4 19 1" stroke="#9aa3ad" stroke-width="1.6" fill="none"/><circle cx="14" cy="18" r="1.5" fill="#1b1b1b"/><circle cx="26" cy="20" r="1.5" fill="#1b1b1b"/>',
    smelter: '<rect x="10" y="12" width="20" height="22" fill="#6b6f78" stroke="#2f3238" stroke-width="1.4"/><rect x="15" y="4" width="10" height="9" fill="#54585f" stroke="#2f3238"/><path d="M14 30 H26 V24 Q20 20 14 24 Z" fill="#ff6a1a"/><path d="M30 28 H36 L34 33 H30" fill="#c9d3dd" stroke="#2f3238"/>',
  });
  function convHtml() {
    const ec = state.econ;
    const tile = k => { const c = CONVERT[k], l = ec.convLv(k), n = ec.convNext(k), r = ec.convRate(k);
      return upTile({ pic: k, name: c.name, lv: l, max: c.levels.length,
        tip: `Gjør ${c.take} ${RES[c.from].name.toLowerCase()} om til ${c.give} ${RES[c.to].name.toLowerCase()} hvert ${c.every}. sekund per nivå, så lenge du har ${RES[c.from].name.toLowerCase()} på lager. Bruker det som hoper seg opp på det som er knapt.`,
        now: l ? `${icon(c.to, 12)}+${r.to}/min` : 'Ikke bygget',
        buy: n && buyBtn(l ? `Nivå ${l + 1}` : 'Bygg', n.cost, 'conv', `data-k="${k}"`) }); };
    return `<div class="card"><h3>Kullmile og smelteovn ${tipIcon('Tømmer og stein hoper seg opp, jern og kull er knappe. Kullmila brenner tømmer til kull, smelteovnen smelter jern ut av stein.')}</h3>${tiles([tile('kiln'), tile('smelter')])}</div>`;
  }
  function wallGearTiles() {
    const ec = state.econ, no = ec.wallNext('oil'), nb = ec.wallNext('ballista'), lo = ec.wallLv('oil'), lb = ec.wallLv('ballista');
    return [
      upTile({ pic: 'ballista', name: 'Ballista', lv: lb, max: WALL_BALLISTA.length - 1,
        tip: `Tunge bolter fra muren mot den største fienden innen ${BALLISTA.range} m: ${BALLISTA.dmg} skade, går gjennom ${BALLISTA.pierce} rustning, 60 % mer mot kjemper.`,
        now: `${WALL_BALLISTA[lb].count} stk`, buy: nb && buyBtn(`${nb.count} stk`, nb.cost, 'wallgear', 'data-k="ballista"') }),
      upTile({ pic: 'oil', name: 'Kokende olje', lv: lo, max: WALL_OIL.length - 1,
        tip: `Hvert ${OIL.interval}. sekund heller muren kokende olje over alle fiender ved porten. Går gjennom all rustning. Fyres med kull.`,
        now: lo ? `${WALL_OIL[lo].dmg} skade` : 'Ingen', buy: no && buyBtn(`${no.dmg} skade`, no.cost, 'wallgear', 'data-k="oil"') }),
    ];
  }
"""


def apply(s):
    # Mindre gull per wave (Rune: alt var oppgradert for tidlig).
    s = sub(s, "const waveBonus = w => 6 + 2 * Math.min(w, 10) + Math.max(0, w - 10);   // vokser saktere i World 2",
               "const waveBonus = w => 4 + Math.round(1.5 * Math.min(w, 10) + 0.5 * Math.max(0, w - 10));   // versjon 28: mindre enn før")
    # Portfeilen: kjempene stoppet før porten fordi de er store. Nå teller kroppen, ikke midtpunktet.
    s = sub(s, "      if (u.z >= MAP.gateZ - 0.9 && (!u.T.flies || Math.abs(u.x) <= MAP.gateHalf)) {",
               "      if (u.z >= MAP.gateZ - 0.9 - Math.max(0, (u.T.radius || 0.4) - 0.4) * 2.2 && (!u.T.flies || Math.abs(u.x) <= MAP.gateHalf)) {")
    s = sub(s, "\nif (typeof module !== 'undefined') module.exports = { supplyOf, WARDEN_GEAR,", LOGIC + "\nif (typeof module !== 'undefined') module.exports = { supplyOf, WARDEN_GEAR,")
    s = sub(s, "    this.units = []; let id = 0;\n    for (const a of army) {", SIM_INIT + "\n    for (const a of army) {")
    s = sub(s, "      this.events.push({ kind: 'shot', from: { x: a.x, z: a.z, y: 3.8 }, to: best, type: 'archer' });\n    }\n    for (const u of this.units) { u.px = u.x; u.pz = u.z; }",
               "      this.events.push({ kind: 'shot', from: { x: a.x, z: a.z, y: 3.8 }, to: best, type: 'archer' });\n    }\n" + SIM_STEP)
    # Alle steder som lager en kamp med porten tar med murforsvaret.
    n = s.count("archers: ARCHERS[ec.archers].count")
    assert n >= 3, n
    s = s.replace("archers: ARCHERS[ec.archers].count", "archers: ARCHERS[ec.archers].count, wallgear: ec.wallgear")
    # Boten og rivalen bruker det nye (heroBot kalles av begge).
    s = sub(s, "function heroBot(ec, w) {\n", "function heroBot(ec, w) {\n  extrasBot(ec, w);\n")
    # Grensesnitt.
    s = sub(s, "  function renderBuildings() {", UI + "  function renderBuildings() {")
    s = sub(s, "          upTile({ pic: 'archers', name: 'Bueskyttere på muren', lv: ec.archers, max: ARCHERS.length - 1,",
               "          ...wallGearTiles(),\n          upTile({ pic: 'archers', name: 'Bueskyttere på muren', lv: ec.archers, max: ARCHERS.length - 1,")
    s = sub(s, "    $('#nodes').innerHTML = Object.keys(NODES).map(nodeHtml).join('');",
               "    $('#nodes').innerHTML = Object.keys(NODES).map(nodeHtml).join('') + convHtml();")
    s = sub(s, "barracks: () => ec.buyBarracks(), wall: () => ec.buyWall(),",
               "wallgear: () => ec.buyWallGear(k), conv: () => ec.buyConv(k),\n      barracks: () => ec.buyBarracks(), wall: () => ec.buyWall(),")
    s = sub(s, "      else if (['wall', 'repair', 'archers', 'track', 'wgear', 'wtrain'].includes(b.dataset.act)) toast('Gjelder fra neste wave.');",
               "      else if (['wall', 'repair', 'archers', 'track', 'wgear', 'wtrain', 'wallgear'].includes(b.dataset.act)) toast('Gjelder fra neste wave.');")
    return s
