# Glyph

![Glyph logo](assets/brand/glyph_logotext.png)

Glyph is a family of tiny Polish language models trained from scratch on a single
home GPU. No cluster, no cloud bill — just one graphics card, a lot of patience,
and the question: how good a Polish model can you grow in a homelab?

## Why this exists

Big models are trained behind closed doors on hardware most people will never
touch. Glyph is the opposite: every step happens in the open, on consumer
hardware, with all the mistakes and fixes visible in the commit history. If you
have ever wondered what it actually takes to take a language model from zero to
something that speaks your language — this is that story, with code.

## The story so far

**Glyph-27M — the proof that the pipeline works.** Six layers, 256 tokens of
context, 200,000 training steps. It learned Polish grammar, then promptly started
looping phrases and drifting off-topic. A small instruction-tuning experiment
(1,500 hand-picked examples) taught it to at least answer in the right shape.
Lesson: the training loop, tokenizer, checkpointing and evaluation all worked
end to end. Capacity was the bottleneck, not the plumbing.

**Glyph-100M — the real attempt.** Twelve layers, 768 wide, 512 tokens of
context, ~98M parameters. But a bigger model only helps if you feed it better
text, so most of the work went into the dataset: iterating the Polish mixture
through versions v2–v2.4 (Wikipedia, books, web), auditing every source with
accept/reject samples, and measuring what each change actually did. The v2.4.2
checkpoint reached 15,000 steps (train loss 4.094, validation 3.976, ~246M
tokens) and is now awaiting evaluation before anything continues.

**v2.5 — rebuilding the food supply.** The current work: throwing the mixture
out and rebuilding it properly — download, filtering, tokenization, MinHash
dedup, cross-referencing — targeting roughly 715M clean Polish tokens. A model
is what it eats.

## How it trains

- Decoder-only Transformer, PyTorch, SentencePiece BPE (16k vocabulary)
- Warmup–stable–decay learning-rate schedule, with short cooldown branches
  spun off from main checkpoints for evaluation
- Long runs happen overnight, when electricity is cheap and nobody hears the fans

## How good is it?

Honestly? It is a research toy, not an assistant. It writes grammatical Polish,
then loses the thread. It hallucinates with confidence. It has no safety
alignment and should not be trusted for anything factual, medical, legal, or
financial. The interesting part is not the scores — it is watching a pile of
matrix multiplications slowly learn a language, and knowing exactly which data
and which decisions shaped it.

Evaluation is done with fixed Polish continuation prompts, graded by a separate
larger model acting as judge (never part of training). Sample transcripts and
per-version dataset audits live in `reports/` and `data/reports/`.

## What's in this repo

```text
├── train.py            # training loop (WSD schedule, checkpointing)
├── generate.py         # sample continuations from a checkpoint
├── finetune.py         # supervised fine-tuning path
├── model/              # Transformer definition
├── config.py           # model variants + hyperparameters
├── scripts/            # dataset pipeline stages (download → filter →
│                       #   tokenize → dedup → cross-ref → build)
├── eval/               # fixed Polish evaluation prompts
├── reports/            # samples, eval transcripts, dataset audits
└── data/reports/       # per-mixture-version lineage (v2–v2.5)
```

## What is NOT here

Checkpoints, token streams and raw datasets are far too large for git and stay
local — so this repo is the recipe and the lab notebook, not a download-and-run
package. The code is published as-is: readable, hacky in places, and honest
about what it is.

## Models

| Model | Params | Context | Status |
|---|---|---|---|
| Glyph-27M Base | 27M | 256 | done (200k steps) |
| Glyph-27M SFT v0 | 27M | 256 | experiment, done |
| Glyph-100M v2.4.2 | ~98M | 512 | 15k checkpoint, eval pending |
| Glyph-100M v2.5 | ~98M | 512 | dataset rebuild in progress |
