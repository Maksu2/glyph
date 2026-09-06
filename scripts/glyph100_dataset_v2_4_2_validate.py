#!/usr/bin/env python3
"""Independently validate the corrective Glyph-100M v2.4.2 corpus."""

from __future__ import annotations

import argparse
import collections
import hashlib
import heapq
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from glyph100_dataset_v2_4_build import stable_priority  # noqa: E402
from glyph100_dataset_v2_4_2_build import (  # noqa: E402
    LITERATURE_SOURCES,
    rejection_reasons,
)
from glyph100_dataset_v2_filter import normalize_for_hash, sha1_text, truncate_text  # noqa: E402


DEFAULT_METADATA = ROOT / "data/processed/glyph100_v2_4_2_metadata.json"
DEFAULT_JSON = ROOT / "reports/glyph100_v2_4_2_validation.json"
DEFAULT_MD = ROOT / "reports/glyph100_v2_4_2_validation.md"
DEFAULT_SAMPLES = ROOT / "reports/glyph100_v2_4_2_validation_samples.json"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def heap_sample(
    heap: list[tuple[int, str, dict[str, Any]]],
    record: dict[str, Any],
    prefix: str,
    limit: int,
    flags: list[str] | None = None,
) -> None:
    record_id = str(record.get("id") or "")
    priority = stable_priority(f"{prefix}:{record_id}")
    payload = {
        "id": record_id,
        "source": record.get("source"),
        "parent_doc_id": record.get("parent_doc_id"),
        "split": (record.get("meta") or {}).get("split"),
        "token_count": int((record.get("meta") or {}).get("token_count") or 0),
        "quality_score": record.get("quality_score"),
        "audit_flags": flags or [],
        "text": truncate_text(str(record.get("text") or ""), 1800),
    }
    item = (-priority, record_id, payload)
    if len(heap) < limit:
        heapq.heappush(heap, item)
    elif priority < -heap[0][0]:
        heapq.heapreplace(heap, item)


def ordered(heap: list[tuple[int, str, dict[str, Any]]]) -> list[dict[str, Any]]:
    return [item[2] for item in sorted(heap, key=lambda item: (-item[0], item[1]))]


