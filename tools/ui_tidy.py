"""Smaller selection panel and partial upgrades (10 Oct 2026, Rune's feedback on version 26).
- The selection panel opens compact: a small portrait, name, level and HP / damage / armour with what the next upgrade adds.
  The full number table is behind a «Tall» button. An X closes the panel, and a tap outside it closes it too.
- «Oppgrader» with many units selected upgrades as many as you can afford (cheapest first), not all or nothing.
- The hero card in Heltehallen no longer squeezes its text into a thin column.
Applied by build_v2.py after hero.py."""
from patch import sub

CSS = """
/* Kompakt valgpanel (versjon 27): tabellen ligger bak «Tall», X lukker. */
.ordermenu { width: min(520px, calc(100% - 24px)); padding: 8px 10px; gap: 6px; }
.om-x { position: absolute; top: 4px; right: 6px; background: none; border: 0; color: var(--muted); font-size: 22px; line-height: 1; padding: 2px 8px; z-index: 1; }
.om-x:hover { color: var(--fg); }
.om-head { padding-right: 30px; }
#om-cancel { display: none; }
.oi-line { display: none; font-family: var(--mono); font-size: 12px; color: var(--fg); }
.oi-line i { font-style: normal; color: var(--good); font-size: 11px; margin-left: 2px; }
.ordermenu:not(.num-open) .om-info { grid-template-columns: minmax(0, 1fr); padding-top: 6px; }
.ordermenu:not(.num-open) .oi-card { flex-direction: row; align-items: center; gap: 8px; text-align: left; flex-wrap: wrap; }
.ordermenu:not(.num-open) .oi-card img { width: 40px; height: 40px; border-radius: 7px; }
.ordermenu:not(.num-open) .oi-tab, .ordermenu:not(.num-open) .oi-note { display: none; }
.ordermenu:not(.num-open) .oi-line { display: block; flex: 1 1 100%; }
.oi-card .oi-nm { display: flex; flex-direction: column; gap: 0; }
#om-numtog { color: var(--fg); }
.ordermenu.num-open #om-numtog { border-color: var(--flame); color: var(--flame); }
.om-up { padding-top: 6px; }
.om-up button { padding: 6px 10px; }
.om-up span { font-size: 11.5px; }
@media (max-width: 600px) { .ordermenu { max-height: 45vh; padding: 6px 8px calc(6px + env(safe-area-inset-bottom, 0px)); } .ordermenu:not(.num-open) .oi-line { flex: 1 1 0; min-width: 0; } }
/* Heltekortet: knappen under teksten når det er trangt. */
.herostrip { flex-wrap: wrap; }
.herostrip .hs-mid { flex: 1 1 160px; }
.herostrip .hs-fallen { color: #f0a59d; }
.herostrip > .buy, .herostrip > .hs-go { margin-left: auto; }
"""

