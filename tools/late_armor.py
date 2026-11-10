"""Tier 3+ becomes necessary (version 33, Rune: «surviving on tier 1 and 2 is NOT an option ... after a certain level tier 1-2 isn't enough»).
Creatures from World 2 on wear armour that soaks a flat amount of every hit: +2 in waves 11–20, +8 in waves 21–30.
Small hits (Tier 1–2, 12–30 damage) lose a big share; heavy hits (Tier 3–4, Forge-upgraded, ballista) barely notice.
WAVE_ARMOR is applied through the wave scale (W.scale.armor) in Econ.types, so the game, the rival and every test tool get it.
Applied by build_v2.py after botplay.py."""
from patch import sub

LOGIC = r"""
// ===== Versjon 33: rustning på fiendene fra verden 2, så Tier 3+ trengs =====
const WAVE_ARMOR = w => w <= 10 ? 0 : w <= 20 ? 2 : 8;
WAVES.forEach(W => { W.scale.armor = WAVE_ARMOR(W.n); });
{
  const _t = Econ.prototype.types;
  Econ.prototype.types = function (baseTypes, enemyScale) {
    const out = _t.call(this, baseTypes, enemyScale), a = enemyScale && enemyScale.armor;
    if (a) for (const k in out) if (out[k].side === 'e') out[k].armor = (out[k].armor || 0) + a;
    return out;
  };
}
"""


def apply(s):
    s = sub(s, "\nif (typeof module !== 'undefined') module.exports = { supplyOf, WARDEN_GEAR,", LOGIC + "\nif (typeof module !== 'undefined') module.exports = { supplyOf, WARDEN_GEAR,")
    s = sub(s, "const versusScale = W => ({ hp: W.scale.hp * VERSUS.wave, dmg: W.scale.dmg * Math.sqrt(VERSUS.wave) });",
               "const versusScale = W => ({ hp: W.scale.hp * VERSUS.wave, dmg: W.scale.dmg * Math.sqrt(VERSUS.wave), armor: W.scale.armor || 0 });")
    return s
