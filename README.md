# The Last Flame

A Squadron-inspired unit tower defence. Hold the gate through waves of creatures from the Fallen Worlds, and keep the last flame burning.

This repository holds the browser prototype, the balance tools and the design notes. Everything is a work in progress, and all numbers are prototype values.

## Prototype (`prototype/`)

Each file is a single HTML page. Open it in a browser; it only needs an internet connection for the fonts and the three.js library.

| File | What it is |
| --- | --- |
| `kamptest-2.html` | Current version. 30 waves across three worlds (Askemyr, Vrangheim, Urheim with dinosaurs and urdragons), four tiers, per-unit upgrades (three levels per soldier, visible gear), the scarce economy (Tier 1 = 10 gold, worker = 5 gold), and waves balanced with whole-game simulations. |
| `kamptest-1.html` | The earlier combat prototype, before upgrades and the new economy. Kept for comparison. |
| `askemyr-style-test.html` | Style and animation test: jointed Hollow Husk and Ashen Brute walking, attacking, getting hit and dying at the gate. |

## Balance tools (`tools/`)

Node.js and Python 3. The tools run the same battle engine as the prototype, without graphics.

- `upgrades.js` – the three upgrades for every unit, the new prices (`BALANCE`) and `levelType()`, which builds a unit's stats at a given level.
- `patch.py` – adds per-unit upgrades and their special abilities to the battle engine.
- `build_v2.py` – builds `prototype/kamptest-2.html` from `kamptest-1.html`: upgrades, economy, visible gear, the upgrade button and the wave factors.
- `world3.py` – World 3 (Urheim) and Tier 4: creatures, new mechanics (flyers, roar, stun, blind, carriers, revive), units, upgrades, models, world look and sounds. Applied by `build_v2.py`.
- `tune4.js` – measures Tier 4 against fully upgraded Tier 3.
- `game_sim.js` – plays whole games with a sensible bot player (gathers, buys, upgrades, builds Barracks) and reports how often each wave is held. `node tools/game_sim.js 20`
- `tune_waves.js` – finds a strength factor per wave so the bot holds each wave at its target rate, and multiplies it into `wave_factors.json`. It measures on top of the factors already built into `kamptest-2.html`. `node tools/tune_waves.js 16 21` tunes only waves 21 and up; rebuild with `build_v2.py` before tuning again.
- `run_all.js`, `tune.js`, `bench.js`, `bench_core.js`, `logic_up.js` – measure how strong one unit type is at each level, used to set the tier rule (a fresh Tier 2 ≈ 90 % of a maxed Tier 1, ≈ 120 % after its first upgrade).

To rebuild the current prototype after changing `upgrades.js` or `wave_factors.json`:

```
python3 tools/build_v2.py
```

## Design notes (`docs/`, in Norwegian)

- `verdener-og-tiers.md` – worlds, tiers, army space, bosses.
- `oppgraderinger-og-balanse.md` – every unit's three upgrades, the economy, and the balance measurements.
- `design-flyvere-assets-flerspiller.md` – flyers and the flame dome, skeleton families for animation, art direction (incl. the Warden), multiplayer ideas (1v1 arena, sending units, scouting) and open questions.
