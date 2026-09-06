# Glyph migration from ROCm homelab to Google Colab CUDA

## Scope

This runbook moves only the files needed to load Glyph-100M base 44k, validate
the SFT contract and optionally start a manually approved SFT run. Preparing a
bundle does not train, upload, publish or modify any existing checkpoint.

Approved base:

```text
checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt
```

Checkpoint 50k is diagnostic and is deliberately excluded. The tokenizer is
the existing SentencePiece 16k file with SHA256:

```text
21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029
```

## Data flow

```text
homelab repo
  -> pack separate code/tokenizer/base44k/dataset archives
  -> verify manifest, SHA256, model state and label mask locally
  -> user uploads archives to MyDrive/Glyph/colab/input
  -> Colab mounts Drive and copies archives to /content/glyph-input
  -> Colab verifies SHA256 and extracts to /content/glyph
  -> preflight and optional training use local /content storage
  -> checkpoints land in /content/glyph-output/<run_id>
  -> exporter reloads best checkpoint, runs inference, packs and re-verifies
  -> only a confirmed validated result is copied to Drive output
```

Training directly on mounted Drive is intentionally unsupported. Drive latency
and partial writes make it unsuitable as the active checkpoint directory.

## Local audit and bundle preparation

Run from `/home/maksu/ai-model`:

```bash
.venv/bin/python scripts/pack_glyph_colab_bundle.py \
  --base-checkpoint checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt \
  --dataset data/sft/glyph100_sft_smoke_v0_3.jsonl \
  --output-dir dist/glyph-colab \
  --include-reports \
  --dry-run
```

Review every listed source. The full command is identical without `--dry-run`:

```bash
.venv/bin/python scripts/pack_glyph_colab_bundle.py \
  --base-checkpoint checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt \
  --dataset data/sft/glyph100_sft_smoke_v0_3.jsonl \
  --output-dir dist/glyph-colab \
  --include-reports
```

Do not add `--force` unless an existing bundle has been inspected and replacing
it is intentional. The packer creates an optimizer-free copy of base 44k for a
fresh SFT optimizer; the source checkpoint remains unchanged.

Verify the completed bundle before upload:

```bash
.venv/bin/python scripts/verify_glyph_colab_bundle.py \
  --bundle-dir dist/glyph-colab \
  --cpu-inference \
  --report-json dist/glyph-colab/local-verification.json
```

The verifier checks archive traversal safety, all member hashes, tokenizer,
checkpoint metadata and shapes, strict CPU model loading and SFT labels. Any
failure returns a non-zero exit status.

## Files to upload manually

Create these folders in Google Drive:

```text
MyDrive/Glyph/colab/input
MyDrive/Glyph/colab/output
MyDrive/Glyph/colab/reports
```

Upload to `input/`:

- `manifest.json`
- `SHA256SUMS`
- `glyph-code-<timestamp>.tar.zst`
- `glyph-tokenizer-<timestamp>.tar.zst`
- `glyph-base44k-<timestamp>.tar.zst`
- `glyph-sft-data-<timestamp>.tar.zst`
- optionally `glyph-reports-<timestamp>.tar.zst`

Open `Glyph_Colab.ipynb` from the bundle. No token, service account or Drive API
credential is required.

## First Colab run

1. Choose **Runtime -> Change runtime type -> GPU**.
2. Edit only the configuration cell, including actual archive names and a new
   `RUN_ID`.
3. Keep `RUN_TRAINING = False`.
4. Mount Drive using the standard authorization dialog.
5. Run the environment cell and confirm CUDA and VRAM.
6. Copy, hash-check and extract input archives locally.
7. Install the small requirements file. Do not reinstall PyTorch if CUDA works.
8. Run `scripts/colab_preflight.py`.
9. Read both generated preflight reports before considering any training.

Preflight validates step 44k, the Glyph-100M config, context 512, tokenizer SHA,
strict state shapes, label mask, local I/O and a small CUDA inference. It never
calls backward or an optimizer.

## SFT label contract

The template is:

```text
<|user|>
{instruction}
<|assistant|>
{response}
<|end|>
```

