# Homelab core restore report

Date: 2026-07-07  
Checked at: 2026-07-07T19:23:51Z

## Outcome

Restored the old homelab Home Assistant core after the Raspberry Pi migration test was parked.

Only these services were started:

- `mosquitto`
- `zigbee2mqtt`
- `homeassistant`

The restore used only the intended compose files:

- `/home/maksu/zigbee/docker-compose.yml`
- `/home/maksu/docker/homeassistant/docker-compose.yml`

No global Docker stop/start/down command was used.

## Service status

All three target containers are running:

```text
NAMES           STATUS         PORTS
zigbee2mqtt     Up 3 minutes   0.0.0.0:8099->8080/tcp, [::]:8099->8080/tcp
mosquitto       Up 3 minutes   0.0.0.0:1883->1883/tcp, [::]:1883->1883/tcp
homeassistant   Up 3 minutes
```

Inspect status:

```text
mosquitto status=running running=true restartCount=0 startedAt=2026-07-07T19:20:21.859730313Z
zigbee2mqtt status=running running=true restartCount=0 startedAt=2026-07-07T19:20:22.081620625Z
homeassistant status=running running=true restartCount=0 startedAt=2026-07-07T19:20:22.324502337Z
```

Late restart check after roughly three minutes:

```text
mosquitto restartCount=0 status=running running=true
zigbee2mqtt restartCount=0 status=running running=true
homeassistant restartCount=0 status=running running=true
```

## Endpoint and protocol checks

```text
ha_root_http=200
ha_api_http=401
z2m_http=200
mqtt_tcp=open
```

`ha_api_http=401` is expected without an authentication token and confirms the Home Assistant API endpoint is responding.

MQTT bridge state:

```json
{"state":"online"}
```

## Zigbee2MQTT checks

The Sonoff Zigbee dongle is visible again on the homelab host:

```text
/dev/serial/by-id/usb-Itead_Sonoff_Zigbee_3.0_USB_Dongle_Plus_V2_4abceaef33f4ef118cd7bf1b6d9880ab-if00-port0 -> /dev/ttyUSB0
```

Zigbee2MQTT logs after restore show:

- coordinator firmware detected,
- MQTT server connected,
- frontend started,
- bridge state published as online,
- `Zigbee2MQTT started!`.

## Home Assistant checks

Home Assistant configuration validation passed:

```text
Testing configuration at /config
```

Exit code: `0`.

Configuration file counts:

```text
configuration.yaml: entries=5
automations.yaml: entries=11
scripts.yaml: entries=7
scenes.yaml: entries=0
```

Recent Home Assistant logs after restart had no matching warnings or errors for:

- invalid config,
- setup failures,
- platform errors,
- automations,
- scripts,
- MQTT,
- Zigbee.

A second log scan after roughly three minutes found no matching warning/error lines in `homeassistant`, `zigbee2mqtt`, or `mosquitto`.

## Notes

Automations and scripts were validated as loaded configuration, not manually triggered. This avoids accidentally toggling devices or running home routines while still confirming that Home Assistant starts cleanly with the automation and script definitions present.
