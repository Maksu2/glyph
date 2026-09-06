#!/usr/bin/env python3
"""Prepare a cleaner pretraining split for Glyph-100M.

This script intentionally writes to glyph100_* outputs and never touches the
legacy 27M tokens.bin. It is a practical filter/report pipeline for the
existing mixed Polish corpus, not a perfect Common Crawl cleaner.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import html
import json
import math
import re
import statistics
import time
from pathlib import Path
from typing import Any

import numpy as np


DEFAULT_INPUT = Path("data/raw/corpus.txt")
DEFAULT_TOKENIZER = Path("data/processed/tokenizer.model")
DEFAULT_TRAIN_BIN = Path("data/processed/glyph100_train.bin")
DEFAULT_VAL_BIN = Path("data/processed/glyph100_val.bin")
DEFAULT_METADATA = Path("data/processed/glyph100_metadata.json")
DEFAULT_REPORT = Path("data/reports/glyph_100m_dataset_report.md")
DEFAULT_STATS = Path("data/reports/glyph_100m_dataset_stats.json")
DEFAULT_DATASET_NAME = "glyph100_stage1_candidate"

HTML_RE = re.compile(r"<[^>]+>")
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
MULTISPACE_RE = re.compile(r"[ \t\r\f\v]+")
REPEATED_PUNCT_RE = re.compile(r"([.?!,;:])\1{3,}")
WORD_RE = re.compile(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]+", re.UNICODE)

POLISH_CHARS = set("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")
POLISH_STOPWORDS = {
    "i", "oraz", "że", "jest", "są", "nie", "to", "w", "we", "na", "z",
    "ze", "do", "dla", "po", "od", "przez", "który", "która", "które",
    "jako", "się", "ma", "był", "była", "było", "może", "ale", "także",
    "ten", "ta", "te", "tym", "jego", "jej", "ich", "więc", "czy",
}

BOILERPLATE_PATTERNS = [
    "strona główna",
    "czytaj więcej",
    "zobacz także",
    "źródło:",
    "anonimowy",
    "dodaj komentarz",
    "napisz komentarz",
    "zaloguj się",
    "rejestracja",
    "koszyk",
    "regulamin",
    "polityka prywatności",
    "cookies",
    "wszelkie prawa zastrzeżone",
    "wolne lektury",
    "fundacja wolne lektury",
    "lektury szkolne",
    "biblioteka internetowa",
]

SOURCE_CATALOG = [
    {
        "name": "Polish Wikipedia",
        "source": "wikimedia/wikipedia 20231101.pl",
        "type": "encyclopedic articles",
        "license": "various Wikimedia project licenses; verify per dump/card",
        "decision": "use",
        "reason": "High-density Polish encyclopedic prose; good base material for a small model.",
    },
    {
        "name": "Wolne Lektury",
        "source": "wolnelektury.pl plain text/API",
        "type": "public-domain / freely licensed literary texts",
        "license": "public domain or CC BY-SA depending on work metadata; verify per work",
        "decision": "use_with_boilerplate_filter",
        "reason": "Long-form Polish literary text is valuable, but project/license boilerplate must be filtered.",
    },
    {
        "name": "mC4 / OSCAR PL",
        "source": "allenai/c4 pl, oscar-corpus/OSCAR-2301 pl fallback",
        "type": "web crawl text",
        "license": "dataset-card dependent; research hygiene required",
        "decision": "use_filtered_only",
        "reason": "Adds breadth, but was the main risk for web/forum/SEO garbage in Glyph-27M.",
    },
]


def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def stable_bucket(text: str, modulo: int) -> int:
    digest = hashlib.blake2b(text.encode("utf-8", errors="ignore"), digest_size=8).digest()
    return int.from_bytes(digest, "big") % modulo


def clean_text(text: str) -> tuple[str, dict[str, int]]:
    raw_url_count = len(URL_RE.findall(text))
    raw_html_count = len(HTML_RE.findall(text))
    text = html.unescape(text)
    text = HTML_RE.sub(" ", text)
    text = URL_RE.sub(" ", text)
    text = CONTROL_RE.sub("", text)
    text = REPEATED_PUNCT_RE.sub(r"\1\1\1", text)
    text = MULTISPACE_RE.sub(" ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip(), {"urls": raw_url_count, "html_tags": raw_html_count}


def token_stats_for_text(text: str) -> dict[str, float | int]:
    words = WORD_RE.findall(text)
    chars = len(text)
    alpha = sum(ch.isalpha() for ch in text)
    polish_chars = sum(ch in POLISH_CHARS for ch in text)
    control = len(CONTROL_RE.findall(text))
    punct_or_symbol = sum((not ch.isalnum()) and (not ch.isspace()) for ch in text)
    lower_words = [w.lower() for w in words]
    stop_hits = sum(1 for w in lower_words if w in POLISH_STOPWORDS)
    unique_words = len(set(lower_words))
    max_word_freq = max(collections.Counter(lower_words).values(), default=0)
    return {
        "chars": chars,
        "words": len(words),
        "alpha_ratio": alpha / max(chars, 1),
        "polish_char_ratio": polish_chars / max(alpha, 1),
        "polish_stopword_ratio": stop_hits / max(len(words), 1),
        "control_count": control,
        "punct_symbol_ratio": punct_or_symbol / max(chars, 1),
        "unique_word_ratio": unique_words / max(len(words), 1),
        "max_word_frequency_ratio": max_word_freq / max(len(words), 1),
        "line_count": text.count("\n") + 1,
        "max_line_length": max((len(line) for line in text.splitlines()), default=0),
    }


def repetition_score(words: list[str]) -> float:
    if len(words) < 16:
        return 0.0
    grams = [" ".join(words[i:i + 4]) for i in range(len(words) - 3)]
    counts = collections.Counter(grams)
    repeated = sum(count - 1 for count in counts.values() if count > 1)
    return repeated / max(len(grams), 1)


def near_duplicate_key(words: list[str]) -> str:
    normalized = " ".join(w.lower() for w in words[:80])
    return sha1_text(normalized)[:16]


def classify_source(text: str) -> str:
    lower = text.lower()
    if "wolne lektury" in lower or "fundacja wolne lektury" in lower:
        return "legacy_wolne_lektury_marker"
    if len(text) > 4000:
        return "legacy_long_article_like"
    return "legacy_mixed_paragraph_like"


def reject_reasons(
    raw: str,
    clean: str,
    raw_markers: dict[str, int],
    seen_hashes: set[str],
    seen_near: set[str],
    min_words: int,
    max_chars: int,
) -> tuple[list[str], dict[str, float | int | str]]:
    metrics = token_stats_for_text(clean)
    words = [w.lower() for w in WORD_RE.findall(clean)]
    metrics["repetition_score"] = repetition_score(words)
    metrics["source_guess"] = classify_source(clean)

    reasons: list[str] = []
    lower = clean.lower()

    if not clean:
        reasons.append("empty_after_clean")
    if metrics["words"] < min_words:
        reasons.append("too_short")
    if metrics["chars"] > max_chars:
        reasons.append("too_long")
    if raw_markers["html_tags"] > 0:
        reasons.append("html_present")
    if raw_markers["urls"] >= 2:
        reasons.append("too_many_urls")
    if any(pattern in lower for pattern in BOILERPLATE_PATTERNS):
        reasons.append("boilerplate_phrase")
    if metrics["alpha_ratio"] < 0.55:
        reasons.append("low_alpha_ratio")
    if (
        metrics["polish_stopword_ratio"] < 0.02
        and metrics["polish_char_ratio"] < 0.002
        and metrics["words"] >= 30
    ):
        reasons.append("low_polish_signal")
    if metrics["punct_symbol_ratio"] > 0.18:
        reasons.append("too_much_punctuation_or_symbols")
    if metrics["max_line_length"] > 20000:
        reasons.append("very_long_line")
    if metrics["unique_word_ratio"] < 0.28 and metrics["words"] >= 80:
        reasons.append("low_unique_word_ratio")
    if metrics["max_word_frequency_ratio"] > 0.12 and metrics["words"] >= 80:
        reasons.append("single_word_repetition")
    if metrics["repetition_score"] > 0.05:
        reasons.append("repeated_ngrams")

    exact = sha1_text(clean.lower())
    near = near_duplicate_key(words)
    metrics["exact_hash"] = exact
    metrics["near_hash"] = near
    if exact in seen_hashes:
        reasons.append("exact_duplicate")
    if near in seen_near and len(words) >= 80:
        reasons.append("near_duplicate_prefix")

    return reasons, metrics


def percentile(values: list[int | float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    idx = (len(ordered) - 1) * p
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return float(ordered[lo])
    return float(ordered[lo] * (hi - idx) + ordered[hi] * (idx - lo))


def write_uint16_tokens(handle, ids: list[int]) -> None:
    np.asarray(ids, dtype=np.uint16).tofile(handle)


def truncate_sample(text: str, max_chars: int = 700) -> str:
    text = text.replace("\n", " ")
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def format_samples(samples: list[dict[str, Any]]) -> str:
    chunks = []
    for i, sample in enumerate(samples, 1):
        reasons = sample.get("reasons")
        reason_text = f" reasons={','.join(reasons)}" if reasons else ""
        chunks.append(f"{i}. source={sample.get('source_guess', 'unknown')}{reason_text}\n\n   {sample['text']}")
    return "\n\n".join(chunks)


def build_report(stats: dict[str, Any]) -> str:
    p = stats["doc_token_percentiles"]
    return f"""# Glyph-100M Dataset Report

