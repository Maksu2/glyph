# Glyph-100M Dataset v2.1 Report

Generated: 2026-06-01T05:04:22.223381+00:00

## Recommendation

B: v2.1 is cleaner than v2 and is the best current candidate, but 50k would still be 6.10 epochs. I recommend approving only a short stage-3 preflight or adding more clean sources before full 50k.

## Output

- selected variant: `D`
- train bin: `data/processed/glyph100_v2_1_train.bin`
- val bin: `data/processed/glyph100_v2_1_val.bin`
- docs JSONL: `data/processed/glyph100_v2_1_docs.jsonl`
- tokenizer: `data/processed/tokenizer.model`

## Counts

- train docs: 187,431
- val docs: 990
- train tokens: 133,401,769
- val tokens: 787,164
- total tokens: 134,188,933
- token/word ratio: 2.009

## Source Mix

| source | docs | total tokens | train tokens | val tokens |
|---|---:|---:|---:|---:|
| `wolne_lektury` | 1,525 | 3,143,341 | 3,128,722 | 14,619 |
| `wikipedia_pl` | 184,466 | 127,929,637 | 127,169,999 | 759,638 |
| `wikisource_pl` | 2,430 | 3,115,955 | 3,103,048 | 12,907 |

## Variant Comparison

| variant | total tokens | legacy tokens | 50k epochs | risk |
|---|---:|---:|---:|---|
| A | 149,098,802 | 14,909,869 | 5.49 | best quality compromise; legacy capped near 10% |
| B | 167,736,162 | 33,547,229 | 4.88 | more data, more legacy risk |
| C | 168,510,760 | 34,321,827 | 4.86 | legacy still too influential |
| D | 134,188,933 | 0 | 6.10 | cleanest but small; many repeated epochs at 50k |

## Rejection Reasons

```json
{
  "legacy_commerce": 126344,
  "legacy_quality_below_0_72": 123115,
  "legacy_forum": 48939,
  "legacy_price_like": 29066,
  "legacy_short_sentence_noise": 20801,
  "too_short": 8127,
  "legacy_seo": 2347,
  "html_present": 2191,
  "repeated_ngrams": 2118,
  "low_alpha_ratio": 1425,
  "legacy_navigation": 1048,
  "legacy_comments": 162,
  "too_long": 114,
  "low_unique_word_ratio": 86,
  "low_polish_signal": 59,
  "empty_after_clean": 48,
  "single_word_repetition": 47,
  "too_much_punctuation_or_symbols": 19,
  "too_many_urls": 15,
  "very_long_line": 2,
  "too_many_boilerplate_patterns": 2,
  "legacy_many_short_lines": 1
}
```

## Training Math

- stage 3 / 50k: 819,200,000 tokens = 6.10 epochs
- 100k: 1,638,400,000 tokens = 12.21 epochs
- 200k: 3,276,800,000 tokens = 24.42 epochs

## Final Random Samples

1. `wikipedia_pl` (1147) Stavropolis

   (1147) Stavropolis – planetoida z pasa głównego asteroid okrążająca Słońce w ciągu 3 lat i 155 dni w średniej odległości 2,27 au. Została odkryta 11 czerwca 1929 roku przez Grigorija Nieujmina w Obserwatorium Simejiz na górze Koszka na Półwyspie Krymskim. Nazwa planetoidy pochodzi od Stawropola, miasta w Rosji. Przed nadaniem nazwy planetoida nosiła oznaczenie tymczasowe (1147) 1929 LF.

2. `wikisource_pl` W miasteczku

   W miasteczku – utwór Klemensa Junoszy ze zbioru Drobiazgi W miasteczku – wiersz Józefa Gary ze zbioru „Wymysöjer śtytła” – miasteczko Wilamowice oraz jego osobliwości zawarte w zbiorze piosenek wilamowskich Józefa Gary W miasteczku – wiersz Marii Konopnickiej W miasteczku... – wiersz Georges’a Rodenbacha z antologii Liryka francuska

3. `wikipedia_pl` William Higgins (chemik)

   William Higgins, (ur. 1763 r. w Collooney, zm. w 1825) – irlandzki chemik, współtwórca nowożytnej teorii atomistycznej materii. W 1789 r., w wieku 26 lat, po ukończeniu studiów na Uniwersytecie w Oksfordzie, opublikował książkę, w której poparł teorię atomistyczną Antoine-Laurent de Lavoisiera, poszerzając ją o swoje pomysły. Był kierownikiem zbiorów mineralogicznych Dublińskiego Towarzystwa Królewskiego i od 1800 członkiem Królewskiego Towarzystwa Chemicznego. Specjalizował się w technikach wybielania tkanin. Higgins twierdził aż do śmierci, że John Dalton dokonał przeróbek jego dzieła z lat młodości i opublikował je jako swoje przemyślenia, przypisując sobie ich autorstwo. Dalton nigdy nie przyznawał się do plagiatu i do dziś uważany jest za twórcę nowożytnej atomistycznej teorii materii. Higgins z powodu choroby nie mógł bronić swoich praw do podstaw teorii atomistycznej. W jego pu...

4. `wikipedia_pl` Kevin O’Flanagan

   Kevin O’Flanagan (ur. 10 czerwca 1919 w Dublinie, zm. 26 maja 2006 tamże) – irlandzki sportowiec, specjalista medycyny sportowej, działacz sportowy, członek Międzynarodowego Komitetu Olimpijskiego. Studiował m.in. na uniwersytecie w Dublinie. Kierował narodowym instytutem rehabilitacji oraz obradami międzynarodowego kongresu rehabilitacji w Dublinie w 1969. Był członkiem brytyjskiej komisji medycznej w czasie olimpiady w Londynie w 1948, a w latach 1960–1976 lekarzem kadry olimpijskiej. Pełnił funkcję wiceprezydenta Komitetu Olimpijskiego Irlandii. Ogłosił szereg publikacji dotyczących kontuzji sportowych. W 1976 został wybrany na członka Międzynarodowego Komitetu Olimpijskiego, brał udział w pracach Komisji Medycznej MKOl (1980–1994) oraz Komisji ds. Programu Letnich Igrzysk Olimpijskich (1993–1994). W 1995 otrzymał godność członka honorowego MKOl. W młodości uprawiał kilka dyscyplin...

5. `wikipedia_pl` Glonojad

   Glonojady – potoczna nazwa przypisywana rybom odżywiającym się glonami. Popularność niektórych gatunków spowodowała przypisywanie im nazwy zwyczajowej glonojad, np.: rodzaj Gyrinocheilus lub cała rodzina okrągłoprzyssawkowatych (Gyrinocheilidae). Miłośnicy akwarystyki cenią glonojady za ich "pomoc" w ograniczaniu rozwoju glonów w akwarium. Do najbardziej znanych należą: grubowarg syjamski (Crossocheilus oblongus) (inaczej „kosiarka” – ryba kosząca glony) ryby z rodziny przylgowatych (Balitoridae) wymienione wyżej okrągłoprzyssawkowate oraz wiele gatunków zbrojników, między innymi: zbrojnik lamparci (Glyptoperichthys gibbiceps) ryby z rodzaju Ancistrus, a wśród nich wąsacz niebieski (Ancistrus dolichopterus), nazywany również zbrojnikiem niebieskim.

