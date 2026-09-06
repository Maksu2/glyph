#!/usr/bin/env python3
"""Render human-readable reports for Glyph-100M dataset v2 stats."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_STATS = Path("data/reports/glyph100_dataset_v2_stats.json")
DEFAULT_REPORT = Path("data/reports/glyph100_dataset_v2_report.md")


def fmt_int(value: int | float | None) -> str:
    if value is None:
        return "unknown"
    return f"{int(value):,}"


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "unknown"
    return f"{value:.2%}"


def table_rows(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "_none_\n"
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(str(row.get(col, "")) for col in columns) + " |")
    return "\n".join([header, sep, *body]) + "\n"


def render_samples(samples: list[dict[str, Any]]) -> str:
    chunks: list[str] = []
    for i, sample in enumerate(samples[:50], 1):
        label = sample.get("source", "unknown")
        title = sample.get("title") or sample.get("id") or ""
        text = sample.get("text", "")
        reasons = sample.get("reject_reasons")
        suffix = f" reasons={', '.join(reasons)}" if reasons else ""
        chunks.append(f"{i}. `{label}` {title}{suffix}\n\n   {text}")
    return "\n\n".join(chunks) if chunks else "_none_"


def build_report(stats: dict[str, Any]) -> str:
    source_rows = []
    for source, item in stats.get("sources", {}).items():
        source_rows.append(
            {
                "source": source,
                "seen_docs": fmt_int(item.get("seen_docs", 0)),
                "accepted_docs": fmt_int(item.get("accepted_docs", 0)),
                "train_tokens": fmt_int(item.get("train_tokens", 0)),
                "val_tokens": fmt_int(item.get("val_tokens", 0)),
                "acceptance": fmt_pct(item.get("acceptance_rate", 0.0)),
                "decision": item.get("decision", ""),
            }
        )

    p = stats.get("doc_token_percentiles", {})
    stage = stats.get("training_token_math", {})
    source_decisions = stats.get("source_decisions", [])
    quality_audit = stats.get("manual_quality_audit", {})
    quality_section = ""
    if quality_audit:
        quality_section = f"""
## Manual Quality Audit

- verdict: {quality_audit.get("verdict", "not recorded")}
- checked pattern counts are heuristic and do not replace reading samples.

```json
{json.dumps(quality_audit.get("accepted_pattern_counts", {}), ensure_ascii=False, indent=2)}
```

### Audit Notes

{quality_audit.get("notes", "No notes.")}
"""

    return f"""# Glyph-100M Dataset v2 Report

Generated: {stats.get("generated_at", "unknown")}

## Recommendation

{stats.get("recommendation", "No recommendation recorded.")}

## Dataset Identity

- dataset name: `{stats.get("dataset_name", "glyph100_dataset_v2")}`
- output train bin: `{stats.get("train_bin", "not written")}`
- output val bin: `{stats.get("val_bin", "not written")}`
- metadata: `{stats.get("metadata_path", "not written")}`
- tokenizer: `{stats.get("tokenizer_path", "unknown")}`
- tokenizer vocab size: {fmt_int(stats.get("tokenizer_vocab_size"))}
- context length target: {fmt_int(stats.get("context_len"))}
- split: document-level, stable hash, source-stratified
- val target: {stats.get("val_per_mille", 0) / 10:.1f}% by document hash per source

## Important Caveat

This v2 pipeline preserves `source`, `source_id` and stable `doc_id` from the
point where each source is loaded. For the old monolithic `data/raw/corpus.txt`
the original upstream source was not preserved, so those rows are labeled as
`legacy_mixed_corpus` and should not be treated as clean source attribution.

## Source Decisions

{table_rows(source_decisions, ["name", "decision", "type", "license", "risk"])}

## Counts

- documents seen: {fmt_int(stats.get("seen_docs"))}
- documents accepted: {fmt_int(stats.get("accepted_docs"))}
- documents rejected: {fmt_int(stats.get("rejected_docs"))}
- acceptance rate: {fmt_pct(stats.get("acceptance_rate"))}
- train documents: {fmt_int(stats.get("train_docs"))}
- val documents: {fmt_int(stats.get("val_docs"))}
- train tokens: {fmt_int(stats.get("train_tokens"))}
- val tokens: {fmt_int(stats.get("val_tokens"))}
- total tokens: {fmt_int(stats.get("total_tokens"))}
- estimated pre-filter tokens: {fmt_int(stats.get("estimated_prefilter_tokens"))}
- token/word ratio: {stats.get("token_word_ratio", 0):.3f}
- word/token ratio: {stats.get("word_token_ratio", 0):.3f}

## Source Mix

{table_rows(source_rows, ["source", "seen_docs", "accepted_docs", "train_tokens", "val_tokens", "acceptance", "decision"])}

## Document Lengths After Tokenization

- p50: {p.get("p50", 0):.0f}
- p75: {p.get("p75", 0):.0f}
- p90: {p.get("p90", 0):.0f}
- p95: {p.get("p95", 0):.0f}
- p99: {p.get("p99", 0):.0f}
- max: {fmt_int(stats.get("max_doc_tokens"))}
- docs <= context {fmt_int(stats.get("context_len"))}: {fmt_int(stats.get("docs_within_context"))} ({fmt_pct(stats.get("docs_within_context_ratio"))})

## Top Rejection Reasons

```json
{json.dumps(stats.get("rejection_reasons", {}), ensure_ascii=False, indent=2)}
```

## Suspicious Patterns

```json
{json.dumps(stats.get("suspicious_patterns", {}), ensure_ascii=False, indent=2)}
```

{quality_section}

## Training Token Math

- tokens per optimizer step: {fmt_int(stage.get("tokens_per_step"))}
- stage 3 / 50k total tokens: {fmt_int(stage.get("stage3_50k_tokens"))}
- stage 3 epochs on this v2 dataset: {stage.get("stage3_50k_epochs", 0):.2f}
- 100k total tokens: {fmt_int(stage.get("stage4_100k_tokens"))}
- 100k epochs on this v2 dataset: {stage.get("stage4_100k_epochs", 0):.2f}
- 200k total tokens: {fmt_int(stage.get("stage5_200k_tokens"))}
- 200k epochs on this v2 dataset: {stage.get("stage5_200k_epochs", 0):.2f}

## Accepted Samples

{render_samples(stats.get("accepted_samples", []))}

## Rejected Samples

{render_samples(stats.get("rejected_samples", []))}

## Random Final Samples

{render_samples(stats.get("final_samples", []))}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Glyph-100M dataset v2 markdown report")
    parser.add_argument("--stats", type=Path, default=DEFAULT_STATS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    stats = json.loads(args.stats.read_text(encoding="utf-8"))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(build_report(stats), encoding="utf-8")
    print(args.report)


if __name__ == "__main__":
    main()
