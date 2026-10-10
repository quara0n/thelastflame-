"""Version 24 (10 Oct 2026): the hero, Barracks doctrines and worker finds. Applied last by build_v2.py.

- Hero: your own champion at your gate (the Warden stays the team's king). Recruited in Heltehallen for 40 gold, three
  classes, takes no army space, can't be sold. XP from his kills (bounty) and +2 per wave survived. Each level: +6 % HP
  and damage and a draft of 3 random talents (pick 1, reroll for gold). Level 5: pick one of two paths per class.
- Doctrines: each new Barracks level draws 3 of 9 doctrines; you pick 1 for the rest of the game.
- Worker finds: each delivery has a small chance of a find (gold vein, old weapon = hero XP, iron lump, ember = Warden XP).
The bots (game_sim, the 1v1 rival) recruit a random hero at wave 2 and pick talents and doctrines at random.
Design notes: docs/helt-barracks-arbeidere.md."""
from patch import sub

LOGIC = r"""
// ===== Helt, Barracks-doktriner og arbeiderfunn (versjon 24, 10. okt 2026) =====
// Helten er din egen kriger ved porten (Warden er lagets konge ved flammen). Han tar ingen plass i hæren.
const HERO_COST = { gold: 40 };
const HERO_XP = [12, 35, 70, 150, 225, 290, 370, 500, 680];   // total erfaring for nivå 2, 3, 4 … 10
const HERO_GROWTH = 0.08;                                    // +8 % helse og skade per nivå (var 6 %; Rune: helten falt av for fort)
const HERO_PATH_LEVEL = 5;
const HERO_REVIVE = { base: 5, perLevel: 2 };   // nivå 1: 7 gull, nivå 10: 25 gull (å rekruttere koster 40)
const HERO_FALL_LOSS = 0.25;                      // andel av fremgangen mot neste nivå som går tapt
// Heltens utstyr (versjon 27): tre spor à tre nivåer, kjøpes i Heltehallen for gull og jern. Gjør helten sterkere uavhengig av erfaring.
const HERO_GEAR = {
  vapen:    { name: 'Våpen', desc: '+15 % skade per nivå.', lv: [{ dmgMul: 1.15 }, { dmgMul: 1.15 }, { dmgMul: 1.15 }] },
  rustning: { name: 'Rustning', desc: '+15 % helse og +1 rustning per nivå.', lv: [{ hpMul: 1.15, armor: 1 }, { hpMul: 1.15, armor: 1 }, { hpMul: 1.15, armor: 1 }] },
  amulett:  { name: 'Flammeamulett', desc: 'Nivå 1 og 2: gror 0,4 % helse per sekund. Nivå 3, «Siste glød»: reiser seg én gang per wave med 40 % helse.', lv: [{ regenPct: 0.004 }, { regenPct: 0.004 }, { revive: 0.4 }] },
};
const HERO_GEAR_COST = [{ gold: 25, iron: 3 }, { gold: 50, iron: 8 }, { gold: 90, iron: 15 }];
const HERO_CLASSES = {
  heroKnight: { name: 'Flammeridder', short: 'Nærkamp. Står foran og tåler mye.', paths: ['paladin', 'berserker'] },
  heroHunter: { name: 'Askejeger', short: 'Skytter med lang rekkevidde, god mot flyvere.', paths: ['falkoye', 'stormskytter'] },
  heroPriest: { name: 'Glødeprest', short: 'Leger og gjør hæren rundt seg sterkere.', paths: ['lysbringer', 'askeorakel'] },
};
Object.assign(TYPES, {
  heroKnight: { name: 'Flammeridder', side: 'p', hero: true, role: 'Din helt. Nærkamp, står foran og tåler mye', cost: 40, hp: 420, armor: 4, dmg: 26, interval: 0.9, range: 0.5, speed: 2.6, radius: 0.55, aggro: 8 },
  heroHunter: { name: 'Askejeger', side: 'p', hero: true, role: 'Din helt. Skytter med lang rekkevidde, god mot flyvere', cost: 40, hp: 190, armor: 1, dmg: 30, interval: 1.2, range: 11, speed: 2.6, radius: 0.45, aggro: 13, ranged: true, pierce: 3, bonus: { flies: 1.5 } },
  heroPriest: { name: 'Glødeprest', side: 'p', hero: true, role: 'Din helt. Leger, og allierte rundt ham slår 20 % hardere', cost: 40, hp: 260, armor: 2, dmg: 14, interval: 1.0, range: 6, speed: 2.4, radius: 0.45, aggro: 7, ranged: true, heal: 30, healEvery: 1.3, healRange: 8, aura: 4 },
});
// Talenter: hvert nivå trekkes 3 tilfeldige (felles + klassens egne), og du velger 1. Felles talenter kan tas flere ganger.
const HERO_TALENTS = {
  seig:       { name: 'Seig', desc: '+20 % helse.', mod: { hpMul: 1.2 }, stack: true },
  skarp:      { name: 'Skarp', desc: '+18 % skade.', mod: { dmgMul: 1.18 }, stack: true },
  rask:       { name: 'Rask hånd', desc: 'Slår og skyter 12 % raskere.', mod: { intervalMul: 0.88 }, stack: true },
  hud:        { name: 'Hard hud', desc: '+2 rustning.', mod: { armor: 2 }, stack: true },
  gjenvekst:  { name: 'Gjenvekst', desc: 'Gror 0,6 % helse per sekund i kamp.', mod: { regenPct: 0.006 } },
  flammeblod: { name: 'Flammeblod', desc: '+8 % helse og skade.', mod: { hpMul: 1.08, dmgMul: 1.08 }, stack: true },
  torn:       { cls: 'heroKnight', name: 'Tornrustning', desc: 'Fiender som slår ham, tar 30 % av skaden selv.', mod: { thorns: 0.3 } },
  skjoldslag: { cls: 'heroKnight', name: 'Skjoldslag', desc: 'Hvert 6. sekund slår han fienden bakover og lammer den.', mod: { bash: 6 } },
  storm:      { cls: 'heroKnight', name: 'Står i stormen', desc: 'Under halv helse tar han halv skade i 5 sekunder.', mod: { brace: 5 } },
  utfordring: { cls: 'heroKnight', name: 'Utfordring', desc: 'Fiender rundt ham går etter ham.', mod: { taunt: 3 } },
  virvel:     { cls: 'heroKnight', name: 'Virvel', desc: 'Hvert 3. slag treffer alle rundt ham.', mod: { spin: 3 } },
  frostegg:   { cls: 'heroKnight', name: 'Frostegg', desc: 'Treffene bremser fienden.', mod: { slows: 1.2 } },
  kull:       { cls: 'heroHunter', name: 'Kull-ladning', desc: 'Hvert 4. skudd sprekker og treffer fiender rundt målet.', mod: { burst: 4 } },
  langtlop:   { cls: 'heroHunter', name: 'Langt løp', desc: '+2 m rekkevidde.', mod: { range: 2 } },
  panser:     { cls: 'heroHunter', name: 'Panserbryter', desc: 'Går gjennom 5 mer rustning.', mod: { pierce: 5 } },
  falkesyn:   { cls: 'heroHunter', name: 'Falkesyn', desc: 'Dobbel skade mot flyvere.', mod: { bonusFlies: 2 } },
  spidd:      { cls: 'heroHunter', name: 'Spidd', desc: 'Skuddet går gjennom og treffer én til bak målet.', mod: { skewer: 1 } },
  merket:     { cls: 'heroHunter', name: 'Merket skudd', desc: 'Velger den sterkeste fienden; første skudd mot et nytt mål gjør dobbel skade.', mod: { marks: true } },
  klar:       { cls: 'heroPriest', name: 'Klarere glød', desc: 'Leger 30 % mer.', mod: { healMul: 1.3 } },
  bonn:       { cls: 'heroPriest', name: 'Raskere bønn', desc: 'Leger oftere.', mod: { healEveryMul: 0.8 } },
  sirkel:     { cls: 'heroPriest', name: 'Vid sirkel', desc: 'Leger 2 m lenger unna.', mod: { healRange: 2 } },
  banner:     { cls: 'heroPriest', name: 'Banner av glør', desc: 'Auraen når 1,5 m lenger.', mod: { aura: 1.5 } },
  samling:    { cls: 'heroPriest', name: 'Samling', desc: 'Allierte i auraen slår 30 % hardere og gror sakte.', mod: { rally: 3 } },
  stav:       { cls: 'heroPriest', name: 'Glødende stav', desc: 'Det han treffer, brenner en stund.', mod: { burn: 8 } },
};
// Nivå 5: veivalg. To retninger per klasse, valget gjelder resten av spillet.
const HERO_PATHS = {
  paladin:      { name: 'Paladin', desc: 'Mye mer helse, roper fiender til seg, og allierte rundt ham slår hardere og gror tilbake.', mod: { hpMul: 1.5, taunt: 3.5, aura: 4, rally: 3 } },
  berserker:    { name: 'Berserker', desc: 'Treffer to om gangen, slår mye hardere og raskere.', mod: { cleave: true, dmgMul: 1.35, intervalMul: 0.85 } },
  falkoye:      { name: 'Falkøye', desc: '+3 m rekkevidde, går gjennom all rustning, og første skudd mot et nytt mål gjør dobbel skade.', mod: { range: 3, pierce: 12, marks: true } },
  stormskytter: { name: 'Stormskytter', desc: 'Skyter mye raskere, og hvert 3. skudd sprekker i et område.', mod: { intervalMul: 0.7, burst: 3 } },
  lysbringer:   { name: 'Lysbringer', desc: 'Leger to om gangen, 50 % mer og 2 m lenger unna.', mod: { twinHeal: true, healMul: 1.5, healRange: 2 } },
  askeorakel:   { name: 'Askeorakel', desc: 'Kampprest: flammen brenner, treffer flere og slår mye hardere.', mod: { burn: 12, splash: 1.5, dmgMul: 1.8 } },
};
// Barracks-doktriner: hvert nytt Barracks-nivå trekker 3 av disse, og du velger 1 for resten av spillet.
const DOCTRINES = {
  skjoldvegg:   { name: 'Skjoldvegg', desc: 'Nærkamp-units får 15 % mer helse.' },
  skarpskytter: { name: 'Skarpskytterskolen', desc: 'Skyttere får +1 m rekkevidde og 8 % mer skade.' },
  rekruttering: { name: 'Rekrutteringsleir', desc: 'Tier 1- og Tier 2-units koster 25 % mindre gull.' },
  veteraner:    { name: 'Veteraner', desc: 'Units på nivå 3 får 12 % mer helse og skade.' },
  folkeoppbud:  { name: 'Folkeoppbud', desc: '+8 plass i hæren.' },
  akademi:      { name: 'Krigsakademiet', desc: 'Helten får 50 % mer erfaring. Warden får 10 % mer helse og skade.' },
  maskin:       { name: 'Maskinverkstedet', desc: 'Tier 3- og Tier 4-units koster 30 % mindre jern og kull.' },
  garde:        { name: 'Flammens garde', desc: 'Alle units får +1 rustning.' },
  kirurg:       { name: 'Feltkirurger', desc: 'Alle units gror 0,5 % helse per sekund i kamp.' },
};
const FIND_CHANCE = 0.005;   // per leveranse; ca. ett funn per wave med en full landsby
const shuffled = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
const anyOf = a => a[Math.floor(Math.random() * a.length)];
function heroMod(out, m) {
  for (const k in m) {
    const v = m[k];
    if (k === 'hpMul') out.hp = Math.round(out.hp * v);
    else if (k === 'dmgMul') out.dmg = Math.round(out.dmg * v);
    else if (k === 'intervalMul') out.interval = +(out.interval * v).toFixed(3);
    else if (k === 'healMul') out.heal = Math.round((out.heal || 0) * v);
    else if (k === 'healEveryMul') out.healEvery = +(out.healEvery * v).toFixed(3);
    else if (k === 'regenPct') out.regenPct = (out.regenPct || 0) + v;
    else if (k === 'bonusFlies') out.bonus = Object.assign({}, out.bonus, { flies: v });
    else if (k === 'range') { out.range = +(out.range + v).toFixed(2); out.aggro = +(out.aggro + v).toFixed(2); }
    else if (['armor', 'splash', 'pierce', 'taunt', 'aura', 'healRange', 'rally', 'burn'].includes(k)) out[k] = +((out[k] || 0) + v).toFixed(2);
    else out[k] = v;
  }
}
// Heltens tall: grunnklassen (med Forge-bonus), nivået, talentene og retningen.
function heroStats(T, h, lv) {
  const out = Object.assign({}, T);
  if (T.bonus) out.bonus = Object.assign({}, T.bonus);
  const g = 1 + HERO_GROWTH * (lv - 1);
  out.hp = Math.round(out.hp * g); out.dmg = Math.round(out.dmg * g);
  for (const k in HERO_GEAR) for (let i = 0; i < ((h.gear || {})[k] || 0); i++) heroMod(out, HERO_GEAR[k].lv[i]);
  for (const id of h.talents) heroMod(out, HERO_TALENTS[id].mod);
  if (h.path) heroMod(out, HERO_PATHS[h.path].mod);
  if (out.regenPct) out.regen = (out.regen || 0) + out.hp * out.regenPct;
  out.heroLevel = lv;
  return out;
}
Object.assign(Econ.prototype, {
  has(d) { return !!(this.docs && this.docs.includes(d)); },
  pickDoctrine(d) { if (!this.docOffer || !this.docOffer.includes(d)) return false; (this.docs = this.docs || []).push(d); this.docOffer = null; return true; },
  heroLevel() { if (!this.hero) return 0; let l = 1; for (const t of HERO_XP) if (this.hero.xp >= t) l++; return l; },
  heroNext() { return this.hero ? HERO_XP[this.heroLevel() - 1] || null : null; },
  heroPending() { return this.hero ? this.heroLevel() - 1 - this.hero.picks : 0; },
  recruitHero(type) {
    if (this.hero || !HERO_CLASSES[type] || !this.pay(HERO_COST)) return false;
    this.hero = { type, xp: 0, talents: [], path: null, picks: 0, offer: null, kind: null, rerolls: 0 };
    return true;
  },
  heroGain(n) {
    const h = this.hero; if (!h || n <= 0) return 0;
    const a = this.heroLevel(); h.xp += n;
    const up = this.heroLevel() - a;
    if (!h.offer) this.heroDraw();
    return up;
  },
  heroDraw() {
    const h = this.hero; h.offer = null; h.kind = null;
    if (this.heroPending() <= 0) return;
    if (h.picks + 2 === HERO_PATH_LEVEL) { h.offer = HERO_CLASSES[h.type].paths.slice(); h.kind = 'path'; return; }
    const pool = Object.keys(HERO_TALENTS).filter(id => { const t = HERO_TALENTS[id]; return (!t.cls || t.cls === h.type) && (t.stack || !h.talents.includes(id)); });
    h.offer = shuffled(pool).slice(0, 3); h.kind = 'talent';
  },
  heroPick(id) {
    const h = this.hero; if (!h || !h.offer || !h.offer.includes(id)) return false;
    if (h.kind === 'path') h.path = id; else h.talents.push(id);
    h.picks++; h.rerolls = 0; this.heroDraw();
    return true;
  },
  // Helten kan falle (Rune 10. okt): han mister halve fremgangen mot neste nivå (aldri et nivå eller talenter),
  // og må gjenopplives for gull før han kan kjempe igjen. Det koster mindre enn å rekruttere ham.
  heroReviveCost() { return { gold: HERO_REVIVE.base + HERO_REVIVE.perLevel * this.heroLevel() }; },
  heroFall() {
    const h = this.hero; if (!h || h.fallen) return 0;
    const lv = this.heroLevel(), floor = HERO_XP[lv - 2] || 0, next = HERO_XP[lv - 1];
    const lost = next ? Math.floor((h.xp - floor) * HERO_FALL_LOSS) : 0;
    h.xp -= lost; h.fallen = true;
    return lost;
  },
  heroGearLevel(k) { return this.hero && this.hero.gear ? this.hero.gear[k] || 0 : 0; },
  heroGearCost(k) { return HERO_GEAR_COST[this.heroGearLevel(k)] || null; },
  buyHeroGear(k) { const c = HERO_GEAR[k] && this.heroGearCost(k); if (!this.hero || !c || !this.pay(c)) return false; (this.hero.gear = this.hero.gear || {})[k] = this.heroGearLevel(k) + 1; return true; },
  heroRevive() { const h = this.hero; if (!h || !h.fallen || !this.pay(this.heroReviveCost())) return false; h.fallen = false; return true; },
  heroRerollCost() { return { gold: 10 * ((this.hero && this.hero.rerolls || 0) + 1) }; },
  heroReroll() { const h = this.hero; if (!h || h.kind !== 'talent' || !this.pay(this.heroRerollCost())) return false; h.rerolls++; this.heroDraw(); return true; },
  // Arbeiderfunn: en liten sjanse per leveranse.
  _find(k) {
    if (Math.random() >= FIND_CHANCE) return;
    const r = Math.random(), where = NODES[k].name.toLowerCase();
    let f;
    if (r < 0.08) { f = { kind: 'glo', text: `Glo av den første flammen i ${where}: +1 kull, og Warden får 5 erfaring`, bag: { coal: 1 } }; this.addWardenXp(5); }
    else if (r < 0.3 && this.barracks >= 1) { const n = 3 + Math.floor(Math.random() * 4); f = { kind: 'iron', text: `Jernklump i ${where}: +${n} jern`, bag: { iron: n } }; }
    else if (r < 0.5 && this.hero) { this.heroGain(4); f = { kind: 'weapon', text: `Gammelt våpen i ${where}: helten får 4 erfaring` }; }
    else if (r < 0.5) f = { kind: 'weapon', text: `Gammelt våpen i ${where}, solgt for 8 gull`, bag: { gold: 8 } };
    else { const n = 6 + Math.floor(Math.random() * 9); f = { kind: 'gold', text: `Gullåre i ${where}: +${n} gull`, bag: { gold: n } }; }
    if (f.bag) this.add(f.bag);
    f.node = k; (this.finds = this.finds || []).push(f); if (this.finds.length > 20) this.finds.shift();
  },
});
{
  const _types = Econ.prototype.types, _price = Econ.prototype.unitPrice, _cap = Econ.prototype.supplyCap, _barracks = Econ.prototype.buyBarracks;
  Econ.prototype.types = function (baseTypes, enemyScale) {
    const out = _types.call(this, baseTypes, enemyScale), d = this.docs || [];
    for (const k in out) {
      if (!baseTypes[k] || baseTypes[k].side !== 'p') continue;
      let T = out[k];
      if (k === 'warden') {
        if (d.includes('akademi')) { T.hp = Math.round(T.hp * 1.1); T.dmg = Math.round(T.dmg * 1.1); }
        if (d.includes('garde')) T.armor += 1;
        continue;
      }
      if (T.hero && this.hero && this.hero.type === k) out[k] = T = heroStats(T, this.hero, this.heroLevel());
      if (d.includes('skjoldvegg') && !T.ranged) T.hp = Math.round(T.hp * 1.15);
      if (d.includes('skarpskytter') && T.ranged) { T.range += 1; T.aggro += 1; T.dmg = Math.round(T.dmg * 1.08); }
      if (d.includes('garde')) T.armor += 1;
      if (d.includes('veteraner')) T.vet = 0.12;
      if (d.includes('kirurg')) T.regen = (T.regen || 0) + T.hp * 0.005;
    }
    return out;
  };
  Econ.prototype.unitPrice = function (T) {
    const p = _price.call(this, T), tier = (T && T.tier) || 1;
    if (this.has('rekruttering') && tier <= 2) p.gold = Math.round(p.gold * 0.75);
    if (this.has('maskin') && tier >= 3) { if (p.iron) p.iron = Math.round(p.iron * 0.7); if (p.coal) p.coal = Math.round(p.coal * 0.7); }
    return p;
  };
  Econ.prototype.supplyCap = function () { return _cap.call(this) + (this.has('folkeoppbud') ? 8 : 0); };
  // Nytt Barracks-nivå: 3 tilfeldige doktriner du ikke har. Et valg som står åpent, tas automatisk først.
  Econ.prototype.buyBarracks = function () {
    const old = this.docOffer;
    if (!_barracks.call(this)) return false;
    if (old) this.pickDoctrine(old[0]);
    this.docOffer = shuffled(Object.keys(DOCTRINES).filter(d => !this.has(d))).slice(0, 3);
    return true;
  };
}
// Etter en wave: erfaring for drapene hans og +2 hvis han står. auto = boten velger talent og doktrine selv.
function heroAfterWave(ec, sim, auto) {
  let res = null;
  const hu = ec.hero && !ec.hero.fallen && sim && sim.units.find(u => u.side === 'p' && u.T.hero);
  if (hu) {
    let xp = Math.round((sim.heroXp || 0) + (hu.alive ? 2 : 0));
    if (ec.has('akademi')) xp = Math.round(xp * 1.5);
    res = { xp, up: ec.heroGain(xp), alive: hu.alive };
    if (!hu.alive) res.lost = ec.heroFall();
  }
  if (auto) heroAuto(ec);
  return res;
}
function heroAuto(ec) {
  if (ec.docOffer) ec.pickDoctrine(anyOf(ec.docOffer));
  for (let g = 0; g < 20 && ec.hero && ec.hero.offer; g++) ec.heroPick(anyOf(ec.hero.offer));
}
// Boter: helten står i hæren uten å være i army-lista (så den aldri selges eller oppgraderes som en vanlig unit).
function withHero(army, ec) {
  const h = ec && ec.hero;
  if (!h || h.fallen || army.some(a => a.type === h.type)) return army;
  const r = TYPES[h.type].ranged;
  return army.concat([{ type: h.type, col: 7.5, row: r ? 3.5 : 1.5, order: r ? 'follow' : 'advance' }]);
}
function heroBot(ec, w) {
  if (!ec.hero && w >= 2 && ec.res.gold >= HERO_COST.gold + 12) ec.recruitHero(anyOf(Object.keys(HERO_CLASSES)));
  if (ec.hero && ec.hero.fallen && ec.res.gold >= ec.heroReviveCost().gold + 10) ec.heroRevive();
  // Utstyr: billigste spor først, bare når det er gull og jern til overs.
  if (ec.hero && w >= 8) { const k = Object.keys(HERO_GEAR).sort((a, b) => ec.heroGearLevel(a) - ec.heroGearLevel(b))[0], c = ec.heroGearCost(k);
    if (c && ec.res.gold >= c.gold + 80 && ec.res.iron >= c.iron + 25) ec.buyHeroGear(k); }
  heroAuto(ec);
}
"""

