# Glyph cold-storage migration - 2026-07-04

## Result

- status: `complete`
- archive: `/mnt/data/mac/GlyphArchive/glyph-cold-20260704`
- files migrated: `3955`
- data migrated: `64.32 GiB`
- system repository after: `7.9G`
- system filesystem free after: `209.55 GiB`
- HDD free after: `228.45 GiB`

## Kept on the system disk

- `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm-best.pt`
- `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`
- `checkpoints/public-demo.pt`
- `glyph100_v2_3_1_metadata.json`
- `glyph100_v2_3_1_train.bin`
- `glyph100_v2_3_1_val.bin`
- `tokenizer.model`
- `tokenizer.vocab`

## Migrated groups

- `.cache/llama-rocm-gfx1012`: 3916 files, 575.52 MiB
- `checkpoints/final.pt`: 1 files, 311.83 MiB
- `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm`: 1 files, 1.09 GiB
- `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_3-fixedmask-rocm`: 2 files, 2.19 GiB
- `checkpoints/glyph-100m-v2_3_1-50k`: 1 files, 1.09 GiB
- `checkpoints/sft-v0`: 1 files, 311.84 MiB
- `data/processed`: 27 files, 35.08 GiB
- `data/raw`: 3 files, 18.35 GiB
- `models/gemma4`: 2 files, 4.97 GiB
- `reports/glyph100_smoke_checkpoint.pt`: 1 files, 375.56 MiB

## Compatibility

- Original host paths were replaced with absolute symlinks to the HDD archive.
- Current training inputs, tokenizer and active checkpoints remain physically on the system disk.
- Public inference remains on the local `public-demo.pt` checkpoint.
- Docker jobs that need archived paths may require an explicit `/mnt/data` mount because absolute host symlinks are outside the project bind mount.
