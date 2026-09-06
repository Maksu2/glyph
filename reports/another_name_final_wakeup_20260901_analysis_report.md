# „Another Name” — analiza audio i koncepcja światła

Status: **wyłącznie analiza i projekt / brak aktywnej automatyzacji**  
Data analizy: 2026-08-31 UTC  
Katalog: `/home/maksu/audio-alarm-lab/analysis/another-name/`

W tej pracy nie wysłano żadnego polecenia do światła, nie odtworzono utworu,
nie zmieniono konfiguracji Home Assistant i nie utworzono harmonogramu,
automatyzacji, timera ani usługi uruchamiającej muzykę.

## Zaktualizowany wynik projektu

Choreografia zachowuje ciemny, filmowy początek i muzyczną rolę taśmy, lecz
nie uspokaja już światła razem z końcowym fade'em. Climax przy `1:26.959`
osiąga 55/70/58%, po czym od `1:36.665` pokój przechodzi ciągłą, dwustopniową
rampą do **100% neutralnej bieli dokładnie przy `1:51.177`**. Obie żarówki
używają natywnego `color_temp` przy 5000 K, a taśma — jedynej raportowanej
metody bieli, czyli XY `[0.346, 0.359]`. Kanał dodatkowej lampy Aqara pozostaje
`TBD`; zarezerwowany moment `1:47.926` nie jest wykonywalnym poleceniem do
czasu ręcznej identyfikacji obwodu.

## Potwierdzony plik

Plik został zaakceptowany dopiero po porównaniu tagów i parametrów strumienia,
nie na podstawie samej nazwy.

| Pole | Wartość |
|---|---|
| Ścieżka | `/home/maksu/.codex/attachments/c4da231d-7fd9-4dc9-baae-2a1f42a58225/Another Name.mp3` |
| SHA-256 | `d0311089770db56dd4d7d9d2049c0b980a57ea4f921f8aca29504b354cef8008` |
| Tytuł | Another Name |
| Artysta | Ludwig Göransson |
| Album | The Odyssey (Original Motion Picture Soundtrack) |
| Rok w tagu | 2026 |
| Długość według kontenera | 111,177143 s (`1:51.177`) |
| Długość zdekodowanych próbek | 111,130703 s (`1:51.131`) |
| Codec | MP3 / MPEG Audio Layer III |
| Bitrate strumienia | 320 000 bit/s |
| Bitrate kontenera | 320 092 bit/s |
| Sample rate | 44 100 Hz |
| Kanały | 2, stereo |
| Start time strumienia | 25,057 ms |

Pełny wynik `ffprobe` i znormalizowane metadane są w
[`audio_metadata.json`](audio_metadata.json).

## Metoda

Na hoście nie było `ffmpeg`, `ffprobe`, `librosa` ani `soundfile`. Nie
instalowano nowych dużych zależności. Do samego, odłączonego od sieci
dekodowania wykorzystano istniejący lokalnie obraz Jellyfin z jego
`ffmpeg/ffprobe`; wejście zamontowano read-only. Analiza używała obecnych już
NumPy, SciPy i Matplotlib.

Utwór zdekodowano analitycznie do mono, float32, 22 050 Hz. Nie otwierano
ALSA/PulseAudio i nie przekazano sygnału do Sony SRS-XB33. Obliczono:

- waveform min/max;
- RMS co 23,22 ms oraz wygładzoną obwiednię 1,5 s;
- STFT 2048 próbek / hop 512;
- spectral-flux onset strength i lokalne transienty;
- centroid widmowy oraz udziały pasma niskiego, średniego i wysokiego;
- 12-klasowe chroma;
- autokorelację onset envelope, beat grid i orientacyjną fazę downbeatów;
- wielowymiarową novelty: różnicę średnich cech w oknach 2,5 s po obu stronach
  badanego punktu.

Algorytm dostarczył kandydatów, ale finalny cue sheet został zredagowany po
wizualnym porównaniu waveformu, RMS, onsetów, widma i przestrzennej funkcji
lamp. Nie skopiowano automatycznie wszystkich granic ani 212 transientów.

## Dynamika i makrostruktura

Przybliżony zintegrowany RMS dekodu wynosi `-9,90 dBFS`. Float decode pokazuje
rekonstrukcyjne overshooty MP3 powyżej 0 dBFS; nie normalizowano ich, ponieważ
analiza względnych zmian nie wymaga modyfikacji pliku źródłowego.

Najważniejsza cecha przebiegu to długi, kontrolowany wzrost:

- do około `0:54` średni RMS sekcji pozostaje w pobliżu `-12 do -11 dBFS`;
- `0:54–1:11.8` rośnie do około `-9,2 dBFS` i wyraźnie wzmacnia dół;
- `1:11.8–1:30.4` osiąga około `-7,3 dBFS` oraz najwyższą regularną aktywność
  onsetów;
