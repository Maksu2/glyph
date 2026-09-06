# Glyph HDD cleanup - 2026-08-31

## Outcome

The explicitly approved cleanup is complete. No training process or training
container was running, and no active Glyph checkpoint was modified.

## Actions completed

### Old checkpoint history

- Scope: `/mnt/data/mac/GlyphArchive/glyph-cleanup-20260522-170209/ai-model/checkpoints/steps`
- Before: 256 `.pt` files, 85,344,040,919 bytes (79.48 GiB)
- After: 4 milestone files, 1,307,955,452 bytes (1.22 GiB)
- Reclaimed: 84,036,085,467 bytes (78.26 GiB)
- Kept: `step_0050000.pt`, `step_0100000.pt`, `step_0150000.pt`, `step_0199500.pt`

The four retained files were re-hashed after cleanup and match the pre-cleanup
manifest. Other checkpoint directories, including current 27M/100M runs and
SFT artifacts, were left in place.

### Bambu recordings

- Removed: `/mnt/data/mac/GlyphArchive/glyph-cleanup-20260522-170209/bambu`
- Before: 76,016,438,869 bytes (70.80 GiB)
- Result: directory absent

This deletion was explicitly requested and is irreversible unless another
external backup exists.

### Gemma

- Removed: `/mnt/data/mac/GlyphArchive/glyph-cold-20260704/models/gemma4`
- Before: 5,335,290,128 bytes (4.97 GiB)
- Removed the obsolete repo symlink: `/home/maksu/ai-model/models/gemma4`
- Result: target and symlink absent

The running local inference service does not use this Gemma path.

### Old corpus text

Both old 27M text artifacts were compressed with zstd level 3 and verified by
decompressing and comparing the full SHA256 before removing the plain-text
source:

| Artifact | Original | Compressed | Reclaimed |
|---|---:|---:|---:|
| `data/raw/corpus.txt` | 19,676,304,049 B (18.32 GiB) | 7,476,259,252 B (6.96 GiB) | 12,200,044,797 B (11.36 GiB) |
| `data/processed/corpus_clean.txt` | 19,367,506,505 B (18.04 GiB) | 7,350,584,666 B (6.85 GiB) | 12,016,921,839 B (11.19 GiB) |

Compressed files:

- `.../data/raw/corpus.txt.zst`
- `.../data/processed/corpus_clean.txt.zst`

Verification:

- raw source SHA256: `1f0eca37955dd232f68eb50348c2b5581c39249b442d5413561212c8b79d2aa9`
- clean source SHA256: `feadf70827e210efe64a3cbee4911fd676dc8291d7fcdecff071529a36a824af`
- both archives passed `zstd -t`
- decompressed archive hashes matched their original source hashes

The old `corpus_clean.txt` symlink in the active repo was removed because its
target was intentionally archived and no longer exists as plain text.
`tokens.bin`, `val_tokens.bin`, other datasets, current checkpoints, reports,
and code were intentionally left untouched.

## Space result

- Estimated logical space reclaimed by the approved targets: 189,604,781,100
  bytes (176.58 GiB)
- Post-cleanup archive sizes: `glyph-cleanup-20260522-170209` 2.8 GB,
  `glyph-cold-20260704` 45 GB, active repo 32 GB (`du -sh`)
- Post-cleanup `/mnt/data`: about 1.4 TiB free according to `df -h`
- Post-cleanup `/home` filesystem: about 212 GiB free according to `df -h`

The logical reclaim estimate excludes filesystem metadata and any unrelated
background changes.

## Safety checks

- No `train.py` process was active after cleanup.
- No Docker container matching training/ROCm was active after cleanup.
- Retained checkpoint count is exactly 4 in the approved historical `steps`
  directory.
- No current Glyph checkpoint directory was targeted.
- No dataset, tokenizer, configuration, secret, or credential was changed.

## Remaining intentional storage

The old tokenized `tokens.bin` and related data remain because the request was
to leave the rest of the project in place. They can be considered in a later,
separate cleanup after confirming that no current workflow needs them.
