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
    return s
