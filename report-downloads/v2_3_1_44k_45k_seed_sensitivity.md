# Glyph-100M v2.3.1 44k vs 45k seed sensitivity

Stochastic eval: 20 broad prompts, `current_normal_80`, 5 seeds.

- 45k wins: `23`
- 44k wins: `44`
- ties: `33`

## Overall seed stats

```json
{
  "mean_44k": 8.37,
  "mean_45k": 7.06,
  "diff_45k_minus_44k": -1.31,
  "stdev_44k": 3.8916,
  "stdev_45k": 4.483
}
```

- prompts where mean diff exceeds local seed noise: `1/20`

## Per-prompt mean/stdev

| prompt | mean 44k | mean 45k | diff | stdev 44k | stdev 45k | diff > noise |
|---|---:|---:|---:|---:|---:|---:|
| broad-031 | 9.6 | 6.2 | -3.4 | 1.3416 | 3.8341 | False |
| broad-032 | 6.2 | 2.2 | -4.0 | 4.1473 | 3.8987 | False |
| broad-025 | 11 | 9 | -2 | 2.8284 | 5.3385 | False |
| broad-026 | 11.8 | 10.6 | -1.2 | 1.6432 | 2.1909 | False |
| broad-007 | 9.2 | 9.2 | 0.0 | 4.5497 | 2.8636 | False |
| broad-008 | 11.2 | 6.6 | -4.6 | 2.2804 | 5.2726 | False |
| broad-001 | 7.2 | 9 | 1.8 | 2.49 | 0.0 | False |
| broad-002 | 6.6 | 7.2 | 0.6 | 2.51 | 5.1672 | False |
| broad-055 | 9 | 7.6 | -1.4 | 2.1213 | 3.7815 | False |
| broad-056 | 6.8 | 7.4 | 0.6 | 4.0249 | 4.5056 | False |
| broad-049 | 5.4 | 6.4 | 1.0 | 5.3666 | 4.3359 | False |
| broad-050 | 6.8 | 2.8 | -4.0 | 6.4962 | 4.8683 | False |
| broad-019 | 9 | 7.2 | -1.8 | 0.0 | 4.7117 | False |
| broad-020 | 8 | 10 | 2 | 4.7958 | 3.0822 | False |
| broad-043 | 8.6 | 7.6 | -1.0 | 2.881 | 5.4589 | False |
| broad-044 | 8.4 | 2 | -6.4 | 6.3875 | 6.5574 | False |
| broad-037 | 7.6 | 8.4 | 0.8 | 3.9749 | 2.51 | False |
| broad-038 | 6.2 | 10.6 | 4.4 | 6.6106 | 0.8944 | False |
| broad-013 | 8.4 | 7.6 | -0.8 | 1.3416 | 1.9494 | False |
| broad-014 | 10.4 | 3.6 | -6.8 | 1.9494 | 4.1593 | True |