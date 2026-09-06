# Interstellar Samsung USB report - 2026-07-07

## Result

Prepared USB pendrive for Samsung Tizen playback.

- USB disk wiped: `/dev/sdc`
- Stable USB path: `/dev/disk/by-id/usb-USB_SanDisk_3.2Gen1_010187d8143c2acb9a96b234f5c5b92e9d1091792c94f4aefa0c45f959a61959b55a000000000000000000007822ff1c000e5700ab5581078d2c998a-0:0`
- Device: SanDisk 3.2Gen1, 114.6G, `TRAN=usb`, `RM=1`
- Partition created: `/dev/sdc1`
- Filesystem: exFAT
- Label used: `INTERSTELLA`
- Mount point: `/mnt/interstellar_usb`
- `sync`: completed

Note: `mkfs.exfat -L INTERSTELLAR` rejected the requested 12-character label as too long on this host, so the label was shortened to `INTERSTELLA`. The filesystem itself is exFAT and the movie filename matches the requested Samsung naming.

## Source

- Source movie: `/mnt/data/media/movies/Interstellar (2014)/Interstellar.2014.UHD.BluRay.2160p.DTS-HD.MA.5.1.HEVC.REMUX-FraMeSToR.mkv`
- Source size: 70,586,488,468 bytes
- Final work file: `/home/maksu/interstellar_usb_work/Interstellar_Samsung.mkv`
- Final USB file: `/mnt/interstellar_usb/Interstellar_Samsung.mkv`
- Final size: 71,404,388,246 bytes

## Final USB contents

```text
total 67G
-rwxrwxrwx 1 maksu maksu 67G Jul  7 20:52 Interstellar_Samsung.mkv
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/sdc1       115G   67G   49G  59% /mnt/interstellar_usb
```

The final file size on USB matches the prepared work file:

```text
71404388246 /home/maksu/interstellar_usb_work/Interstellar_Samsung.mkv
71404388246 /mnt/interstellar_usb/Interstellar_Samsung.mkv
```

## Video

- Container: MKV
- Video codec: HEVC/H.265 Main 10
- Resolution: 3840x2160
- Pixel format / bit depth: `yuv420p10le`, 10-bit
- HDR metadata: BT.2020 / SMPTE ST 2084 preserved
- Video processing: copied without recompression using `-c:v copy`
- Scaling: none
- Tone mapping: none

## Audio

Source audio was English DTS-HD MA 5.1. For Samsung compatibility, a first/default AC3 track was created while preserving the original audio as a second track.

- Track 1: English AC3 5.1, 640 kb/s, default, title `Compatible AC3 5.1`
- Track 2: English DTS-HD MA 5.1, original copied, non-default, title `Original DTS-HD MA 5.1`

## Subtitles

No trustworthy local external Interstellar `.srt` subtitles were found. Jellyfin cached `.srt` files were inspected but belonged to other movies, so they were not used.

Embedded source PGS subtitle tracks were copied into the final MKV:

- English full, PGS, default because no Polish subtitle was available
- English SDH/CC, PGS
- French, PGS
- Spanish Latin American, PGS

External `.srt` files not found and therefore not copied:

- `Interstellar_Samsung.pl.srt`
- `Interstellar_Samsung.pl-alt.srt`
- `Interstellar_Samsung.pl-forced.srt`
- `Interstellar_Samsung.en.srt`
- `Interstellar_Samsung.en-sdh.srt`

## Safety notes

The only USB storage candidate was `/dev/sdc`. System and data disks were not formatted or modified:

- `/dev/sda`: internal SATA system/root disk
- `/dev/sdb`: internal SATA data disk mounted at `/mnt/data`
- `/dev/nvme0n1`: internal NVMe disk

Final USB state:

```text
NAME   MODEL             SIZE TRAN RM TYPE MOUNTPOINTS           FSTYPE LABEL       SERIAL
sdc    SanDisk 3.2Gen1 114.6G usb   1 disk                                          010187d8143c2acb9a96b234f5c5b92e9d1091792c94f4aefa0c45f959a61959b55a000000000000000000007822ff1c000e5700ab5581078d2c998a
`-sdc1                 114.6G       1 part /mnt/interstellar_usb exfat  INTERSTELLA
```
