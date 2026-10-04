"""Order bar shows the selected unit (4 Oct 2026): a small portrait, what the next upgrade improves (HP 280 → 350 (+70) …),
and value numbers: gold per damage per second and gold per HP counting armor. Armor removes that many points from every hit
(minimum 1); "HP with armor" uses an average enemy hit of 20 as reference. Applied by build_v2.py."""
from patch import sub

CSS = """
.om-info { flex: 1 1 100%; display: grid; grid-template-columns: 92px minmax(0, 1fr); gap: 10px; align-items: start; border-top: 1px solid var(--line); padding-top: 8px; }
.oi-card { display: flex; flex-direction: column; align-items: center; gap: 3px; text-align: center; }
.oi-card img { width: 64px; height: 64px; border-radius: 9px; border: 1px solid var(--line); background: radial-gradient(circle at 50% 35%, #2c3646, #12161e); }
.oi-card b { font-family: var(--display); font-size: 13px; letter-spacing: .02em; }
.oi-card span { font-size: 11px; color: var(--muted); }
.oi-tab { width: 100%; border-collapse: collapse; font-size: 12px; }
.oi-tab th { font-weight: 500; color: var(--muted); text-align: right; padding: 0 0 3px 8px; border-bottom: 1px solid var(--line); font-size: 11px; }
.oi-tab th:first-child { text-align: left; padding-left: 0; }
.oi-tab td { text-align: right; padding: 2px 0 2px 8px; font-family: var(--mono); border: 0; white-space: nowrap; }
.oi-tab td:first-child { text-align: left; padding-left: 0; font-family: var(--body); color: var(--muted); }
.oi-tab td i { font-style: normal; color: var(--good); font-size: 11px; margin-left: 3px; }
.oi-tab td i.worse { color: #f0a59d; }
.oi-tab td i.neutral { color: var(--muted); }
.oi-tab tr.val td i.worse { color: #f0a59d; }
.oi-tab tr.sep td { border-top: 1px solid var(--line); padding-top: 4px; }
.oi-tab tr.val td:not(:first-child) { color: #f1cf7a; }
.oi-note { grid-column: 1 / -1; font-size: 11.5px; color: var(--muted); margin: 0; }
/* Ordre ligger bak én knapp, så linjen er ryddig. */
.ordermenu:not(.ord-open) #om-orders, .ordermenu:not(.ord-open) .om-tog, .ordermenu:not(.ord-open) .om-dl { display: none !important; }
#om-ordtog { color: var(--fg); }
.ordermenu.ord-open #om-ordtog { border-color: var(--flame); color: var(--flame); }
@media (max-width: 600px) { .om-info { grid-template-columns: 76px minmax(0, 1fr); } .oi-card img { width: 52px; height: 52px; } }
"""

