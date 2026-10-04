# The Last Flame – unit-oppgraderinger, alle tiers (2.–3. okt 2026)

Tier 4-oppgraderingene står i `verdener-og-tiers.md`.

Bygget inn i `prototype/kamptest-2.html` ("Last Flame Kamptest II"). `kamptest-1.html` er den gamle versjonen, urørt.
Regel: hver unit har grunnversjon + 3 oppgraderinger, kjøpt på én bestemt soldat (velg den på kartet, trykk «Oppgrader»). Samme modell, nytt utstyr per nivå: nivå 1 skulderplater, nivå 2 rød kappe, nivå 3 glødende kam. Gull-ruter over hodet viser nivået. Plass i hæren endres ikke. Selger du, får du 75 % av alt du har brukt, også oppgraderingene.
Forge og Workshop (felles oppgraderinger for alle units av en type) er beholdt og virker i tillegg.

## Økonomi: knapphet, ikke inflasjon
- Arbeider 5 gull (+2 per arbeider etter de ni første). Tier 1-unit 10 gull.
- Start: 75 gull (før 125). Gullgruva leverer saktere (hvert 8. sek i stedet for 5.), ca. 7,5 gull/min per arbeider.
- Alle andre gullpriser (Forge, Workshop, verktøy, bueskyttere, Warden-utstyr, utvidelser) er ganget med 0,6. Wave-bonus 6 + 2 per wave.
- Plass i hæren: Barracks I 20, II 30, III 40 (IV 50, V 60).
- Tier 1: 10 g. Oppgraderinger 5 g / 8 g + 1 jern / 12 g + 2 jern + 1 kull. Fullt oppgradert ca. 35 g.
- Tier 2: 24–26 g + 1–2 jern. Oppgraderinger 12 / 18 / 25 g + jern og kull.
- Tier 3: 55–62 g + jern (og kull for Pyreguard). Oppgraderinger 20 / 30 / 40 g + jern og kull.

## Balansemål og målinger
- En fersk Tier 2 ≈ 90 % av en fullt oppgradert Tier 1. Etter første oppgradering ≈ 120 %. Samme mønster mellom Tier 2 og Tier 3.
- Målt med kampmotoren fra prototypen (`tools/run_all.js`, `tools/tune.js`): tre units av typen lagt til en fast kjernehær, mot wave 4, 6 og 8, og målt hvor sterke fiender hæren slår halvparten av gangene.
- Resultat (fersk / etter 1. oppgradering, mot fullt oppgradert unit ett tier under):
  - Ironwall 94 % / 119 % (mot Shieldguard)
  - Frostbrand 90 % / 120 % (mot Stormreaver)
  - Thunderbore ca. 90 % / ca. 120 % (mot Ironshot)
  - Hearthkeeper 90 % / 119 % (mot Stormreaver)
  - Warbanner Captain 94 % / 127 % (mot Ironwall)
  - Huskarl ca. 100 % / ca. 125 % (mot Frostbrand)
  - Pyreguard 95 % / 114 % (mot Thunderbore)
  - Siegebreaker 96 % / 124 % (mot Thunderbore)
- For å få dette ble grunnversjonene av Tier 2 og 3 svakere (f.eks. Ironwall 340 HP i stedet for 640, Huskarl 400 i stedet for 900). Styrken kommer nå fra oppgraderingene.

