# Glyph-100M v2.3.1 broad checkpoint eval

Base LM continuation eval. Nie ocenia instrukcyjności ani zachowania chatbota.

- prompts: `60`
- checkpoints: `7`
- presets: `8`
- total generations: `3360`

## Checkpoint Quality

| item | avg_q | rep | natural | cutoff | pseudo | web | wiki | drift | overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 35k | 5.719 | 235/480 | 18/480 | 462/480 | 46/480 | 15/480 | 4/480 | 277/480 | 0.085 |
| 36k | 5.715 | 228/480 | 21/480 | 459/480 | 84/480 | 18/480 | 2/480 | 245/480 | 0.103 |
| 38k | 5.135 | 250/480 | 16/480 | 464/480 | 65/480 | 8/480 | 5/480 | 278/480 | 0.076 |
| 40k | 5.225 | 253/480 | 17/480 | 463/480 | 73/480 | 18/480 | 16/480 | 232/480 | 0.133 |
| 42k | 6.019 | 202/480 | 26/480 | 454/480 | 86/480 | 20/480 | 5/480 | 266/480 | 0.109 |
| 44k | 6.198 | 214/480 | 22/480 | 458/480 | 58/480 | 20/480 | 3/480 | 243/480 | 0.115 |
| 45k | 5.721 | 223/480 | 16/480 | 464/480 | 61/480 | 27/480 | 2/480 | 263/480 | 0.103 |

## Wins vs 35k

| checkpoint | candidate wins | 35k wins | ties |
|---|---:|---:|---:|
| 36k | 137 | 150 | 193 |
| 38k | 124 | 160 | 196 |
| 40k | 121 | 175 | 184 |
| 42k | 145 | 135 | 200 |
| 44k | 157 | 128 | 195 |
| 45k | 143 | 149 | 188 |

## Best Samples

### 35k · current_normal_80 · broad-006 · score=17

**Prompt:** `Energia w fizyce jest`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': [], 'geo_history_suspect': []} · **drift:** `False` · **overlap:** `0.5`

```text
Energia w fizyce jest odwrócona od planety (w zależności od jej położenia), a następnie uformowanie jądra (w zależności od typu widma, do której zaliczane są planety). Pojęcie planety nie jest jednak akceptowane w fizyce, gdyż jest to bardzo trudne. Do planety należy także planeta, która może ją pochwalić jako planeta, która nie jest planetą.
```

### 35k · nucleus_safe_120 · broad-023 · score=17

**Prompt:** `Błąd w konfiguracji może powodować`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': [], 'geo_history_suspect': []} · **drift:** `False` · **overlap:** `0.5`

```text
Błąd w konfiguracji może powodować zakłócenia związane z innym użytkownikiem. Zarówno funkcjonariusze, jak i funkcjonariusze są w stanie wykorzystać konfiguracji przy użyciu systemu operacyjnego, który nie jest używany w przypadku aktualizacji, ale jest w stanie uruchomić system operacyjny, który może być wyświetlany w postaci danych, wyświetlane na ekranie. Jeżeli w przypadku aktualizacji system operacyjny jest wyświetlany w postaci cyfrowej, to do zapisu plików (np. programów) używane są również pliki w postaci cyfrowej. Przy pomocy programów można dotrzeć do plików z rozszerzeniem od jednej do kilku innych aplikacji, np.
```

### 36k · nucleus_safe_80 · broad-006 · score=17

**Prompt:** `Energia w fizyce jest`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': [], 'geo_history_suspect': []} · **drift:** `False` · **overlap:** `0.5`

```text
Energia w fizyce jest silnie uzależniona od energii, jej efektywność oraz jej efektywność. W efekcie, w jaki sposób wykorzystuje się energię elektryczną, energia elektryczna może być bardziej efektywna niż w przypadku modeli z silnikami elektrycznymi. Rozwiązanie to nie tylko technologia, ale także technologia, która pozwala na efektywne zastosowanie energii w przemyśle, w tym elektronicznym, elektronicznym czy elektronicznym.
```

### 42k · current_normal_80 · broad-018 · score=17

**Prompt:** `Jeśli coś działa wolno, trzeba`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': [], 'geo_history_suspect': []} · **drift:** `False` · **overlap:** `0.5`

```text
Jeśli coś działa wolno, trzeba, ale może być to też na tym samym poziomie, że na całym świecie trzeba będzie na nas czekać. Z powodu, iż jeśli mamy jakieś kłopoty, możemy zostać gotową do czynienia z czymś innym, którego mamy okazję porozmawiać na całym świecie. Wybudowanie w mieście to coś więcej, niż w innych przypadkach, gdy miasto nie jest w stanie zapełnić obowiązków do zamieszkania.
```

### 42k · nucleus_safe_80 · broad-054 · score=17

**Prompt:** `Tatry to góry`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': [], 'geo_history_suspect': []} · **drift:** `False` · **overlap:** `0.5`

