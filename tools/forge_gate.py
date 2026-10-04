"""Barracks styrer Forge (4 Oct 2026). Hvert Barracks-nivå åpner neste Forge-nivå: nivå 1 er fritt, nivå 2 krever
Barracks II, nivå 3 Barracks III, og et nytt nivå 4 krever Barracks IV. Barracks gir også mer plass i hæren
(20 / 32 / 46 / 62 / 80 i stedet for 20 / 30 / 40 / 50 / 60). Workshop (teknologi) er ikke låst. Applied by build_v2.py."""
from patch import sub

def apply(s):
    # Mer plass i hæren per Barracks-nivå.
    for old, new in [("tier: 2, supply: 30,", "tier: 2, supply: 32,"), ("tier: 3, supply: 40,", "tier: 3, supply: 46,"),
                     ("tier: 4, supply: 50,", "tier: 4, supply: 62,"), ("tier: 5, supply: 60,", "tier: 5, supply: 80,")]:
        s = sub(s, old, new)
    # Fjerde Forge-nivå (krever Barracks IV).
    s = sub(s, "    { name: 'Blacksteel-egg',  val: 0.40, cost: { gold: 42, iron: 28, coal: 10 } } ] },",
        "    { name: 'Blacksteel-egg',  val: 0.40, cost: { gold: 42, iron: 28, coal: 10 } },\n"
        "    { name: 'Runesmidd egg',   val: 0.58, cost: { gold: 64, iron: 42, coal: 22 } } ] },")
    s = sub(s, "    { name: 'Kull-ladning',    val: 0.40, cost: { gold: 42, iron: 28, coal: 10 } } ] },",
        "    { name: 'Kull-ladning',    val: 0.40, cost: { gold: 42, iron: 28, coal: 10 } },\n"
        "    { name: 'Runeladning',     val: 0.58, cost: { gold: 64, iron: 42, coal: 22 } } ] },")
    s = sub(s, "    { name: 'Blacksteel-plater', val: 3, cost: { gold: 39, iron: 30, coal: 10 } } ] },",
        "    { name: 'Blacksteel-plater', val: 3, cost: { gold: 39, iron: 30, coal: 10 } },\n"
        "    { name: 'Runeplater',      val: 4, cost: { gold: 60, iron: 45, coal: 20 } } ] },")
    # Regelen i økonomien (gjelder også boten og rivalen).
    s = sub(s, "  buyTrack(k) { const lv = TRACKS[k].levels[this.up[k]]; if (!lv || !this.pay(lv.cost)) return false; this.up[k]++; return true; }",
        "  // Forge-nivå n (1-basert) krever Barracks-nivå n (Barracks I = 0 her). Workshop er ikke låst.\n"
        "  trackLocked(k) { return TRACKS[k].building === 'Forge' && this.up[k] > this.barracks; }\n"
        "  buyTrack(k) { const lv = TRACKS[k].levels[this.up[k]]; if (!lv || this.trackLocked(k) || !this.pay(lv.cost)) return false; this.up[k]++; return true; }")
    # Grensesnitt: vis låsen på knappen og forklar ved trykk.
    s = sub(s, "      now: trackEffect(k, lv), buy: nx && buyBtn(trackEffect(k, lv + 1), nx.cost, 'track', `data-k=\"${k}\"`) });",
        "      now: trackEffect(k, lv), buy: nx && (state.econ.trackLocked(k)\n"
        "        ? buyBtn(`🔒 ${BARRACKS[lv].name}`, nx.cost, 'track', `data-k=\"${k}\" data-lock=\"forge\" data-need=\"${BARRACKS[lv].name}\"`)\n"
        "        : buyBtn(trackEffect(k, lv + 1), nx.cost, 'track', `data-k=\"${k}\"`)) });")
    s = sub(s, "    if (b.dataset.lock === 'deep') {",
        "    if (b.dataset.lock === 'forge') { toast(`Neste Forge-nivå krever ${b.dataset.need}. Hvert Barracks-nivå åpner ett nytt Forge-nivå.`); return; }\n"
        "    if (b.dataset.lock === 'deep') {")
    s = sub(s, "tipIcon('Våpen og rustning for hele hæren. Krever jern; de høyeste nivåene også kull.')",
        "tipIcon('Våpen og rustning for hele hæren. Nivå 1 er åpent; hvert nytt Barracks-nivå åpner neste Forge-nivå (II → 2, III → 3, IV → 4). Krever jern; de høyeste nivåene også kull.')")
    return s
