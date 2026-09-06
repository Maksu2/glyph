#!/usr/bin/env python3
"""Safe amdgpu hwmon fan controller for long Glyph ROCm training."""
from __future__ import annotations

import argparse
import atexit
import os
import signal
import shutil
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


HWMON_ROOT = Path("/sys/class/hwmon")


@dataclass(frozen=True)
class TempSensor:
    label: str
    input_path: Path
    label_path: Path | None
    crit_path: Path | None
    emergency_path: Path | None


@dataclass(frozen=True)
class AmdgpuHwmon:
    root: Path
    real_root: Path
    device_root: Path
    temps: dict[str, TempSensor]
    fan_rpm: Path | None
    pwm: Path | None
    pwm_enable: Path | None
    pwm_min: Path | None
    pwm_max: Path | None
    power_average: Path | None
    power_cap: Path | None
    gpu_busy_percent: Path | None
    mem_busy_percent: Path | None


@dataclass(frozen=True)
class Snapshot:
    edge_c: float | None
    hotspot_c: float | None
    mem_c: float | None
    fan_rpm: int | None
    pwm: int | None
    pwm_enable: int | None
    power_w: float | None
    power_cap_w: float | None
    gpu_busy_percent: int | None
    mem_busy_percent: int | None


@dataclass(frozen=True)
class Profile:
    name: str
    hotspot_curve: tuple[tuple[float, float], ...]
    edge_curve: tuple[tuple[float, float], ...]
    hotspot_fail_c: float
    edge_fail_c: float
    idle_enter_hotspot_c: float
    idle_exit_hotspot_c: float
    idle_enter_edge_c: float
    idle_exit_edge_c: float
    idle_enter_power_w: float
    idle_exit_power_w: float
    idle_manual_percent: float
    smoothing_alpha: float
    max_pwm_step_percent: float
    zero_enter_hotspot_c: float
    zero_exit_hotspot_c: float
    zero_enter_edge_c: float
    zero_exit_edge_c: float
    zero_enter_power_w: float
    zero_exit_power_w: float
    zero_enter_gpu_busy_percent: int
    zero_exit_gpu_busy_percent: int
    zero_dwell_s: float
    kickstart_percent: float
    kickstart_s: float
    rpm_running_threshold: int
    rpm_verify_delay_s: float
    rpm_verify_retry_s: float
    rpm_retry_boost_percent: float
    zero_test_stop_timeout_s: float
    zero_test_spinup_timeout_s: float
    zero_test_hold_step_s: float


GLYPH_TRAINING = Profile(
    name="glyph-training",
    # RX 5500 XT exposes pwm 0..255 here. Percent values are converted to the
    # detected pwm range at runtime.
    hotspot_curve=(
        (45.0, 22.0),
        (55.0, 28.0),
        (65.0, 36.0),
        (75.0, 50.0),
        (85.0, 68.0),
        (90.0, 82.0),
        (95.0, 100.0),
    ),
    # If junction/hotspot is missing, edge is a weaker signal. Keep a bigger
    # safety margin and ramp earlier.
    edge_curve=(
        (35.0, 25.0),
        (45.0, 35.0),
        (55.0, 50.0),
        (65.0, 70.0),
        (75.0, 90.0),
        (80.0, 100.0),
    ),
    hotspot_fail_c=95.0,
    edge_fail_c=80.0,
    idle_enter_hotspot_c=40.0,
    idle_exit_hotspot_c=48.0,
    idle_enter_edge_c=34.0,
    idle_exit_edge_c=40.0,
    idle_enter_power_w=18.0,
    idle_exit_power_w=35.0,
    idle_manual_percent=18.0,
    smoothing_alpha=0.35,
    max_pwm_step_percent=8.0,
    zero_enter_hotspot_c=38.0,
    zero_exit_hotspot_c=48.0,
    zero_enter_edge_c=34.0,
    zero_exit_edge_c=42.0,
    zero_enter_power_w=12.0,
    zero_exit_power_w=25.0,
    zero_enter_gpu_busy_percent=3,
    zero_exit_gpu_busy_percent=10,
    zero_dwell_s=90.0,
    kickstart_percent=45.0,
    kickstart_s=2.0,
    rpm_running_threshold=100,
    rpm_verify_delay_s=3.0,
    rpm_verify_retry_s=4.0,
    rpm_retry_boost_percent=20.0,
    zero_test_stop_timeout_s=45.0,
    zero_test_spinup_timeout_s=8.0,
    zero_test_hold_step_s=5.0,
)

PROFILES = {GLYPH_TRAINING.name: GLYPH_TRAINING}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").strip()


def read_int(path: Path | None) -> int | None:
    if path is None or not path.exists():
        return None
    try:
        return int(read_text(path))
    except (OSError, ValueError):
        return None


def read_temp_c(path: Path | None) -> float | None:
    value = read_int(path)
    if value is None:
        return None
    return value / 1000.0


def read_power_w(path: Path | None) -> float | None:
    value = read_int(path)
    if value is None:
        return None
    return value / 1_000_000.0


def write_sysfs(path: Path, value: int) -> None:
    with path.open("w", encoding="utf-8") as handle:
        handle.write(f"{value}\n")


