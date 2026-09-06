# Glyph-100M Dataset v2.3 Decision Report

Generated: 2026-06-06T19:21:33.532108+00:00

No training was started.

## Recommendation

A) v2.3 gotowy, można rozważyć stage 3 / 50k po osobnej zgodzie.

v2.3 reaches the practical token target with legacy excluded and a much lower Wikipedia share. Before training, inspect FineWeb2 samples and confirm that web residue is acceptable.

## Key Numbers

- total tokens: 300,001,394
- train tokens: 298,418,722
- val tokens: 1,582,672
- Wikipedia share: 42.64%
- FineWeb2 PL share: 53.65%
- legacy share: 0.00%
- stage 3 / 50k epochs: 2.73
- FineWeb2 raw rows seen: 407,663
- FineWeb2 accepted docs: 231,152
- FineWeb2 acceptance rate: 56.70%

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
    "docs": 231152,
    "tokens": 160959241,
    "train_docs": 229984,
    "val_docs": 1168,
    "train_tokens": 160184327,
    "val_tokens": 774914
  }
}
```

## Decision Options

- A) v2.3 gotowy, można odpalić stage 3 / 50k po osobnej zgodzie.
- B) v2.3 lepszy, ale jeszcze wymaga poprawek.
- C) potrzebne inne źródła / ostrzejsze filtrowanie.
- D) lepiej zrobić krótki preflight, nie 50k.
- E) zatrzymać się, bo dane są za słabe.

No stage 3 command was executed.