## Waves balansert på nytt (3. okt 2026, alle 30 waves)
- Hele spill simulert (`tools/game_sim.js`): en fornuftig bot-spiller samler, kjøper, oppgraderer, bygger Barracks, bueskyttere og mur, og selger gamle fullt oppgraderte units for å få plass til en ny tier når hele hæren er fullt oppgradert.
- Hver wave har en styrkefaktor (`tools/tune_waves.js`, `tools/wave_factors.json`): fiendenes helse × faktor, skade × kvadratroten av faktoren. Mål for hvor ofte waven holdes (vinner og porten står): wave 1–4 alltid, 5–8 ca. 95 %, 10 (boss) ca. 80 %, 11–19 ca. 93 %, 20 (boss) ca. 70 %, 21–29 ca. 90 %, 30 (boss) ca. 65 %. Bossene i wave 10 og to topper (15, 19, 25, 26) ble justert litt ned for hånd, sluttbossen litt opp.
- Faktorer, wave 1–30: 0,9 · 1,6 · 1,54 · 1,331 · 1,1 · 1,54 · 2,24 · 0,88 · 0,81 · 0,648 · 0,81 · 0,891 · 0,9 · 0,891 · 0,81 · 0,624 · 0,88 · 0,81 · 0,833 · 0,9 · 1,25 · 0,9 · 1,238 · 1,125 · 0,729 · 0,693 · 0,8 · 0,594 · 0,594 · 0,569.
- Sjekk (30 nye spill): 24 av 30 kom til wave 30. Tapene var spredt på de tøffeste wavene (20, 27, 28). Sluttbossen vinnes ca. 1 av 8 ganger.
- World 3 fikk en mildere kurve enn først tenkt (helse ×3,4 + 0,12 per wave, skade ×2,0 + 0,05) og svakere urdrager, fordi fire urdrager rev ned porten på sekunder.

## Tier 1
- Shieldguard: 1 Jernkant (mer helse og rustning). 2 Tårnskjold (units rett bak tar 25 % mindre skade fra skudd og spytt). 3 Runeskjold (skjoldslag hvert 6. sek, slår bakover og lammer).
- Stormreaver: 1 Slipt øks (+20 % skade). 2 Skjegg-øks (raskere slag, rustning). 3 Stormraseri (hvert 3. slag treffer alle rundt ham).
- Ironshot: 1 Riflet løp (+2 rekkevidde, +15 % skade). 2 Damptank (raskere skudd, mer helse). 3 Kull-ladning (hvert 4. skudd sprekker rundt målet).
- Longfang: 1 Kikkertsikte (+2 rekkevidde, +15 % skade). 2 Langt løp (gjennom mer rustning, sikter raskere). 3 Merket skudd (velger den sterkeste fienden, dobbel skade på første skudd mot hvert nytt mål).

## Tier 2
- Ironwall: 1 Naglede plater (mye mer helse og rustning). 2 Piggskjold (fiender som slår ham skader seg selv, roper lenger). 3 Jernbastion (under halv helse: tar halv skade i 5 sek, én gang per kamp).
- Frostbrand: 1 Frostsmidde økser (+45 % skade). 2 Blodrus (raskere slag, helse, rustning). 3 Frostbitt (hvert treff bremser fienden).
- Thunderbore: 1 Større løp (mer skade, større område). 2 Forsterket stativ (+2 rekkevidde, helse, rustning). 3 Sjokkbølge (treffene dytter fiender bakover).
- Hearthkeeper: 1 Klarere lykt (leger mer). 2 Glødesirkel (leger oftere og lenger unna). 3 Varm glo (leger to allierte om gangen).

## Tier 3
- Pyreguard: 1 Bred dyse (større område, helse). 2 Kulltank (varmere, lenger flamme). 3 Glødende bakke (det som treffes brenner videre).
- Siegebreaker: 1 Mothaker (+30 % skade). 2 Vinsj (lader raskere). 3 Spidd (harpunen treffer opptil to fiender bak målet).
- Warbanner Captain: 1 Jernbanner (helse og rustning). 2 Bredt banner (auraen når lenger, mer skade). 3 Samling (allierte i auraen slår 30 % hardere og gror sakte tilbake).
- Huskarl: 1 Daneøks (+45 % skade). 2 Skjold og brynje (mye mer helse og rustning). 3 Feiende slag (hvert slag treffer opptil tre).

