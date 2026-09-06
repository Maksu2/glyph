# Glyph-100M batch 8 / accum 4 benchmark
Generated: 2026-06-08T16:14:46.244043+00:00
## Result
The accidental 35k run was stopped cleanly. The batch 8 / accum 4 benchmark completed from step 25,000 to 25,100 in a separate directory.
## Stopped 35k run
- Log: `logs/glyph-100m-v2_3_1-35k/train.log`
- Resume/start: `25000`
- Last logged step: `26720`
- Last logged train loss: `3.5684`
- Last eval: `{'step': 26500, 'val_loss': 3.5991, 'line': '2026-06-08 15:43:55 eval step=  26500 | val_loss=3.5991 | batches=5'}`
- Clean exit detected: `True`
- Partial files, not removed:
  - `checkpoints/glyph-100m-v2_3_1-35k/latest.pt` · 1.094 GiB · 2026-06-08T16:02:52.143478+00:00
  - `checkpoints/glyph-100m-v2_3_1-35k/step_0026000.pt` · 1.094 GiB · 2026-06-08T15:02:24.194777+00:00
  - `checkpoints/glyph-100m-v2_3_1-35k/emergency.pt` · 1.094 GiB · 2026-06-08T16:02:51.174474+00:00

## Baseline batch 4 / accum 8
- Config: batch 4, accum 8, effective tokens/step 16,384
- Average tok/s, excluding first logged point: `3289.6`
- Last logged tok/s: `3292`
- Observed VRAM during earlier 35k run: about `61%`
- Observed GPU temps during earlier 35k run: edge about `63°C`, hotspot about `87°C`

## Benchmark batch 8 / accum 4
- Log: `logs/glyph-100m-v2_3_1-batch8-bench/train.log`
- Resume/start: `25000`
- Range: `(25001, 25100)`
- Config: `{'batch_size': 8, 'context': 512, 'gradient_accumulation_steps': 4, 'effective_tokens_per_step': 16384}`
- Average tok/s, excluding first logged point: `3373.9`
- Last logged tok/s: `3375`
- Val loss at 25,100: `3.4101`
- Difference vs baseline: `2.56%`
- Observed VRAM: `98%`
- Observed max GPU temps: edge `64°C`, hotspot `86°C`
- NaN/Inf/OOM/crash: `no`
- Benchmark files:
  - `checkpoints/glyph-100m-v2_3_1-batch8-bench/latest.pt` · 1.094 GiB · 2026-06-08T16:12:05.763309+00:00
  - `checkpoints/glyph-100m-v2_3_1-batch8-bench/step_0025100.pt` · 1.094 GiB · 2026-06-08T16:12:04.816303+00:00

## Checkpoint metadata
```json
{
  "bench_latest": {
    "step": 25100,
    "current_step": 25100,
    "variant": "glyph-100m",
    "dataset_name": "glyph100_v2_3_1",
    "batch_size": 8,
    "gradient_accumulation_steps": 4
  },
  "bench_step_25100": {
    "step": 25100,
    "current_step": 25100,
    "variant": "glyph-100m",
    "dataset_name": "glyph100_v2_3_1",
    "batch_size": 8,
    "gradient_accumulation_steps": 4
  }
}
```

## Recommendation
B) Stay with `batch_size=4`, `gradient_accumulation_steps=8` for longer unattended runs.

Batch 8 / accum 4 is about 2.56% faster in this short benchmark, but it uses about 98% VRAM. That is too little headroom for a long unattended ROCm run on this GPU. It did not crash in 100 steps, so it is usable for short supervised tests, but I would not switch the 35k continuation to it without accepting higher OOM/fragmentation risk.
