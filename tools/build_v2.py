"""Build proto_v2.html: per-unit upgrades, the scarce economy and visible gear, on top of the combat prototype."""
import re, pathlib
from patch import patch, sub

HERE = pathlib.Path(__file__).parent
src = (HERE / '../prototype/kamptest-1.html').read_text()
s = patch(src)

# ---------- Economy: small numbers, scarcity ----------
econ_start = s.index('// ===== The Last Flame — økonomi for North')
econ_end = s.index('class Econ {', econ_start)
block = s[econ_start:econ_end]
block = re.sub(r'gold: (\d+)', lambda m: f'gold: {max(1, round(int(m.group(1)) * 0.6))}', block)
block = sub(block, "const WORKER_BASE = 15, WORKER_FREE = 10, WORKER_STEP = 5;", "const WORKER_BASE = 5, WORKER_FREE = 10, WORKER_STEP = 2;")
block = sub(block, "gold:   { name: 'Gullgruve',  res: 'gold',   yield: 1, every: 5, cap: 6 },", "gold:   { name: 'Gullgruve',  res: 'gold',   yield: 1, every: 8, cap: 6 },")
block = sub(block, "const waveBonus = w => 10 + 3 * Math.min(w, 10) + Math.max(0, w - 10);", "const waveBonus = w => 6 + 2 * Math.min(w, 10) + Math.max(0, w - 10);")
for a, b in [("supply: 30,", "supply: 20,"), ("supply: 45,", "supply: 30,"), ("supply: 60,", "supply: 40,"), ("supply: 75,", "supply: 50,"), ("supply: 90,", "supply: 60,")]:
    block = sub(block, a, b)
s = s[:econ_start] + block + s[econ_end:]
s = sub(s, "this.res = { gold: 125, timber: 15, stone: 15, iron: 0, coal: 0 };", "this.res = { gold: 75, timber: 15, stone: 15, iron: 0, coal: 0 };")

# ---------- Gear: each upgrade shows on the soldier ----------
s = sub(s, """    const r = new THREE.Mesh(GEO.ring, u.side === 'p' ? (ringMats[u.order] || ringMats.warden) : ringMats.enemy);""",
"""    if (u.side === 'p' && u.level) addGear(rig, u.level, height / (rig.scale.y || 1));
    const r = new THREE.Mesh(GEO.ring, u.side === 'p' ? (ringMats[u.order] || ringMats.warden) : ringMats.enemy);""")
s = sub(s, """  let visuals = new Map();""", """  // Oppgraderinger synes på soldaten: skulderplater, så kappe, så en glødende kam. Gull-ruter over hodet viser nivået.
  const pipMat = new THREE.MeshBasicMaterial({ color: 0xffc766 });
  const padGeo = new THREE.SphereGeometry(0.17, 8, 6, 0, Math.PI * 2, 0, Math.PI / 2), pipGeo = new THREE.OctahedronGeometry(0.09);
  function addGear(rig, lv, h) {
    const sh = h * 0.66;
    if (lv >= 1) [-1, 1].forEach(s => { const p = mesh(padGeo, mats.steelLight, s * 0.4, sh, 0); p.scale.set(1, 0.75, 1.15); rig.add(p); });
    if (lv >= 2) rig.add(mesh(new THREE.BoxGeometry(0.62, h * 0.5, 0.05), mats.flag, 0, sh - h * 0.25, -0.32));
    if (lv >= 3) rig.add(mesh(new THREE.ConeGeometry(0.09, 0.32, 6), mats.pilot, 0, h + 0.12, 0));
    for (let i = 0; i < lv; i++) { const p = mesh(pipGeo, pipMat, (i - (lv - 1) / 2) * 0.24, h + 0.42, 0); p.castShadow = false; rig.add(p); }
  }
  let visuals = new Map();""")

# ---------- Refunds include what was spent on upgrades ----------
s = sub(s, "function refundOf(type) { const p = state.econ.unitPrice(TYPES[type]), b = {}; for (const r in p) b[r] = Math.floor(p[r] * REFUND); return b; }",
"""function refundOf(a) {
    const type = a.type || a, p = Object.assign({}, state.econ.unitPrice(TYPES[type])), up = upgradeSpent(type, a.level || 0), b = {};
    for (const r in up) p[r] = (p[r] || 0) + up[r];
    for (const r in p) b[r] = Math.floor(p[r] * REFUND);
    return b;
  }""")
