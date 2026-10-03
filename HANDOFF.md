# HANDOFF – The Last Flame (3 Oct 2026)

Read `CLAUDE.md` first. This file says where the work stopped and what comes next.

## State right now

- **Playable:** "Last Flame Kamptest II" (https://claude.ai/artifact/4h6eEwfWuJEPxzigKGvk3V), version 4. 30 waves over three worlds, Tier 1–4, per-unit upgrades, scarce economy, simulation-balanced waves, phone layout. The user plays it on a phone.
- **Repo:** 6 commits on `main`, not pushed. Pushing failed because the user's GitHub account isn't linked to Claude (`add_repo` → permission_denied; `gh` has no valid token). The user was told to link GitHub under claude.ai Settings → Connectors and to create an empty `quara0n/thelastflame` if it doesn't exist. The full repo with history was sent to the user as `thelastflame.zip`.
- **Project notes** in claude.ai are up to date and match `docs/`.

## Done in the last session (2–3 Oct)

1. Asset direction: 2D vs 3D settled (stay 3D), skeleton families, Askemyr Style Test (jointed Husk and Brute), style option 2 "detailed stylized".
2. Flyer rules (flame dome), flyer waves 5/15/25/35, multiplayer ideas (1v1 arena at wave 7–8, sending units, flags, scouting).
3. Per-unit upgrades: 3 per unit for all 12 units of Tier 1–3, visible gear, Upgrade button.
4. Economy rebuilt around scarcity (worker 5, Tier 1 10 gold).
5. Waves 1–20 rebalanced with whole-game simulations.
6. Warden look locked (`docs/art/warden-concept.png`).
7. World 3 Urheim (dinosaurs, urdragons, Tyrant King) and Tier 4 (Ironhulk, War Mammoth, Skyspear, Hearth Engine) built, balanced and checked in the browser.
8. Phone layout.

## Next steps (in suggested order)

1. **Push the repo** once GitHub is linked: `add_repo` quara0n/thelastflame with push access, then `git remote add origin … && git push -u origin main`. In a new thread the local repo is gone: rebuild it from the project (`claude/kode/…` plus the artifacts), or ask the user to attach `thelastflame.zip`.
2. **Ask the user how waves 21–30 feel on the phone.** The balance comes from a bot, not a human.
3. **Multiplayer basics before World 4:** team setup (how many players per team, who meets whom with 8 teams), what happens when the gate falls (is the gate or the flame the "king"), sending units (which, and the price per world), the arena wave (7 or 8). These are the biggest open design questions.
4. **World 4 (divine robotics, waves 31–40) and Tier 5 (Legendary)**, built the same way as World 3: draft in the notes, user approval, `tools/world4.py`, tune with `tune4.js`-style measurement and `tune_waves.js`.
5. Missing flyer creatures: Ash Crow (wave 5) and drones (wave 35).
6. About 30 enemies per wave (today 10–40, uneven).
7. Models: choose between an AI 3D tool (Meshy, Tripo, Rodin) and bought packs. Start with Husk and Brute, then a clean Warden character sheet.

## Rebuilding the repo in a new thread (if the zip isn't attached)

1. `Projects` → `project_read` every `claude/kode/…` file and save it under `tools/` with the same name (`claude/kode/world3.py` → `tools/world3.py`). Save `claude/CLAUDE.md` and `claude/HANDOFF.md` at the repo root.
2. Notes: `claude/verdener-og-tiers.md` → `docs/verdener-og-tiers.md`, `claude/tier1-oppgraderinger.md` → `docs/oppgraderinger-og-balanse.md`, `claude/flyvere-skjeletter-og-flerspiller.md` → `docs/design-flyvere-assets-flerspiller.md`.
3. `Artifact` action `read` with `path: "index.html"` on the old Kamptest URL → `prototype/kamptest-1.html`, and on the Askemyr Style Test URL → `prototype/askemyr-style-test.html`.
4. `python3 tools/build_v2.py` → `prototype/kamptest-2.html`. Compare it with the published Kamptest II (read it the same way); they should match.
5. The Warden images in `docs/art/` only exist in the zip and in the old thread; ask the user to re-attach them if needed.

## Known rough edges

- Shooters can hit flyers in the air, but shot-down flyers don't fall and fight on the ground yet (designed, not built).
- Camera rotation needs Q/E on a keyboard; on a phone the view is fixed toward the portal.
- The test bench tab only tests level 0 units.
- The bot never uses Workshop tech or Warden gear, so those aren't part of the balance.
- Tier 4 measurements have ±10 % noise (Ironhulk and Mammoth sit a bit above target after upgrade 1).
- `tools/logic_up.js` patches kamptest-1 on the fly (it calls python3) and is only used by the Tier 1–3 measurement scripts.
