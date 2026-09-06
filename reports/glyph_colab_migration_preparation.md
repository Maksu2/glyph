# Glyph Colab migration preparation

**Status: PASS - migration tooling is ready; no training or upload was run.**

Generated: `2026-08-02T00:24:53Z`

## Scope and safety result

The existing Glyph repository was extended in place. No new application
project was created. This work did not start pretraining, SFT, backward, an
optimizer step or a training container. Nothing was uploaded to Google Drive,
no Drive API or credentials were used, and no existing checkpoint was changed.

The Colab workflow is private and manual by design:

1. Build and verify separate archives on the homelab.
2. Upload them manually to `MyDrive/Glyph/colab/input/`.
3. Copy them from mounted Drive to local `/content`.
4. Verify SHA256 before extraction and run CUDA preflight.
5. Keep training disabled unless the user enters an exact confirmation.
6. Train and checkpoint only on local `/content`.
7. Reload, archive and re-verify a result before an explicitly confirmed Drive copy.

## Repository audit

- Repository root: `/home/maksu/ai-model`
- Git metadata: not present, so the manifest records `git_commit: null`
- Model config: `config.py`, variant `glyph-100m`
- Model implementation: `model/transformer.py`, class `GPT`
- SFT pipeline: `finetune.py`, `SFTDataset`
- Tokenizer: `data/processed/tokenizer.model`
- Selected SFT dataset: `data/sft/glyph100_sft_smoke_v0_3.jsonl`
- Train split: `data/sft/processed/glyph100_sft_smoke_v0_3_train.jsonl`
- Validation split: `data/sft/processed/glyph100_sft_smoke_v0_3_val.jsonl`
- Test split: `data/sft/processed/glyph100_sft_smoke_v0_3_test.jsonl`
- Approved base: `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`
- Checkpoint 50k: explicitly rejected by the packer as a base

## Base checkpoint validation