RIVAL = r"""
// Rivalen har også en helt (rivalBot er boten fra game_sim.js, som kaller heroBot), og velger talenter og doktriner tilfeldig.
{ const _end = Rival.prototype.end; Rival.prototype.end = function (foe) { const r = _end.call(this, foe); heroAfterWave(this.ec, r.sim, true); return r; }; }
"""

CSS = r"""
.choicecard { position: fixed; z-index: 60; text-align: left; max-height: calc(100dvh - 24px); background: linear-gradient(180deg, #2a1a08, #120e0a); box-shadow: 0 0 0 100vmax rgba(0, 0, 0, .6), 0 20px 50px rgba(0, 0, 0, .6); }
.choicecard h2, .choicecard .ac-eyebrow, .choicecard .ac-note { text-align: center; }
.ch-opts { display: flex; flex-direction: column; gap: 8px; }
.ch-opt { text-align: left; background: rgba(233, 162, 59, .08); border: 1px solid #6b4a1f; border-radius: 10px; padding: 10px 12px; color: var(--fg); display: flex; gap: 10px; align-items: center; cursor: pointer; font: inherit; width: 100%; }
.ch-opt img { width: 52px; height: 52px; flex: none; border-radius: 8px; background: rgba(0, 0, 0, .25); }
.ch-opt .ch-t { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.ch-opt b { font-family: var(--display); font-size: 16px; color: var(--flame); }
.ch-opt span { font-size: 13px; color: var(--muted); }
.ch-opt small { font-size: 11px; color: #c9a36a; }
.ch-opt:hover, .ch-opt:focus-visible { border-color: var(--flame); background: rgba(233, 162, 59, .16); }
.ch-row { display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; }
.ch-later { background: transparent; border: 1px solid var(--line); color: var(--muted); border-radius: 8px; padding: 8px 14px; font: inherit; }
.herostrip { display: flex; align-items: center; gap: 10px; border: 1px solid #6b4a1f; background: rgba(233, 162, 59, .07); border-radius: 10px; padding: 8px 10px; margin: 6px 0 8px; }
.herostrip img { width: 48px; height: 48px; border-radius: 8px; background: rgba(0, 0, 0, .25); flex: none; }
.herostrip .hs-mid { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 3px; }
.herostrip .hs-mid b { color: var(--flame); font-family: var(--display); }
.herostrip .hs-mid small { color: var(--muted); font-size: 12px; }
.herostrip .xpbar { margin: 0; }
.chips { display: flex; flex-wrap: wrap; gap: 4px; }
.chips span { font-size: 11px; border: 1px solid #5a4630; border-radius: 999px; padding: 1px 7px; color: #e6d2b0; }
.chips span.path { border-color: var(--flame); color: var(--flame); }
.hs-gear { flex: 1 1 100%; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 4px; }
.hs-gear .buy, .hs-gear .maxed { align-items: center; padding: 4px; font-size: 11.5px; white-space: normal; text-align: center; }
.hs-gear .buy small { color: var(--muted); font-weight: 400; }
.hs-go { background: var(--flame); color: var(--flame-ink); border: 0; border-radius: 8px; padding: 8px 10px; font-weight: 700; flex: none; font: inherit; font-weight: 700; }
"""

