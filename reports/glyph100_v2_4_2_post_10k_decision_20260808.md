# Glyph-100M v2.4.2 decision after 10k

## Verdict

**The 10k checkpoint is technically healthy and is the best v2.4.2 training checkpoint so far, but it is still a weak early base LM. Do not present it as a useful model or assistant. Do not start another stage automatically.**

A separately approved continuation to 15k is technically reasonable because validation loss is still falling, every source-specific loss improved and 10k represents only about 0.71 pass through the corpus. The quality gain from 5k to 10k is modest, so 15k should remain another checkpointed diagnostic stage rather than an open-ended run.

## Quantitative comparison

| metric | v2.4.1 10k | v2.4.2 5k | v2.4.2 10k |
|---|---:|---:|---:|
| heuristic average | 3.025 | 3.175 | 3.200 |
| natural endings | 4/40 | 5/40 | 9/40 |
| cutoff-like | 37/40 | 40/40 | 34/40 |
| repetition | 14/40 | 13/40 | 17/40 |
| pseudo-ency | 2/40 | 0/40 | 1/40 |
| web residue | 0/40 | 0/40 | 0/40 |

Pairwise v2.4.2 10k versus 5k: 10k won 11, 5k won 10, 19 tied. Against v2.4.1 10k: v2.4.2 won 9, lost 8 and tied 23.

The normal preset improved from `3.45` at v2.4.2 5k to `3.70` at 10k with repetition unchanged at `4/20`. The conservative preset regressed: `2.70` average with repetition in `13/20`. Low-temperature decoding is currently a poor default.

## Source-specific validation

Every fixed v2.4.2 source bin improved from 5k to 10k, and v2.4.2 10k beat v2.4.1 10k on all seven bins.

| source | v2.4.2 5k | v2.4.2 10k | delta | v2.4.1 10k |
|---|---:|---:|---:|---:|
| 1000_novels | 4.6776 | 4.0814 | -0.5962 | 4.3510 |
| eltec_pol | 4.4728 | 3.8470 | -0.6259 | 4.1103 |
| parliamentary | 4.6581 | 3.9184 | -0.7397 | 3.9852 |
| wikibooks | 5.2153 | 4.3293 | -0.8860 | 4.6204 |
| wikinews | 5.0649 | 4.2297 | -0.8352 | 4.4554 |
| wikipedia_pl | 4.6670 | 3.7956 | -0.8714 | 4.0973 |
| wolne_lektury | 4.4923 | 3.8876 | -0.6047 | 4.1414 |

## Manual semantic review

The automatic score overstates usefulness. Most factual prompts remain wrong or incoherent. Examples include incorrect continuations for Warsaw, Poland, energy, machine learning, water, the Sun, computers and operating systems. Several narrative prompts are more fluent, but many factual-looking passages invent dates, institutions or technical terms.

This means:

- the model is learning the corpus distribution;
- data-source balance is measurably better than v2.4.1;
- semantic competence is not established at 10k;
- completion length and looping are still strongly decoding-dependent;
- no SFT or public demo should be based on a claim that the base model is already good.

## Next gate

If continuing, use the verified 10k checkpoint and stop at 15k total. Re-run the same source validation and matched generation panel before any later step. A continuation beyond 15k should require both continued validation improvement and visible semantic progress.

No next training stage was started as part of this decision.

