# Rekonesans homelaba przed migracją lekkich usług na Raspberry Pi

Data rekonesansu: 2026-07-05 (UTC)  
Host: `maxoo-pc` — Ubuntu 24.04.4 LTS, `x86_64`, 6 CPU, 31 GiB RAM  
Tryb pracy: **read-only**. Nie użyto `sudo`, nie instalowano pakietów, nie zatrzymano ani nie zrestartowano usług lub kontenerów, nie zmieniono konfiguracji i nie odczytano wartości sekretów.

## Wniosek wykonawczy

Najbardziej sensowny pierwszy zakres migracji to:

1. **Home Assistant**
2. **Mosquitto / MQTT**
3. **Zigbee2MQTT wraz z donglem Sonoff**
4. **Tailscale**, najlepiej jako nowy węzeł

To jest spójny, lekki rdzeń 24/7. Aktywny łańcuch zależności wygląda tak:

`Sonoff Zigbee USB → Zigbee2MQTT → Mosquitto MQTT → Home Assistant`

Home Assistant ma aktywną integrację `mqtt`, automatyzacje zawierają odwołania do MQTT/Zigbee, a Zigbee2MQTT ma włączoną integrację Home Assistant i używa brokera `mqtt://mosquitto:1883`. Nie znaleziono ESPHome ani ZHA. Obecny Zigbee działa przez Zigbee2MQTT, nie przez ZHA.

Uptime Kuma i ewentualnie Nginx Proxy Manager można rozważyć dopiero później. Cloudflared działający jako usługa systemowa kieruje ruch do Minecrafta na `localhost:25565`; pozostałe tunele Cloudflare obsługują projekty Glyph. Żaden znaleziony tunel Cloudflare nie wskazuje na Home Assistanta.

Ciężkie i hostowo zależne usługi — Nextcloud, Jellyfin, Frigate, arr-stack, Minecraft, Time Machine, AI/Glyph oraz monitoring całego PC — powinny zostać na homelabie.

## Stan hosta i magazynu

- System plików `/`: 466 GiB, użyte 237 GiB.
- `/mnt/data`: ext4 na `/dev/sdb1`, 3.6 TiB, użyte 2.4 TiB.
- Największe logiczne drzewa danych: `/mnt/data/downloads` około 1.2 TiB, `/mnt/data/mac` około 1.2 TiB, `/mnt/data/media` około 804 GiB, Time Machine około 220 GiB.
- W `/mnt/data` występują hardlinki pomiędzy drzewami pobrań i mediów. Rozmiarów logicznych nie wolno sumować; częściowe kopiowanie mogłoby zamienić hardlinki w duplikaty i gwałtownie zwiększyć zapotrzebowanie na miejsce.
- Aktywny host jest `x86_64`; Raspberry Pi będzie najpewniej `arm64`. Obrazy i własne buildy trzeba zweryfikować oraz przypiąć wersjami w osobnym goalu migracyjnym.

## Home Assistant i zależności

### Home Assistant — `MIGRATE_TO_RPI_NOW`

- Typ / stan: kontener Docker `homeassistant`, działa.
- Porty: TCP 8123 przez `network_mode: host`.
- Compose: `/home/maksu/docker/homeassistant/docker-compose.yml`.
- Config/data: `/home/maksu/docker/homeassistant/config`, około 92 MiB.
- Mounty: config → `/config` RW; `/etc/localtime` RO.
- Ważne pliki: `configuration.yaml`, `automations.yaml`, `scripts.yaml`, `scenes.yaml`, `secrets.yaml`, `.storage`, `home-assistant_v2.db`.
- Zależności: Mosquitto i pośrednio Zigbee2MQTT; brak bezpośredniego urządzenia USB.
- Sekrety: tak — `secrets.yaml`, `.storage`, auth i tokeny są wrażliwe; wartości pozostają `[REDACTED]`.
- Duże dane `/mnt/data`: nie.
- Uzasadnienie: właściwa usługa 24/7; około 553 MiB RAM w chwili odczytu i mały zbiór danych.
- Ryzyka: aktywna baza SQLite ma pliki WAL/SHM, więc przyszła kopia musi być aplikacyjnie spójna; mogą zmienić się adres brokera i endpoint zdalnego dostępu; trzeba użyć obrazu `arm64`.
- Do migration kitu: compose i cały katalog `config`, ale dopiero po kontrolowanym zatrzymaniu w osobnym goalu.

