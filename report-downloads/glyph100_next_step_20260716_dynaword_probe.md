# Glyph-100M Polish Dynaword Controlled Source Probe

The probe used streaming reads, bounded samples and the real Glyph tokenizer. No complete dataset was downloaded and no training was started.

## Decision

Polish Dynaword is the strongest currently accessible replacement for gated FinetextPL-Edu because it is public, source-aware and license-documented. It must still be remixed and filtered per source; its raw legal/parliamentary proportions are unsuitable for a general Polish base model.

## Source Results

| Source | Upstream docs | Upstream tokens | Probe accepted | Probe tokens | Residue | Decision |
|---|---:|---:|---:|---:|---:|---|
| wolne_lektury | 6,141 | 103,009,797 | 157/200 (78.5%) | 863,005 | 4 | use as a capped source in the v2.4 pilot mix |
| 1000_novels | 1,000 | 60,517,363 | 165/200 (82.5%) | 2,260,922 | 5 | use as a capped source in the v2.4 pilot mix |
| eltec_pol | 100 | 21,486,720 | 100/100 (100.0%) | 2,274,996 | 3 | use as a capped source in the v2.4 pilot mix |
| wikibooks | 9,112 | 15,571,295 | 66/200 (33.0%) | 42,882 | 1 | later: inspect and add source-specific cleanup before inclusion |
| wikinews | 24,386 | 12,141,355 | 85/200 (42.5%) | 28,397 | 1 | use as a capped source in the v2.4 pilot mix |
| wikisource | 632,005 | 801,947,427 | 171/200 (85.5%) | 55,897 | 0 | use after parent-work grouping and technical-page cleanup |
| parliamentary | 324,622 | 1,646,835,986 | 113/200 (56.5%) | 140,581 | 5 | use with a 10% token cap to avoid parliamentary style dominance |

## Recommended 300M-token Pilot Mix

- 30% clean Wikipedia PL (90M)
- 25% literature: Wolne Lektury, 1000 Novels and ELTeC (75M)
- 15% cleaned Wikisource grouped by parent work (45M)
- 10% parliamentary text, capped (30M)
- 10% Wikibooks + Wikinews (30M)
- 5% official/legal explanatory prose, capped (15M)
- up to 5% register-gated HPLT only after a manual precision gate (15M)

This mix deliberately does not depend on FinetextPL-Edu and does not make open web the dominant source.

## Detailed Samples

### wolne_lektury

Accepted:

- `wolne_lektury_2372009`: Świat z nas drwi. KARMAZYN Myśleć o lepszej trudno doli. HOŁYSZ Trzeba by za krew łaknąć krwi. KARMAZYN Na synów patrzeć serce boli. HOŁYSZ Na wnuki patrzeć: hańba, tfy! KARMAZYN Cóż acan myśli? HOŁYSZ Że w niewoli Nawykły jarzmo dźwigać łby. KARMAZYN Kiedyż ten przyjdzie, kto wyzwoli? HOŁYSZ Nie przyjdzie, to są złudne sny. To w przewidzenie wiara, w gusła. KARMAZYN Więc cóż zostało? HOŁYSZ Kajdan stos, trucizna, brzytwa i powrósła, jeśli wam obrzydł, bracie, los. KARMAZYN Aleć strój na mnie do

- `wolne_lektury_2371673`: Stanisław Jachowicz Bajki i powiastki Waluś Długo Waluś pieniędzy ocenić nie umiał, Co mu dano, to przeszumiał, A chociaż nieraz pieniądz dostał mu się wielki, Poszedł zaraz na ciastka, pierniki, karmelki. Raz z ojcem na przechadzkę wychodzi wieczorem; Zgięty z ciężkim na plecach idzie starzec worem. „Kupcie piasku!” głośno krzyczy. Nikt sobie nabyć nie życzy. Pot starcowi płynie z czoła, Coraz głośniej z płaczem woła: „Tanio sprzedam to się przyda. Ach widzicie jaka bieda! Ledwie dźwigam, sił n

- `wolne_lektury_2371597`: Jan Kochanowski Treny Tren XIV. (Gdzie te wrota nieszczęsne, któremi przed laty…) Gdzie te wrota nieszczesne, któremi przed laty Puszczał sie w ziemię Orfeus, szukając swej straty, Żebych ja też tąż ścieżką swej namilszej córy Poszedł szukać i on bród mógł przebyć, przez który Srogi jakiś przewoźnik wozi blade cienie I w lasy niewesołe cyprysowe żenie. A ty mię nie zostawaj, wdzięczna lutni moja, Ale ze mną pospołu pódź aż do pokoja Surowego Plutona: owa go [to] łzami, To temi żałosnemi zmiękczy

- `wolne_lektury_2371766`: Adam Wiedemann Samczyk *** [wszyscy mówią] wszyscy mówią że im się nie chce mnie też się teraz nie chce mówię sobie mówię Jarkowi chodzę siadam gdzieś daleko leje jest lato wolę to skrzypce bzyczą leżymy na pryczy brzydzisz się mną we śnie teraz już nie pamiętasz deszcz kapie więc to nie trzmiele tam brzęczą prąd się przeciska drutami wirują szprychy świata przyjechały do domu w domu ciemno na parapecie zdechłe osy szeleszczą już mogę iść spać może jeszcze jeden wers albo nawet dwa :ten co umarł

- `wolne_lektury_2371817`: Charles Cros W knajpie tłum. Stefan Napierski Marzeniem: nie zawsze jadać, Ale żartować, pić, gadać, Gdy noc zapada; Na dnie szklanki śledzić rysy, Śmiać się z was, dumne cyprysy, Mogiło blada! Nie przeczyć racji nikomu I w niczym, kiedy tam w domu Znów zupa stygnie; Zapomnieć, o, wielkie słowa, Że kędyś tacza się głowa Dzieci w malignie. Mija się, gubiąc wśród drogi, Przyjacioły, mija wrogi, Czułości płoną! Lepiej zagrać sobie w kości, Słowa to chwyty miłości, Z której się kona. Ich — nigdy nic

- `wolne_lektury_2371623`: Juliusz Słowacki Trzy poemata Ojciec zadżumionych W El-Arish Dla objaśnienia następnego poematu potrzeba mi nieodbicie powiedzieć kilka słów o kwarantannie na pustyni między Egiptem a Palestyną, blisko miasteczka El-Arish. Wymysłem to jest dziwnym Mohameda Ali, że między dwoma swoimi państwami naznaczył myślą na błędnym piasku granicę i pod karą miecza zmusił wolne Beduiny rozbijać w tym miejscu namioty i żyć przez dni kilkanaście pod dozorem straży i doktora; inaczej zaś z Egiptu do Syrii dosta

- `wolne_lektury_2371769`: Juliusz Słowacki Wielcyśmy byli i śmieszniśmy byli… Wielcyśmy byli i śmieszniśmy byli, Bośmy się duchem bożym tak popili, Że nam pogórza, ojczyste grobowce Przy dźwięku fletni skakały jak owce, A górom onym skaczącym na głowie Stali olbrzymy — miecza aniołowie. Ustały dla nas bić godzin zegary, Duch nie miał czasu, a czas nie miał miary; Szedł błyskawicą do wieczności progu Duch — a stał wieczność — kiedy stanął w Bogu. Zaprawdę powiem, bracia moi mili, Żeśmy się duchem przeświętym popili. Teraz

- `wolne_lektury_2371905`: Agnieszka Wolny-Hamkało Nikon i Leica Historia prawdziwa Od psa pochodzę a pióra dał bażant. Chłopcy lubią z mąki moją duszę płytką jak wydma. W środku mam pełno pajęczyn. Lalki bez ust są znów chudsze, daję im zupę z ziemi i mrówki z cukrem. Moja małpka Rita wyniosła się z jajka skulona jak żółtko, jak smocza wróżka. Teraz panowie wyciągają ze mnie pieśni przez usta. Patrzę wtedy na rzekę, płynie w niej zsiadłe srebro i księżyc nadstawia złamany obojczyk pod nurt. Ziemia znów dymi jak azot. Ran