- absolutnie najgłośniejsze dwusekundowe okno wypada około `1:34–1:36`;
- od około `1:36.7` zaczyna się zdecydowany spadek, a po `1:43.933` pozostaje
  głównie ogon i prawie cisza.

### Wybrane sekcje

| Zakres | Nazwa robocza | Evidence | Konsekwencja świetlna |
|---|---|---|---|
| `0:00.000–0:14.652` | restrained opening | Niski, stabilny RMS; słaba aktywność transientów | Tylko 2–5% taśmy wokół łóżka |
| `0:14.652–0:26.610` | early development | Zmiana harmoniczno-widmowa bez dużego skoku głośności | Nadal bez żarówek; cieplejszy glow |
| `0:26.610–0:39.869` | rhythmic lift | Wzrost RMS, centroidu i czytelności onsetów | Pierwsze 3–8% żarówki przy łóżku; lekkie pulsy taśmy |
| `0:39.869–0:45.627` | tension opening | Silna novelty i większa definicja transientów | Taśma 13–16%, near key 8–12% |
| `0:45.627–0:54.381` | pre-build / transient gate | Najsilniejsza granica przed serią uderzeń | Pierwsze 2% dalekiej żarówki; przestrzeń zaczyna się otwierać |
| `0:54.381–1:11.819` | bass/rhythm expansion | Skok energii niskiego pasma i gęstości onsetów | Obie żarówki widoczne, lecz near-bed pozostaje jaśniejsza |
| `1:11.819–1:26.959` | full build | Low-band ratio około 0,74; RMS i rytm stale rosną | Pokój otwarty; taśma wciąż prowadzi muzycznie |
| `1:26.959–1:30.651` | kinetic climax | Maksimum złożonego energy/onset/spectral score | Wyraźny szczyt 55/70/58%; ostatni puls taśmy, ale jeszcze nie 100% |
| `1:30.651–1:36.665` | final plateau | Głośna końcowa półka i drugi wzrost około 1:34–1:36 | Daylight bridge do 64/80/70%, nadal bez nagłego Aqara |
| `1:36.665–1:43.933` | release / wake-up ramp | Szybki, ciągły spadek RMS | Wbrew muzycznemu wyciszeniu wszystkie światła rosną do 88/95/92% i neutralizują barwę |
| `1:43.933–1:51.177` | tail / final white top-off | RMS spada od około -40 do -80 dBFS; ostatnia novelty `1:47.926` | Płynne dojście do 100% bieli; `1:47.926` rezerwuje warunkowy Aqara ON |

Granice `0:08.522`, `0:14.652`, `0:26.610`, `0:39.869`, `0:45.627`,
`0:54.381`, `1:11.819`, `1:30.395`, `1:43.933` i `1:47.926` pochodzą z
feature novelty. Punkt `1:26.959` pochodzi z maksimum złożonej energii, a
`1:36.665` został wybrany redakcyjnie jako downbeat przy faktycznym początku
gwałtownego spadku RMS.

## Tempo i mikro-rytm

Najsilniejsza globalna periodyczność wynosi **80,7495 BPM**, czyli jeden beat
co około **743,04 ms**. Autokorelacja `0,834` i grid-alignment z-score `2,095`
dają wysoką pewność samego pulsu. Słabsze kandydatury to około `112,35 BPM` i
`63,02 BPM`.

Faza downbeatów w grupach po cztery ma tylko średnią pewność. Bez separacji
stemów i kontrolowanego odsłuchu nie należy nazywać jej pewnym metrum. Dlatego:

- cue sheet używa głównie **co czwartego** orientacyjnego beatu;
- regularna seria daje jeden puls co około `2,972 s`;
- jeden puls to wzrost i powrót, czyli średnio około `0,673` komendy ZigBee/s;
- żarówki i Aqara nie dostają mikro-cue;
- ostatni mikro-cue wypada przy `1:27.888`, a potem choreografia przechodzi w
  stałe rampy jasności bez pulsów;
- osobno zachowano trzy bardzo silne transienty: `0:51.873`, `0:54.126` i
  `0:57.864`.

Wykryto 212 lokalnych transientów, ale do projektu wybrano tylko 20 punktów.
To świadome filtrowanie chroni estetykę przed efektem RGB disco i ogranicza
ruch w sieci ZigBee.

## Inwentaryzacja świateł

Home Assistant i Zigbee2MQTT sprawdzono wyłącznie odczytowo.

