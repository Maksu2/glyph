# Another Name — budzik produkcyjny

## Stan

System jest wdrożony i aktywny. Home Assistant 2026.8.3 jest orkiestratorem,
a precyzyjny scheduler audio/światła działa lokalnie na Ubuntu. Instalacja,
reload i restart nie uruchamiają show: start następuje tylko od triggera
`06:00:00` albo jawnego `--execute`.

Nie wykonano pełnego fizycznego show podczas wdrożenia, zgodnie z wymaganiem.
Kod, dane, konfigurację HA i ścieżkę MQTT sprawdzono bez efektów ubocznych.

## Aktywny harmonogram

- strefa czasu: `Europe/Warsaw`;
- dni: poniedziałek–piątek;
- warunek: `person.maksu` musi być w `zone.home`;
- `05:59:40`: pre-wake Bluetooth;
- `06:00:00`: start audio i choreografii.

Automatyzacja HA:

- ID konfiguracji: `another_name_alarm_schedule_v1`;
- entity ID: `automation.another_name_budzik_06_00`;
- alias: `Another Name - budzik 06:00`;
- stan po wdrożeniu: `on`.

Most cue:

- ID konfiguracji: `another_name_light_bridge_v1`;
- entity ID: `automation.another_name_most_cue_mqtt`;
- topic: `audio-alarm/another-name/light/set`;
- przyjmuje wyłącznie pięć jawnie dozwolonych encji oraz ograniczone parametry
  `turn_on`/`turn_off`, jasności, XY, temperatury i transition.

## Przebieg runtime

1. HA publikuje nieretained wiadomość `prewake` o `05:59:40`.
2. Dispatcher uruchamia runner w trybie `--prewake`.
3. Runner sprawdza hashe plików, dostępność HA, Bluetooth i sink. Jeśli SRS nie
   jest gotowy, wykonuje maksymalnie trzy ograniczone czasowo próby połączenia.
4. Ustawia wyłącznie sink SRS na 70%, przygotowuje scenę M00 i otwiera 30 s
   bezgłośny stream, aby A2DP nie zaczynało od zimnego handshake'u.
5. O `06:00:00` HA publikuje `start`; runner zatrzymuje ciszę i ustawia jedno
   monotoniczne `t0` bezpośrednio przed `paplay`.
6. Wszystkie cue mają absolutne deadline'y względem `t0`; nie ma łańcucha
   kumulujących się `sleep`.
7. Po końcu runner idempotentnie potwierdza finalny invariant i niczego nie
   wyłącza.

Źródłowy MP3 jest obowiązkowo weryfikowany SHA-256. Odtwarzany jest wcześniej
zdekodowany PCM WAV 44,1 kHz, stereo, s16le, aby uniknąć zmiennego startu
dekodera MP3. Globalny default sink nie jest zmieniany; tylko `paplay` dostaje
`PULSE_SINK=bluez_sink.04_21_44_06_6B_B9.a2dp_sink`.

## Awaria

- brak sinka: runner ponawia połączenie; jeśli nadal go nie ma, nie odtwarza
  utworu i żąda awaryjnego 100% białego światła;
- błąd startu albo przedwczesny koniec audio: choreografia zostaje przerwana,
  a trzy dimmable lights dostają rampę awaryjną do finalnego stanu;
- pojedyncza niedostępna lampa nie zatrzymuje kolejnych MQTT cue;
- brak HA/MQTT przed audio: show nie zaczyna się;
- lock procesu nie pozwala uruchomić dwóch show równocześnie.

## Finalny invariant

Po `1:51.177` bez limitu czasu:

- `light.zarowka_fotel`: ON, 100%, natywny `color_temp`, 5000 K;
- `light.zarowka_szafa`: ON, 100%, natywny `color_temp`, 5000 K;
- `light.tasma_lozko`: ON, 100%, natywne XY `[0.346, 0.359]` jako biel;
- nic nie gaśnie i nic nie cofa się do ambientu.

`entities.aqara_target` w `another_name_cues.yaml` pozostaje `TBD`, ponieważ
stara automatyzacja sterowała jednocześnie Left i Right i nie dowodzi mapowania.
Runner nie wysyła więc żadnego polecenia do Aqara. Po nadzorowanej identyfikacji
należy zmienić tylko to jedno pole na jeden potwierdzony candidate entity ID.

## Obsługa

Dry-run bez Bluetooth, audio, publikacji cue i światła:

```bash
cd /home/maksu/audio-alarm-lab
./show/another_name_show.py --dry-run
```

Jawny pełny show (uruchamia urządzenia i audio):

```bash
cd /home/maksu/audio-alarm-lab
./show/another_name_show.py --execute
```

Jawny sam pre-wake:

```bash
cd /home/maksu/audio-alarm-lab
./show/another_name_show.py --prewake
```

Natychmiastowy host-side kill switch harmonogramu:

```bash
systemctl --user disable --now another-name-alarm-dispatcher.service
```

To unieszkodliwia wiadomości harmonogramu HA; domyślne `KillMode=control-group`
zatrzyma również uruchomiony runner. Światła pozostaną wtedy w ostatnim stanie.
Aby wyłączyć także wpis po stronie HA, przełącz na OFF
`automation.another_name_budzik_06_00` w UI Home Assistant.

Ponowne włączenie host-side:

```bash
systemctl --user enable --now another-name-alarm-dispatcher.service
```

Status i logi:

```bash
systemctl --user status another-name-alarm-dispatcher.service
journalctl --user -u another-name-alarm-dispatcher.service
ls -lt /home/maksu/audio-alarm-lab/logs/
```

## Pliki

- runner: `/home/maksu/audio-alarm-lab/show/another_name_show.py`;
- dispatcher: `/home/maksu/audio-alarm-lab/show/another_name_dispatcher.py`;
- runtime config: `/home/maksu/audio-alarm-lab/show/config.yaml`;
- cue source: `/home/maksu/audio-alarm-lab/analysis/another-name/another_name_cues.yaml`;
- HA deployment copy: `/home/maksu/audio-alarm-lab/deploy/homeassistant/automations.yaml`;
- systemd deployment copy: `/home/maksu/audio-alarm-lab/deploy/systemd/another-name-alarm-dispatcher.service`;
- backup HA: `/home/maksu/audio-alarm-lab/backups/ha-another-name-20260901T062437Z/`;
- execution logs: `/home/maksu/audio-alarm-lab/logs/`.
