# „Another Name” — cue sheet do akceptacji

Status: **projekt nieaktywny**. Ten dokument ani towarzyszący YAML nie są
automatyzacją Home Assistant. Nie utworzono żadnego harmonogramu i nie wysłano
żadnej komendy do urządzeń.

## Zasada czasu

- Ostry cue: `send = track event + 0,163 s`.
- Transition kończący się na wydarzeniu: `send = target + 0,163 s - duration`.
- Transition zaczynający się z wydarzeniem: `send = start + 0,163 s`.
- Wszystkie czasy wysłania są liczone od chwili wydania przyszłego polecenia
  startu audio, nie od chwili usłyszenia pierwszej próbki.
- M00 wymaga ujemnego pre-rollu. M14 jest świadomym „hold” bez komendy.

## Skrót macro cues

| ID | Track time | Typ | Cel wizualny | Pierwszy send | Transition |
|---|---:|---|---|---:|---:|
| M00 | `0:00.000` | gradual | 2% bursztynowej taśmy gotowe na start | `-0:01.837` | 2,000 s |
| M01 | `0:08.522` | gradual | pierwszy oddech glow, strip 3% | `0:04.685` | 4,000 s |
| M02 | `0:14.652` | structural | cieplejszy strip 5% | `0:11.815` | 3,000 s |
| M03 | `0:26.610` | structural | pierwsze światło przy łóżku | `0:22.773` | 4,000 s |
| M04 | `0:39.869` | structural | rytmiczny lift, nadal lokalnie | `0:36.032` | 4,000 s |
| M05 | `0:45.627` | gradual | pierwsze światło po drugiej stronie | `0:42.790` | 3,000 s |
| M06 | `0:51.873` | accent | najmocniejszy transient, strip pulse | `0:52.036` | sharp + 200 ms hold |
| M07 | `0:54.381` | structural | wejście mocnego dołu i room opening | `0:53.044` | 1,500 s |
| M08 | `1:11.819` | structural | cały pokój jest już czytelny | `1:08.982` | 3,000 s |
| M09 | `1:26.959` | climax | wyraźny, lecz jeszcze niepełny szczyt: 55/70/58% | `1:25.922` | 1,200 s |
| M10 | `1:30.651` | structural | daylight bridge: 64/80/70%, bez Aqara | `1:28.314` | 2,500 s |
| M11 | `1:36.665` | ending | start wake-up ramp podczas uspokojenia muzyki | `1:36.828` | 7,268 s |
| M12 | `1:43.933` | ending | finalny top-off do 100% bieli na koniec pliku | `1:44.096` | 7,245 s |
| M13 | `1:47.926` | accent | zarezerwowany późny Aqara ON; `aqara_target: TBD` | `1:48.089` warunkowo | sharp |
| M14 | `1:51.177` | ending | invariant: wszystkie trzy światła 100% bieli | brak komendy | hold |

## Szczegółowe macro cues

### M00 — pre-roll glow

1. **Exact track timestamp:** `0:00.000`.
2. **Cue type:** gradual.
3. **Musical reason:** otwarcie jest powściągliwe; scena ma istnieć przed
   pierwszym słyszalnym materiałem.
4. **Spatial reason:** światło pozostaje wyłącznie przy łóżku.
5. **LED strip:** ON, 2%, CIE XY `[0.585, 0.390]`, głęboki bursztyn.
6. **Near-bed bulb:** OFF.
7. **Far-room bulb:** OFF.
8. **Brightness:** strip 2%; reszta 0%.
9. **Color:** tylko amber strip; żarówki bez światła.
10. **Transition:** 2,000 s.
11. **Intended visual target:** strip osiąga 2% dokładnie przy track `0:00.000`.
12. **Calculated command send time:** `-0:01.837`, czyli pre-roll.
13. **Confidence:** wysoka dla projektu, niska dla minimum sprzętowego.
14. **Manual tuning:** sprawdzić w ciemnym pokoju, czy 2% jest widoczne i
    komfortowe; oba Aqara mają być przed startem wyłączone.

### M01 — first breath

