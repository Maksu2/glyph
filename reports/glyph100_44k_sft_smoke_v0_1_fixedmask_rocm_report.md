# Glyph-100M corrected SFT smoke v0.1 fixed-mask ROCm report

## Verdict

B) SFT v0.1 działa częściowo, ale trzeba poprawić dataset/ustawienia przed większym SFT.

Nie uruchamiałem SFT v1, większego SFT ani dalszego pretrainingu.

## Training

- base checkpoint: `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`
- output dir: `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm`
- device: ROCm/GPU, fp32 only, no autocast, no mixed precision, no GradScaler
- batch size: 1
- gradient accumulation: 4
- learning rate: 1e-5
- grad clip: 0.5
- max steps: 400
- train loss: 4.7426 -> 1.3191
- final avg train loss: 2.3594
- avg logged tok/s: 551
- final val loss: 1.514836
- min observed val loss: step 350 = 1.380674
- NaN/Inf/OOM/crash: `{'nan_inf': False, 'oom': False, 'crash_exception': False, 'emergency_report_exists': False}`

## Val Losses

- step 50: 3.215213
- step 100: 2.450624
- step 150: 2.241859
- step 200: 2.132044
- step 250: 1.880261
- step 300: 1.605227
- step 350: 1.380674
- step 400: 1.524028
- final step 400: 1.514836

## Checkpoints

- `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm-step_000100-step_000100.pt`
- `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm-step_000200-step_000200.pt`
- `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm-step_000300-step_000300.pt`
- `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm-step_000400-step_000400.pt`
- `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm-final-step_000400.pt`
- `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm-latest.pt`

## Before/After Eval

- eval file: `eval/glyph-100m/sft_smoke_v0_1_fixedmask_before_after.md`
- examples: 50 (32 held-out target, 10 diagnostic, 8 continuation)
- decoding: `greedy temperature=0.0 top_k=None top_p=1.0`
- winners: `{'tie': 14, 'sft': 34, 'base': 2}`
- base avg score: -0.94
- SFT avg score: 4.22
- SFT first-token correct on target examples: 17/32
- SFT ended by `<|end|>` on instruction examples: 35/42
- SFT natural endings: 37/50
- SFT repetition samples: 20/50
- SFT pseudo-ency: 0/50
- SFT web residue: 0/50
- generic assistant template samples: 0/50
- exact target matches on held-out val: 0

## Interpretation

- Mechanicznie pipeline SFT po fixed-mask działa na ROCm safe settings.
- Jakościowo v0.1 jest dużo lepszy od base w instruction-shaped prompts, ale nadal łapie powtórzenia i nie zawsze trafia pierwszy token odpowiedzi.
- Continuation sanity nie jest lepsze od base i nie powinno być traktowane jako finalna jakość base LM.
- Ten wynik uzasadnia poprawę datasetu/ustawień i ewentualny kolejny mały smoke, ale nie automatyczne skalowanie do SFT v1.
