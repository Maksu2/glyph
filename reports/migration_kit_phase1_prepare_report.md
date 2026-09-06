# Raport przygotowania migration kitu — faza 1

Data: `2026-07-05T19:36:00Z`  
Host źródłowy: `maxoo-pc`  
Nośnik: `/dev/sdc1`, ext4, etykieta `HOMELAB_MIG`  
Kit: `/mnt/homelab-migration-usb/homelab-migration-kit`  
Status: **prepare-only**

## Wynik

Przygotowano kompletny szkielet migracji do Raspberry Pi OS 64-bit / `arm64` dla wyłącznie:

- Home Assistant Container,
- Mosquitto / MQTT,
- Zigbee2MQTT,
- instrukcji utworzenia nowego node'a Tailscale.

Nie wykonano capture live data, nie zatrzymano ani nie zrestartowano usług i nie skopiowano danych konfiguracyjnych. Katalogi `configs/` pozostają puste.

## Utworzone artefakty

- `install_on_rpi.sh` — idempotentna instalacja do `/opt/homelab-lite`; wymusza `arm64`, Debian/Raspberry Pi OS, miejsce, Docker/Compose, capture i dongle.
- `preflight_check.sh` — read-only kontrola kitu, środowiska, portów, Dockera, checksum i `/dev/serial/by-id/`.
- `verify_after_install.sh` — kontrola kontenerów, HTTP 8123/8099, MQTT 1883 i redagowanych logów.
- `capture_live_data.sh` — przygotowany; w tym goalu wywołano wyłącznie bezpieczne `--help`, bez wejścia w tryb capture. Po dokładnej frazie zatrzymuje wyłącznie HA, Zigbee2MQTT i Mosquitto.
- `compose/docker-compose.yml` — tylko trzy usługi fazy 1.
- `README.md` — pełna instrukcja po polsku.
- `MIGRATION_NOTES.md` — założenia, zależności i checklista cutoveru.
- `rollback_notes.md` — bezpieczny powrót dongla i rdzenia na stary host.
- `manifest.json` — status `prepare-only`, capture `false`, źródła, cele, porty, wykluczenia i klasyfikacja plików wrażliwych.
- `checksums/prepare-only.sha256` — SHA-256 niemutowalnego szkieletu.

## Compose i arm64

Compose zawiera dokładnie `homeassistant`, `mosquitto` i `zigbee2mqtt`. Nie zawiera `platform: linux/amd64` ani usług ciężkiego homelaba.

W dniu przygotowania manifesty registry zawierały `linux/arm64` dla:

- `ghcr.io/home-assistant/home-assistant:stable`,
- `eclipse-mosquitto:2`,
- `koenkk/zigbee2mqtt:latest`.

README zaznacza, że `stable` i `latest` są pływające i po stabilizacji należy przypiąć przetestowane wersje lub digesty.

## Bramki bezpieczeństwa

- Capture wymaga uruchomienia przez `sudo`, ponieważ część `.storage` HA i baza Mosquitto są czytelne tylko dla roota.
- Capture wymaga dokładnie `TAK, ZATRZYMAJ RDZEN HA`.
- Skrypt nie zawiera `docker stop`, `docker compose down`, zatrzymania Dockera ani odwołań do obcych stacków.
- Po capture pyta o dokładne `URUCHOM PONOWNIE` dla starego rdzenia.
- Instalator nie instaluje Dockera bez dokładnego `ZAINSTALUJ DOCKER`.
- Ponowne uruchomienie instalatora nie nadpisuje działających danych w `/opt/homelab-lite/configs`.
- Tailscale ma zostać dodany jako nowy node; `tailscaled.state` nie znajduje się w kicie.
- Weryfikator zastępuje potencjalnie wrażliwe linie logów przez `[REDACTED sensitive log line]`.

## Walidacja

- `bash -n`: PASS dla wszystkich czterech skryptów.
- Tryb `--help`: PASS bez skutków ubocznych.
- `docker compose config --no-interpolate`: PASS.
- `manifest.json`: poprawny JSON UTF-8.
- `preflight_check.sh --prepare-only`: 0 błędów, 0 ostrzeżeń.
- Pełny preflight na PC: kontrolowana odmowa z powodu `x86_64`, zajętych portów i niewykonanego capture.
- Audyt UTF-8/mojibake: PASS.
- Audyt zakresu Compose: dokładnie trzy usługi.
- Audyt zakazanych komend capture: PASS.
- Skan typowych wzorców kluczy prywatnych/tokenów: PASS.
- `checksums/prepare-only.sha256`: wszystkie wpisy OK.
- Pliki payloadu w `configs/`: `0`.

## Stan usług po przygotowaniu

Nadal działają, z niezmienionymi czasami startu:

- `homeassistant`,
- `mosquitto`,
- `zigbee2mqtt`.

Tailscale pozostaje aktywny. Łącznie nadal działa 26 kontenerów. Nie wykonano formatowania, ponownego montowania ani zmian w `/mnt/data`.

## Następny krok

W osobnym, świadomie uruchomionym oknie serwisowym:

```bash
cd /mnt/homelab-migration-usb/homelab-migration-kit
sudo ./capture_live_data.sh
```

Ten raport nie jest potwierdzeniem wykonania capture; manifest nadal ma status `prepare-only` i `capture_live_data.performed=false`.
