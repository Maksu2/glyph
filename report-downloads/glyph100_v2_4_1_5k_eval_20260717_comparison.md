# Glyph-100M v2.4.1: 1k–5k checkpoint comparison

## Checkpoint trajectory

| checkpoint | avg score | median | natural | cutoff | repetition | pseudo-ency | web residue |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1k | 2.150 | 1.000 | 6/40 | 37/40 | 22/40 | 12/40 | 0/40 |
| 2k | 2.975 | 4.000 | 9/40 | 33/40 | 17/40 | 9/40 | 0/40 |
| 3k | 2.825 | 4.000 | 5/40 | 37/40 | 16/40 | 6/40 | 0/40 |
| 4k | 2.875 | 4.000 | 4/40 | 39/40 | 11/40 | 11/40 | 0/40 |
| 5k | 3.000 | 4.000 | 6/40 | 40/40 | 13/40 | 7/40 | 0/40 |

## Validation loss

- step `250`: `7.9565`
- step `500`: `7.3277`
- step `750`: `6.8266`
- step `1000`: `6.4298`
- step `1500`: `5.922`
- step `2000`: `5.6551`
- step `2500`: `5.3442`
- step `3000`: `5.0933`
- step `3500`: `4.911`
- step `4000`: `4.7702`
- step `4500`: `4.6665`
- step `5000`: `4.5902`

## Pairwise heuristic

- 1k vs 5k: `{'1k': 7, '5k': 21, 'ties': 12}`
- 4k vs 5k: `{'4k': 10, '5k': 14, 'ties': 16}`
- heuristic best checkpoint: `5k`

The score is a deterministic diagnostic for endings, loops and residue. It is not a substitute for manual semantic review.
