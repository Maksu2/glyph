# Gemma 4 E4B Vulkan tuning - 2026-05-22

Goal: improve Gemma 4 E4B inference throughput on RX 5500 XT without changing the model, quant, or production path.

## Baseline

- Model: `gemma-4-e4b-it-q4_k_m.gguf`
- Backend: llama.cpp Vulkan server
- Stable image kept as: `gemma-vulkan-server:baseline-9144`
- Baseline args: `-c 4096 -b 256 -ub 64 -ngl 99 -fa off --parallel 1 --threads 2 --threads-batch 2 --cache-ram 0 --no-cont-batching`
- Earlier stable average: ~43.23 tok/s

## Tested

- Flash attention on/off.
- Larger `batch` / `ubatch`.
- Polling flags.
- Q8 KV cache.
- N-gram speculative decoding.
- Newer `ghcr.io/ggml-org/llama.cpp:server-vulkan` image.

## Result

Best stable config:

```text
-c 4096 -b 256 -ub 64 -ngl 99 -fa on --parallel 1 --threads 2 --threads-batch 2 --cache-ram 0 --poll 100 --poll-batch 1 --no-cont-batching
```

Measured average in the stable sweep: ~44.06 tok/s.

That is only a small gain over the old Vulkan baseline, but it survived both short and longer prompts. The faster short-prompt configs with large batch/ubatch reached ~45.6 tok/s, but crashed or closed the connection on longer prompts, so they are not safe defaults.

## Rejected

- `-b 2048 -ub 512`: fastest on short prompts, unstable on longer prompt.
- Intermediate batch sizes above `256/64`: unstable on longer prompt.
- Q8 KV cache: slower in this setup.
- N-gram speculation: negligible gain here, not worth making the default.
- Fresh `server-vulkan` pull from 2026-05-22: container exits at startup with `libllama-common.so.0` missing. The `server-vulkan` tag was restored to the known stable image.

## Applied

`docker-compose.teacher.yml` now defaults to:

- `GEMMA4_FLASH_ATTN=on`
- `GEMMA4_POLL=100`
- `GEMMA4_POLL_BATCH=1`

These can still be overridden through environment variables.
