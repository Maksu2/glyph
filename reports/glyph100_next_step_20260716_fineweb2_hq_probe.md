# Glyph-100M FineWeb2 PL Probe

Generated: 2026-07-16T05:30:45.728144+00:00

No training was started. No v2.3 dataset was built by this probe.

## Access

- dataset: `epfml/FineWeb2-HQ`
- gated: `False`
- private: `False`
- disabled: `False`
- parquet files: 5891
- parquet size: ~5627.4 GiB
- stream status: sampled 1,000 rows, accepted 152 (15.2%)

## Fields

```json
[
  "date",
  "dump",
  "embeddings",
  "file_path",
  "id",
  "language",
  "language_score",
  "language_script",
  "minhash_cluster_size",
  "quality_score",
  "text",
  "top_langs",
  "url"
]
```

## Probe Counts

- raw rows seen: 1,000
- accepted docs: 152
- rejected docs: 848
- accepted tokens: 125,979
- avg tokens / accepted doc: 828.8
- token/word ratio: 1.903

## Token Length Percentiles

```json
{
  "p50": 386.0,
  "p75": 861.5,
  "p90": 2081.4000000000015,
  "p95": 2889.7,
  "p99": 4731.140000000001
}
```

## Rejection Reasons

```json
{
  "large_minhash_cluster": 675,
  "too_short": 253,
  "repeated_ngrams": 71,
  "forum_or_qa_url": 48,
  "low_language_score": 27,
  "contact_commerce_policy_url": 26,
  "too_many_urls": 21,
  "commerce_or_prices": 13,
  "too_many_boilerplate_patterns": 9,
  "html_present": 9,
  "forum_patterns": 5,
  "landing_or_product_url": 3,
  "single_word_repetition": 3,
  "too_long": 2,
  "commerce_patterns": 2,
  "gambling_spam": 1,
  "link_list": 1,
  "forum_or_comments": 1,
  "list_heavy_short_doc": 1
}
```

## Top URL Domains

```json
{
  "pl.wikipedia.org": 344,
  "www.polish.hostelworld.com": 41,
  "pl.urbandictionary.com": 36,
  "zapytaj.onet.pl": 20,
  "support.microsoft.com": 11,
  "www.news-medical.net": 10,
  "europa.eu": 9,
  "pl.tripadvisor.com": 8,
  "www.filehippo.com": 8,
  "forumprawne.org": 8,
  "forum.gazeta.pl": 5,
  "www.rambow.de": 5,
  "www.filmweb.pl": 5,
  "www.europarl.europa.eu": 4,
  "eu.blizzard.com": 4,
  "www.wielkiezarcie.com": 4,
  "www.bryk.pl": 4,
  "www.tipy.pl": 4,
  "www.seans-online.eu": 4,
  "krzyzowka.net": 4,
  "www.zgapa.pl": 4,
  "film.onet.pl": 4,
  "gotowanie.onet.pl": 4,
  "www.zadaj.pl": 4,
  "gotquestions.org": 3
}
```

## v2.3 Options

| variant | target tokens | 50k epochs | recommended now | risk |
|---|---:|---:|---|---|
| A | 300,000,000 | 2.73 | True | Good first v2.3 target if accepted samples remain mostly continuous Polish prose. |
| B | 500,000,000 | 1.64 | False | Better epoch math, but only after FineWeb2 residue looks acceptable at larger sample sizes. |
| C | 200,000,000 | 4.10 | False | Quality-first fallback; still about 4.1 epochs for stage 3. |
| D | 37,000,000 | 22.14 | False | No good long-run dataset without a larger clean source. |

## Accepted Samples

1. `http://www.smokvina.hr/pl/kategorii/island/stomorska-rogac` tokens=256 score=0.9616

   Stomorska na wsi, Split-Dalmacja County, w południowej chorwackim. Jej położenie geograficzne jest 43 ° 22 'szerokości geograficznej północnej i 16 ° 21' długości geograficznej wschodniej. Jest on nazwany na cześć Marii Panny (Maryjo). W szczególności, znajduje się poniżej Sanktuarium Matki Bożej Stomorija ust lub Matka Boża Bori). Kiedyś to było najważniejsze przemysł morski i transport morski, jest transportowany przez żaglowce z Adriatyku wapna i wina. To samo jest teraz używany do celów turystycznych. Oferta turystyczna jest dość dobry w tym miejscu, i wiele restauracji. Drugi jest najsilniejszym miejscem na wyspie, za Nečujam. W lecie często "zabawa rybołówstwo". Są plaże w centrum Stomorska, tak, że turyści pójść łatwiej na morzu. Ludność zajmuje się połowów, ryby rolnictwa i posiada (w pobliżu gospodarstwa rybnego - morze leszcz i okoń morski). Stomorska (Rogač) - Zakwaterowanie Chorwacja jest idealnym miejscem na wakacje, pogoda w domach, mieszkaniach lub pomieszczeniach prywatnych. Związane

2. `http://www.lastfm.pl/music/A+Thousand+Knives+Of+Fire/+wiki?ver=1` tokens=180 score=0.9689

   skład Lee Stuart : Vocals, Guitar, harmonica Dan Gollin : Drums Paul Wiegand : Guitar Taj Briggles : Bass dyskografia The Last Train To Scornsville (CD - 2008 Edytowana przez Lord_Krichian dnia 15 VII 2011, 18:25 Zarejestrowani użytkownicy mogą edytować tę stronę. Zarejestruj się teraz, nic za to nie płacisz, a odkryjesz ogromną ilość wspaniałej muzyki :) Cała zawartość tej strony pochodząca od użytkowników jest dostępna zgodnie z warunkami Creative Commons Attribution/Share-Alike License. Tekst może być również dostępny zgodnie z warunkami licencji wolnej dokumentacji GNU. Fakty Wygenerowano na podstawie faktów oznaczonych w wiki. Brak danych na temat tego wykonawcy

3. `http://pl.tripadvisor.com/Hotel_Review-g60908-d97686-Reviews-Roosevelt_Inn-Keystone_South_Dakota.html` tokens=184 score=0.967

   Hotel był tym, czego się spodziewałem, za bardzo rozsądną cenę w bardzo pracowity weekend! Nie jest to sieć, więc tych, którzy oczekują, że może być rozczarowany. Śniadanie nie było reklamowane, ale proste śniadanie było wliczone w cenę (ale jak jakiś sok). Miejsce to doskonale nadaje się do wszystkich naszych podróży w tej części Południowej Dakoty. Mój syn bardzo zadowoleni z... Więcej - Znany także jako: - Roosevelt Hotel Keystone - Opcje rezerwacji: - TripAdvisor jest dumnym partnerem firm Cheap Tickets, dzięki czemu możesz dokonywać rezerwacji w następującym hotelu bez obaw: Roosevelt Inn. Co miesiąc pomagamy milionom podróżnych w wyszukiwaniu najlepszych hoteli na podróże w celach wypoczynkowych i biznesowych. Zawsze oferujemy najkorzystniejsze zniżki i oferty specjalne.

