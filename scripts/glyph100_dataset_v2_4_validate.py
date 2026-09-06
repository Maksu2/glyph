#!/usr/bin/env python3
"""Independently validate v2.4.1 binaries, metadata, split and samples."""

from __future__ import annotations

import argparse
import collections
import heapq
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from glyph100_dataset_v2_4_build import WEB_RESIDUE_RE, WIKI_MARKUP_RE, stable_priority, write_jsonl  # noqa: E402
from glyph100_dataset_v2_filter import truncate_text  # noqa: E402


DEFAULT_METADATA = ROOT / "data/processed/glyph100_v2_4_1_metadata.json"
DEFAULT_JSON = ROOT / "reports/glyph100_next_step_20260716_v2_4_1_validation.json"
DEFAULT_MD = ROOT / "reports/glyph100_next_step_20260716_v2_4_1_validation.md"
DEFAULT_SAMPLES = ROOT / "reports/glyph100_next_step_20260716_v2_4_1_samples.json"
PSEUDO_ENCY_RE = re.compile(
    r"\bw latach 1975[–-]1998\b|\bgminie\b|\bpowiecie\b|\bwojewództwie\b",
    re.IGNORECASE,
)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def heap_sample(heap: list[tuple[int, str, dict[str, Any]]], record: dict[str, Any], prefix: str, limit: int) -> None:
    record_id = str(record.get("id") or "")
    priority = stable_priority(f"{prefix}:{record_id}")
    payload = {
        "id": record_id,
        "source": record.get("source"),
        "parent_doc_id": record.get("parent_doc_id"),
        "split": (record.get("meta") or {}).get("split"),
        "token_count": int((record.get("meta") or {}).get("token_count") or 0),
        "quality_score": record.get("quality_score"),
        "audit_flags": record.get("_audit_flags", []),
        "text": truncate_text(str(record.get("text") or ""), 1600),
    }
    item = (-priority, record_id, payload)
    if len(heap) < limit:
        heapq.heappush(heap, item)
    elif priority < -heap[0][0]:
        heapq.heapreplace(heap, item)


def ordered_samples(heap: list[tuple[int, str, dict[str, Any]]]) -> list[dict[str, Any]]:
    return [item[2] for item in sorted(heap, key=lambda item: (-item[0], item[1]))]