## Åpent / neste steg
- Hærstørrelse: boten ender med ca. 27 units på wave 20. Det er greit (bestemt 3. okt), så lenge det ikke blir rundt 40. Plass i hæren beholdes på 20 / 30 / 40.
- Ca. 30 fiender per wave (målet) er ikke lagt inn ennå. Wavene har fortsatt 10–40 fiender.
- Testbenken tester bare grunnversjoner (nivå 0) foreløpig.
- Ikke avklart: skal Longfang koste litt mer enn 10?
- Shieldguards oppgraderinger gir mindre målbar styrke enn de andre Tier 1 (ca. +40 % mot +100 %), fordi testene måler drepeevne.

## Deflasjon (4. okt 2026)
Spilleren kunne maksere nesten alt og nå Tier 4 før wave 10. Nå er det knapphet igjen:
- Innsamling er omtrent halvert: gull hvert 12. sekund (før 8), tømmer og stein hvert 10. (før 5), jern hvert 12. (før 6), kull hvert 16. (før 8). Fortsatt 1 per arbeider.
- Arbeidere: 5 gull, men prisen stiger med 3 for hver arbeider etter den 8. (før: +2 etter den 10.).
- Barracks er priset etter verdenene: II = 154 tømmer, 88 stein, 35 jern. III ≈ 400 tømmer, 270 stein, 135 jern. IV ≈ 585 tømmer, 390 stein, 230 jern, 100 kull.
- Mål (målt med simulering): en vanlig spiller når Tier 2 på slutten av World 1 (ca. wave 9), Tier 3 midt i World 2 (ca. wave 16) og Tier 4 i World 3 (ca. wave 26). En spiller som satser alt på økonomi kan komme til wave 5, 12 og 18.
- Warden-utstyr og trening koster dobbelt. Verktøy koster 1,5 ganger.
- Wavene er stemt om til den nye økonomien. Den simulerte spilleren når wave 30 i 27 av 30 spill.
- Tallene ligger i `tools/economy.json`.

### Billigere Barracks (4. okt 2026, ettermiddag)
- Barracks kostet for mye til at man fikk utvidet før mot slutten. Prisene er omtrent halvert: II = 84 tømmer, 48 stein, 19 jern. III = 222 tømmer, 148 stein, 74 jern. IV = 324 tømmer, 216 stein, 126 jern, 54 kull.
- Den simulerte spilleren når nå Tier 2 på wave 6, Tier 3 på wave 12 og Tier 4 på wave 22. En spiller som satser alt på økonomi: wave 3, 7 og 12.
- Wave 5–30 er stemt om etterpå. Den simulerte spilleren når wave 30 i 27 av 30 spill.

## Tilbakemelding 4. okt, ettermiddag
- Arbeidere: 5 gull for de 6 første på hvert sted; deretter +4 gull for hver (før: prisen steg for alle etter 8 totalt).
- Gull og ressurser kommer per tur: hver arbeider går fra gruva til lageret (leverer når han kommer frem, med et lite tall over lageret) og tilbake. En tur tar like lang tid som før (gull 12 s, tømmer/stein 10 s, jern 12 s, kull 16 s), så inntekten er den samme per arbeider.
- Barracks III billigere: ca. 150 tømmer, 100 stein, 50 jern. Barracks IV dyrere: ca. 630 tømmer, 420 stein, 245 jern, 105 kull (ellers kunne man rushe den før wave 10 med billige arbeidere).
- Høyere tiers er verdt mer per plass og per gull (`tools/tier_power.py`): Ironhulk ×2,45 kraft (fersk 1190 HP, 36 skade/s), Ironwall ×1,8, Thunderbore og Captain ×1,6, Skyspear og Hearth Engine ×1,5, Mammoth ×1,25, Siegebreaker ×1,15. HP og skade ganges med kvadratroten.
- Razorclaw (raptor): 220 HP, 19 skade (før 160/16).
- Vanskelighet: World 1 som før; World 2 og 3 strammet inn (simulert spiller holder 80 % av wavene i World 2 og 72 % i World 3). Wave 15 og 19 litt dempet. Den simulerte spilleren når wave 30 i ca. halvparten av spillene.
- Rustning: trekkes fra hvert slag, minst 1 skade går gjennom. «Gjennomborer» ignorerer så mye rustning. Rustning er mest verdt mot mange små slag.
- Ordrelinjen viser valgt unit: bilde, hva neste oppgradering gir (HP 280 → 350 (+70) osv.), og verdi: gull per skade/s og gull per 100 HP med rustning (vanlig fiendeslag på 20 som mål).

