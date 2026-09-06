# Glyph-100M v2.3.1 45k samples

Base LM completion eval. To nie jest eval asystenta ani instruction-following.

- checkpoint: `checkpoints/glyph-100m-v2_3_1-45k/latest.pt`
- step: `45000`
- variant: `glyph-100m`
- dataset: `glyph100_v2_3_1`
- tokenizer sha256 actual: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`

## g100-eval-001 · krotka_kontynuacja · normal_80

**Prompt:** `Warszawa to`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260609

**Output:**

```text
Warszawa to jeden z najnowocześniejszych i najbardziej prestiżowych projektów modernizacji Polski. W listopadzie 2012 roku wydano w Polsce książkę poświęconą modernizacji i modernizacji infrastruktury drogowej. Za realizację projektu odpowiadała firma KPZM, która jest obecnie jednym z najbardziej znanych kierunków modernizacji transportu publicznego na świecie. Podkreślana jest również mianem „otwartego transportu kolejowego w Polsce
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.59

## g100-eval-002 · krotka_kontynuacja · normal_80

**Prompt:** `Polska jest`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260610

**Output:**

```text
Polska jest częścią Unia Socjalistyczna. Historia W latach 50. XX w. wieś w powiecie strzeleckim w gminie Strzelce Krajeńskie. W latach 1975–1998 miejscowość administracyjnie należała do województwa kaliskiego. Osada leży na wschodnim skraju wsi, w odległości około 50 km od Strzelc Krajeńskich. Na północny zachód od wsi znajduje się jezioro Piaseczno. Pia
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach', 'województwa', 'powiecie', 'gminie']
**Quality score:** 3
**Tok/s generation:** 73.51

## g100-eval-003 · edukacyjny · normal_80

**Prompt:** `W fizyce energia`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260611

**Output:**

```text
W fizyce energia makroskopowa jest jednak proporcjonalna do ilości promieniowania. W przypadku niektórych pierwiastków lub pierwiastków, energia makroskopowa jest równa zeru. Energia makroskopowa jest również równa zeru (oznaczaną dla promieniowania elektromagnetycznego). Ze względu na ograniczona pojemność masową jest to masa promieniowania elektroma
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.47

## g100-eval-004 · edukacyjny · normal_80

**Prompt:** `Sztuczna inteligencja jest`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260612

**Output:**

```text
Sztuczna inteligencja jest częścią kultury, która miałaby stać się swoistym elementem kultury. Wpłynęła ona na rozwój społecznego dziedzictwa kulturalnego i kulturalnego. Inni popłynęli w kierunku badań nad kulturą starożytną. Kultura starożytna, w której kultura stała się podstawą jej rozwoju, miała wpływ na sztukę. Za początek kultury starożytnej uznano dzieła sztuki starożytnej i nowożytnej (
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.45

## g100-eval-005 · skladnia · normal_80

**Prompt:** `Rower składa się z`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260613

**Output:**

```text
Rower składa się z trzech części: I – dookoła lasu, oraz II – dookoła lasu. Do najszerszej części należą również: I – dookoła lasu, I – dookoła lasu, I – dookoła lasu. Po stronie południowej występują trzy dookoła lasu. I – dookoła lasu, z domieszką drzew, które występują w domieszce drzew,
```

**Heurystyka:** Problemy: powtórzenia 5, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 0
**Tok/s generation:** 72.74

## g100-eval-006 · web_garbage · normal_80

**Prompt:** `Według najnowszych danych`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260614

**Output:**

```text
Według najnowszych danych GUS z 30 czerwca 2014 r. miasto miało 14 315 mieszkańców. Miasto zostało zniszczone przez trzęsienia ziemi; w latach 1975–1998 miasto administracyjnie należało do województwa piotrkowskiego. Do roku 2023 miasto było siedzibą gminy o tej samej nazwie. Demografia Piramida wieku mieszkańców GUS w 2014 roku. Zabytki Do wojewódzkiego rejestru zabytków wpisane są obiekty: kościół parafialny
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach', 'województwa']
**Quality score:** 4
**Tok/s generation:** 72.79

## g100-eval-007 · projektowy · normal_80

**Prompt:** `Najważniejszym problemem tego projektu jest`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260615

**Output:**

