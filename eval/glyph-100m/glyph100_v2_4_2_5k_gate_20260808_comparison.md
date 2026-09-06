# Glyph-100M v2.4.2 5k matched quality gate

| checkpoint | avg score | median | natural | cutoff | repetition | pseudo-ency | web residue |
|---|---:|---:|---:|---:|---:|---:|---:|
| v241_5k | 3.000 | 4.000 | 6/40 | 40/40 | 13/40 | 7/40 | 0/40 |
| v242_1k | 2.575 | 2.500 | 2/40 | 40/40 | 15/40 | 0/40 | 0/40 |
| v242_3k | 3.225 | 4.000 | 5/40 | 39/40 | 12/40 | 0/40 | 0/40 |
| v242_5k | 3.175 | 4.000 | 5/40 | 40/40 | 13/40 | 0/40 | 0/40 |

## Pairwise heuristic

- v2.4.1 5k vs v2.4.2 5k: `{'v241_5k': 9, 'v242_5k': 14, 'ties': 17}`
- v2.4.2 1k vs 5k: `{'v242_1k': 7, 'v242_5k': 16, 'ties': 17}`
- v2.4.2 3k vs 5k: `{'v242_3k': 11, 'v242_5k': 11, 'ties': 18}`
- heuristic best checkpoint: `v242_3k`

## v2.4.2 validation loss

- step `500`: `7.3346`
- step `1000`: `6.4385`
- step `1500`: `5.9524`
- step `2000`: `5.6915`
- step `2500`: `5.4662`
- step `3000`: `5.1757`
- step `3500`: `4.9787`
- step `4000`: `4.8189`
- step `4500`: `4.7063`
- step `5000`: `4.5994`

The score is a deterministic diagnostic for endings, loops and residue. Manual semantic review is part of the gate.
