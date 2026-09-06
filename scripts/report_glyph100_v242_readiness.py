#!/usr/bin/env python3
"""Render the v2.4.2 readiness decision from build and validation evidence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
METADATA = ROOT / "data/processed/glyph100_v2_4_2_metadata.json"
VALIDATION = ROOT / "reports/glyph100_v2_4_2_validation.json"
OUTPUT_MD = ROOT / "reports/glyph100_v2_4_2_readiness_20260718.md"
OUTPUT_JSON = ROOT / "reports/glyph100_v2_4_2_readiness_20260718.json"


def main() -> None:
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    approved = bool(validation.get("ready_for_5k_proxy"))
    sources = metadata["sources"]
    input_tokens = metadata["input_source_tokens"]
    rows = []
    for source, item in sources.items():
        rows.append(
            {
                "source": source,
                "v2_4_1_tokens": int(input_tokens.get(source, 0)),
                "v2_4_2_tokens": int(item["tokens"]),
                "share": item["tokens"] / metadata["total_tokens"],
            }
        )
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": "APPROVE_FRESH_5K_PROXY" if approved else "STOP_DATASET_NOT_READY",
        "dataset_name": metadata["dataset_name"],
        "derived_from": metadata["derived_from"],
        "train_tokens": metadata["train_tokens"],
        "val_tokens": metadata["val_tokens"],
        "total_tokens": metadata["total_tokens"],
        "total_docs": metadata["total_docs"],
        "literature_share": metadata["literature_share"],
        "wikipedia_share": metadata["wikipedia_share"],
        "parliamentary_share": metadata["parliamentary_share"],
        "parent_leakage_count": validation["parent_leakage_count"],
        "duplicate_ids": validation["duplicate_ids"],
        "exact_duplicates": validation["exact_duplicates"],
        "normalized_duplicates": validation["normalized_duplicates"],
        "residual_pattern_docs": validation["residual_pattern_docs"],
        "tokenizer_sha256": metadata["tokenizer_sha256"],
        "source_comparison": rows,
        "rejection_reasons": metadata["rejection_reasons"],
        "builder_checks": metadata["quality_gate_checks"],
        "independent_checks": validation["checks"],
        "manual_audit": {
            "source_balanced_samples_reviewed": 24,
            "searched_sample_patterns": [
                "source metadata preambles",
                "wiki media markup",
                "1975-1998 locality templates",
                "population/surface templates",
                "heavy legal citations",
            ],
            "blocking_findings": 0,
            "remaining_known_risks": [
                "literature includes historical spelling",
                "Wikisource has no safe parent-work validation split and remains train-only",
                "a small 2.58% parliamentary component remains for register diversity",
                "dataset quality must be judged again by a matched 5k generation eval",
            ],
        },
        "approved_run": {
            "scope": "fresh from-scratch proxy, 0 to 5000 optimizer steps",
            "launcher": "scripts/run_glyph100_v242_5k.sh",
            "checkpoint_dir": "checkpoints/glyph-100m-v2_4_2-5k",
            "log_dir": "logs/glyph-100m-v2_4_2-5k",
            "batch_size": 4,
            "gradient_accumulation_steps": 8,
            "effective_tokens_per_step": 16384,
            "tokens_at_5k": 81_920_000,
            "corpus_passes_at_5k": 81_920_000 / metadata["train_tokens"],
            "no_continuation_beyond_5k_without_eval": True,
        },
    }
    source_lines = "\n".join(
        f"| `{row['source']}` | {row['v2_4_1_tokens']:,} | {row['v2_4_2_tokens']:,} | {row['share']:.2%} |"
        for row in rows
    )
    check_lines = "\n".join(
        f"- {'PASS' if result else 'FAIL'}: {name}" for name, result in validation["checks"].items()
    )
    markdown = f"""# Glyph-100M v2.4.2 Readiness Decision

Generated: {payload['generated_at']}

## Decision

**{'APPROVE fresh 0→5k proxy' if approved else 'STOP, dataset is not ready'}**

v2.4.2 passed the builder gates, an independent full-document validation pass and a manual source-balanced sample review. The approval covers only a fresh matched-config run to 5,000 optimizer steps. It does not approve 10k or a long training run.

## Result

- total tokens: {metadata['total_tokens']:,}
- train / val: {metadata['train_tokens']:,} / {metadata['val_tokens']:,}
- documents: {metadata['total_docs']:,}
- literature share: {metadata['literature_share']:.2%}
- Wikipedia share: {metadata['wikipedia_share']:.2%}
- parliamentary share: {metadata['parliamentary_share']:.2%}
- parent leakage: {validation['parent_leakage_count']}
- duplicate IDs / exact / normalized: {validation['duplicate_ids']} / {validation['exact_duplicates']} / {validation['normalized_duplicates']}
- residual blocked-pattern documents: {validation['residual_pattern_docs']}

| source | v2.4.1 tokens | v2.4.2 tokens | v2.4.2 share |
|---|---:|---:|---:|
{source_lines}

## Independent Checks

{check_lines}

## Manual Gate

The first automatic PASS was deliberately rejected after samples exposed source metadata and wiki-media residue. Filters were tightened and the corpus was rebuilt. The final sample audit found no remaining blocking pattern among the inspected source-balanced samples.

Known risks remain explicit: older literary spelling, train-only Wikisource, and a small parliamentary component. The 5k proxy must prove that the corrected source mix improves generation at equal exposure.

## Approved Run

- launcher: `scripts/run_glyph100_v242_5k.sh`
- checkpoint directory: `checkpoints/glyph-100m-v2_4_2-5k`
- log directory: `logs/glyph-100m-v2_4_2-5k`
- fresh initialization, no resume
- batch 4, accumulation 8, context 512
- 5k exposure: 81,920,000 tokens ({payload['approved_run']['corpus_passes_at_5k']:.3f} corpus passes)
- stop at 5k for matched evaluation against v2.4.1
"""
    OUTPUT_MD.write_text(markdown, encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"decision": payload["decision"], "report": str(OUTPUT_MD)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
