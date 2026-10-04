"""Order bar shows the selected unit (4 Oct 2026): a small portrait, what the next upgrade improves (HP 280 → 350 (+70) …),
and value numbers: gold per damage per second and gold per HP counting armor. Armor removes that many points from every hit
(minimum 1); "HP with armor" uses an average enemy hit of 20 as reference. Applied by build_v2.py."""
from patch import sub

CSS = """
.om-info { flex: 1 1 100%; display: grid; grid-template-columns: 56px minmax(0, 1fr); gap: 4px 10px; align-items: start; border-top: 1px solid var(--line); padding-top: 8px; }
.om-info img { width: 56px; height: 56px; border-radius: 8px; border: 1px solid var(--line); background: radial-gradient(circle at 50% 35%, #2c3646, #12161e); grid-row: span 2; }
.om-info .oi-rows { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1px 12px; font-size: 12px; }
.om-info .oi-rows span { display: flex; justify-content: space-between; gap: 6px; color: var(--muted); white-space: nowrap; }
.om-info .oi-rows b { color: var(--fg); font-family: var(--mono); font-weight: 500; }
.om-info .oi-rows i { font-style: normal; color: var(--good); font-family: var(--mono); }
.om-info .oi-val { font-size: 11.5px; color: var(--muted); }
.om-info .oi-val b { color: #f1cf7a; font-family: var(--mono); font-weight: 500; }
.om-info .oi-note { grid-column: 1 / -1; font-size: 11.5px; color: var(--muted); }
@media (max-width: 600px) { .om-info { grid-template-columns: 44px minmax(0, 1fr); } .om-info img { width: 44px; height: 44px; } .om-info .oi-rows { grid-template-columns: minmax(0, 1fr); gap: 1px; } }
"""

UI = r"""
  // ---------- Valgt unit: bilde, hva neste oppgradering gir, og verdi for pengene ----------
  const ARMOR_REF = 20;   // et vanlig fiendeslag; rustning trekkes fra hvert slag, minst 1 skade går gjennom
  const ehp = T => Math.round(T.hp * ARMOR_REF / Math.max(1, ARMOR_REF - T.armor));
  const goldOf = (k, lvl) => { const p = state.econ.unitPrice(TYPES[k]), up = upgradeSpent(k, lvl || 0); const g = r => (p[r] || 0) + (up[r] || 0); return g('gold') + 2 * g('iron') + 2 * g('coal'); };
  function renderSelInfo() {
    const el = $('#om-info'); if (!el) return;
    const list = [...state.selection].map(i => state.army[i]).filter(Boolean);
    const one = list.length && list.every(a => a.type === list[0].type && (a.level || 0) === (list[0].level || 0));
    if (!one) { el.innerHTML = `<p class="oi-note">${list.length ? 'Velg én type på samme nivå for å se tallene.' : ''}</p>`; return; }
    const k = list[0].type, lvl = list[0].level || 0, base = state.econ.types(TYPES)[k];
    const now = levelType(base, k, lvl), next = UPGRADES[k] && lvl < MAX_LEVEL ? levelType(base, k, lvl + 1) : null;
    const dps = T => T.dmg / T.interval * (T.cleave ? 1 + (T.sweep || 1) * 0.5 : 1);
    const row = (label, a, b, f) => { const fa = f(a), fb = b == null ? null : f(b), d = fb == null ? 0 : +(fb - fa).toFixed(1);
      return `<span>${label}<b>${String(fa).replace('.', ',')}${fb != null && d ? ` → ${String(fb).replace('.', ',')}` : ''}${d ? ` <i>(${d > 0 ? '+' : ''}${String(d).replace('.', ',')})</i>` : ''}</b></span>`; };
    const r1 = x => Math.round(x * 10) / 10, nb = x => String(r1(x)).replace('.', ',');
    const rows = [row('HP', now, next, T => T.hp), row('Skade/s', now, next, T => r1(dps(T))), row('Rustning', now, next, T => T.armor)];
    if (now.ranged) rows.push(row('Rekkevidde', now, next, T => T.range));
    else rows.push(row('HP m/rustning', now, next, T => ehp(T)));
    const g = goldOf(k, lvl), gn = next ? goldOf(k, lvl + 1) : null;
    const val = (gold, T) => `<b>${nb(gold / Math.max(0.1, dps(T)))}</b> gull per skade/s · <b>${nb(gold / ehp(T) * 100)}</b> gull per 100 HP m/rustning`;
    el.innerHTML = `<img alt="" src="${portraits[k] || ''}"><div class="oi-rows">${rows.join('')}</div>
      <div class="oi-val">Verdi nå (${g} gull brukt): ${val(g, now)}${next ? `<br>Etter oppgradering (${gn} gull): ${val(gn, next)}` : ''} ${tipIcon(`Lavere er bedre. Jern og kull teller som 2 gull. Rustning trekkes fra hvert slag (minst 1 skade går gjennom); HP med rustning regner med et vanlig fiendeslag på ${ARMOR_REF}.`)}</div>`;
  }
"""

def apply(s):
    s = sub(s, "#om-remove { color: #f0a59d; }", "#om-remove { color: #f0a59d; }" + CSS)
    s = sub(s, '<div class="om-orders" id="om-orders"></div>', '<div class="om-info" id="om-info"></div>\n      <div class="om-orders" id="om-orders"></div>')
    s = sub(s, "    syncUpgradeBtn();\n", "    syncUpgradeBtn(); renderSelInfo();\n")
    s = sub(s, "  // ---------- 1 mot 1: Send-fanen ----------", UI + "\n  // ---------- 1 mot 1: Send-fanen ----------")
    return s
