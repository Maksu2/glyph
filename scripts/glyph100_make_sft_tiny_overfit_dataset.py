#!/usr/bin/env python3
"""Select a small diverse SFT subset for fixed-mask tiny overfit."""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.sft_utils import collect_dataset_stats, format_sft_text, load_jsonl, load_sentencepiece, write_jsonl


PREFERRED_CATEGORIES = [
    "krotkie_definicje",
    "proste_techniczne_wyjasnienia",
    "mvp_first_project_advice",
    "brak_danych",
    "krotkie_poprawki_tekstu",
    "mini_streszczenia",
    "anty_petle",
    "naturalne_zakonczenia_odpowiedzi",
    "codzienne_proste_pytania",
    "ostrozne_odpowiedzi_przy_niepewnosci",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Glyph-100M fixed-mask tiny overfit SFT subset")
    parser.add_argument("--input", default="data/sft/glyph100_sft_smoke_v0.jsonl")
    parser.add_argument("--output", default="data/sft/processed/glyph100_sft_tiny_overfit_fixedmask_train.jsonl")
    parser.add_argument("--txt-output", default="data/sft/processed/glyph100_sft_tiny_overfit_fixedmask_train.txt")
    parser.add_argument("--report-md", default="data/sft/glyph100_sft_tiny_overfit_fixedmask_dataset_report.md")
    parser.add_argument("--report-json", default="data/sft/glyph100_sft_tiny_overfit_fixedmask_dataset_report.json")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--context-len", type=int, default=512)
    parser.add_argument("--examples", type=int, default=64)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    loaded = load_jsonl(args.input)
    rng = random.Random(args.seed)
    by_category: dict[str, list[dict]] = defaultdict(list)
    for record in loaded.records:
        by_category[str(record.get("category", ""))].append(record)
    for records in by_category.values():
        rng.shuffle(records)

    selected: list[dict] = []
    target_per_category = max(1, args.examples // len(PREFERRED_CATEGORIES))
    for category in PREFERRED_CATEGORIES:
        selected.extend(by_category.get(category, [])[:target_per_category])
    cursor = Counter(str(record.get("category", "")) for record in selected)
    while len(selected) < args.examples:
        candidates = sorted(PREFERRED_CATEGORIES, key=lambda c: cursor[c])
        added = False
        used_ids = {record.get("id") for record in selected}
        for category in candidates:
            for record in by_category.get(category, []):
                if record.get("id") not in used_ids:
                    selected.append(record)
                    cursor[category] += 1
                    added = True
                    break
            if added:
                break
        if not added:
            break

    for index, record in enumerate(selected, 1):
        record["tiny_overfit_id"] = f"tiny-fixedmask-{index:04d}"

    sp = load_sentencepiece(args.tokenizer)
    stats = collect_dataset_stats(selected, sp=sp, context_len=args.context_len)
    template_lengths = [len(sp.encode(format_sft_text(record), out_type=int)) for record in selected]
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_dataset": args.input,
        "output": args.output,
        "examples": len(selected),
        "seed": args.seed,
        "categories": dict(Counter(str(record.get("category", "")) for record in selected)),
        "stats": stats,
        "max_template_tokens": max(template_lengths) if template_lengths else 0,
        "over_context": sum(1 for n in template_lengths if n > args.context_len),
        "sample_examples": [
            {
                "id": record.get("id"),
                "tiny_overfit_id": record.get("tiny_overfit_id"),
                "category": record.get("category"),
                "instruction": record.get("instruction"),
                "response": record.get("response"),
                "template_tokens": template_lengths[i],
            }
            for i, record in enumerate(selected[:20])
        ],
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.txt_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report_md).parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.output, selected)
    Path(args.txt_output).write_text("\n".join(format_sft_text(record) for record in selected), encoding="utf-8")
    Path(args.report_json).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Glyph-100M fixed-mask tiny overfit dataset",
        "",
        f"- source dataset: `{args.input}`",
        f"- output: `{args.output}`",
        f"- examples: {len(selected)}",
        f"- max template tokens: {report['max_template_tokens']}",
        f"- over context {args.context_len}: {report['over_context']}",
        "",
        "## Categories",
        "",
    ]
    for category, count in report["categories"].items():
        lines.append(f"- `{category}`: {count}")
    lines.extend(["", "## Sample Examples", ""])
    for item in report["sample_examples"][:10]:
        lines.extend(
            [
                f"### {item['tiny_overfit_id']} / {item['category']}",
                "",
                f"Instruction: {item['instruction']}",
                "",
                f"Response: {item['response']}",
                "",
            ]
        )
    Path(args.report_md).write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