```text
Tatry to góry o wysokości 2000 m n.p.m. na północy, w Tatry Wysokie (część północna) i odgałęzienie Doliny Kościeliskiej. Najwyższym szczytem jest Groń Tatrzański (część północna). Taternictwo Z wierzchołka po bokach opadających na grań Tatr Wysokich opadają do Doliny Kościeliskiej.
```

### 45k · current_normal_80 · broad-057 · score=17

**Prompt:** `W praktyce oznacza to, że`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': [], 'geo_history_suspect': []} · **drift:** `False` · **overlap:** `0.5`

```text
W praktyce oznacza to, że w różnych warunkach, na podstawie obserwacji, na podstawie danych lub sygnałów odprowadzanych, na podstawie obserwacji, badacze przy pomocy obserwacji stosuje się informacje o tym, co dany obserwator może wykonać, przy założeniu, że obserwator jest w stanie dostarczyć dowolną informację. Zjawisko to jest zwykle obserwowane przez obserwatorów, lecz nie jest w praktyce możliwe.
```

### 36k · current_normal_80 · broad-029 · score=16

**Prompt:** `Wieczorem usiadłem przy biurku i`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': [], 'geo_history_suspect': []} · **drift:** `False` · **overlap:** `0.25`

```text
Wieczorem usiadłem przy biurku i przy stole wznosił się z przodu, pod którymi znajdowały się magazyny. Przebudowa była możliwa do pokonania przez wroga. Po bitwie pod Mostowem zrzutki armii polskiej w 1939 i jej zdobyciu w czerwcu, Polacy wycofali się z Polski, a po zajęciu Mostowa przez wojska niemieckie, udało się ponownie odbić na południe.
```

### 40k · safer_low_temp_80 · broad-018 · score=16

**Prompt:** `Jeśli coś działa wolno, trzeba`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': [], 'geo_history_suspect': []} · **drift:** `False` · **overlap:** `0.25`

```text
Jeśli coś działa wolno, trzeba, ale może być to konieczne. Dlatego też można być w stanie uzyskać dostęp do telefonu, telefonu, telefonu, internetu, internetu i innych usług. Warto również sprawdzić, czy telefon jest zablokowany lub zablokowany, ale może to być też bardzo trudne, ponieważ trzeba je mieć. W tym przypadku warto pamiętać, że telefon jest zablokowany, co może być zagrożone przez telefon lub telefon.
```

### 40k · nucleus_safe_80 · broad-027 · score=16

**Prompt:** `Kupiłem chleb, wróciłem do domu i`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': [], 'geo_history_suspect': []} · **drift:** `False` · **overlap:** `0.25`

```text
Kupiłem chleb, wróciłem do domu i zjechałem do domu, a z mężem przyjechałem do domu. Po kilku dniach w domu, byłem na tyle duży, że przyjechałem do domu. Ona chciała się do tego czasu, ponieważ nie chciałbym tego robić. Jak widzisz, to była droga i ja jestem wdzięczna za to, że już nie byłem w domu. Uczyłem się nawet po całej szkole.
```

### 44k · safer_low_temp_120 · broad-014 · score=16

**Prompt:** `Kiedy brakuje danych, najlepiej`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': [], 'geo_history_suspect': []} · **drift:** `False` · **overlap:** `0.25`

```text
Kiedy brakuje danych, najlepiej w tym przypadku przygotować się do wykonania kilku czynności, które pomogą Ci w czasie nauki w szkoleniu. Dzięki temu możesz także cieszyć się, że Twoje życie jest dla Ciebie idealnym rozwiązaniem. Dlatego też, aby znaleźć idealną dla Ciebie opcję, abyś mógł znaleźć idealny dla siebie sposób na życie. Rozwój technologii w dziedzinie technologii w branży technologicznej jest bardzo popularny w całym świecie. Jednym z najważniejszych elementów, w których można znaleźć idealne rozwiązania technologiczne, jest stworzenie innowacyjnych rozwiązań technologicznych. Dzięki temu możemy cieszyć się swoimi technologiami technologicznymi, takimi jak analiza i analiza danych.
```

## Worst Samples

### 36k · nucleus_safe_120 · broad-052 · score=-10

**Prompt:** `Kraków jest znany z`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': ['w latach', 'województwa', 'województwie', 'powiecie', 'gminie'], 'geo_history_suspect': ['województwie', 'powiecie', 'gminie', 'w latach']} · **drift:** `True` · **overlap:** `0.0`

```text
Kraków jest znany z licznych wypożyczeń w Polsce. Jest jednym z najbardziej popularnych w Polsce klubów sportowych, w tym piłka nożna. W swojej lidze rozegrał 62 mecze i strzelił 38 goli. Zaniemyśl – wieś w Polsce położona w województwie świętokrzyskim, w powiecie kieleckim, w gminie Chmielnik. W latach 1975–1998 miejscowość administracyjnie należała do województwa kieleckiego. Przez miejscowość przebiega droga krajowa nr 98. Wierni kościoła rzymskokatolickiego należą do parafii św. Katarzyny w Chmielniku. Zaniemyśl – wieś w Polsce położona w województwie wielkopolskim, w powiecie szamotu
```

