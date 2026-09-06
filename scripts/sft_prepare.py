#!/usr/bin/env python3
"""Prepare Glyph SFT v0 train/val splits and token artifacts."""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

import numpy as np

from sft_utils import format_sft_text, load_jsonl, load_sentencepiece, token_ids, write_json, write_jsonl


def stratified_split(records: list[dict], val_fraction: float, seed: int) -> tuple[list[dict], list[dict]]:
    rng = random.Random(seed)
    by_category: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        by_category[str(record.get("category", ""))].append(record)

    train: list[dict] = []
    val: list[dict] = []
    for _, items in sorted(by_category.items()):
        items = list(items)
        rng.shuffle(items)
        n_val = max(1, round(len(items) * val_fraction)) if len(items) > 1 else 0
        val.extend(items[:n_val])
        train.extend(items[n_val:])

    rng.shuffle(train)
    rng.shuffle(val)
    return train, val


def write_txt_and_bin(records: list[dict], txt_path: Path, bin_path: Path, sp) -> int:
    txt_path.parent.mkdir(parents=True, exist_ok=True)
    bin_path.parent.mkdir(parents=True, exist_ok=True)
    all_ids: list[int] = []
    with txt_path.open("w", encoding="utf-8") as f:
        for record in records:
            text = format_sft_text(record)
            f.write(text)
            f.write("\n")
            all_ids.extend(token_ids(sp, text))
    arr = np.asarray(all_ids, dtype=np.uint16)
    arr.tofile(bin_path)
    return int(arr.size)


def clean_record(record: dict) -> dict:
    return {k: v for k, v in record.items() if not k.startswith("_")}


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare Glyph SFT v0 dataset")
    parser.add_argument("--input", required=True)
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--context-len", type=int, default=256)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--val-fraction", type=float, default=0.10)
    parser.add_argument("--prefix", default="sft_v0")
    parser.add_argument("--out-dir", default="data/sft/processed")
    parser.add_argument("--report", default="data/sft/reports/sft_v0_prepare_report.json")
    parser.add_argument(
        "--overflow",
        choices=("drop", "keep"),
        default="drop",
        help="How to handle examples whose full template exceeds context length",
    )
    args = parser.parse_args()

    loaded = load_jsonl(args.input)
    sp = load_sentencepiece(args.tokenizer)

    kept: list[dict] = []
    dropped: list[dict] = []
    for record in loaded.records:
        n_tokens = len(token_ids(sp, format_sft_text(record)))
        record["_template_tokens"] = n_tokens
        if n_tokens > args.context_len and args.overflow == "drop":
            dropped.append(record)
        else:
            kept.append(record)

    train, val = stratified_split(kept, args.val_fraction, args.seed)

    out_dir = Path(args.out_dir)
    train_jsonl = out_dir / f"{args.prefix}_train.jsonl"
    val_jsonl = out_dir / f"{args.prefix}_val.jsonl"
    train_txt = out_dir / f"{args.prefix}_train.txt"
    val_txt = out_dir / f"{args.prefix}_val.txt"
    train_bin = out_dir / f"{args.prefix}_train.bin"
    val_bin = out_dir / f"{args.prefix}_val.bin"

    write_jsonl(train_jsonl, (clean_record(r) for r in train))
    write_jsonl(val_jsonl, (clean_record(r) for r in val))
    train_tokens = write_txt_and_bin(train, train_txt, train_bin, sp)
    val_tokens = write_txt_and_bin(val, val_txt, val_bin, sp)

    report = {
        "input": args.input,
        "tokenizer": args.tokenizer,
        "context_len": args.context_len,
        "seed": args.seed,
        "val_fraction": args.val_fraction,
        "overflow": args.overflow,
        "input_examples": len(loaded.records),
        "kept_examples": len(kept),
        "dropped_over_context": len(dropped),
        "truncated_examples": 0,
        "train_examples": len(train),
        "val_examples": len(val),
        "train_tokens": train_tokens,
        "val_tokens": val_tokens,
        "paths": {
            "train_jsonl": str(train_jsonl),
            "val_jsonl": str(val_jsonl),
            "train_txt": str(train_txt),
            "val_txt": str(val_txt),
            "train_bin": str(train_bin),
            "val_bin": str(val_bin),
        },
        "dropped_lines": [int(r.get("_line", 0)) for r in dropped[:100]],
        "category_counts_train": {},
        "category_counts_val": {},
    }
    for target, items in (("category_counts_train", train), ("category_counts_val", val)):
        counts: dict[str, int] = {}
        for record in items:
            category = str(record.get("category", ""))
            counts[category] = counts.get(category, 0) + 1
        report[target] = dict(sorted(counts.items()))

    write_json(args.report, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