4. `http://pl.wikipedia.org/wiki/Incydent_Trent` tokens=375 score=0.984

   Incydent Trent 8 listopada 1861 brytyjski statek pocztowy Trent został zatrzymany przez amerykański okręt San Jacinto w okolicach Bahamów. Na statku płynęli konfederaccy posłowie do Londynu i Paryża. Choć sam statek nie został zatrzymany, obaj dyplomaci zostali aresztowani, dostarczeni do Bostonu, a następnie internowani. Dowódca San Jacinto, kapitan Charles Wilkes, został okrzyknięty bohaterem i uzyskał podziękowanie za swoją akcję specjalnym adresem Izby Reprezentantów. Ze strony brytyjskiej akcja amerykańska została przyjęta jako akt agresji. Brytyjskie władze wystosowały bardzo ostrą w tonie notę protestacyjną, dającą stronie amerykańskiej siedem dni na zadowalające je wyjaśnienia. W swym ultimatum Wielka Brytania groziła nie tylko oficjalnym uznaniem Konfederacji, lecz także przystąpieniem po jej stronie do wojny i umiędzynarodowieniem konfliktu. Nota miała być dostarczona do władz amerykańskich za pośrednictwem ambasadora brytyjskiego w USA, Lorda Lyons. Lyons, rozumiejąc jednak powagę sytuacji, wstrzymał dostarczenie noty o kilka dni, w międzyczasie kontaktując się z sekretarzem stanu Williamem Sewardem. Ta zwłoka oraz inne zakulisowe działania dały administracji amerykań...

5. `http://www.news-medical.net/news/20120711/23421/Polish.aspx` tokens=431 score=0.9663

   Nowa nauka publikująca w Lipa 11 zagadnieniu czasopismo Neuroscience wyszczególnia rozwój pierwszy mysz model konstruujący nieść pospolitą mutację w Usher syndromu III kauzatywnym genie w Północna Ameryka. (Clarin-1) Dalej zespół badaniowy od skrzynka westernu rezerwy Uniwersyteckiej szkoły medycznej używał ten nowego modela rozumieć dlaczego mutacja w Clarin-1 prowadzi utrata słuchu. Usher syndrom jest nieuleczalnym genetycznym chorobą i ja jest najwięcej wspólnej sprawy podwójni sensualni niedobory głuchota i ślepota. Ja wpływa obliczonych 50.000 amerykan i jeszcze więcej na całym świecie. Clinically subdivided w typ i-iii opierających się na stopniu głuchota ja i obecność balansowy nieład i each typ kojarzy z odrębnymi genami. Podczas gdy progresja choroba jest różna z each typ, wszystkie pacjenci ostatecznie przyjeżdżają przy ten sam konsekwencją. Ostrość ten nauka jest Usher typ III. Więcej niż tuzin genetycznych mutacj kojarzą z Usher III, z "N48K" mutacją w Clarin-1 jest przeważajacym mutacją w Usher III pacjentach w Północna Ameryka. Od N48K mutaci zapoczątkowywającej w Europa, rezultaty ten nauka będą znaczenie podzbiór Usher III pacjenci w Europa także. To jest znacząc...

6. `http://www.polish.hostelworld.com/hosteldetails.php/May-De-Ville-Backpackers-Hostel/Hanoi/52968` tokens=339 score=0.9792

   May De Ville Backpackers Hostel Informacje O Placówce:Przetłumaczone przez Prowadzony przez Zachodu, to jest twój dom z dala od domu w Hanoi. Zbudowany w 2011, w samym sercu starej dzielnicy Hanois jego doskonałą bazą do odkrywania uroków tego miasta. Przestronne sześć dorms łóżko są czyste, wygodne i klimatyzowane z łazienkami w standardzie. Mamy również bardzo przystępnej cenie prywatne podwójne, pojedyncze lub pokoje rodzinne. Wszystkie z nich są ładnie urządzone i wyposażone w dodatkowe akcenty luksusu w tym duże i wygodne łóżka, telewizory LCD i laptop osobistego. Darmowe śniadanie w formie bufetu serwowane jest codziennie rano i obejmuje szeroki wybór ciast, owoców, mięs na zimno i gorąco, i jajka gotowane w dowolnym stylu. Bezpłatny internet bezprzewodowy na każdym piętrze i komputerów w holu, aby był w kontakcie ze znajomymi i rodziną. Dawca ochotę kolejną noc na mieście? Pobyt w maju na De Ville Backpackers to tylko jako zabawę, z ogromnym amerykańskiego stół bilardowy, rzutki "pokładzie i kina do Państwa dyspozycji. Bądź bezpieczny, która za pomocą 24 ochroniarza godzin, jak również kamer bezpieczeństwa i klucz elektroniczny dostęp do wszystkich pomieszczeń. Na kosztow...

7. `http://www.tourmycountry.com/austria/l-polski.htm` tokens=426 score=0.916

   Travel Guide Wiednia i Austrii Kultura: TourMyCountry.com Zapraszamy do TourMyCountry.com, osobisty przewodnik dla Austrii, koncentrując się na Wiedeń. Ta strona została przetłumaczona przez program automatycznego tłumaczenia, dlatego można znaleźć jakieś zabawne błędy. Większość innych materiałów na tej stronie jest angielski. Tutaj znajdziesz przegląd zagadnień, które są objęte tym przewodnik. Specjalne rzeczy na temat tego przewodnika jest to, że został napisany przez lokalne: Jestem austriackiej sobie, pochodzi z Salzburga. Ja mieszkam w Wiedniu, gdzie pracował jako dziennikarz. Celem mojej przewodnik jest dostarczenie osobiste, subiektywne informacje na temat Austrii, a zwłaszcza w Wiedniu. W ten sposób można się nauczyć lokalnych doświadczeń tego kraju. Turyści często widzimy tylko zniekształcony obraz obraz-Austria idealne, jeśli szukasz zrównoważonego widzenia tej stronie może być idealnym miejscem dla Ciebie. Jest on podzielony na sześć kategorii. 1). Dodatkowe informacje: Informacje na temat kultury, historii i współczesnego życia w Austrii. Zawiera praktyczne porady dotyczące planowania wakacji. 2). Atrakcje: Informacje na temat atrakcji turystycznych w poszczególnych...

8. `http://pl.wikipedia.org/wiki/Aleksandras_Abi%C5%A1ala` tokens=244 score=0.9434

   Aleksandras Abišala |Aleksandras Abišala| |Data i miejsce urodzenia||28 grudnia 1955 Inta |Premier Litwy| |Okres urzędowania||od 21 lipca 1992 do 2 grudnia 1992 |Poprzednik||Gediminas Vagnorius| |Następca||Bronislovas Lubys| Ukończył w 1978 studia z zakresu fizyki na Uniwersytecie Wileńskim. Po ukończeniu studiów przez dwa lata służył w Armii Radzieckiej. Na początku lat 80. pracował jako inżynier w Kowieńskim Instytucie Politechnicznym, a od 1981 jako naczelny inżynier w Instytucie Naukowo-Badawczym Pomiarów Radiowych. W 1988 zaangażował się w działalność niepodległościowego ruchu Sąjūdis. W lutym 1990 został członkiem Rady Najwyższej Litewskiej SRR, należał do sygnatariuszy aktu Aktu Odtworzenia Niepodległości Litwy. W 1991 objął stanowisko ministra bez teki. W 1992 od 21 lipca do 2 grudnia sprawował urząd premiera. W tym samym roku wycofał się z działalności politycznej. Od 1993 prowadzi firmę konsultingową "A. Abišala i partnerzy".

