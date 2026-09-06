# Glyph-100M SFT v0.2 final next decision

## Verdict

- verdict: `D`
- label: główny problem to dataset/repetition
- recommendation: Zrobić dataset v0.3; nie skalować SFT v0.2.

## Evidence

- best decoding mode: `no_repeat_ngram_size_3`
- best mode stats: `{'rows': 150, 'avg_score': 5.38, 'median_score': 4.0, 'repetition_samples': 1, 'end_token_rate': 1.0, 'natural_endings': 142, 'pseudo_ency': 0, 'web_residue': 4, 'topic_drift': 0, 'generic_assistant_template': 0, 'first_token_correct': 43, 'avg_generated_tokens': 80, 'too_short_answers': 1, 'too_long_answers': 8}`
- v0.2 vs v0.1: `{'tie': 121, 'sft_v0_2': 17, 'sft_v0_1': 12}`
- web classification counts: `{'real web residue': 13}`

## Constraints Honored

- No SFT v1 was run.
- No larger SFT was run.
- No pretraining was run.
- 50k was not used as base.
- Model was not published as final.
