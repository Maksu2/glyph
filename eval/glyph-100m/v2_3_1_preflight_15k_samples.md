# Glyph-100M v2.3.1 preflight 15k samples

Base LM completion eval. To nie jest eval asystenta ani instruction-following.

- checkpoint: `checkpoints/glyph-100m-v2_3_1-preflight/latest.pt`
- step: `15000`
- variant: `glyph-100m`
- tokenizer sha256: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`

## g100-eval-001 · krotka_kontynuacja · conservative

**Prompt:** `Warszawa to`

**Settings:** temp=0.6 · top_k=30 · max_new_tokens=120 · seed=20260531

**Output:**

```text
Warszawa to nie tylko wspólny element. Na przykład: „Strata” – „Strata” – „Strata” – „Strata” – „Strata” – „Strata” – „Strata” – „Strata” – „Strata” – „Strata” – „Strata” – „Strata” (Strata”) – „Strata” – „Strata” – „Strata” – „Strata” – „Strata” – „Strata
```

**Heurystyka:** Problemy: powtórzenia 15, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 12.89

## g100-eval-002 · krotka_kontynuacja · conservative

**Prompt:** `Polska jest`

**Settings:** temp=0.6 · top_k=30 · max_new_tokens=120 · seed=20260532

**Output:**

```text
Polska jest jedną z głównych ośrodków turystycznych – jest częścią naszego kraju, a także w kraju. W Polsce jest to najliczniej odwiedzanych turystów na świecie. W Polsce w Polsce w okolicach Polski znajduje się schronisko PTTK „Życie”. W latach 2009–2012 na obszarze Polski jest to miejsce wypoczynku dla turystów z Polski. W Polsce w ramach „Biuletynu Przemysłu” (w Polsce) oraz „Życie” (w Polsce) znajduje się muzeum „Humanistyczny” (w Polsce). W latach 2013–2012 odsłonięty został pomnik Jana Pawła
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Tok/s generation:** 12.83

## g100-eval-003 · edukacyjny · conservative

**Prompt:** `W fizyce energia`

**Settings:** temp=0.6 · top_k=30 · max_new_tokens=120 · seed=20260533

**Output:**

```text
W fizyce energia fizyczna jest bardzo skuteczna, gdyż w przypadku promieniowania elektromagnetycznego, który może być zastosowany przez elektromagnetyzm w tym samym czasie, gdzie jest bardzo skuteczny, a w przypadku promieniowania elektromagnetycznego, w tym promieniowanie elektromagnetyczne (magnetyzm) może być określona na określony czas transformacji, gdyż w pewnym sensie promieniowanie elektromagnetyczne jest bardzo przydatne w czasie transformacji. Zjawisko promieniowania elektromagnetycznego może być też efektem transformacji, gdyż promieniowanie elektroma
```

**Heurystyka:** Problemy: powtórzenia 1, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 11.33

## g100-eval-004 · edukacyjny · conservative

**Prompt:** `Sztuczna inteligencja jest`

**Settings:** temp=0.6 · top_k=30 · max_new_tokens=120 · seed=20260534

**Output:**

```text
Sztuczna inteligencja jest zrównowana do depresji, a także poprzez ich rozbudowę w kierunku rzeki. Jest to sposób, w którym woda jest w stanie wody. W ten sposób woda będzie w stanie przekwalifikowana do wody, a woda jest w stanie utrzymać się w domu. W tym celu woda staje się w stanie odtworzyć, a woda będzie w stanie przekwalifikowana do wody. W celu ochrony zdrowia, woda staje się miejscem, gdzie woda staje się bardziej wilgotna. Z uwagi na na duże zanieczyszczenia wody, woda staje się bardziej niebezpieczna. W tym przypadku woda może u
```

**Heurystyka:** Problemy: powtórzenia 6, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 13.88

## g100-eval-005 · skladnia · conservative

**Prompt:** `Rower składa się z`

**Settings:** temp=0.6 · top_k=30 · max_new_tokens=120 · seed=20260535

**Output:**

```text
Rower składa się z: Zbiornik – BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB, B
```

**Heurystyka:** Problemy: niski udział liter, powtórzenia 34, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 11.4

## g100-eval-006 · web_garbage · conservative

**Prompt:** `Według najnowszych danych`

**Settings:** temp=0.6 · top_k=30 · max_new_tokens=120 · seed=20260536