9. `http://www.polish.hostelworld.com/hosteldetails.php/Euphemia-Hotel/Amsterdam/647` tokens=262 score=0.9595

   Euphemia Hotel Informacje O Placówce:Przetłumaczone przez Mamy jedno-, dwu-, trzy-, cztero-, pięcio-, sześcio-i 10-osobowe pokoje, z podziałem na 4 piętrze (bez windy). Większość pokoi z łazienkami, a wspólne pokoje udogodnienia w korytarzu. Eufemii był dawniej klasztor zbudowany na przełomie XIX i XX wieku. To jest w pobliżu wszystkich głównych atrakcji turystycznych w centrum miasta, takich jak Heineken Brewery, Leidseplein, nocnych klubów i muzeów. Ze względu na nasze położenie przy cichej, bocznej ulicy, jeden jest w stanie uciec od zgiełku miasta. Jesteśmy również łatwy dojazd z Dworca Centralnego. Rano serwujemy proste śniadanie z karty € 0,3, - do € 5, podawane w godzinach od 8 do 11 rano. Mamy też automat do gorących i zimnych napojów. Salon czynny jest w godzinach pracy recepcji (8am-11pm). Tutaj można spędzić pocztówek pisania południu spotkanie innych turystów, oglądania telewizji lub korzystania z naszego bezpłatnego bezprzewodowego dostępu do Internetu. Życzymy miłego pobytu. Proszę przeczytaj nasze rzeczy do odnotowania poniżej przed dokonaniem rezerwacji.

10. `http://www.polish.hostelworld.com/hosteldetails.php/Armada-Lodge/Limerick/45999` tokens=195 score=0.9692

   Armada Lodge Informacje O Placówce:Przetłumaczone przez Tutaj w B & B są cztery prywatne pokoje z łazienkami do wyboru. Każdy pokój wyposażony jest w telewizor, z wielokanałowym oglądania, jak również herbaty i kawy. Inne udogodnienia obejmują sprzęt do prasowania i suszarkę do włosów. Parking strzeżony gość jest w ofercie. Łącze internetowe. Śniadanie jest przygotowany świeżo każdego dnia. Atrakcje znajdujące się w pobliżu Armada Lodge i Bunratty Castle (15 minut jazdy), Shannon Airport (15 minut jazdy), a niektóre z największych atrakcji miasta Limerick, w tym Zamku Króla Jana i uniwersytetu. Uwaga: Sprawdź się w czasie przed 6pm-Jeśli później prosimy nieruchomości połączenia bezpośrednio. Sprawdź 11 rano czasu. Proszę pamiętać, że nie posiadają karty kredytowej obiektów na płatności B & B, w związku z tym w gotówce jest wymagane.

11. `http://library.thinkquest.org/20868/gaz_art/jzds/pol/moe/brwa.htm` tokens=2358 score=0.9525

   BARWA Barwy podstawowe i pochodne W wielkim zespole barw istnieją trzy barwy podstawowe oraz trzy pochodne. Barwy podstawowe to czerwona, żółta i niebieska (il. 1). Ich nazwa wzięła się stąd, że nie można ich uzyskać ze zmieszania farb o jakichkolwiek innych barwach. Ze zmieszania farby czerwonej z żółtą uzyskamy barwę pomarańczową, z połączenia farby czerwonej z niebieską - fioletową, a niebieskiej z żółtą - zieloną. Natomiast po nałożeniu na siebie trzech barw podstawowych uzyskamy barwę czarną. Barwy pomarańczowa, fioletowa i zielona p o c h o d z ą z odpowiedniego zmieszania farb czerwonej, żółtej i niebieskiej. Stąd ich nazwa - pochodne (il. 2). 1. Barwy podstawowe Nałożenie na siebie trzech barw podstawowych 2. Barwy pochodne Odcień, a tym samym i temperatura barwy pochodnej zależy od proporcji użytych farb o barwach podstawowych. Jeśli w połączeniu czerwieni z żółcieniem przeważać będzie żółcień - powstała farba pomarańczowa będzie miała odcień jaśniejszy niż wówczas, gdybyśmy zastosowali więcej czerwieni. Jeżeli w mieszance farby niebieskiej z żółtą użyjemy więcej tej pierwszej, zieleń okaże się ciemniejsza, bardziej chłodna niż wówczas, gdyby przeważała farba żółta itd....

12. `http://www.polish.hostelworld.com/hosteldetails.php/Dragon-Hostel-Hong-Kong/Hong-Kong/5065` tokens=461 score=0.9321

   Dragon Hostel Hong Kong Informacje O Placówce:Przetłumaczone przez Wszystkie 66 pokoi w hostelu są wyposażone w udogodnienia takie jak klimatyzacja, telewizor, telefon z bezpośrednim wyjściem (nieograniczony darmowe połączenia lokalne), węzeł sanitarny, biurko, szuflady oraz miejsce zapisu. Pokoje Ecomony ze wspólną łazienką dostępne są dla budżetu travelers.The hostel przestrzega przepisów państwowych dotyczących bezpieczeństwa pożarowego i bezpieczeństwa budynku. Wszystkie pokoje są bardzo czyste i komfortowe przez przyjazne sztabów. bezpłatny dostęp do internetu boardband dostępne. Kije mówi płynnie po angielsku, mandaryński, kantoński, Wietnamczyków i indonezyjsku. 24h recepcja daje pełną informacje o podróży. Dragon Hostel zapewnia także usługi turystyczne m.in. Chiny (Biznes / Tourist) i Wietnam Wizy Wiza turystyczna, Hongkong lokalnych wycieczek i aranżację biletów. Mamy też bilety Disneya! Proszę wybrać 'czas przyjazdu "bardzo starannie przed confriming rezerwacji, hostel zastrzega sobie wszelkie prawa, aby anulować wszystkie zameldowania bez refundacji. Proszę zrozumieć, że schroniska muszą przydzielić późne wymeldowanie, wczesny check-in, walk-in klientów codziennego,...

13. `http://pl.tripadvisor.com/Hotel_Review-g150813-d1413156-Reviews-Playa_Selva-Tulum_Yucatan_Peninsula.html` tokens=153 score=0.9724

   Playa Selva jest piękny, czysty i bezpieczny. Przyjazny personel jest bardzo pomocny i duża wspólna kuchnia jest dobrze wyposażona. Są tam również miły akcent, jak zapalić świece w godzinach wieczornych i piękny talerz owoców po przyjeździe. - Znany także jako: - Playa Selva Hotel Tulum - Playa Selva Hotel - Opcje rezerwacji: - TripAdvisor jest dumnym partnerem firm Booking.com, dzięki czemu możesz dokonywać rezerwacji w następującym hotelu bez obaw: Playa Selva. Co miesiąc pomagamy milionom podróżnych w wyszukiwaniu najlepszych hoteli na podróże w celach wypoczynkowych i biznesowych. Zawsze oferujemy najkorzystniejsze zniżki i oferty specjalne.

14. `http://www.polish.hostelworld.com/hosteldetails.php/The-Melting-Pot-Hostel-Tanger/Tanger/69460` tokens=672 score=0.962

   The Melting Pot Hostel Tanger Informacje O Placówce:Przetłumaczone przez Melting Pot Hostel położony jest w samym sercu medyny tangerskiego. Będąc jednym z największych Medina kraju, jest jednym z miejsc, w Tangier, że przyciąga uwagę użytkowników. Jego historia jest bardzo stara, okupacja swojej ziemi to zeznał od starożytności. Otoczone murami, Kasbah i Medina Tanger wiele zabytków: - "Big Zoco" to główne drzwi wejściowe do Medyny, zazwyczaj są wieśniaczki sprzedające warzywa rosną same. - "Meczet Sidi Bu Abid" z minaretem objętej pięknych polichromii ceramiki. - "Mendubia" był rezydencją Mendub, odpowiedzialny za oglądanie na sułtana w obcych mocarstw podczas epoki, w której Tangier miała międzynarodowy region. - "Kasbah Tanger", położony w zachodniej części Medyny, to kolejne miejsce z wielkim zainteresowaniem. Tutaj znajduje się "Dar el Makzen ', pałacu gubernatora, zbudowany na zlecenie Mulay Ismail w XVII wieku. Teraz jest to siedziba Muzeum Sztuki Maroka, które pokoje otaczają pięknie zdobione płytki dziedziniec, a gdzie można podziwiać przedmioty pochodzące z całego Maroka: dywany, biżuteria, ceramiczne, tkaniny i wyroby włókiennicze, między innymi. Istnieje również oto...

