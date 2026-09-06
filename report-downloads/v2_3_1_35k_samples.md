# Glyph-100M v2.3.1 35k samples

Base LM completion eval. To nie jest eval asystenta ani instruction-following.

- checkpoint: `checkpoints/glyph-100m-v2_3_1-35k/latest.pt`
- step: `35000`
- variant: `glyph-100m`
- dataset: `glyph100_v2_3_1`
- tokenizer sha256 actual: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`

## g100-eval-001 · krotka_kontynuacja · normal_80

**Prompt:** `Warszawa to`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260609

**Output:**

```text
Warszawa to jeden z najcenniejszych zabytków w Polsce. Zabytki Kościół parafialny pw. św. Jana Chrzciciela, zbudowany w latach 1839-1904, posiadający cechy barokowe i gotyckie, wzniesiony w stylu późnoklasycystycznym, z fundacji Jana Chrzciciela. Kościół drewniany, klasycystyczny, otynkowany, z 1781 roku,
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Quality score:** 5
**Tok/s generation:** 73.3

## g100-eval-002 · krotka_kontynuacja · normal_80

**Prompt:** `Polska jest`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260610

**Output:**

```text
Polska jest częścią Unia Europejska. Władza ustawodawcza składa się z parlamentu, parlamentu, parlamentu i parlamentu. Władzę wykonawczą pełni rząd, parlament, władza sądownicza, niezależny od władzy sądowniczej. Władzę wykonawczą sprawuje Rada, której zwierzchnikiem jest władza sądownicza. Władzę zwierzchnią sprawuje
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 73.52

## g100-eval-003 · edukacyjny · normal_80

**Prompt:** `W fizyce energia`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260611

**Output:**

```text
W fizyce energia elektryczna jest równoważna od prędkości światła. W fizyce gazowej równania różniczkowe są to: gdzie: – energia elektryczna, – energia elektryczna. Współcześnie energia elektryczna w fizyce różniczkowej jest równa prędkości światła w czasie, w którym to energia elektryczna jest równa prędkości światła. W fizyce gazowej ma postać postaci  ⁇
```

**Heurystyka:** Problemy: powtórzenia 4, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 1
**Tok/s generation:** 72.54

## g100-eval-004 · edukacyjny · normal_80

**Prompt:** `Sztuczna inteligencja jest`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260612

**Output:**

```text
Sztuczna inteligencja jest częścią kultury, która może być postrzegana w formie magicznych i nierównych kultur. Mogą oni wyjaśnić różnicę między różnymi typami, w zależności od ich położenia geograficznego, ich położenia geograficznego, a także w ogólnym ujęciu kulturowym, ich położenia geograficznego, kulturowego itp. Z tego względu, na zjawisko w historii sztuki, często można
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.55

## g100-eval-005 · skladnia · normal_80

**Prompt:** `Rower składa się z`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260613

**Output:**

```text
Rower składa się z dwóch grup połączonych równolegle do ziemi, oraz częściowo z łącznika między dwiema stronami (zwanych też czasem „Galistą Górą”. Składa się ona z czterech warstw, rozciągających się przy drodze nr 315) i dwóch dopływów (zwanych później „Galistą Górą”. Na terenie dzielnicy znajdują się dwie, aleja Jana Pawła II, z
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.89

## g100-eval-006 · web_garbage · normal_80

**Prompt:** `Według najnowszych danych`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260614

**Output:**

```text
Według najnowszych danych GUS z 2021 roku odnotowano, że liczba mieszkańców GUS w GUS waha się od 15,5% do ok. 8% w 2020 roku, z czego 97,8% mieszkańców stanowił użytki rolne. GUS leży w strefie przejściowej w strefie przejściowej, od południowo-wschodniej strony w rejonie środkowej części Niziny Południowochińskiej. W G
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.69

## g100-eval-007 · projektowy · normal_80

**Prompt:** `Najważniejszym problemem tego projektu jest`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260615

**Output:**

```text
Najważniejszym problemem tego projektu jest to, że nie są one już w pełni funkcjonalne. Nie są to jednak narzędzia używane do prowadzenia rozmów, ale są też wykorzystywane w celu zapewnienia szybkości ich prowadzenia. Są one również wyposażone w różnego rodzaju narzędzia, takie jak narzędzia do pisania książek (np. narzędzia do pisania książek, a następnie przez pewien czas w celu zapewnienia bezpieczeństwa przed czynnikami zewnętrznymi), które są przeznaczone do
```

