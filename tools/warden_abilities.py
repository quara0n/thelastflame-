"""Warden abilities you trigger yourself during battle (4 Oct 2026). Applied by build_v2.py after warden_nerf.py.
Bought and upgraded in Warden's Sanctum (3 levels each; level 1 unlocks). Recharge counts in battle time and starts ready
each wave. Flammesjokk stuns enemies around him, Virvelvind makes him spin with the sword for 5 seconds hitting everything
close, Frostflamme freezes enemies in a large circle and slows them afterwards. The bot never uses them."""
from patch import sub

ECON = """
// Wardens evner (4. okt 2026): kjøpes og oppgraderes i Sanctum, brukes med knapper under kampen.
const WARDEN_ABIL = {
  stun:   { name: 'Flammesjokk', icon: '⚡', desc: lv => `Lammer fiender innen ${5 + lv} m i ${(1.5 + 0.5 * lv).toFixed(1).replace('.', ',')} s. Lades på ${[18, 15, 12][lv - 1]} s.`,
            levels: [{ cost: { gold: 20, iron: 6 } }, { cost: { gold: 30, iron: 12 } }, { cost: { gold: 45, iron: 18, coal: 6 } }] },
  spin:   { name: 'Virvelvind', icon: '🌀', desc: lv => `Snurrer med sverdet i 5 s og treffer alt innen ${(2.4 + 0.3 * lv).toFixed(1).replace('.', ',')} m (${Math.round((0.45 + 0.15 * lv) * 100)} % skade hvert 0,4 s). Lades på ${[30, 25, 20][lv - 1]} s.`,
            levels: [{ cost: { gold: 30, iron: 10 } }, { cost: { gold: 45, iron: 16 } }, { cost: { gold: 65, iron: 24, coal: 10 } }] },
  freeze: { name: 'Frostflamme', icon: '❄', desc: lv => `Fryser fiender innen ${8 + 2 * lv} m i ${2 + lv} s, så går de sakte en stund. Lades på ${[45, 38, 30][lv - 1]} s.`,
            levels: [{ cost: { gold: 40, iron: 12, coal: 4 } }, { cost: { gold: 60, iron: 20, coal: 8 } }, { cost: { gold: 85, iron: 28, coal: 14 } }] },
};
const ABIL_CD = { stun: [18, 15, 12], spin: [30, 25, 20], freeze: [45, 38, 30] };
const WARDEN_TRAIN"""

SIM = """  // Wardens evner. lv = nivået spilleren har kjøpt. Returnerer antall fiender som ble truffet.
  wardenAbility(kind, lv) {
    const w = this.warden; if (!w || !w.alive || !lv) return -1;
    const foes = this.units.filter(e => e.alive && e.side === 'e');
    if (kind === 'stun') {
      const r = 5 + lv, hit = foes.filter(e => dist(e, w) < r);
      hit.forEach(e => { e.stunUntil = this.t + (e.T.boss ? 0.6 : 1.5 + 0.5 * lv); });
      this.events.push({ kind: 'ability', ab: 'stun', x: w.x, z: w.z, r });
      return hit.length;
    }
    if (kind === 'spin') {
      w.spinUntil = this.t + 5; w.spinLv = lv; w.spinNext = this.t;
      this.events.push({ kind: 'ability', ab: 'spin', x: w.x, z: w.z, r: 2.4 + 0.3 * lv });
      return foes.filter(e => dist(e, w) < 2.4 + 0.3 * lv + 3).length;
    }
    if (kind === 'freeze') {
      const r = 8 + 2 * lv, hit = foes.filter(e => dist(e, w) < r);
      hit.forEach(e => { e.stunUntil = this.t + (e.T.boss ? 1 : 2 + lv); e.slowUntil = this.t + (e.T.boss ? 3 : 4 + 2 * lv); e.frozenUntil = this.t + (e.T.boss ? 1 : 2 + lv); });
      this.events.push({ kind: 'ability', ab: 'freeze', x: w.x, z: w.z, r });
      return hit.length;
    }
    return -1;
  }
  _wardenSpin() {
    const w = this.warden;
    if (!w || !w.alive || !(w.spinUntil > this.t) || this.t < w.spinNext) return;
    w.spinNext = this.t + 0.4;
    const r = 2.4 + 0.3 * w.spinLv;
    for (const e of this.units) if (e.alive && e.side === 'e' && dist(e, w) < r + e.T.radius) this._damage(w, e, 0.45 + 0.15 * w.spinLv);
    this.events.push({ kind: 'swing', from: w, to: w, type: 'warden' });
  }

  _pickTarget(u, foes, attackers, maxRange) {"""

