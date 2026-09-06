#!/usr/bin/env python3
"""Bounded FineWeb2 PL probe for Glyph-100M dataset v2.3.

This script intentionally does not build a training dataset and does not train
anything. It samples a controlled number of streamed rows, applies the existing
Glyph filters plus FineWeb-specific checks, and writes human-readable reports.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys
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
    truncate_text,
)
from glyph100_dataset_v2_2_build import (  # noqa: E402
    common_bad_pattern_reasons,
    keep_sample,
    word_count,
)


DEFAULT_REPO = "ReactiveAI/fineweb-2-pol-latest"
DEFAULT_TOKENIZER = Path("data/processed/tokenizer.model")
DEFAULT_REPORT = Path("reports/glyph100_fineweb2_pl_probe.md")
DEFAULT_JSON = Path("reports/glyph100_fineweb2_pl_probe.json")
DEFAULT_ACCEPTED = Path("reports/glyph100_fineweb2_pl_probe_samples_accepted.jsonl")
DEFAULT_REJECTED = Path("reports/glyph100_fineweb2_pl_probe_samples_rejected.jsonl")
DEFAULT_RANDOM = Path("reports/glyph100_fineweb2_pl_probe_samples_random.jsonl")

TOKENS_PER_STEP = 4 * 512 * 8
STAGE3_TOKENS = 50_000 * TOKENS_PER_STEP

PRICE_RE = re.compile(r"\b\d+([,.]\d+)?\s?(zł|pln|eur|usd)\b", re.IGNORECASE)
LIST_LINE_RE = re.compile(r"(?m)^\s*(?:[-*•]|\d+[.)])\s+")
LINK_LINE_RE = re.compile(r"(?im)^\s*(https?://|www\.|\[[^\]]+\]\([^)]+\))")
CONTACT_URL_RE = re.compile(
    r"/(kontakt|contact|regulamin|polityka-prywatnosci|privacy|cookies|koszyk|cart|checkout|produkt|product|lp,|category|kategoria)(/|$|[-_])",
    re.IGNORECASE,
)
FORUM_URL_RE = re.compile(r"(^|[./_-])(forum[a-z0-9-]*|fora|zapytaj|pytania|odpowiedzi)([./_-]|$)", re.IGNORECASE)
LANDING_PRODUCT_URL_RE = re.compile(r"/(lp[,0-9-]|produkt|product|sklep|oferta)(/|$|[-_,0-9])", re.IGNORECASE)
GAMBLING_RE = re.compile(
    r"\b(kasyn[ao]|sloty|spiny|ruletka|blackjack|bonus bez depozytu|automaty do gry|bukmacher)\b",
    re.IGNORECASE,
)
TDM_RE = re.compile(r"systematyczne pobieranie treści|text and data mining|eksploracja tekstu i danych", re.IGNORECASE)
SEO_PHRASES = [
    "pozycjonowanie",
    "najlepsza oferta",
    "sprawdź ofertę",
    "skontaktuj się z nami",
    "zapraszamy do kontaktu",
    "nasza firma",
    "świadczymy usługi",
    "profesjonalne usługi",
]
NAV_PHRASES = [
    "strona główna",
    "menu",
    "czytaj więcej",
    "zobacz także",
    "linki zewnętrzne",
    "polityka prywatności",
    "regulamin",
    "cookies",
    "newsletter",
    "logowanie",
    "rejestracja",
]
FORUM_PHRASES = [
    "postautor",
    "napisał/a",
    "odpowiedz:",
    "cytuj:",
    "dołączył:",
    "użytkownik forum",
]
COMMERCE_PHRASES = [
    "dodaj do koszyka",
    "koszyk",
    "darmowa dostawa",
    "koszt wysyłki",
    "sklep internetowy",
    "zamów teraz",
    "opinie klientów",
    "opinie o produkcie",
    "dane techniczne",
    "kod produktu",
    "w magazynie",
    "czas i koszty dostawy",
    "płatność przed wysyłką",
    "wyłącznie zalogowani klienci",
    "kliknij tu, aby skorzystać",
    "sprawdź ofertę",
    "skorzystaj z oferty",
]
CONTACT_PHRASES = [
    "aktualne dane kontaktowe",
    "formularza kontaktowego",
    "biura obsługi klienta",
    "kontakt telefoniczny",
    "kontakt z firmą",
    "skorzystaj z pomocy konsultantów",
]
DONATION_PHRASES = [
    "przelej darowiznę",
    "podarować mi jakiś prezent",
    "lista prezentów",
    "ogólną pomoc",
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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            json_dump_line(handle, row)


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
                    for s in data_files[:20]
                ],
            }
        )
    except Exception as exc:  # noqa: BLE001 - report access failures
        out["metadata_error"] = f"{type(exc).__name__}: {str(exc)[:1200]}"
    try:
        readme_path = hf_hub_download(repo, "README.md", repo_type="dataset")
        readme = Path(readme_path).read_text(encoding="utf-8", errors="replace")
        out["readme_excerpt"] = truncate_text(readme, 5000)
    except Exception as exc:  # noqa: BLE001
        out["readme_error"] = f"{type(exc).__name__}: {str(exc)[:1200]}"
    return out


def fineweb_config() -> FilterConfig:
    return FilterConfig(
        min_words=90,
        max_chars=80_000,
        min_alpha_ratio=0.56,
        min_polish_stopword_ratio=0.020,
        max_punct_symbol_ratio=0.14,
        max_repetition_score=0.035,
        min_unique_word_ratio=0.23,
        max_word_frequency_ratio=0.11,
        max_urls=1,
        max_line_length=18_000,
    )


def fineweb_extra_reasons(text: str, row: dict[str, Any], args: argparse.Namespace) -> list[str]:
    lower = text.lower()
    url = str(row.get("url") or "")
    reasons: list[str] = []
    language = str(row.get("language") or "").lower()
    if language and language not in {"pol", "pl", "polish"}:
        reasons.append("non_polish_language_field")
    score = row.get("language_score")
    if isinstance(score, (int, float)) and score < args.min_language_score:
        reasons.append("low_language_score")
    if str(row.get("language_script") or "").lower() not in {"", "latn"}:
        reasons.append("non_latin_script")
    cluster = row.get("minhash_cluster_size")
    if isinstance(cluster, int) and cluster > args.max_minhash_cluster_size:
        reasons.append("large_minhash_cluster")
    if CONTACT_URL_RE.search(url):
        reasons.append("contact_commerce_policy_url")
    if LANDING_PRODUCT_URL_RE.search(url):
        reasons.append("landing_or_product_url")
    if FORUM_URL_RE.search(url):
        reasons.append("forum_or_qa_url")
    if GAMBLING_RE.search(text) or GAMBLING_RE.search(url):
        reasons.append("gambling_spam")
    if TDM_RE.search(text):
        reasons.append("tdm_legal_boilerplate")
    if sum(1 for phrase in NAV_PHRASES if phrase in lower) >= 3:
        reasons.append("navigation_or_boilerplate")
    if sum(1 for phrase in SEO_PHRASES if phrase in lower) >= 3:
        reasons.append("seo_service_language")
    if any(phrase in lower for phrase in FORUM_PHRASES):
        reasons.append("forum_or_comments")
    if sum(1 for phrase in CONTACT_PHRASES if phrase in lower) >= 2:
        reasons.append("contact_page_content")
    if any(phrase in lower for phrase in DONATION_PHRASES):
        reasons.append("donation_page")
    commerce_hits = [phrase for phrase in COMMERCE_PHRASES if phrase in lower]
    if commerce_hits or len(PRICE_RE.findall(text)) >= 5:
        reasons.append("commerce_or_prices")
    if len(commerce_hits) >= 2:
        reasons.append("commerce_page_structure")
    if len(LINK_LINE_RE.findall(text)) >= 6:
        reasons.append("link_list")
    if len(LIST_LINE_RE.findall(text)) >= 24 and word_count(text) < 500:
        reasons.append("list_heavy_short_doc")
    return reasons


def row_id(row: dict[str, Any], idx: int) -> str:
    return str(row.get("id") or sha1_text(f"{idx}:{row.get('url','')}:{row.get('text','')[:200]}")[:24])


def sample_payload(row: dict[str, Any], text: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "id": str(row.get("id") or ""),
        "url": row.get("url") or "",
        "language": row.get("language") or "",
        "language_score": row.get("language_score"),
        "minhash_cluster_size": row.get("minhash_cluster_size"),
        "dump": row.get("dump") or "",
        "file_path": row.get("file_path") or "",
        "text": truncate_text(text, 1200),
    }
    if extra:
        payload.update(extra)
    return payload


def stream_probe(args: argparse.Namespace, sp) -> dict[str, Any]:
    from datasets import load_dataset

    config = fineweb_config()
    exact_seen: set[str] = set()
    normalized_seen: set[str] = set()
    near_seen: set[str] = set()
    source_counts: collections.Counter[str] = collections.Counter()
    rejection_reasons: collections.Counter[str] = collections.Counter()
    accepted_token_lengths: list[int] = []
    accepted_word_lengths: list[int] = []
    accepted_samples: list[dict[str, Any]] = []
    rejected_samples: list[dict[str, Any]] = []
    random_samples: list[dict[str, Any]] = []
    fields_seen: set[str] = set()
    url_domains: collections.Counter[str] = collections.Counter()
    raw_seen = 0
    accepted = 0
    rejected = 0
    eos_id = sp.eos_id()

    dataset = load_dataset(args.repo, args.config, split=args.split, streaming=True) if args.config else load_dataset(
        args.repo,
        split=args.split,
        streaming=True,
    )
    for idx, row in enumerate(dataset, 1):
        raw_seen += 1
        fields_seen.update(row.keys())
        text = row.get("text") or ""
        source_key = str(row.get("dump") or "fineweb2_pl")
        source_counts[source_key] += 1
        url = str(row.get("url") or "")
        if url:
            domain = re.sub(r"^https?://", "", url).split("/", 1)[0].lower()
            url_domains[domain] += 1
        keep_sample(random_samples, sample_payload(row, text), f"random:{row_id(row, idx)}", args.sample_limit)

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
                rejection_reasons[reason] += 1
            keep_sample(
                rejected_samples,
                sample_payload(
                    row,
                    result.text or text,
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
                                "suspicious_patterns",
                            ]
                        },
                    },
                ),
                f"reject:{row_id(row, idx)}",
                args.sample_limit,
            )
        else:
            ids = sp.encode(result.text, out_type=int)
            ids.append(eos_id)
            accepted += 1
            accepted_token_lengths.append(len(ids))
            accepted_word_lengths.append(word_count(result.text))
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
                        "word_count": word_count(result.text),
                        "quality_score": round(float(result.metrics.get("quality_score", 0.0)), 4),
                    },
                ),
                f"accept:{row_id(row, idx)}",
                args.sample_limit,
            )
        if args.max_accepted_docs and accepted >= args.max_accepted_docs:
            break
        if args.max_raw_docs and raw_seen >= args.max_raw_docs:
            break

    accepted_tokens = sum(accepted_token_lengths)
    return {
        "raw_seen": raw_seen,
        "accepted_docs": accepted,
        "rejected_docs": rejected,
        "accepted_tokens": accepted_tokens,
        "acceptance_rate": accepted / max(raw_seen, 1),
        "fields": sorted(fields_seen),
        "source_counts": dict(source_counts.most_common(20)),
        "top_url_domains": dict(url_domains.most_common(25)),
        "rejection_reasons": dict(rejection_reasons.most_common(50)),
        "tokens_per_accepted_doc_avg": accepted_tokens / max(accepted, 1),
        "words_per_accepted_doc_avg": sum(accepted_word_lengths) / max(accepted, 1),
        "token_word_ratio": accepted_tokens / max(sum(accepted_word_lengths), 1),
        "accepted_token_percentiles": {
            "p50": percentile(accepted_token_lengths, 0.50),
            "p75": percentile(accepted_token_lengths, 0.75),
            "p90": percentile(accepted_token_lengths, 0.90),
            "p95": percentile(accepted_token_lengths, 0.95),
            "p99": percentile(accepted_token_lengths, 0.99),
        },
        "accepted_samples": accepted_samples,
        "rejected_samples": rejected_samples,
        "random_samples": random_samples,
    }


def build_options(stream: dict[str, Any]) -> list[dict[str, Any]]:
    accepted = bool(stream.get("accepted_docs"))
    return [
        {
            "variant": "A",
            "description": "target ~300M tokens, Wikipedia <=50%, FineWeb2 PL as main non-Wiki source",
            "target_tokens": 300_000_000,
            "stage3_50k_epochs": STAGE3_TOKENS / 300_000_000,
            "recommended": accepted,
            "risk": "Good first v2.3 target if accepted samples remain mostly continuous Polish prose.",
        },
        {
            "variant": "B",
            "description": "target ~500M tokens, Wikipedia <=40-50%, more FineWeb2 PL",
            "target_tokens": 500_000_000,
            "stage3_50k_epochs": STAGE3_TOKENS / 500_000_000,
            "recommended": False,
            "risk": "Better epoch math, but only after FineWeb2 residue looks acceptable at larger sample sizes.",
        },
        {
            "variant": "C",
            "description": "more conservative clean build, sharper filters, fewer tokens",
            "target_tokens": 200_000_000,
            "stage3_50k_epochs": STAGE3_TOKENS / 200_000_000,
            "recommended": False,
            "risk": "Quality-first fallback; still about 4.1 epochs for stage 3.",
        },
        {
            "variant": "D",
            "description": "do not build v2.3 if FineWeb2 PL probe is weak",
            "target_tokens": 37_000_000,
            "stage3_50k_epochs": STAGE3_TOKENS / 37_000_000,
            "recommended": not accepted,
            "risk": "No good long-run dataset without a larger clean source.",
        },
    ]


def render_samples(samples: list[dict[str, Any]], limit: int = 12) -> str:
    if not samples:
        return "_none_"
    chunks = []
    for i, sample in enumerate(samples[:limit], 1):
        chunks.append(
            f"{i}. `{sample.get('url', '')}` tokens={sample.get('token_count', 'n/a')} "
            f"score={sample.get('quality_score', 'n/a')}\n\n"
            f"   {sample.get('text', '')}"
        )
    return "\n\n".join(chunks)


def render_report(payload: dict[str, Any]) -> str:
    metadata = payload["metadata"]
    stream = payload["stream"]
    size_gb = (metadata.get("parquet_size_bytes") or metadata.get("total_size_bytes") or 0) / 1024 / 1024 / 1024
    if stream.get("stream_error"):
        stream_status = f"failed: `{stream['stream_error']}`"
    elif stream.get("accepted_docs"):
        stream_status = (
            f"sampled {stream['raw_seen']:,} rows, accepted {stream['accepted_docs']:,} "
            f"({stream['acceptance_rate']:.1%})"
        )
    else:
        stream_status = "metadata-only; no sample collected"
    options_rows = "\n".join(
        f"| {item['variant']} | {item['target_tokens']:,} | {item['stage3_50k_epochs']:.2f} | "
        f"{item['recommended']} | {item['risk']} |"
        for item in payload["v2_3_options"]
    )
    return f"""# Glyph-100M FineWeb2 PL Probe

