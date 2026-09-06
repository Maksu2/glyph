# Glyph-100M Kaggle GPU launch

## Verdict

**BLOCKED BEFORE TRAINING: Kaggle did not attach a CUDA device.**

The private kernel and input dataset are valid, but every fresh Kaggle runtime
received CPU only. The guard in the runner stopped immediately, before model
loading, optimizer creation, or training.

## What was attempted

- Kernel: `maksymilianputa/glyph-100m-v0-3-p100-cuda-smoke`
- Private input: `maksymilianputa/glyph100-sft-cuda-smoke-input`
- Planned run: 25 optimizer-step CUDA compatibility and throughput smoke
- Base checkpoint: approved Glyph-100M 44k, optimizer-free transport copy
- Dataset: `glyph100_sft_smoke_v0_3`
- Precision: FP32
- Batch / accumulation: 1 / 4
- Learning rate: `1e-5`

Attempts made for this work batch:

| Version | Accelerator request | Internet | Result |
|---:|---|---:|---|
| 4 | metadata `enable_gpu=true` | on | CPU runtime; CUDA unavailable |
| 5 | metadata `enable_gpu=true` | off | CPU runtime; CUDA unavailable |
| 6 | explicit `--accelerator NvidiaTeslaP100` | off | CPU runtime; CUDA unavailable |
| 7 | explicit `--accelerator NvidiaTeslaT4` | off | CPU runtime; CUDA unavailable |

The pulled server metadata confirms `enable_gpu=true` and
`machine_shape=Gpu`. The account quota command reports `30.00h` GPU total,
`30.00h` remaining, and `0.00h` used. Nevertheless, both `nvidia-smi` and
PyTorch CUDA were unavailable inside the runtime.

## Safety

- Training started: **no**
- Optimizer steps: **0**
- Checkpoints written: **0**
- Existing checkpoints modified: **no**
- GPU quota consumed: **0.00 h**
- Local training processes: **none**
- Active training containers: **none**

The runner behaved correctly by refusing to fall back silently to CPU.

## Diagnosis

This is not a Glyph checkpoint, dataset, PyTorch-code, or quota-exhaustion
failure. The Kaggle scheduler/API accepted GPU settings but mounted no CUDA
device. The remaining likely causes are account accelerator eligibility or a
Kaggle backend/UI allocation issue.

## Required next action

Open <https://www.kaggle.com/settings> and make sure phone/account verification
is complete. Then open the private kernel in Kaggle, select a GPU accelerator in
the notebook settings, and save/commit one version from the web UI. Once that
setting is demonstrably active, rerun the existing 25-step smoke through CLI.

Do not start the redundant full v0.3 rerun before the smoke provides a real GPU
name, throughput, and a reloadable checkpoint.

