# Audio alarm lab — preflight

Timestamp: 2026-08-31 UTC  
Host: `maxoo-pc`  
User/session: `maksu` (uid 1000), `/run/user/1000`, user state active, linger enabled

No audio or Bluetooth configuration was changed during preflight. Calling
`pactl` socket-activated the already configured PulseAudio user service.

## OS

- Ubuntu 24.04.4 LTS (Noble)
- Kernel `6.8.0-138-generic`
- Board: MSI B450 GAMING PLUS MAX (`MS-7B86`, version 3.0)

Commands:

```sh
cat /etc/os-release
uname -a
id
loginctl show-user "$(id -u)" -p State -p Linger -p RuntimePath
```

## Audio stack

- Active stack: PulseAudio 16.1 (native server protocol 35).
- `pulseaudio.socket` was active; `pactl` started `pulseaudio.service` normally.
- PipeWire, pipewire-pulse and WirePlumber are not installed; `wpctl` is absent.
- `pactl info` reports `Server Name: pulseaudio`.
- PulseAudio Bluetooth modules are installed and loaded.
- `alsa-utils` is not installed, so `aplay`, `arecord`, and `amixer` are absent.
- Current PulseAudio devices: only `auto_null` and `auto_null.monitor`.

Commands:

```sh
systemctl --user --no-pager --full status pipewire.service pipewire-pulse.service wireplumber.service pulseaudio.service pulseaudio.socket
dpkg -l | rg '^(ii|rc)\s+(alsa|bluez|libspa-0.2-bluetooth|pipewire|pulseaudio|wireplumber)'
apt-cache policy alsa-utils pipewire pipewire-pulse wireplumber libspa-0.2-bluetooth pulseaudio pulseaudio-module-bluetooth bluez
pactl info
pactl list short modules
pactl list cards
pactl list sinks
pactl list sources
```

Key `pactl info` result:

```text
Server Name: pulseaudio
Server Version: 16.1
Default Sample Specification: s16le 2ch 44100Hz
Default Sink: auto_null
Default Source: auto_null.monitor
```

## Bluetooth

- Physical adapter exists: Intel Wireless-AC 9260 Bluetooth, USB `8087:0025`, kernel device `hci0` using `btusb`.
- Firmware loaded successfully (`intel/ibt-18-16-1.sfi`, firmware 155-35.23).
- `bluetooth.service` is installed but disabled and inactive.
- Because `bluetoothd` is not running, `bluetoothctl` and `btmgmt` did not return controller information; no adapter or device MAC was guessed.
- PulseAudio logged that the BlueZ D-Bus service was unavailable.

Commands:

```sh
systemctl status bluetooth.service --no-pager --full
find /sys/class/bluetooth -maxdepth 2 -printf '%p -> %l\n'
lsusb
udevadm info --attribute-walk --path=/sys/class/bluetooth/hci0
journalctl -k -b --no-pager | rg -i 'bluetooth|hci0'
timeout 5s btmgmt --index 0 info
timeout 5s bluetoothctl --timeout 4 list
```

## ALSA and microphone jack

- ALSA sees exactly one card: `card 0: HDA ATI HDMI`.
- It exposes playback PCMs 3, 7, 8, 9, and 10 only.
- There is no capture PCM at all; therefore the microphone jack is not currently detected by the kernel.
- PCI enumeration contains only GPU HDMI audio at `28:00.1`.
- The expected onboard AMD HD Audio PCI function is absent; no relevant module blacklist or kernel boot option was found.
- The board is specified by MSI as having a Realtek ALC892/ALC897 onboard HD Audio codec. The evidence strongly indicates that `HD Audio Controller` is disabled in UEFI/BIOS.

Commands:

```sh
ls -la /dev/snd
sed -n '1,240p' /proc/asound/cards
sed -n '1,260p' /proc/asound/pcm
sed -n '1,260p' /proc/asound/devices
lspci -nnk
lsmod | rg '^(snd|soundcore)'
sed -n '1p' /proc/cmdline
rg -n '(^|\s)(blacklist|install|options)\s+(snd|sound|sof|ac97|hda)' /etc/modprobe.d /lib/modprobe.d
journalctl -k -b --no-pager | rg -i 'snd|audio|sound|hda'
```

Key ALSA result:

```text
0 [HDMI]: HDA-Intel - HDA ATI HDMI
00-03: HDMI 0 : playback 1
00-07: HDMI 1 : playback 1
00-08: HDMI 2 : playback 1
00-09: HDMI 3 : playback 1
00-10: HDMI 4 : playback 1
```

## Preflight conclusion

Keep PulseAudio for this session because it is the existing, functional stack
and already has Bluetooth support. Do not migrate to PipeWire as part of this
task. Before device setup can continue, BlueZ must be enabled and `alsa-utils`
installed. The onboard HD Audio controller must also be enabled in UEFI so the
3.5 mm capture path can exist.

## Addendum: BIOS versus Linux disablement

Historical evidence makes BIOS/UEFI disablement effectively conclusive:

- On boot `-14` at 2026-08-26 17:12:03 UTC, PCI function `2a:00.4`
  (`1022:1487`) was enumerated and bound to `snd_hda_intel`.
- The Realtek codec was identified as ALC892, and both `Rear Mic` and
  `Front Mic` input devices were created.
- A saved diagnostic report from 2026-08-26 17:54 UTC independently contains
  the same PCI function and driver.
- From boot `-13` at 2026-08-27 10:44 UTC onward, the function is absent from
  the kernel's initial PCI enumeration. It is also absent on the current boot.
- No matching blacklist, GRUB parameter, persistent systemd/udev rule, or
  startup script was found. Driver unbinding, blacklisting, or VFIO binding
  would leave the PCI function visible in `lspci` anyway.

Therefore `HD Audio Controller` was almost certainly disabled in the MSI
firmware between the 26 August and 27 August boots. A one-off Linux sysfs PCI
removal is not consistent with the device remaining absent across later boots.