**Output:**

```text
Według najnowszych danych na terenie gminy znajduje się 5 obiektów zabytkowych. Na terenie gminy znajduje się 5 kapliczek. Na terenie gminy znajduje się kapliczka z końca XIX w. oraz kapliczka z XIX w. Łąckowice (niem. Schwarzwalde) – wieś w Polsce położona w województwie dolnośląskim, w powiecie kłodzkim, w gminie Kłodzko. Podział administracyjny W latach 1975–1998 miejscowość administracyjnie należała do województwa wrocławskiego. Nazwa Nazwa miejscowości wywodzi się od "Ründe", co oznacza „Ründe”. Przynależność administracyjna W latach 1975–1998 miejscowość administracyjnie należała
```

**Heurystyka:** Problemy: powtórzenia 9, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach', 'województwa', 'powiecie', 'gminie']
**Tok/s generation:** 13.04

## g100-eval-007 · projektowy · conservative

**Prompt:** `Najważniejszym problemem tego projektu jest`

**Settings:** temp=0.6 · top_k=30 · max_new_tokens=120 · seed=20260537

**Output:**

```text
Najważniejszym problemem tego projektu jest zwiększenie poziomu bezpieczeństwa w zakresie bezpieczeństwa i bezpieczeństwa. W tym celu, w tym celu, należy zwrócić uwagę na możliwość, by zapewnić bezpieczeństwo i bezpieczeństwo. Jednakże, gdy koszty transportu nie mogą się upewnić, że w przypadku zagrożenia w zakresie bezpieczeństwa, może zostać osiągnięty koszt inwestycji, a także koszty budowy. Property, property, property, property, property, property, property, property, property, property, property, property, property, property, pro
```

**Heurystyka:** Problemy: powtórzenia 10, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 10.94

## g100-eval-008 · edukacyjny · conservative

**Prompt:** `Uczenie maszynowe polega na`

**Settings:** temp=0.6 · top_k=30 · max_new_tokens=120 · seed=20260538

**Output:**

```text
Uczenie maszynowe polega na przeciągu kolejnych maszyn w celu uzyskania odpowiedniej mocy w zakresie pojemności, co pozwala na przeciągu kolejnych maszyn. Zasilanie paliwa i przeciągu pojazdów, które w trakcie przeciągu pojazdów, mogą być poddawane procesowi przeciągu. Zasilanie paliwa i przeciągu elementów, które w celu zwiększenia pojemności maszyny w celu zwiększenia pojemności maszyny w celu zwiększenia mocy naprężenia. Zasilanie paliwa i przeciągu w celu zwiększenia mocy naprężenia powietrza do maksymalnego ciśnienia. Zasilanie paliwa i przeciągu z paliwa i prze
```

**Heurystyka:** Problemy: powtórzenia 10, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 11.93

## g100-eval-009 · encyklopedyczny · conservative

**Prompt:** `W średniowieczu`

**Settings:** temp=0.6 · top_k=30 · max_new_tokens=120 · seed=20260539

**Output:**

```text
W średniowieczu był częścią Imperium Osmańskiego, a następnie w latach 1492–1495 w pobliżu Palestyny. W 1597 roku opat opat opactwa w Palestynie wybudował kościół św. Stanisława Biskupa i św. Stanisława Biskupa z 1599 roku. Zakończenie budowy kościoła w Palestynie odbudowano w latach 1595–1595 przez Jana z Palestyny. W latach 1595–1595 miasto było miejscem utrwalenia przemysłu, przemysłu i techniki. W 1595 roku miasto stało się stolicą Królestwa Prus, a w
```

**Heurystyka:** Problemy: powtórzenia 1, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Tok/s generation:** 14.02

## g100-eval-010 · skladnia · conservative

**Prompt:** `Na początku eksperymentu`

**Settings:** temp=0.6 · top_k=30 · max_new_tokens=120 · seed=20260540

**Output:**

```text
Na początku eksperymentu, w celu zwiększenia kosztów, zwiększania kosztów, a także odciążenia kosztów. W przypadku wystąpienia problemów, gdy przy produkcji, w przypadku zastosowania, a następnie zmiana kosztów, wytrącania kosztów, jest możliwa. W przypadku uszkodzenia sytuacji, gdy w przypadku awarii, może być możliwa zmiana kosztów, a nawet przy zachowaniu kosztów, a także obniżenia kosztów. W przypadku awarii, w przypadku awarii, w przypadku awarii, nie jest zbyt niska. Dlatego też, gdy awaria jest możliwa do zmniejszenia kosztów, może być możliwa do zwiększenia
```

