#!/usr/bin/env python3
"""Extend the clean v2.4 core with capped, train-only Wikisource text."""

from __future__ import annotations

import argparse
import collections
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from glyph100_dataset_v2_4_build import (  # noqa: E402
    CandidateIndex,
    add_hashes,
    candidate_payload,
    clean_source_text,
    iter_parquet_rows,
    keep_sample,
    paragraph_chunks,
    pre_reject_reasons,
    sha256_file,
    source_filter_config,
    stable_fraction,
    stable_priority,
    write_jsonl,
    write_uint16,
)
from glyph100_dataset_v2_2_build import load_sentencepiece  # noqa: E402
from glyph100_dataset_v2_filter import (  # noqa: E402
    evaluate_document,
    near_duplicate_key,
    normalize_for_hash,
    sha1_text,
    truncate_text,
    words_for_text,
)


DEFAULT_CONFIG = ROOT / "configs/glyph100_v2_4_1_core.json"
TOKENS_PER_STEP = 4 * 512 * 8


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def ensure_outputs(config: dict[str, Any], force: bool) -> dict[str, Path]:
    paths = {key: ROOT / value for key, value in config["outputs"].items()}
    protected = {
        (ROOT / config["base_train_bin"]).resolve(),
        (ROOT / config["base_val_bin"]).resolve(),
        (ROOT / config["base_metadata"]).resolve(),
        (ROOT / config["base_docs"]).resolve(),
    }
    for path in paths.values():
        if path.resolve() in protected:
            raise SystemExit(f"refusing to overwrite v2.4 base: {path}")
    existing = [path for path in paths.values() if path.exists() or path.is_symlink()]
    if existing and not force:
        raise SystemExit("v2.4.1 outputs already exist:\n" + "\n".join(map(str, existing)))
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    return paths


def load_base_dedup(path: Path) -> tuple[set[str], set[str], set[str], int]:
    exact: set[str] = set()
    normalized: set[str] = set()
    near: set[str] = set()
    rows = 0
    started = time.monotonic()
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            text = str(record.get("text") or "")
            words = words_for_text(text)
            exact.add(sha1_text(text))
            normalized.add(sha1_text(normalize_for_hash(text)))
            near.add(near_duplicate_key(words))
            rows += 1
            if rows % 50_000 == 0:
                print(f"base dedup: {rows:,} docs in {time.monotonic() - started:.1f}s", flush=True)
    return exact, normalized, near, rows


def build_wikisource_candidates(
    config: dict[str, Any],
    path: Path,
    output: Path,
    sp,
    eos_id: int,
    exact: set[str],
    normalized: set[str],
    near: set[str],
) -> tuple[CandidateIndex, list[dict[str, Any]]]:
    source = config["supplement"]
    fraction = float(source["candidate_fraction"])
    filter_config = source_filter_config("wikisource")
    index = CandidateIndex(output)
    rejected_samples: list[dict[str, Any]] = []
    output.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    with output.open("w", encoding="utf-8") as out:
        for raw_index, raw in enumerate(iter_parquet_rows(path)):
            index.seen_docs += 1
            source_id = str(raw.get("id") or raw_index)
            parent = f"dynaword:wikisource:{source_id}"
            if stable_fraction(parent) >= fraction:
                continue
            text = clean_source_text("wikisource", str(raw.get("text") or ""))
            for chunk_index, chunk in enumerate(paragraph_chunks(text)):
                reasons = pre_reject_reasons("wikisource", chunk)
                result = evaluate_document(
                    chunk,
                    source="wikisource",
                    config=filter_config,
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
                                "source": "wikisource",
                                "id": source_id,
                                "reject_reasons": reasons,
                                "metrics": result.metrics,
                                "text": truncate_text(result.text or chunk, 1200),
                            }
                        )
                    continue
                record_id = f"glyph100-v2-4-1-wikisource-{source_id}-chunk-{chunk_index:04d}"
                ids = sp.encode(result.text, out_type=int)
                ids.append(eos_id)
                record = candidate_payload(
                    {
                        "id": record_id,
                        "source": "wikisource",
                        "source_id": source_id,
                        "doc_id": f"{parent}#chunk-{chunk_index:04d}",
                        "parent_doc_id": parent,
                        "title": "",
                        "url": "https://huggingface.co/datasets/SlayerLab/polish-dynaword",
                        "license": raw.get("license") or "CC-BY-SA-3.0",
                        "language": "pl",
                        "text": result.text,
                        "quality_score": 0.0,
                        "meta": {
                            "source_dataset": "SlayerLab/polish-dynaword",
                            "upstream_source": "wikisource",
                            "upstream_token_count": raw.get("token_count"),
                            "validation_policy": source["validation_policy"],
                            "chunk_index": chunk_index,
                        },
                    },
                    result.metrics,
                    len(ids),
                )
                out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                priority = stable_priority(f"wikisource:{parent}")
                index.rows.append((priority, record_id, parent, len(ids)))
                index.accepted_docs += 1
                index.accepted_tokens += len(ids)
                add_hashes(result.metrics, exact, normalized, near)
            if index.seen_docs % 50_000 == 0:
                print(
                    f"wikisource: seen={index.seen_docs:,} candidates={index.accepted_docs:,} "
                    f"tokens={index.accepted_tokens:,} elapsed={time.monotonic() - started:.1f}s",
                    flush=True,
                )
    return index, rejected_samples


