# Glyph-100M v2.3.1 50k diagnostic report

## Status

- status: `complete`
- log: `logs/glyph-100m-v2_3_1-50k/train.log`
- checkpoint dir: `checkpoints/glyph-100m-v2_3_1-50k`
- latest checkpoint: `checkpoints/glyph-100m-v2_3_1-50k/latest.pt`
- step checkpoint: `checkpoints/glyph-100m-v2_3_1-50k/step_0050000.pt`

## Checkpoint metadata

- variant: `glyph-100m`
- step/current_step: `50000` / `50000`
- dataset: `glyph100_v2_3_1`
- tokenizer: `data/processed/tokenizer.model`
- tokenizer sha256 stored in checkpoint: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`
- tokenizer sha256 actual file: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`
- batch/accum: `4` / `8`
- effective tokens/step: `16384`

## Timing and throughput

- start: `2026-06-11 21:00:31`
- end: `2026-06-12 04:02:36`
- wall duration: `7h 2m`
- active duration: `7h 2m`
- average tok/s: `3239.78`
- stage tokens expected: `81,920,000`
- total tokens from log: `819.20M`

## Loss

- first logged train loss: `3.2994`
- last logged train loss: `3.2214`
- start-window avg loss: `3.2838`
- mid-window avg loss: `3.2615`
- end-window avg loss: `3.2507`
- val loss trend: `rising`
- overfit signal: `watch_val_loss`

### Validation losses

- step `45500`: val_loss `3.1731` at `2026-06-11 21:41:16`
- step `46000`: val_loss `3.177` at `2026-06-11 22:22:50`
- step `46500`: val_loss `3.1255` at `2026-06-11 23:04:22`
- step `47000`: val_loss `2.9851` at `2026-06-11 23:49:42`
- step `47500`: val_loss `2.9998` at `2026-06-12 00:31:14`
- step `48000`: val_loss `3.1695` at `2026-06-12 01:12:50`
- step `48500`: val_loss `2.9773` at `2026-06-12 01:57:57`
- step `49000`: val_loss `3.1606` at `2026-06-12 02:39:33`
- step `49500`: val_loss `3.1279` at `2026-06-12 03:21:05`
- step `50000`: val_loss `3.3927` at `2026-06-12 04:02:44`

## Stability

- NaN/Inf markers: `0`
- OOM markers: `0`
- crash/traceback markers: `0`
- clean interrupt seen: `False`
- GPU temps: not logged in `train.log`

## Partial/emergency files

- 50k `emergency.pt`: `False`
- 50k partial-like files: `[]`
- earlier 35k `step_0026000.pt`: `True`
- earlier 35k `emergency.pt`: `True`

## Checkpoints

- checkpoint dir size: `6.6 GB`
- checkpoint files: `6`

- `latest.pt`
- `step_0046000.pt`
- `step_0047000.pt`
- `step_0048000.pt`
- `step_0049000.pt`
- `step_0050000.pt`