### Mosquitto — `MIGRATE_TO_RPI_NOW`

- Typ / stan: kontener `mosquitto`, działa.
- Port: TCP 1883 na wszystkich interfejsach.
- Compose: `/home/maksu/zigbee/docker-compose.yml`.
- Config/data: `/home/maksu/zigbee/mosquitto/{config,data,log}`; dane około 404 KiB, config około 8 KiB.
- Mounty: trzy katalogi do `/mosquitto/config`, `/mosquitto/data`, `/mosquitto/log`, RW.
- Zależności: brak; zależne są Zigbee2MQTT i Home Assistant.
- USB: nie. Duże dane: nie.
- Sekrety: w obecnej konfiguracji nie wykryto `password_file`; zawartości wrażliwych nie odczytywano.
- Uzasadnienie: bardzo lekki i niezbędny w aktywnym łańcuchu Zigbee.
- Ryzyka: `allow_anonymous true` i port wystawiony na wszystkich interfejsach. Nie należy mieć dwóch rozbieżnych brokerów po przełączeniu.
- Do migration kitu: compose, `mosquitto.conf` i katalog danych; logi są opcjonalne.

### Zigbee2MQTT — `MIGRATE_TO_RPI_NOW`

- Typ / stan: kontener `zigbee2mqtt`, działa.
- Port: TCP 8099 → 8080 na wszystkich interfejsach.
- Compose: `/home/maksu/zigbee/docker-compose.yml`.
- Config/data: `/home/maksu/zigbee/zigbee2mqtt`, 23 MiB, głównie logi. Rdzeń to `configuration.yaml`, `database.db`, `state.json` i `coordinator_backup.json`.
- Mounty: katalog danych → `/app/data` RW; `/run/udev` RO.
- Zależności: Mosquitto; dongle Zigbee; Home Assistant jest odbiorcą przez MQTT.
- USB: tak. Sonoff Zigbee 3.0 USB Dongle Plus V2, adapter `ember`.
- Stabilna ścieżka urządzenia: `/dev/serial/by-id/usb-Itead_Sonoff_Zigbee_3.0_USB_Dongle_Plus_V2_4abceaef33f4ef118cd7bf1b6d9880ab-if00-port0` → `/dev/ttyUSB0`.
- Sekrety: tak — konfiguracja i backup koordynatora mogą zawierać klucz sieci Zigbee; wartości pozostają `[REDACTED]`.
- Duże dane: nie.
- Uzasadnienie: lekka, krytyczna usługa automatyki domowej.
- Ryzyka: nigdy nie uruchamiać dwóch instancji z tym samym koordynatorem; zachować `by-id`, adapter `ember` i wersję danych; fizyczny transfer wymaga okna niedostępności.
- Do migration kitu: compose, bieżąca konfiguracja, `database.db`, `state.json`, `coordinator_backup.json`; starsze backupy konfiguracji po ręcznej decyzji; logi raczej pominąć.

### Tailscale — `MIGRATE_TO_RPI_NOW`

- Typ / stan: `tailscaled.service`, aktywny i włączony.
- Port: UDP 41641 dla transportu Tailscale.
- Compose: brak; jednostka `/usr/lib/systemd/system/tailscaled.service`.
- Config/data: `/etc/default/tailscaled`, `/var/lib/tailscale/tailscaled.state`.
- Rozmiar: katalog stanu niedostępny bez uprawnień; nie użyto `sudo`.
- Zależności: sieć. USB: nie. Duże dane: nie.
- Sekrety: `tailscaled.state` jest tożsamością węzła i musi być traktowany jak sekret.
- Uzasadnienie: lekki, bezpieczny kanał zdalnego dostępu 24/7.
- Ryzyka: ślepe przeniesienie stanu może sklonować tożsamość węzła.
- Do migration kitu: najwyżej bezsekretna konfiguracja/intencja instalacji. Zalecenie: dodać Pi jako **nowy węzeł**, zamiast kopiować `tailscaled.state`.

## Usługi opcjonalne później

### Uptime Kuma — `OPTIONAL_LATER`