### 38k · current_normal_120 · broad-053 · score=-10

**Prompt:** `Morze Bałtyckie znajduje się`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': ['w latach', 'województwa', 'województwie', 'powiecie', 'gminie'], 'geo_history_suspect': ['województwie', 'powiecie', 'gminie', 'w latach']} · **drift:** `True` · **overlap:** `0.0`

```text
Morze Bałtyckie znajduje się zabytkowy dwór. Niegdyś był to park. Krępa – wieś w Polsce położona w województwie mazowieckim, w powiecie sokołowskim, w gminie Sokołów Podlaski. W latach 1975–1998 miejscowość administracyjnie należała do województwa siedleckiego. Wierni Kościoła rzymskokatolickiego należą do parafii Najświętszego Serca Jezusowego w Dąbrówce Podlaskiej. Krępa-Krępa-Borzymie – wieś w Polsce położona w województwie mazowieckim, w powiecie grójeckim, w gminie Grójec. Wieś duchowna położona była w drugiej połowie XVI
```

### 38k · safer_low_temp_80 · broad-051 · score=-10

**Prompt:** `Wisła przepływa przez`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': ['w latach', 'województwa', 'województwie', 'powiecie', 'gminie'], 'geo_history_suspect': ['województwie', 'powiecie', 'gminie', 'w latach']} · **drift:** `True` · **overlap:** `0.0`

```text
Wisła przepływa przez województwo pomorskie. W miejscowości znajduje się również pomnik przyrody, pole do którego prowadzi obwódki wokół jeziora. W latach 1975–1998 miejscowość administracyjnie należała do województwa gdańskiego. Stępowo – wieś w Polsce położona w województwie kujawsko-pomorskim, w powiecie włocławskim, w gminie Biskupiec Kujawski. W latach 1975–1998 miejscowość administracyjnie należała do województwa włocławskiego
```

### 38k · safer_low_temp_120 · broad-051 · score=-10

**Prompt:** `Wisła przepływa przez`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': ['w latach', 'województwa', 'województwie', 'powiecie', 'gminie', 'spisu'], 'geo_history_suspect': ['województwie', 'powiecie', 'gminie', 'spisu', 'w latach']} · **drift:** `True` · **overlap:** `0.0`

```text
Wisła przepływa przez województwo pomorskie. W miejscowości znajduje się również pomnik przyrody, pole do którego prowadzi obwódki wokół jeziora. W latach 1975–1998 miejscowość administracyjnie należała do województwa gdańskiego. Stępowo – wieś w Polsce położona w województwie kujawsko-pomorskim, w powiecie włocławskim, w gminie Biskupiec Kujawski. W latach 1975–1998 miejscowość administracyjnie należała do województwa włocławskiego. Według Narodowego Spisu Powszechnego (III 2011 r.) liczyła 412 mieszkańców i była trzynastą co do wielkości miejscowością gminy Biskupiec Kujawski. Stępowo – wieś
```

### 40k · nucleus_safe_120 · broad-051 · score=-10

**Prompt:** `Wisła przepływa przez`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': ['w latach', 'województwa', 'województwie', 'powiecie', 'gminie'], 'geo_history_suspect': ['województwie', 'powiecie', 'gminie', 'w latach']} · **drift:** `True` · **overlap:** `0.0`

```text
Wisła przepływa przez kanał w kierunku północno-zachodnim. W pobliżu wsi znajdują się stawy hodowlane i pastewne oraz stawy rybne, a także stawy hodowlane. W pobliżu wsi znajduje się pomnik przyrody – pomnik przyrody – pomnik przyrody. Brodnica – wieś w Polsce położona w województwie świętokrzyskim, w powiecie kieleckim, w gminie Długołęka. W latach 1975–1998 miejscowość administracyjnie należała do województwa kieleckiego. Wieś jest siedzibą rzymskokatolickiej parafii św. Jana Chrzciciela. Brodnica – wieś w Polsce położona w województwie mazowieckim, w powiecie sie
```

### 42k · safer_low_temp_120 · broad-049 · score=-10

**Prompt:** `Warszawa to`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': ['w latach', 'województwa', 'województwie', 'powiecie', 'gminie'], 'geo_history_suspect': ['województwie', 'powiecie', 'gminie', 'w latach']} · **drift:** `True` · **overlap:** `0.0`

```text
Warszawa to miejscowość, w której można znaleźć miejsca parkingowe. W pobliżu miejscowości znajdują się trzy punkty usługowe – jedna z nich zlokalizowana jest na terenie wsi: „Anioł Piaski” i „Anioł Piaski”. W miejscowości działa ponadto szkoła podstawowa oraz punkt biblioteczny. W miejscowości działa również Klub Sportowy „Anioł Piaski”. W latach 1975–1998 miejscowość administracyjnie należała do województwa sieradzkiego. Aniołki – wieś w Polsce położona w województwie podlaskim, w powiecie zambrowskim, w gminie Zambrów. W latach 1975–1998 miejscowość administracyjnie należała do województwa
```

