#!/usr/bin/env python3
"""Bounded, source-aware quality probe for the public Polish Dynaword corpus."""

from __future__ import annotations

import argparse
import collections
import gc
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from datasets import load_dataset

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from glyph100_dataset_v2_2_build import common_bad_pattern_reasons, load_sentencepiece, word_count  # noqa: E402
from glyph100_dataset_v2_filter import FilterConfig, evaluate_document, percentile, truncate_text  # noqa: E402


REPO = "SlayerLab/polish-dynaword"
DEFAULT_SOURCES = (
    "wolne_lektury",
    "1000_novels",
    "eltec_pol",
    "wikibooks",
    "wikinews",
    "wikisource",
    "parliamentary",
)
WEB_RESIDUE_RE = re.compile(
    r"dodaj do koszyka|kup teraz|skontaktuj się z nami|nasza firma|"
    r"polityka prywatności|cookies|czytaj więcej|zobacz także|forum|komentarze|zaloguj|"
    r"zarejestruj|sprawdź ofertę|formularz kontaktowy|reklama",
    re.IGNORECASE,
)
TECHNICAL_WIKI_RE = re.compile(
    r"(?im)^\s*(?:przypisy|linki zewnętrzne|zobacz też|kategoria:|szablon:|dyskusja:|indeks:)\s*$"
)
WIKI_MARKUP_RE = re.compile(r"(?:\bthumb\||\bmały\||\[\[|\]\]|\{\{|\}\})", re.IGNORECASE)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_url(source: str, suffix: str) -> str:
    return f"https://huggingface.co/datasets/{REPO}/resolve/main/data/{source}/{source}.{suffix}"


def source_metadata(source: str) -> dict[str, Any]:
    stats_response = requests.get(resolve_url(source, "stats.json"), timeout=30)
    stats_response.raise_for_status()
    head = requests.head(resolve_url(source, "parquet"), allow_redirects=True, timeout=30)
    head.raise_for_status()
    return {
        "stats": stats_response.json(),
        "compressed_bytes": int(head.headers.get("content-length") or 0),
    }


def filter_config() -> FilterConfig:
    return FilterConfig(
        min_words=80,
        max_chars=120_000,
        min_alpha_ratio=0.55,
        min_polish_stopword_ratio=0.018,
        max_punct_symbol_ratio=0.14,
        max_repetition_score=0.035,
        min_unique_word_ratio=0.22,
        max_word_frequency_ratio=0.11,
        max_urls=0,
        max_line_length=20_000,
    )


def deterministic_excerpt(row: dict[str, Any], text: str, max_chars: int = 80_000) -> tuple[str, bool]:
    """Inspect a stable interior excerpt instead of rejecting an entire long book."""
    if len(text) <= max_chars:
        return text, False
    digest = hashlib.blake2b(str(row.get("id") or "").encode("utf-8"), digest_size=8).digest()
    start = int.from_bytes(digest, "big") % max(1, len(text) - max_chars)
    paragraph = text.find("\n\n", start, min(len(text), start + 2000))
    if paragraph >= 0:
        start = paragraph + 2
    return text[start : start + max_chars], True


def sample_row(row: dict[str, Any], text: str, extra: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("id"),
        "source": row.get("source"),
        "license": row.get("license"),
        "author": row.get("author"),
        "upstream_token_count": row.get("token_count"),
        "text": truncate_text(text, 1600),
        **extra,
    }


