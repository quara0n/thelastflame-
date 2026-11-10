# Mindre statusboks øverst til høyre på telefon (versjon 42, strammet inn i versjon 43: bare wave og nedtelling). Rune: «Den menyen til høyre er for stor.
# Lag den mindre eller fjern noe uviktig og legg den helt oppe til høyre på mobil.»
# - Boksen står i hjørnet øverst til høyre, på høyde med ressursene, ikke under dem.
# - Bort på telefon: overskriften «Forsvar Nord», «Forsvarere/Fiender» og teksten «Neste wave om» (klokka står igjen).
#   Igjen: fasen, wave, nedtellingen og porten med stolpe.
# - Kameraknappene (Slagmark, Rival, Bastion, Lyd) blir små, to og to under boksen.
# - Ressursene viser bare ikon og tall (ikke navnet), og skjoldet til venstre er borte, så alt får plass på én linje.
# - Versjon 44: rivalkartet nede til høyre er lite (60 × 38) på telefon. Første trykk gjør det stort (som før)
#   uten å flytte kameraet; trykk i det store kartet flytter kameraet, og trykk utenfor gjør det lite igjen.
# - Versjon 45: toppen av spillet forsvant opp under appens topplinje etter noen waves. Et sveip på unitkortene
#   nederst (eller knappene) rullet hele siden litt ned. Nå: sveip på det som ligger over spillet ruller ikke siden,
#   og står siden halvveis rullet når du trykker i spillet, glir den tilbake så hele spillet synes.
# Datamaskin er uendret.
from patch import sub

CSS = """
/* Statusboksen i hjørnet øverst til høyre på telefon (versjon 42). */
@media (max-width: 600px) {
  .hud { flex-wrap: nowrap; }
  #crest, .crest { display: none; }
  .hud-l { flex: 1 1 auto; margin-right: 80px; }
  .hud-l .res .rn { display: none; }
  .hud-l .res { padding: 3px 5px; }
  .hud-l .res .rv { gap: 3px; }
  .hud-l .res .rv svg, .hud-l .res .rv img { width: 14px; height: 14px; }
  .hud-r { position: absolute; top: 0; right: 0; width: 108px; gap: 3px; }
  /* Versjon 43: bare wave og nedtelling, tett i hjørnet. */
  .goalbox { align-self: flex-end; width: auto; box-sizing: border-box; padding: 3px 7px; gap: 0; border-radius: 7px; min-width: 0; }
  .goal-h, .goalbox .hud-sub, .goalbox .pill.phase, #h-timelabel { display: none; }
  .goalbox .pill, .goalbox .pill.big { font-size: 11px; gap: 4px; white-space: nowrap; }
  .goalbox .pill::before { content: none; }
  .goalbox .pill.big b { font-size: 12px; }
  #h-timebox::before { content: '⏱'; font-size: 10px; }
  .camjump { display: grid; grid-template-columns: 1fr 1fr; gap: 3px; width: 100%; }
  .camjump button { padding: 3px 2px; font-size: 10px; border-radius: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .camjump button[hidden] { display: none; }
  /* Versjon 44: lite rivalkart til det trykkes på. */
  #minimap { width: 60px; height: 38px; opacity: .85; }
  #minimap.mm-big { width: 120px; height: 78px; opacity: 1; }
  /* Versjon 45: sveip på det som ligger oppå spillet skal ikke rulle siden. */
  .stage > .hud, .stage > .hud *, .ucards, .ucards *, .abilbar, .abilbar * { touch-action: none; }
}
"""

MM_OLD = "  mm.addEventListener('pointerdown', e => { e.stopPropagation(); mm.setPointerCapture(e.pointerId); mmGo(e); mm._drag = true; });"
MM_NEW = (
    "  const mmSmall = () => window.matchMedia('(max-width: 600px)').matches && !mm.classList.contains('mm-big');\n"
    "  mm.addEventListener('pointerdown', e => { e.stopPropagation(); if (mmSmall()) { e.preventDefault(); mm.classList.add('mm-big'); mmT = 0; return; } mm.setPointerCapture(e.pointerId); mmGo(e); mm._drag = true; });\n"
    "  document.addEventListener('pointerdown', e => { if (mm.classList.contains('mm-big') && e.target !== mm) mm.classList.remove('mm-big'); }, true);\n"
    "  // Versjon 45: står siden halvveis rullet forbi toppen av spillet, glir den tilbake når du trykker i spillet.\n"
    "  $('.stage').addEventListener('pointerdown', () => { if (!window.matchMedia('(max-width: 600px)').matches) return; const r = $('.stage').getBoundingClientRect(); if (r.top < -2 && r.bottom > 80) window.scrollTo({ top: window.scrollY + r.top, behavior: 'smooth' }); }, true);"
)

def apply(s):
    s = sub(s, '</style>\n\n<div class="app">', CSS + '</style>\n\n<div class="app">')
    return sub(s, MM_OLD, MM_NEW)