Generated: {stats["generated_at"]}

## Recommendation

{stats["recommendation"]}

## Inputs

- dataset name: `{stats["dataset_name"]}`
- input corpus: `{stats["input_path"]}`
- tokenizer: `{stats["tokenizer_path"]}`
- tokenizer vocab size: {stats["tokenizer_vocab_size"]:,}
- context length target: {stats["context_len"]}
- processing mode: {stats["processing_mode"]}

## Source Notes

The current legacy corpus does not preserve per-document source metadata, so
the split uses approximate source labels inferred from document shape and
known corpus construction. This split is a stage-1 sanity candidate, not the
final cleaner corpus for 10k+ / 50k+ training. Future Glyph-100M data should
preserve source IDs.

| Source | Type | Decision | Risk / note |
|---|---|---|---|
{chr(10).join(f"| {item['name']} | {item['type']} | {item['decision']} | {item['reason']} |" for item in SOURCE_CATALOG)}

## Counts

- documents seen: {stats["seen_docs"]:,}
- documents accepted: {stats["accepted_docs"]:,}
- documents rejected: {stats["rejected_docs"]:,}
- acceptance rate: {stats["acceptance_rate"]:.2%}
- train documents: {stats["train_docs"]:,}
- val documents: {stats["val_docs"]:,}
- train tokens: {stats["train_tokens"]:,}
- val tokens: {stats["val_tokens"]:,}
- total tokens: {stats["total_tokens"]:,}
- word/token ratio: {stats["word_token_ratio"]:.3f}
- token/word ratio: {stats["token_word_ratio"]:.3f}