```text
Najważniejszym problemem tego projektu jest to, że nie są one już w pełni zrealizowane. Nie jest to zatem tak proste, jak tylko budowanie stamtąd, aby móc korzystać z rozwiązań konstrukcyjnych, nie tylko w kontekście konstrukcji stałych, ale również budowy stałych. Jak się więc okazuje, projektowanie stałych i cięższych stałych instalacji w różnych miejscach świata nie ma sensu. To prawda, że każdy ma
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 71.91

## g100-eval-008 · edukacyjny · normal_80

**Prompt:** `Uczenie maszynowe polega na`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260616

**Output:**

```text
Uczenie maszynowe polega na maszynie na ciągłym ruchu (w zależności od rodzaju wykonywanego ruchu np. na ciągłym ruchu wahadłowego lub na ciągłym ruchu wahadłowego), np. rozprężanie o napięciu przemiennym. Izolacja i aerodynamika Mechanizm hydrazynowy Mechanizm hydrazynowy – w którym w wyniku procesu uczenia się siły w kierunku ruchu waha
```

**Heurystyka:** Problemy: powtórzenia 1, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 4
**Tok/s generation:** 72.02

## g100-eval-009 · encyklopedyczny · normal_80

**Prompt:** `W średniowieczu`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260617

**Output:**

```text
W średniowieczu tereny dzisiejszej Polski były tu podzielone pomiędzy najstarszą (ponad 10 mórg): ziemię raciborską i ziemię łukowską. W kolejnych wiekach książęta czescy z dynastii Jagiellonów założyli tu parafię św. Anny. W mieście działał także kościół pw. Miłosierdzia Bożego. W 1428 roku kościół został splądrowany przez wojska mo
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 73.04

## g100-eval-010 · skladnia · normal_80

**Prompt:** `Na początku eksperymentu`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260618

**Output:**

```text
Na początku eksperymentu na temat metod i metod przetwarzania danych, a także za pośrednictwem interfejsu nawigacyjnego oraz innych informacji. W latach 1851–1856 opracował program badawczy i wydawał czasopismo naukowe, które ukształtowało się kilka innych dyscyplin badawczych i społecznych na całym świecie. Jako pierwszy w historii tej dyscypliny badał głównie fizykę, biologię, fizykę, literaturę, e
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Quality score:** 5
**Tok/s generation:** 72.76

## g100-eval-011 · petle · normal_80

**Prompt:** `Ten tekst nie powinien powtarzać tego samego zdania, ponieważ`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260619

**Output:**

```text
Ten tekst nie powinien powtarzać tego samego zdania, ponieważ w tym samym języku literackim nie ma słów „poprawny” i „prawny” i „prawny”. Innym językiem, który często jest używany w literaturze i literaturze, ale jest to język pisany w kontekście poetyckim, który w sposób nierównolegle z jego poglądem na język, nie powinien być używany w literaturze i sztuce. Z tego
```

**Heurystyka:** Problemy: powtórzenia 1, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 4
**Tok/s generation:** 70.38

## g100-eval-012 · forum_garbage · normal_80

**Prompt:** `Komentarze użytkowników wskazują, że`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260620

**Output:**

```text
Komentarze użytkowników wskazują, że większość użytkowników Internetu w Stanach Zjednoczonych ma dostęp do Internetu. W listopadzie 2019 roku IBM uruchomił dystrybucję IBM (Operation Corporation) – część sieci IBM – pierwsza sieć IBM, która miała dostęp do Internetu i sieci GSM. IBM jest w pełni kompatybilne z IBM, gdyż wszystkie te strony są nadawcami IB
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.09

## g100-eval-001 · krotka_kontynuacja · normal_120

**Prompt:** `Warszawa to`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260609

**Output:**

