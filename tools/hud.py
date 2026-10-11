"""Skjermoppsett etter Runes slagmarksbilder (11. okt 2026, versjon 31).

Bildene (docs/art/slagmark-*.png) har samme oppsett på alle sider:
- sidens skjold med merket oppe til venstre, ved ressursene,
- en målboks oppe til høyre («Forsvar Nord») med wave, tid, forsvarere/fiender og porten,
- unitkort nede til venstre: ett kort per type i hæren med bilde, antall, nivå og helse,
- minikartet nede til høyre (fantes fra før).

Trykk på et unitkort velger alle av den typen (som før via kortene i Hær-fanen).
Bare skjerm; kampen og balansen er uendret.
"""
from patch import sub

CSS = r"""
/* Skjermoppsett etter slagmarksbildene (hud.py): skjold, målboks, unitkort. */
.hud { justify-content: flex-start; }
.hud-r { margin-left: auto; }
.crest { flex: none; width: 42px; height: 50px; filter: drop-shadow(0 3px 6px rgba(0, 0, 0, .55)); pointer-events: none; }
.goalbox { background: rgba(16, 13, 10, .86); border: 1px solid rgba(226, 181, 74, .5); border-radius: 9px; padding: 7px 11px 8px; display: flex; flex-direction: column; gap: 3px; min-width: 210px; box-shadow: 0 6px 18px rgba(0, 0, 0, .45); backdrop-filter: blur(4px); }
.goal-h { display: flex; align-items: center; gap: 7px; font-family: var(--display); font-size: 15px; letter-spacing: .03em; color: #ecc970; border-bottom: 1px solid rgba(226, 181, 74, .25); padding-bottom: 4px; margin-bottom: 2px; }
.goal-h i { font-style: normal; font-size: 12px; }
.goalbox .hud-main, .goalbox .hud-sub { flex-direction: column; align-items: stretch; justify-content: flex-start; gap: 3px; }
.goalbox .pill, .goalbox .pill.big { background: none; border: 0; border-radius: 0; padding: 0; backdrop-filter: none; font-size: 12.5px; gap: 7px; justify-content: flex-start; }
.goalbox .pill::before { content: '◇'; color: #e2b54a; font-size: 10px; }
.goalbox .pill.phase { font-size: 10.5px; }
.goalbox .pill.phase::before { content: none; }
.goalbox .pill.big b { font-size: 13px; }
.goalbox .gatebar { flex: 1; min-width: 50px; }
.goalbox #h-gatebox.broken::before { color: var(--enemy); }
.ucards { position: absolute; left: 12px; bottom: 12px; display: flex; gap: 6px; z-index: 5; }
.ordermenu:not([hidden]) ~ .ucards { display: none; }
.ucd { position: relative; width: 62px; padding: 0; border: 1px solid #5a4630; border-radius: 7px; background: #120f0c; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 4px 12px rgba(0, 0, 0, .5); }
.ucd img { width: 100%; height: 62px; object-fit: cover; object-position: 50% 28%; background: radial-gradient(circle at 50% 35%, #2c3646, #12161e); display: block; }
.ucd .ucn { position: absolute; top: 2px; right: 3px; font: 600 11px var(--mono); color: #fff; text-shadow: 0 1px 2px #000; }
.ucd .ucl { position: absolute; left: 3px; top: 44px; font-size: 9px; color: #ffd76a; letter-spacing: -1px; text-shadow: 0 1px 2px #000; }
.ucd .uchp { display: block; height: 6px; background: #1d1a16; }
.ucd .uchp b { display: block; height: 100%; background: linear-gradient(90deg, #3e9a3a, #8fd16a); transition: width .2s; }
.ucd.low .uchp b { background: linear-gradient(90deg, #a8321f, #e0724a); }
.ucd.sel { border-color: #f4efe6; box-shadow: 0 0 0 1px #f4efe6, 0 4px 12px rgba(0, 0, 0, .5); }
.ucd.more { justify-content: center; align-items: center; color: var(--muted); font: 600 13px var(--mono); min-height: 68px; }
.stage.has-cards .hint { display: none; }
.stage.has-cards .abilbar { bottom: 90px; }
@media (max-width: 600px) {
  .crest { width: 30px; height: 36px; }
  .goalbox { min-width: 0; padding: 4px 8px 5px; gap: 1px; }
  .goal-h { font-size: 12px; padding-bottom: 2px; }
  .goalbox .pill, .goalbox .pill.big { font-size: 11px; gap: 5px; }
  .goalbox .pill.big b { font-size: 11.5px; }
  .goalbox .pill.phase { font-size: 9.5px; }
  .ucards { left: 6px; bottom: 6px; gap: 4px; }
  .ucd { width: 46px; }
  .ucd img { height: 46px; }
  .ucd .ucl { top: 32px; }
  .ucd .uchp { height: 5px; }
  .ucd.more { min-height: 51px; }
  .stage.has-cards .abilbar { bottom: 66px; }
}
"""

