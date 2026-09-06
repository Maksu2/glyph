#!/usr/bin/env python3
"""Build Glyph-100M v2.4.2 by correcting the v2.4.1 source mix."""

from __future__ import annotations

import argparse
import collections
import hashlib
import heapq
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from glyph100_dataset_v2_2_build import load_sentencepiece  # noqa: E402
from glyph100_dataset_v2_4_build import (  # noqa: E402
    WEB_RESIDUE_RE,
    WIKI_MARKUP_RE,
    sha256_file,
    stable_priority,
    write_jsonl,
)
from glyph100_dataset_v2_filter import normalize_for_hash, sha1_text, truncate_text  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs/glyph100_v2_4_2_core.json"
TOKENS_PER_STEP = 4 * 512 * 8
LITERATURE_SOURCES = {"wolne_lektury", "1000_novels", "eltec_pol", "wikisource"}

WIKI_LOCALITY_PATTERNS = {
    "wiki_1975_1998_template": re.compile(
        r"\bw latach 1975[–-]1998\b.{0,120}\b(?:miejscowość|gmina|województw)",
        re.IGNORECASE | re.DOTALL,
    ),
    "wiki_population_template": re.compile(
        r"\bgmin[ęa]\s+zamieszkiwał[oa]|\bwedług danych z (?:30 czerwca|31 grudnia)\b",
        re.IGNORECASE,
    ),
    "wiki_surface_template": re.compile(
        r"\bstruktura powierzchni\b|\bgęstość zaludnienia\b",
        re.IGNORECASE,
    ),
    "wiki_register_template": re.compile(
        r"\brejestr(?:u|ze)? zabytków\b.{0,180}\bnr rej\.",
        re.IGNORECASE | re.DOTALL,
    ),
    "wiki_admin_template": re.compile(
        r"\bmiejscowość należała administracyjnie\b",
        re.IGNORECASE,
    ),
}
GEO_TERMS = (
    re.compile(r"\bgmin\w*", re.IGNORECASE),
    re.compile(r"\bpowiat\w*", re.IGNORECASE),
    re.compile(r"\bwojewództw\w*", re.IGNORECASE),
    re.compile(r"\bmiejscowoś\w*", re.IGNORECASE),
    re.compile(r"\bmieszkańc\w*", re.IGNORECASE),
    re.compile(r"\b(?:km2|km²)\b", re.IGNORECASE),
)
PARLIAMENTARY_CITATION_PATTERNS = (
    re.compile(r"\bDz\.\s*U\.", re.IGNORECASE),
    re.compile(r"\bart\.\s*\d+", re.IGNORECASE),
    re.compile(r"\bust\.\s*\d+", re.IGNORECASE),
    re.compile(r"\bz późn\.\s*zm\.", re.IGNORECASE),
)
WIKISOURCE_INDEX_RE = re.compile(
    r"^\s*(?:\[?\d{1,4}\]?\s*)?(?:SPIS TREŚCI|INDEKS|BIBLIOGRAFIA)\b",
    re.IGNORECASE,
)
WIKISOURCE_PAGE_HEADER_RE = re.compile(
    r"^\s*\[?\d{1,4}\]?\s*[A-ZĄĆĘŁŃÓŚŹŻ]{5,}(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ.]{2,}){1,5}[.:]?\s",
)
WIKINEWS_STATS_RE = re.compile(
    r"\b(?:gmin[ęa]\s+zamieszkiwał[oa]|gęstość zaludnienia|struktura powierzchni)\b",
    re.IGNORECASE,
)
SOURCE_METADATA_PREAMBLE_RE = re.compile(
    r"<<<\s*Dane tekstu\b|\bSkany na Commons\b.{0,120}\bIndeks stron\b",
    re.IGNORECASE | re.DOTALL,
)
WIKI_MEDIA_RESIDUE_RE = re.compile(
    r"(?:\b(?:left|right|center)\|\d{2,4}px\b|\b\d{2,4}px\|(?:left|right|center)\b|"
    r"\^Spis treści\^|<\s*Okładka\b)",
    re.IGNORECASE,
)
WIKI_LOCALITY_LEAD_RE = re.compile(
    r"^[^.\n]{0,260}\b(?:wieś|dzielnica|osada|przysiółek|kolonia|gmina)\b",
    re.IGNORECASE,
)


