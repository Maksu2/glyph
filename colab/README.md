# Glyph Colab package

`Glyph_Colab.ipynb` prepares a CUDA runtime from archives built on the Glyph
homelab. It does not require Google Drive API credentials. Drive is mounted with
the standard Colab UI and is used only for durable input and validated exports.

## Safety defaults

- `RUN_TRAINING = False`
- `RUN_COMPATIBILITY_SMOKE = False`
- `EXPORT_RESULTS = False`
- fp32, batch size 1, gradient accumulation 4
- base checkpoint fixed to Glyph-100M step 44,000
- checkpoint 50k is not accepted as the bundle base
- no archive is extracted over an existing local runtime unless explicitly allowed
- no result is copied to Drive before local reload and archive verification

## Drive layout

```text
MyDrive/Glyph/colab/
  input/    # manifest, SHA256SUMS and input archives
  output/   # validated result archives only
  reports/  # optional copied summaries
```

Upload `manifest.json`, `SHA256SUMS`, the four required `.tar.zst` archives and
the notebook from `dist/glyph-colab/` to `input/`. Then open the notebook,
select a GPU runtime, edit the first configuration cell and execute preflight.

The compatibility smoke and real training cells require separate exact-text
confirmations. A notebook restart does not imply permission to train.

See `docs/COLAB_MIGRATION.md` for the complete runbook.
