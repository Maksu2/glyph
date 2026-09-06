# Glyph-100M Dataset v2.3.1 Report

Generated: 2026-06-06T20:46:02.952740+00:00

No training was started.

## Verdict

v2.3.1 is cleaner but now marginal for a full 50k run. Prefer a short preflight or more clean sources.

## Outputs

- train bin: `data/processed/glyph100_v2_3_1_train.bin`
- val bin: `data/processed/glyph100_v2_3_1_val.bin`
- docs JSONL: `data/processed/glyph100_v2_3_1_docs.jsonl`
- metadata: `data/processed/glyph100_v2_3_1_metadata.json`
- tokenizer: `data/processed/tokenizer.model`

## v2.3 vs v2.3.1

| metric | v2.3 | v2.3.1 |
|---|---:|---:|
| total tokens | 300,001,394 | 175,938,499 |
| FineWeb2 tokens | 160,959,241 | 36,896,346 |
| Wikipedia share | 42.64% | 72.71% |
| FineWeb2 share | 53.65% | 20.97% |
| 50k epochs | 2.73 | 4.66 |

- tokens removed from v2.3: 124,062,895
- FineWeb2 tokens removed: 124,062,895

## Source Mix

| source | docs | tokens | share | train tokens | val tokens |
|---|---:|---:|---:|---:|---:|
| `wolne_lektury` | 1,525 | 3,143,341 | 1.79% | 3,126,624 | 16,717 |
| `wikipedia_pl` | 184,466 | 127,929,637 | 72.71% | 127,166,956 | 762,681 |
| `allegro_summaries_source` | 539 | 1,368,381 | 0.78% | 1,364,804 | 3,577 |
| `wikibooks_pl` | 5,388 | 4,328,329 | 2.46% | 4,312,133 | 16,196 |
| `wikisource_pl` | 1,543 | 2,272,465 | 1.29% | 2,263,878 | 8,587 |
| `fineweb2_pl` | 45,533 | 36,896,346 | 20.97% | 36,727,767 | 168,579 |

## Rejection Reasons

```json
{
  "low_page_quality_score": 184484,
  "commerce_terms": 39131,
  "multi_snippet_ellipsis": 27678,
  "too_short": 27229,
  "page_repetition_penalty": 22722,
  "list_heavy_page": 16862,
  "clickbait_or_related_links": 12312,
  "forum_or_comment_layout": 10069,
  "table_or_separator_heavy": 10009,
  "bad_url_path": 9740,
  "repeated_ngrams": 8853,
  "prices_present": 8763,
  "snippet_or_boilerplate_page": 7702,
  "gossip_or_celebrity_content": 6007,
  "service_landing_language": 4255,
  "cookie_privacy_boilerplate": 4195,
  "short_syndicated_blurb": 2773,
  "directory_or_listing_content": 2440,
  "blog_or_snippet_domain": 2263,
  "gossip_domain": 2186,
  "loan_or_credit_spam": 2065,
  "ad_boilerplate": 2062,
  "travel_listing_domain": 1289,
  "directory_or_listing_domain": 1087,
  "forum_domain": 1060,
  "commerce_domain": 1011,
  "social_or_comments_domain": 806,
  "gaming_clickbait_domain": 643,
  "listing_or_image_board_domain": 359,
  "single_word_repetition": 295,
  "spammy_generated_domain": 271,
  "entertainment_listing_domain": 250,
  "image_listing_domain": 250,
  "contact_directory_domain": 242,
  "fandom_or_game_wiki_domain": 180,
  "too_much_punctuation_or_symbols": 69,
  "manual_or_boilerplate_domain": 31,
  "fandom_or_roleplay_domain": 31,
  "book_piracy_or_listing_domain": 22,
  "qa_domain": 21,
  "service_landing_domain": 17,
  "classifieds_domain": 12,
  "fandom_or_category_boilerplate": 9,
  "low_unique_word_ratio": 2,
  "very_long_line": 2,
  "product_page_domain": 1
}
```

## Training Math

- stage 3 / 50k total: 819,200,000 tokens = 4.66 epochs
- 100k total: 1,638,400,000 tokens = 9.31 epochs
- 200k total: 3,276,800,000 tokens = 18.62 epochs

## Quality Notes

- Legacy remains 0.
- FineWeb2 is filtered through domain hard rejects, URL rejects, content boilerplate patterns and a simple page-quality classifier.
- v2.3.1 is intentionally smaller than v2.3 if the cleanup works.
- Remaining risk: accepted FineWeb2 can still contain normal web/news style and occasional mild portal residue. Inspect samples before any 50k run.

## Final Random Samples

1. `fineweb2_pl` `www.polskieradio.pl` www.polskieradio.pl (tokens=1099, score=0.9593)

   Oscar za "Pociągi pod specjalnym nadzorem" to największy sukces w karierze reżyserskiej Jiřego Menzla. Duża w tym zasługa świetnego scenariusz opartego na opowiadaniu Bohumila Hrabala, choć w filmie widać też bardzo dużą zręczność reżyserską młodego twórcy. Aż trudno uwierzyć, że nie śmiał on marzyć o prawdziwej karierze reżysera, bo wydawało mu się, że jest mało zdolny i zostanie najwyżej czyimś asystentem. - Kiedy byłem w wojsku, nie pamiętam czy Evald Schorm, czy Jan Němec powiedzieli, że przygotowują film według opowiadania Hrabala - wspominał Jiří Menzel w audycji Aldony Wołłk w Polskim Radiu. - Ale nie byłem dobrym uczniem, nie wiedziałem, że będę kiedyś sam kręcił filmy. Miałem niską samoocenę. Ale powiedzieli, że mógłbym to z nimi robić. Nikt mnie nie pytał o dyplom - po prostu pozwolili mi pracować. Mamy takie powiedzenie, że kiedy się szczęście zmęczy, to usiądzie i na ośle - dodawał Menzel. 27:50 Pociągi.mp3 Reżyser opowiada o pracy nad swoimi filmami. "Jiri Menzel". Audycja Aldony Wołłk z cyklu "O wszystkim z kulturą". (PR, 08.03.2016) Niespodziewanie więc spadło na Me...

