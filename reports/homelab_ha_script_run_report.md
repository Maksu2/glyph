# Home Assistant script run report

Date: 2026-07-07  
Run window: 2026-07-07T19:27:02Z - 2026-07-07T19:27:17Z

## Outcome

All Home Assistant scripts from `/home/maksu/docker/homeassistant/config/scripts.yaml` were called through the local Home Assistant API.

All seven service calls returned HTTP `200` and every script entity updated `last_triggered`.

## Scripts called

| Script entity | Alias | Result | Last triggered |
| --- | --- | --- | --- |
| `script.zgas_wszystko` | Zgaś wszystko | HTTP 200 | 2026-07-07T19:27:02.782839+00:00 |
| `script.tablet_jasno` | Tablet Jasno | HTTP 200 | 2026-07-07T19:27:03.788249+00:00 |
| `script.tablet_czytanie` | Tablet Czytanie | HTTP 200 | 2026-07-07T19:27:04.796162+00:00 |
| `script.tablet_amber_100` | Tablet Amber 100 | HTTP 200 | 2026-07-07T19:27:05.803808+00:00 |
| `script.tablet_noc` | Tablet Noc | HTTP 200 | 2026-07-07T19:27:06.812202+00:00 |
| `script.tablet_fotel` | Tablet Fotel | HTTP 200 | 2026-07-07T19:27:07.818525+00:00 |
| `script.tablet_wieczor` | Tablet Wieczór | HTTP 200 | 2026-07-07T19:27:08.825451+00:00 |

## Final light state after the last script

The final state matches the last script, `Tablet Wieczór`.

| Entity | State | Brightness | Color | Last updated |
| --- | --- | --- | --- | --- |
| `light.wlacznik_sypialnia_left` | off | - | - | 2026-07-07T19:27:06.188722+00:00 |
| `light.wlacznik_sypialnia_right` | off | - | - | 2026-07-07T19:27:05.576165+00:00 |
| `light.tasma_lozko` | on | 64 | `[255, 151, 28]` | 2026-07-07T19:27:08.922025+00:00 |
| `light.zarowka_fotel` | on | 64 | `[255, 151, 28]` | 2026-07-07T19:27:08.939922+00:00 |
| `light.zarowka_szafa` | on | 128 | `[255, 151, 28]` | 2026-07-07T19:27:17.183733+00:00 |

## Service status after running scripts

```text
NAMES           STATUS         PORTS
zigbee2mqtt     Up 7 minutes   0.0.0.0:8099->8080/tcp, [::]:8099->8080/tcp
mosquitto       Up 7 minutes   0.0.0.0:1883->1883/tcp, [::]:1883->1883/tcp
homeassistant   Up 7 minutes
```

Restart counts stayed at zero:

```text
mosquitto restartCount=0 status=running running=true
zigbee2mqtt restartCount=0 status=running running=true
homeassistant restartCount=0 status=running running=true
```

## Log notes

Home Assistant logs did not show matching warning/error lines around the script calls.

Zigbee2MQTT logged one transient timeout while setting color on `Żarówka szafa`:

```text
Publish 'set' 'color' to 'Żarówka szafa' failed ... timed out after 10000ms
```

After that timeout, Zigbee2MQTT published fresh states for `Żarówka szafa`, ending with brightness `127`/`128` and the same amber color as the other final lights. The post-run Home Assistant state read confirms `light.zarowka_szafa` is `on`, brightness `128`, RGB `[255, 151, 28]`.

Mosquitto showed normal client disconnect notices only; no authentication/refused/error condition was found in the filtered log scan.

## Interpretation

The Home Assistant script layer is working: scripts can be called, state changes propagate through MQTT/Zigbee2MQTT, and the three restored core services remained running without restarts.

The only observed issue was a single Zigbee command timeout for one bulb during rapid sequential script execution. The device recovered/reported the expected final state afterward.
