"""Scarcer economy (version 22, 6 Oct 2026). Rune maxed every mine by wave 10 and never ran short of iron or coal.
Numbers live in economy.json under "scarce". Applied by build_v2.py last.
- After the first few, each worker on a mine costs more than the one before (base + step × workers past the free ones). Iron and coal workers
  are much dearer, and those mines have fewer places.
- Expanding a mine (+3 places) needs a Barracks level: gold, timber and stone need Barracks II, iron Barracks III,
  coal Barracks IV.
- Iron and coal matter more the higher the tier: Tier 2–4 units and all unit upgrades need several times more of them.
- Barracks IV and V need about half the timber and stone they did (iron and coal are now the hard part)."""
import json
from pathlib import Path
from patch import sub

C = json.loads((Path(__file__).parent / 'economy.json').read_text())['scarce']

LOGIC = """
// ===== Knapphet (versjon 22): dyrere arbeidere, utvidelse krever Barracks, jern og kull teller mer i høye tiers =====
const SCARCE = __CFG__;
(() => {
  for (const k in SCARCE.cap) NODES[k].cap = SCARCE.cap[k];
  for (const k in TYPES) {
    const t = TYPES[k]; if (t.side !== 'p' || !t.tier || t.tier < 2) continue;
    const mi = SCARCE.unitIron[t.tier], mc = SCARCE.unitCoal[t.tier], c0 = SCARCE.unitCoalMin[t.tier];
    if (mi) t.iron = Math.round((t.iron || 1) * mi);
    if (mc) t.coal = Math.round(Math.max(t.coal || 0, c0 || 0) * mc) || undefined;
  }
  for (const k in UPGRADES) for (const u of UPGRADES[k]) {
    if (u.cost.iron) u.cost.iron = Math.round(u.cost.iron * SCARCE.upgradeIron);
    if (u.cost.coal) u.cost.coal = Math.round(u.cost.coal * SCARCE.upgradeCoal);
  }
  for (const i in SCARCE.barracksWood) { const c = BARRACKS[i].cost; ['timber', 'stone'].forEach(r => { if (c[r]) c[r] = Math.round(c[r] * SCARCE.barracksWood[i]); }); }
})();
const expandNeeds = k => SCARCE.expand[k].needs;
"""

def apply(s):
    s = sub(s, "if (typeof module !== 'undefined') module.exports = { supplyOf, WARDEN_GEAR,", LOGIC.replace('__CFG__', json.dumps(C)) + "\nif (typeof module !== 'undefined') module.exports = { supplyOf, WARDEN_GEAR,")
    s = sub(s, "  workerPrice(k) { const w = k ? this.nodes[k].workers : 0; return WORKER_BASE + Math.max(0, w + 1 - WORKER_FREE) * WORKER_STEP; }",
               "  // Hver arbeider på samme sted koster mer enn den forrige. Jern og kull er dyrest.\n"
               "  workerPrice(k) { const c = SCARCE.worker[k || 'gold']; return c[0] + Math.max(0, (k ? this.nodes[k].workers : 0) - c[2]) * c[1]; }")
    s = sub(s, "  expandNode(k) { const n = this.nodes[k]; if (!n.unlocked || n.expanded || !this.pay(NODE_EXPAND.cost)) return false; n.expanded = true; return true; }",
               "  expandNode(k) { const n = this.nodes[k]; if (!n.unlocked || n.expanded || this.barracks < expandNeeds(k) || !this.pay(SCARCE.expand[k].cost)) return false; n.expanded = true; return true; }")
    s = sub(s, "    if (!n.expanded) extras.push(buyBtn(`+${NODE_EXPAND.extra} plasser`, NODE_EXPAND.cost, 'expand',",
               "    if (!n.expanded && ec.barracks < expandNeeds(k)) extras.push(`<span class=\"maxed\" data-tip=\"Flere plasser i ${N.name.toLowerCase()} krever ${BARRACKS[expandNeeds(k)].name}\">+${NODE_EXPAND.extra} plasser: ${BARRACKS[expandNeeds(k)].name}</span>`);\n"
               "    else if (!n.expanded) extras.push(buyBtn(`+${NODE_EXPAND.extra} plasser`, SCARCE.expand[k].cost, 'expand',")
    # Neste arbeiders pris står på pluss-knappen.
    s = sub(s, "        <button type=\"button\" class=\"step\" data-act=\"worker+\" data-k=\"${k}\" aria-label=\"Legg til arbeider i ${N.name}\">+</button></div></div>`;",
               "        <button type=\"button\" class=\"step\" data-act=\"worker+\" data-k=\"${k}\" aria-label=\"Legg til arbeider i ${N.name}\" data-tip=\"Neste arbeider: ${ec.idle ? 'ledig arbeider, gratis' : ec.workerPrice(k) + ' gull'}\">+</button></div></div>`;")
    # Langhuset viste én fast arbeiderpris. Nå koster arbeidere forskjellig fra sted til sted.
    s = sub(s, "· ${icon('gold', 12)}${WORKER_BASE} per arbeider</small></h3>",
               "· <span data-tip=\"Hver arbeider på samme sted koster mer enn den forrige. Jern og kull er dyrest.\">arbeidere fra ${icon('gold', 12)}${WORKER_BASE}</span></small></h3>")
    s = sub(s, "<span class=\"maxed\" data-tip=\"Flere plasser i ${N.name.toLowerCase()} krever", "<span class=\"maxed needs\" data-tip=\"Flere plasser i ${N.name.toLowerCase()} krever")
    s = sub(s, ".maxed { font-size: 12px; color: var(--good); }", ".maxed { font-size: 12px; color: var(--good); }\n.maxed.needs { color: var(--muted); }\n.wprice { font-size: 11.5px; color: var(--muted); }")
    # Prisen på neste arbeider under inntekten.
    s = sub(s, "${icon(N.res, 14)} +${Math.round(n.workers * ec.perWorkerMinute(k))}/min</span>",
               "${icon(N.res, 14)} +${Math.round(n.workers * ec.perWorkerMinute(k))}/min</span>\n        ${n.workers < ec.cap(k) ? `<span class=\"wprice\">Neste arbeider: ${ec.idle ? 'ledig, gratis' : `${icon('gold', 11)}${ec.workerPrice(k)}`}</span>` : ''}")
    return s