**Heurystyka:** Problemy: powtórzenia 1, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 4
**Tok/s generation:** 72.13

## g100-eval-008 · edukacyjny · normal_80

**Prompt:** `Uczenie maszynowe polega na`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260616

**Output:**

```text
Uczenie maszynowe polega na odróżnieniu od wcześniejszych (w zależności od czasu), od rodzaju maszyny, sposobu napisu oraz określonego materiału, rodzaju maszyny, w której maszyny mogą być przechowywane, po upływie czasu, czasu, czasu, materiału w zależności od miejsca, sposobu, sposobu jego odczytu. W tym sensie, maszyna może być też przechowywana w pamięci, na przykład w pamięci. Maszyna
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.05

## g100-eval-009 · encyklopedyczny · normal_80

**Prompt:** `W średniowieczu`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260617

**Output:**

```text
W średniowieczu tereny wsi wchodziły w skład dóbr królewskich (część wsi należała do dóbr kościelnych) głogowskiego, a po jej likwidacji wieś stała się królewszczyzną. W 1589 r. wchodziły w skład klucza korygowskiego Łukasza Opalińskiego. W 1630 r. właścicielem posiadłości tabularnej w Zbierzu był Michał
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 73.18

## g100-eval-010 · skladnia · normal_80

**Prompt:** `Na początku eksperymentu`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260618

**Output:**

```text
Na początku eksperymentu w przemyśle motoryzacyjnym, który z pewnością jest na tyle duży, że w przypadku wielu elementów i możliwości jest możliwe, że na przykład maszyna ta jest dostępna w wersji elektronicznej (np. MMS). Możliwe jest również stosowanie specjalnych technologii – np. Avalon, Self, DCN, Self, TTPS, Self, AMD, T
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.77

## g100-eval-011 · petle · normal_80

**Prompt:** `Ten tekst nie powinien powtarzać tego samego zdania, ponieważ`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260619

**Output:**

```text
Ten tekst nie powinien powtarzać tego samego zdania, ponieważ w tym przypadku może się on różnić od kontekstu, i nie może się wiązać z pytaniem, czy jest to tylko element, który jest jednocześnie częścią zdania, czy pytaniem. Czy może być to argument, ale nie oznacza to, że zdanie w ogóle nie może być wyjaśnione? Jak wyjaśnił dziennikarz, nie powinno się powtarzać pytać: Co może być wypowiedzia
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 70.51

## g100-eval-012 · forum_garbage · normal_80

**Prompt:** `Komentarze użytkowników wskazują, że`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=80 · seed=20260620

**Output:**

```text
Komentarze użytkowników wskazują, że mogą one być używane podczas pracy z innymi ludźmi. Najbardziej popularne w przypadku programów komputerowych, które nie są przeznaczone przez programistów, to Microsoft Windows, Phone, GNU/Linux, XP, LHS lub AFS. Istnieją jednak inne programy komputerowe (np. Microsoft Windows), które oferują darmowe edytory, które umożliwiają zarządzanie zasobami
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.13

## g100-eval-001 · krotka_kontynuacja · normal_120

**Prompt:** `Warszawa to`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260609

**Output:**

```text
Warszawa to jeden z najcenniejszych zabytków w Polsce. Zabytki Kościół parafialny pw. św. Jana Chrzciciela, zbudowany w latach 1839-1904, posiadający cechy barokowe i gotyckie, wzniesiony w stylu późnoklasycystycznym, z fundacji Jana Chrzciciela. Kościół drewniany, klasycystyczny, otynkowany, z 1781 roku, wpisany do rejestru zabytków nieruchomych (nr rej.: 438 z 5.04.1967). Chlebowo – wieś w Polsce położona w województwie kujawsko-pomorskim, w powiecie inow
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach', 'powiecie']
**Quality score:** 4
**Tok/s generation:** 67.14

## g100-eval-002 · krotka_kontynuacja · normal_120

**Prompt:** `Polska jest`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260610

**Output:**

