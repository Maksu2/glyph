# Glyph-100M SFT ROCm fixed-mask safe-mode report

## Verdict

A) ROCm fixed-mask safe mode stable; corrected SFT smoke v0.1 can be considered.

## Scope

- This was a ROCm stability test for fixed-mask tiny SFT, not a quality SFT run.
- No SFT v1, larger SFT, pretraining, 50k usage, publication, or checkpoint cleanup was performed.
- Base checkpoint stayed `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`.

## Configuration

- base checkpoint: `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`
- dataset: `glyph100_sft_tiny_overfit_fixedmask`
- output: `checkpoints/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe`
- logs: `logs/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe`
- device: `ROCm/HIP on AMD Radeon RX 5500 XT`
- dtype: `fp32`
- mixed precision/autocast/GradScaler: `disabled`
- batch size: 1
- gradient accumulation: 4
- effective tokens per step: 2048
- LR: 1e-05
- weight decay: 0.0
- grad clip: 0.5

## Results

### safe50

- complete: `True`
- first loss: 4.054152
- final loss: 2.29404
- first val loss: 3.605634
- final val loss: 2.08734
- avg tok/s: 469.1
- max grad norm: 32.772957
- final grad norm: 13.998941
- param norm start/final: 798.416 -> 798.556
- logits min/max observed: -254.193 / -58.872
- NaN/Inf: `False`
- OOM: `False`
- crash/exception: `False`

### safe200

- complete: `True`
- first loss: 4.106993
- final loss: 0.676262
- first val loss: 3.123633
- final val loss: 0.182106
- avg tok/s: 515.7
- max grad norm: 24.56411
- final grad norm: 12.887895
- param norm start/final: 798.416 -> 798.865
- logits min/max observed: -294.684 / -61.001
- NaN/Inf: `False`
- OOM: `False`
- crash/exception: `False`

## Checkpoints

- `checkpoints/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe-final-step_000050.pt`
- `checkpoints/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe-final-step_000200.pt`
- `checkpoints/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe-latest.pt`
- `checkpoints/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe-step_000050-step_000050.pt`
- `checkpoints/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe-step_000100-step_000100.pt`
- `checkpoints/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe-step_000200-step_000200.pt`

## Decision

- A) ROCm fixed-mask safe mode stable; a corrected SFT smoke v0.1 can be considered.
- Because this is only tiny data and safe settings, do not jump directly to larger SFT.
