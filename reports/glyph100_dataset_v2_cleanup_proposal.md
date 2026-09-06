# Glyph-100M Dataset v2 Cleanup Proposal

Generated: 2026-05-31T23:12:38.575903+00:00

No files were removed. This is only a proposal.

| path | decision | possible recovery |
|---|---|---:|
| `checkpoints/glyph-100m` | keep latest.pt, step_0010000.pt, step_0005000.pt; consider removing intermediate 500/1000/2000/3000/4000/6000/7000/8000/9000 after explicit approval | ~8.2 GB |
| `checkpoints/glyph-100m-thermal-test` | can remove after confirming no longer needed; test-only checkpoint dir | ~2.2 GB |
| `checkpoints/sft-v0-smoke` | can remove; SFT smoke test checkpoint, not final | ~1.6 GB |
| `checkpoints/sft-v0-smoke-resume-test` | can remove; SFT resume test checkpoint, not final | ~1.3 GB |
| `logs/glyph-100m*` | keep logs; tiny and useful for reports | ~0.0 GB |

## Suggested Commands (do not run without approval)

```bash
# Keep latest.pt, step_0010000.pt and optionally step_0005000.pt.
# Example only:
rm checkpoints/glyph-100m/step_0000500.pt checkpoints/glyph-100m/step_0001000.pt checkpoints/glyph-100m/step_0002000.pt checkpoints/glyph-100m/step_0003000.pt checkpoints/glyph-100m/step_0004000.pt checkpoints/glyph-100m/step_0006000.pt checkpoints/glyph-100m/step_0007000.pt checkpoints/glyph-100m/step_0008000.pt checkpoints/glyph-100m/step_0009000.pt
rm -rf checkpoints/glyph-100m-thermal-test checkpoints/sft-v0-smoke checkpoints/sft-v0-smoke-resume-test
```

Estimated recoverable space if all proposed cleanup is approved: ~13.3 GB.
