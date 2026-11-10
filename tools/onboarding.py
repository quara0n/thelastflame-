# Enklere vei inn i online 1 mot 1 (versjon 35).
# - Alle som har spillet åpent, står i en lobby (rommets presence). Vennen din dukker opp med navn og en «Utfordre»-knapp,
#   han får et kort med «Spill» / «Ikke nå», og kampen starter hos begge uten kode og uten Klar.
# - «Spill mot en venn»-knapp øverst i panelet, velkomstkort første gang, og en kort «Slik inviterer du en venn».
# - Kode-rommet fra versjon 21 er fortsatt der, under «Spill med kode i stedet».
from patch import sub

GAME_URL = 'https://claude.ai/artifact/4h6eEwfWuJEPxzigKGvk3V'

CSS = r"""
.vsbtn { margin-top: 10px; width: 100%; background: #a35ae0; color: #12061c; border: 0; border-radius: 8px; padding: 10px 12px; font-weight: 700; font-size: 15px; display: flex; justify-content: center; align-items: center; gap: 8px; }
.vsbtn em { font-style: normal; font-weight: 600; font-size: 12px; background: #12061c; color: #c99af0; border-radius: 999px; padding: 1px 8px; }
.vsbtn em:empty { display: none; }
.lob-list { display: flex; flex-direction: column; gap: 6px; }
.lob-p { display: flex; align-items: center; gap: 10px; background: var(--panel-2); border: 1px solid #5a3a7a; border-radius: 8px; padding: 8px 10px; }
.lob-p > span { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.lob-p b { font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lob-p small { font-size: 12px; color: var(--muted); }
.lob-p button, .lob-btn { background: #a35ae0; color: #12061c; border: 0; border-radius: 6px; padding: 8px 14px; font-weight: 700; flex: none; }
.lob-p button:disabled { background: var(--panel); color: var(--muted); }
.online .on-row input#lob-name { width: 150px; text-transform: none; letter-spacing: 0; font: 500 14px var(--body); }
.online details { border-top: 1px solid var(--line); padding-top: 8px; }
.online summary { cursor: pointer; font-size: 13px; font-weight: 600; color: #c99af0; }
.online details[open] summary { margin-bottom: 8px; }
.online ol { margin: 0 0 8px; padding-left: 20px; font-size: 13px; display: flex; flex-direction: column; gap: 6px; }
.online ol b { color: var(--fg); }
.lob-btn.ghost { background: transparent; border: 1px solid #a35ae0; color: #c99af0; }
.invcard { position: fixed; z-index: 70; left: 50%; top: 50%; transform: translate(-50%, -50%); width: min(360px, calc(100% - 24px)); max-height: calc(100dvh - 24px); overflow-y: auto;
  background: linear-gradient(180deg, #24123a, #120a1c); border: 1px solid #a35ae0; border-radius: 14px; padding: 18px 16px 16px; text-align: center; display: flex; flex-direction: column; gap: 10px;
  box-shadow: 0 0 0 100vmax rgba(0, 0, 0, .55), 0 20px 50px rgba(0, 0, 0, .6); color: var(--fg); }
.invcard .ic-eye { font: 600 11px var(--body); letter-spacing: .16em; text-transform: uppercase; color: #c99af0; }
.invcard h2 { font-family: var(--display); font-size: 22px; letter-spacing: .03em; text-transform: none; color: var(--fg); margin: 0; }
.invcard p { margin: 0; font-size: 13.5px; color: var(--muted); }
.invcard .ic-row { display: flex; flex-direction: column; gap: 8px; margin-top: 4px; }
.invcard .ic-row button { border-radius: 8px; padding: 12px; font-weight: 700; font-size: 15px; border: 0; }
.invcard .ic-go { background: #a35ae0; color: #12061c; }
.invcard .ic-cpu { background: var(--flame); color: var(--flame-ink); }
.invcard .ic-no { background: transparent; border: 1px solid var(--line) !important; color: var(--muted); font-weight: 600 !important; }
"""

