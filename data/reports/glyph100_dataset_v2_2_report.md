# Glyph-100M Dataset v2.2 Report

Generated: 2026-06-01T19:36:14.755529+00:00

No training was started.

## Verdict

C: v2.2 is not balanced enough for a 50k run. FinetextPL-Edu or another clean source is needed.

## Source Preflight

| source | decision | size / access | sample quality | risk |
|---|---|---|---|---|
| Wikipedia PL | use with cap <= 70% | 127.9M tokens already built | clean, but strongly Wikipedia-shaped | dominates style if uncapped |
| Wolne Lektury | use | 3.1M tokens already built | good continuous literary Polish | small source, older literary style |
| Wikisource PL | use with stricter cleanup | small streaming source | mixed; useful after removing index/meta/list pages | metadata, indexes, bibliographies, legal/source artifacts |
| Wikibooks PL | use with cleanup | 19.3 MB | educational prose mixed with wikitext/navigation | markup/list-heavy pages, indexes, technical pages |
| Allegro Polish Summaries Corpus | use only `source` field | ~271 MB data files by HF metadata | good long article text in `source`; summaries are not used | news/business/legal style; original source licensing should be verified |
| legacy_mixed_corpus | reject for v2.2 | not used | too much forum/commerce/SEO residue | reintroduces exact problems observed in Glyph-27M |

## Outputs

- train bin: `data/processed/glyph100_v2_2_train.bin`
- val bin: `data/processed/glyph100_v2_2_val.bin`
- docs JSONL: `data/processed/glyph100_v2_2_docs.jsonl`
- metadata: `data/processed/glyph100_v2_2_metadata.json`
- tokenizer: `data/processed/tokenizer.model`

## Counts

- train docs: 46,451
- val docs: 192
- train tokens: 36,850,254
- val tokens: 191,453
- total tokens: 37,041,707
- token/word ratio: 1.976
- Wikipedia share: 70.00%
- non-Wiki share: 30.00%

## Source Mix

| source | docs | tokens | share | train tokens | val tokens |
|---|---:|---:|---:|---:|---:|
| `allegro_summaries_source` | 539 | 1,368,381 | 3.69% | 1,360,347 | 8,034 |
| `wikibooks_pl` | 5,388 | 4,328,329 | 11.69% | 4,305,693 | 22,636 |
| `wikipedia_pl` | 37,648 | 25,929,191 | 70.00% | 25,798,075 | 131,116 |
| `wikisource_pl` | 1,543 | 2,272,465 | 6.13% | 2,258,594 | 13,871 |
| `wolne_lektury` | 1,525 | 3,143,341 | 8.49% | 3,127,545 | 15,796 |

## Wikipedia Cap

```json
{
  "wikipedia_tokens_before_cap": 126594330,
  "non_wikipedia_tokens": 11112516,
  "max_wikipedia_share": 0.7,
  "max_wikipedia_tokens_allowed": 25929203,
  "wikipedia_capped": true,
  "wikipedia_docs_before_cap": 184166,
  "wikipedia_docs_after_cap": 37648,
  "wikipedia_tokens_after_cap": 25929191
}
```

## Rejection Reasons

```json
{
  "too_short": 34053,
  "wikibooks_technical_namespace": 21484,
  "near_duplicate": 19844,
  "exact_duplicate": 19842,
  "normalized_duplicate": 19842,
  "low_alpha_ratio": 16717,
  "empty_after_clean": 9433,
  "too_much_punctuation_or_symbols": 9308,
  "repeated_ngrams": 6742,
  "wikibooks_redirect": 3211,
  "wikibooks_markup_residue": 2432,
  "wikibooks_list_like": 1847,
  "wikisource_list_like": 564,
  "low_unique_word_ratio": 563,
  "single_word_repetition": 440,
  "price_or_currency_heavy": 434,
  "low_polish_signal": 372,
  "forum_patterns": 349,
  "wikibooks_meta_page": 305,
  "allegro_list_heavy": 180,
  "commerce_patterns": 153,
  "wikibooks_index_or_cover_page": 144,
  "too_long": 127,
  "html_present": 117,
  "allegro_line_fragmented": 60,
  "too_many_urls": 48,
  "too_many_boilerplate_patterns": 19,
  "wikisource_disambiguation": 5,
  "very_long_line": 3,
  "wikisource_index_or_bibliography": 3
}
```

## Training Math

- stage 3 / 50k total: 819,200,000 tokens = 22.12 epochs
- 100k total: 1,638,400,000 tokens = 44.23 epochs
- 200k total: 3,276,800,000 tokens = 88.46 epochs

## Quality Notes

- wiki-style residue: reduced versus v2.1 by capping Wikipedia, but still present because Wikipedia remains the largest source
- Allegro `source` quality: uses only `source`; accepted samples are mostly continuous article/news/legal/business text, not summaries
- Wikibooks usefulness: useful educational/tutorial text after wikitext cleanup; some markup/list residue is rejected
- Wikisource usefulness: useful but stricter cleanup removes index, bibliography and technical/list pages

## Final Random Samples

1. `wikipedia_pl` Radziejów (tokens=6604, score=0.9749)

   Radziejów (wcześniej Radziejów Kujawski, ) – miasto w Polsce położone w województwie kujawsko-pomorskim, siedziba powiatu radziejowskiego oraz gminy wiejskiej Radziejów. Leży na Kujawach w odległości 35 km od Inowrocławia. W latach 1975–1998 miasto administracyjnie należało do województwa włocławskiego. Był miastem królewskim Korony Królestwa Polskiego, położony w II połowie XVI wieku w powiecie radziejowskim województwa brzeskokujawskiego, należał do starostwa radziejowskiego. Miejsce obrad sejmików ziemskich województwa brzeskokujawskiego i inowrocławskiego Rzeczypospolitej od XVI wieku do pierwszej połowy XVIII wieku. Według danych GUS z 31 grudnia 2022 r. Radziejów liczył 5127 mieszkańców. Struktura powierzchni Według danych z roku 2002 Radziejów ma obszar 5,75 km², w tym: użytki rolne: 62% użytki leśne: 7% Miasto stanowi 0,95% powierzchni powiatu. Demografia Dane z 31 grudnia 2022 r.: Piramida wieku mieszkańców Radziejowa w 2014 roku. Historia Pierwsza udokumentowana wzmianka w...

2. `wikipedia_pl` Opolnica (tokens=603, score=0.972)

   Opolnica () – wieś w Polsce położona w województwie dolnośląskim, w powiecie ząbkowickim, w gminie Bardo. Położenie Opolnica to wieś położona w centralnej części Gór Bardzkich, po obu stronach Nysy Kłodzkiej, wzdłuż przełomu, na wysokości około 265-275 m n.p.m. Niegdyś jej obie strony miejscowości były ze sobą połączone mostem; dziś już nie istnieje możliwość przeprawy przez rzekę w tym miejscu. Podział administracyjny W latach 1975–1998 miejscowość administracyjnie należała do województwa wałbrzyskiego. Historia Pierwsza wzmianka o Opolnicy pochodzi z roku 1359, z dokumentu dotyczącego zakupu ziemi przez miasto Bardo. Od XVI wieku wieś była ośrodkiem protestantyzmu, od XVII wieku miejscowy kościół należał do ewangelików, wkrótce powstała tam też szkoła ewangelicka. W 1741 roku w miejscowości stacjonowały wojska pruskie, które przez Przełęcz Bardzką wyruszyły na podbój Hrabstwa kłodzkiego. W 1811 r. wybudowany został zameczek. W drugiej połowie XIX wieku w okolicy rozwinęła się tury...

