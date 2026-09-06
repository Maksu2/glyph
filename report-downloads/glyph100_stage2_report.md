# Glyph-100M stage 2 report

Generated: 2026-05-31T20:05:55.013081+00:00

## Verdict

Stage 2 completed technically: checkpoint step 10,000 exists, loss continued downward, no active training container remains, and the public snapshot reports `stage 2 complete`.

Quality is not ready for stage 3 on the same dataset. The quick completion eval shows Polish-looking text and less classic SEO/store garbage than Glyph-27M, but it still has many loops, fabricated encyclopedia fragments, `Przypisy` / `Linki zewnętrzne` style bleed, random entities and truncated continuations.

Recommendation: **B: do a source-aware dataset rebuild before stage 3 / 50k**.

## Run Summary

- Start step: 1,000
- End step: 10,000
- Duration: 12h 27m 32s
- Effective tokens/step: 16,384
- Tokens at 10k: 163,840,000
- Additional stage 2 tokens: 147,456,000
- Avg tok/s near end: 3,293.5
- Train loss: 6.3248 at step 1,000 -> 3.6795 at step 10,000
- Final val loss: 3.3527
- LR at 10k: 1.99e-04

## Stability

- NaN/Inf after recovery: none observed
- OOM: none observed
- ROCm crash/hang: none observed after recovery
- Checkpoint save failure: none observed
- Initial failed resume: non-finite loss at step 1002 before recovery
- Recovery path: AdamW `foreach=false`, SDPA `math`, finite parameter checks

Observed during recovered run around step 1040:

- GPU edge: ~59 C
- GPU junction/hotspot: ~79 C
- VRAM: ~61%
- GPU use: ~99%

Final thermals were not sampled because the training container exited cleanly before this report.

## Validation Losses

| Step | Time UTC | Val loss |
| ---: | --- | ---: |
| 1000 | 2026-05-26 18:13:35 | 6.2177 |
| 1500 | 2026-05-27 06:02:33 | 5.4110 |
| 2000 | 2026-05-27 06:44:08 | 5.3611 |
| 2500 | 2026-05-27 07:25:37 | 5.0758 |
| 3000 | 2026-05-27 08:07:11 | 4.8474 |
| 3500 | 2026-05-27 08:48:41 | 4.2752 |
| 4000 | 2026-05-27 09:30:16 | 4.2509 |
| 4500 | 2026-05-27 10:11:45 | 4.1242 |
| 5000 | 2026-05-27 10:53:19 | 3.6223 |
| 5500 | 2026-05-27 11:34:48 | 3.9339 |
| 6000 | 2026-05-27 12:16:22 | 3.8670 |
| 6500 | 2026-05-27 12:57:51 | 3.6860 |
| 7000 | 2026-05-27 13:39:24 | 3.9593 |
| 7500 | 2026-05-27 14:20:53 | 3.5324 |
| 8000 | 2026-05-27 15:02:27 | 3.9130 |
| 8500 | 2026-05-27 15:43:56 | 3.7152 |
| 9000 | 2026-05-27 16:25:29 | 3.8426 |
| 9500 | 2026-05-27 17:06:58 | 3.5437 |
| 10000 | 2026-05-27 17:48:31 | 3.3527 |

The validation loss is noisy because each eval uses only a few random batches, but the final value is the best late-stage value. There is no obvious overfit signal by 10k. The dataset size is the bigger issue for 50k+.

## Checkpoints

Checkpoint directory size: ~14G.

| Checkpoint | Time UTC | Saved loss |
| --- | --- | ---: |
| `checkpoints/glyph-100m/step_0000500.pt` | 2026-05-26 17:32:02 | 7.3908 |
| `checkpoints/glyph-100m/step_0001000.pt` | 2026-05-26 18:13:33 | 6.2372 |
| `checkpoints/glyph-100m/step_0002000.pt` | 2026-05-27 06:44:07 | 5.0632 |
| `checkpoints/glyph-100m/step_0003000.pt` | 2026-05-27 08:07:10 | 4.6626 |
| `checkpoints/glyph-100m/step_0004000.pt` | 2026-05-27 09:30:15 | 4.2677 |
| `checkpoints/glyph-100m/step_0005000.pt` | 2026-05-27 10:53:17 | 4.0864 |
| `checkpoints/glyph-100m/step_0006000.pt` | 2026-05-27 12:16:21 | 3.9540 |
| `checkpoints/glyph-100m/step_0007000.pt` | 2026-05-27 13:39:23 | 3.9266 |
| `checkpoints/glyph-100m/step_0008000.pt` | 2026-05-27 15:02:26 | 3.7973 |
| `checkpoints/glyph-100m/step_0009000.pt` | 2026-05-27 16:25:28 | 3.3270 |
| `checkpoints/glyph-100m/step_0010000.pt` | 2026-05-27 17:48:30 | 3.8270 |