### 42k · nucleus_safe_120 · broad-049 · score=-10

**Prompt:** `Warszawa to`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': ['w latach', 'województwa', 'województwie', 'powiecie', 'gminie'], 'geo_history_suspect': ['województwie', 'powiecie', 'gminie', 'w latach']} · **drift:** `True` · **overlap:** `0.0`

```text
Warszawa to miejscowość, w której można znaleźć wszystko, co się dzieje na terenie miasta. Pod względem liczby ludności miejscowość ma ok. 26 tys. mieszkańców, w tym ok. 10 tys. katolików i 18 katolików. W latach 1975–1998 miejscowość administracyjnie należała do województwa szczecińskiego. Rożniaty – wieś w Polsce położona w województwie mazowieckim, w powiecie sochaczewskim, w gminie Siennica. Leży przy drodze wojewódzkiej nr 656. Wieś położona jest przy drodze wojewódzkiej nr 659. W latach 1975–1998 miejscowość administracyjnie należała do województwa siedleckiego. Rożnów – wieś
```

### 44k · safer_low_temp_120 · broad-053 · score=-10

**Prompt:** `Morze Bałtyckie znajduje się`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': ['w latach', 'województwa', 'województwie', 'powiecie', 'gminie'], 'geo_history_suspect': ['województwie', 'powiecie', 'gminie', 'w latach']} · **drift:** `True` · **overlap:** `0.0`

```text
Morze Bałtyckie znajduje się na terenie miasta, w rejestrze TERYT jest ich 524. Miasto leży na terenie Pojezierza Wielkopolskiego. W latach 1975–1998 miejscowość administracyjnie należała do województwa poznańskiego. W latach 1945–1947 miejscowość była siedzibą gminy Miłostowo. W roku 2011 wieś liczyła 155 mieszkańców. Miłostowo (niem. Osten, 1938–1945 Osten) – wieś w Polsce położona w województwie zachodniopomorskim, w powiecie drawskim, w gminie Drawsko Pomorskie. W latach 1975–1998 miejscowość administracyjnie należała do województwa koszalińskiego. W roku 2007 wieś liczyła 40 mieszkańców. Geografia
```

### 45k · safer_low_temp_120 · broad-053 · score=-10

**Prompt:** `Morze Bałtyckie znajduje się`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': ['w latach', 'województwa', 'województwie', 'powiecie', 'gminie'], 'geo_history_suspect': ['województwie', 'powiecie', 'gminie', 'w latach']} · **drift:** `True` · **overlap:** `0.0`

```text
Morze Bałtyckie znajduje się na terenie miasta, w miejscowości Szlezwik. Krępa – wieś w Polsce położona w województwie lubelskim, w powiecie bialskim, w gminie Żyrard. W latach 1975–1998 miejscowość administracyjnie należała do województwa bialskopodlaskiego. Wierni Kościoła rzymskokatolickiego należą do parafii Podwyższenia Krzyża Świętego w Żyrardowie. Krępa (dawniej Krępa) – wieś w Polsce położona w województwie lubelskim, w powiecie opolskim, w gminie Lubartów. Wieś stanowi sołectwo w gminie Lubartów. W latach 1975–1998 miejscowość administra
```

### 45k · nucleus_safe_120 · broad-051 · score=-10

**Prompt:** `Wisła przepływa przez`

**Residue:** {'wiki': [], 'web': [], 'pseudo_ency': ['w latach', 'województwa', 'województwie', 'powiecie', 'gminie'], 'geo_history_suspect': ['województwie', 'powiecie', 'gminie', 'w latach']} · **drift:** `True` · **overlap:** `0.0`

```text
Wisła przepływa przez województwo pomorskie. Miasta partnerskie Czechy Drezno Polska Skierniewice – wieś w Polsce położona w województwie łódzkim, w powiecie sieradzkim, w gminie Sieradz. Wieś szlachecka Skierniewice położona była w drugiej połowie XVI wieku w powiecie sieradzkim województwa sieradzkiego. W latach 1975–1998 miejscowość administracyjnie należała do województwa sieradzkiego. Przez wieś przebiega droga wojewódzka nr 844 z Sieradza do Sieradza. Skierniewice – wieś w Polsce położona w województwie mazowieckim, w powiecie siedleckim, w gminie
```

## 45k Regressions vs 35k

### broad-020 · nucleus_safe_80 · delta=-14

**Prompt:** `Docker pozwala uruchamiać aplikacje`

**35k score:** `13` · **45k score:** `-1`

**35k:**

```text
Docker pozwala uruchamiać aplikacje dla środowiska Windows, a także edytować aplikacje wtyczki, które są niezbędne do uruchomienia aplikacji, aby móc się uruchomić. Z danych mobilnych pobiera się pliki mobilne. Wtyczki umożliwiające uruchomienie aplikacji mobilnych mają więcej możliwości. Wtyczki mogą być wykonane z narzędziami dostępowymi do Internetu, które umożliwiają uruchomienie aplikacji mobilnych. Dzięki temu, można uruchomić
```

