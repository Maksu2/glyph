#!/usr/bin/env python3
"""Build the quality-first, source-aware Glyph-100M v2.4 core corpus."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from glyph100_dataset_identity import parent_doc_id_for  # noqa: E402
from glyph100_dataset_v2_2_build import (  # noqa: E402
    clean_wikitext,
    common_bad_pattern_reasons,
    load_sentencepiece,
    word_count,
)
from glyph100_dataset_v2_filter import (  # noqa: E402
    FilterConfig,
    evaluate_document,
    percentile,
    stable_bucket,
    truncate_text,
)


DEFAULT_CONFIG = ROOT / "configs/glyph100_v2_4_core.json"
TOKENS_PER_STEP = 4 * 512 * 8
WEB_RESIDUE_RE = re.compile(
    r"dodaj do koszyka|kup teraz|skontaktuj się z nami|nasza firma|polityka prywatności|"
    r"cookies|czytaj więcej|zobacz także|forum|komentarze|zaloguj|zarejestruj|"
    r"sprawdź ofertę|formularz kontaktowy|newsletter|wszelkie prawa zastrzeżone",
    re.IGNORECASE,
)
WIKI_MARKUP_RE = re.compile(r"(?:\bthumb\||\bmały\||\[\[|\]\]|\{\{|\}\}|Kategoria:)", re.IGNORECASE)
WIKINEWS_TAIL_RE = re.compile(r"(?is)\s+(?:Źródła|Przypisy|Linki zewnętrzne)\s+(?=Kategoria:|https?://|$)")
GUTENBERG_RE = re.compile(r"(?is)\*{0,3}\s*(?:END OF|START OF).*?PROJECT GUTENBERG.*$")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_priority(value: str) -> int:
    return int.from_bytes(hashlib.blake2b(value.encode("utf-8"), digest_size=8).digest(), "big")


def stable_fraction(value: str) -> float:
    return stable_priority(value) / float(2**64 - 1)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_uint16(handle, ids: list[int]) -> None:
    np.asarray(ids, dtype=np.uint16).tofile(handle)


def source_filter_config(source: str) -> FilterConfig:
    if source in {"wolne_lektury", "1000_novels", "eltec_pol"}:
        return FilterConfig(
            min_words=80,
            max_chars=55_000,
            min_alpha_ratio=0.50,
            min_polish_stopword_ratio=0.010,
            max_punct_symbol_ratio=0.16,
            max_repetition_score=0.050,
            min_unique_word_ratio=0.18,
            max_word_frequency_ratio=0.14,
            max_urls=0,
            max_line_length=20_000,
        )
    if source == "parliamentary":
        return FilterConfig(
            min_words=120,
            max_chars=55_000,
            min_alpha_ratio=0.58,
            min_polish_stopword_ratio=0.020,
            max_punct_symbol_ratio=0.12,
            max_repetition_score=0.030,
            min_unique_word_ratio=0.22,
            max_word_frequency_ratio=0.11,
            max_urls=0,
            max_line_length=18_000,
        )
    if source in {"wikibooks", "wikinews", "wikisource"}:
        return FilterConfig(
            min_words=80,
            max_chars=50_000,
            min_alpha_ratio=0.56,
            min_polish_stopword_ratio=0.016,
            max_punct_symbol_ratio=0.13,
            max_repetition_score=0.034,
            min_unique_word_ratio=0.22,
            max_word_frequency_ratio=0.12,
            max_urls=0,
            max_line_length=16_000,
        )
    return FilterConfig(
        min_words=60,
        max_chars=80_000,
        min_alpha_ratio=0.54,
        min_polish_stopword_ratio=0.014,
        max_punct_symbol_ratio=0.14,
        max_repetition_score=0.040,
        min_unique_word_ratio=0.21,
        max_word_frequency_ratio=0.13,
        max_urls=0,
        max_line_length=20_000,
    )


def clean_source_text(source: str, text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    text = GUTENBERG_RE.sub("", text)
    if source == "wikibooks":
        text = clean_wikitext(text)
    elif source == "wikinews":
        tail = WIKINEWS_TAIL_RE.search(text)
        if tail:
            text = text[: tail.start()]
        text = re.sub(r"(?is)\s+Źródła\s+Kategoria:.*$", "", text)
        text = re.sub(r"(?is)\s+Kategoria:[^\n]+$", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def paragraph_chunks(text: str, max_chars: int = 48_000) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    if len(paragraphs) <= 1:
        paragraphs = [part.strip() for part in re.split(r"(?<=[.!?…])\s+(?=[A-ZĄĆĘŁŃÓŚŹŻ„—])", text) if part.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_chars = 0
    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            if current:
                chunks.append("\n\n".join(current))
                current, current_chars = [], 0
            for start in range(0, len(paragraph), max_chars):
                chunks.append(paragraph[start : start + max_chars])
            continue
        extra = len(paragraph) + (2 if current else 0)
        if current and current_chars + extra > max_chars:
            chunks.append("\n\n".join(current))
            current, current_chars = [], 0
        current.append(paragraph)
        current_chars += extra
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def pre_reject_reasons(source: str, text: str) -> list[str]:
    reasons = common_bad_pattern_reasons(text)
    if WEB_RESIDUE_RE.search(text):
        reasons.append("web_residue_pattern")
    if source in {"wikibooks", "wikinews", "wikisource"} and WIKI_MARKUP_RE.search(text):
        reasons.append("wiki_markup_residue")
    if source == "parliamentary" and len(re.findall(r"(?im)^\s*\d+[.)]\s+", text)) >= 15:
        reasons.append("parliamentary_question_list_heavy")
    return list(dict.fromkeys(reasons))


@dataclass
class CandidateIndex:
    path: Path
    rows: list[tuple[int, str, str, int]] = field(default_factory=list)
    seen_docs: int = 0
    accepted_docs: int = 0
    accepted_tokens: int = 0
    rejected_docs: int = 0
    rejection_reasons: collections.Counter[str] = field(default_factory=collections.Counter)

    def select(self, target_tokens: int) -> tuple[set[str], dict[str, int]]:
        parents: dict[str, dict[str, Any]] = {}
        for priority, record_id, parent_id, tokens in self.rows:
            state = parents.setdefault(parent_id, {"priority": priority, "tokens": 0, "ids": []})
            state["priority"] = min(state["priority"], priority)
            state["tokens"] += tokens
            state["ids"].append(record_id)
        selected: set[str] = set()
        selected_parents: dict[str, int] = {}
        used = 0
        for parent_id, state in sorted(parents.items(), key=lambda item: (item[1]["priority"], item[0])):
            selected.update(state["ids"])
            selected_parents[parent_id] = int(state["tokens"])
            used += int(state["tokens"])
            if used >= target_tokens:
                break
        return selected, selected_parents


def add_hashes(metrics: dict[str, Any], exact: set[str], normalized: set[str], near: set[str]) -> None:
    exact.add(str(metrics["exact_hash"]))
    normalized.add(str(metrics["normalized_hash"]))
    near.add(str(metrics["near_hash"]))


def candidate_payload(record: dict[str, Any], metrics: dict[str, Any], token_count: int) -> dict[str, Any]:
    record["quality_score"] = round(float(metrics.get("quality_score") or 0.0), 4)
    record.setdefault("meta", {})["token_count"] = token_count
    record["meta"]["word_count"] = int(metrics.get("words") or word_count(record["text"]))
    record["meta"]["quality_metrics"] = {
        key: metrics.get(key)
        for key in (
            "alpha_ratio",
            "polish_stopword_ratio",
            "repetition_score",
            "unique_word_ratio",
            "quality_score",
        )
    }
    return record


def build_existing_wikipedia_candidates(
    source: dict[str, Any],
    input_path: Path,
    output_path: Path,
    sp,
    eos_id: int,
    exact: set[str],
    normalized: set[str],
    near: set[str],
    rejected_samples: list[dict[str, Any]],
    max_source_rows: int = 0,
) -> CandidateIndex:
    index = CandidateIndex(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    config = source_filter_config("wikipedia_pl")
    with input_path.open(encoding="utf-8") as source_handle, output_path.open("w", encoding="utf-8") as out:
        for line in source_handle:
            if not line.strip():
                continue
            raw = json.loads(line)
            if raw.get("source") != "wikipedia_pl":
                continue
            index.seen_docs += 1
            if max_source_rows and index.seen_docs > max_source_rows:
                break
            result = evaluate_document(
                str(raw.get("text") or ""),
                source="wikipedia_pl",
                config=config,
                exact_seen=exact,
                normalized_seen=normalized,
                near_seen=near,
            )
            if not result.accepted:
                index.rejected_docs += 1
                index.rejection_reasons.update(result.reasons)
                if len(rejected_samples) < 100:
                    rejected_samples.append(
                        {"source": "wikipedia_pl", "id": raw.get("id"), "reject_reasons": result.reasons, "text": truncate_text(result.text)}
                    )
                continue
            record = dict(raw)
            record["text"] = result.text
            parent = str(record.get("parent_doc_id") or record.get("doc_id") or record.get("id"))
            record["parent_doc_id"] = parent
            ids = sp.encode(record["text"], out_type=int)
            ids.append(eos_id)
            record = candidate_payload(record, result.metrics, len(ids))
            priority = stable_priority(f"wikipedia_pl:{parent}")
            out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            index.rows.append((priority, str(record["id"]), parent, len(ids)))
            index.accepted_docs += 1
            index.accepted_tokens += len(ids)
            add_hashes(result.metrics, exact, normalized, near)
    return index


def iter_parquet_rows(path: Path) -> Iterable[dict[str, Any]]:
    parquet = pq.ParquetFile(path)
    columns = [name for name in ("id", "text", "source", "added", "created", "token_count", "license", "author") if name in parquet.schema.names]
    for batch in parquet.iter_batches(batch_size=256, columns=columns, use_threads=True):
        yield from batch.to_pylist()


def build_dynaword_candidates(
    source: dict[str, Any],
    input_path: Path,
    output_path: Path,
    sp,
    eos_id: int,
    exact: set[str],
    normalized: set[str],
    near: set[str],
    rejected_samples: list[dict[str, Any]],
    max_source_rows: int = 0,
) -> CandidateIndex:
    name = source["name"]
    index = CandidateIndex(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    config = source_filter_config(name)
    fraction = float(source.get("candidate_fraction", 1.0))
    started = time.monotonic()
    with output_path.open("w", encoding="utf-8") as out:
        for raw_index, raw in enumerate(iter_parquet_rows(input_path)):
            index.seen_docs += 1
            if max_source_rows and index.seen_docs > max_source_rows:
                break
            source_id = str(raw.get("id") or raw_index)
            parent = f"dynaword:{name}:{source_id}"
            if stable_fraction(parent) >= fraction:
                continue
            text = clean_source_text(name, str(raw.get("text") or ""))
            for chunk_index, chunk in enumerate(paragraph_chunks(text)):
                reasons = pre_reject_reasons(name, chunk)
                result = evaluate_document(
                    chunk,
                    source=name,
                    config=config,
                    exact_seen=exact,
                    normalized_seen=normalized,
                    near_seen=near,
                )
                reasons.extend(result.reasons)
                reasons = list(dict.fromkeys(reasons))
                if reasons:
                    index.rejected_docs += 1
                    index.rejection_reasons.update(reasons)
                    if len(rejected_samples) < 100:
                        rejected_samples.append(
                            {
                                "source": name,
                                "id": source_id,
                                "chunk": chunk_index,
                                "reject_reasons": reasons,
                                "metrics": result.metrics,
                                "text": truncate_text(result.text or chunk),
                            }
                        )
                    continue
                record_id = f"glyph100-v2-4-{name}-{source_id}-chunk-{chunk_index:04d}"
                ids = sp.encode(result.text, out_type=int)
                ids.append(eos_id)
                record = candidate_payload(
                    {
                        "id": record_id,
                        "source": name,
                        "source_id": source_id,
                        "doc_id": f"{parent}#chunk-{chunk_index:04d}",
                        "parent_doc_id": parent,
                        "title": "",
                        "url": f"https://huggingface.co/datasets/SlayerLab/polish-dynaword",
                        "license": raw.get("license") or "see upstream dataset metadata",
                        "language": "pl",
                        "text": result.text,
                        "meta": {
                            "source_dataset": "SlayerLab/polish-dynaword",
                            "upstream_source": raw.get("source") or name,
                            "upstream_token_count": raw.get("token_count"),
                            "author": raw.get("author") or "",
                            "created": raw.get("created"),
                            "added": raw.get("added"),
                            "chunk_index": chunk_index,
                        },
                    },
                    result.metrics,
                    len(ids),
                )
                priority = stable_priority(f"{name}:{parent}")
                out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                index.rows.append((priority, record_id, parent, len(ids)))
                index.accepted_docs += 1
                index.accepted_tokens += len(ids)
                add_hashes(result.metrics, exact, normalized, near)
            if index.seen_docs % 25_000 == 0:
                print(
                    f"{name}: seen={index.seen_docs:,} candidates={index.accepted_docs:,} "
                    f"tokens={index.accepted_tokens:,} elapsed={time.monotonic() - started:.1f}s",
                    flush=True,
                )
    return index


def choose_val_parents(source: str, parents: dict[str, int], val_per_mille: int) -> set[str]:
    target = max(1, int(sum(parents.values()) * val_per_mille / 1000))
    selected: set[str] = set()
    used = 0
    for parent, tokens in sorted(parents.items(), key=lambda item: (stable_priority(f"val:{source}:{item[0]}"), item[0])):
        selected.add(parent)
        used += tokens
        if used >= target:
            break
    return selected


def ensure_outputs(config: dict[str, Any], force: bool) -> dict[str, Path]:
    paths = {key: ROOT / value for key, value in config["outputs"].items()}
    protected = {
        (ROOT / "data/processed/glyph100_v2_3_1_train.bin").resolve(),
        (ROOT / "data/processed/glyph100_v2_3_1_val.bin").resolve(),
        (ROOT / "data/processed/glyph100_v2_3_1_metadata.json").resolve(),
    }
    for path in paths.values():
        if path.resolve() in protected:
            raise SystemExit(f"refusing protected output: {path}")
    existing = [path for path in paths.values() if path.exists() or path.is_symlink()]
    if existing and not force:
        raise SystemExit("v2.4 outputs already exist; use --force-v2-4 only after reviewing them:\n" + "\n".join(map(str, existing)))
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    return paths


def keep_sample(samples: list[dict[str, Any]], record: dict[str, Any], key: str, limit: int = 50) -> None:
    payload = {
        "id": record.get("id"),
        "source": record.get("source"),
        "parent_doc_id": record.get("parent_doc_id"),
        "split": (record.get("meta") or {}).get("split"),
        "token_count": (record.get("meta") or {}).get("token_count"),
        "quality_score": record.get("quality_score"),
        "text": truncate_text(str(record.get("text") or ""), 1200),
    }
    if len(samples) < limit:
        samples.append(payload)
        return
    bucket = stable_bucket(key, 1_000_000)
    if bucket < limit * 100:
        samples[bucket % limit] = payload


def render_report(stats: dict[str, Any]) -> str:
    source_rows = []
    for name, source in stats["sources"].items():
        source_rows.append(
            f"| `{name}` | {source['seen_docs']:,} | {source['selected_docs']:,} | {source['tokens']:,} | "
            f"{source['tokens'] / max(stats['total_tokens'], 1):.1%} | {source['train_tokens']:,} | {source['val_tokens']:,} |"
        )
    training_rows = []
    for steps in (1_000, 5_000, 20_000, 40_000, 50_000):
        tokens = steps * TOKENS_PER_STEP
        training_rows.append(f"| {steps:,} | {tokens:,} | {tokens / max(stats['train_tokens'], 1):.2f} | {tokens / 3239.78 / 3600:.1f} h |")
    return f"""# Glyph-100M Dataset v2.4 Core Report