```text
Warszawa to jeden z najnowocześniejszych i najbardziej prestiżowych projektów modernizacji Polski. W listopadzie 2012 roku wydano w Polsce książkę poświęconą modernizacji i modernizacji infrastruktury drogowej. Za realizację projektu odpowiadała firma KPZM, która jest obecnie jednym z najbardziej znanych kierunków modernizacji transportu publicznego na świecie. Podkreślana jest również mianem „otwartego transportu kolejowego w Polsce”. Transport lotniczy W 2017 roku ukończono budowę trasy kolejowej łączącej Warszawę z Łodzią, które to linie obsługiwane były przez PKS. Przewozów pasażerskich dojeżdżają pociągi
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 67.13

## g100-eval-002 · krotka_kontynuacja · normal_120

**Prompt:** `Polska jest`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260610

**Output:**

```text
Polska jest częścią Unia Socjalistyczna. Historia W latach 50. XX w. wieś w powiecie strzeleckim w gminie Strzelce Krajeńskie. W latach 1975–1998 miejscowość administracyjnie należała do województwa kaliskiego. Osada leży na wschodnim skraju wsi, w odległości około 50 km od Strzelc Krajeńskich. Na północny zachód od wsi znajduje się jezioro Piaseczno. Piaski – wieś w Polsce położona w województwie lubelskim, w powiecie łukowskim, w gminie Łuki. Wieś szlachecka, położona była w drugiej połowie XVI wieku w powiecie łukowskim województwa lubelskiego
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach', 'województwa', 'powiecie', 'gminie']
**Quality score:** 3
**Tok/s generation:** 66.94

## g100-eval-003 · edukacyjny · normal_120

**Prompt:** `W fizyce energia`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260611

**Output:**

```text
W fizyce energia makroskopowa jest jednak proporcjonalna do ilości promieniowania. W przypadku niektórych pierwiastków lub pierwiastków, energia makroskopowa jest równa zeru. Energia makroskopowa jest również równa zeru (oznaczaną dla promieniowania elektromagnetycznego). Ze względu na ograniczona pojemność masową jest to masa promieniowania elektromagnetycznego, które jednak są w stanie się uzyskać dopiero podczas pomiaru czasu lub przestrzeni (w efekcie natężenie prądu w kierunku kierunku osi momentu do kierunku osi momentu, gdzie w próżni
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.38

## g100-eval-004 · edukacyjny · normal_120

**Prompt:** `Sztuczna inteligencja jest`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260612

**Output:**

```text
Sztuczna inteligencja jest częścią kultury, która miałaby stać się swoistym elementem kultury. Wpłynęła ona na rozwój społecznego dziedzictwa kulturalnego i kulturalnego. Inni popłynęli w kierunku badań nad kulturą starożytną. Kultura starożytna, w której kultura stała się podstawą jej rozwoju, miała wpływ na sztukę. Za początek kultury starożytnej uznano dzieła sztuki starożytnej i nowożytnej (np. dzieła Hektora z Aleksandrii). Poszukiwania i zasługi dla cywilizacji starożytnej zostały opisane w pracy A. de Chevaliers (1847) s. 34,
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.44

## g100-eval-005 · skladnia · normal_120

**Prompt:** `Rower składa się z`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260613

**Output:**

```text
Rower składa się z trzech części: I – dookoła lasu, oraz II – dookoła lasu. Do najszerszej części należą również: I – dookoła lasu, I – dookoła lasu, I – dookoła lasu. Po stronie południowej występują trzy dookoła lasu. I – dookoła lasu, z domieszką drzew, które występują w domieszce drzew, które występują w domieszce drzew liściastych. W domieszce drzew liściastych i mieszanych występuje również kilka gatunków drzew liściastych: Lipa drobnolistna (
```

**Heurystyka:** Problemy: powtórzenia 9, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 0
**Tok/s generation:** 66.72

## g100-eval-006 · web_garbage · normal_120

**Prompt:** `Według najnowszych danych`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260614

**Output:**

```text
Według najnowszych danych GUS z 30 czerwca 2014 r. miasto miało 14 315 mieszkańców. Miasto zostało zniszczone przez trzęsienia ziemi; w latach 1975–1998 miasto administracyjnie należało do województwa piotrkowskiego. Do roku 2023 miasto było siedzibą gminy o tej samej nazwie. Demografia Piramida wieku mieszkańców GUS w 2014 roku. Zabytki Do wojewódzkiego rejestru zabytków wpisane są obiekty: kościół parafialny pw. Przemienienia Pańskiego z XIV w., w tym: kościół pw. św. Piotra z 1300 r. – XV w. kościół pw. św. Anny z XIX wieku kościół pw
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach', 'województwa']
**Quality score:** 4
**Tok/s generation:** 66.66

## g100-eval-007 · projektowy · normal_120

**Prompt:** `Najważniejszym problemem tego projektu jest`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260615

**Output:**

```text
Najważniejszym problemem tego projektu jest to, że nie są one już w pełni zrealizowane. Nie jest to zatem tak proste, jak tylko budowanie stamtąd, aby móc korzystać z rozwiązań konstrukcyjnych, nie tylko w kontekście konstrukcji stałych, ale również budowy stałych. Jak się więc okazuje, projektowanie stałych i cięższych stałych instalacji w różnych miejscach świata nie ma sensu. To prawda, że każdy ma swoje zalety i zalety, a co najważniejsze, nie zawsze musi więc być zgodne z ich przeznaczeniem. Warto zastanowić się nad tym, co warto zaplanować w konkretnych miejscach. W tym artyku
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.13

