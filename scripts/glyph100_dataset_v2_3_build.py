#!/usr/bin/env python3
"""Build Glyph-100M dataset v2.3 with FineWeb2 PL as controlled non-Wiki source.

No training is started. Existing v2.1/v2.2/stage1 artifacts are protected from
accidental overwrite. The default build is variant A: about 300M total tokens,
legacy excluded, current SentencePiece tokenizer, document-level split.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
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
    evaluate_document,
    percentile,
    sha1_text,
    stable_bucket,
    truncate_text,
)
from glyph100_dataset_v2_2_build import (  # noqa: E402
    add_seen,
    common_bad_pattern_reasons,
    keep_sample,
    load_sentencepiece,
    source_title_id,
    token_count,
    word_count,
)
from glyph100_fineweb2_pl_probe import (  # noqa: E402
    DEFAULT_REPO as FINEWEB2_REPO,
    fineweb_config,
    fineweb_extra_reasons,
)
from glyph100_dataset_identity import parent_doc_id_for, parent_split_for  # noqa: E402


DEFAULT_BASE_V2_1_DOCS = Path("data/processed/glyph100_v2_1_docs.jsonl")
DEFAULT_BASE_V2_2_DOCS = Path("data/processed/glyph100_v2_2_docs.jsonl")
DEFAULT_TOKENIZER = Path("data/processed/tokenizer.model")
DEFAULT_TRAIN_BIN = Path("data/processed/glyph100_v2_3_train.bin")
DEFAULT_VAL_BIN = Path("data/processed/glyph100_v2_3_val.bin")
DEFAULT_METADATA = Path("data/processed/glyph100_v2_3_metadata.json")
DEFAULT_DOCS_JSONL = Path("data/processed/glyph100_v2_3_docs.jsonl")
DEFAULT_STATS = Path("data/reports/glyph100_dataset_v2_3_stats.json")
DEFAULT_REPORT = Path("data/reports/glyph100_dataset_v2_3_report.md")
DEFAULT_ACCEPTED_SAMPLES = Path("data/reports/glyph100_dataset_v2_3_samples_accepted.jsonl")
DEFAULT_REJECTED_SAMPLES = Path("data/reports/glyph100_dataset_v2_3_samples_rejected.jsonl")
DEFAULT_FINAL_SAMPLES = Path("data/reports/glyph100_dataset_v2_3_samples_final_random.jsonl")
DEFAULT_FINEWEB_ACCEPTED = Path("data/reports/glyph100_dataset_v2_3_samples_fineweb2_accepted.jsonl")
DEFAULT_FINEWEB_REJECTED = Path("data/reports/glyph100_dataset_v2_3_samples_fineweb2_rejected.jsonl")
DEFAULT_DECISION_MD = Path("reports/glyph100_dataset_v2_3_decision_report.md")

TOKENS_PER_STEP = 4 * 512 * 8
TRAINING_TOKENS_50K = 50_000 * TOKENS_PER_STEP
TRAINING_TOKENS_100K = 100_000 * TOKENS_PER_STEP
TRAINING_TOKENS_200K = 200_000 * TOKENS_PER_STEP

SOURCE_LICENSES = {
    "wikipedia_pl": "CC BY-SA / GFDL; verify dump terms",
    "wolne_lektury": "public domain / Wolne Lektury metadata; verify per work",
    "wikisource_pl": "CC BY-SA / GFDL; verify per page",
    "wikibooks_pl": "CC BY-SA / GFDL; verify per page",
    "allegro_summaries_source": "unknown; verify HF dataset card / original PSC terms",
    "fineweb2_pl": "ODC-BY per ReactiveAI/fineweb-2-pol-latest dataset tag; verify card",
}
BASE_V2_1_SOURCES = {"wikipedia_pl", "wolne_lektury"}
BASE_V2_2_EXTRA_SOURCES = {"wikisource_pl", "wikibooks_pl", "allegro_summaries_source"}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def json_dump_line(handle, obj: dict[str, Any]) -> None:
    handle.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")


def write_uint16_tokens(handle, ids: list[int]) -> None:
    np.asarray(ids, dtype=np.uint16).tofile(handle)


def split_for(record: dict[str, Any], val_per_mille: int) -> str:
    return parent_split_for(record, val_per_mille)


def sample_payload(record: dict[str, Any], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "id": record.get("id", ""),
        "source": record.get("source", ""),
        "source_id": record.get("source_id", ""),
        "doc_id": record.get("doc_id", ""),
        "title": record.get("title", ""),
        "url": record.get("url", ""),
        "quality_score": record.get("quality_score", 0),
        "text": truncate_text(record.get("text", ""), 1100),
    }
    if extra:
        payload.update(extra)
    return payload


def safe_id(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_.:-]+", "-", value.strip())
    return value.strip("-")[:96] or sha1_text(value)[:16]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            json_dump_line(handle, row)


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
        Path("data/processed/glyph100_v2_1_train.bin").resolve(),
        Path("data/processed/glyph100_v2_1_val.bin").resolve(),
        Path("data/processed/glyph100_v2_1_docs.jsonl").resolve(),
        Path("data/processed/glyph100_v2_1_metadata.json").resolve(),
        Path("data/processed/glyph100_v2_2_train.bin").resolve(),
        Path("data/processed/glyph100_v2_2_val.bin").resolve(),
        Path("data/processed/glyph100_v2_2_docs.jsonl").resolve(),
        Path("data/processed/glyph100_v2_2_metadata.json").resolve(),
    }
    outputs = [
        args.train_bin,
        args.val_bin,
        args.metadata,
        args.docs_jsonl,
        args.stats,
        args.report,
        args.accepted_samples,
        args.rejected_samples,
        args.final_samples,
        args.fineweb_accepted_samples,
        args.fineweb_rejected_samples,
        args.decision_md,
    ]
    for path in outputs:
        if path.resolve() in forbidden:
            raise SystemExit(f"Refusing to overwrite protected dataset output: {path}")
    existing = [path for path in outputs if path.exists()]
    if existing and not args.force_v2_3:
        formatted = "\n".join(f"- {path}" for path in existing)
        raise SystemExit(f"v2.3 outputs already exist. Use --force-v2-3 to replace v2.3 files only:\n{formatted}")
    for path in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)


def iter_existing_docs(path: Path, allowed_sources: set[str], dataset_label: str) -> Iterable[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("source") not in allowed_sources:
                continue
            record = dict(record)
            source = record.get("source", "")
            doc_id = str(record.get("doc_id") or record.get("id") or sha1_text(record.get("text", ""))[:20])
            record["id"] = f"glyph100-v2-3-{source}-{safe_id(doc_id)}"
            record["source_id"] = str(record.get("source_id") or doc_id)
            record["doc_id"] = doc_id
            record["license"] = record.get("license") or SOURCE_LICENSES.get(source, "unknown")
            record["language"] = "pl"
            record.setdefault("meta", {})["source_dataset"] = dataset_label
            record.setdefault("meta", {})["dataset_name"] = "glyph100_dataset_v2_3"
            record.pop("_raw_text", None)
            record.pop("_namespace", None)
            yield record


def fineweb_record_from_row(row: dict[str, Any], idx: int, text: str, quality_score: float) -> dict[str, Any]:
    source_id = str(row.get("id") or sha1_text(f"{idx}:{row.get('url','')}:{text[:200]}")[:24])
    url = str(row.get("url") or "")
    domain = re.sub(r"^https?://", "", url).split("/", 1)[0].lower()
    title = domain or source_id[:32]
    doc_id = source_title_id("fineweb2_pl", url or source_id, source_id)
    return {
        "id": f"glyph100-v2-3-fineweb2-{safe_id(source_id)}",
        "source": "fineweb2_pl",
        "source_id": "reactiveai_fineweb2_pol_latest",
        "doc_id": doc_id,
        "title": title,
        "url": url,
        "license": SOURCE_LICENSES["fineweb2_pl"],
        "language": "pl",
        "text": text,
        "quality_score": round(quality_score, 4),
        "meta": {
            "source_meta": {
                "dataset": FINEWEB2_REPO,
                "row": idx,
                "hf_id": source_id,
                "language": row.get("language"),
                "language_score": row.get("language_score"),
                "language_script": row.get("language_script"),
                "minhash_cluster_size": row.get("minhash_cluster_size"),
                "dump": row.get("dump"),
                "date": row.get("date"),
                "file_path": row.get("file_path"),
            },
            "source_dataset": FINEWEB2_REPO,
            "dataset_name": "glyph100_dataset_v2_3",
        },
    }


def write_record(
    record: dict[str, Any],
    *,
    sp,
    eos_id: int,
    train_out,
    val_out,
    docs_out,
    val_per_mille: int,
    counters: dict[str, Any],
    final_samples: list[dict[str, Any]],
    accepted_samples: list[dict[str, Any]],
    sample_limit: int,
) -> int:
    ids = sp.encode(record["text"], out_type=int)
    ids.append(eos_id)
    record["parent_doc_id"] = parent_doc_id_for(record)
    split = split_for(record, val_per_mille)
    source_state = counters["source_mix"][record["source"]]
    record.setdefault("meta", {})["token_count"] = len(ids)
    record["meta"]["word_count"] = word_count(record["text"])
    record["meta"]["split"] = split
    json_dump_line(docs_out, record)
    if split == "val":
        write_uint16_tokens(val_out, ids)
        counters["val_docs"] += 1
        counters["val_tokens"] += len(ids)
        source_state["val_docs"] += 1
        source_state["val_tokens"] += len(ids)
    else:
        write_uint16_tokens(train_out, ids)
        counters["train_docs"] += 1
        counters["train_tokens"] += len(ids)
        source_state["train_docs"] += 1
        source_state["train_tokens"] += len(ids)
    source_stats = source_state
    source_stats["docs"] += 1
    source_stats["tokens"] += len(ids)
    counters["total_words"] += record["meta"]["word_count"]
    counters["token_lengths"].append(len(ids))
    keep_sample(
        accepted_samples,
        sample_payload(record, {"token_count": len(ids), "split": split}),
        f"accept:{record.get('id', '')}",
        sample_limit,
    )
    keep_sample(
        final_samples,
        sample_payload(record, {"token_count": len(ids), "split": split}),
        f"final:{record.get('id', '')}",
        sample_limit,
    )
    return len(ids)


def add_existing_sources(
    paths: list[tuple[Path, set[str], str]],
    *,
    sp,
    eos_id: int,
    train_out,
    val_out,
    docs_out,
    exact_seen: set[str],
    normalized_seen: set[str],
    near_seen: set[str],
    counters: dict[str, Any],
    final_samples: list[dict[str, Any]],
    accepted_samples: list[dict[str, Any]],
    sample_limit: int,
    val_per_mille: int,
) -> int:
    total = 0
    for path, sources, label in paths:
        for record in iter_existing_docs(path, sources, label):
            result = evaluate_document(record.get("text", ""), source=record.get("source", ""), config=fineweb_config())
            if result.accepted:
                record["text"] = result.text
                record["quality_score"] = record.get("quality_score") or round(
                    float(result.metrics.get("quality_score", 0.0)), 4
                )
                add_seen(result.metrics, exact_seen, normalized_seen, near_seen)
            else:
                # Existing v2.1/v2.2 records were already filtered. Keep them,
                # but do not add their failed re-check hashes.
                pass
            total += write_record(
                record,
                sp=sp,
                eos_id=eos_id,
                train_out=train_out,
                val_out=val_out,
                docs_out=docs_out,
                val_per_mille=val_per_mille,
                counters=counters,
                final_samples=final_samples,
                accepted_samples=accepted_samples,
                sample_limit=sample_limit,
            )
    return total


def stream_fineweb(
    args: argparse.Namespace,
    *,
    sp,
    eos_id: int,
    train_out,
    val_out,
    docs_out,
    exact_seen: set[str],
    normalized_seen: set[str],
    near_seen: set[str],
    counters: dict[str, Any],
    final_samples: list[dict[str, Any]],
    accepted_samples: list[dict[str, Any]],
    rejected_samples: list[dict[str, Any]],
    fineweb_accepted_samples: list[dict[str, Any]],
    fineweb_rejected_samples: list[dict[str, Any]],
) -> dict[str, Any]:
    from datasets import load_dataset

    config = fineweb_config()
    start = time.time()
    raw_seen = accepted = rejected = accepted_tokens = 0
    fields_seen: set[str] = set()
    top_domains: collections.Counter[str] = collections.Counter()
    dataset = load_dataset(args.fineweb_repo, split=args.fineweb_split, streaming=True)
    for idx, row in enumerate(dataset, 1):
        raw_seen = idx
        fields_seen.update(row.keys())
        text = row.get("text") or ""
        url = str(row.get("url") or "")
        if url:
            domain = re.sub(r"^https?://", "", url).split("/", 1)[0].lower()
            top_domains[domain] += 1

        pre_reasons = fineweb_extra_reasons(text, row, args)
        result = evaluate_document(
            text,
            source="fineweb2_pl",
            config=config,
            exact_seen=exact_seen,
            normalized_seen=normalized_seen,
            near_seen=near_seen,
        )
        reasons = pre_reasons + common_bad_pattern_reasons(result.text) + result.reasons
        if reasons:
            rejected += 1
            for reason in reasons:
                counters["rejection_reasons"][reason] += 1
            reject_record = {
                "id": str(row.get("id") or ""),
                "source": "fineweb2_pl",
                "url": row.get("url") or "",
                "reject_reason": reasons[0],
                "reject_reasons": reasons,
                "metrics": {
                    key: result.metrics.get(key)
                    for key in [
                        "words",
                        "chars",
                        "alpha_ratio",
                        "polish_stopword_ratio",
                        "repetition_score",
                        "quality_score",
                        "suspicious_patterns",
                    ]
                },
                "text": truncate_text(result.text or text, 1100),
            }
            keep_sample(rejected_samples, reject_record, f"reject:{idx}:{row.get('id','')}", args.sample_limit)
            keep_sample(
                fineweb_rejected_samples,
                reject_record,
                f"fineweb-reject:{idx}:{row.get('id','')}",
                args.sample_limit,
            )
        else:
            record = fineweb_record_from_row(row, idx, result.text, float(result.metrics.get("quality_score", 0.0)))
            add_seen(result.metrics, exact_seen, normalized_seen, near_seen)
            count = write_record(
                record,
                sp=sp,
                eos_id=eos_id,
                train_out=train_out,
                val_out=val_out,
                docs_out=docs_out,
                val_per_mille=args.val_per_mille,
                counters=counters,
                final_samples=final_samples,
                accepted_samples=accepted_samples,
                sample_limit=args.sample_limit,
            )
            accepted += 1
            accepted_tokens += count
            keep_sample(
                fineweb_accepted_samples,
                sample_payload(record, {"token_count": count, "split": record["meta"]["split"]}),
                f"fineweb-accept:{idx}:{row.get('id','')}",
                args.sample_limit,
            )
        if args.progress_every and idx % args.progress_every == 0:
            elapsed = time.time() - start
            print(
                f"fineweb2_pl: seen={idx:,} accepted={accepted:,} rejected={rejected:,} "
                f"accepted_tokens={accepted_tokens:,} elapsed={elapsed:.1f}s",
                flush=True,
            )
        if args.max_fineweb_raw_docs and idx >= args.max_fineweb_raw_docs:
            break
        if accepted_tokens >= args.target_fineweb_tokens:
            break
    return {
        "raw_seen": raw_seen,
        "accepted_docs": accepted,
        "rejected_docs": rejected,
        "accepted_tokens": accepted_tokens,
        "acceptance_rate": accepted / max(raw_seen, 1),
        "fields": sorted(fields_seen),
        "top_url_domains": dict(top_domains.most_common(30)),
        "elapsed_seconds": time.time() - start,
    }


def render_samples(samples: list[dict[str, Any]], limit: int = 20) -> str:
    if not samples:
        return "_none_"
    chunks = []
    for i, sample in enumerate(samples[:limit], 1):
        chunks.append(
            f"{i}. `{sample.get('source', '')}` {sample.get('title', '')} "
            f"(tokens={sample.get('token_count', 'n/a')}, score={sample.get('quality_score', 'n/a')})\n\n"
            f"   {sample.get('text', '')}"
        )
    return "\n\n".join(chunks)


def build_options(total_tokens: int) -> list[dict[str, Any]]:
    return [
        {
            "variant": "A",
            "target_tokens": 300_000_000,
            "stage3_50k_epochs": TRAINING_TOKENS_50K / 300_000_000,
            "recommendation": "selected default if quality is acceptable",
        },
        {
            "variant": "B",
            "target_tokens": 500_000_000,
            "stage3_50k_epochs": TRAINING_TOKENS_50K / 500_000_000,
            "recommendation": "later, only if A samples look good and storage/time are acceptable",
        },
        {
            "variant": "C",
            "target_tokens": 200_000_000,
            "stage3_50k_epochs": TRAINING_TOKENS_50K / 200_000_000,
            "recommendation": "quality-first fallback if FineWeb2 is noisy",
        },
        {
            "variant": "current_build",
            "target_tokens": total_tokens,
            "stage3_50k_epochs": TRAINING_TOKENS_50K / max(total_tokens, 1),
            "recommendation": "actual generated v2.3 build",
        },
    ]


def render_report(stats: dict[str, Any]) -> str:
    total = max(stats["total_tokens"], 1)
    source_rows = []
    for source, item in stats["source_mix"].items():
        source_rows.append(
            f"| `{source}` | {item['docs']:,} | {item['tokens']:,} | {item['tokens'] / total:.2%} | "
            f"{item['train_tokens']:,} | {item['val_tokens']:,} |"
        )
    option_rows = "\n".join(
        f"| {item['variant']} | {item['target_tokens']:,} | {item['stage3_50k_epochs']:.2f} | {item['recommendation']} |"
        for item in stats["v2_3_options"]
    )
    return f"""# Glyph-100M Dataset v2.3 Report

