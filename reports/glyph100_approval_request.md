# Glyph-100M Approval Request

Status: readiness complete, waiting for explicit approval.

No Glyph-100M training has been started.

## Question

Do you approve starting Glyph-100M stage 1 training for 1,000 optimizer steps?

Accepted replies:

- `APPROVE_STAGE1`: Codex may start only stage 1 / 1k steps.
- `STOP`: Codex must not train.
- `CHANGES`: Codex should wait for further instructions.

## Readiness Summary

- Glyph-27M Base is frozen at `checkpoints/final.pt`.
- Glyph-27M SFT v0 is frozen at `checkpoints/sft-v0/glyph-27m-sft-v0-final.pt`.
- Glyph-100M config has been added as a separate variant.
- Glyph-100M parameters: 97,654,272 unique/trainable; 109,942,272 logical with tied LM head counted separately.
- ROCm smoke test passed for microbatch 4 and 8 at context 512.
- ROCm smoke test failed with OOM at microbatch 16.
- Recommended stage-1 shape: microbatch 4, gradient accumulation 8, effective tokens/step 16,384.
- Dataset candidate `glyph100_stage1_candidate` exists:
  - train: `data/processed/glyph100_train.bin`
  - val: `data/processed/glyph100_val.bin`
  - train tokens: 117,870,679
  - val tokens: 1,239,948
- Dataset report: `data/reports/glyph_100m_dataset_report.md`.
- Training plan: `docs/glyph-100m-plan.md`.

## Command Not Executed

```bash
cd /home/maksu/ai-model
RENDER_GID=$(getent group render | cut -d: -f3) \
VIDEO_GID=$(getent group video | cut -d: -f3) \
GLYPH_MODEL_VARIANT=glyph-100m \
docker compose -f docker-compose.train.rocm.yml run --rm --no-deps trainer-rocm \
  python train.py \
    --variant glyph-100m \
    --device cuda \
    --max-steps 1000 \
    --batch-size 4 \
    --gradient-accumulation-steps 8 \
    --learning-rate 2e-4 \
    --min-lr 2e-5 \
    --checkpoint-dir checkpoints/glyph-100m \
    --log-dir logs/glyph-100m \
    --dataset-name glyph100_stage1_candidate \
    --dataset-metadata-path data/processed/glyph100_metadata.json \
    --eval-interval 250 \
    --checkpoint-interval 500 \
    --log-interval 10
```

## Recommendation

Start stage 1 / 1k steps only after explicit approval. This is a sanity run, not a full training run. The safer batch 4 / accumulation 8 shape keeps the same effective tokens per optimizer step as batch 8 / accumulation 4, but leaves more VRAM headroom on RX 5500 XT.

Before longer stages, process the full corpus with source-preserving metadata and inspect samples.
