# Glyph-100M SFT v0.3 dataset plan

## Diagnosis from v0.2

- v0.2 improved format and repetition, but did not clearly beat v0.1 enough for SFT v1.
- Best decoding was `no_repeat_ngram_size_3`, which suggests decoding helps but does not remove the dataset issue.
- Manual audit found real web-residue cases, so v0.3 adds explicit anti-web examples.
- v0.2 still had semantic weaknesses in definitions and out-of-dataset prompts.

## What to Add

- More semantically correct definitions and basic facts.
- More missing-data answers with varied first words, not just `Nie`.
- Explicit anti-web-residue examples: no SEO, no shop text, no cookies/privacy boilerplate.
- Anti-repetition examples that end after one clear thought.
- More natural Polish one-to-four sentence answers.

## What to Rewrite / Avoid

- Rewrite repeated starts such as `Nie`, `Najpierw`, `Warto`, `Brakuje`.
- Avoid pseudo-ency patterns: dates, gmina/powiat/wojewodztwo filler.
- Avoid empty refusals and short answers without semantic content.