Generated: {stats["generated_at"]}

No training was started.

## Verdict

{stats["recommendation"]}

## Outputs

- train bin: `{stats["train_bin"]}`
- val bin: `{stats["val_bin"]}`
- docs JSONL: `{stats["docs_jsonl"]}`
- metadata: `{stats["metadata_path"]}`
- tokenizer: `{stats["tokenizer_path"]}`

## Source Mix

| source | docs | tokens | share | train tokens | val tokens |
|---|---:|---:|---:|---:|---:|
{chr(10).join(source_rows)}

## Counts

- train docs: {stats["train_docs"]:,}
- val docs: {stats["val_docs"]:,}
- train tokens: {stats["train_tokens"]:,}
- val tokens: {stats["val_tokens"]:,}
- total tokens: {stats["total_tokens"]:,}
- token/word ratio: {stats["token_word_ratio"]:.3f}
- Wikipedia share: {stats["wikipedia_share"]:.2%}
- FineWeb2 share: {stats["fineweb2_share"]:.2%}
- legacy share: 0.00%

## FineWeb2 PL Probe/Build

```json
{json.dumps(stats["fineweb2"], ensure_ascii=False, indent=2)}
```

## Rejection Reasons

```json
{json.dumps(stats["rejection_reasons"], ensure_ascii=False, indent=2)}
```