| Rola | Entity | Wykryte możliwości | Rola w choreografii |
|---|---|---|---|
| Taśma przy łóżku | `light.tasma_lozko` | brightness, kolor XY; Tuya `TS0503B` | Główna muzyczna warstwa, amber/gold i małe pulsy |
| Żarówka przy fotelu | `light.zarowka_fotel` | brightness, XY, 2000–6535 K; user: EMOS, converter: Tuya `TS0505B_1` | Pierwszy lokalny key light, zawsze jaśniejszy wcześniej |
| Żarówka na szafie | `light.zarowka_szafa` | brightness, XY, 2000–6535 K; user: EMOS, converter: Tuya `TS0505B_1` | Późny room fill otwierający drugą stronę pokoju |
| Kandydat Aqara 1 | `light.wlacznik_sypialnia_left` | friendly/original name `Left`; wyłącznie ON/OFF; Aqara `WS-EUK02` | Nierozstrzygnięty kandydat do późnego sygnału pobudki |
| Kandydat Aqara 2 | `light.wlacznik_sypialnia_right` | friendly/original name `Right`; wyłącznie ON/OFF; Aqara `WS-EUK02` | Nierozstrzygnięty kandydat do późnego sygnału pobudki |

`light.swiatla_kolor_sypialnia` jest grupą trzech kolorowych lamp i celowo nie
jest używana. Jedna komenda grupowa zniszczyłaby asymetrię: łóżko → fotel →
druga strona pokoju.

Rejestry nie dowodzą czasu wykonania `transition`. Cue sheet zakłada tę
możliwość, ale rzeczywista krzywa każdej lampy wymaga późniejszego,
nadzorowanego testu. Wbudowane efekty `blink` i `breathe` nie zostały wybrane,
ponieważ ich timing jest mniej kontrolowalny niż jawne poziomy jasności.

Rejestr encji nie ma nazw użytkownika pozwalających rozróżnić fizyczne obwody
Aqara: widoczne są wyłącznie `Left` i `Right` tego samego podwójnego
włącznika. Istniejące wcześniej skrypty oraz automatyzacja o aliasie
`Uruchamianie dużego światła o 6:00` kierują akcję do **obu** kanałów naraz.
To jest wskazówka, że razem były traktowane jako „duże światło”, ale nie jest
dowodem, który kanał zasila właściwą lampę. Istniejącej automatyzacji nie
utworzono, nie zmieniono i nie uruchomiono podczas tej pracy.

## Decyzja przestrzenna i kolorystyczna

Taśma pracuje mocniej muzycznie, bo świeci w podłogę i ścianę, a nie prosto w
oczy. Zaczyna na 2% w głębokim bursztynie, rośnie do 55% w jaśniejszym złocie
przy climaxie, a następnie — już bez pulsów — dochodzi do 100% bieli. Ponieważ
HA raportuje dla niej XY, a nie `color_temp`, finalna biel jest zadana natywnym
XY `[0.346, 0.359]` (aproksymacja D50/około 5000 K), bez zakładania osobnego
kanału CCT/white. Pulsy mają tylko `+2`, `+3` lub `+4` punkty procentowe i nigdy
nie są pełnym ON/OFF.

Żarówka przy łóżku pojawia się pierwsza (`0:26.610`). Daleka żarówka dopiero
przy `0:45.627`, dlatego pokój otwiera się w przestrzeni, zamiast tylko robić
się równomiernie jaśniejszy. Obie używają głównie trybu białego z temperaturą,
bo użytkownik potwierdził, że ten tryb daje znacznie lepsze światło pokojowe
niż RGB. Temperatura przechodzi od 2200–2500 K do 3500–3600 K w kulminacji,
4200/4000 K przy wejściu finalnej półki i finalnie do **5000 K przy 100%** dla
obu żarówek. W YAML jest to jawnie zapisane jako `color_mode: color_temp` oraz
`native_white_mode_required: true`, a nie jako RGB udające biel.

Dwa kanały Aqara są wyłącznie ON/OFF, a ich fizyczne mapowanie pozostaje
niejednoznaczne. Projekt rezerwuje dla zidentyfikowanej lampy moment
`1:47.926`: to ostatnia wykryta granica novelty w prawie cichym ogonie. Dzięki
temu skok nie psuje wcześniejszej filmowej części, ale staje się jasnym sygnałem
„pora wstać”. Do czasu ręcznej identyfikacji obowiązuje `aqara_target: TBD`,
więc ten cue ma jawne `no_command` i nie wybiera żadnego kanału na ślepo.

### Finalny wake-up ramp i invariant

Od climaxu światło przechodzi następująco:

| Track time | Taśma | Fotel | Szafa | Znaczenie |
|---:|---:|---:|---:|---|
| `1:26.959` | 55% | 70% / 3600 K | 58% / 3500 K | wyraźny, lecz niepełny climax |
| `1:30.651` | 64% | 80% / 4200 K | 70% / 4000 K | daylight bridge |
| `1:36.665` | start z 64% | start z 80% | start z 70% | audio cichnie, światło nadal rośnie |
| `1:43.933` | 88% | 95% / 4700 K | 92% / 4600 K | początek cichego ogona |
| `1:47.926` | modelowo ~95% | ~98% | ~96% | zarezerwowany Aqara ON po identyfikacji |
| `1:51.177` | **100% white XY** | **100% / white mode 5000 K** | **100% / white mode 5000 K** | obowiązujący stan końcowy |

Po końcu kontenera trzy światła dimmable pozostają ON przy 100%; nie ma
blackoutu, cofnięcia do ambientu ani komendy kończącej. Aqara jest częścią
invariantu wyłącznie po jednoznacznym mapowaniu właściwego obwodu.

## Model latency

Przyjęte wartości:

- audio end-to-end: `243 ms`;
- ZigBee light: `80 ms`;
- ostry cue: `+163 ms` od track event do wysłania komendy względem chwili
  wydania polecenia startu audio.

Dla ostrego cue:

```text
send = track_event + 0.243 - 0.080 = track_event + 0.163 s
```

Dla transition kończącego się na wydarzeniu muzycznym:

```text
send = visual_target_track_time + 0.163 s - transition_duration
```

Dla transition, którego początek ma pokrywać się z muzyką:

```text
send = transition_start_track_time + 0.163 s
```

Początkowe 2% taśmy wymaga pre-rollu `-1,837 s`, jeśli dwusekundowy transition
ma zakończyć się dokładnie na pierwszej próbce. To jest wyłącznie wpis
projektowy, nie timer ani aktywna logika.

MP3 raportuje start time `25,057 ms`. Obecny model tego osobno nie koryguje,
zgodnie z poleceniem użytkownika. Przy późniejszej implementacji należy
sprawdzić właściwy program odtwarzający lub użyć przygotowanego PCM/WAV, aby
zegar cue i dekoder miały jednoznaczny początek.

## Punkty wymagające ręcznej korekty

1. Faza downbeatu dla micro-cue; późny Aqara nie zależy już od orientacyjnego
   downbeatu.
2. Percepcyjna granica `0:14.652`, która może wymagać przesunięcia o około
   `±0,5 s`.
3. Minimalny stabilny poziom białego trybu obu żarówek przy 2–3%.
4. Realny przebieg `transition` dla TS0503B i obu TS0505B_1.
5. Fizyczne przypisanie Aqara `left/right`: ręcznie ustalić, czy właściwą
   lampę zasila lewy, prawy czy oba kanały; dopiero potem zastąpić `TBD`.
6. Rzeczywista biel taśmy dla XY `[0.346, 0.359]` i jej gamut; nie zakładać
   niezgłoszonego kanału CCT/white.
7. Czy transition rozpoczęty `1:43.933` rzeczywiście kończy się na 100% przy
   `1:51.177`; finalnej jasności nie wolno później obniżyć.
8. Model `+163 ms` z docelowym programem odtwarzającym ten MP3.

## Wykresy

### Zbiorczy przegląd z cue

![Zbiorczy wykres struktury i cue](analysis_overview.png)

Zbiorczy wykres został odświeżony dla cue v2: `brighter climax`, `daylight
bridge`, `wake-up ramp`, `white top-off`, warunkowy `Aqara TBD` i końcowy
`100% invariant`. Pozostałe wykresy zachowują pierwotne warstwy analityczne;
aktualnym źródłem prawdy dla choreografii jest `another_name_cues.yaml`.

### Waveform

![Waveform](waveform.png)

### RMS / loudness

![RMS loudness](loudness.png)

### Onset strength

![Onset strength](onset.png)

### Beat grid

![Beat grid](beat_grid.png)

### Spectrogram

![Spectrogram](spectrogram.png)

## Pliki pomocnicze

- [`analysis_summary.json`](analysis_summary.json) — statystyki i kandydaci;
- [`analysis_frames.csv`](analysis_frames.csv) — cechy w czasie;
- [`section_candidates.csv`](section_candidates.csv) — novelty boundaries;
- [`onsets.csv`](onsets.csv) — transienty;
- [`beat_grid.csv`](beat_grid.csv) — beaty i orientacyjne downbeaty;
- [`ha_lights_inventory.json`](ha_lights_inventory.json) — odczytowe capabilities;
- [`selected_cues.json`](selected_cues.json) — pierwotne adnotacje analityczne;
  aktualne cue v2 są w YAML i na zbiorczym overview;
- [`another_name_cues.yaml`](another_name_cues.yaml) — neutralny model danych;
- [`cue_sheet.md`](cue_sheet.md) — pełna choreografia do akceptacji;
- [`analyze_another_name.py`](analyze_another_name.py) — reprodukowalny skrypt.

Żaden z tych plików sam niczego nie uruchamia.
