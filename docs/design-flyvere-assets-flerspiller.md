# The Last Flame – flyvere, skjeletter, assets og flerspiller (2.–3. okt 2026)

## Assets: status og neste steg
- Stiltest laget (`prototype/askemyr-style-test.html`): leddet Hollow Husk og Ashen Brute med stå, gå, angripe, ta treff og dø, ved en mur med port. Kan sees på nært hold og fra ekte spillkamera. Dette er en bevegelses-skisse, ikke ferdig grafikk.
- Valgt stil: nr. 2, "detaljert stilisert". Ekte modeller laget i et 3D-verktøy, med tydelige former og sterke farger, men ekte ansikter, rustning og tekstur. Ikke realistisk.
- Modellene kan ikke lages i kode. To veier (ikke valgt ennå): AI 3D-verktøy (f.eks. Meshy, Tripo, Rodin) med modell-brief, eller ferdigkjøpte pakker i én felles stil. Modellene leveres som .glb og settes inn, rigges og animeres.
- Rytme: to units/fiender om gangen, testet i stiltesten og på ekte spillkamera før neste par. Først Husk og Brute.
- Fra spillkameraet er en unit bare noen få piksler høy. Silhuett, farge, glød og bevegelse betyr mer enn fine detaljer.
- Modellene må være lette (få flater), dele skjelett og materialer per familie, og ha enklere versjon langt unna, så mange kan vises samtidig.
- Deretter: full asset-liste (units, fiender, bygninger, effekter, UI), sortert etter skjelettfamilie og prioritet.

## Warden: utseende (låst 3. okt 2026)
- Valgt konsept: `art/warden-concept.png`. Guddommelig ridder i hvit og elfenbensfarget rustning med gullkant, glorie, solemblem på bryst, skjørt og banner, hvit kappe med fillete kant. Det tidlige mørke utkastet ligger i `art/warden-concept-early-dark.png`.
- Kjernen: han er guddommelig, men bærer flammens sverd og skjold. Flammen bor i våpnene: sprekker av glød i sverdet, en flamme midt i skjoldet.
- Glorien er hans kjennetegn. En lysende gyllen ring over hodet synes også fra spillkameraet, der resten bare er noen få piksler.
- Hvit og gull mot mørk askebakke gir sterk silhuett. Han skiller seg tydelig ut fra hæren og fiendene.
- Glød i våpnene: helst gyllen til hvitglødende, ikke lavarød, så flammens side holder seg varm og gyllen. Fiendenes sprekker (Ashen Brute m.fl.) er matte, røde og askete.
- Obs: Fallen Seraph og Fallen Acolyte i Vrangheim har også hvit kappe og glorie. For at de ikke skal ligne Warden: deres glorier er brutte eller magenta og flimrer, kappene er skitne og lilla-flekket. Warden har den eneste hele, gylne glorien.
- Han kan være mer detaljert enn vanlige units (det finnes bare én, og han er større), men skal fortsatt passe stil nr. 2 (detaljert stilisert, ikke fotorealistisk).
- Før 3D-verktøy trengs et rent "character sheet" av samme design: rett forfra, nøytral bakgrunn, armene litt ut fra kroppen, kappen ikke over beina.

## Visuell retning: stort og episk (ønske for ferdig versjon)
- Porten og tårnene skal være mye større og mer majestetiske, i Ringenes herre-stil (tenk Helms dyp / Minas Tirith): høye tårn, en massiv port, tykk mur.
- Slagmarken skal føles som et ekte slag med veldig mange skapninger samtidig.
- Alt skal generelt være større i ferdig versjon.
- Praktisk: størrelsesforholdet mellom porten og unitene er det som gir følelsen (liten hær foran en enorm port). Kart, kamera/zoom og ytelse med mange units må planlegges for det.
- Mål: ca. 30 fiender per wave. Med egen hær blir det ca. 60 animerte skapninger samtidig, mer ved boss-waves og sendte units.

## Oppgradering av units
- Inspirert av Squadron: færre units, men hver unit oppgraderes. Se `oppgraderinger-og-balanse.md`.