`checkpoints/glyph-100m/latest.pt` metadata was verified as `variant=glyph-100m`, `step=10000`, dataset `glyph100_stage1_candidate`.

## Quick Completion Eval

Files:

- `eval/glyph-100m/stage2_completion_prompts.jsonl`
- `eval/glyph-100m/stage2_samples.md`
- `eval/glyph-100m/stage2_samples.json`
- `eval/glyph-100m/stage2_vs_27m.md`

Preset summary:

| Preset | Samples | Avg tok/s | Web garbage | Repetition samples | Natural endings |
| --- | ---: | ---: | ---: | ---: | ---: |
| conservative | 12 | 64.28 | 0 | 10 | 0 |
| normal | 12 | 66.38 | 0 | 6 | 1 |
| creative | 12 | 66.41 | 0 | 4 | 0 |

Manual read:

- Polish surface form is often recognizable.
- Syntax is sometimes locally plausible, but global coherence is weak.
- Repetition remains a major issue, especially conservative decoding.
- The model often falls into fake Wikipedia-like entries: villages, NGC objects, `Przypisy`, `Linki zewnętrzne`.
- It fabricates facts heavily; this is expected for a 10k base LM but still important.
- No obvious URL/HTML spam appeared in this small sample set.
- Most samples are cut off at max tokens and do not end naturally.
- Compared with Glyph-27M, 100M has less store/SEO tone, but it is not clearly better in factual or educational prompts yet.

## Dataset Decision

Current train tokens: 117,870,679.

Token-equivalent epochs:

| Target | Tokens | Epochs vs current train split |
| ---: | ---: | ---: |
| 10k | 163,840,000 | 1.39 |
| 50k | 819,200,000 | 6.95 |
| 100k | 1,638,400,000 | 13.90 |
| 200k | 3,276,800,000 | 27.80 |

The current candidate is enough for sanity and early training, but not a good foundation for 50k+. A 50k run would be almost 7 token-equivalent epochs over a corpus that still leaks Wikipedia/list structure and noisy web patterns. A larger source-aware rebuild should happen before stage 3.

## Cleanup Proposal

Do not run these commands without approval.

Keep:

- `checkpoints/glyph-100m/latest.pt`
- `checkpoints/glyph-100m/step_0010000.pt`
- `checkpoints/glyph-100m/step_0005000.pt` as one middle safety checkpoint

Candidates to remove:

| File | Size |
| --- | ---: |
| `checkpoints/glyph-100m/step_0000500.pt` | 1.09 GiB |
| `checkpoints/glyph-100m/step_0001000.pt` | 1.09 GiB |
| `checkpoints/glyph-100m/step_0002000.pt` | 1.09 GiB |
| `checkpoints/glyph-100m/step_0003000.pt` | 1.09 GiB |
| `checkpoints/glyph-100m/step_0004000.pt` | 1.09 GiB |
| `checkpoints/glyph-100m/step_0006000.pt` | 1.09 GiB |
| `checkpoints/glyph-100m/step_0007000.pt` | 1.09 GiB |
| `checkpoints/glyph-100m/step_0008000.pt` | 1.09 GiB |
| `checkpoints/glyph-100m/step_0009000.pt` | 1.09 GiB |

Estimated reclaim: ~9.85 GiB.

Suggested command, not executed:

```bash
rm checkpoints/glyph-100m/step_0000500.pt    checkpoints/glyph-100m/step_0001000.pt    checkpoints/glyph-100m/step_0002000.pt    checkpoints/glyph-100m/step_0003000.pt    checkpoints/glyph-100m/step_0004000.pt    checkpoints/glyph-100m/step_0006000.pt    checkpoints/glyph-100m/step_0007000.pt    checkpoints/glyph-100m/step_0008000.pt    checkpoints/glyph-100m/step_0009000.pt
```

## Recommendation

**B: first source-aware dataset rebuild.**

Do not start stage 3 / 50k on `glyph100_stage1_candidate` unless the goal is explicitly to study overfitting/noise. For model quality, the next best move is a cleaner, source-aware dataset with document IDs, source IDs, deduplication, leakage control and sample review before longer training.