- `wolne_lektury_2371999`: Stanisław Wyspiański Niech nikt nad grobem mi nie płacze 1. Niech nikt nad grobem mi nie płacze, krom jednej mojej żony, za nic mi wasze łzy sobacze i żal ten wasz zmyślony. 2. Niech dzwon nad trumną mi nie kracze, ni śpiewy wrzeszczą czyje; niech deszcz na pogrzeb mój zapłacze i wicher niech zawyje. 3. Niech kto chce grudę ziemi ciśnie, aż kopiec mnie przywali. Nad kurhan słońce niechaj błyśnie i zeschłą glinę pali. 4. A kiedyś może, kiedyś jeszcze gdy mi się sprzykrzy leżeć, rozburzę dom ten, 

- `wolne_lektury_2371979`: To paradoksalne spotkanie zasług instytucji i dzieł sztuki w pejzażu miejskim Krakowa nie zostało przez Wyspiańskiego bezpośrednio przewidziane i zaprojektowane. Bardzo jest jednak w jego duchu. I chyba cieszy ambiwalentne i wobec rodzinnego miasta częstokroć ironiczne serce jego, największego poety i wizjonera. 1969 „Mam ten dar bowiem: patrzę się inaczej” I W nowym roku 1970 pożegnajmy się z Wyspiańskim — krakowianinem jako dramaturgiem i pisarzem. Ów wzajemny stygmat, podwójny narzut: miasta 

Rejected:

- `wolne_lektury_2371903` (too_short): Agnieszka Wolny-Hamkało Nikon i Leica fleszmob Zaśpijmy dzisiaj — będzie fajnie. Zaśpijmy specjalnie. Udajmy gorączkę, udajmy malarię. Olejmy awizo, zignorujmy dzwonki, grajmy zaginionych, tylko troszkę martwych. Zaśpijmy zupełnie dzień dniem bez nas zróbmy. Bez nas się obejdą te ważne spotkania, te straszne wypadki. Zaśpijmy dzisiaj, nie mówmy już nic.

- `wolne_lektury_2371761` (too_short): Adam Wiedemann Samczyk Venus pobudzona przez Tycjana dla Jarka Górnickiego i Pawła Borowca i gdzie ta toaletka, przy której siadywałam (mów dalej, opowiadaj) pamiętasz? mnie tam wtedy nie było, rzucali kamieniami (skąd brali tyle kamieni?) piliśmy tylko wino ja w samym środku ziemi, ja w płaszczu Kosmosu kropla potu na skórze, obecność nie do zastąpienia, nie do starcia ja rozumiem, ja byłem, dwa 

- `wolne_lektury_2371936` (repeated_ngrams): Maryla Wolska Święto Słońca Poszli wszyscy mokrymi łąkami ku zorzy, Poszli wszyscy w szalach odświętnych przez łan… I ponieśli do chramu daleko, Kadzielny bursztyn i miód, Jagody kraśne i mleko I w cienkie owite płótno Chleby ofiarne, z białej, pszennej mąki… Słyszałam skrzypienie wrót I pieśń ich smutną Od łąki… Słyszałam, jak płonki trzęśli Z domowych drzew, I jęk słyszałam gęśli Branych ze ścia

- `wolne_lektury_2371944` (too_short): Ignacy Krasicki Bajki i przypowieści Woły krnąbrne Miłe złego początki, lecz koniec żałosny, Nie chciały w jarzmie chodzić woły podczas wiosny; W jesieni nie woziły zboża do stodoły; W zimie chleba nie stało, zjadł gospodarz woły.

- `wolne_lektury_2371910` (too_short): Agnieszka Wolny-Hamkało Nikon i Leica lost W studniach łkają jemiołuszki. Mole snują swój niespójny plan. W bramie na Czerskiej płonie bmw. Zakonnice niosą suknie pod wiatr. Miasto rezonuje miękko jak błonka. Ma smak starej herbaty ze smarem.

### 1000_novels

Accepted:

- `1000_novels_0426`: Przyczołgawszy się aż do wrót, padł wyczerpany. Tymczasem nadole wrzała jeszcze walka. Jakże chciałby dowlec się do venty, aby umrzeć w obliczu ukochanej. Nie; oszczędzi jej odrażającego widoku śmierci! Nie ruszał się z miejsca. Siły zaczęły go opuszczać. Krew płynęła obficie; nie tamował jej. Zamknął oczy; był pewien, że śmierć, która go uwolni od wątpliwości i wyrzutów sumienia, jest blisko. Nagle rozległ się z pola bitwy okrzyk triumfu. Otworzył oczy. Juarez wraz ze sztabem był jeszcze ciągle

- `1000_novels_0090`: co daje szkoła, jest powolnym i systematycznym tych uczuć niszczeniem. Nie będę mówił o pierwszym, dziecinnym zetknięciu się bodaj z dziesięciorgiem przykazań i o naiwnych pytaniach małych bębnów, co znaczy „nie cudzołóż” i „pożądać żony bliźniego swego”. Prawdziwy konflikt zaczyna się w gimnazjum. Mówię wedle tego, na co patrzałem. Do każdej lekcji odnoszą się uczniowie rozmaicie, zależnie od przedmiotu i osobistych zamiłowań; ale do jednej lekcji odnoszenie jest jednomyślne, to znaczy z jednom

- `1000_novels_0014`: Hans Christian Andersen Historia roku tłum. Cecylia Niewiadomska Był styczeń. Od rana srożyła się straszna zadymka, śnieg pędził przez ulice całymi chmurami, sypał z dachów, uderzał w szyby, bił przechodniów po twarzy, to znowu wirował w powietrzu, wichrem kręcony. Ludzie biegli skuleni, śpiesząc niesłychanie, mrużąc oczy, wpadając na siebie co chwila i ostrożnie rozchodząc się w strony przeciwne, aby nie upaść od zdradzieckich, silnych porywów wiatru. Powozy i konie wyglądały jak cukrem posypan

- `1000_novels_0320`: Matka, wracając z połowu, udawała się wprost na to miejsce zabaw i dobywała głosu podobnego do beku owcy wołającej koźlęcia, a Kotik odpowiadał na to wezwanie. Wówczas podążała ku niemu wprost odmiatając po drodze płetwami malców na prawo i lewo. Ciągle szukało tam swych dzieci kilkaset matek naraz, a przeto malce musieli pilnie baczyć, by rozpoznać swe rodzicielki. — Jesteś tu całkiem bezpieczny — mówiła Kotikowi matka — pamiętaj tylko nie włazić do błota, by nie oskrostowacieć, nie ocierać zad

- `1000_novels_0183`: Stał przy stole laboratoryjnym, patrząc z zażenowaniem na jej lekko pochyloną postać w białym lekarskim kitlu, na jasne włosy, na mocniej niż zwykle zarumieniony policzek, na bardzo białe ręce, za szerokie może i za muskularne, manipulujące przy mikroskopie. — Bardzo pana przepraszam — powtórzyła. — O, nie ma za co — odezwał się niezręcznie. — Jest za co, bo posądziłam pana o robienie głupstw — odpowiedziała rzeczowo. — To wcale nie było głupstwo — zaoponował. — Właściwie to ja panią muszę przep

- `1000_novels_0234`: KRUK Z PAMIĘTNIKA KAZIMIERZA BRZOSTA Złociste było popołudnie. Rdzawe, jesienną półmgłą przygaszone słońce zasuwało szybę blasków w gęstwę drzew bez ruchu. Stały w glorji wierzchołki cyprysów, piły tęsknotę zachodu cmentarne lipy. Nerwowe liście osiki, białopiennych brzóz, tknięte czerwoną powodzią, drżały tajemnym szmerem, w łaskę przebogate. I cichy był cmentarz, wieczornych przeczuć pełen. Osnute przędzą babiego lata krzyże prężyły linje ramion, śmierci drogowskazy. Marmurowe grobowce, smukłe

- `1000_novels_0040`: Stół był nakryty. Serce Krystyana pełne było radości kolendowej. Marya wydobyła z komody psalmy. — Wy umiecie śpiewać! — rzekła do ojca chrzestnego. — Zacznijcie! — Ja psalmów nie umiem! — odpowiedział. — Jeżeli się ta książka ma nam na co przydać, to lepiej roztwórzmy ją na traf szczęścia i zobaczmy, jakie nas czekają losy. Cóś bo jest w tem proroctwie! To co się stanie, zapisano jest w tej wielkiej księdze, tak samo jak zapisano w naszej krwi i duszy! Marya roztworzyła książkę. — Psalm weselny

