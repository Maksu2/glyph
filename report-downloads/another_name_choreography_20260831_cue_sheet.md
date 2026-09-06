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
- M00 wymaga ujemnego pre-rollu. M13 jest świadomym „hold” bez komendy.

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
| M09 | `1:26.959` | climax | kinetyczny szczyt koloru i bieli | `1:26.322` | 0,800 s |
| M10 | `1:30.651` | accent | opcjonalny Aqara circuit 1 ON | `1:30.814` | sharp |
| M11 | `1:33.716` | climax | opcjonalny Aqara circuit 2 ON | `1:33.879` | sharp |
| M12 | `1:36.665` | ending | start siedmiosekundowego morning settle | `1:36.828` | 7,268 s |
| M13 | `1:43.933` | ending | finalny stan pozostaje włączony | brak komendy | hold |

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
4. **Spatial reason:** szczyt filmowego koloru i głównego białego światła,
   jeszcze przed skokiem dużych obwodów.
5. **LED strip:** 30→42%, pale gold XY `[0.405, 0.385]`.
6. **Near-bed bulb:** 38→55%, 3400 K.
7. **Far-room bulb:** 22→42%, 3200 K.
8. **Brightness:** 42% / 55% / 42%.
9. **Color:** subtelnie chłodniejsze pale gold i cieple-neutralna biel.
10. **Transition:** 0,800 s.
11. **Intended visual target:** szczyt przy `1:26.959`.
12. **Calculated command send time:** `1:26.322`.
13. **Confidence:** wysoka.
14. **Manual tuning:** ocenić komfort 42% taśmy i 55% near-bed bezpośrednio z
    pozycji na poduszce.

### M10 — large light circuit 1

1. **Exact track timestamp:** `1:30.651`.
2. **Cue type:** accent.
3. **Musical reason:** ostry onset przy wejściu finalnej głośnej półki.
4. **Spatial reason:** tylko jeden duży obwód na raz zachowuje etapowość.
5. **LED strip:** hold 42% pale gold.
6. **Near-bed bulb:** hold 55% / 3400 K.
7. **Far-room bulb:** hold 42% / 3200 K.
8. **Brightness:** bez zmian na światłach dimmable.
9. **Color:** bez zmian.
10. **Transition:** Aqara ON/OFF, brak płynnego transition.
11. **Intended visual target:** circuit 1 widoczny ON przy `1:30.651`.
12. **Calculated command send time:** `1:30.814`.
13. **Confidence:** średnio-niska; cue opcjonalny.
14. **Manual tuning:** ustalić fizyczny obwód `left` i ocenić agresywność;
    można całkowicie pominąć.

### M11 — large light circuit 2

1. **Exact track timestamp:** `1:33.716`.
2. **Cue type:** climax.
3. **Musical reason:** orientacyjny downbeat w drugim wzroście końcowej półki.
4. **Spatial reason:** po około trzech sekundach drugi obwód domyka całe
   pomieszczenie.
5. **LED strip:** hold 42%.
6. **Near-bed bulb:** hold 55% / 3400 K.
7. **Far-room bulb:** hold 42% / 3200 K.
8. **Brightness:** bez zmian dimmable; drugi Aqara ON.
9. **Color:** bez zmian.
10. **Transition:** ON/OFF.
11. **Intended visual target:** circuit 2 ON przy `1:33.716`.
12. **Calculated command send time:** `1:33.879`.
13. **Confidence:** niska; cue opcjonalny.
14. **Manual tuning:** najważniejszy punkt do korekty odsłuchowej; sprawdzić
    mapping `right` i rozważyć pominięcie.

### M12 — morning settle

1. **Exact track timestamp:** `1:36.665`.
2. **Cue type:** ending.
3. **Musical reason:** downbeat wypada przy początku gwałtownego, trwałego
   spadku RMS.
4. **Spatial reason:** muzyczna taśma uspokaja się, a dwie żarówki stają się
   właściwym światłem porannym.
