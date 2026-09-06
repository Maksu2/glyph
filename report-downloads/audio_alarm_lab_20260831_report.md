# Tor audio budzika — raport końcowy

Data testu: 2026-08-31 UTC  
Host: `maxoo-pc`  
Zakres: Bluetooth, mikrofon jack 3,5 mm i pomiar opóźnienia akustycznego.  
Home Assistant nie był konfigurowany.

## Wynik w skrócie

- Sony SRS-XB33 jest sparowany, zaufany i połączony przez A2DP.
- Aktywny kodek odtwarzania to `ldac_hq`; głośność ustawiono na 70%, bez mute.
- Realtek ALC892 i przedni jack mikrofonowy są wykrywane.
- Mikrofon Mad Dog działa przy 48 kHz; wejście jest dwukanałowe, ale oba kanały
  zawierają praktycznie ten sam sygnał mono.
- Gain sprzętowy Capture ustawiono na +8,00 dB (52%), a Front Mic Boost
  pozostawiono na 0,00 dB.
- W głównym teście wykryto automatycznie wszystkie 24 z 24 impulsów.
- Mediana zmierzonego opóźnienia end-to-end wynosi 243,221 ms, p95 262,293 ms.
- Zalecany początkowy offset do późniejszej synchronizacji światła to 240 ms:
  polecenie audio w chwili 0, światło około 240 ms później.

## 1. Preflight i wykonane zmiany

System:

- Ubuntu 24.04.4 LTS, kernel `6.8.0-138-generic`.
- Płyta MSI B450 GAMING PLUS MAX (`MS-7B86`).
- Istniejący stos audio: PulseAudio 16.1.
- PipeWire, `pipewire-pulse`, WirePlumber i `wpctl` nie są zainstalowane.
- Nie migrowano ani nie reinstalowano stosu audio.

Bluetooth:

- Adapter: Intel Wireless-AC 9260, kontroler `hci0`.
- MAC kontrolera: `CC:D9:AC:3D:8F:82`.
- `bluetooth.service` był wyłączony; teraz jest `enabled` i `active`.
- Adapter był programowo zablokowany przez rfkill; blokadę zdjęto.

Realtek:

- Funkcja PCI kontrolera onboard była wcześniej wyłączona w UEFI i przez to
  nie pojawiała się nawet w `lspci`.
- Po włączeniu `HD Audio Controller` pojawił się kontroler AMD
  `0000:2a:00.4 [1022:1487]`, sterownik `snd_hda_intel`, kodek Realtek ALC892.
- Zainstalowano brakujące `alsa-utils` i `rfkill`.
- Użytkownika `maksu` dodano do grupy `audio`. Dla bieżącej, już uruchomionej
  sesji ustawiono tymczasowe ACL urządzeń Realtek; po następnym pełnym
  logowaniu/reboocie członkostwo grupy powinno działać bez tych ACL.
- Stan miksera zapisano przez `alsactl store 1` w
  `/var/lib/alsa/asound.state`.

Pełny stan sprzed zmian znajduje się w `preflight-2026-08-31.md`.

## 2. Głośnik Bluetooth

| Pole | Wartość |
|---|---|
| Nazwa | SRS-XB33 |
| MAC | `04:21:44:06:6B:B9` |
| Stan BlueZ | paired, bonded, trusted, connected |
| PulseAudio card | `bluez_card.04_21_44_06_6B_B9` |
| PulseAudio sink | `bluez_sink.04_21_44_06_6B_B9.a2dp_sink` |
| Profil | `a2dp_sink` — High Fidelity Playback |
| Kodek | `ldac_hq` |
| Format sinka | `float32le`, 2 kanały, 44,1 kHz |
| Głośność testowa/końcowa | 70% (`-9,26 dB` według PulseAudio), mute off |
| Bateria podczas końcowej kontroli | około 70% |

Nie ustawiano celowo globalnego wyjścia przez `pactl set-default-sink`.
Odtwarzanie można kierować do tego konkretnego sinka per proces.

Po ręcznym `disconnect` ponowne `connect` przywróciło ten sam sink, profil A2DP
i kodek LDAC HQ. Podczas serii około 172 sekund z siedmiosekundowymi przerwami
oraz osobnego testu po 65 sekundach pełnej ciszy połączenie pozostało aktywne.

Komendy:

```sh
bluetoothctl connect 04:21:44:06:6B:B9
pactl set-card-profile bluez_card.04_21_44_06_6B_B9 a2dp_sink
pactl set-sink-volume bluez_sink.04_21_44_06_6B_B9.a2dp_sink 70%

paplay --device=bluez_sink.04_21_44_06_6B_B9.a2dp_sink /ścieżka/alarm.wav

PULSE_SINK=bluez_sink.04_21_44_06_6B_B9.a2dp_sink \
  dowolny-program-audio [argumenty]
```

Gotowe pomocniki:

```sh
/home/maksu/audio-alarm-lab/connect_srs_xb33.sh
/home/maksu/audio-alarm-lab/run_on_srs_xb33.sh paplay /ścieżka/alarm.wav
```