- Source size: `1,175,128,433` bytes (`1.09 GiB`)
- SHA256: `5c24f234eb8550bb6b44e3e3cbe87e109ff5665a58220b0dd59566b330a120c6`
- Step/current step: `44000`
- Variant: `glyph-100m`
- Pretraining dataset metadata: `glyph100_v2_3_1`
- Context length: `512`
- Model tensors: `113`
- Unique/trainable parameters: `97,654,272`
- Logical parameters with tied embedding/head counted twice: about `109.94M`
- Strict CPU state load: PASS, zero missing/unexpected keys
- Tokenizer SHA256: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`

The full source checkpoint contains historical optimizer and scheduler state.
The packer derives a new optimizer-free base payload for fresh SFT without
modifying the source. Its model tensors are `442,914,816` bytes (`422.40 MiB`).

## SFT data and label contract

- Dataset examples: `2,753`
- Train/val/test: `2,341 / 275 / 137`
- Dataset SHA256: `5583e1e8dea7631cafd7156f2da0cf0b96558c38215f2d62a3ffb3365e339121`
- All examples fit context 512; reported maximum template length: `76` tokens
- Fixed boundary in `finetune.py`: `i < assistant_pos`
- First assistant response token supervised: PASS
- `<|end|>` supervised: PASS
- Prompt/user/instruction masked: PASS
- Padding labels equal `-100`: PASS
- Examples without assistant labels: `0`

## Added files

- `colab/Glyph_Colab.ipynb`
- `colab/README.md`
- `requirements-colab.txt`
- `config/colab_bundle.example.json`
- `docs/COLAB_MIGRATION.md`
- `scripts/colab_bundle_utils.py`
- `scripts/pack_glyph_colab_bundle.py`
- `scripts/verify_glyph_colab_bundle.py`
- `scripts/colab_preflight.py`
- `scripts/colab_run_sft.py`
- `scripts/colab_export_results.py`
- this Markdown report and its JSON companion

The report publisher/index was updated only to expose this completed prompt as
one download-page section.

## Safety features implemented

- Separate code, tokenizer, base44k, SFT data and optional report archives
- Explicit allowlist instead of recursively archiving the repository
- Rejection of `.git`, virtualenvs, caches, logs, credentials, secrets and unrelated data
- Explicit rejection of 50k as base
- Safe tar extraction with traversal, link and device-node rejection
- Outer `SHA256SUMS`, per-archive SHA256 and per-member SHA256
- Strict model load and label audit in the bundle verifier
- `RUN_TRAINING = False` and `RUN_COMPATIBILITY_SMOKE = False` in the notebook
- Exact notebook confirmations for compatibility smoke and real training
- Runner-level `--confirm-training` guard
- Correct loss division by gradient accumulation steps
- fp32 default; fp16/GradScaler and bf16 are opt-in only
- NaN/Inf/OOM/crash stops without replacing the last valid checkpoint
- Temporary checkpoint, flush/fsync, reload validation and atomic rename
- Model, optimizer, scheduler, scaler, step and RNG restoration on resume
- Resume mismatch rejection for model identity, tokenizer, datasets and hyperparameters
- Local result reload and inference before archive creation
- Result archive re-extraction and hash validation before optional Drive copy
- Exact `COPY_VALIDATED_RESULT` confirmation for mounted-Drive export

## Local test results

1. Python compile for all six Colab scripts and helpers: PASS
2. Notebook JSON (`nbformat=4`, 21 cells): PASS
3. Compilation of all 10 notebook code cells: PASS
4. Full base44k CPU strict load: PASS
5. Full label-mask audit on v0.3: PASS
6. CPU inference compatibility smoke: PASS (quality remains base-LM weak, as expected)
7. Packer dry-run with real 44k/dataset/reports: PASS
8. Metadata-only structural bundle creation: PASS
9. Structural bundle extraction/member/SHA verification: PASS
10. One-byte archive tamper detection: PASS (verifier returned non-zero)
11. Checkpoint 50k rejection: PASS (packer returned non-zero)
12. Training confirmation guard: PASS (non-zero, no run directory created)
13. Atomic synthetic checkpoint save/reload/latest/best: PASS
14. Resume batch mismatch rejection: PASS
15. Exporter strict reload and inference dry-run: PASS; no archive or Drive copy made
16. Existing repository unit tests: `12/12` PASS
17. Active `train.py`, `finetune.py` or Colab runner after tests: none
18. Active ROCm/training container after tests: none

No optimizer step or backward pass was executed during these tests.

## Expected bundle size

The optimizer-free base contributes `422.40 MiB` before zstd compression. Code,
tokenizer and selected SFT files add roughly `3 MiB`; curated optional reports
add about `6 MiB` before compression. Expected full upload is therefore around
`0.42 GiB`, with the exact compressed size printed by the real pack command.

## Prepare the full bundle

Run from `/home/maksu/ai-model`:

```bash
.venv/bin/python scripts/pack_glyph_colab_bundle.py \
  --base-checkpoint checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt \
  --dataset data/sft/glyph100_sft_smoke_v0_3.jsonl \
  --output-dir dist/glyph-colab \
  --include-reports
```

The already-tested review command adds `--dry-run`.

## Verify the full bundle

```bash
.venv/bin/python scripts/verify_glyph_colab_bundle.py \
  --bundle-dir dist/glyph-colab \
  --cpu-inference \
  --report-json dist/glyph-colab/local-verification.json
```

## Required Drive upload

Upload these files from `dist/glyph-colab/` to
`MyDrive/Glyph/colab/input/`:

- `manifest.json`
- `SHA256SUMS`
- `glyph-code-<timestamp>.tar.zst`
- `glyph-tokenizer-<timestamp>.tar.zst`
- `glyph-base44k-<timestamp>.tar.zst`
- `glyph-sft-data-<timestamp>.tar.zst`
- optionally `glyph-reports-<timestamp>.tar.zst`

Open `Glyph_Colab.ipynb`, choose a GPU runtime, replace archive placeholders in
the first cell, mount Drive, inspect the environment and run preflight. Leave
`RUN_TRAINING = False` until a separate decision explicitly authorizes work.

## Known limitations

- This homelab process has no CUDA device, so actual Colab GPU/preinstalled
  PyTorch compatibility must be established by the notebook preflight.
- fp16 and bf16 paths are implemented but deliberately untested and disabled.
- The full 422 MiB base archive was not materialized during this preparation;
  the smaller structural bundle exercised the same archive, manifest, extraction
  and label-validation paths without duplicating the full checkpoint.
- Colab hardware and preinstalled versions can change between sessions.
- The selected v0.3 dataset is only a chosen input candidate; this migration does
  not authorize SFT v0.3, SFT v1 or any other training.

## Final state

Migration preparation is complete and locally validated. Full bundle creation,
manual Drive upload, Colab preflight and any later training remain separate user
actions. Best checkpoint metadata and all existing checkpoints remain unchanged.
