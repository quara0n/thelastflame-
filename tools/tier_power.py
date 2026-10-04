"""Higher tiers are worth more per army space and per gold (4 Oct 2026, after the user compared an upgraded Ironhulk with an
upgraded Shieldguard). Each unit gets a power multiplier m (power ≈ HP × damage per second); HP and damage are both scaled by
√m. Targets, fully upgraded, power per gold compared with the Tier 1 unit of the same role: Tier 2 ≈ 1.1×, Tier 3 ≈ 1.25×,
Tier 4 ≈ 1.4×. Units already above target are left alone. Applied by build_v2.py after world3.py."""
from patch import sub

POWER = { 'ironwall': 1.8, 'thunderbore': 1.6, 'captain': 1.6, 'siegebreaker': 1.15,
          'ironhulk': 2.45, 'mammoth': 1.25, 'skyspear': 1.5, 'hearthengine': 1.5 }
# Fiender som var for lette.
ENEMY = { 'raptor': {'hp': 220, 'dmg': 19} }

def apply(s):
    js = ("// Høyere tiers er verdt mer per plass og per gull (4. okt 2026). HP og skade ganges med √m.\n"
          f"const TIER_POWER = {POWER};\n"
          "for (const k in TIER_POWER) { const f = Math.sqrt(TIER_POWER[k]); TYPES[k].hp = Math.round(TYPES[k].hp * f); TYPES[k].dmg = Math.round(TYPES[k].dmg * f); if (TYPES[k].heal) TYPES[k].heal = Math.round(TYPES[k].heal * f); }\n"
          f"Object.entries({ENEMY}).forEach(([k, v]) => Object.assign(TYPES[k], v));\n")
    return sub(s, "const ARCHER = { name: 'Bueskytter på muren'", js + "const ARCHER = { name: 'Bueskytter på muren'")