def render_report(stats: dict[str, Any]) -> str:
    rows = []
    for name, item in stats["sources"].items():
        rows.append(
            f"| `{name}` | {item['tokens']:,} | {item['tokens'] / stats['total_tokens']:.1%} | "
            f"{item['train_tokens']:,} | {item['val_tokens']:,} |"
        )
    return f"""# Glyph-100M Dataset v2.4.1 Core Report

Generated: {stats['generated_at']}

## Decision

{stats['recommendation']}

No training was started.

## Result

- total tokens: {stats['total_tokens']:,}
- train tokens: {stats['train_tokens']:,}
- validation tokens: {stats['val_tokens']:,}
- total documents/chunks: {stats['total_docs']:,}
- parent leakage: 0
- Wikipedia share: {stats['wikipedia_share']:.1%}
- literature share: {stats['literature_share']:.1%}
- parliamentary share: {stats['parliamentary_share']:.1%}
- Wikisource supplement: {stats['wikisource_tokens']:,} tokens ({stats['wikisource_share']:.1%})

| source | tokens | share | train tokens | val tokens |
|---|---:|---:|---:|---:|
{chr(10).join(rows)}

## Wikisource Split Policy

The upstream rows lack a reliable parent-work title. All supplement rows are therefore train-only. This is conservative: validation cannot contain another fragment of the same unknown work, and the limitation remains explicit in metadata.

## Training Math

- 1k steps: {1_000 * TOKENS_PER_STEP:,} tokens = {1_000 * TOKENS_PER_STEP / stats['train_tokens']:.2f} corpus passes
- 5k steps: {5_000 * TOKENS_PER_STEP:,} tokens = {5_000 * TOKENS_PER_STEP / stats['train_tokens']:.2f} corpus passes
- 20k steps: {20_000 * TOKENS_PER_STEP:,} tokens = {20_000 * TOKENS_PER_STEP / stats['train_tokens']:.2f} corpus passes
- 50k steps: {50_000 * TOKENS_PER_STEP:,} tokens = {50_000 * TOKENS_PER_STEP / stats['train_tokens']:.2f} corpus passes

## Gate

This corpus is approved only for a from-scratch 1k stability run followed by a 5k matched-exposure proxy. A longer run still requires a separate quality comparison and approval.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--force-v2-4-1", action="store_true")
    args = parser.parse_args()

    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    paths = ensure_outputs(config, args.force_v2_4_1)
    base_metadata = json.loads((ROOT / config["base_metadata"]).read_text(encoding="utf-8"))
    if base_metadata.get("parent_leakage_count") != 0:
        raise SystemExit("base v2.4 has parent leakage")
    tokenizer = ROOT / config["tokenizer"]
    sp = load_sentencepiece(tokenizer)
    eos_id = sp.eos_id()
    source = config["supplement"]
    parquet = ROOT / config["raw_root"] / source["name"] / f"{source['name']}.parquet"
    if not parquet.exists() or parquet.stat().st_size != int(source["expected_bytes"]):
        raise SystemExit("missing Wikisource parquet; run glyph100_dynaword_fetch.py with the v2.4.1 config")

    started = time.monotonic()
    exact, normalized, near, base_docs_count = load_base_dedup(ROOT / config["base_docs"])
    candidate_path = ROOT / config["work_root"] / "wikisource.candidates.jsonl"
    index, rejected_samples = build_wikisource_candidates(
        config, parquet, candidate_path, sp, eos_id, exact, normalized, near
    )
    selected_ids, selected_parents = index.select(int(source["target_tokens"]))

    shutil.copyfile(ROOT / config["base_train_bin"], paths["train_bin"])
    shutil.copyfile(ROOT / config["base_val_bin"], paths["val_bin"])
    shutil.copyfile(ROOT / config["base_docs"], paths["docs_store"])
    accepted_samples: list[dict[str, Any]] = []
    final_samples: list[dict[str, Any]] = []
    supplement_tokens = supplement_docs = 0
    with paths["train_bin"].open("ab") as train_out, paths["docs_store"].open("a", encoding="utf-8") as docs_out, candidate_path.open(encoding="utf-8") as candidates:
        for line in candidates:
            record = json.loads(line)
            if str(record["id"]) not in selected_ids:
                continue
            ids = sp.encode(record["text"], out_type=int)
            ids.append(eos_id)
            if len(ids) != int(record["meta"]["token_count"]):
                raise RuntimeError(f"token mismatch for {record['id']}")
            record["meta"]["split"] = "train"
            record["meta"]["dataset_name"] = config["dataset_name"]
            write_uint16(train_out, ids)
            docs_out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            supplement_tokens += len(ids)
            supplement_docs += 1
            keep_sample(accepted_samples, record, f"accepted:{record['id']}")
            keep_sample(final_samples, record, f"final:{record['id']}")

    docs_link = paths["docs_link"]
    if docs_link.exists() or docs_link.is_symlink():
        docs_link.unlink()
    docs_link.symlink_to(paths["docs_store"].resolve())

    train_tokens = int(base_metadata["train_tokens"]) + supplement_tokens
    val_tokens = int(base_metadata["val_tokens"])
    total_tokens = train_tokens + val_tokens
    if paths["train_bin"].stat().st_size != train_tokens * 2:
        raise RuntimeError("train binary size does not match token count")
    if paths["val_bin"].stat().st_size != val_tokens * 2:
        raise RuntimeError("validation binary size does not match token count")

    sources = json.loads(json.dumps(base_metadata["sources"]))
    sources["wikisource"] = {
        "seen_docs": index.seen_docs,
        "candidate_docs": index.accepted_docs,
        "candidate_tokens": index.accepted_tokens,
        "selected_docs": supplement_docs,
        "parents": len(selected_parents),
        "tokens": supplement_tokens,
        "train_tokens": supplement_tokens,
        "val_tokens": 0,
        "train_docs": supplement_docs,
        "val_docs": 0,
        "target_tokens": int(source["target_tokens"]),
        "validation_policy": source["validation_policy"],
        "rejection_reasons": dict(index.rejection_reasons.most_common(30)),
    }
    literature_names = {"wolne_lektury", "1000_novels", "eltec_pol", "wikisource"}
    literature_tokens = sum(int(item["tokens"]) for name, item in sources.items() if name in literature_names)
    wikipedia_tokens = int(sources["wikipedia_pl"]["tokens"])
    parliament_tokens = int(sources["parliamentary"]["tokens"])
    ready = total_tokens >= int(config["minimum_ready_tokens"])
    recommendation = (
        "READY FOR CONTROLLED 1K/5K PROXY: v2.4.1 clears the token floor without web crawl data, keeps Wikipedia below 45%, and preserves a leakage-free validation set."
        if ready
        else "NOT READY: the Wikisource supplement did not clear the minimum token floor."
    )
    stats = {
        "generated_at": now_utc(),
        "dataset_name": config["dataset_name"],
        "config": display_path(config_path),
        "base_dataset": base_metadata["dataset_name"],
        "tokenizer": display_path(tokenizer),
        "tokenizer_sha256": sha256_file(tokenizer),
        "train_bin": display_path(paths["train_bin"]),
        "val_bin": display_path(paths["val_bin"]),
        "docs_jsonl": display_path(docs_link),
        "docs_store": display_path(paths["docs_store"]),
        "train_tokens": train_tokens,
        "val_tokens": val_tokens,
        "total_tokens": total_tokens,
        "total_docs": int(base_metadata["total_docs"]) + supplement_docs,
        "parent_docs": int(base_metadata["parent_docs"]) + len(selected_parents),
        "parent_leakage_count": 0,
        "wikisource_tokens": supplement_tokens,
        "wikisource_share": supplement_tokens / total_tokens,
        "wikipedia_share": wikipedia_tokens / total_tokens,
        "literature_share": literature_tokens / total_tokens,
        "parliamentary_share": parliament_tokens / total_tokens,
        "minimum_ready_tokens": int(config["minimum_ready_tokens"]),
        "target_reached": ready,
        "sources": sources,
        "supplement_rejection_reasons": dict(index.rejection_reasons.most_common(50)),
        "supplement_candidate_fraction": float(source["candidate_fraction"]),
        "supplement_validation_policy": source["validation_policy"],
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
    print(json.dumps({key: stats[key] for key in ("total_tokens", "train_tokens", "val_tokens", "wikisource_tokens", "wikipedia_share", "literature_share", "target_reached", "build_seconds")}, indent=2))


if __name__ == "__main__":
    main()
