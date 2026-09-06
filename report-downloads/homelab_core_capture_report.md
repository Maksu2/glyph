# Raport capture i zatrzymania starego rdzenia HA

Data zakończenia: `2026-07-05T19:51:43+00:00`  
Host: `maxoo-pc`  
Migration kit: `/mnt/homelab-migration-usb/homelab-migration-kit`

## Capture

- `manifest.json`: `capture-complete`
- `capture_live_data.performed`: `true`
- Czas capture zapisany w manifeście: `2026-07-05T19:50:45Z`
- Plik checksum: `checksums/live-data.sha256`
- Liczba wpisów checksum: `2716`
- Weryfikacja wszystkich checksum: `PASS`
- Log: `logs/capture_live_data.log`
- Filesystem pendrive'a został zsynchronizowany po capture.

Skopiowane zestawy danych:

- Home Assistant: około `88 MiB`
- Mosquitto: około `420 KiB`
- Zigbee2MQTT: około `44 KiB`

Nie wypisywano zawartości sekretów, `.storage`, baz ani backupu koordynatora.

## Stan starego rdzenia

Zatrzymano wyłącznie:

- `homeassistant` — `Exited (0)`
- `zigbee2mqtt` — `Exited (0)`
- `mosquitto` — `Exited (0)`

Nie uruchomiono ich ponownie po capture. `docker ps` z filtrami dla tych usług nie zwraca żadnego działającego kontenera.

## Usługi poza zakresem

Potwierdzono dalsze działanie m.in.:

- Nextcloud i MariaDB,
- Jellyfin,
- Frigate,
- Sonarr, Radarr i qBittorrent,
- Minecraft,
- Nginx Proxy Manager,
- Uptime Kuma.

Łącznie po zatrzymaniu rdzenia działają `23` kontenery. Docker jako całość nie został zatrzymany. `/mnt/data` pozostaje zamontowane z `/dev/sdb1` jako ext4.

## Dongle Zigbee

- Urządzenie: Sonoff Zigbee 3.0 USB Dongle Plus V2
- Stabilna ścieżka: `/dev/serial/by-id/usb-Itead_Sonoff_Zigbee_3.0_USB_Dongle_Plus_V2_4abceaef33f4ef118cd7bf1b6d9880ab-if00-port0`
- Bieżące urządzenie: `/dev/ttyUSB0`
- Zigbee2MQTT: zatrzymany
- Proces korzystający z `/dev/ttyUSB0`: brak

**Dongle można bezpiecznie fizycznie wyjąć ze starego hosta i podłączyć do Raspberry Pi.**

Nie należy ponownie uruchamiać starego Zigbee2MQTT, dopóki dongle pozostaje podłączony do Raspberry Pi.
