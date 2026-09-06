# Glyph-100M v2.3.1 44k -> 45k training audit

- technical verdict: `healthy`
- log: `logs/glyph-100m-v2_3_1-45k/train.log`
- latest model tensors match `step_0045000.pt`: `True`

## Checkpoints

| checkpoint | exists | size | step | variant | dataset | tokenizer sha ok | batch/accum | optimizer | scheduler | validation |
|---|---:|---:|---:|---|---|---:|---|---:|---:|---|
| 44k | True | 1175128433 | 44000/44000 | glyph-100m | glyph100_v2_3_1 | True | 4/8 | True | True | ok |
| 45k_step | True | 1175128433 | 45000/45000 | glyph-100m | glyph100_v2_3_1 | True | 4/8 | True | True | ok |
| 45k_latest | True | 1175128015 | 45000/45000 | glyph-100m | glyph100_v2_3_1 | True | 4/8 | True | True | ok |

## Training Windows

| window | steps | loss avg | loss min | loss max | lr min | lr max | avg tok/s |
|---|---:|---:|---:|---:|---:|---:|---:|
| 43000_44000 | 101 | 3.286674 | 3.1969 | 3.3899 | 0.000181 | 0.000182 | 3174.94 |
| 44000_45000 | 101 | 3.283262 | 3.1851 | 3.3526 | 0.00018 | 0.000181 | 3287.64 |
| 43500_44000 | 51 | 3.287773 | 3.2167 | 3.3832 | 0.000181 | 0.000181 | 3069.1 |
| 44000_44500 | 51 | 3.284453 | 3.1851 | 3.3526 | 0.00018 | 0.000181 | 3285.04 |
| 44500_45000 | 51 | 3.281984 | 3.2235 | 3.3476 | 0.00018 | 0.00018 | 3290.33 |

## Validation Losses

- step `43500`: `3.3672` at `2026-06-10 01:08:04`
- step `44000`: `3.2275` at `2026-06-10 01:53:15`
- step `44500`: `3.2263` at `2026-06-10 02:34:45`
- step `45000`: `3.1953` at `2026-06-10 03:16:19`

## Log Markers

- resume lines: `1`
- range lines: `['2026-06-09 13:18:26 Training from step 35,001 to 45,000']`
- limited-run lines: `['2026-06-09 13:18:26 Limited run enabled: target step 45,000', '2026-06-10 03:16:19 Limited run complete; no final checkpoint was written.']`
- dataset/config lines: `3`
- emergency lines: `0`
- NaN/Inf lines: `0`
- OOM lines: `0`
- crash/exception lines: `0`

## Read

- The checkpoint metadata and log range are consistent with a normal 35k->45k continuation.
- There is no log evidence of dataset/tokenizer/config change between 44k and 45k.
- The 45k `latest.pt` contains the same model tensors as `step_0045000.pt`.
- Any quality drop must be investigated through eval stability rather than an obvious checkpoint/training corruption.
