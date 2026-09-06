# Glyph-100M SFT postmortem and next decision

## Verdict

C) SFT pipeline has a labels/mask bug.

Do not run larger SFT, SFT v1, ROCm SFT, or more pretraining from this result.

## Updated Status After Fix

The original SFT smoke run is invalid-for-quality because it used the label mask off-by-one bug.
After changing the boundary from `i <= assistant_pos` to `i < assistant_pos`, the label audit passed and CPU tiny overfit succeeded.

Current technical status: fixed-mask SFT works on CPU for tiny overfit. This does not justify larger SFT yet; it only clears the labels/masking bug and moves the next decision to ROCm safe-mode testing or improved SFT data.

## Why

The audit found an off-by-one bug in SFT label masking: `i <= assistant_pos` masks the first token after `<|assistant|>`. The causal shift itself is correct, but the response start is not supervised.

## What Was Not Run

- CPU tiny overfit at the time of this original postmortem: not run.
- ROCm safe tiny overfit: not run.

Reason: the task allowed tiny overfit only if no critical template/labels issue was found.

Later fixed-mask CPU tiny overfit result: passed. See `reports/glyph100_sft_tiny_overfit_cpu_fixedmask_report.md`.

## Next Decision

Approve fixing the mask boundary and adding a label audit test, then rerun CPU tiny overfit. Only after that should ROCm safe mode be tested again.