- Działa jako `uptime-kuma-uptime-kuma-1`; TCP 3001.
- Compose: `/home/maksu/docker/uptime-kuma/docker-compose.yml`.
- Data/mount: `/home/maksu/docker/uptime-kuma/data` → `/app/data`, około 288 KiB.
- Zależności/USB/duże dane: brak.
- Sekrety: baza może zawierać credentiale monitorów i tokeny powiadomień.
- Uzasadnienie: lekka i sensowna na hoście 24/7, ale nie jest zależnością HA.
- Ryzyko/kit: kopiować compose i data w spójnym punkcie dopiero po stabilizacji rdzenia.

### Nginx Proxy Manager — `OPTIONAL_LATER`

- Działa jako `nginx-proxy-manager-app-1`; TCP 80, 443 i panel 81.
- Compose: `/home/maksu/docker/nginx-proxy-manager/docker-compose.yml`.
- Data/mounty: `data` → `/data`, `letsencrypt` → `/etc/letsencrypt`; około 61 MiB plus chronione materiały certyfikatów.
- Zależności: DNS i przekierowania portów, jeśli dostęp publiczny; brak USB i `/mnt/data`.
- Sekrety: tak — baza, klucze i certyfikaty.
- Uzasadnienie: technicznie lekki, ale obsługuje także usługi pozostające na PC i nie jest potwierdzoną zależnością HA.
- Ryzyko/kit: ruch publiczny, certyfikaty i routing mogą zostać przerwane. Najpierw zdecydować, czy HA ma być dostępny przez Tailscale, NPM czy nowy dedykowany tunnel Cloudflare.

## Usługi pozostające na homelabie

Poniższa tabela zawiera wymagane pola dla każdej znalezionej usługi lub stosu. Rozmiary są orientacyjne i pochodzą z działającego systemu.

