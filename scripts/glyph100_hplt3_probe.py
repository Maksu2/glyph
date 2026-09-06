#!/usr/bin/env python3
"""Bounded streaming quality probe for sorted HPLT3 Polish shards."""

from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from glyph100_dataset_v2_2_build import common_bad_pattern_reasons, keep_sample, load_sentencepiece, word_count  # noqa: E402
from glyph100_dataset_v2_3_1_build import fineweb_filter_config, page_quality  # noqa: E402
from glyph100_dataset_v2_filter import evaluate_document, percentile, sha1_text, truncate_text  # noqa: E402


DEFAULT_URLS = [
    "https://data.hplt-project.org/three/sorted/pol_Latn/10_1.jsonl.zst",
    "https://data.hplt-project.org/three/sorted/pol_Latn/9_1.jsonl.zst",
]
WEB_RESIDUE_RE = re.compile(
    r"dodaj do koszyka|cena|promocja|skontaktuj się z nami|nasza firma|polityka prywatności|cookies|"
    r"czytaj więcej|zobacz także|forum|komentarze|zaloguj|zarejestruj|oferta|usługi",
    re.IGNORECASE,
)

REGISTER_LABELS = (
    "MT", "LY", "SP", "ID", "NA", "HI", "IN", "OP", "IP", "it", "ne", "sr", "nb",
    "re", "en", "ra", "dtp", "fi", "lt", "rv", "ob", "rs", "av", "ds", "ed",
)
REGISTER_POSITIVE_LABELS = ("IN", "HI", "NA", "OP", "en", "ra", "dtp")


def register_scores(row: dict[str, Any]) -> dict[str, float]:
    raw = row.get("web-register")
    if not isinstance(raw, dict):
        return {}
    return {label: float(raw.get(label) or 0.0) for label in REGISTER_LABELS}


def register_gate_reasons(
    row: dict[str, Any],
    scores: dict[str, float],
    *,
    max_cluster_size: int,
) -> list[str]:
    """Conservative HPLT-specific gate for a quality-first Polish corpus."""
    reasons: list[str] = []
    if not scores:
        return ["missing_register_scores"]
    if row.get("filter") not in (None, "keep"):
        reasons.append("hplt_filter_not_keep")
    if row.get("pii"):
        reasons.append("hplt_pii_detected")
    if int(row.get("cluster_size") or 1) > max_cluster_size:
        reasons.append("large_duplicate_cluster")
    if scores["MT"] >= 0.35:
        reasons.append("register_machine_translation")
    if scores["ID"] >= 0.45:
        reasons.append("register_interactive_discussion")
    if scores["lt"] >= 0.55:
        reasons.append("register_legal_terms")
    if scores["IP"] >= 0.65:
        reasons.append("register_persuasion_high")
    if scores["ds"] >= 0.40:
        reasons.append("register_selling_description_high")
    if scores["IP"] >= 0.30 and scores["ds"] >= 0.18:
        reasons.append("register_commercial_persuasion")
    if max(scores[label] for label in REGISTER_POSITIVE_LABELS) < 0.42:
        reasons.append("register_no_clear_longform_signal")
    return reasons


def update_register_totals(totals: collections.Counter[str], scores: dict[str, float]) -> None:
    for label, value in scores.items():
        totals[label] += value


