# Glyph-100M v2.4.1 GPU pipeline smoke

Generated: 2026-07-16T07:20:40+00:00

## Verdict

**PASS.** One real optimizer step completed on the RX 5500 XT through the ROCm/HIP container using the final v2.4.1 train and validation binaries. No training checkpoint was written and no long run was started.

## Configuration

- model variant: `glyph-100m`
- parameters: 97,654,272 unique/trainable; 109,942,272 logical with tied output weights counted separately
- context length: 512
- train tokens: 278,089,665
- validation tokens: 1,406,736
- microbatch: 4
- gradient accumulation: 8
- effective tokens per optimizer step: 16,384
- sampler: shuffled non-overlapping blocks, seed 2026
- device: AMD Radeon RX 5500 XT through PyTorch HIP 7.13.0
- optimizer: AdamW, foreach enabled

## Result

- completed optimizer steps: 1/1
- loss: 9.8369
- observed throughput: 2,864 tokens/s
- NaN/Inf: none
- OOM/crash/hang: none
- parameter finite check: passed
- checkpoint written: no, by design
- GPU edge/junction before: 28 C / 28 C
- GPU edge/junction immediately after: 30 C / 30 C

The first-step learning rate was `1.00e-07` because the production schedule begins with a 2,000-step warmup. This smoke therefore validates execution and numerical stability, not convergence.

## Limitations

- A single step does not establish long-run ROCm stability or final throughput.
- Peak VRAM was not sampled independently in this run.
- Quality was not evaluated because the model was freshly initialized and the run intentionally stopped after one optimizer step.

## Next gate

The next meaningful action is a separately approved 1,000-step from-scratch proxy, followed by a 5,000-step quality comparison only if the 1k run is technically healthy.