1. **Exact track timestamp:** `0:08.522`.
2. **Cue type:** gradual.
3. **Musical reason:** pierwsza wyraźna granica novelty w spokojnym intro.
4. **Spatial reason:** rośnie jedynie odbite światło przy łóżku.
5. **LED strip:** 2→3%, XY `[0.570, 0.400]`.
6. **Near-bed bulb:** nadal OFF.
7. **Far-room bulb:** nadal OFF.
8. **Brightness:** strip 3% target.
9. **Color:** głęboki bursztyn staje się minimalnie jaśniejszy.
10. **Transition:** 4,000 s.
11. **Intended visual target:** 3% przy `0:08.522`.
12. **Calculated command send time:** `0:04.685`.
13. **Confidence:** średnia.
14. **Manual tuning:** porównać z rzeczywistym końcem pierwszej frazy; tolerancja
    korekty około ±0,5 s.

### M02 — warm motif

1. **Exact track timestamp:** `0:14.652`.
2. **Cue type:** structural.
3. **Musical reason:** zmiana harmoniczno-widmowa bez agresywnego skoku RMS.
4. **Spatial reason:** dalej budujemy tylko halo łóżka.
5. **LED strip:** 3→5%, XY `[0.545, 0.410]`.
6. **Near-bed bulb:** OFF.
7. **Far-room bulb:** OFF.
8. **Brightness:** strip 5%.
9. **Color:** ciepły bursztyn.
10. **Transition:** 3,000 s.
11. **Intended visual target:** 5% przy `0:14.652`.
12. **Calculated command send time:** `0:11.815`.
13. **Confidence:** średnia.
14. **Manual tuning:** odsłuchowo potwierdzić boundary `0:14.652`; w razie
    potrzeby przesunąć cue, nie zmieniając kolejności przestrzennej.

### M03 — near-bed key appears

1. **Exact track timestamp:** `0:26.610`.
2. **Cue type:** structural.
3. **Musical reason:** wzrost RMS, centroidu i czytelności rytmu.
4. **Spatial reason:** pierwsze właściwe światło pokoju pojawia się najbliżej
   osoby śpiącej, nad fotelem.
5. **LED strip:** 5→9%, XY `[0.525, 0.415]`.
6. **Near-bed bulb:** ON, 3%, 2200 K w jasnym trybie białym.
7. **Far-room bulb:** OFF.
8. **Brightness:** strip 9%, near 3%, far 0%.
9. **Color:** gold/amber + bardzo ciepła biel.
10. **Transition:** 4,000 s.
11. **Intended visual target:** oba poziomy osiągnięte przy `0:26.610`.
12. **Calculated command send time:** `0:22.773`.
13. **Confidence:** wysoka.
14. **Manual tuning:** upewnić się, że 3% white mode EMOS nie jest już zbyt
    mocne; użyć najniższego stabilnego poziomu.

### M04 — rhythmic lift

1. **Exact track timestamp:** `0:39.869`.
2. **Cue type:** structural.
3. **Musical reason:** silna novelty i ostrzejsze transienty.
4. **Spatial reason:** wzmacniamy stronę przy łóżku, daleki fill nadal nie
   istnieje.
5. **LED strip:** 9→13%, XY `[0.505, 0.415]`.
6. **Near-bed bulb:** 3→8%, 2400 K.
7. **Far-room bulb:** OFF.
8. **Brightness:** strip 13%, near 8%, far 0%.
9. **Color:** ciepłe złoto i ciepła biel.
10. **Transition:** 4,000 s.
11. **Intended visual target:** poziomy gotowe przy `0:39.869`.
12. **Calculated command send time:** `0:36.032`.
13. **Confidence:** wysoka.
14. **Manual tuning:** subiektywna fraza może wypaść bliżej downbeatu
    `0:40.287`; oba punkty należy porównać podczas późniejszego odsłuchu.

### M05 — far-room light appears

