# Automatisk test (autotest)

Robot-testere som spiller The Last Flame og leter etter feil, så Rune slipper å teste alt for hånd.

- `logic_check.js` – spiller hele spill med testspilleren og hundrevis av tilfeldige hærer mot tilfeldige waves, uten grafikk
  (ca. 2 min). Ser etter krasj, NaN, soldater/fiender som havner utenfor kartet, negative ressurser, waves som aldri slutter,
  fiender som står fast, og hvor testspilleren taper (brå hopp i vanskelighet).
- `browser_playtest.js` – åpner den ekte siden i Chromium på telefonstørrelse (390 px, touch). I hver byggefase trykker en
  «ape» på tilfeldige knapper, så kjøper testspilleren hæren, og «Start wave» trykkes. Ser etter JavaScript-feil, rar tekst
  (NaN/undefined), sider bredere enn telefonen, knapper utenfor skjermen, spill som fryser og bildefrekvens. Skjermbilder av hver wave.
- `run.js` – kjører begge og skriver `autotest-report/RAPPORT.md`.

```
node tools/autotest/run.js            # full test (20–40 min)
node tools/autotest/run.js --quick    # rask sjekk (noen minutter)
```

Kjører av seg selv på GitHub ved hver push (`.github/workflows/autotest.yml`); rapporten står på kjøringens side og
skjermbildene ligger som artifact «autotest-report».
I en Claude-sandbox er cdnjs sperret: hent three.js med `npm pack three@0.128.0` og bruk `--three package/build/three.min.js`.

Testspilleren er `bot()` fra `tools/game_sim.js`, så den følger med når boten endres. `--html` tester en annen side enn
`prototype/kamptest-2.html`.
