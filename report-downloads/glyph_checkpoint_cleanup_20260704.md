# Glyph checkpoint cleanup - 2026-07-04

## Result

- mode: `applied`
- checkpoint files before: `131`
- checkpoint files kept: `9`
- checkpoint files removed: `122`
- bytes selected for removal: `121.67 GiB`
- residual snapshot support files removed: `7` (`509.65 KiB`)
- checkpoint directory after: `7.48 GiB`
- repository after: `72.46 GiB`
- filesystem free after: `145.28 GiB`

## Kept checkpoints

- `checkpoints/final.pt` (311.83 MiB)
- `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm-latest.pt` (1.09 GiB)
- `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm-best.pt` (1.09 GiB)
- `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_3-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_3-fixedmask-rocm-best.pt` (1.09 GiB)
- `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_3-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_3-fixedmask-rocm-final-step_000586.pt` (1.09 GiB)
- `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt` (1.09 GiB)
- `checkpoints/glyph-100m-v2_3_1-50k/latest.pt` (1.09 GiB)
- `checkpoints/public-demo.pt` (311.84 MiB)
- `checkpoints/sft-v0/glyph-27m-sft-v0-final.pt` (311.84 MiB)

## Removed by directory

- `checkpoints`: 2 files, 623.68 MiB
- `checkpoints/glyph-100m`: 12 files, 13.13 GiB
- `checkpoints/glyph-100m-thermal-test`: 2 files, 2.19 GiB
- `checkpoints/glyph-100m-v2_3_1-25k`: 11 files, 12.04 GiB
- `checkpoints/glyph-100m-v2_3_1-35k`: 12 files, 13.13 GiB
- `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke`: 7 files, 7.66 GiB
- `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm`: 5 files, 5.47 GiB
- `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm`: 11 files, 12.04 GiB
- `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_3-fixedmask-rocm`: 12 files, 13.13 GiB
- `checkpoints/glyph-100m-v2_3_1-44k-sft-tiny-overfit-cpu-fixedmask`: 6 files, 6.57 GiB
- `checkpoints/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe`: 6 files, 6.57 GiB
- `checkpoints/glyph-100m-v2_3_1-45k`: 10 files, 10.94 GiB
- `checkpoints/glyph-100m-v2_3_1-50k`: 5 files, 5.47 GiB
- `checkpoints/glyph-100m-v2_3_1-batch8-bench`: 2 files, 2.19 GiB
- `checkpoints/glyph-100m-v2_3_1-preflight`: 6 files, 6.57 GiB
- `checkpoints/sft-v0`: 3 files, 935.53 MiB
- `checkpoints/sft-v0-smoke`: 5 files, 1.52 GiB
- `checkpoints/sft-v0-smoke-resume-test`: 4 files, 1.22 GiB
- `checkpoints/snapshots/pre-sft-v0-20260525-170501`: 1 files, 311.83 MiB

## Scope

- Only redundant `.pt` files under `checkpoints/` were removed.
- Datasets, tokenizer, source code, logs, evals, reports and model metadata were not removed.
- Empty checkpoint directories were removed after their files were pruned.
- The remaining duplicated config/tokenizer/log files under `checkpoints/snapshots/` were also removed.