3. `allegro_summaries_source` Z Bartoszem Jałowieckim, szefem Fundacji Polsko-Niemieckie Pojednanie, o problemach z wypłatą odszkodowań rozmawia Filip Gawryś (tokens=1864, score=0.9725)

   Z Bartoszem Jałowieckim, szefem Fundacji Polsko-Niemieckie Pojednanie, o problemach z wypłatą odszkodowań rozmawia Filip Gawryś Niemcy muszą się rozliczyć FOT. MICHAŁ SADOWSKI Dziś nowojorska sędzia Shirley Kram zdecyduje, czy odrzucić pozwy poszkodowanych przez Trzecią Rzeszę przeciw niemieckim bankom. Jeśli pozwy zostaną odrzucone, otworzy to drogę do rozpoczęcia wypłaty świadczeń. Ale werdykt wcale nie jest pewny. Sąd może nie odrzucić pozwów (tak stało się w styczniu), bo niemiecki przemysł nie zebrał do tej pory obiecanych pięciu miliardów marek. Aby uzyskać brakujące środki na odszkodowania, niemieckie firmy zamierzają podwyższyć zadeklarowaną wcześniej składkę do funduszu odszkodowawczego z jednego do półtora promila od obrotów. Wczoraj przedstawiciele ofiar III Rzeszy przeprowadzili w warszawskim Teatrze Żydowskim happening połączony ze zbiórką pieniędzy na rzecz Inicjatywy Niemieckich Przedsiębiorstw, które nie zebrały jeszcze pełnej kwoty na odszkodowania. Rz: Kiedy polski...

4. `wikipedia_pl` Osobowość chwiejna emocjonalnie typu impulsywnego (tokens=286, score=0.9752)

   Osobowość chwiejna emocjonalnie podtypu impulsywnego – zaburzenie osobowości, w którym występuje wzorzec zachowań gwałtownych, przy braku przewidywania ich konsekwencji. W ICD-10 występuje pojęcie osobowości chwiejnej emocjonalnie (F60.3), która występuje w dwóch podtypach: podtyp impulsywny (F60.30), podtyp graniczny (F60.31). Kryteria diagnostyczne ICD-10 niestabilność emocjonalna brak kontroli działań impulsywnych wybuchy gwałtownych zachowań tysiące myśli w głowie ochota wyżycia się na innych duże napięcie w sobie wroga postawa wrogie spojrzenia na ludzi nienawiść Muszą wystąpić co najmniej trzy spośród cech wymienionych powyżej, a w tym druga: wyraźna tendencja do nieoczekiwanych działań bez zważania na konsekwencje, wyraźna tendencja do zachowań kłótliwych i do wchodzenia w konflikty z innymi, szczególnie jeżeli impulsywne działania zostały pokrzyżowane lub skrytykowane; ciążenie ku erupcjom gniewu lub gwałtowności, połączone z niezdolnością do kontrolowania wynikającego z teg...

5. `wikipedia_pl` Monestier (Ardèche) (tokens=87, score=0.958)

   Monestier – miejscowość i gmina we Francji, w regionie Owernia-Rodan-Alpy, w departamencie Ardèche. Według danych na rok 1990 gminę zamieszkiwały 52 osoby, a gęstość zaludnienia wynosiła 7 osób/km² (wśród 2880 gmin regionu Rodan-Alpy Monestier plasuje się na 1566. miejscu pod względem liczby ludności, natomiast pod względem powierzchni na miejscu 1326.).

6. `wikipedia_pl` Layrac (tokens=80, score=0.9652)

   Layrac – miejscowość i gmina we Francji, w regionie Nowa Akwitania, w departamencie Lot i Garonna. Według danych na rok 1990 gminę zamieszkiwały 2983 osoby, a gęstość zaludnienia wynosiła 78 osób/km² (wśród 2290 gmin Akwitanii Layrac plasuje się na 142. miejscu pod względem liczby ludności, natomiast pod względem powierzchni na miejscu 193.).

7. `allegro_summaries_source` GÓRNICTWO (tokens=2266, score=0.974)

   GÓRNICTWO Lobby górnicze wie, że kopalnie czeka umorzenie długów Jak sprywatyzować polski węgiel RYS. ROBERT DĄBROWSKI BARBARA CIESZEWSKA Prywatyzacja górnictwa będzie jednym z najtrudniejszych zadań. Jeśli nie uda się jej przeprowadzić obecnemu rządowi, to w przypadku przegranej w wyborach SLD-owski nie przeprowadzi jej także. Będzie to zadanie trudne również ze względów politycznych i ekonomicznych. Nie uda się uniknąć zarzutów związkowców i lewicy, mówiących o wyprzedaży narodowych bogactw i narażaniu bezpieczeństwa energetycznego kraju. Właśnie dlatego, że problem jest tak trudny, powinno się dyskutować o nim publicznie. Ostatnio ministrowie: gospodarki, finansów, pracy i ochrony środowiska otrzymali od Banku Światowego wstępny raport, który powstał po ubiegłorocznej misji brytyjskich ekspertów. Zauważa się w nim pewne analogie pomiędzy brytyjską a polską sytuacją górnictwa węglowego, ale też wskazuje na spore różnice. Eksperci brytyjscy proponują ich uwagi traktować jako wkład...

8. `allegro_summaries_source` Polak nauczył się już, że niezdrowe jest jedzenie zbyt tłuste i zbyt słodkie (tokens=2078, score=0.9479)

   Polak nauczył się już, że niezdrowe jest jedzenie zbyt tłuste i zbyt słodkie Karp trzyma się mocno RYS. PAWEŁ GAŁKA EDMUND SZOT "Najpierw był buraczany kwas, gotowany na grzybach z ziemniakami całymi, a potem przyszły śledzie w mące obtaczane i smażone w oleju konopnym, później zaś pszenne kluski z makiem, a potem szła kapusta z grzybami, olejem również omaszczona, a na ostatek podała Jagusia przysmak prawdziwy, bo racuszki z gryczanej mąki z miodem zatarte i w makowym oleju uprażone, a przegryzali to wszystko prostym chlebem, bo placka ni strucli, że z mlekiem i masłem były, nie godziło się jeść dnia tego. (...) Potem Jaguś nagotowała kawy, to słodzili ją suto i popijali z wolna". Chyba każdy rozpoznał ten opis wigilii z "Chłopów" Reymonta, wigilii zwanej też wilią, postnikiem, pośnikiem, kutią lub obiadem wigilijnym. Charakterystyczną cechą wieczerzy wigilijnej było to, że była postna, stąd ta nieczęsta w polskiej diecie obecność wszelakich ryb oraz unikanie tłuszczów zwierzęcych....

9. `allegro_summaries_source` Mamy nie tylko prawo, ale i obowiązek domagać się poszanowania naszej kultury, o co tak gwałtownie występuje Fallaci (tokens=3737, score=0.9551)

   Mamy nie tylko prawo, ale i obowiązek domagać się poszanowania naszej kultury, o co tak gwałtownie występuje Fallaci Głos w obronie Zachodu RYS. JANUSZ MAYK MAJEWSKI BRONISŁAW WILDSTEIN Po dziesięciu latach milczenia sławna dziennikarka i pisarka włoska, śmiertelnie dziś chora Oriana Fallaci, na łamach "Corriere della Sera' (29.09) wybuchnęła tekstem, który obudził burzę. Wygląda na to, że "GW", która tekst przedrukowała, przestraszyła się jego konsekwencji i opublikowała później wyłącznie wybór zagranicznych tudzież krajowych napaści na autorkę (mimo że odpowiedzią na "Wściekłość i dumę" nie był na świecie wyłącznie chór potępienia). Głosem szczególnym, choć jedynie do ostateczności doprowadzającym tezy oponentów Fallaci, był artykuł polskiego eksperta od poprawności politycznej, Konstantego Geberta, który nie tylko subtelnie uznał autorkę za emanację "europejskiego chama", ale przede wszystkim oburzył się, że artykuł został wydrukowany. Gebert zawyrokował, że w odniesieniu do tego...

