# Dobbelttrykk velger hele typen, og helten er lettere å treffe (versjon 38).
# Før: andre trykk på en markert unit ble tatt som «ta tak og flytt», så dobbeltklikket nådde aldri fram.
# Nå: et trykk uten flytting på en markert unit teller som et klikk, og dobbelttrykket velger alle av typen.
# Units plukkes på skjermen (nærmeste kropp innenfor en radius), ikke bare ruta under fingeren; helten har dobbelt så stor radius.
from patch import sub

def apply(s):
    # Plukk unit ut fra hvor kroppen står på skjermen.
    s = sub(s, "  let lastClick = { t: 0, i: -1 };\n  function clickSelect(c, add) {\n    const i = c ? state.army.findIndex(a => a.col === c.col && a.row === c.row) : -1;\n",
               """  // Nærmeste unit under fingeren: avstand på skjermen til kroppen (fot til hode). Helten har større treffsone.
  const pickA = new THREE.Vector3(), pickB = new THREE.Vector3();
  function unitAt(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    const scr = v => { v.project(camera); return { x: rect.left + (v.x + 1) / 2 * rect.width, y: rect.top + (1 - v.y) / 2 * rect.height }; };
    let best = -1, bestD = Infinity;
    state.army.forEach((a, i) => {
      const p = cellCenter(a.col, a.row), hero = TYPES[a.type] && TYPES[a.type].hero;
      const f = scr(pickA.set(p.x, 0.1, p.z)), h = scr(pickB.set(p.x, hero ? 2.2 : 1.6, p.z));
      const side = scr(pickA.set(p.x + MAP.cell / 2, 0.1, p.z));
      const px = Math.max(8, Math.hypot(side.x - f.x, side.y - f.y));   // en halv rute i piksler
      const r = Math.max(hero ? 34 : 18, px * (hero ? 1.9 : 1.0));
      const vx = h.x - f.x, vy = h.y - f.y, L = vx * vx + vy * vy || 1;
      const t = clampN(((clientX - f.x) * vx + (clientY - f.y) * vy) / L, 0, 1);
      const d = Math.hypot(clientX - (f.x + vx * t), clientY - (f.y + vy * t));
      const score = d / r;
      if (score <= 1 && score < bestD) { best = i; bestD = score; }
    });
    if (best >= 0) return best;
    const c = cellAt(clientX, clientY);
    return c ? state.army.findIndex(a => a.col === c.col && a.row === c.row) : -1;
  }
  let lastClick = { t: 0, i: -1 };
  function clickSelect(c, add, ui) {
    const i = ui !== undefined ? ui : c ? state.army.findIndex(a => a.col === c.col && a.row === c.row) : -1;
""")
    # Litt mer tid til dobbelttrykk på telefon, og trykk nummer to kan treffe naboen av samme type.
    s = sub(s, "    if (lastClick.i === i && now - lastClick.t < 350) {",
               "    if (now - lastClick.t < 450 && (lastClick.i === i || (state.army[lastClick.i] && state.army[lastClick.i].type === state.army[i].type))) {")
    s = sub(s, "      state.army.forEach((a, j) => { if (a.type === type) state.selection.add(j); });\n",
               "      state.army.forEach((a, j) => { if (a.type === type) state.selection.add(j); });\n      lastClick = { t: 0, i: -1 };\n      toast(`Alle ${state.selection.size} ${TYPES[type].name} er valgt.`);\n      selectionChanged();\n      return;\n")
    # Ta tak i markert unit: bruk den nye plukkingen.
    s = sub(s, "        const c = cellAt(e.clientX, e.clientY);\n        const i = c ? state.army.findIndex(a => a.col === c.col && a.row === c.row) : -1;\n        if (i >= 0 && state.selection.has(i)) { drag.box = false; drag.move = { col: c.col, row: c.row, dc: 0, dr: 0, ok: true }; }",
               "        const i = unitAt(e.clientX, e.clientY);\n        if (i >= 0 && state.selection.has(i)) { const u = state.army[i]; drag.box = false; drag.move = { col: u.col, row: u.row, dc: 0, dr: 0, ok: true, i }; }")
    # Trykk uten flytting på en markert unit er et vanlig klikk (dobbelttrykk virker).
    s = sub(s, "    if (drag && drag.move) {\n      if (drag.moved) finishMove();\n    } else if",
               "    if (drag && drag.move && drag.moved) {\n      finishMove();\n    } else if (drag && drag.move && pointers.size === 1) {\n      clickSelect(null, e.shiftKey || e.ctrlKey || e.metaKey, drag.move.i);\n    } else if")
    s = sub(s, "      else clickSelect(c, e.shiftKey || e.ctrlKey || e.metaKey);",
               "      else clickSelect(c, e.shiftKey || e.ctrlKey || e.metaKey, unitAt(e.clientX, e.clientY));")
    # Musepeker og bygningsplukk ser også den større treffsonen.
    s = sub(s, "    return !!c && state.army.some(a => a.col === c.col && a.row === c.row);\n",
               "    return (!!c && state.army.some(a => a.col === c.col && a.row === c.row)) || unitAt(e.clientX, e.clientY) >= 0;\n")
    return s
