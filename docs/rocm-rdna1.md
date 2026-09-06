# ROCm on RX 5500 XT / gfx1012

This is an experimental, unofficial ROCm path for Glyph-27M on the homelab RX 5500 XT.

## Status

- GPU: AMD Radeon RX 5500 XT / Navi 14 / `gfx1012`
- Official ROCm support: no
- Host ROCm install: not required
- Working path found: TheRock multi-arch PyTorch wheel with `device-gfx1012`
- Do not use `HSA_OVERRIDE_GFX_VERSION` for this path

The official `rocm/pytorch:latest` image can see the GPU, but it crashed or hung on trivial CUDA/HIP tensor allocation. The TheRock `torch[device-gfx1012]` wheel worked without the override.

## Probe Results

The synthetic Glyph-27M forward/backward test completed on GPU:

```text
torch 2.12.0+rocm7.14.0a20260521
hip 7.13.0
gpu AMD Radeon RX 5500 XT
Glyph-27M: 6 layers, 8 heads, d_model=512, vocab=16000, context=256
batch 32 x context 256: about 11.9k tokens/s synthetic forward/backward
GPU memory allocated: about 1.0 GiB
```

This is a synthetic test with random token batches. Real training can be slower because of checkpoint loading, validation, logging, data movement, thermal limits and optimizer state behavior.

## Build

```bash
docker compose -f docker-compose.train.rocm.yml build trainer-rocm
```

## Smoke Test

This does not read datasets or checkpoints and does not write training checkpoints.

```bash
docker compose -f docker-compose.train.rocm.yml run --rm trainer-rocm \
  python scripts/rocm_gfx1012_probe.py --batch-size 32 --steps 3
```

## Real Training

Do not run ROCm training at the same time as the existing CPU trainer unless you deliberately isolate logs and checkpoints. Two trainers writing to the same `checkpoints/latest.pt` would be a bad idea.

Before switching from CPU to GPU:

1. Run the ROCm probe.
2. Stop the CPU trainer gracefully with `docker stop -t 300 <container>`.
3. Create a pre-GPU snapshot.
4. Run a short `--max-steps` GPU resume test.
5. Start the watchdog for long training.

Short resume smoke test:

```bash
docker compose -f docker-compose.train.rocm.yml run --rm trainer-rocm \
  python train.py --device cuda --resume checkpoints/emergency.pt --max-steps 10 --checkpoint-interval 500
```

Long training should be started through the watchdog:

```bash
systemctl --user start glyph-training-watchdog.service
```

The current service runs:

```bash
python3 scripts/train_watchdog.py --checkpoint checkpoints/latest.pt \
  --checkpoint-interval 500 --gpu-retries 2 --stale-minutes 15
```

The watchdog creates `logs/training.paused`, which prevents the CPU auto-resume scheduler from starting a duplicate CPU trainer while GPU training is active. The service is enabled in user-systemd so it can resume after a user session restart.

## Watchdog and CPU Fallback

The watchdog:

- starts one ROCm trainer container at a time,
- monitors `logs/train.log` for increasing training steps,
- treats no progress for 15 minutes as a hang,
- saves failed container logs under `logs/watchdog/`,
- retries GPU a small number of times,
- falls back to the CPU trainer if GPU remains broken.

Fallback uses the existing CPU Docker compose setup and resumes from the newest stable checkpoint. The pause file remains in place so auto-resume does not create duplicate trainers.

## Checkpoints

GPU training should use a shorter checkpoint interval than CPU training:

```bash
--checkpoint-interval 500
```

This updates `latest.pt` and writes milestone `step_*.pt` files more often. Retention is intentionally not destructive yet: old checkpoints are not deleted automatically.

Create a pre-GPU snapshot:

```bash
python3 scripts/create_pre_gpu_snapshot.py
```

Snapshots live under:

```text
checkpoints/snapshots/pre-gpu-YYYYMMDD-HHMMSS/
```

Each snapshot contains selected checkpoints, `config.py`, `tokenizer.model`, a train log tail and metadata.

## Health Check

```bash
python3 scripts/check_training_progress.py
python3 scripts/check_training_progress.py --json
systemctl --user status glyph-training-watchdog.service --no-pager
```

This reports the active backend, active trainer containers, last step/loss/tokens/s, last validation loss, checkpoint mtimes and watchdog state.

## Glyph-100M Smoke Result

Glyph-100M was tested on the same experimental ROCm/gfx1012 container with
context length 512.

Result file:

```text
reports/glyph100_rocm_smoke.json
```

Summary:

- batch 4: ok
- batch 8: ok
- batch 16: out of memory
- batch 32: not attempted after batch 16 OOM

Recommended Glyph-100M shape is therefore:

```text
microbatch=4
gradient_accumulation_steps=8
effective_tokens_per_step=16,384
```

Batch 8 passed synthetic smoke, but it left little VRAM headroom on RX 5500 XT.
Stage 1 should start with batch 4 / accumulation 8 for the same effective
tokens per optimizer step and a safer ROCm margin. This is enough for a short
stage-1 sanity run, but not proof that long ROCm training is stable. Keep
watchdog/fallback discipline for any approved run.

## Safe Stop

For the active GPU or CPU trainer:

```bash
docker stop -t 300 <training-container>
```

This gives `train.py` time to catch SIGTERM and write `checkpoints/emergency.pt`.

## Notes

- The ROCm image is intentionally separate from the CPU training image.
- The container mounts data read-only, but checkpoints and logs writable, matching the CPU training container.
- The Docker setup uses `/dev/kfd` and `/dev/dri`; it does not use privileged mode or Docker socket access.
- `rocSHMEM` may print a warning about `libibverbs`; the tested tensor and Glyph forward/backward path still works.
- This is an experimental nightly stack. Pinning currently uses `torch[device-gfx1012]==2.12.0+rocm7.14.0a20260521`.
