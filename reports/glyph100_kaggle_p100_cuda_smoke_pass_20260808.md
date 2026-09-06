# Glyph-100M Kaggle P100 CUDA smoke

## Verdict

**PASS. Kaggle can run Glyph-100M on a Tesla P100.**

The account verification change unlocked the accelerator. Kaggle assigned a
`Tesla P100-PCIE-16GB`, and the controlled 25-step FP32 SFT compatibility run
completed without NaN, Inf, OOM, crash, or checkpoint corruption.

This was a diagnostic smoke, not a quality-training run and not a replacement
for the already completed local SFT v0.3 experiment.

## Compatibility fix

Kaggle initially supplied PyTorch `2.10.0+cu128`. That binary supports
`sm_70` and newer, while P100 is Pascal `sm_60`, so CUDA reported
`no kernel image is available for execution on the device`.

The ephemeral Kaggle environment was switched to official PyTorch
`2.10.0+cu126`. CUDA 12.6 builds retain Pascal support. No package was changed
on the homelab.

- PyTorch versions: <https://pytorch.org/get-started/previous-versions/>
- PyTorch CUDA architecture notes: <https://github.com/pytorch/pytorch/releases>

## Preflight

- GPU: `Tesla P100-PCIE-16GB`
- VRAM: `16 GB`
- Initial GPU temperature: `34 C`
- Compute capability: `6.0`
- PyTorch / CUDA: `2.10.0+cu126` / `12.6`
- Base checkpoint: approved Glyph-100M step `44000`
- Variant: `glyph-100m`
- Dataset metadata: `glyph100_v2_3_1`
- Context: `512`
- Unique/trainable parameters: `97,654,272`
- Tokenizer SHA256: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`
- Strict model state load: pass
- Fixed label mask audit: pass
- First assistant token supervised: yes
- `<|end|>` supervised: yes
- Prompt masked: yes
- Padding label: `-100`

## Training smoke

- Steps: `0 -> 25`
- Precision: FP32, no autocast, no GradScaler
- Batch / accumulation: `1 / 4`
- Effective examples per step: `4`
- Learning rate: up to `1e-5`
- Training duration including eval/checkpoint: `15.97 s`
- Steady optimizer rate at step 25: `8.57 step/s`
- Train loss: `4.3118 -> 3.8582`
- Validation loss at step 25: `3.7436`
- NaN / Inf / OOM / crash: `0 / 0 / 0 / 0`
- Peak CUDA allocated: `1.12 GiB`
- Peak CUDA reserved: `1.80 GiB`

The deterministic 25-step sample contained 3,794 input tokens and 1,980
supervised answer tokens. Training-only throughput was approximately:

- Input tokens: `1,301 tok/s`
- Supervised answer tokens: `679 tok/s`

The local RX 5500 XT logged about `540 input tok/s` at the comparable early
step 25, so P100 was approximately **2.41x as fast (+141%)**. Compared with the
local full-run average of `416.7 tok/s`, it was `3.12x`, but that second number
includes more eval/checkpoint overhead and is less directly comparable.

## Checkpoint validation

Kaggle wrote a complete optimizer checkpoint (`1,175,134,979` bytes), loaded it
back successfully, verified optimizer and scheduler state, then intentionally
removed that large temporary file from persisted output.

Persisted model-only diagnostic checkpoint:

- Local path: `kaggle/glyph100-cuda-smoke/downloads/version-9/glyph100-v03-p100-fp32-smoke-001/glyph100-v03-p100-smoke-model-only.pt`
- Size: `393,809,523` bytes
- SHA256: `ce65c410535c02d7d36ae71f497bbcd3f42be88e18568cb1a1baa8b61f7c4a23`
- Step: `25`
- Local strict load: pass
- Model parameters finite: yes

This checkpoint is diagnostic only and does not replace the selected best
pretraining checkpoint 44k or any SFT quality checkpoint.

## Quota and next decision

- Kaggle GPU quota before: `30.00 h`
- Kaggle GPU quota after: `29.93 h`
- Account-level cost: free quota only

The P100 route is technically viable and materially faster than RX 5500 XT for
this FP32 SFT path. Repeating the same full SFT v0.3 is still not useful because
that experiment already completed locally and did not beat v0.2. The next
Kaggle run should be a new, decision-relevant experiment rather than a duplicate.

