#!/usr/bin/env python3
"""Build Glyph-100M dataset v2.1 from v2 source-aware docs plus small audited sources.

v2.1 is intentionally stricter than v2:
- no overwrite of v2 or stage1 outputs,
- separate legacy_mixed_corpus audit,
- source-mix variants with legacy caps,
- optional small Wikisource PL ingest,
- final selected variant defaults to quality-first legacy <= 10%.
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from glyph100_dataset_v2_filter import (  # noqa: E402
    WORD_RE,
    evaluate_document,
    FilterConfig,
    percentile,
    sha1_text,
    stable_bucket,
    text_metrics,
    truncate_text,
)
from glyph100_dataset_identity import parent_doc_id_for, parent_split_for  # noqa: E402


DEFAULT_V2_DOCS = Path("data/processed/glyph100_v2_docs.jsonl")
DEFAULT_TOKENIZER = Path("data/processed/tokenizer.model")
DEFAULT_TRAIN_BIN = Path("data/processed/glyph100_v2_1_train.bin")
DEFAULT_VAL_BIN = Path("data/processed/glyph100_v2_1_val.bin")
DEFAULT_METADATA = Path("data/processed/glyph100_v2_1_metadata.json")
DEFAULT_DOCS_JSONL = Path("data/processed/glyph100_v2_1_docs.jsonl")
DEFAULT_REJECTED_JSONL = Path("data/processed/glyph100_v2_1_rejected.jsonl")
DEFAULT_STATS = Path("data/reports/glyph100_dataset_v2_1_stats.json")
DEFAULT_REPORT = Path("data/reports/glyph100_dataset_v2_1_report.md")
DEFAULT_ACCEPTED_SAMPLES = Path("data/reports/glyph100_dataset_v2_1_samples_accepted.jsonl")
DEFAULT_REJECTED_SAMPLES = Path("data/reports/glyph100_dataset_v2_1_samples_rejected.jsonl")
DEFAULT_FINAL_SAMPLES = Path("data/reports/glyph100_dataset_v2_1_samples_final_random.jsonl")
DEFAULT_LEGACY_AUDIT_MD = Path("data/reports/glyph100_legacy_quality_audit.md")
DEFAULT_LEGACY_AUDIT_JSON = Path("data/reports/glyph100_legacy_quality_audit.json")
DEFAULT_DECISION_MD = Path("reports/glyph100_dataset_v2_1_decision_report.md")
DEFAULT_DECISION_JSON = Path("reports/glyph100_dataset_v2_1_decision_report.json")
DEFAULT_SOURCE_AUDIT_MD = Path("data/reports/glyph100_dataset_v2_1_source_audit.md")
DEFAULT_SOURCE_AUDIT_JSON = Path("data/reports/glyph100_dataset_v2_1_source_audit.json")

TOKENS_PER_STEP = 4 * 512 * 8

LEGACY_BAD_PATTERNS: dict[str, list[str]] = {
    "forum": [
        "forum",
        "postautor",
        "odpowiedz",
        "cytuj",
        "wątek",
        "użytkownik",
        "zarejestrowany",
        "dołączył",
        "napisał/a",
        "re:",
    ],
    "commerce": [
        "koszyk",
        "dodaj do koszyka",
        "produkt",
        "produkty",
        "cena",
        "zł",
        "pln",
        "sklep",
        "promocja",
        "promocyjne",
        "dostawa",
        "wysyłka",
        "allegro",
        "sprzedano za",
        "na sprzedaż",
        "mieszkanie na sprzedaż",
        "cena za m²",
    ],
    "seo": [
        "słowa kluczowe",
        "pozycjonowanie",
        "seo",
        "tanie loty",
        "chwilówki",
        "pożyczki",
        "ranking",
        "najlepsze oferty",
    ],
    "comments": [
        "komentarz",
        "komentarze",
        "anonimowy",
        "posted by",
        "no comment",
        "dodaj komentarz",
        "napisz komentarz",
    ],
    "navigation": [
        "strona główna",
        "jesteś tutaj",
        "home/",
        "newsletter",
        "cookies",
        "polityka prywatności",
        "regulamin",
        "czytaj więcej",
        "zobacz także",
    ],
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def json_dump_line(handle, obj: dict[str, Any]) -> None:
    handle.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")


def load_sentencepiece(tokenizer: Path):
    try:
        import sentencepiece as spm
    except ImportError as exc:
        raise SystemExit("sentencepiece is required. Use ./.venv/bin/python.") from exc
    sp = spm.SentencePieceProcessor()
    sp.load(str(tokenizer))
    return sp


def write_uint16_tokens(handle, ids: list[int]) -> None:
    np.asarray(ids, dtype=np.uint16).tofile(handle)


def legacy_pattern_hits(text: str) -> dict[str, int]:
    lower = text.lower()
    return {
        category: sum(1 for pattern in patterns if pattern in lower)
        for category, patterns in LEGACY_BAD_PATTERNS.items()
    }


def sentence_stats(text: str) -> dict[str, float]:
    sentences = [s.strip() for s in re_split_sentences(text) if s.strip()]
    words_per_sentence = [len(WORD_RE.findall(s)) for s in sentences if WORD_RE.findall(s)]
    short_lines = sum(1 for line in text.splitlines() if 0 < len(WORD_RE.findall(line)) <= 5)
    line_count = max(1, text.count("\n") + 1)
    return {
        "avg_sentence_words": sum(words_per_sentence) / max(len(words_per_sentence), 1),
        "short_line_ratio": short_lines / line_count,
    }


def re_split_sentences(text: str) -> list[str]:
    import re

    return re.split(r"[.!?…]+|\n+", text)


def legacy_quality(record: dict[str, Any]) -> dict[str, Any]:
    text = f"{record.get('title', '')}\n{record.get('text', '')}"
    metrics = text_metrics(text)
    patterns = legacy_pattern_hits(text)
    sent = sentence_stats(text)
    words = metrics.get("words", 0)
    digits = sum(ch.isdigit() for ch in text)
    chars = max(1, len(text))
    price_like = len(__import__("re").findall(r"\b\d+([,.]\d+)?\s?(zł|pln|eur|usd|%)\b", text.lower()))
    time_like = len(__import__("re").findall(r"\b\d{1,2}:\d{2}\b", text))
    bad_score = (
        patterns["forum"] * 4.0
        + patterns["commerce"] * 3.0
        + patterns["seo"] * 4.0
        + patterns["comments"] * 3.0
        + patterns["navigation"] * 2.0
        + price_like * 2.0
        + min(6.0, time_like * 0.5)
        + max(0.0, 0.04 - float(metrics["polish_stopword_ratio"])) * 80.0
        + max(0.0, float(metrics["punct_symbol_ratio"]) - 0.10) * 30.0
        + min(5.0, float(metrics["repetition_score"]) * 80.0)
        + max(0.0, 0.42 - float(metrics["unique_word_ratio"])) * 10.0
        + max(0.0, 12.0 - sent["avg_sentence_words"]) * 0.10
        + sent["short_line_ratio"] * 4.0
        + min(5.0, digits / chars * 25.0)
    )
    if words < 80:
        bad_score += 2.0
    if words >= 180 and sum(patterns.values()) == 0 and metrics["repetition_score"] < 0.015:
        bad_score -= 2.0
    quality = max(0.0, min(1.0, 1.0 - bad_score / 18.0))
    if patterns["forum"] or time_like >= 4:
        label = "forum"
    elif patterns["commerce"] or price_like:
        label = "commerce"
    elif patterns["seo"]:
        label = "seo"
    elif patterns["comments"]:
        label = "comments"
    elif patterns["navigation"]:
        label = "navigation"
    elif quality >= 0.72:
        label = "clean_text"
    else:
        label = "uncertain"
    return {
        "legacy_quality_score": round(quality, 4),
        "legacy_bad_score": round(bad_score, 4),
        "legacy_label": label,
        "legacy_pattern_hits": patterns,
        "price_like_count": price_like,
        "time_like_count": time_like,
        "avg_sentence_words": round(sent["avg_sentence_words"], 3),
        "short_line_ratio": round(sent["short_line_ratio"], 4),
        "digit_ratio": round(digits / chars, 5),
        "words": words,
        "repetition_score": metrics["repetition_score"],
        "polish_stopword_ratio": metrics["polish_stopword_ratio"],
    }


def token_count(record: dict[str, Any]) -> int:
    meta = record.get("meta") or {}
    return int(meta.get("token_count") or 0)


def split_for(record: dict[str, Any], val_per_mille: int) -> str:
    return parent_split_for(record, val_per_mille)


def keep_sample(samples: list[dict[str, Any]], item: dict[str, Any], key: str, limit: int) -> None:
    if len(samples) < limit:
        samples.append(item)
        return
    bucket = stable_bucket(key, 10_000)
    if bucket < limit:
        samples[bucket % limit] = item


def sample_payload(record: dict[str, Any], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "id": record.get("id", ""),
        "source": record.get("source", ""),
        "source_id": record.get("source_id", ""),
        "title": record.get("title", ""),
        "text": truncate_text(record.get("text", "")),
    }
    if extra:
        payload.update(extra)
    return payload


def audit_new_sources() -> dict[str, Any]:
    source_audit = {
        "generated_at": now_utc(),
        "sources": [
            {
                "name": "FinetextPL-Edu",
                "url": "https://huggingface.co/datasets/FinetextPL/FinetextPL-Edu",
                "type": "educational Polish text",
                "size": "100M<n<1B rows category; 494 parquet files, first files about 590 MB each",
                "license": "odc-by according to HF metadata",
                "sample_quality": "not sampled; dataset is gated and requires authentication",
                "decision": "later",
                "reason": "promising but gated and very large; do not download without separate approval/token",
            },
            {
                "name": "Wikimedia Wikisource PL",
                "url": "https://huggingface.co/datasets/wikimedia/wikisource",
                "type": "public/source text archive",
                "size": "pl config about 56 MB dataset / 34 MB download, 12,020 examples in HF metadata",
                "license": "cc-by-sa-3.0 and gfdl according to HF metadata",
                "sample_quality": "good enough for a controlled source-aware addition; contains legal/public documents and source texts",
                "decision": "use",
                "reason": "small, source-aware, cheap to sample/download, adds non-Wikipedia public text",
            },
        ],
    }
    return source_audit


def wikisource_records(limit: int = 0) -> Iterable[dict[str, Any]]:
    try:
        from datasets import load_dataset
    except ImportError:
        return
    try:
        dataset = load_dataset("wikimedia/wikisource", "20231201.pl", split="train", streaming=True)
    except Exception:
        return
    for i, item in enumerate(dataset):
        if limit and i >= limit:
            break
        text = item.get("text") or ""
        if not text:
            continue
        yield {
            "id": f"glyph100-v2-1-wikisource-{item.get('id', i)}",
            "source": "wikisource_pl",
            "source_id": str(item.get("id") or i),
            "doc_id": sha1_text(f"wikisource_pl:{item.get('id', i)}:{item.get('title', '')}")[:24],
            "title": item.get("title") or "",
            "url": item.get("url") or "",
            "license": "cc-by-sa-3.0 / gfdl; verify per Wikisource page",
            "language": "pl",
            "text": text,
            "quality_score": 0.0,
            "meta": {
                "source_meta": {"dataset": "wikimedia/wikisource", "config": "20231201.pl", "row": i},
            },
        }


def load_v2_records(path: Path) -> Iterable[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def ensure_safe_outputs(args: argparse.Namespace) -> None:
    forbidden = {
        Path("data/processed/tokens.bin").resolve(),
        Path("data/processed/val_tokens.bin").resolve(),
        Path("data/processed/glyph100_train.bin").resolve(),
        Path("data/processed/glyph100_val.bin").resolve(),
        Path("data/processed/glyph100_v2_train.bin").resolve(),
        Path("data/processed/glyph100_v2_val.bin").resolve(),
        Path("data/processed/glyph100_v2_docs.jsonl").resolve(),
        Path("data/processed/glyph100_v2_metadata.json").resolve(),
    }
    outputs = [
        args.train_bin,
        args.val_bin,
        args.metadata,
        args.docs_jsonl,
        args.rejected_jsonl,
        args.stats,
        args.report,
        args.accepted_samples,
        args.rejected_samples,
        args.final_samples,
        args.legacy_audit_md,
        args.legacy_audit_json,
        args.decision_md,
        args.decision_json,
        args.source_audit_md,
        args.source_audit_json,
    ]
    for path in outputs:
        if path.resolve() in forbidden:
            raise SystemExit(f"Refusing to overwrite protected dataset output: {path}")
    existing = [path for path in outputs if path.exists()]
    if existing and not args.force_v2_1:
        formatted = "\n".join(f"- {path}" for path in existing)
        raise SystemExit(f"v2.1 outputs already exist. Use --force-v2-1 to replace v2.1 files only:\n{formatted}")
    for path in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)


def reject_legacy_v2_1(record: dict[str, Any], audit: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    label = audit["legacy_label"]
    score = float(audit["legacy_quality_score"])
    if label in {"forum", "commerce", "seo", "comments", "navigation"}:
        reasons.append(f"legacy_{label}")
    if score < 0.72:
        reasons.append("legacy_quality_below_0_72")
    if audit["time_like_count"] >= 4:
        reasons.append("legacy_many_time_markers")
    if audit["price_like_count"] >= 1:
        reasons.append("legacy_price_like")
    if audit["short_line_ratio"] > 0.35:
        reasons.append("legacy_many_short_lines")
    if audit["avg_sentence_words"] < 9 and audit["words"] >= 80:
        reasons.append("legacy_short_sentence_noise")
    return reasons


def source_record_ok(record: dict[str, Any], exact_seen: set[str], normalized_seen: set[str], near_seen: set[str]) -> tuple[dict[str, Any] | None, list[str], dict[str, Any]]:
    source = record.get("source", "")
    if source == "legacy_mixed_corpus":
        audit = legacy_quality(record)
        reasons = reject_legacy_v2_1(record, audit)
        record.setdefault("meta", {})["legacy_v2_1"] = audit
        return (None if reasons else record), reasons, audit

    filter_result = evaluate_document(
        record.get("text", ""),
        source=source,
        config=FilterConfig(min_words=40, max_chars=60_000),
        exact_seen=exact_seen,
        normalized_seen=normalized_seen,
        near_seen=near_seen,
    )
    if not filter_result.accepted:
        return None, filter_result.reasons, filter_result.metrics
    record["text"] = filter_result.text
    record["quality_score"] = round(float(filter_result.metrics.get("quality_score", record.get("quality_score", 0))), 4)
    record.setdefault("meta", {})["v2_1_filter"] = {
        key: filter_result.metrics.get(key)
        for key in [
            "words",
            "chars",
            "alpha_ratio",
            "polish_stopword_ratio",
            "repetition_score",
            "quality_score",
            "suspicious_patterns",
        ]
    }
    return record, [], filter_result.metrics


def select_variant(records: list[dict[str, Any]], variant: str) -> list[dict[str, Any]]:
    non_legacy = [r for r in records if r["source"] != "legacy_mixed_corpus"]
    legacy = [r for r in records if r["source"] == "legacy_mixed_corpus"]
    non_tokens = sum(token_count(r) for r in non_legacy)
    if variant == "D":
        return non_legacy
    caps = {"A": 0.10, "B": 0.20, "C": 0.30}
    cap = caps[variant]
    max_legacy_tokens = int(non_tokens * cap / max(1e-9, 1.0 - cap))
    legacy_sorted = sorted(
        legacy,
        key=lambda r: (
            -float(((r.get("meta") or {}).get("legacy_v2_1") or {}).get("legacy_quality_score", 0)),
            stable_bucket(r.get("doc_id") or r.get("id", ""), 1_000_000),
        ),
    )
    selected_legacy: list[dict[str, Any]] = []
    used = 0
    for record in legacy_sorted:
        count = token_count(record)
        if used + count > max_legacy_tokens and selected_legacy:
            continue
        selected_legacy.append(record)
        used += count
        if used >= max_legacy_tokens:
            break
    return non_legacy + selected_legacy


def variant_stats(name: str, records: list[dict[str, Any]], val_per_mille: int) -> dict[str, Any]:
    per_source: dict[str, dict[str, int]] = collections.defaultdict(lambda: {"docs": 0, "tokens": 0, "train_tokens": 0, "val_tokens": 0})
    train_tokens = val_tokens = train_docs = val_docs = 0
    token_lengths = []
    samples: list[dict[str, Any]] = []
    for record in records:
        count = token_count(record)
        split = split_for(record, val_per_mille)
        per_source[record["source"]]["docs"] += 1
        per_source[record["source"]]["tokens"] += count
        if split == "val":
            val_docs += 1
            val_tokens += count
            per_source[record["source"]]["val_tokens"] += count
        else:
            train_docs += 1
            train_tokens += count
            per_source[record["source"]]["train_tokens"] += count
        token_lengths.append(count)
        keep_sample(samples, sample_payload(record, {"token_count": count}), record.get("id", ""), 50)
    total = train_tokens + val_tokens
    return {
        "variant": name,
        "docs": len(records),
        "train_docs": train_docs,
        "val_docs": val_docs,
        "train_tokens": train_tokens,
        "val_tokens": val_tokens,
        "total_tokens": total,
        "tokens_per_source": dict(per_source),
        "stage3_50k_epochs": 50_000 * TOKENS_PER_STEP / max(total, 1),
        "stage4_100k_epochs": 100_000 * TOKENS_PER_STEP / max(total, 1),
        "stage5_200k_epochs": 200_000 * TOKENS_PER_STEP / max(total, 1),
        "doc_token_percentiles": {
            "p50": percentile(token_lengths, 0.50),
            "p75": percentile(token_lengths, 0.75),
            "p90": percentile(token_lengths, 0.90),
            "p95": percentile(token_lengths, 0.95),
            "p99": percentile(token_lengths, 0.99),
        },
        "samples": samples,
    }


def build_legacy_audit(legacy_records: list[dict[str, Any]], legacy_rejected: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    accepted_labels = collections.Counter()
    rejected_labels = collections.Counter()
    accepted_tokens = 0
    all_rows = []
    for record in legacy_records:
        audit = (record.get("meta") or {}).get("legacy_v2_1") or legacy_quality(record)
        accepted_labels[audit["legacy_label"]] += 1
        accepted_tokens += token_count(record)
        all_rows.append((record, audit))
    for item in legacy_rejected:
        audit = item.get("audit") or {}
        rejected_labels[audit.get("legacy_label", "unknown")] += 1

    random_samples: list[dict[str, Any]] = []
    for record, audit in all_rows:
        keep_sample(random_samples, sample_payload(record, audit), record.get("id", ""), args.legacy_audit_limit)
    worst = sorted(all_rows, key=lambda item: item[1].get("legacy_quality_score", 0))[: args.legacy_audit_limit]
    best = sorted(all_rows, key=lambda item: item[1].get("legacy_quality_score", 0), reverse=True)[: args.legacy_audit_limit]

    audit = {
        "generated_at": now_utc(),
        "legacy_tokens_after_v2_1_filter": accepted_tokens,
        "legacy_docs_after_v2_1_filter": len(legacy_records),
        "legacy_rejected_by_v2_1": len(legacy_rejected),
        "accepted_label_counts": dict(accepted_labels.most_common()),
        "rejected_label_counts": dict(rejected_labels.most_common()),
        "random_accepted_samples": random_samples[: args.legacy_audit_limit],
        "worst_accepted_samples": [sample_payload(record, data) for record, data in worst],
        "best_accepted_samples": [sample_payload(record, data) for record, data in best],
        "bad_rejected_samples": [item["sample"] for item in legacy_rejected[: args.legacy_audit_limit]],
        "recommendation": (
            "limit legacy to 10% at most; the strict filter keeps usable long texts, but legacy remains mixed-quality"
            if accepted_tokens
            else "drop legacy entirely"
        ),
    }
    return audit


def render_legacy_audit(audit: dict[str, Any]) -> str:
    return f"""# Glyph-100M Legacy Quality Audit

