# Glyph-100M stage 2 attempt - 2026-05-27

## Result

Stage 2 was started from `checkpoints/glyph-100m/latest.pt` at step 1000, targeting 10000 total steps. It stopped almost immediately on the configured non-finite loss guard.

No stage 2 checkpoint was written. `latest.pt` remains the stage 1 checkpoint at step 1000.

## Command intent

- variant: `glyph-100m`
- device: ROCm/CUDA API
- resume: `checkpoints/glyph-100m/latest.pt`
- target step: 10000 total
- batch size: 4
- gradient accumulation: 8
- effective tokens per optimizer step: 16384
- dataset: `glyph100_stage1_candidate`
- eval interval: 500
- checkpoint interval: 1000

## Observed log

- resumed from step: 1000
- training range: 1001 to 10000
- stop: `non_finite_loss`
- stop location: step 1002, micro step 1
- loss: `nan`
- emergency report: `logs/glyph-100m/emergency_stop.json`
- latest checkpoint overwritten: no

## Preserved checkpoints

- `checkpoints/glyph-100m/latest.pt` - step 1000
- `checkpoints/glyph-100m/step_0001000.pt` - step 1000
- `checkpoints/glyph-100m/step_0000500.pt` - step 500

## Initial diagnosis

The checkpoint itself was checked after the stop and did not contain non-finite model or optimizer tensors. The failure happened after resume, after at least one optimizer update, so the likely area to investigate is the resumed optimizer/update path rather than the saved model weights alone.

Do not start stage 3. Do not retry stage 2 blindly. Next diagnostic should isolate:

- forward loss from the resumed checkpoint,
- gradients before optimizer step,
- parameters after optimizer step,
- ROCm AdamW `foreach=True` vs `foreach=False`,
- learning rate on resumed optimizer state,
- whether the first resumed optimizer step creates non-finite weights.
