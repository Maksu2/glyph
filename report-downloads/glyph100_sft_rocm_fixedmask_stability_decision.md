# Glyph-100M SFT ROCm fixed-mask stability decision

## Verdict

A) ROCm fixed-mask safe mode stable; corrected SFT smoke v0.1 can be considered.

## Evidence

- safe50 complete: `True`; final val loss: `2.08734`
- safe200 complete: `True`; final val loss: `0.182106`
- NaN/Inf/OOM/crash in either pass: `False`
- final safe200 loss: `0.676262`
- max grad norm safe200: `24.56411`

## Recommendation

A) ROCm fixed-mask safe mode stable, można rozważyć poprawiony SFT smoke v0.1.

Constraints before any next step:

- keep 44k as base;
- do not use 50k as base;
- do not run SFT v1 yet;
- if running smoke v0.1 on ROCm, start with conservative settings similar to this safe mode.
