# Gemma 4 E4B benchmark: Vulkan vs ROCm

Date: 2026-05-22T14:23:14.180751+00:00

## Scope

- Model: Gemma 4 E4B GGUF Q4_K_M
- GPU: AMD Radeon RX 5500 XT 8GB
- Vulkan: current production llama.cpp Vulkan image/path
- ROCm: official llama.cpp server-rocm image tested side-by-side, not made default
- Generation settings: max new tokens 128, temperature 0.7, top_p 0.9, top_k 40, ctx 4096, batch 256, ubatch 64, GPU layers 99

## Vulkan results

- Page-cache-warm load time to /health: 4467 ms
- Average generation speed: 43.23 tok/s (range 43.14-43.29)
- Average prefill speed: 142.12 tok/s (range 41.94-190.97)
- Max VRAM observed: 2.99 GiB
- Max GPU busy observed: 98%
- Max edge/junction temp observed: 50.0 C / 61.0 C
- Container CPU avg/max observed: 35.49% / 54.51%

| Prompt | Runs | Prefill tok/s avg | Generation tok/s avg | Generation range tok/s | Avg client time ms |
|---|---:|---:|---:|---:|---:|
| pl_short | 3 | 153.45 | 43.24 | 43.21-43.28 | 3105 |
| pl_tech | 3 | 190.31 | 43.20 | 43.14-43.26 | 3112 |
| pl_writing | 3 | 184.85 | 43.21 | 43.18-43.23 | 3110 |
| en_inference | 3 | 99.10 | 43.23 | 43.19-43.26 | 3120 |
| long_prefill | 3 | 82.89 | 43.27 | 43.24-43.29 | 3979 |

## ROCm result

- The official `server-rocm` image starts when `LD_LIBRARY_PATH=/app` is set and can list the RX 5500 XT as `ROCm0`.
- Gemma 4 E4B does not reach a healthy server state: it exits with code 139 during slot initialization.
- Reproduced with full GPU offload, one GPU layer, and zero GPU layers; also with Flash Attention on/off, fit on/off, and warmup disabled.
- No ROCm tokens/s result was produced because no completion request could be served.

## Recommendation

Keep Vulkan as the working Gemma inference backend. ROCm is not currently worth switching for this GGUF Gemma path on RX 5500 XT without a custom llama.cpp/HIP build or deeper debugging.