UI = r"""
  // ---------- Helten, doktriner og funn (versjon 24) ----------
  const choiceCard = document.createElement('div'); choiceCard.className = 'arenacard choicecard'; choiceCard.hidden = true; $('.stage').appendChild(choiceCard);
  const heroStatLine = T => `❤ ${T.hp} · ⚔ ${T.dmg} · ⛨ ${T.armor}${T.ranged ? ` · ${String(T.range).replace('.', ',')} m` : ''}${T.heal ? ` · ✚ ${T.heal}` : ''}`;
  function placeHero() {
    const ec = state.econ, h = ec.hero; if (!h || state.army.some(a => a.type === h.type)) return;
    const ranged = TYPES[h.type].ranged, rows = ranged ? [3, 4, 2, 5] : [1, 0, 2];
    const cols = [7, 8, 6, 9, 5, 10, 4, 11, 3, 12, 2, 13, 1, 14, 0, 15];
    for (const row of rows) for (const col of cols) {
      if (col >= MAP.cols || row >= MAP.rows || state.army.some(a => a.col === col && a.row === row)) continue;
      state.army.push({ type: h.type, col, row, order: ranged ? 'follow' : 'advance', squad: null, delay: 0 });
      return;
    }
  }
  function closeChoice() { choiceCard.hidden = true; renderPanel(); }
  function choiceOpt(attrs, title, text, extra, pic) {
    return `<button type="button" class="ch-opt" ${attrs}>${pic ? `<img alt="" src="${pic}">` : ''}<span class="ch-t"><b>${title}</b><span>${text}</span>${extra ? `<small>${extra}</small>` : ''}</span></button>`;
  }
  function openChoice(kind) {
    const ec = state.econ, h = ec.hero;
    let html = '';
    if (kind === 'class') {
      if (h) return;
      const eff = ec.types(TYPES);
      html = `<div class="ac-eyebrow">Heltehallen</div><h2>Velg din helt</h2>
        <p class="ac-note">Helten tar ingen plass i hæren, kan ikke selges, og kommer tilbake hver wave. Han får erfaring av fiender han dreper. Hvert nivå velger du ett av tre tilfeldige talenter; på nivå ${HERO_PATH_LEVEL} velger du retning.</p>
        <div class="ch-opts">${Object.keys(HERO_CLASSES).map(k => choiceOpt(`data-hire="${k}"`, HERO_CLASSES[k].name, HERO_CLASSES[k].short, `${heroStatLine(eff[k])} · Nivå ${HERO_PATH_LEVEL}: ${HERO_CLASSES[k].paths.map(p => HERO_PATHS[p].name).join(' eller ')}`, portraits[k])).join('')}</div>
        <div class="ch-row"><span class="ac-prize">Koster ${HERO_COST.gold} gull</span><button type="button" class="ch-later" data-later>Senere</button></div>`;
    } else if (kind === 'talent') {
      if (!h || !h.offer) return;
      const lv = h.picks + 2, path = h.kind === 'path';
      html = `<div class="ac-eyebrow">${HERO_CLASSES[h.type].name} · nivå ${lv}</div><h2>${path ? 'Velg retning' : 'Velg et talent'}</h2>
        <p class="ac-note">${path ? 'Retningen gjelder resten av spillet.' : `+${Math.round(HERO_GROWTH * 100)} % helse og skade, og ett talent.`}${ec.heroPending() > 1 ? ` Du har ${ec.heroPending()} valg å ta.` : ''}</p>
        <div class="ch-opts">${h.offer.map(id => { const t = path ? HERO_PATHS[id] : HERO_TALENTS[id];
          return choiceOpt(`data-talent="${id}"`, t.name, t.desc, path ? 'Retning' : t.cls ? `${HERO_CLASSES[t.cls].name}` : h.talents.includes(id) ? 'Felles · tatt før, stables' : 'Felles'); }).join('')}</div>
        <div class="ch-row">${path ? '' : buyBtn('Trekk på nytt', ec.heroRerollCost(), 'heroReroll')}<button type="button" class="ch-later" data-later>Senere</button></div>`;
    } else if (kind === 'doctrine') {
      if (!ec.docOffer) return;
      html = `<div class="ac-eyebrow">${BARRACKS[ec.barracks].name}</div><h2>Velg doktrine</h2>
        <p class="ac-note">Tre tilfeldige doktriner. Den du velger, gjelder resten av spillet.</p>
        <div class="ch-opts">${ec.docOffer.map(d => choiceOpt(`data-doc="${d}"`, DOCTRINES[d].name, DOCTRINES[d].desc)).join('')}</div>
        <div class="ch-row"><button type="button" class="ch-later" data-later>Senere</button></div>`;
    }
    choiceCard.innerHTML = html; choiceCard.hidden = false; choiceCard.dataset.kind = kind;
    refreshLive();
  }
  choiceCard.addEventListener('click', e => {
    const ec = state.econ;
    if (e.target.closest('[data-later]')) { closeChoice(); return; }
    const hire = e.target.closest('[data-hire]');
    if (hire) {
      if (!ec.can(HERO_COST)) { explainMissing(HERO_COST); return; }
      if (state.phase !== 'build') { toast('Helten kan rekrutteres i byggefasen.'); return; }
      if (!ec.recruitHero(hire.dataset.hire)) return;
      placeHero(); sfx('build'); closeChoice(); rebuild(); renderPanel();
      toast(`${HERO_CLASSES[hire.dataset.hire].name} står i hæren. Dra ham dit du vil ha ham.`);
      return;
    }
    const tl = e.target.closest('[data-talent]');
    if (tl) {
      const path = ec.hero.kind === 'path', id = tl.dataset.talent;
      if (!ec.heroPick(id)) return;
      sfx('build'); toast(`${path ? 'Retning' : 'Talent'}: ${(path ? HERO_PATHS : HERO_TALENTS)[id].name}.${state.phase === 'build' ? '' : ' Gjelder fra neste wave.'}`);
      if (state.phase === 'build') rebuild();
      if (ec.hero.offer) openChoice('talent'); else closeChoice();
      return;
    }
    const rr = e.target.closest('[data-act="heroReroll"]');
    if (rr) { if (!ec.heroReroll()) { explainMissing(ec.heroRerollCost()); return; } sfx('build'); openChoice('talent'); renderPanel(); return; }
    const dc = e.target.closest('[data-doc]');
    if (dc) {
      if (!ec.pickDoctrine(dc.dataset.doc)) return;
      sfx('build'); toast(`Doktrine: ${DOCTRINES[dc.dataset.doc].name}. ${DOCTRINES[dc.dataset.doc].desc}`);
      if (state.phase === 'build') rebuild();
      closeChoice();
    }
  });
  // Åpne et valg som venter, når det passer (i byggefasen, uten andre kort oppe).
  function maybeChoice() {
    const ec = state.econ;
    if (state.phase !== 'build' || !choiceCard.hidden || !arenaCard.hidden) return;
    if (ec.docOffer) openChoice('doctrine');
    else if (ec.hero && ec.hero.offer) openChoice('talent');
  }
  // En falt helt står igjen på rutenettet, men er borte fra slagmarken til han er gjenopplivet.
  function markFallenHero() {
    const h = state.econ.hero; if (!h || !h.fallen || !sim) return;
    sim.units.forEach(u => { if (u.side === 'p' && u.type === h.type) { u.alive = false; u.hp = 0; const v = visuals.get(u.id); if (v) v.deadT = 3; } });
  }
  function heroGearHtml() {
    const ec = state.econ;
    return `<div class="hs-gear">${Object.keys(HERO_GEAR).map(k => { const g = HERO_GEAR[k], l = ec.heroGearLevel(k), c = ec.heroGearCost(k);
      return c ? buyBtn(`${g.name} <small>${l}/3</small>`, c, 'heroGear', `data-k="${k}" data-tip="${g.desc}"`) : `<span class="maxed" data-tip="${g.desc}">${g.name} 3/3</span>`; }).join('')}</div>`;
  }
  function heroStripHtml() {
    const ec = state.econ, h = ec.hero;
    if (!h) return `<div class="herostrip"><img alt="" src="${portraits.heroKnight || ''}"><div class="hs-mid"><b>Helt</b><small>Din egen kriger. Tar ingen plass i hæren og blir sterkere for hver wave.</small></div><button type="button" class="hs-go" data-act="heroOpen">Velg helt</button></div>`;
    const lv = ec.heroLevel(), nx = ec.heroNext(), prev = HERO_XP[lv - 2] || 0, pct = nx ? (h.xp - prev) / (nx - prev) * 100 : 100, pend = ec.heroPending();
    const T = ec.types(TYPES)[h.type];
    return `<div class="herostrip"><img alt="" src="${portraits[h.type] || ''}"${h.fallen ? ' style="filter:grayscale(1) brightness(.6)"' : ''}><div class="hs-mid"><b>${HERO_CLASSES[h.type].name} · nivå ${lv}${h.fallen ? ' · falt' : ''}</b>
      <div class="xpbar" data-tip="${nx ? `Erfaring ${h.xp} av ${nx} til nivå ${lv + 1}` : 'Høyeste nivå'}"><i style="width:${pct}%"></i><span>★ ${lv}</span></div>
      <small>${heroStatLine(T)}</small>
      ${h.path || h.talents.length ? `<div class="chips">${h.path ? `<span class="path">${HERO_PATHS[h.path].name}</span>` : ''}${h.talents.map(id => `<span data-tip="${HERO_TALENTS[id].desc}">${HERO_TALENTS[id].name}</span>`).join('')}</div>` : ''}</div>
      ${h.fallen ? `<small style="color:#f0a59d">Falt i kamp. Gjenopplives for å kjempe igjen.</small>` : ''}</div>
      ${h.fallen ? buyBtn('Gjenopplive', ec.heroReviveCost(), 'heroRevive') : pend > 0 ? `<button type="button" class="hs-go" data-act="heroChoice">Velg${pend > 1 ? ` (${pend})` : ''}</button>` : ''}${heroGearHtml()}</div>`;
  }
  function doctrineHtml() {
    const ec = state.econ, d = ec.docs || [];
    return `<h3 style="margin-top:6px">Doktriner ${tipIcon('Hvert nytt Barracks-nivå trekker tre tilfeldige doktriner. Du velger én, og den gjelder resten av spillet.')}</h3>
      ${d.length ? `<div class="chips">${d.map(k => `<span data-tip="${DOCTRINES[k].desc}">${DOCTRINES[k].name}</span>`).join('')}</div>` : '<p class="note">Ingen ennå. Den første kommer med Barracks II.</p>'}
      ${ec.docOffer ? `<button type="button" class="hs-go" data-act="docChoice" style="margin-top:6px">Velg doktrine</button>` : ''}`;
  }
"""