def render_markdown(payload: dict[str, Any]) -> str:
    checks = "\n".join(
        f"- {'PASS' if result else 'FAIL'}: {name}" for name, result in payload["checks"].items()
    )
    rows = []
    for source, item in payload["sources"].items():
        rows.append(
            f"| `{source}` | {item['docs']:,} | {item['tokens']:,} | "
            f"{item['tokens'] / payload['total_tokens']:.2%} | "
            f"{item['train_tokens']:,} | {item['val_tokens']:,} |"
        )
    return f"""# Glyph-100M v2.4.2 Independent Validation

Generated: {payload['generated_at']}

## Verdict

{payload['verdict']}

## Hard Checks

{checks}

## Observed Corpus

- documents: {payload['docs']:,}
- parent documents: {payload['parents']:,}
- train tokens: {payload['train_tokens']:,}
- validation tokens: {payload['val_tokens']:,}
- total tokens: {payload['total_tokens']:,}
- literature share: {payload['literature_share']:.2%}
- Wikipedia share: {payload['wikipedia_share']:.2%}
- parliamentary share: {payload['parliamentary_share']:.2%}
- duplicate IDs: {payload['duplicate_ids']}
- exact text duplicates: {payload['exact_duplicates']}
- normalized text duplicates: {payload['normalized_duplicates']}
- parent leakage: {payload['parent_leakage_count']}
- residual rejected-pattern documents: {payload['residual_pattern_docs']}

| source | docs | tokens | share | train tokens | val tokens |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

## Residual Pattern Audit

```json
{json.dumps(payload['residual_patterns'], ensure_ascii=False, indent=2)}
```

The JSON companion contains 50 deterministic global samples, source-balanced samples and every residual pattern category found by the audit.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.resolve().read_text(encoding="utf-8"))
    docs_path = ROOT / metadata["docs_jsonl"]
    train_path = ROOT / metadata["train_bin"]
    val_path = ROOT / metadata["val_bin"]
    tokenizer_path = ROOT / metadata["tokenizer"]

    source_stats: dict[str, dict[str, int]] = collections.defaultdict(
        lambda: {"docs": 0, "tokens": 0, "train_tokens": 0, "val_tokens": 0}
    )
    ids: set[str] = set()
    exact: set[str] = set()
    normalized: set[str] = set()
    duplicate_ids = exact_duplicates = normalized_duplicates = 0
    parent_splits: dict[str, str] = {}
    leakage: set[str] = set()
    residual_patterns = collections.Counter()
    random_heap: list[tuple[int, str, dict[str, Any]]] = []
    source_heaps: dict[str, list[tuple[int, str, dict[str, Any]]]] = collections.defaultdict(list)
    residual_heaps: dict[str, list[tuple[int, str, dict[str, Any]]]] = collections.defaultdict(list)
    docs = train_tokens = val_tokens = 0

    with docs_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            docs += 1
            record_id = str(record.get("id") or "")
            if record_id in ids:
                duplicate_ids += 1
            ids.add(record_id)
            text = str(record.get("text") or "")
            exact_hash = sha1_text(text)
            normalized_hash = sha1_text(normalize_for_hash(text))
            if exact_hash in exact:
                exact_duplicates += 1
            if normalized_hash in normalized:
                normalized_duplicates += 1
            exact.add(exact_hash)
            normalized.add(normalized_hash)

            source = str(record.get("source") or "")
            meta = record.get("meta") or {}
            split = str(meta.get("split") or "")
            tokens = int(meta.get("token_count") or 0)
            parent = str(record.get("parent_doc_id") or record.get("doc_id") or record_id)
            parent_key = f"{source}:{parent}"
            previous = parent_splits.setdefault(parent_key, split)
            if previous != split:
                leakage.add(parent_key)
            state = source_stats[source]
            state["docs"] += 1
            state["tokens"] += tokens
            if split == "train":
                train_tokens += tokens
                state["train_tokens"] += tokens
            elif split == "val":
                val_tokens += tokens
                state["val_tokens"] += tokens
            else:
                residual_patterns["invalid_split"] += 1

            flags = rejection_reasons(source, text)
            for flag in flags:
                residual_patterns[flag] += 1
                heap_sample(residual_heaps[flag], record, f"residual:{flag}", 10, flags)
            heap_sample(random_heap, record, "global", 50)
            heap_sample(source_heaps[source], record, f"source:{source}", 10)

    total_tokens = train_tokens + val_tokens
    literature_tokens = sum(source_stats[source]["tokens"] for source in LITERATURE_SOURCES)
    wikipedia_tokens = source_stats["wikipedia_pl"]["tokens"]
    parliamentary_tokens = source_stats["parliamentary"]["tokens"]
    build_checks = metadata["quality_gate_checks"]
    checks = {
        "dataset identity": metadata["dataset_name"] == "glyph100_dataset_v2_4_2_core",
        "metadata total matches docs": total_tokens == int(metadata["total_tokens"]),
        "metadata train matches docs": train_tokens == int(metadata["train_tokens"]),
        "metadata val matches docs": val_tokens == int(metadata["val_tokens"]),
        "metadata docs match": docs == int(metadata["total_docs"]),
        "train binary size": train_path.stat().st_size == train_tokens * 2,
        "validation binary size": val_path.stat().st_size == val_tokens * 2,
        "tokenizer checksum": file_sha256(tokenizer_path) == metadata["tokenizer_sha256"],
        "minimum token floor": total_tokens >= int(metadata["minimum_ready_tokens"]),
        "literature share": literature_tokens / total_tokens >= 0.52,
        "Wikipedia share": wikipedia_tokens / total_tokens <= 0.42,
        "parliamentary share": parliamentary_tokens / total_tokens <= 0.03,
        "unique document IDs": duplicate_ids == 0,
        "no exact duplicates": exact_duplicates == 0,
        "no normalized duplicates": normalized_duplicates == 0,
        "no parent leakage": not leakage,
        "no residual rejected patterns": not residual_patterns,
        "builder gates passed": all(build_checks.values()),
        "all validation sources represented": all(
            item["val_tokens"] > 0 for source, item in source_stats.items() if source != "wikisource"
        ),
        "Wikisource remains train-only": source_stats["wikisource"]["val_tokens"] == 0,
    }
    ready = all(checks.values())
    payload: dict[str, Any] = {
        "generated_at": now_utc(),
        "dataset_name": metadata["dataset_name"],
        "verdict": (
            "PASS: v2.4.2 is mechanically and compositionally ready for one fresh 5k matched proxy."
            if ready
            else "FAIL: v2.4.2 has a failed consistency or quality gate. Do not train."
        ),
        "ready_for_5k_proxy": ready,
        "checks": checks,
        "docs": docs,
        "parents": len(parent_splits),
        "train_tokens": train_tokens,
        "val_tokens": val_tokens,
        "total_tokens": total_tokens,
        "literature_share": literature_tokens / total_tokens,
        "wikipedia_share": wikipedia_tokens / total_tokens,
        "parliamentary_share": parliamentary_tokens / total_tokens,
        "duplicate_ids": duplicate_ids,
        "exact_duplicates": exact_duplicates,
        "normalized_duplicates": normalized_duplicates,
        "parent_leakage_count": len(leakage),
        "parent_leakage_examples": sorted(leakage)[:20],
        "residual_pattern_docs": sum(residual_patterns.values()),
        "residual_patterns": dict(residual_patterns),
        "sources": {source: dict(item) for source, item in sorted(source_stats.items())},
        "samples_file": str(args.samples.resolve()),
    }
    samples = {
        "global_random": ordered(random_heap),
        "source_balanced": {source: ordered(heap) for source, heap in sorted(source_heaps.items())},
        "residual_patterns": {name: ordered(heap) for name, heap in sorted(residual_heaps.items())},
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(render_markdown(payload), encoding="utf-8")
    args.samples.write_text(json.dumps(samples, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ready_for_5k_proxy": ready, "checks": checks}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