def probe_source(
    source: str,
    args: argparse.Namespace,
    sp,
    exact_seen: set[str],
    normalized_seen: set[str],
    near_seen: set[str],
) -> dict[str, Any]:
    metadata = source_metadata(source)
    dataset = load_dataset(
        "parquet",
        data_files={"train": resolve_url(source, "parquet")},
        split="train",
        streaming=True,
    ).shuffle(seed=args.seed, buffer_size=args.shuffle_buffer)
    config = filter_config()
    accepted_samples: list[dict[str, Any]] = []
    rejected_samples: list[dict[str, Any]] = []
    rejection_reasons: collections.Counter[str] = collections.Counter()
    token_lengths: list[int] = []
    word_lengths: list[int] = []
    raw_seen = accepted = rejected = residue = technical_wiki = 0

    for row in dataset:
        raw_seen += 1
        full_text = str(row.get("text") or "")
        text, excerpted = deterministic_excerpt(row, full_text)
        result = evaluate_document(
            text,
            source=source,
            config=config,
            exact_seen=exact_seen,
            normalized_seen=normalized_seen,
            near_seen=near_seen,
        )
        reasons = list(result.reasons)
        reasons.extend(common_bad_pattern_reasons(result.text or text))
        if TECHNICAL_WIKI_RE.search(result.text or text):
            reasons.append("technical_wiki_tail")
        if source in {"wikibooks", "wikinews", "wikisource"} and WIKI_MARKUP_RE.search(result.text or text):
            reasons.append("wiki_markup_residue")
        reasons = list(dict.fromkeys(reasons))
        if reasons:
            rejected += 1
            rejection_reasons.update(reasons)
            if len(rejected_samples) < args.sample_limit:
                rejected_samples.append(
                    sample_row(
                        row,
                        result.text or text,
                        {"reject_reasons": reasons, "metrics": result.metrics, "excerpted": excerpted},
                    )
                )
        else:
            ids = sp.encode(result.text, out_type=int)
            if sp.eos_id() >= 0:
                ids.append(sp.eos_id())
            accepted += 1
            token_lengths.append(len(ids))
            word_lengths.append(word_count(result.text))
            if WEB_RESIDUE_RE.search(result.text):
                residue += 1
            if TECHNICAL_WIKI_RE.search(result.text):
                technical_wiki += 1
            exact_seen.add(str(result.metrics.get("exact_hash")))
            normalized_seen.add(str(result.metrics.get("normalized_hash")))
            near_seen.add(str(result.metrics.get("near_hash")))
            if len(accepted_samples) < args.sample_limit:
                accepted_samples.append(
                    sample_row(
                        row,
                        result.text,
                        {
                            "token_count": len(ids),
                            "word_count": word_lengths[-1],
                            "quality_score": result.metrics.get("quality_score"),
                            "excerpted": excerpted,
                        },
                    )
                )
        if raw_seen >= args.max_docs_per_source:
            break

    del dataset
    gc.collect()

    return {
        "source": source,
        "upstream": metadata,
        "raw_seen": raw_seen,
        "accepted_docs": accepted,
        "rejected_docs": rejected,
        "acceptance_rate": accepted / max(raw_seen, 1),
        "accepted_tokens": sum(token_lengths),
        "token_word_ratio": sum(token_lengths) / max(sum(word_lengths), 1),
        "web_residue_hits": residue,
        "technical_wiki_hits": technical_wiki,
        "rejection_reasons": dict(rejection_reasons.most_common(30)),
        "token_length_percentiles": {
            name: percentile(token_lengths, quantile)
            for name, quantile in (("p50", 0.5), ("p90", 0.9), ("p99", 0.99))
        },
        "accepted_samples": accepted_samples,
        "rejected_samples": rejected_samples,
    }


