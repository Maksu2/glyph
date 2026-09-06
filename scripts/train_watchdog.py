#!/usr/bin/env python3
"""Start and monitor Glyph training on ROCm, with conservative CPU fallback."""
import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
TRAIN_LOG = LOG_DIR / "train.log"
WATCHDOG_LOG = LOG_DIR / "training-watchdog.log"
STATE_FILE = LOG_DIR / "training-watchdog-state.json"
PAUSE_FILE = LOG_DIR / "training.paused"
LOCK_FILE = Path("/tmp/glyph-training-watchdog.lock")
GPU_COMPOSE = ROOT / "docker-compose.train.rocm.yml"
CPU_COMPOSE = ROOT / "docker-compose.train.yml"
STEP_RE = re.compile(r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*step=\s*(?P<step>\d+).*loss=(?P<loss>[0-9.]+).*tok/s=(?P<toks>[0-9,]+)")
ERROR_RE = re.compile(r"(HSA_STATUS|segmentation fault|core dumped|RuntimeError|Traceback|ROCm|HIP error)", re.IGNORECASE)


def now():
    return datetime.now(timezone.utc).isoformat()


def log(message):
    LOG_DIR.mkdir(exist_ok=True)
    line = f"{now()} {message}"
    with WATCHDOG_LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    print(line, flush=True)


def run(cmd, check=False):
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=check)


def write_state(**kwargs):
    payload = {
        "updated_at": now(),
        **kwargs,
    }
    STATE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def acquire_lock():
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    handle = LOCK_FILE.open("w")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit("Another Glyph training watchdog is already running")
    handle.write(str(os.getpid()))
    handle.flush()
    return handle


def running_trainers():
    proc = run(["docker", "ps", "--format", "{{.Names}}\t{{.Image}}\t{{.Status}}"])
    rows = []
    for line in proc.stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) < 3:
            continue
        name, image, status = parts
        if image in {"ai-model-trainer:cpu", "ai-model-trainer:rocm-gfx1012"}:
            rows.append({"name": name, "image": image, "status": status})
    return rows


def container_running(name):
    proc = run(["docker", "inspect", "-f", "{{.State.Running}}", name])
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def container_status(name):
    proc = run(["docker", "inspect", "-f", "{{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}", name])
    return proc.stdout.strip() if proc.returncode == 0 else "missing"


def save_container_logs(name, reason):
    out_dir = LOG_DIR / "watchdog"
    out_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = out_dir / f"{name}-{reason}-{stamp}.log"
    proc = run(["docker", "logs", "--timestamps", name])
    path.write_text(proc.stdout + proc.stderr, encoding="utf-8", errors="replace")
    log(f"Saved container logs for {name} reason={reason} path={path}")
    return path


def latest_progress():
    latest = None
    if not TRAIN_LOG.exists():
        return None
    with TRAIN_LOG.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = STEP_RE.search(line)
            if match:
                latest = {
                    "timestamp": match.group("ts"),
                    "step": int(match.group("step")),
                    "loss": float(match.group("loss")),
                    "tokens_per_second": int(match.group("toks").replace(",", "")),
                    "line": line.rstrip("\n"),
                }
    return latest


def recent_errors(lines=200):
    if not TRAIN_LOG.exists():
        return []
    tail = TRAIN_LOG.read_text(encoding="utf-8", errors="replace").splitlines()[-lines:]
    return [line for line in tail if ERROR_RE.search(line)]


def checkpoint_candidates():
    candidates = []
    for path in [ROOT / "checkpoints" / "emergency.pt", ROOT / "checkpoints" / "latest.pt"]:
        if path.exists():
            candidates.append(path)
    candidates.extend(sorted((ROOT / "checkpoints").glob("step_*.pt"), key=lambda p: p.stat().st_mtime)[-3:])
    return candidates


def stable_checkpoint(path):
    first = path.stat()
    time.sleep(3)
    second = path.stat()
    return first.st_size == second.st_size and first.st_mtime_ns == second.st_mtime_ns


def best_checkpoint(explicit=None):
    if explicit:
        path = (ROOT / explicit).resolve() if not Path(explicit).is_absolute() else Path(explicit)
        if path.exists() and stable_checkpoint(path):
            return path
        raise SystemExit(f"Explicit checkpoint is missing or unstable: {path}")
    stable = [path for path in checkpoint_candidates() if stable_checkpoint(path)]
    if not stable:
        raise SystemExit("No stable checkpoint available")
    return max(stable, key=lambda p: p.stat().st_mtime_ns)


def container_checkpoint_path(path: Path) -> str:
    path = path.resolve()
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return str(path)
    return str(Path("/workspace") / rel)


def ensure_pause_file(reason):
    PAUSE_FILE.write_text(f"{now()} {reason}\n", encoding="utf-8")


def start_gpu(checkpoint, checkpoint_interval):
    existing = running_trainers()
    if existing:
        raise SystemExit(f"Refusing to start GPU trainer while training container is running: {existing}")
    name = f"glyph-train-rocm-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    cmd = [
        "docker", "compose", "-f", str(GPU_COMPOSE), "run", "--rm", "-d",
        "--name", name,
        "trainer-rocm",
        "python", "train.py",
        "--device", "cuda",
        "--resume", container_checkpoint_path(checkpoint),
        "--checkpoint-interval", str(checkpoint_interval),
    ]
    proc = run(cmd)
    if proc.returncode != 0:
        log(f"GPU start failed: {proc.stdout} {proc.stderr}")
        raise RuntimeError("GPU start failed")
    log(f"Started GPU trainer {name} from {checkpoint}")
    return name