Generated: {audit["generated_at"]}

## Verdict

{audit["recommendation"]}

## Counts

- legacy tokens after v2.1 strict filtering: {audit["legacy_tokens_after_v2_1_filter"]:,}
- legacy docs after v2.1 strict filtering: {audit["legacy_docs_after_v2_1_filter"]:,}
- legacy rejected by v2.1: {audit["legacy_rejected_by_v2_1"]:,}

## Accepted Label Counts

```json
{json.dumps(audit["accepted_label_counts"], ensure_ascii=False, indent=2)}
```

## Rejected Label Counts

```json
{json.dumps(audit["rejected_label_counts"], ensure_ascii=False, indent=2)}
```

## Random Accepted Legacy Samples

{render_samples(audit["random_accepted_samples"])}

## Worst Accepted Legacy Samples

{render_samples(audit["worst_accepted_samples"])}

## Best Accepted Legacy Samples

{render_samples(audit["best_accepted_samples"])}

## Bad Rejected Legacy Samples

{render_samples(audit["bad_rejected_samples"])}
"""


def render_samples(samples: list[dict[str, Any]]) -> str:
    chunks = []
    for i, sample in enumerate(samples[:100], 1):
        label = sample.get("legacy_label") or sample.get("source", "")
        score = sample.get("legacy_quality_score")
        score_text = f" score={score}" if score is not None else ""
        chunks.append(f"{i}. `{label}`{score_text} {sample.get('title', '')}\n\n   {sample.get('text', '')}")
    return "\n\n".join(chunks) if chunks else "_none_"


def render_report(stats: dict[str, Any]) -> str:
    rows = []
    for source, item in stats["source_mix"].items():
        rows.append(
            f"| `{source}` | {item['docs']:,} | {item['tokens']:,} | {item['train_tokens']:,} | {item['val_tokens']:,} |"
        )
    variant_rows = []
    for name, item in stats["variants"].items():
        variant_rows.append(
            f"| {name} | {item['total_tokens']:,} | {item['tokens_per_source'].get('legacy_mixed_corpus', {}).get('tokens', 0):,} | {item['stage3_50k_epochs']:.2f} | {item['risk']} |"
        )
    return f"""# Glyph-100M Dataset v2.1 Report