**Heurystyka:** Problemy: powtórzenia 3, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 12.3

## g100-eval-011 · petle · conservative

**Prompt:** `Ten tekst nie powinien powtarzać tego samego zdania, ponieważ`

**Settings:** temp=0.6 · top_k=30 · max_new_tokens=120 · seed=20260541

**Output:**

```text
Ten tekst nie powinien powtarzać tego samego zdania, ponieważ nie może zostać wysłany do Polski. Na przykład w tej sprawie, że w Polsce nie ma już nic wspólnego z tym, że jest on bardzo niebezpieczny. W Polsce i w Polsce – w latach 80. XX wieku w Polsce, a także w Polsce, gdzie w ostatnich latach – na Węgrzech, gdzie w latach 80. XX wieku, w Polsce – po II wojnie światowej – w latach 90. XX wieku, kiedy to zaczęło się odbudować w Polsce. Od początku lat 90. XX wieku, kiedy to w Warszawie i Warszawie, w latach 90. XX wieku władze PRL przejęły Polskę, prze
```

**Heurystyka:** Problemy: powtórzenia 8, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Tok/s generation:** 11.22

## g100-eval-012 · forum_garbage · conservative

**Prompt:** `Komentarze użytkowników wskazują, że`

**Settings:** temp=0.6 · top_k=30 · max_new_tokens=120 · seed=20260542

**Output:**

```text
Komentarze użytkowników wskazują, że nie jest to możliwe, gdyż w przypadku braku informacji na temat tego, czy nie będzie wymagane. W przypadku, gdy nie ma takiej informacji, to nie musi się dotrzeć do komputera. W takim wypadku należy złożyć dane do użytkownika, lub też użyć go do klienta. W przypadku, gdy nie ma takiej informacji, należy pamiętać o tym, że klient może mieć bardzo dobre wyniki. W przypadku, gdy klient może pracować z klientem, warto wybrać się na stronie internetowej lub na stronie internetowej. Przykładowo, w którym klient może nam się dowiedzieć, czy klient może pracować z klientem, czy też skorzystać
```

**Heurystyka:** Problemy: powtórzenia 6, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 13.4

## g100-eval-001 · krotka_kontynuacja · normal

**Prompt:** `Warszawa to`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260531

**Output:**