## Skjelettfamilier (animer per kroppstype, ikke per skapning)
1. To bein: alle egne units, acolytes, husks, Wardens.
2. Fire bein: ulver, villsvin, beist.
3. Seks bein: insekter, edderkopper, krabber (krabber går sidelengs og får klør).
4. Trær: Thornling, Rotroot Treant.
5. Slange/hale: slanger, sirenens hale, sjømonstre, tentakler, krypende røtter.
6. Flyvere: liten kropp, store vinger (flakse, gli, stupe).
- Tillegg som kan festes på alle: vinger (f.eks. Fallen Seraph), klør/ekstra armer (Mantis, krabbe).
- Ingen skjelett: skygger, sverm og spøkelsesting lages som partikkelskyer.
- Vrangheim-utseendet (lilla hud, magenta årer, cyan øyne) lages helst som shader/omfarging oppå.
- World 4 trenger trolig en egen maskinfamilie (droner m.m.).

## Flyvere (låst)
- Flammekuppelen: Den siste flammen lager en kuppel over byen. Kuppelen er alltid der, men usynlig til noe treffer den (oransje bølge, som ild på glass). Kanten sitter på muren, med en åpning over porten som bare er like høy som porten.
- Kuppelen brenner litt og er et gjerde, ikke et våpen. Kloke flyvere (drager, serafer) glir langs den. Ville flyvere (gale fugler, insekter) smeller inn, brennes, faller ned utenfor muren og går til porten.
- Flyvere ignorerer hæren og flyr over unitene rett mot porten (som "kongen" i Squadron). De svever ved porten og angriper den.
- Mens de svever ved porten er de lave, så alle units nær porten kan treffe dem, også nærkamp.
- Høyt oppe kan bare skyttere treffe dem (Longfang, Ironshot, Thunderbore). Skutt ned = de faller og fortsetter på bakken der de landet.
- Flyvere skal være raske, mange og skjøre. Store flyvere (drage) er sjeldne skremmende hendelser.
- Pyreguard (sterk mot sverm) er naturlig motsvar ved porten.
- Ingen angriper muren, bare porten.
- Senere/valgfritt: swoopers (stuper, slår, flyr opp igjen), bærere som slipper fiender ved porten, kuppelen sprekker når flammen er svak eller en boss angriper den.

## Flyver-waves (låst)
- Wave 5 (World 1, Askemyr): Ash Crow / askekråker. Ny skapning. Bygget i versjon 20 (`tools/ashcrow.py`).
- Wave 15 (World 2, Vrangheim): Locust Swarm. Sverm, skjør, passer Pyreguard. Flyr fra versjon 21 (gresshopper finnes også i wave 13, 14 og 17).
- Wave 25 (World 3): drager. Unntaket fra "mange og skjøre": få, store og skremmende.
- Wave 35 (World 4, guddommelig robotikk): gale droner. Maskinfamilien.

## 1 mot 1-arena (må med)
- Rundt wave 7–8 (eksakt wave ikke bestemt).
- Lag A stemmer frem sin representant, lag B gjør det samme. De møtes i en arena i midten.
- Vinneren tar gull, stein, tømmer og kull, som deles mellom alle på vinnerlaget.
- Vinneren får et Champion-flagg.

## Sende units til motstanderen
- Spillere kan sende fiende-units fra verdenene til motstanderen. Billigere i World 1, dyrere i World 2, 3 og 4.
- Hvis en sendt unit lekker gjennom, får avsenderen gull.
- Den som sender flest units får et eget merke/flagg.

## Flerspiller: grunnregler (låst 3. okt 2026)
- **Lag:** 2 lag à 4 spillere, som klassisk Squadron. 8 spillere i én kamp.
- **Hver spiller har sin egen port og sin egen hær.** Fire porter per lag, side om side.
- **Én felles Warden per lag (kongen).** Alle fire porter fører opp til samme citadell med flammen. Fiender som bryter gjennom hos hvem som helst, går dit, og Warden kjemper mot dem. Når en fiende når flammen, taper hele laget.
- **Warden eies av laget.** Alle fire kan betale for utstyr og trening i Warden's Sanctum. Erfaring fra drap gjelder for laget.
- **Arena:** etter wave 8, 18 og 28 (endret 4. okt: tre arenaer, ikke bare én).
- **Sending:** man sender skapninger fra verdenen laget er i nå (World 1 sender Askemyr-skapninger osv.). Pris og styrke stiger per verden.

