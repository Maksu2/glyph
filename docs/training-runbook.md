# Glyph-27M Training Runbook

Operational notes for switching between CPU and experimental ROCm/GPU training.

## Preflight

```bash
cd /home/maksu/ai-model
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}' | rg 'train|rocm|glyph'
tail -n 40 logs/train.log
ls -lah checkpoints/latest.pt checkpoints/emergency.pt 2>/dev/null || true
df -h /
docker compose -f docker-compose.train.rocm.yml run --rm trainer-rocm \
  python scripts/rocm_gfx1012_probe.py --batch-size 32 --steps 3
```

If the ROCm probe fails, keep CPU training running.

## Gracefully Stop CPU Training

Create the pause file before stopping CPU training, so the resource scheduler does not auto-resume another CPU trainer:

```bash
printf '%s switching to ROCm watchdog\n' "$(date -Iseconds)" > logs/training.paused
docker stop -t 300 <cpu-training-container>
```

Then verify:

```bash
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}' | rg 'train'
tail -n 80 logs/train.log
ls -lah checkpoints/latest.pt checkpoints/emergency.pt
```

Prefer `emergency.pt` after a graceful stop if it is newer than `latest.pt`.

## Snapshot

```bash
python3 scripts/create_pre_gpu_snapshot.py
```

The script refuses to copy a checkpoint whose size or mtime changes during the stability checks.

## Short GPU Resume Test

```bash
docker compose -f docker-compose.train.rocm.yml run --rm trainer-rocm \
  python train.py --device cuda --resume checkpoints/emergency.pt \
  --max-steps 20 --checkpoint-interval 500
```

This appends to `logs/train.log`, but should not write a normal checkpoint unless it crosses a checkpoint boundary.

## Start Long GPU Training With Watchdog

```bash
systemctl --user start glyph-training-watchdog.service
```

Check status:

```bash
python3 scripts/check_training_progress.py
systemctl --user status glyph-training-watchdog.service --no-pager
tail -f logs/training-watchdog.log
```

The service file lives at:

```text
~/.config/systemd/user/glyph-training-watchdog.service
```

It is enabled for the user session and starts:

```bash
python3 scripts/train_watchdog.py --checkpoint checkpoints/latest.pt \
  --checkpoint-interval 500 --gpu-retries 2 --stale-minutes 15
```

## CPU Fallback

If GPU fails repeatedly, the watchdog starts the existing CPU trainer from the newest stable checkpoint. It does not delete failed GPU containers; logs are copied to `logs/watchdog/`.

Manual CPU fallback:

```bash
docker compose -f docker-compose.train.yml run -d --name glyph-train-cpu-fallback-$(date +%Y%m%d-%H%M%S) trainer \
  python train.py --device cpu --resume checkpoints/latest.pt --checkpoint-interval 1000
```

## Safe Stop

```bash
systemctl --user stop glyph-training-watchdog.service
docker stop -t 300 <training-container>
```

Wait for `checkpoints/emergency.pt` to appear or update, then inspect:

```bash
tail -n 80 logs/train.log
ls -lah checkpoints/latest.pt checkpoints/emergency.pt
python3 scripts/check_training_progress.py
```

## Risks

- RX 5500 XT is not officially supported by ROCm.
- The working stack uses TheRock nightly packages pinned to a specific date.
- Long-run stability is not proven yet.
- Do not run CPU and GPU trainers against the same checkpoint directory at the same time.
- Retention is not destructive yet; checkpoint disk usage will grow faster at `--checkpoint-interval 500`.
