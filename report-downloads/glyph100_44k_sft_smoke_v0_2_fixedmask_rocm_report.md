# Glyph-100M SFT smoke v0.2 fixed-mask ROCm report

## Status

- run: `complete`
- type: corrected small SFT smoke, not SFT v1
- base checkpoint: `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`
- output: `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm`
- 50k checkpoint was not used.

## Training

- duration: `3m 18s`
- steps: `462`
- batch/accum: `1/4`
- learning rate: `1e-05`
- grad clip: `0.5`
- train loss start/end: `4.476641` -> `1.470514`
- final running avg loss: `2.343668`
- best val loss: `1.213816` at step `462`
- final val loss: `1.213816`
- avg tok/s from log: `432.5`
- max grad norm: `54.017914`
- NaN/Inf: `False`
- OOM/crash/exception: `False`

## Validation Loss

- step `50`: val_loss `3.133248`
- step `100`: val_loss `2.713382`
- step `150`: val_loss `2.211038`
- step `200`: val_loss `2.386725`
- step `250`: val_loss `2.188972`
- step `300`: val_loss `2.006348`
- step `350`: val_loss `1.5548`
- step `400`: val_loss `1.316465`
- step `450`: val_loss `1.591549`
- final step `462`: val_loss `1.213816`

## Dataset

- dataset: `glyph100_sft_smoke_v0_2`
- train usable: `1846`
- val usable: `218`
- dataset report total examples: `2176`
- split: `{'train': 1846, 'val': 218, 'test': 112}`
- max template tokens: `76`

## Checkpoints

- checkpoint saves: `9`
- best updates: `8`
- best checkpoint was saved with `save_best_on_val=true`.

## Eval Snapshot

- base44k: avg_score_mean `-0.16`, repetition `73`, first-token `0`, web `6`, pseudo `0`
- sft_v0_1: avg_score_mean `2.94`, repetition `29`, first-token `40`, web `4`, pseudo `0`
- sft_v0_2: avg_score_mean `3.40`, repetition `12`, first-token `49`, web `13`, pseudo `0`
- pairwise totals: `{'sft_v0_2_vs_sft_v0_1': {'sft_v0_2': 36, 'tie': 145, 'sft_v0_1': 19}, 'sft_v0_2_vs_base44k': {'sft_v0_2': 111, 'tie': 83, 'base44k': 6}, 'sft_v0_1_vs_base44k': {'sft_v0_1': 101, 'tie': 95, 'base44k': 4}}`
