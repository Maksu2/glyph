# Glyph-100M v2.4.2 matched trajectory: 10k vs 12.5k vs 15k

| checkpoint | avg score | median | natural | cutoff | repetition | pseudo-ency | web residue |
|---|---:|---:|---:|---:|---:|---:|---:|
| v242_10k | 3.450 | 4.000 | 6/40 | 34/40 | 13/40 | 0/40 | 0/40 |
| v242_12_5k | 2.350 | 1.000 | 5/40 | 36/40 | 24/40 | 0/40 | 0/40 |
| v242_15k | 3.525 | 4.000 | 10/40 | 33/40 | 13/40 | 0/40 | 0/40 |
| v231_44k | 3.350 | 4.000 | 12/40 | 30/40 | 20/40 | 0/40 | 0/40 |

## Pairwise heuristic

- v242_10k_vs_v242_12_5k: `{'v242_10k': 17, 'v242_12_5k': 5, 'ties': 18}`
- v242_12_5k_vs_v242_15k: `{'v242_12_5k': 4, 'v242_15k': 19, 'ties': 17}`
- v242_10k_vs_v242_15k: `{'v242_10k': 9, 'v242_15k': 12, 'ties': 19}`
- v242_10k_vs_v231_44k: `{'v242_10k': 12, 'v231_44k': 12, 'ties': 16}`
- v242_12_5k_vs_v231_44k: `{'v242_12_5k': 9, 'v231_44k': 18, 'ties': 13}`
- v242_15k_vs_v231_44k: `{'v242_15k': 13, 'v231_44k': 11, 'ties': 16}`
- heuristic best v2.4.2: `v242_15k`

The score is a deterministic diagnostic for endings, loops and residue. Manual semantic review is required.