## g100-eval-008 · edukacyjny · normal_120

**Prompt:** `Uczenie maszynowe polega na`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260616

**Output:**

```text
Uczenie maszynowe polega na maszynie na ciągłym ruchu (w zależności od rodzaju wykonywanego ruchu np. na ciągłym ruchu wahadłowego lub na ciągłym ruchu wahadłowego), np. rozprężanie o napięciu przemiennym. Izolacja i aerodynamika Mechanizm hydrazynowy Mechanizm hydrazynowy – w którym w wyniku procesu uczenia się siły w kierunku ruchu wahadła. W wyniku tego procesu, drgania i uczenia się siły ujemnej i o napięciu w osi obrotu aerodynamika ulegają zmianie, co prowadzi do uczenia się
```

**Heurystyka:** Problemy: powtórzenia 1, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 4
**Tok/s generation:** 66.23

## g100-eval-009 · encyklopedyczny · normal_120

**Prompt:** `W średniowieczu`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260617

**Output:**

```text
W średniowieczu tereny dzisiejszej Polski były tu podzielone pomiędzy najstarszą (ponad 10 mórg): ziemię raciborską i ziemię łukowską. W kolejnych wiekach książęta czescy z dynastii Jagiellonów założyli tu parafię św. Anny. W mieście działał także kościół pw. Miłosierdzia Bożego. W 1428 roku kościół został splądrowany przez wojska moskiewskie. W latach 1518–1531 miasto przechodziło bez walki z wojskami litewskimi pod dowództwem Jana z Podiebradów. Pod koniec XVI wieku miasto zostało zni
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Quality score:** 5
**Tok/s generation:** 66.88

## g100-eval-010 · skladnia · normal_120

**Prompt:** `Na początku eksperymentu`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260618

**Output:**

```text
Na początku eksperymentu na temat metod i metod przetwarzania danych, a także za pośrednictwem interfejsu nawigacyjnego oraz innych informacji. W latach 1851–1856 opracował program badawczy i wydawał czasopismo naukowe, które ukształtowało się kilka innych dyscyplin badawczych i społecznych na całym świecie. Jako pierwszy w historii tej dyscypliny badał głównie fizykę, biologię, fizykę, literaturę, estetykę, biologię, astrologię (zwłaszcza biologię i astrologię). Był jednym z pionierów jego publikacji naukowych. Był również założycielem wielu czasopism naukowych w Europie. W roku
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Quality score:** 5
**Tok/s generation:** 66.65

## g100-eval-011 · petle · normal_120

**Prompt:** `Ten tekst nie powinien powtarzać tego samego zdania, ponieważ`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260619

**Output:**

```text
Ten tekst nie powinien powtarzać tego samego zdania, ponieważ w tym samym języku literackim nie ma słów „poprawny” i „prawny” i „prawny”. Innym językiem, który często jest używany w literaturze i literaturze, ale jest to język pisany w kontekście poetyckim, który w sposób nierównolegle z jego poglądem na język, nie powinien być używany w literaturze i sztuce. Z tego powodu był używany w poezji, m.in. w poezji i sztuce. Ahmad, ahmad (ajmad-h) – w chrześcijańskiej
```

**Heurystyka:** Problemy: powtórzenia 1, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 4
**Tok/s generation:** 64.77

## g100-eval-012 · forum_garbage · normal_120

**Prompt:** `Komentarze użytkowników wskazują, że`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260620

**Output:**

