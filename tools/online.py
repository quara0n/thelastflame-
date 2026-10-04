"""Online 1 v 1 (version 21, 4 Oct 2026). Applied by build_v2.py after ashcrow.py.
Two players with the game open in Claude meet in a room by a short code (the artifact's `room` capability; publish the
page with capabilities {room: {}}). Each phone runs its own game exactly like 1 v 1 against the computer; a RemoteRival
takes the computer rival's place. Everything that travels between the phones lives in the room's presence (one object
per player that the room shares, re-sends after a reconnect and hands to newcomers):
  out   the last batches of creatures this player sent (sequence numbers, so nothing is applied twice),
  owe   gold this player owes the other for sent creatures that broke through (a running total),
  army  the army at home between waves, bf the battlefield live during a wave (positions ×10, health 0–9, +10 at gate),
  gate, wave, tier, alive.
Arena duels are skipped online for now (both phones must see the same fight; next step).
Outside Claude, `claude.use('room')` is missing and the Send tab says online needs Claude.
Test: tools/online_test.js opens two phone-size pages against a BroadcastChannel stand-in for the room
(tools/online_mockroom.js). Serve a copy of kamptest-2 with local three.js as ton.html on localhost:8765, run it from a
folder with playwright installed. It checks lobby, Klar, sends, live view, leak gold and giving up."""
from patch import sub

CSS = """
.online .on-row { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
.online .on-row input { width: 92px; background: var(--panel-2); border: 1px solid var(--line); border-radius: 6px; color: var(--fg); padding: 6px 8px; font: 600 14px var(--mono); text-transform: uppercase; letter-spacing: .12em; }
.online .on-row button { background: transparent; border: 1px solid #a35ae0; color: #c99af0; border-radius: 6px; padding: 6px 12px; font-weight: 600; font-size: 13px; }
.online .on-row button.go { background: #a35ae0; color: #12061c; }
.online .on-code { font: 700 18px var(--mono); letter-spacing: .18em; color: #c99af0; }
.online .on-st { font-size: 12.5px; color: var(--fg); }
"""

