# Glyph-100M 44k SFT smoke report

## Verdict

B: SFT smoke technically works via CPU fallback, but quality eval does not justify larger SFT before improving SFT data/eval and ROCm stability.

## Inputs

- base checkpoint: `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`
- latest diagnostic reference only: `checkpoints/glyph-100m-v2_3_1-50k/latest.pt`
- output dir: `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke`

## Dataset

- examples: 1500
- train/val: 1350 / 150
- max template tokens: 65 / 512
- over context: 0
- duplicates: {'duplicate_instructions_extra': 0, 'duplicate_pairs_extra': 0}
- suspicious phrases: all zero

## Training

- ROCm attempt stopped at step 3 because SFT loss became NaN; `latest` was not overwritten.
- diagnostic NaN checkpoint: `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke/glyph-100m-v2_3_1-44k-sft-smoke-nan.pt`
- CPU fallback completed 150 SFT steps.
- final checkpoint: `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke/glyph-100m-v2_3_1-44k-sft-smoke-final.pt`
- best checkpoint: `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke/glyph-100m-v2_3_1-44k-sft-smoke-best.pt`
- final val loss: 2.8828
- best val loss: 2.8828
- avg logged CPU tok/s: 183.1

## Eval

- baseline base avg score: 4.21
- before/after winners: {'tie': 25, 'base': 3}
- base avg score: 4.21
- SFT avg score: 3.71
- base web residue: 0
- SFT web residue: 2
- base pseudo-ency: 1
- SFT pseudo-ency: 0

## Interpretation

- The SFT run learned the small dataset in loss terms, but the qualitative probe did not improve over the base checkpoint.
- SFT reduced pseudo-ency in this small probe, but introduced web residue and did not win any prompt.
- This is not good enough to scale to a larger SFT yet.

## Next Recommendation

- Do not run larger SFT yet.
- Fix ROCm SFT backward instability or use CPU only for very small SFT probes.
- Improve SFT dataset with more varied instruction behavior and add stronger eval before a larger SFT v1.
- If continuing, run a smaller LR/better curated SFT v0.1 smoke and require SFT wins over base before scaling.
