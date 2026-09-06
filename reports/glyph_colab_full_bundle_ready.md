# Glyph Colab full upload bundle

**Status: PASS - the complete upload bundle is ready; no training or upload was run.**

Generated: `2026-08-02T00:54:33Z`

## Ready download

- Convenience ZIP: `dist/glyph-colab-upload-ready-20260802T005327Z.zip`
- ZIP size: `362,940,589` bytes (`346.13 MiB`)
- ZIP SHA256: `9adbcd341659235f6f69739190ba2807228ef04030ea6bca3244590029aeeb43`
- Extracted bundle folder: `dist/glyph-colab/`
- Bundle creation timestamp: `2026-08-02T00:53:30.821124+00:00`

The ZIP contains one top-level folder, `glyph-colab/`, with 11 files. It is a
download convenience wrapper. The `.tar.zst` files inside are the inputs the
Colab notebook expects.

## Bundle contents

| File | Role | Size |
|---|---|---:|
| `Glyph_Colab.ipynb` | Preconfigured Colab notebook | 17,500 B |
| `README.md` | Short bundle overview | 1,306 B |
| `UPLOAD_INSTRUCTIONS.md` | Exact upload sequence | 690 B |
| `manifest.json` | Bundle metadata and member hashes | 10,912 B |
| `SHA256SUMS` | Outer integrity checks | 854 B |
| `glyph-code-20260802T005327Z.tar.zst` | Code and configuration | 41,079 B |
| `glyph-tokenizer-20260802T005327Z.tar.zst` | SentencePiece tokenizer | 276,569 B |
| `glyph-base44k-20260802T005327Z.tar.zst` | Optimizer-free approved base 44k | 361,938,453 B |
| `glyph-sft-data-20260802T005327Z.tar.zst` | SFT v0.3 dataset and splits | 107,469 B |
| `glyph-reports-20260802T005327Z.tar.zst` | Optional reports/evals | 541,318 B |
| `local-verification.json` | Full local verifier result | 2,749 B |

## Validation

- ZIP central-directory and CRC check: PASS (`11` entries, no bad member)
- Bundle SHA256 verification: PASS
- Safe extraction of every `.tar.zst`: PASS
- Approved base checkpoint: `44k`, not `50k`
- Checkpoint step: `44000`
- Variant: `glyph-100m`
- Context length: `512`
- Strict CPU model load: PASS, `113` tensors, no missing/unexpected keys
- Unique/trainable parameters: `97,654,272`
- Tokenizer SHA256: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`
- Dataset: `glyph100_sft_smoke_v0_3.jsonl`, `2,753` examples
- Fixed label boundary `i < assistant_pos`: PASS
- First assistant token and `<|end|>` supervised: PASS
- Prompt masked and padding `-100`: PASS
- CPU inference compatibility smoke: PASS

The source checkpoint was not modified. The bundled base payload intentionally
omits historical optimizer/scheduler state because Colab SFT starts with a
fresh optimizer. The model tensors and required checkpoint metadata remain.

## Upload to Google Drive

1. Download and extract the convenience ZIP on the user's computer.
2. In Google Drive create `My Drive/Glyph/colab/input/`.
3. Upload the files *inside* the extracted `glyph-colab/` folder to that Drive
   directory: `manifest.json`, `SHA256SUMS`, and the five `.tar.zst` archives.
   The reports archive is optional.
4. Do not upload only the outer ZIP to `input/`; the notebook expects the
   individual archives.
5. Open the included `Glyph_Colab.ipynb` with Google Colaboratory. Its archive
   names are already filled with the exact timestamped names.
6. Select a GPU runtime, run the mount/environment/extract/preflight cells and
   leave `RUN_TRAINING = False`.

The notebook itself is small because it is only the controller. The 345 MiB
base archive carries the actual model.

## Safety result

No pretraining, SFT, backward pass, optimizer step, Google Drive upload, Drive
API call or credential access occurred while preparing this folder.
