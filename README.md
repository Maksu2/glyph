# Glyph

![Glyph logo](assets/brand/glyph_logotext.png)

Glyph is a family of small Polish decoder-only Transformers trained from scratch on a homelab.
The completed milestone is `Glyph-27M`; the next prepared variant is `Glyph-100M`.

This project was previously known internally under working names such as `miniGPT`, `miniGPT-PL`, `ai-model`, and `Polish GPT`. The on-disk path stays `/home/maksu/ai-model` for operational safety, but the model/project name is now:

- project name: `Glyph`
- base model: `Glyph-27M Base`
- current instruction-tuned experiment: `Glyph-27M SFT v0`
- next base experiment: `Glyph-100M`
- future cleaned-up instruction variant: `Glyph-100M Instruct`

## Status

Glyph-27M Base completed its 200,000-step pretraining run on 2026-05-22. The final base checkpoint is `checkpoints/final.pt`.

Glyph-27M SFT v0 was then trained as a small supervised fine-tuning experiment on 2026-05-25. It used 1,500 synthetic curated instruction examples, a 90/10 stratified split, and one epoch on ROCm/RX 5500 XT. SFT v0 improves response format and instruction-following behavior, but it does not make the 27M model a production assistant.

Glyph-100M is in preparation. The goal is to keep the proven pipeline from Glyph-27M, increase model capacity, extend context to 512 tokens, and use a cleaner filtered Polish corpus before any long run. Do not start full Glyph-100M training without an explicit approval step.

## Architecture

### Glyph-27M

| Field | Value |
|---|---:|
| Type | decoder-only Transformer |
| Framework | PyTorch |
| Layers | 6 |
| Attention heads | 8 |
| Hidden size | 512 |
| FFN width | 2048 |
| Context length | 256 tokens |
| Vocabulary | 16,000 tokens |
| Dropout | 0.1 |
| Parameters | 27.21M counted parameters |
| Weight tying | enabled; about 19.02M unique parameters |

The model definition is in `model/transformer.py`; hyperparameters live in `config.py`.

### Glyph-100M Prepared Variant

| Field | Value |
|---|---:|
| Type | decoder-only Transformer |
| Framework | PyTorch |
| Layers | 12 |
| Attention heads | 12 |
| Hidden size | 768 |
| FFN width | 3072 |
| Context length | 512 tokens |
| Vocabulary | 16,000 tokens |
| Dropout | 0.1 |
| Parameters | 97.65M unique/trainable, 109.94M logical with tied LM head counted separately |
| Weight tying | enabled |

Variant configs are exposed through `MODEL_VARIANTS` in `config.py`. The default remains `glyph-27m` for backward compatibility.

## Tokenizer

Glyph-27M uses a SentencePiece BPE tokenizer:

- model: `data/processed/tokenizer.model`
- vocab: `data/processed/tokenizer.vocab`
- vocab size: 16,000
- token IDs are stored as `uint16` in `data/processed/tokens.bin`

## Data

The training corpus is Polish text assembled for local pretraining. The intended/source mix is:

- Polish Wikipedia
- mC4/OSCAR Polish fallback data
- Wolne Lektury

Current processed artifacts:

- `data/processed/corpus_clean.txt`: cleaned text corpus
- `data/processed/tokens.bin`: training token stream
- `data/processed/val_tokens.bin`: validation holdout
- `data/processed/val_tokens.meta.json`: validation split metadata

Do not regenerate preprocessing during an active training run unless you intentionally plan a new training stream.

Glyph-100M uses separate dataset outputs:

- `data/processed/glyph100_train.bin`
- `data/processed/glyph100_val.bin`
- `data/processed/glyph100_metadata.json`
- `data/reports/glyph_100m_dataset_report.md`
- `data/reports/glyph_100m_dataset_stats.json`

The legacy `data/processed/tokens.bin` remains the Glyph-27M token stream and should not be overwritten.

## Training

Main script:

```bash
python train.py --resume checkpoints/latest.pt
```

Training configuration:

| Field | Value |
|---|---:|
| Batch size | 32 |
| Max steps | 200,000 |
| Max LR | 3e-4 |
| Min LR | 3e-5 |
| Warmup | 2,000 steps |
| Optimizer | AdamW |
| Betas | 0.9, 0.95 |
| Weight decay | 0.1 |
| Grad clip | 1.0 |
| Eval interval | 500 steps |
| Checkpoint interval | 1,000 steps |

Logs:

- `logs/train.log`
- `logs/train.stdout.log`

Checkpoints:

- `checkpoints/latest.pt`
- `checkpoints/step_XXXXXXX.pt`
- `checkpoints/emergency.pt`

