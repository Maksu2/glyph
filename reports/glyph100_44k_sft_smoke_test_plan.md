# Glyph-100M 44k SFT smoke test plan

**Status: plan only. SFT was not started.**

## Goal

Check whether the best practical Glyph-100M base checkpoint can learn a simple answer format from a small, clean supervised dataset without overwriting any pretraining checkpoint.

## Inputs

- base checkpoint: `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`
- dataset size: `1000-3000` very clean examples
- tokenizer: existing SentencePiece BPE, no new tokenizer

## Output

- checkpoint dir: `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke`
- separate logs and eval outputs
- no automatic public demo

## Dataset shape

- short direct factual answers
- rewrite/summarize tasks where the output is only the rewritten text
- missing-data examples with varied wording
- anti-rambling examples with explicit short endings
- avoid repeated template phrases from Glyph-27M SFT v0

## Eval

- before/after on the same prompts
- measure instruction format, topic adherence, repetition and generic-template drift
- keep base LM continuation eval separate from instruction eval

## Safety

- do not overwrite pretraining checkpoints
- do not publish automatically
- stop after smoke test and review samples before any larger SFT