PLAN = """  // Oppgradering av valgte units: hver får sitt neste nivå. Har du ikke råd til alle, oppgraderes så mange du har råd til, billigste først.
  function upgradePlan() {
    const list = [...state.selection].map(i => state.army[i]).filter(a => a && UPGRADES[a.type] && (a.level || 0) < MAX_LEVEL);
    const costOf = a => UPGRADES[a.type][a.level || 0].cost, worth = c => (c.gold || 0) + (c.timber || 0) / 2 + (c.stone || 0) / 2 + 2 * (c.iron || 0) + 2 * (c.coal || 0);
    const add = (t, c) => { for (const r in c) t[r] = (t[r] || 0) + c[r]; return t; };
    const full = list.reduce((t, a) => add(t, costOf(a)), {});
    const left = { ...state.econ.res }, pick = [], cost = {};
    [...list].sort((a, b) => worth(costOf(a)) - worth(costOf(b))).forEach(a => {
      const c = costOf(a); if (Object.keys(c).every(r => (left[r] || 0) >= c[r])) { for (const r in c) left[r] -= c[r]; add(cost, c); pick.push(a); }
    });
    const cheapest = list.length ? list.map(costOf).sort((a, b) => worth(a) - worth(b))[0] : {};
    return { list, pick, cost: pick.length ? cost : full, cheapest };
  }
  function syncUpgradeBtn() {
    const btn = $('#om-upbtn'), desc = $('#om-updesc'), { list, pick, cost } = upgradePlan();
    if (!list.length) { btn.disabled = true; btn.textContent = 'Fullt oppgradert'; desc.textContent = 'Alle valgte har nådd nivå 3.'; return; }
    btn.disabled = false;
    const one = list.length === 1 || list.every(a => a.type === list[0].type && (a.level || 0) === (list[0].level || 0));
    const up = UPGRADES[list[0].type][list[0].level || 0], part = pick.length && pick.length < list.length;
    btn.innerHTML = `${part ? `Oppgrader ${pick.length} av ${list.length}` : one && list.length === 1 ? `Oppgrader: ${up.name}` : `Oppgrader ${list.length}${one ? ` · ${up.name}` : ' units'}`} <span class="cost">${costHtml(cost)}</span>`;
    btn.classList.toggle('cant', !pick.length);
    desc.textContent = part ? `Du har råd til ${pick.length} av ${list.length} nå (billigste først). ${one ? up.desc : ''}`
      : one ? `Nivå ${(list[0].level || 0) + 1} av 3${list.length > 1 ? ` for ${list.length} ${TYPES[list[0].type].name}` : ''}. ${up.desc}` : 'Hver valgt unit får sitt neste nivå.';
  }
  function costHtml(c) { return Object.keys(c).map(r => `${icon(r, 13)}${c[r]}`).join(' '); }
  function upgradeSelected() {
    const { list, pick, cost, cheapest } = upgradePlan();
    if (!list.length) return;
    if (!pick.length) { explainMissing(cheapest); return; }
    state.econ.pay(cost);
    const first = pick[0], name = UPGRADES[first.type][first.level || 0].name;
    pick.forEach(a => { a.level = (a.level || 0) + 1; });
    toast(pick.length === 1 && list.length === 1 ? `${TYPES[first.type].name} fikk ${name}.` : pick.length < list.length ? `${pick.length} av ${list.length} ble oppgradert. Resten når du har råd.` : `${pick.length} units ble oppgradert.`);
    sfx('coin');
    rebuild(); selectionChanged();
  }
"""