6. `wikipedia_pl` Wielki Bukowiec (wieś)

   Wielki Bukowiec – wieś w Polsce położona w województwie pomorskim, w powiecie starogardzkim, w gminie Skórcz, przy drodze wojewódzkiej nr 214. W latach 1975–1998 miejscowość administracyjnie należała do województwa gdańskiego. Położenie Wieś o układzie przestrzennym ulicowym rozwiniętym wzdłuż ulic bocznych, leży przy szosie z Pączewa do Wdy, na lekko falistej wysoczyźnie morenowej, na wysokości 93-115 m n.p.m. Na południu graniczy z obrzeżem Parku Narodowego „Bory Tucholskie”, na wschodzie przylega do podmokłych łąk, przez które przepływa rzeczka Węgiermuca, dopływ Wierzycy wypływający z Jeziora Czarnoleskiego. Północnym skrajem miejscowości przebiega linia kolejowa Skórcz – Szlachta, uruchomiona w sierpniu 1908 r., zamknięta na początku lat 90. XX w. Do sołectwa Wielki Bukowiec administracyjnie należą: Nowy Bukowiec (dawne nazwy: Piątki, Neu Bukowitzw; gwarze ludowej Pionki) oraz os...

7. `wikisource_pl` Żywot Józefa/XII

   XII Tu ku królowi Jakóba Józef wiedzie, ojca swego, a jako ji król wdziecznie przyjął, i jako im dał osiadłość, a to: ROZPRAWA DWANASTA. ROZMOWCE: JÓZEF — JAKÓB — FARAO (JÓZEF mówi:) Pójdzi-ż, namilejszy ojcze, do pana mojego, Bo wierz mi, wielki to dziw też będzie u niego. Wiem iże cię barzo rad będzie u siebie miał, A z tobą stare dzieje będzie rozprawował... JAKÓB: Już mię wiedź, kędy raczysz, ja idę za tobą, A snadź by mi i na śmierć nic nie ciężko z tobą; Bo już Pan Bóg twe sprawy kiedy cię tak przejrzał, Zawżdy na wszytko dobre snadź będzie obracał. JÓZEF przywiodszy ojca mówi ku królowi: Najaśniejszy mój panie, miłościwy królu! Raczył dziś Pan Bóg dziwnie ulżyć mego bólu: Ojca swego, któregom nie widział wiele lat. Teraz ku mnię przyjechał — któremum barzo rad. Zwłaszcza w takich przygodach, co on i ja miewał, Kiedy się panie dowiesz będziesz się dziwował. A takiem go tu przywi...

8. `wikipedia_pl` 2 Brygada Zmechanizowana

   2 Brygada Zmechanizowana Legionów im. Marszałka Józefa Piłsudskiego (2 BZ) – jednostka wojsk zmechanizowanych Sił Zbrojnych RP. Formowanie i zmiany organizacyjne Brygada utworzona została w połowie 1995 roku w wyniku przeformowania 6 Pułku Zmechanizowanego Legionów w Wałczu. Wchodziła ona wtedy w skład 2 Warszawskiej Dywizji Zmechanizowanej. W 1997 r., po rozformowaniu 2 Dywizji Zmechanizowanej, brygadę włączono w skład 8 Bałtyckiej Dywizji Obrony Wybrzeża. W 2001 r. 2 Brygada Zmechanizowana została dyslokowana do m. Złocieniec i jako samodzielny związek taktyczny podporządkowana dowódcy nowo utworzonego 1 Korpusu Zmechanizowanego w Bydgoszczy. Po rozformowaniu korpusu, w marcu 2004 r., brygada weszła w skład 12 Szczecińskiej Dywizji Zmechanizowanej. Obecnie brygada stacjonuje w dwóch garnizonach: Złocieniec i Czarne. Tradycje 2 BZ, decyzją Ministra Obrony Narodowej nr 110/MON z 17.07...

9. `wikipedia_pl` Ekspansybilność

   Ekspansybilność – reakcja ceny danego dobra na zmianę podaży, jest odwrotną sytuacją niż cenowa elastyczność podaży gdzie: – współczynnik ekspansybilności, – przyrost ceny, – wysokość ceny, – przyrost podaży, – wielkość podaży. Współczynnik ekspansybilności cen jest stosunkiem procentowej zmiany ceny dobra do procentowej zmiany podaży na to dobro. Mówi on, o ile procent zmieni się cena jeżeli podaż na dane dobro wzrośnie o 1%.

10. `wikipedia_pl` Wełnianka szerokolistna

   Wełnianka szerokolistna (Eriophorum latifolium) – gatunek rośliny z rodziny ciborowatych (Cyperaceae) (turzycowatych). Występuje w umiarkowanej strefie zarówno na niżu, jak i w górach w Europie, Ameryce Północnej i Azji. W Polsce jest dość rozpowszechniony (częstość występowania 3 w 5–stopniowej skali), jednak ostatnio liczebność tego gatunku maleje. Morfologia Pokrój Bylina trwała tworząca rozległe okazałe darnie. Łodyga Tępa, o trójkątnym przekroju, wewnątrz pełna, prosto wzniesiona, o wysokości od 20 do 60. Na szczycie szarozielonej łodygi, w kącie najkrótszego liścia - tzw. podsadki - wyrasta kilka kłosów zawierających kilkanaście do kilkudziesięciu kwiatów. Liście Odziomkowe płaskie o szerokości od 4 do 8 mm i długich wąskich blaszkach na górnej stronie rynienkowate, na dolnej ostrogrzbieciste, szorstkie na brzegach, najwyższe liście są znacznie krótsze łodygowe, bez blaszkowe, j...

11. `wikipedia_pl` (1996) Adams

   (1996) Adams – planetoida z pasa głównego asteroid okrążająca Słońce w ciągu 4 lat i 35 dni w średniej odległości 2,56 j.a. Została odkryta 16 października 1961 roku w Goethe Link Observatory niedaleko Brooklynu w stanie Indiana w ramach Indiana Asteroid Program. Nazwa planetoidy pochodzi od Johna Coucha Adamsa (1819–1892), brytyjskiego astronoma i matematyka. Przed jej nadaniem planetoida nosiła oznaczenie tymczasowe (1996) 1961 UA.