Generated: {stats['generated_at']}

## Decision

{stats['recommendation']}

No training was started. FineWeb2, HPLT, legacy and gated FinetextPL-Edu are not part of this build.

## Corpus

- total tokens: {stats['total_tokens']:,}
- train tokens: {stats['train_tokens']:,}
- validation tokens: {stats['val_tokens']:,}
- documents/chunks: {stats['total_docs']:,}
- parent documents: {stats['parent_docs']:,}
- parent leakage: {stats['parent_leakage_count']}
- token/word ratio: {stats['token_word_ratio']:.3f}
- target reached: {stats['target_reached']}

| source | upstream rows seen | selected chunks | tokens | share | train tokens | val tokens |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(source_rows)}

## Training Budget

At batch 4, context 512 and gradient accumulation 8, one optimizer step is 16,384 tokens.

| optimizer steps | tokens | train-corpus passes | estimated RX 5500 XT time |
|---:|---:|---:|---:|
{chr(10).join(training_rows)}

## Quality Gates

- deterministic source quotas and parent-level selection
- source-stratified parent-document validation split
- exact, normalized and practical near-duplicate rejection
- source-specific cleanup for literature, parliamentary records, Wikibooks and Wikinews
- real Glyph SentencePiece tokenizer used for every token count
- no web crawl source in the core build

