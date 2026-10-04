"""Tier buttons above «Plass i hæren» (4 Oct 2026): Tier 1–5 as a row of buttons that open and close each tier in the army
list. Only Tier 1 is open at the start; closed tiers take no room. Applied by build_v2.py after tier_cap.py."""
from patch import sub

CSS = """
.tierchips { display: flex; gap: 4px; flex-wrap: wrap; margin: 0 0 8px; }
.tierchips button { flex: 1 1 0; min-width: 0; background: var(--panel-2); border: 1px solid var(--line); border-radius: 999px; padding: 5px 4px; font-size: 12px; font-weight: 600; color: var(--muted); display: flex; flex-direction: column; align-items: center; line-height: 1.15; }
.tierchips button small { font-size: 9.5px; font-weight: 500; opacity: .85; }
.tierchips button.on { border-color: var(--flame); color: var(--flame); background: #2a2012; }
"""

def apply(s):
    s = sub(s, "collapsed: new Set([5])", "collapsed: new Set([2, 3, 4, 5])")
    s = sub(s, '<div class="supply" id="supply"></div>', '<div class="tierchips" id="tierchips"></div>\n        <div class="supply" id="supply"></div>')
    s = sub(s, "    $('#palette').innerHTML = ROSTER.map(tier => {",
               "    $('#tierchips').innerHTML = ROSTER.map(t => { const on = !state.collapsed.has(t.tier), capInfo = t.units && !ec.unitUnlocked(t.units[0]) ? `${tierCount(t.tier)}/${TIER_CAP}` : !t.units ? 'kommer' : 'åpen';\n"
               "      return `<button type=\"button\" class=\"${on ? 'on' : ''}\" data-tier=\"${t.tier}\" aria-pressed=\"${on}\">Tier ${t.tier}<small>${capInfo}</small></button>`; }).join('');\n"
               "    $('#palette').innerHTML = ROSTER.map(tier => {")
    s = sub(s, "      if (!tier.units) return `<section class=\"tier future\">", "      if (!open) return '';   // lukket tier tar ingen plass; knappene over åpner den\n      if (!tier.units) return `<section class=\"tier future\">")
    s = sub(s, "#om-remove { color: #f0a59d; }", "#om-remove { color: #f0a59d; }" + CSS)
    return s