| Usługa | Typ / działa | Porty | Compose | Config/data i mounty | Rozmiar | Zależności / USB / sekrety / `/mnt/data` | Kategoria i uzasadnienie | Ryzyka / migration kit |
|---|---|---|---|---|---:|---|---|---|
| Cloudflared system tunnel | systemd / tak | brak listenera; outbound | brak | `/etc/cloudflared/config.yml`, credential JSON | 12 KiB | Minecraft; USB nie; sekrety tak; duże dane nie | `KEEP_ON_HOMELAB`: ingress wskazuje `tcp://localhost:25565`, nie HA | Credential JSON `[REDACTED]`; nie wkładać do kitu HA |
| Cloudflared Glyph public + training | 2 user-systemd / tak | originy 8194 i 8181 | brak | `/home/maksu/.cloudflared/{glyph-public.yml,training-dashboard.yml}` i credentiale | 652 KiB cały `.cloudflared` | Glyph; USB nie; sekrety tak; duże dane nie | `KEEP_ON_HOMELAB`: tunele projektów AI | Credentiale `[REDACTED]`; nie kopiować |
| Portainer | standalone Docker / tak | 8000, 9443 | nie znaleziono | volume `portainer_data` → `/data`; Docker socket RW | 1.05 MiB | Docker socket; USB nie; sekrety tak; duże dane nie | `DO_NOT_MIGRATE`: zarządza bieżącym hostem | Uprzywilejowany socket; ewentualnie świeża instancja na Pi, bez starego kitu |
| Nextcloud + MariaDB | compose, 2 kontenery / tak | 8080 | `/home/maksu/docker/nextcloud/docker-compose.yml` | app `/home/.../data`, DB `/home/.../db`, user data `/mnt/data/nextcloud` | 820 MiB app, 226 MiB DB, 63 MiB user data | MariaDB i `/mnt/data`; USB nie; sekrety tak | `KEEP_ON_HOMELAB`: stanowa baza i storage | Wymaga skoordynowanego dumpu/kopii i UID/GID; nic do lekkiego kitu |
| Jellyfin | Docker / tak | 8096 | `/home/maksu/docker/jellyfin/docker-compose.yml` | config → `/config`, `/mnt/data/media` → `/media`, volume cache | 508 MiB config, 8.2 MiB cache, 804 GiB media | media; USB nie; sekrety tak; duże dane tak | `KEEP_ON_HOMELAB`: biblioteka i transkodowanie | Wydajność/storage; nic do kitu |
| Frigate | Docker / tak, healthy | 5000, 8554 | `/home/maksu/docker/frigate/docker-compose.yml` | config → `/config`, `/mnt/data/frigate` → `/media/frigate`, `/dev/dri/renderD128` | 248 KiB config; bieżący mount 32 KiB; `/mnt/data/cam` 100 MiB | GPU/kamery; USB nie; sekrety tak; duże dane potencjalnie | `KEEP_ON_HOMELAB`: video + akceleracja | Credentiale kamer i zgodność akceleracji; nic do kitu |
| Minecraft | Docker / tak | 25565 | `/home/maksu/minecraft/docker-compose.yml` | `/home/maksu/minecraft/new` → `/server`; osobne `/mnt/data/minecraft` | 15 GiB aktywne + 12 GiB osobne | Cloudflared i Playit; USB nie; sekrety tak | `KEEP_ON_HOMELAB`: około 4 GiB RAM w chwili odczytu | Spójność świata, RCON, routing tuneli; nic do kitu |
| Time Machine Samba | Docker + 3 user-systemd Avahi / tak, healthy | 445 | `/home/maksu/docker/timemachine/docker-compose.yml` | `/mnt/data/mac/timemachine` → `/timemachine`, `.env` | około 220 GiB | Avahi i HDD; USB nie; sekrety tak; duże dane tak | `KEEP_ON_HOMELAB`: duży backup na HDD | Sparsebundle, Samba, mDNS, UID/GID; nic do kitu |
| Homelab Status | compose, frontend+backend / tak | 18080 | `/home/maksu/homelab-status/docker-compose.yml` | root/proc/sys, `/mnt/data`, Docker socket i wiele DB/configów RO; własne data RW | 2.0 GiB projekt | niemal cały host; USB nie; sekrety tak; duże dane tak | `DO_NOT_MIGRATE`: monitoruje właśnie ten PC | Szeroki dostęp do hosta/socketu; źródła przestaną pasować; nic do kitu |
| Glances | definicja compose / nie znaleziono kontenera | 61208 nie nasłuchuje | `/home/maksu/docker/glances/docker-compose.yml` | root, `/mnt/data`, sensory, Docker socket RO | 28 KiB projekt | host/sensory; USB nie; sekrety nie; duże dane tak | `DO_NOT_MIGRATE`: host-specific i nie działa | Na Pi ewentualnie świeża instancja, bez migracji danych |
| Homelab Pocket Agent | Docker / tak | brak publikowanego | `/home/maksu/homelab-pocket-agent/docker-compose.yml` | config + `.env`; `/mnt/data` i `ai-model` RO | 57 MiB | AI i HDD; USB nie; sekrety tak; duże dane tak | `DO_NOT_MIGRATE`: źródła pozostają na PC | Nie wkładać do kitu |
| OpenClaw Gateway | user-systemd / tak | 18789, 18791 | brak | `/home/maksu/.openclaw`, `gateway.systemd.env` | nie mierzono | Node; USB nie; sekrety tak; duże dane nie | `KEEP_ON_HOMELAB`: własna usługa, niezależna od HA | Env `[REDACTED]`; poza kitem |
| Sunshine | user-systemd / tak | 47984, 47989, 47990, 48010 | brak | config hosta | nie mierzono | desktop/GPU; USB nie; sekrety tak | `DO_NOT_MIGRATE`: streaming gier z PC | Brak sensu na Pi w tym celu |
| VS Code Tunnel | user-systemd / tak | transport wychodzący | brak | konfiguracja użytkownika | nie mierzono | środowisko deweloperskie PC; sekrety tak | `DO_NOT_MIGRATE` | Poza kitem |
| `ruview-esp32` | standalone Docker / nie, exited | brak | nie znaleziono | brak persistent mountów | brak danych trwałych | brak | `DO_NOT_MIGRATE`: eksperyment bez trwałego stanu | Poza kitem |

### arr-stack — `KEEP_ON_HOMELAB`

Wszystkie niżej wymienione kontenery działają z `/home/maksu/docker/arr-stack/docker-compose.yml`, korzystają ze wspólnej sieci `arr-stack_arr-net`, zawierają konfiguracje/credentiale i są związane z dużymi drzewami `/mnt/data`. Plik `.env` wykryto, ale jego treści nie odczytano.