def source_decision(result: dict[str, Any]) -> str:
    source = result["source"]
    if result["acceptance_rate"] < 0.35:
        return "later: inspect and add source-specific cleanup before inclusion"
    if result["web_residue_hits"] > max(1, result["accepted_docs"] // 20):
        return "later: residue rate is too high for direct inclusion"
    if source == "parliamentary":
        return "use with a 10% token cap to avoid parliamentary style dominance"
    if source == "wikisource":
        return "use after parent-work grouping and technical-page cleanup"
    return "use as a capped source in the v2.4 pilot mix"


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Glyph-100M Polish Dynaword Controlled Source Probe",
        "",
        "The probe used streaming reads, bounded samples and the real Glyph tokenizer. No complete dataset was downloaded and no training was started.",
        "",
        "## Decision",
        "",
        "Polish Dynaword is the strongest currently accessible replacement for gated FinetextPL-Edu because it is public, source-aware and license-documented. It must still be remixed and filtered per source; its raw legal/parliamentary proportions are unsuitable for a general Polish base model.",
        "",
        "## Source Results",
        "",
        "| Source | Upstream docs | Upstream tokens | Probe accepted | Probe tokens | Residue | Decision |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for result in payload["sources"]:
        stats = result["upstream"]["stats"]
        lines.append(
            f"| {result['source']} | {int(stats.get('kept') or 0):,} | {int(stats.get('tokens') or 0):,} | "
            f"{result['accepted_docs']}/{result['raw_seen']} ({result['acceptance_rate']:.1%}) | "
            f"{result['accepted_tokens']:,} | {result['web_residue_hits']} | {source_decision(result)} |"
        )
    lines.extend(
        [
            "",
            "## Recommended 300M-token Pilot Mix",
            "",
            "- 30% clean Wikipedia PL (90M)",
            "- 25% literature: Wolne Lektury, 1000 Novels and ELTeC (75M)",
            "- 15% cleaned Wikisource grouped by parent work (45M)",
            "- 10% parliamentary text, capped (30M)",
            "- 10% Wikibooks + Wikinews (30M)",
            "- 5% official/legal explanatory prose, capped (15M)",
            "- up to 5% register-gated HPLT only after a manual precision gate (15M)",
            "",
            "This mix deliberately does not depend on FinetextPL-Edu and does not make open web the dominant source.",
            "",
            "## Detailed Samples",
            "",
        ]
    )
    for result in payload["sources"]:
        lines.extend([f"### {result['source']}", "", "Accepted:", ""])
        for sample in result["accepted_samples"][:10]:
            lines.extend([f"- `{sample['id']}`: {sample['text'][:500]}", ""])
        lines.extend(["Rejected:", ""])
        for sample in result["rejected_samples"][:5]:
            lines.extend(
                [
                    f"- `{sample['id']}` ({', '.join(sample['reject_reasons'])}): {sample['text'][:400]}",
                    "",
                ]
            )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--tokenizer", type=Path, default=Path("data/processed/tokenizer.model"))
    parser.add_argument("--max-docs-per-source", type=int, default=300)
    parser.add_argument("--sample-limit", type=int, default=25)
    parser.add_argument("--shuffle-buffer", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()
    sources = args.source or list(DEFAULT_SOURCES)

    os.environ.setdefault("HF_HOME", "/mnt/data/mac/GlyphArchive/hf-cache")
    sp = load_sentencepiece(args.tokenizer)
    exact_seen: set[str] = set()
    normalized_seen: set[str] = set()
    near_seen: set[str] = set()
    results = [
        probe_source(source, args, sp, exact_seen, normalized_seen, near_seen)
        for source in sources
    ]
    payload = {
        "generated_at": now_utc(),
        "repo": REPO,
        "gated": False,
        "probe_limits": {
            "sources": sources,
            "max_docs_per_source": args.max_docs_per_source,
            "sample_limit": args.sample_limit,
            "shuffle_buffer": args.shuffle_buffer,
            "seed": args.seed,
        },
        "sources": results,
        "recommended_pilot_tokens": 300_000_000,
        "recommendation": "Build a 300M source-balanced v2.4 pilot; do not wait for FinetextPL-Edu and do not use raw HPLT as the base.",
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(render_markdown(payload) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                result["source"]: {
                    "accepted": result["accepted_docs"],
                    "seen": result["raw_seen"],
                    "residue": result["web_residue_hits"],
                }
                for result in results
            },
            ensure_ascii=False,
        )
    )
    sys.stdout.flush()
    # datasets 4.8 + pyarrow 23 can crash in an HTTP filesystem finalizer on
    # Python 3.12 after a successful streaming run. All outputs are durable at
    # this point, so bypass only that broken interpreter shutdown path.
    os._exit(0)


if __name__ == "__main__":
    main()