def register_means(totals: collections.Counter[str], count: int) -> dict[str, float]:
    return {label: round(totals[label] / max(count, 1), 4) for label in REGISTER_LABELS}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def stream_zstd_jsonl(url: str) -> Iterator[dict[str, Any]]:
    curl = subprocess.Popen(
        ["curl", "-fsSL", url],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    assert curl.stdout is not None
    zstd = subprocess.Popen(
        ["zstdcat"],
        stdin=curl.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    curl.stdout.close()
    assert zstd.stdout is not None
    try:
        for line in zstd.stdout:
            if line.strip():
                yield json.loads(line)
    finally:
        zstd.terminate()
        curl.terminate()
        try:
            zstd.wait(timeout=5)
        except subprocess.TimeoutExpired:
            zstd.kill()
        try:
            curl.wait(timeout=5)
        except subprocess.TimeoutExpired:
            curl.kill()


def row_url(row: dict[str, Any]) -> str:
    return str(row.get("u") or row.get("url") or "")


def sample_payload(row: dict[str, Any], text: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "id": sha1_text(f"{row.get('f','')}:{row.get('o','')}:{row_url(row)}")[:24],
        "url": row_url(row),
        "crawl_id": row.get("crawl_id"),
        "languages": row.get("lang"),
        "language_probabilities": row.get("prob"),
        "cluster_size": row.get("cluster_size"),
        "filter": row.get("filter"),
        "pii_count": len(row.get("pii") or []),
        "register_scores": register_scores(row),
        "text": truncate_text(text, 1400),
    }
    if extra:
        payload.update(extra)
    return payload


def probe(args: argparse.Namespace) -> dict[str, Any]:
    sp = load_sentencepiece(args.tokenizer)
    eos_id = sp.eos_id()
    config = fineweb_filter_config()
    exact_seen: set[str] = set()
    normalized_seen: set[str] = set()
    near_seen: set[str] = set()
    accepted_samples: list[dict[str, Any]] = []
    rejected_samples: list[dict[str, Any]] = []
    random_samples: list[dict[str, Any]] = []
    rejection_reasons: collections.Counter[str] = collections.Counter()
    register_rejection_reasons: collections.Counter[str] = collections.Counter()
    domain_counts: collections.Counter[str] = collections.Counter()
    accepted_domain_counts: collections.Counter[str] = collections.Counter()
    register_raw_totals: collections.Counter[str] = collections.Counter()
    register_accepted_totals: collections.Counter[str] = collections.Counter()
    register_rejected_totals: collections.Counter[str] = collections.Counter()
    fields: set[str] = set()
    token_lengths: list[int] = []
    word_lengths: list[int] = []
    residue_accepted = 0
    per_shard: dict[str, dict[str, int]] = {}
    raw_seen = accepted = rejected = 0
    accepted_before_register_gate = register_only_rejected = 0

    for url in args.url:
        shard = url.rsplit("/", 1)[-1]
        shard_state = {"raw_seen": 0, "accepted": 0, "rejected": 0}
        per_shard[shard] = shard_state
        for row in stream_zstd_jsonl(url):
            raw_seen += 1
            shard_state["raw_seen"] += 1
            fields.update(row)
            text = str(row.get("text") or "")
            scores = register_scores(row)
            update_register_totals(register_raw_totals, scores)
            url_value = row_url(row)
            domain = re.sub(r"^https?://", "", url_value).split("/", 1)[0].lower()
            if domain:
                domain_counts[domain] += 1
            keep_sample(random_samples, sample_payload(row, text, {"shard": shard}), f"random:{shard}:{raw_seen}", args.sample_limit)

            result = evaluate_document(
                text,
                source="hplt3_polish",
                config=config,
                exact_seen=exact_seen,
                normalized_seen=normalized_seen,
                near_seen=near_seen,
            )
            record = {"text": result.text or text, "url": url_value}
            page_score, page_reasons, page_labels = page_quality(record, result.metrics)
            reasons = list(result.reasons)
            reasons.extend(common_bad_pattern_reasons(result.text or text))
            reasons.extend(page_reasons)
            if page_score < args.min_page_score:
                reasons.append("low_page_quality_score")
            content_reasons = list(dict.fromkeys(reasons))
            if not content_reasons:
                accepted_before_register_gate += 1
            register_reasons = register_gate_reasons(
                row,
                scores,
                max_cluster_size=args.max_cluster_size,
            )
            reasons.extend(register_reasons)
            reasons = list(dict.fromkeys(reasons))

            if reasons:
                rejected += 1
                shard_state["rejected"] += 1
                rejection_reasons.update(reasons)
                register_rejection_reasons.update(register_reasons)
                update_register_totals(register_rejected_totals, scores)
                if not content_reasons and register_reasons:
                    register_only_rejected += 1
                keep_sample(
                    rejected_samples,
                    sample_payload(
                        row,
                        result.text or text,
                        {
                            "shard": shard,
                            "reject_reasons": reasons,
                            "page_score": round(page_score, 3),
                            "page_labels": page_labels,
                        },
                    ),
                    f"reject:{shard}:{raw_seen}",
                    args.sample_limit,
                )
            else:
                ids = sp.encode(result.text, out_type=int)
                ids.append(eos_id)
                accepted += 1
                shard_state["accepted"] += 1
                accepted_domain_counts[domain] += 1
                update_register_totals(register_accepted_totals, scores)
                token_lengths.append(len(ids))
                word_lengths.append(word_count(result.text))
                if WEB_RESIDUE_RE.search(result.text):
                    residue_accepted += 1
                exact_seen.add(str(result.metrics.get("exact_hash")))
                normalized_seen.add(str(result.metrics.get("normalized_hash")))
                near_seen.add(str(result.metrics.get("near_hash")))
                keep_sample(
                    accepted_samples,
                    sample_payload(
                        row,
                        result.text,
                        {
                            "shard": shard,
                            "token_count": len(ids),
                            "word_count": word_lengths[-1],
                            "quality_score": result.metrics.get("quality_score"),
                            "page_score": round(page_score, 3),
                            "page_labels": page_labels,
                        },
                    ),
                    f"accept:{shard}:{raw_seen}",
                    args.sample_limit,
                )

            if shard_state["raw_seen"] >= args.max_raw_docs_per_shard:
                break

    sizes = {}
    for url in args.url:
        try:
            response = requests.head(url, timeout=20)
            sizes[url] = int(response.headers.get("content-length") or 0)
        except requests.RequestException:
            sizes[url] = 0

    accepted_tokens = sum(token_lengths)
    return {
        "generated_at": now_utc(),
        "source": "HPLT3.0 sorted Polish",
        "urls": args.url,
        "compressed_sizes_bytes": sizes,
        "probe_limits": {"max_raw_docs_per_shard": args.max_raw_docs_per_shard, "sample_limit": args.sample_limit},
        "raw_seen": raw_seen,
        "accepted_docs": accepted,
        "rejected_docs": rejected,
        "acceptance_rate": accepted / max(raw_seen, 1),
        "accepted_before_register_gate": accepted_before_register_gate,
        "acceptance_rate_before_register_gate": accepted_before_register_gate / max(raw_seen, 1),
        "register_only_rejected": register_only_rejected,
        "accepted_tokens": accepted_tokens,
        "token_word_ratio": accepted_tokens / max(sum(word_lengths), 1),
        "accepted_web_residue_hits": residue_accepted,
        "fields": sorted(fields),
        "per_shard": per_shard,
        "top_domains": dict(domain_counts.most_common(40)),
        "top_accepted_domains": dict(accepted_domain_counts.most_common(40)),
        "rejection_reasons": dict(rejection_reasons.most_common(80)),
        "register_rejection_reasons": dict(register_rejection_reasons.most_common()),
        "register_score_means": {
            "raw": register_means(register_raw_totals, raw_seen),
            "accepted": register_means(register_accepted_totals, accepted),
            "rejected": register_means(register_rejected_totals, rejected),
        },
        "token_length_percentiles": {name: percentile(token_lengths, q) for name, q in [("p50", 0.5), ("p90", 0.9), ("p99", 0.99)]},
        "accepted_samples": accepted_samples,
        "rejected_samples": rejected_samples,
        "random_samples": random_samples,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    recommendation = (
        "Use only behind the strict page filter and domain audit; WDS 10/9 is not clean enough by itself."
        if payload["accepted_docs"]
        else "Do not use this source with the current filters."
    )
    lines = [
        "# Glyph-100M HPLT3 Polish Controlled Probe",
        "",
        "No full shard was downloaded and no training was started.",
        "",
        "## Result",
        "",
        f"- raw documents: `{payload['raw_seen']:,}`",
        f"- accepted documents: `{payload['accepted_docs']:,}` ({payload['acceptance_rate']:.1%})",
        f"- accepted before register gate: `{payload['accepted_before_register_gate']:,}` ({payload['acceptance_rate_before_register_gate']:.1%})",
        f"- documents rejected only by register/PII/cluster gate: `{payload['register_only_rejected']:,}`",
        f"- accepted tokens: `{payload['accepted_tokens']:,}`",
        f"- accepted documents still matching a coarse web-residue pattern: `{payload['accepted_web_residue_hits']:,}`",
        f"- recommendation: **{recommendation}**",
        "",
        "The first document in the nominally highest WDS shard was an SEO-like medical service page. HPLT's rank is useful as a prior, not as an acceptance decision.",
        "",
        "## Per Shard",
        "",
        "```json",
        json.dumps(payload["per_shard"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Rejection Reasons",
        "",
        "```json",
        json.dumps(payload["rejection_reasons"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Register Gate",
        "",
        "The gate rejects likely machine translation, discussion, legal boilerplate, persuasion/selling pages, detected PII and large duplicate clusters. It also requires a clear long-form register signal.",
        "",
        "```json",
        json.dumps(
            {
                "reasons": payload["register_rejection_reasons"],
                "score_means": payload["register_score_means"],
                "top_accepted_domains": payload["top_accepted_domains"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        "```",
        "",
        "## Accepted Samples",
        "",
    ]
    for index, sample in enumerate(payload["accepted_samples"][:30], 1):
        lines.extend([f"### {index}. {sample['url']}", "", sample["text"], ""])
    lines.extend(["## Rejected Samples", ""])
    for index, sample in enumerate(payload["rejected_samples"][:30], 1):
        lines.extend(
            [
                f"### {index}. {sample['url']}",
                "",
                f"Reasons: `{', '.join(sample['reject_reasons'])}`",
                "",
                sample["text"],
                "",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", action="append", default=[])
    parser.add_argument("--tokenizer", type=Path, default=Path("data/processed/tokenizer.model"))
    parser.add_argument("--max-raw-docs-per-shard", type=int, default=3000)
    parser.add_argument("--sample-limit", type=int, default=50)
    parser.add_argument("--min-page-score", type=float, default=0.75)
    parser.add_argument("--max-cluster-size", type=int, default=8)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()
    if not args.url:
        args.url = list(DEFAULT_URLS)

    payload = probe(args)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(render_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ["raw_seen", "accepted_docs", "acceptance_rate", "accepted_tokens", "accepted_web_residue_hits"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
