// ===== The Last Flame — oppgraderinger per unit (utkast) =====
// Hver unit har grunnversjon + 3 oppgraderinger, kjøpt på én bestemt soldat.
// mod: hp/armor/range/splash/pierce/taunt/aura/healRange legges til, *Mul ganges, resten settes.
const UPGRADES = {
  shieldguard: [
    { name: 'Jernkant', desc: 'Jernkant på skjoldet og hjelm. Mer helse og rustning.', cost: { gold: 5 }, mod: { hp: 70, armor: 1 } },
    { name: 'Tårnskjold', desc: 'Høyt skjold og brynjekrage. Units rett bak ham tar 25 % mindre skade fra skudd og spytt.', cost: { gold: 8, iron: 1 }, mod: { hp: 90, armor: 1, shieldwall: true } },
    { name: 'Runeskjold', desc: 'Gullkant og glødende rune. Skjoldslag hvert 6. sekund slår fienden bakover og lammer den.', cost: { gold: 12, iron: 2, coal: 1 }, mod: { hp: 50, bash: 6 } },
  ],
  stormreaver: [
    { name: 'Slipt øks', desc: 'Blankere egg og nagler på vesten. Slår hardere.', cost: { gold: 5 }, mod: { dmgMul: 1.2, hp: 30 } },
    { name: 'Skjegg-øks', desc: 'Større øks og ulveskinn. Slår raskere og tåler mer.', cost: { gold: 8, iron: 1 }, mod: { intervalMul: 0.87, armor: 1, hp: 30 } },
    { name: 'Stormraseri', desc: 'Lyn-runer på øksa. Hvert 3. slag er et piruett-slag som treffer alle rundt ham.', cost: { gold: 12, iron: 2, coal: 1 }, mod: { spin: 3 } },
  ],
  ironshot: [
    { name: 'Riflet løp', desc: 'Lengre løp og stålhatt. Skyter lenger og hardere.', cost: { gold: 5 }, mod: { range: 2, dmgMul: 1.15 } },
    { name: 'Damptank', desc: 'Større messingtank. Skyter raskere og tåler mer.', cost: { gold: 8, iron: 1 }, mod: { intervalMul: 0.83, hp: 30 } },
    { name: 'Kull-ladning', desc: 'Glødende munning. Hvert 4. skudd sprekker og treffer fiender rundt målet.', cost: { gold: 12, iron: 2, coal: 1 }, mod: { burst: 4 } },
  ],
  longfang: [
    { name: 'Kikkertsikte', desc: 'Messingkikkert. Skyter lenger og hardere.', cost: { gold: 5 }, mod: { range: 2, dmgMul: 1.15 } },
    { name: 'Langt løp', desc: 'Enda lengre løp og kappe. Går gjennom mer rustning og sikter raskere.', cost: { gold: 8, iron: 1 }, mod: { pierce: 2, intervalMul: 0.86 } },
    { name: 'Merket skudd', desc: 'Glødende linse. Velger den sterkeste fienden, og første skudd mot et nytt mål gjør dobbel skade.', cost: { gold: 12, iron: 2, coal: 1 }, mod: { marks: true } },
  ],
  ironwall: [
    { name: 'Naglede plater', desc: 'Tykke plater over hele kroppen. Mye mer helse og rustning.', cost: { gold: 12, iron: 1 }, mod: { hp: 110, armor: 1 } },
    { name: 'Piggskjold', desc: 'Pigger på skjoldet. Fiender som slår ham, skader seg selv, og han roper lenger.', cost: { gold: 18, iron: 2 }, mod: { hp: 80, thorns: 0.3, taunt: 1.5 } },
    { name: 'Jernbastion', desc: 'Når han er under halv helse, setter han føttene og tar halv skade i 5 sekunder.', cost: { gold: 25, iron: 3, coal: 1 }, mod: { hp: 80, brace: 5 } },
  ],
  frostbrand: [
    { name: 'Frostsmidde økser', desc: 'Blå, iskalde økser. Slår hardere.', cost: { gold: 12, iron: 1 }, mod: { dmgMul: 1.45, hp: 40 } },
    { name: 'Blodrus', desc: 'Bjørneskinn og krigsmaling. Slår raskere og tåler mer.', cost: { gold: 18, iron: 2 }, mod: { intervalMul: 0.85, hp: 70, armor: 1 } },
    { name: 'Frostbitt', desc: 'Rim på øksene. Hvert treff bremser fienden.', cost: { gold: 25, iron: 3, coal: 1 }, mod: { slows: 1.2 } },
  ],
  thunderbore: [
    { name: 'Større løp', desc: 'Videre kanonmunning. Større smell og større område.', cost: { gold: 12, iron: 1 }, mod: { dmgMul: 1.25, splash: 0.4 } },
    { name: 'Forsterket stativ', desc: 'Kraftigere stativ og skjold foran. Skyter lenger og tåler mer.', cost: { gold: 18, iron: 2 }, mod: { range: 2, hp: 60, armor: 1 } },
    { name: 'Sjokkbølge', desc: 'Gnistrende granater. Treffene dytter fiender bakover.', cost: { gold: 25, iron: 3, coal: 1 }, mod: { knock: 0.7 } },
  ],
  hearthkeeper: [
    { name: 'Klarere lykt', desc: 'Lykten brenner sterkere. Leger mer.', cost: { gold: 12, iron: 1 }, mod: { healMul: 1.45, hp: 30 } },
    { name: 'Glødesirkel', desc: 'Ring av glør rundt ham. Leger oftere og lenger unna.', cost: { gold: 18, iron: 2 }, mod: { healEveryMul: 0.8, healRange: 2 } },
    { name: 'Varm glo', desc: 'Lykten deler seg. Leger to allierte om gangen.', cost: { gold: 25, iron: 3, coal: 1 }, mod: { twinHeal: true } },
  ],
  pyreguard: [
    { name: 'Bred dyse', desc: 'Bredere flamme. Treffer flere.', cost: { gold: 20, iron: 1, coal: 1 }, mod: { splash: 0.6, hp: 60, dmgMul: 1.1 } },
    { name: 'Kulltank', desc: 'Større tank på ryggen. Varmere og lenger flamme.', cost: { gold: 30, iron: 2, coal: 1 }, mod: { dmgMul: 1.25, range: 1 } },
    { name: 'Glødende bakke', desc: 'Flammen henger igjen. Det som treffes, brenner videre en stund.', cost: { gold: 40, iron: 3, coal: 2 }, mod: { burn: 10 } },
  ],
  siegebreaker: [
    { name: 'Mothaker', desc: 'Harpun med mothaker. Mer skade.', cost: { gold: 20, iron: 2 }, mod: { dmgMul: 1.3 } },
    { name: 'Vinsj', desc: 'Dampvinsj trekker harpunen raskt tilbake. Lader raskere.', cost: { gold: 30, iron: 3 }, mod: { intervalMul: 0.78, hp: 50 } },
    { name: 'Spidd', desc: 'Harpunen går tvers gjennom og treffer opptil to fiender bak målet.', cost: { gold: 40, iron: 4, coal: 2 }, mod: { skewer: 2 } },
  ],
  captain: [
    { name: 'Jernbanner', desc: 'Tyngre rustning og jernstang i banneret. Mer helse og rustning.', cost: { gold: 20, iron: 2 }, mod: { hp: 200, armor: 2 } },
    { name: 'Bredt banner', desc: 'Større banner som synes lenger. Auraen når lenger.', cost: { gold: 30, iron: 2 }, mod: { aura: 2, dmgMul: 1.2 } },
    { name: 'Samling', desc: 'Banneret brenner. Allierte i auraen slår 30 % hardere og gror sakte tilbake.', cost: { gold: 40, iron: 3, coal: 2 }, mod: { rally: 4 } },
  ],
  huskarl: [
    { name: 'Daneøks', desc: 'Langskaftet øks. Slår hardere.', cost: { gold: 20, iron: 2 }, mod: { dmgMul: 1.45 } },
    { name: 'Skjold og brynje', desc: 'Rundskjold og tung brynje. Mye mer helse og rustning.', cost: { gold: 30, iron: 3 }, mod: { hp: 250, armor: 2 } },
    { name: 'Feiende slag', desc: 'Hvert slag treffer opptil tre fiender.', cost: { gold: 40, iron: 4, coal: 2 }, mod: { sweep: 2 } },
  ],
};
const MAX_LEVEL = 3;