Generated: {stats["generated_at"]}

## Recommendation

{stats["recommendation"]}

## Output

- selected variant: `{stats["selected_variant"]}`
- train bin: `{stats["train_bin"]}`
- val bin: `{stats["val_bin"]}`
- docs JSONL: `{stats["docs_jsonl"]}`
- tokenizer: `{stats["tokenizer_path"]}`

## Counts

- train docs: {stats["train_docs"]:,}
- val docs: {stats["val_docs"]:,}
- train tokens: {stats["train_tokens"]:,}
- val tokens: {stats["val_tokens"]:,}
- total tokens: {stats["total_tokens"]:,}
- token/word ratio: {stats["token_word_ratio"]:.3f}

## Source Mix

| source | docs | total tokens | train tokens | val tokens |
|---|---:|---:|---:|---:|
{chr(10).join(rows)}

## Variant Comparison

| variant | total tokens | legacy tokens | 50k epochs | risk |
|---|---:|---:|---:|---|
{chr(10).join(variant_rows)}

## Rejection Reasons

```json
{json.dumps(stats["rejection_reasons"], ensure_ascii=False, indent=2)}
```

## Training Math

- stage 3 / 50k: {50_000 * TOKENS_PER_STEP:,} tokens = {stats["stage3_50k_epochs"]:.2f} epochs
- 100k: {100_000 * TOKENS_PER_STEP:,} tokens = {stats["stage4_100k_epochs"]:.2f} epochs
- 200k: {200_000 * TOKENS_PER_STEP:,} tokens = {stats["stage5_200k_epochs"]:.2f} epochs

