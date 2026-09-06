# Glyph-100M v2.4.2 10k matched quality gate

| checkpoint | avg score | median | natural | cutoff | repetition | pseudo-ency | web residue |
|---|---:|---:|---:|---:|---:|---:|---:|
| v241_10k | 3.025 | 4.000 | 4/40 | 37/40 | 14/40 | 2/40 | 0/40 |
| v242_5k | 3.175 | 4.000 | 5/40 | 40/40 | 13/40 | 0/40 | 0/40 |
| v242_10k | 3.200 | 4.000 | 9/40 | 34/40 | 17/40 | 1/40 | 0/40 |

## Pairwise heuristic

- v2.4.2 5k vs 10k: `{'v242_5k': 10, 'v242_10k': 11, 'ties': 19}`
- v2.4.1 10k vs v2.4.2 10k: `{'v241_10k': 8, 'v242_10k': 9, 'ties': 23}`
- heuristic best checkpoint: `v242_10k`

The score is a deterministic diagnostic for endings, loops and residue. Manual semantic review is required.
