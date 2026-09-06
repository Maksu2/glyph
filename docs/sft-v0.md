# Glyph-27M SFT v0

Glyph-27M SFT v0 is a small supervised fine-tuning experiment on top of `Glyph-27M Base`.

The goal is not to add large amounts of knowledge. The goal is to teach the small base model a more useful instruction format: shorter answers, better topic adherence, honest uncertainty and less generic filler.

## Current Result

- base checkpoint: `checkpoints/final.pt`
- base pretraining step: `200000`
- SFT checkpoint: `checkpoints/sft-v0/glyph-27m-sft-v0-final.pt`
- SFT steps: `85`
- epochs: `1`
- device: ROCm / RX 5500 XT
- final SFT train loss: `2.3539`
- final SFT val loss: `2.0562`
- throughput during training: about `11.2k tok/s`

## Dataset

Raw files:

- `data/sft/raw/glyph_sft_v0_seed_1500.jsonl`
- `data/sft/raw/glyph_sft_v0_seed_1500_expanded.jsonl`

The expanded dataset was selected because it fits the model context comfortably and has no very short responses in the validation checks.

Real Glyph tokenizer stats:

| file | examples | words | template tokens | avg | p95 | max | over context 256 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `glyph_sft_v0_seed_1500.jsonl` | 1500 | 51500 | 90272 | 60.2 | 74 | 101 | 0 |
| `glyph_sft_v0_seed_1500_expanded.jsonl` | 1500 | 78085 | 130803 | 87.2 | 102 | 124 | 0 |

Category counts:

- `codzienne_decyzje`: 600
- `pisanie_i_streszczanie`: 300
- `proste_wyjasnienia`: 250
- `brak_danych`: 150
- `korekta_zalozen`: 100
- `techniczne_proste`: 100

Validation checks found:

- invalid JSON lines: 0
- missing fields: 0
- duplicate instruction+response pairs: 0
- examples over context 256: 0
- truncated examples: 0
- dropped examples: 0
- exact duplicate instructions: 782 extra copies, expected from reused prompt patterns

## Format

Each record is converted to:

```text
<|user|>
{instruction}
<|assistant|>
{response}
<|end|>
```

No system prompt is used. The model context is only 256 tokens, so the template is intentionally small.

The tokenizer recognizes the special tokens:

- `<|user|>`: id `4`
- `<|assistant|>`: id `5`
- `<|end|>`: id `6`

## Processed Artifacts

- `data/sft/processed/sft_v0_train.jsonl`
- `data/sft/processed/sft_v0_val.jsonl`
- `data/sft/processed/sft_v0_train.txt`
- `data/sft/processed/sft_v0_val.txt`
- `data/sft/processed/sft_v0_train.bin`
- `data/sft/processed/sft_v0_val.bin`
- `data/sft/reports/sft_v0_dataset_report.md`
- `data/sft/reports/sft_v0_token_stats.json`
- `data/sft/reports/sft_v0_prepare_report.json`

Split:

- train: `1350`
- val: `150`
- seed: `2026`
- stratified by category

## Hyperparameters

- epochs: `1`
- batch size: `16`
- learning rate: `2e-5`
- min LR: `2e-6`
- warmup: `10` steps
- weight decay: `0.01`
- grad clip: `1.0`
- eval interval: `25`
- checkpoint interval: `50`
- validation batches: `10`

## Commands

Validate and count tokens:

```bash
cd /home/maksu/ai-model
.venv/bin/python scripts/sft_validate.py \
  data/sft/raw/glyph_sft_v0_seed_1500.jsonl \
  data/sft/raw/glyph_sft_v0_seed_1500_expanded.jsonl
```

Prepare train/val:

```bash
cd /home/maksu/ai-model
.venv/bin/python scripts/sft_prepare.py \
  --input data/sft/raw/glyph_sft_v0_seed_1500_expanded.jsonl \
  --tokenizer data/processed/tokenizer.model \
  --context-len 256 \
  --seed 2026 \
  --val-fraction 0.10 \
  --prefix sft_v0 \
  --out-dir data/sft/processed
```

ROCm smoke test:

```bash
cd /home/maksu/ai-model
docker compose -f docker-compose.train.rocm.yml run --rm trainer-rocm \
  python finetune.py \
    --device cuda \
    --base checkpoints/final.pt \
    --train-jsonl data/sft/processed/sft_v0_train.jsonl \
    --val-jsonl data/sft/processed/sft_v0_val.jsonl \
    --output checkpoints/sft-v0-smoke \
    --epochs 1 \
    --max-steps 50 \
    --batch-size 16 \
    --learning-rate 2e-5
```

Full SFT:

```bash
cd /home/maksu/ai-model
scripts/run_sft_v0_with_fallback.sh
```

CPU fallback:

```bash
cd /home/maksu/ai-model
TRAIN_NUM_THREADS=6 .venv/bin/python finetune.py \
  --device cpu \
  --base checkpoints/final.pt \
  --train-jsonl data/sft/processed/sft_v0_train.jsonl \
  --val-jsonl data/sft/processed/sft_v0_val.jsonl \
  --output checkpoints/sft-v0-cpu-fallback \
  --epochs 1 \
  --batch-size 8 \
  --learning-rate 2e-5
```

Safe stop:

```bash
docker stop -t 300 <sft-container-name>
```

`finetune.py` handles SIGTERM and writes an emergency checkpoint before exit.

## Evaluation

Fixed comparison prompts are stored in `scripts/run_sft_comparison.py`.

Outputs:

- `eval/sft-v0/base_samples.md`
- `eval/sft-v0/sft_v0_samples.md`
- `eval/sft-v0/comparison.md`

The first comparison shows improvement over the base model in avoiding raw web fragments, but SFT v0 still drifts, repeats patterns such as "najkrótszy ruch", and is not reliable as an assistant.

## Risks

- Dataset is synthetic and small.
- 1 epoch is enough for a first SFT; additional epochs may overfit style.
- The model is only 27M parameters with a 256-token context.
- SFT improves instruction shape, not factual knowledge.
- Smoke and resume checkpoints consume disk; review retention before running many SFT variants.