```text
Polska jest częścią Unia Europejska. Władza ustawodawcza składa się z parlamentu, parlamentu, parlamentu i parlamentu. Władzę wykonawczą pełni rząd, parlament, władza sądownicza, niezależny od władzy sądowniczej. Władzę wykonawczą sprawuje Rada, której zwierzchnikiem jest władza sądownicza. Władzę zwierzchnią sprawuje samorząd, sprawujący władzę sądowniczą, władzę sądowniczą. Władzę sądowniczą sprawuje prezydent. Władzę wykonawczą sprawuje Prezydent oraz Rada, która
```

**Heurystyka:** Problemy: powtórzenia 1, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 4
**Tok/s generation:** 67.21

## g100-eval-003 · edukacyjny · normal_120

**Prompt:** `W fizyce energia`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260611

**Output:**

```text
W fizyce energia elektryczna jest równoważna od prędkości światła. W fizyce gazowej równania różniczkowe są to: gdzie: – energia elektryczna, – energia elektryczna. Współcześnie energia elektryczna w fizyce różniczkowej jest równa prędkości światła w czasie, w którym to energia elektryczna jest równa prędkości światła. W fizyce gazowej ma postać postaci  ⁇ ,  ⁇ ,  ⁇ ,  ⁇ −,  ⁇ −−,  ⁇ −,  ⁇ −,  ⁇ −,  ⁇ −,  ⁇ −,  ⁇ −,
```

**Heurystyka:** Problemy: powtórzenia 4, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 1
**Tok/s generation:** 66.54

## g100-eval-004 · edukacyjny · normal_120

**Prompt:** `Sztuczna inteligencja jest`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260612

**Output:**