UI = r"""
  // ---------- Valgt unit: bilde, hva neste oppgradering gir, og verdi for pengene ----------
  const ARMOR_REF = 20;   // et vanlig fiendeslag; rustning trekkes fra hvert slag, minst 1 skade går gjennom
  const ehp = T => Math.round(T.hp * ARMOR_REF / Math.max(1, ARMOR_REF - T.armor));
  const goldOf = (k, lvl) => { const p = state.econ.unitPrice(TYPES[k]), up = upgradeSpent(k, lvl || 0); const g = r => (p[r] || 0) + (up[r] || 0); return g('gold') + 2 * g('iron') + 2 * g('coal'); };
  function renderSelInfo() {
    const el = $('#om-info'); if (!el) return;
    const list = [...state.selection].map(i => state.army[i]).filter(Boolean);
    // Ordreknappen viser hvilken ordre de valgte har.
    const ords = new Set(list.map(a => a.order)), tog = $('#om-ordtog');
    if (tog) tog.textContent = `Ordre: ${ords.size === 1 ? ORDERS[[...ords][0]].name : 'blandet'} ${menu.classList.contains('ord-open') ? '▾' : '▸'}`;
    const one = list.length && list.every(a => a.type === list[0].type && (a.level || 0) === (list[0].level || 0));
    if (!one) { el.innerHTML = `<p class="oi-note">${list.length ? 'Velg én type på samme nivå for å se tallene.' : ''}</p>`; return; }
    const k = list[0].type, lvl = list[0].level || 0, base = state.econ.types(TYPES)[k];
    const now = levelType(base, k, lvl), next = UPGRADES[k] && lvl < MAX_LEVEL ? levelType(base, k, lvl + 1) : null;
    const dps = T => T.dmg / T.interval * (T.cleave ? 1 + (T.sweep || 1) * 0.5 : 1);
    const nb = x => String(Math.round(x * 10) / 10).replace('.', ',');
    // Én rad per egenskap: nå, og etter neste oppgradering med endringen. lowGood = lavere er bedre (verdi-radene).
    const row = (label, f, cls, lowGood = false) => {
      const a = f(now, lvl), b = next ? f(next, lvl + 1) : null, d = b == null ? 0 : Math.round((b - a) * 10) / 10;
      const better = lowGood ? d < 0 : d > 0;
      return `<tr class="${cls || ''}"><td>${label}</td><td>${nb(a)}</td>${next ? `<td>${nb(b)}${d ? `<i class="${lowGood == null ? 'neutral' : better ? '' : 'worse'}">${d > 0 ? '+' : ''}${nb(d)}</i>` : ''}</td>` : ''}</tr>`;
    };
    const rows = [row('HP', T => T.hp), row('Skade/s', T => dps(T)), row('Rustning', T => T.armor), row('HP m/rustning', T => ehp(T))];
    if (now.ranged) rows.push(row('Rekkevidde', T => T.range));
    rows.push(row('Gull brukt', (T, l) => goldOf(k, l), 'sep', null));
    rows.push(row('Gull per skade/s', (T, l) => goldOf(k, l) / Math.max(0.1, dps(T)), 'val', true));
    rows.push(row('Gull per 100 HP', (T, l) => goldOf(k, l) / ehp(T) * 100, 'val', true));
    const pips = Array.from({ length: MAX_LEVEL }, (_, i) => i < lvl ? '◆' : '◇').join('');
    el.innerHTML = `<div class="oi-card"><img alt="" src="${portraits[k] || ''}"><b>${TYPES[k].name}</b><span>Nivå ${lvl}/${MAX_LEVEL} ${pips}</span></div>
      <table class="oi-tab"><thead><tr><th></th><th>Nå</th>${next ? '<th>Etter oppgr.</th>' : ''}</tr></thead><tbody>${rows.join('')}</tbody></table>
      <p class="oi-note">Gull-radene: lavere er bedre. ${tipIcon(`Jern og kull teller som 2 gull. Rustning trekkes fra hvert slag, men minst 1 skade går gjennom. «HP m/rustning» regner med et vanlig fiendeslag på ${ARMOR_REF}: rustning 5 gir 15 skade per slag, så uniten tåler 20/15 = 1,33 ganger så mye.`)}</p>`;
  }
"""

def apply(s):
    s = sub(s, "#om-remove { color: #f0a59d; }", "#om-remove { color: #f0a59d; }" + CSS)
    s = sub(s, '<div class="om-orders" id="om-orders"></div>', '<div class="om-info" id="om-info"></div>\n      <div class="om-orders" id="om-orders"></div>')
    s = sub(s, "    syncUpgradeBtn();\n", "    syncUpgradeBtn(); renderSelInfo();\n")
    s = sub(s, "  // ---------- 1 mot 1: Send-fanen ----------", UI + "\n  // ---------- 1 mot 1: Send-fanen ----------")
    # Ordreknappene, «Gå samlet» og venting ligger bak én knapp.
    s = sub(s, '<label class="om-tog"><input type="checkbox" id="om-together" checked> Gå samlet</label>',
               '<button type="button" id="om-ordtog">Ordre ▸</button><label class="om-tog"><input type="checkbox" id="om-together" checked> Gå samlet</label>')
    s = sub(s, "    $('#om-upbtn').onclick = upgradeSelected;", "    $('#om-upbtn').onclick = upgradeSelected;\n    $('#om-ordtog').onclick = () => { menu.classList.toggle('ord-open'); renderSelInfo(); };")
    return s