s = sub(s, "function refund(type) { const b = refundOf(type);", "function refund(a) { const b = refundOf(a);")
s = sub(s, "refund(ex.type); }", "refund(ex); }", count=2)
s = sub(s, "back = ex ? refundOf(ex.type) : {};", "back = ex ? refundOf(ex) : {};")
s = sub(s, "state.army.forEach((a, i) => { if (state.selection.has(i)) refund(a.type); });", "state.army.forEach((a, i) => { if (state.selection.has(i)) refund(a); });")

# ---------- Upgrade button in the order bar ----------
s = sub(s, """      <div class="om-orders" id="om-orders"></div>""", """      <div class="om-orders" id="om-orders"></div>
      <div class="om-up"><button type="button" id="om-upbtn">Oppgrader</button><span id="om-updesc"></span></div>""")
s = sub(s, "#om-remove { color: #f0a59d; }", """#om-remove { color: #f0a59d; }
.om-up { flex: 1 1 100%; display: flex; align-items: center; gap: 10px; border-top: 1px solid var(--line); padding-top: 8px; min-width: 0; }
.om-up button { flex: none; background: var(--flame); color: var(--flame-ink); border: 1px solid var(--flame); border-radius: 6px; padding: 7px 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 8px; }
.om-up button .cost { color: var(--flame-ink); }
.om-up button:disabled { background: var(--panel-2); color: var(--muted); border-color: var(--line); }
.om-up button.cant { background: transparent; color: var(--flame); }
.om-up span { font-size: 12px; color: var(--muted); min-width: 0; }
.lvpips { display: inline-flex; gap: 2px; margin-left: 6px; vertical-align: middle; }
.lvpips i { width: 6px; height: 6px; transform: rotate(45deg); border: 1px solid #ffc766; }
.lvpips i.on { background: #ffc766; }""")
s = sub(s, """    $('#om-together').checked = state.together;
    menu.hidden = false;""", """    $('#om-together').checked = state.together;
    syncUpgradeBtn();
    menu.hidden = false;""")
s = sub(s, """  function clearSelection(silent) {""", """  // Oppgradering av valgte units: hver får sitt neste nivå. Prisen er summen for alle som kan oppgraderes.
  function upgradePlan() {
    const list = [...state.selection].map(i => state.army[i]).filter(a => a && UPGRADES[a.type] && (a.level || 0) < MAX_LEVEL);
    const cost = {};
    list.forEach(a => { const c = UPGRADES[a.type][a.level || 0].cost; for (const r in c) cost[r] = (cost[r] || 0) + c[r]; });
    return { list, cost };
  }
  function syncUpgradeBtn() {
    const btn = $('#om-upbtn'), desc = $('#om-updesc'), { list, cost } = upgradePlan();
    if (!list.length) { btn.disabled = true; btn.textContent = 'Fullt oppgradert'; desc.textContent = 'Alle valgte har nådd nivå 3.'; return; }
    btn.disabled = false;
    const one = list.length === 1 || list.every(a => a.type === list[0].type && (a.level || 0) === (list[0].level || 0));
    const up = UPGRADES[list[0].type][list[0].level || 0];
    btn.innerHTML = `${one ? `Oppgrader: ${up.name}` : `Oppgrader ${list.length} units`} <span class="cost">${costHtml(cost)}</span>`;
    btn.classList.toggle('cant', !state.econ.can(cost));
    desc.textContent = one ? `Nivå ${(list[0].level || 0) + 1} av 3${list.length > 1 ? ` for ${list.length} ${TYPES[list[0].type].name}` : ''}. ${up.desc}` : 'Hver valgt unit får sitt neste nivå.';
  }
  function costHtml(c) { return Object.keys(c).map(r => `${icon(r, 13)}${c[r]}`).join(' '); }
  function upgradeSelected() {
    const { list, cost } = upgradePlan();
    if (!list.length) return;
    if (!state.econ.can(cost)) { explainMissing(cost); return; }
    state.econ.pay(cost);
    const first = list[0], name = UPGRADES[first.type][first.level || 0].name;
    list.forEach(a => { a.level = (a.level || 0) + 1; });
    toast(list.length === 1 ? `${TYPES[first.type].name} fikk ${name}.` : `${list.length} units ble oppgradert.`);
    sfx('coin');
    rebuild(); selectionChanged();
  }
  function clearSelection(silent) {""")
