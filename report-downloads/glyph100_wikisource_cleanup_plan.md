# Glyph-100M Wikisource Cleanup Plan

Generated: 2026-06-01

No training was started.

## Current State

In `glyph100_dataset_v2_1`, Wikisource contributes:

- docs: 2,430
- tokens: 3,115,955

It adds non-Wikipedia text, but sample audit shows mixed quality.

## Problems Seen In Samples

Accepted/final samples include good continuous texts:

- `Żywot Józefa/XII`
- `Listy do królowej Marysieńki/List z Dnia 15 VII 1665`
- `Mormolyce phyllodes`
- legal/source texts with continuous paragraphs

But they also include pages that should be rejected or downweighted:

- disambiguation/index pages: `W miasteczku`, `Źródło`, `Antychryst`
- Bible chapters and older religious texts that may dominate old orthography if uncapped
- legal acts with dense article formatting
- pages with `<pages index=...>` transclusion markup
- bibliography-like pages listing editions/translations

Rejected samples already catch some of this:

- `<pages index=...>` pages
- short bibliographic pages
- proofread project metadata
- index-like poetry/song pages

## Proposed Filters

Reject by title:

- title contains only a short ambiguous phrase and text has repeated `– wiersz`, `– utwór`, `– opowiadanie`
- title starts or contains technical namespaces: `Wikisource:`, `Indeks:`, `Strona:`, `Kategoria:`, `Szablon:`, `Plik:`
- title includes `/całość` only if the text is real continuous prose after cleaning

Reject by text patterns:

- `<pages index=`
- `Ukończone projekty proofread`
- `wydanie z ... roku` repeated many times with little prose
- many lines shaped like bibliographic entries
- high ratio of `– wiersz`, `– pieśń`, `– fraszka`, `ze zbioru`
- too many wiki links/templates after cleanup
- too many verse-like very short lines unless explicitly allowing poetry

Downweight or cap:

- Bible / old religious texts
- legal acts
- poetry-only texts
- lists of quotations or anthology indexes

Keep:

- continuous prose chapters,
- essays,
- letters,
- educational/scientific texts,
- public-domain books after markup removal.

## Before / After Examples

### Example 1: index/disambiguation

Before:

`W miasteczku – utwór Klemensa Junoszy ... W miasteczku – wiersz Marii Konopnickiej ...`

Decision:

Reject. This is an index/disambiguation page, not training prose.

### Example 2: good continuous old text

Before:

`XII Tu ku królowi Jakóba Józef wiedzie... ROZPRAWA DWANASTA. ROZMOWCE: JÓZEF — JAKÓB — FARAO...`

After:

Keep after removing navigation and capping old-style text contribution.

### Example 3: transclusion markup

Before:

`<pages index="Śpiewnik..." from="..." to="..." />`

Decision:

Reject unless expanded text is available without markup.

### Example 4: Wikibooks-style markup, similar cleanup needed

Before:

`{{SkomplikowanaStronaStart}} ... <MATH>...</MATH> ...`

After:

Keep only after template/math cleanup, and reject if the page becomes mostly table of contents or markup.

## Implementation Plan For v2.2

1. Add `source == "wikisource_pl"` stricter filter separate from generic text filter.
2. Add `wikisource_label`:
   - `continuous_prose`
   - `legal`
   - `religious_old`
   - `poetry`
   - `index_disambiguation`
   - `metadata_transclusion`
   - `bibliography`
3. Include only:
   - all `continuous_prose`,
   - capped legal/religious/poetry,
   - reject index/metadata/bibliography.
4. Write samples:
   - 50 accepted before/after,
   - 50 rejected with reasons,
   - 50 random final.

## Expected Effect

Wikisource will probably shrink from ~3.1M tokens to roughly 1.5-2.5M cleaner tokens.

That is not enough to fix source mix alone, but it prevents Wikisource from adding index-like garbage while still keeping useful public-domain prose.
