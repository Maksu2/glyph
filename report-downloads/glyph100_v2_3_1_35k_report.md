# Glyph-100M v2.3.1 35k post-training report

## Status

- status: `complete`
- log: `logs/glyph-100m-v2_3_1-35k/train.log`
- checkpoint dir: `checkpoints/glyph-100m-v2_3_1-35k`
- latest checkpoint: `checkpoints/glyph-100m-v2_3_1-35k/latest.pt`
- step checkpoint: `checkpoints/glyph-100m-v2_3_1-35k/step_0035000.pt`

## Checkpoint metadata

- variant: `glyph-100m`
- step/current_step: `35000` / `35000`
- dataset: `glyph100_v2_3_1`
- tokenizer: `data/processed/tokenizer.model`
- tokenizer sha256 stored in checkpoint: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`
- tokenizer sha256 actual file: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`
- batch/accum: `4` / `8`
- effective tokens/step: `16384`

## Timing and throughput

- start: `2026-06-08 13:40:13`
- end: `2026-06-09 04:46:04`
- wall duration: `15h 5m`
- active duration, excluding manual stop gap: `13h 56m`
- average tok/s: `3265.1`
- stage tokens expected: `163,840,000`
- total tokens from log: `573.44M`

## Loss

- first logged train loss: `3.6011`
- last logged train loss: `3.4066`
- start-window avg loss: `3.5823`
- mid-window avg loss: `3.5445`
- end-window avg loss: `3.3852`
- val loss trend: `rising`
- overfit signal: `watch_val_loss`

### Validation losses

- step `25500`: val_loss `3.1681` at `2026-06-08 14:20:54`
- step `26000`: val_loss `3.5865` at `2026-06-08 15:02:26`
- step `26500`: val_loss `3.5991` at `2026-06-08 15:43:55`
- step `27000`: val_loss `3.5711` at `2026-06-08 17:34:23`
- step `27500`: val_loss `3.6234` at `2026-06-08 18:15:51`
- step `28000`: val_loss `3.3312` at `2026-06-08 18:57:24`
- step `28500`: val_loss `3.4765` at `2026-06-08 19:38:53`
- step `29000`: val_loss `3.4456` at `2026-06-08 20:20:26`
- step `29500`: val_loss `3.3681` at `2026-06-08 21:01:58`
- step `30000`: val_loss `3.4309` at `2026-06-08 21:43:36`
- step `30500`: val_loss `3.1205` at `2026-06-08 22:25:07`
- step `31000`: val_loss `3.5137` at `2026-06-08 23:06:45`
- step `31500`: val_loss `3.3047` at `2026-06-08 23:51:55`
- step `32000`: val_loss `3.2451` at `2026-06-09 00:33:29`
- step `32500`: val_loss `3.224` at `2026-06-09 01:14:59`
- step `33000`: val_loss `3.3729` at `2026-06-09 02:00:02`
- step `33500`: val_loss `3.4434` at `2026-06-09 02:41:32`
- step `34000`: val_loss `3.5249` at `2026-06-09 03:23:06`
- step `34500`: val_loss `3.2538` at `2026-06-09 04:04:36`
- step `35000`: val_loss `3.2317` at `2026-06-09 04:46:10`

## Stability

- NaN/Inf markers: `0`
- OOM markers: `0`
- crash/traceback markers: `0`
- interrupted segment clean exit seen: `True`
- GPU temps: not logged in `train.log`

## Preserved partial files

- `step_0026000.pt`: `True`
- `emergency.pt`: `True`
- archived manual stop marker: `True`

## Checkpoints

- checkpoint dir size: `13.1 GB`
- checkpoint files: `12`

- `emergency.pt`
- `latest.pt`
- `step_0026000.pt`
- `step_0027000.pt`
- `step_0028000.pt`
- `step_0029000.pt`
- `step_0030000.pt`
- `step_0031000.pt`
- `step_0032000.pt`
- `step_0033000.pt`
- `step_0034000.pt`
- `step_0035000.pt`
