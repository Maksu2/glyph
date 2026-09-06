# Glyph-27M Training Container

Glyph-27M has a CPU-only Docker training setup designed to be polite to the homelab.

## GPU decision

The host has an AMD Radeon RX 5500 XT visible through `/dev/dri`, but ROCm is not installed on the host and `/dev/kfd` is not present. AMD's current ROCm compute support matrix does not list RX 5500 XT, so the recommended path is CPU-only for now.

## Build

```bash
cd /home/maksu/ai-model
mkdir -p .cache/huggingface/datasets .cache/torch logs checkpoints
docker compose -f docker-compose.train.yml build trainer
```

## Smoke test

```bash
cd /home/maksu/ai-model
scripts/smoke_test_container.sh
```

## Inference

```bash
cd /home/maksu/ai-model
docker compose -f docker-compose.train.yml run --rm trainer \
  python generate.py "Stolica Polski to" --max-tokens 40 --temperature 0.8 --top-k 40
```

## Short resume test

This runs a small number of optimizer steps in this invocation and does not write `final.pt`.

```bash
cd /home/maksu/ai-model
docker compose -f docker-compose.train.yml run --rm trainer \
  python train.py --resume checkpoints/latest.pt --max-steps 10
```

## Validation holdout

`train.py` logs validation only when `data/processed/val_tokens.bin` exists. Create a non-destructive tail holdout on the host:

```bash
cd /home/maksu/ai-model
nice -n 10 ionice -c2 -n7 python3 data/create_validation_holdout.py --tokens 50000000
```

This writes `data/processed/val_tokens.bin` plus `data/processed/val_tokens.meta.json`. On the next training restart, `train.py` reads the metadata and limits training to the first part of `tokens.bin`, so the held-out tail is not sampled in future steps. This is still not a pristine validation set for the already-trained checkpoint, because earlier training may have sampled some of those tokens before the split existed.

## Gemma 4 teacher/evaluator

Gemma 4 is not part of the gradient training loop. It runs as a separate Vulkan-backed evaluator, writes reports, then stops.

Default expected model:

```text
models/gemma4/gemma-4-e4b-it-q4_k_m.gguf
```

Manual one-shot run:

```bash
cd /home/maksu/ai-model
scripts/run_gemma4_eval_cycle.sh
```

Default eval sampling:

```text
60 prompts, max_new_tokens=60, temperature=0.75, top_k=50, top_p=0.92,
repetition_penalty=1.10, no_repeat_ngram_size=4
```

The user timer runs only at night, at 01:15 and 03:15 Europe/Warsaw with a small randomized delay:

```bash
systemctl --user status ai-model-gemma4-eval.timer
systemctl --user start ai-model-gemma4-eval.service
```

If the GGUF file is missing, the cycle exits safely and the dashboard shows `model-missing`.

Reports:

```text
reports/samples/latest.jsonl
reports/gemma4_eval/latest.jsonl
reports/gemma4_eval/latest_summary.json
reports/gemma4_eval/status.json
```

The default prompt set is `eval/prompts.jsonl` and is designed for a base pretraining model: 60 Polish continuations, fragments, short dialogue, long-context snippets and technical prose. The older assistant-style instruction set is kept as `eval/prompts_instruct.jsonl` for use after SFT.

The dashboard has a manual Gemma eval button. It requires the owner code, starts `ai-model-gemma4-eval.service` with `--no-block`; the service still owns the long-running work and stops the Vulkan container when done.

Optional SFT seed generation while the teacher is running:

```bash
python3 scripts/gemma4_make_sft.py --out data/sft/gemma4_seed.jsonl
python3 finetune.py --base checkpoints/latest.pt --dataset-jsonl data/sft/gemma4_seed.jsonl
```

## Long resume

Run this manually only when you are ready for long training.

```bash
cd /home/maksu/ai-model
docker compose -f docker-compose.train.yml run --rm trainer \
  python train.py --resume checkpoints/latest.pt
```

## Default resource limits

- no hard CPU quota and no CPU pinning by default: training may use all cores when the host is idle
- `mem_limit=22g`
- `memswap_limit=22g`
- `oom_score_adj=500`
- `TRAIN_NUM_THREADS` defaults to `nproc` inside the container

The training container is burstable: it can use the full CPU when spare cycles exist. A user-level systemd timer switches priority according to active homelab hours:

- weekdays 15:00-22:00 Europe/Warsaw: homelab-friendly mode, `cpu_shares=256`, `nice=10`, `ionice=2:7`
- weekends 08:00-22:00 Europe/Warsaw: homelab-friendly mode, `cpu_shares=256`, `nice=10`, `ionice=2:7`
- outside those windows: full training mode, `cpu_shares=2048`, `nice=0`, `ionice=2:0`, `TRAIN_INTEROP_THREADS=2`, `OMP_WAIT_POLICY=ACTIVE`, `OMP_PROC_BIND=spread`

Check the active mode:

```bash
systemctl --user status ai-model-training-resource-schedule.timer
scripts/training_resource_mode.sh status
```

Lowering niceness from `10` back to `0` is not allowed for an already-running unprivileged process, and OpenMP settings are process environment variables. The scheduler performs a graceful restart when the mode changes so active/full process settings are applied cleanly. `train.py` catches SIGTERM, saves `checkpoints/emergency.pt`, updates `checkpoints/latest.pt`, and resumes from that checkpoint.

If the homelab feels less responsive, cap PyTorch/OpenMP threads first:

```bash
TRAIN_NUM_THREADS=2 docker compose -f docker-compose.train.yml run --rm trainer \
  python train.py --resume checkpoints/latest.pt
```

If you need a hard CPU cap, add a temporary override compose file with `cpus:`/`cpuset:` rather than changing the default burstable mode.
