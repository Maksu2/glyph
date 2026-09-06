# Glyph Colab preflight: glyph100-v03-p100-fp32-smoke-001

**Status: PASS**

## Environment

- Python: `3.12.13`
- PyTorch: `2.10.0+cu126`
- CUDA available: `True`
- CUDA runtime: `12.6`
- GPU: `Tesla P100-PCIE-16GB`
- Free `/content` space: `1096062283776` bytes

## Checkpoint

- Path: `/kaggle/input/datasets/maksymilianputa/glyph100-sft-cuda-smoke-input/checkpoints/glyph-100m-base44k.pt`
- Step: `44000`
- Variant: `glyph-100m`
- Context: `512`
- Strict state load: `True`

## SFT contract

- Label audit: `PASS`
- Boundary: `i < assistant_pos`
- First assistant token and `<|end|>` must be supervised.
- Prompt and padding must be ignored (`-100`).

## Inference smoke

- Outputs: `4`
- This is a compatibility check, not a quality evaluation.

## Warnings

- None.

No training was performed by this preflight.
