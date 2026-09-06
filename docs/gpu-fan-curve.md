# GPU fan curve for RX 5500 XT / amdgpu

Manual-test runbook for `scripts/gpu_fan_curve.py`.

This does not touch VBIOS, does not install a GUI, and does not enable or
start a systemd service. `systemd/glyph-gpu-fan.service` is only a prepared
template.

## Detected hardware

On this host the AMD GPU is exposed as:

```text
/sys/class/hwmon/hwmon3 -> amdgpu
```

Observed idle-ish readings:

```text
edge: about 26-27C
junction/hotspot: about 26-27C
mem: 0.0C
fan: about 1300 RPM
pwm1: 63 / 255
pwm1_enable: 2 (auto)
power1_average: about 4 W
power1_cap: 125 W
gpu_busy_percent: 0%
mem_busy_percent: 0%
```

`rocm-smi` was not found on `PATH`, so the script uses hwmon/sysfs directly.

## Safety model

- The script discovers the `amdgpu` hwmon dynamically under `/sys/class/hwmon`.
- It controls by junction/hotspot when that sensor is present.
- If junction/hotspot is missing, normal fan control falls back to edge
  temperature and ramps earlier. Zero-RPM requires both hotspot and edge.
- On Ctrl+C, SIGTERM, exceptions, and normal process exit it writes
  `pwm1_enable=2` to return the driver to auto fan control.
- `--dry-run` never writes sysfs.
- `--once` performs one control loop and exits.
- Nonzero manual PWM is checked against `fan1_input`; if RPM stays at zero,
  the script boosts PWM and exits back to auto if the fan still does not spin.

## Idle policies

`--idle-policy auto`

Keeps the original idle behavior: when the GPU is cool and low-power, delegate
fan control to amdgpu auto mode. This is the default and safest idle policy.

`--idle-policy manual-low`

Uses a low manual idle PWM while the card is cool. This can be quieter than
auto, but must be tested while watching RPM and hotspot.

`--idle-policy zero`

May set PWM 0 only after a long, stable idle. This is not the default and is
not recommended while training is active.

Zero-RPM entry requires all of these at the same time:

```text
hotspot <= 38C
edge <= 34C
power <= 12 W
gpu_busy_percent <= 3%, when available
stable for 90 s
```

Zero-RPM exit uses higher hysteresis thresholds:

```text
hotspot >= 48C
edge >= 42C
power >= 25 W
gpu_busy_percent >= 10%, when available
```

If the fan is stopped and cooling must resume, the script kickstarts at 45%
PWM for 2 s before returning to the normal curve.

If a foreground daemon run enters zero-RPM but `fan1_input` still reports RPM
after the stop timeout, the script disables zero-RPM for that process and
falls back to auto idle.

## Training profile

The default profile is `glyph-training`.

When junction/hotspot exists:

```text
idle auto by default: <= 40C and <= 18 W
45C: 22%
55C: 28%
65C: 36%
75C: 50%
85C: 68%
90C: 82%
95C: 100% fail-safe
```

When only edge exists:

```text
idle auto by default: <= 34C and <= 18 W
35C: 25%
45C: 35%
55C: 50%
65C: 70%
75C: 90%
80C: 100% fail-safe
```

The controller smooths temperature with an exponential moving average and
limits normal manual PWM changes to 8 percentage points per loop. Fail-safe
cooling is not rate-limited.

## Commands

Detection report:

```bash
python3 scripts/gpu_fan_curve.py --report
```

Guarded zero-RPM stop/start test:

```bash
sudo python3 scripts/gpu_fan_curve.py --test-zero-rpm
```

Dry-run of zero-RPM policy:

```bash
sudo python3 scripts/gpu_fan_curve.py --profile glyph-training \
  --idle-policy zero --dry-run --once
```

Manual foreground training profile:

```bash
sudo python3 scripts/gpu_fan_curve.py --profile glyph-training \
  --log-file logs/gpu-fan-curve.log
```

Manual foreground zero-idle experiment, only after `--test-zero-rpm` passes:

```bash
sudo python3 scripts/gpu_fan_curve.py --profile glyph-training \
  --idle-policy zero --log-file logs/gpu-fan-curve.log
```

Return to auto immediately:

```bash
echo 2 | sudo tee /sys/class/hwmon/hwmon3/pwm1_enable
```

Stop a foreground run with Ctrl+C. The script should log `restore-auto` or
`already-auto`.

## Zero-RPM risks

Zero-RPM is for idle only. During Glyph training use the training curve, not
zero-idle as an assumption of safety. Even with hotspot control, a stopped fan
can lag behind sudden load changes; that is why the script requires low power,
low GPU usage, a 90 s dwell period, hysteresis, kickstart, and RPM verification.

If `--test-zero-rpm` reports that PWM 0 does not stop the fans, zero-idle is
not useful on this card/driver. If kickstart fails, do not use zero-idle.

## Zero-RPM test result

Tested on 2026-05-27 with edge/hotspot around 27C, power around 4 W, and
`gpu_busy_percent=0%`.

```text
PWM 0 stop test: timeout after 45 s
RPM after PWM 0: about 1304 RPM
Kickstart: OK, 45% PWM produced about 600 RPM within 0.5 s
Lowest observed sustaining PWM: 5/255, 2%, about 588 RPM for 5 s
Cleanup: restored pwm1_enable=2 auto
```

Conclusion: real zero-RPM idle is not useful on this RX 5500 XT with the
current amdgpu behavior, because PWM 0 did not stop the fans. Use `auto` for
training safety, or manually test `manual-low` if the goal is lower idle noise.