**45k:**

```text
Docker pozwala uruchamiać aplikacje dla osób niepełnosprawnych, jak również użytkowników, którzy korzystają z Internetu. W tym przypadku można stosować programy takie jak: MS Office, MS Office, MS Office, MS Office, MS Office, MS Office, MS Office, MS Office, MS Office, MS Office, MS Office, MS Office, MS Office, MS Office,
```

### broad-049 · current_normal_80 · delta=-13

**Prompt:** `Warszawa to`

**35k score:** `12` · **45k score:** `-1`

**35k:**

```text
Warszawa to grupa miłośników młodzieży, która jest jego wspólnikiem z całego świata. Ich historia sięga XVII wieku. Ich rozwój przypada na lata 1805-1811. Zakonnicy i baptyści, baptyści, baptyści, żyjący w XVII wieku, rozwijający się szybko, tworzyli głównie baptyści. Dzieła Główne dzieła Baptystów i Baptystów to m.in.
```

**45k:**

```text
Warszawa to: Polska, Polska, Polska, Polska, Słowacja: Polska, Słowacja, Słowacja: Polska, Słowacja, Słowacja, Słowacja, Słowacja, Słowacja, Słowacja, Słowacja, Słowacja, Słowacja, Słowacja, Słowacja, Słowacja, Słowacja, Słowacja, Słowacja, Słowacja, Słowacja, Słowacja, Słowacja, Słowa
```

### broad-018 · current_normal_120 · delta=-13

**Prompt:** `Jeśli coś działa wolno, trzeba`

**35k score:** `13` · **45k score:** `0`

**35k:**

```text
Jeśli coś działa wolno, trzeba pamiętać o tym, żeby pamiętać o tym, aby być świadomym. Można również użyć języka hebrajskiego jako określenia jednego słowa lub w konsekwencji dopełnienia czegoś podobnego. Jeżeli chcesz wiedzieć o tym, co możesz wiedzieć o hebrajsku, możesz użyć jednego języka hebrajskiego lub też w innych przypadkach, jeśli będziesz chciałbyś przeczytać o hebrajsku lub w umowie lub w umowie bądź w umowie. W ten sposób twój hebrajski język może być bardzo ważny, jeśli coś będzie zachowywać się dobrze, wtedy będziesz mógł cieszyć się nim za dużo więcej
```

**45k:**

```text
Jeśli coś działa wolno, trzeba stosować się do zasad bezpieczeństwa. W tym przypadku powinno być jednak wiele problemów. Można również zdecydować się na to, jak w przypadku starszych, ponieważ każda z osób ma świadomość i może się za tym przekonać. Warto również zdecydować się na przykład na to, by nieść pomoc osobom, które nie chcą być w stanie samodzielnie realizować swoje marzenia. W takiej sytuacji warto także zdecydować się na to, że takie podejście jest najważniejsze, a także nie jest to łatwe. Warto także zdecydować się na to, by nieść pomoc osobom, które nie mają czasu na pomoc osobom, które nie mają czasu na pomoc osobom, które
```

### broad-003 · nucleus_safe_120 · delta=-13

**Prompt:** `Fakt różni się od opinii tym, że`

**35k score:** `13` · **45k score:** `0`

**35k:**

```text
Fakt różni się od opinii tym, że jest to jedna z przyczyn dominujących w danej kwestii. Istotą jest też fakt, że są one postrzegane jako „dominujące w grupie osób, które nie mogą sobie poradzić ze swoim doświadczeniem”. Doktryna ta nie jest jednak zbyt popularna. Dlatego też zwolennicy teorii wiążą się z tym, że abstrahując odrzuca się w ten sposób, że abstrahując w takiej samej kwestii nie ma się czego obawiać. Praktycznie doktryna ta może być również używana w innych filozofów i filozofów. W litera
```

**45k:**

```text
Fakt różni się od opinii tym, że jest to zbiór składający się z 10 punktów, co oznacza, że w każdym punkcie podzbiór jest ciągły, a w każdym punkcie – ciągły, ale nie ciągły. Przestrzeń jest przestrzenią skończoną. Przestrzeń jest ciągłą przestrzenią skończoną, a przestrzeń jest ciągłą przestrzenią skończoną. Przestrzeń ma ciągłą przestrzenią skończoną, a przestrzeń jest ciągłą przestrzenią skończoną. Przestrzeń jest ciągłą przestrzenią skończoną, a przestrzeń jest ciągłą przestrzenią skończoną. Przestrzeń
```

### broad-044 · current_normal_120 · delta=-12

**Prompt:** `Miejscowość ta leży w`

**35k score:** `7` · **45k score:** `-5`

**35k:**

