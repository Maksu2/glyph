# Glyph Colab preflight: glyph100-v03-p100-fp32-smoke-001

**Status: FAIL**

## Environment

- Python: `3.12.13`
- PyTorch: `2.10.0+cu128`
- CUDA available: `True`
- CUDA runtime: `12.8`
- GPU: `Tesla P100-PCIE-16GB`
- Free `/content` space: `1102540840960` bytes

## Checkpoint

- Path: `not validated`
- Step: `None`
- Variant: `None`
- Context: `None`
- Strict state load: `None`

## SFT contract

- Label audit: `skipped`
- Boundary: `i < assistant_pos`
- First assistant token and `<|end|>` must be supervised.
- Prompt and padding must be ignored (`-100`).

## Inference smoke

- Outputs: `0`
- This is a compatibility check, not a quality evaluation.

## Warnings

- AcceleratorError: CUDA error: no kernel image is available for execution on the device
Search for `cudaErrorNoKernelImageForDevice' in https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__TYPES.html for more information.
CUDA kernel errors might be asynchronously reported at some other API call, so the stacktrace below might be incorrect.
For debugging consider passing CUDA_LAUNCH_BLOCKING=1
Compile with `TORCH_USE_CUDA_DSA` to enable device-side assertions.


No training was performed by this preflight.
