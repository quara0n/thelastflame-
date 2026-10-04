"""Warden nerf (4 Oct 2026): the user reached wave 25 mostly by upgrading the Warden. Fully upgraded he held waves 3–9
alone. Gear and levels now give less: sword +7 damage and +8 % attack speed per level (was +12 / +15 %), shield +220 HP
(was +350), armor +1 (was +2), +5 % HP and damage per Warden level (was +8 %). Applied by build_v2.py."""
from patch import sub

def apply(s):
    s = sub(s, "    effect: lv => `+${lv * 12} skade og +${lv * 15} % angrepstakt` },", "    effect: lv => `+${lv * 7} skade og +${lv * 8} % angrepstakt` },")
    s = sub(s, "    effect: lv => `+${lv * 350} HP` },", "    effect: lv => `+${lv * 220} HP` },")
    s = sub(s, "    effect: lv => `+${lv * 2} rustning` },", "    effect: lv => `+${lv} rustning` },")
    s = sub(s, "const WARDEN_LEVEL_BONUS = 0.08;                            // +8 % HP og skade per nivå", "const WARDEN_LEVEL_BONUS = 0.05;                            // +5 % HP og skade per nivå (var 8 %)")
    s = sub(s, "        T.hp = Math.round((baseTypes[k].hp + w.shield * 350) * lvb);", "        T.hp = Math.round((baseTypes[k].hp + w.shield * 220) * lvb);")
    s = sub(s, "        T.dmg = Math.round((baseTypes[k].dmg + w.sword * 12) * lvb);", "        T.dmg = Math.round((baseTypes[k].dmg + w.sword * 7) * lvb);")
    s = sub(s, "        T.interval = +(baseTypes[k].interval / (1 + 0.15 * w.sword)).toFixed(3);", "        T.interval = +(baseTypes[k].interval / (1 + 0.08 * w.sword)).toFixed(3);")
    s = sub(s, "        T.armor = baseTypes[k].armor + w.armor * 2;", "        T.armor = baseTypes[k].armor + w.armor;")
    # Teksten i Sanctum.
    s = s.replace("GEAR_NOW = { sword: lv => `+${lv * 12} skade`, shield: lv => `+${lv * 350} HP`, armor: lv => `+${lv * 2} rustn.` }",
                  "GEAR_NOW = { sword: lv => `+${lv * 7} skade`, shield: lv => `+${lv * 220} HP`, armor: lv => `+${lv} rustn.` }")
    s = s.replace("Hvert nivå gir +8 % HP og skade.", "Hvert nivå gir +5 % HP og skade.")
    return s