def render_markdown(payload: dict[str, Any]) -> str:
    rows = []
    for source, item in payload["observed_sources"].items():
        rows.append(
            f"| `{source}` | {item['docs']:,} | {item['tokens']:,} | {item['tokens'] / payload['observed_total_tokens']:.1%} | "
            f"{item['train_tokens']:,} | {item['val_tokens']:,} |"
        )
    checks = "\n".join(f"- {'PASS' if value else 'FAIL'}: {name}" for name, value in payload["checks"].items())
    return f"""# Glyph-100M v2.4.1 Independent Validation

Generated: {payload['generated_at']}

## Verdict

{payload['verdict']}

## Checks

{checks}

## Independently Observed

- docs: {payload['observed_docs']:,}
- parent docs: {payload['observed_parents']:,}
- tokens: {payload['observed_total_tokens']:,}
- train tokens: {payload['observed_train_tokens']:,}
- validation tokens: {payload['observed_val_tokens']:,}
- duplicate IDs: {payload['duplicate_ids']}
- parent split leakage: {payload['parent_leakage_count']}
- web-residue heuristic hits: {payload['web_residue_hits']:,}
- wiki-markup heuristic hits: {payload['wiki_markup_hits']:,}
- pseudo-ency phrase hits: {payload['pseudo_ency_hits']:,}

Heuristic hits by source:

```json
{json.dumps(payload['heuristic_hits_by_source'], ensure_ascii=False, indent=2)}
```

| source | docs | tokens | share | train tokens | val tokens |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

## Interpretation

The residue counters are conservative search heuristics, not automatic quality failures. Every matching sample is retained in the JSON audit for manual inspection. Binary sizes, metadata counts and the parent split are hard gates.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES)
    args = parser.parse_args()

    metadata_path = args.metadata.resolve()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    docs_path = ROOT / metadata["docs_jsonl"]
    train_path = ROOT / metadata["train_bin"]
    val_path = ROOT / metadata["val_bin"]

    ids: set[str] = set()
    duplicate_ids = 0
    parent_splits: dict[str, str] = {}
    leakage: set[str] = set()
    source_stats: dict[str, dict[str, int]] = collections.defaultdict(
        lambda: {"docs": 0, "tokens": 0, "train_tokens": 0, "val_tokens": 0, "train_docs": 0, "val_docs": 0}
    )
    random_heap: list[tuple[int, str, dict[str, Any]]] = []
    source_heaps: dict[str, list[tuple[int, str, dict[str, Any]]]] = collections.defaultdict(list)
    suspicious_heaps: dict[str, list[tuple[int, str, dict[str, Any]]]] = collections.defaultdict(list)
    heuristic_hits_by_source: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    observed_docs = observed_tokens = train_tokens = val_tokens = 0
    web_hits = wiki_hits = pseudo_hits = 0

    with docs_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            observed_docs += 1
            record_id = str(record.get("id") or "")
            if record_id in ids:
                duplicate_ids += 1
            ids.add(record_id)
            source = str(record.get("source") or "")
            meta = record.get("meta") or {}
            split = str(meta.get("split") or "")
            tokens = int(meta.get("token_count") or 0)
            parent = str(record.get("parent_doc_id") or record.get("doc_id") or record_id)
            parent_key = f"{source}:{parent}"
            previous = parent_splits.setdefault(parent_key, split)
            if previous != split:
                leakage.add(parent_key)
            observed_tokens += tokens
            state = source_stats[source]
            state["docs"] += 1
            state["tokens"] += tokens
            if split == "train":
                train_tokens += tokens
                state["train_tokens"] += tokens
                state["train_docs"] += 1
            elif split == "val":
                val_tokens += tokens
                state["val_tokens"] += tokens
                state["val_docs"] += 1
            text = str(record.get("text") or "")
            flags = []
            if WEB_RESIDUE_RE.search(text):
                web_hits += 1
                flags.append("web_residue")
                heuristic_hits_by_source[source]["web_residue"] += 1
            if WIKI_MARKUP_RE.search(text):
                wiki_hits += 1
                flags.append("wiki_markup")
                heuristic_hits_by_source[source]["wiki_markup"] += 1
            if PSEUDO_ENCY_RE.search(text):
                pseudo_hits += 1
                flags.append("pseudo_ency_phrase")
                heuristic_hits_by_source[source]["pseudo_ency_phrase"] += 1
            if flags:
                audit_record = dict(record)
                audit_record["_audit_flags"] = flags
                for flag in flags:
                    heap_sample(suspicious_heaps[f"{source}:{flag}"], audit_record, f"audit:{source}:{flag}", 5)
            heap_sample(random_heap, record, "global", 50)
            heap_sample(source_heaps[source], record, f"source:{source}", 5)

    checks = {
        "metadata token total matches docs JSONL": observed_tokens == int(metadata["total_tokens"]),
        "metadata train tokens match docs JSONL": train_tokens == int(metadata["train_tokens"]),
        "metadata val tokens match docs JSONL": val_tokens == int(metadata["val_tokens"]),
        "train binary byte size equals uint16 token count": train_path.stat().st_size == train_tokens * 2,
        "val binary byte size equals uint16 token count": val_path.stat().st_size == val_tokens * 2,
        "metadata document count matches docs JSONL": observed_docs == int(metadata["total_docs"]),
        "document IDs are unique": duplicate_ids == 0,
        "parent documents do not cross train and val": not leakage,
        "minimum token floor is met": observed_tokens >= int(metadata["minimum_ready_tokens"]),
    }
    all_pass = all(checks.values())
    samples = {
        "global_random": ordered_samples(random_heap),
        "source_balanced": {source: ordered_samples(heap) for source, heap in sorted(source_heaps.items())},
        "suspicious_matches": {
            key: ordered_samples(heap) for key, heap in sorted(suspicious_heaps.items())
        },
    }
    payload: dict[str, Any] = {
        "generated_at": now_utc(),
        "dataset_name": metadata["dataset_name"],
        "verdict": (
            "PASS: v2.4.1 is mechanically valid and ready for a controlled 1k/5k proxy, not an automatic long run."
            if all_pass
            else "FAIL: one or more hard corpus consistency gates failed. Do not train."
        ),
        "checks": checks,
        "observed_docs": observed_docs,
        "observed_parents": len(parent_splits),
        "observed_total_tokens": observed_tokens,
        "observed_train_tokens": train_tokens,
        "observed_val_tokens": val_tokens,
        "duplicate_ids": duplicate_ids,
        "parent_leakage_count": len(leakage),
        "parent_leakage_examples": sorted(leakage)[:20],
        "web_residue_hits": web_hits,
        "wiki_markup_hits": wiki_hits,
        "pseudo_ency_hits": pseudo_hits,
        "heuristic_hits_by_source": {
            source: dict(counts) for source, counts in sorted(heuristic_hits_by_source.items())
        },
        "observed_sources": {name: dict(item) for name, item in sorted(source_stats.items())},
        "samples_file": str(args.samples.resolve()),
        "all_hard_checks_pass": all_pass,
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(render_markdown(payload), encoding="utf-8")
    args.samples.write_text(json.dumps(samples, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_jsonl(ROOT / "data/reports/glyph100_dataset_v2_4_1_samples_final_random.jsonl", samples["global_random"])
    print(json.dumps({"all_hard_checks_pass": all_pass, "checks": checks, "web_residue_hits": web_hits, "wiki_markup_hits": wiki_hits, "pseudo_ency_hits": pseudo_hits}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
