# Glyph-100M Dataset Report

Generated: 2026-05-26 05:28:33 UTC

## Recommendation

Dataset split is acceptable for a 1k-step Glyph-100M sanity run; process the full corpus before long stages.

## Inputs

- dataset name: `glyph100_stage1_candidate`
- input corpus: `data/raw/corpus.txt`
- tokenizer: `data/processed/tokenizer.model`
- tokenizer vocab size: 16,000
- context length target: 512
- processing mode: {'max_docs': 1200000, 'max_accepted_docs': 250000, 'min_words': 20, 'max_chars': 50000, 'val_per_mille': 10}

## Source Notes

The current legacy corpus does not preserve per-document source metadata, so
the split uses approximate source labels inferred from document shape and
known corpus construction. This split is a stage-1 sanity candidate, not the
final cleaner corpus for 10k+ / 50k+ training. Future Glyph-100M data should
preserve source IDs.

| Source | Type | Decision | Risk / note |
|---|---|---|---|
| Polish Wikipedia | encyclopedic articles | use | High-density Polish encyclopedic prose; good base material for a small model. |
| Wolne Lektury | public-domain / freely licensed literary texts | use_with_boilerplate_filter | Long-form Polish literary text is valuable, but project/license boilerplate must be filtered. |
| mC4 / OSCAR PL | web crawl text | use_filtered_only | Adds breadth, but was the main risk for web/forum/SEO garbage in Glyph-27M. |

## Counts

- documents seen: 289,973
- documents accepted: 250,000
- documents rejected: 39,973
- acceptance rate: 86.21%
- train documents: 247,439
- val documents: 2,561
- train tokens: 117,870,679
- val tokens: 1,239,948
- total tokens: 119,110,627
- word/token ratio: 0.495
- token/word ratio: 2.020

## Document Lengths After Tokenization

- p50: 189
- p75: 553
- p90: 1222
- p95: 1878
- p99: 3643
- max: 8,408
- docs <= context 512: 183,041 (73.22%)

## Approximate Source Mix

{
  "legacy_mixed_paragraph_like": 219331,
  "legacy_long_article_like": 30669
}

## Top Rejection Reasons

{
  "repeated_ngrams": 20969,
  "single_word_repetition": 8191,
  "too_short": 7134,
  "boilerplate_phrase": 5458,
  "very_long_line": 4297,
  "too_long": 1017,
  "too_many_urls": 811,
  "low_unique_word_ratio": 773,
  "low_alpha_ratio": 139,
  "too_much_punctuation_or_symbols": 18,
  "low_polish_signal": 12,
  "near_duplicate_prefix": 10
}

## Suspicious Pattern Counts

{}

## Accepted Samples

1. source=legacy_long_article_like

   AWK – interpretowany język programowania, którego główną funkcją jest wyszukiwanie i przetwarzanie wzorców w plikach lub strumieniach danych. Jest także nazwą programu początkowo dostępnego dla systemów operacyjnych będących pochodnymi UNIX-a, obecnie także na inne platformy. AWK jest językiem, który w znacznym stopniu wykorzystuje tablice asocjacyjne, stringi i wyrażenia regularne. Nazwa języka pochodzi od pierwszych liter nazwisk jego autorów Alfreda V. Aho, Petera Weinbergera i Briana Kernighana. Bywa zapisywana małymi literami, odczytywana jako jedno słowo awk, wymawiana jak pierwsza sylaba w awkward. Definicja języka AWK jest zawarta w POSIX 1003.2 Command Language And Utilities Stan...

2. source=legacy_mixed_paragraph_like

   Alergologia – dziedzina medycyny zajmująca się rozpoznawaniem i leczeniem schorzeń alergicznych, czyli takich, u podstaw których stoi zjawisko nadwrażliwości, zwłaszcza inicjowane przez mechanizmy immunologiczne. W Polsce konsultantem krajowym alergologii od 19 lutego 2020 jest prof. dr hab. Karina Jahnz-Różyk. Przypisy Linki zewnętrzne Polskie Towarzystwo Alergologiczne Polskie Towarzystwo Zwalczania Chorób Alergicznych Specjalności lekarskie

3. source=legacy_long_article_like

   ASCII (czyt. aski, skrót od ang. American Standard Code for Information Interchange) – siedmiobitowy system kodowania znaków, używany we współczesnych komputerach oraz sieciach komputerowych, a także innych urządzeniach wyposażonych w mikroprocesor. Przyporządkowuje liczbom z zakresu 0−127: litery alfabetu łacińskiego języka angielskiego, cyfry, znaki przestankowe i inne symbole oraz polecenia sterujące. Na przykład litera „a” jest kodowana jako liczba 97, a znak spacji jest kodowany jako 32. Większość współczesnych systemów kodowania znaków jest rozszerzeniem standardu ASCII. ASCII jest tradycyjną nazwą tego zestawu znaków, jednak IANA zaleca używanie określenia US-ASCII, które podkreśla...