12. `wikipedia_pl` (742) Edisona

   (742) Edisona – planetoida z grupy pasa głównego asteroid okrążająca Słońce w ciągu 5 lat i 83 dni w średniej odległości 3,01 au. Została odkryta 23 lutego 1913 roku w Landessternwarte Heidelberg-Königstuhl, w Heidelbergu przez Franza Kaisera. Nazwa planetoidy pochodzi od Thomasa Edisona, amerykańskiego wynalazcy. Przed nadaniem nazwy planetoida nosiła oznaczenie tymczasowe (742) 1913 QU.

13. `wikipedia_pl` Wozzeck

   Wozzeck – trzyaktowa opera z librettem i muzyką Albana Berga. Osoby Wozzeck, żołnierz – baryton Tamburmajor – tenor Andres – tenor Kapitan – tenor Doktor – bas Błazen – tenor Maria, konkubina Wozzecka – sopran Małgorzata – alt Syn Marii – sopran chłopięcy czeladnicy – bas i baryton (lub tenor) żołnierze, służące, dzieci Treść Dzieje zawodowego żołnierza cierpiącego na halucynacje, którego dręczy sadystyczny kapitan i cyniczny doktor. Jego ukochana Maria, z którą ma nieślubne dziecko, zdradza go z majorem. Wozzeck mocno przeżywa jej nienawiść, zabija ją, a potem popełnia samobójstwo. Ogólną ideą utworu jest problem zagubienia człowieka w świecie bez wartości. Fabuła jest oparta na sztuce Woyzeck Georga Büchnera. Historia utworu Libretto zostało opracowane przez kompozytora na podstawie niedokończonego dramatu Georga Büchnera. W muzyce wyraźny jest, mimo ogromnej melodyjności i ekspresj...

14. `wikisource_pl` Biblia Gdańska/Druga Księga Kronik 28

   2 Krn 28 1 Dwadzieścia lat miał Achaz, gdy królować począł, a szesnaście lat królował w Jeruzalemie, i nie czynił, co było dobrego przed oczyma Pańskiemi, jako Dawid, ojciec jego; 2 Ale chodził drogami królów Izraelskich; nadto ulał i słupy bałwochwalskie. 3 Także i sam kadził w dolinie Benhennon, i palił synów swych ogniem według obrzydliwości pogan, których wygnał Pan przed synami Izraelskimi. 4 Ofiarował też i kadził na wyżynach, i na pagórkach, i pod każdem drzewem gałęzistem. 5 Przetoż dał go Pan, Bóg jego, w rękę króla Syryjskiego, którzy poraziwszy go, pojmali z ludu jego więźniów wiele, a przywiedli ich do Damaszku. Nadto i w rękę króla Izraelskiego podany jest, który go poraził porażką wielka. 6 Albowiem Facejasz, syn Romelijaszowy, pobił w Judzie sto i dwadzieścia tysięcy dnia jednego, wszystko mężów walecznych, przeto, iż opuścili Pana, Boga ojców swoich. 7 Zychry także, mo...

15. `wikipedia_pl` DirectShow

   DirectShow jest technologią programistyczną umożliwiającą obsługę strumieni wideo i audio na platformach Microsoft Windows. Zastosowanie Technologia DirectShow stosowana jest w aplikacjach multimedialnych wykorzystujących strumienie wideo i audio. Umożliwia między innymi odtwarzanie plików medialnych, pobieranie obrazu i dźwięku z urządzeń zewnętrznych takich jak kamery cyfrowe i karty telewizyjne, kodowanie/dekodowanie strumienia oraz dostęp do przesyłanych danych (poszczególnych klatek wideo) i ich przetwarzanie. DirectShow obsługuje większość popularnych typów plików medialnych (m.in. AVI, WAV, ASF, MIDI) oraz formatów kompresji (np. DV, MPEG-1, MPEG-4 część 2, MPEG Audio Layer-3 (MP3)). Historia i rozwój Pierwszą technologią Microsoft Windows umożliwiającą pracę z przechwytywaniem i wyświetlaniem strumieni wideo było Video for Windows (VfW), które pojawiło się na systemie Windows...

16. `wikipedia_pl` Barbara Rittner

   Barbara Rittner (ur. 25 kwietnia 1973 w Krefeldzie) – niemiecka tenisistka. W 1993 roku sklasyfikowana na 24 miejscu rankingu singlistek. Dotarła do czwartej rundy French Open 1996. Wygrała dwa turnieje WTA, w 2001 Antwerpia i 1992 Schenectady. Trzy tytuły deblowe, ostatni z 2002 roku z Dubaju. Reprezentantka Niemiec w Pucharze Federacji i Igrzyskach Olimpijskich w 1992 roku. Jako juniorka, w 1991 roku wygrała Wimbledon. Finały turniejów WTA Gra pojedyncza Gra podwójna Finały juniorskich turniejów wielkoszlemowych Gra pojedyncza (1) Gra podwójna (1)

17. `wikipedia_pl` AWeb

   AWeb – przeglądarka internetowa dla komputerów Amiga autorstwa Yvona Rozijna. Program był rozprowadzany jako część systemu AmigaOS 3.9. Do wersji 3.4 przeglądarka była dosyć prężnie rozwijana, lecz 8 czerwca 2002 zdecydowano o otwarciu jego kodu źródłowego i powołaniu projektu AWeb Open Source, którego zadaniem była kontynuacja rozwoju przeglądarki. Naświetlone w 2003 roku plany zakładały przepisanie kodu programu tak, aby możliwe było bezproblemowe jego portowanie między różnymi systemami (AmigaOS 3.x, AmigaOS 4.x, AROS, MorphOS). W kolejnym etapie zakładano wykorzystanie KHTML w wersjach przeglądarki oznaczonych numerem 4.x. Dodatkowo, prace miały przebiegać dwutorowo: stworzenie wersji Lite, która miała być przeznaczona dla Amig klasycznych oraz wersji właściwej dla nowego sprzętu (czyli w domyśle AmigaOne, Pegasos, czyli systemów AmigaOS 4.x i MorphOS). Obecnie jego rozwojem, dosy...

18. `wikipedia_pl` Apatania

   Apatania – rodzaj owadów z rzędu chruścików i rodziny Apataniidae. Larwy są niewielkie, budują rożkowate, lekko zakrzywione domki z rozszerzoną przednią częścią. Występują w źródłach, ciekach i rzadziej w jeziorach. U wielu gatunków z rodzaju Apatania występuje partenogeneza. U A. hispida, A. muliebris i A. forsslundi samców brak całkowicie, a u wielu innych samice dominują. Dotychczas opisano około 100 gatunków, z których 30 występuje w Europie, w tym 8 w Finlandii. W Polsce stwierdzono 5 gatunków (w tym jeden wykazywany na podstawie wątpliwego oznaczenia). Zobacz: Apataniidae Polski. Wykaz gatunków:

19. `wikisource_pl` Biblia Gdańska/Ewangelia wg św. Łukasza 20

   Łk 20 1 I stało się z onych dni dnia jednego, gdy uczył lud w kościele i kazał Ewangeliję, że nadeszli przedniejsi kapłani i nauczeni w Piśmie z starszymi, 2 I rzekli do niego, mówiąc: Powiedz nam, którą mocą to czynisz, albo kto jest ten, coć dał tę moc? 3 A on odpowiadając, rzekł do nich: Spytam i ja was o jednę rzecz, a powiedzcie mi: 4 Chrzest Jana byłli z nieba, czyli z ludzi? 5 A oni myślili sami w sobie, mówiąc: Jeźli powiemy, z nieba, rzecze: Czemużeście mu tedy nie wierzyli? 6 Jeźliż zasię rzeczemy, z ludzi, wszystek lud ukamionuje nas, ponieważ za pewne mają, że Jan jest prorokiem. 7 I odpowiedzieli, że nie wiedzą, skąd by był. 8 A Jezus im rzekł: I ja wam nie powiem, którą mocą to czynię. 9 I począł do ludu mówić to podobieństwo: Człowiek niektóry nasadził winnicę, i najął ją winiarzom, i odjechał precz na czas niemały. 10 A czasu swego posłał sługę do onych winiarzy, aby m...

20. `wikipedia_pl` Poszła na całość

   Poszła na całość (ang. She Went All The Way ) to książka dla dorosłych autorstwa Meg Cabot. W Polsce została wydana w 2004 roku, przez wydawnictwo Amber, a w USA w 2002 roku, przez wydawnictwo HarperCollins Publishers. Komentarz wydawcy "Wszystko jest tak, jak Lou sobie wymarzyła. Osiągnęła sukces. Jej scenariusze filmowe są rozchwytywane. Zdobyła popularność i powodzenie. Ale dobra passa się kończy. Dlaczego właśnie teraz? Dlaczego Bruno zostawia ją dla aktoreczki! Lou nie chce pracować nad nowym serialem z nadętym gwiazdorem (choćby był najseksowniejszym facetem na świecie)! I nie chce wylądować razem z nim w samym środku alaskiej głuszy po podejrzanej katastrofie helikoptera!" Bohaterowie Najważniejsi bohaterowie Lou Calabrese – główna bohaterka książki, pisarka scenariuszy filmowych Jack Townsend – główny bohater książki, aktor Tim Lord – reżyser filmowy Vicky Lord – przyjaciółka...

21. `wikipedia_pl` Chandyga

   Chandyga (ros. Хандыга) – osiedle typu miejskiego w azjatyckiej części Rosji, w Jakucji; ośrodek administracyjny ułusu tompońskiego. Leży na wschodnim krańcu Niziny Środkowojakuckiej, na prawym brzegu Ałdanu; ok. 300 km na wschód od Jakucka; 6638 mieszkańców (2010); przemysł materiałów budowlanych, spożywczy; muzeum geologiczne; przystań rzeczna. Przez miejscowość przebiega Trakt Kołymski.

22. `wikipedia_pl` (1100) Arnica

   (1100) Arnica – planetoida z pasa głównego asteroid. Odkrycie (1100) Arnica została odkryta 22 września 1928 roku w Landessternwarte Heidelberg-Königstuhl w Heidelbergu przez Karla Reinmutha. Nazwa planetoidy pochodzi od arniki, rośliny z rodziny astrowatych. Przed jej nadaniem planetoida nosiła oznaczenie tymczasowe (1100) 1928 SD. Orbita (1100) Arnica okrąża Słońce w ciągu 4 lat i 340 dni w średniej odległości 2,9 au. Należy do rodziny planetoidy Koronis.