```text
Komentarze użytkowników wskazują, że większość użytkowników Internetu w Stanach Zjednoczonych ma dostęp do Internetu. W listopadzie 2019 roku IBM uruchomił dystrybucję IBM (Operation Corporation) – część sieci IBM – pierwsza sieć IBM, która miała dostęp do Internetu i sieci GSM. IBM jest w pełni kompatybilne z IBM, gdyż wszystkie te strony są nadawcami IBM. W październiku 2019 roku sieć IBM została przekształcona w spółkę akcyjną IBM o nazwie IBM. W lutym 2019 roku IBM zaczęła udostępniać IBM
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.22

## g100-eval-001 · krotka_kontynuacja · creative_80

**Prompt:** `Warszawa to`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260609

**Output:**

```text
Warszawa to jeden z najnowocześniejszych i najbardziej prestiżowych projektów modernizacji Polski. Na szczęście ta decyzja nie może być udana. Dokonał inwestycji w modernizację i modernizację zabytków polskiej gospodarki. - Jest to projekt realizowany w ramach projektu realizowany przez firmy Great Enterprise Polska i Kounité Polska w Warszawie. Skierowany o realizację projektów dotyczących modernizacji i modernizacji
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 73.53

## g100-eval-002 · krotka_kontynuacja · creative_80

**Prompt:** `Polska jest`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260610

**Output:**

```text
Polska jest wspólnotą z Wolnym Miastem. Od 2007 do 2009 zasiadał w niej, ponownie w 2014 i 2015. W latach 2019–1998 był przewodniczącym Komisji Napoleona Bonapartego. Ustawodawstwo W 1989 nie uczestniczył w pracach państwowych. W wyborach parlamentarnych w 1991 z powodzeniem ubiegał się o reelekcję, dostał 4988 głosów. Był
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Quality score:** 5
**Tok/s generation:** 73.51

## g100-eval-003 · edukacyjny · creative_80

**Prompt:** `W fizyce energia`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260611

**Output:**

```text
W fizyce energia makroskopowa Dukkaikaike – miasto w północno-zachodnich Chińskich Republikach Ludowych, w dystrykcie Ginne, ośrodek administracyjny prowincji Hong Kongu w środkowej części dystryktu S ⁇ ipej. Siedziba władz miasta. Miejsce urodzenia chińskiego bohatera Iōnei. W mieście znajduje się stacja kolejowa Dukkai
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.49

## g100-eval-004 · edukacyjny · creative_80

**Prompt:** `Sztuczna inteligencja jest`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260612

**Output:**

```text
Sztuczna inteligencja jest częścią kultury (tj. w niej powstają liczne dzieła, takie jak: „Romanizacja”, „Motyw”, „Ostatni Grosz”, „Śniadania”, „Kronika”, „Ostatni Grosz”, „Nowa Kultura”). Nakład wynosi około 2700 egzemplarzy. Zwierciadłom tego dzieła uznaje się za pierwszy materiał publicystyczny (
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.51

## g100-eval-005 · skladnia · creative_80

**Prompt:** `Rower składa się z`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260613

**Output:**

```text
Rower składa się z trzech części połączonych równolegle. Pierwsza jest zlokalizowana na lewo od wejścia do parku. Połączenie zaporowe jest jednokierunkowe, a druga na lewo – dwukierunkowe. Połączenie przy pomocy jednobiegowej sieci gazowej sieci gazowej z dwoma stacjami, z których każda połączyła centralną część miasta. Drugi, po stronie drogi wojewódzkiej nr 55
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.69

## g100-eval-006 · web_garbage · creative_80

**Prompt:** `Według najnowszych danych`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260614

**Output:**

```text
Według najnowszych danych GUS z 30 czerwca 2014 gminę zamieszkiwało 3610 osób. Natomiast według danych z 2017 roku gminę zamieszkiwało 5026 osób. Struktura powierzchni Według danych z roku 2002 gmina GUS z roku 2002 gmina GUS miała 13117 mieszkańców. Struktura powierzchni Według danych z roku 2002 gmina GUS – 29860 osób. GUS ma 361 km2 pagórki. Sąsiednie gminy By
```

**Heurystyka:** Problemy: powtórzenia 8, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['według danych']
**Quality score:** -1
**Tok/s generation:** 72.78

## g100-eval-007 · projektowy · creative_80

**Prompt:** `Najważniejszym problemem tego projektu jest`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260615

**Output:**

