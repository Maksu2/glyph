#!/usr/bin/env python3
"""Controlled access/probe workflow for FinetextPL-Edu.

This script is deliberately bounded. It never downloads the full dataset and it
never stores Hugging Face tokens. Authentication, if needed, must come from the
user's normal Hugging Face login or HF_TOKEN environment variable.
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
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from glyph100_dataset_v2_filter import (  # noqa: E402
    FilterConfig,
    evaluate_document,
    percentile,
    sha1_text,
    stable_bucket,
    text_metrics,
    truncate_text,
)


DEFAULT_REPO = "FinetextPL/FinetextPL-Edu"
DEFAULT_TOKENIZER = Path("data/processed/tokenizer.model")
DEFAULT_REPORT = Path("reports/glyph100_finetext_access_check.md")
DEFAULT_JSON = Path("reports/glyph100_finetext_access_check.json")
DEFAULT_ACCEPTED = Path("reports/glyph100_finetext_probe_samples_accepted.jsonl")
DEFAULT_REJECTED = Path("reports/glyph100_finetext_probe_samples_rejected.jsonl")
DEFAULT_RANDOM = Path("reports/glyph100_finetext_probe_samples_random.jsonl")

TOKENS_PER_STEP = 4 * 512 * 8
STAGE3_TOKENS = 50_000 * TOKENS_PER_STEP

HTML_RE = re.compile(r"<[^>]+>")
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
LINK_LINE_RE = re.compile(r"(?im)^\s*(https?://|www\.|\[[^\]]+\]\([^)]+\))")
PRICE_RE = re.compile(r"\b\d+([,.]\d+)?\s?(zł|pln|eur|usd)\b", re.IGNORECASE)
TABLE_LINE_RE = re.compile(r"(?m)^\s*[\w\s.-]{1,50}\s{2,}[\w\s.,:-]{1,80}\s{2,}")
LIST_LINE_RE = re.compile(r"(?m)^\s*(?:[-*•]|\d+[.)])\s+")
MENU_PATTERNS = [
    "strona główna",
    "czytaj więcej",
    "linki zewnętrzne",
    "zobacz też",
    "polityka prywatności",
    "regulamin",
    "cookies",
    "newsletter",
    "logowanie",
    "zarejestruj",
]
FORUM_PATTERNS = [
    "postautor",
    "temat postu",
    "napisał/a",
    "odpowiedz:",
    "cytuj:",
    "dołączył:",
]
COMMERCE_PATTERNS = [
    "dodaj do koszyka",
    "koszyk",
    "darmowa dostawa",
    "koszt wysyłki",
    "sklep internetowy",
    "zamów teraz",
    "opinie klientów",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_sentencepiece(tokenizer: Path):
    try:
        import sentencepiece as spm
    except ImportError as exc:
        raise SystemExit("sentencepiece is required. Use ./.venv/bin/python.") from exc
    sp = spm.SentencePieceProcessor()
    sp.load(str(tokenizer))
    return sp


def json_dump_line(handle, obj: dict[str, Any]) -> None:
    handle.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")


def sample_payload(row: dict[str, Any], text: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "id": str(row.get("id", "")),
        "dataset_source": row.get("dataset_source"),
        "prediction": row.get("prediction"),
        "url": row.get("url", ""),
        "file_path": row.get("file_path", ""),
        "text": truncate_text(text, 1200),
    }
    if extra:
        payload.update(extra)
    return payload


def keep_sample(samples: list[dict[str, Any]], item: dict[str, Any], key: str, limit: int) -> None:
    if limit <= 0:
        return
    if len(samples) < limit:
        samples.append(item)
        return
    bucket = stable_bucket(key, 1_000_000)
    if bucket < limit * 40:
        samples[bucket % limit] = item


def finetext_extra_reasons(text: str, row: dict[str, Any]) -> list[str]:
    lower = text.lower()
    reasons: list[str] = []
    if len(HTML_RE.findall(text)) >= 2:
        reasons.append("html_present")
    if len(URL_RE.findall(text)) >= 3:
        reasons.append("url_spam")
    if len(LINK_LINE_RE.findall(text)) >= 8:
        reasons.append("link_list")
    if len(LIST_LINE_RE.findall(text)) >= 20:
        reasons.append("list_heavy")
    if len(TABLE_LINE_RE.findall(text)) >= 15 or text.count("|") >= 20:
        reasons.append("table_or_admin_heavy")
    if any(pattern in lower for pattern in COMMERCE_PATTERNS) or len(PRICE_RE.findall(text)) >= 6:
        reasons.append("commerce_or_prices")
    if any(pattern in lower for pattern in FORUM_PATTERNS):
        reasons.append("forum_or_comments")
    if sum(1 for pattern in MENU_PATTERNS if pattern in lower) >= 3:
        reasons.append("menu_or_boilerplate")
    if row.get("dataset_source") == "finepdfs" and row.get("is_truncated") is True:
        reasons.append("finepdf_truncated")
    lid_score = row.get("full_doc_lid_score")
    if isinstance(lid_score, (int, float)) and lid_score < 0.80:
        reasons.append("low_pdf_language_score")
    return reasons


def metadata_probe(repo: str) -> dict[str, Any]:
    from huggingface_hub import HfApi, hf_hub_download

    api = HfApi()
    out: dict[str, Any] = {"repo": repo, "metadata_error": None, "readme_error": None}
    try:
        info = api.dataset_info(repo, files_metadata=True)
        siblings = info.siblings or []
        data_files = [s for s in siblings if str(s.rfilename).endswith(".parquet")]
        out.update(
            {
                "id": info.id,
                "private": bool(info.private),
                "gated": getattr(info, "gated", None),
                "disabled": bool(getattr(info, "disabled", False)),
                "tags": info.tags or [],
                "downloads": getattr(info, "downloads", None),
                "likes": getattr(info, "likes", None),
                "siblings_count": len(siblings),
                "parquet_files": len(data_files),
                "total_size_bytes": sum((getattr(s, "size", 0) or 0) for s in siblings),
                "parquet_size_bytes": sum((getattr(s, "size", 0) or 0) for s in data_files),
                "first_files": [
                    {"name": s.rfilename, "size": getattr(s, "size", None)}
                    for s in siblings[:16]
                ],
            }
        )
    except Exception as exc:  # noqa: BLE001 - report needs the access error
        out["metadata_error"] = f"{type(exc).__name__}: {str(exc)[:1000]}"

    try:
        readme_path = hf_hub_download(repo, "README.md", repo_type="dataset")
        readme = Path(readme_path).read_text(encoding="utf-8", errors="replace")
        out["readme_excerpt"] = truncate_text(readme, 5000)
        out["card_claims"] = {
            "documents": "~160M Polish documents",
            "sources": "FineWeb2 + FinePDFs",
            "recommended_filter": "prediction >= 2.5",
            "fields": [
                "text",
                "prediction",
                "dataset_source",
                "id",
                "file_path",
                "url",
                "date",
                "dump",
                "offset",
                "full_doc_lid",
                "full_doc_lid_score",
                "is_truncated",
            ],
        }
    except Exception as exc:  # noqa: BLE001
        out["readme_error"] = f"{type(exc).__name__}: {str(exc)[:1000]}"
    return out


def stream_probe(args: argparse.Namespace, sp) -> dict[str, Any]:
    from datasets import load_dataset

    exact_seen: set[str] = set()
    normalized_seen: set[str] = set()
    near_seen: set[str] = set()
    accepted_samples: list[dict[str, Any]] = []
    rejected_samples: list[dict[str, Any]] = []
    random_samples: list[dict[str, Any]] = []
    rejection_reasons: collections.Counter[str] = collections.Counter()
    source_counts: collections.Counter[str] = collections.Counter()
    source_tokens: collections.Counter[str] = collections.Counter()
    prediction_values: list[float] = []
    accepted_token_lengths: list[int] = []
    raw_seen = accepted = rejected = 0
    columns: list[str] = []

    config = FilterConfig(
        min_words=args.min_words,
        max_chars=args.max_chars,
        min_alpha_ratio=0.56,
        min_polish_stopword_ratio=0.018,
        max_punct_symbol_ratio=0.14,
        max_repetition_score=0.040,
        min_unique_word_ratio=0.22,
        max_word_frequency_ratio=0.13,
        max_urls=2,
        max_line_length=18_000,
    )

    ds = load_dataset(args.repo, split=args.split, streaming=True)
    start = time.time()
    for row in ds:
        raw_seen += 1
        if not columns:
            columns = list(row.keys())
        if raw_seen > args.max_raw_docs:
            break

        text = row.get("text") or ""
        prediction = row.get("prediction")
        if isinstance(prediction, (int, float)):
            prediction_values.append(float(prediction))
        if args.min_prediction is not None and (not isinstance(prediction, (int, float)) or prediction < args.min_prediction):
            continue

        keep_sample(random_samples, sample_payload(row, text), str(row.get("id", raw_seen)), args.sample_limit)
        extra = finetext_extra_reasons(text, row)
        result = evaluate_document(
            text,
            source="finetextpl_edu",
            config=config,
            exact_seen=exact_seen,
            normalized_seen=normalized_seen,
            near_seen=near_seen,
        )
        reasons = extra + result.reasons
        if reasons:
            rejected += 1
            for reason in reasons:
                rejection_reasons[reason] += 1
            keep_sample(
                rejected_samples,
                sample_payload(
                    row,
                    text,
                    {
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
                            ]
                        },
                    },
                ),
                f"{row.get('id', raw_seen)}:reject",
                args.sample_limit,
            )
            continue

        ids = sp.encode(result.text, out_type=int)
        ids.append(sp.eos_id())
        accepted += 1
        accepted_token_lengths.append(len(ids))
        source = str(row.get("dataset_source", "unknown"))
        source_counts[source] += 1
        source_tokens[source] += len(ids)
        exact_seen.add(str(result.metrics.get("exact_hash")))
        normalized_seen.add(str(result.metrics.get("normalized_hash")))
        near_seen.add(str(result.metrics.get("near_hash")))
        keep_sample(
            accepted_samples,
            sample_payload(
                row,
                result.text,
                {
                    "token_count": len(ids),
                    "quality_score": round(float(result.metrics.get("quality_score", 0)), 4),
                    "words": result.metrics.get("words"),
                },
            ),
            str(row.get("id", raw_seen)),
            args.sample_limit,
        )
        if accepted >= args.max_accepted_docs:
            break

    total_tokens = sum(accepted_token_lengths)
    return {
        "stream_error": None,
        "columns": columns,
        "raw_seen": raw_seen,
        "accepted_docs": accepted,
        "rejected_docs_after_threshold": rejected,
        "min_prediction": args.min_prediction,
        "accepted_tokens": total_tokens,
        "tokens_per_accepted_doc_avg": total_tokens / max(accepted, 1),
        "accepted_token_percentiles": {
            "p50": percentile(accepted_token_lengths, 0.50),
            "p75": percentile(accepted_token_lengths, 0.75),
            "p90": percentile(accepted_token_lengths, 0.90),
            "p95": percentile(accepted_token_lengths, 0.95),
            "p99": percentile(accepted_token_lengths, 0.99),
        },
        "prediction_percentiles_seen": {
            "p50": percentile(prediction_values, 0.50),
            "p75": percentile(prediction_values, 0.75),
            "p90": percentile(prediction_values, 0.90),
            "p95": percentile(prediction_values, 0.95),
        },
        "source_counts": dict(source_counts.most_common()),
        "source_tokens": dict(source_tokens.most_common()),
        "rejection_reasons": dict(rejection_reasons.most_common(40)),
        "accepted_samples": accepted_samples,
        "rejected_samples": rejected_samples,
        "random_samples": random_samples,
        "elapsed_seconds": time.time() - start,
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            json_dump_line(handle, row)


def render_samples(samples: list[dict[str, Any]], limit: int = 12) -> str:
    if not samples:
        return "_none_"
    out = []
    for i, sample in enumerate(samples[:limit], 1):
        title = sample.get("id") or sample.get("url") or sample.get("file_path") or "sample"
        out.append(
            f"{i}. `{sample.get('dataset_source', 'unknown')}` pred={sample.get('prediction')} {title}\n\n"
            f"   {sample.get('text', '')}"
        )
    return "\n\n".join(out)


def build_plan_variants(sample: dict[str, Any]) -> list[dict[str, Any]]:
    # Conservative defaults until an actual accepted-token estimate is available.
    finetext_ok = bool(sample.get("accepted_docs"))
    variants = [
        {
            "variant": "A",
            "description": "Wikipedia max 50%, Finetext/Edu + books/source texts as the rest",
            "target_tokens": 300_000_000,
            "source_mix": {
                "wikipedia_pl": 150_000_000,
                "finetextpl_edu": 130_000_000,
                "wolne_lektury_wikisource_wikibooks_allegro": 20_000_000,
            },
            "stage3_50k_epochs": STAGE3_TOKENS / 300_000_000,
            "risk": "Good first target if Finetext samples pass filters; still only ~2.7 epochs for 50k.",
            "recommended": finetext_ok,
        },
        {
            "variant": "B",
            "description": "Wikipedia max 40%, Finetext/Edu as main non-Wiki source",
            "target_tokens": 500_000_000,
            "source_mix": {
                "wikipedia_pl": 200_000_000,
                "finetextpl_edu": 275_000_000,
                "books_source_texts_other": 25_000_000,
            },
            "stage3_50k_epochs": STAGE3_TOKENS / 500_000_000,
            "risk": "Best long-run shape, but only after bounded Finetext sampling confirms quality and storage plan.",
            "recommended": False,
        },
        {
            "variant": "C",
            "description": "Smaller very-clean 200-300M set if Finetext quality is uneven",
            "target_tokens": 250_000_000,
            "source_mix": {
                "wikipedia_pl": 100_000_000,
                "finetextpl_edu_high_score": 125_000_000,
                "books_source_texts_other": 25_000_000,
            },
            "stage3_50k_epochs": STAGE3_TOKENS / 250_000_000,
            "risk": "Quality-first fallback; stage 3 becomes ~3.3 epochs, acceptable but not ideal.",
            "recommended": False,
        },
        {
            "variant": "D",
            "description": "No Finetext access: only v2.1/v2.2 short preflight, no 50k",
            "target_tokens": 37_000_000,
            "source_mix": {"glyph100_dataset_v2_2": 37_000_000},
            "stage3_50k_epochs": STAGE3_TOKENS / 37_000_000,
            "risk": "Too many epochs for 50k; useful only for a short continuation sanity probe.",
            "recommended": not finetext_ok,
        },
    ]
    return variants


def detect_local_hf_auth() -> bool:
    """Return whether Hugging Face auth is available without exposing tokens."""
    if os.environ.get("HF_TOKEN"):
        return True
    try:
        from huggingface_hub import HfApi

        return bool(HfApi().whoami())
    except Exception:
        return False


def render_report(payload: dict[str, Any]) -> str:
    metadata = payload["metadata"]
    stream = payload["stream"]
    variants = payload["v2_3_variants"]
    variant_rows = "\n".join(
        f"| {v['variant']} | {v['target_tokens']:,} | {v['stage3_50k_epochs']:.2f} | {v['recommended']} | {v['risk']} |"
        for v in variants
    )
    source_rows = "\n".join(
        f"| {source} | {count:,} | {stream.get('source_tokens', {}).get(source, 0):,} |"
        for source, count in (stream.get("source_counts") or {}).items()
    )
    files_size = metadata.get("parquet_size_bytes") or metadata.get("total_size_bytes") or 0
    size_gb = files_size / 1024 / 1024 / 1024
    if stream.get("stream_error"):
        stream_status = f"not sampled: `{stream['stream_error']}`"
    elif stream.get("accepted_docs"):
        stream_status = f"sampled {stream['accepted_docs']:,} accepted docs from {stream['raw_seen']:,} streamed rows"
    else:
        stream_status = "metadata-only; no accepted sample was collected"
    return f"""# Glyph-100M FinetextPL-Edu Access Check