15. `http://pl.wikipedia.org/wiki/Sara_Jean_Underwood` tokens=185 score=0.9212

   Sara Jean Underwood Z Wikipedii, wolnej encyklopedii |Ten artykuł od 2013-03 wymaga uzupełnienia źródeł podanych informacji. Możliwe, że ten artykuł w całości albo w części zawiera informacje nieprawdziwe. Informacje bez źródeł w każdej chwili mogą zostać zakwestionowane i usunięte. Pomóż Wikipedii i dodaj przypisy do materiałów opublikowanych w wiarygodnych źródłach. |Sara Jean Underwood| Sara Jean Underwood w 2007 r. |Data i miejsce urodzenia||26 marca 1984 Scappoose, USA |Zawód||modelka| |Multimedia w Wikimedia Commons| Wystąpiła w kilku odcinkach reality show Króliczki Playboya (The Girls Next Door). Wystąpiła także w filmie Miss Marca, grała samą siebie.

16. `http://www.labtestsonline.pl/tests/Troponin.html?tab=3` tokens=1102 score=0.9294

   W jakich przypadkach badanie jest wykonywane? Badania troponiny I lub T zleca się przede wszystkim u pacjentów z bólem w klatce piersiowej, w celu wykluczenia lub potwierdzenia zawału serca albo innego uszkodzenia mięśnia sercowego. W praktyce laboratoryjnej stosuje się oznaczanie jednej z troponin I lub T. Oba te w niektórych przypadkach mogą być zastąpione oznaczaniem stężenia CK-MB masy. Troponinę można zlecić jako jedyne badanie albo razem z innym - wczesnym, ale nieswoistym dla serca markerem jakim jest mioglobina. Badanie sercowych troponin I lub T jest badaniem z wyboru ponieważ te markery są najbardziej swoiste dla mięśnia serca i wypiera oznaczenia innych markerów. Oznaczenie to pozwala rozpoznać zawał serca, ocenić rozległość uszkodzenia serca, wybrać optymalną strategię postępowania leczniczego, a także odróżnić zawał serca od bólu w klatce piersiowej z innej, niesercowej przyczyny. Troponina jest badaniem z wyboru u osób, które zgłaszają się do lekarza późno i u których objawy, takie jak ból lub dyskomfort w klatce piersiowej, poty, ból promieniujący do ramion, barków, żuchwy lub szyi, nudności lub zawroty głowy trwają dłużej niż dzień. Stężenie troponiny we krwi będ...

17. `http://pl.wikipedia.org/wiki/Brytania` tokens=537 score=0.8814

   Brytania (łac. Britannia lub Insula Albionum) – nazwa stosowana przez Rzymian w odniesieniu do dwóch największych Wysp Brytyjskich. Miasto Verulamium znajdujące się na obszarze obecnego miasta St Albans w hrabstwie Hertfordshire w Anglii (Wielka Brytania) i położone nad rzeką Ver było największym obok Londinium ośrodkiem rzymskim w Brytanii i od ok. 60 roku stolicą (municipium) rzymskiej prowincji[1][2]. Prowincje rzymskie ok. 120 n.e. Na czerwono zaznaczona Brytania. Personifikacja Brytanii (z prawej), z matką Rosją i Francją, z początku I wojny światowej Etymologia [edytuj] Dzisiejsza Wielka Brytania była określana jako Britannia Maior (Brytania Większa), natomiast dzisiejsza Irlandia była określana mianem Britannia Hibernia (Hibernia). Nazwa Brytania jest związana etymologicznie z Bretania, krainą we Francji. Obydwa obszary były zamieszkiwane przez ludność celtycką. Nazwa Brytania pochodzi od Pretannia. Diodorus Siculus określił ludność wysp brytyjskich jako Pretani. Brytanią nazywano też południową część wyspy, dla odróżnienia od Kaledonii, nigdy nie podbitej przez Rzymian i odgrodzonej od Brytanii Murem Hadriana. Brytanię w czasach rzymskich zasiedlała głównie ludność celty...

18. `http://pl.wikipedia.org/wiki/Front_Wyzwolenia_Narodowego_im._Farabunda_Mart%C3%ADego` tokens=2659 score=0.8584

   Front Wyzwolenia Narodowego im. Farabunda Martíego |Frente Farabundo Martí de Liberación Nacional| |Lider||Medardo González| |Data założenia||10 października 1980| |Adres siedziby||27 Calle Poniente #1316, San Salvador, El Salvador| |Deklarowana ideologia polityczna |Socjalizm demokratyczny Socjaldemokracja Marksizm Socjalizm XXI wieku |Deklarowane poglądy gospodarcze |Socjalizm| |Członkostwo międzynarodowe |Forum São Paulo| |Obecni posłowie||35| | |Salwador Ten artykuł jest częścią serii: Front Wyzwolenia Narodowego im. Farabunda Martíego (hiszp. Frente Farabundo Martí de Liberación Nacional, FMLN) – lewicowa partia polityczna (od 1992) w Salwadorze wywodząca się z organizacji partyzanckiej o tej samej nazwie powstałej w 1980 roku. Spis treści Struktura FMLN [edytuj] FMLN powstał w październiku 1980 w wyniku porozumienia czterech grup zbrojnej lewicy walczących z reżimem wojskowym w Salwadorze. Stanowiąc rodzaj koalicji FMLN łączył różne nurty umiarkowanej i radykalnej lewicy (guevaryści, komuniści, trockiści). FMLN stanowił skrzydło zbrojne politycznej reprezentacji centrolewicy skupionej we Froncie Demokratyczno-Rewolucyjnym (hiszp. Frente Democrático Revolucionario, FDR). W...

19. `http://www.agraart.pl/fogtt/wieza.php` tokens=431 score=0.9641

   WIEŻA ANDRZEJA || EUROPA MUSI POSTRZEGAĆ SIEBIE EKONOMICZNIE POLITYCZNIE I KULTURALNIE. KAŻDE PAŃSTWO MUSI ZDAWAĆ SOBIE SPRAWE, ŻE TEREN EUROPY JEST POLEM DIALOGU I WZAJEMNEJ WSPÓŁPRACY, I POZWALA POTWIERDZAĆ NASZA SIŁE I TOŻSAMOŚĆ". JAQUES DELORS, prezydent Komisji Europejskiej WIEŻA JEDNOśCI EUROPEJSKIEJ Myśl o wieży powstała w 1989 roku. W 1992 rozpocząłem pracę nad formą budowli. Gipsowy model ukończyłem 24 grudnia 1992 r. Jednocześnie wraz z moim przyjacielem, profesorem Jerzym Adamskim tworzyliśmy ideę wspólnej pomocy. Uświadomiłem sobie, że pomoc i zrozumienie jednoczy ludzi. Wieża Jedności Europejskiej jest budynkiem - symbolem wspólnoty ludzkie. W swym wyrazie stanowi bryłę szklaną, gdzie materia szkła wypełnia konstrukcję. Budowla jest "głosem" - zaopatrzona będzie w specjalnie skomponowany dźwięk. Jest światłem emanującym na zewnątrz i do wnętrza. Przewidywana wysokość 200 m. Proponowane funkcje Wieży Jedności Europejskiej: - światowe centrum pomocy i współpracy w tworzeniu warunków ekonomicznego i duchowego rozwoju ludzi. - Wielofunkcyjna przestrzeń dla organizacji targów, koncertów, wystaw, - studio RTV, - centrum Telekomunikacyjne (jest to otwarta propozycja dla św...

