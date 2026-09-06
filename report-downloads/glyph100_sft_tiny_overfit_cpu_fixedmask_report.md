# Glyph-100M SFT tiny overfit CPU fixed-mask report

## Verdict

A) Fixed mask działa; model potrafi overfitować tiny dataset na CPU.

## Scope

- This was a tiny overfit mechanics test, not a quality SFT run.
- No larger SFT, SFT v1, pretraining, ROCm SFT, publication, or checkpoint cleanup was performed.
- The previous SFT smoke is marked invalid-for-quality because it used the label mask off-by-one bug.

## Inputs

- base checkpoint: `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`
- output checkpoint: `checkpoints/glyph-100m-v2_3_1-44k-sft-tiny-overfit-cpu-fixedmask/glyph-100m-v2_3_1-44k-sft-tiny-overfit-cpu-fixedmask-final.pt`
- dataset: `glyph100_sft_tiny_overfit_fixedmask`
- train examples: 64
- device: `cpu`
- steps: 300
- batch size: 4
- learning rate: 5e-05
- weight decay: 0.0

## Loss

- first logged train loss: 4.127
- final logged train loss: 0.0014
- final val loss: 0.0002
- eval losses: `[{'step': 50, 'val_loss': 0.6177, 'line': '2026-06-24 18:20:12 sft eval step=    50 | val_loss=0.6177 | batches=16'}, {'step': 100, 'val_loss': 0.0547, 'line': '2026-06-24 18:21:08 sft eval step=   100 | val_loss=0.0547 | batches=16'}, {'step': 150, 'val_loss': 0.0154, 'line': '2026-06-24 18:22:11 sft eval step=   150 | val_loss=0.0154 | batches=16'}, {'step': 200, 'val_loss': 0.0008, 'line': '2026-06-24 18:23:07 sft eval step=   200 | val_loss=0.0008 | batches=16'}, {'step': 250, 'val_loss': 0.0004, 'line': '2026-06-24 18:24:07 sft eval step=   250 | val_loss=0.0004 | batches=16'}, {'step': 300, 'val_loss': 0.0002, 'line': '2026-06-24 18:25:05 sft eval step=   300 | val_loss=0.0002 | batches=16'}, {'step': 300, 'val_loss': 0.0002, 'line': '2026-06-24 18:25:23 sft final_eval step=   300 | val_loss=0.0002 | batches=16'}]`
- average tok/s from log windows: 179.4

## Stability

- complete: `True`
- NaN/Inf: `False`
- OOM: `False`
- crash/exception: `False`

## Eval

- eval report: `eval/glyph-100m/sft_tiny_overfit_cpu_fixedmask_eval.md`
- examples: 32
- winners: `{'sft': 32}`
- base avg score: -1.53
- SFT avg score: 9.94
- SFT overlap >= 0.70: 32
- SFT starts with expected first word: 32
- SFT ended by `<|end|>`: 32
- SFT repetition samples: 0
- SFT web residue: 1
- SFT pseudo-ency: 0

## Decision

- A) Fixed mask works; the model can overfit the tiny dataset on CPU.
- Next allowed technical step, if approved separately: ROCm safe-mode SFT test with fixed mask.
- Do not scale SFT on the old smoke result; it was invalid-for-quality.
