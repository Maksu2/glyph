# Glyph-100M v2.3.1 45k post-training report

## Status

- status: `complete`
- log: `logs/glyph-100m-v2_3_1-45k/train.log`
- checkpoint dir: `checkpoints/glyph-100m-v2_3_1-45k`
- latest checkpoint: `checkpoints/glyph-100m-v2_3_1-45k/latest.pt`
- step checkpoint: `checkpoints/glyph-100m-v2_3_1-45k/step_0045000.pt`

## Checkpoint metadata

- variant: `glyph-100m`
- step/current_step: `45000` / `45000`
- dataset: `glyph100_v2_3_1`
- tokenizer: `data/processed/tokenizer.model`
- tokenizer sha256 stored in checkpoint: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`
- tokenizer sha256 actual file: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`
- batch/accum: `4` / `8`
- effective tokens/step: `16384`

## Timing and throughput

- start: `2026-06-09 13:19:17`
- end: `2026-06-10 03:16:13`
- wall duration: `13h 56m`
- active duration: `13h 56m`
- average tok/s: `3265.52`
- stage tokens expected: `163,840,000`
- total tokens from log: `737.28M`

## Loss

- first logged train loss: `3.4078`
- last logged train loss: `3.2809`
- start-window avg loss: `3.3799`
- mid-window avg loss: `3.3275`
- end-window avg loss: `3.282`
- val loss trend: `falling`
- overfit signal: `no_obvious_overfit`

### Validation losses

- step `35500`: val_loss `3.2925` at `2026-06-09 13:59:59`
- step `36000`: val_loss `3.4682` at `2026-06-09 14:41:30`
- step `36500`: val_loss `3.0945` at `2026-06-09 15:22:59`
- step `37000`: val_loss `3.2092` at `2026-06-09 16:04:33`
- step `37500`: val_loss `3.5089` at `2026-06-09 16:46:02`
- step `38000`: val_loss `3.2891` at `2026-06-09 17:27:36`
- step `38500`: val_loss `3.2067` at `2026-06-09 18:09:05`
- step `39000`: val_loss `3.4693` at `2026-06-09 18:50:39`
- step `39500`: val_loss `3.3292` at `2026-06-09 19:32:08`
- step `40000`: val_loss `3.3446` at `2026-06-09 20:13:42`
- step `40500`: val_loss `3.0843` at `2026-06-09 20:55:11`
- step `41000`: val_loss `3.3021` at `2026-06-09 21:36:46`
- step `41500`: val_loss `3.2279` at `2026-06-09 22:18:16`
- step `42000`: val_loss `3.3796` at `2026-06-09 22:59:52`
- step `42500`: val_loss `3.3388` at `2026-06-09 23:44:58`
- step `43000`: val_loss `3.1826` at `2026-06-10 00:26:34`
- step `43500`: val_loss `3.3672` at `2026-06-10 01:08:04`
- step `44000`: val_loss `3.2275` at `2026-06-10 01:53:15`
- step `44500`: val_loss `3.2263` at `2026-06-10 02:34:45`
- step `45000`: val_loss `3.1953` at `2026-06-10 03:16:19`

## Stability

- NaN/Inf markers: `0`
- OOM markers: `0`
- crash/traceback markers: `0`
- clean interrupt seen: `False`
- GPU temps: not logged in `train.log`

## Partial/emergency files

- 45k `emergency.pt`: `False`
- 45k partial-like files: `[]`
- earlier 35k `step_0026000.pt`: `True`
- earlier 35k `emergency.pt`: `True`

## Checkpoints

- checkpoint dir size: `12.0 GB`
- checkpoint files: `11`

- `latest.pt`
- `step_0036000.pt`
- `step_0037000.pt`
- `step_0038000.pt`
- `step_0039000.pt`
- `step_0040000.pt`
- `step_0041000.pt`
- `step_0042000.pt`
- `step_0043000.pt`
- `step_0044000.pt`
- `step_0045000.pt`
