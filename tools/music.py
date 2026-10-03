"""Recorded music and a longer break between waves (3 Oct 2026). Applied by build_v2.py.
Build phase and battle each rotate their own tracks: every new phase starts the next track in the list, and if a
phase outlasts a track the next one takes over. The mp3 files are published next to the page under musikk/.
If a phase's files can't load, that phase falls back to the generated music."""
from patch import sub

FILES = """  // Innspilt musikk: byggefasen og kampen har hver sin liste med spor som går på rundgang.
  // Hver ny fase starter neste spor; varer fasen lenger enn sporet, tar det neste over.
  // Mangler filene for en fase, spilles den genererte musikken der.
  const TRACKS = {
    build: ['musikk/building-phase.mp3', 'musikk/a-new-world-assembles.mp3'],
    battle: ['musikk/strategic-march.mp3', 'musikk/battle-2.mp3', 'musikk/strategic-march-2.mp3'],
  };
  const files = {};
  let fileStop = null;
  function initFiles() {
    Object.keys(TRACKS).forEach(m => {
      const F = files[m] = { gain: ctx.createGain(), els: [], idx: -1, ok: false, cur: null };
      F.gain.gain.value = 0; F.gain.connect(musicBus);
      F.els = TRACKS[m].map((src, i) => {
        const a = new Audio(); a.preload = m === 'build' ? 'auto' : 'metadata'; a.src = src;
        a.addEventListener('ended', () => { if (mode === m && F.cur === a) playTrack(m, (i + 1) % F.els.length); });
        a.addEventListener('canplay', () => {
          if (F.ok) return; F.ok = true;
          (m === 'build' ? buildGain : battleGain).gain.setTargetAtTime(0, ctx.currentTime, 0.4);
          if (mode === m) startFiles(m);
        }, { once: true });
        try { ctx.createMediaElementSource(a).connect(F.gain); } catch (e) { /* uten Web Audio-ruting spilles den rett ut */ }
        return a;
      });
      // Kampsporene lastes litt senere, så byggemusikken får starte først.
      if (m === 'battle') setTimeout(() => F.els.forEach(a => { a.preload = 'auto'; a.load(); }), 1500);
    });
  }
  function playTrack(m, i) {
    const F = files[m]; F.idx = i; F.cur = F.els[i];
    F.els.forEach(a => { if (a !== F.cur) a.pause(); });
    try { F.cur.currentTime = 0; } catch (e) {}
    const p = F.cur.play(); if (p && p.catch) p.catch(() => {});
  }
  function startFiles(m) {
    const F = files[m];
    if (!F || !F.ok) return;
    playTrack(m, (F.idx + 1) % F.els.length);
    F.gain.gain.cancelScheduledValues(ctx.currentTime);
    F.gain.gain.setTargetAtTime(0.9, ctx.currentTime, 0.5);
  }
  function stopFiles(m) {
    const F = files[m];
    if (!F) return;
    F.gain.gain.cancelScheduledValues(ctx.currentTime);
    F.gain.gain.setTargetAtTime(0, ctx.currentTime, 0.35);
    setTimeout(() => { if (mode !== m) F.els.forEach(a => a.pause()); }, 1800);
  }
  const filesOn = m => !!(files[m] && files[m].ok);

  // ---- Musikk: to spor i d-moll ----"""

def apply(s):
    s = sub(s, "  // ---- Musikk: to spor i d-moll ----", FILES)
    s = sub(s, "    started = true;\n    schedule();", "    started = true;\n    initFiles();\n    schedule();")
    # Den genererte musikken hviler i en fase som har filer (takten går videre i stillhet).
    s = sub(s, "      const beat = 60 / 132, ch = BATTLE_CH[bar % 4];", "      const beat = 60 / 132, ch = BATTLE_CH[bar % 4];\n      if (filesOn('battle')) { nextBar = t + beat * 4; bar++; return; }")
    s = sub(s, "      const beat = 60 / 70, ch = BUILD_CH[bar % 4];", "      const beat = 60 / 70, ch = BUILD_CH[bar % 4];\n      if (filesOn('build')) { nextBar = t + beat * 4; bar++; return; }")
    s = sub(s, """    buildGain.gain.setTargetAtTime(m === 'build' ? 1 : 0, t, 0.6);
    battleGain.gain.setTargetAtTime(m === 'battle' ? 1 : 0, t, 0.4);""",
             """    buildGain.gain.setTargetAtTime(m === 'build' && !filesOn('build') ? 1 : 0, t, 0.6);
    battleGain.gain.setTargetAtTime(m === 'battle' && !filesOn('battle') ? 1 : 0, t, 0.4);
    stopFiles(m === 'build' ? 'battle' : 'build'); startFiles(m);""")
    # Lengre pause mellom wavene.
    s = sub(s, "const BUILD_FIRST = 45, BUILD_TIME = 30;", "const BUILD_FIRST = 45, BUILD_TIME = 55;")
    return s