Generated: {payload["generated_at"]}

No training was started. No full dataset download was started. No Hugging Face token was written to the repo or printed.

## Access

- dataset: `{payload["repo"]}`
- URL: https://huggingface.co/datasets/{payload["repo"]}
- gated: `{metadata.get("gated")}`
- private: `{metadata.get("private")}`
- disabled: `{metadata.get("disabled")}`
- parquet files: {metadata.get("parquet_files", "unknown")}
- data size: ~{size_gb:.1f} GB
- local HF auth detected: `{payload["local_auth_present"]}` (boolean only; token value not read or printed)
- stream status: {stream_status}

## Dataset Card Facts

- claimed size: ~160M Polish documents
- sources: FineWeb2 + FinePDFs
- key field for pretraining: `text`
- quality score field: `prediction`
- recommended first threshold: `prediction >= 2.5`
- source field: `dataset_source`
- license tag: `odc-by`

## Stream Probe

- raw rows seen: {stream.get("raw_seen", 0):,}
- accepted docs: {stream.get("accepted_docs", 0):,}
- rejected docs after threshold: {stream.get("rejected_docs_after_threshold", 0):,}
- accepted tokens: {stream.get("accepted_tokens", 0):,}
- avg tokens / accepted doc: {stream.get("tokens_per_accepted_doc_avg", 0):.1f}
- columns: `{stream.get("columns", [])}`

