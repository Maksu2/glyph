# Glyph-100M v2.4.1: porównanie 5k / 7,5k / 10k

Base-LM continuation eval, nie test asystenta. Wynik jakości jest heurystyką
zakończeń, pętli i residue; próbki wymagają oceny semantycznej.

## Trajektoria

| checkpoint | avg score | median | natural | cutoff | repetition | pseudo-ency | web residue |
|---|---:|---:|---:|---:|---:|---:|---:|
| 5k | 3.000 | 4.000 | 6/40 | 40/40 | 13/40 | 7/40 | 0/40 |
| 7.5k | 3.000 | 4.000 | 2/40 | 39/40 | 13/40 | 4/40 | 0/40 |
| 10k | 3.025 | 4.000 | 4/40 | 37/40 | 14/40 | 2/40 | 0/40 |

## Pairwise

- 7,5k vs 5k: `{'5k': 12, '7.5k': 12, 'ties': 16}`
- 10k vs 7,5k: `{'7.5k': 11, '10k': 11, 'ties': 18}`
- 10k vs 5k: `{'5k': 13, '10k': 15, 'ties': 12}`
- Heurystycznie najlepszy checkpoint: `10k`

## Validation loss

- step `250`: `7.9565`
- step `500`: `7.3277`
- step `750`: `6.8266`
- step `1000`: `6.4298`
- step `1500`: `5.9220`
- step `2000`: `5.6551`
- step `2500`: `5.3442`
- step `3000`: `5.0933`
- step `3500`: `4.9110`
- step `4000`: `4.7702`
- step `4500`: `4.6665`
- step `5000`: `4.5902`
- step `5500`: `4.5096`
- step `6000`: `4.4387`
- step `6500`: `4.3872`
- step `7000`: `4.3601`
- step `7500`: `4.3126`
- step `8000`: `4.2606`
- step `8500`: `4.2473`
- step `9000`: `4.1908`
- step `9500`: `4.1548`
- step `10000`: `4.1100`