| Usługa | Port | Config / mounty | Orientacyjny rozmiar config | Zależności i ryzyko | Co do kitu |
|---|---:|---|---:|---|---|
| qBittorrent | 8090, 6881 TCP/UDP | `qbittorrent/config`, `/mnt/data/downloads` | 13 MiB | około 5.4 GiB RAM przy odczycie; 1.2 TiB logical downloads | nic |
| FlareSolverr | 8191 | anonimowy volume `/config` | 0 B w volume | zależność Prowlarr; obraz około 986 MiB | nic |
| Prowlarr | 9696 | `prowlarr/config` | 137 MiB | indexery i credentiale | nic |
| Radarr | 7878 | `radarr/config`, `/mnt/data` | 90 MiB | media/hardlinki | nic |
| Sonarr | 8989 | `sonarr/config`, `/mnt/data` | 59 MiB | media/hardlinki | nic |
| Readarr | 8787 | `readarr/config`, `/mnt/data` | 56 MiB | media/hardlinki | nic |
| Bazarr | 6767 | `bazarr/config`, `/mnt/data` | 692 KiB | zależny od Sonarr/Radarr | nic |
| Kavita | 5001 | `kavita/config`, `/mnt/data/media/books` | 4.3 MiB + biblioteka | biblioteka na HDD | nic |
| IA Books Torznab | 8765 | `ia-books-torznab` RO | 12 KiB | mały, ale logicznie część arr-stack | nic |

Powód wspólnej decyzji: stack jest silnie związany z HDD, hardlinkami i usługami pozostającymi na PC. Przenoszenie pojedynczych elementów zwiększyłoby złożoność sieci i ryzyko rozjechania ścieżek bez korzyści dla Home Assistanta.

### Glyph / ai-model i własne projekty — `KEEP_ON_HOMELAB`

- Aktywne kontenery: inferencja CPU `glyph-inference-glyph-inference-1` na `127.0.0.1:8195` oraz serwer raportów na 8101.
- Aktywne user services: publiczny origin Glyph na 8194, dashboard na 8181 i dwa tunele Cloudflare.
- Compose: `docker-compose.inference.yml`, `docker-compose.reports.yml`; istnieją też definicje teacher/train CPU/ROCm.
- Dane i mounty: checkpointy, tokenizer, data, raporty; definicje treningowe używają `/dev/kfd` i `/dev/dri`.
- Rozmiar: około 7.9 GiB projektu; obrazy i build cache to dalsze dziesiątki GiB.
- USB: nie; sekrety: tak; duże dane `/mnt/data`: nie w aktywnych kontenerach, ale workload jest obliczeniowy.
- Ryzyka: własne buildy `amd64`, ROCm/Vulkan i duże obrazy. Nic z tego nie powinno trafić do lekkiego kitu HA.
- Inne wykryte katalogi projektowe bez potwierdzonego runtime: `gemos-cloudflare-pages`, `gemos-recovery-work`, `maksu-strona`, `openclaw-personalization-draft` oraz archiwum OpenClaw. Nie klasyfikowano ich jako działających usług i nie należy kopiować ich automatycznie.

## Pliki compose

Znaleziono 18 definicji compose:

- `/home/maksu/docker/{homeassistant,uptime-kuma,nginx-proxy-manager,nextcloud,jellyfin,frigate,arr-stack,timemachine,glances}/docker-compose.yml`
- `/home/maksu/zigbee/docker-compose.yml`
- `/home/maksu/minecraft/docker-compose.yml`
- `/home/maksu/homelab-status/docker-compose.yml`
- `/home/maksu/homelab-pocket-agent/docker-compose.yml`
- `/home/maksu/ai-model/docker-compose.{inference,reports,teacher,train,train.rocm}.yml`

Portainer i `ruview-esp32` nie mają odnalezionego pliku compose. Glances ma compose, ale nie ma działającego kontenera.

## Potencjalny migration kit — bez tworzenia go teraz

Rdzeń przyszłego kitu powinien objąć:

