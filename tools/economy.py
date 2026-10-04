"""Deflation (4 Oct 2026): slower gathering, pricier workers, Barracks priced so each tier belongs to its world,
and a Warden that takes the whole game to max out. Numbers live in economy.json. Applied by build_v2.py."""
import json, re
from pathlib import Path
from patch import sub

CFG = json.loads((Path(__file__).parent / 'economy.json').read_text())

def scale_cost(txt, mul):
    """Multiply every number inside a { res: n, ... } cost literal."""
    return re.sub(r'(\w+): (\d+)', lambda m: f"{m.group(1)}: {max(1, round(int(m.group(2)) * mul))}", txt)

def apply(s):
    E = CFG['every']
    for k, old in [('gold', "yield: 1, every: 8, cap: 6"), ('timber', "res: 'timber', yield: 1, every: 5"), ('stone', "res: 'stone',  yield: 1, every: 5"),
                   ('iron', "res: 'iron',   yield: 1, every: 6"), ('coal', "res: 'coal',   yield: 1, every: 8")]:
        s = sub(s, old, re.sub(r'every: \d+', f"every: {E[k]}", old))
    W = CFG['worker']
    s = sub(s, "const WORKER_BASE = 5, WORKER_FREE = 10, WORKER_STEP = 2;", f"const WORKER_BASE = {W['base']}, WORKER_FREE = {W['free']}, WORKER_STEP = {W['step']};")
    # Barracks II–V.
    for i, name in enumerate(['Barracks II', 'Barracks III', 'Barracks IV', 'Barracks V']):
        m = re.search(r"\{ name: '" + name + r"',[^\n]*?cost: (\{[^}]*\})", s)
        old = m.group(1)
        s = s.replace(m.group(0), m.group(0).replace(old, scale_cost(old, CFG['barracksMul'][i])), 1)
    # Warden-utstyr og trening.
    a = s.index('const WARDEN_GEAR = {'); b = s.index('const WARDEN_XP')
    block = s[a:b]
    block2 = re.sub(r"cost: (\{[^}]*\})", lambda m: 'cost: ' + scale_cost(m.group(1), CFG['wardenMul']), block)
    s = s[:a] + block2 + s[b:]
    s = sub(s, "const WARDEN_TRAIN = { cost: { gold: 7 }, xp: 5 };", f"const WARDEN_TRAIN = {{ cost: {{ gold: {round(7 * CFG['wardenMul'])} }}, xp: 5 }};")
    # Verktøy.
    a = s.index('const TOOLS = ['); b = s.index('const TOOL_BONUS')
    s = s[:a] + re.sub(r"cost: (\{[^}]*\})", lambda m: 'cost: ' + scale_cost(m.group(1), CFG['toolsMul']), s[a:b]) + s[b:]
    # Arbeidere (4. okt, ettermiddag): prisen stiger først etter 6 arbeidere på samme sted.
    s = sub(s, "  workerPrice() { return WORKER_BASE + Math.max(0, this.owned - (WORKER_FREE - 1)) * WORKER_STEP; }",
               "  // Pris for neste arbeider på stedet k: grunnpris for de 6 første, deretter dyrere for hver.\n"
               "  workerPrice(k) { const w = k ? this.nodes[k].workers : 0; return WORKER_BASE + Math.max(0, w + 1 - WORKER_FREE) * WORKER_STEP; }")
    s = sub(s, "    if (!this.pay({ gold: this.workerPrice() })) return false;\n    this.owned++; n.workers++;", "    if (!this.pay({ gold: this.workerPrice(k) })) return false;\n    this.owned++; n.workers++;")
    # Hver arbeider leverer når han kommer frem til lageret (én tur per leveranse), ikke alle samtidig.
    s = sub(s, """  tick(dt) {
    for (const k of Object.keys(NODES)) {
      const n = this.nodes[k];
      n.pending += n.workers * this.rate(k) / NODES[k].every * dt;
      n.t += dt;
      if (n.t >= NODES[k].every) {
        n.t -= NODES[k].every;
        const amt = Math.floor(n.pending);
        if (amt > 0) {
          n.pending -= amt;
          this.add({ [NODES[k].res]: amt });
          this.deliveries.push({ node: k, res: NODES[k].res, amount: amt });
        }
      }
    }
  }""", """  // Hver arbeider går en tur: fra gruva til lageret (leverer når han kommer frem) og tilbake. En tur tar «every» sekunder.
  tick(dt) {
    for (let rem = dt; rem > 1e-9; ) {
      const s = Math.min(rem, 0.5); rem -= s;
      for (const k of Object.keys(NODES)) {
        const n = this.nodes[k], every = NODES[k].every, half = every / 2;
        n.wt = n.wt || [];
        while (n.wt.length < n.workers) n.wt.push(0);
        if (n.wt.length > n.workers) n.wt.length = n.workers;
        for (let i = 0; i < n.wt.length; i++) {
          const before = n.wt[i]; n.wt[i] = (before + s) % every;
          if (before < half && before + s >= half || before + s >= every + half) {
            n.pending += this.rate(k);
            const amt = Math.floor(n.pending);
            if (amt > 0) { n.pending -= amt; this.add({ [NODES[k].res]: amt }); if (this.deliveries.length < 300) this.deliveries.push({ node: k, res: NODES[k].res, amount: amt, worker: i }); }
          }
        }
      }
    }
  }""")
    # Grensesnittet: pris per sted, og tallet som stiger over lageret.
    s = sub(s, "<span>Neste arbeider ${icon('gold', 13)} ${ec.workerPrice()}</span>", "<span>Arbeider ${icon('gold', 13)} ${WORKER_BASE} (dyrere etter ${WORKER_FREE} på samme sted)</span>")
    s = sub(s, "      b.classList.toggle('cant', ec.idle === 0 && ec.res.gold < ec.workerPrice());", "      b.classList.toggle('cant', ec.idle === 0 && ec.res.gold < ec.workerPrice(k));")
    s = sub(s, "      explainMissing(b.dataset.cost ? JSON.parse(b.dataset.cost) : { gold: ec.workerPrice() });", "      explainMissing(b.dataset.cost ? JSON.parse(b.dataset.cost) : { gold: ec.workerPrice(k) });")
    s = sub(s, "Arbeidere koster ${ec.workerPrice()} gull", "Arbeidere koster ${WORKER_BASE} gull, og blir dyrere etter ${WORKER_FREE} på samme sted")
    s = sub(s, "· neste ${icon('gold', 12)}${ec.workerPrice()}</small>", "· ${icon('gold', 12)}${WORKER_BASE} per arbeider</small>")
    s = sub(s, """        // Går frem og tilbake; bærer last på vei til lageret.
        const ph = ((t * 1.6 / len) + w.userData.phase) % 2;
        const f = ph < 1 ? ph : 2 - ph;""", """        // Turen følger økonomien: første halvdel bærer han last til lageret, andre halvdel går han tom tilbake.
        const wt = ec.nodes[k].wt && ec.nodes[k].wt[i] != null ? ec.nodes[k].wt[i] : 0, fr = wt / NODES[k].every;
        const ph = fr < 0.5 ? fr * 2 : 1 + (fr - 0.5) * 2;
        const f = ph < 1 ? ph : 2 - ph;""")
    s = sub(s, "      ec.deliveries.forEach(d => { popRes(d.res, d.amount); nodeVis[d.node].pulse = 0.35; });",
               "      ec.deliveries.forEach(d => { popRes(d.res, d.amount); nodeVis[d.node].pulse = 0.35; deliveryPop(d); });")
    s = sub(s, "  function clearCoins() {", """  // Et lite tall over lageret hver gang en arbeider leverer.
  function deliveryPop(d) {
    if (state.phase === 'over') return;
    const st = STORES[NODE_POS[d.node].store], el = document.createElement('span');
    el.className = 'coin'; el.style.fontSize = '13px'; el.innerHTML = `+${d.amount}${icon(d.res, 13)}`;
    coinLayer.appendChild(el);
    coins.push({ el, x: st.x + (Math.random() - 0.5) * 1.2, z: st.z, t: 0.15 });
    if (coins.length > 60) { coins[0].el.remove(); coins.shift(); }
  }
  function clearCoins() {""")
    return s