```text
Najważniejszym problemem tego projektu jest to, że nie są ona już w pełni samodzielne. Nie zawsze jednak to on posiada własne możliwości. Przykładem projektu jest firma Centromotive Investment, która od tego momentu realizuje projekty z udziałem kapitału zagranicznego. Zatrudnienie tego, jak firma Centromotive Investment, w połączeniu z nowymi technologiami przeładunkowymi, wiąże się
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 71.94

## g100-eval-008 · edukacyjny · creative_80

**Prompt:** `Uczenie maszynowe polega na`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260616

**Output:**

```text
Uczenie maszynowe polega na maszynie na ciągłym ruchu (w zależności od położenia maszyny), a następnie na użyciu urządzenia do wykonywania tych maszyn. Rozwiązanie stosowane jest do wykonywania ciągłego ruchu bez użycia części maszyn o niewielkiej mocy, np. pionowej, o dużej mocy. Z tego powodu, w przypadku napędzania maszyny maszyny i jej braku może ona być z reguły napędzana maszynami precyzyjnymi. Zasa
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.07

## g100-eval-009 · encyklopedyczny · creative_80

**Prompt:** `W średniowieczu`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260617

**Output:**

```text
W średniowieczu tereny księstwa cieszyńskiego przypadły w księstwie sandomierskim na represje, zwłaszcza po śmierci czeskiego króla Odona I. W kolejnych epokach książę Odoak z dynastii Jagiellonów prowadził wyprawę na Jasło. Stale współtworzył także potężny sojusz obronny, którym przypisuje się powstanie na Górnym Śląsku. W roku
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 73.13

## g100-eval-010 · skladnia · creative_80

**Prompt:** `Na początku eksperymentu`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260618

**Output:**

```text
Na początku eksperymentu na ludziach między ludziami a innymi na zakładzie dla kobiet w Stanach Zjednoczonych oraz na kuracji w zakładach pracy i pracy, w ciągu czterech tygodni później wydano wyrok śmierci, który był podstawą procesu przeciwko rządowi. W końcu wyrok ten został po raz drugi ustalony przez prokuratora Ohio Carrevanovę w 1986 roku. W wyniku operacji na
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.81

## g100-eval-011 · petle · creative_80

**Prompt:** `Ten tekst nie powinien powtarzać tego samego zdania, ponieważ`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260619

**Output:**

```text
Ten tekst nie powinien powtarzać tego samego zdania, ponieważ domaga się tego tekstu. Przez jego sprawą w tej sprawie pojawi się w październiku 2019 dokument dotyczący m.in. dotacji z budżetu obywatelstwa niemieckiego. Do tego czasu jest on dopuszczany we wrześniu 2019 r., gdy to Sąd Konstytucyjny określił, że nie ma już wpływu na jego pobór do Sejmu. Wartość tego dokumentu można było znaleźć w: "Dzienniku praw
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 70.38

## g100-eval-012 · forum_garbage · creative_80

**Prompt:** `Komentarze użytkowników wskazują, że`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260620

**Output:**

```text
Komentarze użytkowników wskazują, że strona internetowa była gotowa do umieszczania adresu. W każdym przypadku usługi sieciowe nie były potrzebne, a informacje zostały wpisane w Internecie. Dlatego najczęściej wykorzystywane w praktyce łącza internetowe nie pokrywały żadnych zbędnych dowodów osobistych. W każdym przypadku każda sieć operacyjna miała na względzie obowiązek wykorzystywania adresów na terenie sieci. Usługa sieciowa była na zasadzie całkowicie niezależna niż
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.07

## g100-eval-001 · krotka_kontynuacja · creative_120

**Prompt:** `Warszawa to`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260609

**Output:**

