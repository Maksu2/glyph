# Glyph-100M Kaggle P100 smoke attempt

## Decision

**Status: BLOCKED BEFORE TRAINING**

The planned full 400-step SFT v0.3 rerun was intentionally not started. The
same v0.3 experiment already completed locally for 586 steps and its broad eval
was worse than v0.2, so repeating it would spend free GPU quota without adding
useful quality evidence.

A short 25-step FP32 CUDA compatibility benchmark was worth attempting. It was
designed to validate the approved 44k base, fixed label mask, checkpoint
round-trip, Kaggle output retrieval, and P100 throughput.

## Inputs

- Kaggle account: `maksymilianputa`
- Private dataset: `maksymilianputa/glyph100-sft-cuda-smoke-input`
- Private kernel: `maksymilianputa/glyph-100m-v0-3-p100-cuda-smoke`
- Requested accelerator: `NvidiaTeslaP100`
- Base: optimizer-free bundle of approved `step_0044000.pt`
- Dataset: `glyph100_sft_smoke_v0_3`, train/val splits
- Tokenizer SHA256: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`
- Transport archive: 347 MB, locally SHA256-verified
- Critical payload files checked against bundle manifest: 12

The private Kaggle dataset is ready and contains no 50k checkpoint, secrets, or
historical checkpoint collection.

## Attempts

1. Version 1 stopped after about 0.96 s because the diagnostic command
   `nvidia-smi` was not present in the Kaggle image. Model loading and training
   did not start.
2. Version 2 stopped after about 1.08 s because Kaggle had already unpacked the
   uploaded `tar.gz`, while the runner expected the archive itself. Model
   loading and training did not start.
3. Version 3 accepted the directly mounted payload and verified its hashes, but
   stopped after about 8.65 s because `torch.cuda.is_available()` returned
   `False`.

The pulled kernel metadata still says `enable_gpu=true` and
`machine_shape=Gpu`, but the runtime did not receive CUDA. This strongly points
to account accelerator eligibility, most commonly incomplete phone/account
verification, rather than a Glyph, PyTorch, checkpoint, or dataset failure.

## Safety result

- Optimizer steps executed: `0`
- Model checkpoints written: `0`
- Existing local checkpoints changed: `0`
- Meaningful GPU quota consumed: effectively none; all attempts stopped within
  seconds before CUDA/model initialization
- Public resources created: `0`
- Private Kaggle input dataset: ready
- Private Kaggle kernel: retained for a single retry after GPU access is fixed

## Recommendation

Do not retry automatically. Open Kaggle account settings on the phone and
complete phone/account verification, then confirm that a GPU accelerator is
available. After that, rerun only the existing 25-step compatibility benchmark.
Do not repeat the full 400-step v0.3 quality run.

Kaggle settings: <https://www.kaggle.com/settings>