10. `allegro_summaries_source` Berdyczów jest dla ukraińskich katolików tym, czym dla polskich Częstochowa. Poza tym od innych, prowincjonalnych miast Ukrainy nie różni go prawie nic. Życie tu prozaiczne aż do b (tokens=2947, score=0.9659)

   Berdyczów jest dla ukraińskich katolików tym, czym dla polskich Częstochowa. Poza tym od innych, prowincjonalnych miast Ukrainy nie różni go prawie nic. Życie tu prozaiczne aż do bólu - bieda, bezrobocie, brud, brak jakichkolwiek perspektyw. Aż dziw, że wciąż są wśród berdyczowian ludzie, którym chce się chcieć. Prawie martwa natura z nieczynną latarnią JAN TRZCIŃSKI Do Berdyczowa, odległego od Kijowa o 185 kilometrów, jedzie się autobusem ukraińskiego PKS-u cztery godziny. Na stołecznym dworcu wsiada do starego, lepkiego ikarusa wszystkiego dziesięć osób. Drugie tyle czeka na drodze, sto, sto pięćdziesiąt metrów od dworca. To prywatni pasażerowie kierowcy. Potem będzie ich co i rusz przybywać i ubywać, najwięcej na ostatnim odcinku, między Żytomierzem a Berdyczowem, gdzie kierowca zatrzymuje się co dwa kilometry, podwożąc ze wsi do wsi przekupki i podpitych chłoporobotników. W głowie kręci się od zapachów - owoce, warzywa, drób, mokre od deszczu kurtki, podły tytoń, nieprzetrawiona...

11. `allegro_summaries_source` BANK ŚWIATOWY (tokens=1819, score=0.9467)

   BANK ŚWIATOWY W ciągu minionych miesięcy nauczyliśmy się, że przyczyny kryzysów finansowych i biedy są takie same Koalicja do walki z nędzą RYS. ALICJA KRZĘTOWSKA JAMES D. WOLFENSOHN Rok temu kryzys azjatycki zniszczył wiele z 30-letnich zdobyczy tego regionu w zakresie dynamicznego wzrostu i zmniejszania ubóstwa. Miałem wówczas wrażenie, że społeczność międzynarodowa musi się bardziej zaangażować w ochronę biednych, a także podejść bardziej kompleksowo do problemu rozwoju. Powinna więc, poza zwykłym przyjęciem rozwiązań finansowych takich kryzysów, wziąć równie pilnie pod uwagę priorytety społeczno-instytucjonalne, które zapewniają zdrowie i dobrobyt ludziom, bo tworzą podstawy prawne, sądowe i zarządzania nowoczesnymi gospodarkami rynkowymi. Dwanaście miesięcy później można pomyśleć, że azjatycki kryzys wreszcie skończył się i można odłożyć reformy zmierzające do tego, by ożywienie stało się solidne i długotrwałe. Istnieje pokusa do stwierdzenia, że region wydostał się już z kłopo...

12. `allegro_summaries_source` W firmach konieczne są zwolnienia i wzrost wydajności pracy (tokens=2333, score=0.9765)

   W firmach konieczne są zwolnienia i wzrost wydajności pracy Zbędne są nie tylko panie od herbaty Pierwszy etap zwolnień najbardziej zbędnych pracowników większość polskich firm ma już za sobą. W najbliższych latach możemy spodziewać się kolejnych redukcji zatrudnienia - oceniają ekonomiści. Firmy będą do tego zmuszone, by ograniczyć koszty i poprawić swą konkurencyjność nie tylko w eksporcie, ale przede wszystkim na rynku krajowym. Bohdan Wyżnikiewicz z Instytutu Badań nad Gospodarką Rynkową (IBnGR) ocenia, że mamy już za sobą pierwszy etap restrukturyzacji przedsiębiorstw, który polegał na pozbyciu się absolutnie niepotrzebnej siły roboczej, np. pań do parzenia herbaty w biurach. Dotychczas jednak bardzo ostrożnie zwalniano pracowników zatrudnionych bezpośrednio w produkcji. Teraz przyszedł na to czas. Jak przypomina Bohdan Wyżnikiewicz, gdy porównamy największe polskie przedsiębiorstwa z ich zachodnimi odpowiednikami, okazuje się, że w stosunku do wielkości produkcji zatrudnienie...

13. `allegro_summaries_source` Polemika Strzembosz nie chce zauważyć, że trzecia część osadzonych w łagrach to Żydzi (tokens=2912, score=0.9373)

   Polemika Strzembosz nie chce zauważyć, że trzecia część osadzonych w łagrach to Żydzi Historia Polski po Jedwabnem będzie wyglądała inaczej RYS. PAWEŁ GAŁKA JÓZEF LEWANDOWSKI W "Rzeczpospolitej" z 27 stycznia 2001 roku przeczytałem artykuł profesora Tomasza Strzembosza o Jedwabnem. W wielu sprawach zgadzam się z nim. Nie należy mordować ludzi, i to niezależnie od pobudek, które by ten mord uzasadniały. Zgadzamy się też co do zbrodniczego charakteru systemu sowieckiego. Niestety, profesor Strzembosz w dalszych rozważaniach anuluje swoje słuszne stwierdzenia. Bo co prawda nie należy mordować, ale w przypadku Jedwabnego winni byli Żydzi, miejscowi i niemiejscowi, którzy byli komunistami. Gdy władza sowiecka zajęła Jedwabne, zbudowali bramę triumfalną, zajęli urzędy dotychczas zajmowane przez polskich urzędników, wstąpili do milicji, a nawet prawdopodobnie (dowodów na to Strzembosz nie ma, ale dedukuje) sporządzali listy proskrypcyjne na Polaków. A więc, jak sądzi, spalenie 600 czy 1600...

14. `wikipedia_pl` Kriogenika (tokens=822, score=0.979)

   Kriogenika (gr. krios „zimno”, genos „ród”) – dział techniki wytwarzający, mierzący i utrzymujący skrajnie niskie temperatury; nie są one zdefiniowane ściśle, lecz czasem za granicę przyjmuje się −150 °C (123 K). Kriogenika jest blisko związana z kriofizyką, która bada właściwości ciał w tych temperaturach, np. charakterystyczne dla tego reżimu zjawiska jak nadprzewodnictwo i nadciekłość. Kriogenika ma poważny udział w takich dziedzinach jak: badania przestrzeni kosmicznej, biologia i chirurgia, w przemyśle spożywczym, metalurgicznym, chemicznym i urządzeniach nadprzewodzących. Zastosowanie elementów nadprzewodzących w urządzeniach energetycznych prowadzi do znacznego zmniejszenia kosztów i masy tych urządzeń oraz zwiększenia sprawności i wydajności przy zachowaniu ich mocy. Skraplanie gazów Ważną poddziedziną kriogeniki są technologie uzyskiwania i magazynowania skroplonych gazów. Zastosowanie skroplonych gazów jest najczęściej stosowaną w przemyśle technicznym metodą osiągnięcia b...

15. `wikipedia_pl` Hans-Josef Becker (tokens=291, score=0.9761)

   Hans-Josef Becker (ur. 8 czerwca 1948 w Belecke, obecnie część miasta Warstein) – niemiecki duchowny rzymskokatolicki, biskup pomocniczy Paderborn w latach 1999–2003, arcybiskup metropolita Paderborn w latach 2003–2022, od 2022 arcybiskup senior archidiecezji Paderborn. Życiorys Do szkoły średniej uczęszczał i maturę zdał w Rüthen (1967). Studiował następnie pedagogikę i w 1972 złożył państwowe egzaminy nauczycielskie. W Paderborn i Monachium studiował filozofię i teologię. 11 czerwca 1977 przyjął święcenia kapłańskie z rąk arcybiskupa Paderborn Johannesa Joachima Degenhardta. Był duszpasterzem w Minden, Paderborn i Lippstadt, od 1995 pracował w kurii archidiecezjalnej. W grudniu 1999 papież Jan Paweł II mianował go biskupem pomocniczym archidiecezji Paderborn ze stolicą tytularną Vina. Sakry biskupiej udzielił mu arcybiskup Degenhardt 23 stycznia 2000. Po śmierci Degenhardta w 2002 zarządzał archidiecezją paderborńską jako administrator, a w lipcu 2003 został mianowany arcybiskupem...