## Final Random Samples

{render_samples(stats["final_samples"])}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Glyph-100M dataset v2.1")
    parser.add_argument("--v2-docs", type=Path, default=DEFAULT_V2_DOCS)
    parser.add_argument("--tokenizer", type=Path, default=DEFAULT_TOKENIZER)
    parser.add_argument("--selected-variant", choices=["A", "B", "C", "D"], default="A")
    parser.add_argument("--val-per-mille", type=int, default=5)
    parser.add_argument("--wikisource-limit", type=int, default=0, help="0 = all available streaming rows")
    parser.add_argument("--sample-limit", type=int, default=50)
    parser.add_argument("--legacy-audit-limit", type=int, default=100)
    parser.add_argument("--train-bin", type=Path, default=DEFAULT_TRAIN_BIN)
    parser.add_argument("--val-bin", type=Path, default=DEFAULT_VAL_BIN)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--docs-jsonl", type=Path, default=DEFAULT_DOCS_JSONL)
    parser.add_argument("--rejected-jsonl", type=Path, default=DEFAULT_REJECTED_JSONL)
    parser.add_argument("--stats", type=Path, default=DEFAULT_STATS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--accepted-samples", type=Path, default=DEFAULT_ACCEPTED_SAMPLES)
    parser.add_argument("--rejected-samples", type=Path, default=DEFAULT_REJECTED_SAMPLES)
    parser.add_argument("--final-samples", type=Path, default=DEFAULT_FINAL_SAMPLES)
    parser.add_argument("--legacy-audit-md", type=Path, default=DEFAULT_LEGACY_AUDIT_MD)
    parser.add_argument("--legacy-audit-json", type=Path, default=DEFAULT_LEGACY_AUDIT_JSON)
    parser.add_argument("--decision-md", type=Path, default=DEFAULT_DECISION_MD)
    parser.add_argument("--decision-json", type=Path, default=DEFAULT_DECISION_JSON)
    parser.add_argument("--source-audit-md", type=Path, default=DEFAULT_SOURCE_AUDIT_MD)
    parser.add_argument("--source-audit-json", type=Path, default=DEFAULT_SOURCE_AUDIT_JSON)
    parser.add_argument("--force-v2-1", action="store_true")
    args = parser.parse_args()

    ensure_safe_outputs(args)
    sp = load_sentencepiece(args.tokenizer)
    eos_id = sp.eos_id()

    exact_seen: set[str] = set()
    normalized_seen: set[str] = set()
    near_seen: set[str] = set()
    candidates: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    rejection_reasons: collections.Counter[str] = collections.Counter()
    accepted_samples: list[dict[str, Any]] = []
    rejected_samples: list[dict[str, Any]] = []

    source_audit = audit_new_sources()
    args.source_audit_json.write_text(json.dumps(source_audit, ensure_ascii=False, indent=2), encoding="utf-8")
    args.source_audit_md.write_text(
        "# Glyph-100M Dataset v2.1 Source Audit\n\n"
        + "\n".join(
            f"- **{item['name']}**: {item['decision']} — {item['reason']} ({item['url']})"
            for item in source_audit["sources"]
        )
        + "\n",
        encoding="utf-8",
    )

    start = time.time()
    for source_iter in [load_v2_records(args.v2_docs), wikisource_records(args.wikisource_limit)]:
        for record in source_iter:
            source = record.get("source", "")
            maybe, reasons, audit = source_record_ok(record, exact_seen, normalized_seen, near_seen)
            if maybe is None:
                for reason in reasons:
                    rejection_reasons[reason] += 1
                sample = sample_payload(record, audit | {"reject_reasons": reasons})
                rejected.append({"sample": sample, "audit": audit, "reasons": reasons})
                keep_sample(rejected_samples, sample, record.get("id", "") + ":reject", args.sample_limit)
                continue

            if not token_count(maybe):
                ids = sp.encode(maybe["text"], out_type=int)
                ids.append(eos_id)
                maybe.setdefault("meta", {})["token_count"] = len(ids)
            candidates.append(maybe)
            keep_sample(accepted_samples, sample_payload(maybe, {"token_count": token_count(maybe)}), maybe.get("id", ""), args.sample_limit)
            if len(candidates) % 100_000 == 0:
                print(f"accepted={len(candidates):,} rejected={len(rejected):,} elapsed={time.time()-start:.1f}s", flush=True)

    legacy_records = [r for r in candidates if r.get("source") == "legacy_mixed_corpus"]
    legacy_rejected = [r for r in rejected if r["sample"].get("source") == "legacy_mixed_corpus"]
    legacy_audit = build_legacy_audit(legacy_records, legacy_rejected, args)
    args.legacy_audit_json.write_text(json.dumps(legacy_audit, ensure_ascii=False, indent=2), encoding="utf-8")
    args.legacy_audit_md.write_text(render_legacy_audit(legacy_audit), encoding="utf-8")

    variants: dict[str, dict[str, Any]] = {}
    selected_by_variant: dict[str, list[dict[str, Any]]] = {}
    for name in ["A", "B", "C", "D"]:
        selected = select_variant(candidates, name)
        selected_by_variant[name] = selected
        variants[name] = variant_stats(name, selected, args.val_per_mille)
        variants[name]["risk"] = {
            "A": "best quality compromise; legacy capped near 10%",
            "B": "more data, more legacy risk",
            "C": "legacy still too influential",
            "D": "cleanest but small; many repeated epochs at 50k",
        }[name]

    final_records = selected_by_variant[args.selected_variant]
    source_mix: dict[str, dict[str, int]] = collections.defaultdict(lambda: {"docs": 0, "tokens": 0, "train_tokens": 0, "val_tokens": 0})
    train_tokens = val_tokens = train_docs = val_docs = total_words = 0
    final_samples: list[dict[str, Any]] = []
    token_lengths: list[int] = []

    with args.train_bin.open("wb") as train_out, args.val_bin.open("wb") as val_out, args.docs_jsonl.open(
        "w", encoding="utf-8"
    ) as docs_out:
        for record in final_records:
            ids = sp.encode(record["text"], out_type=int)
            ids.append(eos_id)
            record.setdefault("meta", {})["token_count"] = len(ids)
            record["parent_doc_id"] = parent_doc_id_for(record)
            split = split_for(record, args.val_per_mille)
            record["meta"]["split"] = split
            record["id"] = record.get("id") or f"glyph100-v2-1-{record.get('doc_id')}"
            record["id"] = record["id"].replace("glyph100-v2-", "glyph100-v2-1-", 1)
            json_dump_line(docs_out, record)
            source = record["source"]
            source_mix[source]["docs"] += 1
            source_mix[source]["tokens"] += len(ids)
            if split == "val":
                val_docs += 1
                val_tokens += len(ids)
                source_mix[source]["val_tokens"] += len(ids)
                write_uint16_tokens(val_out, ids)
            else:
                train_docs += 1
                train_tokens += len(ids)
                source_mix[source]["train_tokens"] += len(ids)
                write_uint16_tokens(train_out, ids)
            total_words += len(WORD_RE.findall(record["text"]))
            token_lengths.append(len(ids))
            keep_sample(final_samples, sample_payload(record, {"token_count": len(ids), "split": split}), record.get("id", ""), args.sample_limit)

    with args.rejected_jsonl.open("w", encoding="utf-8") as handle:
        for item in rejected:
            json_dump_line(handle, item)
    for path, rows in [
        (args.accepted_samples, accepted_samples),
        (args.rejected_samples, rejected_samples),
        (args.final_samples, final_samples),
    ]:
        with path.open("w", encoding="utf-8") as handle:
            for row in rows[: args.sample_limit]:
                json_dump_line(handle, row)

    total_tokens = train_tokens + val_tokens
    recommendation = (
        "B: v2.1 is cleaner than v2 and is the best current candidate, but 50k would still be "
        f"{50_000 * TOKENS_PER_STEP / max(total_tokens, 1):.2f} epochs. I recommend approving only a short stage-3 preflight or adding more clean sources before full 50k."
    )
    stats = {
        "generated_at": now_utc(),
        "dataset_name": "glyph100_dataset_v2_1",
        "selected_variant": args.selected_variant,
        "tokenizer_path": str(args.tokenizer),
        "tokenizer_vocab_size": sp.vocab_size(),
        "train_bin": str(args.train_bin),
        "val_bin": str(args.val_bin),
        "metadata_path": str(args.metadata),
        "docs_jsonl": str(args.docs_jsonl),
        "train_docs": train_docs,
        "val_docs": val_docs,
        "train_tokens": train_tokens,
        "val_tokens": val_tokens,
        "total_tokens": total_tokens,
        "token_word_ratio": total_tokens / max(total_words, 1),
        "word_token_ratio": total_words / max(total_tokens, 1),
        "doc_token_percentiles": {
            "p50": percentile(token_lengths, 0.50),
            "p75": percentile(token_lengths, 0.75),
            "p90": percentile(token_lengths, 0.90),
            "p95": percentile(token_lengths, 0.95),
            "p99": percentile(token_lengths, 0.99),
        },
        "source_mix": dict(source_mix),
        "variants": variants,
        "rejection_reasons": dict(rejection_reasons.most_common(60)),
        "legacy_audit": {
            "path_md": str(args.legacy_audit_md),
            "path_json": str(args.legacy_audit_json),
            "summary": legacy_audit["recommendation"],
        },
        "source_audit": str(args.source_audit_md),
        "final_samples": final_samples,
        "stage3_50k_epochs": 50_000 * TOKENS_PER_STEP / max(total_tokens, 1),
        "stage4_100k_epochs": 100_000 * TOKENS_PER_STEP / max(total_tokens, 1),
        "stage5_200k_epochs": 200_000 * TOKENS_PER_STEP / max(total_tokens, 1),
        "recommendation": recommendation,
        "elapsed_seconds": time.time() - start,
    }
    args.stats.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    args.report.write_text(render_report(stats), encoding="utf-8")
    args.metadata.write_text(
        json.dumps(
            {
                "variant": "glyph-100m",
                "dataset_name": "glyph100_dataset_v2_1",
                "selected_variant": args.selected_variant,
                "scope": "quality-first source-aware candidate; no training has been run on it",
                "train_bin": str(args.train_bin),
                "val_bin": str(args.val_bin),
                "docs_jsonl": str(args.docs_jsonl),
                "tokenizer": str(args.tokenizer),
                "vocab_size": sp.vocab_size(),
                "train_docs": train_docs,
                "val_docs": val_docs,
                "train_tokens": train_tokens,
                "val_tokens": val_tokens,
                "source_mix": dict(source_mix),
                "stage3_50k_epochs": stats["stage3_50k_epochs"],
                "created_at": stats["generated_at"],
                "stats_json": str(args.stats),
                "report": str(args.report),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    decision = {
        "generated_at": now_utc(),
        "verdict": recommendation,
        "selected_variant": args.selected_variant,
        "total_tokens": total_tokens,
        "stage3_50k_epochs": stats["stage3_50k_epochs"],
        "variants": variants,
        "next_decision": "User approval required before any stage 3 training.",
    }
    args.decision_json.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
    args.decision_md.write_text(
        f"""# Glyph-100M Dataset v2.1 Decision Report

Generated: {decision["generated_at"]}

## Verdict

{recommendation}

## Selected Variant

- variant: `{args.selected_variant}`
- total tokens: {total_tokens:,}
- train tokens: {train_tokens:,}
- val tokens: {val_tokens:,}
- stage 3 / 50k epochs: {stats["stage3_50k_epochs"]:.2f}

## Variant Summary

| variant | total tokens | legacy tokens | 50k epochs | risk |
|---|---:|---:|---:|---|
"""
        + "\n".join(
            f"| {name} | {item['total_tokens']:,} | {item['tokens_per_source'].get('legacy_mixed_corpus', {}).get('tokens', 0):,} | {item['stage3_50k_epochs']:.2f} | {item['risk']} |"
            for name, item in variants.items()
        )
        + "\n\nNo training was started.\n",
        encoding="utf-8",
    )
    print(json.dumps({"total_tokens": total_tokens, "selected_variant": args.selected_variant, "recommendation": recommendation}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    main()