## Source Counts In Probe

| source | docs | tokens |
|---|---:|---:|
{source_rows or '| — | — | — |'}

## Rejection Reasons

```json
{json.dumps(stream.get("rejection_reasons", {}), ensure_ascii=False, indent=2)}
```

## Accepted Samples

{render_samples(stream.get("accepted_samples", []))}

## Rejected Samples

{render_samples(stream.get("rejected_samples", []))}

## v2.3 Options

| variant | target tokens | 50k epochs | recommended now | risk |
|---|---:|---:|---|---|
{variant_rows}

## Manual Access Instructions

If stream access failed:

1. Open https://huggingface.co/datasets/{payload["repo"]}.
2. Log in to Hugging Face.
3. Read and accept the gated dataset terms.
4. Prefer `huggingface-cli login` on the homelab, or run a command with `HF_TOKEN` in the environment.
5. Do not paste the token into repo files, scripts or logs.
6. Re-run:

```bash
cd /home/maksu/ai-model
./.venv/bin/python scripts/glyph100_finetext_probe.py --max-raw-docs 10000 --max-accepted-docs 1000
```

## Recommendation

{payload["recommendation"]}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe FinetextPL-Edu safely without full download")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--split", default="train")
    parser.add_argument("--tokenizer", type=Path, default=DEFAULT_TOKENIZER)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--accepted-samples", type=Path, default=DEFAULT_ACCEPTED)
    parser.add_argument("--rejected-samples", type=Path, default=DEFAULT_REJECTED)
    parser.add_argument("--random-samples", type=Path, default=DEFAULT_RANDOM)
    parser.add_argument("--max-raw-docs", type=int, default=10_000)
    parser.add_argument("--max-accepted-docs", type=int, default=1_000)
    parser.add_argument("--sample-limit", type=int, default=50)
    parser.add_argument("--min-prediction", type=float, default=2.5)
    parser.add_argument("--min-words", type=int, default=80)
    parser.add_argument("--max-chars", type=int, default=80_000)
    parser.add_argument("--metadata-only", action="store_true")
    args = parser.parse_args()

    metadata = metadata_probe(args.repo)
    stream: dict[str, Any]
    if args.metadata_only:
        stream = {"stream_error": "metadata_only_requested", "accepted_samples": [], "rejected_samples": [], "random_samples": []}
    else:
        try:
            sp = load_sentencepiece(args.tokenizer)
            stream = stream_probe(args, sp)
        except Exception as exc:  # noqa: BLE001 - access check should report failures
            stream = {
                "stream_error": f"{type(exc).__name__}: {str(exc)[:1500]}",
                "accepted_samples": [],
                "rejected_samples": [],
                "random_samples": [],
            }

    if stream.get("accepted_docs"):
        recommendation = (
            "A) uzyskać/utrzymać dostęp do Finetext i budować glyph100_dataset_v2_3, "
            "starting with a bounded 200-300M token build and source-aware reports."
        )
    elif metadata.get("gated"):
        recommendation = (
            "A) najpierw uzyskać ręczny dostęp do FinetextPL-Edu on Hugging Face, then rerun the bounded probe. "
            "Do not train or download the full dataset yet."
        )
    else:
        recommendation = (
            "B/C) probe did not produce usable samples; inspect the access error and look for alternate clean sources "
            "or only run a short v2.1/v2.2 preflight."
        )

    payload = {
        "generated_at": now_utc(),
        "repo": args.repo,
        "local_auth_present": detect_local_hf_auth(),
        "probe_limits": {
            "max_raw_docs": args.max_raw_docs,
            "max_accepted_docs": args.max_accepted_docs,
            "min_prediction": args.min_prediction,
        },
        "metadata": metadata,
        "stream": stream,
        "v2_3_variants": build_plan_variants(stream),
        "recommendation": recommendation,
    }

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    args.report.write_text(render_report(payload), encoding="utf-8")
    write_jsonl(args.accepted_samples, stream.get("accepted_samples", []))
    write_jsonl(args.rejected_samples, stream.get("rejected_samples", []))
    write_jsonl(args.random_samples, stream.get("random_samples", []))
    print(
        json.dumps(
            {
                "repo": args.repo,
                "gated": metadata.get("gated"),
                "stream_error": stream.get("stream_error"),
                "accepted_docs": stream.get("accepted_docs", 0),
                "accepted_tokens": stream.get("accepted_tokens", 0),
                "report": str(args.report),
                "recommendation": recommendation,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
