# Glyph-100M v2.3.1 best checkpoint decision

**Verdict: B) 40k/42k/44k zostaje best checkpoint**

Reason: 44k has the best broad quality score.

## Direct Answers

1. Best qualitative checkpoint: `44k`.
2. 45k worse than 35k: `False` by aggregate quality score.
3. Best intermediate checkpoint: `44k`.
4. Best inference preset: `repetition_guard_80`.
5. 50k: not recommended from this eval unless a later manual review overturns it.
6. Next: small SFT test is more rational than more pretraining on the same data if the goal is useful behavior.
7. Problem shape: mostly dataset/style and base-LM sampling limits; not a training crash. The model still has cutoff-like completions and pseudo-ency tendencies.

## Checkpoint Summary

| item | avg_q | rep | natural | cutoff | pseudo | web | wiki | drift | overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 35k | 5.719 | 235/480 | 18/480 | 462/480 | 46/480 | 15/480 | 4/480 | 277/480 | 0.085 |
| 36k | 5.715 | 228/480 | 21/480 | 459/480 | 84/480 | 18/480 | 2/480 | 245/480 | 0.103 |
| 38k | 5.135 | 250/480 | 16/480 | 464/480 | 65/480 | 8/480 | 5/480 | 278/480 | 0.076 |
| 40k | 5.225 | 253/480 | 17/480 | 463/480 | 73/480 | 18/480 | 16/480 | 232/480 | 0.133 |
| 42k | 6.019 | 202/480 | 26/480 | 454/480 | 86/480 | 20/480 | 5/480 | 266/480 | 0.109 |
| 44k | 6.198 | 214/480 | 22/480 | 458/480 | 58/480 | 20/480 | 3/480 | 243/480 | 0.115 |
| 45k | 5.721 | 223/480 | 16/480 | 464/480 | 61/480 | 27/480 | 2/480 | 263/480 | 0.103 |

## Preset Summary

| item | avg_q | rep | natural | cutoff | pseudo | web | wiki | drift | overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| current_normal_80 | 6.731 | 164/420 | 22/420 | 398/420 | 62/420 | 16/420 | 4/420 | 214/420 | 0.119 |
| current_normal_120 | 5.017 | 248/420 | 22/420 | 398/420 | 71/420 | 20/420 | 6/420 | 206/420 | 0.137 |
| safer_low_temp_80 | 4.083 | 291/420 | 23/420 | 397/420 | 61/420 | 11/420 | 3/420 | 210/420 | 0.116 |
| safer_low_temp_120 | 2.036 | 368/420 | 17/420 | 403/420 | 74/420 | 14/420 | 3/420 | 204/420 | 0.127 |
| nucleus_safe_80 | 5.757 | 221/420 | 19/420 | 401/420 | 49/420 | 14/420 | 4/420 | 204/420 | 0.136 |
| nucleus_safe_120 | 3.574 | 313/420 | 18/420 | 402/420 | 63/420 | 16/420 | 5/420 | 198/420 | 0.153 |
| repetition_guard_80 | 9.129 | 0/420 | 9/420 | 411/420 | 41/420 | 13/420 | 5/420 | 285/420 | 0.019 |
| repetition_guard_120 | 9.081 | 0/420 | 6/420 | 414/420 | 52/420 | 22/420 | 7/420 | 283/420 | 0.022 |

## Strict Rescore Caveat

The broad eval was rescored with a stronger penalty for topic drift and low prompt overlap. This keeps `44k` as the best checkpoint, but shows why the preset result needs caution: `repetition_guard_80` removes repeated 4-grams, yet still has high topic drift, so it is not a complete fix.

| checkpoint | strict avg_q | repetition | drift | pseudo | web | natural |
|---|---:|---:|---:|---:|---:|---:|
| 35k | -9.2 | 235/480 | 277/480 | 46/480 | 15/480 | 18/480 |
| 36k | -8.923 | 228/480 | 245/480 | 84/480 | 18/480 | 21/480 |
| 38k | -10.723 | 250/480 | 278/480 | 65/480 | 8/480 | 16/480 |
| 40k | -9.36 | 253/480 | 232/480 | 73/480 | 18/480 | 17/480 |
| 42k | -8.952 | 202/480 | 266/480 | 86/480 | 20/480 | 26/480 |
| 44k | -8.254 | 214/480 | 243/480 | 58/480 | 20/480 | 22/480 |
| 45k | -9.037 | 223/480 | 263/480 | 61/480 | 27/480 | 16/480 |

Strict wins vs 35k:

- `36k`: candidate `152`, 35k `152`, ties `176`
- `38k`: candidate `127`, 35k `185`, ties `168`
- `40k`: candidate `142`, 35k `179`, ties `159`
- `42k`: candidate `150`, 35k `154`, ties `176`
- `44k`: candidate `179`, 35k `135`, ties `166`
- `45k`: candidate `160`, 35k `158`, ties `162`
