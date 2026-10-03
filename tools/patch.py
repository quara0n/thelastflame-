"""Apply per-unit upgrade support to the Last Flame logic (works on the extracted logic or the full prototype)."""
import sys, pathlib

UP = pathlib.Path(__file__).with_name('upgrades.js').read_text()

def sub(s, a, b, count=1):
    n = s.count(a)
    assert n == count, f'expected {count} match(es), found {n}: {a[:80]!r}'
    return s.replace(a, b)

def patch(s):
    s = sub(s, "const ARCHER = {", UP + "\nconst ARCHER = {")
    s = sub(s, "const u = this._make(id++, a.type, c.x, c.z, a.order || 'hold');",
               "const u = this._make(id++, a.type, c.x, c.z, a.order || 'hold', a.level || 0);")
    s = sub(s, """  _make(id, type, x, z, order) {
    const T = this.types[type];
    return { id, type, T,""", """  _lvl(type, level) {
    const c = this._lvlCache || (this._lvlCache = {});
    const k = type + ':' + level;
    return c[k] || (c[k] = levelType(this.types[type], type, level));
  }
  _make(id, type, x, z, order, level) {
    const T = level ? this._lvl(type, level) : this.types[type];
    return { id, type, T, level: level || 0, hits: 0, shots: 0,""")
    # stun, burn, rally regen
    s = sub(s, """    this.captains = players.filter(u => u.T.aura);""",
               """    this.captains = players.filter(u => u.T.aura);
    this.rallies = this.captains.filter(u => u.T.rally);
    if (this.rallies.length) for (const p of players) if (p.hp < p.maxHp) {
      const r = this.rallies.find(c => c.alive && c !== p && dist(c, p) < c.T.aura);
      if (r) p.hp = Math.min(p.maxHp, p.hp + r.T.rally * dt);
    }""")
    s = sub(s, """      u.cd -= dt; u.retarget -= dt; u.moving = false;
""", """      u.cd -= dt; u.retarget -= dt; u.moving = false;
      if (u.burnUntil > this.t) { this._hurt(u, u.burnDps * dt, u.burnBy); if (!u.alive) continue; }
      if (u.stunUntil > this.t) continue;
""")
    # twin heal
    s = sub(s, """        let best = null, low = 0.98;
        for (const o of this.units) {
          if (!o.alive || o.side !== 'p' || o === u) continue;
          const r = o.hp / o.maxHp;
          if (r < low && dist(o, u) < u.T.healRange && !(o.healedAt > this.t - 0.9)) { low = r; best = o; }
        }
        if (best) { best.hp = Math.min(best.maxHp, best.hp + u.T.heal); best.healedAt = this.t; u.hcd = u.T.healEvery; this.events.push({ kind: 'heal', from: u, to: best }); }""",
    """        const hurt = this.units.filter(o => o.alive && o.side === 'p' && o !== u && o.hp / o.maxHp < 0.98 && dist(o, u) < u.T.healRange && !(o.healedAt > this.t - 0.9))
          .sort((a, b) => a.hp / a.maxHp - b.hp / b.maxHp).slice(0, u.T.twinHeal ? 2 : 1);
        for (const best of hurt) { best.hp = Math.min(best.maxHp, best.hp + u.T.heal); best.healedAt = this.t; this.events.push({ kind: 'heal', from: u, to: best }); }
        if (hurt.length) u.hcd = u.T.healEvery;""")
    s = sub(s, """      let pref = u.T.hunts === 'ranged' && f.T.ranged ? -8 : 0;""",
               """      let pref = u.T.hunts === 'ranged' && f.T.ranged ? -8 : 0;
      if (u.T.marks) pref -= f.maxHp / 120;""")
    # attack specials
    s = sub(s, """    this._damage(u, t);
    if (u.T.cleave) {
      const other = this.units.find(o => o.alive && o !== t && o.side === t.side && dist(o, t) < 1.6);
      if (other) this._damage(u, other);
    }""", """    let first = 1;
    if (u.T.marks && u.markId !== t.id) { u.markId = t.id; first = 2; }
    this._damage(u, t, first);
    if (u.T.cleave) {
      this.units.filter(o => o.alive && o !== t && o.side === t.side && dist(o, t) < 1.6)
        .sort((a, b) => dist(a, t) - dist(b, t)).slice(0, u.T.sweep || 1).forEach(o => this._damage(u, o));
    }
    if (u.T.spin && ++u.hits % u.T.spin === 0) {
      for (const o of this.units) if (o.alive && o !== t && o.side === t.side && dist(o, u) < u.T.radius + 1.6) this._damage(u, o, 0.8);
      this.events.push({ kind: 'blast', x: u.x, z: u.z, r: 1.8, spin: true });
    }
    if (u.T.burst && ++u.shots % u.T.burst === 0) {
      for (const o of this.units) if (o.alive && o !== t && o.side === t.side && dist(o, t) < 1.5) this._damage(u, o, 0.5);
      this.events.push({ kind: 'blast', x: t.x, z: t.z, r: 1.5 });
    }
    if (u.T.skewer) {
      const d = dist(u, t) || 1, nx = (t.x - u.x) / d, nz = (t.z - u.z) / d;
      this.units.filter(o => o.alive && o !== t && o.side === t.side).map(o => ({ o, along: (o.x - t.x) * nx + (o.z - t.z) * nz, lat: Math.abs(-(o.x - t.x) * nz + (o.z - t.z) * nx) }))
        .filter(p => p.along > 0 && p.along < 3.5 && p.lat < 0.9).sort((a, b) => a.along - b.along).slice(0, u.T.skewer).forEach(p => this._damage(u, p.o, 0.7));
    }
    if (u.T.bash && !(u.bashAt > this.t) && t.alive) {
      u.bashAt = this.t + u.T.bash;
      if (!t.T.boss && !this._steady(t)) { const d = dist(u, t) || 1; t.x += (t.x - u.x) / d * 1.5; t.z += (t.z - u.z) / d * 1.5; }
      t.stunUntil = this.t + (t.T.boss ? 0.3 : 0.9);
      this.events.push({ kind: 'knock', to: t, bash: true });
    }""")
    s = sub(s, """    if (u.side === 'p' && this.captains && this.captains.some(c => c.alive && c !== u && dist(c, u) < c.T.aura)) mult *= 1.2;""",
               """    if (u.side === 'p' && this.captains) {
      const near = this.captains.filter(c => c.alive && c !== u && dist(c, u) < c.T.aura);
      if (near.length) mult *= near.some(c => c.T.rally) ? 1.3 : 1.2;
    }
    if (u.T.ranged && t.side === 'p' && u.side === 'e' && this._sheltered(t)) mult *= 0.75;
    if (t.T.brace) {
      if (!t.braced && t.hp < t.maxHp * 0.5) { t.braced = true; t.braceUntil = this.t + t.T.brace; this.events.push({ kind: 'brace', unit: t }); }
      if (t.braceUntil > this.t) mult *= 0.5;
    }
    if (u.T.burn && t.alive) { t.burnUntil = this.t + 2; t.burnDps = u.T.burn; t.burnBy = u.type; }""")
    s = sub(s, """  _separate() {""", """  _sheltered(t) {
    return this.units.some(a => a.alive && a !== t && a.side === 'p' && a.T.shieldwall && a.z < t.z && t.z - a.z < 2.6 && Math.abs(a.x - t.x) < 1.3);
  }
  // Skade uten angriper (brann): samme regler for død og statistikk.
  _hurt(t, amt, byType) {
    if (!t.alive) return;
    const dealt = Math.min(amt, t.hp);
    t.hp -= amt;
    if (byType && this.stats[byType]) this.stats[byType].dmg += dealt;
    if (t.hp <= 0) {
      t.alive = false; t.target = null;
      if (byType && this.stats[byType]) this.stats[byType].kills++;
      this.stats[t.type].deaths++;
      this.events.push({ kind: 'death', unit: t, by: byType });
      if (t.T.spawn) for (let i = 0; i < t.T.spawn.n; i++) {
        const a = i / t.T.spawn.n * Math.PI * 2;
        const c = this._make(this.nextId++, t.T.spawn.type, t.x + Math.cos(a) * 0.8, t.z + Math.sin(a) * 0.8, null);
        this.units.push(c); this.stats[c.type].count++;
      }
    }
  }
  _separate() {""")
    s = sub(s, "module.exports = { WORLDS,", "module.exports = { UPGRADES, MAX_LEVEL, levelType, WORLDS,")
    return s

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    pathlib.Path(dst).write_text(patch(pathlib.Path(src).read_text()))
    print('patched', dst)