- `/home/maksu/docker/homeassistant/docker-compose.yml`
- `/home/maksu/docker/homeassistant/config/`
- `/home/maksu/zigbee/docker-compose.yml`
- `/home/maksu/zigbee/mosquitto/config/`
- `/home/maksu/zigbee/mosquitto/data/`
- `/home/maksu/zigbee/zigbee2mqtt/configuration.yaml`
- `/home/maksu/zigbee/zigbee2mqtt/database.db`
- `/home/maksu/zigbee/zigbee2mqtt/state.json`
- `/home/maksu/zigbee/zigbee2mqtt/coordinator_backup.json`
- ewentualnie backupy `configuration_backup_v*.yaml`, po ręcznej decyzji
- `/etc/default/tailscaled` jako odniesienie; **nie** kopiować automatycznie `/var/lib/tailscale/tailscaled.state`

Do tego w następnym goalu powinny dojść: manifest, checksums, lista właścicieli/trybów plików, jawnie przypięte obrazy `arm64`, instrukcja rollbacku oraz zaszyfrowane traktowanie sekretów. Nie tworzono ich w tym rekonesansie.

Opcjonalny drugi etap może dodać Uptime Kuma i Nginx Proxy Manager, ale nie powinny być częścią pierwszego przełączenia rdzenia.

## Szczególna ostrożność

1. **Spójność live data.** Ten rekonesans nie zatrzymywał usług. Bazy HA, Kuma, NPM, Nextcloud i inne nie są obecnie gotowymi kopiami migracyjnymi.
2. **Jeden koordynator, jedna instancja.** Przed uruchomieniem Zigbee2MQTT na Pi stara instancja musi być zatrzymana, a dongle fizycznie przeniesiony.
3. **Sekrety.** `.storage`, `secrets.yaml`, Zigbee coordinator backup, Cloudflare credential JSON, Tailscale state, `.env`, bazy NPM/Kuma i credentiale aplikacji wymagają ochrony. W raporcie wartości pozostają `[REDACTED]`.
4. **MQTT.** Broker obecnie zezwala na anonimowych klientów i nasłuchuje na wszystkich interfejsach. To jest osobna decyzja bezpieczeństwa, nie coś do zmiany w read-only rekonesansie.
5. **Architektura.** Nie należy kopiować obrazów `amd64`; trzeba odtworzyć usługi z obrazów `arm64` i sprawdzić kompatybilność wersji.
6. **Adresacja.** HA, MQTT i Zigbee2MQTT muszą dostać przewidywalny adres Pi/DNS. Zmiana broker hosta może wymagać kontrolowanej aktualizacji integracji HA.
7. **Storage Pi.** Dla HA i baz lepszy jest SSD niż sama karta microSD.
8. **Hardlinki.** Rozmiary `/mnt/data/downloads`, `/mnt/data/media` i `/mnt/data/mac` nakładają się; nie sumować i nie kopiować jako części lekkiego kitu.

## Decyzje wymagające użytkownika przed następnym goalem

- Model Raspberry Pi, ilość RAM, system `arm64` i docelowy nośnik.
- Home Assistant Container czy Home Assistant OS; bieżąca instalacja to Container.
- Czy zachować pełną historię/recorder HA, czy zacząć z nową bazą.
- Termin okna serwisowego dla spójnego zatrzymania HA/MQTT/Zigbee2MQTT w przyszłości.
- Nowy węzeł Tailscale (zalecane) czy transfer starej tożsamości.
- Tailscale, NPM czy dedykowany Cloudflare tunnel jako zdalny dostęp do HA.
- Docelowy hostname, rezerwacja DHCP/statyczny IP, DNS i porty Pi.
- Czy w drugim etapie migrować Uptime Kuma i NPM.
- Czy zachować anonimowe MQTT tymczasowo, czy w osobnym kontrolowanym kroku włączyć uwierzytelnianie.
- Czy do zaszyfrowanego kitu dołączyć stare backupy Zigbee2MQTT i logi.

## Ograniczenia rekonesansu

- Bez `sudo` nie odczytano chronionego `/var/lib/tailscale` ani części hostowych katalogów danych. Nie było to konieczne do bezpiecznej rekomendacji.
- Nie czytano treści `.env`, secretów, tokenów, haseł, credential JSON ani kluczy API.
- Rozmiary są orientacyjne i pochodzą z działającego systemu.
- Raport jest mapą, nie migratorem: nie utworzono `install_on_rpi.sh`, nie spakowano danych, nie zamontowano pendrive'a i niczego nie migrowano.
