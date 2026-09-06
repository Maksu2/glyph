#!/usr/bin/env python3
"""Measure command-to-captured-acoustic latency through PulseAudio.

The measurement starts immediately before spawning ``paplay`` for each click
and ends at the matching acoustic marker delivered by ``parecord``. It therefore
includes process startup, PulseAudio output, Bluetooth/A2DP, speaker DSP and
acoustic propagation, as well as the microphone/ADC/ALSA/PulseAudio capture path
and capture delivery. It is not a pure Bluetooth latency measurement.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import wave
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal as scipy_signal


NS_PER_SECOND = 1_000_000_000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sink", required=True, help="Exact PulseAudio sink name")
    parser.add_argument("--source", required=True, help="Exact PulseAudio source name")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--trials", type=int, default=24)
    parser.add_argument("--interval", type=float, default=1.30)
    parser.add_argument("--warmup", type=float, default=2.0)
    parser.add_argument("--tail", type=float, default=2.0)
    parser.add_argument("--rate", type=int, default=48_000)
    parser.add_argument("--channels", type=int, default=2)
    parser.add_argument("--capture-latency-ms", type=int, default=10)
    parser.add_argument("--capture-process-ms", type=int, default=5)
    parser.add_argument("--click-amplitude", type=float, default=0.40)
    parser.add_argument("--min-correlation", type=float, default=0.05)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("--trials must be positive")
    if args.interval < 0.8:
        parser.error("--interval must be at least 0.8 s")
    if not 0 < args.click_amplitude <= 0.5:
        parser.error("--click-amplitude must be in (0, 0.5]")
    if args.channels != 2:
        parser.error("this test currently requires stereo capture")
    return args


def command_text(command: list[str], check: bool = True) -> str:
    completed = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if check and completed.returncode != 0:
        raise RuntimeError(
            f"Command failed ({completed.returncode}): {' '.join(command)}\n"
            f"{completed.stdout}"
        )
    return completed.stdout


def require_commands() -> None:
    missing = [name for name in ("pactl", "paplay", "parecord", "bluetoothctl") if not shutil.which(name)]
    if missing:
        raise RuntimeError(f"Missing required commands: {', '.join(missing)}")


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    path.mkdir(parents=True, exist_ok=True)
    protected = [path / "raw_capture.wav", path / "results.json", path / "results.csv"]
    existing = [str(item) for item in protected if item.exists()]
    if existing and not overwrite:
        raise RuntimeError(
            "Refusing to overwrite existing result files: " + ", ".join(existing)
        )


def validate_devices(sink: str, source: str) -> None:
    sinks = command_text(["pactl", "list", "short", "sinks"])
    sources = command_text(["pactl", "list", "short", "sources"])
    if not any(line.split("\t")[1:2] == [sink] for line in sinks.splitlines()):
        raise RuntimeError(f"PulseAudio sink not found: {sink}")
    if not any(line.split("\t")[1:2] == [source] for line in sources.splitlines()):
        raise RuntimeError(f"PulseAudio source not found: {source}")


def write_click(path: Path, rate: int, amplitude: float) -> np.ndarray:
    signal_duration = 0.012
    total_duration = 0.040
    count = int(round(signal_duration * rate))
    total = int(round(total_duration * rate))
    t = np.arange(count, dtype=np.float64) / rate
    f0, f1 = 1_500.0, 9_000.0
    sweep_rate = (f1 - f0) / signal_duration
    phase = 2.0 * np.pi * (f0 * t + 0.5 * sweep_rate * t * t)
    window = np.sin(np.pi * (np.arange(count) + 0.5) / count) ** 2
    marker = amplitude * np.sin(phase) * window
    mono = np.zeros(total, dtype=np.float64)
    mono[:count] = marker
    pcm = np.clip(np.round(mono * 32767.0), -32768, 32767).astype("<i2")
    stereo = np.column_stack((pcm, pcm))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(stereo.tobytes())
    return mono[:count]


def extract_pulse_object(full_text: str, object_label: str, name: str) -> str:
    blocks = re.split(rf"(?=^{re.escape(object_label)} #\d+)", full_text, flags=re.MULTILINE)
    for block in blocks:
        if re.search(rf"^\s*Name:\s*{re.escape(name)}\s*$", block, flags=re.MULTILINE):
            return block.strip()
    return ""


def parse_latency(block: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    match = re.search(r"^\s*State:\s*(\S+)", block, flags=re.MULTILINE)
    if match:
        result["state"] = match.group(1)
    match = re.search(
        r"^\s*Latency:\s*(\d+) usec, configured (\d+) usec",
        block,
        flags=re.MULTILINE,
    )
    if match:
        result["latency_usec"] = int(match.group(1))
        result["configured_latency_usec"] = int(match.group(2))
    match = re.search(r"^\s*Sample Specification:\s*(.+)$", block, flags=re.MULTILINE)
    if match:
        result["sample_specification"] = match.group(1).strip()
    return result


def latency_snapshot(source: str, sink: str, label: str) -> dict[str, Any]:
    timestamp_ns = time.monotonic_ns()
    source_text = command_text(["pactl", "list", "sources"])
    sink_text = command_text(["pactl", "list", "sinks"])
    source_block = extract_pulse_object(source_text, "Source", source)
    sink_block = extract_pulse_object(sink_text, "Sink", sink)
    return {
        "label": label,
        "monotonic_ns": timestamp_ns,
        "source": parse_latency(source_block),
        "sink": parse_latency(sink_block),
    }


def sleep_until_ns(target_ns: int) -> None:
    while True:
        remaining = (target_ns - time.monotonic_ns()) / NS_PER_SECOND
        if remaining <= 0:
            return
        time.sleep(max(0.0002, remaining - 0.001))


class RawCapture:
    def __init__(
        self,
        source: str,
        rate: int,
        channels: int,
        latency_ms: int,
        process_ms: int,
    ) -> None:
        self.source = source
        self.rate = rate
        self.channels = channels
        self.frame_bytes = channels * 2
        self.read_bytes = max(self.frame_bytes, int(rate * self.frame_bytes * process_ms / 1000))
        self.command = [
            "parecord",
            "--raw",
            f"--device={source}",
            f"--rate={rate}",
            "--format=s16le",
            f"--channels={channels}",
            f"--latency-msec={latency_ms}",
            f"--process-time-msec={process_ms}",
            "--client-name=audio-alarm-latency-test",
            "--stream-name=raw-acoustic-capture",
        ]
        self.process: subprocess.Popen[bytes] | None = None
        self.parts: list[bytes] = []
        self.chunks: list[dict[str, int]] = []
        self.total_frames = 0
        self.start_request_ns = 0
        self.process_started_ns = 0
        self.first_chunk = threading.Event()
        self.reader: threading.Thread | None = None
        self.stderr = ""
        self.returncode: int | None = None

    def start(self) -> None:
        self.start_request_ns = time.monotonic_ns()
        self.process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
        self.process_started_ns = time.monotonic_ns()
        if self.process.stdout is None:
            raise RuntimeError("parecord stdout pipe was not created")
        self.reader = threading.Thread(target=self._reader_loop, daemon=True)
        self.reader.start()
        if not self.first_chunk.wait(timeout=5.0):
            self.stop()
            raise RuntimeError("No PCM data received from parecord within 5 seconds")

    def _reader_loop(self) -> None:
        assert self.process is not None and self.process.stdout is not None
        fd = self.process.stdout.fileno()
        carry = b""
        while True:
            read_start_ns = time.monotonic_ns()
            try:
                data = os.read(fd, self.read_bytes)
            except OSError:
                break
            read_end_ns = time.monotonic_ns()
            if not data:
                break
            combined = carry + data
            usable = len(combined) - (len(combined) % self.frame_bytes)
            if usable == 0:
                carry = combined
                continue
            aligned, carry = combined[:usable], combined[usable:]
            frames = len(aligned) // self.frame_bytes
            start_frame = self.total_frames
            end_frame = start_frame + frames
            self.parts.append(aligned)
            self.chunks.append(
                {
                    "start_frame": start_frame,
                    "end_frame": end_frame,
                    "read_start_ns": read_start_ns,
                    "read_end_ns": read_end_ns,
                    "read_wait_ns": read_end_ns - read_start_ns,
                }
            )
            self.total_frames = end_frame
            self.first_chunk.set()

    def stop(self) -> None:
        if self.process is None:
            return
        if self.process.poll() is None:
            self.process.send_signal(signal.SIGINT)
            try:
                self.process.wait(timeout=3.0)
            except subprocess.TimeoutExpired:
                self.process.terminate()
                try:
                    self.process.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=2.0)
        if self.reader is not None:
            self.reader.join(timeout=3.0)
        self.returncode = self.process.returncode
        if self.process.stderr is not None:
            self.stderr = self.process.stderr.read().decode("utf-8", errors="replace")

    def pcm_bytes(self) -> bytes:
        return b"".join(self.parts)


def write_capture_wav(path: Path, pcm: bytes, rate: int, channels: int) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(pcm)


def detect_events(
    pcm: bytes,
    chunks: list[dict[str, int]],
    plays: list[dict[str, Any]],
    template: np.ndarray,
    rate: int,
    channels: int,
    interval: float,
    min_correlation: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    audio = np.frombuffer(pcm, dtype="<i2")
    usable = len(audio) - len(audio) % channels
    audio = audio[:usable].reshape(-1, channels).astype(np.float64) / 32768.0
    mono = np.mean(audio, axis=1)
    mono -= np.median(mono)

    sos = scipy_signal.butter(3, (800.0, 11_000.0), btype="bandpass", fs=rate, output="sos")
    filtered = scipy_signal.sosfiltfilt(sos, mono)
    filtered_template = scipy_signal.sosfilt(sos, template - np.mean(template))
    template_energy = float(np.sum(filtered_template * filtered_template))

    ns_per_frame = NS_PER_SECOND / rate
    anchors = np.asarray(
        [chunk["read_end_ns"] - chunk["end_frame"] * ns_per_frame for chunk in chunks],
        dtype=np.float64,
    )
    if len(anchors) < 10:
        raise RuntimeError("Too few capture timestamp anchors")
    stable = anchors[min(10, len(anchors) // 10) :]
    anchor_ns = float(np.percentile(stable, 5.0))
    anchor_median_ns = float(np.median(stable))

    def frame_for_ns(timestamp_ns: int | float) -> int:
        return int(round((timestamp_ns - anchor_ns) / ns_per_frame))

    chunk_ends = np.asarray([chunk["end_frame"] for chunk in chunks], dtype=np.int64)
    results: list[dict[str, Any]] = []
    search_start_s = 0.035
    search_end_s = min(1.05, interval - 0.12)

    for play in plays:
        request_ns = int(play["request_monotonic_ns"])
        start = max(0, frame_for_ns(request_ns + search_start_s * NS_PER_SECOND))
        end = min(len(filtered), frame_for_ns(request_ns + search_end_s * NS_PER_SECOND))
        segment = filtered[start:end]
        needed = len(filtered_template)
        valid = len(segment) >= needed
        edge = False
        if valid:
            correlation = scipy_signal.correlate(
                segment, filtered_template, mode="valid", method="fft"
            )
            local_energy = scipy_signal.fftconvolve(
                segment * segment, np.ones(needed), mode="valid"
            )
            denominator = np.sqrt(np.maximum(local_energy * template_energy, 1e-30))
            normalized = np.abs(correlation) / denominator
            best = int(np.argmax(normalized))
            score = float(normalized[best])
            detected_frame = start + best
            edge = best < 2 or best >= len(normalized) - 2
        else:
            score = 0.0
            detected_frame = start

        detected_ns = int(round(anchor_ns + detected_frame * ns_per_frame))
        latency_ms = (detected_ns - request_ns) / 1_000_000.0
        event_end = min(len(mono), detected_frame + int(0.050 * rate))
        event = mono[detected_frame:event_end]
        noise_end = max(0, detected_frame - int(0.030 * rate))
        noise_start = max(0, noise_end - int(0.120 * rate))
        noise = mono[noise_start:noise_end]
        event_peak = float(np.max(np.abs(event))) if len(event) else 0.0
        event_rms = float(np.sqrt(np.mean(event * event))) if len(event) else 0.0
        noise_rms = float(np.sqrt(np.mean(noise * noise))) if len(noise) else 0.0
        snr_db = 20.0 * math.log10(max(event_rms, 1e-12) / max(noise_rms, 1e-12))

        chunk_index = int(np.searchsorted(chunk_ends, detected_frame, side="right"))
        if chunk_index >= len(chunks):
            chunk_index = len(chunks) - 1
        chunk = chunks[chunk_index]
        local_receipt_ns = int(
            round(
                chunk["read_end_ns"]
                - (chunk["end_frame"] - detected_frame) * ns_per_frame
            )
        )
        mapping_delta_ms = (local_receipt_ns - detected_ns) / 1_000_000.0
        is_valid = bool(
            valid
            and not edge
            and score >= min_correlation
            and play.get("returncode") == 0
            and search_start_s * 1000 <= latency_ms <= search_end_s * 1000
        )
        results.append(
            {
                **play,
                "detected_frame": detected_frame,
                "detected_monotonic_ns": detected_ns,
                "detected_local_receipt_ns": local_receipt_ns,
                "latency_ms": latency_ms,
                "correlation": score,
                "event_peak_dbfs": 20.0 * math.log10(max(event_peak, 1e-12)),
                "event_rms_dbfs": 20.0 * math.log10(max(event_rms, 1e-12)),
                "noise_rms_dbfs": 20.0 * math.log10(max(noise_rms, 1e-12)),
                "snr_db": snr_db,
                "capture_mapping_delta_ms": mapping_delta_ms,
                "valid": is_valid,
                "edge_detection": edge,
            }
        )

    mapping = {
        "method": "5th percentile of chunk read-end minus nominal frame time",
        "anchor_ns": int(round(anchor_ns)),
        "anchor_median_ns": int(round(anchor_median_ns)),
        "anchor_p05_ns": int(round(np.percentile(stable, 5.0))),
        "anchor_p95_ns": int(round(np.percentile(stable, 95.0))),
        "anchor_p05_to_p95_ms": float(
            (np.percentile(stable, 95.0) - np.percentile(stable, 5.0)) / 1_000_000.0
        ),
        "nominal_rate_hz": rate,
        "chunk_count": len(chunks),
    }
    return results, mapping


def statistics(results: list[dict[str, Any]]) -> dict[str, Any]:
    values = np.asarray([row["latency_ms"] for row in results if row["valid"]], dtype=float)
    if len(values) == 0:
        return {"valid_trials": 0, "total_trials": len(results)}
    return {
        "valid_trials": int(len(values)),
        "total_trials": len(results),
        "min_ms": float(np.min(values)),
        "median_ms": float(np.median(values)),
        "mean_ms": float(np.mean(values)),
        "p95_ms": float(np.percentile(values, 95.0)),
        "max_ms": float(np.max(values)),
        "stddev_ms": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
        "peak_to_peak_jitter_ms": float(np.max(values) - np.min(values)),
    }


def write_csv(path: Path, results: list[dict[str, Any]]) -> None:
    fields = [
        "trial",
        "target_monotonic_ns",
        "request_monotonic_ns",
        "popen_return_monotonic_ns",
        "complete_monotonic_ns",
        "schedule_lateness_ms",
        "paplay_runtime_ms",
        "returncode",
        "detected_frame",
        "detected_monotonic_ns",
        "detected_local_receipt_ns",
        "latency_ms",
        "correlation",
        "event_peak_dbfs",
        "event_rms_dbfs",
        "noise_rms_dbfs",
        "snr_db",
        "capture_mapping_delta_ms",
        "valid",
        "edge_detection",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)


def write_plot(path: Path, results: list[dict[str, Any]], stats: dict[str, Any]) -> None:
    valid = [row for row in results if row["valid"]]
    invalid = [row for row in results if not row["valid"]]
    fig, ax = plt.subplots(figsize=(10, 5.2), constrained_layout=True)
    if valid:
        ax.scatter(
            [row["trial"] for row in valid],
            [row["latency_ms"] for row in valid],
            color="#1769aa",
            label="valid trial",
            zorder=3,
        )
        ax.axhline(stats["median_ms"], color="#2e7d32", linewidth=1.5, label="median")
        ax.axhline(
            stats["p95_ms"], color="#ef6c00", linewidth=1.2, linestyle="--", label="p95"
        )
    if invalid:
        ax.scatter(
            [row["trial"] for row in invalid],
            [row["latency_ms"] for row in invalid],
            color="#c62828",
            marker="x",
            label="invalid/low confidence",
            zorder=4,
        )
    ax.set_title("Command-to-captured-acoustic latency (includes capture path)")
    ax.set_xlabel("Trial")
    ax.set_ylabel("Latency [ms]")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.savefig(path, dpi=160)
    plt.close(fig)


def write_markdown(
    path: Path,
    results: list[dict[str, Any]],
    stats: dict[str, Any],
    snapshots: list[dict[str, Any]],
    mapping: dict[str, Any],
) -> None:
    lines = [
        "# Bluetooth acoustic latency test",
        "",
        "This is **measured end-to-end acoustic latency including microphone/capture path**.",
        "It is not presented as pure Bluetooth latency.",
        "",
        "## Statistics",
        "",
    ]
    if stats.get("valid_trials", 0):
        lines.extend(
            [
                f"- Valid: {stats['valid_trials']} / {stats['total_trials']}",
                f"- Minimum: {stats['min_ms']:.3f} ms",
                f"- Median: {stats['median_ms']:.3f} ms",
                f"- Mean: {stats['mean_ms']:.3f} ms",
                f"- p95: {stats['p95_ms']:.3f} ms",
                f"- Maximum: {stats['max_ms']:.3f} ms",
                f"- Standard deviation: {stats['stddev_ms']:.3f} ms",
                f"- Peak-to-peak jitter: {stats['peak_to_peak_jitter_ms']:.3f} ms",
            ]
        )
    else:
        lines.append("No valid detections.")
    lines.extend(
        [
            "",
            "## Capture timing",
            "",
            f"- Mapping: {mapping['method']}",
            f"- Capture anchor p05–p95 spread: {mapping['anchor_p05_to_p95_ms']:.3f} ms",
            "- PulseAudio reported latencies are listed in `results.json`.",
            "",
            "## Per-trial results",
            "",
            "| Trial | Latency ms | Correlation | SNR dB | Peak dBFS | Valid |",
            "|---:|---:|---:|---:|---:|:---:|",
        ]
    )
    for row in results:
        lines.append(
            f"| {row['trial']} | {row['latency_ms']:.3f} | {row['correlation']:.3f} | "
            f"{row['snr_db']:.1f} | {row['event_peak_dbfs']:.1f} | "
            f"{'yes' if row['valid'] else 'no'} |"
        )
    lines.extend(
        [
            "",
            "## Definition",
            "",
            "Start: `time.monotonic_ns()` immediately before spawning one `paplay` process.",
            "",
            "End: matched acoustic marker in the 48 kHz microphone waveform, mapped to the",
            "monotonic clock from continuous small `parecord` reads.",
            "",
            "Included: process startup, PulseAudio output, BlueZ/A2DP, Bluetooth radio,",
            "speaker buffering/DSP, acoustic propagation, microphone, ADC, ALSA/PulseAudio",
            "capture buffering, and delivery to the recording client.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    require_commands()
    prepare_output_dir(args.output_dir, args.overwrite)
    validate_devices(args.sink, args.source)

    snapshots_dir = args.output_dir / "snapshots"
    snapshots_dir.mkdir(exist_ok=True)
    snapshots = {
        "pactl_info.txt": command_text(["pactl", "info"]),
        "pactl_cards.txt": command_text(["pactl", "list", "cards"]),
        "pactl_sinks.txt": command_text(["pactl", "list", "sinks"]),
        "pactl_sources.txt": command_text(["pactl", "list", "sources"]),
        "bluetooth_info.txt": command_text(
            ["bluetoothctl", "info", "04:21:44:06:6B:B9"], check=False
        ),
        "aplay_devices.txt": command_text(["aplay", "-l"], check=False),
        "arecord_devices.txt": command_text(["arecord", "-l"], check=False),
        "amixer_capture.txt": command_text(["amixer", "-c", "1", "sget", "Capture"], check=False),
        "amixer_front_mic_boost.txt": command_text(
            ["amixer", "-c", "1", "sget", "Front Mic Boost"], check=False
        ),
    }
    for filename, content in snapshots.items():
        (snapshots_dir / filename).write_text(content, encoding="utf-8")

    click_path = args.output_dir / "click.wav"
    template = write_click(click_path, args.rate, args.click_amplitude)
    capture = RawCapture(
        args.source,
        args.rate,
        args.channels,
        args.capture_latency_ms,
        args.capture_process_ms,
    )
    pulse_latency: list[dict[str, Any]] = []
    plays: list[dict[str, Any]] = []

    print(f"Starting capture from {args.source}", flush=True)
    capture.start()
    pulse_latency.append(latency_snapshot(args.source, args.sink, "capture_started"))
    base_ns = time.monotonic_ns() + int(args.warmup * NS_PER_SECOND)

    try:
        for index in range(args.trials):
            target_ns = base_ns + int(index * args.interval * NS_PER_SECOND)
            sleep_until_ns(target_ns)
            request_ns = time.monotonic_ns()
            process = subprocess.Popen(
                [
                    "paplay",
                    f"--device={args.sink}",
                    "--client-name=audio-alarm-latency-test",
                    f"--stream-name=latency-click-{index + 1:02d}",
                    str(click_path),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            popen_return_ns = time.monotonic_ns()
            try:
                _, error = process.communicate(timeout=5.0)
            except subprocess.TimeoutExpired:
                process.terminate()
                try:
                    _, error = process.communicate(timeout=2.0)
                except subprocess.TimeoutExpired:
                    process.kill()
                    _, error = process.communicate(timeout=2.0)
            complete_ns = time.monotonic_ns()
            plays.append(
                {
                    "trial": index + 1,
                    "target_monotonic_ns": target_ns,
                    "request_monotonic_ns": request_ns,
                    "popen_return_monotonic_ns": popen_return_ns,
                    "complete_monotonic_ns": complete_ns,
                    "schedule_lateness_ms": (request_ns - target_ns) / 1_000_000.0,
                    "paplay_runtime_ms": (complete_ns - request_ns) / 1_000_000.0,
                    "returncode": process.returncode,
                    "stderr": error.decode("utf-8", errors="replace") if error else "",
                }
            )
            print(
                f"trial={index + 1:02d} paplay_rc={process.returncode} "
                f"runtime_ms={(complete_ns - request_ns) / 1_000_000.0:.1f}",
                flush=True,
            )
            if index == 0:
                pulse_latency.append(latency_snapshot(args.source, args.sink, "after_trial_1"))
            if index + 1 == max(2, args.trials // 2):
                pulse_latency.append(latency_snapshot(args.source, args.sink, "mid_test"))
        time.sleep(args.tail)
        pulse_latency.append(latency_snapshot(args.source, args.sink, "before_capture_stop"))
    finally:
        capture.stop()

    pcm = capture.pcm_bytes()
    raw_wav = args.output_dir / "raw_capture.wav"
    write_capture_wav(raw_wav, pcm, args.rate, args.channels)
    results, mapping = detect_events(
        pcm,
        capture.chunks,
        plays,
        template,
        args.rate,
        args.channels,
        args.interval,
        args.min_correlation,
    )
    stats = statistics(results)

    capture_timing = {
        "command": capture.command,
        "capture_start_request_ns": capture.start_request_ns,
        "capture_process_started_ns": capture.process_started_ns,
        "capture_returncode": capture.returncode,
        "capture_stderr": capture.stderr,
        "total_frames": capture.total_frames,
        "total_duration_s": capture.total_frames / args.rate,
        "chunks": capture.chunks,
    }
    (args.output_dir / "capture_timing.json").write_text(
        json.dumps(capture_timing, indent=2), encoding="utf-8"
    )
    metadata = {
        "schema_version": 1,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "clock": {
            "name": "time.monotonic_ns",
            "implementation": time.get_clock_info("monotonic").implementation,
            "resolution_s": time.get_clock_info("monotonic").resolution,
            "adjustable": time.get_clock_info("monotonic").adjustable,
        },
        "measurement_label": "measured end-to-end acoustic latency including microphone/capture path",
        "measurement_start": "monotonic timestamp immediately before spawning paplay",
        "measurement_end": "matched acoustic marker delivered in continuous parecord capture",
        "includes": [
            "paplay process startup",
            "PulseAudio output path",
            "BlueZ/A2DP and Bluetooth radio",
            "speaker buffering and DSP",
            "acoustic propagation",
            "microphone and ADC",
            "ALSA/PulseAudio capture buffering",
            "parecord delivery",
        ],
        "does_not_claim": "pure Bluetooth latency",
        "sink": args.sink,
        "source": args.source,
        "rate_hz": args.rate,
        "channels": args.channels,
        "trials_requested": args.trials,
        "interval_s": args.interval,
        "warmup_s": args.warmup,
        "tail_s": args.tail,
        "capture_latency_request_ms": args.capture_latency_ms,
        "capture_process_request_ms": args.capture_process_ms,
        "click_amplitude_linear": args.click_amplitude,
        "click_signal_duration_ms": 12.0,
        "click_file_duration_ms": 40.0,
        "minimum_correlation": args.min_correlation,
        "pulse_latency_snapshots": pulse_latency,
        "capture_mapping": mapping,
        "statistics": stats,
        "results": results,
    }
    (args.output_dir / "results.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    write_csv(args.output_dir / "results.csv", results)
    write_plot(args.output_dir / "latency_plot.png", results, stats)
    write_markdown(
        args.output_dir / "latency_report.md", results, stats, pulse_latency, mapping
    )

    print(json.dumps(stats, indent=2), flush=True)
    if stats.get("valid_trials", 0) != args.trials:
        print(
            "WARNING: not all trials passed correlation/edge validation; inspect results.csv",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