```text
Warszawa to nie do końca nielegalne w dużej mierze. Otóż nie jest ona dostępna na terenie obecnego miasta. W dzisiejszym regionie zachowały się dwa niewielkie, duże, bliskość ludności pochodzi z XVI wieku. Miasto stanowi ośrodek samorządu terytorialnego. W latach 202–276 miasto ma charakter przemysłowy. Miasto posiadało własny rynek. W końcu XIX wieku miasto stało się ośrodkiem przemysłowym, a w 1872 roku do miasta zaczęto przekształcać w jedną z ważniejszych ośrodków przemysłu w regionie. W 1882 roku wieś liczyła 332 mieszkańców. W XIX wieku w mieście
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Tok/s generation:** 12.64

## g100-eval-002 · krotka_kontynuacja · normal

**Prompt:** `Polska jest`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260532

**Output:**

```text
Polska jest jedną z głównych głównych na świecie placówek naukowy na świecie, które można oglądać na świecie. W 2022 roku Instytut Nauk Ekonomicznych przekazał Fundacji na rzecz Nauki, Nauki i Nauki w Warszawie, aby uzyskać przy okazji 420 miejsc, i instytucji naukowych i naukowych na całym świecie. W 2022 roku Instytut Nauk Ekonomicznych przekazał Instytut Nauk Ekonomicznych wraz zbiorem Uniwersytetu Warszawskiego – Instytut Nauk Ekonomicznych (CK) oraz Instytut Nauk Ekonomicznych (AUA). Historia Wydział Nauk Ekonomicznych (IFI) – Instytut Nauk Ekonomicznych (IFI) – Instytut Nauk Ekonomicznych (
```

**Heurystyka:** Problemy: powtórzenia 8, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 14.44

## g100-eval-003 · edukacyjny · normal

**Prompt:** `W fizyce energia`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260533

**Output:**

```text
W fizyce energia fizyczna jest bardzo skuteczna, jeśli ma ono być bardzo łatwo poznawalne, a co najmniej jedna z tych substancji nie ma, ani jedna z nich, że istnieje w ogóle jedna, jeśli ma onaby duże znaczenie. Jednakże energia elektryczna jest również korzystna, aby utrzymać się w tej sytuacji, jeśli temperatura, w którym temperatura, w której temperatura jest bardziej stabilna, to ciśnienie, ale jest bardzo silne, co jest szczególnie ważne dla temperatury, by wyparć inne zjawiska. Przykładowo, energia elektryczna jest uzależniona, a energia elektryczna
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 10.47

## g100-eval-004 · edukacyjny · normal

**Prompt:** `Sztuczna inteligencja jest`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260534

**Output:**

```text
Sztuczna inteligencja jest zrównowana do depresji, a także poprzez ich rozprowadzenie w kierunku doliny potoku. Z kolei z czasem zaczęto ją stosować już podczas depresji w warunkach domowych. W Polsce masarstwo w Polsce spowodowało, że w Europie około 1800 (w tym w latach 1910–1915) zaczęło używać określenia „nie” (np. „nie” lub „nie”). Przeprowadzono więc układy z górników, których podstawą była depresja na tle zanieczyszczeń powietrza, a nawet zanieczyszczeń atmosferycznych. W latach 1815–1819
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Tok/s generation:** 11.61

## g100-eval-005 · skladnia · normal

**Prompt:** `Rower składa się z`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260535

**Output:**

```text
Rower składa się z: Zjazd autobusia TB, ul. Roweckiego, ul. W. Wolności ul. Sienkiewicza, ul. Sienkiewicza, ul. Sienkiewicza, ul. Zarębska ul. M. Wolności ul. Sienkiewicza, ul. Sienkiewicza, ul. A. Zarębska ul. Sienkiewicza, ul. Sienkiewicza, ul. M. Sienkiewicza, ul. Sienkiewicza, ul. Sienkiewicza, ul. A. Matejki ul. Sienkiewicza, ul. Sienkiewicza
```

**Heurystyka:** Problemy: powtórzenia 12, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 12.77

## g100-eval-006 · web_garbage · normal

**Prompt:** `Według najnowszych danych`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260536

**Output:**

```text
Według najnowszych danych z 2009 roku wieś liczyła 526 mieszkańców, a liczba mieszkańców wynosiła 1034 mieszkańców. Miśowice (dawniej Miświzna) – wieś w Polsce położona w województwie dolnośląskim, w powiecie polkowickim, w gminie Dąbrówka. Podział administracyjny W latach 1975–1998 miejscowość administracyjnie należała do województwa wałbrzyskiego. Położenie Miświzna położona jest na wysokości około 1080 m n.p.m., położona jest na południowo-zachodniej części gminy Dąbrówka. Nazwa Nazwa wywodzi się od słowa miświsko-chłonisko-chło
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach', 'województwa', 'powiecie', 'gminie']
**Tok/s generation:** 12.47

## g100-eval-007 · projektowy · normal

**Prompt:** `Najważniejszym problemem tego projektu jest`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260537

**Output:**

```text
Najważniejszym problemem tego projektu jest zwiększenie poziomu bezpieczeństwa w zakresie bezpieczeństwa i bezpieczeństwa. W 2010 roku, po ukończeniu i odbudowę nowego budynku,,, dobudowano salę konferencyjną, a także poszerzono na nowe skrzydło budynków. Gwizdowość – stała fizyczna analiza fizyczna, która jest jednym z najważniejszych czynników, gdzie np. odwzorientowana, przez czy też nie może być rozumiana jako czynność, czyli pojęcie równowagi, lecz także uogólniona. Jej głównym celem jest umożliwienie doskonałego przeładzania, w którym ma charakter bezwzględny, a także
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 11.31

## g100-eval-008 · edukacyjny · normal

**Prompt:** `Uczenie maszynowe polega na`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260538

**Output:**

```text
Uczenie maszynowe polega na przeciągu kolejnych dwuwydziałów podwozia. W związku z tym uruchamianie produkcji był spowodowane silnikami. W czasie II wojny światowej wyprodukowano trzy pojazdy pasażerskie, a także czterowieżowe. W 1950 roku wyprodukowano łącznie 6 sztuk samochodów. Samoloty były użytkowane przez 3 armaty maszynowe. W 1955 roku wyprodukowano 4 sztuk, a w 1969 roku wprowadzono do uzbrojenia. W 1961 roku wyprodukowano 9 pojazdów osobowych. W 1969 roku wyprodukowanych w Polsce wyprodukowano 2 sztuk samochodów osobowych serii MDK. W latach
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Tok/s generation:** 14.21

## g100-eval-009 · encyklopedyczny · normal

**Prompt:** `W średniowieczu`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260539

**Output:**

```text
W średniowieczu był częścią Imperium Osmańskiego, a potem także jego terytorium, jak również w Imperium Osmańskim. Przez krótki czas rządy Osmanów przeszły na tereny dawnych Osmańskich, których głównym celem stało się opactwo Akwitanii, które w 1792 roku zajęły Zakon Osmański. Na początku XIX wieku w Osmanach zaczęli tu zmieniać się wpływ na rozwój Osmańskich, co doprowadziło do upadku Osmańskiego. W 1827 roku w Osmanach w wyniku wojen napoleońskich, w mieście narastało duże znaczenie, a na
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 11.78

## g100-eval-010 · skladnia · normal

**Prompt:** `Na początku eksperymentu`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260540

**Output:**

```text
Na początku eksperymentu, w programie „Imaginal Motor”. W trakcie eksperymentu, w ramach którego powstał silnik spalinowy. W latach 1972–1989 nastąpił eksplozję spalinową, w której zginęły dwie osoby. W latach 1973–1979 silnik spalinowy, co spowodowało, że awaria spalinowa zakończyła się eksplozją silnika, jednak nie została podjęta. W tym samym roku pojazd był napędzany silnikami spalinowymi, które zamontowały w dużej odległości około 20 m i było rozdzielone. Przykładowo silnik spalinowy, który w tym samym
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Tok/s generation:** 12.31

## g100-eval-011 · petle · normal

**Prompt:** `Ten tekst nie powinien powtarzać tego samego zdania, ponieważ`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260541

**Output:**

```text
Ten tekst nie powinien powtarzać tego samego zdania, ponieważ może zostać napisane w Biblii. Na przykład w Ameniu i Science Fiction, to Ameniusz, a na tym ostatnim tłumaczeniu jest ukazany Ameniusz. Błąd w SGGP (ang. Endless) – zespół ukrtupnych sond, które składają się z dwóch elementów: SGP (ang. shipple) – rekonstrukcji sond, sond, SGP (ang. shipple) – rekonstrukcji sond (ang. shipple)
```

**Heurystyka:** Problemy: powtórzenia 2, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 10.77

## g100-eval-012 · forum_garbage · normal

**Prompt:** `Komentarze użytkowników wskazują, że`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260542

**Output:**

```text
Komentarze użytkowników wskazują, że nie jest ona w stanie wyobrazić sobie tego, co będzie miało miejsce w ciągu ostatnich ostatnich kilku lat. W tym samym roku, po rozpoczęciu, władze, przemówiły list, o tym, że nie doszło już do porozumienia, ale już wkrótce potem, gdy na razie nie przyjęto, a na skutek, żeby ten przemówił się do Polski. W odpowiedzi na pytanie, czy zjednoczenie Polski pod wodzą polskiego na terytorium Polski wystosowało do Polski list. Przy okazji umownie, w którym oświadczenie, że w Warszawie potwierdzono, że nie ma nic
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=['odpowiedz'] · pseudo_ency=[]
**Tok/s generation:** 11.74

## g100-eval-001 · krotka_kontynuacja · creative

**Prompt:** `Warszawa to`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260531

**Output:**

```text
Warszawa to nie do końca nielegalne w dużej mierze. Otóż nie jest ona skomplikowana do podpisu, nie jest jej zdaniem możliwe. Ta jednak nie jest jedynym problemem, a nawet dlatego mamy już wiele rzeczy. Konserwator jest niezwłoczny, dlatego też za tym jest upragniony, a ujemny. Nie ma końca żadnych efektów. To właśnie to jednak nie wiadomo, czy nie jesteśmy w stanie się w stanie przepełnić. Z tego faktu, że nasz rząd nie będzie gotowy w sposób, a nawet, gdzie nie ma wymagań. Nie jest ono w stanie określi
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 13.34

## g100-eval-002 · krotka_kontynuacja · creative

**Prompt:** `Polska jest`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260532

**Output:**

```text
Polska jest jedną z postaci zaistniałej współpracy polsko-litewskiej, która jest dostępna dla polskiej telewizji telewizyjnej Sloss. Film ukazuje się na podstawie umowy międzynarodowej dla Polski w maju, aby uzyskać przy okazji oficjalnego przydział i wręczenie statuetki na wniosek władz państwowych. W Polsce, gdzie polskie Radio TVP, będzie realizowane po podpisaniu sprawozdania, oraz na koniec 2007 roku podpisanie porozumienia o współpracy z Euro-Narodem oraz wydaniu warszawskiego TVP (po raz pierwszy przysłowie TVP SA) TVP, TVP, TV oraz Telewizja Polsatu. Media
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 11.08

## g100-eval-003 · edukacyjny · creative

**Prompt:** `W fizyce energia`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260533

**Output:**

```text
W fizyce energia fizyczna jest bardzo skuteczna, jeśli ma ono prawo do swobodnego rozróżnienia. W fizyce fizycznej większość badanych związków chemicznych ma, że wielu związków chemicznych jest znacznie bardziej skomplikowana. Alternatywny alternatywny alternatywny alternatywny alternatywność algorytmu reakcji związana jest z tą definicjami reakcji. Alternatywny alternatywny alternatywny alternatywny alternatywny Alternatywny alternatywny alternatywny alternatywny alternatywny alterna
```

**Heurystyka:** Problemy: powtórzenia 7, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 12.31

## g100-eval-004 · edukacyjny · creative

**Prompt:** `Sztuczna inteligencja jest`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260534

**Output:**

```text
Sztuczna inteligencja jest zrównowana do destylacji ciała, który poprzez ich rozciągnąć w niewcześnie przy pomocy apetytu z zapału w temperaturze 10–15 °C. Występują wskutek zniszczenia atmosferycznych zapału napłonkowego, który nie jest wyeliminowany podczas destylacji kości, lub uszkodzonego zapału apetytu w głąb lub uderzeń. Bez względu na jej wzrost, po zachowaniu warstwy organicznej napada się na znaczną zmianę temperatury i uprawa uprawa wytrysku, powodując wywierającą na uwa
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 14.04

## g100-eval-005 · skladnia · creative

**Prompt:** `Rower składa się z`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260535

**Output:**

```text
Rower składa się z: ZOAP – TBAN - (GUT) w kierunku Starej Warty z ul. Sienkiewicza. - Uruchomiona w pobliżu: pl. Sienkiewicza (FAB) - BARAN - (DAM) W budynku: ul. Sienkiewicza (OAP) - A. Flimczyk (wester) - ul. Sienkiewicza (wester) - ul. Sienkiewicza, S. BW, S. B. BW, S. BW, Spytkiewicz-Brakowiak-Brakowiak -
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 12.23

## g100-eval-006 · web_garbage · creative

**Prompt:** `Według najnowszych danych`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260536

**Output:**

```text
Według najnowszych danych z 2009 roku wieś liczyła 526 mieszkańców, a liczba ludności wyniosła 432 osoby. Struktura lokalna Piramida wieku mieszkańców wsi Struktura religijna Kościół rzymskokatolicki: parafia pw. św. Wojciecha oraz drewniana dzwonnica rodu Stryjowskich z XIII wieku. W XIX i XX wieku w Skawiczach mieszkających było 357 domów. Na terenie miejscowości znajduje się cmentarz wojenny oraz cmentarz wojenny. Skawina – wieś w Polsce, położona w województwie wielkopolskim, w powiecie gnieźnieńskim, w gminie Balinek. Siedzibą rzymskokatolickiej
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['powiecie', 'gminie']
**Tok/s generation:** 10.9

## g100-eval-007 · projektowy · creative

**Prompt:** `Najważniejszym problemem tego projektu jest`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260537

**Output:**

```text
Najważniejszym problemem tego projektu jest zwiększenie poziomu peryferycznego i zorientowanych na peryferyczne i udźwiglowanego przez inne systemy, które mają wpływ na ich rozwój. Libretto Concorporation (ang. Concorporation Concorporation Association – Libretto Concorporation) – zespół muzyczny założony przez Inc., aby założyć zespół COM – Deef, który po opuszczeniu zespołu CMI, Concorporation jest członkiem AC, gdzie członkowie AC nagrali kilka piosenek z nagrań. Album powstał w ramach programu Deef
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 12.44

## g100-eval-008 · edukacyjny · creative

**Prompt:** `Uczenie maszynowe polega na`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260538

**Output:**

```text
Uczenie maszynowe polega na przeciągu kolejnych dwuwypaństwowych w trzech prototypach. Zadania przeciągu do poszczególnych prototypów są powszechne jako odprowadzanie nowych prototypów w kierunku zachodnim od góry z góry. Przykładowe wersje Układu Warszawskiego oraz Układu Warszawskiego oraz innych elementów oznaczone jest jako Zakłady Warszawskie, które domagają się przeciągu przeciągu przez prawobrzeżny system do budowy. Urządzenia Ministra Środowiska i Budownictwa zostały uwzględnione w PZN, lecz jako uzupełnienie systemu do realizacji projektu. W czasie wojny zdecydowanych było ich uży
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 11.9

## g100-eval-009 · encyklopedyczny · creative

**Prompt:** `W średniowieczu`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260539

**Output:**

```text
W średniowieczu był częścią Imperium Osmańskiego, a potem także jego terytorium, jak również w Imperium Osmańskim. Przez krótki czas miasto było głównym ośrodkiem kultury łużyckiej. W latach 894-102 miasto znajdowało się w granicach miasta. W 1595 roku miasto znajdowało się pod pretekstem administracyjnym Królestwa Polskiego. W 1779 roku miasto stało się stolicą Księstwa Warszawskiego, następnie Księstwa Moskiewskiego, a od 1740 roku w Królestwie Polskim. W 1816 roku po pożarze bolszewickiej w mieście nastąpił okres III, między wojska mo
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Tok/s generation:** 13.71

## g100-eval-010 · skladnia · creative

**Prompt:** `Na początku eksperymentu`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260540

**Output:**

```text
Na początku eksperymentu, w programie „Imaginal Motor”. W sezonie 2008/2004, w ramach którego powstał magazyn „American” w ramach akcji „Panty Polska”; został wyemitowany przez firmę „Tino”. Po miesiącu jego działalności, w 2014 roku Polska wyemitowała nowe miejsce sprzedaży pierwszego „Gamesa”, która sprzedała 4 tys. egzemplarzy. Był to największa seria tego typu w Polsce; pierwsza „Złota” dostępna jest na kanale RC1, co oznacza „Imaginal Motor” oraz „Pogorzejka”. Obecnie w Polsce jest
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 11.11

## g100-eval-011 · petle · creative

**Prompt:** `Ten tekst nie powinien powtarzać tego samego zdania, ponieważ`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260541

**Output:**

```text
Ten tekst nie powinien powtarzać tego samego zdania, ponieważ może zostać napisane w Biblii. Na przykład Bóg jest zaręczony z Izraelitami, że to Bóg ma swoje zdanie, które są na ich prośbę. Niemniej Bóg ma też teorie doktrynami z całego Izraela. Niemniej Bóg zaragował ukrążsamiały z Chrystusem – niegdyś jego poglądy z Biblii arabskiej, a jednak uważany jest za jego ukróla. Nienawidzicie Chrystus dopuszczał też jego wiarygodność do chrześcijańskiej religii, gdyż w przeciwieństwie do
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Tok/s generation:** 11.36

## g100-eval-012 · forum_garbage · creative

**Prompt:** `Komentarze użytkowników wskazują, że`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260542

**Output:**

```text
Komentarze użytkowników wskazują, że nie jest bezwzględny dla klienta. W tym czasie po raz pierwszy w tym czasie spółka zakupiła już pod koniec października w Łodzi, po przejeździe z Warszawy do Łodzi, a w Łodzi w październiku nastąpiły rozmowy o udział w projekcie spółki. Z czasem, gdy spółka zasugermowała działalność spółki zasugerowali projekt, będącej właścicielem spółki od tego roku. Oceniany przez spółkę, z powodów politycznych i ekonomicznych, dzięki których spółka trafiła do biura. W latach 90. ubiegłego wieku, dzięki działalności spółki odkupiła działalność pozasprzedalną spółkę, która
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Tok/s generation:** 11.31
