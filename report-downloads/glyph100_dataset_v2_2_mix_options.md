# Glyph-100M Dataset v2.2 Mix Options

Generated: 2026-06-01

No training was started. These are planning estimates before building `glyph100_dataset_v2_2`.

## Constants

- Current checkpoint: Glyph-100M at 10k.
- Stage 3 / 50k total tokens: `50,000 * 16,384 = 819,200,000`.
- v2.1 total tokens: 134,188,933.
- v2.1 Wikipedia tokens: 127,929,637.

## Candidate Token Estimates

| source | estimated usable tokens | confidence | notes |
|---|---:|---|---|
| Wikipedia PL from v2.1 | 127.9M | high | already built |
| Wolne Lektury | 3.1M | high | already built; local cache nearly complete |
| Wikisource cleaned | 1.5-2.5M | medium | stricter cleanup expected to remove index/meta pages |
| Wikibooks PL cleaned | ~9.4M | medium | in-memory dump audit: 7,671 accepted pages |
| Allegro PSC `source` articles | ~54M | medium | 200-row streaming estimate; use source article text only |
| NKJP1M | ~1M | medium | high-quality, but loader adaptation needed |
| FinetextPL-Edu | very large | high size / unknown sample | gated; likely best large addition |
| FinePDFs-pol | potentially huge | low quality confidence | first samples noisy/table-heavy |

## Option A: Wikipedia Max 70%

Goal:

- keep Wikipedia <= 70%,
- no legacy,
- use non-Wiki sources we can audit without gated access.

Estimated mix:

| source | tokens |
|---|---:|
| Wikipedia PL | 127.9M |
| Allegro PSC articles | ~54M |
| Wikibooks PL cleaned | ~9.4M |
| Wolne Lektury | 3.1M |
| Wikisource cleaned | ~2M |
| total | ~196M |

Estimated Wikipedia share: ~65%.

50k epochs: `819.2M / 196M = ~4.18`.

Risk:

- PSC is news/legal/business article style, not purely educational.
- Wikibooks has wikitext/markup/math cleanup risk.
- Still smaller than ideal, but much less wiki-heavy than v2.1.

Recommendation:

Use. This is the best v2.2 target we can likely build now without FinetextPL access.

## Option B: Wikipedia Max 50%

Goal:

- Wikipedia <= 50%,
- enough non-Wiki text for a more balanced stage 3.

Minimum non-Wiki needed if keeping all current Wikipedia:

- at least ~128M non-Wiki tokens.

Available without FinetextPL:

- PSC + Wikibooks + Wolne + Wikisource + NKJP is roughly 67-70M.

Missing:

- roughly 60M+ clean non-Wiki tokens.

Likely required:

- FinetextPL-Edu filtered by `prediction >= 2.5`, or
- carefully sampled Polish FinePDFs-Edu/FinePDFs with stronger filters.

50k epochs if total reaches ~256M: `819.2M / 256M = ~3.20`.

Risk:

- FinetextPL is gated.
- FinePDFs-pol sample quality was poor without filtering.

Recommendation:

Later. Do not block v2.2-A on this, but use it as v2.3 target if FinetextPL access is approved.

## Option C: Maximum Cleanliness, Smaller Dataset

Goal:

- accept fewer tokens,
- use only sources that look clean in samples,
- avoid noisy PDF/web corpora.

Estimated mix:

| source | tokens |
|---|---:|
| Wikipedia PL, optionally capped/downsampled | 90-110M |
| Allegro PSC high-quality subset | 35-45M |
| Wikibooks strict subset | 5-8M |
| Wolne Lektury | 3.1M |
| Wikisource strict subset | 1-2M |
| NKJP1M if adapted | ~1M |
| total | ~135-167M |

50k epochs: roughly 4.9-6.1.

Risk:

- Still too small for full 50k if quality training is the goal.
- Better as a controlled comparison/preflight dataset.

Recommendation:

Use only if we choose quality over all token-count concerns and accept repeated epochs.

## Option D: v2.1 + Short Preflight

Goal:

- do not build v2.2 yet,
- run only a short continuation on v2.1 to observe whether wiki-heavy clean data helps or hurts.

Suggested length:

- +2k steps: 32.8M additional tokens, ~0.24 v2.1 epochs.
- +5k steps: 81.9M additional tokens, ~0.61 v2.1 epochs.

Risk:

- Still wiki-heavy.
- Gives limited signal about long-run quality.

Recommendation:

Valid only if we want a very cheap experiment, not as replacement for v2.2.

## Decision

Recommended next build: Option A.

`glyph100_dataset_v2_2` should target:

- Wikipedia <= 70%,
- no legacy,
- PSC source articles,
- cleaned Wikibooks PL,
- stricter Wikisource,
- Wolne Lektury,
- optional NKJP1M only if loader adaptation is quick.

Do not use FinePDFs-pol in v2.2 without a separate stronger filter/audit; the first samples are too table-heavy.
