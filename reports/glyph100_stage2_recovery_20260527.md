# Glyph-100M stage 2 recovery - 2026-05-27

## Summary

The first stage 2 resume attempt stopped with `non_finite_loss` at step 1002. The checkpoint remained safe at step 1000.

A diagnostic resume run from the same checkpoint completed steps 1001-1010 without writing checkpoints when using:

- `--optimizer-foreach false`
- `--attention-backend math`
- `--finite-check-interval 1`

The real stage 2 run was then restarted with the same safer optimizer/attention path and target step 10000 total.

## Current stage 2 command changes

The active run keeps the approved stage 2 settings:

- resume: `checkpoints/glyph-100m/latest.pt`
- target step: 10000 total
- batch size: 4
- gradient accumulation: 8
- effective tokens/step: 16384
- dataset: `glyph100_stage1_candidate`

Additional stability flags:

- AdamW foreach disabled
- SDPA math kernel preferred
- model parameter finite check every 10 optimizer steps

## Initial healthy progress

At the time of this recovery note:

- latest observed step: 1050
- latest observed train loss: 6.2584
- latest observed throughput: about 3287 tok/s
- GPU use: 99%
- VRAM use: about 61%
- GPU edge/junction: about 59C / 79C

The old `logs/glyph-100m/emergency_stop.json` remains as a record of the failed attempt, but dashboard/export logic treats it as stale once the training log has advanced beyond the emergency step.

## Working hypothesis

The failure is likely in the experimental ROCm fast path rather than a corrupt checkpoint:

- checkpoint model tensors were finite,
- checkpoint optimizer tensors were finite,
- resume forward/update is stable with AdamW `foreach=false`,
- throughput remains close to the previous run.

The exact culprit is not proven yet. The most likely suspects are AdamW foreach on ROCm/gfx1012 and/or default SDPA kernel selection on unsupported RDNA1.

## Do not do

- Do not start stage 3 / 50k without approval.
- Do not delete the emergency report.
- Do not re-enable AdamW foreach for the active run.
- Do not switch back to default SDPA during this stage.
