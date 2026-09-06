#!/usr/bin/env python3
"""Reproducible, non-playing analysis for Ludwig Göransson's "Another Name".

The script never opens a PulseAudio/ALSA device.  It uses the already-present
Jellyfin ffmpeg image only as an offline decoder/prober, then performs all
analysis with NumPy/SciPy and exports neutral PNG/CSV/JSON artifacts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
from scipy import ndimage, signal


ANALYSIS_RATE = 22_050
FRAME_LENGTH = 2_048
HOP_LENGTH = 512
JELLYFIN_IMAGE = "jellyfin/jellyfin:latest"
FFMPEG = "/usr/lib/jellyfin-ffmpeg/ffmpeg"
FFPROBE = "/usr/lib/jellyfin-ffmpeg/ffprobe"

INK = "#20242a"
MUTED = "#73777f"
GRID = "#d9dce1"
BLUE = "#356a9a"
GOLD = "#c4932f"
ORANGE = "#c56432"
PINK = "#a84b70"
OLIVE = "#77834b"


def run_container_tool(input_path: Path, executable: str, arguments: list[str]) -> bytes:
    command = [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "-v",
        f"{input_path.parent}:/input:ro",
        "--entrypoint",
        executable,
        JELLYFIN_IMAGE,
        *arguments,
    ]
    completed = subprocess.run(command, check=True, capture_output=True)
    return completed.stdout


def probe_audio(input_path: Path) -> dict[str, Any]:
    raw = run_container_tool(
        input_path,
        FFPROBE,
        [
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_streams",
            "-show_format",
            "-show_chapters",
            "-i",
            f"/input/{input_path.name}",
        ],
    )
    return json.loads(raw)


def decode_mono(input_path: Path, rate: int) -> np.ndarray:
    raw = run_container_tool(
        input_path,
        FFMPEG,
        [
            "-v",
            "error",
            "-i",
            f"/input/{input_path.name}",
            "-map",
            "0:a:0",
            "-vn",
            "-ac",
            "1",
            "-ar",
            str(rate),
            "-f",
            "f32le",
            "pipe:1",
        ],
    )
    audio = np.frombuffer(raw, dtype="<f4").astype(np.float64)
    if audio.size == 0:
        raise RuntimeError("Decoder returned no PCM samples")
    audio -= float(np.mean(audio))
    return audio


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def robust_z(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    median = float(np.median(values))
    mad = float(np.median(np.abs(values - median)))
    scale = 1.4826 * mad
    if scale < 1e-10:
        scale = float(np.std(values)) or 1.0
    return (values - median) / scale


def format_time(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    minutes = int(seconds // 60)
    remaining = seconds - minutes * 60
    return f"{minutes}:{remaining:06.3f}"


def axis_time(value: float, _position: int) -> str:
    minutes = int(max(0.0, value) // 60)
    seconds = int(round(max(0.0, value) - minutes * 60))
    if seconds == 60:
        minutes += 1
        seconds = 0
    return f"{minutes}:{seconds:02d}"


def frame_signal(audio: np.ndarray, frame_length: int, hop_length: int) -> np.ndarray:
    frame_count = 1 + (len(audio) - frame_length) // hop_length
    if frame_count <= 0:
        raise RuntimeError("Audio is shorter than one analysis frame")
    shape = (frame_count, frame_length)
    strides = (audio.strides[0] * hop_length, audio.strides[0])
    return np.lib.stride_tricks.as_strided(audio, shape=shape, strides=strides)


def estimate_tempo(onset: np.ndarray, frame_rate: float) -> dict[str, Any]:
    envelope = np.maximum(robust_z(onset), 0.0)
    envelope -= float(np.mean(envelope))
    autocorrelation = signal.correlate(envelope, envelope, mode="full", method="fft")
    autocorrelation = autocorrelation[len(envelope) - 1 :]
    overlap = np.arange(len(envelope), 0, -1, dtype=np.float64)
    autocorrelation /= np.maximum(overlap, 1.0)
    if autocorrelation[0] > 0:
        autocorrelation /= autocorrelation[0]

    minimum_bpm, maximum_bpm = 50.0, 190.0
    min_lag = max(1, int(math.floor(60.0 * frame_rate / maximum_bpm)))
    max_lag = min(len(autocorrelation) - 1, int(math.ceil(60.0 * frame_rate / minimum_bpm)))
    search = autocorrelation[min_lag : max_lag + 1]
    peaks, properties = signal.find_peaks(search, distance=2, prominence=0.002)
    if not len(peaks):
        peaks = np.asarray([int(np.argmax(search))])
        properties = {"prominences": np.asarray([0.0])}

    candidates: list[dict[str, float]] = []
    for index, peak in enumerate(peaks):
        lag = int(peak + min_lag)
        bpm = 60.0 * frame_rate / lag
        period = 60.0 * frame_rate / bpm
        period_i = max(1, int(round(period)))
        phase_means = np.asarray(
            [float(np.mean(np.maximum(onset[phase::period_i], 0.0))) for phase in range(period_i)]
        )
        alignment = (float(np.max(phase_means)) - float(np.mean(phase_means))) / (
            float(np.std(phase_means)) + 1e-9
        )
        ac = float(autocorrelation[lag])
        prominence = float(properties.get("prominences", np.zeros(len(peaks)))[index])
        candidates.append(
            {
                "bpm": bpm,
                "lag_frames": lag,
                "autocorrelation": ac,
                "prominence": prominence,
                "grid_alignment_z": alignment,
                "score": ac + 0.025 * alignment + 0.25 * prominence,
            }
        )

    candidates.sort(key=lambda item: item["score"], reverse=True)
    candidates = candidates[:10]
    selected = candidates[0]
    bpm = selected["bpm"]
    period = 60.0 * frame_rate / bpm
    period_i = max(1, int(round(period)))

    alignment_envelope = ndimage.gaussian_filter1d(np.maximum(onset, 0.0), sigma=1.4)
    phase_scores = np.asarray(
        [float(np.sum(alignment_envelope[phase::period_i])) for phase in range(period_i)]
    )
    phase = int(np.argmax(phase_scores))
    base_beats = np.arange(phase, len(onset), period, dtype=np.float64)
    snap_radius = max(1, int(round(0.10 * frame_rate)))
    beat_frames: list[int] = []
    for predicted in base_beats:
        center = int(round(predicted))
        start = max(0, center - snap_radius)
        end = min(len(onset), center + snap_radius + 1)
        if end <= start:
            continue
        snapped = start + int(np.argmax(alignment_envelope[start:end]))
        if beat_frames and snapped <= beat_frames[-1]:
            snapped = center
        if 0 <= snapped < len(onset) and (not beat_frames or snapped > beat_frames[-1]):
            beat_frames.append(snapped)

    beat_strengths = np.asarray([float(onset[index]) for index in beat_frames])
    phase4_means = np.asarray(
        [float(np.mean(beat_strengths[offset::4])) if len(beat_strengths[offset::4]) else 0.0 for offset in range(4)]
    )
    downbeat_phase = int(np.argmax(phase4_means))
    ordered = np.sort(phase4_means)
    downbeat_contrast = (float(ordered[-1] - ordered[-2]) / (float(np.std(phase4_means)) + 1e-9))
    periodicity = float(selected["autocorrelation"])
    alignment = float(selected["grid_alignment_z"])
    if periodicity >= 0.13 and alignment >= 1.2:
        confidence = "high"
    elif periodicity >= 0.07 and alignment >= 0.7:
        confidence = "medium"
    else:
        confidence = "low"
    downbeat_confidence = "medium" if downbeat_contrast >= 0.65 else "low"

    return {
        "selected_bpm": float(bpm),
        "selected_period_s": float(60.0 / bpm),
        "confidence": confidence,
        "autocorrelation": periodicity,
        "grid_alignment_z": alignment,
        "tempo_candidates": candidates,
        "beat_frames": beat_frames,
        "beat_strengths": beat_strengths.tolist(),
        "downbeat_phase_mod4": downbeat_phase,
        "downbeat_phase_means": phase4_means.tolist(),
        "downbeat_contrast": downbeat_contrast,
        "downbeat_confidence": downbeat_confidence,
    }


def calculate_novelty(features: np.ndarray, frame_rate: float) -> np.ndarray:
    window = max(2, int(round(2.5 * frame_rate)))
    count = features.shape[1]
    cumulative = np.pad(np.cumsum(features, axis=1), ((0, 0), (1, 0)))
    novelty = np.zeros(count, dtype=np.float64)
    for index in range(window, count - window):
        previous = (cumulative[:, index] - cumulative[:, index - window]) / window
        following = (cumulative[:, index + window] - cumulative[:, index]) / window
        novelty[index] = float(np.linalg.norm(following - previous))
    novelty = ndimage.gaussian_filter1d(novelty, sigma=max(1.0, 0.35 * frame_rate))
    return novelty


def waveform_envelope(audio: np.ndarray, rate: int, bins: int = 2_400) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    edges = np.linspace(0, len(audio), bins + 1, dtype=int)
    minimum = np.empty(bins, dtype=np.float64)
    maximum = np.empty(bins, dtype=np.float64)
    for index in range(bins):
        chunk = audio[edges[index] : edges[index + 1]]
        minimum[index] = float(np.min(chunk)) if len(chunk) else 0.0
        maximum[index] = float(np.max(chunk)) if len(chunk) else 0.0
    times = ((edges[:-1] + edges[1:]) * 0.5) / rate
    return times, minimum, maximum


def load_cues(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"macro_cues": [], "selected_micro_times_s": []}
    return json.loads(path.read_text(encoding="utf-8"))


def style_axis(axis: plt.Axes, duration: float) -> None:
    axis.set_xlim(0.0, duration)
    axis.xaxis.set_major_formatter(FuncFormatter(axis_time))
    axis.grid(axis="y", color=GRID, linewidth=0.7, alpha=0.8)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_color(GRID)
    axis.spines["bottom"].set_color(GRID)
    axis.tick_params(colors=MUTED, labelsize=9)


def add_cue_lines(axis: plt.Axes, cues: dict[str, Any], annotate: bool = False) -> None:
    palette = {
        "gradual": BLUE,
        "accent": ORANGE,
        "structural": GOLD,
        "climax": PINK,
        "ending": OLIVE,
    }
    for cue in cues.get("macro_cues", []):
        moment = float(cue["track_time_s"])
        color = palette.get(str(cue.get("cue_type", "structural")), GOLD)
        axis.axvline(moment, color=color, linewidth=1.0, alpha=0.78)
        if annotate:
            axis.annotate(
                str(cue.get("short_label", cue.get("id", "cue"))),
                xy=(moment, 1.0),
                xycoords=("data", "axes fraction"),
                xytext=(3, -4),
                textcoords="offset points",
                rotation=90,
                ha="left",
                va="top",
                color=INK,
                fontsize=7.5,
            )


def save_plots(
    output_dir: Path,
    audio: np.ndarray,
    rate: int,
    times: np.ndarray,
    rms_db: np.ndarray,
    rms_smooth_db: np.ndarray,
    onset: np.ndarray,
    onset_peaks: np.ndarray,
    centroid: np.ndarray,
    low_ratio: np.ndarray,
    high_ratio: np.ndarray,
    beat_times: np.ndarray,
    downbeat_times: np.ndarray,
    frequencies: np.ndarray,
    magnitude: np.ndarray,
    cues: dict[str, Any],
) -> None:
    duration = len(audio) / rate
    wave_t, wave_min, wave_max = waveform_envelope(audio, rate)

    figure, axis = plt.subplots(figsize=(14, 4.2), constrained_layout=True)
    axis.fill_between(wave_t, wave_min, wave_max, color=BLUE, alpha=0.72, linewidth=0)
    add_cue_lines(axis, cues)
    axis.set_title("Another Name — waveform (mono analysis decode)", loc="left", color=INK, weight="semibold")
    axis.set_ylabel("Amplitude", color=MUTED)
    axis.set_xlabel("Track time", color=MUTED)
    style_axis(axis, duration)
    figure.savefig(output_dir / "waveform.png", dpi=180, facecolor="white")
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(14, 4.2), constrained_layout=True)
    axis.plot(times, rms_db, color=BLUE, linewidth=0.65, alpha=0.45, label="RMS frame")
    axis.plot(times, rms_smooth_db, color=INK, linewidth=1.7, label="RMS smoothed 1.5 s")
    add_cue_lines(axis, cues)
    axis.set_title("Another Name — RMS loudness envelope", loc="left", color=INK, weight="semibold")
    axis.set_ylabel("dBFS (RMS)", color=MUTED)
    axis.set_xlabel("Track time", color=MUTED)
    axis.legend(frameon=False, ncol=2, loc="lower right")
    style_axis(axis, duration)
    figure.savefig(output_dir / "loudness.png", dpi=180, facecolor="white")
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(14, 4.2), constrained_layout=True)
    axis.plot(times, onset, color=INK, linewidth=0.8, label="Spectral-flux onset strength")
    axis.scatter(times[onset_peaks], onset[onset_peaks], s=13, color=ORANGE, label="Detected transients", zorder=3)
    for moment in cues.get("selected_micro_times_s", []):
        axis.axvline(float(moment), color=GOLD, linewidth=0.8, alpha=0.5)
    add_cue_lines(axis, cues)
    axis.set_title("Another Name — onset strength and selected transients", loc="left", color=INK, weight="semibold")
    axis.set_ylabel("Normalized strength", color=MUTED)
    axis.set_xlabel("Track time", color=MUTED)
    axis.legend(frameon=False, ncol=2, loc="upper right")
    style_axis(axis, duration)
    figure.savefig(output_dir / "onset.png", dpi=180, facecolor="white")
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(14, 4.5), constrained_layout=True)
    axis.plot(times, onset, color=MUTED, linewidth=0.75, alpha=0.75, label="Onset strength")
    axis.vlines(beat_times, 0.0, 0.18, color=BLUE, linewidth=0.65, alpha=0.5, label="Estimated beats")
    axis.vlines(downbeat_times, 0.0, 0.30, color=GOLD, linewidth=1.1, alpha=0.9, label="Tentative downbeats")
    for moment in cues.get("selected_micro_times_s", []):
        axis.axvline(float(moment), color=ORANGE, linewidth=1.0, alpha=0.72)
    add_cue_lines(axis, cues)
    axis.set_title("Another Name — estimated beat grid (downbeats are lower-confidence)", loc="left", color=INK, weight="semibold")
    axis.set_ylabel("Onset / beat markers", color=MUTED)
    axis.set_xlabel("Track time", color=MUTED)
    axis.legend(frameon=False, ncol=3, loc="upper right")
    style_axis(axis, duration)
    figure.savefig(output_dir / "beat_grid.png", dpi=180, facecolor="white")
    plt.close(figure)

    keep = (frequencies >= 40.0) & (frequencies <= 11_000.0)
    spectrogram_db = 20.0 * np.log10(np.maximum(magnitude[keep], 1e-8))
    vmax = float(np.percentile(spectrogram_db, 99.5))
    vmin = vmax - 70.0
    figure, axis = plt.subplots(figsize=(14, 5.0), constrained_layout=True)
    mesh = axis.pcolormesh(times, frequencies[keep], spectrogram_db, shading="auto", cmap="magma", vmin=vmin, vmax=vmax)
    add_cue_lines(axis, cues)
    axis.set_yscale("log")
    axis.set_ylim(40.0, 11_000.0)
    axis.set_yticks([50, 100, 250, 500, 1000, 2000, 5000, 10_000])
    axis.get_yaxis().set_major_formatter(lambda value, _pos: f"{int(value)}")
    axis.set_title("Another Name — log-frequency spectrogram", loc="left", color=INK, weight="semibold")
    axis.set_ylabel("Frequency (Hz)", color=MUTED)
    axis.set_xlabel("Track time", color=MUTED)
    axis.xaxis.set_major_formatter(FuncFormatter(axis_time))
    colorbar = figure.colorbar(mesh, ax=axis, pad=0.01)
    colorbar.set_label("Magnitude (dB, relative)")
    figure.savefig(output_dir / "spectrogram.png", dpi=180, facecolor="white")
    plt.close(figure)

    figure, axes = plt.subplots(4, 1, figsize=(16, 12), sharex=True, constrained_layout=True)
    axes[0].fill_between(wave_t, wave_min, wave_max, color=BLUE, alpha=0.70, linewidth=0)
    axes[0].set_ylabel("Waveform")
    axes[1].plot(times, rms_smooth_db, color=INK, linewidth=1.5)
    axes[1].set_ylabel("RMS dBFS")
    axes[2].plot(times, onset, color=MUTED, linewidth=0.75)
    axes[2].scatter(times[onset_peaks], onset[onset_peaks], s=9, color=ORANGE, zorder=3)
    for moment in cues.get("selected_micro_times_s", []):
        axes[2].axvline(float(moment), color=GOLD, linewidth=0.75, alpha=0.55)
    axes[2].set_ylabel("Onset")
    axes[3].plot(times, centroid / 1000.0, color=BLUE, linewidth=1.0, label="Centroid (kHz)")
    axes[3].plot(times, low_ratio * 5.0, color=OLIVE, linewidth=0.9, alpha=0.8, label="Low-band ratio ×5")
    axes[3].plot(times, high_ratio * 5.0, color=PINK, linewidth=0.9, alpha=0.8, label="High-band ratio ×5")
    axes[3].set_ylabel("Spectrum")
    axes[3].legend(frameon=False, ncol=3, loc="upper right")
    axes[3].set_xlabel("Track time")
    for index, axis in enumerate(axes):
        add_cue_lines(axis, cues, annotate=index == 0)
        style_axis(axis, duration)
    figure.suptitle("Another Name — audio structure and choreography cues", x=0.01, ha="left", color=INK, weight="semibold", fontsize=15)
    figure.savefig(output_dir / "analysis_overview.png", dpi=180, facecolor="white")
    plt.close(figure)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--cues-json", type=Path)
    args = parser.parse_args()

    input_path = args.input.resolve()
    output_dir = args.output_dir.resolve()
    if not input_path.is_file():
        raise SystemExit(f"Input file does not exist: {input_path}")
    output_dir.mkdir(parents=True, exist_ok=True)

    probe = probe_audio(input_path)
    audio = decode_mono(input_path, ANALYSIS_RATE)
    duration = len(audio) / ANALYSIS_RATE
    frames = frame_signal(audio, FRAME_LENGTH, HOP_LENGTH)
    times = (np.arange(len(frames)) * HOP_LENGTH + FRAME_LENGTH / 2.0) / ANALYSIS_RATE
    rms = np.sqrt(np.mean(frames * frames, axis=1))
    rms_db = 20.0 * np.log10(np.maximum(rms, 1e-10))
    frame_rate = ANALYSIS_RATE / HOP_LENGTH
    rms_smooth_db = ndimage.gaussian_filter1d(rms_db, sigma=max(1.0, 0.75 * frame_rate))

    frequencies, stft_times, spectrum = signal.stft(
        audio,
        fs=ANALYSIS_RATE,
        window="hann",
        nperseg=FRAME_LENGTH,
        noverlap=FRAME_LENGTH - HOP_LENGTH,
        nfft=FRAME_LENGTH,
        boundary=None,
        padded=False,
    )
    magnitude = np.abs(spectrum)
    times = stft_times
    frame_count = min(len(times), len(rms_db), magnitude.shape[1])
    times = times[:frame_count]
    rms_db = rms_db[:frame_count]
    rms_smooth_db = rms_smooth_db[:frame_count]
    magnitude = magnitude[:, :frame_count]

    useful = (frequencies >= 70.0) & (frequencies <= 10_500.0)
    log_magnitude = np.log1p(80.0 * magnitude[useful])
    positive_difference = np.maximum(np.diff(log_magnitude, axis=1, prepend=log_magnitude[:, :1]), 0.0)
    raw_onset = np.sqrt(np.mean(positive_difference * positive_difference, axis=0))
    raw_onset = ndimage.gaussian_filter1d(raw_onset, sigma=0.8)
    onset_scale = float(np.percentile(raw_onset, 95.0)) or 1.0
    onset = np.clip(raw_onset / onset_scale, 0.0, None)
    onset_peaks, onset_properties = signal.find_peaks(
        onset,
        distance=max(1, int(round(0.14 * frame_rate))),
        prominence=max(0.035, float(np.percentile(onset, 65.0)) * 0.10),
        height=float(np.percentile(onset, 62.0)),
    )

    power = magnitude * magnitude
    power_sum = np.sum(power, axis=0) + 1e-20
    centroid = np.sum(frequencies[:, None] * power, axis=0) / power_sum
    low_ratio = np.sum(power[(frequencies >= 35.0) & (frequencies < 250.0)], axis=0) / power_sum
    mid_ratio = np.sum(power[(frequencies >= 250.0) & (frequencies < 2_000.0)], axis=0) / power_sum
    high_ratio = np.sum(power[(frequencies >= 2_000.0) & (frequencies <= 10_500.0)], axis=0) / power_sum

    chroma = np.zeros((12, frame_count), dtype=np.float64)
    chroma_bins = np.where((frequencies >= 55.0) & (frequencies <= 5_000.0))[0]
    midi = np.rint(69.0 + 12.0 * np.log2(frequencies[chroma_bins] / 440.0)).astype(int)
    for pitch_class in range(12):
        selected_bins = chroma_bins[np.mod(midi, 12) == pitch_class]
        if len(selected_bins):
            chroma[pitch_class] = np.sum(power[selected_bins], axis=0)
    chroma /= np.maximum(np.sum(chroma, axis=0, keepdims=True), 1e-20)

    tempo = estimate_tempo(onset, frame_rate)
    beat_frames = np.asarray(tempo.pop("beat_frames"), dtype=int)
    beat_strengths = np.asarray(tempo.pop("beat_strengths"), dtype=np.float64)
    beat_times = times[np.clip(beat_frames, 0, len(times) - 1)]
    downbeat_mask = np.mod(np.arange(len(beat_frames)), 4) == int(tempo["downbeat_phase_mod4"])
    downbeat_times = beat_times[downbeat_mask]

    feature_rows = [
        robust_z(rms_smooth_db),
        robust_z(np.log1p(centroid)),
        robust_z(low_ratio),
        robust_z(mid_ratio),
        robust_z(high_ratio),
        robust_z(ndimage.gaussian_filter1d(onset, sigma=max(1.0, 0.30 * frame_rate))),
    ]
    feature_rows.extend(0.45 * robust_z(row) for row in chroma)
    feature_matrix = np.vstack(feature_rows)
    novelty = calculate_novelty(feature_matrix, frame_rate)
    novelty_prominence = max(float(np.std(novelty)) * 0.35, 0.05)
    boundary_peaks, boundary_properties = signal.find_peaks(
        novelty,
        distance=max(1, int(round(4.0 * frame_rate))),
        prominence=novelty_prominence,
    )
    boundary_records: list[dict[str, Any]] = []
    for index, frame in enumerate(boundary_peaks):
        moment = float(times[frame])
        if moment < 1.0 or moment > duration - 1.0:
            continue
        boundary_records.append(
            {
                "time_s": moment,
                "time": format_time(moment),
                "novelty": float(novelty[frame]),
                "prominence": float(boundary_properties["prominences"][index]),
                "rms_dbfs": float(rms_smooth_db[frame]),
                "centroid_hz": float(centroid[frame]),
                "low_band_ratio": float(low_ratio[frame]),
                "high_band_ratio": float(high_ratio[frame]),
            }
        )
    boundary_records.sort(key=lambda item: item["time_s"])

    energy_score = (
        robust_z(rms_smooth_db)
        + 0.30 * robust_z(high_ratio)
        + 0.20 * robust_z(ndimage.gaussian_filter1d(onset, sigma=max(1.0, frame_rate)))
    )
    energy_score = ndimage.gaussian_filter1d(energy_score, sigma=max(1.0, frame_rate))
    eligible = (times >= duration * 0.25) & (times <= duration * 0.96)
    climax_frame = int(np.flatnonzero(eligible)[int(np.argmax(energy_score[eligible]))])
    climax_time = float(times[climax_frame])

    final_region = np.flatnonzero(times >= duration * 0.74)
    fade_frame = int(final_region[0])
    if len(final_region):
        derivative = ndimage.gaussian_filter1d(np.gradient(rms_smooth_db), sigma=max(1.0, 0.8 * frame_rate))
        candidate_final = [record for record in boundary_records if record["time_s"] >= duration * 0.72]
        if candidate_final:
            fade_time = max(candidate_final, key=lambda record: record["prominence"])["time_s"]
            fade_frame = int(np.argmin(np.abs(times - fade_time)))
        else:
            fade_frame = int(final_region[int(np.argmin(derivative[final_region]))])
    fade_time = float(times[fade_frame])

    stream = next(item for item in probe.get("streams", []) if item.get("codec_type") == "audio")
    format_info = probe.get("format", {})
    normalized_metadata = {
        "source_path": str(input_path),
        "source_sha256": sha256(input_path),
        "size_bytes": input_path.stat().st_size,
        "title": format_info.get("tags", {}).get("title"),
        "artist": format_info.get("tags", {}).get("artist"),
        "album": format_info.get("tags", {}).get("album"),
        "date": format_info.get("tags", {}).get("date"),
        "duration_s_container": float(format_info.get("duration", duration)),
        "duration_s_decoded": duration,
        "codec": stream.get("codec_name"),
        "codec_long_name": stream.get("codec_long_name"),
        "bit_rate_stream_bps": int(stream["bit_rate"]) if stream.get("bit_rate") else None,
        "bit_rate_container_bps": int(format_info["bit_rate"]) if format_info.get("bit_rate") else None,
        "sample_rate_hz": int(stream["sample_rate"]),
        "channels": int(stream["channels"]),
        "channel_layout": stream.get("channel_layout"),
        "format_name": format_info.get("format_name"),
        "analysis_decode": {
            "sample_rate_hz": ANALYSIS_RATE,
            "channels": 1,
            "sample_format": "float32le",
            "playback_performed": False,
            "decoder": f"{JELLYFIN_IMAGE}:{FFMPEG}",
        },
        "ffprobe": probe,
    }
    (output_dir / "audio_metadata.json").write_text(
        json.dumps(normalized_metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    with (output_dir / "analysis_frames.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "time_s",
                "rms_dbfs",
                "rms_smooth_dbfs",
                "onset_strength",
                "spectral_centroid_hz",
                "low_band_ratio",
                "mid_band_ratio",
                "high_band_ratio",
                "structural_novelty",
                "energy_score",
            ]
        )
        for values in zip(
            times,
            rms_db,
            rms_smooth_db,
            onset,
            centroid,
            low_ratio,
            mid_ratio,
            high_ratio,
            novelty,
            energy_score,
        ):
            writer.writerow([f"{float(value):.9f}" for value in values])

    with (output_dir / "onsets.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["index", "time_s", "time", "strength", "prominence"])
        for index, frame in enumerate(onset_peaks):
            writer.writerow(
                [
                    index + 1,
                    f"{float(times[frame]):.9f}",
                    format_time(times[frame]),
                    f"{float(onset[frame]):.9f}",
                    f"{float(onset_properties['prominences'][index]):.9f}",
                ]
            )

    with (output_dir / "beat_grid.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["beat_index", "time_s", "time", "tentative_downbeat", "onset_strength"])
        for index, (moment, strength) in enumerate(zip(beat_times, beat_strengths)):
            writer.writerow(
                [
                    index + 1,
                    f"{float(moment):.9f}",
                    format_time(moment),
                    str(bool(downbeat_mask[index])).lower(),
                    f"{float(strength):.9f}",
                ]
            )

    with (output_dir / "section_candidates.csv").open("w", newline="", encoding="utf-8") as handle:
        fieldnames = list(boundary_records[0]) if boundary_records else ["time_s"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(boundary_records)

    summary = {
        "schema_version": 1,
        "source": normalized_metadata,
        "analysis_parameters": {
            "sample_rate_hz": ANALYSIS_RATE,
            "frame_length": FRAME_LENGTH,
            "hop_length": HOP_LENGTH,
            "frame_rate_hz": frame_rate,
            "structural_comparison_window_s": 2.5,
        },
        "signal": {
            "decoded_duration_s": duration,
            "sample_peak_dbfs": float(20.0 * math.log10(max(float(np.max(np.abs(audio))), 1e-10))),
            "integrated_rms_dbfs": float(20.0 * math.log10(max(float(np.sqrt(np.mean(audio * audio))), 1e-10))),
            "rms_min_smoothed_dbfs": float(np.min(rms_smooth_db)),
            "rms_max_smoothed_dbfs": float(np.max(rms_smooth_db)),
            "rms_dynamic_range_smoothed_db": float(np.max(rms_smooth_db) - np.min(rms_smooth_db)),
        },
        "rhythm": {
            **tempo,
            "beat_count": int(len(beat_times)),
            "first_beat_s": float(beat_times[0]) if len(beat_times) else None,
            "last_beat_s": float(beat_times[-1]) if len(beat_times) else None,
        },
        "transients": {
            "detected_count": int(len(onset_peaks)),
            "strongest": [
                {
                    "time_s": float(times[index]),
                    "time": format_time(times[index]),
                    "strength": float(onset[index]),
                }
                for index in onset_peaks[np.argsort(onset[onset_peaks])[-30:][::-1]]
            ],
        },
        "structure": {
            "boundary_candidates": boundary_records,
            "climax_candidate_s": climax_time,
            "climax_candidate": format_time(climax_time),
            "ending_or_fade_candidate_s": fade_time,
            "ending_or_fade_candidate": format_time(fade_time),
        },
        "limitations": [
            "Tempo and downbeats are estimated from spectral flux without source stems.",
            "Downbeat phase is tentative and must be checked against musical listening before implementation.",
            "Section candidates are evidence for editorial decisions, not automatic final cue points.",
            "No audio playback was performed by this script.",
        ],
    }
    (output_dir / "analysis_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    cues = load_cues(args.cues_json)
    save_plots(
        output_dir,
        audio,
        ANALYSIS_RATE,
        times,
        rms_db,
        rms_smooth_db,
        onset,
        onset_peaks,
        centroid,
        low_ratio,
        high_ratio,
        beat_times,
        downbeat_times,
        frequencies,
        magnitude,
        cues,
    )

    print(json.dumps({
        "confirmed_file": str(input_path),
        "duration_s": duration,
        "selected_bpm": tempo["selected_bpm"],
        "tempo_confidence": tempo["confidence"],
        "transients": len(onset_peaks),
        "boundary_candidates": len(boundary_records),
        "climax_candidate_s": climax_time,
        "ending_candidate_s": fade_time,
        "output_dir": str(output_dir),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
