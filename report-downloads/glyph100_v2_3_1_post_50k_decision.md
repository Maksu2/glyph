# Glyph-100M v2.3.1 post-50k decision

**Verdict: B) 44k zostaje best practical checkpoint.**

50k is technically healthy and slightly better than 45k in seed sensitivity, but it does not beat 44k in broad eval or seed mean score.

## Decision

- best practical checkpoint: `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`
- latest diagnostic checkpoint: `checkpoints/glyph-100m-v2_3_1-50k/latest.pt`
- 50k is diagnostic latest, not best.
- Model status: base LM only, not chatbot, not final published model.

## Training 45k -> 50k

- status: `complete`
- duration: `7h 2m`
- steps: `45000` -> `50000`
- avg tok/s: `3239.78`
- train loss: `3.2994` -> `3.2214`
- train loss min/max: `3.1459` / `3.3619`
- val loss trend: `rising`
- overfit signal: `watch_val_loss`
- NaN/Inf/OOM/crash counts: `0` / `0` / `0`

### Validation losses

- step `45500`: `3.1731` at `2026-06-11 21:41:16`
- step `46000`: `3.177` at `2026-06-11 22:22:50`
- step `46500`: `3.1255` at `2026-06-11 23:04:22`
- step `47000`: `2.9851` at `2026-06-11 23:49:42`
- step `47500`: `2.9998` at `2026-06-12 00:31:14`
- step `48000`: `3.1695` at `2026-06-12 01:12:50`
- step `48500`: `2.9773` at `2026-06-12 01:57:57`
- step `49000`: `3.1606` at `2026-06-12 02:39:33`
- step `49500`: `3.1279` at `2026-06-12 03:21:05`
- step `50000`: `3.3927` at `2026-06-12 04:02:44`

## Broad Eval

| checkpoint | avg quality | median quality | repetition | natural endings | cutoff-like | pseudo-ency | web residue | wiki residue | drift | overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 44k | 6.198 | 8.0 | 214/480 | 22/480 | 458/480 | 58/480 | 20/480 | 3/480 | 243/480 | 0.115 |
| 45k | 5.721 | 6.0 | 223/480 | 16/480 | 464/480 | 61/480 | 27/480 | 2/480 | 263/480 | 0.103 |
| 50k | 5.644 | 6.0 | 237/480 | 10/480 | 470/480 | 62/480 | 28/480 | 1/480 | 229/480 | 0.15 |

## Pairwise

- 50k vs 44k: 50k wins `126`, 44k wins `160`, ties `194`.
- 50k vs 45k: 50k wins `145`, 45k wins `144`, ties `191`.

## Seed Sensitivity

- 44k vs 50k mean: `8.37` vs `7.55`; diff 50k-44k `-0.82`; diff > noise `2/20`.
- 45k vs 50k mean: `7.06` vs `7.55`; diff 50k-45k `0.49`; diff > noise `3/20`.

## Read

- 50k is technically healthy, but quality does not clearly improve over 44k.
- 50k slightly beats 45k in some stochastic checks, but not enough to replace 44k.
- Further pretraining on this dataset is not justified by this diagnostic result without a new decision.
- Next rational step is either a small SFT smoke test on the best checkpoint or dataset v2.4 work, not more blind pretraining.