def first_existing(root: Path, names: Iterable[str]) -> Path | None:
    for name in names:
        path = root / name
        if path.exists():
            return path
    return None


def hwmon_device_root(real_root: Path) -> Path:
    if real_root.parent.name == "hwmon":
        return real_root.parent.parent
    return real_root.parent


def discover_amdgpu_hwmons() -> list[AmdgpuHwmon]:
    devices: list[AmdgpuHwmon] = []
    for root in sorted(HWMON_ROOT.glob("hwmon*"), key=lambda p: p.name):
        name_path = root / "name"
        if not name_path.exists():
            continue
        try:
            name = read_text(name_path)
        except OSError:
            continue
        if name != "amdgpu":
            continue

        temps: dict[str, TempSensor] = {}
        for input_path in sorted(root.glob("temp*_input")):
            base = input_path.name.removesuffix("_input")
            label_path = root / f"{base}_label"
            try:
                label = read_text(label_path) if label_path.exists() else base
            except OSError:
                label = base
            normalized = label.strip().lower()
            temps[normalized] = TempSensor(
                label=label,
                input_path=input_path,
                label_path=label_path if label_path.exists() else None,
                crit_path=first_existing(root, [f"{base}_crit"]),
                emergency_path=first_existing(root, [f"{base}_emergency"]),
            )

        real_root = root.resolve()
        device_root = hwmon_device_root(real_root)
        devices.append(
            AmdgpuHwmon(
                root=root,
                real_root=real_root,
                device_root=device_root,
                temps=temps,
                fan_rpm=first_existing(root, ["fan1_input"]),
                pwm=first_existing(root, ["pwm1"]),
                pwm_enable=first_existing(root, ["pwm1_enable"]),
                pwm_min=first_existing(root, ["pwm1_min"]),
                pwm_max=first_existing(root, ["pwm1_max"]),
                power_average=first_existing(root, ["power1_average", "power1_input"]),
                power_cap=first_existing(root, ["power1_cap"]),
                gpu_busy_percent=first_existing(device_root, ["gpu_busy_percent"]),
                mem_busy_percent=first_existing(device_root, ["mem_busy_percent"]),
            )
        )
    return devices


def pick_hwmon(path: str | None = None) -> AmdgpuHwmon:
    if path:
        requested = Path(path).resolve()
        for hwmon in discover_amdgpu_hwmons():
            if requested in {hwmon.root.resolve(), hwmon.real_root}:
                return hwmon
        raise SystemExit(f"Requested hwmon is not an amdgpu hwmon: {path}")

    devices = discover_amdgpu_hwmons()
    if not devices:
        raise SystemExit("No amdgpu hwmon found under /sys/class/hwmon")
    if len(devices) > 1:
        roots = ", ".join(str(device.root) for device in devices)
        raise SystemExit(f"More than one amdgpu hwmon found ({roots}); pass --hwmon")
    return devices[0]


def temp_by_alias(hwmon: AmdgpuHwmon, aliases: tuple[str, ...]) -> TempSensor | None:
    for alias in aliases:
        sensor = hwmon.temps.get(alias)
        if sensor:
            return sensor
    for label, sensor in hwmon.temps.items():
        if any(alias in label for alias in aliases):
            return sensor
    return None


def edge_sensor(hwmon: AmdgpuHwmon) -> TempSensor | None:
    return temp_by_alias(hwmon, ("edge", "core"))


def hotspot_sensor(hwmon: AmdgpuHwmon) -> TempSensor | None:
    return temp_by_alias(hwmon, ("junction", "hotspot"))


def mem_sensor(hwmon: AmdgpuHwmon) -> TempSensor | None:
    return temp_by_alias(hwmon, ("mem", "memory", "vram"))


def snapshot(hwmon: AmdgpuHwmon) -> Snapshot:
    edge = edge_sensor(hwmon)
    hotspot = hotspot_sensor(hwmon)
    mem = mem_sensor(hwmon)
    return Snapshot(
        edge_c=read_temp_c(edge.input_path if edge else None),
        hotspot_c=read_temp_c(hotspot.input_path if hotspot else None),
        mem_c=read_temp_c(mem.input_path if mem else None),
        fan_rpm=read_int(hwmon.fan_rpm),
        pwm=read_int(hwmon.pwm),
        pwm_enable=read_int(hwmon.pwm_enable),
        power_w=read_power_w(hwmon.power_average),
        power_cap_w=read_power_w(hwmon.power_cap),
        gpu_busy_percent=read_int(hwmon.gpu_busy_percent),
        mem_busy_percent=read_int(hwmon.mem_busy_percent),
    )


def fmt(value: object, suffix: str = "") -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.1f}{suffix}"
    return f"{value}{suffix}"


def writable(path: Path | None) -> str:
    if path is None:
        return "n/a"
    return "yes" if os.access(path, os.W_OK) else "no"