BUILD_CASES = r"""      case 'heroKnight': {
        const hy = humanoid(rig, mats.steelLight, 1.2);
        rig.add(mesh(GEO.helmet, mats.brass, 0, hy + 0.18, 0));
        rig.add(mesh(new THREE.BoxGeometry(0.85, 1.2, 0.07), heroMats.cape, 0, 1.05, -0.32));
        const sw = mesh(new THREE.BoxGeometry(0.11, 1.45, 0.05), mats.ember, 0.45, 1.25, 0.3); sw.rotation.x = -0.35; rig.add(sw);
        rig.add(mesh(GEO.shield, mats.brass, -0.05, 0.85, 0.44));
        rig.add(mesh(heroMats.starGeo, heroMats.star, 0, hy + 0.85, 0));
        rig.scale.setScalar(1.12); height = 2.4; break;
      }
      case 'heroHunter': {
        const hy = humanoid(rig, mats.fur, 1.15);
        rig.add(mesh(GEO.hood, heroMats.cape, 0, hy + 0.2, 0));
        rig.add(mesh(new THREE.BoxGeometry(0.7, 1.1, 0.06), heroMats.cape, 0, 1.0, -0.3));
        const barrel = mesh(GEO.barrel, mats.brass, 0.16, 1.15, 0.72); barrel.rotation.x = Math.PI / 2; rig.add(barrel);
        const scope = mesh(GEO.scope, mats.ember, 0.16, 1.28, 0.45); scope.rotation.x = Math.PI / 2; rig.add(scope);
        rig.add(mesh(heroMats.starGeo, heroMats.star, 0, hy + 0.85, 0));
        height = 2.1; break;
      }
      case 'heroPriest': {
        const hy = humanoid(rig, heroMats.robe);
        rig.add(mesh(new THREE.ConeGeometry(0.5, 1.0, 10), heroMats.robe, 0, 0.5, 0), mesh(GEO.hood, heroMats.robe, 0, hy + 0.15, 0));
        rig.add(mesh(new THREE.CylinderGeometry(0.04, 0.04, 2.1, 6), mats.brass, 0.42, 1.05, 0.15));
        rig.add(mesh(new THREE.OctahedronGeometry(0.17), mats.ember, 0.42, 2.2, 0.15));
        rig.add(mesh(heroMats.starGeo, heroMats.star, 0, hy + 0.85, 0));
        height = 2.3; break;
      }
      case 'warden': {"""