1. **Exact track timestamp:** `0:45.627`.
2. **Cue type:** gradual.
3. **Musical reason:** mocna granica przed serią największych transientów.
4. **Spatial reason:** pierwsze 2% po drugiej stronie pokoju tworzy głębię.
5. **LED strip:** 13→16%, XY `[0.490, 0.410]`.
6. **Near-bed bulb:** 8→12%, 2500 K.
7. **Far-room bulb:** OFF→2%, 2200 K.
8. **Brightness:** 16% / 12% / 2%.
9. **Color:** złoto; near trochę mniej ciepłe niż far.
10. **Transition:** 3,000 s.
11. **Intended visual target:** daleki fill widoczny przy `0:45.627`.
12. **Calculated command send time:** `0:42.790`.
13. **Confidence:** wysoka.
14. **Manual tuning:** jeśli 2% nie jest stabilne, użyć 3%; nie podnosić
    dalekiej żarówki do poziomu near-bed.

### M06 — first strike

1. **Exact track timestamp:** `0:51.873`.
2. **Cue type:** accent.
3. **Musical reason:** najmocniejszy wykryty transient całego utworu.
4. **Spatial reason:** reaguje wyłącznie pośrednia taśma, bez błysku w oczy.
5. **LED strip:** puls 16→21→16%, 200 ms.
6. **Near-bed bulb:** hold 12% / 2500 K.
7. **Far-room bulb:** hold 2% / 2200 K.
8. **Brightness:** chwilowe +5 punktów procentowych na stripie.
9. **Color:** bez zmiany, XY `[0.490, 0.410]`.
10. **Transition:** sharp rise; 200 ms hold przed powrotem.
11. **Intended visual target:** początek glow przy `0:51.873`.
12. **Calculated command send time:** rise `0:52.036`, return `0:52.236`.
13. **Confidence:** wysoka.
14. **Manual tuning:** M06 jest pierwszym punktem P02; nie wolno wysłać go
    podwójnie z dwóch list.

### M07 — bass opening

1. **Exact track timestamp:** `0:54.381`.
2. **Cue type:** structural.
3. **Musical reason:** najwyższa novelty przed climaxem, wejście mocnego dołu i
   powtarzalnych ataków.
4. **Spatial reason:** obie żarówki stają się czytelne, ale near-bed nadal
   prowadzi.
5. **LED strip:** 16→22%, XY `[0.475, 0.405]`.
6. **Near-bed bulb:** 12→22%, 2700 K.
7. **Far-room bulb:** 2→8%, 2400 K.
8. **Brightness:** 22% / 22% / 8%.
9. **Color:** złoto + cieplejszy far-room fill.
10. **Transition:** 1,500 s.
11. **Intended visual target:** trzy poziomy gotowe przy `0:54.381`.
12. **Calculated command send time:** `0:53.044`.
13. **Confidence:** wysoka.
14. **Manual tuning:** nie dodawać pulsowania żarówek do transientów `0:54.126`
    i `0:57.864`; taśma wystarczy.

### M08 — room opens

1. **Exact track timestamp:** `1:11.819`.
2. **Cue type:** structural.
3. **Musical reason:** przejście do pełnego buildu; RMS i onsety są już stale
   wysokie, udział dołu około 0,74.
4. **Spatial reason:** obie strony pokoju są widoczne, ale near-bed pozostaje
   jaśniejsze.
5. **LED strip:** 22→30%, XY `[0.445, 0.400]`.
6. **Near-bed bulb:** 22→38%, 3000 K.
7. **Far-room bulb:** 8→22%, 2800 K.
8. **Brightness:** 30% / 38% / 22%.
9. **Color:** jaśniejsze złoto i stopniowo neutralniejsza biel.
10. **Transition:** 3,000 s.
11. **Intended visual target:** pokój otwarty przy `1:11.819`.
12. **Calculated command send time:** `1:08.982`.
13. **Confidence:** wysoka.
14. **Manual tuning:** zachować asymetrię; nie zastępować działań encją grupy.

### M09 — kinetic climax

1. **Exact track timestamp:** `1:26.959`.
2. **Cue type:** climax.
3. **Musical reason:** maksimum połączonego energy/onset/spectral score.
4. **Spatial reason:** wyraźnie rozjaśniamy cały pokój, ale zostawiamy zapas
   na funkcjonalny wake-up ramp po kulminacji.
