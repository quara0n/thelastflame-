# Stilguide – menneskene (flammens side)

Utkast 29. okt 2026. Gjelder alle egne units, heltene, arbeiderne og Warden. Bygger på det som allerede er låst: stil nr. 2 «detaljert stilisert», Warden-konseptet (`docs/art/warden-concept.png`) og landsbykonseptet (`design/landsby-konsept.png`).

## Kjernen i én setning
Et nordisk folk av stein, tømmer og tidlig dampteknikk som vokter den siste flammen: mørk marineblått stoff, varmt mørkt stål, messing og lær, og en liten gyllen glo i hver soldat.

## Stil
- Detaljert stilisert, som moderne Blizzard-figurer (Warcraft, Hearthstone): litt store hender, skuldre og våpen, tydelige former, håndmalte teksturer. Ikke fotorealistisk, ikke tegneserie.
- Fra spillkameraet er en soldat bare noen få piksler høy. Silhuett og farge betyr mest: hver unit skal kunne kjennes igjen bare på omrisset (skjold, øks, langt løp, kanon, lykt, banner, tank på ryggen).
- Våpenet er litt for stort. Det er det spilleren ser.

## Farger
| Rolle | Farge | Brukes til |
|---|---|---|
| Hovedfarge | Mørk marineblå | Tunika, kappe, banner, skjoldflate |
| Emblem | Hvitt hjortehode | Bryst, skjold, banner, beltespenne |
| Metall | Mørkt, varmt stål | Hjelmer, plater, våpen |
| Detaljer | Messing og kobber | Nagler, kanter, damptanker, rør |
| Stoff 2 | Brunt lær og pels | Remmer, støvler, belter |
| Glød | Gyllen til hvit | Emblemets glo, oppgradering 3, Warden |

Fiendene gløder matt rødt og askete. Vår glød er alltid gyllen og varm, aldri lavarød.

## Tiers synes på utstyret
- **Tier 1 (folket):** ringbrynje, lær, enkle stålhjelmer. Mest blått stoff og lær.
- **Tier 2 (veteranene):** mer stål, tyngre plater, pels. Mer metall enn stoff.
- **Tier 3 (eliten):** fullt utstyr, messingpynt, kapper, tydelig glød i emblemet.
- **Tier 4 (maskinene):** dampmaskiner og store dyr. Messing, kjeler, røyk, glødende ovner.
- **Warden:** den eneste i hvitt og gull, med hel gyllen glorie. Ingen andre får hvitt.

## Oppgraderinger (samme modell, nytt utstyr)
Hver unit har én modell med av/på-deler, ikke fire modeller:
- Nivå 1: skulderplater / bedre hjelm.
- Nivå 2: kappe eller pels, større våpen.
- Nivå 3: glødende rune eller glo på våpen og emblem (gyllen).
Delene lages som egne små modeller som festes på skjelettet.

## Rosteret
- **Tier 1:** Shieldguard (rundskjold, kort sverd), Stormreaver (stor skjeggøks, ingen hjelm), Ironshot (damprifle med messingtank), Longfang (veldig langt musketløp).
- **Tier 2:** Ironwall (tunge naglede plater, tårnskjold), Frostbrand (to blå iskalde økser, pels), Thunderbore (kanon på stativ), Hearthkeeper (leger, bærer en lykt med glo).
- **Tier 3:** Pyreguard (flammekaster, kulltank på ryggen), Siegebreaker (harpun med dampvinsj), Warbanner Captain (stort banner med hjorten), Huskarl (daneøks, rundskjold, tung brynje).
- **Tier 4:** Ironhulk (dampgolem), War Mammoth (mammut med krigstårn), Skyspear (kjempe-ballista), Hearth Engine (rullende smie).
- **Heltene:** Flammeridder, Askejeger, Glødeprest.
- **Arbeiderne:** gruvearbeider, tømmerhugger, steinhugger (enkle, samme kropp).
- **Warden:** låst konsept.

## Slik lages figurene
1. **Karakterark:** ett bilde per unit med front, side og bak, A-stilling, grå bakgrunn (Higgsfield). Rune godkjenner.
2. **3D:** arket gjøres om til en .glb med tekstur (Tripo H3.1 eller Meshy i Higgsfield), ca. 8–15 000 flater.
3. **Skjelett og animasjon:** alle to-beinte deler ett menneskeskjelett (stå, gå, slå, skyte, ta treff, dø). Rigges automatisk (Meshy) eller i Blender.
4. **Inn i spillet:** .glb lastes i three.js i stedet for dagens klosser, testet på mobil (390 px) med 60 figurer samtidig.

Rekkefølge: Tier 1 (4 stk) først, så Warden, så heltene, så Tier 2–4.
