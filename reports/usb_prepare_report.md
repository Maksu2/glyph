# Raport przygotowania pendrive'a pod homelab migration kit

## Podsumowanie

- Data przygotowania: `2026-07-05T19:24:00+00:00`
- Host źródłowy: `maxoo-pc`
- Wybrane urządzenie: `/dev/sdc`
- Nowa partycja: `/dev/sdc1`
- Model: `SanDisk 3.2Gen1`
- USB VID:PID: `0781:55ab`
- Serial: `010187d8143c2acb9a96b234f5c5b92e9d1091792c94f4aefa0c45f959a61959b55a000000000000000000007822ff1c000e5700ab5581078d2c998a`
- Rozmiar urządzenia: `123048296448` bajtów (`114.6 GiB`, klasa handlowa 128 GB)
- Transport / removable: `usb` / `RM=1`
- Nowa tablica partycji: `GPT`
- Nowy filesystem: `ext4`
- Nowa etykieta: `HOMELAB_MIG`
- UUID filesystemu: `af1b3dd4-21da-4d27-becc-ab9c5234665d`
- PARTUUID: `92551817-1730-4443-84ea-a26bb6280d87`
- Mountpoint: `/mnt/homelab-migration-usb`
- Opcje montowania: `rw,nosuid,nodev,relatime`
- Właściciel katalogu głównego filesystemu: `maksu:maksu`

## Stan przed formatowaniem

- Urządzenie miało jedną partycję `/dev/sdc1` obejmującą około `114.6 GiB`.
- Poprzedni filesystem partycji: `exFAT`.
- Poprzednia etykieta: `SANDISK`.
- Narzędzie partycjonujące wykryło prawidłową tablicę MBR oraz nieprawidłowe/pozostałościowe dane GPT; na samym urządzeniu wykrywana była także stara sygnatura `vfat`.
- Partycja nie była zamontowana.
- Odczytowa inspekcja wykazała około `5.9 GiB`, `27788` plików i `1319` katalogów, w tym `Downloads`, `About-me` oraz backup `zorin-thinkpad-backup-20260519-2139`.
- Użytkownik otrzymał to podsumowanie i następnie ponownie potwierdził dokładną frazą `FORMAT /dev/sdc HOMELAB_MIG`.

## Wykonane operacje

1. Ponownie zweryfikowano ścieżkę, model, pełny serial, rozmiar, transport USB, VID:PID, `RM=1` i brak mountpointów.
2. Usunięto stare sygnatury wyłącznie z potwierdzonego `/dev/sdc` i `/dev/sdc1`.
3. Utworzono nową tablicę partycji GPT.
4. Utworzono jedną partycję typu Linux filesystem obejmującą dostępne miejsce.
5. Sformatowano `/dev/sdc1` jako ext4 z etykietą `HOMELAB_MIG`.
6. Zamontowano partycję pod `/mnt/homelab-migration-usb`.
7. Ustawiono właściciela głównego katalogu filesystemu na `maksu:maksu`.
8. Utworzono pustą strukturę `/mnt/homelab-migration-usb/homelab-migration-kit/`.

## Wynik `lsblk` po formatowaniu

```text
NAME   PATH      MODEL             SIZE TYPE FSTYPE LABEL       UUID                                 PARTUUID                             PTTYPE MOUNTPOINTS                     TRAN RM
sdc    /dev/sdc  SanDisk 3.2Gen1 114.6G disk                                                                                              gpt                                    usb   1
└─sdc1 /dev/sdc1                 114.6G part ext4   HOMELAB_MIG af1b3dd4-21da-4d27-becc-ab9c5234665d 92551817-1730-4443-84ea-a26bb6280d87 gpt    /mnt/homelab-migration-usb       1
```

## Utworzona struktura

```text
homelab-migration-kit/
├── compose/
├── configs/
│   ├── homeassistant/
│   ├── mosquitto/
│   └── zigbee2mqtt/
├── backups/
├── logs/
├── checksums/
├── scripts/
├── README.md
└── usb_prepare_report.md
```

## Granice tego etapu

- Nie kopiowano danych Home Assistanta.
- Nie kopiowano danych Mosquitto.
- Nie kopiowano danych Zigbee2MQTT.
- Nie przenoszono stanu Tailscale.
- Nie utworzono `install_on_rpi.sh`.
- Nie zatrzymano ani nie zrestartowano żadnej usługi lub kontenera.
- Nie zmodyfikowano dysku systemowego `/dev/sda`, dysku danych `/dev/sdb` ani `/mnt/data`.

Nośnik jest przygotowany wyłącznie jako pusty szkielet pod kolejny goal.
