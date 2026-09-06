# Raport wdrożenia — budzik „Another Name”

Data wdrożenia: 2026-09-01 UTC  
Home Assistant: 2026.8.3  
Strefa harmonogramu: Europe/Warsaw

## Wynik

Budzik muzyczno-świetlny jest wdrożony, włączony i gotowy na następny
kwalifikujący się trigger. Home Assistant publikuje polecenia pre-wake/start,
lokalna usługa użytkownika odbiera je z MQTT, a Python prowadzi playback i 59
komend choreografii względem jednego monotonicznego `t0`. Wśród nich jest 16
subtelnych pulsów taśmy; cztery analityczne kandydaty zostały celowo pominięte,
bo kolidowały z aktywnymi transition.

Nie wykonano pełnego fizycznego audio+light show podczas instalacji. To celowe
ograniczenie użytkownika, nie błąd wdrożenia.

## Harmonogram

| Zdarzenie | Czas lokalny | Dni | Warunek |
|---|---:|---|---|
| pre-wake | 05:59:40 | pon–pt | `person.maksu` w `zone.home` |
| show | 06:00:00 | pon–pt | `person.maksu` w `zone.home` |

Aktywna automatyzacja:

- config ID `another_name_alarm_schedule_v1`;
- entity `automation.another_name_budzik_06_00`;
- alias `Another Name - budzik 06:00`;
- stan zweryfikowany po restarcie: `on`.

Most wykonawczy `automation.another_name_most_cue_mqtt` również ma stan `on`.
Wiadomości startowe są publikowane z `retain: false`, a przed uruchomieniem
usługi sprawdzono brak retained command. Restart HA/dispatchera nie uruchamia
show.

## Zmiana starych automatów

Zawartość sprzed zmian zachowano w:

`/home/maksu/audio-alarm-lab/backups/ha-another-name-20260901T062437Z/`

- `automations.yaml.before`, SHA-256
  `7ff0781dab82039f12d481c57e442b6ffa1c4b32ad06745c353eb1c395252c7f`;
- `configuration.yaml.before`, SHA-256
  `059cdfdd606b83ff2e59dbd5b8abb46226e7189fd693ecc7803835aa428e4d34`.

Nie usunięto żadnej starej automatyzacji. Dodano `initial_state: false` i opis
zastąpienia do:

- `automation.pobudka_tasma` / ID `1779980853585` (05:50 pon–pt) — stan `off`;
- `automation.nowa_automatyzacja` / ID `1779980923954`, friendly name
  `Uruchamianie dużego światła o 6:00` — stan `off`.

Wyłączenie obu jest konieczne: pierwszy automat ustawiał trzy kolorowe lampy
na 100% już o 05:50, a drugi włączał oba kanały Aqara dokładnie o 06:00.

## Audio i pre-wake

- głośnik: Sony SRS-XB33, `04:21:44:06:6B:B9`;
- sink: `bluez_sink.04_21_44_06_6B_B9.a2dp_sink`;
- profil: A2DP, wcześniej zweryfikowany codec LDAC HQ;
- głośność sinka podczas show: 70%;
- audio latency model: 243 ms;
- ZigBee latency model: 80 ms;
- sharp cue offset: +163 ms.

O 05:59:40 helper najpierw sprawdza istniejące połączenie. Reconnect wykonuje
tylko przy braku `Connected: yes` lub sinka, maksymalnie trzy ograniczone próby.
Po gotowości uruchamiany jest 30-sekundowy bezgłośny PCM keepalive. PulseAudio
jest socket-activated; `pulseaudio.socket` jest enabled/active, a konto `maksu`
ma `Linger=yes`, więc tor jest dostępny bez interaktywnego logowania.

Źródło:

- MP3 `/home/maksu/audio-alarm-lab/media/Another Name.mp3`;
- wymagany i potwierdzony SHA-256
  `d0311089770db56dd4d7d9d2049c0b980a57ea4f921f8aca29504b354cef8008`;
- runtime PCM `/home/maksu/audio-alarm-lab/media/Another Name.wav`, s16le,
  44,1 kHz, stereo, 111,130703 s.

## Światła i finalny stan

Po zakończeniu:

- `light.zarowka_fotel`: ON, 100%, `color_temp`, 5000 K;
- `light.zarowka_szafa`: ON, 100%, `color_temp`, 5000 K;
- `light.tasma_lozko`: ON, 100%, XY `[0.346, 0.359]`;
- brak końcowego OFF i brak powrotu do ambientu.

Aqara pozostaje wyłączona z runtime: `entities.aqara_target: TBD`. Rejestr oraz
stara automatyzacja pokazują tylko, że Left i Right były używane razem; nie
pozwalają wiarygodnie wskazać właściwego obwodu. Późniejsza aktywacja wymaga
jednej zmiany tego pola na potwierdzony entity ID.

## Testy bez efektów ubocznych

- Python `py_compile`: OK;
- Bash `-n` helperów: OK;
- YAML parse i unikalność ID automatyzacji: OK;
- izolowany HA `check_config`: kod 0;
- pełny HA `/config` `check_config`: kod 0;
- restart HA: OK;
- nowe automatyzacje po restarcie: `on` / `on`;
- stare poranne automatyzacje po restarcie: `off` / `off`;
- systemd user dispatcher: `enabled`, `active`, `NRestarts=0`;
- negatywny probe command topic: odrzucony;
- negatywny probe mostu z `light.not_allowed`: trzy właściwe światła pozostały
  `off` z niezmienionymi timestampami;
- finalny dry-run: kod 0, 59 eventów, 16 pulses, zero Aqara, HA HTTP 200;
- mockowany pełny kod `execute`: PASS, 65 publikacji (M00: 3, scheduler:
  59, final reassert: 3), bez procesu audio i bez MQTT do świateł;
- mockowane awarie głośnika i startu audio: oba failsafe PASS, po trzy komendy
  finalnego invariantu;
- lokalny round-trip minimalnego publish klienta MQTT na osobnym topicu
  walidacyjnym: PASS;
- po testach: brak procesu show, brak `paplay`, SRS nadal rozłączony.

## Obsługa

Dry-run:

```bash
cd /home/maksu/audio-alarm-lab
./show/another_name_show.py --dry-run
```

Jawny pełny show:

```bash
cd /home/maksu/audio-alarm-lab
./show/another_name_show.py --execute
```

Natychmiastowy host-side kill switch:

```bash
systemctl --user disable --now another-name-alarm-dispatcher.service
```

Dodatkowo można wyłączyć w UI HA
`automation.another_name_budzik_06_00`. Szczegóły i procedura ponownego
włączenia są w `show/README.md`.