16. `allegro_summaries_source` USA - KUBA (tokens=2630, score=0.9286)

   USA - KUBA Sześcioletni chłopiec w centrum międzynarodowego konfliktu Awantura o Eliana Cudownie uratowany Elian stał się dla Kubańczyków z Florydy symbolem cierpień narodu pod rządami komunistycznego reżimu FOT. (C) REUTERS SYLWESTER WALCZAK "Mam ochotę połamać im karki - powiedział Juan Miguel Gonzalez o swych krewnych w Miami. - Jeśli tam pojadę, mogę wziąć ze sobą strzelbę, żeby skończyć z tym raz na zawsze. Popatrzcie tylko, co oni robią z moim synem?" Syn Juana, 6-letni Elian Gonzalez, cudem przeżył dwie doby na otwartym morzu, przywiązany do gumowej dętki. 25 listopada ubiegłego roku uratowali go dwaj rybacy z Florydy. Chłopiec był pasażerem niewielkiej, aluminiowej łodzi, którą grupa 14 Kubańczyków próbowała uciec z rządzonej przez Fidela Castro wyspy. Łódź się wywróciła, 11 osób utonęło, w tym matka Eliana i jej narzeczony. O Eliana upomniał się jego ojciec, zamieszkały w Cardens pod Hawaną Juan Miguel Gonzalez, pracownik jednego z hoteli w Varadero. Po kilku tygodniach roz...

17. `allegro_summaries_source` ROZMOWA (tokens=1695, score=0.9715)

   ROZMOWA Grzegorz Boguta, były prezes grupy wydawniczej PWN Jak zostać odchodząc FOT. ANDRZEJ WIKTOR Od 1990 roku kierował pan wydawnictwem PWN. Doprowadził je pan do prywatyzacji, z pana nazwiskiem łączą się sukcesy firmy w połowie lat 90. Skąd nagle decyzja o rezygnacji nie tylko ze stanowiska prezesa, ale w ogóle z pracy w Wydawnictwie Naukowym PWN? GRZEGORZ BOGUTA: Jako współwłaściciel PWN - mam blisko 5 proc. akcji spółki - wystosowałem w połowie września tego roku pismo do pozostałych dużych akcjonariuszy, proponując zmiany w dotychczasowej strukturze własnościowej firmy, w moim przekonaniu nie sprzyjającej jej dalszemu rozwojowi. Po ponad dwóch miesiącach osiągnęliśmy w tej sprawie porozumienie. Jednocześnie doszedłem jednak do wniosku, że więcej mogę zrobić dla PWN, odsuwając się od bieżącego zarządzania. Obecnie bardziej interesuje mnie długofalowa strategia, która pozwoliłaby zwiększyć wartość firmy. Przecież cały czas jestem jej współwłaścicielem. Myślę też o nowych inicja...