20. `http://pl.tripadvisor.com/Flights-g56609-San_Angelo_Texas-Cheap_Discount_Airfares.html` tokens=188 score=0.9028

   Zauważyliśmy, że używasz nieobsługiwanej przeglądarki. Witryna TripAdvisor może nie być wyświetlana poprawnie. Obsługiwane są następujące przeglądarki: Windows: Internet Explorer, Mozilla Firefox, Google Chrome. Mac: Safari. - San Angelo jest 12 km z Mathis Field (San Angelo, Teksas). - Mathis Field (San Angelo, Teksas) - Obecnie, 4 linie lotnicze działają na Mathis Field. - Mathis Field oferuje loty bezpośrednie do 2 miast. - Każdego tygodnia przynajmniej 84 krajowych i 0 międzynarodowych lotów startuje z Mathis Field. W serwisie TripAdvisor są wykorzystywane pliki cookie w celu usprawnienia korzystania ze stron. Dowiedz się więcej lub zmień ustawienia . Kontynuacja stanowi zgodę na przesyłanie plików cookie.

## Rejected Samples

1. `http://www.odyssei.com/forum/index.php?showtopic=97956` tokens=n/a score=n/a

   Super! Za 2000Y to ja nakupię 20 drobiazgów w sklepie 100-jenowym )) Super! A wracając do tematu... Nie mam zbyt wiele kasy. Zaliczyłam już Kamakurę, Yokohamę, prawie wszystko, co warto zwiedzić w Tokyo, na przyszły weekend szykuję wyprawę do Nikko. Jeśli prawdą jest, że mają dla mnie na Uniwersytecie dodatkowe fundusze na zwiedzanie, to po zaliczeniu Nikko zostanie mi jeszcze jakieś 10 kY. No i teraz mam dylemat... Bo na wiele to nie wystarczy. Gdzie pojechalibyście za 5000Y w jedną stronę z Tokyo na moim miejscu? Marzyło mi się Himeji, ale to ponad 15 kY w jedną stronę Podobnie Nara - prawie 15 kY. Więc na co mogłabym przeznaczyć taką sumę? W zasadzie przyznam, że mam już dość hałasu wielkomiejskiego. Chętnie wybyłabym gdzieś na łono przyrody, najlepiej takie łono przyrody o charakterze japońskim Szukałam połączenia z Hakone, ale nie znalazłam... Czy Hakone a Hakonegasaki to to samo? Był ktoś może w Okutama? Warto tam jechać? A w Hachioji? Bo znalazłam takie ulotki reklamowe do tych miejscowości, ale nie wiem, czy tam warto jechać... W każdym razie w jedną stronę zmieściłabym się w 1000Y.

2. `http://pl.wikipedia.org/wiki/Misteria_staro%C5%BCytne` tokens=n/a score=n/a

   Misteria starożytne Misteria starożytne – formy kultu religijnego dostępne jedynie dla osób wtajemniczonych, które przeszły rytuał inicjacji. Często odbywały się w nocy, odprawiano je przy śpiewie i tańcach, łączono z przedstawieniem, pokazującym mity związane z bóstwem, które czczono w misterium. Początki misteriów wiąże się z kultem Demeter i Dionizosa (misteria eleuzyjskie), które w VII wieku p.n.e zostały usankcjonowane jako element ateńskiego kultu państwowego. Pomiędzy III a I wiekiem p.n.e. (okres hellenistyczny) rozpowszechniły się orgie dionizyjskie oraz misteria orfickie, odwołujące się do mitu o pożarciu przez tytanów Dionizosa-Zagreusa i jego odrodzeniu w postaci Dionizosa-Lyseuksa (Wyzwoliciela). Synkretyzm religijny doby hellenistycznej doprowadził do rozwoju licznych misterów związanych z kultami wschodnimi: orgiastyczny kult Kybele i Attisa, syryjskie misteria ku czci Atargatis i Adonisa czy najszerzej rozpowszechnione obrzędy na cześć Izydy i Ozyrysa.

3. `http://pl.wikipedia.org/wiki/Chleby_pok%C5%82adne` tokens=n/a score=n/a

   Chleby pokładne Chleby były bardzo duże (do wypieku każdego z nich używano 2/10 efy najczystszej mąki, tj. ok. 4 l[1]) i układano je na złotym stole w dwa stosy – po sześć. Chleby składano w każdy szabat w Miejscu Świętym Namiotu Spotkania, a później w świątyni. Po tygodniu były usuwane; mogli zjeść je tylko kapłani. Ofiara chlebów pokładnych była symbolem wdzięczności Izraela dla Jahwe za chleb powszedni[2]. Odniesienia w Biblii [edytuj] Nakaz składania chlebów pokładnych w charakterze ofiary znajduje się w Księdze Kapłańskiej. Po rozdzieleniu chlebów na dwa stosy na każdym z nich kapłan miał położyć trochę kadzidła jako upamiętnienie ofiary spalanej dla Jahwe[3]. Pierwsza wzmianka o chlebach pokładnych znajduje się w Księdze Wyjścia, przy okazji nakazu zbudowania złotego stołu (Wj 25, 23–28): |„|| Będziesz zawsze kładł na stole przede mną chleby pokładne[4]. |”| Podobny fragment zawiera Księga Liczb: |„|| Chleb ustawicznej ofiary powinien również na nim [na stole] się znajdować[5]. |”|

4. `http://europa.eu/about-eu/eu-history/1945-1959/1947/index_pl.htm` tokens=n/a score=n/a

   Narzędzia dostępności Narzędzia serwisu Wybór języka Pod patronatem Winstona Churchilla powstaje Ruch Zjednoczonej Europy. Ruch jest przeciwny ponadnarodowym organom, opowiada się za współpracą międzyrządową. René Courtin tworzy Francuską Radę na rzecz Zjednoczonej Europy, która później zostanie wchłonięta przez Ruch Europejski (1953). Pod patronatem Chrześcijańskich Demokratów powstaje organizacja Nouvelles Equipes Internationales, która później będzie znana jako Europejska Unia Chrześcijańskich Demokratów (1965). Powstaje Ruch Socjalistycznych Zjednoczonych Państw Europy, który w 1961 r. zmieni nazwę na Lewicę Europejską. Ogłoszenie Planu Marshalla, którego celem jest ożywienie gospodarcze Europy. Kongres Unii Europejskich Federalistów w Montreux w Szwajcarii. Organizacje federalistów i unionistów spotykają się w ramach Międzynarodowego Komitetu Koordynacji Ruchów na rzecz Zjednoczenia Europy.