```text
Warszawa to jeden z najnowocześniejszych i najbardziej prestiżowych projektów modernizacji Polski. Na szczęście ta decyzja nie może być udana. Dokonał inwestycji w modernizację i modernizację zabytków polskiej gospodarki. - Jest to projekt realizowany w ramach projektu realizowany przez firmy Great Enterprise Polska i Kounité Polska w Warszawie. Skierowany o realizację projektów dotyczących modernizacji i modernizacji zabytkowego budynku w dzielnicy Dworc. Jego realizacja realizowana jest przez firmę Saw Tok. Dzięki temu firma realizowana będzie ze środków BBBTS. Przewiduje on
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.78

## g100-eval-002 · krotka_kontynuacja · creative_120

**Prompt:** `Polska jest`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260610

**Output:**

```text
Polska jest wspólnotą z Wolnym Miastem. Od 2007 do 2009 zasiadał w niej, ponownie w 2014 i 2015. W latach 2019–1998 był przewodniczącym Komisji Napoleona Bonapartego. Ustawodawstwo W 1989 nie uczestniczył w pracach państwowych. W wyborach parlamentarnych w 1991 z powodzeniem ubiegał się o reelekcję, dostał 4988 głosów. Był też członkiem gabinetu Jerzego Buzka, który w 1997 uzyskał mandat poselski. W wyborach parlamentarnych w 1997 z powodzeniem ubiegał się o reelekcję z ramienia Litwy, o
```

**Heurystyka:** Problemy: powtórzenia 4, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Quality score:** 0
**Tok/s generation:** 67.16

## g100-eval-003 · edukacyjny · creative_120

**Prompt:** `W fizyce energia`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260611

**Output:**

```text
W fizyce energia makroskopowa Dukkaikaike – miasto w północno-zachodnich Chińskich Republikach Ludowych, w dystrykcie Ginne, ośrodek administracyjny prowincji Hong Kongu w środkowej części dystryktu S ⁇ ipej. Siedziba władz miasta. Miejsce urodzenia chińskiego bohatera Iōnei. W mieście znajduje się stacja kolejowa Dukkaike. Nitron – miejscowość w środkowej części Francji, położona w regionie Grand Est, w departamencie Est. Według danych na rok 1990 gminę zamieszkiwało 29 013 mieszkańców. Wśród 10
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['według danych', 'departamencie']
**Quality score:** 4
**Tok/s generation:** 66.53

## g100-eval-004 · edukacyjny · creative_120

**Prompt:** `Sztuczna inteligencja jest`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260612

**Output:**

```text
Sztuczna inteligencja jest częścią kultury (tj. w niej powstają liczne dzieła, takie jak: „Romanizacja”, „Motyw”, „Ostatni Grosz”, „Śniadania”, „Kronika”, „Ostatni Grosz”, „Nowa Kultura”). Nakład wynosi około 2700 egzemplarzy. Zwierciadłom tego dzieła uznaje się za pierwszy materiał publicystyczny (pod pseudonimami: „Ostatni Grosz”, „Ostatni Grosz”, „Panurki”, „Znak”, „Kronika”). Przełomem cieszy się też
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.59

## g100-eval-005 · skladnia · creative_120

**Prompt:** `Rower składa się z`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260613

**Output:**

```text
Rower składa się z trzech części połączonych równolegle. Pierwsza jest zlokalizowana na lewo od wejścia do parku. Połączenie zaporowe jest jednokierunkowe, a druga na lewo – dwukierunkowe. Połączenie przy pomocy jednobiegowej sieci gazowej sieci gazowej z dwoma stacjami, z których każda połączyła centralną część miasta. Drugi, po stronie drogi wojewódzkiej nr 553, jest zamknięty. Znajduje się tam parking na ok. 40 minut drogi wojewódzkiej nr 732. Komunikację mierzą 6 linii tramwajowej, kursującej na linii nr 453. Łącznie przejeżdża
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.76

## g100-eval-006 · web_garbage · creative_120

**Prompt:** `Według najnowszych danych`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260614

**Output:**

```text
Według najnowszych danych GUS z 30 czerwca 2014 gminę zamieszkiwało 3610 osób. Natomiast według danych z 2017 roku gminę zamieszkiwało 5026 osób. Struktura powierzchni Według danych z roku 2002 gmina GUS z roku 2002 gmina GUS miała 13117 mieszkańców. Struktura powierzchni Według danych z roku 2002 gmina GUS – 29860 osób. GUS ma 361 km2 pagórki. Sąsiednie gminy Bystrzyca Gronowo (daw. gmina Gronowo II) – gmina w Polsce położona w województwie zachodniopomorskim, w powiecie gryfińskim. W latach 1975–1998 gmina położona była w województwie szcze
```

**Heurystyka:** Problemy: powtórzenia 8, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['według danych', 'w latach', 'powiecie']
**Quality score:** -3
**Tok/s generation:** 66.76

## g100-eval-007 · projektowy · creative_120

**Prompt:** `Najważniejszym problemem tego projektu jest`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260615

**Output:**

