#!/usr/bin/env python3
"""
Create a non-destructive validation holdout from the tail of tokens.bin.

This copies the last N uint16 token IDs into val_tokens.bin and writes metadata
that lets train.py exclude the same tail from future training restarts.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


DEFAULT_SOURCE = Path("data/processed/tokens.bin")
DEFAULT_OUTPUT = Path("data/processed/val_tokens.bin")
DEFAULT_HOLDOUT_TOKENS = 50_000_000
DTYPE = np.uint16
DTYPE_BYTES = np.dtype(DTYPE).itemsize


def format_bytes(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{size} B"


def parse_args():
    parser = argparse.ArgumentParser(description="Create val_tokens.bin from the tail of tokens.bin")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Source uint16 token file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output validation token file")
    parser.add_argument(
        "--tokens",
        type=int,
        default=DEFAULT_HOLDOUT_TOKENS,
        help="Number of tail tokens to hold out",
    )
    parser.add_argument(
        "--chunk-tokens",
        type=int,
        default=8_000_000,
        help="Copy chunk size in tokens",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing output and metadata")
    parser.add_argument("--dry-run", action="store_true", help="Print planned split without writing files")
    return parser.parse_args()


def main():
    args = parse_args()
    source = args.source
    output = args.output
    meta_path = output.with_suffix(".meta.json")

    if not source.exists():
        print(f"Source token file not found: {source}", file=sys.stderr)
        return 1
    if args.tokens <= 0:
        print("--tokens must be positive", file=sys.stderr)
        return 2
    if args.chunk_tokens <= 0:
        print("--chunk-tokens must be positive", file=sys.stderr)
        return 2
    if (output.exists() or meta_path.exists()) and not args.force:
        print(f"Refusing to overwrite existing {output} or {meta_path}; use --force", file=sys.stderr)
        return 2

    source_size = source.stat().st_size
    if source_size % DTYPE_BYTES != 0:
        print(f"Source size is not aligned to uint16 tokens: {source_size} bytes", file=sys.stderr)
        return 1

    total_tokens = source_size // DTYPE_BYTES
    if args.tokens >= total_tokens:
        print(
            f"Holdout is too large: requested {args.tokens:,} of {total_tokens:,} tokens",
            file=sys.stderr,
        )
        return 2

    train_token_limit = total_tokens - args.tokens
    output_size = args.tokens * DTYPE_BYTES

    print(f"source: {source}")
    print(f"source tokens: {total_tokens:,} ({format_bytes(source_size)})")
    print(f"validation: {args.tokens:,} tokens ({format_bytes(output_size)}) -> {output}")
    print(f"future training limit: first {train_token_limit:,} tokens")
    print("split: tail holdout, source file is not modified")

    if args.dry_run:
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    data = np.memmap(source, dtype=DTYPE, mode="r")
    tmp_path = output.with_suffix(output.suffix + ".tmp")

    try:
        with tmp_path.open("wb") as fout:
            start = train_token_limit
            end = total_tokens
            for pos in range(start, end, args.chunk_tokens):
                chunk_end = min(pos + args.chunk_tokens, end)
                fout.write(np.asarray(data[pos:chunk_end], dtype=DTYPE).tobytes())
            fout.flush()
            os.fsync(fout.fileno())
        tmp_path.replace(output)

        meta = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "dtype": "uint16",
            "split": "tail",
            "source_path": str(source),
            "source_size_bytes": source_size,
            "source_total_tokens": total_tokens,
            "output_path": str(output),
            "holdout_tokens": args.tokens,
            "train_token_limit": train_token_limit,
        }
        with meta_path.open("w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
            f.write("\n")

    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    print(f"wrote: {output} ({format_bytes(output.stat().st_size)})")
    print(f"wrote: {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