```text
Miejscowość ta leży w województwie małopolskim, w powiecie tarnowskim, w gminie Zakliczyn. W latach 1975–1998 miejscowość administracyjnie należała do województwa tarnowskiego. Przez wieś przebiega droga krajowa nr 75. Integralne części wsi Dawne części wsi Historia Dawne części wsi – obiekty fizjograficzne W latach 70. ubiegłego wieku przyporządkowano i opracowano spis lokalnych części integralnych dla Dawnego Janusza Korczaka, który opisuje jako „Stary Janusz Korczak, książę Tarnowskich” w „Podhalu nad Wartą” . W miejscowości znajduje się kościół pw.
```

**45k:**

```text
Miejscowość ta leży w województwie małopolskim, w powiecie tarnowskim, w gminie Dębowa. W latach 1975–1998 miejscowość administracyjnie należała do województwa tarnowskiego. Przez wieś przebiega droga krajowa nr 79 Kraków – Tarnów. Wierni kościoła rzymskokatolickiego należą do parafii św. Jana Chrzciciela w Dębowej. Kozień – wieś w Polsce położona w województwie mazowieckim, w powiecie sochaczewskim, w gminie Sochaczew. Leży w powiecie sochaczewskim, w gminie Sochaczew. W latach 1975–1998 miejscowość administracyjnie należała do województwa siedleckiego. Wierni kościoła rzymskokatoli
```

### broad-012 · safer_low_temp_80 · delta=-12

**Prompt:** `Model językowy przewiduje`

**35k score:** `12` · **45k score:** `0`

**35k:**

```text
Model językowy przewiduje, że w języku polskim istnieje wiele różnych odmian języka czeskiego. W języku czeskim występuje ok. 2% wyrazów, które mają łącznie ok. 1,5% (dosłownie ok. 2,1%). W czeskim występują ok. 3% wyrazów, w czeskim – ok. 2,1% (dosłownie ok. 1%), odmiana samogłosek (dosłownie ok.
```

**45k:**

```text
Model językowy przewiduje, że w języku polskim język polski jest językiem urzędowym. W językach urzędowych język polski jest językiem urzędowym, a język polski jest językiem urzędowym. W językach urzędowych języka polskiego język polski jest językiem urzędowym, który jest językiem urzędowym. W języku polskim język polski jest językiem urzędowym, który jest językiem urzędowym na danym terytorium. W języku polskim język polski jest językiem urzędowym
```

### broad-018 · current_normal_80 · delta=-11

**Prompt:** `Jeśli coś działa wolno, trzeba`

**35k score:** `13` · **45k score:** `2`

**35k:**

```text
Jeśli coś działa wolno, trzeba pamiętać o tym, żeby pamiętać o tym, aby być świadomym. Można również użyć języka hebrajskiego jako określenia jednego słowa lub w konsekwencji dopełnienia czegoś podobnego. Jeżeli chcesz wiedzieć o tym, co możesz wiedzieć o hebrajsku, możesz użyć jednego języka hebrajskiego lub też w innych przypadkach, jeśli będziesz chciałbyś przeczytać o hebrajsku lub w umowie
```

**45k:**

```text
Jeśli coś działa wolno, trzeba stosować się do zasad bezpieczeństwa. W tym przypadku powinno być jednak wiele problemów. Można również zdecydować się na to, jak w przypadku starszych, ponieważ każda z osób ma świadomość i może się za tym przekonać. Warto również zdecydować się na przykład na to, by nieść pomoc osobom, które nie chcą być w stanie samodzielnie realizować swoje marzenia. W takiej sytuacji warto także zdecydować się na to, że takie podejście
```

### broad-052 · safer_low_temp_80 · delta=-11

**Prompt:** `Kraków jest znany z`

**35k score:** `9` · **45k score:** `-2`

**35k:**

```text
Kraków jest znany z serialu telewizyjnego w serialu „Katastrofalny świat” (w tym także serialu telewizyjnym) w reżyserii Wojciecha Bogusławskiego. W serialu telewizyjnym występuje również jako ojciec, którego żona jest dziennikarką. W serialu występują również siostra, w której wciela się w postać męża. W serialu występują także siostry, które mają syna i syna. Postacie i postacie W
```

**45k:**

```text
Kraków jest znany z licznych publikacji, w tym m.in. w „Elżbietażu”, „Elżbietażu”, „Elżbietażu”, „Elżbietażu”, „Elżbietażu”, „Elżbietażu”, „Elżbietażu”, „Elżbietażu”, „Elżbietażu”, „Elżbietażu”,
```

## 45k Improvements vs 35k

### broad-006 · safer_low_temp_80 · delta=14

**Prompt:** `Energia w fizyce jest`

**35k score:** `0` · **45k score:** `14`

**35k:**

```text
Energia w fizyce jest odwracalna od planety (w zależności od wielkości), ale jest ona odwracalna od planety (w zależności od typu planety, jej rozmiar i rozmiar) oraz planety (w zależności od wielkości), np. planeta, planeta, planeta. Zatem, planeta jest odwracalna od planety. Układ SI (ang. Układ SI) – układ
```

**45k:**