## Document Lengths After Tokenization

- p50: {p["p50"]:.0f}
- p75: {p["p75"]:.0f}
- p90: {p["p90"]:.0f}
- p95: {p["p95"]:.0f}
- p99: {p["p99"]:.0f}
- max: {stats["max_doc_tokens"]:,}
- docs <= context {stats["context_len"]}: {stats["docs_within_context"]:,} ({stats["docs_within_context_ratio"]:.2%})

## Approximate Source Mix

{json.dumps(stats["source_counts"], ensure_ascii=False, indent=2)}

## Top Rejection Reasons

{json.dumps(stats["rejection_reasons"], ensure_ascii=False, indent=2)}

## Suspicious Pattern Counts

{json.dumps(stats["suspicious_patterns"], ensure_ascii=False, indent=2)}

## Accepted Samples

{format_samples(stats["accepted_samples"])}

## Rejected Samples

{format_samples(stats["rejected_samples"])}

## Random Final Samples

{format_samples(stats["final_samples"])}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare Glyph-100M filtered pretraining split")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--tokenizer", type=Path, default=DEFAULT_TOKENIZER)
    parser.add_argument("--train-bin", type=Path, default=DEFAULT_TRAIN_BIN)
    parser.add_argument("--val-bin", type=Path, default=DEFAULT_VAL_BIN)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--stats", type=Path, default=DEFAULT_STATS)
    parser.add_argument("--dataset-name", default=DEFAULT_DATASET_NAME)
    parser.add_argument("--context-len", type=int, default=512)
    parser.add_argument("--min-words", type=int, default=20)
    parser.add_argument("--max-chars", type=int, default=50_000)
    parser.add_argument("--val-per-mille", type=int, default=10, help="Validation split per mille by document hash")
    parser.add_argument("--max-docs", type=int, default=None, help="Stop after reading this many raw documents")
    parser.add_argument("--max-accepted-docs", type=int, default=None, help="Stop after accepting this many documents")
    parser.add_argument("--sample-limit", type=int, default=50)
    parser.add_argument("--force", action="store_true", help="Overwrite glyph100 output files")
    return parser.parse_args()