def start_cpu_fallback(checkpoint, checkpoint_interval):
    existing = running_trainers()
    if existing:
        raise SystemExit(f"Refusing to start CPU fallback while trainer is running: {existing}")
    name = f"glyph-train-cpu-fallback-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    cmd = [
        "docker", "compose", "-f", str(CPU_COMPOSE), "run", "--rm", "-d",
        "--name", name,
        "trainer",
        "python", "train.py",
        "--device", "cpu",
        "--resume", container_checkpoint_path(checkpoint),
        "--checkpoint-interval", str(checkpoint_interval),
    ]
    proc = run(cmd)
    if proc.returncode != 0:
        log(f"CPU fallback start failed: {proc.stdout} {proc.stderr}")
        raise RuntimeError("CPU fallback start failed")
    log(f"Started CPU fallback {name} from {checkpoint}")
    return name


def graceful_stop(name, timeout):
    log(f"Stopping {name} with timeout={timeout}s")
    proc = run(["docker", "stop", "-t", str(timeout), name])
    if proc.returncode != 0:
        log(f"Stop returned non-zero for {name}: {proc.stdout} {proc.stderr}")
    save_container_logs(name, "stopped")


def monitor(args, name, backend, gpu_attempts):
    last = latest_progress()
    last_step = last["step"] if last else 0
    last_progress_seen = time.time()
    log(f"Monitoring {backend} container={name} initial_step={last_step}")

    while True:
        time.sleep(args.poll_seconds)
        progress = latest_progress()
        if progress and progress["step"] > last_step:
            last_step = progress["step"]
            last_progress_seen = time.time()
            write_state(
                status="running",
                backend=backend,
                container=name,
                gpu_attempts=gpu_attempts,
                last_progress=progress,
                checkpoint=str(best_checkpoint(None)),
            )

        if not container_running(name):
            status = container_status(name)
            log(f"{backend} container exited: {name} status={status}")
            save_container_logs(name, "exited")
            return "exited"

        stale_for = time.time() - last_progress_seen
        if stale_for > args.stale_minutes * 60:
            errors = recent_errors()
            log(f"{backend} container stale for {stale_for:.0f}s at step={last_step}; recent_errors={len(errors)}")
            graceful_stop(name, args.stop_timeout)
            return "stale"


def main():
    parser = argparse.ArgumentParser(description="Run Glyph GPU training with watchdog and CPU fallback")
    parser.add_argument("--checkpoint", default=None, help="Checkpoint to resume from; default: newest stable emergency/latest/step")
    parser.add_argument("--gpu-retries", type=int, default=2)
    parser.add_argument("--stale-minutes", type=int, default=15)
    parser.add_argument("--poll-seconds", type=int, default=60)
    parser.add_argument("--stop-timeout", type=int, default=300)
    parser.add_argument("--checkpoint-interval", type=int, default=500)
    parser.add_argument("--no-fallback", action="store_true")
    args = parser.parse_args()

    LOG_DIR.mkdir(exist_ok=True)
    acquire_lock()
    ensure_pause_file("GPU watchdog owns training; prevents CPU auto-resume duplicates")

    checkpoint = best_checkpoint(args.checkpoint)
    log(f"Watchdog starting with checkpoint={checkpoint}")

    gpu_attempts = 0
    while gpu_attempts <= args.gpu_retries:
        gpu_attempts += 1
        try:
            name = start_gpu(checkpoint, args.checkpoint_interval)
            write_state(status="starting", backend="ROCm gfx1012", container=name, gpu_attempts=gpu_attempts, checkpoint=str(checkpoint))
            result = monitor(args, name, "ROCm gfx1012", gpu_attempts)
        except Exception as exc:
            log(f"GPU attempt {gpu_attempts} failed before/while starting: {exc}")
            result = "start-failed"

        progress = latest_progress() or {}
        if progress.get("step", 0) >= 200000:
            write_state(status="complete", backend="ROCm gfx1012", container=name if "name" in locals() else None, gpu_attempts=gpu_attempts, last_progress=progress)
            log("Training appears complete; watchdog exiting")
            return

        checkpoint = best_checkpoint(None)
        if gpu_attempts <= args.gpu_retries:
            log(f"Retrying GPU after result={result}; next checkpoint={checkpoint}")
            continue
        break

    if args.no_fallback:
        write_state(status="gpu-failed-no-fallback", backend="none", container=None, gpu_attempts=gpu_attempts, checkpoint=str(checkpoint))
        log("GPU failed and fallback disabled")
        return

    log(f"GPU failed after {gpu_attempts} attempts; starting CPU fallback from {checkpoint}")
    cpu_name = start_cpu_fallback(checkpoint, max(args.checkpoint_interval, 1000))
    write_state(status="fallback-cpu-running", backend="CPU", container=cpu_name, gpu_attempts=gpu_attempts, checkpoint=str(checkpoint))
    monitor(args, cpu_name, "CPU fallback", gpu_attempts)


if __name__ == "__main__":
    main()
