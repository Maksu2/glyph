# Glyph

![Glyph logo](assets/brand/glyph_logotext.png?raw=true)

Glyph is a family of small Polish decoder-only Transformers trained from scratch
on a single home GPU. No cluster, no cloud budget — one graphics card, overnight
runs, and a simple question: how good a Polish language model can you grow in a
homelab, and what does every step of that actually look like?

This repo is the full lab notebook: model code, the dataset pipeline with all
its iterations, training and evaluation scripts, per-version data audits, and
the honest results — including the failures.

## Highlights

- **Real models, real training runs** — Glyph-27M trained for 200,000 steps;
  Glyph-100M v2.4.2 reached a 15,000-step checkpoint (~246M tokens).
- **Dataset work is the main character** — the Polish mixture was rebuilt and
  audited through versions v2–v2.5, with accept/reject samples published for
  every source, so you can see exactly what the models ate.
- **Everything measured** — fixed Polish evaluation prompts, an external judge
  model kept strictly out of the training loop, and transcripts committed to
  `reports/`.
- **Consumer hardware, honest constraints** — a single RX 5500 XT (8 GB VRAM)
  dictated the batch sizes, the schedule design, and the overnight-only
  training windows.

## Why "Glyph"?

The name carries its own justification. English *glyph* arrives via French
*glyphe* from Greek *γλυφή* (*glyphē*) — "a carving, an engraved mark" — and
that from *γλύφω* (*glyphō*), "to carve, to cut, to engrave". Every layer of
that lineage maps onto what this project does:

- **Carving, not building.** Nobody assembles a model the way you assemble
  furniture. Training presses an entire written language down into millions
  of weights — the Polish language, engraved into matrices. And doing it on
  a single home GPU, against datacenter-scale labs, is hand engraving next
  to a printing press: slower, smaller, every cut visible in the open.
- **Cutting, not reading.** The tokenizer never understands a word; byte-pair
  encoding slices text into subword fragments and the model shuffles those
  fragments to imitate speech. Tokens are the machine's glyphs — cut marks
  traded for the appearance of meaning.
- **A shared word.** Polish already owns this one: *glif* is the native term
  for the visible shape of a character. No translation needed, pronounced
  identically in both languages — fitting for a Polish-first project.
- **A measure of honesty.** AI products name themselves after gods and cosmic
  forces. This is a 27-million-parameter model that repeats itself and loses
  the thread. A glyph is small and handmade — and a writing system is nothing
  but glyphs accumulated, which is the whole roadmap: 27M, then 100M, then
  whatever cleaner data allows.
- **Form before meaning.** A glyph is pure shape with no guaranteed
  understanding behind it — and whether next-token prediction amounts to
  comprehension is precisely the question the evaluations here keep probing.
  The name states the question instead of pretending to answer it. (For an
  LLM, that supposed weakness — "more sign than intelligence" — is exactly
  the point.)

The logo follows the same logic: a pen nib drawn as the letter G — the tool
that makes glyphs, signing the project with its own initial.

## Models

| Model | Parameters | Context | Status |
|---|---|---|---|
| Glyph-27M Base | 27.2M (19.0M unique) | 256 | done — 200k steps, 2026-05-22 |
| Glyph-27M SFT v0 | 27.2M | 256 | done — 1-epoch instruction experiment |
| Glyph-100M v2.4.2 | 97.7M unique / 109.9M logical | 512 | 15k checkpoint, evaluation pending |
| Glyph-100M v2.5 | ~98M | 512 | dataset rebuild in progress |