- `1000_novels_0186`: M. DOMAŃSKA DZWONY NOWELA Zaszczytnie odznaczona na konkursie Kurjera Litewskiego. Grafika do Dzwony (Michalina Domańska) 007.jpg WARSZAWA Nakładem księgarni „PRZEGLĄDU KATOLICKIEGO,” Warecka 11 Łódź — ul. św. Andrzeja 3 1914 Czcionkami „Przeglądu Katolickiego,” Warszawa, Warecka 15 Chata Serafiny stała nawprost kościoła. Z okien widać było wysokie, zmurszałe ogrodzenie cmentarne i stojącą w rogu bardzo starą, pochyloną, ciekawej struktury dzwonnicę kościelną. Starszą była od kościoła, z modrzew

- `1000_novels_0322`: — Jak… mam to rozumieć? — zapytał Troop, podnosząc jedną z krzaczastych brwi, spod której wyjrzało niebieskie oko, łagodne a jednocześnie podejrzliwe. — W dolarach i centach — odrzekł Harvey, myśląc z radością, jakie wrażenie wywołają jego słowa. — Dolary i centy w bitej monecie!… To rzekłszy, włożył rękę do kieszeni i z lekka wydął brzuch, co u niego było formą okazywania swej wspaniałości, po czym mówił dalej: — Gdy dowieziecie mnie do domu, czeka was najlepszy zarobek, jaki się wam udało zdob

- `1000_novels_0178`: Gdy Monika zbliżyła się do łóżka, poznała: to była jej fotografia, ta sama fotografia w mundurku gimnazjalnym, którą wysłała mu kiedyś na front. — To ja — szepnęła i nic więcej powiedzieć nie mogła. Jakże dobrze zrozumiała tę swoją obecność w tym pustym mieszkaniu człowieka, który nic tu poza nią nie miał. Ogromny smutek ogarnął ją i rozczulenie i żal i jakaś bezsensowna wdzięczność, bezsensowna, bo przecież nie była egoistką, nie była próżna… Na stoliku, przy łóżku tykał głośno zwyczajny niklow

Rejected:

- `1000_novels_0396` (too_many_urls): Antoni Lange W czwartym wymiarze Memoriał doktora Czang-Fu-Li Paryż, w r. 2652 Wyprawa naukowa do szczególnej części świata, zwanej Europą, dokąd wysłany zostałem przez czcigodną Akademię Nauk w Pekinie — dała rezultaty tak nieoczekiwane, że gdyby się okazały prawdą fantastyczne teorie uczonego Lapończyka dra Teene Weene, byłby to po prostu przewrót zarówno w nauce geologii, jak i historii. To zaś

- `1000_novels_0083` (too_many_urls): Tadeusz Boy-Żeleński Piosenki „Zielonego Balonika” Kilka słów o piosence (Nietzsche, Geburt der Tragödie) Było to w Paryżu; któregoś wieczora wałęsałem się wzdłuż bulwarów, gdy nagle zbudził mnie z zamyślenia głos przeraźliwie donośny a zachrypły, który śpiewał, a raczej mówiąc ściślej, darł się co następuje: Moi j'aime La femme A la folie… Zdumiony tym niespodziewanym publicznym wyznaniem zwrócił

- `1000_novels_0318` (too_many_urls): Immanuel Kant O potędze ducha czyli jak panem być chorobliwych uczuć przez samo tylko postanowienie tłum. Adam Stögbauer Wstęp tłumacza *Kant*, jeden z największych filozofów świata, jest znany także poza gronem ludzi bliżej filozofią się zajmujących — z imienia. I zważywszy, jak trudne są jego dzieła, nie można się temu dziwić; raczej powinno się w tym upatrywać dowód, że twórca systemu, dostępne

- `1000_novels_0258` (too_many_urls): Stefan Grabiński Na wzgórzu róż W willi nad morzem Krągłe, miękko zwiewne obłoczki dymu wysnuwały się z wolna z kształtujących je ust, położyły w karbowanych falisto pierścieniach i roztapiały na lazurowym tle nieba. Cygara były wyborne; delikatnie zwinięte liście żarzyły się wonnie, ulatniając soczystą, szlachetnie ześrodkowaną treść. Paliliśmy powoli, zaciągając się z maestrią, jak znawcy. Znako

- `1000_novels_0225` (too_many_urls): Stefan Grabiński Szalony pątnik Dziedzina Od lat przeszło dwunastu Wrześmian przestał pisać zupełnie. Wydawszy w roku 1900 czwarty z rzędu tom swych oryginalnych, jak obłąkanie dziwnych utworów — zamilkł i bezpowrotnie usunął się z widowni świata. Od tego czasu nie ruszył piórem, nie odezwał się choćby błahym wierszem. Nie wydrożyły go z milczenia zachęty przyjaciół, nie podnieciły uwabne głosy kr

### eltec_pol

Accepted:

- `eltec_pol_2455247`: — Opowiadałem jej o tym — mówił stryj — w takim rozczulającym przypływie wspomnień, że się dała złapać na haczyk. Powiedziała mi: „»Flora«?… To zabawne. Niech pan sobie wyobrazi, że i ja kiedyś wynajmowałam tę willę. Jest ślicznie położona”. To już stryjowi w zupełności wystarczyło. Uradziliśmy natychmiast depeszować do Brukseli, by trzymano się tego śladu i postarano się dowiedzieć jak najwięcej o owym panu Folkstonie. Jednocześnie stryjowi przyszedł do głowy wcale niezły pomysł, by skomunikowa

- `eltec_pol_2455248`: Pracy w młynie, jak zwykle na przednówku, było mało. Zaczęły się wiosenne roboty w polu, ludzie na chorowanie i na leczenie się nie mieli czasu. Tedy i pacjenci nie najeżdżali już tak masowo. Toteż Antoni co drugi, co trzeci dzień chodził do miasteczka. Nie prosił już nikogo o załatwienie dlań zakupów, co oczywiście zwróciło uwagę rodziny Prokopa Mielnika. — Coś ciebie ciągnie do Radoliszek — z przekąsem mówiła Zonia. — Co ma ciągnąć — żartował Wasil. — On pewno tam do baby chodzi. — Idźże ty, m

- `eltec_pol_2455328`: Usiadł wyczerpany, twarz w dłoniach ukrywając. — Je l'aime, je l'aime! — dodał głucho i skończył, jak gdyby spazmem zrywającego się w piersi płaczu. Turski siedział w milczeniu, czując, że nic nie ma do odpowiedzenia. Gdy po chwili książę powstał, aby się pożegnać, nie było już znać na nim przebytego wzruszenia. Rysy zastygły mu na nowo; około wąskich, sinych ust wieszał się zdawkowy, wytworny uśmiech grzeczności. — Pan daruje, że pana trudziłem. — Niech książę raczy wierzyć, że jeżeli tylko cok

- `eltec_pol_2455241`: — Ale wszystkim trzęsą — przerwał chudy Frydrych. — Wszystkim trzęsą, a nam co po tym? Kto flotą rządzi? Panowie Szpiryngi. Kto cła wybiera? Panowie Szpiryngi. Kto wszelaki zatarg rozsądza? Panowie Szpiryngi. Dlaczego właśnie oni? — Dlatego, że król jegomość raz przecie znalazł sobie ludzi, co nie służą prywacie tej lub owej prowincji abo prywacie tego lub onego miasta, ale służą pospolitej rzeczy. I kłamie, kto powieda, że oni sami jedni rządzą. Wszak ci w onej Morskiej Komisji zasiadają rozmai

- `eltec_pol_2455322`: Otrzymawszy te wyjaśnienia Cezary, pouczony i pokrzepiony na duchu, już się o nic nie kramarzył. Mieszkał i już. Pokój mu się jednak nie podobał. Był mały — na jakie dziesięć lat przed wojną europejską pomalowany na kolor zupy pomidorowej — jakiś nieporęczny, a nadto przewiewny. Nie wiało jednak z okna i ze drzwi czyste powietrze, lecz zapach pewnych niezbędnych ubikacji, które mieściły się na dole wprawdzie, lecz właśnie pod oknem tego pokoju. Nadto stał tuż za murem blaszany komin piekarni, kt