@dataclass
class ParentState:
    tokens: int = 0
    docs: int = 0
    split: str = ""
    quality_sum: float = 0.0
    penalty: int = 0


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def ensure_outputs(config: dict[str, Any], force: bool) -> dict[str, Path]:
    paths = {name: ROOT / value for name, value in config["outputs"].items()}
    protected = {
        (ROOT / config["input_metadata"]).resolve(),
        (ROOT / config["input_docs"]).resolve(),
        (ROOT / "data/processed/glyph100_v2_4_1_train.bin").resolve(),
        (ROOT / "data/processed/glyph100_v2_4_1_val.bin").resolve(),
    }
    for path in paths.values():
        if path.resolve() in protected:
            raise SystemExit(f"refusing to overwrite v2.4.1 input: {path}")
    existing = [path for path in paths.values() if path.exists() or path.is_symlink()]
    if existing and not force:
        raise SystemExit(
            "v2.4.2 outputs already exist; inspect them before using --force-v2-4-2:\n"
            + "\n".join(str(path) for path in existing)
        )
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    return paths


def rejection_reasons(source: str, text: str) -> list[str]:
    reasons: list[str] = []
    if WEB_RESIDUE_RE.search(text):
        reasons.append("web_residue_pattern")
    if WIKI_MARKUP_RE.search(text):
        reasons.append("wiki_markup_residue")

    if source == "wikipedia_pl":
        for name, pattern in WIKI_LOCALITY_PATTERNS.items():
            if pattern.search(text):
                reasons.append(name)
        geo_hits = sum(bool(pattern.search(text)) for pattern in GEO_TERMS)
        if geo_hits >= 4 and re.search(r"\bwedług danych\b|\bdemografia\b", text, re.IGNORECASE):
            reasons.append("wiki_locality_template_cluster")
        if WIKI_LOCALITY_LEAD_RE.search(text) and geo_hits >= 2:
            reasons.append("wiki_locality_administrative_lead")

    if source == "parliamentary":
        citation_counts = [len(pattern.findall(text)) for pattern in PARLIAMENTARY_CITATION_PATTERNS]
        if citation_counts[0] >= 3 or citation_counts[1] >= 5 or citation_counts[2] >= 6 or citation_counts[3] >= 2:
            reasons.append("parliamentary_legal_citation_heavy")

    if source == "wikisource":
        prefix = text[:800]
        if WIKISOURCE_INDEX_RE.search(prefix):
            reasons.append("wikisource_index_or_bibliography")
        if WIKISOURCE_PAGE_HEADER_RE.search(prefix):
            reasons.append("wikisource_page_header_ocr")

    if source == "wikinews" and WIKINEWS_STATS_RE.search(text):
        reasons.append("wikinews_demographic_template")
    if source in {"wolne_lektury", "1000_novels", "eltec_pol", "wikisource"}:
        if SOURCE_METADATA_PREAMBLE_RE.search(text[:1600]):
            reasons.append("source_metadata_preamble")
    if source in {"wikibooks", "wikinews", "wikisource"}:
        if WIKI_MEDIA_RESIDUE_RE.search(text[:2000]):
            reasons.append("wiki_media_residue")
    if source == "wikibooks" and text.count("→") >= 5:
        reasons.append("wikibooks_link_list_heavy")

    return list(dict.fromkeys(reasons))


def parent_key(record: dict[str, Any]) -> str:
    return str(record.get("parent_doc_id") or record.get("doc_id") or record.get("id") or "")