5. **LED strip:** 30→55%, pale gold XY `[0.395, 0.380]`.
6. **Near-bed bulb:** 38→70%, **natywny white mode / `color_temp`**, 3600 K.
7. **Far-room bulb:** 22→58%, **natywny white mode / `color_temp`**, 3500 K.
8. **Brightness:** strip 55%, near 70%, far 58%.
9. **Color:** taśma nadal zachowuje filmowe złoto; żarówki są już
   cieple-neutralną prawdziwą bielą, nie RGB udającym biel.
10. **Transition:** 1,200 s.
11. **Intended visual target:** szczyt przy `1:26.959`.
12. **Calculated command send time:** `1:25.922` (`86,958730 + 0,163 - 1,200`).
13. **Confidence:** wysoka.
14. **Manual tuning:** ocenić komfort 55% taśmy i 70% near-bed z pozycji na
    poduszce; nie obniżać finału, jeśli ten punkt okaże się mocny.

### M10 — daylight bridge

1. **Exact track timestamp:** `1:30.651`.
2. **Cue type:** structural.
3. **Musical reason:** ostry onset przy wejściu finalnej głośnej półki.
4. **Spatial reason:** obie strony pokoju rosną, lecz unikamy jeszcze ostrego
   ON/OFF dużej lampy.
5. **LED strip:** 55→64%, low-saturation warm white XY `[0.370, 0.370]`.
6. **Near-bed bulb:** 70→80%, natywny white mode, 4200 K.
7. **Far-room bulb:** 58→70%, natywny white mode, 4000 K.
8. **Brightness:** strip 64%, near 80%, far 70%.
9. **Color:** filmowe złoto przechodzi w wyraźniejszą biel dzienną.
10. **Transition:** 2,500 s.
11. **Intended visual target:** poziomy są gotowe przy `1:30.651`.
12. **Calculated command send time:** `1:28.314`
    (`90,650703 + 0,163 - 2,500`).
13. **Confidence:** wysoka dla progresji, średnia dla krzywej sprzętowej.
14. **Manual tuning:** sprawdzić, czy zmiana temperatury w żarówkach jest
    płynna przy równoczesnej zmianie jasności.

### M11 — wake-up ramp

1. **Exact track timestamp:** `1:36.665`.
2. **Cue type:** ending.
3. **Musical reason:** downbeat wypada przy początku gwałtownego, trwałego
   spadku RMS.
4. **Spatial reason:** muzyka zaczyna się wyciszać, ale światło świadomie
   kontynuuje wzrost i przestaje być wyłącznie scenografią.
5. **LED strip:** 64→88%, native XY `[0.355, 0.360]`, prawie neutralna biel.
6. **Near-bed bulb:** 80→95%, natywny white mode, 4700 K.
7. **Far-room bulb:** 70→92%, natywny white mode, 4600 K.
8. **Brightness:** wszystkie trzy źródła rosną; nic nie uspokaja się wizualnie.
9. **Color:** wyraźne przejście z warm-white do neutralnego światła porannego.
10. **Transition:** 7,267846 s.
11. **Intended visual target:** transition zaczyna się przy `1:36.665`, kończy
    przy `1:43.933` na 88/95/92%.
12. **Calculated command send time:** `1:36.828` — formuła dla początku
    transition; koniec zgrywa się dzięki długości 7,267846 s.
13. **Confidence:** wysoka dla idei fade, średnia dla sprzętowej krzywej.
14. **Manual tuning:** przetestować realny transition TS0503B/TS0505B_1;
    szczególnie jednoczesne rozjaśnianie i przejście `color_temp`.

### M12 — final white top-off

1. **Exact track timestamp:** `1:43.933`.
2. **Cue type:** ending.
3. **Musical reason:** granica końca treści i wejścia w bardzo cichy ogon.
4. **Spatial reason:** cichy ogon staje się przestrzenią na ostatnie, łagodne
   dojście całego pokoju do normalnego dnia.
5. **LED strip:** 88→100%, **native XY white** `[0.346, 0.359]` (D50 około
   5000 K); nie zakładamy osobnego kanału CCT/white.