UI = r"""
  // ---------- Online 1 mot 1 (versjon 21) ----------
  // To spillere med spillet åpent i Claude møtes i et rom med en kode. Hver telefon kjører sitt eget spill. Det som går
  // mellom dem (sendte skapninger, lekk-gull, port, hær og slagmarken live) ligger i rommets «presence».
  const NET_TYPES = Object.keys(TYPES), NET_V = NET_TYPES.length + ':' + WAVES.length;
  const NET_GONE = 120;   // sekunder borte før motspilleren taper på walkover
  const net = { lobby: null, avail: null, room: null, code: '', typed: '', peer: null, foe: null, mid: null, ready: false, rmid: '',
    out: [], seq: 0, owe: 0, got: 0, lastIn: 0, lk: 0, goneAt: 0, goneTold: false, verTold: false, last: '', tPush: 0, tRender: 0 };
  (async () => {
    try { net.lobby = window.claude && window.claude.use ? await window.claude.use('room') : null; } catch (e) { net.lobby = null; }
    net.avail = !!net.lobby; if (state.tab === 'send') renderPanel();
  })();
  // Motspilleren i stedet for computeren. Den kjører ingen kamp her; alt den vet, kommer fra rommet.
  class RemoteRival {
    constructor() {
      this.remote = true; this.alive = true; this.hold = null; this.sim = null; this.view = null; this.live = null; this.liveWave = -1;
      this.army = []; this.armyKey = ''; this.bank = 0; this.strike = false; this.why = ''; this.intent = ''; this.memo = {};
      // Gull for hans skapninger som kom gjennom porten din: skyldes ham, og står i presence til han har hentet det.
      this.ec = { add: r => { if (r && r.gold) { net.owe += r.gold; netPush(true); } } };
    }
    running() { return false; }
    // Du starter waven din: det du har lagt i kø, sendes til ham (med i hans neste wave).
    begin(wi, queue) {
      if (!queue || !queue.length) return;
      net.out.push([++net.seq, wi, queue.map(s => NET_TYPES.indexOf(s.type))]);
      if (net.out.length > 3) net.out.shift();
      netPush(true);
    }
    // Etter waven din: hvor mange av hans kom gjennom (vises hos ham).
    learn(sim) { net.lk = sim.units.filter(u => u.sent && u.sent.by === 'r' && (u.leaked || u.z > MAP.gateZ + 1.5)).length; }
  }
  // ----- Det du deler med motspilleren -----
  function netState() {
    const P = { g: 'kt2', v: NET_V };
    if (!net.mid) { P.ready = net.ready; P.rmid = net.rmid; return P; }
    const ec = state.econ, rep = state.lastReport, battle = state.phase === 'battle' && sim;
    Object.assign(P, { mid: net.mid, alive: !(state.phase === 'over' && (state.outcome === 'lost' || state.outcome === 'draw')),
      done: rep ? rep.wave : 0, lw: !!(rep && rep.win), gate: Math.round(battle ? sim.gateHp : ec.gateHp), gmax: ec.gateMax(),
      tier: ec.barracks + 1, n: state.army.length, out: net.out, owe: net.owe, lk: net.lk, ph: battle ? 'battle' : 'build' });
    if (battle) {
      P.bf = [];
      for (const u of sim.units) if (u.alive && !u.staged) {
        const ti = NET_TYPES.indexOf(u.type); if (ti < 0) continue;
        P.bf.push([u.id, ti, Math.round(u.x * 10), Math.round(u.z * 10), Math.ceil(Math.max(0, u.hp) / u.maxHp * 9) + (u.atGate ? 10 : 0)]);
      }
    } else P.army = state.army.map(a => [NET_TYPES.indexOf(a.type), a.level || 0, a.col, a.row]);
    // Presence tåler 4 KiB. Er slagmarken for stor, vises bare de første.
    const key = P.bf ? 'bf' : 'army';
    while (JSON.stringify(P).length > 3800 && P[key].length) P[key].length = Math.floor(P[key].length * 0.85);
    return P;
  }
  function netPush(now) {
    const room = net.room; if (!room) return;
    const t = performance.now(); if (!now && t - net.tPush < (state.phase === 'battle' ? 250 : 1000)) return;
    net.tPush = t;
    const P = netState(), s = JSON.stringify(P);
    if (s === net.last) return;
    net.last = s; room.presence(P).catch(() => {});
  }
  // ----- Rommet -----
  const netNewCode = () => Array.from({ length: 4 }, () => 'abcdefghjkmnpqrstuvwxyz23456789'[Math.floor(Math.random() * 31)]).join('');
  async function netJoin(code) {
    code = String(code || '').toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 6);
    if (!net.lobby) { toast('Online virker bare når spillet er åpnet i Claude.'); return; }
    if (code.length < 3) { toast('Skriv en kode på minst 3 tegn.'); return; }
    if (net.room) await netLeave(true);
    let room;
    try { room = await net.lobby.join('kt2-' + code); } catch (e) { toast('Fikk ikke koblet til rommet. Prøv igjen om litt.'); return; }
    Object.assign(net, { room, code: code.toUpperCase(), ready: false, mid: null, foe: null, peer: null, last: '', verTold: false, rmid: Math.random().toString(36).slice(2, 10) });
    room.onPeers(netPeers, () => { net.room = null; net.foe = null; toast('Mistet forbindelsen til rommet.'); renderPanel(); });
    netPush(true); renderPanel();
  }
  async function netLeave(quiet) {
    const room = net.room; if (!room) return;
    // Forlater du midt i en kamp, gir du opp: motspilleren vinner med en gang.
    if (net.mid && state.phase !== 'over') {
      state.phase = 'over'; state.outcome = 'lost'; net.last = ''; netPush(true);
      await new Promise(r => setTimeout(r, 600));
    }
    net.room = null; net.foe = null; net.mid = null; net.ready = false;
    try { await room.leave(); } catch (e) {}
    if (!quiet) { newMatch(); toast('Du forlot rommet. Neste kamp er mot computeren.'); }
  }
  function netPeers(ch) {
    const others = ch.peers.filter(p => !p.sameTab && p.presence && p.presence.g === 'kt2');
    let foe;
    if (net.mid) foe = others.find(p => p.presence.mid === net.mid) || null;
    else foe = others.find(p => p.peer === net.peer) || others.slice().sort((a, b) => a.peer < b.peer ? -1 : 1)[0] || null;
    net.peer = foe ? foe.peer : net.peer;
    net.foe = foe ? foe.presence : null;
    if (foe) { net.goneAt = 0; net.goneTold = false; }
    else if (net.mid && !net.goneAt && state.phase !== 'over') net.goneAt = performance.now();
    if (foe && foe.presence.v !== NET_V && !net.verTold) { net.verTold = true; toast('Dere har ulike versjoner av spillet. Last inn siden på nytt, begge to.'); }
    // Begge har trykket Klar: kampen starter likt på begge telefonene.
    if (!net.mid && net.ready && foe && foe.presence.ready && foe.presence.v === NET_V) netStart([net.rmid, String(foe.presence.rmid)].sort()[0]);
    else if (net.mid && foe) netApply(foe.presence);
    netRender();
  }
  // Send-fanen tegnes på nytt høyst én gang i sekundet (presence kommer fire ganger i sekundet under en wave).
  function netRender() {
    if (net.renderT) return;
    const wait = Math.max(0, 1000 - (performance.now() - net.tRender));
    net.renderT = setTimeout(() => {
      net.renderT = 0; net.tRender = performance.now();
      if (state.tab !== 'send') return;
      // Bare statuslinjen endret seg: bytt teksten, så knappene ikke tegnes på nytt mens noen trykker.
      const key = netKey(), el = document.getElementById('net-st');
      if (el && key === net.shownKey) el.textContent = netStatus(); else renderPanel();
    }, wait);
  }
  function netStart(mid) {
    newMatch();
    Object.assign(net, { mid, ready: false, out: [], seq: 0, owe: 0, got: 0, lastIn: 0, lk: 0, goneAt: 0, last: '' });
    state.versus = true; state.rival = new RemoteRival();
    sfx('horn'); toast(`Kampen mot motspilleren starter. Lykke til!`);
    netPush(true); renderPanel();
    if (net.foe) netApply(net.foe);
  }
  // Ny kamp (Spill igjen): ut av den online kampen, men bli i rommet.
  function netEndMatch() { if (net.mid) { net.mid = null; net.ready = false; net.last = ''; setTimeout(() => netPush(true), 0); } }
  // ----- Det motspilleren deler -----
  function netApply(p) {
    const r = state.rival; if (!r || !r.remote || !p) return;
    // Nye skapninger fra ham: med i din neste wave.
    let fresh = 0;
    for (const b of Array.isArray(p.out) ? p.out : []) {
      if (!Array.isArray(b) || !(b[0] > net.lastIn) || !Array.isArray(b[2])) continue;
      net.lastIn = b[0];
      for (const ti of b[2].slice(0, 24)) { const k = NET_TYPES[ti]; if (SEND[k]) { state.incoming.push({ type: k, by: 'r', price: sendPrice(k) }); fresh++; } }
    }
    if (fresh && state.phase !== 'over') {
      toast(`Motspilleren sender deg ${fresh} skapninger. De kommer i ${state.phase === 'battle' ? 'neste' : 'denne'} waven din. Se «Neste wave».`);
      if (state.phase === 'build') rebuild();
    }
    // Gull for dine som kom gjennom porten hans.
    const owe = Math.min(5000, Math.max(0, +p.owe || 0));
    if (owe > net.got) {
      const g = Math.floor(owe - net.got); net.got = owe;
      if (g > 0 && state.phase !== 'over') { state.econ.add({ gold: g }); popRes('gold', g); state.rivalRes = { leakGold: g }; toast(`Dine skapninger kom gjennom porten hans: +${g} gull.`); }
    }
    r.hold = !p.done ? null : { wave: +p.done || 0, win: !!p.lw, lost: p.alive === false, gate: +p.gate || 0, gateMax: +p.gmax || 1, army: +p.n || 0, tier: +p.tier || 1, got: 0, leaked: +p.lk || 0 };
    // Hæren hans hjemme, eller slagmarken hans live.
    if (p.ph === 'battle' && Array.isArray(p.bf)) r.sim = netLive(r, p);
    else {
      r.sim = null; r.live = null;
      const key = JSON.stringify(p.army || []);
      if (key !== r.armyKey) {
        r.armyKey = key;
        r.army = (Array.isArray(p.army) ? p.army : []).filter(a => Array.isArray(a) && TYPES[NET_TYPES[a[0]]])
          .map(a => ({ type: NET_TYPES[a[0]], level: Math.max(0, Math.min(MAX_LEVEL, +a[1] || 0)), col: +a[2] || 0, row: +a[3] || 0 }));
        r.view = new Sim(r.army, { types: TYPES, enemies: [], gateHp: +p.gate || 1, gateMax: +p.gmax || 1, archers: 0 });
      }
    }
    if (p.alive === false && r.alive) { r.alive = false; netFoeDown(false); }
  }
  // Slagmarken hans: enhetene glir mot siste kjente plass (oppdateres fire ganger i sekundet).
  function netLive(r, p) {
    if (!r.live || r.liveWave !== p.done) { r.live = { units: [], byId: new Map(), events: [], gateHp: 0, gateMax: 1 }; r.liveWave = p.done; }
    const L = r.live, seen = new Set();
    L.gateHp = +p.gate || 0; L.gateMax = +p.gmax || 1;
    for (const a of p.bf) {
      if (!Array.isArray(a)) continue;
      const id = a[0], k = NET_TYPES[a[1]], T = TYPES[k]; if (!T) continue;
      seen.add(id);
      let u = L.byId.get(id);
      if (!u || u.type !== k) { u = { id, type: k, T, side: T.side === 'p' ? 'p' : 'e', x: a[2] / 10, z: a[3] / 10, facing: T.side === 'p' ? Math.PI : 0, alive: true, moving: false }; L.byId.set(id, u); L.units.push(u); }
      u.tx = a[2] / 10; u.tz = a[3] / 10; u.atGate = a[4] >= 10; u.alive = true;
    }
    for (const u of L.units) if (u.alive && !seen.has(u.id)) u.alive = false;
    return L;
  }
  function netFoeDown(walkover) {
    if (state.phase === 'over') return;
    toast(walkover ? 'Motspilleren er borte. Du vinner på walkover.' : 'Motspillerens flamme falt!');
    if (state.phase !== 'battle') {
      state.phase = 'over'; state.outcome = 'won-vs'; sfx('victory'); hideArenaCard();
      const el = $('#result'); el.hidden = false; el.className = 'result win';
      el.innerHTML = `<div class="r-head"><h2>Seier! ${walkover ? 'Motspilleren ga opp' : 'Motspillerens flamme falt'}</h2></div><p class="note">Trykk «Spill igjen» for en ny kamp, eller «Klar» i Send-fanen for omkamp.</p>`;
    }
    netPush(true); renderPanel();
  }
  // Hver frame: gli hans enheter på plass, del din tilstand, og se etter om han er borte.
  function netTick(dt) {
    if (!net.room) return;
    const L = state.rival && state.rival.remote && state.rival.sim;
    if (L) for (const u of L.units) if (u.alive && u.tx != null) {
      const dx = u.tx - u.x, dz = u.tz - u.z, d = Math.hypot(dx, dz), k = Math.min(1, dt * 5);
      u.moving = d > 0.05; if (d > 0.08) u.facing = Math.atan2(dx, dz);
      if (d > 12) { u.x = u.tx; u.z = u.tz; } else { u.x += dx * k; u.z += dz * k; }
    }
    netPush(false);
    if (net.mid && net.goneAt && state.phase !== 'over') {
      const gone = (performance.now() - net.goneAt) / 1000;
      if (gone > 10 && !net.goneTold) { net.goneTold = true; toast(`Motspilleren er borte. Kommer han ikke tilbake innen ${Math.round(NET_GONE / 60)} minutter, vinner du.`); }
      if (gone > NET_GONE) { net.goneAt = 0; state.rival.alive = false; netFoeDown(true); }
    }
  }
  function netClick(what) {
    if (what === 'create') netJoin(netNewCode());
    else if (what === 'join') netJoin(net.typed || ($('#net-code') || {}).value);
    else if (what === 'ready') { net.ready = true; net.last = ''; netPush(true); renderPanel(); if (net.foe && net.foe.ready) netPeers({ peers: net.room.peers() }); }
    else if (what === 'unready') { net.ready = false; net.last = ''; netPush(true); renderPanel(); }
    else if (what === 'leave') netLeave(false);
  }
  document.addEventListener('input', e => { if (e.target.id === 'net-code') net.typed = e.target.value; });
  document.addEventListener('keydown', e => { if (e.target.id === 'net-code' && e.key === 'Enter') { e.preventDefault(); netJoin(e.target.value); } });
  function onlineHtml() {
    if (net.avail === null) return '';
    const tip = tipIcon('Dere spiller hvert deres spill med de samme wavene og sender skapninger til hverandre, akkurat som mot computeren. Den som mister flammen først, taper. Arenaen er ikke med online ennå.');
    if (!net.avail) return `<section class="online"><h2>Spill online ${tip}</h2><p class="note">Online 1 mot 1 virker når spillet er åpnet i Claude. Her spiller du mot computeren.</p></section>`;
    if (!net.room) return `<section class="online"><h2>Spill online ${tip}</h2>
        <div class="on-row"><button type="button" class="go" data-net="create">Lag rom</button><span class="on-st">eller</span>
          <input id="net-code" maxlength="6" placeholder="KODE" autocomplete="off" autocapitalize="characters" value="${(net.typed || '').replace(/[^a-z0-9]/gi, '')}"><button type="button" data-net="join">Bli med</button></div>
        <p class="note">Motspilleren må være logget inn i Claude og ha fått tilgang til spillet gjennom Del-menyen. Du kan teste alene med telefon og PC på samme konto.</p></section>`;
    net.shownKey = netKey();
    const f = net.foe;
    const btn = net.mid ? '' : f ? (net.ready ? '<button type="button" data-net="unready">Ikke klar</button>' : '<button type="button" class="go" data-net="ready">Klar</button>') : '';
    return `<section class="online"><h2>Spill online ${tip}</h2>
        <div class="on-row"><span class="on-st">Rom</span><span class="on-code">${net.code}</span>${btn}<button type="button" data-net="leave">${net.mid && state.phase !== 'over' ? 'Gi opp' : 'Forlat rommet'}</button></div>
        <p class="on-st" id="net-st">${netStatus()}</p>${!net.mid ? '<p class="note">Når begge trykker Klar, starter en ny kamp fra wave 1 hos begge.</p>' : ''}</section>`;
  }
  // Det som avgjør hvilke knapper som vises. Endres det, tegnes Send-fanen på nytt.
  const netKey = () => [!!net.room, !!net.foe, net.ready, !!(net.foe && net.foe.ready), net.mid, state.phase === 'over'].join();
  function netStatus() {
    const f = net.foe, h = state.rival && state.rival.remote ? state.rival.hold : null;
    return net.mid && state.phase === 'over' ? 'Kampen er over. Trykk «Spill igjen» og så Klar for omkamp.' : net.mid ? (f ? `Kamp pågår. Motspilleren: ${h ? `ferdig med wave ${h.wave}, port ${h.gate}/${h.gateMax}, ${h.army} soldater, Tier ${h.tier}` : 'har ikke kjempet ennå'}${f.ph === 'battle' ? ' (kjemper nå)' : ''}.` : 'Motspilleren er borte fra rommet. Venter …')
      : !f ? 'Venter på motspiller. Gi dem koden.' : net.ready ? (f.ready ? 'Starter …' : 'Venter på at motspilleren trykker Klar.') : f.ready ? 'Motspilleren er klar. Trykk Klar for å starte.' : 'Motspilleren er her. Trykk Klar når du vil starte.';
  }
"""

