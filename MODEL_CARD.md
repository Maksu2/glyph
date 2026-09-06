# Model Card: Glyph-27M

![Glyph logo](assets/brand/glyph_logotext.png)

## Model Details

- Model name: `Glyph-27M`
- Project name: `Glyph`
- Base variant: `Glyph-27M Base`
- Current instruction experiment: `Glyph-27M SFT v0`
- Next prepared base variant: `Glyph-100M`
- Future planned instruct variant: `Glyph-100M Instruct`
- Language: Polish
- Type: decoder-only Transformer
- Framework: PyTorch
- Parameters: about 27M counted parameters; current config reports 27.21M
- Context length: 256 tokens
- Tokenizer: SentencePiece BPE
- Vocabulary size: 16,000
- Training location: local homelab

Description:

Glyph-27M is a small Polish decoder-only Transformer trained from scratch on a homelab.
It is now frozen as a proof-of-pipeline milestone: the tokenizer, corpus assembly,
training loop, checkpointing, dashboard, ROCm path, SFT path and evaluation flow
all worked end to end. The next model-capacity experiment is Glyph-100M.

## Variant Status

| Variant | Status | Notes |
|---|---|---|
| `Glyph-27M Base` | completed | 200,000-step pretraining milestone, final checkpoint in `checkpoints/final.pt` |
| `Glyph-27M SFT v0` | completed / experimental | improves endings and format, but eval v2 still shows weak instruction quality |
| `Glyph-100M` | preparation | larger base model, 512-token context, cleaner filtered corpus, no full training yet |

## Training Data

Training data is a Polish text mixture intended for base language-model pretraining:

- Polish Wikipedia
- mC4/OSCAR Polish fallback data
- Wolne Lektury

Processed local artifacts include:

- `data/processed/corpus_clean.txt`
- `data/processed/tokens.bin`
- `data/processed/val_tokens.bin`
- `data/processed/tokenizer.model`
- `data/processed/tokenizer.vocab`

SFT v0 data is a synthetic curated instruction dataset:

- 1,500 examples
- 90/10 stratified train/val split
- template: `<|user|> ... <|assistant|> ... <|end|>`
- final checkpoint: `checkpoints/sft-v0/glyph-27m-sft-v0-final.pt`

## Intended Use

Glyph-27M is intended for:

- educational experiments
- research and learning about small language models
- portfolio/demo use
- local inference experiments
- studying Polish tokenizer, corpus, and decoder-only Transformer behavior

## Not Intended For

Glyph-27M is not intended for:

- production assistant use
- factual question answering
- safety-critical decisions
- medical, legal, or financial advice
- automated moderation
- public API use without rate limits and monitoring

## Limitations

Known limitations:

- repetition and phrase loops
- topic drift
- short 256-token context
- small model size
- noisy dataset artifacts
- unreliable factual recall
- weak long-context coherence
- SFT v0 can improve format while still drifting or repeating
- no RLHF or safety alignment

## Evaluation

Current evaluation uses:

- fixed Polish continuation prompts
- validation loss from `data/processed/val_tokens.bin`
- Gemma 4 as an external judge for qualitative scoring

Gemma evaluation is a diagnostic tool, not a replacement for manual review.

## Safety Notes

Glyph-27M Base should be treated as a text continuation model. Glyph-27M SFT v0 is a small instruction-tuning experiment, not a reliable assistant. It may generate incorrect, repetitive, offensive, or nonsensical text. Outputs should be manually reviewed, especially when shared publicly.

Glyph-100M should not be described as trained or usable until a stage run has
actually completed and been evaluated.