```text
Energia w fizyce jest silnie związana z energią (w przeciwieństwie do energii kinetycznej). W praktyce jednak energia nie ma wpływu na energię kinetyczną danego obiektu. Elektroda jest źródłem energii kinetycznej z wykorzystaniem energii kinetycznej w fizyce. Zjawisko to dotyczy energii kinetycznej na energię kinetyczną w postaci energii kinetycznej. Energia kinetyczna w fizyce
```

### broad-025 · current_normal_120 · delta=13

**Prompt:** `Rano wyszedłem z domu i`

**35k score:** `0` · **45k score:** `13`

**35k:**

```text
Rano wyszedłem z domu i od razu odmładzała, jak w przypadku tych dwóch pierwszych dzieci. To było naprawdę proste. Nie wiem, czy jest coś, co będzie można zrobić. Są tylko dwie osoby, których chce to zrobić. Uważam, że w ogóle nie mam. Nie wiem, czy jest to możliwe, bo nikt nie będzie miał czasu na to, żeby to robić. To jest tylko jedna osoba, która chciałaby wiedzieć, kiedy chce sobie wyobrazić i dać sobie znać. Nie wiem, czy jest to łatwe, czy naprawdę jest to możliwe. A może to być? To wszystko było łatwe i że
```

**45k:**

```text
Rano wyszedłem z domu i od razu odjechałem się do pracy. Po powrocie do pracy, wstąpiłem do domu. Chciałem iść do pracy przymusowej, a potem już tam, gdzie miałem pracę jako robotnik, a następnie wyjechałem do Berlina, gdzie pracował na roli w fabryce wagonów dla tej firmy, na której pracowałem, a potem do Berlina. Jak się okazało, praca była w tej samej fabryce. Z czasem się zaczęło mnie coraz bardziej uczęszczać na kurs poboczny. Już teraz mam problemy z sercem, a ja w końcu zaczęłam pracować
```

### broad-004 · current_normal_80 · delta=12

**Prompt:** `Backup to`

**35k score:** `-3` · **45k score:** `9`

**35k:**

```text
Backup to jeden z największych miast w USA, położony w Stanach Zjednoczonych. Jego miasto jest znane jako King’s Township, i jest znane jako King Crimson, a jego mieszkańcy są znane jako King’s Township (Blizards Township) i King Crimson. W mieście jest stacja kolejowa King Crimson. Demografia Według spisu z 2010 roku liczy
```

**45k:**

```text
Backup to jeden z największych miast na świecie, położony na całym świecie. Jego miasto jest ważnym centrum kulturalnym i kulturalnym. Miasto i jego okolice mają wiele atrakcji turystycznych, szczególnie w dużych miastach i miasteczkach. W mieście ma swoje tradycje religijne i rodzinne. W mieście znajduje się kilka restauracji, hoteli i hoteli. Miasta partnerskie Baku, Japonia Leiningen, Słowacja Lenin
```

### broad-004 · current_normal_120 · delta=12

**Prompt:** `Backup to`

**35k score:** `-3` · **45k score:** `9`

**35k:**

```text
Backup to jeden z największych miast w USA, położony w Stanach Zjednoczonych. Jego miasto jest znane jako King’s Township, i jest znane jako King Crimson, a jego mieszkańcy są znane jako King’s Township (Blizards Township) i King Crimson. W mieście jest stacja kolejowa King Crimson. Demografia Według spisu z 2010 roku liczy 1438 mieszkańców. Są piątą co do wielkości miejscowością gminy King Crimson w USA. Założone w 1967 roku przez miasto King Crimson w stanie Teksas, posiadającą status
```

**45k:**

```text
Backup to jeden z największych miast na świecie, położony na całym świecie. Jego miasto jest ważnym centrum kulturalnym i kulturalnym. Miasto i jego okolice mają wiele atrakcji turystycznych, szczególnie w dużych miastach i miasteczkach. W mieście ma swoje tradycje religijne i rodzinne. W mieście znajduje się kilka restauracji, hoteli i hoteli. Miasta partnerskie Baku, Japonia Leiningen, Słowacja Leningradu, Słowacja Dolina Łaby (Dwrict Stell, Stell, Stell) – jedna z najważniejszych dolin polskich w Polsce. Znajduje się na
```

### broad-036 · current_normal_120 · delta=12

**Prompt:** `Najważniejsza myśl tego akapitu to`

**35k score:** `-3` · **45k score:** `9`

**35k:**

```text
Najważniejsza myśl tego akapitu to nie tylko pamięć, ale również pamięć. Przykładowo, można ją zapamiętać jako pamięć, pamięć, pamięć, pamięć, pamięć i pamięć. Warto także zapamiętać jako pamięć o tym, że jest ona zapamiętana jako pamięć, pamięć, pamięć, pamięć, pamięć. Zdzisław Marecki (ur. 23 lutego 1956 w Łodzi) – polski gitarzysta, wokalista, gitarzysta, kompozytor, aktor i autor tekstów. W latach 1996–2014 współzałożyciel zespołu Machine, od 1998 do 2012 współzałożyciel grupy Cyberpunk. W latach 1997–1998
```

