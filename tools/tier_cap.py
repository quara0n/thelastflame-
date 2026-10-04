"""All tiers open from the start (4 Oct 2026). Without the Barracks for a tier you may field at most TIER_CAP units of
that tier, at full price. Building that Barracks removes the cap and, as before, gives more army space. Applied by build_v2.py."""
from patch import sub

def apply(s):
    s = sub(s, "  unitUnlocked(type) { for (let i = 0; i <= this.barracks; i++) if (BARRACKS[i].unlocks.includes(type)) return true; return false; }",
        "  // unitUnlocked = Barracks for denne tieren er bygget (ingen grense). Uten den kan man ha TIER_CAP av tieren.\n"
        "  unitUnlocked(type) { for (let i = 0; i <= this.barracks; i++) if (BARRACKS[i].unlocks.includes(type)) return true; return false; }")
    s = sub(s, "const supplyOf = T => (T && T.tier) || 1;", "const supplyOf = T => (T && T.tier) || 1;\nconst TIER_CAP = 2;   // units av en tier man har uten tierens Barracks")
    # Hjelpere i grensesnittet.
    s = sub(s, "  const armySupply = () => state.army.reduce((n, a) => n + supplyOf(TYPES[a.type]), 0);",
        "  const armySupply = () => state.army.reduce((n, a) => n + supplyOf(TYPES[a.type]), 0);\n"
        "  const tierOf = k => TYPES[k].tier || 1;\n"
        "  const tierCount = (t, skip) => state.army.filter(a => a !== skip && tierOf(a.type) === t).length;\n"
        "  // Nådd taket: tieren mangler sin Barracks og hæren har allerede TIER_CAP av den.\n"
        "  const capped = (k, skip) => !state.econ.unitUnlocked(k) && tierCount(tierOf(k), skip) >= TIER_CAP;\n"
        "  const capMsg = k => `Uten ${BARRACKS[tierOf(k) - 1].name} kan du ha maks ${TIER_CAP} Tier ${tierOf(k)}-units. Bygg ${BARRACKS[tierOf(k) - 1].name} for å fjerne taket.`;")
    s = sub(s, "      if (!ec.unitUnlocked(tool)) { toast(`${TYPES[tool].name} er Tier ${TYPES[tool].tier || 2} og krever ${BARRACKS[(TYPES[tool].tier || 2) - 1].name}.`); return; }",
        "      if (capped(tool, ex)) { toast(capMsg(tool)); return; }")
    s = sub(s, "b.classList.toggle('cant', !ec.unitUnlocked(k) || ((", "b.classList.toggle('cant', capped(k) || ((")
    s = sub(s, "${tier.units && !unlocked ? `<em>🔒 ${tier.need}</em>` : ''}",
        "${tier.units && !unlocked ? `<em data-tip=\"Uten ${tier.need} kan du ha maks ${TIER_CAP} av denne tieren. ${tier.need} fjerner taket og gir mer plass i hæren.\">${tierCount(tier.tier)}/${TIER_CAP} · ${tier.need} fjerner taket</em>` : ''}")
    s = sub(s, "return `<section class=\"tier${unlocked ? '' : ' locked'}\">${head}</section>`;", "return `<section class=\"tier\">${head}</section>`;")
    s = sub(s, "return `<section class=\"tier${unlocked ? '' : ' locked'}\">${head}<div class=\"ugrid\">`", "return `<section class=\"tier\">${head}<div class=\"ugrid\">`")
    s = sub(s, "sel = selCounts[k] || 0, locked = !ec.unitUnlocked(k);", "sel = selCounts[k] || 0, locked = capped(k);")
    s = sub(s, "${locked ? `🔒 ${tier.need}` : state.tool === k ? 'Plasserer …' : '+ Plasser'}", "${locked ? `Maks ${TIER_CAP} · ${tier.need}` : state.tool === k ? 'Plasserer …' : '+ Plasser'}")
    s = sub(s, "      if (!state.econ.unitUnlocked(k)) { toast(`${TYPES[k].name} er Tier 2 og krever Barracks II. Klikk Barracks i landsbyen.`); return; }",
        "      if (capped(k)) { toast(capMsg(k)); return; }")
    s = sub(s, "tipIcon('Hvert nivå åpner en ny tier av units og gir mer plass i hæren (30, 45, 60). Bygningen i landsbyen vokser.')",
        "tipIcon('Alle tiers kan kjøpes, men uten riktig Barracks bare 2 av hver høyere tier. Hvert nivå fjerner taket for sin tier og gir mer plass i hæren. Bygningen i landsbyen vokser.')")
    s = sub(s, "tip: 'Nivå I: Tier 1 (Shieldguard, Stormreaver, Ironshot, Longfang). Nivå II: Tier 2 (Ironwall, Frostbrand, Thunderbore, Hearthkeeper). Nivå III–V åpner Tier 3–5 når de er designet.',",
        "tip: 'Nivå II fjerner taket på Tier 2, III på Tier 3, IV på Tier 4. Uten nivået kan du ha 2 av tieren. Hvert nivå gir også mer plass i hæren.',")
    return s
