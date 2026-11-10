# Fortsett der du slapp (versjon 48). Rune ble «dratt ut» av spillet rundt wave 14 og mistet runden.
# I byggefasen lagres spillet i nettleseren hvert 2. sekund (din økonomi, hær, wave, computer-rivalen, innkommende
# skapninger). Startskjermen viser «Fortsett wave N» når det finnes et lagret spill. Ikke online og ikke lag-modus.
from patch import sub

CSS = """
.intro-go.intro-resume { background: linear-gradient(180deg, #c99af0, #a35ae0); color: #12061c; box-shadow: 0 0 22px rgba(163, 90, 224, .35); }
.intro-go.intro-resume small { display: block; font-size: 12px; letter-spacing: .02em; text-transform: none; font-weight: 600; opacity: .8; }
.intro-go.intro-new { background: transparent; color: var(--fg); border: 1px solid var(--line); box-shadow: none; font-size: 15px; }
"""

JS = r"""
  // ---------- Fortsett der du slapp (versjon 48) ----------
  const SAVE_KEY = 'kt2-save';
  const saveGet = () => { try { const s = JSON.parse(localStorage.getItem(SAVE_KEY) || 'null'); return s && s.v === NET_V && s.wave > 0 ? s : null; } catch (e) { return null; } };
  const saveDel = () => { try { localStorage.removeItem(SAVE_KEY); } catch (e) {} };
  function saveNow() {
    if (state.phase === 'over') { saveDel(); return; }
    if (state.intro || state.phase !== 'build' || net.mid || state.team || state.wave < 1 || state.arena) return;
    const r = state.rival, R = r && !r.remote ? { ec: r.ec, army: r.army, memo: r.memo, bank: r.bank, intent: r.intent, t: r.t, alive: r.alive, wi: r.wi, saved: r.saved } : null;
    const d = { v: NET_V, when: Date.now(), wave: state.wave, buildLeft: state.buildLeft, buildTotal: state.buildTotal, army: state.army, econ: state.econ, rival: R,
      versus: state.versus, flags: state.flags, rivalFlags: state.rivalFlags, incoming: state.incoming, sendQueue: state.sendQueue, arenaCount: state.arenaCount || 0 };
    try { localStorage.setItem(SAVE_KEY, JSON.stringify(d)); } catch (e) {}
  }
  setInterval(saveNow, 2000);
  const asEcon = o => Object.assign(Object.create(Econ.prototype), JSON.parse(JSON.stringify(o)));
  function resumeSave(d) {
    newMatch();
    Object.assign(state, { econ: asEcon(d.econ), army: d.army || [], wave: d.wave, buildLeft: Math.max(25, d.buildLeft || BUILD_TIME), buildTotal: Math.max(25, d.buildTotal || BUILD_TIME),
      versus: !!d.versus, flags: d.flags || 0, rivalFlags: d.rivalFlags || 0, incoming: d.incoming || [], sendQueue: d.sendQueue || [], arenaCount: d.arenaCount || 0 });
    if (d.rival && state.rival && !state.rival.remote) { const r = state.rival; Object.assign(r, d.rival); r.ec = asEcon(d.rival.ec); r.hold = null; r.sim = null; }
    rebuild(); syncVillage(); renderPanel();
    toast(`Velkommen tilbake. Du er på wave ${curWave().n}.`);
  }
  (() => {
    const d = saveGet(), go = document.getElementById('intro-go'); if (!d || !go) return;
    const ago = Math.round((Date.now() - (d.when || 0)) / 60000);
    const b = document.createElement('button'); b.type = 'button'; b.className = 'intro-go intro-resume'; b.id = 'intro-resume';
    b.innerHTML = `Fortsett wave ${d.wave + 1}<small>${ago < 1 ? 'lagret nå nettopp' : ago < 120 ? `lagret for ${ago} min siden` : `lagret for ${Math.round(ago / 60)} timer siden`}</small>`;
    go.parentNode.insertBefore(b, go);
    go.textContent = 'Nytt spill'; go.classList.add('intro-new');
    b.addEventListener('click', e => { e.stopPropagation(); closeIntro(); resumeSave(d); });
  })();
"""

def apply(s):
    s = sub(s, ".intro-go:hover { filter: brightness(1.08); }\n", ".intro-go:hover { filter: brightness(1.08); }\n" + CSS)
    s = sub(s, "  if (/dbg/.test(location.hash)) window.__dbg", JS + "\n  if (/dbg/.test(location.hash)) window.__dbg")
    return s
