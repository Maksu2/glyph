# Glyph-100M v2.3.1 pre-50k manifest

- created_at_utc: `2026-06-11T20:58:36+00:00`
- decision: `50k is diagnostic only; 44k remains best before experiment`
- dataset: `glyph100_v2_3_1`
- tokenizer: `data/processed/tokenizer.model`
- tokenizer SHA expected: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`
- tokenizer SHA actual: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`
- start checkpoint: `checkpoints/glyph-100m-v2_3_1-45k/latest.pt`
- target step: `50000`
- output checkpoint dir: `checkpoints/glyph-100m-v2_3_1-50k`
- output log dir: `logs/glyph-100m-v2_3_1-50k`

## Checkpoints

| role | path | exists | step | variant | dataset | batch/accum | optimizer | scheduler | size |
|---|---|---:|---:|---|---|---|---:|---:|---:|
| best_practical_checkpoint_before_50k | `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt` | True | 44000 | glyph-100m | glyph100_v2_3_1 | 4/8 | True | True | 1175128433 |
| latest_checkpoint_before_50k | `checkpoints/glyph-100m-v2_3_1-45k/latest.pt` | True | 45000 | glyph-100m | glyph100_v2_3_1 | 4/8 | True | True | 1175128015 |
| step_45k_checkpoint | `checkpoints/glyph-100m-v2_3_1-45k/step_0045000.pt` | True | 45000 | glyph-100m | glyph100_v2_3_1 | 4/8 | True | True | 1175128433 |

## Read

- 44k remains the best practical checkpoint before this diagnostic run.
- 45k is the latest healthy checkpoint and the resume source for the 50k diagnostic run.
- The 50k checkpoint must not become the best checkpoint without a separate eval.
