# CLAUDE.md – The Last Flame

Read this first, then `HANDOFF.md` for where the work stopped.

## What this is

The Last Flame is a Squadron-inspired unit tower defence. The player holds a gate in front of a city where the last flame burns. Waves of creatures from the "Fallen Worlds" come through a portal. Between waves the player gathers resources with workers, buys and upgrades soldiers, and gives them orders. The designer is the user (GitHub: quara0n). It is meant to become a team multiplayer game (1v1 arena, sending units to opponents), but today it is a single-player browser prototype.

## Working with the user

- The user writes in English (often voice-dictated, so expect filler words and odd spellings: "squadron" = Squadron, "side guard" = Shieldguard, "PyroGuard" = Pyreguard). Answer in English.
- The design notes are in Norwegian, and so is the in-game text. Keep both in Norwegian unless asked otherwise.
- The user thinks in game feel, not code. Explain in plain words. "Explain like I'm five" has been asked for and worked well.
- The user likes Claude to take initiative ("keep going", "do your magic"). Make sensible calls, say what was decided, and save decisions in the notes.
- The user plays on a phone. Every change to the prototype must work at phone width (390 px).
- Ask only real design questions (themes, names, rules), and offer 2–4 concrete options.
- Don't make the user use the test bench or read numbers. Run the simulations and report the result in words.

## Where things live

- **Repo** (this folder): `prototype/` HTML pages, `tools/` build and balance tools, `docs/` design notes (Norwegian), `docs/art/` reference images.
- **claude.ai project "The Last Flame"**: the same design notes (`claude/verdener-og-tiers.md`, `claude/tier1-oppgraderinger.md`, `claude/flyvere-skjeletter-og-flerspiller.md`), plus `claude/CLAUDE.md`, `claude/HANDOFF.md` and the tool sources under `claude/kode/`. A new thread can rebuild the repo from the project and the artifacts below.
- **Artifacts (the user's playable pages):**
  - Last Flame Kamptest II (current game): https://claude.ai/artifact/4h6eEwfWuJEPxzigKGvk3V
  - Askemyr Style Test (jointed Husk and Brute): https://claude.ai/artifact/3MRBrtYoFSkHycms9KQads
  - Last Flame Kamptest (old v1, the build source): https://claude.ai/code/artifact/246365ce-6d75-4f4a-bed6-5e06e14347d0
  - To update Kamptest II from a new thread: `Artifact` action `read` on its URL first, then publish with `url` set to it.
- **GitHub**: quara0n/thelastflame. Not pushed yet (see HANDOFF.md).

## How the prototype is built

- `prototype/kamptest-1.html` is the original single-file game (three.js r128 from cdnjs, no other files). Never edit it by hand. It is the source for the build.
- `prototype/kamptest-2.html` is generated: `python3 tools/build_v2.py` reads kamptest-1, applies a chain of exact string patches and writes kamptest-2:
  1. `tools/patch.py` adds per-unit upgrade levels and their abilities to the battle engine (`Sim`), and injects `tools/upgrades.js` (all upgrades, `BALANCE` prices, `levelType()`).
  2. `build_v2.py` itself: scarce economy, visible gear per level, the Upgrade button in the order bar, refunds incl. upgrades, wave factors from `tools/wave_factors.json`.
  3. `tools/world3.py`: World 3 (Urheim) creatures and mechanics, Tier 4 units and upgrades, Barracks IV, models, world look, sounds.
  4. `tools/mobile.py`: phone layout.
  6. `tools/economy.py` (numbers in `tools/economy.json`): deflation — slower gathering, pricier workers, Barracks priced per world, Warden gear ×2.
  5. `tools/music.py`: recorded music (build phase rotates 2 tracks, battle rotates 3) and 55 s between waves. The mp3s live in `prototype/musikk/` and must be published with the page via the Artifact `files` map (`musikk/<name>.mp3`).
- Every patch uses `sub()`, which fails loudly if the target text isn't found exactly once. If a build fails, the anchor text moved; fix the patch, don't hand-edit kamptest-2.
- After building, copy `prototype/kamptest-2.html` to a local file and publish it to the Kamptest II artifact URL. The music files are already published there and are kept on later publishes, so only pass `files` again if a track changes.
- The page has three code sections: battle logic (`// ===== The Last Flame — kampsimulering`), economy (`Econ`), sound (`Sound`, Web Audio, no files), then graphics and UI in an IIFE. The logic part runs headless in Node; the tools cut it out of the HTML between the `kampsimulering` and `musikk` markers.
- Checking pages: Playwright with Chromium (`python3 -m playwright install chromium`, launch with `--use-gl=swiftshader`). cdnjs is blocked from the shell, so get three.js with `npm pack three@0.128.0` and point the page at `package/build/three.min.js` in a scratch copy.

## Balance method

- **Tier rule:** a fresh unit of tier N+1 ≈ 90 % of a fully upgraded unit of tier N, and ≈ 120 % after its first upgrade. Measured with `tools/run_all.js` / `tools/tune.js` (Tier 1–3) and `tools/tune4.js` (Tier 4). The measurements have about ±10 % noise.
- **Waves:** `tools/game_sim.js` plays whole games with a bot player (gathers, buys, upgrades, Barracks, archers, walls, sells fully upgraded old units to make room for a new tier). `tools/tune_waves.js R FROM` finds a strength factor per wave (enemy HP × k, damage × √k) so the bot holds each wave at a target rate, and multiplies it into `wave_factors.json`. Always rebuild before tuning again, because it measures on top of the factors already in kamptest-2.
- **Check:** `node tools/game_sim.js 30` – the current state is 27 of 30 games reaching wave 30 (55 s breaks, deflated economy; the user found the game a bit hard, so keep it on the gentle side).
- The bot and the tuner use 55 s between waves (`t = 55` in game_sim.js and tune_waves.js); change both if the break changes.
- If the bot's strategy changes, earlier waves shift too. Retune from wave 1 afterwards.

## Locked design decisions (details in docs/)

- Economy: scarcity like Squadron. Worker 5 gold, Tier 1 unit 10 gold, start 75 gold. Deflated 4 Oct: a normal player reaches Tier 2 at the end of World 1, Tier 3 in World 2, Tier 4 in World 3 (bot: waves 9/16/26; an all-in economy rush: 5/12/18). Check with /tmp-style rush and tier scripts before changing prices.
- Every unit has a base version and 3 upgrades, bought on one specific soldier. Same model with new gear. Forge and Workshop upgrades (all units of a type) stay as well.
- Army size around 27 units at wave 20 is fine; not 40. Army space 20 / 30 / 40 / 50.
- Tiers: Tier 4 belongs to World 3 and Tier 5 to World 4, but Barracks prices decide, not wave locks. A strong player may buy Barracks V in World 3.
- Worlds: 1 Askemyr (ash and poison), 2 Vrangheim (twisted wild nature), 3 Urheim (dinosaurs, time is broken), 4 divine robotics (not designed).
- Flyers: the flame's dome covers the city up to the wall. Flyers ignore the army and go to the gate; only ranged units and wall archers reach them in the air. Flyer waves: 5 ash crows, 15 locusts, 25 urdragons, 35 drones (5 and 35 not built).
- Art: style "detailed stylized" (option 2), models from an AI 3D tool or bought packs, one skeleton per body family. The Warden is divine (white and gold, halo) and carries the flame's sword and shield. The flame's side glows gold, the enemies glow dull red and ashy. Gate and towers should end up huge (Helm's Deep feel), about 30 enemies per wave.