5. **LED strip:** 42→24%, final gold XY `[0.455, 0.410]`.
6. **Near-bed bulb:** 55→72%, 3800 K.
7. **Far-room bulb:** 42→68%, 3600 K.
8. **Brightness:** strip spada, obie białe żarówki rosną.
9. **Color:** użyteczna ciepło-neutralna biel; strip wraca do spokojnego złota.
10. **Transition:** 7,267846 s.
11. **Intended visual target:** transition zaczyna się przy `1:36.665`, kończy
    dokładnie przy `1:43.933`.
12. **Calculated command send time:** `1:36.828` — formuła dla początku
    transition; koniec zgrywa się dzięki długości 7,267846 s.
13. **Confidence:** wysoka dla idei fade, średnia dla sprzętowej krzywej.
14. **Manual tuning:** przetestować realny transition TS0503B/TS0505B_1;
    Aqara pozostają w poprzednim stanie.

### M13 — hold final

1. **Exact track timestamp:** `1:43.933`.
2. **Cue type:** ending.
3. **Musical reason:** granica końca treści i wejścia w bardzo cichy ogon.
4. **Spatial reason:** budzik kończy się użytecznym światłem, nie blackoutem.
5. **LED strip:** hold 24%, XY `[0.455, 0.410]`.
6. **Near-bed bulb:** hold 72%, 3800 K.
7. **Far-room bulb:** hold 68%, 3600 K.
8. **Brightness:** bez zmian.
9. **Color:** bez zmian.
10. **Transition:** brak.
11. **Intended visual target:** finalna scena pozostaje aktywna po końcu.
12. **Calculated command send time:** brak — świadomie nie wysyłamy zbędnego
    idempotentnego reassertion.
13. **Confidence:** wysoka.
14. **Manual tuning:** zaakceptować osobno wariant z Aqara oraz bez Aqara.

## Micro cues

| Pattern | Sekcja i logika | Urządzenie | Base | Delta | Czas pulsu | Częstotliwość | Latency | Dlaczego subtelne |
|---|---|---|---:|---:|---:|---|---|---|
| P01 early downbeats | `0:26.610–0:45.627`, co 4 orientacyjne beaty | strip | 9–16% | +2 pp | 220 ms | ~0,673 cmd/s z powrotem | rise `beat+0,163`; return `+0,220` | mały ruch wyłącznie w świetle odbitym |
| P02 transient triptych | `0:51.873`, `0:54.126`, `0:57.864` | strip | 16–22% | +4 pp, M06 +5 pp | 200 ms | 3 pulsy / 6 s | rise `event+0,163`; return `+0,200` | tylko trzy największe ataki, bez bulb flash |
| P03 mid-build | `0:58.120–1:10.055`, co 4 beaty | strip | 22–30% | +3 pp | 180 ms | ~0,673 cmd/s | rise `beat+0,163`; return `+0,180` | powolny rytmiczny oddech, nie każdy beat |
| P04 climax | `1:12.887–1:27.888`, co 4 beaty | strip | 30–42% | +4 pp | 160 ms | ~0,673 cmd/s | rise `beat+0,163`; return `+0,160` | krótka seria tylko w pełnym buildzie; koniec przed Aqara |

Dokładne wybrane czasy znajdują się w `another_name_cues.yaml` i
`selected_cues.json`. Nie należy wykonywać osobno M06 i pierwszego eventu P02.

## Pięć najważniejszych momentów choreografii

1. **`0:26.610`** — pierwszy lokalny key light przy łóżku; budzik przestaje
   być wyłącznie ambientem.
2. **`0:45.627`** — pierwsze 2% dalekiej żarówki; pokój po raz pierwszy ma
   odczuwalną głębię.
3. **`0:51.873–0:57.864`** — trzy duże, ale strip-only akcenty prowadzą do
   wejścia mocnego dołu.
4. **`1:26.959–1:33.716`** — climax, jaśniejsza biel i dwa opcjonalne stopnie
   dużego światła.
5. **`1:36.665–1:43.933`** — strip uspokaja się, żarówki dochodzą do stałego
   światła porannego; nic nie gaśnie po utworze.

Pełne dane maszynowe: [`another_name_cues.yaml`](another_name_cues.yaml).