// Ny økonomi og tier-balanse (2. okt 2026). Knapphet som i Squadron: Tier 1 koster 10 gull.
// En fersk Tier 2 er ca. 90 % av en fullt oppgradert Tier 1 og ca. 120 % etter første oppgradering.
// Samme mønster mellom Tier 2 og Tier 3. Målt med simuleringer mot wave 4, 6 og 8.
const BALANCE = {
  shieldguard: { cost: 10 }, stormreaver: { cost: 10 }, ironshot: { cost: 10 }, longfang: { cost: 10 },
  ironwall: { cost: 25, iron: 2, hp: 340, armor: 4 },
  frostbrand: { cost: 26, iron: 1, hp: 250, dmg: 20 },
  thunderbore: { cost: 26, iron: 2, dmg: 23 },
  hearthkeeper: { cost: 24, iron: 1, heal: 26 },
  pyreguard: { cost: 58, iron: 2, coal: 2, hp: 300, dmg: 13 },
  siegebreaker: { cost: 62, iron: 3, coal: 0, dmg: 78 },
  captain: { cost: 55, iron: 2, hp: 360, dmg: 22, armor: 5 },
  huskarl: { cost: 60, iron: 3, hp: 400, armor: 6, dmg: 28 },
};
for (const k in BALANCE) Object.assign(TYPES[k], BALANCE[k]);
// Hva det koster å ta en unit fra nivå 0 til `level` (brukes til salg og visning).
function upgradeSpent(key, level) {
  const out = {};
  for (let i = 0; i < Math.min(level || 0, MAX_LEVEL); i++) { const c = UPGRADES[key][i].cost; for (const r in c) out[r] = (out[r] || 0) + c[r]; }
  return out;
}
// Bygger stat-blokken for en unit på et gitt nivå (0 = grunn).
function levelType(T, key, level) {
  if (!level || !UPGRADES[key]) return T;
  const out = Object.assign({}, T);
  if (T.bonus) out.bonus = Object.assign({}, T.bonus);
  for (let i = 0; i < Math.min(level, MAX_LEVEL); i++) {
    const m = UPGRADES[key][i].mod;
    for (const k in m) {
      const v = m[k];
      if (k === 'dmgMul') out.dmg = Math.round(out.dmg * v);
      else if (k === 'intervalMul') out.interval = +(out.interval * v).toFixed(3);
      else if (k === 'healMul') out.heal = Math.round(out.heal * v);
      else if (k === 'healEveryMul') out.healEvery = +(out.healEvery * v).toFixed(3);
      else if (['hp', 'armor', 'range', 'splash', 'pierce', 'taunt', 'aura', 'healRange'].includes(k)) out[k] = +((out[k] || 0) + v).toFixed(2);
      else out[k] = v;
    }
  }
  out.level = level;
  return out;
}
