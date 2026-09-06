#!/usr/bin/env python3
"""Build a source-aware Glyph-100M dataset v2 candidate.

This script writes only glyph100_v2_* outputs. It refuses to touch legacy
tokens.bin, glyph100_train.bin, old reports, or checkpoints.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import requests

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from glyph100_dataset_v2_filter import (  # noqa: E402
    FilterConfig,
    evaluate_document,
    percentile,
    sha1_text,
    stable_bucket,
    truncate_text,
)
from glyph100_dataset_v2_report import build_report  # noqa: E402
from glyph100_dataset_identity import parent_doc_id_for, parent_split_for  # noqa: E402


DEFAULT_TOKENIZER = Path("data/processed/tokenizer.model")
DEFAULT_WIKI_DATASET = "wikimedia/wikipedia"
DEFAULT_WIKI_CONFIG = "20231101.pl"
DEFAULT_RAW_CORPUS = Path("data/raw/corpus.txt")
DEFAULT_WL_CACHE = Path("data/raw/wolnelektury_cache.json")
DEFAULT_TRAIN_BIN = Path("data/processed/glyph100_v2_train.bin")
DEFAULT_VAL_BIN = Path("data/processed/glyph100_v2_val.bin")
DEFAULT_METADATA = Path("data/processed/glyph100_v2_metadata.json")
DEFAULT_DOCS_JSONL = Path("data/processed/glyph100_v2_docs.jsonl")
DEFAULT_REJECTED_JSONL = Path("data/processed/glyph100_v2_rejected.jsonl")
DEFAULT_STATS = Path("data/reports/glyph100_dataset_v2_stats.json")
DEFAULT_REPORT = Path("data/reports/glyph100_dataset_v2_report.md")
DEFAULT_ACCEPTED_SAMPLES = Path("data/reports/glyph100_dataset_v2_samples_accepted.jsonl")
DEFAULT_REJECTED_SAMPLES = Path("data/reports/glyph100_dataset_v2_samples_rejected.jsonl")
DEFAULT_FINAL_SAMPLES = Path("data/reports/glyph100_dataset_v2_samples_final_random.jsonl")

DATASET_NAME = "glyph100_dataset_v2"
TOKENS_PER_STEP = 4 * 512 * 8

SOURCE_DECISIONS = [
    {
        "name": "wikipedia_pl",
        "location": "Hugging Face cache / wikimedia/wikipedia 20231101.pl",
        "type": "encyclopedic articles",
        "language": "pl",
        "approx_size": "2.8G cached arrow locally",
        "license": "Wikipedia project licenses, commonly CC BY-SA/GFDL; verify per dump/card",
        "decision": "use",
        "risk": "encyclopedic monoculture, reference/link sections, title/list artifacts",
        "reason": "Clean Polish continuous prose with stable id/title/url fields.",
    },
    {
        "name": "wolne_lektury",
        "location": "Wolne Lektury API/cache",
        "type": "literary texts",
        "language": "pl",
        "approx_size": "small/moderate API fetch; capped by --wolne-limit",
        "license": "work-dependent public domain / free licenses; verify individual metadata",
        "decision": "use_limited",
        "risk": "front matter, poems/dialogue, archaic style, repeated project boilerplate",
        "reason": "Adds long-form Polish literary style, but should not dominate a technical base model.",
    },
    {
        "name": "legacy_mixed_corpus",
        "location": "data/raw/corpus.txt after skipping cached Wikipedia prefix",
        "type": "legacy mixed web corpus",
        "language": "pl mostly",
        "approx_size": "19G raw monolithic text",
        "license": "mixed/unknown upstream; research-only local training hygiene required",
        "decision": "use_filtered_only",
        "risk": "no original source_id, web/forum/SEO garbage, possible duplicates",
        "reason": "Useful for breadth after strict filters, but not clean attribution.",
    },
    {
        "name": "FinetextPL-Edu",
        "location": "external HF dataset candidate",
        "type": "Polish educational/web text",
        "language": "pl",
        "approx_size": "not downloaded in this run",
        "license": "dataset-card dependent",
        "decision": "later",
        "risk": "needs separate size/license/sample audit before a large download",
        "reason": "Potentially useful, but the current task avoids uncapped large downloads.",
    },
    {
        "name": "mC4/OSCAR PL",
        "location": "external HF stream / legacy raw corpus",
        "type": "web crawl",
        "language": "pl mostly",
        "approx_size": "large",
        "license": "dataset-card dependent",
        "decision": "later_or_filtered_legacy",
        "risk": "the likely source of web/forum garbage in the 27M model",
        "reason": "Only acceptable with source metadata and strict filters.",
    },
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def json_dump_line(handle, obj: dict[str, Any]) -> None:
    handle.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")


def write_uint16_tokens(handle, ids: list[int]) -> None:
    np.asarray(ids, dtype=np.uint16).tofile(handle)


def parse_caps(value: str, target: int) -> dict[str, int]:
    if not value:
        return {
            "wikipedia_pl": int(target * 0.56),
            "legacy_mixed_corpus": int(target * 0.40),
            "wolne_lektury": int(target * 0.12),
        }
    caps: dict[str, int] = {}
    for part in value.split(","):
        if not part.strip():
            continue
        key, raw = part.split("=", 1)
        caps[key.strip()] = int(raw.replace("_", ""))
    return caps


def safe_outputs(args: argparse.Namespace) -> list[Path]:
    return [
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
    ]


def ensure_safe_outputs(args: argparse.Namespace) -> None:
    forbidden = {
        Path("data/processed/tokens.bin").resolve(),
        Path("data/processed/val_tokens.bin").resolve(),
        Path("data/processed/glyph100_train.bin").resolve(),
        Path("data/processed/glyph100_val.bin").resolve(),
        Path("data/processed/glyph100_metadata.json").resolve(),
        Path("data/reports/glyph_100m_dataset_report.md").resolve(),
        Path("data/reports/glyph_100m_dataset_stats.json").resolve(),
    }
    for path in safe_outputs(args):
        if path.resolve() in forbidden:
            raise SystemExit(f"Refusing to write protected legacy output: {path}")
    existing = [path for path in safe_outputs(args) if path.exists()]
    if existing and not args.force_v2:
        formatted = "\n".join(f"- {path}" for path in existing)
        raise SystemExit(f"v2 outputs already exist. Re-run with --force-v2 to replace only these v2 files:\n{formatted}")
    for path in safe_outputs(args):
        path.parent.mkdir(parents=True, exist_ok=True)


def load_sentencepiece(tokenizer: Path):
    try:
        import sentencepiece as spm
    except ImportError as exc:
        raise SystemExit("sentencepiece is required. Use ./.venv/bin/python or the training container.") from exc
    sp = spm.SentencePieceProcessor()
    sp.load(str(tokenizer))
    return sp


def wikipedia_docs(args: argparse.Namespace) -> Iterable[dict[str, Any]]:
    if args.skip_wikipedia:
        return
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise SystemExit("datasets is required for cached Wikipedia loading. Use ./.venv/bin/python.") from exc

    ds = load_dataset(args.wikipedia_dataset, args.wikipedia_config, split="train")
    limit = min(args.wikipedia_limit, len(ds)) if args.wikipedia_limit else len(ds)
    for i in range(limit):
        item = ds[i]
        text = item.get("text") or ""
        if not text:
            continue
        source_id = str(item.get("id") or i)
        title = str(item.get("title") or "")
        url = str(item.get("url") or "")
        yield {
            "source": "wikipedia_pl",
            "source_id": source_id,
            "title": title,
            "url": url,
            "license": "Wikipedia project license; verify per dump/card",
            "language": "pl",
            "text": text,
            "meta": {"dataset": args.wikipedia_dataset, "config": args.wikipedia_config, "row": i},
        }


def wolne_lektury_books(cache_path: Path) -> list[dict[str, Any]]:
    if not cache_path.exists():
        return []
    try:
        return json.loads(cache_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def fetch_wolne_text(slug: str, timeout: int = 30) -> str | None:
    url = f"https://wolnelektury.pl/media/book/txt/{slug}.txt"
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200 and response.text.strip():
            return response.text
    except requests.RequestException:
        return None
    return None


def chunk_wolne_text(text: str, max_chars: int = 8_000) -> list[str]:
    """Split a book into paragraph groups so one long book is not one document."""
    raw_parts = [part.strip() for part in text.split("\n\n") if part.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_chars = 0
    for part in raw_parts:
        if len(part) > max_chars:
            if current:
                chunks.append("\n\n".join(current))
                current = []
                current_chars = 0
            for start in range(0, len(part), max_chars):
                chunks.append(part[start : start + max_chars])
            continue
        if current and current_chars + len(part) > max_chars:
            chunks.append("\n\n".join(current))
            current = []
            current_chars = 0
        current.append(part)
        current_chars += len(part) + 2
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def wolne_lektury_docs(args: argparse.Namespace) -> Iterable[dict[str, Any]]:
    if args.wolne_limit <= 0:
        return
    books = wolne_lektury_books(args.wolne_cache)
    for i, book in enumerate(books[: args.wolne_limit]):
        slug = book.get("slug") or str(book.get("href", "")).rstrip("/").split("/")[-1]
        if not slug:
            continue
        text = fetch_wolne_text(slug)
        if not text:
            continue
        for chunk_idx, chunk in enumerate(chunk_wolne_text(text)):
            yield {
                "source": "wolne_lektury",
                "source_id": f"{slug}#chunk-{chunk_idx:04d}",
                "parent_doc_id": slug,
                "title": book.get("title") or slug,
                "url": f"https://wolnelektury.pl/katalog/lektura/{slug}/",
                "license": str(book.get("license") or "work-dependent; verify individual metadata"),
                "language": "pl",
                "text": chunk,
                "meta": {"slug": slug, "author": book.get("author"), "row": i, "chunk": chunk_idx},
            }
        if args.wolne_sleep > 0:
            time.sleep(args.wolne_sleep)


def legacy_mixed_docs(args: argparse.Namespace) -> Iterable[dict[str, Any]]:
    if args.skip_legacy or not args.raw_corpus.exists():
        return
    with args.raw_corpus.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, 1):
            if line_no <= args.legacy_skip_lines:
                continue
            if args.legacy_limit and line_no > args.legacy_skip_lines + args.legacy_limit:
                break
            text = line.strip()
            if not text:
                continue
            yield {
                "source": "legacy_mixed_corpus",
                "source_id": f"corpus-line-{line_no}",
                "title": "",
                "url": "",
                "license": "mixed/unknown upstream; local research use only",
                "language": "pl",
                "text": text,
                "meta": {"raw_path": str(args.raw_corpus), "line_no": line_no, "source_metadata": "not_preserved"},
            }


def doc_id_for(record: dict[str, Any], clean_text: str) -> str:
    base = "|".join(
        [
            str(record.get("source", "")),
            str(record.get("source_id", "")),
            str(record.get("title", "")),
            sha1_text(clean_text)[:16],
        ]
    )
    return sha1_text(base)[:24]


def build_public_record(record: dict[str, Any], text: str, doc_id: str, metrics: dict[str, Any], token_count: int, split: str) -> dict[str, Any]:
    return {
        "id": f"glyph100-v2-{doc_id}",
        "source": record.get("source", ""),
        "source_id": str(record.get("source_id", "")),
        "doc_id": doc_id,
        "parent_doc_id": str(record.get("parent_doc_id") or record.get("source_id") or doc_id),
        "title": record.get("title", ""),
        "url": record.get("url", ""),
        "license": record.get("license", ""),
        "language": record.get("language", "pl"),
        "text": text,
        "quality_score": round(float(metrics.get("quality_score", 0.0)), 4),
        "meta": {
            "split": split,
            "token_count": token_count,
            "chars": metrics.get("chars"),
            "words": metrics.get("words"),
            "alpha_ratio": metrics.get("alpha_ratio"),
            "polish_char_ratio": metrics.get("polish_char_ratio"),
            "polish_stopword_ratio": metrics.get("polish_stopword_ratio"),
            "repetition_score": metrics.get("repetition_score"),
            "suspicious_patterns": metrics.get("suspicious_patterns", []),
            "source_meta": record.get("meta", {}),
        },
    }


def sample_record(record: dict[str, Any], text: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "id": record.get("id", ""),
        "source": record.get("source", ""),
        "source_id": record.get("source_id", ""),
        "title": record.get("title", ""),
        "text": truncate_text(text),
    }
    if extra:
        payload.update(extra)
    return payload


def keep_sample(samples: list[dict[str, Any]], item: dict[str, Any], key: str, limit: int) -> None:
    if len(samples) < limit:
        samples.append(item)
        return
    bucket = stable_bucket(key, 10_000)
    if bucket < limit:
        samples[bucket % limit] = item


def source_iterators(args: argparse.Namespace) -> list[tuple[str, Iterable[dict[str, Any]]]]:
    return [
        ("wolne_lektury", wolne_lektury_docs(args)),
        ("wikipedia_pl", wikipedia_docs(args)),
        ("legacy_mixed_corpus", legacy_mixed_docs(args)),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build source-aware Glyph-100M dataset v2 candidate")
    parser.add_argument("--tokenizer", type=Path, default=DEFAULT_TOKENIZER)
    parser.add_argument("--target-tokens", type=int, default=300_000_000)
    parser.add_argument("--source-token-caps", default="")
    parser.add_argument("--dataset-name", default=DATASET_NAME)
    parser.add_argument("--context-len", type=int, default=512)
    parser.add_argument("--val-per-mille", type=int, default=5)
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
    parser.add_argument("--wikipedia-dataset", default=DEFAULT_WIKI_DATASET)
    parser.add_argument("--wikipedia-config", default=DEFAULT_WIKI_CONFIG)
    parser.add_argument("--wikipedia-limit", type=int, default=0)
    parser.add_argument("--skip-wikipedia", action="store_true")
    parser.add_argument("--raw-corpus", type=Path, default=DEFAULT_RAW_CORPUS)
    parser.add_argument("--legacy-skip-lines", type=int, default=1_587_721)
    parser.add_argument("--legacy-limit", type=int, default=0)
    parser.add_argument("--skip-legacy", action="store_true")
    parser.add_argument("--wolne-cache", type=Path, default=DEFAULT_WL_CACHE)
    parser.add_argument("--wolne-limit", type=int, default=250)
    parser.add_argument("--wolne-sleep", type=float, default=0.03)
    parser.add_argument("--sample-limit", type=int, default=50)
    parser.add_argument("--min-words", type=int, default=40)
    parser.add_argument("--max-chars", type=int, default=60_000)
    parser.add_argument("--force-v2", action="store_true")
    args = parser.parse_args()

    ensure_safe_outputs(args)
    if not args.tokenizer.exists():
        raise SystemExit(f"Tokenizer not found: {args.tokenizer}")

    sp = load_sentencepiece(args.tokenizer)
    eos_id = sp.eos_id()
    caps = parse_caps(args.source_token_caps, args.target_tokens)
    filter_config = FilterConfig(min_words=args.min_words, max_chars=args.max_chars)

    exact_seen: set[str] = set()
    normalized_seen: set[str] = set()
    near_seen: set[str] = set()

    source_stats: dict[str, dict[str, Any]] = collections.defaultdict(
        lambda: {
            "seen_docs": 0,
            "accepted_docs": 0,
            "rejected_docs": 0,
            "train_docs": 0,
            "val_docs": 0,
            "train_tokens": 0,
            "val_tokens": 0,
            "estimated_prefilter_tokens": 0,
            "decision": "",
        }
    )
    rejection_reasons: collections.Counter[str] = collections.Counter()
    suspicious_patterns: collections.Counter[str] = collections.Counter()
    token_lengths: list[int] = []
    accepted_samples: list[dict[str, Any]] = []
    rejected_samples: list[dict[str, Any]] = []
    final_samples: list[dict[str, Any]] = []

    seen_docs = accepted_docs = rejected_docs = 0
    train_docs = val_docs = 0
    train_tokens = val_tokens = 0
    total_words = 0
    estimated_prefilter_tokens = 0
    max_doc_tokens = 0
    docs_within_context = 0
    started = time.time()
    last_progress_tokens = 0

    with args.train_bin.open("wb") as train_out, args.val_bin.open("wb") as val_out, args.docs_jsonl.open(
        "w", encoding="utf-8"
    ) as docs_out, args.rejected_jsonl.open("w", encoding="utf-8") as rejected_out:
        for source, iterator in source_iterators(args):
            source_cap = caps.get(source, args.target_tokens)
            source_stats[source]["decision"] = "use_until_cap"
            for record in iterator:
                current_total = train_tokens + val_tokens
                if current_total >= args.target_tokens:
                    break
                source_total = source_stats[source]["train_tokens"] + source_stats[source]["val_tokens"]
                if source_total >= source_cap:
                    break

                seen_docs += 1
                source_stats[source]["seen_docs"] += 1
                result = evaluate_document(
                    record["text"],
                    source=source,
                    config=filter_config,
                    exact_seen=exact_seen,
                    normalized_seen=normalized_seen,
                    near_seen=near_seen,
                )
                word_estimate = int(result.metrics.get("words", 0))
                estimated_prefilter_tokens += int(word_estimate * 2.02)
                source_stats[source]["estimated_prefilter_tokens"] += int(word_estimate * 2.02)

                if not result.accepted:
                    rejected_docs += 1
                    source_stats[source]["rejected_docs"] += 1
                    for reason in result.reasons:
                        rejection_reasons[reason] += 1
                    rejected_payload = {
                        "source": source,
                        "source_id": record.get("source_id", ""),
                        "title": record.get("title", ""),
                        "reject_reasons": result.reasons,
                        "quality_score": round(float(result.metrics.get("quality_score", 0.0)), 4),
                        "text": truncate_text(result.text or record["text"]),
                    }
                    json_dump_line(rejected_out, rejected_payload)
                    keep_sample(
                        rejected_samples,
                        sample_record(record, result.text or record["text"], {"reject_reasons": result.reasons[:6]}),
                        f"{source}:{record.get('source_id', '')}:reject",
                        args.sample_limit,
                    )
                    continue

                ids = sp.encode(result.text, out_type=int)
                if not ids:
                    rejected_docs += 1
                    source_stats[source]["rejected_docs"] += 1
                    rejection_reasons["empty_tokenization"] += 1
                    continue
                ids.append(eos_id)
                if source_total + len(ids) > source_cap and source_total > 0:
                    continue

                exact_seen.add(str(result.metrics["exact_hash"]))
                normalized_seen.add(str(result.metrics["normalized_hash"]))
                near_seen.add(str(result.metrics["near_hash"]))

                doc_id = doc_id_for(record, result.text)
                record["parent_doc_id"] = parent_doc_id_for(record)
                split = parent_split_for(record, args.val_per_mille)
                public_record = build_public_record(record, result.text, doc_id, result.metrics, len(ids), split)
                json_dump_line(docs_out, public_record)

                if split == "val":
                    write_uint16_tokens(val_out, ids)
                    val_docs += 1
                    val_tokens += len(ids)
                    source_stats[source]["val_docs"] += 1
                    source_stats[source]["val_tokens"] += len(ids)
                else:
                    write_uint16_tokens(train_out, ids)
                    train_docs += 1
                    train_tokens += len(ids)
                    source_stats[source]["train_docs"] += 1
                    source_stats[source]["train_tokens"] += len(ids)

                accepted_docs += 1
                source_stats[source]["accepted_docs"] += 1
                total_words += word_estimate
                token_lengths.append(len(ids))
                max_doc_tokens = max(max_doc_tokens, len(ids))
                if len(ids) <= args.context_len:
                    docs_within_context += 1
                for pattern in result.metrics.get("suspicious_patterns", []):
                    suspicious_patterns[pattern] += 1

                sample = sample_record(public_record, result.text, {"token_count": len(ids), "split": split})
                keep_sample(accepted_samples, sample, f"{source}:{doc_id}:accepted", args.sample_limit)
                keep_sample(final_samples, sample, f"{source}:{doc_id}:final", args.sample_limit)

                total_after = train_tokens + val_tokens
                if total_after - last_progress_tokens >= 25_000_000:
                    last_progress_tokens = total_after
                    elapsed = time.time() - started
                    print(
                        f"tokens={total_after:,}/{args.target_tokens:,} "
                        f"accepted={accepted_docs:,} rejected={rejected_docs:,} "
                        f"source={source} elapsed={elapsed:.1f}s",
                        flush=True,
                    )

    total_tokens = train_tokens + val_tokens
    for item in source_stats.values():
        seen = item["seen_docs"]
        item["acceptance_rate"] = item["accepted_docs"] / max(seen, 1)

    stage3_tokens = 50_000 * TOKENS_PER_STEP
    stage4_tokens = 100_000 * TOKENS_PER_STEP
    stage5_tokens = 200_000 * TOKENS_PER_STEP
    if total_tokens >= 500_000_000:
        recommendation = "A: dataset v2 is large enough to consider stage 3 / 50k after a quick sample review."
    elif total_tokens >= 300_000_000:
        recommendation = (
            "B-light: dataset v2 reaches the minimum 300M-token target and is much better than stage1_candidate, "
            "but 50k still repeats it multiple times; review samples before approval."
        )
    else:
        recommendation = "B/C: local clean source-aware data did not reach 300M tokens; add sources before stage 3."

    stats: dict[str, Any] = {
        "generated_at": now_utc(),
        "dataset_name": args.dataset_name,
        "tokenizer_path": str(args.tokenizer),
        "tokenizer_vocab_size": sp.vocab_size(),
        "context_len": args.context_len,
        "val_per_mille": args.val_per_mille,
        "target_tokens": args.target_tokens,
        "source_token_caps": caps,
        "source_decisions": SOURCE_DECISIONS,
        "seen_docs": seen_docs,
        "accepted_docs": accepted_docs,
        "rejected_docs": rejected_docs,
        "acceptance_rate": accepted_docs / max(seen_docs, 1),
        "train_docs": train_docs,
        "val_docs": val_docs,
        "train_tokens": train_tokens,
        "val_tokens": val_tokens,
        "total_tokens": total_tokens,
        "estimated_prefilter_tokens": estimated_prefilter_tokens,
        "total_words": total_words,
        "token_word_ratio": total_tokens / max(total_words, 1),
        "word_token_ratio": total_words / max(total_tokens, 1),
        "doc_token_percentiles": {
            "p50": percentile(token_lengths, 0.50),
            "p75": percentile(token_lengths, 0.75),
            "p90": percentile(token_lengths, 0.90),
            "p95": percentile(token_lengths, 0.95),
            "p99": percentile(token_lengths, 0.99),
        },
        "max_doc_tokens": max_doc_tokens,
        "docs_within_context": docs_within_context,
        "docs_within_context_ratio": docs_within_context / max(accepted_docs, 1),
        "sources": dict(source_stats),
        "rejection_reasons": dict(rejection_reasons.most_common(50)),
        "suspicious_patterns": dict(suspicious_patterns.most_common(50)),
        "accepted_samples": accepted_samples,
        "rejected_samples": rejected_samples,
        "final_samples": final_samples,
        "train_bin": str(args.train_bin),
        "val_bin": str(args.val_bin),
        "metadata_path": str(args.metadata),
        "docs_jsonl": str(args.docs_jsonl),
        "rejected_jsonl": str(args.rejected_jsonl),
        "training_token_math": {
            "tokens_per_step": TOKENS_PER_STEP,
            "stage3_50k_tokens": stage3_tokens,
            "stage3_50k_epochs": stage3_tokens / max(total_tokens, 1),
            "stage4_100k_tokens": stage4_tokens,
            "stage4_100k_epochs": stage4_tokens / max(total_tokens, 1),
            "stage5_200k_tokens": stage5_tokens,
            "stage5_200k_epochs": stage5_tokens / max(total_tokens, 1),
        },
        "elapsed_seconds": time.time() - started,
        "recommendation": recommendation,
    }

    args.metadata.write_text(
        json.dumps(
            {
                "variant": "glyph-100m",
                "dataset_name": args.dataset_name,
                "scope": "source-aware dataset v2 candidate for post-10k Glyph-100M training decision",
                "train_bin": str(args.train_bin),
                "val_bin": str(args.val_bin),
                "docs_jsonl": str(args.docs_jsonl),
                "rejected_jsonl": str(args.rejected_jsonl),
                "tokenizer": str(args.tokenizer),
                "vocab_size": sp.vocab_size(),
                "context_len": args.context_len,
                "train_docs": train_docs,
                "val_docs": val_docs,
                "train_tokens": train_tokens,
                "val_tokens": val_tokens,
                "source_token_caps": caps,
                "source_decisions": SOURCE_DECISIONS,
                "created_at": stats["generated_at"],
                "filter_report": str(args.report),
                "stats_json": str(args.stats),
                "stage3_50k_epochs": stats["training_token_math"]["stage3_50k_epochs"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    args.stats.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    args.report.write_text(build_report(stats), encoding="utf-8")
    for path, rows in [
        (args.accepted_samples, accepted_samples),
        (args.rejected_samples, rejected_samples),
        (args.final_samples, final_samples),
    ]:
        with path.open("w", encoding="utf-8") as handle:
            for row in rows[: args.sample_limit]:
                json_dump_line(handle, row)

    print(
        json.dumps(
            {
                "dataset_name": args.dataset_name,
                "train_tokens": train_tokens,
                "val_tokens": val_tokens,
                "total_tokens": total_tokens,
                "accepted_docs": accepted_docs,
                "rejected_docs": rejected_docs,
                "report": str(args.report),
                "recommendation": recommendation,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    main()