5. `http://pl.wikipedia.org/wiki/Waldemar_Hoven` tokens=n/a score=n/a

   Waldemar Hoven |Ten artykuł od 2010-04 wymaga uzupełnienia źródeł podanych informacji. Możliwe, że ten artykuł w całości albo w części zawiera informacje nieprawdziwe. Informacje bez źródeł w każdej chwili mogą zostać zakwestionowane i usunięte. Pomóż Wikipedii i dodaj przypisy do materiałów opublikowanych w wiarygodnych źródłach. Urodzony we Fryburgu, studia medyczne rozpoczął w wieku 32 lat, aby objąć po swoim bracie sanatorium. W 1934 wstąpił do SS oraz do NSDAP w 1937. W 1939 ukończył studia medyczne, dzięki specjalnej sesji związanej z jego przyjęciem do Waffen-SS. W 1941 został asystentem Enno Lollinga (szefa Urzędu D III w WVHA, czyli naczelnego lekarza wszystkich obozów koncentracyjnych). W latach 1941-1943 Hoven był naczelnym lekarzem obozowym w Buchenwaldzie. Podczas swojej służby w tym obozie dopuścił się licznych zbrodni, zwłaszcza mordując wielu więźniów i radzieckich jeńców wojennych zastrzykami z fenolu lub benzyny. Oprócz tego zabił także w ten sposób kilku oficerów SS, którzy byli potencjalnymi świadkami w sprawie przeciw byłemu komendantowi Buchenwaldu Karlowi Kochowi. Hoven został w związku z tym aresztowany we wrześniu 1943 i postawiony przed sądem SS. Za zab...

6. `http://pl.tripadvisor.com/Hotel_Review-g551924-d642606-Reviews-Bay_Glenburn_Hotel-Rothesay_Isle_of_Bute_Argyll_and_Bute_Scotland.html` tokens=n/a score=n/a

   choruję na stwardnienie rozsiane właśnie wróciliśmy z kolejnego wakacjami Shearings przerwy. Doskonały stosunek jakości do ceny. W hydro w pitlockry było ciepłe, czyste. Piękne widoki. Jedzenie dobre, z rozsądnym wyborem. Basen nie do relaksu. Rozrywka była dobra. Wyróżnienie dla Gordona z kierowca autokaru, którzy zapewnili nam odpowiednie informacje na temat wycieczek z własną marką humoru. Kolejny sukces. - Znany także jako: - Glenburn Hotel Rothesay

7. `http://pl.wikipedia.org/wiki/Komitet_%22Fair_Play%22_wobec_Kuby` tokens=n/a score=n/a

   Komitet „Fair Play” wobec Kuby |Ten artykuł opisuje część Śledztwa Jima Garrisona nad zabójstwem Johna F. Kennedy'go |Ludzie| |Jim Garrison| |John F. Kennedy| |Clay Shaw| |David Ferrie| |Perry Russo| |Guy Banister| |George de Mohrenschildt| |Grupy| |Komitet „Fair Play” wobec Kuby| |Kubański Demokratyczny Front Rewolucyjny| |Powiązane artykuły| |Proces Claya Shawa| |Ludzie powiązani z procesem Claya Shawa| Komitet „Fair Play” wobec Kuby (Fair Play for Cuba Committee - FPCC)- była to grupa aktywistyczna utworzona w Nowym Jorku w kwietniu 1960 roku[1]. Celem FPCC było zwiększenie poparcia wśród obywateli dla rewolucji kubańskiej, w czasie gdy Fidel Castro zaczął otwarcie przyznawać się do marksizmu, rozpoczynając wywłaszczenie oraz nacjonalizacje kubańskich aktywów należących do korporacji amerykańskich. Komitet protestował przeciwko inwazji w Zatoce Świń w 1961 roku, nałożeniu embarga przez USA na Kubę oraz popierał stanowisko Kuby podczas kryzysu kubańskiego w 1962 roku. Lokalne komitety "Fair Play" zostały założone na terytorium Stanów Zjednoczonych oraz Kanady. Wśród pierwszych zwolenników Komitetu znalazły się znane osoby: William Appleman Williams, Norman Mailer, Allen Ginsbe...

8. `http://gotquestions.org/Polski/czysciec.html` tokens=n/a score=n/a

   Co Biblia mówi na temat czyśćca? Pytanie: Co Biblia mówi na temat czyśćca? Odpowiedź: Według Encyklopedii Katolickiej, czyściec jest “miejscem lub stanem przejściowej kary dla tych, którzy odeszli z tego świata w Bożej łasce, ale nie są całkowicie wolni od grzechów powszednich albo dla tych, którzy w pełni nie spłacili zadośćuczynienia za swoje występki”. Podsumowując, w teologii katolickiej czyściec to miejsce gdzie dusza chrześcijanina udaje się po śmierci, aby być oczyszczona z grzechów, które nie zostały w pełni zadośćuczynione w czasie życia. Czy doktryna czyśćca pozostaje w zgodzie z Biblią? Absolutnie nie! Jezus umarł, aby zapłacić karę za wszystkie nasze grzechy (Rzymian 5:8). Izajasza 53:5 mówi: “Lecz on zraniony jest za występki nasze, starty za winy nasze. Ukarany został dla naszego zbawienia, a jego ranami jesteśmy uleczeni.” Jezus cierpiał za nasze grzechy abyśmy mogli zostać uwolnieni od cierpienia. Powiedzenie, że my także musimy cierpieć za nasze grzechy jest stwierdzeniem, że cierpienie Jezusa było niewystarczające. Powiedzenie, że musimy odpokutować nasze grzechy przez oczyszczenie się w czyśćcu jest zaprzeczeniem wystarczalności ofiary przebłagalnej Chrystusa...

9. `http://pl.wikipedia.org/wiki/Czarny_%C5%BB%C3%B3%C5%82w` tokens=n/a score=n/a

   Czarny Żółw Czasami nazywany Czarnym Wojownikiem Północy (北方玄武), gdyż w podziale kompetencji przypadła mu domena Północy (w sensie strony świata) oraz zimy. Znany jest również pod chińskim imieniem Xuánwǔ, często tłumaczonym jako Czarny Żółw, a zazwyczaj przedstawiany jako żółw i wąż, a dokładniej - jako wąż owinięty wokół żółwia. Gwiazdozbiory chińskie były używane nie tylko przez chińskich kartografów z dynastii Han, lecz również przez kartografów japońskich i koreańskich. W języku japońskim Czarny Żółw nazywany jest Genbu, a jego rysunki można znaleźć w mandze i anime. Spis treści Siedem Pałaców Czarnego Żółwia [edytuj] Tak jak wszystkim Strażnikom Nieba, również Czarnemu Żółwiowi podlega siedem gwiazdozbiorów chińskich. Są nimi: - Nurek pinyin 斗, Dǒu - Wół pinyin 牛, Niú - Dziewczyna pinyin 女, Nǚ - Pustka pinyin 虛, Xū - Szczyt Dachu pinyin危, Wēi - Obozowisko pinyin 室, Shì - Ściana pinyin 壁, Bì Pochodzenie [edytuj] W starożytnych Chinach żółw i wąż były, w sensie religijnym i duchowym, symbolami długowieczności. Za czasów dynastii Han Chińczycy często nosili wisiorki i amulety w kształcie żółwia. W wyniku wpływów kultury chińskiej na sąsiednią Japonię, japońskie tytuły szlache...