## 3. Mikrofon jack 3,5 mm

| Pole | Wartość |
|---|---|
| Kodek | Realtek ALC892 |
| ALSA card | `1: Generic [HD-Audio Generic]` |
| Właściwe capture PCM | `hw:1,0` — ALC892 Analog |
| Dodatkowe capture PCM | `hw:1,2` — ALC892 Alt Analog |
| PulseAudio source | `alsa_input.pci-0000_2a_00.4.analog-stereo` |
| Aktywny port | `analog-input-front-mic` / Front Microphone |
| Parametry testu | PCM signed 16-bit LE, 2 kanały, 48 000 Hz |
| Capture | 24/46, 52%, +8,00 dB, oba kanały włączone |
| Front Mic Boost | 0/3, 0%, 0,00 dB |
| Input Source | Front Mic |

Detekcja jacka rozróżnia porty poprawnie: przedni mikrofon jest `available`,
rear mic oraz line-in są `not available`.

Nagranie testowe przy 48 kHz jest poprawnym WAV-em i nie zawiera clippingu.
Korelacja lewego i prawego kanału wyniosła około 0,9999, więc mikrofon jest
mono powielonym przez wejście stereo. Skrypt pomiarowy uśrednia kanały do mono
przed filtracją i matched-correlation; nie traktuje ich jako dwóch niezależnych
mikrofonów.

Surowe pierwsze nagranie:

```text
/home/maksu/audio-alarm-lab/artifacts/2026-08-31/mic_front_48k_initial.wav
```

Kontrola miksera:

```sh
amixer -c 1 sget Capture
amixer -c 1 sget 'Front Mic Boost'
amixer -c 1 sget 'Input Source'
```

## 4. Metoda pomiaru latency

Skrypt generuje 12-ms marker typu chirp z oknem Hanna (1,5–9 kHz), zapisany
w 40-ms pliku WAV. Dla każdego pomiaru:

1. `parecord` prowadzi jedno ciągłe nagranie raw PCM z mikrofonu przy 48 kHz,
   stereo, z żądaniem `--latency-msec=10 --process-time-msec=5`.
2. Skrypt zapisuje `time.monotonic_ns()` bezpośrednio przed uruchomieniem
   osobnego procesu `paplay` skierowanego do dokładnego sinka Bluetooth.
3. Marker jest wyszukiwany automatycznie w nagraniu po filtracji pasmowej i
   znormalizowanej korelacji dopasowanej.
4. Chwile próbek nagrania są mapowane na zegar monotoniczny z małych odczytów
   PCM; wykorzystano piąty percentyl różnicy końca odczytu i nominalnego czasu
   ramki, aby ograniczyć wpływ opóźnienia planisty klienta.

Główna seria: 24 impulsy, przerwa 7 s, warm-up 8 s, tail 3 s, amplituda pliku
0,40, głośnik 70%. Wszystkie procesy `paplay` zakończyły się kodem 0, a wszystkie
markery przeszły walidację.

## 5. Wyniki latency

To jest **measured end-to-end acoustic latency including microphone/capture
path** — zmierzone opóźnienie akustyczne end-to-end uwzględniające tor
mikrofonu i przechwytywania.

| Metryka | Wynik |
|---|---:|
| Liczba poprawnych prób | 24 / 24 |
| Minimum | 213,656 ms |
| Mediana | 243,221 ms |
| Średnia | 243,224 ms |
| p95 | 262,293 ms |
| Maksimum | 300,752 ms |
| Jitter — odchylenie standardowe próby (`ddof=1`) | 17,876 ms |
| Jitter peak-to-peak | 87,097 ms |

Jakość detekcji:

- mediana SNR markera: około 22,1 dB;
- korelacja dopasowania: 0,774–0,829;
- poziom wykrytych markerów: około -43,4 dBFS, stabilny między próbami;
- brak próbek z clippingiem;
- rozrzut p05–p95 kotwic mapowania czasu capture: 0,328 ms.

Osobny test po 65 sekundach ciszy dał 233,753 ms; głośnik pozostał połączony,
a odtwarzanie zadziałało bez ręcznej interwencji.

### Co dokładnie obejmuje wynik

Początek: wywołanie `time.monotonic_ns()` bezpośrednio przed utworzeniem
procesu `paplay`.

Koniec: znaleziony marker akustyczny dostarczony przez ciągły capture
`parecord`.

W środku są: start procesu, PulseAudio output, BlueZ/A2DP, transmisja radiowa,
bufor i DSP głośnika, propagacja akustyczna, mikrofon, analogowy preamp, ADC,
ALSA/PulseAudio capture oraz dostarczenie próbek do klienta.

### Latencja wejściowa i ograniczenie kalibracji

