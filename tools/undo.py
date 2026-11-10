# Avbryt og Angre (versjon 47). Rune: når en unit er valgt for kjøp og du trykker på en annen unit på kartet,
# ble den byttet ut i stedet for valgt. Han ville ha en lett måte å avbryte på, og en angre-knapp.
# - Med en unit valgt for kjøp: trykk på en unit som allerede står der velger den (og avslutter kjøpet).
#   Den blir ikke lenger byttet ut eller solgt. Vil du bytte: velg unit-en, «Fjern», og plasser den nye.
# - «✕ Shieldguard»-knapp oppe til venstre i spillet så lenge du plasserer: trykk for å avslutte.
#   Høyreklikk og Esc avslutter som før, og et nytt trykk på samme kort i panelet også.
# - «↶ Angre» ved siden av: angrer siste kjøp, salg, bytte eller oppgradering i byggefasen (opptil 20 steg),
#   med full refusjon. Ctrl/Cmd+Z gjør det samme. Tømmes når waven starter. Har du brukt gullet du fikk
#   for et salg, kan salget ikke angres før du har råd.
from patch import sub

CSS = """
/* Avbryt og Angre (versjon 47). */
.undobar { position: absolute; left: 12px; top: 84px; z-index: 5; display: flex; gap: 6px; pointer-events: none; }
.undobar button { pointer-events: auto; background: rgba(11, 14, 20, .86); border: 1px solid var(--line); border-radius: 999px; color: var(--fg);
  padding: 6px 12px; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px; box-shadow: 0 3px 10px rgba(0, 0, 0, .4); cursor: pointer; touch-action: manipulation; }
.undobar button[hidden] { display: none; }
.undobar #ub-cancel { border-color: rgba(226, 181, 74, .7); color: #ecc970; }
.undobar #ub-cancel b { font-size: 16px; line-height: 1; }
@media (max-width: 600px) {
  .undobar { left: 6px; top: 38px; gap: 5px; }
  .undobar button { padding: 6px 11px; font-size: 12px; }
}
"""

HTML_OLD = '    <div class="selbox" id="selbox" hidden></div>'
HTML_NEW = ('    <div class="undobar"><button type="button" id="ub-cancel" hidden><b>✕</b><span></span></button>'
            '<button type="button" id="ub-undo" hidden>↶ Angre</button></div>\n' + HTML_OLD)

TAP_OLD = "      } else if (state.tool && c) placeAt(c, state.tool);"
TAP_NEW = ("      } else if (state.tool && c && !state.army.some(a => a.col === c.col && a.row === c.row)) placeAt(c, state.tool);\n"
           "      else if (state.tool && c) { state.tool = null; clickSelect(c, false, unitAt(e.clientX, e.clientY)); renderPanel(); }")

FULL_OLD = "eller bytt` : 'Bytt'} ut en svakere unit ved å plassere oppå den.`); return; }"
FULL_NEW = "eller fjern` : 'Fjern'} en svakere unit (trykk på den, så «Fjern») og plasser den nye.`); return; }"

UNDO_JS = """
  // ---------- Angre (versjon 47): siste kjøp, salg, bytte eller oppgradering i byggefasen ----------
  const undoStack = [];
  function withUndo(fn, label) {
    if (state.phase !== 'build') return fn();
    const army = JSON.stringify(state.army), res = Object.assign({}, state.econ.res);
    const n0 = state.army.length;
    fn();
    if (JSON.stringify(state.army) === army) return;
    const d = {}; for (const r in state.econ.res) d[r] = state.econ.res[r] - (res[r] || 0);
    const n1 = state.army.length;
    undoStack.push({ army, d, label: label || (n1 > n0 ? 'kjøp' : n1 < n0 ? 'salg' : 'bytte') });
    if (undoStack.length > 20) undoStack.shift();
    syncUndo();
  }
  function undoLast() {
    if (state.phase !== 'build' || !undoStack.length) return;
    const u = undoStack[undoStack.length - 1], res = state.econ.res;
    const short = Object.keys(u.d).filter(r => u.d[r] > 0 && res[r] < u.d[r]);
    if (short.length) { toast('Du har brukt det du fikk igjen for salget. Skaff det tilbake først, så kan du angre.'); return; }
    undoStack.pop();
    for (const r in u.d) res[r] -= u.d[r];
    state.army = JSON.parse(u.army);
    state.tool = null; clearSelection(true);
    rebuild(); renderPanel(); syncUndo();
    toast(`Angret ${u.label}.`); sfx('coin');
  }
  function syncUndo() {
    const cb = document.getElementById('ub-cancel'), ub = document.getElementById('ub-undo');
    if (!cb || !ub) return;
    const placing = state.phase === 'build' && state.tool && TYPES[state.tool];
    cb.hidden = !placing;
    if (placing) { const t = TYPES[state.tool].name; if (cb.dataset.t !== t) { cb.dataset.t = t; cb.querySelector('span').textContent = t; cb.title = 'Avslutt plasseringen'; } }
    ub.hidden = state.phase !== 'build' || !undoStack.length;
    if (!ub.hidden) ub.title = 'Angre siste ' + undoStack[undoStack.length - 1].label;
  }
  setInterval(syncUndo, 200);
  document.addEventListener('click', e => {
    if (e.target.closest('#ub-cancel')) { state.tool = null; renderPanel(); syncUndo(); }
    else if (e.target.closest('#ub-undo')) undoLast();
  });
  window.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey && (e.key === 'z' || e.key === 'Z') && !(e.target.closest && e.target.closest('input, textarea'))) { e.preventDefault(); undoLast(); }
  });
"""

def apply(s):
    s = sub(s, '</style>\n\n<div class="app">', CSS + '</style>\n\n<div class="app">')
    s = sub(s, HTML_OLD, HTML_NEW)
    s = sub(s, TAP_OLD, TAP_NEW)
    s = sub(s, FULL_OLD, FULL_NEW)
    # Kjøp, salg og bytte på kartet, «Fjern» og «Oppgrader» går gjennom withUndo.
    s = sub(s, "  function placeAt(c, tool) {", "  const placeAt = (c, tool) => withUndo(() => placeAtRaw(c, tool));\n  function placeAtRaw(c, tool) {")
    s = sub(s, "  function upgradeSelected() {", "  const upgradeSelected = () => withUndo(upgradeSelectedRaw, 'oppgradering');\n  function upgradeSelectedRaw() {")
    s = sub(s, "  function removeSelected() {", "  const removeSelected = () => withUndo(removeSelectedRaw, 'salg');\n  function removeSelectedRaw() {")
    s = sub(s, "  function startWave() {\n    if (state.phase !== 'build') return;\n",
               "  function startWave() {\n    if (state.phase !== 'build') return;\n    undoStack.length = 0;\n")
    s = sub(s, '  // ---------- Startskjerm (versjon 46) ----------', UNDO_JS + '\n  // ---------- Startskjerm (versjon 46) ----------')
    return s