## Top Rejection Reasons

```json
{json.dumps(stats['rejection_reasons'], ensure_ascii=False, indent=2)}
```

## Risks

- Literature is intentionally prominent; it improves continuous Polish but includes older style.
- Parliamentary text is capped and should not be allowed to dominate later builds.
- Wikibooks/Wikinews remain small because markup and short-page filters are strict.
- This corpus supports a staged from-scratch proxy run, not an automatic long training approval.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--force-v2-4", action="store_true")
    parser.add_argument("--keep-work", action="store_true")
    parser.add_argument("--max-source-rows", type=int, default=0)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if args.smoke:
        smoke_root = Path("/tmp/glyph100_v2_4_smoke")
        config["work_root"] = str(smoke_root / "work")
        config["minimum_ready_tokens"] = 1
        config["target_total_tokens"] = 70_000
        config["outputs"] = {
            "train_bin": str(smoke_root / "train.bin"),
            "val_bin": str(smoke_root / "val.bin"),
            "metadata": str(smoke_root / "metadata.json"),
            "docs_store": str(smoke_root / "docs.jsonl"),
            "docs_link": str(smoke_root / "docs-link.jsonl"),
            "stats": str(smoke_root / "stats.json"),
            "report": str(smoke_root / "report.md"),
            "accepted_samples": str(smoke_root / "accepted.jsonl"),
            "rejected_samples": str(smoke_root / "rejected.jsonl"),
            "final_samples": str(smoke_root / "final.jsonl"),
        }
        for source in config["sources"]:
            source["target_tokens"] = 10_000
            source["candidate_fraction"] = 1.0
        args.max_source_rows = args.max_source_rows or 32
        args.force_v2_4 = True
    paths = ensure_outputs(config, args.force_v2_4)
    tokenizer_path = ROOT / config["tokenizer"]
    raw_root = ROOT / config["raw_root"]
    work_root = ROOT / config["work_root"]
    work_root.mkdir(parents=True, exist_ok=True)
    sp = load_sentencepiece(tokenizer_path)
    eos_id = sp.eos_id()
    if eos_id < 0:
        raise SystemExit("tokenizer has no EOS token")

    exact: set[str] = set()
    normalized: set[str] = set()
    near: set[str] = set()
    rejected_samples: list[dict[str, Any]] = []
    indices: dict[str, CandidateIndex] = {}
    started = time.monotonic()

    for source in config["sources"]:
        name = source["name"]
        candidate_path = work_root / f"{name}.candidates.jsonl"
        print(f"building candidates: {name}", flush=True)
        if source["kind"] == "existing_jsonl":
            indices[name] = build_existing_wikipedia_candidates(
                source,
                ROOT / config["existing_wikipedia_docs"],
                candidate_path,
                sp,
                eos_id,
                exact,
                normalized,
                near,
                rejected_samples,
                args.max_source_rows,
            )
        else:
            parquet_path = raw_root / name / f"{name}.parquet"
            expected = int(source["expected_bytes"])
            if not parquet_path.exists() or parquet_path.stat().st_size != expected:
                raise SystemExit(f"missing or incomplete source {name}: run scripts/glyph100_dynaword_fetch.py")
            indices[name] = build_dynaword_candidates(
                source,
                parquet_path,
                candidate_path,
                sp,
                eos_id,
                exact,
                normalized,
                near,
                rejected_samples,
                args.max_source_rows,
            )
        print(
            f"{name}: accepted candidate tokens={indices[name].accepted_tokens:,} "
            f"rejected chunks={indices[name].rejected_docs:,}",
            flush=True,
        )

    selected_ids: dict[str, set[str]] = {}
    selected_parents: dict[str, dict[str, int]] = {}
    val_parents: dict[str, set[str]] = {}
    for source in config["sources"]:
        name = source["name"]
        selected_ids[name], selected_parents[name] = indices[name].select(int(source["target_tokens"]))
        val_parents[name] = choose_val_parents(name, selected_parents[name], int(config["val_per_mille"]))

    train_tokens = val_tokens = total_words = total_docs = 0
    source_stats: dict[str, dict[str, Any]] = {}
    final_samples: list[dict[str, Any]] = []
    accepted_samples: list[dict[str, Any]] = []
    seen_parent_splits: dict[str, str] = {}
    leakage: set[str] = set()
    token_lengths: list[int] = []

    docs_store = paths["docs_store"]
    with paths["train_bin"].open("wb") as train_out, paths["val_bin"].open("wb") as val_out, docs_store.open("w", encoding="utf-8") as docs_out:
        for source in config["sources"]:
            name = source["name"]
            stats = {
                "seen_docs": indices[name].seen_docs,
                "candidate_docs": indices[name].accepted_docs,
                "candidate_tokens": indices[name].accepted_tokens,
                "selected_docs": 0,
                "parents": len(selected_parents[name]),
                "tokens": 0,
                "train_tokens": 0,
                "val_tokens": 0,
                "train_docs": 0,
                "val_docs": 0,
                "target_tokens": int(source["target_tokens"]),
                "rejection_reasons": dict(indices[name].rejection_reasons.most_common(30)),
            }
            with indices[name].path.open(encoding="utf-8") as handle:
                for line in handle:
                    record = json.loads(line)
                    if str(record["id"]) not in selected_ids[name]:
                        continue
                    parent = str(record["parent_doc_id"])
                    split = "val" if parent in val_parents[name] else "train"
                    previous = seen_parent_splits.setdefault(f"{name}:{parent}", split)
                    if previous != split:
                        leakage.add(f"{name}:{parent}")
                    ids = sp.encode(record["text"], out_type=int)
                    ids.append(eos_id)
                    expected_tokens = int(record["meta"]["token_count"])
                    if len(ids) != expected_tokens:
                        raise RuntimeError(f"token count changed for {record['id']}: {expected_tokens} -> {len(ids)}")
                    record["meta"]["split"] = split
                    record["meta"]["dataset_name"] = config["dataset_name"]
                    docs_out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                    if split == "val":
                        write_uint16(val_out, ids)
                        val_tokens += len(ids)
                        stats["val_tokens"] += len(ids)
                        stats["val_docs"] += 1
                    else:
                        write_uint16(train_out, ids)
                        train_tokens += len(ids)
                        stats["train_tokens"] += len(ids)
                        stats["train_docs"] += 1
                    stats["tokens"] += len(ids)
                    stats["selected_docs"] += 1
                    total_docs += 1
                    total_words += int(record["meta"]["word_count"])
                    token_lengths.append(len(ids))
                    keep_sample(accepted_samples, record, f"accepted:{record['id']}")
                    keep_sample(final_samples, record, f"final:{record['id']}")
            source_stats[name] = stats

    docs_link = paths["docs_link"]
    if docs_link.exists() or docs_link.is_symlink():
        docs_link.unlink()
    docs_link.symlink_to(docs_store.resolve())

    total_tokens = train_tokens + val_tokens
    rejection_reasons = collections.Counter()
    for index in indices.values():
        rejection_reasons.update(index.rejection_reasons)
    manifest_path = raw_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None
    target_reached = total_tokens >= int(config["minimum_ready_tokens"])
    recommendation = (
        "READY FOR A 1K/5K FROM-SCRATCH PROXY: the core corpus passed the token target, source mix and parent-leakage gates. "
        "Do not approve a long run until the proxy beats the old v2.3.1 baseline at matched exposure."
        if target_reached and not leakage
        else "NOT READY: the core corpus missed the minimum token target or parent split gate; inspect source shortfalls before training."
    )
    stats = {
        "generated_at": now_utc(),
        "dataset_name": config["dataset_name"],
        "config": str(config_path.relative_to(ROOT)),
        "tokenizer": str(tokenizer_path.relative_to(ROOT)),
        "tokenizer_sha256": sha256_file(tokenizer_path),
        "train_bin": display_path(paths["train_bin"]),
        "val_bin": display_path(paths["val_bin"]),
        "docs_jsonl": display_path(docs_link),
        "docs_store": display_path(docs_store),
        "train_tokens": train_tokens,
        "val_tokens": val_tokens,
        "total_tokens": total_tokens,
        "total_docs": total_docs,
        "parent_docs": len(seen_parent_splits),
        "parent_leakage_count": len(leakage),
        "parent_leakage_examples": sorted(leakage)[:20],
        "token_word_ratio": total_tokens / max(total_words, 1),
        "token_length_percentiles": {name: percentile(token_lengths, p) for name, p in (("p50", 0.5), ("p90", 0.9), ("p99", 0.99))},
        "target_total_tokens": int(config["target_total_tokens"]),
        "minimum_ready_tokens": int(config["minimum_ready_tokens"]),
        "target_reached": target_reached,
        "sources": source_stats,
        "rejection_reasons": dict(rejection_reasons.most_common(50)),
        "raw_manifest": manifest,
        "build_seconds": round(time.monotonic() - started, 3),
        "recommendation": recommendation,
        "no_training_started": True,
    }
    paths["metadata"].write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths["stats"].write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths["report"].write_text(render_report(stats), encoding="utf-8")
    write_jsonl(paths["accepted_samples"], accepted_samples)
    write_jsonl(paths["rejected_samples"], rejected_samples)
    write_jsonl(paths["final_samples"], final_samples)
    print(json.dumps({key: stats[key] for key in ("total_tokens", "train_tokens", "val_tokens", "total_docs", "parent_leakage_count", "target_reached", "build_seconds")}, indent=2))


if __name__ == "__main__":
    main()
