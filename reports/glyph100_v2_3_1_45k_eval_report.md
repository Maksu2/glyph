# Glyph-100M v2.3.1 45k eval report

## Checkpointy

- 35k: `checkpoints/glyph-100m-v2_3_1-35k/latest.pt` · step `35000` · variant `glyph-100m`
- 45k: `checkpoints/glyph-100m-v2_3_1-45k/latest.pt` · step `45000` · variant `glyph-100m`
- tokenizer: `data/processed/tokenizer.model`
- tokenizer sha256 actual: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`

## Ustawienia

- base LM continuation, nie assistant/instruction eval
- prompts: `eval/glyph-100m/stage2_completion_prompts.jsonl`
- prompt count: `12`
- seed base: `20260609`
- presets: normal_80, normal_120, creative_80, creative_120

## Wyniki heurystyczne

- 45k wins: 7
- 35k wins: 13
- ties: 28

## Summary 35k

```json
{
  "normal_80": {
    "count": 12,
    "avg_tokens_per_second": 69.16,
    "repetition_samples": 2,
    "natural_endings": 0,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 1,
    "cutoff_like_samples": 12,
    "avg_quality_score": 5.33
  },
  "normal_120": {
    "count": 12,
    "avg_tokens_per_second": 66.31,
    "repetition_samples": 5,
    "natural_endings": 0,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 1,
    "cutoff_like_samples": 12,
    "avg_quality_score": 4.08
  },
  "creative_80": {
    "count": 12,
    "avg_tokens_per_second": 72.44,
    "repetition_samples": 0,
    "natural_endings": 0,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 2,
    "cutoff_like_samples": 12,
    "avg_quality_score": 5.75
  },
  "creative_120": {
    "count": 12,
    "avg_tokens_per_second": 66.44,
    "repetition_samples": 0,
    "natural_endings": 1,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 2,
    "cutoff_like_samples": 11,
    "avg_quality_score": 5.92
  }
}
```

## Summary 45k

```json
{
  "normal_80": {
    "count": 12,
    "avg_tokens_per_second": 71.9,
    "repetition_samples": 3,
    "natural_endings": 0,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 3,
    "cutoff_like_samples": 12,
    "avg_quality_score": 4.67
  },
  "normal_120": {
    "count": 12,
    "avg_tokens_per_second": 66.43,
    "repetition_samples": 3,
    "natural_endings": 0,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 4,
    "cutoff_like_samples": 12,
    "avg_quality_score": 4.58
  },
  "creative_80": {
    "count": 12,
    "avg_tokens_per_second": 72.49,
    "repetition_samples": 1,
    "natural_endings": 0,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 2,
    "cutoff_like_samples": 12,
    "avg_quality_score": 5.33
  },
  "creative_120": {
    "count": 12,
    "avg_tokens_per_second": 66.46,
    "repetition_samples": 2,
    "natural_endings": 0,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 4,
    "cutoff_like_samples": 12,
    "avg_quality_score": 4.5
  }
}
```

## Werdykt

**D) Poprawić dataset przed dalszym treningiem.**

## Uwagi

- To nadal base LM, więc porównanie mierzy kontynuacje tekstu, nie odpowiedzi asystenta.
- Najważniejsze są próbki w `eval/glyph-100m/v2_3_1_35k_vs_45k.md`.
- Ten raport nie uruchamia kolejnego treningu.