s = sub(s, """    $('#om-remove').onclick = removeSelected;""", """    $('#om-remove').onclick = removeSelected;
    $('#om-upbtn').onclick = upgradeSelected;""")

# ---------- Hover card shows the level ----------
s = sub(s, """        <div class="ir">${T.role}</div>""", """        <div class="ir">${T.role}${!foe && UPGRADES[u.type] ? ` · Nivå ${u.level || 0}/3` : ''}</div>""")
import json
K = json.load(open(HERE / 'wave_factors.json'))
s = sub(s, "const WORLDS = { 1:", "// Styrkefaktor per wave, målt med hele spill simulert mot en fornuftig spiller (3. okt 2026).\nconst WAVE_FACTOR = " + json.dumps(K) + ";\nWAVES.forEach((w, i) => { const k = WAVE_FACTOR[i] || 1; w.scale = { hp: +(w.scale.hp * k).toFixed(3), dmg: +(w.scale.dmg * Math.sqrt(k)).toFixed(3) }; });\nconst WORLDS = { 1:")
s = sub(s, "<title>Last Flame Kamptest</title>", "<title>Last Flame Kamptest II</title>")
s = sub(s, '<div class="eyebrow">Prototype · milepæl A–C · North</div>', '<div class="eyebrow">Prototype · milepæl A–D · oppgraderinger</div>')
s = sub(s, '<p class="note">«+ Plasser» kjøper units i byggefasen. Fjerner du en, får du tilbake 75 % av gullet, rundet ned.</p>',
  '<p class="note">«+ Plasser» kjøper units i byggefasen. Velg en unit på kartet og trykk «Oppgrader» for å gjøre akkurat den soldaten sterkere (tre nivåer). Fjerner du en, får du tilbake 75 % av alt du brukte på den, rundet ned.</p>')
# Warden jager også fiender som skyter på ham (3. okt 2026). Før sto skyttere rett utenfor
# flamme-sirkelen og drepte ham mens han gikk hjem igjen.
s = sub(s, """      const near = enemies.filter(e => Math.hypot(e.x - 0, e.z - MAP.flameZ) < MAP.flameReach + 9);
      if (near.length) { if (!this.wardenFought) { this.wardenFought = true; this.events.push({ kind: 'warden' }); } if (this._engage(u, near, attackers, dt, 9)) return; }""",
"""      const near = enemies.filter(e => Math.hypot(e.x - 0, e.z - MAP.flameZ) < MAP.flameReach + 9 || (e.target === u && dist(e, u) < 16));
      if (near.length) { if (!this.wardenFought) { this.wardenFought = true; this.events.push({ kind: 'warden' }); } if (this._engage(u, near, attackers, dt, 16)) return; }""")
import world3
s = world3.apply(s)
import tier_power
s = tier_power.apply(s)
import mobile
s = mobile.apply(s)
import music
s = music.apply(s)
import economy
s = economy.apply(s)
import tier_cap
s = tier_cap.apply(s)
import tier_chips
s = tier_chips.apply(s)
import waves30
s = waves30.apply(s)
import versus
s = versus.apply(s)
import arena
s = arena.apply(s)
import rival_view
s = rival_view.apply(s)
import select_info
s = select_info.apply(s)
import warden_nerf
s = warden_nerf.apply(s)
import warden_abilities
s = warden_abilities.apply(s)
import forge_gate
s = forge_gate.apply(s)
import ashcrow
s = ashcrow.apply(s)
import online
s = online.apply(s)
import scarcity
s = scarcity.apply(s)
import bastion
s = bastion.apply(s)
import biomes
s = biomes.apply(s)
import hero
s = hero.apply(s)
import ui_tidy
s = ui_tidy.apply(s)
(HERE / '../prototype/kamptest-2.html').write_text(s)
print('ok', len(s))
