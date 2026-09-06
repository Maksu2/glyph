# Changelog

## 2026-05-25

- Added SFT v0 dataset validation, token counting and preparation scripts.
- Prepared `glyph_sft_v0_seed_1500_expanded.jsonl` as the SFT v0 dataset.
- Ran Glyph-27M SFT v0 for one epoch on ROCm/RX 5500 XT.
- Added SFT checkpoints under `checkpoints/sft-v0/`.
- Added base vs SFT comparison samples under `eval/sft-v0/`.
- Updated dashboard and public site metadata for the SFT v0 phase.
- Added `docs/sft-v0.md`.

## 2026-05-15

- Rebranded project display/documentation from working names to `Glyph` / `Glyph-27M`.
- Added `MODEL_CARD.md`.
- Added informational model identity constants in `config.py`.
- Updated dashboard title, visible labels, and API metadata to `Glyph-27M`.
- Switched Glyph brand assets to the provided PNG logos; dashboard uses the cropped PNG mark.
- Left checkpoints, tokenizer, datasets, training path, and active training process unchanged.
