# Startskjerm (versjon 46). Rune: fjern overskriften, «Prototype · milepæl A–D» og beskrivelsen øverst i panelet,
# og vis i stedet en boks midt på skjermen når spillet åpnes: logoen, «The Last Flame» og en Start-knapp.
# Spillet står stille (ingen nedtelling, ingen arbeidere) til du trykker Start. Senere skal det spilles en video her:
# legg den i .intro-media (bytt ut skjoldet med en <video>).
# - Velkomstkortet (computer eller venn) kommer først etter Start, første gang.
# - Får du en invitasjon mens startskjermen står, kommer den over; «Spill mot X» lukker startskjermen.
# - På telefon: står siden litt rullet slik at toppen av spillet er skjult, glir den tilbake (sjekkes hvert sekund og ved trykk).
from patch import sub

CSS = """
/* Startskjerm (versjon 46). */
.intro { position: fixed; inset: 0; z-index: 65; display: flex; align-items: center; justify-content: center; padding: 16px;
  background: radial-gradient(ellipse at 50% 40%, rgba(60, 34, 10, .92), rgba(8, 9, 12, .97) 70%); }
.intro[hidden] { display: none; }
.intro-box { width: min(380px, 100%); text-align: center; display: flex; flex-direction: column; align-items: center; gap: 12px;
  padding: 26px 22px 22px; border: 1px solid rgba(226, 181, 74, .5); border-radius: 14px; background: rgba(16, 13, 10, .88); box-shadow: 0 20px 60px rgba(0, 0, 0, .6); }
.intro-media { width: 100%; display: flex; justify-content: center; }
.intro-media svg, .intro-media .crest { display: block !important; width: 92px; height: 110px; filter: drop-shadow(0 0 18px rgba(255, 170, 60, .45)); }
.intro-media video { width: 100%; border-radius: 10px; }
.intro h1 { font-family: var(--display); font-weight: 700; font-size: 30px; letter-spacing: .06em; margin: 0; color: #ecc970; text-shadow: 0 0 18px rgba(255, 170, 60, .35); }
.intro p { margin: 0; color: var(--muted); font-size: 14px; }
.intro-go { margin-top: 6px; width: 100%; padding: 14px 16px; font-size: 18px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
  color: #1a1006; background: linear-gradient(180deg, #ffd27a, #e2a23b); border: 0; border-radius: 10px; cursor: pointer; box-shadow: 0 0 22px rgba(255, 170, 60, .35); }
.intro-go:hover { filter: brightness(1.08); }
.brand .vsbtn { margin-top: 0; }
"""

HEADER_OLD = """      <div class="eyebrow">Prototype · milepæl A–D · oppgraderinger</div>
      <h1>The Last Flame</h1>
      <p>Hold ut i tretti waves gjennom tre verdener. Arbeiderne samler hele tiden; bruk ressursene på hær, oppgraderinger og mur. Klikk på bygningene i landsbyen for å bruke dem.</p>
"""

HELLO_OLD = """  setTimeout(() => {
    if (store.get('kt2-hello') || icEl || net.mid) return;"""
HELLO_NEW = """  const helloCard = () => {
    if (state.intro || store.get('kt2-hello') || icEl || net.mid) return;"""
HELLO_END_OLD = """data-ic="friend">Spill mot en venn</button></div>`);
  }, 900);
"""
HELLO_END_NEW = """data-ic="friend">Spill mot en venn</button></div>`);
  };
  setTimeout(helloCard, 900);

  // ---------- Startskjerm (versjon 46) ----------
  // Spillet står stille til Start trykkes. Senere: video i .intro-media.
  state.intro = !/nointro/.test(location.hash);
  const introEl = document.createElement('div');
  introEl.className = 'intro'; introEl.hidden = !state.intro;
  introEl.innerHTML = `<div class="intro-box" role="dialog" aria-label="The Last Flame">
    <div class="intro-media"></div>
    <h1>The Last Flame</h1>
    <p>Hold porten. Vokt flammen.</p>
    <button type="button" class="intro-go" id="intro-go">Start</button></div>`;
  document.body.appendChild(introEl);
  setTimeout(() => { const m = introEl.querySelector('.intro-media'); if (m && !m.firstChild) m.innerHTML = crestSvg(0); }, 0);   // skjoldet tegnes når resten av koden er lest inn
  function closeIntro() {
    if (!state.intro) return;
    state.intro = false; introEl.hidden = true; last = performance.now();
    try { Sound.init(); syncSoundBtns(); } catch (e) {}
    setTimeout(helloCard, 300);
  }
  introEl.addEventListener('click', e => { if (e.target.closest('#intro-go')) closeIntro(); });
  document.addEventListener('click', e => { if (e.target.closest && e.target.closest('[data-ic="yes"]')) closeIntro(); });
  // Telefon: står siden litt rullet så toppen av spillet er skjult, glir den tilbake.
  const stageEl = document.querySelector('.stage');
  const unscroll = () => {
    if (!window.matchMedia('(max-width: 600px)').matches) return;
    const r = stageEl.getBoundingClientRect();
    if (r.top < -2 && r.top > -90) stageEl.scrollIntoView({ block: 'start', behavior: 'smooth' });
  };
  setInterval(() => { if (!pointers.size) unscroll(); }, 1000);
"""

def apply(s):
    s = sub(s, '</style>\n\n<div class="app">', CSS + '</style>\n\n<div class="app">')
    s = sub(s, HEADER_OLD, '')
    s = sub(s, HELLO_OLD, HELLO_NEW)
    s = sub(s, HELLO_END_OLD, HELLO_END_NEW)
    s = sub(s, "    if (state.phase === 'build') {\n      stageEnemies();", "    if (state.phase === 'build' && !state.intro) {\n      stageEnemies();")
    # Versjon 45 sin tilbakeglidning bruker nå scrollIntoView (virker også når det er rammen rundt som er rullet).
    s = sub(s, "window.scrollTo({ top: window.scrollY + r.top, behavior: 'smooth' });", "$('.stage').scrollIntoView({ block: 'start', behavior: 'smooth' });")
    return s