JS = r"""
  // ---------- Lobby: spill mot en venn uten kode (versjon 35) ----------
  // Alle med spillet åpent står i rommets presence med navn. Trykker du «Utfordre», lager spillet et rom og legger
  // invitasjonen i presence; vennen får et kort, og når han sier ja, går begge inn og er klare med en gang.
  const GAME_URL = '__GAME_URL__';
  const store = { get: k => { try { return localStorage.getItem(k); } catch (e) { return null; } }, set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} } };
  const lob = { room: null, me: null, peers: [], name: store.get('kt2-name') || '', inv: null, nope: null, seen: new Set(), first: true, declined: new Set(), shown: null, sent: '' };
  const esc = t => String(t == null ? '' : t).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const lobName = p => esc(String((p && p.presence && p.presence.nm) || 'En spiller').slice(0, 14));
  const lobOthers = () => lob.peers.filter(p => !p.sameTab && p.kind !== 'agent' && p.presence && p.presence.g === 'kt2l');
  function lobSet() {
    if (!lob.room) return;
    const P = { g: 'kt2l', v: NET_V, nm: (lob.name || '').slice(0, 14), busy: !!net.mid, inv: lob.inv, nope: lob.nope };
    const s = JSON.stringify(P); if (s === lob.sent) return;
    lob.sent = s; lob.room.presence(P).catch(() => {});
  }
  (async () => {
    let L = null;
    try { L = window.claude && window.claude.use ? await window.claude.use('room') : null; } catch (e) { L = null; }
    if (!L) return;
    lob.room = L; lobSet();
    L.onPeers(ch => {
      lob.peers = ch.peers || [];
      const me = lob.peers.find(p => p.sameTab); if (me) lob.me = me.peer;
      const others = lobOthers();
      // Noen åpnet spillet nå (ikke de som var her da du kom).
      for (const p of others) if (!lob.seen.has(p.peer)) { lob.seen.add(p.peer); if (!lob.first && !net.mid) toast(`${lobName(p)} har åpnet spillet. Trykk «Spill mot en venn» for å utfordre.`); }
      lob.first = false;
      // Svar på din utfordring.
      if (lob.inv) {
        const to = others.find(p => p.peer === lob.inv.to);
        if (!to) { toast('Den du utfordret, lukket spillet.'); lobCancel(); }
        else if (to.presence.nope === lob.inv.c) { toast(`${lobName(to)} vil ikke spille akkurat nå.`); lobCancel(); }
      }
      lobInviteCheck(others);
      lobBadge();
      // Bare lista tegnes på nytt, så navnefeltet ikke mister det du skriver.
      const wrap = document.getElementById('lob-wrap');
      if (state.tab === 'send' && !net.room && wrap) wrap.innerHTML = lobListHtml();
    }, () => { lob.room = null; lob.peers = []; lobBadge(); });
  })();
  setInterval(lobSet, 3000);   // «i en kamp» følger med uten egne kall overalt
  function lobBadge() {
    const el = document.getElementById('vs-online'); if (!el) return;
    const n = lobOthers().length; el.textContent = n ? `${n} online` : '';
  }
  async function lobChallenge(peer) {
    const p = lobOthers().find(o => o.peer === peer); if (!p) return;
    if (p.presence.v !== NET_V) { toast('Dere har ulike versjoner av spillet. Last inn siden på nytt, begge to.'); return; }
    if (!lob.name) { lob.name = 'Spiller'; }
    const code = netNewCode();
    lob.inv = { to: peer, c: code, nm: lobName(p) }; lobSet();
    await netJoin(code);
    if (!net.room) { lobCancel(); return; }
    net.ready = true; net.last = ''; netPush(true); renderPanel();
  }
  function lobCancel() {
    lob.inv = null; lobSet();
    if (net.room && !net.mid) { netLeave(true).then(() => renderPanel()); } else renderPanel();
  }
  async function lobAccept(inv) {
    lob.declined.add(inv.c); lobHideCard(); lob.nope = null;
    await netJoin(inv.c);
    if (!net.room) return;
    net.ready = true; net.last = ''; netPush(true); renderPanel();
    if (net.foe && net.foe.ready) netPeers({ peers: net.room.peers() });
  }
  function lobDecline(inv) { lob.declined.add(inv.c); lob.nope = inv.c; lobSet(); lobHideCard(); }
  function lobInviteCheck(others) {
    if (lob.shown && !others.some(p => p.presence.inv && p.presence.inv.c === lob.shown.c && p.presence.inv.to === lob.me)) lobHideCard();
    if (lob.shown || !lob.me || net.mid || lob.inv) return;
    const from = others.find(p => p.presence.inv && p.presence.inv.to === lob.me && !lob.declined.has(p.presence.inv.c));
    if (!from) return;
    const inv = { c: String(from.presence.inv.c || '').slice(0, 6), from: lobName(from) };
    if (inv.c.length < 3) return;
    lob.shown = inv; sfx('horn');
    const midGame = state.phase === 'battle' || (state.lastReport && state.phase !== 'over');
    lobShowCard(`<div class="ic-eye">Utfordring</div><h2>${inv.from} vil spille mot deg</h2>
      <p>Dere spiller hvert deres spill med de samme wavene og sender skapninger til hverandre. Den som mister flammen først, taper.</p>
      ${midGame ? '<p>Kampen du er i nå, avsluttes.</p>' : ''}
      <div class="ic-row"><button type="button" class="ic-go" data-ic="yes">Spill mot ${inv.from}</button><button type="button" class="ic-no" data-ic="no">Ikke nå</button></div>`);
  }
  let icEl = null;
  function lobShowCard(html) { lobHideCard(true); icEl = document.createElement('div'); icEl.className = 'invcard'; icEl.innerHTML = html; document.body.appendChild(icEl); }
  function lobHideCard(keep) { if (icEl) { icEl.remove(); icEl = null; } if (!keep) lob.shown = null; }
  function lobDone() { if (lob.inv || lob.nope) { lob.inv = null; lob.nope = null; } lobSet(); }
  async function lobShare() {
    const text = `Bli med og spill The Last Flame mot meg! Åpne lenken, trykk «Spill mot en venn» og velg meg. ${GAME_URL}`;
    try { if (navigator.share) { await navigator.share({ title: 'The Last Flame', text, url: GAME_URL }); return; } } catch (e) { if (e && e.name === 'AbortError') return; }
    try { await navigator.clipboard.writeText(text); toast('Lenken er kopiert. Lim den inn til vennen din.'); return; } catch (e) {}
    toast('Lenken: ' + GAME_URL);
  }
  function lobWaitText() {
    return lob.inv ? `Venter på svar fra ${lob.inv.nm} …` : 'Venter på motspiller. Gi dem koden.';
  }
  function lobbyHtml(tip, codeHtml) {
    const others = lobOthers(), row = (codeHtml.match(/<div class="on-row">[\s\S]*?<\/div>/) || [''])[0];
    return `<section class="online"><h2>Spill mot en venn ${tip}</h2>
        <div class="on-row"><span class="on-st">Ditt navn</span><input id="lob-name" maxlength="14" placeholder="Skriv navnet ditt" autocomplete="off" value="${esc(lob.name)}"></div>
        <div id="lob-wrap">${lobListHtml()}</div>
        <details${others.length ? '' : ' open'}><summary>Slik inviterer du en venn</summary><ol>
          <li>Trykk <b>Del</b> øverst på siden i Claude og inviter vennen din <b>på e-post</b>. Ikke velg «alle med lenken», da kommer han ikke inn.</li>
          <li>Han trenger en Claude-konto. Gratis holder. Han åpner lenken i e-posten.</li>
          <li>Når han har spillet åpent, står navnet hans her. Trykk <b>Utfordre</b>, så får han spørsmål om å spille.</li></ol>
          <button type="button" class="lob-btn ghost" data-lob-share>Send lenken til spillet</button></details>
        <details><summary>Spill med kode i stedet</summary>${row}<p class="note">Den ene lager rom og gir koden til den andre. Begge trykker Klar.</p></details></section>`;
  }
  function lobListHtml() {
    const others = lobOthers();
    return !lob.room ? '<p class="on-st">Kobler til …</p>' : others.length ? `<div class="lob-list">${others.map(p => {
      const old = p.presence.v !== NET_V, busy = !!p.presence.busy;
      return `<div class="lob-p"><span><b>${lobName(p)}</b><small>${old ? 'Har en annen versjon. Begge må laste inn siden på nytt.' : busy ? 'Er i en kamp nå' : 'Har spillet åpent nå'}</small></span><button type="button" data-lob="${esc(p.peer)}"${old || busy ? ' disabled' : ''}>Utfordre</button></div>`;
    }).join('')}</div>` : '<p class="on-st">Ingen andre har spillet åpent akkurat nå. Når vennen din åpner det, står navnet hans her.</p>';
  }
  document.addEventListener('input', e => { if (e.target.id === 'lob-name') { lob.name = e.target.value.slice(0, 14); store.set('kt2-name', lob.name); lobSet(); } });
  document.addEventListener('click', e => {
    const ch = e.target.closest('[data-lob]'); if (ch && !ch.disabled) { lobChallenge(ch.dataset.lob); return; }
    if (e.target.closest('[data-lob-share]')) { lobShare(); return; }
    if (e.target.closest('[data-lob-cancel]')) { lobCancel(); return; }
    const ic = e.target.closest('[data-ic]'); if (!ic) return;
    const v = ic.dataset.ic, inv = lob.shown;
    if (v === 'yes' && inv) lobAccept(inv);
    else if (v === 'no' && inv) lobDecline(inv);
    else if (v === 'cpu') { lobHideCard(); store.set('kt2-hello', '1'); }
    else if (v === 'friend') { lobHideCard(); store.set('kt2-hello', '1'); state.tab = 'send'; renderPanel(); lobScroll(); }
  });
  function lobScroll() { setTimeout(() => { const el = document.querySelector('#pane-send .online'); if (el && el.scrollIntoView) el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 50); }
  // Første gang: velg motstander.
  setTimeout(() => {
    if (store.get('kt2-hello') || icEl || net.mid) return;
    lobShowCard(`<div class="ic-eye">Velkommen</div><h2>The Last Flame</h2>
      <p>Hold porten mot tretti waves. Arbeiderne samler ressurser mens du kjøper soldater og oppgraderer dem mellom wavene.</p>
      <p>Du har en motstander som sender skapninger til deg, og du kan sende til ham i Send-fanen.</p>
      <div class="ic-row"><button type="button" class="ic-cpu" data-ic="cpu">Spill mot computeren</button><button type="button" class="ic-go" data-ic="friend">Spill mot en venn</button></div>`);
  }, 900);
"""