def parent_rank(source: str, parent: str, state: ParentState) -> tuple[Any, ...]:
    avg_quality = state.quality_sum / max(state.docs, 1)
    if source == "parliamentary":
        return (state.penalty, -avg_quality, stable_priority(f"v242:{source}:{parent}"))
    return (stable_priority(f"v242:{source}:{parent}"),)


def select_parents(
    parent_states: dict[str, dict[str, ParentState]],
    targets: dict[str, int | None],
) -> tuple[dict[str, set[str]], dict[str, int]]:
    selected: dict[str, set[str]] = {}
    selected_tokens: dict[str, int] = {}
    for source, states in parent_states.items():
        target = targets.get(source)
        used = 0
        chosen: set[str] = set()
        for parent, state in sorted(states.items(), key=lambda item: parent_rank(source, item[0], item[1])):
            chosen.add(parent)
            used += state.tokens
            if target is not None and used >= int(target):
                break
        selected[source] = chosen
        selected_tokens[source] = used
    return selected, selected_tokens


def heap_sample(
    heap: list[tuple[int, str, dict[str, Any]]],
    record: dict[str, Any],
    prefix: str,
    limit: int,
    extra: dict[str, Any] | None = None,
) -> None:
    record_id = str(record.get("id") or "")
    priority = stable_priority(f"{prefix}:{record_id}")
    payload = {
        "id": record_id,
        "source": record.get("source"),
        "parent_doc_id": parent_key(record),
        "split": (record.get("meta") or {}).get("split"),
        "token_count": int((record.get("meta") or {}).get("token_count") or 0),
        "quality_score": record.get("quality_score"),
        "text": truncate_text(str(record.get("text") or ""), 1600),
    }
    if extra:
        payload.update(extra)
    item = (-priority, record_id, payload)
    if len(heap) < limit:
        heapq.heappush(heap, item)
    elif priority < -heap[0][0]:
        heapq.heapreplace(heap, item)


def ordered_samples(heap: list[tuple[int, str, dict[str, Any]]]) -> list[dict[str, Any]]:
    return [item[2] for item in sorted(heap, key=lambda item: (-item[0], item[1]))]


def write_uint16(handle, ids: Iterable[int]) -> None:
    np.asarray(list(ids), dtype=np.uint16).tofile(handle)


def scan_candidates(
    docs_path: Path,
) -> tuple[
    dict[str, dict[str, ParentState]],
    collections.Counter[str],
    collections.Counter[str],
    list[dict[str, Any]],
    dict[str, int],
]:
    states: dict[str, dict[str, ParentState]] = collections.defaultdict(dict)
    rejected = collections.Counter()
    before_sources = collections.Counter()
    rejected_heap: list[tuple[int, str, dict[str, Any]]] = []
    seen_ids: set[str] = set()
    duplicate_input_ids = 0
    with docs_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            source = str(record.get("source") or "")
            record_id = str(record.get("id") or "")
            if record_id in seen_ids:
                duplicate_input_ids += 1
            seen_ids.add(record_id)
            meta = record.get("meta") or {}
            tokens = int(meta.get("token_count") or 0)
            before_sources[source] += tokens
            text = str(record.get("text") or "")
            reasons = rejection_reasons(source, text)
            if reasons:
                rejected.update(reasons)
                heap_sample(rejected_heap, record, "rejected", 50, {"reject_reasons": reasons})
                continue
            parent = parent_key(record)
            state = states[source].setdefault(parent, ParentState())
            split = str(meta.get("split") or "")
            if state.split and state.split != split:
                raise RuntimeError(f"input parent leakage for {source}:{parent}")
            state.split = split
            state.tokens += tokens
            state.docs += 1
            state.quality_sum += float(record.get("quality_score") or 0.0)
            if source == "parliamentary":
                state.penalty += sum(len(pattern.findall(text)) for pattern in PARLIAMENTARY_CITATION_PATTERNS)
    return (
        states,
        rejected,
        before_sources,
        ordered_samples(rejected_heap),
        {"duplicate_input_ids": duplicate_input_ids, "input_docs": len(seen_ids)},
    )