Generated: {payload["generated_at"]}

No training was started. No v2.3 dataset was built by this probe.

## Access

- dataset: `{payload["repo"]}`
- gated: `{metadata.get("gated")}`
- private: `{metadata.get("private")}`
- disabled: `{metadata.get("disabled")}`
- parquet files: {metadata.get("parquet_files", 0)}
- parquet size: ~{size_gb:.1f} GiB
- stream status: {stream_status}

## Fields

```json
{json.dumps(stream.get("fields", []), ensure_ascii=False, indent=2)}
```

## Probe Counts

- raw rows seen: {stream.get("raw_seen", 0):,}
- accepted docs: {stream.get("accepted_docs", 0):,}
- rejected docs: {stream.get("rejected_docs", 0):,}
- accepted tokens: {stream.get("accepted_tokens", 0):,}
- avg tokens / accepted doc: {stream.get("tokens_per_accepted_doc_avg", 0):.1f}
- token/word ratio: {stream.get("token_word_ratio", 0):.3f}

## Token Length Percentiles

```json
{json.dumps(stream.get("accepted_token_percentiles", {}), ensure_ascii=False, indent=2)}
```

## Rejection Reasons

```json
{json.dumps(stream.get("rejection_reasons", {}), ensure_ascii=False, indent=2)}
```

