#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

docker compose -f docker-compose.train.yml run --rm trainer python - <<'PY'
from pathlib import Path
import os
import numpy as np
import sentencepiece as spm
import torch

print("python smoke: ok")
print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
print("torch hip:", getattr(torch.version, "hip", None))
print("torch threads:", torch.get_num_threads())
print("env TRAIN_NUM_THREADS:", os.environ.get("TRAIN_NUM_THREADS"))

tokens_path = Path("data/processed/tokens.bin")
tokenizer_path = Path("data/processed/tokenizer.model")
checkpoint_path = Path("checkpoints/latest.pt")

print("tokens.bin exists:", tokens_path.exists(), "size:", tokens_path.stat().st_size if tokens_path.exists() else None)
print("tokenizer exists:", tokenizer_path.exists())
print("latest checkpoint exists:", checkpoint_path.exists(), "size:", checkpoint_path.stat().st_size if checkpoint_path.exists() else None)

if not tokens_path.exists() or not tokenizer_path.exists() or not checkpoint_path.exists():
    raise SystemExit("missing required training artifact")

tokens = np.memmap(tokens_path, dtype=np.uint16, mode="r")
print("token count:", len(tokens))

sp = spm.SentencePieceProcessor()
sp.load(str(tokenizer_path))
print("vocab size:", sp.vocab_size())
print("smoke test complete")
PY
