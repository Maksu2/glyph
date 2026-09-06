# Glyph-100M v2.3.1 inference preset eval

Ten raport rozdziela jakość checkpointu od jakości ustawień generacji.

## Preset Quality Across Checkpoints

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

## Preset Wins vs 35k Baseline

| preset | candidate wins | 35k wins | ties |
|---|---:|---:|---:|
| current_normal_80 | 160 | 123 | 77 |
| current_normal_120 | 153 | 142 | 65 |
| safer_low_temp_80 | 114 | 141 | 105 |
| safer_low_temp_120 | 91 | 132 | 137 |
| nucleus_safe_80 | 120 | 126 | 114 |
| nucleus_safe_120 | 116 | 124 | 120 |
| repetition_guard_80 | 32 | 50 | 278 |
| repetition_guard_120 | 41 | 59 | 260 |

## Read

- best preset by avg quality: `repetition_guard_80`
- best checkpoint by avg quality: `44k`
- `nucleus_safe` uses top_p=0.9 with top_k disabled.
- `repetition_guard` uses repetition_penalty=1.15.