- **Lagspill: ingen deling av gull.** Spillere kan ikke gi hverandre gull (det blir bare krangel).
- **Hjelp ved lekk:** når en spiller har drept sin egen wave og en lagkamerat har lekket, flyttes de gjenlevende soldatene hans automatisk opp til Warden og kjemper der. Etter waven går de tilbake til sin egen port.
- **Gull for lekk som en lagkamerat dreper** (eksempel: skapning verdt 20 gull lekker fra P1, P2 dreper den):
  - 25 % går tapt (lekkstraff): 5.
  - Lekkeren (P1) får 25 %: 5. Hjelperen (P2) får 50 %: 10.
  - Hjelperen velger: beholde alt (P1 5 / P2 10), gi halvparten tilbake (P1 10 / P2 5) eller gi alt tilbake (P1 15 / P2 0).
  - Ikke bestemt: hvem får gullet når Warden selv dreper skapningen (forslag: lekkeren får 75 %).
- **Hvem sender til hvem:** fast par. Spiller 1 på lag A sender til spiller 1 på lag B, og omvendt. (Forslag, ikke kommentert.)
- **Når sendte units kommer:** de legges til motstanderens neste wave og kommer gjennom portalen sammen med den. (Forslag.)
- **Sendepris (World 1, gull), 25 % billigere enn første forslag:** Husk 3, Spider 3, Serpent 5, Spitter 5, Brute 8, Beetle 9. World 2 ca. ×2, World 3 ca. ×3,5.
- **Lekk-gull for sendte units (godkjent):** når en sendt skapning bryter gjennom porten, får avsenderen halve sendeprisen tilbake.
- **Sende-flagg:** den som har sendt mest (i gull) når kampen er over, får flagget.
- **Arena wave 8: hærduell (valgt).** Hvert lag stemmer frem én spiller. En kopi av begge hærene settes inn i en rund arena midt på kartet. Ca. 60 sekunder, alle ser på. Siste hær som står, vinner. Ingen units dør på ekte. Vinnerlaget deler premien (forslag: 40 gull + 20 stein + 20 tømmer + 10 kull per spiller), og vinneren får Champion-flagget.
  - Svakhet: den rikeste spilleren vinner ofte. Laget løser det selv ved å stemme frem den beste hæren.
  - Ikke bestemt: tidsgrense-regel hvis begge står etter 60 sekunder (forslag: mest gjenværende HP vinner), og hvordan arenaen ser ut.

## 1 mot 1 mot computer (bygget 4. okt 2026)
- Prototype av sending før ekte flerspiller. Rivalen er den samme fornuftige spilleren som simuleringene bruker. Den spiller sitt eget spill i bakgrunnen med samme waves, egen økonomi, hær og Warden.
- Send-fanen: i byggefasen kjøper du skapninger fra verdenen dere er i, som allerede har dukket opp. De kommer bak rivalens neste wave. Bryter en gjennom porten hans, får du halve prisen tilbake. Maks 24 per wave. «Angre siste» gir pengene tilbake.
- Rivalen sender 35 % av gullet sitt fra wave 3 (justert 4. okt). Det du får, vises i «Neste wave» merket SENDT.
- Sendepriser: Husk 3, Spider 3, Spitter 5, Serpent 5, Brute 8, Beetle 9, Stalker 6, Broodmother 12, Colossus 30. World 2 og 3 har egne, høyere priser.
- I 1 mot 1 er portalens egne waves på 47 % styrke; resten av presset kommer fra rivalen (som i Squadron).
- Den som mister flammen først, taper. Faller begge samme wave, eller står begge etter wave 30: uavgjort.
- Målt med to computere mot hverandre: ca. 5 sendte per wave hver vei; ca. 1/3 av kampene avgjøres på wave 19 (18 Acolytes som leger), resten går til wave 30.
- Kan slås av før første wave (Send-fanen); da er spillet som før.
- Se rivalen (bygget 4. okt): rivalen har sin egen slagmark til høyre for din, og waven hans går live samtidig med din. Kart nede i høyre hjørne viser begge basene, alle units som prikker og hvor kameraet er; trykk på kartet for å flytte dit. «Rival»-knappen hopper dit, og man kan dra skjermen over. Ser du på ham, viser linjen øverst hans tall (lilla kant). Mellom wavene ser du hæren hans vokse når han kjøper.
- Rivalens resultater (lekk-gull, det han sender deg, om flammen hans falt) kommer når hans wave er ferdig, ikke når din er det.
- Senere: betal ressurser for et kort blikk (5–10 sek) på motstanderens base i ekte flerspiller. Nå er det fritt innsyn.
- Arena (bygget 4. okt): etter wave 8, 18 og 28 møter en kopi av hæren din en kopi av rivalens hær på slagmarken, i maks 60 sekunder. Ingen dør på ekte. Siste hær som står, vinner; går tiden ut, vinner den med mest helse igjen (andel). Vinneren får 40/80/120 gull, 20/40/60 tømmer og stein, 10/20/30 kull og et Champion-flagg. Byggefasen starter etter arenaen med full tid.
- Arenaen er en hendelse (4. okt): kort med lagets champion (stemt frem; mot computeren er det deg) mot rivalens, antall soldater, premie og flagg, 10 sekunders nedtelling med trommer (eller «Til kamp!»), fakkelring på bakken, og et stort resultatkort etterpå.
- For at arenaen skal være rettferdig virker Warbanner Captains aura, Ironwalls taunt og Shieldguards skjoldmur nå for begge sider. Målt med to computere: omtrent jevnt (9–8), kampene tar ca. 20 sekunder.
- Ikke laget ennå: at rivalen sender smartere (nå tilfeldig), ekte flerspiller.