## Top URL Domains

```json
{json.dumps(stream.get("top_url_domains", {}), ensure_ascii=False, indent=2)}
```

## v2.3 Options

| variant | target tokens | 50k epochs | recommended now | risk |
|---|---:|---:|---|---|
{options_rows}

## Accepted Samples

{render_samples(stream.get("accepted_samples", []), 20)}

## Rejected Samples

{render_samples(stream.get("rejected_samples", []), 20)}

## Recommendation

{payload["recommendation"]}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe ReactiveAI FineWeb2 PL safely without full download")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--config", default=None, help="Optional dataset config, e.g. pol_Latn")
    parser.add_argument("--split", default="train")
    parser.add_argument("--tokenizer", type=Path, default=DEFAULT_TOKENIZER)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--accepted-samples", type=Path, default=DEFAULT_ACCEPTED)
    parser.add_argument("--rejected-samples", type=Path, default=DEFAULT_REJECTED)
    parser.add_argument("--random-samples", type=Path, default=DEFAULT_RANDOM)
    parser.add_argument("--max-raw-docs", type=int, default=50_000)
    parser.add_argument("--max-accepted-docs", type=int, default=5_000)
    parser.add_argument("--sample-limit", type=int, default=50)
    parser.add_argument("--min-language-score", type=float, default=0.98)
    parser.add_argument("--max-minhash-cluster-size", type=int, default=25)
    parser.add_argument("--metadata-only", action="store_true")
    args = parser.parse_args()

    metadata = metadata_probe(args.repo)
    if args.metadata_only:
        stream: dict[str, Any] = {
            "stream_error": "metadata_only_requested",
            "accepted_samples": [],
            "rejected_samples": [],
            "random_samples": [],
        }
    else:
        try:
            sp = load_sentencepiece(args.tokenizer)
            stream = stream_probe(args, sp)
        except Exception as exc:  # noqa: BLE001
            stream = {
                "stream_error": f"{type(exc).__name__}: {str(exc)[:1500]}",
                "accepted_samples": [],
                "rejected_samples": [],
                "random_samples": [],
            }
    if stream.get("accepted_docs") and stream.get("acceptance_rate", 0) >= 0.10:
        recommendation = (
            "A) FineWeb2 PL is usable as a controlled v2.3 candidate. Build variant A first "
            "(~300M tokens), then inspect reports before any stage 3 training."
        )
    elif stream.get("accepted_docs"):
        recommendation = (
            "C) FineWeb2 PL has usable documents, but acceptance rate is low. Prefer a conservative "
            "v2.3 build or collect a larger probe before building 300M+ tokens."
        )
    elif metadata.get("metadata_error"):
        recommendation = "D) dataset metadata failed; do not build v2.3 until access/network is fixed."
    else:
        recommendation = "D) probe did not find acceptable samples; do not build v2.3 from this source yet."

    payload = {
        "generated_at": now_utc(),
        "repo": args.repo,
        "probe_limits": {
            "max_raw_docs": args.max_raw_docs,
            "max_accepted_docs": args.max_accepted_docs,
            "min_language_score": args.min_language_score,
            "max_minhash_cluster_size": args.max_minhash_cluster_size,
        },
        "metadata": metadata,
        "stream": stream,
        "v2_3_options": build_options(stream),
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
                "stream_error": stream.get("stream_error"),
                "raw_seen": stream.get("raw_seen", 0),
                "accepted_docs": stream.get("accepted_docs", 0),
                "accepted_tokens": stream.get("accepted_tokens", 0),
                "acceptance_rate": stream.get("acceptance_rate", 0),
                "report": str(args.report),
                "recommendation": recommendation,
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
