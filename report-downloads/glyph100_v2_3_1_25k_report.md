# Glyph-100M v2.3.1 25k post-training report

## Status

- status: `complete`
- log: `logs/glyph-100m-v2_3_1-25k/train.log`
- checkpoint dir: `checkpoints/glyph-100m-v2_3_1-25k`
- latest checkpoint: `checkpoints/glyph-100m-v2_3_1-25k/latest.pt`
- step checkpoint: `checkpoints/glyph-100m-v2_3_1-25k/step_0025000.pt`

## Checkpoint metadata

- variant: `glyph-100m`
- step/current_step: `25000` / `25000`
- dataset: `glyph100_v2_3_1`
- tokenizer: `data/processed/tokenizer.model`
- tokenizer sha256: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`
- batch/accum: `4` / `8`
- effective tokens/step: `16384`

## Timing and throughput

- start: `2026-06-07 18:38:43`
- end: `2026-06-08 08:35:48`
- duration: `13h 57m`
- average tok/s: `3265.21`
- stage tokens expected: `163,840,000`
- total tokens from log: `409.60M`

## Loss

- first logged train loss: `3.7738`
- last logged train loss: `3.6503`
- start-window avg loss: `3.7774`
- end-window avg loss: `3.5907`
- val loss trend: `falling`
- overfit signal: `no_obvious_overfit`

### Validation losses

- step `15500`: val_loss `3.801` at `2026-06-07 19:19:24`
- step `16000`: val_loss `3.8429` at `2026-06-07 20:00:55`
- step `16500`: val_loss `3.5067` at `2026-06-07 20:42:24`
- step `17000`: val_loss `3.7756` at `2026-06-07 21:23:57`
- step `17500`: val_loss `3.8311` at `2026-06-07 22:05:27`
- step `18000`: val_loss `3.6028` at `2026-06-07 22:47:02`
- step `18500`: val_loss `3.5842` at `2026-06-07 23:29:51`
- step `19000`: val_loss `3.5872` at `2026-06-08 00:13:53`
- step `19500`: val_loss `3.4656` at `2026-06-08 00:55:22`
- step `20000`: val_loss `3.3631` at `2026-06-08 01:40:38`
- step `20500`: val_loss `3.576` at `2026-06-08 02:22:07`
- step `21000`: val_loss `3.6531` at `2026-06-08 03:03:42`
- step `21500`: val_loss `3.5013` at `2026-06-08 03:45:11`
- step `22000`: val_loss `3.5641` at `2026-06-08 04:26:45`
- step `22500`: val_loss `3.5486` at `2026-06-08 05:08:14`
- step `23000`: val_loss `3.4081` at `2026-06-08 05:49:48`
- step `23500`: val_loss `3.7573` at `2026-06-08 06:31:18`
- step `24000`: val_loss `3.2205` at `2026-06-08 07:12:51`
- step `24500`: val_loss `3.6674` at `2026-06-08 07:54:20`
- step `25000`: val_loss `3.4745` at `2026-06-08 08:35:53`

## Stability

- NaN/Inf: `0`
- OOM: `0`
- crash/traceback markers: `0`
- GPU temps: not logged in `train.log`

## Checkpoints

- checkpoint dir size: `12.0 GB`
- checkpoint files: `11`

- `latest.pt`
- `step_0016000.pt`
- `step_0017000.pt`
- `step_0018000.pt`
- `step_0019000.pt`
- `step_0020000.pt`
- `step_0021000.pt`
- `step_0022000.pt`
- `step_0023000.pt`
- `step_0024000.pt`
- `step_0025000.pt`