- `eltec_pol_2455262`: Przyznam się, iż lubo baron po kilka razy dawał mi święte słowo kawalerskie, iż co bądź usłyszy ode mnie, w tajemnicy dochowa na wieki, i pomimo tego uczucia, które koniecznie kazało dawać wiarę słowom żołnierza i kawalera, jakaś nieufność, jakieś podejrzenie po kilka razy odzywało się we mnie. Nuż wyspowiada mnie i poleci z językiem do sądu, nuż zdradzi?... dopiero by człowiek przepadł bez ratunku. Ale tak ginąć czy owak, wszystko to jedno; niechże choć nieufnością nie grzeszę! I zasiadłszy z n

- `eltec_pol_2455243`: Zosia zmieszała się, siostra zawsze jej imponowała. — Bóg rozkazał nam fundować zakon, który by walczył za Kościół święty, za ginące w grzechu dusze ludzkie. Dzieło to jest wielkie, święte. Czymże wobec tego, powiedz, czymże jesteś ty, abyś miała, dla swej przyjemności czy wygody, głos przeciw nam podnosić? Powiedz sama, czy wobec takiego celu możemy myśleć o twoich zachciankach, o twoich — zresztą bardzo poczciwych — uczuciach? Powiedz, co ważniejszego? Bóg i Jego rozkaz czy też twoja przyjemno

- `eltec_pol_2455295`: Za to stary Stanisławski i inspicyent byli jej serdecznymi przyjaciółmi. Ileż to razy podczas prób szli razem na górę, do pustych garderób, albo pod scenę, zawaloną różnymi rupieciami i opowiadali jej dzieje swoich teatrów, dzieje ludzi i epoki już umarłej; rysowali przed nią jakieś wielkie postacie, wielkie dusze i wielkie namiętności, takie właśnie nieomal, o jakich marzyła. Czasami chodziła z niemi do Łazienek, namawiała ich sama do tych wycieczek, bo ją zaczynało dusić miasto i miała coraz d

- `eltec_pol_2455315`: - Od tej strasznej uschyzy" progu wara wam i wara Bogu mruczał Izydor trawestując Micińskiego, którego jako jedynego wielkiego poetę polskiego przed- i powojennego uwielbiał. W łeb tego drania, pykniczeńkę! Dochodził jui właśnie do swego domku na Dębnikach. Mały, parszywy murek z przeszłego dziewiętnastego wieku jakby dzieci ułożyły z niemieckich, dziecinnych klocków. Tam była Rustalka - jego żona, własna, ukochana, przynitowana do niego stalowymi nitami „na fest" , „na amen" , na wieczność - w 

- `eltec_pol_2455286`: — Nu! Ty ją zobaczysz! — uspokajająco odrzekła matka. — My do nich dziś z wizytą wszyscy pójdziemy! — A co to za dziewczyna? — zapytała znowu siostry. — Iii! — odparła jak pierwej pani Hana. — Prosta dziewczyna! — Ojciec jej, Rafał, daje za nią sześć tysięcy rubli! — wtrącił Eli. Leopold ściągnął brwi chmurnie. — A co mnie z tego? — rzekł. — Czy ja mogę z sześciu tysięcy utrzymać się? — Handel zaczniesz! — zauważył kupiec. Ale matka ładnego chłopca z gniewem nieledwie zwróciła się ku szwagrowi: 

Rejected:

### wikibooks

Accepted:

- `wikibooks_2415795`: Wystarczy kartka i długopis Od kółka krzyżyka można się uzależnić. Od szewca również. A może jesteście fanami kartofla? Okręty albo bitwa morska Na kartce zawodnicy rysują kwadrat 10 x 10 kratek. Na górze nad linią poziomą każdą kratkę oznaczają kolejną literą alfabetu od A do J. Z boku wzdłuż linii pionowej wpisują cyfry od 1 do 10. W tak ograniczonym kwadracie każdy rozmieszcza swoją flotę, na którą składa się dziesięć okrętów: cztery łodzie podwodne (każda zajmuje jedną kratkę), trzy ścigacze

- `wikibooks_2416151`: ¡Bienvenidos! – Witamy! Hiszpański jest jednym z najbardziej rozpowszechnionych języków świata. Co dzień mówi nim ponad 350 milionów ludzi, zaś kolejne 70 milionów używa go jako drugiego języka. Mówiąc o języku hiszpańskim, zwykle mamy na myśli język kastylijski (castellano), który jest najczęściej używanym w Hiszpanii i na całym świecie dialektem. Inne języki używane na terenie Hiszpanii to kataloński, galicyjski, czy też oksytański. W wielu krajach, zwłaszcza w Ameryce Południowej, do kastylij

- `wikibooks_2416108`: Co to jest FTP? FTP jest jak magiczna skrzynka pocztowa dla komputerów! Jeśli chcesz wysłać plik z jednego komputera do drugiego, możesz umieścić go w magicznej skrzynce pocztowej, a zostanie on wysłany do innego komputera. Aby skorzystać z magicznej skrzynki pocztowej, musisz powiedzieć swojemu komputerowi, gdzie ją znaleźć (tak jakbyś dał listonoszowi list z adresem). Gdy komputer znajdzie skrzynkę pocztową, umieszcza plik w środku i wysyła go do innego komputera. Następnie drugi komputer spra