def print_report(hwmon: AmdgpuHwmon) -> None:
    snap = snapshot(hwmon)
    print("AMDGPU hwmon report")
    print(f"  hwmon: {hwmon.root}")
    print(f"  real path: {hwmon.real_root}")
    print(f"  device path: {hwmon.device_root}")
    print(f"  rocm-smi: {shutil.which('rocm-smi') or shutil.which('rocm-smi.py') or 'not found on PATH'}")
    print()
    print("Temperature sensors:")
    for _label, sensor in sorted(hwmon.temps.items()):
        temp = read_temp_c(sensor.input_path)
        crit = read_temp_c(sensor.crit_path)
        emergency = read_temp_c(sensor.emergency_path)
        print(
            f"  {sensor.label}: input={sensor.input_path} "
            f"current={fmt(temp, 'C')} crit={fmt(crit, 'C')} emergency={fmt(emergency, 'C')}"
        )
    print()
    print("Fan and PWM:")
    print(f"  fan rpm: {hwmon.fan_rpm or 'missing'} current={fmt(snap.fan_rpm)}")
    print(f"  pwm: {hwmon.pwm or 'missing'} current={fmt(snap.pwm)} writable={writable(hwmon.pwm)}")
    print(
        f"  pwm enable: {hwmon.pwm_enable or 'missing'} current={fmt(snap.pwm_enable)} "
        f"writable={writable(hwmon.pwm_enable)}"
    )
    print(f"  pwm min: {hwmon.pwm_min or 'missing'} current={fmt(read_int(hwmon.pwm_min))}")
    print(f"  pwm max: {hwmon.pwm_max or 'missing'} current={fmt(read_int(hwmon.pwm_max))}")
    print()
    print("Power:")
    print(f"  average: {hwmon.power_average or 'missing'} current={fmt(snap.power_w, 'W')}")
    print(f"  cap: {hwmon.power_cap or 'missing'} current={fmt(snap.power_cap_w, 'W')}")
    print()
    print("Usage:")
    print(f"  gpu busy: {hwmon.gpu_busy_percent or 'missing'} current={fmt(snap.gpu_busy_percent, '%')}")
    print(f"  mem busy: {hwmon.mem_busy_percent or 'missing'} current={fmt(snap.mem_busy_percent, '%')}")
    print()
    if hotspot_sensor(hwmon):
        print("Control sensor: junction/hotspot is available and will be used.")
    elif edge_sensor(hwmon):
        print("Control sensor: hotspot is missing; edge fallback will ramp earlier.")
    else:
        print("Control sensor: missing edge and hotspot; fan control cannot run.")


def interpolate(points: tuple[tuple[float, float], ...], temp_c: float) -> float:
    if temp_c <= points[0][0]:
        return points[0][1]
    for (left_t, left_pwm), (right_t, right_pwm) in zip(points, points[1:]):
        if temp_c <= right_t:
            ratio = (temp_c - left_t) / (right_t - left_t)
            return left_pwm + ratio * (right_pwm - left_pwm)
    return points[-1][1]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def percent_to_pwm(percent: float, pwm_min: int, pwm_max: int) -> int:
    percent = clamp(percent, 0.0, 100.0)
    return int(round(pwm_min + (pwm_max - pwm_min) * percent / 100.0))


