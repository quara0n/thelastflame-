"""Gate repair costs gold as well as stone (version 40, 13 Oct 2026, Rune: «harde valg i begynnelsen … produksjon, hæren, porten»).
Before, a full repair cost only 6–12 stone, so the gate was free to keep whole and never competed with the army or workers.
Now a full repair also costs gold (REPAIR_GOLD: base + per wall level), scaled by how much of the gate is missing.
Applied by build_v2.py last in the chain."""
from patch import sub


def apply(s):
    s = sub(s, "    return { stone: Math.max(1, Math.ceil(miss / this.gateMax() * (6 + 6 * this.wall))) };",
            "    const f = miss / this.gateMax();\n"
            "    return { gold: Math.max(1, Math.ceil(f * (REPAIR_GOLD.base + REPAIR_GOLD.perWall * this.wall))), stone: Math.max(1, Math.ceil(f * (6 + 6 * this.wall))) };")
    s = sub(s, "const WALLS = [", "// Versjon 40: reparasjon av porten koster gull også (full reparasjon: base + perWall × murnivå, delt på skaden).\n"
            "const REPAIR_GOLD = { base: 10, perWall: 6 };\nconst WALLS = [")
    s = sub(s, "tip: 'Setter porten i full stand. Prisen avhenger av skaden og murens nivå.'",
            "tip: 'Setter porten i full stand. Koster gull og stein etter hvor skadet den er og murens nivå.'")
    return s