4. source=legacy_long_article_like

   Aksjomat, postulat, pewnik (gr. axíōma, godność, pewność, oczywistość) – jedno z podstawowych pojęć logiki matematycznej. Od czasów Euklidesa uznawano, że aksjomaty to zdania przyjmowane za prawdziwe, których nie dowodzi się w obrębie danej teorii matematycznej. We współczesnej matematyce definicja aksjomatu jest nieco inna: Aksjomaty są zdaniami wyodrębnionymi spośród wszystkich twierdzeń danej teorii, wybranymi tak, aby wynikały z nich wszystkie pozostałe twierdzenia tej teorii. Taki układ aksjomatów nazywany jest aksjomatyką. Zbiór aksjomatów i ich konsekwencji to system aksjomatyczny. Wyjaśnienie pojęcia aksjomatu Matematyka jest zbiorem różnych teorii (geometria euklidesowa, arytmety...

5. source=legacy_long_article_like

   Arytmetyka (łac. arithmetica, gr. ἀριθμητική arithmētikē, z ἀριθμός – liczba) – dział matematyki zajmujący się liczbami; jeden z podstawowych i najstarszych. Obejmuje co najmniej dwa obszary wiedzy: arytmetyka elementarna opisuje podstawowe działania na liczbach, zwłaszcza tych rzeczywistych, choć mówi się także o arytmetyce liczb kardynalnych czy porządkowych; działania uznawane za arytmetyczne to dodawanie, odejmowanie, mnożenie i dzielenie, a czasem też potęgowanie, pierwiastkowanie i logarytmy; arytmetyka teoretyczna to inaczej teoria liczb; bada ich własności i w mniejszym stopniu dotyczy obliczeń, choć zajmuje się też niektórymi algorytmami jak sprawdzanie pierwszości czy faktoryzac...

6. source=legacy_mixed_paragraph_like

   Alkeny – organiczne związki chemiczne z grupy węglowodorów nienasyconych, w których występuje jedno podwójne wiązanie chemiczne między atomami węgla (). Razem ze związkami, które posiadają dwa lub więcej wiązań podwójnych (polienami, takimi jak dieny, trieny itd.) oraz z analogami pierścieniowymi (cykloalkenami i cyklopolienami) tworzą grupę olefin. Mają więcej izomerów i są bardziej aktywne niż alkany. Wraz ze zwiększającą się długością łańcucha węglowego maleje ich reaktywność. Można je otrzymać z ropy naftowej, a w laboratorium w reakcji eliminacji fluorowca z halogenków alkilowych lub przez alkoholi. Ich wzór ogólny to . Nazewnictwo Nazwy alkenów są tworzone z nazw odpowiednich alkanó...

7. source=legacy_mixed_paragraph_like

   ActiveX – przestarzała biblioteka komponentów i kontrolek stworzona przez Microsoft. ActiveX mógł służyć do wymiany danych pomiędzy różnymi aplikacjami działającymi pod kontrolą systemów operacyjnych Windows. W szczególności był wykorzystywany w przeglądarce Internet Explorer do wywoływania różnych funkcji systemowych (np. do wsparcia AJAX). Wsparcie dla ActiveX zostało wycofane w 2015 w przeglądarce Microsoft Edge. ActiveX wywodzi się z wcześniejszych technologii Microsoftu – OLE i COM. ActiveX jest zaprojektowana jako technologia modularna. Z technologicznego punktu widzenia, kontrolki ActiveX są podzbiorem komponentów typu COM. Kontrolki ActiveX mają swój początek w komponentach VBX, n...

8. source=legacy_mixed_paragraph_like

   Interfejs programowania aplikacji, interfejs programistyczny aplikacji, interfejs programu aplikacyjnego (ang. application programming interface, API) – zbiór reguł ściśle opisujący, w jaki sposób programy lub podprogramy komunikują się ze sobą. API jest przede wszystkim specyfikacją wytycznych, jak powinna przebiegać interakcja między komponentami programowymi. Implementacja API jest zestawem rutyn, protokołów i rozwiązań informatycznych do budowy aplikacji komputerowych. Dodatkowo API może korzystać z komponentów graficznego interfejsu użytkownika. Dobre API ułatwia budowę oprogramowania, sprowadzając ją do łączenia przez programistę bloków elementów w ustalonej konwencji. Definiuje się...

9. source=legacy_long_article_like

   AmigaOS – system operacyjny opracowany przez firmę Commodore International dla produkowanych przez nią komputerów Amiga. Wersja 1.0 została wydana w 1985 roku, wraz z premierą komputera Amiga 1000. Charakterystyka System od początku 32-bitowy, napisany został dla procesora Motorola 68000. Obsługiwane procesory to: MC68000, MC68010, MC68020, MC68030, MC68040, MC68060. Systemy w wersjach 3.x obsługują również procesory PowerPC znane także jako PPC, dzięki podsystemom WarpOS albo PowerUP. System pracuje nadal na M68x00, istnieje jednak możliwość uruchamiania programów napisanych dla PPC. Konstrukcja i oprogramowanie kart procesorowych umożliwia jednoczesną pracę obu procesorów, przy czym PPC...

10. source=legacy_mixed_paragraph_like

   Alternatywa, suma logiczna, alternatywa zwykła, alternatywa nierozłączna, alternatywa łączna – zdanie logiczne o postaci p lub q, gdzie p, q są zdaniami. W logice matematycznej alternatywę zapisuje się Alternatywa p lub q jest zdaniem prawdziwym, gdy co najmniej jedno z jej zdań składowych p, q jest prawdziwe. W logice matematycznej Alternatywa (suma logiczna): Działanie dwuargumentowe określone w dowolnym zbiorze zdań bądź w zbiorze funkcji zdaniowych, które zdaniom (funkcjom zdaniowym) i przypisuje zdanie (funkcję zdaniową) prawdziwe wtedy i tylko wtedy, gdy prawdziwe jest przynajmniej jedno ze zdań (funkcji) i Dwuargumentowy spójnik zdaniowy, oznaczany (łac. ) o znaczeniu odpowiadające...

11. source=legacy_mixed_paragraph_like

   Aksjomat indukcji – aksjomat, a właściwie nieskończony przeliczalny zbiór aksjomatów pierwszego rzędu, pozalogicznych rozważany zwłaszcza w teorii arytmetyki liczb naturalnych. Jest on formalizacją zasady indukcji matematycznej. Jego treść przedstawia się następująco: gdzie oznacza: „dla każdego n” ⇒, to wynikanie (implikacja) oznacza „i”. Tak wyrażony aksjomat indukcji nie spełnia jednak założeń rozlicznych podejść, a w tym np. analizy Gödla niesprzeczności teorii matematycznych w szczególności arytmetyki. Problemem jest zupełna nieobliczalność relacji użytych do konstrukcji powyższego zdania: kwantyfikator ogólny „dla każdego n” nie da się bowiem zapisać jako funkcja obliczalna. Ponadto...

12. source=legacy_mixed_paragraph_like

   Alleny – organiczne związki chemiczne, węglowodory nienasycone, w których jeden z atomów węgla jest związany z dwoma innymi atomami węgla wiązaniami podwójnymi (tzw. układ ). Zwyczajowo allenem określa się najprostszy związek z tej grupy, czyli . Skumulowanie dwóch podwójnych wiązań chemicznych obok siebie powoduje, że alleny są dużo bardziej reaktywne od innych alkenów. Ich reaktywność, między innymi w reakcji z gazowym chlorem, jest bardziej zbliżona do reaktywności alkinów niż alkenów. Alleny są związkami nietrwałymi i ulegają reakcji przekształcenia w odpowiedni izomer alkinowy, na przykład: CH2=C=CH2 → CH3-C≡CH Zobacz też karbodiimidy Polieny

13. source=legacy_mixed_paragraph_like

   Alkiny (zwyczajowo: acetyleny) – grupa organicznych związków chemicznych będących węglowodorami nienasyconymi, w których występuje jedno wiązanie potrójne między atomami węgla (). Najprostszym alkinem jest etyn, zwykle zwany acetylenem, . Alkiny są bardziej reaktywne od alkanów i alkenów, są nietrwałe i podlegają wielu samorzutnym reakcjom. Ogólny wzór alkinów: . Alkiny, tak jak wszystkie węglowodory, ulegają reakcjom spalania. Nazewnictwo Nazwy alkinów są tworzone z nazw odpowiednich alkanów. Z nazwy alkanu mającego ten sam szkielet węglowy usuwa się końcówkę „-an” i dodaje końcówkę „-yn” (lub „-in” po spółgłoskach ch, f, g, k, l), a przed nią umieszcza się lokant wskazujący, przy którym...

14. source=legacy_long_article_like

   Alkany (parafiny, z = mało powinowaty) – łańcuchowe węglowodory nasycone, organiczne związki chemiczne zbudowane wyłącznie z atomów węgla i wodoru, przy czym atomy węgla połączone są ze sobą wyłącznie wiązaniami pojedynczymi. Ogólny wzór sumaryczny alkanów ma postać . Według obowiązującej systematyki IUPAC węglowe łańcuchy atomów w cząsteczkach alkanów mogą być zarówno proste, jak i rozgałęzione, jednak nie mogą tworzyć pierścieni ani zamkniętych pętli – cykloalkany nie są zatem alkanami. Grupa alkanów uszeregowana według długości łańcuchów węglowych stanowi szereg homologiczny alkanów. Dalsze elementy tego szeregu określane są jako wyższe alkany (według różnych kryteriów jako wyższe alka...

15. source=legacy_long_article_like

   Alkohole – związki organiczne zawierające jedną lub więcej grup hydroksylowych połączonych z atomem węgla o hybrydyzacji sp3. Najprostsze i najczęściej spotykane w życiu codziennym alkohole, to pochodne alkanów zawierające jedną grupę hydroksylową w cząsteczce, o wzorze ogólnym CnH2n+1OH, czyli alkohole monohydroksylowe, na przykład metylowy, etylowy, propylowy. Analogiczne związki organiczne, w których grupa hydroksylowa połączona jest z atomem węgla o hybrydyzacji sp2, to fenole (hydroksylowe pochodne benzenu i innych związków aromatycznych) lub enole (hydroksylowe pochodne alkenów). Właściwości fizyczne Ze względu na obecność silnie elektroujemnego atomu tlenu i związanego z nim atomu...

16. source=legacy_mixed_paragraph_like

   Anarchia ( – "bez władcy") – forma struktury społeczno-politycznej, w której nie ma żadnej ukonstytuowanej władzy, nie obowiązują żadne normy prawne. W rozumieniu politycznym (w anarchizmie) to taka struktura, w której państwo zostaje zastąpione przez nieprzymusową i niescentralizowaną organizację społeczeństwa (np. federację autonomicznych miejscowości). W rozumieniu potocznym anarchia to pojęcie określające: rozkład lub niedowład struktur lub instytucji państwa niezależnie od ich przyczyn; chaos organizacyjny w instytucji, organizacji lub społeczności. Zobacz też Anarchizm Przypisy

17. source=legacy_mixed_paragraph_like

   ASN.1 (skrót od Abstract Syntax Notation One – abstrakcyjna notacja składniowa numer jeden) – standard ITU-T służący do opisu struktur przeznaczonych do reprezentacji, kodowania, transmisji i dekodowania danych. Dostarcza zbiór formalnych zasad pozwalających na opis struktur obiektów w sposób niezależny od konkretnych rozwiązań sprzętowych. Jest to standard ITU-T/ISO, po raz pierwszy został opisany w roku 1984 jako część dokumentu CCITT X.409'84. Następnie w 1988 wydano go jako samodzielny dokument ITU-T X.208. W roku 1994 wydano jego nową wersję w dokumentach ITU-T z serii X.680 (X.680-X.683). W roku 2002 wycofano dokument ITU-T X.208. Standard ASN.1 określa jedynie składnię abstrakcyjną...

18. source=legacy_mixed_paragraph_like

   Przylądek Igielny, Przylądek Agulhas (port. Cabo das Agulhas, wym. []) – przylądek stanowiący najbardziej wysunięty na południe kraniec Afryki. Przebiegający przez niego południk uznawany jest za umowną granicę dwóch oceanów: Indyjskiego i Atlantyckiego. Nazwa Przylądka Igielnego w języku portugalskim, Agulhas, dosłownie oznaczająca „igły”, prawdopodobnie odnosi się do poszarpanych skał, o które rozbijały się statki, lub do zerowej deklinacji magnetycznej w tym rejonie na przełomie XV i XVI w., dzięki czemu igła kompasu wskazywała dokładnie kierunek północy geograficznej. W 1849 na przylądku zbudowano latarnię morską. Przypisy Linki zewnętrzne Zdjęcie satelitarne południowego końca Afryki...

19. source=legacy_mixed_paragraph_like

   Aldehydy ( = „alkohol odwodorniony”) – klasa organicznych związków chemicznych posiadających grupę aldehydową, czyli grupę karbonylową () połączoną z jednym () lub dwoma () atomami wodoru. Proste aldehydy, będące pochodnymi alkanów i zawierające w cząsteczce jedną grupę aldehydową to alkanale o wzorze ogólnym . Pokrewną klasę związków stanowią ketony (), nieposiadające atomu wodoru przy grupie karbonylowej. Ketony i aldehydy mają zbliżone właściwości chemiczne, przy czym aldehydy są z reguły bardziej reaktywne. Istnieje też szereg reakcji charakterystycznych jedynie dla aldehydów. Otrzymywanie Aldehydy otrzymuje się w przemyśle przez katalityczne odwodornienie pierwszorzędowych alkoholi:...

20. source=legacy_long_article_like

   Agatha Christie, lady Mallowan, DBE, właśc. Agatha Mary Clarissa Miller Christie (ur. 15 września 1890 w Torquay, zm. 12 stycznia 1976 w Wallingford) – brytyjska autorka powieści kryminalnych i obyczajowych. Najbardziej znana na świecie pisarka kryminałów oraz najlepiej sprzedająca się autorka wszech czasów. Wydano ponad miliard egzemplarzy jej książek w języku angielskim oraz drugi miliard przetłumaczonych na 45 języków obcych. Pod pseudonimem Mary Westmacott wydała kilka powieści obyczajowych, które również cieszyły się popularnością. Christie wydała ponad 90 powieści i sztuk teatralnych. Ich akcja toczyła się głównie w zamkniętych pomieszczeniach, a mordercą mógł być tylko jeden z mies...

21. source=legacy_mixed_paragraph_like

   Allel – jedna z wersji genu. Allel najczęściej występuje w określonym locus na danym chromosomie homologicznym, jednak pojęcie to odnosi się także do genomu cytoplazmatycznego oraz prokariotycznego. Allele tego samego genu różnią się jednym lub kilkoma nukleotydami. Istnienie więcej niż jednej wersji danego genu określa się jako polimorfizm. Dzięki zdegenerowaniu kodu genetycznego tylko część tych różnic przekłada się na różnice w budowie kodowanych białek. Powoduje to zróżnicowanie właściwości cząsteczek białka kodowanego przez różne allele tego samego genu. Model Mendla W uproszczonym modelu genetyki mendlowskiej przyjmuje się, że allele mogą być dominujące (oznaczane zwyczajowo wielką...

22. source=legacy_long_article_like

   Anatole France, właśc. Jacques-Anatole-François Thibault (ur. 16 kwietnia 1844 w Paryżu, zm. 12 października 1924 w Saint-Cyr-sur-Loire) – poeta, powieściopisarz i krytyk francuski. Zapalony bibliofil i historyk, przedstawiciel postawy racjonalistycznej oraz sceptycznej. Przez jemu współczesnych porównywany do Voltaire’a i Jean Baptiste Racine’a. Jako poeta – przedstawiciel parnasizmu. Autor licznych powieści satyryczno-heroikomicznych wzorowanych na XVII-wiecznych powiastkach filozoficznych i libertyńskich. W swojej twórczości, zarówno literackiej, jak i eseistycznej, głośno krytykował konwenanse religijno-obyczajowo-społeczne we Francji przełomu XIX i XX wieku. Laureat Literackiej Nagro...

23. source=legacy_long_article_like

   Alkaloidy (arabskie alkali – potaż i eidos – postać = „przyjmujący postać zasady”) – według rekomendacji IUPAC z 1995 roku jest to grupa naturalnie występujących zasadowych związków organicznych (na ogół heterocyklicznych), głównie pochodzenia roślinnego, zawierających azot. Aminokwasy, peptydy, białka, nukleotydy, kwasy nukleinowe, aminocukry i antybiotyki nie są zwykle zaliczane do alkaloidów. Dodatkowo do tej grupy włączone są niektóre obojętne związki chemiczne biogenetycznie związane z alkaloidami zasadowymi. Prekursorami do biosyntezy tych związków chemicznych są aminokwasy. Alkaloidy wykazują zwykle silne, nieraz trujące działanie fizjologiczne na organizm człowieka. Dla chemii org...

24. source=legacy_long_article_like

   Archeologia (z gr. ἀρχαῖος archaīos – dawny, stary i -λογία -logiā – mowa, nauka) – nauka, której celem jest odtwarzanie społeczno-kulturowej przeszłości człowieka na podstawie znajdujących się w ziemi, na ziemi lub w wodzie źródeł archeologicznych, czyli materialnych pozostałości działań ludzkich. Źródła archeologiczne Źródła archeologiczne obejmują wytwory ręki ludzkiej (artefakty), ślady wpływu człowieka na środowisko naturalne (ekofakty), jak też i szczątki samych ludzi. Źródła archeologiczne można podzielić na: nieruchome (obiekty); do kategorii archeologicznych źródeł nieruchomych należą np. pozostałości budowli, groby, starożytne drogi czy ślady orki. ruchome (przedmioty); do tej k...

25. source=legacy_long_article_like

   Andrespol – wieś w Polsce, położona w województwie łódzkim, w powiecie łódzkim wschodnim, siedziba gminy Andrespol. Historia Do roku 1809 tereny sołectw obecnej gminy Andrespol (oprócz Kraszewa i Zielonej Góry) oraz łódzkiej dzielnicy Andrzejów nosiły nazwę Bedoń. Pierwsza wzmianka o Bedoniu pochodzi z roku 1391, z łęczyckiej księgi grodzkiej. Bedoń był wsią szlachecką i graniczył z Karpinem, Wiączyniem Polnym, Wiączyniem Leśnym, Mileszkami, Kraszewem i Gałkowem. Znajdował się w zaborze rosyjskim. Powstanie Andrespola W drugiej połowie XVIII wieku na ziemie łódzką sprowadzani byli koloniści z Wielkopolski i Niemiec. Jedną z pierwszych osad rolniczych utworzonych poprzez prawo olęderskie b...

26. source=legacy_long_article_like

   Andrzejewo – wieś w Polsce położona w województwie mazowieckim, w powiecie ostrowskim, w gminie Andrzejewo. Dawniej miasto. Do 1954 roku siedziba gminy Warchoły. W latach 1975–1998 miejscowość administracyjnie należała do województwa łomżyńskiego. Miejscowość jest siedzibą władz gminy Andrzejewo oraz parafii rzymskokatolickiej Wniebowzięcia NMP. Sołectwo Andrzejewo obejmuje: Andrzejewo, i Jabłonowo-Klacze Historia Miejscowość jako wieś wymieniona została w I połowie XIII wieku w inwentarzu dóbr biskupstwa płockiego. Pierwotnie nazwana Wronie. Położona nad rzeką Brok Mały, na połączeniu szlaków z Łomży i Pułtuska na Podlasie. Andrzejewo uzyskało lokację miejską w 1528 roku. Powstało na gru...

27. source=legacy_long_article_like

   Aminy – organiczne związki chemiczne zawierające w swojej budowie grupę aminową, będącą organiczną pochodną amoniaku. Rzędowość amin Rzędowość amin wyznacza się tak samo jak rzędowość atomów węgla. Jest więc równa liczbie atomów wodoru przy atomie azotu zastąpionych atomami węgla. Stąd aminy dzielą się na pierwszorzędowe (), drugorzędowe (), trzeciorzędowe (); ponadto znane są czwartorzędowe związki (sole, kationy) amoniowe (), które charakteryzują się obecnością ładunku dodatniego i należą do grupy tzw. związków oniowych. Aminy o dużych masach cząsteczkowych, zwykle trzeciorzędowe i wyższe, nazywa się również aminami wielkocząsteczkowymi. Osobną grupę tworzą heterocykliczne związki aroma...

28. source=legacy_mixed_paragraph_like

   Aceton, propanon, keton metylowy – organiczny związek chemiczny z grupy ketonów, najprostszy keton alifatyczny. Ma ostry, charakterystyczny zapach. Miesza się w każdych proporcjach z wodą, etanolem, eterami i innymi ketonami o niskiej masie cząsteczkowej. Występowanie i otrzymywanie Aceton obecny jest w niewielkich ilościach w krwi i moczu. Większe od normy jego stężenie pojawia się w organizmie przy zaawansowanej i nieleczonej cukrzycy. Aceton jest naturalnie obecny w tkankach wielu roślin (np. ziemniaków, żyta), gazach wulkanicznych i gazach spalinowych. Tworzy się on w dużych ilościach w trakcie suchej destylacji drewna, która była niegdyś głównym sposobem jego produkcji. Obecnie w prz...

29. source=legacy_long_article_like

   Algebra (, al-dżabr) – jedna z głównych dziedzin matematyki, zajmująca się wszelkimi strukturami algebraicznymi, czyli zbiorami – lub bardziej ogólnymi klasami – wyposażonymi w działania; struktury te bywają też nazywane algebrami ogólnymi. Początkowym przykładem takiego obiektu, długo definiującym tę dziedzinę, były liczby rzeczywiste ze standardowymi działaniami arytmetycznymi, a także liczby zespolone rozszerzające ten zbiór, wprowadzone właśnie na potrzeby klasycznie rozumianej algebry. Historycznie była to nauka o równaniach algebraicznych, ich układach i ogólnych tożsamościach algebraicznych – regułach manipulacji symbolami zmiennych. Dominowały w niej badania wielomianów o zmiennyc...

30. source=legacy_long_article_like

   Polonezköy (także Adampol; nazwa turecka oznacza „polska wieś”) – wieś w Turcji, założona w połowie XIX wieku, licząca 390 mieszkańców (2010 r.). Osada polskich imigrantów na obrzeżach Stambułu, położona po azjatyckiej stronie cieśniny Bosfor, w dystrykcie Beykoz, na północny wschód od centrum metropolii. Do około 1960 roku typowa wieś rolnicza, w której obok języka tureckiego używano także polszczyzny i pielęgnowano polskie obyczaje. W drugiej połowie XX wieku miejscowość zmieniła charakter na typowo turystyczny i obecnie składa się głównie z hoteli. Na wójta Polonezköy wybiera się tradycyjnie Polaka, jednak językiem polskim posługują się już tylko najstarsi mieszkańcy, a osoby pochodzen...

31. source=legacy_mixed_paragraph_like

   AtheOS – zaprojektowany przez norweskiego programistę Kurta Skauena system operacyjny, przeznaczony do zastosowań multimedialnych i biurowych. Obecnie projekt nie jest rozwijany, jego kontynuację stanowi Syllable. Architektura systemu posiada wiele podobieństw do systemu BeOS oraz AmigaOS. Jądro systemu obsługuje architekturę SMP, posiada możliwość dołączania sterowników urządzeń oraz systemów plików podczas działania, ponadto oferuje wbudowany stos TCP/IP oraz system graficzny (GUI). System graficzny jest podzielony na dwie części: serwera aplikacji, z którym programista komunikuje się za pomocą API w języku C++, a który to oferuje funkcje wysokiego poziomu, części umieszczonej w jądrze,...

32. source=legacy_mixed_paragraph_like

   AIX () – odmiana systemu Unix tworzona przez firmę IBM na podstawie zarówno SysV, jak i BSD. W systemie zostały zaimplementowane także technologie z systemów mainframe, które zwiększają jego niezawodność i dostępność. System operacyjny AIX jest przeznaczony dla serwerów firmy IBM z procesorami z rodziny Power (RS/6000, pSeries, Power System). Wczesne wersje systemu AIX były też instalowane na komputerach Macintosh firmy Apple wyposażonych w procesory POWER. Obecnie dostępna jest bardzo szeroka gama systemów serwerowych wyposażonych w procesory Power, od największych Power System 795 (do 256 układów POWER7) do serwerów typu blade (najmniejszy dostępny serwer JS12 wyposażony w 2 układy POWE...

33. source=legacy_long_article_like

   Aparat Golgiego – organellum występujące powszechnie w komórkach eukariotycznych, służące chemicznym modyfikacjom wytwarzanych przez komórkę substancji, ich sortowaniu oraz dystrybucji w obrębie komórki. Składa się ze stosu spłaszczonych cystern. Organellum zostało odkryte przez Camilla Golgiego w roku 1898. Od nazwiska odkrywcy pochodzi nazwa struktury. Znane są dwie formy aparatu Golgiego, siateczkowa jest charakterystyczna dla komórek zwierząt kręgowych (nie występuje jedynie w oocytach i plemnikach), druga nazywana łuskowatą albo diktiosomową występuje w komórkach roślinnych oraz w komórkach zwierząt bezkręgowych. Specyficzną cechą aparatu Golgiego jest to, że posiada zdolność redukcj...

34. source=legacy_mixed_paragraph_like

   Acetylocholina, ACh – organiczny związek chemiczny, ester kwasu octowego i choliny. Jest neuroprzekaźnikiem syntetyzowanym w neuronach cholinergicznych. Występuje w: połączeniach nerwowo-mięśniowych, synapsach przedzwojowych układu współczulnego, zakończeniach zazwojowych układu przywspółczulnego, a także w różnych strukturach mózgowia. Istnieją dwa typy receptorów cholinergicznych: nikotynowe – wbudowane w błonę komórki zwoju autonomicznego; muskarynowe – występujące w synapsach obwodowych zakończeń przywspółczulnych, wbudowane w błonę komórki efektorowej. Działanie Acetylocholina pobudza mięśnie szkieletowe. Powoduje także rozszerzenie naczyń krwionośnych, przez co obniża ciśnienie tętn...

35. source=legacy_long_article_like

   Adobe Photoshop – program graficzny przeznaczony do tworzenia i obróbki grafiki rastrowej, będący sztandarowym produktem firmy Adobe Systems. Program jest dostępny na platformy Windows i macOS. Projekty programu zapisywane są w dedykowanym formacie plików PSD. Historia W roku 1987 Thomas Knoll na komputerze Apple Macintosh Plus rozpoczął pisanie programu służącego do wyświetlania obrazów na monitorze monochromatycznym (będącym w stanie wyświetlać tylko różne odcienie szarości). Program nazwany Display przykuł uwagę jego brata, Johna Knolla, który zasugerował Thomasowi, aby dodał do programu funkcje edycyjne. W 1988 r. Thomas przerwał naukę na pół roku, by wspólnie z bratem rozwijać progra...

36. source=legacy_mixed_paragraph_like

   Architektura komputera oznacza w informatyce technicznej zbiór zasad i metod opisujących funkcjonalność, organizację i implementację komputerów. Niektóre definicje architektury komputerów definiują ją jako opis możliwości i model programowy komputera, ale nie konkretną implementację. W innych definicjach architektura komputera obejmuje projekt architektury zestawu instrukcji, projekt mikroarchitektury, syntezę logiczną i implementację. Wprowadzenie Komputer jest systemem złożonym o strukturze hierarchicznej - układem wzajemnie powiązanych podsystemów, z których każdy również ma strukturę hierarchiczną, aż do osiągnięcia najniższego poziomu - podsystemu elementarnego. Na każdym poziomie pr...

37. source=legacy_long_article_like

   Amiga (hiszp. amiga – przyjaciółka) – marka komputerów produkowanych od 1985 r. między innymi przez firmę Commodore, popularna w XX wieku. Po bankructwie Commodore marka została przejęta przez firmę Escom, a następnie przez Gateway. W końcu wyłoniła się samodzielna firma Amiga INC, która po bankructwie sprzedała wszelkie prawa firmie KMOS. Z kolei KMOS zmienił nazwę na Amiga Inc. System operacyjny Systemem operacyjnym Amigi jest AmigaOS z interfejsem Workbench. W momencie wydania AmigaOS był jednym z pierwszych systemów wielozadaniowych na komputery osobiste, znacznie przewyższającym pod tym względem systemy operacyjne produkowane w tamtych latach, na przykład Windows produkowany przez Mi...

38. source=legacy_mixed_paragraph_like

   Aromorfoza – termin wprowadzony przez Aleksieja Siewiercowa na określenie kluczowej innowacji w rozwoju istot żywych – istotnych zmian w budowie i funkcjonowaniu organizmów, podnoszące je na wyższy poziom rozwoju ewolucyjnego, umożliwiające opanowanie nowych środowisk (w odróżnieniu od drobnych zmian przystosowawczych, dla których zaproponował termin idioadaptacja). Przykłady aromorfoz u zwierząt: struna grzbietowa u bezczaszkowców błony płodowe u owodniowców przystosowanie do lotu u ptaków łożysko u ssaków Przykłady aromorfoz u roślin: wytworzenie tkanek przewodzących powstanie nasienia powstanie łagiewki pyłkowej Przypisy Ewolucja

39. source=legacy_long_article_like

   Azot (N, ) – pierwiastek chemiczny o liczbie atomowej 7, niemetal z grupy 15 (azotowców) układu okresowego. W warunkach normalnych jest bezbarwnym, bezzapachowym gazem. Został odkryty w 1772 roku przez Daniela Rutherforda. Azot jest podstawowym składnikiem powietrza (78,09% objętości), a jego zawartość w litosferze Ziemi wynosi 50 ppm. Wchodzi w skład wielu związków, takich jak: amoniak, kwas azotowy, azotyny oraz wielu ważnych związków organicznych (kwasy nukleinowe, białka, alkaloidy i wiele innych). Stabilnymi izotopami azotu są 14N i 15N. W stanie wolnym występuje w postaci dwuatomowej cząsteczki N2. W cząsteczce te dwa atomy tego pierwiastka są połączone ze sobą wiązaniem potrójnym....

40. source=legacy_mixed_paragraph_like

   Amedeo Avogadro, in. Amadeo Avogadro (ur. 9 sierpnia 1776 w Turynie, zm. 9 lipca 1856 tamże) – włoski fizyk, jeden z najważniejszych na przestrzeni wieków naukowców rozwijających atomistyczną teorię budowy materii. Życiorys Pełne jego nazwisko brzmiało: Lorenzo Romano Amedeo Carlo Avogadro hrabia di Quaregna e Cerreto, zawsze jednak podpisywał się jako Amedeo Avogadro. Pochodził z rodu o tradycjach prawniczych, członkowie jego rodziny zajmowali wysokie stanowiska w aparacie państwowym i w jurysdykcji, ojciec był prawnikiem i senatorem. Sam też, zgodnie z rodzinną tradycją ukończył studia prawnicze i rozpoczął pracę jako prawnik. Znał język francuski, angielski i niemiecki oraz literaturę...

41. source=legacy_mixed_paragraph_like

   Uwierzytelnienie – czynność polegająca na sprawdzeniu, stwierdzeniu i poświadczeniu, że przyrząd pomiarowy spełnia wymagania metrologiczne ustalone w przepisach, normach, zaleceniach międzynarodowych lub innych właściwych dokumentach, a jego wskazania zostały odniesione do państwowych wzorców jednostek miar i są z nimi zgodne w granicach określonych błędów pomiaru. Użycie w polskim prawodawstwie To określenie jest nieobowiązujące wraz z wejściem w życie w dniu 1 stycznia 2003 r. ustawy "Prawo o miarach" z dnia 11 maja 2001 r. W związku z ujednolicaniem przepisów przed wstąpieniem Polski do Unii Europejskiej jego funkcję przejęła w zakresie metrologii prawnej – legalizacja oraz w zakresie...

42. source=legacy_long_article_like

   Autoryzacja – wyrażenie zgody przez udzielającego informacji prasie na publiczne rozpowszechnienie swej wypowiedzi w danej formie. Potocznie: W przypadku wywiadów prasowych, autoryzacja polega na wspólnym uzgodnieniu ostatecznego tekstu wywiadu przez osobę jej udzielającą i dziennikarza, przed jego publikacją. Według polskiego prawa Art. 14a Prawa prasowego (ustawa z dnia 26 stycznia 1984 r.) reguluje kwestię autoryzacji od 12 grudnia 2017 r. Wcześniej w tym zakresie obowiązywał art. 14 ust. 2 (obecnie uchylony), który stanowił, że dziennikarz nie może odmówić osobie udzielającej informacji autoryzacji dosłownie cytowanej wypowiedzi, o ile nie była ona uprzednio publikowana. Dziennikarz n...

43. source=legacy_long_article_like

   Alfabet, abecadło (od stgr. nazw pierwszych liter alfabetu: alfa i beta lub z ) – najpopularniejszy system zapisywania mowy. Termin ten bywa używany w kilku znaczeniach, co jest źródłem licznych nieporozumień w dziedzinie historii i teorii pisma. Nieściśle „alfabetami” nazywa się też systemy pisma, które nimi nie są (pseudoalfabety). Nazwa „alfabet” i nazwy pokrewne Greckie pismo zostało nazywane alfabetem (skąd nazwa ta rozprzestrzeniła się też na pismo łacińskie), cyrylickie – azbuką, polskie abecadłem, ze względu na zestaw znaków (sens 2.) i porządek alfabetyczny (sens 3.) danego pisma, z wykorzystaniem nazw pierwszych liter (polskie: „a, be, ce, de”; greckie: „alpha, beta”; starocyryl...

44. source=legacy_mixed_paragraph_like

   Akronim AMP oznaczać może: Asynchronous multiprocessing – wieloprocesorowość asynchroniczna w architekturze komputera adenozyno-5′-monofosforan – organiczny związek chemiczny, jeden z nukleotydów Akademickie Mistrzostwa Polski – ogólnopolskie rozgrywki sportowe AMP – zestaw oprogramowania Apache, MySQL, PHP/Perl/Python AMP Warsaw – od Advanced Management Program Warsaw – nazwa programu dla menedżerów najwyższego szczebla prowadzonego w Polsce przez hiszpańską Wyższą Szkołę Zarządzania IESE. Australian MultiCam Pattern – nowy kamuflaż australijski oparty na MultiCam ArcelorMittal Poland – polski koncern hutniczy Accelerated Mobile Pages – zarzucony przez Google format tworzenia stron inter...

45. source=legacy_mixed_paragraph_like

   Wieloprocesorowość asynchroniczna (, AMP) – architektura komputerowa mająca na celu zwiększenie mocy obliczeniowej komputera poprzez wykorzystanie kilku procesorów pracujących niezależnie od siebie. W architekturze asynchronicznej, która jest odmianą wieloprocesorowości asymetrycznej, poszczególne procesory nie są traktowane jednakowo. W szczególności procesory mogą pracować niezależnie od siebie, być taktowane innymi zegarami, a nawet mogą być na nich uruchamiane różne systemy operacyjne. Układy AMP wykorzystywane są w systemach czasu rzeczywistego (RTOS), które wymagają utrzymywania ścisłej kontroli nad procesorem, na którym system jest uruchomiony. Procesory w układzie AMP mogą mieć do...

46. source=legacy_mixed_paragraph_like

   Apla – pojęcie z zakresu poligrafii, może oznaczać: jednobarwną, nierastrowaną płaszczyznę mogąca stanowić tło np. plakatu, okładki, na którym można umieścić tekst czy ilustracje, a także wykorzystać je jako swoisty kontrast wobec innych elementów powierzchnię zadrukowaną w powyższy sposób blachę cynkową służącą jako formę do druku wypukłego ilość użytej farby drukowej W przypadku zastosowania apli o jasnych barwach, na którą będą nanoszone elementy o barwach ciemniejszych określa się ją mianem tinty. Nanoszenie apli z wykorzystaniem starszego bądź zużytego sprzętu drukarskiego może nieść ryzyko wystąpienia wad druku, takich jak nierównomierne rozłożenie koloru na arkuszu, pasy, czy powta...

47. source=legacy_long_article_like

   Asembler (z ang. assembler) – termin informatyczny związany z programowaniem i tworzeniem kodu maszynowego dla procesorów. W języku polskim oznacza on program tworzący kod maszynowy na podstawie kodu źródłowego (tzw. asemblacja) wykonanego w niskopoziomowym języku programowania bazującym na podstawowych operacjach procesora zwanym językiem asemblera, popularnie nazywanym również asemblerem. W tym artykule język programowania nazywany będzie językiem asemblera, a program tłumaczący – asemblerem. Język asemblera Języki asemblera (zwyczajowo asemblery) to rodzina języków programowania niskiego poziomu, których jedno polecenie odpowiada zasadniczo jednemu rozkazowi procesora. Języki te powsta...

48. source=legacy_long_article_like

   Alfred Jodl (ur. 10 maja 1890 w Würzburgu, zm. 16 października 1946 w Norymberdze) – niemiecki dowódca wojskowy z czasów II wojny światowej w stopniu generała pułkownika (Generaloberst), skazany na śmierć i stracony jako zbrodniarz wojenny i zbrodniarz przeciwko ludzkości. Życiorys Po ukończeniu akademii wojskowej i szkoły sztabu generalnego rozpoczął swoją karierę jako podporucznik w bawarskim pułku artylerii. W czasie I wojny światowej pełnił funkcje frontowe i sztabowe. Walczył we Francji i w Rosji, odnosząc rany. Po zakończeniu wojny nie porzucił służby w wojsku i kontynuował ją, dochodząc do coraz wyższych stanowisk. Od 1919 roku Jodl był członkiem Straży Narodowej Volkswehr. Został...

49. source=legacy_long_article_like

   Antonio de Padua María Severino López de Santa Anna y Pérez de Lebrón (ur. 21 lutego 1794 w Xalapa-Enríquez, zm. 21 czerwca 1876 w Meksyku) – meksykański polityk konserwatywny i wojskowy, wielokrotny prezydent Meksyku. W 1821 roku, po proklamacji „planu z Iguali”, poparł Agustina de Iturbide (1783–1824) i walczył o niepodległość Meksyku. Po uzyskaniu niepodległości przywodził czterem rebeliom (w 1823, 1828, 1832 i 1841 roku). Sprawował urząd prezydenta wielokrotnie przez różne okresy w latach: 1833–1835, 1839, 1841–1843, 1843–1844, 1846–1847 i 1853–1855. Odparł hiszpańską inwazję w 1829 roku, francuską w 1838 roku, a w 1836 roku wygrał bitwę o Alamo. Jego przegrana w bitwie pod San Jacint...

50. source=legacy_mixed_paragraph_like

   Argon (Ar, ) – pierwiastek chemiczny będący gazem szlachetnym. Jest praktycznie niereaktywny i nie ma żadnego znaczenia biologicznego, jest także jednym ze składników powietrza. Argon wyodrębnili i zidentyfikowali Lord Rayleigh i sir William Ramsay w 1894 roku, usuwając z powietrza tlen, azot, dwutlenek węgla i parę wodną. Atomy argonu mogą zostać uwięzione w sieci innych cząsteczek tworząc klatraty, np. Ar6(H2O)46 i Ar(hydrochinon)3. W roku 2000 doniesiono o otrzymaniu pierwszego związku argonu, fluorowodorku HArF. Izotopy stabilne to 36Ar, 38Ar i 40Ar. Występujący na Ziemi argon ma wyższą masę atomową (39,948 u) niż następny po nim potas (39,0983 u). Jest to spowodowane tym, że nietrwał...

## Rejected Samples

1. source=legacy_long_article_like reasons=very_long_line

   Atom – podstawowy składnik materii. Składa się z małego dodatnio naładowanego jądra o dużej gęstości i otaczającej go chmury elektronowej o ujemnym ładunku elektrycznym. Słowo atom pochodzi z greckiego – átomos (od α-, „nie-” + τέμνω – temno, „ciąć”), oznaczającego coś, czego nie da się przeciąć ani podzielić. Idea istnienia niepodzielnych składników materii pojawiła się już w pismach starożytnych filozofów indyjskich i greckich. W XVII i XVIII wieku chemicy potwierdzili te przypuszczenia, identyfikując pierwiastki chemiczne i pokazując, że reagują one ze sobą w ściśle określonych proporcjach. W XIX wieku odkryto ruchy Browna, będące pośrednim dowodem ziarnistości materii. Na początku XX...

2. source=legacy_mixed_paragraph_like reasons=boilerplate_phrase

   Association for Computing Machinery (ACM) to największa na świecie społeczność ludzi nauki, nauczycieli i profesjonalistów zajmujących się informatyką. Nazwa w tłumaczeniu na język polski to Stowarzyszenie dla Maszyn Liczących. Celem ACM jest rozwój nauki, sztuki oraz inżynierii i zastosowań IT poprzez dialog, integrację środowiska, promowanie wiedzy, tworzenie i promowanie etycznych i zawodowych standardów. Historia ACM zostało utworzone 15 września 1947 roku w Nowym Jorku w trakcie serii spotkań na Uniwersytecie Columbia. Utworzenie stowarzyszenia było odpowiedzią na postęp informatyki. Artykuły i prace z tej dziedziny wcześniej były związane z matematyką, elektryką i innymi naukami. Sp...

3. source=legacy_long_article_like reasons=too_long,very_long_line

   Anarchizm – doktryna polityczna i ruch społeczny, które cechują się niechęcią wobec władzy oraz odrzuceniem własności prywatnej i wszelkich przymusowych form hierarchii. Anarchizm wzywa do zniesienia państwa, które uważa za niepotrzebne i szkodliwe. Pojawiły się pewne kontrowersje co do definicji anarchizmu, a tym samym jego historii. Jedna grupa uczonych uważa anarchizm za ściśle powiązany z walką klas. Inni uznają, że ta perspektywa jest zbyt wąska. Podczas gdy pierwsza grupa bada anarchizm jako zjawisko, które miało miejsce w XIX wieku, druga szuka jego korzeni w historii starożytnej. Murray Bookchin opisywał kontynuację „dziedzictwa wolności” ludzkości (tj. momentów rewolucyjnych), kt...

4. source=legacy_long_article_like reasons=very_long_line

   Algorytm – skończony ciąg jasno zdefiniowanych czynności koniecznych do wykonania pewnego rodzaju zadań, sposób postępowania prowadzący do rozwiązania problemu. Można go przedstawić na schemacie blokowym. Słowo „algorytm” pochodzi od łacińskiego słowa algorithmus, oznaczającego wykonywanie działań przy pomocy liczb arabskich (w odróżnieniu od abacism – przy pomocy abakusa), które z kolei wzięło się od nazwy „Algoritmi”, zlatynizowanej wersji nazwiska „al-Chwarizmi” Abu Abdullaha Muhammada ibn Musy al-Chuwarizmiego, matematyka perskiego z IX wieku. Zadaniem algorytmu jest przeprowadzenie systemu z pewnego stanu początkowego do pożądanego stanu końcowego. Badaniem algorytmów zajmuje się alg...

5. source=legacy_mixed_paragraph_like reasons=too_short

   energetyka jądrowa fizyka jądrowa ochrona radiologiczna atomizm Atomistyka – album Elektrycznych Gitar

6. source=legacy_long_article_like reasons=boilerplate_phrase,very_long_line

   Albania, Republika Albanii () – państwo w południowo-wschodniej Europie na Bałkanach. Albania na zachodzie ma dostęp do Morza Adriatyckiego, a na południowym zachodzie do Morza Jońskiego. Od Włoch oddziela ją cieśnina Otranto o szerokości ok. 72 km. Łączna długość granic lądowych wynosi 720 km, natomiast wybrzeża morskiego – 362 km. Graniczy z: Grecją (282 km), Czarnogórą (173 km), Macedonią Północną (151 km) oraz Serbią/Kosowem (114 km). Jest członkiem ONZ, NATO, OBWE, Rady Europy, WTO oraz jednym z założycieli Unii na rzecz Regionu Morza Śródziemnego. Od 2014 roku Albania ma status kandydata do Unii Europejskiej. Albania ma system parlamentarny. Stolicą kraju jest Tirana, jest to równie...

7. source=legacy_long_article_like reasons=boilerplate_phrase,very_long_line

   Austria (niem. Österreich, ), Republika Austrii (niem. Republik Österreich, ) – państwo śródlądowe położone w Europie Środkowej, federacja dziewięciu krajów związkowych ze stolicą w Wiedniu. Od 1995 Austria należy do Unii Europejskiej. Pochodzenie nazwy W języku niemieckim Österreich ze starowysokoniemieckiego ôstarrîhhi, znaczącego „państwo na wschodzie”. W IX wieku terytorium było wschodnią częścią imperium Franków, a także wschodnimi rubieżami osadnictwa niemieckiego na terenach Słowian. Za czasów Karola Wielkiego i w czasie wczesnego średniowiecza tereny te nazywano marchia orientalis (Marchia Wschodnia), co w lokalnym języku przyjęto jako właśnie ôstarrîhhi. To słowo po raz pierwszy...

8. source=legacy_long_article_like reasons=boilerplate_phrase

   Andora, Księstwo Andory (kat. Principat d’Andorra []), nazwa historyczna (tradycyjna): Doliny Andory (kat. Les Valls d’Andorra) – małe państwo w południowo-zachodniej Europie, bez dostępu do morza. Leży w Pirenejach, granicząc od północy z Francją, a od południa z Hiszpanią. Geografia Andora to kraj leżący w Pirenejach i całkowicie pokryty górami. Ma powierzchnię 468 km². Średnia wysokość terenu to 1996 m n.p.m. Na licznych zboczach często występują wysokogórskie łąki i lasy. Najwyższy punkt w państwie to szczyt góry Pic Alt de la Coma Pedrosa (2946 m n.p.m.), najniższym jest Riu Runer, który leży w pobliżu granicy z Hiszpanią na wysokości 840 m n.p.m. Najdłuższą rzeką jest Valira, będąca...

9. source=legacy_long_article_like reasons=very_long_line

   Armia Radziecka () – oficjalna nazwa wojsk lądowych, sił powietrznych, wojsk obrony przeciwlotniczej i wojsk rakietowych przeznaczenia strategicznego Sił Zbrojnych ZSRR (w latach 1946–1991) i WNP (1991–1992), które tworzyła razem z marynarką, wojskami pogranicznymi i wewnętrznymi. Nazwa została wprowadzona w 1946 roku (uprzednio Robotniczo-Chłopska Armia Czerwona, RKKA). Armia Radziecka w powojennej Polsce Po II wojnie światowej Naczelne Dowództwo Armii Czerwonej przeformowało dotychczasowe formacje. Na terenie Polski utworzona została tzw. PGW – Północna Grupa Wojsk dyrektywą nr 11097 z dnia 10 czerwca 1945 roku. W grupę tę przekształcono 2 Front Białoruski pod dowództwem marszałka Związ...

10. source=legacy_long_article_like reasons=very_long_line

   Arystofanes z Aten (gr. , Aristophanes) (ok. 446–385 p.n.e.) – grecki komediopisarz, jeden z twórców komedii staroattyckiej, syn średnio zamożnego chłopa o imieniu Filippos. Jego działalność przypadła na schyłkowy okres demokracji ateńskiej, gdy następowały zmiany w życiu politycznym, społecznym i kulturalnym, a także w sposobie myślenia i metodach kształcenia młodzieży (zob. Sokrates). Zapewne nie do końca porzucił wieś i choć nie mieszkał w Atenach, to bywał w nich często. Nie piastował w mieście urzędów i patrzył na demokrację ateńską z boku, zachowując większy obiektywizm. Arystofanes jest najlepiej rozpoznanym i najszerzej opisanym spośród autorów komedii staroattyckiej. Jego poprzed...

11. source=legacy_mixed_paragraph_like reasons=single_word_repetition,repeated_ngrams

   geografia Alabama – stan w USA Alabama – miasto w Stanach Zjednoczonych, w stanie Nowy Jork, w hrabstwie Genesee Alabama (ang. Alabama Township) – gmina w Stanach Zjednoczonych, w stanie Arkansas, w hrabstwie Nevada Alabama (ang. Alabama Town) – gmina w Stanach Zjednoczonych, w stanie Nowy Jork, w hrabstwie Genesee Alabama – rzeka w USA etnografia Alabama – plemię Indian z Ameryki Płn. kinematografia i muzyka Alabama (Noemi i diabeł) - piosenka z repertuaru Ludmiły Jakubczak - 1957 Alabama Song (Whiskey Bar) - piosenka z repertuaru The Doors - 1967 Alabama – amerykański zespół muzyczny powstały w 1970 Alabama – film polski z 1984 r. Alabama: 2000 Light Years from Home – film Wima Wendersa...

12. source=legacy_long_article_like reasons=very_long_line

   Alabama (wym. ) – stan w południowo-wschodniej części Stanów Zjednoczonych, położony nad Zatoką Meksykańską. Obszar nizinny, od północnego wschodu ograniczony wyżyną Cumberland, od północnego wschodu górami – Appalachami. Na północy sąsiaduje ze stanem Tennessee, na wschodzie z Georgią, na południu z Florydą i Zatoką Meksykańską, na zachodzie z Missisipi. Alabama zajmuje 30. miejsce pod względem powierzchni oraz 23. pod względem liczby ludności wśród stanów Stanów Zjednoczonych. Od wojny secesyjnej do II wojny światowej stan ten odczuwał trudności gospodarcze ze względu na ciągłe uzależnienie od rolnictwa. Pomimo rozwoju przemysłu i ośrodków miejskich, aż do 1960 roku w stanowej legislatu...

13. source=legacy_long_article_like reasons=repeated_ngrams

   Alaska () – stan Stanów Zjednoczonych w północno-zachodniej części Ameryki Północnej, będący eksklawą Stanów Zjednoczonych. Graniczy od wschodu z Kanadą, a od zachodu, przez Cieśninę Beringa, z Rosją. Dominują góry, z najwyższym punktem Ameryki Północnej, którym jest szczyt Denali (McKinley, 6194 m n.p.m.), oraz wyżyny i liczne stożki wulkaniczne. Do terytorium należą też Aleuty. Alaska ma największą powierzchnię wśród stanów Stanów Zjednoczonych oraz najmniejszą gęstość zaludnienia. W odróżnieniu od większości stanów Alaska nie dzieli się na hrabstwa, lecz okręgi (borough), przy czym znaczna część stanu stanowi terytorium niezorganizowane. Geografia Powierzchnia stanu jest górzysta. Na p...

14. source=legacy_long_article_like reasons=very_long_line

   Ameryka Południowa – kontynent o powierzchni 17,8 miliona km² leżący na półkuli zachodniej oraz w większej części na półkuli południowej, a w mniejszej – na półkuli północnej. Niekiedy uważana jest również za subkontynent Ameryki. Amerykę Południową oblewa od wschodu Ocean Atlantycki, a od zachodu Ocean Spokojny. Od północy, przez Przesmyk Panamski oraz Morze Karaibskie, kontynent graniczy z Ameryką Północną. Jego powierzchnię zajmuje 13 państw: Argentyna, Boliwia, Brazylia, Chile, Ekwador, Gujana, Kolumbia, Paragwaj, Peru, Surinam, Urugwaj, Wenezuela, Trynidad i Tobago oraz pięć terytoriów zależnych: Aruba, Bonaire, Curaçao należące do Holandii, Gujana Francuska należąca do Francji i bry...

15. source=legacy_long_article_like reasons=very_long_line

   Alergia (popularnie stosowane synonimy: uczulenie, nadwrażliwość) – patologiczna, jakościowo zmieniona odpowiedź tkanek na oddziaływanie różnych obcych substancji, zwanych alergenami, polegająca na reakcji immunologicznej związanej z powstaniem swoistych przeciwciał, które po związaniu z antygenem doprowadzają do uwolnienia różnych substancji – mediatorów stanu zapalnego. Czynnik środowiskowy wywołujący alergię sam w sobie zazwyczaj nie jest dla organizmu szkodliwy. W reakcjach alergicznych uczestniczy układ immunologiczny, jego komórki, na przykład limfocyty (zwłaszcza z podgrupy Th2), granulocyty kwasochłonne (eozynofile) oraz komórki tuczne (mastocyty). Istotną rolę w alergicznych odcz...

16. source=legacy_long_article_like reasons=repeated_ngrams

   Alfabet łaciński, pismo łacińskie, łacinka, alfabet rzymski – alfabet, system znaków służących do zapisu większości języków europejskich oraz wielu innych. Jest najbardziej rozpowszechnionym alfabetem na świecie – posługuje się nim około 35% ludzkości. W odróżnieniu od greckiego jest de facto abecadłem – ponieważ jego pierwsze litery to: a, b, c, d – a nie alfa i beta. Wywodzi się z systemu służącego do zapisu łaciny. Opis Kształtowanie się alfabetu Alfabet łaciński wywodzi się z alfabetu etruskiego, początkowo składał się z 21 znaków: Litera Z została usunięta w IV wieku p.n.e. jako niepotrzebna do zapisu łaciny przez cenzora Appiusza Klaudiusza Caecusa. Początkowo litera C służyła do od...

17. source=legacy_long_article_like reasons=very_long_line

   Albert Einstein (wym. ) (ur. 14 marca 1879 w Ulm, zm. 18 kwietnia 1955 w Princeton) – fizyk teoretyk, noblista, obywatel Szwajcarii i USA pochodzenia niemiecko-żydowskiego. Profesor różnych placówek w Szwajcarii, Austro-Węgrzech, Niemczech i USA: Uniwersytetu w Zurychu, Uniwersytetu Karola w Pradze, Politechniki Federalnej w Zurychu (ETHZ), Uniwersytetu Berlińskiego i Instytutu Badań Zaawansowanych (IAS) w Princeton. Einstein zrewolucjonizował zarówno mechanikę, jak i teorię pola, głównie w wersji klasycznej, choć odegrał też kluczową rolę dla mechaniki kwantowej. Laureat Nagrody Nobla w dziedzinie fizyki za 1921 rok, w uznaniu za „wkład do fizyki teoretycznej, zwłaszcza opis prawa efektu...

18. source=legacy_mixed_paragraph_like reasons=boilerplate_phrase,single_word_repetition

   Alba – imię żeńskie Alba – szata liturgiczna koloru białego Alba – w jęz. irlandzkim i szkockim gaelickim to oficjalna nazwa Szkocji Królestwo Alby – dawne królestwo w Szkocji BBC Alba – brytyjski kanał telewizyjny nadający w jęz. szkockim gaelickim Alba – średniowieczna pieśń prowansalska Alba – wino włoskie z okręgu Alba ALBA (Boliwariańska Alternatywa dla Ameryki) – porozumienie gospodarcze Księstwo Alba – (Alva) księstwo w Hiszpanii, z najsłynniejszym przedstawicielem Ferdynandem Álvarazem de Toledo. XIII księżna Alba była patronka i muzą Francisca Goi Jessica Marie Alba – aktorka amerykańska Alba Berlin – niemiecki klub koszykarski Alba Chorzów – nieistniejący polski klub koszykarski...

19. source=legacy_mixed_paragraph_like reasons=too_short

   Alfa Centauri – gwiazda Alpha Centauri – gra komputerowa Alpha Centauri – album Tangerine Dream

20. source=legacy_long_article_like reasons=repeated_ngrams

   Antoni Gorecki herbu Dołęga, pseud. i krypt.: G., Litwanis, Litwin, Wapru, (ur. 1787 w Wilnie, zm. 18 września 1861 w Paryżu) – polski poeta, satyryk i bajkopisarz, powstaniec listopadowy i uczestnik wojen napoleońskich, członek korespondent Towarzystwa Królewskiego Przyjaciół Nauk w Warszawie w 1829 roku. Życiorys Pochodził z rodziny szlacheckiej pieczętującej się herbem Dołęga. Był synem Walentego i Anny z Reuttów. Był absolwentem Szkoły Głównej Wileńskiej. W latach 1803-1806 kształcił się na wydziale literatury Uniwersytetu Wileńskiego. W czasie studiów poznał się i zaprzyjaźnił się z Lelewelem. Przekradł się do Księstwa Warszawskiego i zaciągnął do polskiego wojska. Od roku 1809 służy...

21. source=legacy_long_article_like reasons=too_long,very_long_line

   Alfred Joseph Hitchcock, KBE (wym. []; ur. 13 sierpnia 1899 w Londynie, zm. 29 kwietnia 1980 w Los Angeles) – angielski reżyser filmowy, telewizyjny, scenarzysta i producent, uznawany za jednego z najbardziej wpływowych twórców filmowych w historii kina. Określany mianem „mistrza suspensu”. W trwającej sześć dekad karierze wyreżyserował 53 filmy fabularne. Stał się rozpoznawalny dzięki licznym wywiadom, występom cameo w swoich produkcjach i serialowi kryminalnemu Alfred Hitchcock przedstawia (1955–1962). Podobne uznanie zyskiwali aktorzy grający w jego filmach. W 1955 przyjął obywatelstwo amerykańskie. Hitchcock początkowo zarabiał jako copywriter i pracownik techniczny w przedsiębiorstwi...

22. source=legacy_long_article_like reasons=too_long,boilerplate_phrase,very_long_line

   Argentyna (hiszp. Argentina, ), oficjalnie Republika Argentyńska (hiszp. República Argentina, wym. ) – państwo w Ameryce Południowej, w południowo-wschodniej części kontynentu, nad Oceanem Atlantyckim. Graniczy z Chile na zachodzie, Boliwią i Paragwajem na północy, Brazylią i Urugwajem na północnym wschodzie. Nazwa „Argentyna” pochodzi od łacińskiego argentum (srebro, plata po hiszpańsku) i jest związana z legendą o górach pełnych srebra, która była powszechna pośród pierwszych europejskich odkrywców Niziny La Platy. Argentyna zajmuje jedno z najwyższych miejsc w rankingach wskaźnika rozwoju społecznego, PKB per capita i jakości życia pośród krajów Ameryki Łacińskiej. Według statystyk Ban...

23. source=legacy_long_article_like reasons=too_long,very_long_line

   Armia Krajowa (AK) lub Siły Zbrojne w Kraju, kryptonim „PZP” (Polski Związek Powstańczy) – zakonspirowane siły zbrojne Polskiego Państwa Podziemnego w latach II wojny światowej, powstałe z przemianowania Związku Walki Zbrojnej (powstałego w listopadzie 1939) rozkazem Naczelnego Wodza generała broni Władysława Sikorskiego z 14 lutego 1942 r. Działała na terytorium Rzeczypospolitej Polskiej, okupowanej przez Niemcy i ZSRR (po wkroczeniu Armii Czerwonej na terytorium państwa polskiego 4 stycznia 1944 r.). Siły Zbrojne w Kraju były integralną częścią Polskich Sił Zbrojnych, podporządkowaną Naczelnemu Wodzowi. Największą operacją militarną Armii Krajowej była akcja „Burza” i w jej ramach powst...

24. source=legacy_long_article_like reasons=repeated_ngrams

   Asembler x86 – język programowania z rodziny asemblerów do komputerów klasy PC, które posiadają architekturę głównego procesora zgodną z x86. W rzeczywistości jest to kilka różnych języków używanych do zapisu tych samych instrukcji i dyrektyw, różniących się składnią. Trzy najpopularniejsze składnie to: składnia Intel/Microsoft - używana w asemblerze MASM firmy Microsoft i w przykładach zamieszczonych w dokumentacji firmowej procesorów Intel rodziny x86; dawniej korzystała z niej większość narzędzi programistycznych dla systemów DOS i Windows. składnia NASM - używana w asemblerze NASM, podobna do składni Intel/Microsoft, ale uproszczona i pozbawiona niejednoznaczności zapisu składnia AT&T...

25. source=legacy_long_article_like reasons=repeated_ngrams

   Aleksander Gieysztor, ps. „Borodzicz”, „Lissowski”, „Olicki”, „Walda” (ur. w Moskwie, zm. 9 lutego 1999 w Warszawie) – polski historyk mediewista, profesor Uniwersytetu Warszawskiego, członek Polskiej Akademii Nauk. Kawaler Orderu Orła Białego. Uczestnik kampanii wrześniowej, żołnierz Związku Walki Zbrojnej i Armii Krajowej, szef Wydziału Biura Informacji i Propagandy AK, powstaniec warszawski, szef Biura Informacji i Propagandy Delegatury Sił Zbrojnych na Kraj oraz Zrzeszenia Wolność i Niezawisłość. Autor około pięciuset publikacji. W latach 1955–1975 dyrektor Instytutu Historycznego Uniwersytetu Warszawskiego. W latach 1979–1991 dyrektor Zamku Królewskiego w Warszawie. W latach 1980–198...

26. source=legacy_long_article_like reasons=very_long_line

   Ateizm (z gr. „bezbożny” – a-, „bez” oraz , theos, „bóg”) – brak wiary w istnienie jednego bądź wielu bogów czy też odrzucający wiarę w stwórcę; ewentualnie odrzucenie teizmu. Może uznawać religię za sprzeczną z nauką, sprzeczną z rozumem lub niepotrzebną. Kwestionowanie wiary w bogów-stwórców można odnaleźć już w hymnach Rygwedy oraz w poglądach myślicieli antycznych takich jak Diagoras z Melos. Ateistami na przestrzeni dziejów były określane osoby, które uznano za wierzące w fałszywych bogów, niewierzące w bogów lub wyznające doktryny wchodzące w konflikt z lokalnie dominującymi religiami. Wraz z upowszechnianiem się wolnomyślicielstwa, sceptycyzmu i późniejszego nasilenia krytyki relig...

27. source=legacy_mixed_paragraph_like reasons=too_short

   Koniunkcja (logika) AND – MKOl kod Andory AND – IATA kod miasta Anderson, Seszele

28. source=legacy_long_article_like reasons=too_many_urls

   Artemida, Artemis; Ártemis, ) – w mitologii greckiej bogini łowów, zwierząt, lasów, gór i roślinności; wielka łowczyni. Uważana również za boginię płodności, niosącą pomoc rodzącym kobietom. Podobnie jak Apollo był bogiem słońca i życia, tak Artemidę uznawano za boginię księżyca i śmierci. Wierzono bowiem, że bliźniacze rodzeństwo charakteryzuje podobna konstrukcja duchowa. Ze względu na związek między obrotami księżyca a przypływami i odpływami morza, Artemidę zaczęto uważać za bóstwo opiekuńcze rybaków. Jej atrybutami były łuk, strzały i kołczan, a ulubionym zwierzęciem łania. Była córką Zeusa i Latony, siostrą bliźniaczką Apollina. Należała do grona 12 bogów olimpijskich. Bogini-dziewi...

29. source=legacy_long_article_like reasons=very_long_line

   Atena (gr. Athene, Athenaie, łac. Minerva) – w mitologii greckiej bogini mądrości, sztuki, sprawiedliwej wojny oraz opiekunka miast, m.in. Aten i Sparty. Jest jedną z dwunastu głównych bogów olimpijskich. Jej atrybutami są: włócznia, tarcza i łuk. Jej świętym zwierzęciem jest sowa, a rośliną – oliwka. Jej rzymskim odpowiednikiem jest Minerwa. Geneza Geneza Ateny nie została jednoznacznie ustalona. Wiadomo jednakże, że istniała już za czasów przedgreckich. Teksty zapisane pismem linearnym B wskazują na jej dużą rolę w okresie mykeńskim. Miałaby wtedy opiekować się władcami i pałacami królów, co wiązałoby się z jej późniejszą rolą patronki miast i rodów bohaterskich. Rodowód i narodziny Jes...

30. source=legacy_long_article_like reasons=very_long_line

   Aborcja ( lub „poronienie, wywołanie poronienia”) – zamierzone zakończenie ciąży w wyniku interwencji zewnętrznej, np. działań lekarskich, w j. łacińskim abortus provocatus. Przeważnie w efekcie dochodzi do śmierci zarodka lub płodu ludzkiego (łac. nasciturus). Wykonywanie aborcji w wielu krajach jest regulowane prawnie. Aborcja legalna, czyli wykonana w zgodzie z obowiązującymi w danym państwie ustawami i przez dyplomowanego lekarza, nazywana jest po łacinie abortus provocatus lege artis. Aborcja nielegalna, czyli wykonana przez osobę nieuprawnioną lub niezgodnie z regulacjami prawnymi nosi nazwę abortus provocatus criminalis. Ustawodawstwo w tym zakresie różni się od siebie w różnych kr...

31. source=legacy_mixed_paragraph_like reasons=single_word_repetition

   Archipelag – grupa wysp położonych blisko siebie, najczęściej o wspólnej genezie i podobnej budowie geologicznej. Ze względu na ułożenie wysp można wyróżnić roje wysp – archipelagi składające się z bezładnie rozmieszczonych niedużych wysp oraz łańcuchy wysp, w których wyspy rozmieszczone są rzędem jedna obok drugiej. Etymologia Nazwa pochodzi z Archipelagos – nazwa prowincji bizantyjskiej obejmującej główne wyspy Morza Egejskiego. Archipelagi świata Ocean Arktyczny Archipelag Arktyczny, Nowa Ziemia, Svalbard, Wyspy Nowosyberyjskie, Ziemia Franciszka Józefa, Ziemia Północna. Ocean Atlantycki: Antyle, Azory, Bahamy, Baleary, Cyklady, Falklandy, Florida Keys, Hebrydy, Lofoty, Madera, Orkady,...

32. source=legacy_mixed_paragraph_like reasons=too_short

   Andorra – gmina w Hiszpanii Andora – państwo w Europie

33. source=legacy_long_article_like reasons=too_long,very_long_line

   (wym. ; ur. 20 kwietnia 1889 w Braunau am Inn, zm. 30 kwietnia 1945 w Berlinie) – niemiecki polityk pochodzenia austriackiego, kanclerz Rzeszy od 30 stycznia 1933, Wódz i kanclerz Rzeszy (niem. Der Führer und Reichskanzler) od 2 sierpnia 1934 do śmierci; twórca i dyktator III Rzeszy, przywódca Narodowosocjalistycznej Niemieckiej Partii Robotników (NSDAP), ideolog narodowego socjalizmu; zbrodniarz wojenny, odpowiedzialny za zbrodnie przeciw ludzkości. Uznawany za osobiście odpowiedzialnego za politykę rasową III Rzeszy i śmierć milionów ludzi zabitych podczas jego rządów – w tym – za Holocaust i Porajmos. Urodził się na obszarze ówczesnych Austro-Węgier i wychował się w pobliżu Linzu. W 19...

34. source=legacy_long_article_like reasons=very_long_line

   Azja (gr. Asía, łac. Asia) – w zależności od podejścia: największy kontynent na Ziemi lub część świata, która razem z Europą tworzy największy kontynent, Eurazję. Nazywana jest często kontynentem wielkich kontrastów geograficznych. Sąsiaduje z Europą od zachodu, Afryką od południowego zachodu, Oceanem Indyjskim i Australią od południowego wschodu oraz Pacyfikiem od wschodu. Dokładny przebieg zachodniej granicy geograficznej przedstawiony jest w haśle granica Europa-Azja. Obszar Azji to 44,6 mln km² powierzchni lądów, co stanowi około 30% powierzchni wszystkich lądów. Ma charakter wyżynno-górski (wyżyny stanowią 75% powierzchni tego kontynentu – średnia wysokość Azji to prawie 1000 m n.p.m...

35. source=legacy_long_article_like reasons=very_long_line,repeated_ngrams

   Uniwersytet Medyczny w Białymstoku (UMB), do 2008 Akademia Medyczna w Białymstoku – publiczna uczelnia o profilu medycznym utworzona w 1950 jako Akademia Lekarska w Białymstoku. Siedzibę Uniwersytetu stanowi spalony w czasie wojny, a następnie odbudowany pałac Branickich. W latach pięćdziesiątych i sześćdziesiątych główny wysiłek badawczy uczelni koncentrował się wokół zagadnień patofizjologii i biochemii procesów krzepnięcia krwi i fibrynolizy. Później stała się znana głównie z pierwszych wykonywanych w Polsce operacji in vitro. Na Uniwersytecie funkcjonują trzy wydziały: Wydział Lekarski z Oddziałem Stomatologii i Oddziałem Nauczania w Języku Angielskim, Wydział Farmaceutyczny z Oddział...

36. source=legacy_long_article_like reasons=repeated_ngrams

   Uczelnie medyczne w Polsce – wykaz działających w Polsce uczelni medycznych oraz podstawowych jednostek organizacyjnych (w tym wydziałów uniwersyteckich), kształcących na kierunku lekarskim. Charakterystyka Zgodnie z Ustawą z dnia 20 lipca 2018 r. Prawo o szkolnictwie wyższym i nauce, uczelnia medyczna w Polsce jest uczelnią publiczną nadzorowaną przez ministra właściwego ds. zdrowia. Minister zdrowia nadzoruje zgodność działań uniwersytetów medycznych z przepisami prawa i statutem, a także prawidłowe wydatkowanie środków publicznych. W Polsce funkcjonuje 9 uniwersytetów medycznych, Collegium Medicum Uniwersytetu Jagiellońskiego (w latach 1950–1993 Akademia Medyczna im. Mikołaja Kopernika...

37. source=legacy_mixed_paragraph_like reasons=single_word_repetition

   Antonia – imię noszone przez przedstawicielki rzymskiego rodu Antoniuszy (Antonii) Antonia Hybryda – wnuczka Marka Antoniusza Oratora Antonia – żona Lucjusza Kaniniusza Gallusa Antonia – żona Pythodorosa Antonia Starsza – babka cesarza Nerona. Antonia Młodsza – matka cesarza Klaudiusza Klaudia Antonia – córka cesarza Klaudiusza Zobacz też: Drzewo genealogiczne Antoniuszów Miejscowości o nazwie Antonia w Polsce: Antonia – wieś w woj. mazowieckim, w pow. ostrołęckim, w gminie Łyse Antonia – wieś w woj. warmińsko-mazurskim, w pow. szczycieńskim, w gminie Rozogi Inne: Antonia – twierdza w starożytnej Jerozolimie broniąca dostępu do Świątyni Jerozolimskiej. Antonia – imię żeńskie

38. source=legacy_long_article_like reasons=boilerplate_phrase,very_long_line

   Apollo 11 – misja kosmiczna, której głównym celem było pierwsze lądowanie człowieka na Księżycu. Lądowanie nastąpiło 20 lipca 1969 roku o godzinie 20:17:40 UTC w miejscu o współrzędnych 0°40′26.69″N i 23°28′22.69″E. Lot Apollo 11 był elementem szerszego programu Apollo. W 1961 roku prezydent USA, John F. Kennedy ogłosił, że Amerykanie wylądują na Księżycu przed upływem dekady. Inżynierowie musieli zbudować rakietę na tyle silną, by doleciała do Księżyca oraz statek kosmiczny zdolny odbyć tę podróż w obie strony. Pomocne okazały się doświadczenia twórcy rakiety V2, Wernhera von Brauna. Zbudowano rakietę Saturn V, która miała wynieść statki kosmiczne Apollo. Rakieta wraz z modułem załogowym...

39. source=legacy_mixed_paragraph_like reasons=single_word_repetition

   A – pierwsza litera alfabetu polskiego i łacińskiego. A A – oznaczenie jednostki fizycznej amper jednostka natężenia prądu elektrycznego zalegalizowana w układzie SI i MKSA jednostka siły magnetomotorycznej i napięcia magnetycznego, jednostka pochodna w układzie SI A, ang. absolute temperature – temperatura absolutna A – liczba masowa A – oznaczenie adeniny A – oznaczenie adenozyny także w kodzie genetycznym A – oznaczenie adrenaliny witamina A A – cyfra symbolizująca w układzie szesnastkowym i innych o podstawie większej od 10 decymalną wartość 10 A – nazwa dźwięku muzycznego, szóstego stopnia gamy C-dur A – oznaczenie akumulatora w asemblerze kilku mikroprocesorów (np. MOS 6502) A – oce...

40. source=legacy_long_article_like reasons=repeated_ngrams

   Andrzej Sapkowski (ur. 21 czerwca 1948 w Łodzi) – polski pisarz fantasy, z wykształcenia ekonomista. Twórca postaci wiedźmina. Jest najczęściej po Stanisławie Lemie tłumaczonym polskim autorem fantastyki. Życiorys Jego matka urodziła się w podkieleckiej wsi, a ojciec – pod Wilnem. Dziadek od strony ojca pochodził z drobnoszlacheckiej rodziny herbu Łodzia, wywodzącej się z Kowieńszczyzny, służył w armii rosyjskiej, po rewolucji 1917 wraz z rodziną powrócił na Wileńszczyznę, gdzie następnie pracował jako naczelnik poczty w Święcianach. Po zakończeniu II wojny światowej rodzina Sapkowskich zamieszkała w okolicach Nowej Soli, a następnie w Łodzi. Urodził się i mieszka w Łodzi. Od 9 lipca 2008...

41. source=legacy_mixed_paragraph_like reasons=single_word_repetition

   AL – Aeroklub Lubelski AL – Aeroklub Lwowski AL – Armia Ludowa, organizacja partyzancka w czasie II wojny światowej al. – skrót od słowa aleja, np. aleja Pokoju Al. – skrót od słowa aleje, np. Aleje Jerozolimskie .al – krajowa domena internetowa najwyższego poziomu przypisana dla stron internetowych Albanii AL – Albania (oznaczenie kodowe ISO 3166-1) Alabama – stan w USA (ISO 3166-2) Al – symbol pierwiastka glin (łac. aluminium) Sztuczne życie (AL z ang. Artificial Life) Al- – arabski rodzajnik (ال۔) Ål – gmina w Norwegii Al – powieść Williama Whartona A L – płyta Amandy Lear z 1985 roku Al – skrócone imię Albert (np. Al Gore), Alfred (np. Al Pacino), Alphonse (np. Al Capone, Al Bundy)

42. source=legacy_mixed_paragraph_like reasons=single_word_repetition

   As – symbol chemiczny arsenu as – karta do gry as – moneta w cesarstwie rzymskim as – dźwięk as – symbol attosekundy as – w astronomii, symbol pozaukładowej sekundy łuku (z ) As – polski samochód osobowy produkowany w latach 20. XX w. As – polski miniserial nakręcony w 2002 roku "As" – polski tygodnik ukazujący się do 1939 as – polecenie systemu Linux, wchodzące w skład zestawu programów binutils AS – system autonomiczny (ang. autonomous system) Ås – miasto i gmina w Norwegii Aš – miasto w Czechach Ås – miasto w Szwecji As – gmina w Belgii as myśliwski – honorowy tytuł w lotnictwie wojskowym As – dynastia bogów nordyckich As – superbohater, postać w filmie Hydrozagadka As (samolot) – proj...

43. source=legacy_long_article_like reasons=too_long,very_long_line

   Andrzej Witold Wajda (ur. 6 marca 1926 w Suwałkach, zm. 9 października 2016 w Warszawie) – polski reżyser filmowy i teatralny, w młodości aktywny jako malarz. W sezonie 1989/1990 dyrektor artystyczny Teatru Powszechnego w Warszawie. Czterokrotnie jego filmy były nominowane do Oscara dla najlepszego filmu nieanglojęzycznego. W latach 1989–1991 senator I kadencji. Kawaler Orderu Orła Białego. Popularność przyniosły mu filmy inicjujące tzw. polską szkołę filmową: Kanał oraz Popiół i diament, w których dokonywał rozrachunku z czasami II wojny światowej. Dokonał ekranizacji wielu dzieł literackich, jak Popioły, Brzezina, Wesele, Ziemia obiecana, Panny z Wilka i Pan Tadeusz. Współtworzył kino m...

44. source=legacy_long_article_like reasons=repeated_ngrams

   Anthony Minghella (ur. 6 stycznia 1954 w Ryde, Anglia, zm. 18 marca 2008 w Londynie) – brytyjski dramaturg i reżyser filmowy. Zobywca Oscara za film Angielski pacjent (1996). Życiorys Wczesne lata Jego rodzice byli Włochami. Studiował na University of Hull w Kingston upon Hull, a w 1981 r. rozpoczął karierę dramaturga piszącego sztuki dla teatru, radia i telewizji. W 1984 londyńscy krytycy teatralni, po zapoznaniu się z trzema sztukami Minghelli – A Little Like Drowning, Love Bites, Two Planks and a Passion – przyznali mu miano najbardziej obiecującego dramaturga roku. W dwa lata później ci sami krytycy uznali jego Made in Bangkok za najlepszą sztukę roku. Radiowa sztuka Minghelli Hang Up...

45. source=legacy_long_article_like reasons=very_long_line

   Adam Bernard Mickiewicz (ur. w Zaosiu lub Nowogródku, zm. 26 listopada 1855 w Stambule) – polski poeta, działacz polityczny, publicysta, tłumacz, filozof, działacz religijny, mistyk, organizator i dowódca wojskowy, nauczyciel akademicki. Obok Juliusza Słowackiego i Zygmunta Krasińskiego uważany za największego poetę polskiego romantyzmu (zaliczany do grona tzw. Trzech Wieszczów) oraz literatury polskiej, a nawet za jednego z największych na skalę europejską. Określany też przez innych jako poeta przeobrażeń oraz bard słowiański. Członek i założyciel Towarzystwa Filomatycznego, mesjanista związany z Kołem Sprawy Bożej Andrzeja Towiańskiego. Jeden z najwybitniejszych twórców dramatu romanty...

46. source=legacy_mixed_paragraph_like reasons=repeated_ngrams

   Ahenobarbus ( – miedziany oraz barba – broda; Miedzianobrody) – przydomek jednej z dwu głównych gałęzi rzymskiego rodu plebejskiego Domicjuszów. Jak głosiła legenda, Dioskurowie zwiastowali protoplaście rodu, Lucjuszowi Domicjuszowi, zwycięstwo Rzymian nad Latynami w 496 p.n.e. nad jeziorem Regillus i na potwierdzenie, że to co mówią jest prawdą, uderzyli jego czarną brodę i włosy, które natychmiast przemieniły się w rude. Zobacz Drzewo genealogiczne Domicjuszy Ahenobarbów. Gnejusz Domicjusz Ahenobarbus k.192 Gnejusz Domicjusz Ahenobarbus k.162 Gnejusz Domicjusz Ahenobarbus k.122 Gnejusz Domicjusz Ahenobarbus k.96 Lucjusz Domicjusz Ahenobarbus k.94 Gnejusz Domicjusz Ahenobarbus zm. 82 Luc...

47. source=legacy_long_article_like reasons=very_long_line

   Antropologia kulturowa (antropologia społeczna) – dyscyplina nauk społecznych badająca organizację kultury, rządzące nią prawa, historyczną zmienność i etniczną różnorodność kultur w celu skonstruowania ogólnej teorii kultury. Jest to jeden z głównych działów szeroko rozumianej antropologii, zajmuje się badaniem kultury we wszystkich jej przejawach. Antropologia kulturowa to dziedzina antropologii zajmująca się człowiekiem traktowanym jako indywiduum, jednostka ukształtowana przez społeczeństwo i twórca kultury. Zajmuje się zatem ludzkimi kulturami, wierzeniami, praktykami, wartościami, ideami, technologiami, ekonomiami, życiem społecznym i organizacją poznania. Antropolodzy kulturowi kor...

48. source=legacy_mixed_paragraph_like reasons=repeated_ngrams

   As myśliwski – tytuł honorowy nadawany pilotom myśliwskim, którzy zestrzelili określoną liczbę samolotów nieprzyjaciela, zwykle co najmniej 5, lub nieoficjalne określenie takiego pilota. System ewidencji zestrzeleń i swojego rodzaju rankingu pilotów, połączony z nadawaniem tytułów asa, powstał we Francji w czasie I wojny światowej, około 1916 – prawo do tytułu asa miał pilot, który zestrzelił 5 samolotów. Następnie system asów został przyjęty także przez inne kraje, czasami w zmodyfikowanej postaci. W Niemczech nie używano wówczas tego tytułu, chociaż prowadzono ewidencję zestrzeleń. W czasie I wojny światowej zmagania wybitnych pilotów i ich wyniki były wręcz obiektem zainteresowania pub...

49. source=legacy_long_article_like reasons=boilerplate_phrase

   Awers i rewers (łac.) – dwie strony zdobionego przedmiotu płaskiego, pokrytego jedno- lub dwustronnie malowidłem, grafiką lub drukiem, zawierającego płaskorzeźbę, wizerunek wykonany metodą rycia, kucia lub zdobionego w jeszcze inny sposób. Oba pojęcia funkcjonują wyłącznie razem, gdy w danym przedmiocie występuje swobodny dostęp do obu jego powierzchni, przy czym jedna z nich jest wyłączną lub główną stroną zawierającą przedstawiane treści. Tą główną lub ważniejszą stroną jest awers, natomiast rewers zawiera treści uzupełniające lub też jest po prostu „plecami” danego przedmiotu. W znaczeniu bardziej ogólnym awers to strona przednia czegoś, zwana też w tym znaczeniu stroną „prawą”, a rewe...

50. source=legacy_mixed_paragraph_like reasons=repeated_ngrams

   Ortografia Au – dwuznak występujący w języku francuskim Geografia Austria Au – gmina w kraju związkowym Vorarlberg, w powiecie Bregencja Au am Leithaberge – gmina targowa w kraju związkowym Dolna Austria, w powiecie Bruck an der Leitha Niemcy Au – gmina w kraju związkowym Badenia-Wirtembergia, w powiecie Breisgau-Hochschwarzweald Au am Rhein – gmina w kraju związkowym Badenia-Wirtembergia, w powiecie Rastatt Au in der Hallertau – gmina targowa w kraju związkowym Bawarii, w powiecie Freising Au-Haidhausen – okręg administracyjny Monachium Au (Sieg) – część gminy (Ortsteil) Windeck w kraju związkowym Nadrenia Północna-Westfalia, w powiecie Rhein-Sieg-Kreis Au (Sieg) – stacja kolejowa w Au (...

## Random Final Samples

1. source=legacy_mixed_paragraph_like

   Gmina Negotino (mac. Општина Неготино) – gmina w centralnej Macedonii Północnej. Graniczy z gminami: Sztip od północy, Koncze i Demir Kapija od wschodu, Gradsko i Rosoman od zachodu oraz z gminą Kawadarci od południa. Skład etniczny 92,48% – Macedończycy 3,26% – Serbowie 2,36% – Romowie 1,28% – Turcy 0,62% – pozostali W skład gminy wchodzą: miasto: Negotino; 18 wsi: Brusnik, Crweni Bregowi, Dołni Disan, Dubrowo, Dżidimirci, Gorni Disan, Janoszewo, Kalańewo, Kriwołak, Kurija, Lipa, Pepeliszte, Peszternica, Szeoba, Timjanik, Tremnik, Weszje, Wojszanci. Linki zewnętrzne oficjalna strona gminy Negotino Negotino

2. source=legacy_mixed_paragraph_like

   (10091) Bandaisan (1990 VD3) – planetoida z grupy pasa głównego asteroid okrążająca Słońce w ciągu 3,66 lat w średniej odległości 2,37 j.a. Odkryta 11 listopada 1990 roku. Zobacz też lista planetoid 10001–11000 lista planetoid Linki zewnętrzne Planetoidy pasa głównego Nazwane planetoidy Obiekty astronomiczne odkryte w 1990

3. source=legacy_mixed_paragraph_like

   NGC 7337 (również PGC 69344 lub UGC 12120) – galaktyka spiralna z poprzeczką (SBab), znajdująca się w gwiazdozbiorze Pegaza. Odkrył ją 10 września 1849 roku George Stoney – asystent Williama Parsonsa. Galaktyka ta jest członkiem grupy NGC 7331. W galaktyce tej zaobserwowano do tej pory jedną supernową – SN 1973O. Zobacz też Lista obiektów NGC Przypisy Linki zewnętrzne 7337 Galaktyki spiralne z poprzeczką Gwiazdozbiór Pegaza Grupa NGC 7331 Obiekty astronomiczne odkryte w 1849

4. source=legacy_mixed_paragraph_like

   Jan Kopałka ps. Antek, Antek z Woli, Żar, Hanka (ur. 10 maja 1914 w Warszawie, zm. 8 lipca 1999 w Łodzi) – harcmistrz, sierżant podchorąży Armii Krajowej, komendant Hufca „Wola” Grup Szturmowych. Wczesne lata Urodził się w rodzinie handlowca Adama Kopałki i Stanisławy z Grzybowskich. Uczęszczał do Publicznej Szkoły Powszechnej nr 23, a później Męskiego Gimnazjum i Liceum im. Tomasza Niklewskiego. Aby móc uczyć się w prywatnym gimnazjum i liceum pracował m.in. jako kasjer w Totalizatorze Towarzystwa Wyścigów Konnych na Polu Mokotowskim. Od 1934 r. był studentem Politechniki Warszawskiej na Wydziale Chemii. W 1930 roku został harcerzem 7. Warszawskiej Drużyny Harcerskiej im. gen. Karola Kni...

5. source=legacy_mixed_paragraph_like

   Jezioro Jeleń (kaszb. Jezoro Jeléń lub Gëlink) – jezioro wytopiskowe położone na Pojezierzu Bytowskim (powiat bytowski, województwo pomorskie). Jeleń zajmuje powierzchnię 88,9 ha, znajduje się na północnym obszarze miejskim Bytowa i służy przede wszystkim rekreacji i turystyce. Jezioro Jeleń jest bardzo czystym jeziorem. Zaliczane jest do jezior lobeliowych. Lobelia i poryblin rośnie tu dość licznie, występuje moczarka i rogatek, z ryb spotkać można szczupaka, węgorza, okonie, płocie. Obecnie nurkowanie na jeziorze jest zabronione, ze względu na ochronę przyrody. Jednak nie zawsze tak było – zakaz obowiązuje od 1999 r. Zakaz nurkowania zostaje zniesiony na podstawie UCHWAŁY NR XVIII/188/2...

6. source=legacy_mixed_paragraph_like

   Jezioro Karun (w starożytności stgr. Μοῖρις Moeris, – Buhajrat Karun) – jezioro w północnym Egipcie w gubernatorstwie Fajum o powierzchni 233 km². Położone ok. 80 km na południowy zachód od Kairu. Na jego obszarze i w okolicach utworzono Rezerwat jeziora Karun. W starożytności często wspominane i opisywane, m.in. przez Herodota (2,148 – 149) i Diodora Sycylijskiego (1, 66). Istnieją rozbieżności co do pochodzenia pierwotnej nazwy jeziora – Moeris: Pochodzi od Nimaatre, imienia tronowego Amenemhata III Wywodzi się od określenia Mewer (egip. Wielkie Jeziora), poświadczonego jako nazwa miasta nad jeziorem Przez starożytnych uważane za twór sztuczny, faktycznie jest naturalnym zbiornikiem wod...

7. source=legacy_mixed_paragraph_like

   Henry Vane (ur. ok. 1705 roku, zm. 6 marca 1758 roku) – brytyjski arystokrata i polityk, syn Gilberta Vane’a, 2. barona Barnard i Mary Randyll, córki Morgana Randylla. Był wielokrotnym członkiem Parlamentu z ramienia partii wigów. W latach 1726-1727 z okręgu Launceston, w latach 1727-1741 St Mawes, w latach 1741-1747 Ripon i w latach 1747-1753 Durham. W 1753 r. odziedziczył ojcowski tytuł barona Barnard i zasiadł w Izbie Lordów. Rok później król Jerzy II Hanowerski nadał mu tytuł hrabiego Darlington. W latach 1742-1744 był zastępcą Skarbnika Irlandii, w latach 1749-1755 był Lordem Skarbu, zaś w latach 1753-1758 Lordem Namiestnikiem Durham. Od 1742 r. był członkiem Irlandzkiej Tajnej Rady....

8. source=legacy_mixed_paragraph_like

   IC 2944 (znana także jako Mgławica Biegnący Kurczak i Mgławica Lambdy Centaura) – mgławica emisyjna powiązana z gromadą otwartą Collinder 249. Leży w granicach gwiazdozbioru Centaura w odległości około 6500 lat świetlnych. Została odkryta 5 maja 1904 roku przez Royala Frosta. IC 2944 rozciąga się na obszarze około 100 lat świetlnych. Jest to region gwiazdotwórczy (tzw. obszar H II). Cechują go globule Boka. Obraz uzyskany przez VLT po lewej jest zbliżeniem globul Boka odkrytych w IC 2944 przez południowoafrykańskiego astronoma A. Davida Thackeraya w 1950 roku. Globule te, znane jako Globule Thackeraya, są rozsiane w obszarze IC 2944 na tle świecącego na różowo gazu mgławicy. Znajdują się...

9. source=legacy_mixed_paragraph_like

   NGC 5555 (również PGC 51124) – galaktyka spiralna (Sb), znajdująca się w gwiazdozbiorze Panny. Odkrył ją Ormond Stone w 1886 roku. Zobacz też Lista obiektów NGC Przypisy Linki zewnętrzne 5555 Galaktyki spiralne Gwiazdozbiór Panny Obiekty astronomiczne odkryte w 1886

10. source=legacy_mixed_paragraph_like

   NGC 5885 (również PGC 54429) – galaktyka spiralna z poprzeczką (SBc), znajdująca się w gwiazdozbiorze Wagi. Odkrył ją William Herschel 9 maja 1784 roku. Zobacz też Lista obiektów NGC Przypisy Linki zewnętrzne 5885 Galaktyki spiralne z poprzeczką Gwiazdozbiór Wagi Obiekty astronomiczne odkryte w 1784

11. source=legacy_mixed_paragraph_like

   (74161) 1998 QF101 – planetoida z pasa głównego asteroid okrążająca Słońce w ciągu 4,36 lat w średniej odległości 2,67 j.a. Odkryta 26 sierpnia 1998 roku. Zobacz też lista planetoid 74001–75000 lista planetoid Linki zewnętrzne Planetoidy pasa głównego Nienazwane planetoidy Obiekty astronomiczne odkryte w 1998

12. source=legacy_mixed_paragraph_like

   Konrad II Wirtemberski (zm. 1143) – pan na Zamku Wirtemberg. Panował w latach 1110-1143. Był synem niejakiego Werntruda oraz Liutgard siostry Konrada I. Po śmierci Konrada I odziedziczył zamek. Pojął za żonę Jadwigę. 12 maja 1110 roku wraz z małżonką podarował ziemię w okolicach Göppingen klasztorowi z Blaubeuren. W grudniu 1122 roku jako świadek cesarza Henryka V udał się do Spiry (Był tam tytułowany Hrabia). Władcy Wirtembergii Wirtembergowie Zmarli w 1143

13. source=legacy_mixed_paragraph_like

   NGC 5721 (również PGC 52346) – galaktyka soczewkowata (S0), znajdująca się w gwiazdozbiorze Wolarza. Odkrył ją 16 kwietnia 1855 roku R.J. Mitchell – asystent Williama Parsonsa. Zobacz też Lista obiektów NGC Przypisy Linki zewnętrzne 5721 Galaktyki soczewkowate Gwiazdozbiór Wolarza Obiekty astronomiczne odkryte w 1855

14. source=legacy_mixed_paragraph_like

   (73326) 2002 JH102 – planetoida z pasa głównego asteroid okrążająca Słońce w ciągu 3,63 lat w średniej odległości 2,36 j.a. Odkryta 9 maja 2002 roku. Zobacz też lista planetoid 73001–74000 lista planetoid Linki zewnętrzne Planetoidy pasa głównego Nienazwane planetoidy Obiekty astronomiczne odkryte w 2002

15. source=legacy_mixed_paragraph_like

   Xeneretmus – rodzaj morskich ryb skorpenokształtnych z rodziny lisicowatych. Klasyfikacja Gatunki zaliczane do tego rodzaju : Xeneretmus latifrons Xeneretmus leiops Xeneretmus ritteri Xeneretmus triacanthus Przypisy Lisicowate

16. source=legacy_mixed_paragraph_like

   Józef Karol Lasocki (ur. 4 listopada 1907 w Olejowie, zm. 19 sierpnia 1996 w Łodzi) – polski dyrygent, kompozytor, pedagog i organizator życia muzycznego. Życiorys W latach 1929–1935 studiował na Wydziale Pedagogicznym i Teoretycznym w Państwowym Konserwatorium Muzycznym w Warszawie, m.in. u Kazimierza Sikorskiego. W latach 1935–1939 pracował jako nauczyciel w Szkole Muzycznej i Instytucie Muzycznym w Łucku. Działał także jako dyrygent zespołów amatorskich - chórów i orkiestr: w latach 1926–1929 Towarzystwa Teatrów i Chórów Ludowych w Międzyrzeczu, w latach 1930–1931 Związku Nauczycielstwa Polskiego w Równem, w latach 1931–1939 Państwowego Gimnazjum i Liceum w Łucku, a od 1935 do 1939 Łuc...

17. source=legacy_mixed_paragraph_like

   Okręty US Navy o nazwie USS "Winslow". Nazwa pierwszych dwóch pochodzi od kontradmirała Johna Ancrum Winslowa. Nazwa trzeciego pochodzi od Johna Winslowa i jego dalekiego krewnego – admirała Camerona Winslowa: Pierwszy "Winslow" (TB-5) był kutrem torpedowym służącym podczas wojny amerykańsko-hiszpańskiej. Drugi "Winslow" (DD-53) był niszczycielem typu O’Brien przyjętym do służby w 1915, służącym podczas I wojny światowej i skreślonym ze służby w 1922. Trzeci "Winslow" (DD-359) był niszczycielem typu Porter przyjętym do służby w 1937 i służącym w czasie II wojny światowej. Przeklasyfikowany na AG-127 w 1945 i wycofany ze służby w 1950. Wisconsin

18. source=legacy_mixed_paragraph_like

   Gołąbek fiołkowozielony (Russula ionochlora Romagn.) – gatunek grzybów należący do rodziny gołąbkowatych (Russulaceae). Systematyka i nazewnictwo Pozycja w klasyfikacji według Index Fungorum: Russula, Russulaceae, Russulales, Incertae sedis, Agaricomycetes, Agaricomycotina, Basidiomycota, Fungi. Nazwę polską podała Alina Skirgiełło w 1991 r. Morfologia Kapelusz Fioletowo–zielonkawy z różowym lub żółtym odcieniem. Średnica 4–8 cm. Blaszki Białe, u starszych owocników jasnokremowe. Trzon Biały, masywny z wiekiem pusty. Miąższ Smak łagodny. Zapach słaby, kwaskowaty. Pod wpływem siarczanu żelaza staje się różowo-czerwony. Wysyp zarodników Białokremowy. Występowanie i siedlisko Występuje niema...

19. source=legacy_mixed_paragraph_like

   Vieja – rodzaj słodkowodnych ryb okoniokształtnych z rodziny pielęgnicowatych (Cichlidae). Występowanie Rodzaj Vieja obejmuje gatunki występujące w Ameryce Środkowej. Podział systematyczny Do rodzaju należą następujące gatunki: Vieja bifasciata (Steindachner, 1864) Vieja breidohri (Werner & Stawikowski, 1987) Vieja fenestrata (Günther, 1860) Vieja guttulata (Günther, 1864) Vieja hartwegi (Taylor & Miller, 1980) Vieja maculicauda (Regan, 1905) Vieja melanurus (Günther, 1862) Vieja zonata (Meek, 1905) Przypisy Cichlinae

20. source=legacy_long_article_like

   Joe Lieberman, właśc. Joseph Isadore Lieberman (ur. 24 lutego 1942 w Stamfordzie) – amerykański polityk, demokrata, senator ze stanu Connecticut (wybrany w 1988 i ponownie w 1994 i 2000). W wyborach prezydenckich roku 2000 był kandydatem na wiceprezydenta Stanów Zjednoczonych wystawionym przez Partię Demokratyczną. Był pierwszym Amerykaninem pochodzenia żydowskiego wystawionym przez jedną z głównych partii jako kandydat na wiceprezydenta. Wczesne lata i edukacja Jego rodzicami byli Henry Lieberman (3 kwietnia 1915 – 3 stycznia 1986), syn żydowskich emigrantów z Polski, i Marcia Manger (1 października 1914 – 25 czerwca 2005), o korzeniach żydowsko-austriackich. Liebermanowie posiadali Hami...

21. source=legacy_long_article_like

   Lwówek Śląski – przelotowa stacja kolejowa w Lwówku Śląskim, w Polsce. Stacja powstała 15 października 1885, wraz z budową linii z Gryfowa Śląskiego. Odgrywała ona dawniej w ruchu osobowym znaczącą rolę jako węzeł kolejowy, z którego odchodziły linie w czterech kierunkach: do Gryfowa Śląskiego, Jeleniej Góry, Jerzmanic-Zdroju oraz Zebrzydowej. Stacja przynależy do oddziału regionalnego PKP Polskich Linii Kolejowych we Wrocławiu i Zakładu Linii Kolejowych w Wałbrzychu. Położenie Stacja jest położona w centralnej części Lwówka Śląskiego, na wschód od Starego Miasta, ok. 600 m od Placu Wolności. Ograniczają ją ulice: Andrzeja Struga (od wschodu), Betleja (droga wojewódzka nr 364, od południa...

22. source=legacy_mixed_paragraph_like

   Jacoba Francisca Maria „Cobie” Smulders (ur. 3 kwietnia 1982 w Vancouver) – kanadyjska aktorka i modelka. Wystąpiła m.in. w roli Robin Scherbatsky w serialu Jak poznałem waszą matkę oraz Marii Hill z produkcji Filmowego Uniwersum Marvela. Życiorys Dzieciństwo Urodziła się w Vancouver w Kolumbii Brytyjskiej, jest córką Holendra i Brytyjki. Imię „Jacoba” zawdzięcza swojej holenderskiej pra-ciotce. Jako dziecko chciała być lekarzem lub biologiem morskim, w szkole średniej zaczęła zyskiwać zainteresowanie osób pojawiających się w produkcjach szkolnych. W 2000 ukończyła Lord Byng Liceum z wyróżnieniem. Kariera Po zakończeniu nauki w liceum została odkryta przez agencję nastoletnich modelek i z...

23. source=legacy_mixed_paragraph_like

   Bajanchongor () – miasto w Mongolii, stolica administracyjna ajmaku bajanchongorskiego, położone 620 km na południowy zachód od stolicy kraju Ułan Bator. W 2010 roku liczyło 29,8 tys. mieszkańców. Prawie cała populacja reprezentowana jest przez Chałchasów. Leży na wysokości około 1850 m n.p.m. Ajmak powstał w 1942, ale stolicę ajmaku przeniesiono do Bajanchongoru w 1961. W latach 80. XX w. działał w mieście kombinat spożywczy, cegielnia, fabryki: odzieży i obuwia. Obecnie (2008) w mieście jest Muzeum Ajmaku i Muzeum Przyrodnicze, a także klasztor lamajski założony w 1991. 20 km od centrum dzisiejszego miasta do 1937 istniał duży i aktywny klasztor lamajski, znany jako ośrodek wydawniczy t...

24. source=legacy_mixed_paragraph_like

   Brachttal – miejscowość i gmina w Niemczech, w kraju związkowym Hesja, w rejencji Darmstadt, w powiecie Main-Kinzig. Przypisy Powiat Main-Kinzig Gminy w Hesji

25. source=legacy_mixed_paragraph_like

   NGC 1864 (również ESO 56-SC79) – gromada otwarta, znajdująca się w gwiazdozbiorze Złotej Ryby, w Wielkim Obłoku Magellana. Odkrył ją John Herschel 23 grudnia 1834 roku. Zobacz też asocjacja gwiazdowa Lista obiektów NGC Przypisy Linki zewnętrzne 1864 Gromady otwarte Gwiazdozbiór Złotej Ryby Wielki Obłok Magellana Obiekty astronomiczne odkryte w 1834

26. source=legacy_mixed_paragraph_like

   (73310) 2002 JE76 – planetoida z pasa głównego asteroid okrążająca Słońce w ciągu 3,58 lat w średniej odległości 2,34 j.a. Odkryta 11 maja 2002 roku. Zobacz też lista planetoid 73001–74000 lista planetoid Linki zewnętrzne Planetoidy pasa głównego Nienazwane planetoidy Obiekty astronomiczne odkryte w 2002

27. source=legacy_mixed_paragraph_like

   Dąbrowa Puzdrowska (dodatkowa nazwa w j. kaszub. Dąbrowa Pùzdrowskô) – wieś w Polsce, położona w województwie pomorskim, w powiecie kartuskim, w gminie Sierakowice Wieś leży na Pojezierzu Kaszubskim. Wchodzi w skład sołectwa Puzdrowo. W latach 1975–1998 Dąbrowa Puzdrowska administracyjnie należała do województwa gdańskiego. Przed 2023 r. miejscowość była częścią wsi Puzdrowo. Z kart historii Od końca I wojny światowej wieś znajdowała się w granicach Polski (powiat kartuski). Do 1918 roku obowiązującą nazwą niemieckiej administracji dla Dąbrowy Puzdrowskiej było Dombrowo. Podczas okupacji niemieckiej w 1942 r. nazwa Dombrowo została przez nazistowskich propagandystów niemieckich (w ramach...

28. source=legacy_long_article_like

   Kazimierz Aleksandrowicz ps. Huragan (ur. 3 kwietnia 1915 w Warce, zm. 20 października 1982 w Radomiu) – członek Służby Zwycięstwu Polski, dowódca grupy sabotażowo-dywersyjnej Organizacji Wojskowej PPS i Socjalistycznej Organizacji Bojowej, dowódca partyzancki Armii Krajowej w Radomskiem. Życiorys Młodość i udział w kampanii wrześniowej Był synem Jana Aleksandrowicza i Natalii z domu Kubryn. Uczył się w szkole powszechnej w Warce. W 1929 r. przeniósł się do Warszawy, gdzie podjął pracę w firmie swojego wujka, Zakładzie Mechaniki Precyzyjnej. Jednocześnie uczęszczał na Kursy Maturalne im. Marcina Konopnickiego, na których w 1936 r. zdał maturę. Następnie zamieszkał w Radomiu, gdzie zatrudn...

29. source=legacy_mixed_paragraph_like

   NGC 7043 (również PGC 66385 lub UGC 11704) – galaktyka spiralna z poprzeczką (SBa), znajdująca się w gwiazdozbiorze Pegaza. Odkrył ją Albert Marth 18 sierpnia 1863 roku. Zobacz też Lista obiektów NGC Przypisy Linki zewnętrzne 7043 Galaktyki spiralne z poprzeczką Gwiazdozbiór Pegaza Obiekty astronomiczne odkryte w 1863

30. source=legacy_mixed_paragraph_like

   NGC 7338 – prawdopodobnie gwiazda podwójna znajdująca się w gwiazdozbiorze Pegaza. Jej składniki mają jasność obserwowaną 14,6 i 16,4. Zaobserwował ją Wilhelm Tempel w 1882 roku i skatalogował jako obiekt typu „mgławicowego”. Zobacz też Lista obiektów NGC Przypisy 7338 Gwiazdy podwójne Gwiazdozbiór Pegaza

31. source=legacy_mixed_paragraph_like

   Barbara Mikołajewska (ur. w grudniu 1947 r. w Polsce, od 1990 roku zamieszkała w USA) – socjolożka, tłumaczka, pisarka. Życiorys Studiowała w Instytucie Socjologii Wydziału Filozoficznego na Uniwersytecie Warszawskim, broniąc swej pracy doktorskiej napisanej pod opieką profesora Stefana Nowaka w 1979 roku. W latach 1970-1972 pracownik naukowy Politechniki Warszawskiej; w latach 1972-2002 pracownik naukowy Uniwersytetu Warszawskiego. Jej wcześniejsze prace dotyczą zagadnień grup etnicznych i mikrosocjologii, podczas gdy późniejsze poświęcone są głównie girardowskiej interpretacji starożytnych hinduskich i japońskich tekstów religijnych. Jest tłumaczką książki René Girarda Szekspir: teatr z...

32. source=legacy_mixed_paragraph_like

   Robert M. Solovay (ur. 1938 w Brooklynie) – amerykański matematyk specjalizujący się w logice matematycznej. Emerytowany profesor matematyki na Uniwersytecie Kalifornijskim w Berkeley. Znany głównie za wkład w teorię mnogości. Członek Amerykańskiej Akademii Sztuki i Nauki (ang. American Academy of Arts and Sciences). Doktoryzował się w 1964 na Uniwersytecie Chicagowskim pod kierunkiem Saundersa Mac Lane’a. Wypromował kilkunastu doktorów, wśród jego wychowanków są m.in. Matthew Foreman i William Woodin. Ważniejsze osiągnięcia Około roku 1965, Robert Solovay i Stanley Tennenbaum rozwinęli metodę forsingu wprowadzając forsing iterowany, aby udowodnić niezależność hipotezy Suslina. We współcz...

33. source=legacy_mixed_paragraph_like

   (74368) 1998 WG41 – planetoida z pasa głównego asteroid okrążająca Słońce w ciągu 5,19 lat w średniej odległości 3 j.a. Odkryta 18 listopada 1998 roku. Zobacz też lista planetoid 74001–75000 lista planetoid Linki zewnętrzne Planetoidy pasa głównego Nienazwane planetoidy Obiekty astronomiczne odkryte w 1998

34. source=legacy_mixed_paragraph_like

   Mięsień odwodziciel krótki kciuka () – w anatomii człowieka płaski, najbardziej powierzchowny mięsień kłębu, położony między szeregiem bliższym kości nadgarstka a bliższym paliczkiem kciuka. Przyczep proksymalny ma na troczku zginaczy, guzku kości łódeczkowatej, kości czworobocznej większej i w przedłużeniu ścięgna odwodziciela długiego kciuka. Następnie poprzez krótkie ścięgno, które na swym przebiegu obejmuje trzeszczkę promieniową stawu śródręczno-paliczkowego, przytwierdza się do bocznego brzegu podstawy bliższego paliczka kciuka. Unaczyniony jest przez gałąź dłoniową powierzchowną od tętnicy promieniowej, a unerwiony przez nerw pośrodkowy. Jego funkcją jest odwodzenie i przeciwstawia...

35. source=legacy_mixed_paragraph_like

   CD+G, CD+Graphics – specjalny rodzaj płyty kompaktowej, który oprócz dźwięku zawiera dane graficzne. Dysk może być odgrywany na zwykłych odtwarzaczach CD oraz na odtwarzaczach CD+G, które mogą wyświetlać zapisane obrazy (zwykle odtwarzacz CD+G podłączony jest do zestawu telewizyjnego lub monitora komputerowego); funkcja ta jest wykorzystywana przede wszystkim do prezentowania tekstu piosenek dla wykonawców karaoke. W każdym sektorze są 2352 bajty (24×98) danych dźwiękowych i 96 bajtów danych subkanałowych. 96 bajtów danych subkanałowych w każdym sektorze zawiera cztery pakiety po 24 bajty każdy: 1 bajt dla polecenia, 1 bajt dla instrukcji, 2 bajty parzystości Q, 16 bajtów danych, 4 bajty...

36. source=legacy_mixed_paragraph_like

   Dynastia amoryjska – zwana też frygijską, dynastia cesarzy bizantyjskich panująca w latach 820-867, wywodząca się z Amorion w Anatolii. Należeli do niej cesarze: Michał II (820-829), Teofil (829-842), Michał III (842-867). Za panowania dynastii amoryjskiej definitywnie zakończył się okres wielkich konfliktów religijnych, (przywrócenie kultu ikon), ugruntowano również pozycję Bizancjum na Zachodzie poprzez chrystianizację Bułgarii (866) oraz misję Cyryla i Metodego na Morawach (863). !

37. source=legacy_mixed_paragraph_like

   Powerade – napój izotoniczny produkowany przez koncern The Coca-Cola Company od roku 1988. Przeznaczony jest przede wszystkim dla sportowców oraz osób, które wykonują zajęcia wymagające długotrwałego, dużego wysiłku fizycznego, tracąc z wydzielanym przez skórę potem sole mineralne i mikroelementy niezbędne do prawidłowego funkcjonowania organizmu. Zawody Powerade, jako marka napoju izotonicznego jest sponsorem tytularnym zawodów w Kolarstwie Górskim MTB o nazwie Powerade MTB Marathon. Jest także jednym ze sponsorów klubu piłkarskiego Śląsk Wrocław. Oprócz tego propaguje sport i aktywność fizyczną sponsorując i organizując różnorakie zawody i festyny sportowe. Skład woda dekstroza maltodek...

38. source=legacy_mixed_paragraph_like

   (21270) Otokar (1996 OK) – planetoida z pasa głównego asteroid okrążająca Słońce w ciągu 3,26 lat w średniej odległości 2,2 j.a. Odkryta 19 lipca 1996 roku. Zobacz też lista planetoid 21001–22000 lista planetoid Linki zewnętrzne Planetoidy pasa głównego Nazwane planetoidy Obiekty astronomiczne odkryte w 1996

39. source=legacy_mixed_paragraph_like

   Pseudoblennius – rodzaj ryb skorpenokształtnych z rodziny głowaczowatych. Klasyfikacja Gatunki zaliczane do tego rodzaju : Pseudoblennius argenteus Pseudoblennius cottoides Pseudoblennius marmoratus Pseudoblennius percoides Pseudoblennius totomius Pseudoblennius zonostigma Przypisy Głowaczowate

40. source=legacy_mixed_paragraph_like

   Emil Bratro (ur. 31 października 1878 w Podgórzu, zm. 21 grudnia 1944 we Lwowie) – inżynier budowy dróg, profesor zwyczajny robót ziemnych, budowy dróg i tuneli Politechniki Lwowskiej, dziekan Wydziału Inżynieryjnego PLw., długoletni redaktor Czasopisma Technicznego, członek korespondent Akademii Nauk Technicznych, członek Rady Technicznej przy Ministrze Komunikacji. Życiorys Urodził się w 1878 w Krakowie-Podgórzu. Ukończył szkołę realną z egzaminem dojrzałości. W 1896 ukończył we Lwowie szkołę średnią i podjął studia na Wydziale Inżynierii Politechniki Lwowskiej. W lipcu 1898 złożył I egzamin rządowy. Dyplom inżyniera uzyskał w 1901. W latach 1901–1929 był zatrudniony w państwowej admini...

41. source=legacy_mixed_paragraph_like

   Jacob de Gheyn III, znany również jako Jacob III de Gheyn – obraz olejny z 1632 roku autorstwa holenderskiego malarza Rembrandta. Opis obrazu Portret przedstawia holenderskiego twórcę miedziorytu Jacoba de Gheyn III i należy do pary obrazów. Drugim obrazem w parze jest portret przyjaciela Gheyna, Mauritsa Huygensa, który ma na sobie podobny strój i zwrócony jest w przeciwnym kierunku. Dwójka przyjaciół zleciła Rembrandtowi wykonanie portretów – artysta uczynił to, korzystając z tego samego kawałka dębowej deski. Obrazy nie miały być pokazywane razem, lecz portret Gheyna po jego śmierci został przekazany Huygensowi. Rembrandt użył tego samego kawałka dębowej deski do wykonania swojego auto...

42. source=legacy_long_article_like

   Współczesna Proza Światowa – seria wydawnicza Państwowego Instytutu Wydawniczego, ukazująca się od 1968. Popularnie nazywana „czarną serią” była jedną z najpopularniejszych w Polsce serii prezentujących współczesną literaturę piękną. W ramach serii publikowane były dzieła przedstawicieli nowych nurtów literackich, uznanych debiutantów i najgłośniejszych autorów na świecie. Od 2015 PIW wznowił serię pod nazwą Proza światowa. Wybrane pozycje wydane w serii Norman Mailer Amerykańskie marzenie Muriel Spark Ballada o Peckham Rye, Pełnia życia panny Brodie E.L. Doctorow Billy Bathgate, Jezioro Nurów, Ragtime, Witajcie w Ciężkich Czasach Vladimir Nabokov Blady ogień, Dar, Lolita, Maszeńka, Pnin,...

43. source=legacy_mixed_paragraph_like

   Claude Louis Berthollet, również Claude-Louis Berthollet (ur. 9 grudnia 1748 w Talloires, zm. 6 listopada 1822 w Arcueil) – francuski chemik. Życiorys Wraz z Antoine'em Lavoisierem i innymi opracował nomenklaturę chemiczną (Méthode de nomenclature chimique, 1787), która jest podstawą współczesnego nazewnictwa związków chemicznych. Prowadził również badania nad barwnikami oraz wybielaczami (wprowadził do użycia chlor jako środek wybielający). Odkrył skład amoniaku. Chloran potasu (KClO3), mocny utleniacz, znany jest również jako sól Bertholleta. Berthollet zwalczał koncepcję Josepha Prousta stałości składu związku chemicznego. Z tej przyczyny niestechiometryczne związki chemiczne nazywane...

44. source=legacy_long_article_like

   Pornografia – polski film fabularny z 2003 roku w reżyserii Jana Jakuba Kolskiego, na podstawie powieści Witolda Gombrowicza pod tym samym tytułem. Akcja rozgrywa się w 1943 roku, głównie w majątku ziemiańskim na Sandomierszczyźnie, gdzie zjawia się para głównych bohaterów Witold i Fryderyk. W pozornie odseparowanym od wojennej zawieruchy dworku, Fryderyk rozpoczyna dziwną grę, której celem jest połączenie ze sobą córki gospodarza i młodego syna rządcy z sąsiedniego majątku. Przy okazji zmaga się z własnymi demonami z przeszłości. Film został dobrze oceniony przez krytyków, którzy wśród jego głównych zalet wymieniali rolę Krzysztofa Majchrzaka, charakterystyczną muzykę Zygmunta Konieczneg...

45. source=legacy_mixed_paragraph_like

   Droga wojewódzka nr 374 (DW374) – droga wojewódzka w województwie dolnośląskim o długości 33 kilometrów łącząca Jawor ze Świebodzicami. Droga biegnie przez powiaty jaworski i świdnicki. Historia numeracji Na przestrzeni lat trasa posiadała różne oznaczenia i klasyfikacje: Miejscowości leżące przy trasie DW374 Jawor Niedaszów Rogoźnica Wieśnica Strzegom Grochotów Świebodzice Uwagi 374

46. source=legacy_mixed_paragraph_like

   Konfiguracja CDC () – jedna z dwóch, obok CLDC (), konfiguracji środowiska Java ME zdefiniowanych przez Java Community Process (dokumenty JSR-36 i JSR-218). Konfiguracja przeznaczona jest dla m.in. wideotelefonów, konsoli gier, zestawów audio-wideo, PDA. Wymagania CDC w wersji 1.1 przeznaczona jest na urządzenia posiadające: możliwość połączenia z siecią, minimum 512 kB dostępnej pamięci RAM, od 128 do 256 kB dostępnej pamięci ROM. Różnice wobec CLDC W stosunku do mocno ograniczonej konfiguracji CLDC dodano z JVM takie funkcjonalności jak: uruchamianie kodu natywnego dzięki JNI (ang. Java Native Interface), serializację obiektów, definiowanie przez użytkownika loaderów klas, obsługę mecha...

47. source=legacy_mixed_paragraph_like

   NGC 7193 – grupa gwiazd znajdująca się w gwiazdozbiorze Pegaza. Odkrył ją John Herschel 13 października 1825 roku. Klasyfikowana jest jako gromada otwarta lub pozostałość po dużej gromadzie otwartej. Jej odległość od Słońca szacuje się na od około 1,6 tys. do 3,5 tys. lat świetlnych. Niektóre starsze katalogi astronomiczne uznawały ją za nieistniejącą, np. Revised New General Catalogue (RNGC). Zobacz też Lista gromad otwartych Drogi Mlecznej Lista obiektów NGC Przypisy Linki zewnętrzne 7193 Gromady otwarte Gwiazdozbiór Pegaza Obiekty astronomiczne odkryte w 1825

48. source=legacy_mixed_paragraph_like

   66 w nauce liczba atomowa dysprozu obiekt na niebie Messier 66 galaktyka NGC 66 planetoida (66) Maja 66 w kalendarzu 66. dniem w roku jest 7 marca (w latach przestępnych jest to 6 marca). Zobacz też co wydarzyło się w roku 66. Zobacz też dzielnik i cechy podzielności symbolika liczb 0066

49. source=legacy_mixed_paragraph_like

   Jachting (ang. yachting) – żeglowanie za pośrednictwem jachtu. Szerzej jest to sztuka sterowania łodzią i wykorzystywania siły wiatru za pomocą żagli dla celów sportowych lub rekreacyjno-turystycznych. Potocznie określa się tą nazwą żeglowanie od portu do portu, w porze dziennej przy ładnej pogodzie. W języku angielskim określenie yachting jest pojęciem szerszym, oznaczającym ogólnie żeglarstwo. Polskie określenie jachting bardziej odpowiada angielskiemu cruising. Zobacz też Żeglarstwo Żegluga Marynistyka Przypisy Linki zewnętrzne Benedykt Bohdan Grabowski: Historia Jachtingu w zarysie, Toruńskie Towarzystwo Tradycji Morskich Żeglarstwo Turystyka

50. source=legacy_mixed_paragraph_like

   Chociński Młyn (kaszb. Chòcyńsczi Młin lub też Stari Mòst, Chòczińsczi Młin, niem. Chotzenmühl) – wieś kaszubska w Polsce położona w województwie pomorskim, w powiecie chojnickim, w gminie Chojnice, nad rzeką Chociną. Wieś jest częścią składową sołectwa Swornegacie. W latach 1975–1998 miejscowość administracyjnie należała do województwa bydgoskiego. Chociński Młyn jest położony na terenie Zaborskiego Parku Krajobrazowego przy trasie drogi wojewódzkiej nr 236. Połączenie z centrum Chojnic umożliwiają autobusy komunikacji miejskiej (linia nr 1A). Zabytki leśniczówka z poł. XIX w. o skromnych cechach klasycystycznych, nakryta dachem naczółkowym, obok chałupa zrębowa, zniszczony tartak wodny...