## Docker Training

The training setup is CPU-only and designed to coexist with other homelab services. The path remains `/home/maksu/ai-model`.

Build:

```bash
cd /home/maksu/ai-model
docker compose -f docker-compose.train.yml build trainer
```

Smoke test:

```bash
cd /home/maksu/ai-model
scripts/smoke_test_container.sh
```

Short resume test:

```bash
cd /home/maksu/ai-model
docker compose -f docker-compose.train.yml run --rm trainer \
  python train.py --resume checkpoints/latest.pt --max-steps 10
```

Long resume:

```bash
cd /home/maksu/ai-model
docker compose -f docker-compose.train.yml run --rm trainer \
  python train.py --resume checkpoints/latest.pt
```

Do not start long training while another training process is already running.

## SFT v0

SFT v0 is documented in `docs/sft-v0.md`.

Key artifacts:

- raw data: `data/sft/raw/glyph_sft_v0_seed_1500_expanded.jsonl`
- processed split: `data/sft/processed/sft_v0_train.jsonl`, `data/sft/processed/sft_v0_val.jsonl`
- token stats and validation report: `data/sft/reports/`
- final checkpoint: `checkpoints/sft-v0/glyph-27m-sft-v0-final.pt`
- comparison samples: `eval/sft-v0/comparison.md`

Safe ROCm command:

```bash
cd /home/maksu/ai-model
docker compose -f docker-compose.train.rocm.yml run --rm trainer-rocm \
  python finetune.py \
    --device cuda \
    --base checkpoints/final.pt \
    --train-jsonl data/sft/processed/sft_v0_train.jsonl \
    --val-jsonl data/sft/processed/sft_v0_val.jsonl \
    --output checkpoints/sft-v0 \
    --epochs 1 \
    --batch-size 16 \
    --learning-rate 2e-5
```

## Inference

Basic continuation:

```bash
cd /home/maksu/ai-model
python generate.py "Paryż, stolica Francji, jest" \
  --checkpoint checkpoints/latest.pt \
  --max-tokens 50 \
  --temperature 0.75 \
  --top-k 50 \
  --top-p 0.92 \
  --repetition-penalty 1.10 \
  --no-repeat-ngram-size 4
```

The private training dashboard does not expose inference. Public testing lives in the separate locked-down demo service for `glyph.maksu.online`.

## Evaluation

Glyph-27M is evaluated with fixed Polish continuation prompts plus Gemma 4 as a separate judge. Gemma is not part of the gradient training loop.

Key outputs:

- `reports/samples/latest.jsonl`
- `reports/gemma4_eval/latest.jsonl`
- `reports/gemma4_eval/latest_summary.json`
- `reports/gemma4_eval/status.json`

The scheduled Gemma evaluation runs only at night. Manual runs from the private dashboard require a configured owner code, same-origin fetch, rate limits and the configured night window.

Glyph-100M base evaluation prompts are prepared in `eval/glyph-100m/base_continuation_prompts.jsonl`. These prompts treat the base model as a continuation model, not as an instruction-following assistant.

## Dashboard

The local dashboard runs on:

```text
http://127.0.0.1:8181
```

Public/tunnel usage has been documented in `DASHBOARD_USAGE.md`. The dashboard title is `Glyph-27M Training` and reports metadata fields:

```json
{
  "project_name": "Glyph",
  "model_name": "Glyph-27M",
  "variant": "Base"
}
```

## Limitations

Glyph-27M Base is a small base language model. Glyph-27M SFT v0 is an instruction-tuning experiment, not a production chatbot.

Known limitations:

- repetition and phrase loops
- topic drift after a few sentences
- short 256-token context
- factual unreliability
- noisy/statistical templates from source data
- weak long-range coherence
- no safety alignment or RLHF

Not intended for:

- production assistant use
- factual Q&A
- medical, legal, financial, or safety-critical decisions
- unsupervised public API usage

## Directory Overview

```text
/home/maksu/ai-model/
├── config.py
├── train.py
├── generate.py
├── finetune.py
├── model/
├── data/
├── checkpoints/
├── logs/
├── reports/
├── web/
├── scripts/
├── Dockerfile.train
├── docker-compose.train.yml
├── docker-compose.teacher.yml
├── DASHBOARD_USAGE.md
├── TRAINING_CONTAINER.md
└── MODEL_CARD.md
```

## Rebranding Note

Only display names, documentation, metadata, and non-behavioral labels were changed during the Glyph-27M rebrand. Checkpoints, tokenizer files, datasets, container-safe paths, and the `/home/maksu/ai-model` directory name were intentionally left unchanged.