# Sidens skjold: mørkeblått (grønt i øst) med merket i gull/lyst. Samme merker som på bannerne (village.py).
CREST = r"""
  // ---------- Skjermoppsett etter slagmarksbildene (hud.py) ----------
  const CREST_MARK = [
    '<path d="M20 30 l-2 -6 h4 z M20 25 q-1 -4 -6 -8 l-3 -5 M14 17 l-4 1 M12 13 l1 -4 M20 25 q1 -4 6 -8 l3 -5 M26 17 l4 1 M28 13 l-1 -4" fill="none" stroke-width="2" stroke-linecap="round"/><ellipse cx="20" cy="28" rx="3" ry="4"/>',
    '<path d="M20 34 v-12 M20 30 l-4 4 M20 30 l4 4" fill="none" stroke-width="2.2" stroke-linecap="round"/><circle cx="20" cy="17" r="8"/>',
    '<path d="M20 8 l2.5 9.5 l9.5 2.5 l-9.5 2.5 l-2.5 9.5 l-2.5 -9.5 l-9.5 -2.5 l9.5 -2.5 z"/><circle cx="20" cy="20" r="6" fill="none" stroke-width="1.5"/>',
    '<path d="M20 12 v20 M14 16 h12 M11 25 q2 8 9 8 q7 0 9 -8 M11 25 l-1 3 M29 25 l1 3" fill="none" stroke-width="2.2" stroke-linecap="round"/><circle cx="20" cy="10" r="2.6" fill="none" stroke-width="1.8"/>',
  ];
  const CREST_COL = [['#22325a', '#d9c79a'], ['#1f4a2a', '#d8c27a'], ['#24346a', '#e2b54a'], ['#22325a', '#e8e2d0']];
  function crestSvg(si) {
    const [bg, fg] = CREST_COL[si];
    return `<svg class="crest" viewBox="0 0 40 48" aria-hidden="true"><path d="M3 3 h34 v22 q0 14 -17 21 q-17 -7 -17 -21 z" fill="${bg}" stroke="#b88b45" stroke-width="2"/>`
      + `<g fill="${fg}" stroke="${fg}">${CREST_MARK[si]}</g></svg>`;
  }
  function syncGoalBox() {
    const sd = SIDES[MY_SIDE];
    $('#goal-title').textContent = `Forsvar ${MY_SIDE ? sd.land : sd.name}`;
    const c = $('#crest'); if (c.dataset.si !== String(MY_SIDE)) { c.dataset.si = MY_SIDE; c.innerHTML = crestSvg(MY_SIDE); }
  }
  // Unitkort nede til venstre: ett per type i hæren, med antall, nivå og samlet helse. Trykk velger typen.
  let ucBox = null, ucSig = '';
  function syncUnitCards() {
    if (!ucBox) {
      ucBox = document.createElement('div'); ucBox.className = 'ucards'; $('.stage').appendChild(ucBox);
      ucBox.addEventListener('click', e => { const b = e.target.closest('[data-uc]'); if (b) toggleType(b.dataset.uc); else if (e.target.closest('.more')) $('#tab-army').click(); });
    }
    const groups = {};
    state.army.forEach((a, i) => { const g = groups[a.type] || (groups[a.type] = { n: 0, lv: 0, sel: 0 }); g.n++; g.lv = Math.max(g.lv, a.level || 0); if (state.selection.has(i)) g.sel++; });
    const types = Object.keys(groups).sort((a, b) => (TYPES[b].hero ? 1 : 0) - (TYPES[a].hero ? 1 : 0) || groups[b].n - groups[a].n);
    const max = PHONE ? 5 : 7, shown = types.length > max ? types.slice(0, max - 1) : types, rest = types.length - shown.length;
    const sig = shown.map(t => `${t}:${groups[t].n}:${groups[t].lv}:${groups[t].sel === groups[t].n}`).join('|') + '|' + rest;
    if (sig !== ucSig) {
      ucSig = sig;
      ucBox.innerHTML = shown.map(t => { const g = groups[t];
        return `<button type="button" class="ucd${g.sel === g.n ? ' sel' : ''}" data-uc="${t}" title="${TYPES[t].name}"><img alt="" src="${portraits[t] || ''}"><span class="ucn">×${g.n}</span><span class="ucl">${'▲'.repeat(g.lv)}</span><i class="uchp"><b></b></i></button>`;
      }).join('') + (rest > 0 ? `<button type="button" class="ucd more">+${rest}</button>` : '');
      $('.stage').classList.toggle('has-cards', shown.length > 0);
    }
    // Helse: alle av typen i slaget nå (døde teller som 0).
    const hp = {}, mx = {};
    if (sim) sim.units.forEach(u => { if (u.side !== 'p' || !groups[u.type]) return; hp[u.type] = (hp[u.type] || 0) + (u.alive ? Math.max(0, u.hp) : 0); mx[u.type] = (mx[u.type] || 0) + u.maxHp; });
    ucBox.querySelectorAll('[data-uc]').forEach(b => {
      const t = b.dataset.uc, r = mx[t] ? hp[t] / mx[t] : 1;
      b.querySelector('.uchp b').style.width = `${Math.round(r * 100)}%`;
      b.classList.toggle('low', r < 0.35);
    });
  }
"""


def apply(s):
    s = sub(s, "\n</style>\n", CSS + "</style>\n")
    s = sub(s, '      <div class="hud-l" aria-label="Ressurser">\n',
               '      <span id="crest"></span>\n      <div class="hud-l" aria-label="Ressurser">\n')
    s = sub(s, '      <div class="hud-r">\n        <div class="hud-main">\n',
               '      <div class="hud-r">\n        <div class="goalbox">\n        <div class="goal-h"><i>◇</i><b id="goal-title">Forsvar Nord</b></div>\n        <div class="hud-main">\n')
    s = sub(s, '          <div class="pill" id="h-gatebox"><span id="h-gate">Port 600</span><span class="gatebar"><i id="h-gatefill"></i></span></div>\n        </div>\n',
               '          <div class="pill" id="h-gatebox"><span id="h-gate">Port 600</span><span class="gatebar"><i id="h-gatefill"></i></span></div>\n        </div>\n        </div>\n')
    s = sub(s, "  function updateHud() {\n    updateBoss();\n", CREST + "  function updateHud() {\n    updateBoss(); syncGoalBox(); syncUnitCards();\n")
    return s