23. `wikipedia_pl` Dongbei

   Dongbei (Chiny Północno-Wschodnie) () - region Chin, w skład którego wchodzą trzy prowincje: Heilongjiang, Jilin i Liaoning, rozciągające się na przestrzeniach Niziny Mandżurskiej (patrz również: Mandżuria). Dongbei jest uznawany za odmienny od reszty kraju ze względu na surowy, subsyberyjski klimat, a także historię i obyczaje. Zamieszkuje go łącznie ok. 100 mln osób. Historia Z terenów Dongbei pochodziły ludy, które najeżdżały Chiny i tworzyły własne państwa. Np. Kitanowie, którzy założyli państwo Jin, Dżurdżeni oraz Mandżurowie, którzy w XVII wieku opuścili ojczystą Mandżurię i w 1644 roku podbili Pekin instalując w Chinach mandżurską dynastię Qing. Na przełomie XIX i XX wieku region był pod kontrolą Rosji, która zbudowała przez jego tereny Kolej Wschodniochińską wiodącą z Syberii do Władywostoku, Dalnego oraz Port Arthur. Wpływy Rosjan osłabły po przegranej wojnie z Japonią (1904-...

24. `wikipedia_pl` Joel Rifkin

   Joel Rifkin (ur. 20 stycznia 1959 roku w East Meadow w stanie Nowy Jork w USA), to amerykański seryjny morderca, którego ofiarą w latach 1989-1993 padło 17 młodych kobiet, głównie narkomanek oraz prostytutek. W celu utrudnienia identyfikacji ofiar Rifikin ćwiartował ich ciała (trzech jego ofiar nigdy nie udało się zidentyfikować). Motywami zbrodni było to, że ze względu na swoją tuszę, Joel nie potrafił sobie radzić z kobietami. Aresztowano go 28 czerwca 1993 roku - nie zatrzymał się do kontroli drogowej. Gdy go zatrzymano, okazało się, że powodem ucieczki były znajdujące się w bagażniku zwłoki. Później przyznał się do pozostałych morderstw. Został skazany na 203 lata pozbawienia wolności. Ofiary

25. `wikipedia_pl` Choristodera

   Choristodera – rząd wodnych gadów. Jego najstarsi znani przedstawiciele żyli w środkowej jurze (Cteniogenys), a być może nawet późnym triasie (kontrowersyjny Pachystropheus); grupa dotrwała przynajmniej do końca eocenu, a być może nawet do wczesnego miocenu (przy założeniu, że do Choristodera należał rodzaj Lazarussuchus; część autorów klasyfikuje go jednak jako takson siostrzany Choristodera). Choristodera należą więc do kilku (obok ptaków, krokodylomorfów, lepidozaurów i żółwi) grup zauropsydów, które przetrwały wymieranie kredowe. Skamieniałe szczątki ich przedstawicieli znaleziono w Ameryce Północnej, Azji i Europie. Najwięcej w pokładach od późnej kredy do niższego eocenu. Filogenetyczna pozycja Choristodera nie jest pewna – różne analizy kladystyczne sugerują, że Choristodera mogły być bazalnymi przedstawicielami kladu Archosauromorpha (sensu Dilkes, 1998), bazalnymi lepidozauro...

26. `wikipedia_pl` Katowice Załęże

   Katowice Załęże – przystanek kolejowy w Katowicach, położony na terenie dzielnicy Załęże, w południowej Polsce. Przystanek, położony na międzynarodowej magistrali E 30, został wybudowany w 1957 roku, natomiast planowy ruch pociągów odbywa się tu od 1966 roku. Na przystanku zatrzymują się pociągi regionalne Kolei Śląskich jadące w stronę Częstochowy, Katowic, Lublińca i Gliwic. Ruch pasażerski Przystanek ten znajduje się w północno-zachodniej części Katowic, w pobliżu skrzyżowania ulic F. Bocheńskiego i J. Pukowca. Przynależy on do Zakładu Linii Kolejowych PKP Polskich Linii Kolejowych w Sosnowcu. Składa się z jednego dwukrawędziowego peronu wysokiego, do którego prowadzi przejście podziemne z ulicy J. Pukowca. Historia Przystanek Katowice Załęże powstał na linii kolejowej wybudowanej przez Towarzystwo Kolei Górnośląskiej, która pierwotnie łączyła Wrocław z Mysłowicami. W 1835 roku pro...

27. `wikipedia_pl` Hydrazony

   Hydrazony - grupa organicznych związków chemicznych o ogólnym wzorze: R1R2C=NNH2. Związki te otrzymuje się w reakcji kondensacji aldehydów lub ketonów z hydrazyną. Reakcja ta przebiega dwuetapowo. Pierwszy etap to addycja nukleofilowa substratów. Drugi etap polega na eliminacji cząsteczki wody.

28. `wikipedia_pl` Enkoder przyrostowy

   Enkoder inkrementalny, przyrostowy, impulsowy – przetwornik, którego zadaniem jest generowanie impulsów (przyrosty kątowe) odpowiadających ruchowi obrotowemu. Charakterystyczną cechą tych enkoderów jest stała liczba impulsów na wyjściu do 10000 impulsów/obrót, odpowiadająca rozdzielczości systemu pomiarowego. W celu kontroli kierunku (prawo-lewo), drugi w kolejności sygnał jest przesunięty fazowo o 90°. Licznik zewnętrznego systemu kontroli może być ponownie ustawiany dodatkowym zerowym impulsem. Pomiar położenia następuje niezależnie od rozdzielczości wyjściowej enkodera. Oznacza to, że każda rozdzielczość od 1 do 32768 impulsów na obrót może być uzyskana na podstawie wewnętrznego próbkowania. Takie precyzyjne rejestrowanie mechanicznego ruchu obrotowego i jego zamiana na sygnał elektryczny jest zasadnicze dla niezawodnego działania w pozycjonowaniu i CNC.

29. `wikipedia_pl` Postępowanie administracyjne

   Postępowanie administracyjne – administracyjne prawo formalne (procesowe), w doktrynie jest definiowane jako określony tryb działań organów administracji publicznej w sprawach dotyczących praw i obowiązków niepodporządkowanych im służbowo konkretnych podmiotów bądź też jako uporządkowany ciąg czynności procesowych, dokonywanych przez organ administracji publicznej i inne podmioty tego postępowania, zmierzających do załatwienia sprawy indywidualnej w drodze decyzji administracyjnej. Postępowanie administracyjne sensu stricto nazywa się także ogólnym postępowaniem administracyjnym oraz postępowaniem administracyjnym jurysdykcyjnym. W znaczeniu szerokim zalicza się do postępowania administracyjnego także postępowanie uproszczone w sprawach skarg i wniosków oraz w sprawach wydawania zaświadczeń, postępowania karno-administracyjne, postępowania dyscyplinarne, postępowanie egzekucyjne w adm...

30. `wikisource_pl` Listy do królowej Marysieńki/List z Dnia 15 VII 1665

   W obozie pod Kockiem, [15] VII [1665]. Najśliczniejsza serca i duszy pociecho! Nie czwarty dzień, ale czwarty rok już i więcej, zda mi się, jakom się z moim rozjechał sercem. A jeszcze najcięższa, że żadnej po odjeździe moim od duszy mojej nie odebrałem wiadomości, lubo już kilka z Warszawy przyszło okazy j; a to się dlatego dzieje, żem ja wszystkie poprzedził poczty i żadnego tu dotąd, który by po mnie wyjechać miał, nie widziałem. Jak ciężko, jak tęskno z duszy kochającego Sylwandra bez swej Astrei! Snadno imaginować, co się z takim dzieje, kto bez duszy i bez serca, bo to wszystko w Warszawie zostało. Co się z nami sam dzieje, ichmość drudzy wypisują. Ja tylko to namieniam, że gdyby mię byli słuchali, tedyby to teraz sześcią kroć, jako obiecowali, sprawili byli tysięcy, czego potem kilką nie naprawią milionów. Wołałem ustawicznie, swarzyłem się — nie pomogło nic, bo się tylko ichmo...

31. `wikipedia_pl` Warszawa Zoo

   Warszawa Zoo – przystanek kolejowy położony na terenie warszawskiej Pragi-Północ przy rondzie Stefana Starzyńskiego, tworzący tzw. węzeł kolei obwodowej. Z przystanku można dojechać elektrycznymi pociągami podmiejskimi Kolei Mazowieckich i Szybkiej Kolei Miejskiej do m.in.: dworca Zachodniego, dworca Gdańskiego, Legionowa i Modlina. W roku 2022 dzienna wymiana pasażerska na przystanku wyniosła 700-999 osób. Opis Nazwa przystanku pochodzi od pobliskiego Ogrodu Zoologicznego znajdującego się przy ulicy Ratuszowej 1/3.. Za wiaduktem kolejowym znajdował się posterunek odgałęźny służący sterowaniu ruchem kolejowym - możliwość jazdy w stronę Legionowa lub w stronę Warszawy Wschodniej. W październiku 2016 roku, ze względu na zamknięcie jednego toru mostu przy Cytadeli i jego przedłużający się remont, tor nr 1 (od strony ronda Starzyńskiego) obsługiwał pociągi kończące i zaczynające tu bieg....

32. `wikipedia_pl` Mentalizm

   Mentalizm – kategoria sztuki iluzji reprezentowana przez iluzjonistów mentalistów, z wykorzystaniem sugestii i hipnozy oraz mnemoniki. Wiedza dotycząca wykorzystania iluzji kognitywnych, psychologii, pozwala osiągnąć pozornie niesamowite efekty sprowadzające się głównie do oszukania widza dzięki jego nieświadomości ograniczeń percepcji i błędów poznawczych.

33. `wikipedia_pl` Komora wstępna

   Komora wstępna – komora spalania w silnikach wysokoprężnych z wtryskiem pośrednim. Geneza Kluczowym czynnikiem w każdym silniku wysokoprężnym jest dobre rozpylenie paliwa i jego dokładne wymieszanie się z powietrzem. W początkowym okresie rozwoju silnika wysokoprężnego wtrysk paliwa odbywał się przy użyciu sprężonego powietrza, przez co paliwo było dobrze rozpylone i co bardzo ułatwiało sam zapłon i spalanie. Próba przejścia na wtrysk paliwa bezpośrednio do cylindra spowodowała jednak gorsze rozpylenie paliwa, a przez to niską szybkobieżność silnika, leniwą reakcję na „dodanie gazu”, „twardą” pracę silnika i silne drgania. Wykluczało to zastosowanie takiego silnika jako źródła napędu samochodu. Aby usunąć te wady inż. Prosper L’Orange zatrudniony w firmie Benz & Cie zaprojektował w 1908 r. komorę wstępną. Komora wstępna połączona była z komorą główną (nad tłokiem) wąskim przewężeniem,...

34. `wikisource_pl` Ustawa o odpowiedzialności dyscyplinarnej sędziów, którzy w latach 1944-1989 sprzeniewierzyli się niezawisłości sędziowskiej

   Art. 1. Wobec sędziego, który w latach 1944-1989, orzekając w procesach będących formą represji za działalność niepodległościową, polityczną, obronę praw człowieka lub korzystanie z podstawowych praw człowieka, sprzeniewierzył się niezawisłości sędziowskiej, nie stosuje się, do dnia 31 grudnia 2002 r., przepisów o przedawnieniu w postępowaniu dyscyplinarnym dotyczącym sędziów. Postępowanie dyscyplinarne w sprawach, o których mowa w ust. 1, wszczęte przed dniem 31 grudnia 2002 r., toczy się do czasu jego prawomocnego zakończenia. Przepisy ust. 1 i 2 stosuje się odpowiednio do sędziego, który, wykonując kierownicze funkcje w administracji sądowej lub organizacjach politycznych, naruszył niezawisłość sędziowską poprzez wywieranie wpływu na wydawanie przez innych sędziów orzeczeń w indywidualnych sprawach, o których mowa w ust. 1. Art. 2. Z żądaniem wszczęcia postępowania dyscyplinarnego,...

35. `wikipedia_pl` Krakatit

   Krakatit – pochodząca z 1922 (wydana w 1924) roku powieść Karela Čapka, nosząca cechy utworu science fiction, kryminalnego, przygodowego i sensacyjnego dreszczowca. Fabuła Bohaterem książki jest Prokop – inżynier chemik, specjalista od materiałów wybuchowych. Wędruje on ulicami miasta i spotyka swojego kolegę z uniwersytetu, Jurka Tomesza. Opowiada mu o swoim nowym wynalazku – materiale wybuchowym o wielkiej sile, który nazwał Krakatitem (od nazwy wulkanu Krakatau). Tomesz odprowadza kolegę do swojego mieszkania i tam przez przypadek słyszy formułę chemiczną Krakatitu. Zaraz po tym opuszcza mieszkanie. Prokopa budzi nieznana mu dziewczyna, która powierza mu list do Tomesza. Chemik wyjeżdża do ojca Tomesza; tam też leczy swoje mocno nadwątlone zdrowie. Poznaje także Anusię, córkę doktora Tomesza, i zakochuje się w niej. Pewnego dnia znajduje w gazecie adresowane do siebie ogłoszenie. N...

36. `wikipedia_pl` SAGEM myX5-2v

   SAGEM myX5-2v – ulepszona wersja SAGEM myX5-2 przede wszystkim o kamerę cyfrową. Dane techniczne Bateria Typ: Li-Ion Maksymalny czas rozmów: 4h 45 min Maksymalny czas czuwania: 370h Pojemność 920 mAh W praktyce (w tym 30 min rozmów): przy dużej sile sygnału ok. 7 dni, przy minimalnej sile sygnału ok. 2 dni Dodatkowe WAP 2.0 Java: JTWI 1.0, MIDP 2.0, CLDC 1.0 (brak możliwości wgrania apletu przez kabel czy IrDA) Gry Java (2 wbudowane) Łącza: USB - niestandardowe gniazdo, IrDA GPRS Class 10 (4+1 & 3+2) CSD Wiadomości: SMS (T9)/EMS/MMS, pamięć 100 SMS w aparacie Obsługa typów plików BMP, JPEG, PNG, GIF, animacje gif, 3GP MP3 albo AAc, iMelody, Midi, spMidi, WAV, AMR, Inne: blokada klawiatury, budzik, zegar, timer, kalkulator, kalendarz, przelicznik walut, notatki głosowe, lista spraw, alarm wibracyjny, zestaw głośnomówiący, prosty edytor obrazów (tylko dla fotografii zrobionych telefonem...

37. `wikipedia_pl` Sprzątanie Świata

   Sprzątanie świata () – międzynarodowy ruch i kampania wywodząca się z akcji Sprzątanie Australii, założona przez Kim McKay oraz żeglarza Iana Kiernana, odbywająca się na całym świecie w trzeci weekend września. Globalne akcje obejmują zbieranie śmieci, kampanie edukacyjne, koncerty na rzecz środowiska, twórcze współzawodnictwo oraz wystawy dotyczące zdrowej wody, sadzenie drzew, minimalizacje odpadów, redukcję gazów cieplarnianych oraz organizacje ośrodków recyklingu. Sprzątanie Świata, wspólnie z Programem Ochrony Środowiska ONZ (United Nations Environment Programme, UNEP), przyciąga co roku ponad 35 milionów ochotników, którzy wspierają inicjatywę lokalnych władz rozmaitego szczebla mającą na celu sprzątanie, porządkowanie i ochronę środowiska. Uczestnikami są całe kraje, mniejsze społeczności i grupy środowiskowe, szkoły, departamenty rządowe, firmy, organizacje konsumenckie oraz p...

38. `wikisource_pl` Biblia Gdańska/Księga Ezechiela 19

   Ez 19 1 A ty uczyń narzekanie nad książętami Izraelskimi, 2 A mów: Cóż była matka twoja? Lwica między lwami leżąca, która w pośrodku lwiąt wychowywała szczenięta swoje. 3 A gdy odchowała jedno z szczeniąt swoich, stało się lwem, tak, że nauczywszy się chwytać łupu pożerał i ludzi. 4 To gdy usłyszały o nim narody, w jamie ich pojmany jest, a zawiedziony w łańcuchach do ziemi Egipskiej. 5 Co widząc lwica, że nadzieja jej, którą miała, zginęła, wziąwszy jedno z szczeniąt swoich, lwem je uczyniła; 6 Który chodząc w pośrodku lwów stał się lwem, a nauczywszy się chwytać łupu pożerał i ludzi. 7 Poburzył też pałace ich, i miasta ich spustoszył, tak, iż i ziemia i pełność jej od głosu ryku jego spustoszała. 8 I zeszły się przeciwko niemu narody z okolicznych krain, i zarzucili nań sieci swoje; a tak w jamie ich pojmany jest. 9 I wsadzili go do klatki w łańcuchach, i przywiedli go do króla Babi...

39. `wikipedia_pl` Cukrownia „Józefów”

   Fabryka Cukru i Rafineria „Józefów” – w Józefowie, zbudowana w 1866 przez braci Przeworskich. Od 1874 roku własność Towarzystwa Akcyjnego Cukrowni i Rafinerii „Józefów”, przy czym kierownictwo spółki sprawowała rodzina Przeworskich. Twórcami Towarzystwa byli Leon Goldstand, Jakub Janasz, Ignacy Leipziger, Justynian i Jan Karnicki, w pracach uczestniczyli również: Jan i Leopold Górscy, Ludwik Ołlendorf i książę Maciej Radziwiłł. W pierwszych zarządach firmy zasiadał Aleksander Goldstand, Wacław Popiel i Władysław Krzywoszewski. Dysponowano kapitałem zakładowym 850 000 rubli, tj. 3400 akcji po 250 rubli. Była pierwszą cukrownią dyfuzyjną na ziemiach polskich i jedną z pierwszych w świecie. Została rozbudowana w latach 70., od 1881 posiadała oświetlenie elektryczne (jedno z pierwszych w europejskich zakładach przemysłowych), do końca XIX wieku należała do największych i najnowocześniejsz...

40. `wikisource_pl` Mormolyce phyllodes

   Każdy dziś, cokolwiek oswojony z entomologią i zbieraniem owadów, zna przynajmniej z wizerunku osobliwszą szczypawkę, którą niezbyt dawno Kuhl i van Hasfelt w pierworodnych lasach wyspy Jawy odkryli, a Hagenbach pierwszy opisał pod nazwiskiem Mormolyce phyllodes, przyczyniając przez to nowy rodzaj licznej familii chrząszczów zwanej szczypawkowatemi (Carabici). Okazy tej szczypawki, jakby w liść oprawionej i przez to tak różniącej się od wszystkich pokrewnych gatunków, zrazu uważane za wielką rzadkość, teraz się bardziej upowszechniły po zbiorach; lubo ona zawsze dla entomologów tyle przedstawia zajęcia, że wiadomość o jej przemianach rzeczą ciekawą jest dla nich. C. van Ovendyk, gorliwy naturalista mieszkający na Jawie, znalazł jej gąsienice i poczwarki, żyjące w gatunku bdły Polyporus fomentarius, na pniach i korzeniach drzew leśnych rosnącej, i przesłał je panu Ver Huel, który opisa...

41. `wikipedia_pl` Spór o inwestyturę

   Spór o inwestyturę – spór między cesarstwem a papiestwem o mianowanie biskupów. Spór ten w istocie dotyczył przywództwa w ówczesnym świecie chrześcijańskim, ponieważ obozy papieski (gregoriański) i cesarski chciały realizować sprzeczne wizje uniwersalistycznej Europy. Geneza Reformy kongregacji Cluny oraz wzmożona chrystianizacja przyczyniły się do powstania wśród dostojników kościelnych idei uniwersalizmu papieskiego, czyli zwierzchności papieża nad władzą cesarską. Decydujące mogło mieć przekonanie, że społeczność chrześcijan musi „funkcjonować”, by w ten sposób zwiększyć swą skuteczność. Na podstawie tego przekonania pojawił się pogląd, że społeczeństwo dzieli się na różne stany, które wypełniają swoje zadania – chłopi troszczyli się o wyżywienie, rycerze bronili królestwa i zapewniali bezpieczeństwo, a kler zajmował się zbawieniem dusz ludzkich. Każda była zobowiązana do jak najle...

42. `wikipedia_pl` Jack Warden

   Jack Warden, właśc. John H. Lebzelter (ur. 18 września 1920 w Newark, zm. 19 lipca 2006 w Nowym Jorku) – amerykański aktor filmowy, teatralny i telewizyjny. Był dwukrotnie nominowany do Oscara za drugoplanowe role w filmach: Szampon (1975; reż. Hal Ashby) oraz Niebiosa mogą zaczekać (1978; reż. Warren Beatty i Buck Henry). W młodości był zawodowym bokserem, w czasie II wojny światowej służył w armii, najpierw jako marynarz, a potem jako spadochroniarz. Karierę aktorską rozpoczął w teatrach nowojorskich, debiutował na Broadwayu w 1952. Na dużym ekranie pojawił się po raz pierwszy w epizodycznej roli w filmie Asfaltowa dżungla z 1950. Pierwszą ważną rolę zagrał 7 lat później w legendarnym filmie Sidneya Lumeta Dwunastu gniewnych ludzi. W sumie zagrał w około 80 filmach; pojawił się także w dziesiątkach seriali telewizyjnych. Od 1958 był żonaty z aktorką Vandą Dupree. Od lat 70. pozostaw...

43. `wikipedia_pl` Aglomeracja bielska

   Aglomeracja bielska – aglomeracja monocentryczna w południowej Polsce, której głównym ośrodkiem jest miasto Bielsko-Biała. Według koncepcji Roberta Krzysztofika aglomerację bielską tworzy Bielsko-Biała oraz cały otaczający je powiat bielski, przy czym gmina miejsko-wiejska Czechowice-Dziedzice należy do strefy wewnętrznej aglomeracji, a pozostałe gminy powiatu (Bestwina, Buczkowice, Jasienica, Jaworze, Kozy, Porąbka, Szczyrk, Wilamowice, Wilkowice) do strefy zewnętrznej. W takim ujęciu jest to obszar o powierzchni 583 km² zamieszkiwany przez około 335 tysięcy osób. Zgodnie z alternatywną delimitacją przeprowadzoną w 2012 przez Regionalne Centrum Analiz Strategicznych przy Urzędzie Marszałkowskim Województwa Śląskiego aglomerację tworzy Bielsko-Biała oraz gmina miejsko-wiejska Czechowice-Dziedzice (łącznie 214 tysięcy mieszkańców), a do jej obszaru funkcjonalnego należą również gminy B...

44. `wikipedia_pl` Dariusz Fijałkowski

   Dariusz Fijałkowski (ur. 8 lutego 1979 w Krakowie) – polski żużlowiec. Życiorys Wychowanek Wandy Kraków. Licencje uzyskał w 1995 roku. Jest ostatnim wychowankiem Wandy Kraków. Pierwszy i jedyny wystąpił w zawodach rangi Mistrzostw Polski w 2000 roku w Rybniku: w finale MDMP wraz z kolegami z Włókniarza Częstochowa wywalczył złoty medal, a sam zdobył w tych zawodach 10 punktów. W 2002 roku wystąpił w Bydgoszczy w finale Złotego Kasku, jednakże z 3 punktami zajął odległe, 15. miejsce. W sezonie 2004 podpisał kontrakt w Ekstralidze z drużyną Polonii Bydgoszcz. Startując w barwach Polonii zajął szóste miejsce w Kryterium Asów. W sezonie 2005 popularny „Zibi” zasilił GTŻ Grudziądz. Sezon ten okazał się pechowy, gdyż podczas meczu z KM Intar Dartom Ostrów Fijałkowski już w 2 biegu uczestniczył w karambolu. W jego wyniku złamał bark, łopatkę i dwa żebra. Kontuzja ta wykluczyła go z jazdy pra...

45. `wikipedia_pl` Chronicon Lethrense

   Chronicon Lethrense (pl. Kronika z Lejre; duń. Lejrekrøniken) – niewielka duńska kronika z XII wieku, napisana po łacinie. Kronika w całości została zawarta w Annales Lundenses (annałach biskupstwa w Lund), pierwotnie jest jednak dziełem osobnym; na temat jej pochodzenia i wieku panują sprzeczne poglądy. W przeciwieństwie do Kroniki z Roskilde, która zawiera historyczne informacje o chrześcijańskiej już Danii, Kronika z Lejre jest zapisem przedchrześcijańskiego folkloru (opowieści o psie-królu Danii i o królu zjedzonym przez wszy) i zawiera historie legendarnych władców Danii, takich jak Roar, Rolf Krake czy Ursula. Pod tym względem jest to praca porównywalna z pierwszą częścią kroniki Svena Aggesena Brevis Historia Regum Dacie oraz z Gesta Danorum Saxo Gramatyka, jest to jednak dzieło znacznie krótsze. Chronicon Lethrense powstała prawdopodobnie w drugiej połowie XII wieku, być może...

46. `wikipedia_pl` Abebe Bikila

   Abebe Bikila (ur. 7 sierpnia 1932 we wsi Jato, zm. 25 października 1973 w Addis Abebie) – etiopski lekkoatleta, biegacz długodystansowy, dwukrotny złoty medalista olimpijski w biegu maratońskim. Stał się ikoną afrykańskiego sportu w okresie rozpadu kolonializmu. Pomimo braku doświadczenia międzynarodowego zdobył złoty medal w maratonie na igrzyskach olimpijskich w 1960 w Rzymie, przed faworytem Rhadim Ben Abdesselamem z Maroka i Barrym Magee z Nowej Zelandii. Biegł na tych igrzyskach boso. Na sześć tygodni przed igrzyskami olimpijskimi w 1964 w Tokio poddał się operacji wycięcia wyrostka robaczkowego. Mimo to ponownie zdobył złoty medal (jako pierwszy w historii, później dokonali tego także Waldemar Cierpinski i Eliud Kipchoge), wyprzedzając Basila Heatleya z Wielkiej Brytanii i Kōkichiego Tsuburayę z Japonii. W obu przypadkach Bikila ustanawiał najlepsze wyniki na świecie w biegu mar...

47. `wikipedia_pl` Hrabstwo St. Lawrence

   St. Lawrence – hrabstwo (ang. county) w stanie Nowy Jork w USA. Geografia Powierzchnia hrabstwa wynosi 2821,44 mi² (około 7307,5 km²). Według stanu na 2010 rok jego populacja wynosi 111 944 osoby, a liczba gospodarstw domowych: 52 133. W 2000 roku zamieszkiwało je 111 919 osób, a w 1990 mieszkańców było 111 974. Miasta Wsie CDP Brasher Falls–Winthrop Colton Cranberry Lake DeKalb Junction Edwards Hailesboro Hannawa Falls Madrid Norfolk Parishville Star Lake

48. `wikipedia_pl` Bílina (rzeka)

   Bílina (niem. Biela) – rzeka w północnej części Czech, w kraju usteckim. Lewy dopływ Łaby o długości ok. 82 km. Źródło rzeki w Rudawach na północ od Chomutova, powyżej Jirkova. Ujście w Ústí nad Labem. Powierzchnia dorzecza 1082,5 km². Jeden większy, prawy dopływ Srpina. Większe miejscowości nad Bíliną: Jirkov Most Bílina (miasto) Trmice Uście nad Łabą

49. `wikipedia_pl` Patrick Duffy

   Patrick George Duffy (ur. 17 marca 1949 w Townsend) – amerykański aktor, reżyser i producent telewizyjny i filmowy. Zagrał rolę Bobby’ego Jamesa Ewinga w operze mydlanej CBS Dallas (1978-1991), za którą w 1985 dostał nagrodę Soap Opera Digest dla najlepszego aktora w serialu czasu największej oglądalności, a w 1987 otrzymał niemiecką nagrodę Bambi. W 1981 i 1981 został uhonorowany statuetką Bravo Otto dla najlepszej gwiazdy telewizyjnej, przyznaną przez niemiecki dwutygodnik dla młodzieży „Bravo”. Życiorys Wczesne lata Przyszedł na świat w Townsend w stanie Montana jako drugie dziecko właścicieli tawerny - Terrence’a i Marie Duffy. Otrzymał imię Patrick, ponieważ urodził się w Dzień Świętego Patryka. Po ukończeniu dwunastego roku życia dorastał w Seattle. Jako nastolatek został certyfikowanym płetwonurkiem. W liceum był cheerleaderem. Miał zostać zawodowym sportowcem, lecz po ukończen...

50. `wikisource_pl` Biblia Gdańska/Księga Izajasza 47

   Iz 47 1 Zstąp, a usiądź w prochu, panno, córko Babilońska! siądź na ziemi, a nie na stolicy, córko Chaldejska! bo cię nie będą więcej nazywać kochanką i rozkosznicą. 2 Weźmij żarna, a miel mąkę; odkryj warkocze swoje, obnaż nogi, odkryj golenie, brnij przez rzekę. 3 Odkryta będzie nagość twoja, a hańba twoja widziana będzie; wezmę pomstę z ciebie, a nie dam się nikomu zahamować. 4 To mówi odkupiciel nasz, imię jego Pan zastępów, Święty Izraelski. 5 Siedź milcząc, a wnijdź do ciemności, córko Chaldejska! bo cię więcej nie będą nazywać panią królestw. 6 Rozgniewałem się był na lud mój, splugawiłem dziedzictwo moje, a dałem je w ręce twoje; aleś im ty nie okazała miłosierdzia, i starców obciążałaś jarzmem twojem bardzo, 7 I rzekłaś: Na wieki panią będę; i tak nie przypuściłaś tego do serca swego, aniś sobie przywodziła na pamięć dokończenia tego. 8 Przetoż słuchaj tego teraz, rozkosznico...
