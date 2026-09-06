# Glyph-100M Dataset v2.3.1 Decision Report

Generated: 2026-06-06T20:46:02.952740+00:00

No training was started.

## Recommendation

D) zrobić krótki preflight, nie 50k.

v2.3.1 is cleaner but now marginal for a full 50k run. Prefer a short preflight or more clean sources.

## Key Numbers

- total tokens: 175,938,499
- train tokens: 174,962,162
- val tokens: 976,337
- Wikipedia share: 72.71%
- FineWeb2 PL share: 20.97%
- legacy share: 0.00%
- stage 3 / 50k epochs: 4.66
- FineWeb2 docs kept/rejected: 45,533 / 185,619
- FineWeb2 tokens kept/rejected: 36,896,346 / 124,062,895
- tokens removed from v2.3: 124,062,895

## Source Mix

```json
{
  "wolne_lektury": {
    "docs": 1525,
    "tokens": 3143341,
    "train_docs": 1517,
    "val_docs": 8,
    "train_tokens": 3126624,
    "val_tokens": 16717
  },
  "wikipedia_pl": {
    "docs": 184466,
    "tokens": 127929637,
    "train_docs": 183493,
    "val_docs": 973,
    "train_tokens": 127166956,
    "val_tokens": 762681
  },
  "allegro_summaries_source": {
    "docs": 539,
    "tokens": 1368381,
    "train_docs": 538,
    "val_docs": 1,
    "train_tokens": 1364804,
    "val_tokens": 3577
  },
  "wikibooks_pl": {
    "docs": 5388,
    "tokens": 4328329,
    "train_docs": 5364,
    "val_docs": 24,
    "train_tokens": 4312133,
    "val_tokens": 16196
  },
  "wikisource_pl": {
    "docs": 1543,
    "tokens": 2272465,
    "train_docs": 1535,
    "val_docs": 8,
    "train_tokens": 2263878,
    "val_tokens": 8587
  },
  "fineweb2_pl": {
    "docs": 45533,
    "tokens": 36896346,
    "train_docs": 45329,
    "val_docs": 204,
    "train_tokens": 36727767,
    "val_tokens": 168579
  }
}
```

## Decision Options

- A) v2.3.1 gotowy do stage 3 / 50k po osobnej zgodzie.
- B) jeszcze poprawić filtry.
- C) FineWeb2 jest za brudny i trzeba inne źródło.
- D) zrobić krótki preflight, nie 50k.

No stage 3 command was executed.