The corrected causal boundary is `i < assistant_pos`. Therefore the prompt and
assistant marker are inputs, the first response token and `<|end|>` are
supervised, and padding labels are `-100`.

## Compatibility smoke

The optional notebook cell is disabled. It runs only after setting both:

```python
RUN_COMPATIBILITY_SMOKE = True
TRAINING_CONFIRMATION = "RUN_COMPATIBILITY_SMOKE"
```

It uses 20 steps by default, fp32, no autocast, no GradScaler, batch 1,
accumulation 4, LR `1e-5`, clipping `0.5` and a fresh AdamW optimizer. It writes
to a separate run directory and reloads each exposed checkpoint.

## Deliberately enabling a real run

Review the command printed by the notebook. Training requires:

```python
RUN_TRAINING = True
TRAINING_CONFIRMATION = "START_GLYPH_SFT"
```

The runner additionally requires `--confirm-training`. Defaults remain fp32,
batch 1, accumulation 4, LR `1e-5`, weight decay 0 and save-best-on-val.
`fp16` uses GradScaler and `bf16` is rejected unless the GPU reports support.
Neither reduced-precision mode is enabled automatically.

## Checkpoint integrity and resume

Each run lives under `/content/glyph-output/<run_id>/`:

```text
run_config.json
run_state.json
resume_request.json       # only after a resume request
checkpoints/
logs/
reports/
```

Checkpoint creation is local and transactional:

1. write a temporary file,
2. flush and `fsync`,
3. reload and validate model/optimizer/scheduler metadata,
4. atomically rename,
5. update `latest.pt` or `best.pt` only after validation.

Resume uses `--resume-checkpoint` and restores model, optimizer, scheduler,
GradScaler when applicable, RNG state, step and best validation loss. It rejects
changes to variant, tokenizer, datasets, batch, accumulation or precision.
Use the same `RUN_ID` and output directory after a runtime reconnect.

Drive should contain only best, a validated milestone, final, manifest, config
and summary. Do not mirror every small checkpoint.

## Export and return to the homelab

Export is disabled by default. `scripts/colab_export_results.py` first reloads
the selected checkpoint, performs strict state validation and inference, builds
a local `.tar.zst`, extracts it again and verifies all hashes. Drive copy occurs
only with:

```text
--confirm-copy COPY_VALIDATED_RESULT
```

After downloading the result archive to the homelab, verify the SHA in its
external manifest and SHA256SUMS before extracting. Keep imported results in a
new directory; never overwrite 44k, 45k or 50k.

## Dependencies

`requirements-colab.txt` intentionally omits PyTorch. Colab's CUDA-enabled build
is preferred. The bundle needs only NumPy, SentencePiece, psutil and zstandard.
The homelab audit used Python 3.12.3, PyTorch 2.11.0 and SentencePiece 0.2.1;
Colab versions may differ and are recorded by every preflight.

If Colab's PyTorch cannot see CUDA or load the checkpoint, stop. A replacement
PyTorch install must be justified and explicitly enabled in the notebook rather
than silently performed.

## Common failures

- **No GPU:** select a GPU runtime and restart preflight. Do not fall back to CPU
  for an intended training run.
- **T4/L4/A100 differences:** begin with fp32 compatibility smoke. Test bf16 only
  when reported as supported; T4 generally requires fp16 for reduced precision.
- **Out of memory:** stop, retain the last validated checkpoint and reduce batch
  size before changing precision.
- **Not enough `/content` space:** remove only disposable Colab runtime files or
  start a fresh runtime; do not train on Drive.
- **Slow Drive:** copy once before work and once after validated export.
- **Session loss:** remount Drive, restore a validated milestone locally and
  resume with the same run config.
- **PyTorch incompatibility:** record versions and the exact error; do not
  reinstall automatically.
- **Corrupt checkpoint/archive:** stop on SHA or reload failure. Never promote a
  partial file to `latest.pt`.

## Never commit or upload publicly

Do not commit secrets, Drive credentials, HF tokens, `.env`, virtualenvs,
historical logs, unrelated datasets or private report contents. Do not upload
the model or dataset publicly. This workflow is a private migration aid, not a
release pipeline.