def render_report(stats: dict[str, Any]) -> str:
    rows = []
    for source, item in stats["sources"].items():
        before = stats["input_source_tokens"].get(source, 0)
        rows.append(
            f"| `{source}` | {before:,} | {item['tokens']:,} | "
            f"{item['tokens'] / stats['total_tokens']:.1%} | {item['train_tokens']:,} | "
            f"{item['val_tokens']:,} |"
        )
    gates = "\n".join(
        f"- {'PASS' if value else 'FAIL'}: {name}" for name, value in stats["quality_gate_checks"].items()
    )
    return f"""# Glyph-100M Dataset v2.4.2 Core Report

Generated: {stats['generated_at']}

## Decision

{stats['recommendation']}

This build does not overwrite v2.4.1. It removes strong Wikipedia locality/demography templates, caps parliamentary text and keeps only already source-aware, non-web-crawl material.

## Hard Gates

{gates}

## Corpus

- total tokens: {stats['total_tokens']:,}
- train tokens: {stats['train_tokens']:,}
- validation tokens: {stats['val_tokens']:,}
- documents/chunks: {stats['total_docs']:,}
- parent leakage: {stats['parent_leakage_count']}
- duplicate IDs: {stats['duplicate_ids']}
- literature share: {stats['literature_share']:.2%}
- Wikipedia share: {stats['wikipedia_share']:.2%}
- parliamentary share: {stats['parliamentary_share']:.2%}
- web residue documents: {stats['residual_web_docs']:,}
- strong locality-template documents: {stats['residual_locality_docs']:,}

| source | v2.4.1 tokens | v2.4.2 tokens | share | train tokens | val tokens |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

## Removed Patterns

```json
{json.dumps(stats['rejection_reasons'], ensure_ascii=False, indent=2)}
```

## Training Budget

- 5k proxy: {5_000 * TOKENS_PER_STEP:,} tokens = {5_000 * TOKENS_PER_STEP / stats['train_tokens']:.3f} train-corpus passes
- 10k: {10_000 * TOKENS_PER_STEP:,} tokens = {10_000 * TOKENS_PER_STEP / stats['train_tokens']:.3f} train-corpus passes

## Scope

The only approved automatic run after independent validation is a fresh, matched-config 5k proxy. A continuation beyond 5k requires checkpoint evaluation against v2.4.1 at equal exposure.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--force-v2-4-2", action="store_true")
    args = parser.parse_args()

    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    paths = ensure_outputs(config, args.force_v2_4_2)
    input_metadata = json.loads((ROOT / config["input_metadata"]).read_text(encoding="utf-8"))
    if input_metadata.get("dataset_name") != "glyph100_dataset_v2_4_1_core":
        raise SystemExit("v2.4.2 must be derived from the reviewed v2.4.1 corpus")
    if int(input_metadata.get("parent_leakage_count", -1)) != 0:
        raise SystemExit("v2.4.1 input has parent leakage")

    tokenizer_path = ROOT / config["tokenizer"]
    sp = load_sentencepiece(tokenizer_path)
    eos_id = sp.eos_id()
    if eos_id < 0:
        raise SystemExit("tokenizer has no EOS token")
    docs_path = ROOT / config["input_docs"]
    started = time.monotonic()
    parent_states, rejected, before_sources, rejected_samples, scan_meta = scan_candidates(docs_path)
    selected, selected_estimates = select_parents(parent_states, config["source_targets"])

    accepted_heap: list[tuple[int, str, dict[str, Any]]] = []
    final_heap: list[tuple[int, str, dict[str, Any]]] = []
    source_stats: dict[str, dict[str, int]] = collections.defaultdict(
        lambda: {"tokens": 0, "train_tokens": 0, "val_tokens": 0, "docs": 0, "train_docs": 0, "val_docs": 0}
    )
    seen_ids: set[str] = set()
    duplicate_ids = 0
    parent_splits: dict[str, str] = {}
    leakage: set[str] = set()
    exact_hashes: set[str] = set()
    normalized_hashes: set[str] = set()
    exact_duplicates = 0
    normalized_duplicates = 0
    residual_web_docs = 0
    residual_locality_docs = 0
    total_words = 0

    with (
        paths["train_bin"].open("wb") as train_out,
        paths["val_bin"].open("wb") as val_out,
        paths["docs_store"].open("w", encoding="utf-8") as docs_out,
        docs_path.open(encoding="utf-8") as source_handle,
    ):
        for line in source_handle:
            if not line.strip():
                continue
            record = json.loads(line)
            source = str(record.get("source") or "")
            text = str(record.get("text") or "")
            if rejection_reasons(source, text):
                continue
            parent = parent_key(record)
            if parent not in selected.get(source, set()):
                continue
            record_id = str(record.get("id") or "")
            if record_id in seen_ids:
                duplicate_ids += 1
            seen_ids.add(record_id)
            exact = sha1_text(text)
            normalized = sha1_text(normalize_for_hash(text))
            if exact in exact_hashes:
                exact_duplicates += 1
            if normalized in normalized_hashes:
                normalized_duplicates += 1
            exact_hashes.add(exact)
            normalized_hashes.add(normalized)

            ids = sp.encode(text, out_type=int)
            ids.append(eos_id)
            meta = dict(record.get("meta") or {})
            expected = int(meta.get("token_count") or 0)
            if len(ids) != expected:
                raise RuntimeError(f"token count changed for {record_id}: {expected} -> {len(ids)}")
            split = str(meta.get("split") or "")
            if split not in {"train", "val"}:
                raise RuntimeError(f"invalid split for {record_id}: {split!r}")
            key = f"{source}:{parent}"
            previous = parent_splits.setdefault(key, split)
            if previous != split:
                leakage.add(key)

            meta["split"] = split
            meta["dataset_name"] = config["dataset_name"]
            meta["derived_from"] = input_metadata["dataset_name"]
            meta["v2_4_2_filter_contract"] = "locality_templates+capped_parliamentary"
            meta["token_count"] = len(ids)
            record["meta"] = meta
            docs_out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            if split == "val":
                write_uint16(val_out, ids)
            else:
                write_uint16(train_out, ids)

            state = source_stats[source]
            state["tokens"] += len(ids)
            state[f"{split}_tokens"] += len(ids)
            state["docs"] += 1
            state[f"{split}_docs"] += 1
            total_words += int(meta.get("word_count") or len(text.split()))
            if WEB_RESIDUE_RE.search(text):
                residual_web_docs += 1
            if source == "wikipedia_pl" and rejection_reasons(source, text):
                residual_locality_docs += 1
            heap_sample(accepted_heap, record, "accepted", 50)
            heap_sample(final_heap, record, "final", 50)

    docs_link = paths["docs_link"]
    if docs_link.exists() or docs_link.is_symlink():
        docs_link.unlink()
    docs_link.symlink_to(paths["docs_store"].resolve())

    train_tokens = sum(item["train_tokens"] for item in source_stats.values())
    val_tokens = sum(item["val_tokens"] for item in source_stats.values())
    total_tokens = train_tokens + val_tokens
    total_docs = sum(item["docs"] for item in source_stats.values())
    if paths["train_bin"].stat().st_size != train_tokens * 2:
        raise RuntimeError("train binary size does not match token count")
    if paths["val_bin"].stat().st_size != val_tokens * 2:
        raise RuntimeError("validation binary size does not match token count")

    literature_tokens = sum(source_stats[name]["tokens"] for name in LITERATURE_SOURCES)
    wikipedia_tokens = source_stats["wikipedia_pl"]["tokens"]
    parliamentary_tokens = source_stats["parliamentary"]["tokens"]
    gates = config["quality_gates"]
    checks = {
        "minimum token floor": total_tokens >= int(config["minimum_ready_tokens"]),
        "literature share": literature_tokens / total_tokens >= float(gates["minimum_literature_share"]),
        "Wikipedia share": wikipedia_tokens / total_tokens <= float(gates["maximum_wikipedia_share"]),
        "parliamentary share": parliamentary_tokens / total_tokens <= float(gates["maximum_parliamentary_share"]),
        "web residue": residual_web_docs <= int(gates["maximum_web_residue_docs"]),
        "strong locality templates": residual_locality_docs <= int(gates["maximum_strong_locality_template_docs"]),
        "parent split leakage": len(leakage) <= int(gates["maximum_parent_leakage"]),
        "duplicate IDs": duplicate_ids <= int(gates["maximum_duplicate_ids"]),
        "exact text duplicates": exact_duplicates == 0,
        "normalized text duplicates": normalized_duplicates == 0,
        "tokenizer checksum": sha256_file(tokenizer_path) == input_metadata["tokenizer_sha256"],
    }
    ready = all(checks.values())
    recommendation = (
        "READY FOR INDEPENDENT VALIDATION AND A FRESH 5K PROXY: all source-mix, residue, split, dedup and tokenizer gates passed."
        if ready
        else "NOT READY: at least one hard v2.4.2 quality gate failed. Do not train."
    )
    stats: dict[str, Any] = {
        "generated_at": now_utc(),
        "dataset_name": config["dataset_name"],
        "description": config["description"],
        "config": display_path(config_path),
        "derived_from": input_metadata["dataset_name"],
        "tokenizer": display_path(tokenizer_path),
        "tokenizer_sha256": sha256_file(tokenizer_path),
        "train_bin": display_path(paths["train_bin"]),
        "val_bin": display_path(paths["val_bin"]),
        "docs_jsonl": display_path(docs_link),
        "docs_store": display_path(paths["docs_store"]),
        "train_tokens": train_tokens,
        "val_tokens": val_tokens,
        "total_tokens": total_tokens,
        "total_docs": total_docs,
        "parent_docs": len(parent_splits),
        "parent_leakage_count": len(leakage),
        "parent_leakage_examples": sorted(leakage)[:20],
        "duplicate_ids": duplicate_ids,
        "exact_duplicates": exact_duplicates,
        "normalized_duplicates": normalized_duplicates,
        "token_word_ratio": total_tokens / max(total_words, 1),
        "literature_share": literature_tokens / total_tokens,
        "wikipedia_share": wikipedia_tokens / total_tokens,
        "parliamentary_share": parliamentary_tokens / total_tokens,
        "residual_web_docs": residual_web_docs,
        "residual_locality_docs": residual_locality_docs,
        "minimum_ready_tokens": int(config["minimum_ready_tokens"]),
        "input_source_tokens": dict(before_sources),
        "selected_parent_token_estimates": selected_estimates,
        "sources": {name: dict(item) for name, item in sorted(source_stats.items())},
        "rejection_reasons": dict(rejected.most_common()),
        "input_scan": scan_meta,
        "quality_gate_checks": checks,
        "ready_for_training_validation": ready,
        "recommendation": recommendation,
        "build_seconds": round(time.monotonic() - started, 3),
        "no_training_started": True,
    }
    paths["metadata"].write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths["stats"].write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths["report"].write_text(render_report(stats), encoding="utf-8")
    write_jsonl(paths["accepted_samples"], ordered_samples(accepted_heap))
    write_jsonl(paths["rejected_samples"], rejected_samples)
    write_jsonl(paths["final_samples"], ordered_samples(final_heap))
    print(
        json.dumps(
            {
                "ready_for_training_validation": ready,
                "total_tokens": total_tokens,
                "train_tokens": train_tokens,
                "val_tokens": val_tokens,
                "literature_share": stats["literature_share"],
                "wikipedia_share": stats["wikipedia_share"],
                "parliamentary_share": stats["parliamentary_share"],
                "quality_gate_checks": checks,
                "build_seconds": stats["build_seconds"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