**45k:**

```text
Najważniejsza myśl tego akapitu to nie tylko rozbieżność. Jednakże w niektórych przypadkach, gdy nie zadziałamy, powinniśmy zastanowić się co będzie konieczne i jak będzie to możliwe, żebyśmy mogli bezpiecznie, a także jak nam dany obiekt miał sens i jak będziemy mogli to zrobić. W środę, 23 czerwca, w związku z uroczystościami otwarcia kościoła pw. św. Jana Chrzciciela w Ostrowie Wielkopolskim, w czasie której nabożeństwa były w Ostrowie Poznańskim, w kościele odbyła się uroczystość Bożego Ciała. Mszę św. w intencji rodzinnej w Ostrowie Wielkopolskim
```

### broad-057 · current_normal_120 · delta=12

**Prompt:** `W praktyce oznacza to, że`

**35k score:** `2` · **45k score:** `14`

**35k:**

```text
W praktyce oznacza to, że w niektórych krajach europejskich na podstawie badań genetycznych, takich jak: EKG, Niemcy, Niemcy, Rosja, Francja, Austria, Wielka Brytania oraz Niemcy, są to wszystkie kraje członkowskie Unii Europejskiej. Poza Polską, w Polsce dominującą grupę etniczną, w Polsce posługuje się ok. 50% populacji. W Polsce dominującym ujemnym wskaźnikiem zgodnym z wskaźnikiem zgodnym z wskaźnikiem zgodnym z wskaźnikiem zgodnym z wskaźnikami zgodnym z wskaźnikiem zgodnym z wskaźnikiem zgodności z wskaźnikiem zgodności z wskaźnikiem zgo
```

**45k:**

```text
W praktyce oznacza to, że w różnych warunkach, na podstawie obserwacji, na podstawie danych lub sygnałów odprowadzanych, na podstawie obserwacji, badacze przy pomocy obserwacji stosuje się informacje o tym, co dany obserwator może wykonać, przy założeniu, że obserwator jest w stanie dostarczyć dowolną informację. Zjawisko to jest zwykle obserwowane przez obserwatorów, lecz nie jest w praktyce możliwe. Przykładowo badanie to jest obserwowane przez obserwatorów ze względów naukowych. Przykładowo, obserwacja powinna zostać przeprowadzona w odległości około 12 metrów od środka obserwatora. Przykładowo,
```

### broad-040 · current_normal_80 · delta=11

**Prompt:** `Zaloguj się, aby odpowiedzieć`

**35k score:** `0` · **45k score:** `11`

**35k:**

```text
Zaloguj się, aby odpowiedzieć na pytanie: "Pan Paolo, Aerosmita, Argora, Bodo, Argora, Argora, Bodo: "Paolo, Aerosmita, Aerosmita, Argora, Bodo, Argora, Argora, Bodo, Argora, Argora, Bodo i
```

**45k:**

```text
Zaloguj się, aby odpowiedzieć: “Nie ma na to szansy” – napisał. Nie zgadzał się na to, że jest to niemożność zastąpienia miejsca na liście w historii. Dokładny, ale i niebezpieczny, byłby nie tylko jednym z największych sukcesów ICC. W końcu, jeżelibyśmy chcieli mieć pewność, że będzie to miejsce, to w przypadku, kiedy chcemy coś sobie
```

### broad-010 · current_normal_120 · delta=11

**Prompt:** `Sieć komputerowa pozwala`

**35k score:** `2` · **45k score:** `13`

**35k:**

```text
Sieć komputerowa pozwala na łatwe przechowywanie danych w sieci. Rozszerzyła się także w przypadku sieci komputerowej, ponieważ nie ma możliwości uruchamiania oprogramowania, z powodu czego nie jest on bardzo kompatybilny z urządzeniem systemowym. Rozszerzyła się w przypadku sieci komputerowej. W praktyce, w przypadku wersji komputerowej nie ma potrzeby wymiany danych z urządzeniem. Rozszerzyła się znacznie, a w przypadku technologii Linuksa można łatwo usunąć (np. w wersji NDMA). Rozszerzyła się np. w wersji NDMA. Pozwalałaby ona na tworzenie danych z dodatkowego
```

**45k:**

```text
Sieć komputerowa pozwala na łatwe podłączanie komputerów z komputera. Dzięki temu możliwe jest również ładowanie urządzeń przenośnych i innych zasobów przez systemy operacyjne. W zależności od przeznaczania komputera do sieci przenośnej konieczne jest również ładowanie komputera i innych urządzeń przenośnych lub innych urządzeń przenośnych. W praktyce każdy komputer wykorzystywany jest do tworzenia wielu urządzeń przenośnych. Umożliwia to dostosowywanie się do konkretnych potrzeb danej firmy, co pozwala na tworzenie własnych modułów przenośnych. W przypadku takich urządzeń, każdy komputer posiada dostęp do wszystkich niezbędnych zasobów, co pozwala na ładowanie, które jest niezbędne w
```