- `wikibooks_2416058`: RefTeX to potężny pakiet do zarządzania odniesieniami bibliograficznymi w dokumentach LaTeX w GNU Emacs. Oto krótki przewodnik dotyczący korzystania z RefTeX: Zainstaluj RefTeX: RefTeX jest zwykle dołączany do większości dystrybucji Emacsa. Jeśli nie jest zainstalowany, możesz go zainstalować, dodając następujący wiersz do pliku .emacs: (require 'reftex) Włącz RefTeX: Aby włączyć RefTeX, dodaj następujące wiersze do pliku .emacs: (add-hook 'LaTeX-mode-hook 'turn-on-reftex) (setq reftex-plug-into

- `wikibooks_2415815`: Programowanie deklaratywne to paradygmat programowania, w którym program jest napisany jako zestaw deklaracji lub instrukcji opisujących pożądany wynik, a nie jako sekwencja kroków lub instrukcji do wykonania. W programowaniu deklaratywnym programista określa, co program powinien zrobić, a nie jak program powinien to zrobić. Na przykład wyobraź sobie, że piszesz program sortujący listę liczb w porządku rosnącym. W deklaratywnym języku programowania można napisać pojedynczą instrukcję, która mówi

- `wikibooks_2416013`: Konfigurowanie serwera XMPP obejmuje szereg kroków, które różnią się w zależności od używanego oprogramowania serwera. Oto kilka ogólnych kroków konfigurowania serwera XMPP: Zainstaluj i skonfiguruj oprogramowanie serwera: Pierwszym krokiem jest instalacja oprogramowania serwera XMPP na serwerze. Zwykle obejmuje to pobranie pakietu oprogramowania i postępowanie zgodnie z instrukcjami instalacji. Po zainstalowaniu oprogramowania skonfiguruj ustawienia serwera, w tym nazwę domeny i adres IP. Skonf

- `wikibooks_2415980`: 25px|Gracze Gracze od 2 do 6 graczy 25px|Talia Talia Gra się dwoma standardowymi taliami kart (w tym jokerami), co daje w sumie 108 kart. 25px|Zasady Zasady Celem gry jest zdobywanie punktów poprzez układanie układów kart i wychodzenie przed przeciwnikami. Rozdający tasuje karty i rozdaje każdemu graczowi po 11 kart. Pozostałe karty są umieszczane na środku stołu, tworząc stos do dobierania. Górna karta ze stosu dobierania jest odwracana, aby rozpocząć stos kart odrzuconych. Meld to zestaw trzec

- `wikibooks_2415925`: Uzyskany plik FASTA białek φOS10 zaimplementowano do programu VIRFAM (Podrozdziały 1.6.6 i 4.17.3), skąd otrzymano przyporządkowanie φOS10 do rodziny. Program VIRFAM przypisał φOS10 do rodziny Myoviridae (Rycina 20); niemniej jak wspomniano w Podrozdziale 1.2, w ciągu ostatnich kilkunastu miesięcy ustanowiono 2 nowe rodziny w rzędzie Caudovirales (tj. Ackermannviridae i Herelleviridae) o wielu cechach przypisywanym dotychczas tylko rodzinie Myoviridae; w związku z czym aktualnie dostępne program

- `wikibooks_2415894`: W wariancie procedury opisanej w Podrozdziale 4.14 wykorzystywano matrycę w postaci chromosomalnego DNA ze szczepu lizogennego. Przebieg był następujący: (i) do PCR-ówki dodawano 20 µl buforu lizującego; (ii) na czubek wymiennej końcówki pipety automatycznej pobierano 1 kolonię szczepu lizogennego; (iii) pobraną kolonię zawieszano w 20 µl buforu lizującego; (iv) mieszaninę inkubowano przez 10 min w temperaturze 98 °C, (v) zawartość PCR-ówki przenoszono do nowej probówki typu Eppendorf i dopełnia

- `wikibooks_2416018`: Świadectwa w mistycyzmie i tradycji religijnej odnoszą się do osobistych relacji osób, które doświadczyły głębokiego i głębokiego związku z Bogiem lub boskością. Świadectwa te często opisują doświadczenia intensywnego duchowego przebudzenia, oświecenia lub komunii z boskością, które mogą być trudne do wyrażenia samymi słowami. W tradycji chrześcijańskiej jest wiele przykładów mistyków i pisarzy religijnych, którzy pozostawili po sobie mocne świadectwa swoich spotkań z Bogiem. Niektóre z najbardz

Rejected:

- `wikibooks_2416181` (repeated_ngrams): Mechanika Newtona (nierelatywistyczna) dla układów słabozakrzywionych i globalnie (lokalnie) płaskich Będziemy tutaj rozpatrywali mechanikę Newtona w układach globalnie (lokalnie) płaskich, w nich prawa rządzące ruchem, a także uogólnimy pewne wielkości tej teorii dla układów słabozakrzywionych, gdzie tam wielkości zachodzą tylko w przybliżeniu, a nie dokładnie, a dla układów globalnie (lokalnie) 

- `wikibooks_2415845` (too_short, repeated_ngrams, technical_wiki_tail): Muzyka Autor: nieznany Źródło: Franciszek Barański, Jeszcze Polska nie zginęła! : pieśni patryotyczne i narodowe. Cz. 1-2. Lwów : Księgarnia Polska B. Połonieckiego, [post 1910]. S. 10 (pieśń 12). Tekst Autor: nieznany (niektóre źródła podają jako autora Marcelego Skałkowskiego (1818–1846) Źródło: Franciszek Barański, Jeszcze Polska nie zginęła! : pieśni patryotyczne i narodowe. Cz. 1-2. Lwów : Ks

- `wikibooks_2415769` (too_short, html_present): Whichunix.stackexchange question: why-not-use-which-what-to-use-then Działanie ignoruje wbudowane polecenia i wyszukuje tylko polecenia zewnętrzne, dlatego pokazał tylko te zewnętrzne przeszukuje katalogi wykazane w zmiennej środowiskowej $PATH i sprawdza, czy istnieje plik Opis jest zewnętrznym plikiem binarnym, znajdującym się w /usr/bin/ Pomoc offline online Porównaj command -v Źródła Kategoria

- `wikibooks_2416075` (repeated_ngrams): Użycie zaimków przed rzeczownikiem lub w zastępstwie rzeczownika (Gebrauch von Pronomen als Begleiter oder Stellvertreter des Substantivs) Zaimki, obok rodzajników, należą do grupy przedimków. Niektóre zaimki w zdaniu mogą występować zarówno przed rzeczownikiem jak i w jego zastępstwie , np. przed rzeczownikiem: Ist das dein Handy? w zastępstwie rzeczownika: Ja, das ist meins. Do takich zaimków na

- `wikibooks_2415938` (too_short, repeated_ngrams): Übugen - Präteritum (Imperfekt) test { |type="[]"} | | | ++- -++ --+ Inny przykład { } Następny przykład np. Test sprawdzajacy znajomosc form angielskich czasownikow Wpisz odpowiednie formy czasownikow: { infinitivepast tensepast participlePrzykladgowentgonedotu puste quizowe pole, by wpisac : didtu puste quizowe pole, by wpisac :donebringtu puste quizowe pole, by wpisac : broughttu puste quizowe 

### wikinews

Accepted:

- `wikinews_2377814`: od 2 marca 2026 mieszkańcy Krakowa oraz Skawiny mogą ponownie korzystać z systemu Park-e-Bike. Po zimowej przerwie do dyspozycji użytkowników oddano 143 jednoślady rozmieszczone na stacjach zlokalizowanych przy kluczowych parkingach przesiadkowych. Wypożyczalnia Park-e-Bike jest usługą darmową, skierowaną do osób pełnoletnich posiadających numer PESEL oraz ważny dokument tożsamości. System został zaprojektowany głównie z myślą o kierowcach korzystających z parkingów Park&Ride (P+R), umożliwiając

- `wikinews_2378044`: Zakład Ubezpieczeń Społecznych w dniu 26 marca 2026 wydał na swojej stronie internetowej oficjalny komunikat, w którym oświadczono, że instytucja ta będzie respektować akty stanu cywilnego dotyczące małżeństwa, którego dotyczył wyrok NSA z dnia 20 marca 2026 r. (sygnatura akt: II OSK 216/21). Komunikat zamieszczony na stronie zus.pl,. w zakładce komunikaty brzmi następująco: Tym samym Zakład zadeklarował, że wspomniana para będzie przez tę instytucję traktowana na równi z tradycyjnymi małżeństwa

- `wikinews_2377958`: 14 marca 2026 roku doszło do ataku irańskich bezzałogowców na cele w Kuwejcie. Trzech kuwejckich żołnierzy odniosło lekkie obrażenia w wyniku uderzenia na bazę lotniczą Ahmed Al-Dżaber. Obiekt ten znajduje się w bliskim sąsiedztwie Camp Arifjan, kluczowej instalacji wojskowej wykorzystywanej przez armię Stanów Zjednoczonych. Równolegle drony zaatakowały międzynarodowy port lotniczy w Kuwejcie. Kuwejcki sztab generalny poinformował, że krajowe systemy obrony powietrznej podjęły działania i skutec

- `wikinews_2377764`: Nowelizacja prawa o ruchu drogowym wprowadza od 3 marca 2026 roku istotne zmiany w zakresie uprawnień do prowadzenia pojazdów oraz sankcji dla kierowców. Najważniejsza korekta dotyczy rozszerzenia zasady czasowego odbierania prawa jazdy na trzy miesiące. Dotychczas kara ta była stosowana wobec osób przekraczających dopuszczalną prędkość o ponad 50 kilometrów na godzinę wyłącznie w obszarze zabudowanym. Zgodnie z nowymi uregulowaniami identyczne konsekwencje poniosą kierujący, którzy dopuszczą si

- `wikinews_2377910`: 11 marca 2026 roku Ministerstwo Zdrowia zapowiedziało wprowadzenie zmian w systemie refundacji leków, które wejdą w życie z początkiem kwietnia bieżącego roku. Jak poinformowała wiceminister Katarzyna Kacperczyk, wykaz zostanie rozszerzony o 16 nowych metod leczenia, z których większość dedykowana jest pacjentom onkologicznym. Wśród nowości na liście znajdzie się 14 terapii stosowanych w nowotworach oraz dwie o charakterze nieonkologicznym. Sześć z zapowiedzianych pozycji dotyczy leczenia chorób

- `wikinews_2378046`: zdecydował się powierzyć stanowisko metropolity łódzkiego Kardynałowi Konradowi Krajewskiemu, dotychczasowemu papieskiemu jałmużnikowi. Nowe obowiązki zaczął piastować w sobotę 28 marca 2026. Zastąpił na tym stanowisku, dotychczas pełniącego na nim posługę Grzegorza Rysia, którego pod koniec 2025 roku mianowano metropolitą krakowskim. Powołanie Krajewskiego miało miejsce podczas uroczystości w łódzkiej Archikatedrze pod wezwaniem św. Stanisława Kostki. Zdecydowano się wówczas, aby publicznie odc

- `wikinews_2377902`: Policjanci z grupy „Speed” zatrzymali 40-letniego mieszkańca , który 9 marca 2026 drastycznie złamał przepisy na . Mężczyzna kierujący jechał w okolicach z prędkością 226 km/h, przekraczając dozwolony limit o aż 106 km/h. Funkcjonariusze opublikowali nagranie z wideorejestratora ku przestrodze, przypominając, że nadmierna prędkość odpowiada za blisko 40% śmiertelnych wypadków w Polsce. Przy tak ekstremalnej jeździe droga hamowania wydłuża się drastycznie, a pole widzenia kierowcy ulega znacznemu

- `wikinews_2378085`: 14 kwietnia 2026 roku (prezes partii ) zwołał pilne spotkanie władz tego ugrupowania. Kluczowym tematem rozmów była być napięta sytuacja w strukturach partii oraz zamiary byłego premiera , który zamierza stworzyć własne ugrupowanie polityczne. Lider PiS stanął przed szeregiem wyzwań, które były tematem rozmów z kluczowymi politykami ugrupowania. Sytuację partii komplikuje aktywność Mateusza Morawieckiego budującego własne zaplecze polityczne oraz przegrana w . Dodatkowo Prawo i Sprawiedliwość no

- `wikinews_2377813`: 4 marca 2026 roku policjanci z Grodkowa zatrzymali 32-letniego mężczyznę, który kamieniem rozbił szybę w drzwiach wejściowych do budynku komisariatu. Sprawca, będący pod wpływem alkoholu, usłyszał zarzuty zniszczenia mienia oraz znieważenia funkcjonariuszki. Do zdarzenia doszło 26 lutego 2026 roku. Funkcjonariusze przebywający wewnątrz komisariatu w Grodkowie usłyszeli hałas dochodzący z zewnątrz. Po wyjściu przed budynek zauważyli napastnika, który rzucił kamieniem w szklany element drzwi. Spra

- `wikinews_2377874`: mały 8 marca 2026 roku na polskim Wikinews ukazał się siedemdziesiąty trzeci Quiz zawierający pytania z ostatniego tygodnia. Ideą Quizu jest możliwość sprawdzenia się Wikireporterów i wszystkich osób, które trafią na Wikinews, jak dobrze śledzą wydarzenia z ostatnich dni. Każde pytanie jest zamknięte i posiada maksymalnie pięć odpowiedzi. Wszystkie informacje, jakie są w pytaniach, pojawiły się na Wikinews w artykułach z ostatniego tygodnia, a więc aktywny czytelnik powinien sobie bez problemu z

Rejected:

- `wikinews_2378150` (too_short, wiki_markup_residue): mały|Gabriel Attal (2017) 9 stycznia 2024 roku mianował na , po tym jak dzień wcześniej odwołał z tej funkcji . Gabriel Attal dotychczas był ministrem edukacji, jest też bliskim współpracownikiem Macrona. Gabriel Attal jest pierwszym premierem Francji, który przyznaje się do bycia homoseksualistą. Źródła Kategoria:Emmanuel Macron Kategoria:Gabriel Attal Kategoria:Francja Kategoria:Francuska polity

- `wikinews_2377738` (wiki_markup_residue): thumb|Wojewódzki Szpital Specjalistyczny nr 5 im. św. Barbary w Sosnowcu. 19 lutego 2026 otrzymał zestaw do elektromagnetycznej śródoperacyjnej nawigacji obrazem, który ma wspierać lekarzy podczas zabiegów operacyjnych. 19 lutego 2026 poinformowało, że do Wojewódzkiego Szpitala Specjalistycznego im. św. Barbary w Sosnowcu trafił nowoczesny sprzęt wspomagający lekarzy w trakcie operacji. Według roz

- `wikinews_2377907` (wiki_markup_residue): mały|Michał Dworczyk (2024) 11 marca 2026 roku Prokuratura Okręgowa w Warszawie skierowała do sądu akt oskarżenia przeciwko Michałowi Dworczykowi w związku z tzw. aferą mailową. Byłemu szefowi Kancelarii Prezesa Rady Ministrów grozi kara pozbawienia wolności od 3 miesięcy do 5 lat. Główny zarzut dotyczy niedopełnienia obowiązków służbowych w okresie, gdy polityk pełnił funkcje wiceministra obrony 

- `wikinews_2378140` (too_short): Wybory prezydenckie na odbędą się 23 marca 2024. Ewentualna druga tura może się odbyć 6 kwietnia 2024 roku. Termin wyborów ogłosił (przewodniczący Rady Narodowej) 8 stycznia 2024 na konferencji prasowej. Źródła Kategoria:Słowacja Kategoria:Wybory prezydenckie na Słowacji w 2024 roku Kategoria:Wybory Kategoria:Słowacka polityka Kategoria:Archiwalne

- `wikinews_2378120` (wiki_markup_residue): mały|Ryoyu Kobayashi (2018) 6 stycznia 2024 roku odbyły się czwarte zawody , którego zwycięzcą został . Pierwsze zawody turnieju zwyciężył Andreas Wellinger, noworoczne zawody wygrał natomiast Anže Lanišek, a Andreas Wellinger był trzeci, wciąż utrzymując pozycję lidera. Po trzecich zawodów, które wygrał Jan Hörl, Ryōyū Kobayashi awansował na lidera turnieju, po tym jak za każdym razem zajmował dr

### wikisource

Accepted:

- `wikisource_1172322`: Uderzyli na nas — Jak ogień się rzucili — Oto nie mamy odpoczynku! Apsu jest pełny trwogi — On i Muumu — nasi jeńce! Żywo — wyruszmy — zbudźmy się! Oczy nasze ciężkie — zbudź się! Pomsta! Niechaj w burzy zostaną unicestwieni! Tiamat usłyszała słowa świetnego boga. Rzecze: Zginiesz! Stańmy do walki. Bogowie w niebiosach ruszyli przeciw bogom stworzycielom. Przeklinają światło — idą pobok Tiamat — Idą też stworzeni Lahmu i Lahamu[1] Idą wściekli — rozważają rzecz bez odpoczynku we dnie i w nocy — 

- `wikisource_1171986`: Matko miła, matko droga, Ojcze — bracie, żegnaj nam! — Niech się dzieje wola Boga! Córki miłe, ja wam dam Czarodziejskie trzy pierścienie Z sióstr — rodziny portretami, Na wspomnienie — pocieszenie I poznanie między wami. Oto Sygoń, brat wasz mały: On wyrośnie nam na chwata. W krąg obejdzie świat ten cały, Znajdzie was na końcu świata! Królewicze mężni, mili Ojca, matkę — całowali. Wszystkim grzecznie się skłonili, Z królewnami odjechali. Popłakały — odjechały, W domu został tylko brat... Rośnie

- `wikisource_1171910`: Królestwa mego krainę Za niecaluśką godzinę Obejdę w koło wszerz i wzdłuż, Opłynę morzem fali zbóż, Które mi biją pokłony, — Składają w dani swe plony, Bukiety kwiatów bogate Makiem, kąkolem, bławatem... Hej, jam jest władca, król i pan — Niczem car, sułtan, cesarz, chan! Królewska moja korona Ze złotych kłosów spleciona.. Potęgą siły moja dłoń... Dyadem znoju zdobi mi skroń, Niczem dyamentów kamienie, Co skrzą się zimnym płomieniem... Hej, ja to sobie jestem król — Gór, lasów, łanów, łąk i pół,

- `wikisource_1172216`: Na ozdobę swą osobę sprowadziłeś w te gęstwiny? — Mą ucieczką jest Gandiwa i te groty me ogniste, A te puszcze ocieniste — zamieszkuję niby Siwa. Ten zaś czart niesamowity tu przezemnie był ubity — — Powalony moim grotem, w piekło zwalił się pokotem. — Jam go pierwszy trafił strzałą: mojem jest to martwe ciało! — Nie przypisuj chwały sobie, co należna mej osobie. Pełny pychy, mocą dumny, tyś rycerzu nierozumny — I nie ujdziesz rąk mych żywy! Bądź wytrwały i cierpliwy: Rzucę w ciebie swoje groty,

- `wikisource_1172079`: Przy którym pas bogaty, suta frędzla pływa, Majdan gładko ciosany i tęga cięciwa, Co tak żałośnie jęczy, gdy z niej grot wyleci, Jako matka wydarte ścigająca dzieci: Jam nie sługa pragnienia, co się w noc zaczaja, I odstraszywszy źrebce, sam klacze wydaja; Jam nie tchórz ni za dziewic ogonem włóczęga, Co w każdej drobnej sprawie rady ich zasięga; Nie strusie serce moje: choć strach zakołata, Nierównym pędem w piersiach jak wróbel nie lata. Kto mię widział od rana do nocy śród gachów, Brew malowa

- `wikisource_1172130`: ACHMED BEN MOHAMED MOK’RI. I. (OGRÓD). Dla kwiatów tego ogrodu z jedwabiu utkała wiosna- Szatę: złoto i tęczę stubarwną kładąc na krosna. Zefiru, który się zbliża — pieściwe tu wieją tchnienia: Kochankiem on traw bogatych — i krynic srebrzystych drżenia. Ileż tu dziwnej piękności, gdy rosa perły rozdzieli Pomiędzy kielichy mirtów i róże. co stoją w bieli, Kiedy zdrój świeży wstrzymuje przechodnia swemi ramiony — I zdaje mu się podawać i uśmiech i anemony! Jak słodkim jest śpiew słowika, którego 

- `wikisource_1172082`: Gdy ujrzałem nad głową skał podniebne stropy. Na klęczkach pnąc się, jak pies, włazłem im na czoło. Tam dzikie antylopy biegały wokoło, Białonogie i wełną odziane bogatą, Jak nadobne dziewice wlekącą się szatą; I w oczy mi bez trwogi patrzyła gromada, Bo myślały, że jestem kozieł, wódz ich stada, Co mu rogi w tak długie piętrzą się ramiona, Że wznosząc łeb, rogami dostaje ogona, Albo niemi do skały przyczepia się szczytu I wisi, jako ptaszek w otchłani błękitu. (Adam Mickiewicz).

- `wikisource_1172074`: IMRUL-KAIS. I. Rankiem wyjeżdżam na łowy, gdy jeszcze w gniazdach są ptaki. Koń mnie unosi skrzydlaty, co niby łańcuch żelazny W locie swym niewstrzymanym zwierza dzikiego zakuwa. Koń jako wieża wysoki — to skacze wprzód, to się cofa, To się oddala, to zbliża — jakoby skała ogromna, Z gór strącona potokiem. Gniadą ma szerść jako jedwab’. Czaprak w galopie od grzbietu tak odskakuje jak deszczu Krople, które odrzuca głaz polerowny. — Wychudłe Nogi ma, życiem kipi, w zapałach pościgu i pędu Z piers

- `wikisource_1172292`: ...Czas — jest to źródło powszechne Rzeczy tych, co istnieją i co nie istnieją na świecie; Źródło nieszczęścia i szczęścia, źródło początku i końca. Czas wytwarza stworzenia, czas też unosi stworzenia. Czas pożera stworzenia, czas na spoczynek je składa. Czas więc je czyni dobremi, albo też złemi na świecie. Czas łączy wszystkie istoty, czas je rozpędza na nowo. Czas, kiedy śpimy, trwa czujnie. Więc trudno przestąpić moc czasu. Czas przenika zarówno wszystkie istoty i zjawy, A nikt zaiste na zie

- `wikisource_1172249`: Którzyby uwiecznili jego ród szlachetny: To trzecia laska, Jamo, przed twój tron wzniesiona. Jama. Aby utrwalić żywot swego pokolenia — Ojcu twojemu setne urodzą się syny: A teraz, gdy spełnione są twoje życzenia, Wracaj. Daleko zaszłaś w te leśne gęstwiny. Sawitri. Nie daleka mi droga, gdym przy Satyawanie: Dusza się moja w dalsze wydziera przestworze. Więc pozwól mi iść dalej. Tego co nastanie W słowach mych, racz posłuchać, o świetlany boże. Ty jesteś promienistym synem Wiwaswata, Przeto cię 

Rejected:

- `wikisource_1171936` (too_short): IV. Gdy zmartwychwstaną okryci siermięgą, Pełnią sił ducha i serc swych potęgą, Jak jedno wielkie milionów morze — Z Ojczyzny Matki opadną obroże. Gdy zmartwychwstaną i krew chłopską zdrową, Żywą, gorącą, płynącą, Piastową, Wleją w te inne, strupieszałe stany... Z Ojczyzny Matki opadną kajdany Gdy zmartwychwstaną, z duchem sercem w łonie Silnem, hartownem, jak pracą dłonie, Wróg, co nas zakuł w ka

- `wikisource_1172218` (too_short): Pełny smutku, krwią oblany, wzywa pana między pany, Wzywa boga mroków toni, który dzierży trójząb w dłoni; Poczem kurhan stawia mały, Siwie głosi hymn pochwały. Wieniec z kwiatów bogu wiąże. I w tej samej chwili książe, Tą modlitwą odrodzony, swój ofiarny ujrzy wieniec Na górala skroni złotej. I zrozumiał rzecz młodzieniec: Oto zjawił mu się bóg! Więc mu kornie padł do nóg. (A. Lange).

- `wikisource_1172312` (too_short): Mahâ-Bhârata. Kairata 303 Powieść o Rybie 309 Nal i Damajanti 312 Sawitri 331 Sokół i gołąb 345 Bhagawad-gîta 348 Kalidasa. Meghadûta 356 Ritusanhara 358 Dżajadewa. Gita-Gowinda 361 Bhartrihari. Setki 366 Z mądrości braminów 369 Poezje gnomiczne 372 Hitopadesa 378 Katha-sarit-sagra 381 Dhamma-padam 388 WAŻNIEJSZE OMYŁKI DRUKU. Str. wtersz zamiast powinno być 89 17 od góry trupów trudów 250 2 od do

- `wikisource_1171946` (too_short, repeated_ngrams): JESZCZE POLSKA NIE ZGINĘŁA! Jeszcze Polska nie zginęła! „Chłop potęgą jest i basta“. W jego łonie życia siła, Z której wolna przyszłość wzrasta. Jeszcze Polska nie zginęła! Miliony żyją kmieci, Którym polska ziemia miła, Jako matka dla swych dzieci. Jeszcze Polska nie zginęła! Rośnie w siłę plemię Piasta, Nie zmoże go wrogów siła: „Chłop potęgą jest i basta!“ Nie zginęła i nie zginie! Wolny orzeł 

- `wikisource_1171979` (too_short): — Doskonale! Więc teraz powiedz, jaką chcesz bajkę? — Już dziękuję wujaszkowi, bo to śliczna bajka, co mi wujaszek opowiedział o Heniusiu — o tym drugim Heniusiu. — Bardzo dobrze. A teraz powiedz, co wybierasz: psa czy ptaka? — Jeśli mam prawdę powiedzieć, to proszę o konia, takiego konia, jakiego miał ten Heniuś z bajki.

### parliamentary

Accepted:

- `parliamentary_2047387`: Szanowny Panie Marszałku! W odpowiedzi na interpelację poselską Pani Marii Zbyrowskiej, przesłaną przy piśmie z dnia 16 marca 2005 roku, znak: SPS-0202-9682/05, w sprawie potrzeby przyznania śmigłowca ratunkowego dla województwa podkarpackiego uprzejmie wyjaśniam, co następuje: W dniu 15 lutego 2005 roku Rada Ministrów zdecydowała o skierowaniu przedłożonego przez Ministra Zdrowia projektu ustawy o ustanowieniu programu ˝Wymiana śmigłowców Samodzielnego Publicznego Zakładu Opieki Zdrowotnej Lotn

- `parliamentary_2047051`: W jednym ze szpitali woj. podlaskiego pracownicy wystąpili do komornika o pomoc w ściągnięciu należnych wynagrodzeń. Początek całemu zamieszaniu dała ustawa z 2001 roku przyznająca pracownikom służby zdrowia podwyżki w 2001 r. o 203 zł, a w 2002 r. o dalsze 110 zł. Szpital z tego zobowiązania nie wywiązał się. Obecnie wobec załogi ma ponad trzy mln zł długu. Uzgodniony harmonogram spłaty zobowiązań nie został wykonany. Część pracowników (około 60 osób) poszło do komornika. Dyrektor szpitala w zw

- `parliamentary_2047281`: Pismem z dnia 28 września 2012 r. zwróciłam się do dyrektora GDDKiA w sprawie konsultacji przebiegu drogi ekspresowej S1 na odcinku od węzła Kosztowy II w Mysłowicach do węzła Suchy Potok w Bielsku-Białej. Rzeczowy ton odpowiedzi udzielonej przez GDDKiA nie uspokaja. Od wyboru wariantu trasy i jej przebiegu przez województwa małopolskie może zależeć istnienie Kopalni Węgla Kamiennego Brzeszcze. Odbyte konsultacje ujawniły ogromne koszty społeczne, z którymi będą zmuszeni zmierzyć się mieszkańcy 

- `parliamentary_2047144`: Szanowny Panie Ministrze! Na prośbę mieszkańców Katowic, dzielnicy Panewniki zwracam się do pana Ministra z pytaniami oraz przedstawiam obawy dotyczące niszczącego działania szkód górniczych na środowisko, zniszczenia domów, budynków, dróg oraz wielu innych konsekwencji wydobywania węgla ze złoża ˝Śląsk - Pole Panewnickie˝. Mieszkańcy wskazują również na problem niezgodności decyzji koncesyjnej z programem restrukturyzacji górnictwa węgla kamiennego. Wskazując na fakt, że decyzję o udzieleniu ko

- `parliamentary_2047001`: naję, że porządek obrad został przyjęty. Zanim przystąpimy do realizacji porządku dzisiejszych obrad, chciałbym przedstawić kilka informacji i uwag technicznych. Przed salą obrad wyłożone zostały przykładowe numery periodyków zajmujących się problematyką wojskową, które mogą szczególnie interesujące dla osób pojawiających się na posiedzeniu Komisji Obrony Narodowej po raz pierwszy. Wszelkie wydawnictwa tego typu są dostępne w sekretariacie Komisji. Jeśli ktoś z państwa będzie chciał do nich zajr

- `parliamentary_2047147`: Szanowny Panie Marszałku! W związku z zapytaniem posła Lecha Kołakowskiego, przesłanym przy piśmie z dnia 8 maja br., znak: SPS-024-1055/06, w sprawie ˝zmiany sposobu obliczania podstawy wymiaru emerytur i rent˝, uprzejmie wyjaśniam, co następuje: Zgodnie z ustawą z dnia 17 grudnia 1998 r. o emeryturach i rentach z Funduszu Ubezpieczeń Społecznych (Dz.U. z 2004 r. Nr 39, poz. 353 ze zmian.) podstawę wymiaru emerytury i renty może stanowić przeciętna podstawa wymiaru składki w okresie kolejnych 1

- `parliamentary_2047283`: Szanowna Pani Minister! Zwracam się do Pani ze sprawą, jaką do mnie zgłosili przedstawiciele Gdyńskiej Szkoły Filmowej. Centrum Edukacji Artystycznej w Warszawie powołując się na zmianę ustawy o systemie informacji oświatowej oraz rozporządzenia ministra edukacji narodowej z dnia 23 grudnia 2011 r. w sprawie klasyfikacji zawodów szkolnictwa zawodowego, zobowiązuje szkoły artystyczne wszystkich typów do dostosowania kierunków, specjalności i specjalizacji do wymogów tych aktów prawnych. W załącze

- `parliamentary_2047139`: Szanowny Panie Marszałku! W związku z interpelacją pań posłanek Marii Zbyrowskiej i Wandy Łyżwińskiej, nadesłaną przy piśmie z dnia 18 kwietnia 2003 r., nr SPS-0202-3455/03, w sprawie planowanych zmian w ustawie o podatku dochodowym od osób fizycznych, uprzejmie informuję. Istniejący system podatkowy ukształtowany został w wyniku procesu zainicjowanego na początku lat 90. Od tego czasu warunki gospodarowania ulegały systematycznym zmianom. W ich rezultacie ukształtował się skomplikowany, niespój

- `parliamentary_2047377`: Szanowny Panie Premierze! W myśl art. 20 ust. 1 ustawy z dnia 22 marca 1990 r. o pracownikach samorządowych (DzU z 2001 r. nr 142, poz. 1593) pracownikowi samorządowemu przysługuje wynagrodzenie stosowne do zajmowanego stanowiska oraz posiadanych kwalifikacji zawodowych. Maksymalne wynagrodzenie członka zarządu jednostki samorządu terytorialnego nie może przekroczyć w ciągu miesiąca łącznie z dodatkiem za wieloletnią pracę siedmiokrotności kwoty bazowej określonej w ustawie budżetowej dla osób z

- `parliamentary_2047357`: Szanowny Panie Marszałku! W związku z zapytaniem pana Antoniego Szymańskiego, posła na Sejm RP, z dnia 21 lutego 2001 r. w sprawie utrzymania rangi portu w Gdyni jako międzynarodowego przejścia granicznego dla surowców i produktów spożywczych po rozszerzeniu Unii Europejskiej, przekazanym przy piśmie pana marszałka znak: SPS-0203-3316/01, przedstawiam poniżej stanowisko Ministerstwa Transportu i Gospodarki Morskiej. 1. Pragnę wyjaśnić, że problematyka objęta zapytaniem pana posła w zasadniczej c

Rejected:

- `parliamentary_2046975` (too_short): Szanowna Pani Marszałek! W odpowiedzi na interpelację poseł Anny Sobeckiej w sprawie wypowiedzi radiowej posła dotyczącej obecności katolików w Platformie Obywatelskiej, z upoważnienia prezesa Rady Ministrów, uprzejmie informuję, że do cytowanej przez panią poseł Annę Sobecką wypowiedzi pana posła Andrzeja Halickiego odniósł się publicznie pan Marek Biernacki, minister sprawiedliwości, bezpośredni

- `parliamentary_2047195` (repeated_ngrams): Podatnik w postępowaniu podatkowym ma pozycję podporządkowaną władczym rozstrzygnięciom organu podatkowego. Z całą pewnością podatnikom nie ułatwia sprawy również fakt, iż przepisy podatkowe są bardzo skomplikowane i ulegają częstym zmianom. Dlatego też stworzono samorząd zawodowy doradców podatkowych mający na celu obronę interesów podatników i pomoc w zrozumieniu zawiłych przepisów podatkowych. 

- `parliamentary_2047314` (repeated_ngrams): Szanowny Panie Marszałku! Odpowiadając na interpelację panów posłów Józefa Rojka i Edwarda Czesaka (pismo znak: SPS-023-5330/08 z dnia 3 października 2008 r.) w sprawie warunków przejmowania terenów rodzinnych ogrodów działkowych w związku z realizacją inwestycji drogowych, uprzejmie wyjaśniam, iż zgodnie z art. 11j ustawy z dnia 10 kwietnia 2003 r. o szczególnych zasadach przygotowania i realizac

- `parliamentary_2047414` (repeated_ngrams): Szanowna Pani Marszałek, odpowiadając na interpelację numer 34321 poseł Doroty Arciszewskiej-Mielewczyk z dnia 28 sierpnia 2015 r., w sprawie możliwości wprowadzenia połączenia kolejowego relacji Gdynia Główna – Chojnice – Poznań Główny, przedstawiam następujące informacje. W związku z pytaniem dotyczącym analizy ruchów migracyjnych ludności w południowej części województwa pomorskiego informuję, 

- `parliamentary_2047050` (repeated_ngrams): Szanowny Panie Marszałku! Nawiązując do zapytania Pana Posła Zbigniewa Janowskiego w sprawie zaniżonej wysokości subwencji oświatowej przeznaczonej na funkcjonowanie szkół specjalnych, na przykładzie Specjalnego Ośrodka Szkolno-Wychowawczego w Zalutyniu (Nr SPS-0203-3560/04), przekazuję następujące informacje. Część oświatowa subwencji ogólnej dzielona jest pomiędzy poszczególne jednostki samorząd

