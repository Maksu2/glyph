# Glyph-100M v2.3.1 50k seed sensitivity

Stochastic eval: 20 broad prompts, `current_normal_80`, 5 seeds.

## 50k vs 44k

- 50k wins: `28`
- 44k wins: `34`
- ties: `38`

```json
{
  "mean_44k": 8.37,
  "mean_50k": 7.55,
  "diff_50k_minus_44k": -0.82,
  "stdev_44k": 3.8916,
  "stdev_50k": 4.0211
}
```

- prompts where mean diff exceeds local seed noise: `2/20`

## 50k vs 45k

- 50k wins: `38`
- 45k wins: `32`
- ties: `30`

```json
{
  "mean_45k": 7.06,
  "mean_50k": 7.55,
  "diff_50k_minus_45k": 0.49,
  "stdev_45k": 4.483,
  "stdev_50k": 4.0211
}
```

- prompts where mean diff exceeds local seed noise: `3/20`