Podczas głównego testu PulseAudio raportował dla aktywnego source żądaną
latencję 10 000 µs, a chwilowe wartości około 670, 696, 679 i 2784 µs.
To nie obejmuje w sposób wiarygodny całej analogowej i przetwornikowej części
toru mikrofonowego. Inny klient bez małego żądania latency dostał znacznie
większy bufor ALSA/PulseAudio, co pokazuje, że nie istnieje jedna stała wartość,
którą można bezpiecznie odjąć.

Nie odjęto więc żadnego „input offsetu” i wynik nie jest nazywany czystą
latencją Bluetooth. Bez dodatkowego wspólnego odniesienia elektrycznego nie ma
wiarygodniejszej metody absolutnego rozdzielenia tych składników. Nagrywanie
monitora sinka obok mikrofonu nadal pozostawia różne zegary, resampling i
nieznaną latencję ADC.

Lepsza kalibracja absolutna wymagałaby dwukanałowego interfejsu/wejścia z
jednym kanałem nagrywającym elektryczny sygnał odniesienia i drugim kanałem
mikrofonowym w tym samym zegarze ADC (ewentualnie oscyloskopu). Nie wdrażano
tego, ponieważ takiego sprzętu nie ma w podanym zakresie sesji.

## 6. Offset do późniejszej synchronizacji

Zalecany punkt startowy: **240 ms** — najpierw zlecić odtwarzanie, następnie
po około 240 ms uruchomić zmianę świateł. To zaokrąglenie mediany i średniej.

Jeżeli priorytetem jest, aby światło prawie nigdy nie wyprzedziło dźwięku,
można użyć około 260 ms (p95), kosztem tego, że zwykle światło pojawi się
kilkanaście milisekund po dźwięku. Praktyczny zakres strojenia to 230–250 ms.
Tor wejściowy zawyża zmierzoną wartość względem samego outputu o nieznaną,
prawdopodobnie niewielką wartość, więc 240 ms należy później sprawdzić na
docelowym alarmie.

## 7. Stabilność do codziennego budzika

Linuxowa część zestawu jest wystarczająco stabilna: usługa Bluetooth startuje
automatycznie, urządzenie jest trusted/bonded, ponowne połączenie działa
jednoznacznym poleceniem, A2DP i LDAC HQ wracają po reconnect, a routing może
być wykonany per proces.

Pozostaje ograniczenie samego Sony: Auto Standby może wyłączyć SRS-XB33 po
około 15 minutach bezczynności. Do budzika głośnik powinien być zasilany z USB
i mieć w aplikacji Sony Music Center włączone `Bluetooth Standby`, albo należy
wyłączyć `Auto Standby`. Według instrukcji Sony Bluetooth Standby działa tylko
przy zasilaniu przez USB AC; na samej baterii nie zapewnia pewnego wybudzenia.

Źródła producenta:

- https://helpguide.sony.net/speaker/srs-xb33/v1/en/contents/TP0002741484.html
- https://helpguide.sony.net/speaker/srs-xb33/v1/en/contents/TP0002741512.html

Po następnym restarcie warto wykonać jedną kontrolę `arecord -l` oraz
`pactl list short sources`, aby potwierdzić trwałe prawa grupy `audio`.

## 8. Zachowane pliki

Główne pliki:

```text
/home/maksu/audio-alarm-lab/report-2026-08-31.md
/home/maksu/audio-alarm-lab/preflight-2026-08-31.md
/home/maksu/audio-alarm-lab/latency_test.py
/home/maksu/audio-alarm-lab/connect_srs_xb33.sh
/home/maksu/audio-alarm-lab/run_on_srs_xb33.sh
/home/maksu/audio-alarm-lab/audio_alarm_lab_20260831_artifacts.tar.gz
```

Wynik główny:

```text
/home/maksu/audio-alarm-lab/artifacts/2026-08-31/latency-main/click.wav
/home/maksu/audio-alarm-lab/artifacts/2026-08-31/latency-main/raw_capture.wav
/home/maksu/audio-alarm-lab/artifacts/2026-08-31/latency-main/results.csv
/home/maksu/audio-alarm-lab/artifacts/2026-08-31/latency-main/results.json
/home/maksu/audio-alarm-lab/artifacts/2026-08-31/latency-main/capture_timing.json
/home/maksu/audio-alarm-lab/artifacts/2026-08-31/latency-main/latency_plot.png
/home/maksu/audio-alarm-lab/artifacts/2026-08-31/latency-main/latency_report.md
/home/maksu/audio-alarm-lab/artifacts/2026-08-31/latency-main/snapshots/
```

Test po dłuższej ciszy znajduje się w katalogu `latency-long-idle/`, a piloty
w `latency-pilot/` i `latency-pilot-cold/`.

## 9. Najważniejsze wykonane komendy administracyjne

```sh
sudo systemctl enable --now bluetooth.service
sudo rfkill unblock bluetooth
sudo apt-get install --no-install-recommends -y alsa-utils rfkill
sudo usermod -aG audio maksu
systemctl --user restart pulseaudio.service
sudo alsactl store 1
```

Nie przeprowadzono migracji na PipeWire, nie zmieniono konfiguracji Home
Assistanta i nie wykonano destrukcyjnych operacji.
