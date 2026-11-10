# Info-bokser på mobil (versjon 37). På telefon kom boblene og enhetskortene fram ved trykk (falsk «mus over»),
# men lukket seg aldri. Nå: trykk viser, nytt trykk hvor som helst lukker, og de forsvinner selv etter 6 s.
from patch import sub

def apply(s):
    s = sub(s, "  $('.panel').addEventListener('mouseover', e => {\n    const c = e.target.closest('.ucard[data-unit]');\n    if (c && !ustatPinned)",
               "  $('.panel').addEventListener('mouseover', e => {\n    const c = e.target.closest('.ucard[data-unit]');\n    if (c && !ustatPinned && !touchUi)")
    s = sub(s, "  document.addEventListener('mouseover', e => { const t = e.target.closest && e.target.closest('[data-tip]'); if (t) showTip(t); else tipEl.hidden = true; });\n  document.addEventListener('focusin', e => { const t",
               "  document.addEventListener('mouseover', e => { if (touchUi) return; const t = e.target.closest && e.target.closest('[data-tip]'); if (t) showTip(t); else tipEl.hidden = true; });\n  document.addEventListener('focusin', e => { if (touchUi) return; const t")
    s = sub(s, "  const ustat = document.createElement('div');\n",
               """  // Telefon: ingen mus. Ett trykk viser en boble, neste trykk (hvor som helst) lukker den.
  let touchUi = false, tipFor = null, tipT = 0, ustatT = 0;
  document.addEventListener('pointerdown', e => {
    touchUi = e.pointerType === 'touch' || e.pointerType === 'pen';
    if (!touchUi) return;
    const t = e.target.closest && e.target.closest('[data-tip]'), was = tipFor;
    tipEl.hidden = true; tipFor = null; clearTimeout(tipT);
    if (t && t !== was) { showTip(t); tipFor = t; tipT = setTimeout(() => { tipEl.hidden = true; tipFor = null; }, 6000); }
    if (!(e.target.closest && e.target.closest('[data-info]'))) { ustatPinned = null; ustat.hidden = true; }
  }, true);
  const ustat = document.createElement('div');
""")
    # Et festet enhetskort lukker seg også selv på telefon.
    s = sub(s, "      else { ustatPinned = null; showUnitStat(k, info.closest('.ucard')); ustatPinned = k; }",
               "      else { ustatPinned = null; showUnitStat(k, info.closest('.ucard')); ustatPinned = k; if (touchUi) { clearTimeout(ustatT); ustatT = setTimeout(() => { if (ustatPinned === k) { ustatPinned = null; ustat.hidden = true; } }, 8000); } }")
    return s
