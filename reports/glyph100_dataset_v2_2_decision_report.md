# Glyph-100M Dataset v2.2 Decision Report

Generated: 2026-06-01T19:36:14.755529+00:00

No training was started.

## Recommendation

C: v2.2 is not balanced enough for a 50k run. FinetextPL-Edu or another clean source is needed.

## What Changed From v2.1

- legacy remains 0.
- Wikipedia is capped to 70.0% of tokens.
- non-Wikipedia sources are 30.0%: Allegro PSC `source`, Wikibooks, Wolne Lektury and stricter Wikisource.
- v2.2 total tokens: 37,041,707.
- stage 3 / 50k would be 22.12 epochs over v2.2.

## Source Mix

```json
{
  "allegro_summaries_source": {
    "docs": 539,
    "tokens": 1368381,
    "train_tokens": 1360347,
    "val_tokens": 8034,
    "train_docs": 536,
    "val_docs": 3
  },
  "wikibooks_pl": {
    "docs": 5388,
    "tokens": 4328329,
    "train_tokens": 4305693,
    "val_tokens": 22636,
    "train_docs": 5373,
    "val_docs": 15
  },
  "wikipedia_pl": {
    "docs": 37648,
    "tokens": 25929191,
    "train_tokens": 25798075,
    "val_tokens": 131116,
    "train_docs": 37495,
    "val_docs": 153
  },
  "wikisource_pl": {
    "docs": 1543,
    "tokens": 2272465,
    "train_tokens": 2258594,
    "val_tokens": 13871,
    "train_docs": 1530,
    "val_docs": 13
  },
  "wolne_lektury": {
    "docs": 1525,
    "tokens": 3143341,
    "train_tokens": 3127545,
    "val_tokens": 15796,
    "train_docs": 1517,
    "val_docs": 8
  }
}
```

## Decision Options

- A) v2.2 gotowy, można odpalić stage 3 / 50k.
- B) v2.2 lepszy, ale jeszcze wymaga poprawek.
- C) potrzebny FinetextPL-Edu / inne źródła.
- D) lepiej zrobić krótki preflight, nie 50k.
- E) zatrzymać się, bo dane są za słabe.

## Current Verdict

C) potrzebny FinetextPL-Edu / inne źródła.

No stage 3 command was executed.