## Training Math

- stage 3 / 50k total: {TRAINING_TOKENS_50K:,} tokens = {stats["stage3_50k_epochs"]:.2f} epochs
- 100k total: {TRAINING_TOKENS_100K:,} tokens = {stats["stage4_100k_epochs"]:.2f} epochs
- 200k total: {TRAINING_TOKENS_200K:,} tokens = {stats["stage5_200k_epochs"]:.2f} epochs

## v2.3 Options

| variant | target tokens | 50k epochs | recommendation |
|---|---:|---:|---|
{option_rows}

## Quality Notes

- FineWeb2 is web text, not trusted blindly. URL/contact/commerce/forum/SEO/list-heavy documents are rejected.
- v2.3 excludes legacy entirely.
- v2.3 uses old SentencePiece 16k for comparability with Glyph-27M and Glyph-100M stage 1/2.
- The split is document-level by stable source/doc hash.

## Final Random Samples

{render_samples(stats["final_samples"], 50)}
"""


def render_decision(stats: dict[str, Any]) -> str:
    return f"""# Glyph-100M Dataset v2.3 Decision Report

Generated: {stats["generated_at"]}

No training was started.

## Recommendation

{stats["decision_code"]}

{stats["recommendation"]}

## Key Numbers

- total tokens: {stats["total_tokens"]:,}
- train tokens: {stats["train_tokens"]:,}
- val tokens: {stats["val_tokens"]:,}
- Wikipedia share: {stats["wikipedia_share"]:.2%}
- FineWeb2 PL share: {stats["fineweb2_share"]:.2%}
- legacy share: 0.00%
- stage 3 / 50k epochs: {stats["stage3_50k_epochs"]:.2f}
- FineWeb2 raw rows seen: {stats["fineweb2"]["raw_seen"]:,}
- FineWeb2 accepted docs: {stats["fineweb2"]["accepted_docs"]:,}
- FineWeb2 acceptance rate: {stats["fineweb2"]["acceptance_rate"]:.2%}