```text
Sztuczna inteligencja jest częścią kultury, która może być postrzegana w formie magicznych i nierównych kultur. Mogą oni wyjaśnić różnicę między różnymi typami, w zależności od ich położenia geograficznego, ich położenia geograficznego, a także w ogólnym ujęciu kulturowym, ich położenia geograficznego, kulturowego itp. Z tego względu, na zjawisko w historii sztuki, często można znaleźć zarówno koncepcje artystyczne, jak i kulturowe. Cechy kulturowe Na przykład: kultury, kultury, sztuki, kultury, kultury, religii, religii, kultu i kultu
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.56

## g100-eval-005 · skladnia · normal_120

**Prompt:** `Rower składa się z`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260613

**Output:**

```text
Rower składa się z dwóch grup połączonych równolegle do ziemi, oraz częściowo z łącznika między dwiema stronami (zwanych też czasem „Galistą Górą”. Składa się ona z czterech warstw, rozciągających się przy drodze nr 315) i dwóch dopływów (zwanych później „Galistą Górą”. Na terenie dzielnicy znajdują się dwie, aleja Jana Pawła II, z których jeden jest częścią drogi nr 320. Przy drodze nr 315 znajduje się tzw. „Galińska Przełęcz” (dawna nazwa „Galista Górska”), przełę
```

**Heurystyka:** Problemy: powtórzenia 1, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 4
**Tok/s generation:** 66.77

## g100-eval-006 · web_garbage · normal_120

**Prompt:** `Według najnowszych danych`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260614

**Output:**

```text
Według najnowszych danych GUS z 2021 roku odnotowano, że liczba mieszkańców GUS w GUS waha się od 15,5% do ok. 8% w 2020 roku, z czego 97,8% mieszkańców stanowił użytki rolne. GUS leży w strefie przejściowej w strefie przejściowej, od południowo-wschodniej strony w rejonie środkowej części Niziny Południowochińskiej. W GUS znajduje się ok. 10 tysięcy jezior (największe z nich to: w okolicach północno-wschodniej granicy Niziny Południowochińskiej, na południu do Morza Czarnego
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.8

## g100-eval-007 · projektowy · normal_120

**Prompt:** `Najważniejszym problemem tego projektu jest`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260615

**Output:**

```text
Najważniejszym problemem tego projektu jest to, że nie są one już w pełni funkcjonalne. Nie są to jednak narzędzia używane do prowadzenia rozmów, ale są też wykorzystywane w celu zapewnienia szybkości ich prowadzenia. Są one również wyposażone w różnego rodzaju narzędzia, takie jak narzędzia do pisania książek (np. narzędzia do pisania książek, a następnie przez pewien czas w celu zapewnienia bezpieczeństwa przed czynnikami zewnętrznymi), które są przeznaczone do użycia. Dostarczają one zarówno do przechowywania, jak i do przechowywania. Zachowała się duża ilość, co sprawia, że w procesie tworzenia dzieła są używane zarówno do przechowywania, jak i do przechowywania
```

**Heurystyka:** Problemy: powtórzenia 5, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 0
**Tok/s generation:** 66.19

## g100-eval-008 · edukacyjny · normal_120

**Prompt:** `Uczenie maszynowe polega na`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260616

**Output:**

```text
Uczenie maszynowe polega na odróżnieniu od wcześniejszych (w zależności od czasu), od rodzaju maszyny, sposobu napisu oraz określonego materiału, rodzaju maszyny, w której maszyny mogą być przechowywane, po upływie czasu, czasu, czasu, materiału w zależności od miejsca, sposobu, sposobu jego odczytu. W tym sensie, maszyna może być też przechowywana w pamięci, na przykład w pamięci. Maszyna może być przechowywana w pamięci, np. w pamięci operatorskiej, w pamięci, w pamięci, w pamięci, w pamięci, w pamięci, w pamięci, w pamięci itd. Maszyny może
```

**Heurystyka:** Problemy: powtórzenia 9, ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 0
**Tok/s generation:** 66.34

## g100-eval-009 · encyklopedyczny · normal_120

**Prompt:** `W średniowieczu`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260617

**Output:**

```text
W średniowieczu tereny wsi wchodziły w skład dóbr królewskich (część wsi należała do dóbr kościelnych) głogowskiego, a po jej likwidacji wieś stała się królewszczyzną. W 1589 r. wchodziły w skład klucza korygowskiego Łukasza Opalińskiego. W 1630 r. właścicielem posiadłości tabularnej w Zbierzu był Michał Tarnowski, wojewoda poznański. Miejscowość liczyła 30 łanów kmiecych, 26 zagrodników zagrodników, folwark i młyn wodny. W 1630 r. w
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 67.04

## g100-eval-010 · skladnia · normal_120

**Prompt:** `Na początku eksperymentu`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260618

**Output:**

```text
Na początku eksperymentu w przemyśle motoryzacyjnym, który z pewnością jest na tyle duży, że w przypadku wielu elementów i możliwości jest możliwe, że na przykład maszyna ta jest dostępna w wersji elektronicznej (np. MMS). Możliwe jest również stosowanie specjalnych technologii – np. Avalon, Self, DCN, Self, TTPS, Self, AMD, TTPS, DCNC, Self, AMD, TTP, QMS. To nie tylko sprawdzone i skomplikowane rozwiązanie, ale również skuteczne w postaci aplikacji mobilnej
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.67

## g100-eval-011 · petle · normal_120

**Prompt:** `Ten tekst nie powinien powtarzać tego samego zdania, ponieważ`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260619

**Output:**

```text
Ten tekst nie powinien powtarzać tego samego zdania, ponieważ w tym przypadku może się on różnić od kontekstu, i nie może się wiązać z pytaniem, czy jest to tylko element, który jest jednocześnie częścią zdania, czy pytaniem. Czy może być to argument, ale nie oznacza to, że zdanie w ogóle nie może być wyjaśnione? Jak wyjaśnił dziennikarz, nie powinno się powtarzać pytać: Co może być wypowiedziane? Jakie zdanie musi wyjaśniać? Na przykład słowo "nie powinno być wypowiedziane" może być wypowiedzią, którą określamy jako zdanie w formie pytań lub zdanie. Na przykład nazwisko kogoś jest
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 56.46

## g100-eval-012 · forum_garbage · normal_120

**Prompt:** `Komentarze użytkowników wskazują, że`

**Settings:** temp=0.8 · top_k=40 · max_new_tokens=120 · seed=20260620

**Output:**

```text
Komentarze użytkowników wskazują, że mogą one być używane podczas pracy z innymi ludźmi. Najbardziej popularne w przypadku programów komputerowych, które nie są przeznaczone przez programistów, to Microsoft Windows, Phone, GNU/Linux, XP, LHS lub AFS. Istnieją jednak inne programy komputerowe (np. Microsoft Windows), które oferują darmowe edytory, które umożliwiają zarządzanie zasobami komputerowymi. Układ kodowania (ang. utortory) – rodzaj układzie kodowania, który ma postać okrągłej lub prostokątnej (rzadko okrągłej, do której są dwie
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.26

## g100-eval-001 · krotka_kontynuacja · creative_80

**Prompt:** `Warszawa to`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260609

**Output:**

```text
Warszawa to jeden z najcenniejszych przykładów, jakie należy zwrócić o wsparcie dla innych użytkowników, wśród nich. Poza tym, iż zarządzanie klientem jest także niezwykle proste w prowadzeniu biznesu, możemy zdecydować się na takie rozwiązania jak: - Usługa powinna być oferowana online, na przykład opcję „docelować”. Usługa może być przeprowadzana bez opcji „docelować”, ale w ten sposób
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 73.54

## g100-eval-002 · krotka_kontynuacja · creative_80

**Prompt:** `Polska jest`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260610

**Output:**

```text
Polska jest częścią Unia Socjalistycznej Europy. W latach 1919-1948 za działalność KT odpowiadał jeden z najbardziej znanych przedstawicieli polskiej socjalistycznej partii. Zarys ekonomiczny W 1921 został ukarany za liczne zaniepokojenie się ze śmiercią kobiety i jej domem. W okresie międzywojennym zasiadł na Śląsku i w innych rejonach zaborów. Był jednym z
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Quality score:** 5
**Tok/s generation:** 73.5

## g100-eval-003 · edukacyjny · creative_80

**Prompt:** `W fizyce energia`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260611

**Output:**

```text
W fizyce energia elektryczna cząsteczek o słabym energią, nie jest równa energii elektrycznej. W tym sensie elektrodynamika kwantowa może być bardzo wysoka w stosunku do innych pierwiastków – w przypadku związków kompleksów z grupy gazów, w których temperatura może być prawie zerowa. W efekcie elektrodynamika kwantowa jest bardzo słaba od temperatury i
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.53

## g100-eval-004 · edukacyjny · creative_80

**Prompt:** `Sztuczna inteligencja jest`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260612

**Output:**

```text
Sztuczna inteligencja jest częścią kultury (np. religii czysto religijnej). Mogą to być również nauki dotyczące natury, życia religijnego, materialnego, kulturowego lub obyczajowego. Dzieje sztuki Limfocyty – bezbarwne limfocyty o charakterze antropomorficznym, zwykle obejmujące całą społeczność, np. etniczne, w przeszłości zakładano, że
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.48

## g100-eval-005 · skladnia · creative_80

**Prompt:** `Rower składa się z`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260613

**Output:**

```text
Rower składa się z dwóch grup połączonych równolegle do ziemi, oraz tworzących ją dwóch samodzielnych zbiorników wodne (m.in.: A, B, B, A, D). Są one budowane na zasadzie długości. Zbiorniki składają się z trzech części uskoków o kształcie wąskim, z których każda połączona jest równolegle do ziemi, a z nich jednego z pozostałych części,
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.86

## g100-eval-006 · web_garbage · creative_80

**Prompt:** `Według najnowszych danych`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260614

**Output:**

```text
Według najnowszych danych GUS-u podczas kampanii wyborczej, które odnotowały ok. 8,5% wyborców, było więc wynikiem ok. 82,1%. Do wyborów z września 2006 przyjechał kandydat KO, Robert Gładysz (ur. 465), który zasiadł w opozycji, a po przewlekłych protestanckich nalotach przeprowadził liczne obrady w wyborach. W
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.79

## g100-eval-007 · projektowy · creative_80

**Prompt:** `Najważniejszym problemem tego projektu jest`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260615

**Output:**

```text
Najważniejszym problemem tego projektu jest to, że nie są one już w pełni funkcjonalne. Nie zawsze jednak wiemy jak wyglądała firma, którą zamierzałby kupić, aby wybrać swój odpowiednik. Dlatego też nie powinniśmy pamiętać o tym, że z jakiej firmy wychodził on na konto w tym samym czasie, czyli na jego początku. Dlatego też wiemy jak wygląda normalny podział posiadany przez osobę lub osobę jest zdecydowanie ważniejsza od tej
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.13

## g100-eval-008 · edukacyjny · creative_80

**Prompt:** `Uczenie maszynowe polega na`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260616

**Output:**

```text
Uczenie maszynowe polega na odróżnieniu sposobu odniesienia (w zależności od czasu), kształtu, stylu, stylu, charakteru obiektów, stylu, rodzaju czy sposobu przygotowania, do odpowiedniego przygotowania. W przypadku warsztatowych warsztatów, techniki planszowe to np. warsztaty wulkaniczne, projektowanie, projektowanie, konstrukcję, tworzenie lub stosowanie wkładu dla uczestników. Układ SI (ang. UNIX) – układ
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.02

## g100-eval-009 · encyklopedyczny · creative_80

**Prompt:** `W średniowieczu`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260617

**Output:**

```text
W średniowieczu tereny ziemi czerskiej w dorzeczu Wisły i Wisły dominowały wsie, które to tereny włączono do dóbr królewskich w roku 1462 (dawne ziemie dawnej gminy i wsi leżące w powiecie brzeskim, gmina Olkusz), które to obszar oddzielał między innymi miasto Sławno, położone 10 km na wschód od Tykocina, na
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['powiecie']
**Quality score:** 4
**Tok/s generation:** 73.13

## g100-eval-010 · skladnia · creative_80

**Prompt:** `Na początku eksperymentu`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260618

**Output:**

```text
Na początku eksperymentu w przemyśle motoryzacyjne zaczęto tworzyć samochody bez przegubowego oświetlenia, a w drugiej połowie lat 60. i 70. i 70. XX wieku zaczęto wytwarzać modele samochodów, które wykorzystywano już tylko do produkcji samochodów samochodowych. Początkowo samochody te były jednymi z rodzajów konstrukcji. Na początku XX wieku powstała wersja M135 o takim samym nazwie, tym razem M1352. Roz
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.6

## g100-eval-011 · petle · creative_80

**Prompt:** `Ten tekst nie powinien powtarzać tego samego zdania, ponieważ`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260619

**Output:**

```text
Ten tekst nie powinien powtarzać tego samego zdania, ponieważ domagają się wtedy dodatkowego przedstawienia wszystkich pytań na temat konkretnego tematu. Wyraźnie odnoszą się do nich zarówno wypowiedzi, jak i przemocy wobec właściciela. Zmienianie może być objawem naśladownictwa właściciela – czyli określone w przepisach ustawowych ustawowa regulacja może się jednak wiązać z sytuacją, w jakiej posiadasz dokumenty, a także na przykład
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 70.55

## g100-eval-012 · forum_garbage · creative_80

**Prompt:** `Komentarze użytkowników wskazują, że`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=80 · seed=20260620

**Output:**

```text
Komentarze użytkowników wskazują, że mogą one być używane podczas pracy z innymi ludźmi. Najbardziej spektakularniejszymi wydarzeniami, które miały miejsce 1 września 1995, są wybory do parlamentu francuskiego. Od marca 1999 do marca 2000 na ziemiach polskich były posiedzenia sejmowe dotyczące wyborów i wyborów w styczniu 2001. Są one wykorzystywane w sytuacjach, w których głosowane uprawnienia do składania wniosków, są nadużywane, a także
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 72.2

## g100-eval-001 · krotka_kontynuacja · creative_120

**Prompt:** `Warszawa to`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260609

**Output:**

```text
Warszawa to jeden z najcenniejszych przykładów, jakie należy zwrócić o wsparcie dla innych użytkowników, wśród nich. Poza tym, iż zarządzanie klientem jest także niezwykle proste w prowadzeniu biznesu, możemy zdecydować się na takie rozwiązania jak: - Usługa powinna być oferowana online, na przykład opcję „docelować”. Usługa może być przeprowadzana bez opcji „docelować”, ale w ten sposób może wystąpić z użyciem narzędzia, które umożliwia tworzenie nowego celu. - Usługa mogłaby być oferowana przez użytkowników, ale nie ma możliwości korzystania z usług internetowych, lecz powinna go wykorzystywać.
```

**Heurystyka:** OK jako krótka kontynuacja base LM.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 8
**Tok/s generation:** 67.26

## g100-eval-002 · krotka_kontynuacja · creative_120

**Prompt:** `Polska jest`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260610

**Output:**

```text
Polska jest częścią Unia Socjalistycznej Europy. W latach 1919-1948 za działalność KT odpowiadał jeden z najbardziej znanych przedstawicieli polskiej socjalistycznej partii. Zarys ekonomiczny W 1921 został ukarany za liczne zaniepokojenie się ze śmiercią kobiety i jej domem. W okresie międzywojennym zasiadł na Śląsku i w innych rejonach zaborów. Był jednym z inicjatorów powstania KTZR, który w 1920 zdobył Wolność i niepodległość. Podczas służby wojskowej w 1939 został żołnierzem Armii Czerwonej. Od 1939 wchodził też w skład Grupy Na
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['w latach']
**Quality score:** 5
**Tok/s generation:** 67.26

## g100-eval-003 · edukacyjny · creative_120

**Prompt:** `W fizyce energia`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260611

**Output:**

```text
W fizyce energia elektryczna cząsteczek o słabym energią, nie jest równa energii elektrycznej. W tym sensie elektrodynamika kwantowa może być bardzo wysoka w stosunku do innych pierwiastków – w przypadku związków kompleksów z grupy gazów, w których temperatura może być prawie zerowa. W efekcie elektrodynamika kwantowa jest bardzo słaba od temperatury i aerodynamiki kwantowej, a cząsteczki kwantowej mogą być jedynie jedno- i jednoelementowe, po których jest dużo światła. Jest to równanie pola magnetycznego
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.54

## g100-eval-004 · edukacyjny · creative_120

**Prompt:** `Sztuczna inteligencja jest`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260612

**Output:**

```text
Sztuczna inteligencja jest częścią kultury (np. religii czysto religijnej). Mogą to być również nauki dotyczące natury, życia religijnego, materialnego, kulturowego lub obyczajowego. Dzieje sztuki Limfocyty – bezbarwne limfocyty o charakterze antropomorficznym, zwykle obejmujące całą społeczność, np. etniczne, w przeszłości zakładano, że „koocyty mają zdolność do tworzenia naturalnych i inteligentnych kulturowo systemów politycznych, lub politycznych, lub do tworzenia nowych struktur”. Są to między innymi: scyty,
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
Rower składa się z dwóch grup połączonych równolegle do ziemi, oraz tworzących ją dwóch samodzielnych zbiorników wodne (m.in.: A, B, B, A, D). Są one budowane na zasadzie długości. Zbiorniki składają się z trzech części uskoków o kształcie wąskim, z których każda połączona jest równolegle do ziemi, a z nich jednego z pozostałych części, przy czym dwie stanowią zbiorniki zbudowane na skutek przetopienia i ewentualnego zaniku wody. Każda podklasa wspólna tworzące zbiorniki wodne stanowią zbiorniki wodne tworzą zbiorniki wodne łączą
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.79

## g100-eval-006 · web_garbage · creative_120

**Prompt:** `Według najnowszych danych`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260614

**Output:**

```text
Według najnowszych danych GUS-u podczas kampanii wyborczej, które odnotowały ok. 8,5% wyborców, było więc wynikiem ok. 82,1%. Do wyborów z września 2006 przyjechał kandydat KO, Robert Gładysz (ur. 465), który zasiadł w opozycji, a po przewlekłych protestanckich nalotach przeprowadził liczne obrady w wyborach. W 2008 został członkiem PiS. Great Gates (pol. „Ganowie”) w mitologii greckiej – bogini płodności, mającej swoje źródło w świątyni Efezu
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.82

## g100-eval-007 · projektowy · creative_120

**Prompt:** `Najważniejszym problemem tego projektu jest`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260615

**Output:**

```text
Najważniejszym problemem tego projektu jest to, że nie są one już w pełni funkcjonalne. Nie zawsze jednak wiemy jak wyglądała firma, którą zamierzałby kupić, aby wybrać swój odpowiednik. Dlatego też nie powinniśmy pamiętać o tym, że z jakiej firmy wychodził on na konto w tym samym czasie, czyli na jego początku. Dlatego też wiemy jak wygląda normalny podział posiadany przez osobę lub osobę jest zdecydowanie ważniejsza od tej w jakiej konkretnej sytuacji, co wiąże się z posiadaniem w swojej firmie potencjalnych klientów. Nie należy zatem trzymać się za tą gwarancją. Jeżeli ktoś ma jakąś formę, powinna być ona okreś
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.25

## g100-eval-008 · edukacyjny · creative_120

**Prompt:** `Uczenie maszynowe polega na`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260616

**Output:**

```text
Uczenie maszynowe polega na odróżnieniu sposobu odniesienia (w zależności od czasu), kształtu, stylu, stylu, charakteru obiektów, stylu, rodzaju czy sposobu przygotowania, do odpowiedniego przygotowania. W przypadku warsztatowych warsztatów, techniki planszowe to np. warsztaty wulkaniczne, projektowanie, projektowanie, konstrukcję, tworzenie lub stosowanie wkładu dla uczestników. Układ SI (ang. UNIX) – układ SI zbudowany na podstawie układów SI o stałej charakterystyce, składający się z trzech, dwóch lub pięciu podstawowych wartości. Dwie jednostki pochodzą od jednego i dwóch takich aksteonów, nazywane
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.36

## g100-eval-009 · encyklopedyczny · creative_120

**Prompt:** `W średniowieczu`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260617

**Output:**

```text
W średniowieczu tereny ziemi czerskiej w dorzeczu Wisły i Wisły dominowały wsie, które to tereny włączono do dóbr królewskich w roku 1462 (dawne ziemie dawnej gminy i wsi leżące w powiecie brzeskim, gmina Olkusz), które to obszar oddzielał między innymi miasto Sławno, położone 10 km na wschód od Tykocina, na północny wschód od Opola, gdzie zatraciły zabudowania na pograniczu Wisły, a następnie w okolice Tykocina, natomiast osadnikami byli także ziemiacy nazywani Tykoci
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=['powiecie']
**Quality score:** 4
**Tok/s generation:** 67.06

## g100-eval-010 · skladnia · creative_120

**Prompt:** `Na początku eksperymentu`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260618

**Output:**

```text
Na początku eksperymentu w przemyśle motoryzacyjne zaczęto tworzyć samochody bez przegubowego oświetlenia, a w drugiej połowie lat 60. i 70. i 70. XX wieku zaczęto wytwarzać modele samochodów, które wykorzystywano już tylko do produkcji samochodów samochodowych. Początkowo samochody te były jednymi z rodzajów konstrukcji. Na początku XX wieku powstała wersja M135 o takim samym nazwie, tym razem M1352. Rozwój konstrukcji pojazdu wiąże się z coraz większym popularności marki, co skutkuje częstszym zmianami konstrukcyjnym pojazdów. Pomimo prób i wdrożeń nowych modeli już w drugiej połowie XX wieku w fabry
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.61

## g100-eval-011 · petle · creative_120

**Prompt:** `Ten tekst nie powinien powtarzać tego samego zdania, ponieważ`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260619

**Output:**

```text
Ten tekst nie powinien powtarzać tego samego zdania, ponieważ domagają się wtedy dodatkowego przedstawienia wszystkich pytań na temat konkretnego tematu. Wyraźnie odnoszą się do nich zarówno wypowiedzi, jak i przemocy wobec właściciela. Zmienianie może być objawem naśladownictwa właściciela – czyli określone w przepisach ustawowych ustawowa regulacja może się jednak wiązać z sytuacją, w jakiej posiadasz dokumenty, a także na przykład nie jest elementem składki akcentowanej. Nie bez znaczenia jest sprawa – jeśli się nie poddasz złego, może to zostać popełnione w przypadku przemocy domowej lub złej czy innej
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 64.99

## g100-eval-012 · forum_garbage · creative_120

**Prompt:** `Komentarze użytkowników wskazują, że`

**Settings:** temp=1.0 · top_k=50 · max_new_tokens=120 · seed=20260620

**Output:**

```text
Komentarze użytkowników wskazują, że mogą one być używane podczas pracy z innymi ludźmi. Najbardziej spektakularniejszymi wydarzeniami, które miały miejsce 1 września 1995, są wybory do parlamentu francuskiego. Od marca 1999 do marca 2000 na ziemiach polskich były posiedzenia sejmowe dotyczące wyborów i wyborów w styczniu 2001. Są one wykorzystywane w sytuacjach, w których głosowane uprawnienia do składania wniosków, są nadużywane, a także w przypadku podejmowania aktywności pobocznej (np. w czasie wyborów). W listopadzie 2007 były to wybory parlamentarne, które odbyły się 8 lipca 2008. Poparły ją grupy Platformy Obywatelskiej
```

**Heurystyka:** Problemy: ucięte zakończenie.
**Residue:** wiki=[] · web=[] · pseudo_ency=[]
**Quality score:** 6
**Tok/s generation:** 66.26