2. `fineweb2_pl` `tylkokobiecyfutbol.pl` tylkokobiecyfutbol.pl (tokens=463, score=0.9676)

   Futbol jest po to, by łamać stereotypy. Mówią, że kobieta w męskiej szatni przynosi pecha, ten mit pada. Mury już skruszyła Chan Yuen – Ting prowadząc najpierw Eastern Sports Club do mistrzostwa Hongkongu w zeszłym roku, a obecnie w Lidze Mistrzów AFC. Teraz trend ten doszedł do Europy. Właśnie 42-letnia włoska legenda kobiecej piłki Patrizia Panico została pierwszym w historii swojego kraju selekcjonerem męskiej reprezentacji. Objęła kadrę do lat 16. O żadnym trzęsieniu ziemi nie mowy. Panico pracuje z męską kadrą młodzieżową jako drugi trener od wakacji zeszłego roku, a teraz po prostu naturalnie ją poprowadzi po przejściu Zorattiego do U-19. Sama Panico według wywiadów nie widzi w tym nic nadzwyczajnego, jest profesjonalistką w każdym calu, a w dodatku ze sporym autorytetem. Uważa, że dodatkowo pomoże to w walce ze stereotypami. Problemów nie widzą również trenowani chłopcy ani federacja. Największy „sprzeciw” wśród kibiców, jeśli już wydawał się płynąć od zatwardziałych 50+ latków. Wielu z nich jednak przycichło, kiedy odkryło, że Panico ma najwięcej występów w reprezentacji (...

3. `fineweb2_pl` `www.poznan.pl` www.poznan.pl (tokens=1407, score=0.969)

   Trenerski gigant wioślarstwa 29 czerwca podczas uroczystej Sesji Rady Miasta Poznania nagrodę sportową w kategorii trenerskiej otrzymał Aleksander Wojciechowski. Trener wioślarstwa zasłużył na tę nagrodę jak nikt inny. Związany jest z Poznaniem przez całą karierę zawodniczą i trenerską, a od grudnia 1996 roku nieprzerwanie trenuje też kadrę narodową mężczyzn wioseł krótkich. Był opiekunem osad wioślarzy podczas sześciu startów w igrzyskach olimpijskich: Sydney 2000, Ateny 2004, Pekin 2008, Londyn 2012, Rio de Janeiro 2016 i Tokio 2020. Jego podopieczni zawsze pływali w finałach A. Pracę z najmłodszymi adeptami wioślarstwa rozpoczął w swoim klubie Tryton Poznań. Natomiast poważna praca trenerska rozpoczęła się od 1982 roku, kiedy przeniósł się do AZS AWF Poznań. Pod koniec 1996 roku rozpoczął pracę w Polskim Związku Towarzystw Wioślarskich. Wojciechowski odmłodził kadrę i zmienił osady. Dwójka Adam Korol i Marek Kolbowicz cały czas startowała w finałach mistrzostw świata, w 1999 roku zdobyła brązowy medal. W igrzyskach w Sydney Korol i Kolbowicz zajęli 6. miejsce. Czwórka podwójna,...

4. `wikipedia_pl` `pl.wikipedia.org` Bratków (województwo dolnośląskie) (tokens=306, score=0.9575)

   Bratków (niem. Blumberg) – wieś w Polsce położona w województwie dolnośląskim, w powiecie zgorzeleckim, w gminie Bogatynia. Położenie Bratków to niewielka wieś leżąca na Pogórzu Izerskim, na Wyniosłości Działoszyńskiej, na prawym brzegu Nysy Łużyckiej, pomiędzy wsiami Krzewina na północy i Posada na południowwym-zachodzie, na wysokości około 250-260 m n.p.m. Podział administracyjny W latach 1975–1998 miejscowość administracyjnie należała do województwa jeleniogórskiego. Historia Nie wiadomo dokładnie jakie są początki Bratkowa, pierwsza wzmianka o miejscowości pochodzi z XV wieku. Wieś zawsze miała typowo rolniczy charakter i słabo się rozwijała, w 1936 roku było tu 97 domów. W 1875 roku wybudowano linię kolejową i przystanek, co jednak nie wpłynęło korzystnie na rozwój wsi. Po 1945 roku w Bratkowie zlokalizowano jedną z pierwszych strażnic granicznych WOP. Wieś poważnie wyludniła się, rozwój nastąpił dopiero w latach 60. XX wieku, kiedy rozpoczęto budowę Elektrowni Turów. W 1978 roku było tu 28 gospodarstw rolnych, w 1988 roku ich liczba zmalała do 25. Zabytki W Bratkowie zachowa...

5. `wikipedia_pl` `pl.wikipedia.org` Karczówka (województwo lubuskie) (tokens=148, score=0.9734)

   Karczówka () – wieś w Polsce położona w województwie lubuskim, w powiecie żagańskim, w gminie Brzeźnica. W latach 1975–1998 miejscowość administracyjnie należała do województwa zielonogórskiego. Nazwa W księdze łacińskiej Liber fundationis episcopatus Vratislaviensis (pol. Księga uposażeń biskupstwa wrocławskiego) spisanej za czasów biskupa Henryka z Wierzbna w latach 1295–1305 miejscowość wymieniona jest w zlatynizowanej formie Kalcruch. Zabytki Do wojewódzkiego rejestru zabytków wpisany jest: kościół filialny pod wezwaniem MB Bolesnej, z końca XVII wieku. Demografia Liczba mieszkańców miejscowości w poszczególnych latach:

6. `wikipedia_pl` `pl.wikipedia.org` Kutyski (tokens=299, score=0.9325)

   Kutyski – wieś w Polsce położona w województwie mazowieckim, w powiecie sokołowskim, w gminie Kosów Lacki. Wieś była początkowo przysiółkiem wsi Wyszomierz i Niepiekły. W połowie XVI wieku nosiła nazwę Wyszomierz Wypychy. Nazwę wzięła od spotykanego w rodzie Wyszomierskich herbu Rawicz przydomku Kutaska. W 1523 roku występuje w Księgach Grodzkich Drohickich Stanisław Kutaska z Wyszomierza. W 1567 roku na pospolite ruszenie w Radoszkowicach stawiło się ze wsi Wyszomierz Wypychy 9 zbrojnych, wśród nich Szczęsny Kutyska. W roku 1600 Zofia i Dorota występują o spadek po ojcu - Feliksie Kutaska, synu Mateusza Kutaska. W roku 1605 po raz pierwszy pojawia się nazwisko Kutyski. W 1606 roku wieś występuje pod nazwą Wyszomierz - Kutaski. Po zniszczeniu w czasie "potopu" sąsiednich Niepiekłów, w Kutaskach następuje skokowy przyrost liczby mieszkańców. Później nazwę zmieniano na Kuteski lub Kutyski.[źródło: księgi grodzkie drohickie, AGAD]. W latach 1975–1998 miejscowość administracyjnie należała do województwa siedleckiego. Mieszkańcy wyznania rzymskokatolickiego należą do parafii św. Wojcie...

7. `wikipedia_pl` `pl.wikipedia.org` Starszy szeregowy (tokens=713, score=0.9332)

   Starszy szeregowy (do 1977 r. starszy szeregowiec) – do 2022 najwyższy stopień w korpusie szeregowych w Wojsku Polskim. Niższym stopniem jest szeregowy, a wyższym starszy szeregowy specjalista. Żeby go posiadać, trzeba m.in. posiadać przygotowanie zawodowe, np. zasadniczą szkołę zawodową, odbytą zasadniczą służbę wojskową w pełnym wymiarze (są wyjątki zwalniające z tego obowiązku), przejść testy sprawnościowe i psychologiczne, być osobą niekaraną. Równorzędnym stopniem jest stopień starszego marynarza w Marynarce Wojennej. Odpowiednikiem starszego szeregowego w artylerii był do 5 lipca 1994 bombardier. Stopień starszego szeregowego zamiast starszego szeregowca został wprowadzony rozkazem nr 18/MON Ministra Obrony Narodowej z 8 grudnia 1976 wprowadzającym z dniem 15 października 1977 do użytku w Siłach Zbrojnych PRL Regulamin służby wewnętrznej Sił Zbrojnych PRL, sygn. Szt.Gen. 791/76. W regulaminie tym w wykazach stopni wojskowych podano nazwę najniższego stopnia wojskowego – szeregowy. Zmiana ta została uwzględniona również w ustawie o powszechnym obowiązku obrony Polskiej Rzeczy...

8. `fineweb2_pl` `chojnice24.pl` chojnice24.pl (tokens=1305, score=0.9595)

   'Jak w komorze gazowej' Wielki mróz i wielki smog. W niedzielę (17.01) wieczorem stężenie pyłów zawieszonych PM 2,5 w centrum miasta zostało przekroczone o ponad 1500 procent! Katastrofalna jakość powietrza odczuwalna była też w innych rejonach Chojnic. Ekolodzy biją na alarm, a z ratusza płynie deklaracja o kolejnym programie do walki ze smogiem. Rozprawić się z kopciucami ma ZGM. Urzędnicy przypominają również o programie skierowanym do indywidualnych mieszkańców, tj. "Stop dla smogu". Reklama | Czytaj dalej » Widząc temperatury sięgające nawet - 20 st. C. chojniczanie dorzucili do pieców. Efekt był praktycznie natychmiastowy. W niedzielę (17.01) wieczorem, całe miasto zanotowało gigantyczne przekroczenia stężenia pyłów zawieszonych. Najgorzej sytuacja przedstawiała się na ul. Składowej (PM 2,5 1504 porc., PM 10 977 proc. ) i Starym Mieście (PM 2,5 1513 proc., PM 10 1038 proc.). Dzisiaj, kiedy temperatury zelżały przekroczenia sięgają kilkuset procent. Stop dla smogu. W ramach programu do tej pory wymieniono 5 kotłów... - To czy ten smog, będzie taki straszny, zależy tylko od na...

9. `allegro_summaries_source` `huggingface.co` Wydatki socjalne służą zaspokojeniu potrzeb partykularnych kosztem społecznych (tokens=1857, score=0.9812)

   Wydatki socjalne służą zaspokojeniu potrzeb partykularnych kosztem społecznych Egoizm a sfera publiczna RYS. MICHAŁ KORSUN JANUSZ A. MAJCHEREK Polityka socjalna, również ta realizowana obecnie w Polsce, nie służy zaspokajaniu potrzeb ogólnospołecznych, lecz indywidualnych, realizuje więc cele nie mniej partykularne niż liberalny model działalności gospodarczej, obwiniany o sankcjonowanie egoizmu i lekceważenie problemów społecznych. Poziom życia i standardy cywilizacyjne społeczeństwa odzwierciedlane są nie tylko w wielkości dochodów i zasobów oraz wartości dóbr posiadanych przez indywidualnych obywateli lub będących w ich zasięgu. Zależą także od ilości i wartości wspólnych zasobów i zgromadzonych razem dóbr oraz dostępu do nich. Komfort życia opiera się nie tylko na tym, co ma się we własnym domu lub na prywatnym koncie, lecz uzależniony jest również od stanu wszelkich obiektów i instytucji użyteczności publicznej, z których trzeba lub musi się korzystać, poczynając od ulicznych trotuarów i skwerów, przez infrastrukturę komunikacyjną czy służby publiczne, skończywszy na zbiorach...

10. `fineweb2_pl` `wrc.net.pl` wrc.net.pl (tokens=538, score=0.9669)

   Niczym bumerang powraca temat pt. radio w samochodzie i opłata abonamentu. Dochodzi bowiem do różnego rodzaju sytuacji, które nawet ciężko skomentować. Wszystko po to, aby jak najwięcej osób zapłaciło za swój odbiornik w pojeździe. Ustawa jedno, Poczta Polska drugie, a prawo i czysta logika to trzecie. Przypomina to nieco walkę Don Kichota z wiatrakami. Radio w samochodzie, zło niekonieczne Jak donosi coraz więcej lokalnych mediów i można wyczytać na internetowych forach, listonosze Poczty Polskiej robią zdjęcia zaparkowanym samochodom, które mają zamontowane radio. Następnie sprawdzane jest to, czy ich właściciel opłaca abonament RTV. Brzmi niczym scena z kabaretu, ale okazuje się, że to rzeczywistość życia w Polsce. To nie pierwsze tego typu przypadki. Niedawno było dość głośno o podobnej sytuacji w Rudzie Śląskiej, gdzie mężczyzna po sesji fotograficznej wykonanej przez listonosza, następnie otrzymał pismo z Wydziału Abonamentu RTV Centrum Obsługi Finansowej Poczty Polskiej. W nim była informacja o wszczęciu postępowania administracyjnego dotyczącego abonamentu RTV. Ustawa niem...

11. `fineweb2_pl` `faktykrakowa.pl` faktykrakowa.pl (tokens=1709, score=0.9454)

   Jako drugie co do wielkości miasto w Polsce, Kraków to tętniące życiem centrum miejskie z mnóstwem potencjalnych klientów usług ridehailingowych. Historyczny urok miasta, dynamiczny rynek pracy i rozwinięty sektor turystyczny stwarzają sprzyjające warunki dla rozwoju kierowców. Kluczem do sukcesu na tym rynku jest zrozumienie lokalnego popytu na przejazdy oraz unikalnych cech krajobrazu transportowego Krakowa. Pierwszym krokiem do zwiększenia zarobków jako kierowca Bolt, Uber czy Free Now jest zapoznanie się z popularnymi miejscami docelowymi i godzinami szczytu. Wiedza kiedy i gdzie szukać pasażerów jest kluczowa. Niektóre z najpopularniejszych miejsc docelowych w Krakowie obejmują Rynek Główny, Zamek Królewski na Wawelu, Kazimierz, Stare Miasto, Trakt Królewski oraz centra biznesowe i biurowe. Szczyty popytu występują zwykle podczas porannych i wieczornych godzin, w weekendy oraz podczas świąt, wydarzeń czy festiwali. Zrozumienie lokalnych wzorców ruchu i parkowania jest ważne dla efektywnej obsługi i unikania opóźnień. Wąskie ulice i historyczna architektura Krakowa sprawiają,...

12. `fineweb2_pl` `gdansk-gdynia-sopot.pl` gdansk-gdynia-sopot.pl (tokens=750, score=0.9489)

   Literatura od wieków pełni funkcję wirtualnego przewodnika, prowadząc czytelników przez niewidzialne ścieżki wyobraźni. Jednak co by było, gdybyśmy mogli przemierzać te same szlaki, które zainspirowały wielkich pisarzy do stworzenia ich niezapomnianych dzieł? Szlaki literackie to idealna okazja do odkrywania miejsc, które stały się tłem dla wyjątkowych opowieści. Wyruszając w podróż po tych miejscach, przenosimy się do świata literatury, gdzie fikcja miesza się z rzeczywistością. Jednym z najbardziej znanych szlaków literackich jest Droga Jacquesa Cocteau we Francji. Ta trasa wiedzie przez miasta i wsie, które zainspirowały francuskiego pisarza Jacques’a Cocteau do napisania jego znanych utworów. Od wąskich uliczek Saint-Tropez po malownicze wybrzeże na Lazurowym Wybrzeżu, trasa ta pozwala wczuć się w atmosferę, która kiedyś otaczała samego Cocteau. Innym fascynującym szlakiem jest Droga Johna Steinbecka w Stanach Zjednoczonych. Ta trasa, nazwana na cześć noblisty literatury Johna Steinbecka, przechodzi przez różnorodne miejsca, które stały się tłem dla jego dzieł. Od klimatycznej...

13. `fineweb2_pl` `debica.naszemiasto.pl` debica.naszemiasto.pl (tokens=362, score=0.948)

   Przebudowa dworca PKP w Dębicy „W chwili obecnej dopracowywana jest ostateczna wizualizacja przebudowy dworca PKP w Dębicy , która będzie gotowa najpóźniej w ciągu 2 tygodni. Ustalamy detale projektu – mówi architekt Paweł Kośmicki , zajmujący się przygotowaniem projektu przebudowy. Na mocy porozumienia między PKP a władzami miejskimi na potrzeby miasta nieodpłatnie zostaną udostępnione pomieszczenia na terenie dworca. „W ramach dobrej współpracy z władzami PKP do dyspozycji otrzymamy kilka pomieszczeń. Planujemy utworzenie w nich świetlicy dla dzieci i młodzieży w której młodzi ludzie będą mogli spędzić czas w oczekiwaniu na pociąg lub autobus oraz Punktu Informacyjnego” – mówi Paweł Wolicki, burmistrz Dębicy. W opracowanym projekcie przebudowy nie ma zmian kubatury budynku, który pozostanie w dotychczasowym kształcie. Według wstępnych ustaleń między władzami miasta a PKP na parterze budynku, po lewej stronie tuż przy wejściu głównym do budynku dworca na powierzchni kilkudziesięciu metrów zlokalizowany zostanie Punkt Informacyjny, natomiast na I piętrze na powierzchni blisko 170...

14. `wikipedia_pl` `pl.wikipedia.org` Zgniłe miasteczka (tokens=322, score=0.9673)

   Zgniłe miasteczka (ang. rotten boroughs) – podupadłe i wyludnione miejscowości w Anglii, które do 1832 były okręgami wyborczymi do Izby Gmin. Prawo to przyznano im w średniowieczu, za czasów ich świetności. Bywało to dogodne dla rządu. Rodziny takie jak Pelhamowie w Susseksie, w Norfolk, Courtenayowie w hrabstwie Devon, Napierowie w hrabstwie Dorset czy Cartwrightowie w Northampton poprzez znajomości z okolicznymi kupcami i prawnikami przez swoich dzierżawców kontrolowały w praktyce elekcję w swojej okolicy. Gdy Robert Walpole był brytyjskim premierem (1721–1742), głosy dla niego zdobywał jego ministerialny kolega Thomas Pelham-Holles, 1. książę Newcastle. W 1832 na mocy reformy ordynacji wyborczej (zwanej reformą Greya) 52 „zgniłe miasteczka” utraciły swoje mandaty na rzecz innych miast – często ośrodków, które powstały podczas rewolucji przemysłowej w XVIII w. Procent wyborców podniósł się wtedy z 3 do 5 w skali kraju. Charles Dickens w powieści „Klub Pickwicka” obnaża mechanizm pozyskiwania głosów w prowincjonalnych okręgach wyborczych. Nieco mniej drastyczna była sytuacja tzw....

15. `wikipedia_pl` `pl.wikipedia.org` Daniel Clementinus (tokens=179, score=0.9603)

   Daniel Clementinus (zm. 1644 w Chmielniku) – pastor kalwiński, pisarz, minister zboru kalwińskiego w Górach, kaznodzieja w Jodłówce (obecnie Szczepanowice (powiat tarnowski), Wiatowicach, Górach i na końcu w Chmielniku. Pisarz, polemizował z braćmi polskimi, w szczególności z Jonaszem Szlichtyngiem. Autor wydanej w roku 1623 książki Antilogiae at Absurda (Sprzeciwieństwa i niesłuszności wypływające z Opinijej Socynistów Ponurzonych), w której polemizował m.in. z Grzegorzem Pawłem z Brzezin. Był wychowankiem alumnatu założonego przez wojewodę bełskiego Rafała Leszczyńskiego.

16. `fineweb2_pl` `www.zskrzemien.pl` www.zskrzemien.pl (tokens=486, score=0.9618)

   16-06-22 Jeśli dziecko uczęszcza do szkoły publicznej, można zapytać nauczyciela, czy jest jakaś dodatkowa praca z matematyką, którą dziecko może wykonywać po lekcjach. Na przykład może istnieć kółko matematyczne lub grupa naukowa, do której można się zapisać razem z dzieckiem. Można też zapisać dziecko na zajęcia matematyczne online. W zależności od wieku dziecka może ono także brać udział w konkursach matematycznych, aby sprawdzić swoje umiejętności. Jeśli dziecko nie uczęszcza do szkoły publicznej, można poprosić nauczyciela dziecka o książki, łamigłówki i gry związane z matematyką, które można wykorzystać w domu. Można też zapytać nauczyciela, czy może polecić jakieś ćwiczenia matematyczne online, którymi dziecko może się zajmować w wolnym czasie. Oto kilka innych zadań, które możesz wykonać, aby uczynić naukę matematyki dla swojego dziecka bardziej interesującą i wciągającą. Stwórz grę planszową, w której gracze będą musieli rozwiązywać zadania matematyczne, aby przejść do następnego poziomu. Jeśli Twoje dziecko jest osobą kreatywną, daj mu zeszyt, w którym może rysować probl...

17. `fineweb2_pl` `wirlandii.pl` wirlandii.pl (tokens=665, score=0.9691)

   Według raportu Tourism Ireland, w internecie odnotowuje się stały wzrost negatywnych opinii od turystów odwiedzających Irlandię. Po tym jak organizacja Tourism Ireland wyraziła zaniepokojenie, na Lonely Planet pojawił się artykuł o kosztach wizyty w Irlandii. Jednocześnie monitoring stron internetowych wykazał wzrost ilości skarg w mediach społecznościowych od turystów odwiedzających Irlandię. Przy czym 55 z 68 negatywnych opinii zgłoszonych w ciągu jednego tygodnia dotyczyło rosnących kosztów. 42% wszystkich skarg dotyczyło w szczególności wynajmu samochodu. Organizację Tourism Ireland zaniepokoił szczególnie artykułu z „biblii” podróżniczej Lonely Planet, który ostrzegał turystów przed „rosnącymi kosztami hotelów” i tym, jak wynajem samochodu może „znacznie obniżyć budżet”. W reakcji na tę publikację, opublikowano raport specjalny dla poszczególnych krajów na temat rosnących kosztów w turystyce, w Irlandii. W raporcie tym stwierdzono, że partnerzy handlowi we Francji są szczególnie zaniepokojeni „ciągłymi problemami z cenami i dostępnością”. „Podwyżki cen w restauracjach również...

18. `wikipedia_pl` `pl.wikipedia.org` Jan Długosz z Niedzielska (tokens=193, score=0.9403)

   Jan Długosz z Niedzielska pod Wieluniem herbu Wieniawa (zm. 1444) – rycerz, starosta nowokorczyński i brzeźnicki. Ojciec 12 synów z dwiema żonami, w tym 3 synów o imieniu Jan (między innymi Jana Długosza, kronikarza). Uczestnik bitwy pod Grunwaldem, walczył w chorągwi ziemi wieluńskiej za co otrzymał starostwo brzeźnickie. Pochowany w Wieluniu, w krypcie nieistniejącego już kościoła św. Michała. Jan Długosz z Niedzielska Starostowie nowokorczyńscy (Zjednoczone Królestwo Polskie) Starostowie Zjednoczonego Królestwa Polskiego Szlachta Korony Królestwa Polskiego Uczestnicy wojny polsko-krzyżackiej 1409–1411 (strona polska) Polscy rycerze Ludzie związani z Wieluniem Ludzie związani z Parzymiechami Zmarli w 1444

19. `fineweb2_pl` `dosenatu.org.pl` dosenatu.org.pl (tokens=1019, score=0.9676)

   Grudzień 13, 2019 przez admin Sd Okrgowy w Katowicach skaza Romana S, byego zomowca, oskaronego o strzelanie do grnikw w KWK Wujek na pocztku stanu wojennego w 1981 roku, na 3,5 roku wizienia. Byy zomowiec, ktry ma niemieckie obywatelstwo, by cigany Europejskim Nakazem Aresztowania. W maju zosta zatrzymany w Chorwacji. Wyrok jest nieprawomocny. Obrona Romana S. zapowiedziaa zoenie apelacji. – Trudno zgodzi si w caoci z argumentacj sdu, na pewno bdzie wywiedziona apelacja – powiedzia dziennikarzom obroca oskaronego Tomasz Pirg. W jego ocenie, kara wymierzona jego klientowi jest zbyt wysoka. Na pocztku procesu adwokat zoy wniosek o umorzenie postpowania, sd si na to nie zgodzi. – Nadal nie zgadzam si z argumentacj sdu w tym zakresie i bdzie to jedna z podstaw apelacji – wskaza. Uczestnicy krwawo stumionego 38 lat temu protestu uznali wyrok za sprawiedliwy, prokurator jest zadowolony z uznania winy. Jeszcze przed rozpoczciem rozprawy w sdzie doszo do awantury. Sdzia wezwa stra. Osoby zwizane z Adamem Somk, dziaaczem opozycji w PRL oraz byym posem, przyniosy do sdu transparenty; krzyc...

20. `wikipedia_pl` `pl.wikipedia.org` Grzegorz Przemyk (tokens=1705, score=0.9592)

   Grzegorz Przemyk (ur. 17 maja 1964 w Warszawie, zm. 14 maja 1983 tamże) – polski poeta, syn poetki Barbary Sadowskiej i Leopolda Przemyka. Uczeń XVII LO im. Frycza Modrzewskiego. Został pobity przez milicjantów, co doprowadziło do jego śmierci. Zabójstwo i konsekwencje Zabójstwo i pogrzeb Grzegorz Przemyk został zatrzymany przez milicję 12 maja 1983, na placu Zamkowym w Warszawie, kiedy wraz z kolegami świętował zdaną maturę. Wraz z nim zatrzymano kolegę Cezarego Filozofa. Żaden z nich nie miał przy sobie dokumentów. Przemyk został zabrany do pobliskiego komisariatu MO przy ul. Jezuickiej 1/3, gdzie został pobity przez 3 funkcjonariuszy. Po powrocie do domu zaczął odczuwać bardzo silne bóle w rejonie brzusznym. Karetka zabrała go do szpitala. Zmarł po dwóch dniach od pobicia w wyniku ciężkich urazów jamy brzusznej, czyli 3 dni przed swoimi 19 urodzinami. W szpitalu operowali go dr Leszek Karpiński, Filip Grzejszczyk oraz Marek Bagniewski. Ten ostatni zeznawał później o sprawie w angielskim parlamencie. 19 maja biskup Władysław Miziołek odprawił mszę za Przemyka w kościele św. Stan...

21. `fineweb2_pl` `defence24.pl` defence24.pl (tokens=675, score=0.9735)

   Tegoroczne międzynarodowe Targi Technologii Obronnych i Bezpieczeństwa (IDET) odbywają się w dniach 6-8 października w Brnie w Czechach. Rheinmetall oferując KF41 Lynx dla czeskiej armii przygotował także kompleksową ofertę przemysłową. Przedstawiciele niemieckiego koncernu zapowiadają włączenie spółek czeskiej zbrojeniówki w globalny łańcuch dostaw tych wozów. Zainteresowanie w tej kwestii miało wyrazić już kilkanaście czeskich firm. Obecnie konstrukcja ta oprócz Czech jest oferowana w Australii i USA, na jej wybór zdecydowały się już sąsiednie Węgry. Pierwszym ze wspomnianych systemów jest zdalnie sterowany moduł uzbrojenia Main Sensor Slaved Armament, który został zainstalowany na stropie wieży niemieckiego bwp. Jego uzbrojenie może stanowić karabin maszynowy kal. 7,62 mm lub wielkokalibrowy karabin maszynowy kal. 12,7 mm, a także granatnik automatyczny kal. 40 mm. Głównym zadaniem tego modułu jest zwalczanie drugorzędnych celów dla głównego uzbrojenia wozu zarówno na lądzie jak i w powietrzu. Innym systemem uzbrojenia stosowanym w Lynxie jest armata automatyczna MK30-2/ABM kal...

22. `wikibooks_pl` `pl.wikibooks.org` Wikijunior:Polska/Trybunał Stanu (tokens=621, score=0.9699)

   Trybunał Stanu (w skrócie TS) to specjalny sąd, który ma za zadanie pilnować, żeby najważniejsze osoby w państwie (np. Prezydent) działały zgodnie z prawem. Jeśli złamią Konstytucję lub inne ważne przepisy w związku ze swoimi obowiązkami, Trybunał Stanu może je za to ukarać. Kto może być sądzony przed Trybunałem Stanu Przed Trybunałem Stanu mogą stanąć osoby, które zajmują w państwie najwyższe stanowiska. To są: Prezydent Rzeczypospolitej Polskiej. Prezes Rady Ministrów (Premier) i ministrowie. Prezes Narodowego Banku Polskiego (odpowiada za sprawy związane z pieniędzmi w państwie). Prezes Najwyższej Izby Kontroli (osoba kontrolująca, jak wydawane są pieniądze publiczne). Członkowie Krajowej Rady Radiofonii i Telewizji. Naczelny Dowódca Sił Zbrojnych (tylko w czasie wojny). Posłowie i senatorowie (za naruszenie pewnych zakazów). Kto wchodzi w skład Trybunału Stanu W skład Trybunał Stanu wchodzą: Przewodniczący: zawsze jest nim Pierwszy Prezes Sądu Najwyższego (czyli szef wszystkich sędziów w najważniejszym sądzie w Polsce). 2 zastępców przewodniczącego 16 sędziów: są to osoby wybi...

23. `fineweb2_pl` `www.smakizpolski.com.pl` www.smakizpolski.com.pl (tokens=417, score=0.9776)

   Historyczna stopa zwrotu, choć bardzo istotna, nie powinna być jedynym kryterium wyboru funduszu inwestycyjnego. Przed powierzeniem komuś naszych pieniędzy, warto sprawdzić reputację danego Towarzystwa Funduszy Inwestycyjnych, choćby zasięgając opinii w internecie oraz analizując dotyczące go komunikaty sprawującej pieczę nad rynkiem finansowym Komisji Nadzoru Finansowego. Bezpieczeństwo naszych pieniędzy jest najważniejsze, dlatego trzeba poświęcić trochę czasu na analizę strategii inwestycyjnej funduszu. Warto na przykład sprawdzić stopień koncentracji środków funduszu w papiery jednego emitenta lub wybrany segment rynku. Jeśli okaże się, że przykładowo proponowany nam fundusz jest w dużym procencie skoncentrowany na inwestycji w kilka spółek, to trzeba mieć świadomość, że jest to być może inwestycja potencjalnie zyskowna, ale na pewno bardziej ryzykowna. Bezpieczniejszym rozwiązaniem jest także wybór tych funduszy, które mogą inwestować na większej ilości rynków (np. w kilku krajach). Taka potencjalna dywersyfikacja wewnątrz funduszu pomaga chronić przed niemiłymi niespodzianka...

24. `wikipedia_pl` `pl.wikipedia.org` Stosunki amerykańsko-fińskie (tokens=7574, score=0.9739)

   Stosunki amerykańsko-fińskie – relacje międzynarodowe łączące Stany Zjednoczone i Finlandię. Historia Wojny napoleońskie – kontekst Wojny napoleońskie oddziałały bezpośrednio na północną Europę, powodując poważne zmiany wewnątrzpolityczne oraz daleko idące przesunięcia granic państwowych. Szwecja i Dania – państwa istniejące wówczas w tym regionie – zostały włączone do walk zbrojnych do obozów przeciwnych i zapłaciły za to wysoką cenę. Jako część ówczesnego państwa szwedzkiego Finlandia stała się terenem długotrwałych walk i okupacji wojskowej. Ostatecznie przeszła w skład innego państwa – Rosji. 20 stycznia 1809 roku car Aleksander I zwołał na dzień 22 marca 1809 roku do miasteczka Porvoo Parlament Finlandii. Parlament zebrał się 25 marca, a cztery dni później Aleksander I wygłosił uroczystą przemowę z potwierdzeniem głównych obietnic i jej pisemny tekst wręczył przewodniczącemu stanu szlacheckiego (zawierał on deklarację poszanowania praw, obyczajów, pozycji dotychczasowej religii, wysokości podatków itd.). W deklaracjach tych użyto kilkakrotnie określenia „naród fiński”, co mia...

25. `wikipedia_pl` `pl.wikipedia.org` Chauzon (tokens=85, score=0.9577)

   Chauzon – miejscowość i gmina we Francji, w regionie Owernia-Rodan-Alpy, w departamencie Ardèche. Według danych na rok 1990 gminę zamieszkiwały 224 osoby, a gęstość zaludnienia wynosiła 21 osób/km² (wśród 2880 gmin regionu Rodan-Alpy Chauzon plasuje się na 1403. miejscu pod względem liczby ludności, natomiast pod względem powierzchni na miejscu 1070.).

26. `fineweb2_pl` `tvn24.pl` tvn24.pl (tokens=825, score=0.9229)

   "Wywrócił" samolot na drugą stronę. Słynna rzeźba Romana Stańczaka w Zachęcie Samolot wywrócony na drugą stronę, czyli rzeźba "Lot" autorstwa Romana Stańczaka, pojawi się wkrótce w Zachęcie. Wszystkie elementy maszyny widoczne zwyczajowo we wnętrzu znalazły się na jej poszyciu. Artysta własnoręcznie przenicował całą instalację. Wystawa będzie dostępna dla publiczności od 28 kwietnia do 3 lipca. Premiera "Lotu" odbyła się w 2019 roku, w Pawilonie Polskim przygotowanym w ramach 58. Międzynarodowej Wystawy Sztuki w Wenecji. To 15-metrowy, wywrócony na lewą stronę samolot. Całe jego wnętrze, czyli elementy kokpitu i pokładu oraz siedzenia pasażerów są widoczne na zewnątrz, a skrzydła wraz z poszyciem samolotu znalazły się w środku. Przygotowanie maszyny trwało kilka miesięcy. Artysta używał wyłącznie własnych rąk i młota. "Lot" autorstwa Romana Stańczaka będzie można zobaczyć wkrótce w Zachęcie Narodowej Galerii Sztuki. Otwarcie wystawy zaplanowano na 28 kwietnia i będzie ona dostępna dla publiczności aż do 3 lipca 2022 roku. Stańczak przechodzi "na drugą stronę rzeczywistości" W zapo...

27. `wikipedia_pl` `pl.wikipedia.org` Bitwa pod Newbury (1643) (tokens=396, score=0.9748)

   Pierwsza bitwa pod Newbury – starcie zbrojne, które miało miejsce 20 sierpnia 1643 podczas angielskiej wojny domowej (1642–1651). Bitwa stoczona została w Enborne i Wash Common graniczące z Newbury, między armią Parlamentu dowodzoną przez hrabiego Essex, a armią Rojalistów dowodzoną osobiście przez króla Anglii Karola I, któremu towarzyszył książę Rupert oraz Jacob Astley. Obie strony posiadały podobne siły. Karol I miał około 8 000 piechoty i 6 000 jazdy, podczas gdy Essex miał 10 000 piechoty, 4 000 jazdy. Obie strony miały po około 20 dział. Pomimo że armia Rojalistów przybyła pod Newbury przed armią Parlamentu, Essex potrafił lepiej wykorzystać warunki terenowe, zabezpieczając pozycje na wzgórzu górującym nad polem bitwy. Kawaleria Rojalistów pobiła kawalerię Parlamentu, nie była jednak zdolna do wyparcia piechoty z jej pozycji na wzgórzu. Bitwa trwała cały dzień, zażarte zmagania ciągnęły się, ale żadna ze stron nie potrafiła przechylić zwycięstwa na swoją stronę. Król Karol, przerażony ilością przelanej krwi, odrzucił sugestie swoich doradców by kontynuować bitwę następnego...

28. `wikipedia_pl` `pl.wikipedia.org` Władcy Danii (tokens=141, score=0.9552)

   Władcy Danii (do X wieku) Do X wieku – zobacz hasło legendarni władcy Danii. Królestwo Danii (X wiek – 1397) Skjoldungowie Ynglingowie Estrydsenidzi Folkungowie Estrydsenidzi Unia kalmarska (1397–1523) Gryfici Wittelsbachowie Oldenburgowie Królestwo Danii i Norwegii (1523–1814) Oldenburgowie Królestwo Danii (od 1814) Oldenburgowie Oldenburgowie, linia Szlezwik-Holsztyn-Sonderburg-Glüksburg Następca tronu

29. `fineweb2_pl` `nakanapie.pl` nakanapie.pl (tokens=425, score=0.9736)

   Udzielanie kredytów, pożyczek i gwarancji to – obok prowadzenia rachunków bankowych – podstawowa działalność banków. Jednakże nie tylko banki zajmują się finansowaniem przedsiębiorców i konsumentów. Ryzyko, jakie potencjalnie wiąże się z każdym kredytem, pożyczką czy gwarancją, powoduje konieczność zabezpieczania się przed skutkami ewentualnego niespłacenia długu. Pomocą w wyborze jak najlepszego prawnego zabezpieczenia, ma służyć kolejna ksiązka z serii BIBLIOTEKA BANKOWCA. Autorka omawia w niej nie tylko te najczęściej i najchętniej stosowane zabezpieczenia, takie jak weksel in blanco, poręczenie, zastawy na rzeczach ruchomych czy hipoteka, ale również te mniej znane i niesłusznie rzadziej stosowane, jak zastaw na prawach oraz zabezpieczenia przejęte przez banki z praktyki banków zagranicznych jak oświadczenie patronackie czy niedawno uznane za dopuszczalne przez Sąd Najwyższy jak przewłaszczenie nieruchomości. Niniejsza publikacja jest najobszerniejszą pracą, jaka ukazała się na polskim rynku księgarskim na temat prawnych zabezpieczeń wierzytelności banków. Autorka wykorzystuje...

30. `wikipedia_pl` `pl.wikipedia.org` Ostrygowate (tokens=580, score=0.973)

   Ostrygowate, ostrygi (Ostreidae) – rodzina osiadłych małży nitkoskrzelnych z rzędu Ostreoida, licząca około , m.in. ostryga jadalna (Ostrea edulis), ostryżyca amerykańska (Crassostrea virginica) i ostryżyca japońska (Crassostrea gigas). Są uznawane za najcenniejsze mięczaki jadalne, poławiane i hodowane. Występowanie Są to gatunki szeroko rozprzestrzenione we wszystkich płytkich morzach słonych stref ciepłej i umiarkowanej. Nie ma ich w rejonach polarnych. Żyją na przybrzeżnych skałach, na głębokości kilku metrów. Niektóre gatunki tworzą duże ławice. Budowa Mają asymetryczną, płaską muszlę, cienkościenna połówka górna przykrywa wypukłą i grubościenną połówkę dolną, przyrośniętą do podłoża, ściśle do niego dopasowaną (co powoduje znaczne różnice kształtu pomiędzy osobnikami). Połówki muszli łączy elastyczne więzadło. Zamek muszli jest pozbawiony zębów, a noga całkowicie zredukowana. Szeroki mięsień zwieracz jest położony w pobliżu środka skorup. Długość muszli zróżnicowana – od około 1 cm do 60 cm. Zwykle są to dość duże małże, przy czym największe rozmiary i najbardziej regularne...

31. `wikipedia_pl` `pl.wikipedia.org` Rzeszotary (województwo dolnośląskie) (tokens=628, score=0.9723)

   Rzeszotary (niem. Rüstern) – wieś nad Czarną Wodą, w Polsce położona w centralnej części województwa dolnośląskiego, w powiecie legnickim, w gminie Miłkowice. Rzeszotary stanowią drugą wieś w gminie pod względem liczby mieszkańców (782). Podział administracyjny W latach 1975–1998 miejscowość administracyjnie należała do województwa legnickiego. Strategia rozwoju gminy Wraz z miejscowością Dobrzejów, Rzeszotary tworzą jedno sołectwo. W strategii rozwoju gminy Miłkowice określono Rzeszotary jako ośrodek gminny wspomagający I poziomu, obsługujący wsie: Bobrów, Dobrzejów, Głuchowice, Kochlice i Pątnówek. Nazwa Nazwa Rzeszotar wskazuje dawną funkcję służebną osady (podobnie jak w przypadku Złotników czy też Piekar). Mieszkańcy mieli obowiązek dostarczania na zamek sit do czyszczenia zboża i przesiewania mąki nazywanych trzyniakami, przetakami lub rzeszotami. Nazwy sit wiązały się przede wszystkim z ich przeznaczeniem, uzależnionym od wielkości oczek. Tak więc Rzeszotary zamieszkiwali ludzie wyrabiający rzeszota – „rzeszotarze”. Za czasów biskupa Henryka z Wierzbna w kronice łacińskiej...

32. `wikipedia_pl` `pl.wikipedia.org` Łaszczów-Kolonia (tokens=73, score=0.9746)

   Łaszczów-Kolonia – wieś w Polsce położona w województwie lubelskim, w powiecie tomaszowskim, w gminie Łaszczów. 1 stycznia 2010 roku część tej miejscowości została włączona do miasta Łaszczów. W latach 1975–1998 miejscowość administracyjnie należała do województwa zamojskiego. Wieś stanowi sołectwo gminy Łaszczów obejmujące także część terenu miasta.

33. `wikipedia_pl` `pl.wikipedia.org` Vera Salvequart (tokens=931, score=0.9775)

   Vera Salvequart (ur. 26 listopada 1919, zm. 26 czerwca 1947 w Hameln) – niemiecka pielęgniarka, kapo w hitlerowskim obozie koncentracyjnym Ravensbrück i zbrodniarka nazistowska. Życiorys Urodziła się w Wohontsch w Czechosłowacji w rodzinie Niemców sudeckich, lecz wkrótce wyemigrowała do Niemiec. Ukończyła szkołę pielęgniarską w Lipsku i dwa semestry medycyny. Z zawodu była pielęgniarką. W maju 1941 została aresztowana przez Gestapo na podstawie norymberskich ustaw rasowych za związki z żydowskim mężczyzną i odmowę ujawnienia miejsca jego pobytu. Spędziła 10 miesięcy w obozie KL Flossenbürg. Pod identycznymi zarzutami Salvequart aresztowano ponownie w 1942 i skazano tym razem na 2 lata. Wyszła na wolność w kwietniu 1944. Po krótkim czasie 11 listopada została aresztowana po raz trzeci ze swym ukochanym i jego siostrą. Obie kobiety po krótkim pobycie w areszcie w KL Theresienstadt zostały przeniesione z grupą 300 więźniarek do więzienia Berlin-Alexanderplatz, a 6 grudnia 1944 umieszczono ją w kobiecym obozie KL Ravensbrück Z powodu braków w personelu, SS zaczęło na szerszą skalę uży...

34. `fineweb2_pl` `www.mmarocks.pl` www.mmarocks.pl (tokens=1870, score=0.961)

   Ich pierwsza walka miała miejsce w 2015 roku. Do kolejnej dojdzie już w ten weekend. Jan Błachowicz i Jimi Manuwa ponownie wejdą razem do klatki 17 marca na UFC w Londynie. W Krakowie Polak musiał uznać wyższość „Poster Boy’a” a teraz… teraz o zdanie poprosiliśmy ponownie branżę MMA. Aby urozmaicić nieco typowanie, o wypowiedź poprosiliśmy nie tylko polskie środowisko, ale też kilku dziennikarzy z zagranicznych mediów zajmujących się MMA. Jak przedstawiają się opinie? Jak typuje branża MMA? Marcin Tybura (zawodnik UFC) Myślę, że Janek jest teraz zupełnie innym zawodnikiem, niż w pierwszej walce. Myślę, że tym razem będzie wywierał większą presję, że będzie też sprowadzał i wygra to starcie na dystansie 3 rund. TYP: Jan Błachowicz przez decyzję sędziów. Baysangur Edelbiev (przedstawiciel ACB) Wydaje mi się, że tym razem wygra Janek Błachowicz. W ubiegłym roku pokazał, że się zmienił, że to ten Janek którego ja pamiętam z KSW. Myślę, że podejdzie do tej walki mądrze i to jego ręka powędruje do góry. TYP: Jan Błachowicz. Jim Edwards (MMANytt.com) Rewanż Janka Błachowicza z Jimim Manu...

35. `wikipedia_pl` `pl.wikipedia.org` (1815) Beethoven (tokens=113, score=0.9665)

   (1815) Beethoven – planetoida z grupy pasa głównego planetoid okrążająca Słońce w ciągu 5 lat i 235 dni w średniej odległości 3,17 au Została odkryta 27 stycznia 1932 roku w Landessternwarte Heidelberg-Königstuhl w Heidelbergu przez Karla Reinmutha. Nazwa planetoidy pochodzi od Ludwiga van Beethovena (1770-1827), niemieckiego kompozytora. Przed nadaniem nazwy planetoida nosiła oznaczenie tymczasowe (1815) 1932 CE1.

36. `wikipedia_pl` `pl.wikipedia.org` Wyższa Szkoła Informatyki i Zarządzania w Rzeszowie (tokens=2267, score=0.8911)

   Wyższa Szkoła Informatyki i Zarządzania w Rzeszowie (WSIiZ) – największa niepubliczna uczelnia na Podkarpaciu, powołana w 1996 roku. Oferta edukacyjna WSIiZ obejmuje 13 kierunków studiów I i II stopnia, studia podyplomowe oraz doktoranckie. Kształcenie realizowane jest w czterech Kolegiach: Medycznym, Mediów i Komunikacji Społecznej, Informatyki Stosowanej oraz Zarządzania. Wyróżnikiem WSIiZ są prowadzone od 2004 roku studia anglojęzyczne oraz wysoki stopień umiędzynarodowienia: w ciągu 25 lat działalności uczelni studia we WSIiZ wybrało ponad 7 tysięcy obcokrajowców (w tym okresie mury WSIiZ opuściło w sumie ponad 60 tysięcy absolwentów). Uczelnia jest wysoko oceniana w ogólnopolskich i międzynarodowych rankingach. W roku akademickim 2020/2021 WSIiZ posiada 47 uprawnień do prowadzenia kształcenia, w tym 11 uprawnień magisterskich oraz prawo do nadawania tytułu doktora w dyscyplinie nauki o komunikacji społecznej i mediach, co daje uczelni status uczelni akademickiej. W 2021 roku WSIiZ obchodzi jubileusz 25-lecia istnienia. Historia Wyższa Szkoła Informatyki i Zarządzania w Rzeszo...

37. `wolne_lektury` `wolnelektury.pl` 20 000 mil podmorskiej żeglugi (tokens=2204, score=0.9609)

   — Hm — chrząknął Kanadyjczyk. — Czy ci mało jeszcze? — pytał Conseil. — Te rośliny nie stanowią przecie obiadu — odpowiedział Ned — bo to dopiero jego koniec, wety; a gdzie zupa, gdzie pieczeń? — To prawda — wtrąciłem — Ned obiecał nam kotlety, na które jakoś się nie zanosi. — Polowanie nasze — rzekł Ned — nieskończone jeszcze, bo się nawet nie zaczęło. Cierpliwości! Przecież spotkamy jakie zwierzę w pierzu lub sierści; nie w tym miejscu, to w innym. — A nie dziś, to jutro — dodał Conseil — bo nie trzeba się bardzo oddalać od brzegu; ja bym nawet radził powrócić do łodzi. — Jak to, już? — zawołał Ned. — Mamy przecie wrócić, nim noc zapadnie — zauważyłem. — A któraż teraz jest godzina? — zapytał Kanadyjczyk. — Będzie najmniej druga — odpowiedział Conseil. — Jak też to czas prędko ubiega na lądzie! — zawołał Ned, wzdychając. — Ruszajmy! — mówił Conseil. Zaczęliśmy więc wracać przez las, dopełniając nasze wiktuały: to kapustą palmową, którą trzeba było zbierać spod wierzchołków drzew, to groszkiem, który, o ile wiedziałem, Malaje nazywają abru, to ignamami przewybornego gatunku. Nadź...

38. `fineweb2_pl` `infoplanet.pl` infoplanet.pl (tokens=604, score=0.9625)

   Narodowy program dla zdrowia i oszczędności Tysiące Brytyjczyków przeżyje październik bez alkoholu w ramach programu „Go Sober”, zorganizowanego przez Macmillan Cancer Support. Organizacja sugeruje, że oprócz oszczędzania sporej sumy pieniędzy uczestnicy mogą również czerpać korzyści zdrowotne, takie jak dobry sen bez chrapania i zwiększony poziom energii. Podobnych korzyści spodziewają się osoby biorące udział w wydarzeniu organizowanym przez Alcohol Concern nazywanym „Suchy Styczeń”, które jest czymś w rodzaju corocznego rytuału oczyszczenia po okresie świątecznych i sylwestrowych ekscesów. Według sondażu YouGov, w styczniu 2017 roku na abstynencję zdecydowało się aż 5 milionów Brytyjczyków. Kiedyś uważano, że picie w małych ilościach jest nieszkodliwe, a może nawet korzystne, ale ostatnie badania zdają się temu przeczyć. Jedne z analiz opublikowane w The Lancet sugerowało, że nie ma bezpiecznego poziomu spożycia alkoholu – im więcej pijesz, tym większe jest ryzyko wystąpienia różnych chorób. Nic więc dziwnego, że wiele osób decyduje się na abstynencję przynajmniej przez kilka t...

39. `wikipedia_pl` `pl.wikipedia.org` Świętopełk Przemyślida (tokens=351, score=0.9723)

   Świętopełk (zm. 21 września 1109) – książę Czech z ołomunieckiej linii dynastii Przemyślidów. Panował w latach 1107-1109. Świętopełk był starszym synem Ottona I Pięknego, księcia ołomunieckiego, i jego żony Eufemii. Jego wujem był król Wratysław II. W 1103 roku, wspólnie z księciem Borzywojem II, uczestniczył w wyprawie na Polskę. W 1105 podjął nieudaną próbę obalenia Borzywoja II. W 1107 roku, dzięki wyprawie Bolesława Krzywoustego i króla węgierskiego Kolomana przeciw Czechom, Świętopełk został osadzony na stolcu praskim 14 maja 1107. W 1108 roku książę czeski uczestniczył w niemiecko-czeskim najeździe na Węgry, co spowodowało najazd ze strony Bolesława Krzywoustego na Czechy. Polska wyprawa na Czechy była także związana z brakiem wypełnienia przez Świętopełka układu, w którym zobowiązywał się do zwrotu przez Czechów, zagarniętych grodów na Śląsku (m.in. Racibórz, Kamieniec, Koźle). Próba zdetronizowania go przez polskiego księcia i osadzeniu na jego miejscu Borzywoja II nie doszła do skutku. W 1109 roku pomagał królowi niemieckiemu Henrykowi V w walkach z Polską. Z nieznaną z i...

40. `fineweb2_pl` `ownetic.com` ownetic.com (tokens=883, score=0.9755)

   Do 15 października 2011 roku można nadsyłać prace do kolejnej edycji konkursu w ramach projektu Marymont_metro dla sztuki, której tematem jest sam warszawski Marymont. Praca w dowolny sposób nawiązywać może do historii okolicy, jej nazwy lub życia mieszkańców. Celem konkursu jest wybór projektu (np. rzeźby, instalacji), który będzie miał szansę realizacji nad stacją metra Marymont (ze szczególnym wskazaniem placu od strony Hali Marymonckiej). W październiku zaś w przestrzeni galerii pojawią się wizualizacje najlepszych propozycji. Miasta stają się funkcjonalne, przyjazne i atrakcyjne nie tylko za sprawą odpowiednich planów urbanistycznych i ciekawej architektury, ale także ze względu na obecną w nich sztukę w przestrzeni publicznej. Zależności między sztuką a przestrzenią publiczną biegną zwykle w obu kierunkach. Z jednej strony, aby projekt artystyczny mógł w pełni zaistnieć w określonej lokalizacji potrzebuje odpowiedniego otoczenia, z drugiej zaś to fragmenty miasta potrzebują elementu, który podkreśli ich specyfikę, subtelnie wydobędzie z nich to, co najistotniejsze, a wcześni...

41. `wikipedia_pl` `pl.wikipedia.org` Carl Rogers (tokens=560, score=0.9603)

   Carl Ransom Rogers (ur. 8 stycznia 1902 w Oak Park w stanie Illinois, zm. 4 lutego 1987 w La Jolla w Kalifornii) – amerykański psycholog i psychoterapeuta, jeden z głównych przedstawicieli psychologii humanistycznej, twórca psychoterapii zorientowanej na klienta oraz teorii organizmicznej. Życiorys Początkowo studiował rolnictwo, potem przez dwa lata uczęszczał do seminarium, by ostatecznie podjąć studia pedagogiczne w Teachers College, gdzie również obronił swoją rozprawę doktorską. Mając 20 lat, był delegatem na światową konferencję młodzieży chrześcijańskiej w Pekinie. Praktyki pedagogiczne odbył w latach 1927-1928 w Institute for Child Guidance, gdzie zetknął się z psychoterapią. Twórca counsellingu psychologicznego. Pierwszą swoją książkę pt. The Clinical Treatment of the Problem Child wydał w 1938 r. podejmując w niej problem terapeutycznej pomocy dziecku w rozumieniu siebie i w samoakceptacji. Pracował też na uniwersytetach w Ohio, Chicago i Wisconsin rozwijając swoją teorię i praktykę terapii niedyrektywnej, a następnie terapii skoncentrowanej na kliencie. Jego oryginalna...

42. `fineweb2_pl` `www.ezdrasz.eu` www.ezdrasz.eu (tokens=374, score=0.9647)

   Ojcze nasz, który jesteś w niebie. - Ewangelia wg św. Łukasza 11,2 Przeczytaj: Ewangelia wg św. Jana 14,9-14 Jako chrześcijanie często zapominamy, jak bardzo jesteśmy uprzywilejowani. Możemy się cieszyć różnymi korzyściami płynącymi z Ewangelii, których wyznawcy innych religii nigdy nie będą w stanie pojąć. Kilka lat temu miałem okazję wysłuchać świadectwa nawrócenia pewnej kobiety w Pakistanie. Przez wiele lat jej mąż był ważnym przedstawicielem władz tego kraju. Opowiedziała o tym, jak czytała Nowy Testament i jak trudno jej było uwierzyć, że ludzie mogą zaczynać modlitwę od słów: Ojcze Nasz. Jedyną rzeczą dotycząca Allaha, której była pewna, było to, że różnił się od ludzi. Był od nich większy i całkowicie inny; nie można go było określić za pomocą ludzkich kategorii, a już z pewnością nie można było użyć tak osobistego i bezpośredniego określenia jak ojciec. Kiedy przyjęła wiarę w Jezusa Chrystusa, najpierw wzniosła serce, wołając „Ojcze!” i w momencie, kiedy wypowiedziała to słowo, osunęła się na podłogę w absolutnym przerażeniu, myśląc, że za taką zuchwałość za chwilę padnie...

43. `fineweb2_pl` `certesto.com` certesto.com (tokens=633, score=0.9544)

   W zakładce „Pola dynamiczne”, w ustawieniach szablonu certyfikatu, możesz zmienić zachowanie i niektóre elementy pól dynamicznych dodanych do szablonu. Typ pola W Certesto dostępnych jest kilka typów pól dynamicznych. Dzielimy je na dwie grupy: - Pola standardowe – wymagają podania odpowiednich danych w celu wystawienia certyfikatu. - Pola automatyczne – nie wymagają podawania danych. Dane są uzupełniane automatycznie. Poszczególne typy pól są opisane poniżej. Pole tekstowe Podstawowy typ pola dynamicznego. Pozwala na wpisanie dowolnego tekstu. Możliwe jest zdefiniowanie zaawansowanego sprawdzania formatu wprowadzonych danych. Wartość z listy Lista wartości, z której należy wybrać jedną pozycję. Przydatne przy ograniczonym zbiorze możliwych wartości danego pola np. miasto w którym odbywa się szkolenie lub imię i nazwisko trenera. Data Dowolna data, wybierana z kalendarza. Adres email Adres email w poprawnym formacie. Data wystawienia certyfikatu (auto) Data wystawienia certyfikatu. Pole jest uzupełniane automatycznie. Data wygaśnięcia certyfikatu (auto) Data wygaśnięcia certyfikat...

44. `fineweb2_pl` `www.niedziela.pl` www.niedziela.pl (tokens=1058, score=0.9599)

   2015-11-06 09:58 Redakcja Tygodnika Katolickiego „Niedziela” 6 listopada 2015 r. zmarł o. Jan Maria Sochocki OFMCap, budowniczy i kustosz Sanktuarium Matki Bożej Fatimskiej i o. Pio w Terliczce. Ojciec Jan w ostatnim czasie przebywał w klasztorze w Nowej Soli, gdzie zmarł. Zmarł w wieku 66 lat, przeżywszy 41 lat w Zakonie i 35 w kapłaństwie. „Wszystko mi dałeś, co dać mogłeś, Panie...” - ta myśl umieszczona na obrazku prymicyjnym śp. o. Jana Marii Sochockiego - kapucyna, wielkiego przyjaciela „Niedzieli”, dokładnie wyraża jego postawę pokory, dziękczynienia i zawierzenie Bogu. Takim go znaliśmy. Dla tych, którzy spotykali go po raz pierwszy widoczna była przede wszystkim jego franciszkańska radość, wyrażana śpiewem, uśmiechem, gościnnością, życzliwością dla wszystkich, których spotykał na swojej drodze. Ale był też człowiekiem głęboko rozmodlonym - po przyjeździe do redakcji pierwsze kroki kierował do kaplicy, potem szedł na Jasną Górę, w każdej wolnej chwili sięgał po brewiarz. Odszedł 6 listopada 2015 r., w pierwszy piątek miesiąca, kiedy spieszył z Najświętszym Sakramentem do c...

45. `fineweb2_pl` `www.zoumalaphoto.com` www.zoumalaphoto.com (tokens=397, score=0.9685)

   Opis Majtki damskie z koronką – romantyczna i zmysłowa bielizna Lubisz nosić bieliznę, która jest nie tylko wygodna i praktyczna, ale również zmysłowa i efektowna? Trudno o lepszy wybór niż koronkowe majtki damskie Camilla o fasonie bikini. To model z nowej kolekcji Gatta Intimate na sezon jesienno-zimowy. Lubisz granat i ażurowe koronki? Zrób nieco miejsca w swojej szafce na romantyczną bieliznę z linii Camilla. W kolekcji znajdziesz nie tylko prezentowane tu bikini damskie, ale też koronkowy biustonosz oraz majtki brazyliany, które kusząco eksponują pośladki i zapewniają najwyższy komfort w każdej sytuacji. Bieliznę z linii Camilla zaprojektowaliśmy w eleganckim odcieniu głębokiego granatu – to doskonały wybór na nadchodzący sezon! Koronkowe bikini Camilla – nie musisz wybierać między estetyką i wygodą! Piękna bielizna damska z koronką może zaskoczyć Cię nie tylko dopracowanym wzornictwem, ale też wygodą noszenia! Tym właśnie wyróżniają się majtki damskie bikini Camilla. Ich krój uwzględnia specyfikę kobiecej sylwetki, a materiał wykonania charakteryzuje się wysoką trwałością, e...

46. `wikibooks_pl` `pl.wikibooks.org` GnuPG/Informacje ogólne (tokens=1132, score=0.9725)

   Co to jest GnuPG jest udostępnianym na licencji GPL w pełni funkcjonalnym zamiennikiem PGP zgodnym ze standardem OpenPGP. Ważne jest, że GnuPG nie używa opatentowanego algorytmu IDEA, dzięki czemu jego używanie nie jest w żaden sposób ograniczone. Jest to oprogramowanie stabilne, działające na systemach zgodnych z POSIX (takich jak GNU/Linux i różne odmiany BSD), Mac OS X a nawet MS-Windows. Sam GnuPG jest programem konsolowym, ale jeśli nie lubisz wpisywania poleceń, to istnieje wiele nakładek graficznych (takie jak GPA pod GNU/Linux lub WinPT pod Windows). Niektóre programy pocztowe (np. Sylpheed-claws) mają wbudowaną obsługę kluczy GnuPG. Inne wymagają instalacji odpowiedniego pluginu. Enigmail to plugin, dzięki któremu Mozilla Thunderbird może korzystać z GnuPG. Do czego to służy GnuPG to skrót od GNU Privacy Guard. Jeśli ktoś zna nieco język angielski pewnie domyśla się, że jest to oprogramowanie, które ma dbać o naszą prywatność. Tak właśnie jest, GnuPG jest oprogramowaniem kryptograficznym, które umożliwia bezpieczną komunikację i przechowywanie danych. W czasach, kiedy Int...

47. `fineweb2_pl` `www.salon24.pl` www.salon24.pl (tokens=751, score=0.9798)

   Interesująco się prezentują dane Eurobarometru w przedmiocie zadowolenia Polaków z warunków życia. Jest to szczególnie istotne teraz, kiedy się w kampanii wyborczej podnosi konieczność odbudowy kraju ze zgliszcz, w jakie rzekomo popadł w wyniku odsunięcia Prawa i Sprawiedliwości od władzy. Z unijnych badań wynika, że systematycznie rośnie u nas odsetek ludzi zadowolonych ze swego losu. Ba, oni przeważają. O ile w czasie rządów SLD albo też w pierwszych latach przynależności do Unii oscylował on w przedziale 56 do 58%, to w trakcie rządów PiS wzrósł już do 60% by teraz osiągać wartość 69%. Jednocześnie maleje udział ludzi niezbyt zadowolonych, od 22% w czasie władzy Sojuszu, przez 19 po rządach Prawa i Sprawiedliwości, do 13% obecnie. Podobnie jest ze zdecydowanie niezadowolonymi, których początkowo było 6%, potem 4 a teraz 2%. Tylko bardzo zadowoleni utrzymują się na tym samym piętnastoprocentowym poziomie od początku badań w 2004 roku do teraz. Rzecz nie jest bez znaczenia wobec klęski, stale wmawianej Polakom przez partie odsunięte od władzy, jako kary za to, że ich przestali wy...

48. `wikipedia_pl` `pl.wikipedia.org` Sosjerka (tokens=131, score=0.9691)

   Sosjerka – rodzaj naczynia, element zastawy stołowej, przeznaczona do podawania sosów. Klasyczna sosjerka ma zazwyczaj kształt łódki z dwoma dziobkami i dwoma uchwytami, stojącej na podstawce. Czasami ma kształt zbliżony do dzbanka, z jednym dziobkiem i pojedynczym uchwytem, czasem bez podstawki lub z nóżkami zamiast niej. Sosjerka zazwyczaj wykonywana bywa z porcelany lub podobnych materiałów (fajans, kamionka), ale także ze szkła lub metalu, współcześnie także plastiku. Często bywa zdobiona. Naczynia stołowe

49. `fineweb2_pl` `pol.obozrevatel.com` pol.obozrevatel.com (tokens=1200, score=0.95)

   Trending: "Nie widzimy powodu": Ławrow cynicznie o wojnie z Ukrainą i możliwości negocjacji Podczas konferencji prasowej na szczycie ministrów spraw zagranicznych OBWE, rosyjski minister spraw zagranicznych Siergiej Ławrow wygłosił kolejną rundę cynicznych oświadczeń na temat rosyjskiej inwazji na Ukrainę. Zaczął twierdzić, że Rosja rzekomo prowadzi wojnę z Zachodem, podczas gdy Ukraina odmawia negocjacji z agresorem. Szef rosyjskiej "dyplomacji", w typowy dla siebie chamski sposób, powiedział, że zamiast negocjować "tango", Kijów i Zachód "tańczą breakdance", a Moskwa "nie widzi powodu, by zmieniać cele operacji specjalnej". Wypowiedzi Ławrowa, wygłoszone w Skopje w Macedonii Północnej, są powielane przez rosyjskich dziennikarzy. Według Ławrowa państwo-agresor chce negocjować, ale Kijów i zachodni partnerzy Ukrainy rzekomo nie chcą powstrzymać rosyjskiej agresji na Ukrainę. "Do rozpoczęcia procesu politycznego potrzeba dwojga. To jak tango. Ale faceci po drugiej stronie nie tańczą tanga, ale breakdance. Tam trzeba solo" - powiedział rosyjski minister spraw zagranicznych. Przypomn...

50. `wikipedia_pl` `pl.wikipedia.org` Rouffilhac (tokens=86, score=0.9629)

   Rouffilhac – miejscowość i gmina we Francji, w regionie Oksytania, w departamencie Lot. Według danych na rok 1990 gminę zamieszkiwały 152 osoby, a gęstość zaludnienia wynosiła 23 osób/km² (wśród 3020 gmin regionu Midi-Pireneje Rouffilhac plasuje się na 911. miejscu pod względem liczby ludności, natomiast pod względem powierzchni na miejscu 1357.).
