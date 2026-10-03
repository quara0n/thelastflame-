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
- Wave 5 (World 1, Askemyr): Ash Crow / askekråker. Ny skapning.
- Wave 15 (World 2, Vrangheim): Locust Swarm. Sverm, skjør, passer Pyreguard.
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
- **Arena:** wave 8.
- **Sending:** man sender skapninger fra verdenen laget er i nå (World 1 sender Askemyr-skapninger osv.). Pris og styrke stiger per verden.

### Forslag under de låste reglene (ikke låst, kan justeres)
- **Hvem sender til hvem:** fast par. Spiller 1 på lag A sender til spiller 1 på lag B, og omvendt. Gir en tydelig "motstander" å følge med på.
- **Når sendte units kommer:** de legges til motstanderens neste wave og kommer gjennom portalen sammen med den.
- **Pris (World 1-forslag, gull):** Husk 4, Spider 4, Serpent 6, Spitter 7, Brute 10, Beetle 12. World 2 ca. ×2, World 3 ca. ×3,5. Grunnlag: Tier 1-unit koster 10 gull.
- **Lekk-gull:** når en sendt unit bryter gjennom porten, får avsenderen halve sendeprisen tilbake.
- **Sende-flagg:** den som har sendt mest (i gull) når kampen er over, får flagget.
- **Lekk til felles Warden:** en spiller som lekker mye, sender fiender opp til laget sitt. Det er presset som gjør lagspill viktig: nabospillere kan sende units over for å hjelpe (ikke bestemt hvordan).
- **Arena wave 8:** hvert lag stemmer frem én spiller. De to møtes i arenaen i midten med en kopi av hæren sin (ingen units dør på ekte). Vinnerlaget deler premien likt: forslag 40 gull + 20 stein + 20 tømmer + 10 kull per spiller, og vinneren får Champion-flagget.

## Speiding (ikke MVP)
- Alle kan kjøpe et kort blikk (ca. 5 sekunder) på motstanderlagets units.

## Åpne spørsmål
- Besvart 3. okt: kongen er lagets felles Warden; 2 lag à 4; arena wave 8; send skapninger fra nåværende verden. Se "Flerspiller: grunnregler".
- Hvordan kan nabospillere hjelpe hverandre (sende egne units over, dele gull)?
- Bekrefte sendepriser, lekk-gull og arenapremie (forslag over).
- Kan Warden dø, eller bare flammen? (I dag: fiende ved flammen = tap, Warden har HP men kampen går videre.)
- Modeller: AI 3D-verktøy eller ferdigkjøpte pakker?