## Source Mix

```json
{json.dumps(stats["source_mix"], ensure_ascii=False, indent=2)}
```

## Decision Options

- A) v2.3 gotowy, można odpalić stage 3 / 50k po osobnej zgodzie.
- B) v2.3 lepszy, ale jeszcze wymaga poprawek.
- C) potrzebne inne źródła / ostrzejsze filtrowanie.
- D) lepiej zrobić krótki preflight, nie 50k.
- E) zatrzymać się, bo dane są za słabe.

No stage 3 command was executed.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Glyph-100M dataset v2.3")
    parser.add_argument("--base-v2-1-docs", type=Path, default=DEFAULT_BASE_V2_1_DOCS)
    parser.add_argument("--base-v2-2-docs", type=Path, default=DEFAULT_BASE_V2_2_DOCS)
    parser.add_argument("--tokenizer", type=Path, default=DEFAULT_TOKENIZER)
    parser.add_argument("--fineweb-repo", default=FINEWEB2_REPO)
    parser.add_argument("--fineweb-split", default="train")
    parser.add_argument("--target-total-tokens", type=int, default=300_000_000)
    parser.add_argument("--target-fineweb-tokens", type=int, default=0)
    parser.add_argument("--max-fineweb-raw-docs", type=int, default=1_000_000)
    parser.add_argument("--min-language-score", type=float, default=0.98)
    parser.add_argument("--max-minhash-cluster-size", type=int, default=25)
    parser.add_argument("--val-per-mille", type=int, default=5)
    parser.add_argument("--sample-limit", type=int, default=50)
    parser.add_argument("--progress-every", type=int, default=25_000)
    parser.add_argument("--train-bin", type=Path, default=DEFAULT_TRAIN_BIN)
    parser.add_argument("--val-bin", type=Path, default=DEFAULT_VAL_BIN)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--docs-jsonl", type=Path, default=DEFAULT_DOCS_JSONL)
    parser.add_argument("--stats", type=Path, default=DEFAULT_STATS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--accepted-samples", type=Path, default=DEFAULT_ACCEPTED_SAMPLES)
    parser.add_argument("--rejected-samples", type=Path, default=DEFAULT_REJECTED_SAMPLES)
    parser.add_argument("--final-samples", type=Path, default=DEFAULT_FINAL_SAMPLES)
    parser.add_argument("--fineweb-accepted-samples", type=Path, default=DEFAULT_FINEWEB_ACCEPTED)
    parser.add_argument("--fineweb-rejected-samples", type=Path, default=DEFAULT_FINEWEB_REJECTED)
    parser.add_argument("--decision-md", type=Path, default=DEFAULT_DECISION_MD)
    parser.add_argument("--force-v2-3", action="store_true")
    args = parser.parse_args()

    ensure_safe_outputs(args)
    sp = load_sentencepiece(args.tokenizer)
    eos_id = sp.eos_id()
    start = time.time()
    exact_seen: set[str] = set()
    normalized_seen: set[str] = set()
    near_seen: set[str] = set()
    accepted_samples: list[dict[str, Any]] = []
    rejected_samples: list[dict[str, Any]] = []
    fineweb_accepted_samples: list[dict[str, Any]] = []
    fineweb_rejected_samples: list[dict[str, Any]] = []
    final_samples: list[dict[str, Any]] = []
    counters: dict[str, Any] = {
        "train_docs": 0,
        "val_docs": 0,
        "train_tokens": 0,
        "val_tokens": 0,
        "total_words": 0,
        "token_lengths": [],
        "source_mix": collections.defaultdict(
            lambda: {"docs": 0, "tokens": 0, "train_docs": 0, "val_docs": 0, "train_tokens": 0, "val_tokens": 0}
        ),
        "rejection_reasons": collections.Counter(),
    }

    with args.train_bin.open("wb") as train_out, args.val_bin.open("wb") as val_out, args.docs_jsonl.open(
        "w", encoding="utf-8"
    ) as docs_out:
        baseline_tokens = add_existing_sources(
            [
                (args.base_v2_1_docs, BASE_V2_1_SOURCES, "glyph100_dataset_v2_1"),
                (args.base_v2_2_docs, BASE_V2_2_EXTRA_SOURCES, "glyph100_dataset_v2_2"),
            ],
            sp=sp,
            eos_id=eos_id,
            train_out=train_out,
            val_out=val_out,
            docs_out=docs_out,
            exact_seen=exact_seen,
            normalized_seen=normalized_seen,
            near_seen=near_seen,
            counters=counters,
            final_samples=final_samples,
            accepted_samples=accepted_samples,
            sample_limit=args.sample_limit,
            val_per_mille=args.val_per_mille,
        )
        if args.target_fineweb_tokens <= 0:
            args.target_fineweb_tokens = max(0, args.target_total_tokens - baseline_tokens)
        fineweb_stats = stream_fineweb(
            args,
            sp=sp,
            eos_id=eos_id,
            train_out=train_out,
            val_out=val_out,
            docs_out=docs_out,
            exact_seen=exact_seen,
            normalized_seen=normalized_seen,
            near_seen=near_seen,
            counters=counters,
            final_samples=final_samples,
            accepted_samples=accepted_samples,
            rejected_samples=rejected_samples,
            fineweb_accepted_samples=fineweb_accepted_samples,
            fineweb_rejected_samples=fineweb_rejected_samples,
        )

    write_jsonl(args.accepted_samples, accepted_samples[: args.sample_limit])
    write_jsonl(args.rejected_samples, rejected_samples[: args.sample_limit])
    write_jsonl(args.final_samples, final_samples[: args.sample_limit])
    write_jsonl(args.fineweb_accepted_samples, fineweb_accepted_samples[: args.sample_limit])
    write_jsonl(args.fineweb_rejected_samples, fineweb_rejected_samples[: args.sample_limit])

    train_tokens = int(counters["train_tokens"])
    val_tokens = int(counters["val_tokens"])
    total_tokens = train_tokens + val_tokens
    source_mix = {source: dict(item) for source, item in counters["source_mix"].items()}
    wiki_tokens = source_mix.get("wikipedia_pl", {}).get("tokens", 0)
    fineweb_tokens = source_mix.get("fineweb2_pl", {}).get("tokens", 0)
    wikipedia_share = wiki_tokens / max(total_tokens, 1)
    fineweb_share = fineweb_tokens / max(total_tokens, 1)
    stage3_epochs = TRAINING_TOKENS_50K / max(total_tokens, 1)
    if total_tokens >= 280_000_000 and wikipedia_share <= 0.50 and fineweb_share >= 0.35 and stage3_epochs <= 3.2:
        decision_code = "A) v2.3 gotowy, można rozważyć stage 3 / 50k po osobnej zgodzie."
        recommendation = (
            "v2.3 reaches the practical token target with legacy excluded and a much lower Wikipedia share. "
            "Before training, inspect FineWeb2 samples and confirm that web residue is acceptable."
        )
    elif total_tokens >= 180_000_000:
        decision_code = "B) v2.3 lepszy, ale jeszcze wymaga poprawek albo większego targetu."
        recommendation = (
            "v2.3 is larger and more diverse than v2.2, but token count/source mix is still marginal for 50k. "
            "Prefer a larger/cleaner build or a shorter preflight."
        )
    else:
        decision_code = "D) lepiej zrobić krótki preflight, nie 50k."
        recommendation = "v2.3 did not reach enough clean tokens for a 50k run."

    stats = {
        "generated_at": now_utc(),
        "dataset_name": "glyph100_dataset_v2_3",
        "selected_variant": "A_fineweb2_pl_target_300m_wikipedia_max_50_legacy_0",
        "variant": "glyph-100m",
        "scope": "source-aware dataset candidate; no training has been run on it",
        "tokenizer_path": str(args.tokenizer),
        "tokenizer_vocab_size": sp.vocab_size(),
        "train_bin": str(args.train_bin),
        "val_bin": str(args.val_bin),
        "metadata_path": str(args.metadata),
        "docs_jsonl": str(args.docs_jsonl),
        "train_docs": counters["train_docs"],
        "val_docs": counters["val_docs"],
        "train_tokens": train_tokens,
        "val_tokens": val_tokens,
        "total_tokens": total_tokens,
        "token_word_ratio": total_tokens / max(counters["total_words"], 1),
        "word_token_ratio": counters["total_words"] / max(total_tokens, 1),
        "source_mix": source_mix,
        "wikipedia_tokens": wiki_tokens,
        "fineweb2_tokens": fineweb_tokens,
        "wikipedia_share": wikipedia_share,
        "fineweb2_share": fineweb_share,
        "legacy_share": 0.0,
        "fineweb2": fineweb_stats,
        "rejection_reasons": dict(counters["rejection_reasons"].most_common(80)),
        "doc_token_percentiles": {
            "p50": percentile(counters["token_lengths"], 0.50),
            "p75": percentile(counters["token_lengths"], 0.75),
            "p90": percentile(counters["token_lengths"], 0.90),
            "p95": percentile(counters["token_lengths"], 0.95),
            "p99": percentile(counters["token_lengths"], 0.99),
        },
        "stage3_50k_tokens": TRAINING_TOKENS_50K,
        "stage3_50k_epochs": stage3_epochs,
        "stage4_100k_epochs": TRAINING_TOKENS_100K / max(total_tokens, 1),
        "stage5_200k_epochs": TRAINING_TOKENS_200K / max(total_tokens, 1),
        "v2_3_options": build_options(total_tokens),
        "final_samples": final_samples,
        "decision_code": decision_code,
        "recommendation": recommendation,
        "elapsed_seconds": time.time() - start,
    }

    args.stats.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    args.report.write_text(render_report(stats), encoding="utf-8")
    args.metadata.write_text(
        json.dumps(
            {
                "variant": "glyph-100m",
                "dataset_name": "glyph100_dataset_v2_3",
                "selected_variant": stats["selected_variant"],
                "scope": stats["scope"],
                "train_bin": str(args.train_bin),
                "val_bin": str(args.val_bin),
                "docs_jsonl": str(args.docs_jsonl),
                "tokenizer": str(args.tokenizer),
                "vocab_size": sp.vocab_size(),
                "train_docs": counters["train_docs"],
                "val_docs": counters["val_docs"],
                "train_tokens": train_tokens,
                "val_tokens": val_tokens,
                "total_tokens": total_tokens,
                "source_mix": source_mix,
                "wikipedia_share": wikipedia_share,
                "fineweb2_share": fineweb_share,
                "legacy_share": 0.0,
                "stage3_50k_epochs": stage3_epochs,
                "created_at": stats["generated_at"],
                "stats_json": str(args.stats),
                "report": str(args.report),
                "split_note": (
                    "document-level stable source/doc hash split with at least one validation document per source; "
                    "no legacy source included"
                ),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    args.decision_md.write_text(render_decision(stats), encoding="utf-8")
    print(
        json.dumps(
            {
                "dataset_name": "glyph100_dataset_v2_3",
                "total_tokens": total_tokens,
                "wikipedia_share": wikipedia_share,
                "fineweb2_share": fineweb_share,
                "stage3_50k_epochs": stage3_epochs,
                "decision": decision_code,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)


if __name__ == "__main__":
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    main()
