# Glyph-100M SFT v0.3 next decision

## Verdict

- verdict: `C`
- label: v0.3 nie poprawia v0.2
- recommendation: Nie kontynuować SFT w tym kierunku.

## Criteria A

- avg_score_ge_6: `False`
- repetition_le_2: `False`
- end_rate_ge_95: `True`
- real_web_le_2: `False`
- v03_clear_vs_v02: `False`
- manual_semantic_review_pass: `False`

## Evidence

- best mode: `no_repeat_ngram_size_3`
- best mode stats: `{'avg_score': 4.785, 'median_score': 4.0, 'repetition_samples': 4, 'end_token_rate': 0.9947916666666666, 'natural_endings': 192, 'real_web_residue': 5, 'web_residue': 5, 'pseudo_ency': 0, 'topic_drift': 0, 'generic_assistant_template': 0, 'first_token_correct': 59, 'avg_generated_tokens': 80, 'too_short_answers': 4, 'too_long_answers': 9}`
- v0.3 best vs v0.2: `{'sft_v0_2': 29, 'tie': 151, 'sft_v0_3_best': 20}`
- manual semantic review: `{'pass': False, 'finding': 'High automated scores still include factually or semantically wrong answers; format improved more than meaning.', 'examples': ['Eval was incorrectly described as a graphics processor.', 'A kilometre was incorrectly described as a projectile storing input data.', 'Train loss and gradient accumulation definitions remained nonsensical.']}`

## Constraints Honored

- No SFT v1 was run.
- No further training was run after v0.3 smoke.
- No pretraining was run.
- 50k was not used as base.
- Model was not published as final.
