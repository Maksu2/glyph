# Glyph-100M v2.3.1 trend: 25k -> 35k -> 45k

Base LM continuation eval. To nie jest ocena modelu jako asystenta.

## Aggregate Metrics

| checkpoint | repetition | natural endings | cutoff-like | pseudo-ency | web residue | wiki residue | avg quality | final val_loss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 25k | 18/48 | 1/48 | 47/48 | 6/48 | 6/48 | 0/48 | 3.9 | 3.4745 |
| 35k | 7/48 | 1/48 | 47/48 | 6/48 | 0/48 | 0/48 | 5.27 | 3.2317 |
| 45k | 9/48 | 0/48 | 48/48 | 13/48 | 0/48 | 0/48 | 4.77 | 3.1953 |

## Pairwise Comparisons

### 25k vs 35k

- 35k wins: `20`
- 25k wins: `2`
- ties: `26`

### 35k vs 45k

- 45k wins: `7`
- 35k wins: `13`
- ties: `28`

## Read

- 35k was the clear improvement step: fewer repetitions than 25k and much better pairwise score.
- 45k does not improve as strongly as 35k did over 25k; in this eval it loses more often than it wins.
- 45k keeps web/wiki residue near zero, but pseudo-ency patterns increase and natural endings do not improve.
- Cutoff-like completions remain the dominant issue across all checkpoints.
- The final validation loss at 45k is lower than the noisy 35k endpoint, but sample quality does not clearly track that improvement.

## Decision Implication

The 45k checkpoint should not automatically justify a 50k continuation. The next decision should be based on either a broader eval/inference sweep or a deliberate stop/pre-SFT branch, not momentum alone.
