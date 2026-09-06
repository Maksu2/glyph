# Glyph-100M v2.3.1 final decision

**Verdict: 44k remains the best practical checkpoint.**

50k finished cleanly, but it did not beat 44k in the broad eval or seed-sensitivity check. Pretraining on dataset v2.3.1 is stopped; 50k is diagnostic latest, not best.

## Checkpoints

- best practical checkpoint: `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`
- latest diagnostic checkpoint: `checkpoints/glyph-100m-v2_3_1-50k/latest.pt`
- tokenizer SHA-256: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`
- status: `pretraining stopped`
- no 55k/60k continuation planned

## 50k training result

- status: `complete`
- duration: `7h 2m`
- avg tok/s: `3239.78`
- train loss: `3.2994` -> `3.2214`
- val loss trend: `rising`
- overfit signal: `watch_val_loss`
- final val loss: `3.3927`
- NaN/Inf/OOM/crash: `0` / `0` / `0`

## Broad eval

| checkpoint | avg quality | median quality |
|---|---:|---:|
| 44k | 6.198 | 8.0 |
| 45k | 5.721 | 6.0 |
| 50k | 5.644 | 6.0 |

## Pairwise

- 50k vs 44k: 50k wins `126`, 44k wins `160`, ties `194`.
- 50k vs 45k: 50k wins `145`, 45k wins `144`, ties `191`.

## Seed sensitivity

- 44k mean `8.37` vs 50k mean `7.55`; diff 50k-44k `-0.82`.
- 45k mean `7.06` vs 50k mean `7.55`; diff 50k-45k `0.49`.

## Next options

- A: run a small SFT smoke test on 44k, only with explicit approval.
- B: work on dataset v2.4 before any further pretraining.
- C: freeze the project and document it as a portfolio/research milestone.

## Non-goals

- no 55k / 60k / further v2.3.1 pretraining
- no automatic SFT
- no checkpoint cleanup
- no automatic publication as a final model