A live demo of the small model runs at
[glyph.maksu.online](https://glyph.maksu.online/).

## Architecture

Both models are decoder-only Transformers (PyTorch) with tied input/output
embeddings and a shared SentencePiece BPE tokenizer with a 16,000-token vocabulary.

**Glyph-27M**

| Field | Value |
|---|---|
| Layers | 6 |
| Attention heads | 8 |
| Hidden size | 512 |
| FFN width | 2048 |
| Context length | 256 tokens |
| Vocabulary | 16,000 |
| Dropout | 0.1 |
| Parameters | 27.21M counted, ~19.02M unique |

**Glyph-100M (v2.4.x)**

| Field | Value |
|---|---|
| Layers | 12 |
| Attention heads | 12 |
| Hidden size | 768 |
| FFN width | 3072 |
| Context length | 512 tokens |
| Vocabulary | 16,000 |
| Dropout | 0.1 |
| Parameters | 97.65M unique / 109.94M logical |

Model definitions live in `model/`; variants and hyperparameters in `config.py`.

## Tokenizer

A single SentencePiece BPE tokenizer serves the whole family: 16,000 tokens,
trained on Polish text, stored as `uint16` token streams. Keeping one tokenizer
across model sizes means datasets stay comparable between generations — when
v2.4.2 and v2.5 report different quality, the difference is the data and the
training, not a new vocabulary.

## Data

The dataset is where most of this project's effort went. The Polish pretraining
mixture went through successive rebuilds (v2 → v2.5), drawing on Polish
Wikipedia, books (Wolne Lektury), web crawls (mC4/OSCAR-style fallbacks), and
— for v2.5 — large educational PDF and web collections. Each version is
documented in `data/reports/` with statistics and per-source accept/reject
samples, so nothing about the models' diet is a mystery.

The v2.5 rebuild pipeline (`scripts/`) runs as explicit stages:

```text
download → filter → tokenize/chunk → MinHash dedup → cross-ref → build
```

with a progress monitor tracking every stage. Target: roughly 715M clean
Polish tokens. The v2.4.2 mixture it replaces carried 231.5M training tokens
plus a 1.18M-token validation holdout.

Guiding lessons, learned the hard way:

- **Volume without filtering is noise.** Early mixtures were big and bad;
  aggressive per-source filtering beat raw size every time.
- **Audit with your eyes.** Every source ships accepted *and rejected* sample
  texts — statistics alone hid entire classes of garbage (slide decks,
  truncated lines, machine-generated filler).
- **Dedup is not optional.** Near-duplicate web text measurably wastes
  training; MinHash dedup is a permanent pipeline stage now.

## Training

**Glyph-27M** trained with a classic recipe:

| Field | Value |
|---|---|
| Batch size | 32 |
| Steps | 200,000 |
| LR | 3e-4 → 3e-5, 2,000-step warmup |
| Optimizer | AdamW (0.9, 0.95), weight decay 0.1 |
| Gradient clipping | 1.0 |
| Eval / checkpoint cadence | every 500 / 1,000 steps |

**Glyph-100M** moved to a warmup–stable–decay (WSD) schedule in `train.py`,
with short cooldown branches (`scripts/run_decay_branch.sh`) spun off from
main-line checkpoints for evaluation. The 8 GB VRAM ceiling shaped the setup:
effective batch 16,384 tokens (micro-batch 4 × 512 × 8 accumulation steps) is
stable, batch 8 is tight, batch 16 OOMs — all verified by smoke test before
any long run.

Long runs train overnight, when power is cheap and the fan noise bothers no
one. The schedule, power caps and fan behavior are tuned from measured
power→noise curves, not guesses.

**Glyph-27M SFT v0** (2026-05-25) tested whether 1,500 curated synthetic
instruction examples, one epoch, 90/10 split, could teach the 27M model to at
least answer in the right shape (train loss 2.38, val 2.06). Verdict: format
improved, instruction quality stayed weak — capacity, not data, was the wall.
Base-vs-SFT comparison transcripts are in `eval/sft-v0/`.

## Evaluation

Base models are evaluated as continuation models, not chatbots: fixed Polish
prompts (`eval/`), sampled with temperature/top-k/top-p controls
(`generate.py`), graded by a separate larger model acting purely as judge —
never part of the gradient loop. Eval transcripts and judge reports are
committed under `reports/`, including the domain-loss and checkpoint-comparison
studies from the v2.3/v2.4 eras. A `tests/` suite covers generation/sampling
behavior and dataset-build invariants, so refactors can't silently change what
the model emits or what the pipeline produces.

## Repository layout

```text
├── train.py            # training loop (WSD schedule, checkpointing, resume)
├── generate.py         # sample continuations from a checkpoint
├── finetune.py         # supervised fine-tuning path
├── model/              # Transformer definition
├── config.py           # model variants + hyperparameters
├── scripts/            # dataset pipeline + eval/scheduling utilities
├── eval/               # fixed Polish prompts, base-vs-SFT comparisons
├── tests/              # generation/sampling + dataset regression tests
├── reports/            # samples, judge transcripts, data audits
├── data/reports/       # per-mixture dataset lineage (v2–v2.5)
├── docs/               # runbook, 100M plan, SFT spec, hardware notes
├── MODEL_CARD.md       # model card (27M + 100M)
└── CHANGELOG.md        # project history
```

Start with `docs/glyph-100m-plan.md` for where the project is going,
`docs/training-runbook.md` for how runs are operated, and `data/reports/` for
what the models were fed.

## Limitations

Read this before getting excited. These are small base models:

- phrase loops and repetition, topic drift after a few sentences
- confident hallucinations — useless for factual Q&A
- short context (256 / 512 tokens), weak long-range coherence
- template-ese absorbed from web data
- no safety alignment, no RLHF — not for medical, legal, financial, or
  safety-critical use, not for unsupervised public exposure

The SFT variant improves answer *shape*, not answer *quality*.

## Roadmap

1. Finish the v2.5 mixture rebuild (download → build, ~715M tokens).
2. Evaluate the frozen v2.4.2 15k checkpoint; decide continue-vs-restart.
3. Train Glyph-100M on v2.5 with the WSD schedule.
4. Revisit instruction tuning only once the base is worth tuning
   (`docs/sft-v0.1-spec.md` sketches the next attempt).

## What is not in this repo

Checkpoints, token streams and raw datasets are gigabytes-to-terabytes and
stay local — git carries the recipe and the lab notebook, not the artifacts.
Nothing here will train a model on your machine without those. The code is
published as-is: readable, hacky in places, honest about what it is.