def apply(s):
    s = sub(s, "@media (max-width: 600px) { .om-info { grid-template-columns: 76px minmax(0, 1fr); } .oi-card img { width: 52px; height: 52px; } }\n",
               "@media (max-width: 600px) { .om-info { grid-template-columns: 76px minmax(0, 1fr); } .oi-card img { width: 52px; height: 52px; } }\n" + CSS)
    # X i hjørnet, «Tall»-knapp ved siden av «Ordre».
    s = sub(s, '<div class="om-head"><b id="om-title">0 valgt</b>',
               '<button type="button" class="om-x" id="om-x" aria-label="Lukk">×</button>\n      <div class="om-head"><b id="om-title">0 valgt</b>')
    s = sub(s, '<button type="button" id="om-ordtog">Ordre ▸</button>', '<button type="button" id="om-numtog">Tall ▸</button><button type="button" id="om-ordtog">Ordre ▸</button>')
    s = sub(s, "    $('#om-cancel').onclick = () => clearSelection();",
               "    $('#om-cancel').onclick = () => clearSelection();\n"
               "    $('#om-x').onclick = () => clearSelection();\n"
               "    $('#om-numtog').onclick = () => { menu.classList.toggle('num-open'); $('#om-numtog').textContent = `Tall ${menu.classList.contains('num-open') ? '▾' : '▸'}`; };\n"
               "    // Trykk utenfor panelet lukker det (kartet håndterer egne trykk; sidepanelet og kort lar det stå).\n"
               "    document.addEventListener('pointerdown', e => {\n"
               "      if (menu.hidden || menu.contains(e.target) || canvas.contains(e.target) || e.target.closest('.panel, .choicecard, .arenacard, .bpop, .ustat, #minimap')) return;\n"
               "      clearSelection();\n"
               "    }, true);")
    # I kamp lukker et trykk på kartet også panelet (i byggefasen gjør klikket på tom bakke det allerede).
    s = sub(s, "      else clickSelect(c, e.shiftKey || e.ctrlKey || e.metaKey);\n    }\n",
               "      else clickSelect(c, e.shiftKey || e.ctrlKey || e.metaKey);\n    } else if (drag && !drag.moved && pointers.size === 1 && drag.button === 0 && state.selection.size) clearSelection();\n")
    # Kompakt linje i bildekortet: HP, skade og rustning, med det neste oppgradering gir.
    s = sub(s, "    const pips = Array.from({ length: MAX_LEVEL }, (_, i) => i < lvl ? '◆' : '◇').join('');\n    el.innerHTML = `<div class=\"oi-card\"><img alt=\"\" src=\"${portraits[k] || ''}\"><b>${TYPES[k].name}</b><span>${TYPES[k].hero ? `Helt · nivå ${state.econ.heroLevel()}` : `Nivå ${lvl}/${MAX_LEVEL} ${pips}`}</span></div>",
               "    const pips = Array.from({ length: MAX_LEVEL }, (_, i) => i < lvl ? '◆' : '◇').join('');\n"
               "    const q = (ic, f) => { const a = f(now), d = next ? Math.round((f(next) - a) * 10) / 10 : 0; return `${ic} ${nb(a)}${d > 0 ? `<i>+${nb(d)}</i>` : ''}`; };\n"
               "    const line = [q('❤', T => T.hp), q('⚔', dps), q('⛨', T => T.armor)].concat(now.ranged ? [q('➶', T => T.range)] : []).join(' · ');\n"
               "    el.innerHTML = `<div class=\"oi-card\"><img alt=\"\" src=\"${portraits[k] || ''}\"><span class=\"oi-nm\"><b>${TYPES[k].name}</b><span>${TYPES[k].hero ? `Helt · nivå ${state.econ.heroLevel()}` : `Nivå ${lvl}/${MAX_LEVEL} ${pips}`}</span></span><span class=\"oi-line\">${line}${next ? ' <small style=\"color:var(--muted)\">(grønt = neste nivå)</small>' : ''}</span></div>")
    # Delvis oppgradering.
    a = s.index("  // Oppgradering av valgte units: hver får sitt neste nivå. Prisen er summen for alle som kan oppgraderes.\n")
    b = s.index("  function clearSelection(silent) {", a)
    s = s[:a] + PLAN + s[b:]
    # Heltekortet: merknaden og knappen inne i kortet (før lukket kortet seg for tidlig og presset teksten).
    s = sub(s, "<div class=\"chips\">${h.path ? `<span class=\"path\">${HERO_PATHS[h.path].name}</span>` : ''}${h.talents.map(id => `<span data-tip=\"${HERO_TALENTS[id].desc}\">${HERO_TALENTS[id].name}</span>`).join('')}</div>` : ''}</div>\n      ${h.fallen ? `<small style=\"color:#f0a59d\">Falt i kamp. Gjenopplives for å kjempe igjen.</small>` : ''}</div>",
               "<div class=\"chips\">${h.path ? `<span class=\"path\">${HERO_PATHS[h.path].name}</span>` : ''}${h.talents.map(id => `<span data-tip=\"${HERO_TALENTS[id].desc}\">${HERO_TALENTS[id].name}</span>`).join('')}</div>` : ''}\n      ${h.fallen ? `<small class=\"hs-fallen\">Falt i kamp. Gjenopplives for å kjempe igjen.</small>` : ''}</div>")
    s = sub(s, "Din egen helt. Han tar ingen plass i hæren, kommer tilbake hver wave og får erfaring av fiender han dreper.",
               "Din egen helt. Han tar ingen plass i hæren og får erfaring av fiender han dreper. Faller han, mister han litt erfaring og må gjenopplives for gull.")
    return s