def apply(s):
    s = sub(s, "#om-remove { color: #f0a59d; }", "#om-remove { color: #f0a59d; }" + CSS)
    s = sub(s, "  // ---------- 1 mot 1: Send-fanen ----------", UI + "\n  // ---------- 1 mot 1: Send-fanen ----------")
    # Send-fanen: online øverst, og rivalen heter motspiller når han er et menneske.
    s = sub(s, "$('#pane-send').innerHTML = `<section class=\"rival\"><div class=\"rv-h\"><b>Rival: computer</b>",
               "$('#pane-send').innerHTML = onlineHtml() + `<section class=\"rival\"><div class=\"rv-h\"><b>${r.remote ? 'Motspiller (online)' : 'Rival: computer'}</b>")
    # Ikke tegn Send-fanen på nytt mens du skriver inn koden.
    s = sub(s, "    if (state.tab === 'send') renderSend();\n    // Hær", "    if (state.tab === 'send' && !(document.activeElement && document.activeElement.id === 'net-code')) renderSend();\n    // Hær")
    s = sub(s, "  function onUiClick(e) {\n",
               "  function onUiClick(e) {\n"
               "    const nb = e.target.closest('[data-net]'); if (nb) { netClick(nb.dataset.net); return; }\n"
               "    if (e.target.closest('#vs-toggle') && state.rival.remote) { e.target.checked = true; toast('Online-kampen er alltid 1 mot 1.'); return; }\n")
    # Ingen 1 mot 1-bryter og ingen arena online ennå.
    s = sub(s, '<label class="vs-tog">', '<label class="vs-tog" ${r.remote ? \'style="display:none"\' : \'\'}>')
    s = sub(s, '<p class="note">Champion-flagg: du ${state.flags}, rivalen ${state.rivalFlags}. ${(() =>', '<p class="note" ${state.rival.remote ? \'style="display:none"\' : \'\'}>Champion-flagg: du ${state.flags}, rivalen ${state.rivalFlags}. ${(() =>')
    s = sub(s, "&& state.army.length && state.rival.army.length) startArena(W.n);", "&& state.army.length && state.rival.army.length && !state.rival.remote) startArena(W.n);")
    # Ny kamp: ut av online-kampen.
    s = sub(s, "    clearRivalVisuals(); rivalVisSim = null;\n    state.rival = new Rival();", "    netEndMatch();\n    clearRivalVisuals(); rivalVisSim = null;\n    state.rival = new Rival();")
    s = sub(s, "    syncRival(vdt); drawMinimap(dt);", "    syncRival(vdt); drawMinimap(dt); netTick(dt);")
    # Feilsøking (#dbg): se rommet.
    s = sub(s, "window.__dbg = {", "window.__dbg = { net: () => net,")
    return s