10. `http://pl.wow.wikia.com/wiki/Rise_of_the_Blood_Elves` tokens=n/a score=n/a

   W tym samym czasie nieumarła Plaga przemieniła większość Lordaeron i Quel'Thalas w toksyczne Ziemie Plagi. Pozostało tylko kilka nielicznych oddziałów oporu Przymierza. Jedna z takich grup, składająca się głównie z wysokich elfów, była prowadzona przez ostatniego z dynastii Sunstriderów: Księcia Kael'thasa. Kael, wykształcony czarodziej, obawiał się upadku Sojuszu. Wysokie elfy opłakiwały utratę swojej ojczyzny i zdecydowały nazywać się krwawymi elfami ku czci poległego ludu. Jednak gdy działali, by trzymać Plagę w ryzach, okrutnie cierpieli od odcięcia od Słonecznej Studni, która ich wzmacniała. Zdesperowany, by odnaleźć lekarstwo na uzależnienie od magii swego ludu, Kael dokonał czegoś, co wydawało sięnie do pomyślenia: zebrał dziedzictwo Wysoko Urodzonych i przyłączył się do Illidana i jego nag w nadziei odnalezienia nowej mocy magicznej, którą elfy będą mogły się żywić. Pozostali dowódcy Przymierza ogłosili krwawe elfy zdrajcami i wygnali je na dobre. Nie mając dokąd pójść, Kael i jego krwawe elfy podązyli za Lady Vashj do Outland, by pomóc pokonać Maiev, która ponownie uwięziła Illidana. Połączywszy siły, nagi i krwawe elfy pokonały Maiev i wyzwoliły Illidana. Bazując w Out...

11. `http://forum.gazeta.pl/forum/w,211,22702624,,Czy_macie_jakies_triki_na_gladkie_i_miekkie_piety_.html?v=2&wv.x=1` tokens=n/a score=n/a

   zamiast zwykłych tarek i pumeksów polecam węglikowe (np. firmy Gulivere, można kupić na targach medycyny naturalnej albo wysyłkowo od firmy) oraz krem do stóp z kwasami AHA Avonu - stopy mam po nim wyczuwalnie gładsze i bardziej miękkie, a tarki węglikowe zapobiegają narastaniu i grubieniu naskórka. -- Forum Nu Skin Zanim zapytasz...

12. `http://support.microsoft.com/kb/310429/pl` tokens=n/a score=n/a

   W tym artykule opisano krok po kroku, jak usuwać elementy z paska zadań. Wielu producentów oprogramowania projektuje swoje programy w taki sposób, aby uruchamiały program na pasku zadań w celu zwiększenia dostępności (i widoczności) produktu. Mimo że programy paska zadań mogą ułatwiać uzyskiwanie dostępu do programów i sterowanie nimi, użytkownik czasami nie korzysta z niektórych ikon na pasku zadań, a ikony te niepotrzebnie zajmują miejsce. Ukrywanie programu paska zadań przy jednoczesnym zezwoleniu na działanie programu głównego w tle Wiele programów udostępniających formanty na pasku zadań ma opcję ukrywania ikony na pasku zadań bez zatrzymywania właściwego programu. Przykładami ikon takich programów są: zegar systemowy, wskaźnik głośności i stan sieci. - Aby zapobiec wyświetlaniu zegara na pasku zadań: - Kliknij przycisk Start, wskaż polecenie Ustawienia, a następnie kliknij polecenie Pasek zadań i menu Start. - Wyczyść pole wyboru Pokaż zegar, a następnie kliknij przycisk OK. - Aby zapobiec wyświetlaniu ikony połączenia sieciowego na pasku zadań: - Kliknij prawym przyciskiem myszy ikonę Moje miejsca sieciowe, a następnie kliknij polecenie Właściwości. - Kliknij połączenie s...

13. `http://www.did.kuchnia.com.pl/DiD/salat.html` tokens=n/a score=n/a

   Opowieści znad talerza Okolica na talerzu Księga gości Napisz do mnie Adresy kuchenne SAŁATKI I SURÓWKI SAŁATKA Z CZERWONEJ KAPUSTY Spora główka czerwonej kapusty, 1 cebula, 3-4 winne jabłka, sól, ocet, olej, cukier Kapustę poszatkować, ugotować w dużej ilości wody z octem i solą, odcedzić na pół ugotowaną. Cebulę pokrajać, jabłka zetrzeć na grubej tarce. Wymieszać kapustę z jabłkami i cebulą, doprawić olejem, octem, solą i cukrem. SAŁATKA ŚRÓDZIEMNOMORSKA 1 puszka kukurydzy, 2 strąki papryki (czerwonej i zielonej), 1 świeży ogórek, szczypiorek SOS : 2 łyżki octu, 6 łyżek oleju, 2 łyżki keczupu, sól, pieprz, sos Tabasco do smaku Paprykę i ogórka pokroić w bardzo drobną kosteczkę. Dodać osączoną kukurydzę, dokładnie wymieszać. Przygotować sos: olej utrzeć z octem, dodać keczup, przyprawić solą, pieprzem i sosem Tabasco. Polać tym warzywa, dobrze wymieszać, przed podaniem posypać posiekanym szczypiorkiem. SAŁATKA SZANGHAJSKA Kapusta pekińska, 2 kwaśne jabłka, majonez, musztarda, uprażone ziarnka sezamu, posiekane orzechy włoskie Kapustę drobno poszatkować, jabłka zetrzeć na grubej tarce. Majonez doprawić niewielką ilością musztardy, wymieszać z kapustą i jabłkami, doprawić solą i...

14. `http://www.kan.de/pl/big/publikacje/kanbrief/kandocs/fed3b1f6a16b61da76c5c9474a5e1f2d/kanbrief/2136.html` tokens=n/a score=n/a

   KANBrief Cele: KANBrief dostarcza informacji o zagadnieniach ochrony pracy w procesach normalizacji. Ma przede wszystkim zwiększać zainteresowanie a tematyką oraz poprawiać wymianę informacji pomiędzy ekspertami z dziedziny bezpieczeństwa i zdrowia w pracy biorącymi udział w procesach normalizacji a KAN. Ma on również wspomagać porozumienie się z ekspertami BHP w innych krajach UE. Zawartość: "Brief" oznacza w języku angielskim "krótko/ zwięźle", co wskazuje na charakter artykułów. Są one sporządzane przez referentów Biura KAN, członków Komisji KAN lub autorów "z zewnątrz". Każde wydanie KANBrief posiada temat wiodący, zawiera kilka krótkich artykułów o różnorodnej tematyce i część serwisową z krótkimi informacjami, a także wzmianki o publikacjach, przedsięwzięciach oraz adresach internetowych. Ze względu na europejski i w coraz większej mierze międzynarodowy wymiar normalizacji, KANBrief sporządzany jest w trzech wersjach językowych. Dystrybucja: KANBrief pojawia się co kwartał. Dystrybucja wydrukowanych publikacji prowadzona jest bezpłatnie drogą pocztową. Jeśli chcielibyście Państwo otrzymywać KANBrief, proszę przesłać nam e-mail z krótką informacją. Wszystkie pozostałe wydan...

15. `http://pl.wikipedia.org/wiki/Majolika` tokens=n/a score=n/a

   Majolika Majolika – ceramika pokryta nieprzezroczystą polewą ołowiowo-cynową o bogatej kolorystyce. Rodzaj fajansu produkowanego we Włoszech od XIV w. do XVII w. Z majoliki wyrabiano przede wszystkim bogato zdobione naczynia. Produkcja majoliki rozwinęła się pod wpływem ceramiki mauretańsko-hiszpańskiej importowanej do Włoch przez Majorkę (stąd nazwa). W XV wieku produkcję rozpoczęto także we Florencji (wprowadzono rzeźby z majoliki). Na początku XVI w. rozwinął się styl istoriato (narracyjny), czyli zdobienie scenami mitologicznymi, historycznymi oraz biblijnymi. Malarzami tego stylu byli zazwyczaj wybitni artyści, a inspiracji szukali w dziełach Rafaela i jego uczniów.

