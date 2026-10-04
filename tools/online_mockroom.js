// Stand-in for claude.use('room') over BroadcastChannel (test only).
(() => {
  const me = Math.random().toString(36).slice(2, 10);
  function join(name) {
    const bc = new BroadcastChannel('room-' + name), peers = new Map(), subs = [];
    let mine = {};
    const snap = () => [{ peer: me, presence: mine, sameTab: true, isMe: true, kind: 'viewer', by: null, guest: false, updatedAt: Date.now() }]
      .concat([...peers].map(([p, pr]) => ({ peer: p, presence: pr, sameTab: false, isMe: false, kind: 'viewer', by: null, guest: false, updatedAt: Date.now() })));
    const fire = () => { const ps = snap(); subs.forEach(f => f({ peers: ps, joined: [], left: [], updated: [] })); };
    bc.onmessage = e => { const m = e.data;
      if (m.t === 'p') { peers.set(m.peer, m.presence); fire(); }
      else if (m.t === 'hello') { peers.set(m.peer, m.presence || {}); bc.postMessage({ t: 'p', peer: me, presence: mine }); fire(); }
      else if (m.t === 'bye') { peers.delete(m.peer); fire(); } };
    bc.postMessage({ t: 'hello', peer: me, presence: mine });
    window.__mockSent = 0;
    return { name, presence: async patch => { mine = Object.assign({}, mine, patch); window.__mockSent++; window.__mockBytes = JSON.stringify(mine).length; if (window.__mockBytes > 4096) throw { code: 'invalid_argument' }; bc.postMessage({ t: 'p', peer: me, presence: mine }); fire(); },
      onPeers: f => { subs.push(f); setTimeout(fire, 0); return () => {}; }, peers: snap, emit: async () => {}, on: () => () => {},
      connected: () => true, onConnection: () => () => {}, leave: async () => { bc.postMessage({ t: 'bye', peer: me }); bc.close(); } };
  }
  const room = { join, emit: async () => {}, on: () => () => {}, presence: async () => {}, peers: () => [], onPeers: () => () => {}, connected: () => true, onConnection: () => () => {} };
  window.claude = { use: async n => n === 'room' ? room : null };
})();