def ensure_safe_outputs(args: argparse.Namespace) -> None:
    forbidden = {Path("data/processed/tokens.bin").resolve(), Path("data/processed/val_tokens.bin").resolve()}
    for path in [args.train_bin, args.val_bin]:
        if path.resolve() in forbidden:
            raise SystemExit(f"Refusing to write legacy 27M token file: {path}")
    outputs = [args.train_bin, args.val_bin, args.metadata, args.report, args.stats]
    existing = [path for path in outputs if path.exists()]
    if existing and not args.force:
        formatted = "\n".join(f"- {path}" for path in existing)
        raise SystemExit(f"Output files already exist. Use --force to replace glyph100 outputs only:\n{formatted}")
    for path in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    args = parse_args()
    ensure_safe_outputs(args)

    try:
        import sentencepiece as spm
    except ImportError as exc:
        raise SystemExit("sentencepiece is required for token counting/tokenization") from exc

    if not args.input.exists():
        raise SystemExit(f"Input corpus not found: {args.input}")
    if not args.tokenizer.exists():
        raise SystemExit(f"Tokenizer not found: {args.tokenizer}")

    sp = spm.SentencePieceProcessor()
    sp.load(str(args.tokenizer))
    eos_id = sp.eos_id()

    seen_hashes: set[str] = set()
    seen_near: set[str] = set()
    rejection_reasons: collections.Counter[str] = collections.Counter()
    suspicious_patterns: collections.Counter[str] = collections.Counter()
    source_counts: collections.Counter[str] = collections.Counter()
    token_lengths: list[int] = []

    accepted_samples: list[dict[str, Any]] = []
    rejected_samples: list[dict[str, Any]] = []
    final_samples: list[dict[str, Any]] = []

    seen_docs = accepted_docs = rejected_docs = 0
    train_docs = val_docs = 0
    train_tokens = val_tokens = 0
    total_words = 0
    docs_within_context = 0
    max_doc_tokens = 0
    started = time.time()

    with args.input.open("r", encoding="utf-8", errors="replace") as fin, \
            args.train_bin.open("wb") as train_out, \
            args.val_bin.open("wb") as val_out:
        for line_no, raw in enumerate(fin, 1):
            if args.max_docs is not None and seen_docs >= args.max_docs:
                break

            seen_docs += 1
            raw = raw.rstrip("\n")
            clean, raw_markers = clean_text(raw)
            reasons, metrics = reject_reasons(
                raw,
                clean,
                raw_markers,
                seen_hashes,
                seen_near,
                args.min_words,
                args.max_chars,
            )

            if reasons:
                rejected_docs += 1
                for reason in reasons:
                    rejection_reasons[reason] += 1
                if len(rejected_samples) < args.sample_limit:
                    rejected_samples.append({
                        "text": truncate_sample(clean or raw),
                        "reasons": reasons[:5],
                        "source_guess": metrics.get("source_guess", "unknown"),
                    })
                continue

            ids = sp.encode(clean, out_type=int)
            if not ids:
                rejected_docs += 1
                rejection_reasons["empty_tokenization"] += 1
                continue
            ids.append(eos_id)

            seen_hashes.add(str(metrics["exact_hash"]))
            seen_near.add(str(metrics["near_hash"]))
            accepted_docs += 1
            total_words += int(metrics["words"])
            source = str(metrics["source_guess"])
            source_counts[source] += 1
            token_lengths.append(len(ids))
            max_doc_tokens = max(max_doc_tokens, len(ids))
            if len(ids) <= args.context_len:
                docs_within_context += 1

            for pattern in BOILERPLATE_PATTERNS:
                if pattern in clean.lower():
                    suspicious_patterns[pattern] += 1

            sample = {"text": truncate_sample(clean), "source_guess": source}
            if len(accepted_samples) < args.sample_limit:
                accepted_samples.append(sample)
            if len(final_samples) < args.sample_limit or stable_bucket(clean, 10_000) < args.sample_limit:
                if len(final_samples) >= args.sample_limit:
                    final_samples[stable_bucket(clean, args.sample_limit)] = sample
                else:
                    final_samples.append(sample)

            is_val = stable_bucket(clean, 1000) < args.val_per_mille
            if is_val:
                write_uint16_tokens(val_out, ids)
                val_docs += 1
                val_tokens += len(ids)
            else:
                write_uint16_tokens(train_out, ids)
                train_docs += 1
                train_tokens += len(ids)

            if args.max_accepted_docs is not None and accepted_docs >= args.max_accepted_docs:
                break
            if seen_docs % 100_000 == 0:
                elapsed = time.time() - started
                print(
                    f"seen={seen_docs:,} accepted={accepted_docs:,} rejected={rejected_docs:,} "
                    f"tokens={train_tokens + val_tokens:,} elapsed={elapsed:.1f}s",
                    flush=True,
                )

    total_tokens = train_tokens + val_tokens
    stats: dict[str, Any] = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "dataset_name": args.dataset_name,
        "input_path": str(args.input),
        "tokenizer_path": str(args.tokenizer),
        "tokenizer_vocab_size": sp.vocab_size(),
        "context_len": args.context_len,
        "processing_mode": {
            "max_docs": args.max_docs,
            "max_accepted_docs": args.max_accepted_docs,
            "min_words": args.min_words,
            "max_chars": args.max_chars,
            "val_per_mille": args.val_per_mille,
        },
        "source_catalog": SOURCE_CATALOG,
        "seen_docs": seen_docs,
        "accepted_docs": accepted_docs,
        "rejected_docs": rejected_docs,
        "acceptance_rate": accepted_docs / max(seen_docs, 1),
        "train_docs": train_docs,
        "val_docs": val_docs,
        "train_tokens": train_tokens,
        "val_tokens": val_tokens,
        "total_tokens": total_tokens,
        "total_words": total_words,
        "word_token_ratio": total_words / max(total_tokens, 1),
        "token_word_ratio": total_tokens / max(total_words, 1),
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
        "source_counts": dict(source_counts.most_common()),
        "rejection_reasons": dict(rejection_reasons.most_common(30)),
        "suspicious_patterns": dict(suspicious_patterns.most_common(30)),
        "accepted_samples": accepted_samples,
        "rejected_samples": rejected_samples,
        "final_samples": final_samples[: args.sample_limit],
        "train_bin": str(args.train_bin),
        "val_bin": str(args.val_bin),
        "metadata": str(args.metadata),
        "elapsed_seconds": time.time() - started,
    }

    if total_tokens < 10_000_000:
        stats["recommendation"] = (
            "Candidate split is useful for smoke/stage-1 experiments, but is too small for longer Glyph-100M training."
        )
    elif stats["acceptance_rate"] < 0.20:
        stats["recommendation"] = (
            "Filters are very strict or corpus quality is poor; inspect rejected samples before longer training."
        )
    else:
        stats["recommendation"] = (
            "Dataset split is acceptable for a 1k-step Glyph-100M sanity run; process the full corpus before long stages."
        )

    args.stats.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    args.metadata.write_text(json.dumps({
        "variant": "glyph-100m",
        "dataset_name": args.dataset_name,
        "scope": "stage 1 sanity candidate; not final cleaner corpus",
        "train_bin": str(args.train_bin),
        "val_bin": str(args.val_bin),
        "tokenizer": str(args.tokenizer),
        "vocab_size": sp.vocab_size(),
        "context_len": args.context_len,
        "train_docs": train_docs,
        "val_docs": val_docs,
        "train_tokens": train_tokens,
        "val_tokens": val_tokens,
        "created_at": stats["generated_at"],
        "filter_report": str(args.report),
        "stats_json": str(args.stats),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    args.report.write_text(build_report(stats), encoding="utf-8")

    print(json.dumps({
        "seen_docs": seen_docs,
        "accepted_docs": accepted_docs,
        "train_tokens": train_tokens,
        "val_tokens": val_tokens,
        "recommendation": stats["recommendation"],
        "report": str(args.report),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