```text
Najważniejszym problemem tego projektu jest to, że nie są ona już w pełni samodzielne. Nie zawsze jednak to on posiada własne możliwości. Przykładem projektu jest firma Centromotive Investment, która od tego momentu realizuje projekty z udziałem kapitału zagranicznego. Zatrudnienie tego, jak firma Centromotive Investment, w połączeniu z nowymi technologiami przeładunkowymi, wiąże się również z wieloma problemami ze strony konkurencji klientów telekomunikacyjnych i infrastrukturalnych. Inaczej mówiąc, firma Centromotive Investment stała się wiodącym dostawcą usług telekomunika
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.19

## g100-eval-008 · edukacyjny · creative_120

**Prompt:** `Uczenie maszynowe polega na`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260616

**Output:**

```text
Uczenie maszynowe polega na maszynie na ciągłym ruchu (w zależności od położenia maszyny), a następnie na użyciu urządzenia do wykonywania tych maszyn. Rozwiązanie stosowane jest do wykonywania ciągłego ruchu bez użycia części maszyn o niewielkiej mocy, np. pionowej, o dużej mocy. Z tego powodu, w przypadku napędzania maszyny maszyny i jej braku może ona być z reguły napędzana maszynami precyzyjnymi. Zasada działania W przypadku układów elektrycznych o stałej mocy jest ona taka uwarunkowana, że praca w niej jest ograniczona wyłącznie komora nabojowa, co stanowi, że mocna
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.17

## g100-eval-009 · encyklopedyczny · creative_120

**Prompt:** `W średniowieczu`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260617

**Output:**

```text
W średniowieczu tereny księstwa cieszyńskiego przypadły w księstwie sandomierskim na represje, zwłaszcza po śmierci czeskiego króla Odona I. W kolejnych epokach książę Odoak z dynastii Jagiellonów prowadził wyprawę na Jasło. Stale współtworzył także potężny sojusz obronny, którym przypisuje się powstanie na Górnym Śląsku. W roku 1305 książę Odoak udał się na wyprawę po raz kolejny na Węgry do Czech opolskiego, zakończoną śmiercią króla Władysława Opolczyka. W latach 1332–
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Quality score:** 5
**Tok/s generation:** 66.95

## g100-eval-010 · skladnia · creative_120

**Prompt:** `Na początku eksperymentu`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260618

**Output:**

```text
Na początku eksperymentu na ludziach między ludziami a innymi na zakładzie dla kobiet w Stanach Zjednoczonych oraz na kuracji w zakładach pracy i pracy, w ciągu czterech tygodni później wydano wyrok śmierci, który był podstawą procesu przeciwko rządowi. W końcu wyrok ten został po raz drugi ustalony przez prokuratora Ohio Carrevanovę w 1986 roku. W wyniku operacji na terenie Ohio Carrevanovę, ofiarami był wieloletni chłopiec. Eric Owen Owen (ur. 27 listopada 1841 w Greenbury w hrabstwie
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.38

## g100-eval-011 · petle · creative_120

**Prompt:** `Ten tekst nie powinien powtarzać tego samego zdania, ponieważ`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260619

**Output:**

```text
Ten tekst nie powinien powtarzać tego samego zdania, ponieważ domaga się tego tekstu. Przez jego sprawą w tej sprawie pojawi się w październiku 2019 dokument dotyczący m.in. dotacji z budżetu obywatelstwa niemieckiego. Do tego czasu jest on dopuszczany we wrześniu 2019 r., gdy to Sąd Konstytucyjny określił, że nie ma już wpływu na jego pobór do Sejmu. Wartość tego dokumentu można było znaleźć w: "Dzienniku prawnym": "Dochodzimy do sądu" (z wyjątkiem dokumentu kodeksu postępowania cywilnego – z 8.03.1982). Do tego dokumentu do Trybunału Konstytucyjnego przynależy m.in
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 64.94

## g100-eval-012 · forum_garbage · creative_120

**Prompt:** `Komentarze użytkowników wskazują, że`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260620

**Output:**

```text
Komentarze użytkowników wskazują, że strona internetowa była gotowa do umieszczania adresu. W każdym przypadku usługi sieciowe nie były potrzebne, a informacje zostały wpisane w Internecie. Dlatego najczęściej wykorzystywane w praktyce łącza internetowe nie pokrywały żadnych zbędnych dowodów osobistych. W każdym przypadku każda sieć operacyjna miała na względzie obowiązek wykorzystywania adresów na terenie sieci. Usługa sieciowa była na zasadzie całkowicie niezależna niż udostępnianie adresów (a więc jedynie adresów) i nie zawierała informacji o sieci. Z tego względu strona internetowa nie ma określonej sieci, a komunikacja między urządzeniami jest zgodna z
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.29