class FanController:
    def __init__(
        self,
        hwmon: AmdgpuHwmon,
        profile: Profile,
        *,
        dry_run: bool,
        once: bool,
        interval_s: float,
        idle_policy: str,
        log_file: Path | None,
    ) -> None:
        self.hwmon = hwmon
        self.profile = profile
        self.dry_run = dry_run
        self.once = once
        self.interval_s = interval_s
        self.idle_policy = idle_policy
        self.log_file = log_file
        self.restored = False
        self.smoothed_temp_c: float | None = None
        self.last_manual_percent: float | None = None
        self.last_mode: str | None = None
        self.idle_latched = False
        self.zero_active = False
        self.zero_candidate_since: float | None = None
        self.zero_entered_at: float | None = None
        self.zero_disabled_reason: str | None = None

        self.edge = edge_sensor(hwmon)
        self.hotspot = hotspot_sensor(hwmon)
        self.control_kind = "hotspot" if self.hotspot else "edge"
        if self.hotspot:
            self.control_sensor = self.hotspot
        elif self.edge:
            self.control_sensor = self.edge
        else:
            raise SystemExit("No usable edge or junction/hotspot temperature sensor found")

        if not hwmon.pwm or not hwmon.pwm_enable:
            raise SystemExit("This amdgpu hwmon does not expose pwm1 and pwm1_enable")

        self.pwm_min = read_int(hwmon.pwm_min)
        self.pwm_max = read_int(hwmon.pwm_max)
        if self.pwm_min is None:
            self.pwm_min = 0
        if self.pwm_max is None:
            self.pwm_max = 255
        if self.pwm_max <= self.pwm_min:
            raise SystemExit(f"Invalid PWM range: min={self.pwm_min} max={self.pwm_max}")

    def log(self, message: str) -> None:
        print(message, flush=True)
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with self.log_file.open("a", encoding="utf-8") as handle:
                handle.write(message + "\n")

    def restore_auto(self, reason: str = "cleanup") -> None:
        if self.restored:
            return
        self.restored = True
        if not self.hwmon.pwm_enable:
            return
        if self.dry_run:
            self.log(f"{utc_now()} profile={self.profile.name} state=cleanup action=would-restore-auto reason={reason}")
            return
        try:
            if read_int(self.hwmon.pwm_enable) == 2:
                self.log(f"{utc_now()} profile={self.profile.name} state=cleanup action=already-auto reason={reason}")
                return
            write_sysfs(self.hwmon.pwm_enable, 2)
            self.log(f"{utc_now()} profile={self.profile.name} state=cleanup action=restore-auto reason={reason}")
        except OSError as exc:
            self.log(
                f"{utc_now()} profile={self.profile.name} state=cleanup action=restore-auto-failed "
                f"reason={reason} error={exc}"
            )

    def set_manual_pwm(self, pwm: int) -> None:
        if not self.hwmon.pwm or not self.hwmon.pwm_enable:
            raise RuntimeError("PWM sysfs paths are missing")
        if read_int(self.hwmon.pwm_enable) != 1:
            write_sysfs(self.hwmon.pwm_enable, 1)
        if read_int(self.hwmon.pwm) != pwm:
            write_sysfs(self.hwmon.pwm, pwm)

    def fan_running(self, rpm: int | None) -> bool:
        return rpm is not None and rpm > self.profile.rpm_running_threshold

    def current_rpm(self) -> int | None:
        return read_int(self.hwmon.fan_rpm)

    def control_temp(self) -> float:
        value = read_temp_c(self.control_sensor.input_path)
        if value is None:
            raise RuntimeError(f"Could not read control temperature from {self.control_sensor.input_path}")
        if self.smoothed_temp_c is None:
            self.smoothed_temp_c = value
        else:
            alpha = self.profile.smoothing_alpha
            self.smoothed_temp_c = alpha * value + (1.0 - alpha) * self.smoothed_temp_c
        return value

    def idle_thresholds(self) -> tuple[float, float]:
        if self.control_kind == "hotspot":
            return self.profile.idle_enter_hotspot_c, self.profile.idle_exit_hotspot_c
        return self.profile.idle_enter_edge_c, self.profile.idle_exit_edge_c

    def should_fail_safe(self, raw_temp_c: float) -> bool:
        if self.control_kind == "hotspot":
            return raw_temp_c >= self.profile.hotspot_fail_c
        return raw_temp_c >= self.profile.edge_fail_c

    def zero_entry_reasons(self, snap: Snapshot) -> list[str]:
        reasons: list[str] = []
        if self.hotspot is None or snap.hotspot_c is None:
            reasons.append("missing junction/hotspot sensor")
        elif snap.hotspot_c > self.profile.zero_enter_hotspot_c:
            reasons.append(f"hotspot {snap.hotspot_c:.1f}C > {self.profile.zero_enter_hotspot_c:.1f}C")

        if self.edge is None or snap.edge_c is None:
            reasons.append("missing edge sensor")
        elif snap.edge_c > self.profile.zero_enter_edge_c:
            reasons.append(f"edge {snap.edge_c:.1f}C > {self.profile.zero_enter_edge_c:.1f}C")

        if snap.power_w is None:
            reasons.append("missing power sensor")
        elif snap.power_w > self.profile.zero_enter_power_w:
            reasons.append(f"power {snap.power_w:.1f}W > {self.profile.zero_enter_power_w:.1f}W")

        if self.hwmon.gpu_busy_percent and snap.gpu_busy_percent is None:
            reasons.append("gpu busy sensor unreadable")
        elif snap.gpu_busy_percent is not None and snap.gpu_busy_percent > self.profile.zero_enter_gpu_busy_percent:
            reasons.append(
                f"gpu busy {snap.gpu_busy_percent}% > {self.profile.zero_enter_gpu_busy_percent}%"
            )

        return reasons

    def zero_exit_reasons(self, snap: Snapshot, raw_temp_c: float | None = None) -> list[str]:
        reasons: list[str] = []
        if raw_temp_c is not None and self.should_fail_safe(raw_temp_c):
            threshold = self.profile.hotspot_fail_c if self.control_kind == "hotspot" else self.profile.edge_fail_c
            reasons.append(f"{self.control_kind} {raw_temp_c:.1f}C >= fail-safe {threshold:.1f}C")
        if snap.hotspot_c is None:
            reasons.append("missing junction/hotspot sensor")
        elif snap.hotspot_c >= self.profile.zero_exit_hotspot_c:
            reasons.append(f"hotspot {snap.hotspot_c:.1f}C >= {self.profile.zero_exit_hotspot_c:.1f}C")
        if snap.edge_c is None:
            reasons.append("missing edge sensor")
        elif snap.edge_c >= self.profile.zero_exit_edge_c:
            reasons.append(f"edge {snap.edge_c:.1f}C >= {self.profile.zero_exit_edge_c:.1f}C")
        if snap.power_w is None:
            reasons.append("missing power sensor")
        elif snap.power_w >= self.profile.zero_exit_power_w:
            reasons.append(f"power {snap.power_w:.1f}W >= {self.profile.zero_exit_power_w:.1f}W")
        if snap.gpu_busy_percent is not None and snap.gpu_busy_percent >= self.profile.zero_exit_gpu_busy_percent:
            reasons.append(f"gpu busy {snap.gpu_busy_percent}% >= {self.profile.zero_exit_gpu_busy_percent}%")
        return reasons

    def zero_snapshot_text(self, snap: Snapshot) -> str:
        return (
            f"edge_c={fmt(snap.edge_c)} hotspot_c={fmt(snap.hotspot_c)} power_w={fmt(snap.power_w)} "
            f"gpu_busy={fmt(snap.gpu_busy_percent, '%')} fan_rpm={fmt(snap.fan_rpm)} "
            f"pwm={fmt(snap.pwm)} pwm_enable={fmt(snap.pwm_enable)}"
        )

    def enter_zero(self, snap: Snapshot, reason: str) -> None:
        if self.zero_active:
            return
        self.zero_active = True
        action = "would-enter-zero-rpm" if self.dry_run else "enter-zero-rpm"
        self.log(
            f"{utc_now()} profile={self.profile.name} state=zero-rpm action={action} "
            f"{self.zero_snapshot_text(snap)} reason=\"{reason}\""
        )

    def leave_zero(self, snap: Snapshot, reason: str) -> None:
        if not self.zero_active:
            return
        self.zero_active = False
        self.zero_entered_at = None
        self.zero_candidate_since = None
        action = "would-exit-zero-rpm" if self.dry_run else "exit-zero-rpm"
        self.log(
            f"{utc_now()} profile={self.profile.name} state=zero-rpm action={action} "
            f"{self.zero_snapshot_text(snap)} reason=\"{reason}\""
        )

    def disable_zero(self, snap: Snapshot, reason: str) -> None:
        self.zero_disabled_reason = reason
        self.leave_zero(snap, reason)
        self.log(
            f"{utc_now()} profile={self.profile.name} state=zero-rpm action=disable "
            f"{self.zero_snapshot_text(snap)} reason=\"{reason}\""
        )

    def decide_zero(self, snap: Snapshot, raw_temp_c: float, now_s: float) -> tuple[str, float | None, str, str] | None:
        if self.idle_policy != "zero":
            return None

        if self.zero_disabled_reason:
            return "auto", None, "zero-disabled", self.zero_disabled_reason

        if self.should_fail_safe(raw_temp_c):
            self.leave_zero(snap, f"{self.control_kind} fail-safe temperature")
            self.zero_candidate_since = None
            return "manual", 100.0, "fail-safe", f"{self.control_kind} {raw_temp_c:.1f}C >= fail-safe threshold"

        if self.zero_active:
            exit_reasons = self.zero_exit_reasons(snap, raw_temp_c)
            if exit_reasons:
                reason = "; ".join(exit_reasons)
                self.leave_zero(snap, reason)
                return None
            if (
                self.zero_entered_at is not None
                and now_s - self.zero_entered_at >= self.profile.zero_test_stop_timeout_s
                and self.fan_running(snap.fan_rpm)
            ):
                reason = (
                    f"PWM 0 did not stop fan after {now_s - self.zero_entered_at:.0f}s; "
                    f"rpm={fmt(snap.fan_rpm)}"
                )
                self.disable_zero(snap, reason)
                return "auto", None, "zero-disabled", reason
            return "manual", 0.0, "zero-rpm", "zero-RPM active; idle conditions still inside hysteresis"

        entry_reasons = self.zero_entry_reasons(snap)
        if entry_reasons:
            if self.zero_candidate_since is not None:
                self.log(
                    f"{utc_now()} profile={self.profile.name} state=zero-rpm action=disarm "
                    f"{self.zero_snapshot_text(snap)} reason=\"{'; '.join(entry_reasons)}\""
                )
            self.zero_candidate_since = None
            return None

        if self.zero_candidate_since is None:
            self.zero_candidate_since = now_s
        elapsed = now_s - self.zero_candidate_since
        reason = (
            f"zero idle criteria stable for {elapsed:.0f}/{self.profile.zero_dwell_s:.0f}s; "
            f"hotspot, edge, power and gpu busy are low"
        )
        if elapsed >= self.profile.zero_dwell_s:
            self.enter_zero(snap, reason)
            self.zero_entered_at = now_s
            return "manual", 0.0, "zero-rpm", reason
        return "auto", None, "zero-armed", reason

    def decide(self, snap: Snapshot, raw_temp_c: float) -> tuple[str, float | None, str, str]:
        assert self.smoothed_temp_c is not None
        now_s = time.monotonic()
        zero_decision = self.decide_zero(snap, raw_temp_c, now_s)
        if zero_decision is not None:
            return zero_decision

        enter_temp, exit_temp = self.idle_thresholds()
        power_w = snap.power_w
        power_low = power_w is None or power_w <= self.profile.idle_enter_power_w
        power_high = power_w is not None and power_w >= self.profile.idle_exit_power_w

        if self.should_fail_safe(raw_temp_c):
            self.idle_latched = False
            return "manual", 100.0, "fail-safe", f"{self.control_kind} {raw_temp_c:.1f}C >= fail-safe threshold"

        if self.idle_latched:
            if self.smoothed_temp_c >= exit_temp or power_high:
                self.idle_latched = False
        elif self.smoothed_temp_c <= enter_temp and power_low:
            self.idle_latched = True

        if self.idle_latched:
            if self.idle_policy in {"auto", "zero"}:
                return "auto", None, "idle-auto", "cool and low power; delegate to amdgpu auto fan mode"
            return (
                "manual",
                self.profile.idle_manual_percent,
                "idle-manual-low",
                "cool and low power; quiet manual idle pwm",
            )

        curve = self.profile.hotspot_curve if self.control_kind == "hotspot" else self.profile.edge_curve
        target_percent = interpolate(curve, self.smoothed_temp_c)
        state = "training"
        if target_percent >= 95.0:
            state = "max-cooling"
        elif target_percent >= 65.0:
            state = "hot-training"
        elif target_percent <= 30.0:
            state = "quiet-training"

        reason = f"{self.control_kind} smoothed {self.smoothed_temp_c:.1f}C on {self.profile.name} curve"
        if self.last_manual_percent is not None:
            delta = target_percent - self.last_manual_percent
            max_step = self.profile.max_pwm_step_percent
            if abs(delta) > max_step and state != "fail-safe":
                target_percent = self.last_manual_percent + max_step * (1 if delta > 0 else -1)
                reason += f"; rate-limited to {target_percent:.1f}%"
        return "manual", target_percent, state, reason

    def ensure_fan_spinning(self, target_pwm: int, target_percent: float) -> tuple[int, float]:
        if target_pwm <= self.pwm_min:
            return target_pwm, target_percent
        if self.hwmon.fan_rpm is None:
            self.log(
                f"{utc_now()} profile={self.profile.name} state=fan-check action=skip "
                "reason=\"fan RPM sensor missing\""
            )
            return target_pwm, target_percent

        time.sleep(self.profile.rpm_verify_delay_s)
        rpm = self.current_rpm()
        if self.fan_running(rpm):
            self.log(
                f"{utc_now()} profile={self.profile.name} state=fan-check action=ok "
                f"rpm={fmt(rpm)} pwm={target_pwm} reason=\"nonzero PWM produced RPM\""
            )
            return target_pwm, target_percent

        boost_percent = clamp(
            max(target_percent + self.profile.rpm_retry_boost_percent, self.profile.kickstart_percent),
            0.0,
            100.0,
        )
        boost_pwm = percent_to_pwm(boost_percent, self.pwm_min, self.pwm_max)
        self.log(
            f"{utc_now()} profile={self.profile.name} state=fan-check action=warning "
            f"rpm={fmt(rpm)} pwm={target_pwm} boost_pwm={boost_pwm} boost_percent={boost_percent:.1f} "
            "reason=\"nonzero PWM did not start fan\""
        )
        self.set_manual_pwm(boost_pwm)
        time.sleep(self.profile.rpm_verify_retry_s)
        rpm_after = self.current_rpm()
        if not self.fan_running(rpm_after):
            self.log(
                f"{utc_now()} profile={self.profile.name} state=fan-check action=error "
                f"rpm={fmt(rpm_after)} pwm={boost_pwm} reason=\"fan did not start after boosted PWM\""
            )
            self.restore_auto("fan-rpm-verification-failed")
            raise RuntimeError("Fan RPM stayed at zero after nonzero and boosted PWM")

        self.log(
            f"{utc_now()} profile={self.profile.name} state=fan-check action=recovered "
            f"rpm={fmt(rpm_after)} pwm={boost_pwm} reason=\"boosted PWM started fan\""
        )
        return boost_pwm, boost_percent

    def maybe_kickstart(self, target_pwm: int, target_percent: float) -> None:
        if target_pwm <= self.pwm_min or self.hwmon.fan_rpm is None:
            return
        rpm_before = self.current_rpm()
        if self.fan_running(rpm_before):
            return

        kick_pwm = percent_to_pwm(self.profile.kickstart_percent, self.pwm_min, self.pwm_max)
        if target_pwm >= kick_pwm:
            self.log(
                f"{utc_now()} profile={self.profile.name} state=kickstart action=skip "
                f"rpm_before={fmt(rpm_before)} target_pwm={target_pwm} "
                "reason=\"target PWM is already at least kickstart PWM\""
            )
            return

        self.log(
            f"{utc_now()} profile={self.profile.name} state=kickstart action=start "
            f"rpm_before={fmt(rpm_before)} kick_pwm={kick_pwm} kick_percent={self.profile.kickstart_percent:.1f} "
            f"duration_s={self.profile.kickstart_s:.1f} target_pwm={target_pwm}"
        )
        self.set_manual_pwm(kick_pwm)
        time.sleep(self.profile.kickstart_s)
        rpm_after = self.current_rpm()
        action = "ok" if self.fan_running(rpm_after) else "warning"
        self.log(
            f"{utc_now()} profile={self.profile.name} state=kickstart action={action} "
            f"rpm_before={fmt(rpm_before)} rpm_after={fmt(rpm_after)} target_pwm={target_pwm}"
        )

    def apply(self, mode: str, target_percent: float | None) -> tuple[int | None, float | None]:
        if mode == "auto":
            if self.dry_run:
                return None, None
            if read_int(self.hwmon.pwm_enable) != 2:
                write_sysfs(self.hwmon.pwm_enable, 2)
            return None, None

        assert target_percent is not None
        target_pwm = percent_to_pwm(target_percent, self.pwm_min, self.pwm_max)
        if self.dry_run:
            return target_pwm, target_percent

        rpm_before = self.current_rpm()
        self.maybe_kickstart(target_pwm, target_percent)
        self.set_manual_pwm(target_pwm)
        if target_pwm > self.pwm_min and not self.fan_running(rpm_before):
            return self.ensure_fan_spinning(target_pwm, target_percent)
        return target_pwm, target_percent

    def log_iteration(
        self,
        snap: Snapshot,
        raw_temp_c: float,
        mode: str,
        applied_percent: float | None,
        applied_pwm: int | None,
        state: str,
        reason: str,
    ) -> None:
        action = "dry-run" if self.dry_run else "set"
        target = "auto" if mode == "auto" else f"{applied_pwm}/{self.pwm_max}({applied_percent:.1f}%)"
        self.log(
            f"{utc_now()} profile={self.profile.name} state={state} action={action} "
            f"sensor={self.control_kind} raw_c={raw_temp_c:.1f} smooth_c={fmt(self.smoothed_temp_c)} "
            f"edge_c={fmt(snap.edge_c)} hotspot_c={fmt(snap.hotspot_c)} mem_c={fmt(snap.mem_c)} "
            f"power_w={fmt(snap.power_w)} gpu_busy={fmt(snap.gpu_busy_percent, '%')} "
            f"fan_rpm={fmt(snap.fan_rpm)} pwm={fmt(snap.pwm)} pwm_enable={fmt(snap.pwm_enable)} "
            f"target={target} reason=\"{reason}\""
        )

    def run_once(self) -> None:
        raw_temp = self.control_temp()
        snap = snapshot(self.hwmon)
        mode, target_percent, state, reason = self.decide(snap, raw_temp)
        applied_pwm, applied_percent = self.apply(mode, target_percent)
        self.log_iteration(snap, raw_temp, mode, applied_percent, applied_pwm, state, reason)
        if mode == "manual":
            self.last_manual_percent = applied_percent
        self.last_mode = mode

    def run(self) -> None:
        while True:
            self.run_once()
            if self.once:
                return
            time.sleep(self.interval_s)

    def require_low_zero_test_conditions(self, snap: Snapshot) -> None:
        reasons = self.zero_entry_reasons(snap)
        if reasons:
            raise SystemExit(
                "Refusing zero-RPM test because idle conditions are not cold/quiet enough: "
                + "; ".join(reasons)
            )

    def ensure_write_access(self) -> None:
        missing = [str(path) for path in (self.hwmon.pwm_enable, self.hwmon.pwm) if path and not os.access(path, os.W_OK)]
        if missing:
            raise SystemExit("PWM sysfs paths are not writable; run with sudo: " + ", ".join(missing))

    def test_temperatures_still_safe(self) -> Snapshot:
        snap = snapshot(self.hwmon)
        exit_reasons = self.zero_exit_reasons(snap)
        if exit_reasons:
            raise RuntimeError("Zero-RPM test became unsafe: " + "; ".join(exit_reasons))
        return snap

    def test_zero_rpm(self) -> None:
        if self.dry_run:
            raise SystemExit("--test-zero-rpm performs real PWM writes; do not combine it with --dry-run")
        self.ensure_write_access()
        start = snapshot(self.hwmon)
        self.log(
            f"{utc_now()} profile={self.profile.name} state=zero-test action=start "
            f"{self.zero_snapshot_text(start)}"
        )
        self.require_low_zero_test_conditions(start)

        stop_started = time.monotonic()
        self.log(
            f"{utc_now()} profile={self.profile.name} state=zero-test action=set-zero "
            f"rpm_before={fmt(start.fan_rpm)} pwm_before={fmt(start.pwm)}"
        )
        self.set_manual_pwm(self.pwm_min)

        stopped = False
        stop_elapsed = 0.0
        last_stop_snap = start
        while stop_elapsed <= self.profile.zero_test_stop_timeout_s:
            time.sleep(1.0)
            last_stop_snap = self.test_temperatures_still_safe()
            stop_elapsed = time.monotonic() - stop_started
            if not self.fan_running(last_stop_snap.fan_rpm):
                stopped = True
                break

        if stopped:
            self.log(
                f"{utc_now()} profile={self.profile.name} state=zero-test action=zero-stop-ok "
                f"rpm_after={fmt(last_stop_snap.fan_rpm)} elapsed_s={stop_elapsed:.1f} "
                f"{self.zero_snapshot_text(last_stop_snap)}"
            )
        else:
            self.log(
                f"{utc_now()} profile={self.profile.name} state=zero-test action=zero-stop-timeout "
                f"rpm_after={fmt(last_stop_snap.fan_rpm)} elapsed_s={stop_elapsed:.1f} "
                f"reason=\"PWM 0 did not stop fans within timeout\""
            )

        kick_pwm = percent_to_pwm(self.profile.kickstart_percent, self.pwm_min, self.pwm_max)
        kick_started = time.monotonic()
        rpm_before_kick = self.current_rpm()
        self.log(
            f"{utc_now()} profile={self.profile.name} state=zero-test action=kickstart-start "
            f"rpm_before={fmt(rpm_before_kick)} kick_pwm={kick_pwm} "
            f"kick_percent={self.profile.kickstart_percent:.1f}"
        )
        self.set_manual_pwm(kick_pwm)

        spin_snap = snapshot(self.hwmon)
        spin_elapsed = 0.0
        while spin_elapsed <= self.profile.zero_test_spinup_timeout_s:
            time.sleep(0.5)
            spin_snap = self.test_temperatures_still_safe()
            spin_elapsed = time.monotonic() - kick_started
            if self.fan_running(spin_snap.fan_rpm):
                break

        if not self.fan_running(spin_snap.fan_rpm):
            raise RuntimeError(
                f"Kickstart failed: RPM stayed {fmt(spin_snap.fan_rpm)} after {spin_elapsed:.1f}s"
            )

        self.log(
            f"{utc_now()} profile={self.profile.name} state=zero-test action=kickstart-ok "
            f"rpm_before={fmt(rpm_before_kick)} rpm_after={fmt(spin_snap.fan_rpm)} "
            f"elapsed_s={spin_elapsed:.1f} kick_pwm={kick_pwm}"
        )

        min_percent, min_pwm, min_rpm = self.find_min_sustain_pwm()
        if min_pwm is None:
            self.log(
                f"{utc_now()} profile={self.profile.name} state=zero-test action=min-sustain-unknown "
                "reason=\"fan stopped before any tested low PWM held RPM\""
            )
        else:
            self.log(
                f"{utc_now()} profile={self.profile.name} state=zero-test action=min-sustain-observed "
                f"min_pwm={min_pwm} min_percent={min_percent:.1f} rpm={fmt(min_rpm)} "
                f"hold_s={self.profile.zero_test_hold_step_s:.1f}"
            )

    def find_min_sustain_pwm(self) -> tuple[float | None, int | None, int | None]:
        observed: tuple[float | None, int | None, int | None] = (None, None, None)
        for percent in (18.0, 16.0, 14.0, 12.0, 10.0, 8.0, 6.0, 4.0, 2.0):
            pwm = percent_to_pwm(percent, self.pwm_min, self.pwm_max)
            self.set_manual_pwm(pwm)
            time.sleep(self.profile.zero_test_hold_step_s)
            snap = self.test_temperatures_still_safe()
            running = self.fan_running(snap.fan_rpm)
            self.log(
                f"{utc_now()} profile={self.profile.name} state=zero-test action=min-sustain-step "
                f"percent={percent:.1f} pwm={pwm} rpm={fmt(snap.fan_rpm)} running={str(running).lower()}"
            )
            if running:
                observed = (percent, pwm, snap.fan_rpm)
            else:
                break
        return observed


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safe amdgpu fan controller for Glyph ROCm training")
    parser.add_argument("--profile", choices=sorted(PROFILES), default=GLYPH_TRAINING.name)
    parser.add_argument("--hwmon", help="Explicit amdgpu hwmon path, for example /sys/class/hwmon/hwmon3")
    parser.add_argument("--report", action="store_true", help="Print detected hwmon paths and capabilities, then exit")
    parser.add_argument("--dry-run", action="store_true", help="Log the fan decision without writing sysfs")
    parser.add_argument("--once", action="store_true", help="Run one control iteration, then restore auto and exit")
    parser.add_argument("--test-zero-rpm", action="store_true", help="Run a guarded zero-RPM stop/start test, then restore auto")
    parser.add_argument("--interval", type=float, default=2.0, help="Seconds between control iterations")
    parser.add_argument(
        "--idle-policy",
        choices=("auto", "manual-low", "zero"),
        default="auto",
        help="auto delegates idle to amdgpu; manual-low uses quiet PWM; zero may stop fans after a long stable idle",
    )
    parser.add_argument("--log-file", type=Path, help="Append logs to this file as well as stdout")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    hwmon = pick_hwmon(args.hwmon)

    if args.report:
        print_report(hwmon)
        return 0

    controller = FanController(
        hwmon,
        PROFILES[args.profile],
        dry_run=args.dry_run,
        once=args.once,
        interval_s=args.interval,
        idle_policy=args.idle_policy,
        log_file=args.log_file,
    )

    def cleanup(reason: str = "process-exit") -> None:
        controller.restore_auto(reason)

    def signal_handler(signum: int, _frame: object) -> None:
        signame = signal.Signals(signum).name
        controller.log(f"{utc_now()} profile={args.profile} state=signal action=received signal={signame}")
        controller.restore_auto(f"signal-{signame}")
        raise SystemExit(128 + signum)

    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        if args.test_zero_rpm:
            controller.test_zero_rpm()
        else:
            controller.run()
    except Exception as exc:
        controller.log(f"{utc_now()} profile={args.profile} state=exception action=abort error={exc}")
        controller.restore_auto("exception")
        raise
    finally:
        controller.restore_auto("normal-exit")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
