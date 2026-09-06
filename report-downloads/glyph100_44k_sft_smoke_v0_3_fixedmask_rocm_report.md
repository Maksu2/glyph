# Glyph-100M SFT smoke v0.3 fixed-mask ROCm report

## Status

- run: `complete`
- type: small SFT smoke v0.3, not SFT v1
- base: `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`
- output: `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_3-fixedmask-rocm`
- 50k was not used as base.

## Training

- logged steps: `121`
- loss start/end: `4.813179` -> `1.404461`
- avg loss end: `2.261383`
- best val loss: `1.080073` at step `450`
- final val loss: `1.188109` at step `586`
- avg tok/s: `416.7`
- max grad norm: `41.874626`
- NaN/Inf: `False`
- OOM/crash: `False`

## Val Losses

- step `50`: `3.137342`
- step `100`: `2.936439`
- step `150`: `2.16149`
- step `200`: `2.378358`
- step `250`: `2.096902`
- step `300`: `2.060734`
- step `350`: `2.015179`
- step `400`: `1.512109`
- step `450`: `1.080073`
- step `500`: `1.516906`
- step `550`: `1.085965`
- final step `586`: `1.188109`

## Dataset

- examples: `2753`
- split: `{'train': 2341, 'val': 275, 'test': 137}`
- max template tokens: `76`
- label sanity: `{'first_token_supervised': True, 'end_token_supervised': True, 'prompt_masked': True, 'padding_ignore_index': True, 'examples_without_labels': 0}`