## Speiding (ikke MVP)
- Alle kan kjøpe et kort blikk (ca. 5 sekunder) på motstanderlagets units.

## Åpne spørsmål
- Besvart 3. okt: kongen er lagets felles Warden; 2 lag à 4; arena wave 8; send skapninger fra nåværende verden. Se "Flerspiller: grunnregler".
- Besvart 3. okt kveld: ingen gulldeling; soldater flyttes automatisk til Warden; lekkgull-deling; sendepriser −25 %; arena = hærduell.
- Arenapremie, tidsgrense i arenaen, og hvem får gull når Warden dreper en lekk.
- Kan Warden dø, eller bare flammen? (I dag: fiende ved flammen = tap, Warden har HP men kampen går videre.)
- Modeller: AI 3D-verktøy eller ferdigkjøpte pakker?

## Smartere rival (4. okt, versjon 19)

Computeren velger det den sender ut fra hæren din, husker hva som virket, og sparer opp til store angrep (porten din under 60 %, hæren krympet, ny verden neste wave, eller full sparegris). Samme gull gir ca. 75 % mer trøbbel enn tilfeldige valg. Spillet forteller hvorfor han valgte som han gjorde.

## Bastion med fire sider (10. okt 2026, version 23)

Rune (10. okt): tre nye spillere i tillegg til nord: øst, sør og vest, hver med sin egen arbeiderlandsby, Barracks og resten. Ingen waves på de nye sidene ennå. Finn en skala for Bastion.

- **Ett lag på fire rundt én flamme.** Dette er laget fra «2 lag à 4»: hver spiller holder én himmelretning. Nord er deg. Alle fire portene fører inn til samme citadell, og Warden er lagets konge der.
- **Hver side har:** sin portal og slagmark rett ut fra byen, sin port med tårn, sitt distrikt (landsby med gruver, Longhouse, Barracks, Forge, Workshop) og egne bannerfarger (nord blå, øst grønn, sør gul, vest rød).
- **Skala:** avstanden port til flamme er den samme som før (ca. 35 m), og distriktet ditt er like bredt (35 m). Derfor er kampen og balansen helt uendret. Det som er større er muren: den går nå rundt hele byen som et kvadrat på ca. 70 × 70 m (før en stripe på 35 m). Med slagmarkene er kartet ca. 170 m fra portal til portal.
- **Mellom distriktene:** innerst skrår distriktsmurene inn mot plassen rundt citadellet, så fire distrikter får plass uten å kollidere. I de fire hjørnene ligger gamlebyen (hus, plass til felles bygninger senere). Ringveien går rundt citadellet og binder distriktene sammen; det er veien hjelpere bruker når de går til Warden.
- **Ledige plasser:** øst, sør og vest står klare med landsby slik den ser ut ved start (gull, tømmer og stein bygget). Skilt over porten: «Øst · ledig plass».
- **Kamera:** ny knapp «Bastion» viser hele byen ovenfra (også på telefon). Man kan dra og zoome rundt hele byen.
- **Rivalen** (1 mot 1) har flyttet lenger ut (x = 140), så østsiden din får plass. Kartet i hjørnet ser likt ut som før.
- **Kode:** `tools/bastion.py`. `SIDES` og `sideToWorld(side, x, z)` i logikken: hver spiller regnes i egne koordinater (portalen mot −z), og `sideToWorld` snur punktet rundt flammen. Det er det 2 mot 2 / 4 mot 4 skal bruke.
- **Neste:** fylle sidene med spillere (lagkamerater online eller computer), deretter waves på alle fire sider og hjelp ved lekk via ringveien. Motstanderlaget får sin egen Bastion.
