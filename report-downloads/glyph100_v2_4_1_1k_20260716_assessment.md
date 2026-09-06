# Glyph-100M v2.4.1 1k generation assessment

## Scope

This is an early base-LM continuation sanity check at optimizer step 1,000. It is not an assistant or instruction-following evaluation.

## Manual assessment

- prompts: `8`
- samples: `16` (`normal` and `creative`)
- max new tokens: `80`
- meaningful, coherent continuations: `0/16`
- cutoff-like outputs: `15/16`
- natural endings: `1/16`
- literal repetition detected: `1/16`
- pseudo-encyclopedic/date/place residue: `5/16`
- URL/HTML/SEO residue: `0/16`

The outputs use recognizably Polish tokens and fragments, but they are not yet semantically coherent. The normal preset is less erratic than creative; creative more often falls into dates, villages and malformed pseudo-encyclopedic text.

## Interpretation

The checkpoint passes a mechanical generation sanity check: it loads, generates and already reflects Polish surface statistics. It does not pass a language-quality check. At 1,000 steps and 16.38M training tokens, this is expected.

The 1k result should be treated as successful pipeline validation only, not as evidence that Glyph-100M v2.4.1 is already useful. No 5k continuation was started.