18. `wikipedia_pl` Kazimierz Karaś (tokens=669, score=0.9761)

   Kazimierz Karaś herbu Dąbrowa (ur. 1711, zm. 6 lutego 1775 w Warszawie) – generał major wojsk koronnych, kasztelan wiski, marszałek prywatny króla Stanisława Augusta Poniatowskiego, asesor Komisji Skarbu Jego Królewskiej Mości w 1768 roku. Życiorys Wychowanek i zaufany domownik Stanisława Poniatowskiego, kasztelana krakowskiego i ojca króla. Cześnik buski, później cześnik liwski, od 1749 pułkownik wojsk królewskich. Konsyliarz konfederacji Czartoryskich w 1764 roku. Był elektorem Stanisława Augusta Poniatowskiego z ziemi warszawskiej w 1764 roku. W 1764 został wybrany posłem ziemi warszawskiej na sejm elekcyjny. Został mianowany członkiem komisji skarbowej dóbr stołowych. W lipcu mianowany kasztelanem wiskim i z tytułem Administrator Poczt kierował Naczelnym Zarządem Poczt Koronnych i Litewskich. Od 1765 prywatny marszałek dworu królewskiego Stanisława Augusta Poniatowskiego. Odznaczony Orderem św. Stanisława 8 maja 1765 (były to pierwsze ordery Stanisława Augusta Poniatowskiego, kt...

19. `wikipedia_pl` Podlodów (gmina Łaszczów) (tokens=549, score=0.9089)

   Podlodów – wieś w Polsce położona w województwie lubelskim, w powiecie tomaszowskim, w gminie Łaszczów. W latach 1975–1998 miejscowość należała administracyjnie do województwa zamojskiego. Wieś stanowi sołectwo gminy Łaszczów. Historia Ślady osadnictwa sięgają okresu kultury przeworskiej - w roku 1960 znaleziono tu bogato wyposażony grób z III wieku, ze zdobionym mieczem rzymskim. Wieś notowana w roku 1439 jako „Pollodow”. Z Podlodowa pisali się w roku 1439 Mikołaj i Jan. W wieku XIX Podlodów stanowił wieś z folwarkiem, a także dobra tej nazwy w powiecie tomaszowskim, gminie Czerkasy, parafii Gródek. Wieś odległa 16 wiorst od Tomaszowa położona wówczas przy granicy galicyjskiej. W roku 1885 Podlodów posiadał 54 domy i 301 mieszkańców, w tym wyznania rzymskokatolickiego 119 osób. Według spisu miast, wsi, osad Królestwa Polskiego z 1827 r. we wsi były 43 domy i 312 mieszkańców. W ówczesnej wsi była cerkiew drewniana zbudowana w roku 1752, filialna do parafii w Pienianach, a także szkó...

20. `allegro_summaries_source` STULECIE BOKSU (tokens=4728, score=0.9213)

   STULECIE BOKSU Kariery wielu mistrzów pięści rodzą się z nędzy, ambicji i nieposkromionej dumy Magia zła Dwie przedwojenne walki Joe Louisa i Maksa Schmellinga przeszły do legendy. Pierwszą wygrał Schmelling, w drugiej (na zdjęciu) Amerykanin znokautował Niemca w drugiej minucie i czwartej sekundzie pierwszej rundy (C) AP JANUSZ PINDERA W czym tkwi fenomen boksu, sportu od lat budzącego kontrowersje i mieszane uczucia? Jedni twierdzą, nie kryjąc oburzenia, że boks jest niegodny cywilizacji końca XX wieku, inni z kolei uważają, że w świecie, gdzie dobro przemieszane jest ze złem, zawsze będzie miejsce dla tych, którzy chcą oglądać boks. Kto jest bliższy prawdy, czy ci, którzy twierdzą, że z medycznego punktu widzenia sport ten powinien być zakazany, czy może ci, którzy stoją na stanowisku, że boks jest wentylem pozwalającym rozładować naturalną agresję tkwiącą w człowieku. Jedni i drudzy mają rację. Setki wypadków śmiertelnych mających ścisły związek z boksem to fakty, których nie da...

21. `wikipedia_pl` 1048 (tokens=100, score=0.9601)

   Wydarzenia w Polsce Odzyskanie Pomorza. Wydarzenia na świecie 17 lipca – Damazy II został papieżem. Urodzili się Świętosława Swatawa – siostra Bolesława Śmiałego, córka Kazimierza Odnowiciela i Marii Dobroniegi (data sporna lub przybliżona) (ur. w latach 1041-1048, zm. 1126) Zmarli Li Yuanhao – przywódca Tangutów Papież Damazy II 1048

22. `wikipedia_pl` Markowizna (województwo podkarpackie) (tokens=420, score=0.9759)

   Markowizna – wieś w Polsce położona w województwie podkarpackim, w powiecie rzeszowskim, w gminie Sokołów Małopolski. W latach 1975–1998 miejscowość administracyjnie należała do województwa rzeszowskiego. Nazwy obiektów fizjograficznych: pole - Olszyny, łąka - Łączyska, Olszyny, Pasternik, rzeka - Czerwonka, Turka, zagajnik - Nad Dworskiem, Na Granicy. Historia W osiemnastym wieku powstała akcja osadnicza w dobrach królewskich na obszarze Puszczy Sandomierskiej w wyniku, której powstała wieś Markowizna. Dnia 5 grudnia 1752 roku król August III wystawił w Warszawie dokument dla szlachcica Antoniego Ratyńskiego i jego żony Katarzyny z Lewickich zezwalający na lokację Markowizny w dobrach ekonomii sandomierskiej. Wyznaczono dla niej miejsce między wsiami królewskimi Mazury, Kamień oraz Rękawem i Turzą. Antoni Ratyński, podejmujący się osadzenia wsi, otrzymał ją prawem wieczystej dzierżawy na 40 lat. Przez 6 lat osadnicy zostali zwolnieni od wszelkich świadczeń na rzecz skarbu królewski...

23. `wikipedia_pl` Klingoni (tokens=278, score=0.9773)

   Klingoni (w języku klingońskim tlhİngan) – fikcyjna rasa humanoidalna przedstawiona w serii Star Trek. Klingoni to rasa wojowników. Ich ojczystą planetą jest Qo'noS. Klingoni słyną z wielkiego męstwa oraz chęci do walki, a ich społeczeństwo funkcjonuje w oparciu o brutalne zasady, w których współczucie i słabość traktowane są z największą odrazą. W swoich poczynaniach kierują się zasadami honoru i chęcią zdobycia chwały. Posługują się językiem klingońskim, który został wymyślony na potrzeby serialu, a następnie, dzięki zaangażowaniu fanów z całego świata, stał się jednym z najlepiej rozwiniętych sztucznych języków. W pierwszym serialu spod znaku Star Trek (ang. Star Trek: The Original Series) Klingoni zostali przedstawieni jako wrogowie i antagoniści Zjednoczonej Federacji Planet. Utworzone przez nich imperium stanowi jedną z głównych sił Kwadrantu Alfa. W kolejnych serialach stosunki między Klingonami a Zjednoczoną Federacją Planet ulegają znacznej poprawie. W pewnych okresach Impe...

24. `wikipedia_pl` Escrignelles (tokens=81, score=0.962)

   Escrignelles – miejscowość i gmina we Francji, w Regionie Centralnym, w departamencie Loiret. Według danych na rok 1990 gminę zamieszkiwały 83 osoby, a gęstość zaludnienia wynosiła 6 osób/km² (wśród 1842 gmin Centre, Escrignelles plasuje się na 1046. miejscu pod względem liczby ludności, natomiast pod względem powierzchni na miejscu 948.).

25. `wikipedia_pl` Cazavet (tokens=85, score=0.9623)

   Cazavet – miejscowość i gmina we Francji, w regionie Oksytania, w departamencie Ariège. Według danych na rok 1990 gminę zamieszkiwało 185 osób, a gęstość zaludnienia wynosiła 10 osób/km² (wśród 3020 gmin regionu Midi-Pyrénées Cazavet plasuje się na 878. miejscu pod względem liczby ludności, natomiast pod względem powierzchni na miejscu 614.).

26. `wikipedia_pl` Naddniestrze (tokens=4735, score=0.931)

   Naddniestrze (oficjalnie Naddniestrzańska Republika Mołdawska, także: Mołdawska Republika Naddniestrza) – de iure region autonomiczny we wschodniej Mołdawii, de facto państwo nieuznawane ze stolicą w Tyraspolu, obejmujące tereny położone na lewym brzegu Dniestru oraz prawobrzeżne miasto Bendery (Tighina). Jest to pas ziemi o długości około 200 km i średniej szerokości około 12–15 km (najmniejsza szerokość 6 km, największa 38 km). Państwo jednostronnie oderwało się od Mołdawii 2 września 1990, deklarując pozostanie w składzie Związku Radzieckiego, podczas gdy Mołdawia wystąpiła z niego 23 czerwca tego roku. Niepodległość ogłosiło 5 grudnia 1990 roku. Jest uznawane wyłącznie przez Abchazję i Osetię Południową, które same nie są uznawane za osobne państwa przez większość świata. Na arenie międzynarodowej Naddniestrze jest traktowane jako region autonomiczny Mołdawii, jej integralna część. Flaga Naddniestrza pozbawiona była symboliki radzieckiej, od 2000 roku używa się jednak flagi z si...

27. `wolne_lektury` XXXIII (Pośród narodów, wyście nędzarzami!...) (tokens=476, score=0.9004)

   Adam Asnyk Nad głębiami XXXIII Pośród narodów, wyście nędzarzami! Z dumą hidalgów nosicie łachmany, I odkrywacie światu swoje rany, Aby zarabiać na chleb krwią i łzami. Własną nikczemność znacie dobrze sami, Więc się chowacie w pamiątek kurhany, I gdy kto skargę podniesie stroskany, Wołacie: że on świętość grobu plami. Trzeba mieć litość nad wami, nędzarze, Trzeba wam życzyć o biedni, ułomni! Żebyście ciche zalegli cmentarze, I z tego świata zeszli bezpotomni; Śmierć wam tę jedną nadzieję ukaże: Że o was Polska i przyszłość zapomni! ----- Ta lektura, podobnie jak tysiące innych, dostępna jest na stronie wolnelektury.pl. Wersja lektury w opracowaniu merytorycznym i krytycznym (przypisy i motywy) dostępna jest na stronie Utwór opracowany został w ramach projektu Wolne Lektury przez fundację Wolne Lektury. Wszystkie zasoby Wolnych Lektur możesz swobodnie wykorzystywać, publikować i rozpowszechniać pod warunkiem zachowania warunków licencji i zgodnie z Zasadami wykorzystania Wolnych Lek...

28. `wikipedia_pl` Sandouville (tokens=120, score=0.967)

   Sandouville – miejscowość i gmina we Francji, w regionie Normandia, w departamencie Sekwana Nadmorska. Według danych na rok 1990 gminę zamieszkiwały 703 osoby, a gęstość zaludnienia wynosiła 47 osób/km² (wśród 1421 gmin Górnej Normandii Sandouville plasuje się na 339. miejscu pod względem liczby ludności, natomiast pod względem powierzchni na miejscu 140.). W Sandouville mieści się fabryka samochodów Renault, w której produkowane były modele m.in. Renault Laguna i Renault Vel Satis, a obecnie Renault Trafic.

29. `allegro_summaries_source` ROZMOWA (tokens=1783, score=0.968)

   ROZMOWA Basil Kavalsky, przedstawiciel Banku Światowego na Polskę i kraje bałtyckie Jeszcze jest co robić KREDYTY BANKU ŚWIATOWEGO DLA POLSKI W LATACH 1990-2000 Basil Kavalsky, przedstawiciel Banku Światowego FOT. PIOTR KOWALCZYK Wyjeżdża pan z Polski po trzyletnim pobycie. Jakie są, pana zdaniem, największe różnice pomiędzy Polską trzy lata temu i teraz? BASIL KAVALSKY: Wtedy mieliśmy mniej dowodów na to, jak silne są podstawy polskich przemian gospodarczych. Byliśmy zaniepokojeni, czy Polska będzie miała dość odporności, aby uporać się z niekorzystnymi wpływami z zewnątrz, gdyby coś takiego miało miejsce. Obawialiśmy się, że popyt konsumpcyjny jest zbyt silny, a gospodarka przegrzana Ale od tego czasu polska gospodarka przeszła próbę ognia. Okazało się, że kryzys w Azji i Rosji oraz recesja na zachodzie wydarzyły się, a Polska uzyskała w tym czasie 4 proc. wzrostu PKB. Teraz więc mamy znacznie więcej zaufania co do polskich fundamentów. Obawialiśmy się jednak o sytuację polskiego...

30. `allegro_summaries_source` ROZMOWA (tokens=2464, score=0.9297)

   ROZMOWA Longin Komołowski, wicepremier oraz minister pracy i polityki społecznej Musimy dostrzegać oczekiwania FOT. PIOTR KOWALCZYK Pamięta Pan początki rozmów koalicyjnych, poprzedzających utworzenie rządu Jerzego Buzka? Zakładano wówczas, że będzie dwóch wicepremierów: Leszek Balcerowicz, szef resortu finansów, i minister pracy. Miało to zagwarantować równowagę ekonomicznych i społecznych priorytetów rządu... LONGIN KOMOłOWSKI: Tak, wtedy rzeczywiście myślano takimi kategoriami. Teraz jednak, po dwóch latach pracy w rządzie, sądzę, a nawet wiem, że przypisywanie funkcji wicepremiera nadzwyczajnych możliwości jest błędem. Prawdą jest, że wicepremier, minister finansów kieruje pracami Komitetu Ekonomicznego Rady Ministrów, a wicepremier, minister pracy - Komitetem Społecznym Rady Ministrów. Kierowanie KSRM da Panu możliwość wpływania na prace innych poza Ministerstwem Pracy "społecznych" resortów? Da możliwość większej koordynacji rozwiązań i decyzji wypracowywanych w tych resortach...

31. `wikipedia_pl` Inferencja gramatyki (tokens=162, score=0.9622)

   Inferencja gramatyki – szczególny przypadek indukcyjnego uczenia się, w którym celem jest stworzenie pewnej gramatyki formalnej na podstawie dostarczonych pozytywnych przykładów słów pewnego języka, oraz przykładów negatywnych. Przykłady pozytywne powinny należeć do języka generowanego przez tę gramatykę, natomiast negatywne nie powinny się w nim znaleźć. Istnieją algorytmy pozwalające na inferencję gramatyki języków regularnych (k-TSSI, RPNI, MGGI, GIG, ALERGIA, ECGI) oraz bezkontekstowych (ALERGIA, Inside-Outside, RPNI++). Nie są znane skuteczne algorytmy dla języków kontekstowych. Języki formalne

32. `allegro_summaries_source` POLSKA-UE (tokens=2347, score=0.9407)

   POLSKA-UE Poparcie dla integracji dramatycznie maleje Polska wieś u wrót Europy RYS. JÓZEF KACZMARCZYK EDMUND SZOT Z ostatnich sondaży opinii publicznej wynika, że poparcie wejścia Polski do Unii Europejskiej dramatycznie maleje. Ostatnio wyniosło około 46 proc. Wśród ludności wiejskiej idea integracji Polski z UE ma jeszcze mniej zwolenników, co trudno zrozumieć, gdyż głównym jej beneficjentem będzie właśnie wieś. Na połączeniu z Unią skorzystają rolnicy, gdyż wsparcie dla rolnictwa jest w UE dwa - trzy razy większe niż w Polsce, korzyść odniosą także pozostali mieszkańcy wsi, gdyż Unia łoży bardzo duże środki na ogólny rozwój obszarów wiejskich, czyli na zbliżanie tutejszych warunków bytowania do tych, jakie ma ludność miejska. W tej sytuacji opór przed integracją trudno pojmować inaczej niż lęk przed czymś nowym, nieznanym, a trzeba pamiętać, że tego typu bojaźń na konserwatywnej z natury wsi była zawsze większa niż w mieście. Obawy te są umiejętnie podsycane przez różne niechętn...

33. `allegro_summaries_source` W najgłębszym interesie Rzeczypospolitej leży przyłączenie się do europejskiej współpracy polityczno-obronnej (tokens=2205, score=0.9679)

   W najgłębszym interesie Rzeczypospolitej leży przyłączenie się do europejskiej współpracy polityczno-obronnej Zacieśnianie wspólnoty Mnożą się wątpliwości co do daty wejścia Polski do Unii Europejskiej. Równocześnie ruszyła u nas nareszcie z miejsca publiczna debata nad pożądanym kształtem unijnych instytucji. Debata ruszyła tam właśnie, gdzie się odbywać powinna: w gronach przywódczych partii politycznych (mam na myśli przede wszystkim wypowiedź Jana Marii Rokity na europejskiej konferencji SKL). To tylko pozorny paradoks; w istocie bowiem obojętność polskich środowisk politycznych na wyzwania i problemy, przed którymi stoi Europa, jest - moim niezmiennym zdaniem - czynnikiem poważnie osłabiającym naszą pozycję jako państwa kandydującego. Podzielając wiele myśli, a także obaw wyrażonych w poważnym artykule Ryszarda Bugaja ("Chcieć - nie musieć", "Rz" z 27 marca 2001 r.), nie zgadzam się z jego sugestią, iż do Unii nie musimy się spieszyć. Bugaj zdaje się zakładać, że Polska może le...

34. `wikipedia_pl` Hélder Câmara (tokens=756, score=0.9424)

   Hélder Pessôa Câmara (ur. 7 lutego 1909 w Fortaleza, Ceará, zm. 27 sierpnia 1999 w Recife) – brazylijski biskup katolicki, jeden z czołowych przedstawicieli teologii wyzwolenia. Życiorys Hélder Pessôa Câmara urodził się w wielodzietnej rodzinie jako jedenaste dziecko. W roku 1923 wstąpił do seminarium duchownego, a w wieku 22 lat został przyjął święcenia kapłańskie. W roku 1952 otrzymał sakrę biskupią, został biskupem pomocniczym archidiecezji Rio de Janeiro, później biskupem Recife i Olindy w stanie Pernambuco (uważanych za najbiedniejsze części Brazylii). Zyskał sobie przydomek „czerwonego biskupa”. Uznał, że Marks w kulturze współczesnej osiągnął taką rangę, jak Arystoteles w czasach średniowiecza, przeto należy, podobnie jak to uczynił św. Tomasz z Arystotelesem, dostosować teorię Marksa do wymogów wiary chrześcijańskiej. Do historii przeszło jego powiedzenie: „Kiedy daję biednym chleb, nazywają mnie świętym. Kiedy pytam, dlaczego biedni nie mają chleba, nazywają mnie komunistą”...

35. `wolne_lektury` Australczyk (tokens=2237, score=0.9305)

   alej: — Człowiek goni marę, która mu się piękną wydaje, a gdy ją pochwyci, już jej nie chce, i gryzie się tem, że nie chce; czegoby zaś chciał, sam nie wie dobrze. Słuchała uważnie, potem z uśmiechem, który jednocześnie wytryskał na ustach i w oczach, odpowiedziała: — To jest rzeczywiście jakiś człowiek kapryśny. Nie znałam jeszcze takiego. — Poznajże teraz — z żartobliwym ukłonem rzekł Roman. Równie żartobliwie dygając, odrzekła: — Bardzo mi smutno. — Poznawać takiego człowieka? — Tak; bo jemu na świecie i światu z nim nie musi być wesoło. — O, o! dlaczegoż światu z nim? Cóż on biedny zawinił wobec świata? Pomyślała chwilę i, trochę wahając się, zcicha odpowiedziała: — Może to, że świat jest dla niego tylko dodatkiem… — Do czego? — Do niego samego. Roman był zadziwiony. — Masz na myśli samolubstwo, kuzynko? — Mniej więcej — zaśmiała się. To jest taka deklinacja: ja, moje, mnie, dla mnie, o mnie, przy mnie, we mnie… W tej chwili Bronia z pękiem kwiatów, które zrywała nad strumieniem...

36. `allegro_summaries_source` MAJĄTEK (tokens=3289, score=0.9641)

   MAJĄTEK Można by powiedzieć, że państwo jest warte 809 miliardów 358 milionów 885 tysięcy złotych brutto, ale jest kilka wątpliwości Za ile kupić Polskę RYS. ALICJA KRZĘTOWSKA PAWEŁ RESZKA Przed wojną polska policja celna miała 55 psów, które były warte 8 tysięcy 200 złotych. Natomiast żłoby, drabiny i konwie znajdujące się w oborze folwarku doświadczalnego Mochełek wyceniono na 1200 zł. Zamek Królewski był wart 21 milionów złotych, a Wawel niecałe 5 milionów. Skąd to wiadomo? Stąd, że przedwojenne Ministerstwo Skarbu zinwentaryzowało cały majątek narodowy. A co dziś możemy powiedzieć o majątku, który ma Polska? Najpierw jednak warto odpowiedzieć na inne pytanie. Po co w ogóle interesować się tym, ile warte jest państwo. Po pierwsze państwa przecież nikt nie będzie sprzedawał, a po drugie, trzeba to przyznać, konwie i drabiny nie mają przełomowego znaczenia dla "rozwoju gospodarki w skali makro". Przytoczmy dwie opinie fachowców: przedwojennego i współczesnego. Ignacy Hugo Matuszews...

37. `wolne_lektury` Tylko grajek (tokens=2121, score=0.9647)

   chałem do Fionii. Byłem szczęśliwy, jak dziecko! jakżem już opowiadał w myśli wszystkim znajomym o bitwie pod Bornhöwed, o marszu do Rosji, o wszystkim, com widział i wycierpiał. Ach! jakżem tęsknił za Maryą i za tobą! Doszedłszy do Örebäk, uczułem się jakoś głodnym i zmęczonym; chciałem więc wstąpić do bogatego brata owego gospodarza, w zastępstwie którego wstąpiłem do wojska, a spodziewałem się, że i on mi przecież coś powie, co tam słychać o mojej rodzinie w Swendborgu. Wszedłem tedy do izby, gdzie siedział sam gospodarz, kołysząc małe dziecię. — Dobry wieczór! — rzekłem, a on mnie spytał kto jestem. — Umarły! — odpowiedziałem, — ale skoro się przekonacie, że ma ciepłą krew i kości, zapewne się jego nie zlękniecie, — i opowiedziałem mu wszystko, skąd powstała fałszywa wieść o mojej śmierci. — Wielki Boże! — krzyknął tak dziwnym głosem, żem się aż sam przestraszył. — Czy moja żona nie żyje? — spytałem. Wówczas wziął mnie za rękę i zaklął na wszystko, żebym natychmiast dom jego, a...

38. `wikipedia_pl` Jan Palach (tokens=939, score=0.9773)

   Jan Palach (ur. 11 sierpnia 1948 w Pradze, zm. 19 stycznia 1969 tamże) – student historii i ekonomii politycznej na Wydziale Filozoficznym Uniwersytetu Karola w Pradze, który w proteście przeciwko agresji wojsk Układu Warszawskiego na Czechosłowację i powszechnej apatii czeskiego społeczeństwa 16 stycznia 1969 o godz. 16 dokonał aktu samospalenia przed Muzeum Narodowym na placu Wacława w Pradze. Śmierć i upamiętnienie Zmarł 3 dni później o 3:15 w wyniku odniesionych poparzeń (85% ciała) w specjalistycznej klinice oparzeniowej przy ulicy Legère’a. Rzeźbiarz Olbram Zoubek zdjął potajemnie jego maskę pośmiertną, której odlew zaniesiono następnego dnia na plac Wacława. 25 stycznia 1969 wielotysięczna procesja pogrzebowa na cmentarz Olszański przerodziła się w wielki protest przeciwko okupacji. Jej uczestnicy byli potem prześladowani przez tajną policję Státní bezpečnost (StB), która fotografowała i nagrywała jej przebieg. W październiku 1973 szczątki Palacha ekshumowano, skremowano i pr...

39. `wikipedia_pl` Tujon (tokens=519, score=0.9704)

   Tujon – organiczny związek chemiczny, związek terpenowy, występujący w olejku eterycznym m.in. piołunu (Artemisia absinthium), bylicy pospolitej (Artemisia vulgaris), wrotyczu pospolitego (Tanacetum vulgare), szałwii lekarskiej (Salvia officinalis), żywotnika zachodniego (Thuja occidentalis), a także w napoju alkoholowym z domieszką wyciągu z piołunu – absyncie i gorzkiej ziołowej wódce zwanej piołunówką. Tujon jest łatwo rozpuszczalny w alkoholach i eterze dietylowym. Nie rozpuszcza się natomiast w wodzie. Wywołuje w większych dawkach wzmożoną czynność kory mózgowej z niepokojem ruchowym i dużą drażliwością. W zatruciach pojawiają się stany podniecenia i psychozy. Spośród narządów zmianom zwyrodnieniowym ulega przede wszystkim układ nerwowy. Działanie farmakologiczne związane jest prawdopodobnie z interakcjami z receptorem GABA. Podejrzenia o zatrucia tujonem były dość częstym zjawiskiem, zwłaszcza we Francji, gdzie używano w dużej ilości napojów zawierające olejek eteryczny, skład...

40. `allegro_summaries_source` ROZMOWA (tokens=2097, score=0.9706)

   ROZMOWA Zbigniew Boniek, kandydat na prezesa Polskiego Związku Piłki Nożnej Nikomu nic nie obiecałem BARTŁOMIEJ ZBOROWSKI Czy ktoś, kto reklamuje piwo, może być prezesem PZPN? ZBIGNIEW BONIEK: Dlaczego nie? Mam długoletni kontrakt z kompanią piwowarską z Poznania. Zgodnie z hasłem: "Po godzinach, po pracy" napić się dobrego piwa to przyjemność. Jedno dobre piwo jest lepsze od wielu innych napojów, które piją dzieci i o których teraz tak głośno jest w Europie. Nie widzę żadnego związku między tym, że kandyduję na stanowisko prezesa PZPN, i reklamowaniem przeze mnie piwa. Jeśli zostanę prezesem, to może coś się w tym układzie zmieni, choć nie sądzę. Czy kandydat na prezesa PZPN może zajmować się sprzedażą zawodników za granicę? To całkowita nieprawda, wiadomość wyssana z palca. Pewnie chodzi o plotki związane z Arturem Wichniarkiem z Widzewa. Kilka razy rozmawiałem z Arturem Zgłosił się do mnie jeden menedżer z Włoch z pytaniem, jak mógłby się spotkać z Wichniarkiem. Spotkali się. To...

41. `wikipedia_pl` Janusz Rewiński (tokens=1394, score=0.947)

   Janusz Rewiński (ur. 16 września 1949 w Żarach) – polski aktor, satyryk i polityk, poseł na Sejm I kadencji. Życiorys Rodzina i wykształcenie Urodził się w rodzinie pochodzącej z okolic Równego na Wołyniu. Ukończył Technikum Budowy Silników Lotniczych we Wrocławiu, następnie w 1972 studia na Wydziale Aktorskim PWST w Krakowie. Działalność artystyczna Podczas studiów występował w prowadzonych przez Wiesława Dymnego Spotkaniach z Balladą oraz w Piwnicy Pod Baranami (wtedy powstał monolog Fiut rozszyfrowywany jako Film i uwentualnie telewizja). Był aktorem Teatru Polskiego w Poznaniu, w którym występował w roli Wacława oraz Papkina w Zemście Aleksandra Fredry. Po udanym debiucie w Poznaniu przez kilka lat wraz z Zenonem Laskowikiem występował w kabarecie Tey. W latach 80. pojawił się m.in. w duecie z Bohdanem Smoleniem. Popularność przyniosły mu występy w Kabarecie Olgi Lipińskiej, w którym wcielił się w rolę „Miśka”, gruboskórnego dyrektora teatru. Wystąpił w licznych filmach, m.in. w...

42. `wikipedia_pl` Maria Jarema (tokens=1373, score=0.9654)

   Maria Jarema, wzgl. Maria Jaremianka (ur. 24 listopada 1908 w Starym Samborze, zm. 1 listopada 1958 w Krakowie) – polska malarka, rzeźbiarka i scenografka. Życiorys Była córką prawnika i adwokata Józefa Jaremy i absolwentki konserwatorium muzycznego Stefanii ze Śmigielskich. Po ukończeniu szkoły powszechnej uczęszczała do Prywatnego Gimnazjum Żeńskiego im. Marii Konopnickiej w Samborze. Egzamin maturalny zdała w 1928 roku, po czym w latach 1929–1935 studiowała rzeźbę w Akademii Sztuk Pięknych w Krakowie, w pracowni Xawerego Dunikowskiego. Była współzałożycielką awangardowej i radykalnie lewicowej Grupy Krakowskiej (1930) . W 1937 roku za swoje poglądy i pracę kolporterską w Międzynarodowej Organizacji Pomocy Rewolucjonistom (MOPR) była represjonowana. Współpracowała z teatrem eksperymentalnym Cricot jako scenografka i projektantka kostiumów oraz teatrzykiem kukiełkowym Jana Polewki, który tworzył szopki polityczne w środowisku robotników. W czasie okupacji hitlerowskiej działała w t...

43. `wikipedia_pl` Frouzins (tokens=86, score=0.9635)

   Frouzins – miejscowość i gmina we Francji, w regionie Oksytania, w departamencie Górna Garonna. Według danych na rok 1990 gminę zamieszkiwało 3941 osób, a gęstość zaludnienia wynosiła 498 osób/km² (wśród 3020 gmin regionu Midi-Pireneje Frouzins plasuje się na 78. miejscu pod względem liczby ludności, natomiast pod względem powierzchni na miejscu 1252.).

44. `allegro_summaries_source` ROZMOWA (tokens=4378, score=0.9692)

   ROZMOWA Ryszard Kapuściński, reporter i podróżnik, o sytuacji w Zairze i w innych państwach Afryki Laboratorium polityczne Czy wydarzenia rozgrywające się w Zairze rzeczywiście są takie ważne? Nagle Afryka jest znowu na pierwszych stronach gazet, wszyscy analizują sytuację... RYSZARD KAPUŚCIŃSKI: Niewątpliwie tak. Jest to ważne wydarzenie z kilku względów. Konflikt w Zairze jest dziś jednym z największych na naszej planecie. Ale jeśli chodzi o samą Afrykę, jest to wyraźne zakończenie epoki zimnej wojny. Okres zimnej wojny na tym kontynencie przebiegał bardzo dramatycznie. Dziś to, co sobie wówczas wyobrażano, wydaje się dziwne. Ale w okresie dekolonizacji, walki o niepodległość, nie znając dobrze Afryki, zakładano, że procesy tam zachodzące mogą stać się zalążkiem wielkiego konfliktu między mocarstwami, że może wybuchnąć tam trzecia wojna światowa. Pamiętam, że kiedy w 1960 roku po raz pierwszy jechałem do Konga (dziś Zairu), w ówczesnej prasie światowej pisano o wielkim niebezpiecz...

45. `allegro_summaries_source` BANKI (tokens=2189, score=0.9727)

   BANKI Czy pozostaną banki z krajowym kapitałem Kłopoty z polskimi akcjonariuszami RYS. ANDRZEJ JACYSZYN W ostatnich tygodniach w poważne kłopoty popadły dwa niewielkie banki. Powodem nie była jednak ich zła kondycja finansowa, lecz nieporozumienia pomiędzy akcjonariuszami. Banki te poza tym miały wspólną cechę - były kontrolowane przez krajowy kapitał. Jest coraz więcej przykładów na to, że w polskim sektorze bankowym udział narodowego kapitału zmniejsza się nie dlatego, że go brakuje, ale że jego przedstawiciele nie są w stanie się porozumieć albo nie potrafią ocenić sytuacji kontrolowanych przez siebie instytucji. W zeszłym roku, głównie w wyniku strategii prywatyzacyjnej Ministerstwa Skarbu Państwa, zagraniczny kapitał przejął kontrolę nad kilkoma dużymi bankami. W tym roku nastąpił dalszy etap tego procesu. Dzięki zaostrzeniu wymagań NBP oraz rosnącej konkurencji kilka mniejszych instytucji bankowych przejmują wkrótce zagraniczni inwestorzy. Można szacować, że liczba prywatnych...

46. `wolne_lektury` Tylko grajek (tokens=2209, score=0.9663)

   ły pienia zakonników, gdyby mogli z zachodem słońca powstać z trumien i pobujać nad łąką, uwierzyliby że w Danii wszystko tak samo jak wówczas, gdy zamknęli na zawsze swoje oczy. Poczciwy lud z tą samą jeszcze pobożną wiarą w sercu tłoczył się naokoło świętego źródła, dzwony kościelne przy zachodzie słońca biły jak dawniej, kiedy wzywały jeszcze wiernych do Pozdrowienia Anielskiego, w wiejskim kościółku tak samo uśmiechał się jeszcze obraz Matki Boskiej z Dziecięciem. Nawet sąsiedni dwór szlachecki, starożytny Örbäk, niezmieniony stał jeszcze ze swymi śpiczastymi szczytami i z wysoką wieżą, całkiem odwieczny ów budynek gotycki! Niedaleko od miejsca gdzie matka kąpała Krystiana w świeżej, zimnej wodzie, stały dwie kobiety z młodą, może trzynastoletnią dziewczyną, nie mającą na sobie śladu żadnej ani ułomności ciała, ani choroby wewnętrznej. Twarz jej miała wszystkie cechy najsilniejszego zdrowia; postać jej była prawie zupełnie rozwiniętą; długie, gęste włosy spływały na białe, pełne...

47. `allegro_summaries_source` Kościół i twórcy (tokens=4951, score=0.9571)

   Kościół i twórcy Czas wspólny i czas osobny RYS. JANUSZ KAPUSTA KATARZYNA KOŁODZIEJCZYK Mieliśmy spotkanie w wieży przy warszawskim kościele św. Anny na Krakowskim Przedmieściu, u księdza Wiesława Niewęgłowskiego. Zaledwie kilka osób. Był wczesny okres jaruzelskiej wojny. Nieoczekiwanie odezwał się dzwonek domofonu. Po chwili nasze obawy rozproszył Wiktor Woroszylski, który zjawił się niespodziewanie. Prosto z miejsca internowania. To nie przypadek sprawił, że zwolniony z interny poeta skierował swe kroki najpierw do księdza. Tak, jak nie było przypadkiem to, że zaledwie kilka godzin po wprowadzeniu stanu wojennego twórcy polskiej kultury udali się do świątyń i znaleźli oparcie w Kościele. W Teatrze Dramatycznym trwały obrady niezależnego Kongresu Kultury Polskiej. Intelektualiści publicznie przełamywali państwowy, PRL-owski monopol w dziedzinie "nadbudowy". Już przeszło rok krzepiące słowo "Solidarność" dodawało odwagi, otwierało nowe możliwości i powoli docierało do najbardziej od...

48. `allegro_summaries_source` ROZMOWA (tokens=2311, score=0.9431)

   ROZMOWA Joram Bronowski, izraelski krytyk: Teatr był źle widziany przez Żydów. Uznawano go za przejaw obcej tradycji Greków Biblia nie uznaje tragedii Habima była uważana za teatr diasporowy FOT. HABIMA Jaka jest obecnie kondycja teatru w Izraelu? JORAM BRONOWSKI: Jak zawsze, kryzysowa. Coraz mniej Izraelczyków mówi po hebrajsku. Duża część imigrantów, w tym milionowa rzesza przybyła z byłego Związku Radzieckiego, patrzy na tutejsze dziedzictwo z góry. Utworzony na przedmieściach Tel Awiwu, w Jaffie, przez moskiewskich aktorów Teatr Geszer, czyli Most, wystawia sztuki głównie po rosyjsku. Starają się nauczyć hebrajskiego, ale robią to z niechęcią, z obowiązku. Ostatnio wystawili adaptację "Opowiadań odeskich" Babla. Połączyli w ten sposób tradycję rosyjską i żydowską. Grają też "Zmierzch" Babla, także klasykę, którą ceniono w sowieckich teatrach - Czechowa, Moliera i Szekspira. Grają w bardzo pięknej sali, a poza zyskami z kasy otrzymują też państwowe dotacje. Tak jak wszystkie teat...

49. `wikipedia_pl` Laurence Harbor (New Jersey) (tokens=101, score=0.8709)

   Laurence Harbor - jednostka osadnicza w hrabstwie Middlesex w stanie New Jersey w USA. Miejscowość należy do konglomeracji Old Bridge Township. Liczba ludności (2000) - ok. 6,2 tys. Powierzchnia – 7,5 km², z czego 7,3 km² to powierzchnia lądowa, a 0,2 km² wodna Położenie - 40°27'3" N i 74°14'44" W CDP w stanie New Jersey

50. `wikipedia_pl` Okręg Gramsh (tokens=136, score=0.9439)

   Okręg Gramsh (alb. rrethi i Gramshit) – jeden z trzydziestu sześciu okręgów administracyjnych w Albanii; leży w środkowej części kraju, w obwodzie Elbasan. Liczy ok. 25 tys. osób (2008) i zajmuje powierzchnię 695 km². Jego stolicą jest Gramsh. W skład okręgu wchodzi dziesięć gmin: jedna miejska Gramsh oraz dziewięć wiejskich Kodovjat, Kukur, Kushovë, Pishaj, Poroçan, Shënepremte, Skënderbegas, Sult, Tunjë.
