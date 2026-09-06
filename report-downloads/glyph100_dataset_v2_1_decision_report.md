# Glyph-100M Dataset v2.1 Decision Report

Generated: 2026-06-01T05:04:22.395021+00:00

## Verdict

B: v2.1 is cleaner than v2 and is the best current candidate, but 50k would still be 6.10 epochs. I recommend approving only a short stage-3 preflight or adding more clean sources before full 50k.

## Selected Variant

- variant: `D`
- total tokens: 134,188,933
- train tokens: 133,401,769
- val tokens: 787,164
- stage 3 / 50k epochs: 6.10

## Variant Summary

| variant | total tokens | legacy tokens | 50k epochs | risk |
|---|---:|---:|---:|---|
| A | 149,098,802 | 14,909,869 | 5.49 | best quality compromise; legacy capped near 10% |
| B | 167,736,162 | 33,547,229 | 4.88 | more data, more legacy risk |
| C | 168,510,760 | 34,321,827 | 4.86 | legacy still too influential |
| D | 134,188,933 | 0 | 6.10 | cleanest but small; many repeated epochs at 50k |

No training was started.
