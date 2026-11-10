"""The test players use the whole game (version 33, 11 Oct 2026, Rune: «how do we know the bots upgrade the forge, the warden etc.?»).
Before this, the bots (balance bot and the 1v1 rival) never bought Warden gear or abilities, Workshop tech or worker tools,
their Warden never earned experience, and he started every wave at full health for free.
- wardenBot (called from extrasBot): worker tools, Workshop tech, Warden gear (cheapest slot first), Warden abilities, Warden healing.
- A Sim made with cfg.bot = the bot's Econ casts the Warden's abilities by itself when enough enemies are close,
  starts the Warden at the health he ended the last wave with, and gives him experience for his kills (as the game does).
- botSpend: optional spending log per category (tools/spend.js reads it) so we can see where the bots' gold, iron and coal go.
Applied by build_v2.py last in the chain."""
from patch import sub

LOGIC = r"""
// ===== Versjon 33: testspillerne bruker hele spillet (Warden, Workshop, verktøy) =====
function wardenBot(ec, w) {
  const spare = (c, g, i) => c && ec.can(c) && ec.res.gold >= (c.gold || 0) + g && (ec.res.iron || 0) >= (c.iron || 0) + i;
  if (ec.wardenHp != null && ec.wardenHp < 0.6) { const c = ec.wardenHealCost(); if (c && ec.res.gold >= c.gold + 20) ec.healWarden(); }
  // Hvor mye som er lurt å ha kjøpt etter hvert: litt Warden og Workshop hver tredje wave, så hæren ikke sulter.
  const gearN = ec.warden.sword + ec.warden.shield + ec.warden.armor, abilN = ec.warden.abil.stun + ec.warden.abil.spin + ec.warden.abil.freeze;
  for (let g = 0; g < 4; g++) {
    let did = false;
    // Verktøy til arbeiderne: alle leveranser blir større, betaler seg fort.
    // Ett nivå per Barracks-nivå, og bare med tømmer til overs (ellers kommer Barracks for sent).
    const tl = TOOLS[ec.tools]; if (tl && ec.barracks > ec.tools && (ec.res.timber || 0) >= tl.cost.timber + 40 && spare(tl.cost, 15, 5)) did = ec.buyTools();
    // Forge: gjelder alle units av typen, så det er mer verdt enn å oppgradere én soldat.
    if (!did && w >= 4) for (const k of ['melee', 'ranged', 'armor']) { const lv = TRACKS[k].levels[ec.up[k]]; if (lv && !ec.trackLocked(k) && spare(lv.cost, 20, 5) && ec.buyTrack(k)) { did = true; break; } }
    // Warden-utstyr: billigste del først, omtrent én del per tredje wave.
    if (!did && w >= 4 && gearN < Math.floor(w / 3)) { const k = Object.keys(WARDEN_GEAR).sort((a, b) => ec.warden[a] - ec.warden[b])[0], lv = WARDEN_GEAR[k].levels[ec.warden[k]];
      if (lv && spare(lv.cost, 50, 25)) did = ec.buyWardenGear(k); }
    // Warden-evner: lammelse først, så virvelvind, så frost, omtrent én per fjerde wave.
    if (!did && abilN < Math.floor((w - 2) / 4)) for (const [k, from] of [['stun', 6], ['spin', 9], ['freeze', 13]]) {
      if (did || w < from) continue; const lv = WARDEN_ABIL[k].levels[ec.warden.abil[k]];
      if (lv && spare(lv.cost, 50, 25)) did = ec.buyWardenAbility(k);
    }
    // Workshop: teknologi for skytterne når det er kull til overs.
    if (!did && w >= 8 && ec.up.tech < Math.floor(w / 8)) { const lv = TRACKS.tech.levels[ec.up.tech]; if (lv && (ec.res.coal || 0) >= (lv.cost.coal || 0) + 15 && spare(lv.cost, 30, 15)) did = ec.buyTrack('tech'); }
    if (!did) break;
  }
}
{ const _x = extrasBot; extrasBot = function (ec, w) { _x(ec, w); wardenBot(ec, w); }; }
// Når neste Barracks er på tur, holdes tømmer, stein, jern og kull til den igjen før helt, utstyr og ekstra bygg får noe
// (før kjøpte boten kullmile, ballista og Warden-skjold for tømmeret og steinen, og fikk Barracks II altfor sent).
{ const _h = heroBot; heroBot = function (ec, w) {
  const due = (w >= 5 && ec.barracks === 0) || (w >= 9 && ec.barracks === 1) || (w >= 16 && ec.barracks === 2);
  const r = due && BARRACKS[ec.barracks + 1] && BARRACKS[ec.barracks + 1].cost, held = {};
  if (r) for (const k in r) if (k !== 'gold') { held[k] = Math.min(ec.res[k] || 0, r[k]); ec.res[k] -= held[k]; }
  try { return _h(ec, w); } finally { for (const k in held) ec.res[k] += held[k]; }
}; }
// Kamper for testspillerne (cfg.bot = Econ): Warden bruker evnene selv, har helsen fra forrige wave og får erfaring av drap.
{
  const step0 = Sim.prototype.step;
  Sim.prototype.step = function (dt) {
    const ec = this.cfg && this.cfg.bot;
    if (!ec) return step0.call(this, dt);
    const w = this.warden;
    if (!this._botInit) {
      this._botInit = true; this._abReady = {}; this._evI = 0;
      if (w && ec.wardenHp != null && ec.wardenHp < 1) w.hp = Math.max(1, Math.round(w.maxHp * ec.wardenHp));
    }
    if (w && w.alive && this.t > 1) for (const k of ['freeze', 'stun', 'spin']) {
      const lv = ec.warden.abil[k]; if (!lv || (this._abReady[k] || 0) > this.t || this.t < (this._abLook || 0)) continue;
      const r = k === 'freeze' ? 8 + 2 * lv : k === 'stun' ? 5 + lv : 3;
      const near = this.units.filter(e => e.alive && e.side === 'e' && dist(e, w) < r).length;
      if (near >= (k === 'freeze' ? 6 : 4) && this.wardenAbility(k, lv) >= 0) this._abReady[k] = this.t + ABIL_CD[k][lv - 1];
    }
    // Et menneske ser ikke alt på en gang: boten ser etter en sjanse til evnene hvert andre sekund.
    if (this.t >= (this._abLook || 0)) this._abLook = this.t + 2;
    step0.call(this, dt);
    if (this.events.length < this._evI) this._evI = 0;
    for (; this._evI < this.events.length; this._evI++) { const e = this.events[this._evI]; if (e.kind === 'death' && e.unit.side === 'e' && e.by === 'warden') ec.addWardenXp(WARDEN_KILL_XP[e.unit.type] || 1); }
    if (this.result && this.warden) { const v = this.warden; ec.wardenHp = Math.min(1, (v.alive ? Math.max(0, v.hp) / v.maxHp : 0.25) + (v.alive ? 0.1 : 0)); }
  };
}
"""

