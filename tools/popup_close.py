# Popups på telefon (versjon 41). Rune: noen vinduer for units o.l. gikk ikke an å komme ut av på mobil.
# Nå: stor, tydelig X på alle vinduer, og et trykk utenfor lukker dem.
# - Ordrelinjen (valgte units): X, trykk på tomt kart (som før) og nå også trykk i sidepanelet (unntatt «velg alle»-bildet og «i»).
#   Lukkes på click, ikke pointerdown, så knappen du trykket på ikke tegnes bort før den rekker å virke.
# - Bygningsvinduet: X som blir stående når du blar, trykk på kartet (ikke dra) eller hvor som helst utenfor.
# - Valgkortene (helt, talent, doktrine) og velkomst/utfordring: X, og trykk utenfor = «Senere» / «Spill mot computeren» / «Ikke nå».
#   Trykket utenfor svelges, så det ikke også velger en unit eller trykker en knapp under.
# - Arenaresultatet: X og trykk utenfor. Kortet før duellen (nedtelling) lukkes ikke.
# - Enhetsboksen som følger musen, henger ikke igjen etter et fingertrykk.
# Dobbelttrykk for å velge hele typen og helte-treffsonen (versjon 38) er urørt: kartets egne trykk går som før.
from patch import sub

CSS = """
/* Popups på telefon (versjon 41): stor, tydelig X, og trykk utenfor lukker. */
.om-x, .bpop-x, .pc-x { width: 38px; height: 38px; padding: 0; display: flex; align-items: center; justify-content: center; border-radius: 50%;
  background: rgba(255, 255, 255, .09); border: 1px solid rgba(255, 255, 255, .3); color: var(--fg); font-size: 26px; line-height: 1; z-index: 3; cursor: pointer; }
.om-x:hover, .bpop-x:hover, .pc-x:hover { background: rgba(255, 255, 255, .18); color: #fff; }
.om-x { top: 6px; right: 6px; }
.om-head { padding-right: 46px; }
/* I vinduer som kan blas i, blir X stående øverst. */
.bpop-x, .pc-x { position: sticky; top: 0; right: auto; align-self: flex-end; flex: none; margin: 0 0 -46px; }
.bpop h3 { padding-right: 46px; }
.choicecard h2, .invcard h2, .arenacard h2 { padding-inline: 40px; }
@media (max-width: 600px) {
  .om-x, .bpop-x, .pc-x { width: 42px; height: 42px; font-size: 28px; }
  .om-x { top: 4px; right: 4px; }
  .bpop-x, .pc-x { margin-bottom: -50px; }
  .om-head { padding-right: 50px; }
  .bpop h3 { padding-right: 50px; }
  .ordermenu { max-height: 40vh; }
  .om-up span { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
  .bpop { left: 8px; right: 8px; width: auto; max-height: calc(100% - 112px); }
  .ch-opt { padding: 8px 10px; }
  .ch-opt img { width: 44px; height: 44px; }
}
"""

JS = r"""  // ---------- Popups på telefon (versjon 41): stor X, og trykk utenfor lukker ----------
  let pcSwallow = 0, pcPanelTap = false;
  document.addEventListener('pointerdown', e => {
    const t = e.target;
    pcPanelTap = false;
    if (!t || !t.closest) return;
    // Kort som krever et valg: trykk utenfor = lukk-knappen på kortet. Trykket går ikke videre til det som er under.
    const inv = document.querySelector('.invcard'), modal = inv || (choiceCard.hidden ? null : choiceCard);
    if (modal) {
      if (modal.contains(t)) return;
      e.stopPropagation(); e.preventDefault();
      const b = modal.querySelector('[data-later], [data-ic="no"], [data-ic="cpu"]'); if (b) b.click();
      pcSwallow = performance.now() + 500;
      return;
    }
    // Bygningsvinduet. Trykk på kartet håndteres ved slipp (så du kan dra kartet uten å lukke).
    if (state.pop && !bpop.hidden && !bpop.contains(t) && !canvas.contains(t)) closePop();
    // Arenaresultatet (ikke nedtellingen før duellen).
    if (!arenaCard.hidden && state.phase !== 'arena-intro' && !arenaCard.contains(t)) hideArenaCard();
    // Ordrelinjen: trykk i sidepanelet lukker den, men først når trykket er ferdig (se click under).
    pcPanelTap = !menu.hidden && !!t.closest('.panel') && !t.closest('[data-pick], [data-info], .u-add');
  }, true);
  document.addEventListener('click', e => {
    if (performance.now() < pcSwallow) { pcSwallow = 0; e.stopPropagation(); e.preventDefault(); }
  }, true);
  document.addEventListener('click', e => {
    if (e.target.closest && e.target.closest('[data-pcx="arena"]')) { hideArenaCard(); return; }
    if (pcPanelTap) { pcPanelTap = false; if (!menu.hidden) clearSelection(); }
  });

"""

X = '<button type="button" class="pc-x" aria-label="Lukk"'

def apply(s):
    s = sub(s, '</style>\n\n<div class="app">', CSS + '</style>\n\n<div class="app">')
    # Trykk (ikke dra) på kartet utenfor en bygning lukker bygningsvinduet. Må kjøre før endPointer nullstiller drag.
    s = sub(s, "  canvas.addEventListener('pointerup', endPointer);",
               "  canvas.addEventListener('pointerup', e => { if (state.pop && drag && !drag.moved && pointers.size === 1 && !pickBuilding(e.clientX, e.clientY)) closePop(); });\n"
               "  canvas.addEventListener('pointerup', endPointer);")
    # Fingeren er borte når den slippes: enhetsboksen som følger musen, skal ikke bli hengende.
    s = sub(s, "  canvas.addEventListener('pointerleave', () => { hover.visible = false; mouse.inside = false; });",
               "  canvas.addEventListener('pointerleave', () => { hover.visible = false; mouse.inside = false; });\n"
               "  canvas.addEventListener('pointerup', e => { if (e.pointerType !== 'mouse') mouse.inside = false; });\n"
               "  canvas.addEventListener('pointercancel', () => { mouse.inside = false; });")
    s = sub(s, 'choiceCard.innerHTML = html; choiceCard.hidden = false;',
               "choiceCard.innerHTML = '" + X + " data-later>×</button>' + html; choiceCard.hidden = false;")
    s = sub(s, 'icEl.innerHTML = html;',
               "icEl.innerHTML = '" + X + " data-ic=\"' + (html.includes('data-ic=\"no\"') ? 'no' : 'cpu') + '\">×</button>' + html;")
    s = sub(s, '<button type="button" class="ac-go" id="ac-go">Tilbake til byggingen</button>',
               X + ' data-pcx="arena">×</button><button type="button" class="ac-go" id="ac-go">Tilbake til byggingen</button>')
    s = sub(s, '  // Testsnarvei: #w7 i adressen starter på wave 7.', JS + '  // Testsnarvei: #w7 i adressen starter på wave 7.')
    return s