6. **Near-bed bulb:** 95→100%, **natywny white mode / `color_temp`**, 5000 K.
7. **Far-room bulb:** 92→100%, **natywny white mode / `color_temp`**, 5000 K.
8. **Brightness:** wszystkie trzy źródła osiągają 100% dokładnie przy końcu
   kontenera `1:51.177`.
9. **Color:** neutralna/dzienna biel; żadnego bursztynu w stanie końcowym.
10. **Transition:** 7,244626 s.
11. **Intended visual target:** start przy `1:43.933`, koniec przy `1:51.177`.
12. **Calculated command send time:** `1:44.096`
    (`103,932517 + 0,163`); długość `111,177143 - 103,932517`.
13. **Confidence:** wysoka dla konstrukcji, średnia dla percepcyjnej liniowości.
14. **Manual tuning:** zweryfikować gamut taśmy dla XY D50 oraz rzeczywiste
    kończenie transition na urządzeniach; nie zastępować bieli żarówek RGB.

### M13 — reserved late Aqara wake signal

1. **Exact track timestamp:** `1:47.926`.
2. **Cue type:** accent.
3. **Musical reason:** ostatnia wykryta granica novelty (`107,926349 s`) w
   bardzo cichym ogonie; daje jednoznaczny finał bez naruszania climaxu.
4. **Spatial reason:** dopiero tutaj nagły obwód ON/OFF może powiedzieć „pora
   wstać”, gdy trzy światła dimmable są już prawie pełne.
5. **LED strip:** kontynuuje M12; modelowo około 95%.
6. **Near-bed bulb:** kontynuuje M12; modelowo około 98% / white mode.
7. **Far-room bulb:** kontynuuje M12; modelowo około 96% / white mode.
8. **Brightness:** bez nowej komendy dla dimmable; Aqara byłaby ON.
9. **Color:** bez zmiany — trwa neutralizacja do 5000 K / D50.
10. **Transition:** Aqara ON/OFF, brak fade.
11. **Intended visual target:** właściwa lampa pokojowa ON przy `1:47.926`.
12. **Calculated command send time:** warunkowo `1:48.089`
    (`107,926349 + 0,163`).
13. **Confidence:** wysoka dla timestampu, **nierozstrzygnięta dla encji**.
14. **Manual tuning:** `aqara_target: TBD`. Rejestr HA pokazuje jedynie
    `Left` i `Right`; przed implementacją trzeba ręcznie potwierdzić, czy
    lampę pokojową zasila `light.wlacznik_sypialnia_left`,
    `light.wlacznik_sypialnia_right`, czy oba. Dopóki tego nie wiadomo, cue
    nie może wysłać komendy do żadnego z nich.

### M14 — full-room invariant

1. **Exact track timestamp:** `1:51.177` (koniec kontenera).
2. **Cue type:** ending.
3. **Musical reason:** koniec pliku; audio domknęło historię.
4. **Spatial reason:** pokój jest już w normalnym trybie dziennym i pozostaje
   oświetlony po ciszy.
5. **LED strip:** hold ON, 100%, native XY white `[0.346, 0.359]`.
6. **Near-bed bulb:** hold ON, 100%, natywny white mode, 5000 K.
7. **Far-room bulb:** hold ON, 100%, natywny white mode, 5000 K.
8. **Brightness:** 100% / 100% / 100%.
9. **Color:** dzienna/neutralna biel; brak RGB-white na żarówkach i brak
   bursztynu na taśmie.
10. **Transition:** brak nowej komendy; M12 właśnie zakończył 7,244626 s ramp.
11. **Intended visual target:** invariant obowiązuje od `1:51.177` bez timeoutu.
12. **Calculated command send time:** brak; jest to kontrola stanu, nie cue
    wymagający dodatkowego ruchu ZigBee.
13. **Confidence:** wysoka dla trzech świateł dimmable.
14. **Manual tuning:** Aqara należy do invariantu wyłącznie po identyfikacji
    targetu; jeśli target pozostaje TBD, nie wolno włączać obu na ślepo.

## Dokładny przebieg od climaxu do końca