# Spending log: only active when botSpend.on is set (tools/spend.js). Each Econ purchase method tags its payment.
SPEND = r"""
const botSpend = { on: false, tot: {}, cat: null };
{
  const pay0 = Econ.prototype.pay;
  Econ.prototype.pay = function (cost) {
    const ok = pay0.call(this, cost);
    if (ok && botSpend.on && cost) { let c = botSpend.cat; if (!c) { const st = new Error().stack || ''; c = /at upgrade /.test(st) ? 'unitUpgrade' : /at buy /.test(st) ? 'unit' : 'other'; }
      const b = botSpend.tot[c] || (botSpend.tot[c] = {}); for (const r in cost) b[r] = (b[r] || 0) + cost[r]; }
    return ok;
  };
  const CAT = { addWorker: 'workers', unlockNode: 'mines', expandNode: 'mines', deepen: 'mines', buyTools: 'tools', buyBarracks: 'barracks', buyWall: 'wall', buyArchers: 'wall',
    repair: 'repair', buyWallGear: 'wallgear', buyConv: 'converters', buyWardenGear: 'warden', buyWardenAbility: 'warden', healWarden: 'warden', trainWarden: 'warden',
    recruitHero: 'hero', heroRevive: 'hero', buyHeroGear: 'hero' };
  for (const m in CAT) { const f = Econ.prototype[m]; if (!f) continue;
    Econ.prototype[m] = function (...a) { const prev = botSpend.cat; botSpend.cat = m === 'buyTrack' ? null : CAT[m]; try { return f.apply(this, a); } finally { botSpend.cat = prev; } }; }
  const bt = Econ.prototype.buyTrack;
  Econ.prototype.buyTrack = function (k) { const prev = botSpend.cat; botSpend.cat = k === 'tech' ? 'workshop' : 'forge'; try { return bt.call(this, k); } finally { botSpend.cat = prev; } };
}
"""


def apply(s):
    s = sub(s, "if (typeof module !== 'undefined') module.exports = { supplyOf, WARDEN_GEAR,", LOGIC + SPEND + "\nif (typeof module !== 'undefined') module.exports = { supplyOf, WARDEN_GEAR,")
    # Rivalen i 1v1 er også en testspiller: Warden bruker evner selv og bærer helsen videre.
    s = sub(s, "this.sim = new Sim(withHero(this.army, ec), { types: ec.types(TYPES, versusScale(W)),", "this.sim = new Sim(withHero(this.army, ec), { bot: ec, types: ec.types(TYPES, versusScale(W)),")
    return s