UI = r"""
  // ---------- Wardens evner: knapper under kampen ----------
  const abilBar = document.createElement('div'); abilBar.className = 'abilbar'; $('.stage').appendChild(abilBar);
  abilBar.innerHTML = Object.keys(WARDEN_ABIL).map(k => `<button type="button" class="abil" data-abil="${k}" title="${WARDEN_ABIL[k].name}"><span class="ai">${WARDEN_ABIL[k].icon}</span><span class="an">${WARDEN_ABIL[k].name}</span><i class="acd"></i></button>`).join('');
  state.abilReady = {};
  function useAbility(k) {
    const lv = state.econ.warden.abil[k];
    if (!lv) { toast(`${WARDEN_ABIL[k].name} kjøpes i Warden's Sanctum (klikk flammen).`); return; }
    if (state.phase !== 'battle' || !sim) { toast('Evnene brukes under kampen.'); return; }
    if ((state.abilReady[k] || 0) > sim.t) return;
    const n = sim.wardenAbility(k, lv);
    if (n < 0) { toast('Warden kan ikke bruke evner nå.'); return; }
    state.abilReady[k] = sim.t + ABIL_CD[k][lv - 1];
    if (n === 0 && k !== 'spin') toast(`${WARDEN_ABIL[k].name}: ingen fiender nær Warden.`);
    camGoto(0, MAP.flameZ - 14, PHONE ? 46 : 36, 0.75);
  }
  abilBar.addEventListener('click', e => { const b = e.target.closest('[data-abil]'); if (b) useAbility(b.dataset.abil); });
  window.addEventListener('keydown', e => { const m = { z: 'stun', x: 'spin', c: 'freeze' }[e.key.toLowerCase()]; if (m && state.phase === 'battle' && !(e.target.closest && e.target.closest('input, select'))) useAbility(m); });
  function syncAbilBar() {
    const owned = Object.keys(WARDEN_ABIL).filter(k => state.econ.warden.abil[k]);
    abilBar.hidden = !owned.length || state.phase !== 'battle';
    if (abilBar.hidden) return;
    abilBar.querySelectorAll('[data-abil]').forEach(b => {
      const k = b.dataset.abil, lv = state.econ.warden.abil[k];
      b.hidden = !lv;
      if (!lv) return;
      const left = Math.max(0, (state.abilReady[k] || 0) - sim.t), cd = ABIL_CD[k][lv - 1];
      b.classList.toggle('cool', left > 0);
      b.style.setProperty('--p', `${(1 - left / cd) * 360}deg`);
      b.querySelector('.acd').textContent = left > 0 ? Math.ceil(left) : '';
    });
  }
"""

CSS = """
.abilbar { position: absolute; left: 12px; bottom: 12px; display: flex; gap: 8px; z-index: 6; }
.abil { position: relative; width: 64px; height: 64px; border-radius: 50%; border: 2px solid #e9a23b; background: radial-gradient(circle at 50% 40%, #3a2a12, #120c06); color: var(--fg); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0; padding: 0; overflow: hidden; box-shadow: 0 6px 16px rgba(0, 0, 0, .5); }
.abil .ai { font-size: 22px; line-height: 1; }
.abil .an { font-size: 8.5px; font-weight: 600; letter-spacing: .02em; }
.abil.cool { border-color: #4a4f58; filter: grayscale(.7); }
.abil.cool::after { content: ''; position: absolute; inset: 0; background: conic-gradient(transparent 0 var(--p), rgba(0, 0, 0, .6) var(--p) 360deg); }
.abil .acd { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font: 700 20px var(--mono); font-style: normal; color: #fff; z-index: 1; text-shadow: 0 1px 3px #000; }
@media (max-width: 600px) { .abilbar { left: 6px; bottom: 6px; gap: 6px; } .abil { width: 54px; height: 54px; } .abil .ai { font-size: 19px; } .abil .an { font-size: 7.5px; } }
"""

