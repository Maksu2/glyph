# Glyph-100M v2.3.1 25k eval report

## Checkpointy

- 15k: `checkpoints/glyph-100m-v2_3_1-preflight/latest.pt` · step `15000` · variant `glyph-100m`
- 25k: `checkpoints/glyph-100m-v2_3_1-25k/latest.pt` · step `25000` · variant `glyph-100m`
- tokenizer: `data/processed/tokenizer.model`
- tokenizer sha256: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`

## Ustawienia

- base LM continuation, nie assistant/instruction eval
- prompts: `eval/glyph-100m/stage2_completion_prompts.jsonl`
- prompt count: `12`
- seed base: `20260608`
- presets: normal_80, normal_120, creative_80, creative_120

## Wyniki heurystyczne

- 25k wins: 14
- 15k wins: 7
- ties: 27

## Summary 15k

```json
{
  "normal_80": {
    "count": 12,
    "avg_tokens_per_second": 68.94,
    "repetition_samples": 5,
    "natural_endings": 0,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 3,
    "cutoff_like_samples": 12,
    "avg_quality_score": 4.08
  },
  "normal_120": {
    "count": 12,
    "avg_tokens_per_second": 66.41,
    "repetition_samples": 8,
    "natural_endings": 0,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 4,
    "cutoff_like_samples": 12,
    "avg_quality_score": 2.08
  },
  "creative_80": {
    "count": 12,
    "avg_tokens_per_second": 72.46,
    "repetition_samples": 2,
    "natural_endings": 0,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 0,
    "cutoff_like_samples": 12,
    "avg_quality_score": 5.58
  },
  "creative_120": {
    "count": 12,
    "avg_tokens_per_second": 66.51,
    "repetition_samples": 3,
    "natural_endings": 1,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 0,
    "cutoff_like_samples": 11,
    "avg_quality_score": 5.58
  }
}
```

## Summary 25k

```json
{
  "normal_80": {
    "count": 12,
    "avg_tokens_per_second": 72.5,
    "repetition_samples": 2,
    "natural_endings": 0,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 0,
    "cutoff_like_samples": 12,
    "avg_quality_score": 5.58
  },
  "normal_120": {
    "count": 12,
    "avg_tokens_per_second": 65.8,
    "repetition_samples": 6,
    "natural_endings": 1,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 1,
    "pseudo_ency_samples": 0,
    "cutoff_like_samples": 11,
    "avg_quality_score": 4.33
  },
  "creative_80": {
    "count": 12,
    "avg_tokens_per_second": 72.53,
    "repetition_samples": 1,
    "natural_endings": 0,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 1,
    "cutoff_like_samples": 12,
    "avg_quality_score": 5.58
  },
  "creative_120": {
    "count": 12,
    "avg_tokens_per_second": 66.58,
    "repetition_samples": 3,
    "natural_endings": 0,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 1,
    "pseudo_ency_samples": 1,
    "cutoff_like_samples": 12,
    "avg_quality_score": 5
  }
}
```

## Werdykt

**C) 25k trochę lepsze, ale lepiej najpierw zrobić 35k jako kolejny punkt kontrolny.**

## Uwagi

- To nadal base LM, więc porównanie mierzy kontynuacje tekstu, nie odpowiedzi asystenta.
- Najważniejsze są próbki w `eval/glyph-100m/v2_3_1_15k_vs_25k.md`.
- Ten raport nie uruchamia kolejnego treningu.