16. `http://www.berzinarchives.com/web/pl/archives/sutra/level1_getting_started/approaching_study_meditation/dealing_difficulties_meditation.html` tokens=n/a score=n/a

   Radzenie sobie z trudnymi doświadczeniami pojawiającymi się podczas odosobnień Monachium, Niemcy, 12 lipca 2002 Tłumaczenie na polski: Milena Bianga W ramach Czterech Szlachetnych Prawd Budda nauczał o problemach, ich przyczynach, stanie ich całkowitego usunięcia oraz ścieżkach umysłu, które prowadzą do usunięcia problemów. Z tego względu, aby nauczyć się radzić sobie z trudnymi doświadczeniami, które pojawiają się podczas medytacji i w czasie odosobnień, oraz usunąć je, musimy najpierw dowiedzieć się, jakie są przyczyny tych problemów. Zrównoważona praktyka buddyjska obejmuje trzy obszary: - konstruktywny pogląd, podejście lub postawę (lta-ba); - medytowanie nad tym poglądem (sgom), co oznacza przyzwyczajanie się do niego; - zintegrowanie tego poglądu z naszymi codziennymi zachowaniami (spyod-pa). Jeśli brakuje któregokolwiek z tych elementów, nasza praktyka przyniesie bardzo ograniczone korzyści. Prawdopodobnie napotkamy trudności i doświadczymy frustracji — nie tylko w medytacji, ale także w życiu. - Próbowanie medytacji bez konstruktywnego poglądu czy postawy jako stanu umysłu, który chcemy rozwinąć za pomocą medytacji, daje niewiele. - Uczenie się o konstruktywnej postawie...

17. `http://pl.wikipedia.org/wiki/Mistrzostwa_%C5%9Bwiata_w_hokeju_na_lodzie_m%C4%99%C5%BCczyzn` tokens=n/a score=n/a

   Mistrzostwa świata w hokeju na lodzie mężczyzn Mistrzostwa Świata w hokeju na lodzie mężczyzn – międzynarodowy turniej hokejowy organizowany przez IIHF. Poprzednikiem były Mistrzostwa Europy, które odbywały się między 1910 a 1932 rokiem. Igrzyska olimpijskie w Antwerpii zalicza się jako pierwsze mistrzostwa świata. Tak też było przez kolejne 11 imprez. Ostatnim razem połączono igrzyska z mistrzostwami w 1968 roku w Grenoble. Dotychczas czempionat rozegrano 76 razy. Najczęściej wygrywali Rosjanie (w tym ZSRR) którzy zdobyli 26 tytułów. Spis treści Historia [edytuj] Pierwsze Mistrzostwa Świata w hokeju na lodzie mężczyzn rozegrano w 1920 roku na letnich igrzyskach olimpijskich w Antwerpii. Natomiast następne mistrzostwa zostały rozegrane na Zimowych igrzyskach olimpijskich w Chamonix. Pierwsze trzy mistrzostwa były rozgrywane co cztery lata na igrzyskach olimpijskich. Dopiero roku 1930 zaczęto je rozgrywać co rok. Od 1920 do 1968 jeśli mistrzostwa odbywały się w roku olimpijskim to rozgrywano je na igrzyskach olimpijskich. W latach między wojennych od 1920 do 1939 mistrzostwa zostały zdominowane przez reprezentację Kanady. (zdobyli 11 tytułów mistrzowskich na 13 możliwych). Podcza...

18. `http://pl.wikipedia.org/wiki/M%C4%99czennik` tokens=n/a score=n/a

   Męczennik W chrześcijaństwie, a szczególnie w katolicyzmie i prawosławiu był to chrześcijanin, który został uśmiercony przez prześladowcę za wiarę w Jezusa Chrystusa. Taka śmierć określana jest mianem śmierci męczeńskiej. Pojęcie męczeństwa istnieje także w pozostałych religiach abrahamicznych oraz w sikhizmie, częściowo również w hinduizmie i shintō. Pojęcie męczeństwa było też wykorzystywane przez ideologie państwowe np. w III Rzeszy i w Chinach. Spis treści Śmierć męczeńska[edytuj] Śmierć męczeńska jest wyrazem bezwzględnego przywiązania do idei i przekonań dlatego ma ogromne znaczenie w utrwalaniu postaw i wzorców kulturowych lub religijnych. Przykładem takich wzorców w kulturze polskiej może być męczeństwo dzieci głogowskich lub tzw. Męczennicy katyńscy. Najważniejsze jednak znaczenie śmierć męczeńska ma w wymiarze religijnym. Jednak nie każda religia ma swoich męczenników, a tylko niektóre z nich otaczają ich kultem. Pojęcie męczeństwa za wiarę istnieje w chrześcijaństwie, judaizmie i islamie, ale w zasadzie nie występuje np. w hinduizmie i buddyzmie. Bardzo wyraźnie widać zjawisko męczeństwa w chrześcijaństwie, gdzie męczennicy traktowani byli od początku jako najwierniej...

19. `http://pl.wikipedia.org/wiki/Rickenbacker` tokens=n/a score=n/a

   Rickenbacker Rickenbacker, właściwie Rickenbacker International Corporation (RIC) – pierwszy na świecie producent gitar elektrycznych z siedzibą w Santa Ana w Kalifornii istniejący do dnia dzisiejszego. Korporacja rozwinięta z przedsiębiorstwa założonego w celu tworzenia i produkcji instrumentów całkowicie opartych na podzespołach elektronicznych, oraz produkującego wzmacniacze elektroakustyczne. Przedsiębiorstwo założyli w 1931 roku Adolph Rickenbacker i George Beauchamp. "Rickenbacker Electro Instruments" wyprodukowała pierwsze nowoczesne gitary elektryczne. Historia RIC sięga 76 lat w interesie muzycznym. Gitarę tej firmy posiadał m.in John Lennon, George Harrison, a także Per Gessle z duetu Roxette (vide teledysk: Joyride, Dangerous, It must have been love). Gitarą basową Rickenbackera posługiwał się chociażby Cliff Burton czy Paul McCartney, do dziś używa ich Lemmy Kilmister.

20. `http://pl.wikipedia.org/wiki/Angelo_Dundee` tokens=n/a score=n/a

   Angelo Dundee Karierę trenerska rozpoczął w końcu lat 40. XX wieku w Nowym Jorku. Pierwszym mistrzem świata, którego trenował był Carmen Basilio. Po przeniesieniu się do Miami Beach w 1960 rozpoczął współpracę z Muhammadem Alim, która trwała do jego ostatniej walki w 1981. Równocześnie trenował mistrzów Jimmy'ego Ellisa, Luisa Rodrigueza, Sugara Ramosa, Williego Pastrano i Ralpha Dupasa. W 1976 rozpoczął współpracę z Sugarem Rayem Leonardem doprowadzając go do trzech tytułów mistrza świata. U schyłku kariery służył pomocą George'owi Foremanowi. W roku 1992 został przyjęty do Międzynarodowej Galerii Sław Boksu.

## Recommendation

A) FineWeb2 PL is usable as a controlled v2.3 candidate. Build variant A first (~300M tokens), then inspect reports before any stage 3 training.