PICS = """Object.assign(UP_PIC, {
    stun: '<path d="M22 3 L9 22 H18 L15 37 L31 15 H21 Z" fill="#ffcf6a" stroke="#c4521b" stroke-width="1.2"/>',
    spin: '<circle cx="20" cy="20" r="13" fill="none" stroke="#e9a23b" stroke-width="2.4" stroke-dasharray="14 6"/><path d="M20 6 L23 20 L20 34 L17 20 Z" fill="#c9d3dd" stroke="#55606b"/><circle cx="20" cy="20" r="2.4" fill="#b88b45"/>',
    freeze: '<path d="M20 4 V36 M6 12 L34 28 M6 28 L34 12" stroke="#9fe0ff" stroke-width="2.4" stroke-linecap="round"/><path d="M16 7 L20 11 L24 7 M16 33 L20 29 L24 33" stroke="#9fe0ff" stroke-width="1.6" fill="none"/><circle cx="20" cy="20" r="3.2" fill="#e8f8ff"/>',
  });
  const upPic = k =>"""

def apply(s):
    s = sub(s, "const WARDEN_TRAIN", ECON, count=1) if False else s.replace("\nconst WARDEN_TRAIN", ECON, 1)
    s = sub(s, "    this.warden = { sword: 0, shield: 0, armor: 0, xp: 0 };", "    this.warden = { sword: 0, shield: 0, armor: 0, xp: 0, abil: { stun: 0, spin: 0, freeze: 0 } };")
    s = sub(s, "  buyWardenGear(k) {", "  buyWardenAbility(k) { const lv = WARDEN_ABIL[k].levels[this.warden.abil[k]]; if (!lv || !this.pay(lv.cost)) return false; this.warden.abil[k]++; return true; }\n  buyWardenGear(k) {")
    s = sub(s, "  _pickTarget(u, foes, attackers, maxRange) {", SIM)
    s = sub(s, "      if (u.burnUntil > this.t) { this._hurt", "      if (u === this.warden) this._wardenSpin();\n      if (u.burnUntil > this.t) { this._hurt")
    s = sub(s, "      else if (e.kind === 'blast') { addBlast(e.x, e.z, e.r); sfx('boom'); }",
               "      else if (e.kind === 'ability') { addBlast(e.x, e.z, e.r * 0.6, { stun: 0xffcf6a, spin: 0xe9a23b, freeze: 0x9fe0ff }[e.ab]); sfx(e.ab === 'freeze' ? 'heal' : 'boom'); if (e.ab !== 'spin') addBlast(e.x, e.z, e.r * 0.35, { stun: 0xfff1c9, freeze: 0xe8f8ff }[e.ab]); }\n"
               "      else if (e.kind === 'blast') { addBlast(e.x, e.z, e.r); sfx('boom'); }")
    # Virvelvind synes: Warden snurrer. Frosne fiender blir blå.
    s = sub(s, "      v.g.position.set(u.x, 0, u.z);\n",
               "      v.g.position.set(u.x, 0, u.z);\n"
               "      if (u.spinUntil > sim.t) v.rig.rotation.y += dt * 18; else if (u.type === 'warden') v.rig.rotation.y = 0;\n"
               "      if (u.frozenUntil != null) { const fz = u.frozenUntil > sim.t; if (fz !== !!v.frozen) { v.frozen = fz; v.rig.traverse(o => { if (o.isMesh && o.material && o.material.emissive) { if (fz) { o.userData.em = o.material; o.material = o.material.clone(); o.material.emissive.setHex(0x3aa0d0); } else if (o.userData.em) o.material = o.userData.em; } }); } }\n", count=1)
    s = sub(s, "    state.phase = 'battle'; state.paused = false; state.acc = 0;", "    state.phase = 'battle'; state.paused = false; state.acc = 0; state.abilReady = {};")
    # Sanctum: evnene som egne fliser.
    s = sub(s, "  const upPic = k =>", PICS)
    s = sub(s, "buy: nx && buyBtn('Tren', WARDEN_TRAIN.cost, 'wtrain') })])}</div>`;",
               "buy: nx && buyBtn('Tren', WARDEN_TRAIN.cost, 'wtrain') })])}\n"
               "        <h3 style=\"margin-top:6px\">Evner ${tipIcon('Brukes med knappene nede til venstre under kampen (eller Z, X, C). De lades opp igjen etter noen sekunder, og er klare ved starten av hver wave.')}</h3>\n"
               "        ${tiles(Object.keys(WARDEN_ABIL).map(k => { const A = WARDEN_ABIL[k], lv = ec.warden.abil[k], nx2 = A.levels[lv];\n"
               "          return upTile({ pic: k, name: A.name, lv, max: A.levels.length, tip: lv ? `Nå: ${A.desc(lv)}${nx2 ? ` Neste: ${A.desc(lv + 1)}` : ''}` : A.desc(1),\n"
               "            now: lv ? `Nivå ${lv}` : 'Ikke kjøpt', buy: nx2 && buyBtn(lv ? `Nivå ${lv + 1}` : 'Lær', nx2.cost, 'wabil', `data-k=\"${k}\"`) }); }))}</div>`;")
    s = sub(s, "wtrain: () => ec.trainWarden(),", "wtrain: () => ec.trainWarden(), wabil: () => ec.buyWardenAbility(k),")
    s = sub(s, "#om-remove { color: #f0a59d; }", "#om-remove { color: #f0a59d; }" + CSS)
    s = sub(s, "  // ---------- 1 mot 1: Send-fanen ----------", UI + "\n  // ---------- 1 mot 1: Send-fanen ----------")
    s = sub(s, "    syncRival(vdt); drawMinimap(dt);", "    syncRival(vdt); drawMinimap(dt); syncAbilBar();")
    # Wardens helse følger med mellom wavene (4. okt): han får 10 % tilbake i hver pause, kommer tilbake på 25 % hvis han falt,
    # og kan pleies til full helse i Sanctum for gull.
    s = sub(s, "  buyWardenAbility(k) {", "  wardenHealCost() { const m = 1 - (this.wardenHp == null ? 1 : this.wardenHp); return m > 0.005 ? { gold: Math.max(1, Math.ceil(m * 40)) } : null; }\n"
               "  healWarden() { const c = this.wardenHealCost(); if (!c || !this.pay(c)) return false; this.wardenHp = 1; return true; }\n  buyWardenAbility(k) {")
    s = sub(s, "    ec.gateHp = sim.gateHp;\n", "    ec.gateHp = sim.gateHp;\n"
               "    if (sim.warden) { const f = sim.warden.alive ? Math.max(0, sim.warden.hp) / sim.warden.maxHp : 0.25; ec.wardenHp = Math.min(1, f + (sim.warden.alive ? 0.1 : 0)); }\n")
    s = sub(s, "    buildArchers();\n", "    if (sim.warden && ec.wardenHp != null && ec.wardenHp < 1) sim.warden.hp = Math.max(1, Math.round(sim.warden.maxHp * ec.wardenHp));\n    buildArchers();\n")
    s = sub(s, '<div class="wstats"><span data-tip="HP">❤ ${W.hp}</span>',
               '<div class="xpbar" data-tip="Wardens helse. Han får 10 % tilbake i hver pause, og kommer tilbake på 25 % hvis han faller."><i style="width:${Math.round((ec.wardenHp == null ? 1 : ec.wardenHp) * 100)}%;background:linear-gradient(90deg,#3e6a2c,#8fd16a)"></i><span>❤ ${Math.round(W.hp * (ec.wardenHp == null ? 1 : ec.wardenHp))} / ${W.hp}</span></div>\n'
               '        ${ec.wardenHealCost() ? `<div style="display:flex;justify-content:flex-end">${buyBtn(\'Pleie til full helse\', ec.wardenHealCost(), \'wheal\')}</div>` : \'\'}\n'
               '        <div class="wstats"><span data-tip="Maks HP">❤ ${W.hp}</span>')
    s = sub(s, "wabil: () => ec.buyWardenAbility(k),", "wabil: () => ec.buyWardenAbility(k), wheal: () => ec.healWarden(),")
    return s