### Warden nerfet (4. okt, kveld)
- Brukeren kom til wave 25 nesten bare ved å oppgradere Warden. Fullt oppgradert holdt han wave 3–9 helt alene.
- Nå: sverd +7 skade og +8 % angrepstakt per nivå (var +12 / +15 %), skjold +220 HP (var +350), rustning +1 (var +2), +5 % HP og skade per Warden-nivå (var +8 %). Fullt oppgradert: ca. 2700 HP, 81 skade, 8 rustning. Han holder nå bare til ca. wave 6 alene.

### Wardens evner og helse (4. okt, kveld)
- Tre evner man bruker selv under kampen (knapper nede til venstre, eller Z, X, C), kjøpt og oppgradert i Sanctum (3 nivåer, nivå 1 låser opp). De lades opp igjen og er klare ved starten av hver wave:
  - Flammesjokk: lammer fiender innen 6–8 m i 2–3 s. Lades på 18/15/12 s. Pris 20/30/45 gull + jern (kull på nivå 3).
  - Virvelvind: snurrer med sverdet i 5 s og treffer alt innen ca. 2,7–3,3 m hvert 0,4 s (60–90 % skade). Lades på 30/25/20 s. Pris 30/45/65 gull + jern (+ kull).
  - Frostflamme: fryser fiender innen 10–14 m i 3–5 s (de blir blå), så går de sakte. Lades på 45/38/30 s. Pris 40/60/85 gull + jern og kull.
  - Bosser lammes og fryses kortere.
- Wardens helse følger med mellom wavene: han får 10 % tilbake i hver pause, og kommer tilbake på 25 % hvis han falt. I Sanctum kan han pleies til full helse for gull (ca. 4 gull per 10 % som mangler).

### Ordrelinjen (4. okt, kveld)
- Ordreknappene, «Gå samlet» og venting ligger bak én knapp («Ordre: Avanser ▸»).
- Tallene står i en tabell: Nå | Etter oppgradering, med endringen i grønt (rødt når det blir dårligere). Gull-radene: lavere er bedre.

### Venter (ikke gjort, brukeren sier fra)
- En oppgradering skal koste minst like mye som uniten kostet, og hvert nivå minst like mye som det forrige.

## Barracks åpner Forge (4. okt, versjon 18)

Hvert Barracks-nivå åpner neste Forge-nivå (nærkamp, avstand, rustning). Nivå 1 er åpent fra start, nivå 2 krever Barracks II, nivå 3 Barracks III, og et nytt nivå 4 krever Barracks IV:

| Spor | Nivå 4 | Effekt | Pris |
|---|---|---|---|
| Nærkampvåpen | Runesmidd egg | +58 % skade | 64 gull, 42 jern, 22 kull |
| Avstandsvåpen | Runeladning | +58 % skade | 64 gull, 42 jern, 22 kull |
| Rustning | Runeplater | +4 rustning | 60 gull, 45 jern, 20 kull |

Workshop (teknologi) er ikke låst. Barracks gir også mer plass i hæren: 20 / 32 / 46 / 62 / 80.

World 1 er gjort litt tøffere: bølge 5–7 ca. 10 % sterkere, bølge 10 ca. 25 %. Bølge 1–4 er uendret fordi selv 10 % ekstra fikk boten til å tape dem.
