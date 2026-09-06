#!/usr/bin/env python3
"""Validate Glyph SFT v0 JSONL datasets."""

from __future__ import annotations

import argparse
from pathlib import Path

from sft_utils import collect_dataset_stats, load_jsonl, load_sentencepiece, similar_instruction_pairs, write_json


def render_markdown(results: list[dict]) -> str:
    lines = ["# Glyph SFT v0 dataset validation", ""]
    for result in results:
        stats = result["stats"]
        token = stats.get("token_stats") or {}
        lines += [
            f"## {Path(result['path']).name}",
            "",
            f"- examples: {stats['examples']}",
            f"- invalid JSON lines: {len(result['invalid_json'])}",
            f"- records with missing fields: {len(result['missing_fields'])}",
            f"- total words: {stats['total_words']}",
            f"- avg instruction words: {stats['instruction_words_avg']:.1f}",
            f"- avg response words: {stats['response_words_avg']:.1f}",
            f"- duplicate instructions, extra copies: {stats['instruction_duplicate_extra']}",
            f"- duplicate instruction+response pairs, extra copies: {stats['instruction_response_duplicate_extra']}",
        ]
        if token:
            lines += [
                f"- real tokenizer template tokens: {token['template_total_tokens']}",
                f"- template tokens avg/p50/p90/p95/max: {token['template_avg']:.1f} / {token['template_p50']:.1f} / {token['template_p90']:.1f} / {token['template_p95']:.1f} / {token['template_max']}",
                f"- fits context 256: {token['fits_context']}",
                f"- over context 256: {token['over_context']}",
            ]
        lines += ["", "### Categories", ""]
        for category, count in sorted(stats["categories"].items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"- {category}: {count}")
        lines += ["", "### Bad-pattern checks", ""]
        for key, value in stats["bad_patterns"].items():
            lines.append(f"- {key}: {value}")
        if result["similar_instruction_pairs"]:
            lines += ["", "### Similar instruction pairs sample", ""]
            for pair in result["similar_instruction_pairs"][:10]:
                lines.append(
                    f"- lines {pair['line_a']} / {pair['line_b']} score={pair['score']}: "
                    f"{pair['instruction_a']!r} <> {pair['instruction_b']!r}"
                )
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Glyph SFT JSONL files")
    parser.add_argument("inputs", nargs="+")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--context-len", type=int, default=256)
    parser.add_argument("--out-json", default="data/sft/reports/sft_v0_validation.json")
    parser.add_argument("--out-md", default="data/sft/reports/sft_v0_dataset_report.md")
    args = parser.parse_args()

    sp = load_sentencepiece(args.tokenizer)
    results = []
    for path in args.inputs:
        loaded = load_jsonl(path)
        stats = collect_dataset_stats(loaded.records, sp=sp, context_len=args.context_len)
        results.append(
            {
                "path": str(loaded.path),
                "invalid_json": loaded.invalid_json,
                "missing_fields": loaded.missing_fields,
                "stats": stats,
                "similar_instruction_pairs": similar_instruction_pairs(loaded.records),
            }
        )

    write_json(args.out_json, results)
    Path(args.out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_md).write_text(render_markdown(results), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