| Track time | LED strip | Near-bed / fotel | Far-room / szafa | Aqara |
|---:|---|---|---|---|
| `1:26.959` | 55%, pale gold XY | 70%, white mode 3600 K | 58%, white mode 3500 K | OFF / brak cue |
| `1:30.651` | 64%, warm-white XY | 80%, white mode 4200 K | 70%, white mode 4000 K | OFF / brak cue |
| `1:36.665` | start ramp z 64% | start ramp z 80% | start ramp z 70% | OFF / brak cue |
| `1:43.933` | 88%, near-white XY | 95%, white mode 4700 K | 92%, white mode 4600 K | nadal bez komendy |
| `1:47.926` | modelowo ~95% | modelowo ~98% | modelowo ~96% | warunkowe ON, `aqara_target: TBD` |
| `1:51.177` | **100%, D50 XY** | **100%, white mode 5000 K** | **100%, white mode 5000 K** | ON tylko po ręcznym mapowaniu |

Wartości pośrednie przy `1:47.926` są interpolacją modelu komendy. Faktyczna
krzywa jasności urządzeń może nie być liniowa percepcyjnie.

## Finalny invariant

Po `1:51.177` i bez limitu czasu:

- `light.zarowka_fotel`: **ON, 100%, `color_temp`/white mode, 5000 K**;
- `light.zarowka_szafa`: **ON, 100%, `color_temp`/white mode, 5000 K**;
- `light.tasma_lozko`: **ON, 100%, native XY `[0.346, 0.359]` jako biel**;
- lampa Aqara: **ON tylko po jednoznacznym wskazaniu targetu**; obecnie
  `aqara_target: TBD`, więc żaden kanał nie jest wybierany automatycznie;
- brak wygaszenia, cofnięcia do ambientu i komendy kończącej po muzyce.

## Micro cues

| Pattern | Sekcja i logika | Urządzenie | Base | Delta | Czas pulsu | Częstotliwość | Latency | Dlaczego subtelne |
|---|---|---|---:|---:|---:|---|---|---|
| P01 early downbeats | `0:26.610–0:45.627`, co 4 orientacyjne beaty | strip | 9–16% | +2 pp | 220 ms | ~0,673 cmd/s z powrotem | rise `beat+0,163`; return `+0,220` | mały ruch wyłącznie w świetle odbitym |
| P02 transient triptych | `0:51.873`, `0:54.126`, `0:57.864` | strip | 16–22% | +4 pp, M06 +5 pp | 200 ms | 3 pulsy / 6 s | rise `event+0,163`; return `+0,200` | tylko trzy największe ataki, bez bulb flash |
| P03 mid-build | `0:58.120–1:10.055`, co 4 beaty | strip | 22–30% | +3 pp | 180 ms | ~0,673 cmd/s | rise `beat+0,163`; return `+0,180` | powolny rytmiczny oddech, nie każdy beat |
| P04 climax | `1:12.887–1:27.888`, co 4 beaty | strip | 30–55% | +4 pp | 160 ms | ~0,673 cmd/s | rise `beat+0,163`; return `+0,160` | ostatni puls po climaxie; potem wyłącznie płynne rampy do stałej bieli |

Dokładne wybrane czasy znajdują się w `another_name_cues.yaml` i
`selected_cues.json`. Nie należy wykonywać osobno M06 i pierwszego eventu P02.

## Pięć najważniejszych momentów choreografii

1. **`0:26.610`** — pierwszy lokalny key light przy łóżku; budzik przestaje
   być wyłącznie ambientem.
2. **`0:45.627`** — pierwsze 2% dalekiej żarówki; pokój po raz pierwszy ma
   odczuwalną głębię.
3. **`0:51.873–0:57.864`** — trzy duże, ale strip-only akcenty prowadzą do
   wejścia mocnego dołu.
4. **`1:26.959–1:30.651`** — mocniejszy climax i daylight bridge, ale nadal
   bez 100% oraz bez nagłego Aqara.
5. **`1:36.665–1:51.177`** — kontrast finału: audio cichnie, podczas gdy cały
   pokój płynnie dochodzi do 100% neutralnej bieli; `1:47.926` jest
   zarezerwowane dla późnego Aqara po ręcznej identyfikacji.

Pełne dane maszynowe: [`another_name_cues.yaml`](another_name_cues.yaml).
