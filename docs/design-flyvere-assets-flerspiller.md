# The Last Flame – flyvere, skjeletter, assets og flerspiller (2.–3. okt 2026)

## Assets: status og neste steg
- Stiltest laget (`prototype/askemyr-style-test.html`): leddet Hollow Husk og Ashen Brute med stå, gå, angripe, ta treff og dø, ved en mur med port. Kan sees på nært hold og fra ekte spillkamera. Dette er en bevegelses-skisse, ikke ferdig grafikk.
- Valgt stil: nr. 2, "detaljert stilisert". Ekte modeller laget i et 3D-verktøy, med tydelige former og sterke farger, men ekte ansikter, rustning og tekstur. Ikke realistisk.
- Modellene kan ikke lages i kode. To veier (ikke valgt ennå): AI 3D-verktøy (f.eks. Meshy, Tripo, Rodin) med modell-brief, eller ferdigkjøpte pakker i én felles stil. Modellene leveres som .glb og settes inn, rigges og animeres.
- Rytme: to units/fiender om gangen, testet i stiltesten og på ekte spillkamera før neste par. Først Husk og Brute.
- Fra spillkameraet er en unit bare noen få piksler høy. Silhuett, farge, glød og bevegelse betyr mer enn fine detaljer.
- Modellene må være lette (få flater), dele skjelett og materialer per familie, og ha enklere versjon langt unna, så mange kan vises samtidig.
- Deretter: full asset-liste (units, fiender, bygninger, effekter, UI), sortert etter skjelettfamilie og prioritet.

## Warden: utseende (3. okt 2026)
- Referansebilde: ridder i svartnet jern med gullkant, solemblem, sverd og skjold med ild i sprekkene.
- Retning: majestetisk, ikke "fallen". Mer gull og lys, mindre lava og ruin. Han er flammens vokter og helten.
- Han kan være mer detaljert enn vanlige units (det finnes bare én, og han er større), men må fortsatt passe stil nr. 2.
- Visuelt språk for flammens side: svartnet jern, gullkant, solemblem, varm gyllen glød. Kan brukes på Warden, porten, nivå 3-utstyr og kuppelen.
- Skill fra fiendene: flammens side er gyllen og varm. Fiendenes sprekker (Ashen Brute m.fl.) er matte, røde og askete.
- Før 3D-verktøy trengs et rent "character sheet": rett forfra, nøytral bakgrunn, armene litt ut fra kroppen, kappen ikke over beina.

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

## Speiding (ikke MVP)
- Alle kan kjøpe et kort blikk (ca. 5 sekunder) på motstanderlagets units.

## Åpne spørsmål
- Har porten egen helse, eller er det flammen som er "kongen"? Hva skjer når porten faller?
- Hvordan er lagene satt opp: hvor mange spillere per lag, og hvem møter hvem når det er f.eks. 8 lag?
- Nøyaktig wave for arenaen (7 eller 8).
- Hvilke sendbare units finnes, og hva koster de per verden?
- Hvor mye gull gir en lekk, og hvor mye ressurser vinner arenaen?
- Modeller: AI 3D-verktøy eller ferdigkjøpte pakker?