def apply(s):
    s = sub(s, '</style>\n\n<div class="app">', CSS + '</style>\n\n<div class="app">')
    s = sub(s, 'Klikk på bygningene i landsbyen for å bruke dem.</p>',
               'Klikk på bygningene i landsbyen for å bruke dem.</p>\n      <button type="button" class="vsbtn" data-tab="send" data-vs>⚔ Spill mot en venn <em id="vs-online"></em></button>')
    # Lobbyen i stedet for kode-raden når du ikke er i et rom.
    s = sub(s, "    if (!net.room) return `<section class=\"online\"><h2>Spill online ${tip}</h2>",
               "    if (!net.room) return lobbyHtml(tip, `<section class=\"online\"><h2>Spill online ${tip}</h2>")
    s = sub(s, "Du kan teste alene med telefon og PC på samme konto.</p></section>`;",
               "Du kan teste alene med telefon og PC på samme konto.</p></section>`);")
    s = sub(s, "Online 1 mot 1 virker når spillet er åpnet i Claude. Her spiller du mot computeren.",
               "Online virker når du er logget inn i Claude og er invitert til spillet på e-post. Kom du inn via en offentlig lenke, spiller du mot computeren.")
    s = sub(s, ": !f ? 'Venter på motspiller. Gi dem koden.'", ": !f ? lobWaitText()")
    # Mens du venter på svar: «Avbryt» i stedet for «Forlat rommet».
    s = sub(s, "<button type=\"button\" data-net=\"leave\">${net.mid && state.phase !== 'over' ? 'Gi opp' : 'Forlat rommet'}</button>",
               "${lob.inv && !net.mid && !net.foe ? '<button type=\"button\" data-lob-cancel>Avbryt</button>' : `<button type=\"button\" data-net=\"leave\">${net.mid && state.phase !== 'over' ? 'Gi opp' : 'Forlat rommet'}</button>`}")
    s = sub(s, "    state.versus = true; state.rival = new RemoteRival();\n", "    state.versus = true; state.rival = new RemoteRival(); lobDone();\n")
    # Knappen øverst: til Send-fanen og ned til lobbyen.
    s = sub(s, "    if (tab) { state.tab = tab.dataset.tab; renderPanel(); return; }",
               "    if (tab) { state.tab = tab.dataset.tab; renderPanel(); if (tab.hasAttribute('data-vs')) lobScroll(); return; }")
    s = sub(s, "\n\n  // ---------- Flammeskjoldet og Warden mellom sidene (versjon 34) ----------",
               JS.replace('__GAME_URL__', GAME_URL) + "\n\n  // ---------- Flammeskjoldet og Warden mellom sidene (versjon 34) ----------")
    return s
