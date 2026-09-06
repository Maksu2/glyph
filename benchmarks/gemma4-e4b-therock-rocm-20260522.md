# Gemma 4 E4B benchmark: TheRock ROCm / gfx1012

Date: 2026-05-22

## Scope

- Model: Gemma 4 E4B GGUF Q4_K_M
- Model path: `/home/maksu/ai-model/models/gemma4/gemma-4-e4b-it-q4_k_m.gguf`
- GPU: AMD Radeon RX 5500 XT 8GB, `gfx1012`
- Existing baseline: Vulkan llama.cpp path from `gemma4-e4b-vulkan-vs-rocm-20260522.md`
- Goal: test whether a custom TheRock ROCm/HIP llama.cpp build can run Gemma and beat Vulkan.

## Build

Source:

- llama.cpp commit: `4f0e43d`
- source path: `/home/maksu/ai-model/.cache/llama-rocm-gfx1012/llama.cpp`

TheRock SDK:

- base image: `ai-model-trainer:rocm-gfx1012`
- ROCm Python packages: `7.14.0a20260521`
- devel package installed inside temporary builder container from `https://rocm.nightlies.amd.com/whl-multi-arch/`
- `rocm_sdk init` expanded devel contents to `_rocm_sdk_devel`

Build flags, main variant:

```text
GGML_HIP=ON
AMDGPU_TARGETS=gfx1012
CMAKE_HIP_ARCHITECTURES=gfx1012
GGML_HIP_MMQ_MFMA=OFF
GGML_HIP_ROCWMMA_FATTN=OFF
GGML_HIP_GRAPHS=OFF
```

Build path:

```text
/home/maksu/ai-model/.cache/llama-rocm-gfx1012/llama.cpp/build-therock-gfx1012
```

MFMA test variant:

```text
GGML_HIP_MMQ_MFMA=ON
```

Build path:

```text
/home/maksu/ai-model/.cache/llama-rocm-gfx1012/llama.cpp/build-therock-gfx1012-mfma
```

## Runtime command shape

The runtime container used:

```text
--device=/dev/kfd
--device=/dev/dri
--group-add render
--group-add video
LD_LIBRARY_PATH=<llama-build-bin>:_rocm_sdk_libraries/lib:_rocm_sdk_core/lib
```

No production Gemma/Vulkan configuration was changed.

## Results

### Sanity generation

`llama-completion`, `-ngl 1`, `ctx=1024`, `fa=off`, `n=64`:

```text
prompt eval: 8.55 tok/s
generation: 11.58 tok/s
```

`llama-completion`, `-ngl 99`, `ctx=4096`, `fa=off`, `n=128`:

```text
prompt eval: 88.65 tok/s
generation: 28.36 tok/s
```

### llama-bench, full offload

Settings:

```text
p=128
n=128
repetitions=3
ngl=99
```

| Variant | Batch | UBatch | FA | Poll | Prompt tok/s | Gen tok/s |
|---|---:|---:|---:|---:|---:|---:|
| TheRock ROCm | 256 | 64 | off | 50 | 219.74 +/- 14.20 | 28.55 +/- 0.10 |
| TheRock ROCm | 256 | 64 | on | 50 | 199.19 +/- 1.73 | 29.25 +/- 0.01 |
| TheRock ROCm | 512 | 128 | on | 100 | 212.99 +/- 13.41 | 29.23 +/- 0.10 |
| TheRock ROCm | 512 | 512 | on | 100 | 220.66 +/- 0.17 | 29.30 +/- 0.00 |
| TheRock ROCm | 2048 | 128 | on | 100 | 220.96 +/- 0.24 | 29.34 +/- 0.00 |
| TheRock ROCm | 2048 | 512 | on | 100 | 220.91 +/- 0.18 | 29.35 +/- 0.00 |
| TheRock ROCm, MFMA on | 2048 | 512 | on | 100 | 212.59 +/- 13.44 | 29.19 +/- 0.11 |

## Comparison to Vulkan baseline

Previous Vulkan benchmark:

```text
generation: 43.23 tok/s average
prefill:    142.12 tok/s average
```

Best TheRock ROCm result:

```text
generation: 29.35 tok/s
prefill:    220.91 tok/s
```

Interpretation:

- ROCm/TheRock fixed the official ROCm image crash for this model.
- ROCm prompt processing can be faster than the earlier Vulkan baseline in the synthetic `pp128` benchmark.
- ROCm generation is still slower: Vulkan is about 1.47x faster for token generation.
- MFMA did not help on RX 5500 XT / `gfx1012`.

## Recommendation

Do not switch Gemma 4 E4B inference from Vulkan to ROCm right now.

Keep:

- Vulkan for Gemma inference.
- TheRock ROCm for PyTorch/Glyph training experiments and as a working experimental llama.cpp build.

ROCm is now useful as a fallback/test path, but not as the default Gemma backend.

