#!/usr/bin/env python3
"""Count real Glyph tokenizer lengths for SFT datasets."""

from __future__ import annotations

import argparse

from sft_utils import collect_dataset_stats, load_jsonl, load_sentencepiece, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Count SFT tokens with the real Glyph tokenizer")
    parser.add_argument("inputs", nargs="+")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--context-len", type=int, default=256)
    parser.add_argument("--out", default="data/sft/reports/sft_v0_token_stats.json")
    args = parser.parse_args()

    sp = load_sentencepiece(args.tokenizer)
    report = {
        "tokenizer": args.tokenizer,
        "context_len": args.context_len,
        "files": [],
    }
    for path in args.inputs:
        loaded = load_jsonl(path)
        stats = collect_dataset_stats(loaded.records, sp=sp, context_len=args.context_len)
        report["files"].append(
            {
                "path": str(loaded.path),
                "examples": len(loaded.records),
                "categories": stats["categories"],
                "words": stats["total_words"],
                "token_stats": stats["token_stats"],
            }
        )

    write_json(args.out, report)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