def apply(s):
    # ---- Logikk ----
    s = sub(s, "const supplyOf = T => (T && T.tier) || 1;", "const supplyOf = T => T && T.hero ? 0 : (T && T.tier) || 1;   // helten tar ingen plass")
    s = sub(s, "  out.level = level;\n  return out;\n}", "  if (out.vet && level >= MAX_LEVEL) { out.hp = Math.round(out.hp * (1 + out.vet)); out.dmg = Math.round(out.dmg * (1 + out.vet)); }   // doktrinen Veteraner\n  out.level = level;\n  return out;\n}")
    s = sub(s, "      this.events.push({ kind: 'death', unit: t, by: u.type });\n",
               "      this.events.push({ kind: 'death', unit: t, by: u.type });\n      if (this.heroU === undefined) this.heroU = this.units.find(x => x.side === 'p' && x.T.hero) || null;\n"
               "      if (this.heroU && this.heroU.alive && t.side === 'e' && (u === this.heroU || dist(this.heroU, t) < 10)) this.heroXp = (this.heroXp || 0) + (BOUNTY[t.type] || 1) * (u === this.heroU ? 1 : 0.4);   // helten lærer av det som faller rundt ham\n")
    s = sub(s, "if (this.deliveries.length < 300) this.deliveries.push({ node: k, res: NODES[k].res, amount: amt, worker: i }); }",
               "if (this.deliveries.length < 300) this.deliveries.push({ node: k, res: NODES[k].res, amount: amt, worker: i }); if (this._find) this._find(k); }")
    s = sub(s, "\nif (typeof module !== 'undefined') module.exports = { supplyOf, WARDEN_GEAR,", LOGIC + RIVAL + "\nif (typeof module !== 'undefined') module.exports = { supplyOf, WARDEN_GEAR,")
    s = sub(s, "const RIVAL_L = { TYPES,", "const RIVAL_L = { heroBot, TYPES,")
    # Rivalens helt står i hæren hans (også i arenaen).
    s = sub(s, "makeView() { const ec = this.ec; this.view = new Sim(this.army,", "makeView() { const ec = this.ec; this.view = new Sim(withHero(this.army, ec),")
    s = sub(s, "    this.sim = new Sim(this.army, { types: ec.types(TYPES, versusScale(W)),", "    this.sim = new Sim(withHero(this.army, ec), { types: ec.types(TYPES, versusScale(W)),")
    s = sub(s, "  const foes = rival.army.map(a => {", "  const foes = withHero(rival.army, rival.ec).map(a => {")

    # ---- Grafikk og UI ----
    s = sub(s, ".ac-go span { font-family: var(--mono); margin-left: 6px; }\n", ".ac-go span { font-family: var(--mono); margin-left: 6px; }\n" + CSS)
    s = sub(s, "  function buildUnit(u) {\n", "  const heroMats = { cape: M(0x8a1f1a, { roughness: 0.8 }), robe: M(0xd9cdb5, { roughness: 0.9 }), star: new THREE.MeshBasicMaterial({ color: 0xffd36a }), starGeo: new THREE.OctahedronGeometry(0.16) };\n  function buildUnit(u) {\n")
    s = sub(s, "      case 'warden': {", BUILD_CASES)
    s = sub(s, '<div class="roster" id="palette"></div>', '<div id="herostrip"></div>\n        <div class="roster" id="palette"></div>')
    s = sub(s, "    $('#groups').innerHTML = ORDER_KEYS.map(k => {", "    $('#herostrip').innerHTML = heroStripHtml();\n    $('#groups').innerHTML = ORDER_KEYS.map(k => {")
    # Kortene viser prisen etter doktriner.
    s = sub(s, "<span class=\"u-cost\">${icon('gold', 14)}${T.cost}${T.iron ? ` ${icon('iron', 14)}${T.iron}` : ''}${T.coal ? ` ${icon('coal', 14)}${T.coal}` : ''}",
               "<span class=\"u-cost\">${(p => `${icon('gold', 14)}${p.gold}${p.iron ? ` ${icon('iron', 14)}${p.iron}` : ''}${p.coal ? ` ${icon('coal', 14)}${p.coal}` : ''}`)(ec.unitPrice(T))}")
    # Barracks-kortet viser doktrinene.
    s = sub(s, "nb.cost, 'barracks', nb.future ? 'data-lock=\"future\"' : '') })])}</div>`;", "nb.cost, 'barracks', nb.future ? 'data-lock=\"future\"' : '') })])}${doctrineHtml()}</div>`;")
    s = sub(s, "    $('#buildings').innerHTML = ['barracks', 'forge', 'workshop', 'gatehouse', 'sanctum'].map(k => BUILDING_HTML[k]()).join('');",
               "    $('#buildings').innerHTML = `<div class=\"card\"><h3>Heltehallen ${tipIcon('Din egen helt. Han tar ingen plass i hæren, kommer tilbake hver wave og får erfaring av fiender han dreper.')}</h3>${heroStripHtml()}</div>` + ['barracks', 'forge', 'workshop', 'gatehouse', 'sanctum'].map(k => BUILDING_HTML[k]()).join('');")
    s = sub(s, "barracks: () => ec.buyBarracks(), wall:", "heroGear: () => { if (!ec.buyHeroGear(k)) return false; toast(`${HERO_CLASSES[ec.hero.type].name} fikk ${HERO_GEAR[k].name.toLowerCase()} nivå ${ec.heroGearLevel(k)}.`); return true; }, heroOpen: () => (openChoice('class'), false), heroRevive: () => { if (state.phase !== 'build') { toast('Helten kan gjenopplives i byggefasen.'); return false; } if (!ec.heroRevive()) return false; toast(`${HERO_CLASSES[ec.hero.type].name} er tilbake i hæren.`); return true; }, heroChoice: () => (openChoice('talent'), false), docChoice: () => (openChoice('doctrine'), false),\n      barracks: () => ec.buyBarracks(), wall:")
    s = sub(s, "      sfx('build');\n      // Oppgraderinger virker", "      sfx('build');\n      if (b.dataset.act === 'barracks' && ec.docOffer) setTimeout(() => openChoice('doctrine'), 60);\n      // Oppgraderinger virker")
    # Helten kan ikke selges eller byttes ut.
    s = sub(s, "    const ex = i >= 0 ? state.army[i] : null;\n    if (tool === 'remove' || (ex && ex.type === tool)) {",
               "    const ex = i >= 0 ? state.army[i] : null;\n    if (ex && TYPES[ex.type].hero) { toast('Helten kan ikke selges eller byttes ut. Dra ham til en annen rute.'); return; }\n    if (tool === 'remove' || (ex && ex.type === tool)) {")
    s = sub(s, """  function removeSelected() {
    state.army.forEach((a, i) => { if (state.selection.has(i)) refund(a); });
    state.army = state.army.filter((a, i) => !state.selection.has(i));""", """  function removeSelected() {
    const gone = (a, i) => state.selection.has(i) && !TYPES[a.type].hero;
    if (state.army.some((a, i) => state.selection.has(i) && TYPES[a.type].hero)) toast('Helten kan ikke selges. Han blir stående.');
    state.army.forEach((a, i) => { if (gone(a, i)) refund(a); });
    state.army = state.army.filter((a, i) => !gone(a, i));""")
    s = sub(s, "u.type === 'warden' ? 'Flammens vokter' : 'Din unit'", "u.type === 'warden' ? 'Flammens vokter' : TYPES[u.type].hero ? 'Din helt' : 'Din unit'")
    s = sub(s, "<span>Nivå ${lvl}/${MAX_LEVEL} ${pips}</span></div>", "<span>${TYPES[k].hero ? `Helt · nivå ${state.econ.heroLevel()}` : `Nivå ${lvl}/${MAX_LEVEL} ${pips}`}</span></div>")
    # Etter waven: erfaring, nivå og valg.
    s = sub(s, "    if (r.win) { report.bonus = waveBonus(W.n); ec.add({ gold: report.bonus }); popRes('gold', report.bonus); }\n    state.lastReport = report;",
               "    if (r.win) { report.bonus = waveBonus(W.n); ec.add({ gold: report.bonus }); popRes('gold', report.bonus); }\n    report.hero = heroAfterWave(ec, sim);\n"
               "    if (report.hero && report.hero.lost != null) setTimeout(() => toast(`${HERO_CLASSES[ec.hero.type].name} falt${report.hero.lost ? ` og mistet ${report.hero.lost} erfaring` : ''}. Gjenopplive ham for ${ec.heroReviveCost().gold} gull (Hær-fanen eller Heltehallen).`), 600);\n"
               "    if (report.hero && report.hero.up) setTimeout(() => toast(`${HERO_CLASSES[ec.hero.type].name} nådde nivå ${ec.heroLevel()}! Velg ${ec.hero.kind === 'path' ? 'retning' : 'talent'}.`), 900);\n"
               "    setTimeout(maybeChoice, 1800);\n    state.lastReport = report;")
    s = sub(s, "      ec.deliveries.length = 0;\n    }\n", "      ec.deliveries.length = 0;\n    }\n    if (ec.finds && ec.finds.length) { const f = ec.finds.shift(); toast('⛏ ' + f.text); if (f.bag) Object.keys(f.bag).forEach(r => popRes(r, f.bag[r])); if (f.node && nodeVis[f.node]) nodeVis[f.node].pulse = 0.8; }\n")
    s = sub(s, "  function renderBuildings() {", UI + "  function renderBuildings() {")
    s = sub(s, "    sim.units.forEach(u => visuals.set(u.id, buildUnit(u)));\n    clearShots();\n    buildPlan();",
            "    sim.units.forEach(u => visuals.set(u.id, buildUnit(u)));\n    markFallenHero();\n    clearShots();\n    buildPlan();")
    return s
