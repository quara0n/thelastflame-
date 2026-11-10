# Runes spilltest 15. okt (versjon 48).
# - Hver wave har bare den nye arten (wave 5 også slangene som kommer samtidig). Bosswaves beholder følget.
#   Kjemper og kullmødre står alene, 14 og 12 av dem.
# - Fiender på bakken går etter hæren din så lenge noen av dine står ute på slagmarken, i stedet for å gå forbi til porten.
# - Oppgraderinger koster minst like mye som uniten, og mer per nivå (×1, ×1,4, ×1,8 av prisen).
# - Tømmerhogsten har plass til 6 arbeidere.
import waves30
from patch import sub

GIANT_N = {'colossus': 14, 'treant': 14, 'urdragon': 14, 'tyrant': 14, 'earthshaker': 14, 'broodmother': 12}

def pure(W):
    out, seen = [], set()
    for st, g, ex in W:
        debut = {t for t, n, r in g if t not in seen}
        seen |= {t for t, n, r in g}
        if ex.get('boss'): out.append((st, g, ex)); continue
        head = g[0]
        others = [x for x in g[1:] if x[0] in debut]
        if head[0] in GIANT_N and not others:
            out.append((st, [(head[0], GIANT_N[head[0]], head[2])], ex)); continue
        if others:   # wave 5: kråker og slanger, 70/30
            n2 = 12; others = [(others[0][0], n2, others[0][2])]
            out.append((st, [(head[0], 40 - n2, head[2])] + others, ex)); continue
        out.append((st, [(head[0], 40, head[2])], ex))
    return out

LOGIC = r"""
// ---------- Versjon 48 (Runes spilltest 15. okt) ----------
// Tømmer: seks arbeidere i hogsten.
NODES.timber.cap = 6;
// Oppgraderinger: minst prisen på uniten, og dyrere for hvert nivå.
(() => {
  const ec0 = new Econ(), MUL = [1, 1.4, 1.8];
  for (const k in UPGRADES) {
    const T = TYPES[k]; if (!T || T.side !== 'p' || !(T.cost > 0) || !Array.isArray(UPGRADES[k])) continue;
    const p = ec0.unitPrice(T);
    UPGRADES[k].forEach((u, i) => {
      const m = MUL[i] || MUL[MUL.length - 1], c = u.cost || (u.cost = {});
      c.gold = Math.max(c.gold || 0, Math.round(p.gold * m));
      if (p.iron) c.iron = Math.max(c.iron || 0, Math.round(p.iron * m));
      if (p.coal) c.coal = Math.max(c.coal || 0, Math.round(p.coal * m));
    });
  }
})();
"""

def apply(s):
    a = s.index("const WAVES = [\n") + len("const WAVES = [\n")
    b = s.index("].map((w, i) => Object.assign(w, { n: i + 1", a)
    old = s[a:b]
    assert "\n".join(waves30.js(*w) for w in waves30.W) in old, 'wave list moved'
    new = pure(waves30.W)
    s = s[:a] + "  // Versjon 48: bare den nye arten i hver wave (Rune).\n" + "\n".join(waves30.js(*w) for w in new) + "\n" + s[b:]
    s = sub(s, "    if (!u.atGate && !u.T.flies && this._engage(u, players, attackers, dt, u.T.aggro)) return;\n",
               "    if (!u.atGate && !u.T.flies && this._engage(u, players, attackers, dt, u.T.aggro)) return;\n"
               "    // Versjon 48: står noen av dine ute på slagmarken, går fienden etter dem i stedet for porten.\n"
               "    if (!u.atGate && !u.T.flies && this.gateHp > 0) { const field = players.filter(p => p.order !== 'warden' && p.z < MAP.gateZ - 1); if (field.length && this._engage(u, field, attackers, dt, 80)) return; }\n")
    s = sub(s, "// ===== The Last Flame — musikk", LOGIC + "\n// ===== The Last Flame — musikk")
    return s
