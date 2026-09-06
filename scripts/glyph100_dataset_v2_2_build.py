#!/usr/bin/env python3
"""Build Glyph-100M dataset v2.2 with a cleaner source-aware mix.

This script intentionally does not train anything. It creates a new dataset
namespace only: glyph100_v2_2_*. Existing v2, v2.1 and stage1 artifacts are
protected from accidental overwrite.
"""

from __future__ import annotations

import argparse
import bz2
import collections
import html
import json
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from glyph100_dataset_v2_filter import (  # noqa: E402
    WORD_RE,
    FilterConfig,
    evaluate_document,
    percentile,
    sha1_text,
    stable_bucket,
    text_metrics,
    truncate_text,
)
from glyph100_dataset_identity import parent_doc_id_for, parent_split_for  # noqa: E402


DEFAULT_BASE_DOCS = Path("data/processed/glyph100_v2_1_docs.jsonl")
DEFAULT_TOKENIZER = Path("data/processed/tokenizer.model")
DEFAULT_TRAIN_BIN = Path("data/processed/glyph100_v2_2_train.bin")
DEFAULT_VAL_BIN = Path("data/processed/glyph100_v2_2_val.bin")
DEFAULT_METADATA = Path("data/processed/glyph100_v2_2_metadata.json")
DEFAULT_DOCS_JSONL = Path("data/processed/glyph100_v2_2_docs.jsonl")
DEFAULT_REJECTED_JSONL = Path("data/processed/glyph100_v2_2_rejected.jsonl")
DEFAULT_STATS = Path("data/reports/glyph100_dataset_v2_2_stats.json")
DEFAULT_REPORT = Path("data/reports/glyph100_dataset_v2_2_report.md")
DEFAULT_ACCEPTED_SAMPLES = Path("data/reports/glyph100_dataset_v2_2_samples_accepted.jsonl")
DEFAULT_REJECTED_SAMPLES = Path("data/reports/glyph100_dataset_v2_2_samples_rejected.jsonl")
DEFAULT_FINAL_SAMPLES = Path("data/reports/glyph100_dataset_v2_2_samples_final_random.jsonl")
DEFAULT_DECISION_MD = Path("reports/glyph100_dataset_v2_2_decision_report.md")
DEFAULT_WIKIBOOKS_CACHE = Path("data/raw/wikibooks/plwikibooks-latest-pages-articles.xml.bz2")
DEFAULT_WIKIBOOKS_URL = (
    "https://dumps.wikimedia.org/plwikibooks/latest/"
    "plwikibooks-latest-pages-articles.xml.bz2"
)

TOKENS_PER_STEP = 4 * 512 * 8
TRAINING_TOKENS_50K = 50_000 * TOKENS_PER_STEP
TRAINING_TOKENS_100K = 100_000 * TOKENS_PER_STEP
TRAINING_TOKENS_200K = 200_000 * TOKENS_PER_STEP

ALLOWED_BASE_SOURCES = {"wikipedia_pl", "wolne_lektury"}

SOURCE_LICENSES = {
    "wikipedia_pl": "CC BY-SA / GFDL; verify dump terms",
    "wolne_lektury": "public domain / Wolne Lektury metadata; verify per work",
    "wikisource_pl": "CC BY-SA / GFDL; verify per page",
    "wikibooks_pl": "CC BY-SA / GFDL; verify per page",
    "allegro_summaries_source": "unknown; verify HF dataset card / original PSC terms",
}

COMMERCE_HARD_PATTERNS = [
    "dodaj do koszyka",
    "sklep internetowy",
    "zamów teraz",
    "opinie klientów",
    "darmowa dostawa",
    "koszt wysyłki",
]

COMMERCE_CONTEXT_RE = re.compile(
    r"\b(koszyk|produkty?|wysyłka|dostawa|promocj[aei]|rabat|zamów|sprzedawca)\b",
    re.IGNORECASE,
)

FORUM_HARD_PATTERNS = [
    "postautor",
    "napisał/a",
    "temat postu",
    "temat: re:",
]

FORUM_CONTEXT_RE = re.compile(
    r"\b(odpowiedz|cytuj|użytkownik|zarejestrowany|dołączył)\b[: ]",
    re.IGNORECASE,
)

NAV_PATTERNS = [
    "strona główna",
    "spis treści",
    "zobacz też",
    "linki zewnętrzne",
    "przypisy",
    "bibliografia",
    "polityka prywatności",
    "cookies",
    "regulamin",
]

WIKIMEDIA_TECH_NAMESPACES = (
    "dyskusja:",
    "plik:",
    "mediawiki:",
    "moduł:",
    "pomoc:",
    "portal:",
    "szablon:",
    "kategoria:",
    "wikibooks:",
    "wikisource:",
)

WIKISOURCE_EXTRA_NAMESPACES = ("indeks:", "strona:", "autor:")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def json_dump_line(handle, obj: dict[str, Any]) -> None:
    handle.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")


def load_sentencepiece(tokenizer: Path):
    try:
        import sentencepiece as spm
    except ImportError as exc:
        raise SystemExit("sentencepiece is required. Use ./.venv/bin/python.") from exc
    sp = spm.SentencePieceProcessor()
    sp.load(str(tokenizer))
    return sp


def write_uint16_tokens(handle, ids: list[int]) -> None:
    np.asarray(ids, dtype=np.uint16).tofile(handle)


def token_count(record: dict[str, Any]) -> int:
    return int((record.get("meta") or {}).get("token_count") or 0)


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def split_for(record: dict[str, Any], val_per_mille: int) -> str:
    return parent_split_for(record, val_per_mille)


def choose_source_stratified_val_ids(records: list[dict[str, Any]], val_per_mille: int) -> set[str]:
    """Choose validation docs by source.

    The stable-bucket split can leave a small source with zero validation docs.
    For v2.2 we keep document-level splitting, but explicitly choose a small
    deterministic validation slice per source.
    """
    by_source: dict[str, dict[str, list[dict[str, Any]]]] = collections.defaultdict(
        lambda: collections.defaultdict(list)
    )
    for record in records:
        by_source[record.get("source", "")][parent_doc_id_for(record)].append(record)
    val_ids: set[str] = set()
    for source, parent_groups in by_source.items():
        total_tokens = sum(token_count(record) for items in parent_groups.values() for record in items)
        target_tokens = max(1, int(total_tokens * val_per_mille / 1000))
        used = 0
        for parent_id, items in sorted(
            parent_groups.items(),
            key=lambda item: stable_bucket(f"{source}:{item[0]}", 1_000_000_000),
        ):
            for record in items:
                doc_key = record.get("doc_id") or record.get("id")
                if doc_key:
                    val_ids.add(str(doc_key))
            used += sum(token_count(record) for record in items)
            if used >= target_tokens:
                break
    return val_ids


def record_split(record: dict[str, Any], val_ids: set[str]) -> str:
    doc_key = str(record.get("doc_id") or record.get("id") or "")
    return "val" if doc_key in val_ids else "train"


def keep_sample(samples: list[dict[str, Any]], item: dict[str, Any], key: str, limit: int) -> None:
    if limit <= 0:
        return
    if len(samples) < limit:
        samples.append(item)
        return
    bucket = stable_bucket(key, 1_000_000)
    if bucket < limit * 20:
        samples[bucket % limit] = item


def sample_payload(record: dict[str, Any], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "id": record.get("id", ""),
        "source": record.get("source", ""),
        "source_id": record.get("source_id", ""),
        "doc_id": record.get("doc_id", ""),
        "title": record.get("title", ""),
        "url": record.get("url", ""),
        "quality_score": record.get("quality_score", 0),
        "text": truncate_text(record.get("text", ""), 1000),
    }
    if extra:
        payload.update(extra)
    return payload


def safe_id(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_.:-]+", "-", value.strip())
    return value.strip("-")[:96] or sha1_text(value)[:16]


def add_seen(metrics: dict[str, Any], exact_seen: set[str], normalized_seen: set[str], near_seen: set[str]) -> None:
    exact = metrics.get("exact_hash")
    normalized = metrics.get("normalized_hash")
    near = metrics.get("near_hash")
    if exact:
        exact_seen.add(str(exact))
    if normalized:
        normalized_seen.add(str(normalized))
    if near:
        near_seen.add(str(near))


def source_title_id(source: str, title: str, source_id: str) -> str:
    return sha1_text(f"{source}:{source_id}:{title}")[:24]


def line_shape(text: str) -> dict[str, float]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return {"line_count": 0, "short_line_ratio": 0.0, "list_line_ratio": 0.0, "avg_line_words": 0.0}
    word_counts = [word_count(line) for line in lines]
    short = sum(1 for count in word_counts if 0 < count <= 5)
    list_like = sum(1 for line in lines if re.match(r"^([*#;:]+|[-–—]\s+|\d+[.)]\s+)", line))
    return {
        "line_count": len(lines),
        "short_line_ratio": short / len(lines),
        "list_line_ratio": list_like / len(lines),
        "avg_line_words": sum(word_counts) / max(len(word_counts), 1),
    }


def common_bad_pattern_reasons(text: str) -> list[str]:
    lower = text.lower()
    reasons: list[str] = []
    commerce_hard_hits = [p for p in COMMERCE_HARD_PATTERNS if p in lower]
    commerce_context_hits = COMMERCE_CONTEXT_RE.findall(text)
    forum_hard_hits = [p for p in FORUM_HARD_PATTERNS if p in lower]
    forum_context_hits = FORUM_CONTEXT_RE.findall(text)
    price_hits = re.findall(r"\b\d+([,.]\d+)?\s?(zł|pln|eur|usd)\b", lower)
    if commerce_hard_hits or (len(commerce_context_hits) >= 4 and len(price_hits) >= 2):
        reasons.append("commerce_patterns")
    if forum_hard_hits or len(forum_context_hits) >= 3:
        reasons.append("forum_patterns")
    if len(price_hits) >= 6:
        reasons.append("price_or_currency_heavy")
    return reasons


def wikisource_reject_reasons(title: str, text: str) -> list[str]:
    lower_title = title.strip().lower()
    lower = text.lower()
    reasons: list[str] = []
    if lower_title.startswith(WIKIMEDIA_TECH_NAMESPACES + WIKISOURCE_EXTRA_NAMESPACES):
        reasons.append("wikisource_technical_namespace")
    if "ujednoznacznienie" in lower or "strona ujednoznaczniająca" in lower:
        reasons.append("wikisource_disambiguation")
    if "<pages index=" in lower or "__notoc__" in lower:
        reasons.append("wikisource_transclusion_or_index_markup")
    if re.search(r"(?im)^\s*(bibliografia|spis treści|indeks|skorowidz)\s*$", text):
        reasons.append("wikisource_index_or_bibliography")
    shape = line_shape(text)
    if shape["line_count"] >= 30 and (shape["short_line_ratio"] > 0.55 or shape["list_line_ratio"] > 0.35):
        reasons.append("wikisource_list_like")
    if text.count("[[") + text.count("]]") > 20:
        reasons.append("wikisource_link_markup_heavy")
    reasons.extend(common_bad_pattern_reasons(text))
    return reasons


def clean_wikisource_text(text: str) -> str:
    text = re.split(
        r"(?im)^\s*(przypisy|bibliografia|linki zewnętrzne|zobacz też|uwagi|źródła)\s*$",
        text,
        maxsplit=1,
    )[0]
    text = re.sub(r"<pages[^>]*>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"__\w+__", " ", text)
    return text.strip()


def strip_templates(text: str) -> str:
    for _ in range(8):
        new = re.sub(r"\{\{[^{}]*\}\}", " ", text, flags=re.DOTALL)
        if new == text:
            break
        text = new
    return text


def clean_wikitext(text: str) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    text = re.sub(r"<nowiki>(.*?)</nowiki>", r"\1", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<ref[^>/]*/>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<ref[^>]*>.*?</ref>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"\{\|.*?\|\}", " ", text, flags=re.DOTALL)
    text = strip_templates(text)
    text = re.sub(r"\[\[(?:Plik|File|Image|Grafika|Kategoria):[^\]]+\]\]", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\[\[[^|\]]+\|([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[https?://[^\s\]]+\s+([^\]]+)\]", r"\1", text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"'{2,}", "", text)
    text = re.sub(r"={2,}\s*([^=]+?)\s*={2,}", r"\n\1\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"__\w+__", " ", text)
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        line = re.sub(r"^([*#;:]+|[-–—]\s+|\d+[.)]\s+)", "", line).strip()
        if not line:
            lines.append("")
            continue
        if line.lower() in {"spis treści", "zobacz też", "linki zewnętrzne", "przypisy"}:
            continue
        lines.append(line)
    text = "\n".join(lines)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def wikibooks_reject_reasons(title: str, ns: str, raw_text: str, cleaned: str) -> list[str]:
    lower_title = title.strip().lower()
    lower = raw_text.lower()
    cleaned_lower = cleaned.lower()
    reasons: list[str] = []
    if lower_title.startswith(WIKIMEDIA_TECH_NAMESPACES):
        reasons.append("wikibooks_technical_namespace")
    if lower.startswith("#redirect") or lower.startswith("#patrz"):
        reasons.append("wikibooks_redirect")
    if lower_title.endswith("/spis treści") or lower_title.endswith("/okładka"):
        reasons.append("wikibooks_index_or_cover_page")
    if "interwiki" in lower_title or "spis treści" == lower_title:
        reasons.append("wikibooks_index_or_cover_page")
    shape = line_shape(cleaned)
    if shape["line_count"] >= 25 and (shape["short_line_ratio"] > 0.58 or shape["list_line_ratio"] > 0.42):
        reasons.append("wikibooks_list_like")
    markup_leftovers = sum(cleaned.count(token) for token in ["{{", "}}", "[[", "]]", "{|", "|}", "thumb|"])
    if markup_leftovers >= 4:
        reasons.append("wikibooks_markup_residue")
    if any(section in cleaned_lower for section in ["bibliografia", "linki zewnętrzne", "zobacz też"]) and word_count(cleaned) < 180:
        reasons.append("wikibooks_meta_page")
    reasons.extend(common_bad_pattern_reasons(cleaned))
    return reasons


def allegro_reject_reasons(text: str) -> list[str]:
    reasons = common_bad_pattern_reasons(text)
    shape = line_shape(text)
    if shape["line_count"] >= 30 and shape["short_line_ratio"] > 0.50:
        reasons.append("allegro_line_fragmented")
    if text.count("|") >= 10 or len(re.findall(r"\s[-–—]{2,}\s", text)) >= 5:
        reasons.append("allegro_table_or_separator_heavy")
    if shape["line_count"] >= 30 and shape["list_line_ratio"] > 0.42:
        reasons.append("allegro_list_heavy")
    if word_count(text) < 120:
        reasons.append("allegro_source_too_short")
    return reasons


def tokenize_into_record(sp, eos_id: int, record: dict[str, Any]) -> list[int]:
    ids = sp.encode(record["text"], out_type=int)
    ids.append(eos_id)
    record.setdefault("meta", {})["token_count"] = len(ids)
    return ids


def run_filter(
    record: dict[str, Any],
    *,
    config: FilterConfig,
    exact_seen: set[str],
    normalized_seen: set[str],
    near_seen: set[str],
    pre_reasons: list[str] | None = None,
) -> tuple[dict[str, Any] | None, list[str], dict[str, Any]]:
    pre_reasons = pre_reasons or []
    result = evaluate_document(
        record.get("text", ""),
        source=record.get("source", ""),
        config=config,
        exact_seen=exact_seen,
        normalized_seen=normalized_seen,
        near_seen=near_seen,
    )
    reasons = list(pre_reasons) + result.reasons
    metrics = result.metrics
    if reasons:
        return None, reasons, metrics
    record["text"] = result.text
    record["quality_score"] = round(float(metrics.get("quality_score", 0.0)), 4)
    record.setdefault("meta", {})["v2_2_filter"] = {
        key: metrics.get(key)
        for key in [
            "words",
            "chars",
            "alpha_ratio",
            "polish_stopword_ratio",
            "repetition_score",
            "unique_word_ratio",
            "quality_score",
            "suspicious_patterns",
        ]
    }
    add_seen(metrics, exact_seen, normalized_seen, near_seen)
    return record, [], metrics


def load_base_records(path: Path) -> Iterable[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("source") in ALLOWED_BASE_SOURCES:
                record = dict(record)
                record["id"] = f"glyph100-v2-2-{record.get('source')}-{record.get('doc_id') or safe_id(record.get('id', ''))}"
                record.setdefault("meta", {})["source_dataset"] = "glyph100_dataset_v2_1"
                yield record


def wikisource_records(limit: int = 0) -> Iterable[dict[str, Any]]:
    try:
        from datasets import load_dataset
    except ImportError:
        return
    try:
        dataset = load_dataset("wikimedia/wikisource", "20231201.pl", split="train", streaming=True)
    except Exception as exc:
        print(f"warning: could not load wikisource dataset: {exc}", file=sys.stderr)
        return
    for i, item in enumerate(dataset):
        if limit and i >= limit:
            break
        text = clean_wikisource_text(item.get("text") or "")
        title = item.get("title") or ""
        source_id = str(item.get("id") or i)
        yield {
            "id": f"glyph100-v2-2-wikisource-{source_id}",
            "source": "wikisource_pl",
            "source_id": source_id,
            "doc_id": source_title_id("wikisource_pl", title, source_id),
            "title": title,
            "url": item.get("url") or "",
            "license": SOURCE_LICENSES["wikisource_pl"],
            "language": "pl",
            "text": text,
            "quality_score": 0.0,
            "meta": {"source_meta": {"dataset": "wikimedia/wikisource", "config": "20231201.pl", "row": i}},
        }


def allegro_records(limit: int = 0) -> Iterable[dict[str, Any]]:
    try:
        from datasets import get_dataset_split_names, load_dataset
    except ImportError:
        return
    dataset_name = "allegro/summarization-polish-summaries-corpus"
    try:
        splits = get_dataset_split_names(dataset_name)
    except Exception:
        splits = ["train", "validation", "test"]
    emitted = 0
    for split in splits:
        try:
            dataset = load_dataset(dataset_name, split=split, streaming=True)
        except Exception as exc:
            print(f"warning: could not load allegro split {split}: {exc}", file=sys.stderr)
            continue
        for i, item in enumerate(dataset):
            text = item.get("source") or ""
            source_id = f"{split}:{i}"
            title = text.splitlines()[0].strip()[:180] if text.strip() else ""
            yield {
                "id": f"glyph100-v2-2-allegro-{split}-{i}",
                "source": "allegro_summaries_source",
                "source_id": source_id,
                "doc_id": source_title_id("allegro_summaries_source", title, source_id),
                "title": title,
                "url": "https://huggingface.co/datasets/allegro/summarization-polish-summaries-corpus",
                "license": SOURCE_LICENSES["allegro_summaries_source"],
                "language": "pl",
                "text": text,
                "quality_score": 0.0,
                "meta": {"source_meta": {"dataset": dataset_name, "split": split, "row": i, "field": "source"}},
            }
            emitted += 1
            if limit and emitted >= limit:
                return


def download_if_needed(url: str, target: Path, max_mb: float) -> dict[str, Any]:
    target.parent.mkdir(parents=True, exist_ok=True)
    info: dict[str, Any] = {"url": url, "path": str(target), "downloaded": False, "size_bytes": None}
    if target.exists() and target.stat().st_size > 0:
        info["size_bytes"] = target.stat().st_size
        return info
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "GlyphDatasetBuilder/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        size = int(response.headers.get("Content-Length") or 0)
    info["size_bytes"] = size
    if size > max_mb * 1024 * 1024:
        raise SystemExit(f"Refusing download over {max_mb:.1f} MB: {url} size={size}")
    tmp = target.with_suffix(target.suffix + ".tmp")
    req = urllib.request.Request(url, headers={"User-Agent": "GlyphDatasetBuilder/1.0"})
    with urllib.request.urlopen(req, timeout=120) as response, tmp.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    tmp.replace(target)
    info["downloaded"] = True
    info["size_bytes"] = target.stat().st_size
    return info


def xml_child_text(elem: ET.Element, name: str) -> str:
    for child in elem:
        if child.tag.rsplit("}", 1)[-1] == name:
            return child.text or ""
    return ""


def xml_revision_text(elem: ET.Element) -> str:
    for child in elem:
        if child.tag.rsplit("}", 1)[-1] != "revision":
            continue
        for rev_child in child:
            if rev_child.tag.rsplit("}", 1)[-1] == "text":
                return rev_child.text or ""
    return ""


def wikibooks_records(path: Path, limit_pages: int = 0) -> Iterable[dict[str, Any]]:
    seen_pages = 0
    with bz2.open(path, "rb") as handle:
        context = ET.iterparse(handle, events=("end",))
        for _, elem in context:
            if elem.tag.rsplit("}", 1)[-1] != "page":
                continue
            title = xml_child_text(elem, "title")
            ns = xml_child_text(elem, "ns") or "0"
            page_id = xml_child_text(elem, "id")
            raw_text = xml_revision_text(elem)
            cleaned = clean_wikitext(raw_text)
            seen_pages += 1
            yield {
                "id": f"glyph100-v2-2-wikibooks-{page_id or seen_pages}",
                "source": "wikibooks_pl",
                "source_id": str(page_id or seen_pages),
                "doc_id": source_title_id("wikibooks_pl", title, str(page_id or seen_pages)),
                "title": title,
                "url": f"https://pl.wikibooks.org/wiki/{title.replace(' ', '_')}" if title else "",
                "license": SOURCE_LICENSES["wikibooks_pl"],
                "language": "pl",
                "text": cleaned,
                "quality_score": 0.0,
                "meta": {
                    "source_meta": {
                        "dump": str(path),
                        "page_id": page_id,
                        "namespace": ns,
                        "raw_chars": len(raw_text),
                    }
                },
                "_raw_text": raw_text,
                "_namespace": ns,
            }
            elem.clear()
            if limit_pages and seen_pages >= limit_pages:
                return


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
    }
    outputs = [
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
        args.decision_md,
    ]
    for path in outputs:
        if path.resolve() in forbidden:
            raise SystemExit(f"Refusing to overwrite protected dataset output: {path}")
    existing = [path for path in outputs if path.exists()]
    if existing and not args.force_v2_2:
        formatted = "\n".join(f"- {path}" for path in existing)
        raise SystemExit(f"v2.2 outputs already exist. Use --force-v2-2 to replace v2.2 files only:\n{formatted}")
    for path in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)


def maybe_reject_record(record: dict[str, Any]) -> list[str]:
    source = record.get("source", "")
    if source == "wikisource_pl":
        return wikisource_reject_reasons(record.get("title", ""), record.get("text", ""))
    if source == "wikibooks_pl":
        return wikibooks_reject_reasons(
            record.get("title", ""),
            str(record.get("_namespace") or "0"),
            record.get("_raw_text", ""),
            record.get("text", ""),
        )
    if source == "allegro_summaries_source":
        return allegro_reject_reasons(record.get("text", ""))
    return common_bad_pattern_reasons(record.get("text", ""))


def config_for_source(source: str) -> FilterConfig:
    if source == "allegro_summaries_source":
        return FilterConfig(
            min_words=120,
            max_chars=80_000,
            min_alpha_ratio=0.58,
            min_polish_stopword_ratio=0.020,
            max_punct_symbol_ratio=0.13,
            max_repetition_score=0.032,
            min_unique_word_ratio=0.24,
            max_word_frequency_ratio=0.10,
            max_urls=1,
            max_line_length=18_000,
        )
    if source == "wikibooks_pl":
        return FilterConfig(
            min_words=60,
            max_chars=70_000,
            min_alpha_ratio=0.56,
            min_polish_stopword_ratio=0.016,
            max_punct_symbol_ratio=0.15,
            max_repetition_score=0.038,
            min_unique_word_ratio=0.24,
            max_word_frequency_ratio=0.12,
            max_urls=1,
            max_line_length=16_000,
        )
    if source == "wikisource_pl":
        return FilterConfig(
            min_words=60,
            max_chars=70_000,
            min_alpha_ratio=0.55,
            min_polish_stopword_ratio=0.014,
            max_punct_symbol_ratio=0.15,
            max_repetition_score=0.036,
            min_unique_word_ratio=0.22,
            max_word_frequency_ratio=0.13,
            max_urls=1,
            max_line_length=18_000,
        )
    return FilterConfig(min_words=40, max_chars=60_000)


def process_source(
    source_name: str,
    records: Iterable[dict[str, Any]],
    *,
    sp,
    eos_id: int,
    exact_seen: set[str],
    normalized_seen: set[str],
    near_seen: set[str],
    candidates: list[dict[str, Any]],
    rejected: list[dict[str, Any]],
    counters: dict[str, Any],
    accepted_samples: list[dict[str, Any]],
    rejected_samples: list[dict[str, Any]],
    sample_limit: int,
    progress_every: int = 25_000,
) -> None:
    start = time.time()
    config = config_for_source(source_name)
    for i, raw_record in enumerate(records, 1):
        counters["seen_by_source"][source_name] += 1
        record = dict(raw_record)
        pre_reasons = maybe_reject_record(record)
        maybe, reasons, metrics = run_filter(
            record,
            config=config,
            exact_seen=exact_seen,
            normalized_seen=normalized_seen,
            near_seen=near_seen,
            pre_reasons=pre_reasons,
        )
        if maybe is None:
            for reason in reasons:
                counters["rejection_reasons"][reason] += 1
            reject_record = {
                "id": record.get("id", ""),
                "source": source_name,
                "source_id": record.get("source_id", ""),
                "doc_id": record.get("doc_id", ""),
                "title": record.get("title", ""),
                "reject_reason": reasons[0] if reasons else "rejected",
                "reject_reasons": reasons,
                "metrics": {
                    key: metrics.get(key)
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
                "text": truncate_text(record.get("text", ""), 900),
            }
            rejected.append(reject_record)
            keep_sample(rejected_samples, reject_record, f"{record.get('id', '')}:reject", sample_limit)
            continue

        ids = tokenize_into_record(sp, eos_id, maybe)
        maybe.setdefault("meta", {})["word_count"] = word_count(maybe["text"])
        maybe["meta"]["source_build"] = "glyph100_dataset_v2_2"
        candidates.append(maybe)
        counters["accepted_by_source"][source_name] += 1
        counters["tokens_by_source_raw"][source_name] += len(ids)
        keep_sample(
            accepted_samples,
            sample_payload(maybe, {"token_count": len(ids), "words": maybe["meta"]["word_count"]}),
            maybe.get("id", ""),
            sample_limit,
        )
        if progress_every and i % progress_every == 0:
            print(
                f"{source_name}: seen={i:,} accepted={counters['accepted_by_source'][source_name]:,} "
                f"rejected={sum(1 for r in rejected if r.get('source') == source_name):,} "
                f"elapsed={time.time() - start:.1f}s",
                flush=True,
            )


def select_final_records(
    candidates: list[dict[str, Any]],
    *,
    max_wikipedia_share: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    wiki = [r for r in candidates if r.get("source") == "wikipedia_pl"]
    non_wiki = [r for r in candidates if r.get("source") != "wikipedia_pl"]
    wiki_tokens = sum(token_count(r) for r in wiki)
    non_wiki_tokens = sum(token_count(r) for r in non_wiki)
    max_wiki_tokens = int(non_wiki_tokens * max_wikipedia_share / max(1e-9, 1.0 - max_wikipedia_share))
    selected_wiki = wiki
    capped = False
    if wiki_tokens > max_wiki_tokens:
        capped = True
        selected_wiki = []
        used = 0
        for record in sorted(wiki, key=lambda r: stable_bucket(r.get("doc_id") or r.get("id", ""), 1_000_000_000)):
            count = token_count(record)
            if selected_wiki and used + count > max_wiki_tokens:
                continue
            selected_wiki.append(record)
            used += count
            if used >= max_wiki_tokens:
                break
    final_records = sorted(non_wiki + selected_wiki, key=lambda r: (r.get("source", ""), stable_bucket(r.get("doc_id") or r.get("id", ""), 1_000_000_000)))
    selection = {
        "wikipedia_tokens_before_cap": wiki_tokens,
        "non_wikipedia_tokens": non_wiki_tokens,
        "max_wikipedia_share": max_wikipedia_share,
        "max_wikipedia_tokens_allowed": max_wiki_tokens,
        "wikipedia_capped": capped,
        "wikipedia_docs_before_cap": len(wiki),
        "wikipedia_docs_after_cap": len(selected_wiki),
        "wikipedia_tokens_after_cap": sum(token_count(r) for r in selected_wiki),
    }
    return final_records, selection


def source_stats(records: list[dict[str, Any]], val_ids: set[str]) -> dict[str, dict[str, int]]:
    stats: dict[str, dict[str, int]] = collections.defaultdict(
        lambda: {"docs": 0, "tokens": 0, "train_tokens": 0, "val_tokens": 0, "train_docs": 0, "val_docs": 0}
    )
    for record in records:
        source = record["source"]
        count = token_count(record)
        split = record_split(record, val_ids)
        stats[source]["docs"] += 1
        stats[source]["tokens"] += count
        if split == "val":
            stats[source]["val_docs"] += 1
            stats[source]["val_tokens"] += count
        else:
            stats[source]["train_docs"] += 1
            stats[source]["train_tokens"] += count
    return dict(stats)


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


def render_report(stats: dict[str, Any]) -> str:
    source_rows = []
    total = max(stats["total_tokens"], 1)
    for source, item in stats["source_mix"].items():
        share = item["tokens"] / total * 100
        source_rows.append(
            f"| `{source}` | {item['docs']:,} | {item['tokens']:,} | {share:.2f}% | "
            f"{item['train_tokens']:,} | {item['val_tokens']:,} |"
        )
    source_audit_rows = []
    for item in stats["source_audit"]:
        source_audit_rows.append(
            f"| {item['name']} | {item['decision']} | {item['size']} | {item['sample_quality']} | {item['risk']} |"
        )
    return f"""# Glyph-100M Dataset v2.2 Report

Generated: {stats["generated_at"]}

No training was started.

## Verdict

{stats["recommendation"]}

## Source Preflight

| source | decision | size / access | sample quality | risk |
|---|---|---|---|---|
{chr(10).join(source_audit_rows)}

## Outputs

- train bin: `{stats["train_bin"]}`
- val bin: `{stats["val_bin"]}`
- docs JSONL: `{stats["docs_jsonl"]}`
- metadata: `{stats["metadata_path"]}`
- tokenizer: `{stats["tokenizer_path"]}`

## Counts

- train docs: {stats["train_docs"]:,}
- val docs: {stats["val_docs"]:,}
- train tokens: {stats["train_tokens"]:,}
- val tokens: {stats["val_tokens"]:,}
- total tokens: {stats["total_tokens"]:,}
- token/word ratio: {stats["token_word_ratio"]:.3f}
- Wikipedia share: {stats["wikipedia_share"]:.2%}
- non-Wiki share: {stats["non_wikipedia_share"]:.2%}

## Source Mix

| source | docs | tokens | share | train tokens | val tokens |
|---|---:|---:|---:|---:|---:|
{chr(10).join(source_rows)}

## Wikipedia Cap

```json
{json.dumps(stats["selection"], ensure_ascii=False, indent=2)}
```

## Rejection Reasons

```json
{json.dumps(stats["rejection_reasons"], ensure_ascii=False, indent=2)}
```

## Training Math

- stage 3 / 50k total: {TRAINING_TOKENS_50K:,} tokens = {stats["stage3_50k_epochs"]:.2f} epochs
- 100k total: {TRAINING_TOKENS_100K:,} tokens = {stats["stage4_100k_epochs"]:.2f} epochs
- 200k total: {TRAINING_TOKENS_200K:,} tokens = {stats["stage5_200k_epochs"]:.2f} epochs

## Quality Notes

- wiki-style residue: {stats["quality_notes"]["wiki_style_residue"]}
- Allegro `source` quality: {stats["quality_notes"]["allegro_quality"]}
- Wikibooks usefulness: {stats["quality_notes"]["wikibooks_quality"]}
- Wikisource usefulness: {stats["quality_notes"]["wikisource_quality"]}

## Final Random Samples

{render_samples(stats["final_samples"], 50)}
"""


def render_decision(stats: dict[str, Any]) -> str:
    return f"""# Glyph-100M Dataset v2.2 Decision Report

Generated: {stats["generated_at"]}

No training was started.

## Recommendation

{stats["recommendation"]}

## What Changed From v2.1

- legacy remains 0.
- Wikipedia is capped to {stats["wikipedia_share"]:.1%} of tokens.
- non-Wikipedia sources are {stats["non_wikipedia_share"]:.1%}: Allegro PSC `source`, Wikibooks, Wolne Lektury and stricter Wikisource.
- v2.2 total tokens: {stats["total_tokens"]:,}.
- stage 3 / 50k would be {stats["stage3_50k_epochs"]:.2f} epochs over v2.2.

## Source Mix

```json
{json.dumps(stats["source_mix"], ensure_ascii=False, indent=2)}
```

## Decision Options

- A) v2.2 gotowy, można odpalić stage 3 / 50k.
- B) v2.2 lepszy, ale jeszcze wymaga poprawek.
- C) potrzebny FinetextPL-Edu / inne źródła.
- D) lepiej zrobić krótki preflight, nie 50k.
- E) zatrzymać się, bo dane są za słabe.

## Current Verdict

{stats["decision_code"]}

No stage 3 command was executed.
"""


def source_audit_template(wikibooks_info: dict[str, Any]) -> list[dict[str, Any]]:
    wikibooks_size = wikibooks_info.get("size_bytes")
    wikibooks_size_text = f"{wikibooks_size / 1024 / 1024:.1f} MB" if wikibooks_size else "unknown"
    return [
        {
            "name": "Wikipedia PL",
            "url": "local glyph100_dataset_v2_1_docs.jsonl",
            "size": "127.9M tokens already built",
            "type": "encyclopedic article text",
            "license": SOURCE_LICENSES["wikipedia_pl"],
            "available_without_login": True,
            "sample_quality": "clean, but strongly Wikipedia-shaped",
            "risk": "dominates style if uncapped",
            "decision": "use with cap <= 70%",
        },
        {
            "name": "Wolne Lektury",
            "url": "local glyph100_dataset_v2_1_docs.jsonl / https://wolnelektury.pl/api/",
            "size": "3.1M tokens already built",
            "type": "literary/public-domain books",
            "license": SOURCE_LICENSES["wolne_lektury"],
            "available_without_login": True,
            "sample_quality": "good continuous literary Polish",
            "risk": "small source, older literary style",
            "decision": "use",
        },
        {
            "name": "Wikisource PL",
            "url": "https://huggingface.co/datasets/wikimedia/wikisource",
            "size": "small streaming source",
            "type": "public source texts",
            "license": SOURCE_LICENSES["wikisource_pl"],
            "available_without_login": True,
            "sample_quality": "mixed; useful after removing index/meta/list pages",
            "risk": "metadata, indexes, bibliographies, legal/source artifacts",
            "decision": "use with stricter cleanup",
        },
        {
            "name": "Wikibooks PL",
            "url": DEFAULT_WIKIBOOKS_URL,
            "size": wikibooks_size_text,
            "type": "educational/tutorial wiki books",
            "license": SOURCE_LICENSES["wikibooks_pl"],
            "available_without_login": True,
            "sample_quality": "educational prose mixed with wikitext/navigation",
            "risk": "markup/list-heavy pages, indexes, technical pages",
            "decision": "use with cleanup",
        },
        {
            "name": "Allegro Polish Summaries Corpus",
            "url": "https://huggingface.co/datasets/allegro/summarization-polish-summaries-corpus",
            "size": "~271 MB data files by HF metadata",
            "type": "Polish article/source text paired with summaries",
            "license": SOURCE_LICENSES["allegro_summaries_source"],
            "available_without_login": True,
            "sample_quality": "good long article text in `source`; summaries are not used",
            "risk": "news/business/legal style; original source licensing should be verified",
            "decision": "use only `source` field",
        },
        {
            "name": "legacy_mixed_corpus",
            "url": "local old mixed corpus",
            "size": "not used",
            "type": "mixed web corpus",
            "license": "mixed/unknown",
            "available_without_login": True,
            "sample_quality": "too much forum/commerce/SEO residue",
            "risk": "reintroduces exact problems observed in Glyph-27M",
            "decision": "reject for v2.2",
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Glyph-100M dataset v2.2")
    parser.add_argument("--base-docs", type=Path, default=DEFAULT_BASE_DOCS)
    parser.add_argument("--tokenizer", type=Path, default=DEFAULT_TOKENIZER)
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
    parser.add_argument("--decision-md", type=Path, default=DEFAULT_DECISION_MD)
    parser.add_argument("--wikibooks-url", default=DEFAULT_WIKIBOOKS_URL)
    parser.add_argument("--wikibooks-cache", type=Path, default=DEFAULT_WIKIBOOKS_CACHE)
    parser.add_argument("--wikibooks-max-download-mb", type=float, default=80.0)
    parser.add_argument("--wikisource-limit", type=int, default=0)
    parser.add_argument("--wikibooks-limit-pages", type=int, default=0)
    parser.add_argument("--allegro-limit", type=int, default=0)
    parser.add_argument("--max-wikipedia-share", type=float, default=0.70)
    parser.add_argument("--val-per-mille", type=int, default=5)
    parser.add_argument("--sample-limit", type=int, default=50)
    parser.add_argument("--force-v2-2", action="store_true")
    args = parser.parse_args()

    ensure_safe_outputs(args)
    sp = load_sentencepiece(args.tokenizer)
    eos_id = sp.eos_id()
    start = time.time()

    exact_seen: set[str] = set()
    normalized_seen: set[str] = set()
    near_seen: set[str] = set()
    candidates: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    accepted_samples: list[dict[str, Any]] = []
    rejected_samples: list[dict[str, Any]] = []
    counters: dict[str, Any] = {
        "seen_by_source": collections.Counter(),
        "accepted_by_source": collections.Counter(),
        "tokens_by_source_raw": collections.Counter(),
        "rejection_reasons": collections.Counter(),
    }

    wikibooks_info = download_if_needed(args.wikibooks_url, args.wikibooks_cache, args.wikibooks_max_download_mb)
    source_audit = source_audit_template(wikibooks_info)

    sources = [
        ("base_v2_1", load_base_records(args.base_docs)),
        ("wikisource_pl", wikisource_records(args.wikisource_limit)),
        ("wikibooks_pl", wikibooks_records(args.wikibooks_cache, args.wikibooks_limit_pages)),
        ("allegro_summaries_source", allegro_records(args.allegro_limit)),
    ]
    for label, iterator in sources:
        if label == "base_v2_1":
            # These records keep their original source names: wikipedia_pl / wolne_lektury.
            process_source(
                "wikipedia_pl",
                (r for r in iterator if r.get("source") == "wikipedia_pl"),
                sp=sp,
                eos_id=eos_id,
                exact_seen=exact_seen,
                normalized_seen=normalized_seen,
                near_seen=near_seen,
                candidates=candidates,
                rejected=rejected,
                counters=counters,
                accepted_samples=accepted_samples,
                rejected_samples=rejected_samples,
                sample_limit=args.sample_limit,
            )
            # Reload because the first generator has been exhausted by filtering above.
            process_source(
                "wolne_lektury",
                (r for r in load_base_records(args.base_docs) if r.get("source") == "wolne_lektury"),
                sp=sp,
                eos_id=eos_id,
                exact_seen=exact_seen,
                normalized_seen=normalized_seen,
                near_seen=near_seen,
                candidates=candidates,
                rejected=rejected,
                counters=counters,
                accepted_samples=accepted_samples,
                rejected_samples=rejected_samples,
                sample_limit=args.sample_limit,
            )
            continue
        process_source(
            label,
            iterator,
            sp=sp,
            eos_id=eos_id,
            exact_seen=exact_seen,
            normalized_seen=normalized_seen,
            near_seen=near_seen,
            candidates=candidates,
            rejected=rejected,
            counters=counters,
            accepted_samples=accepted_samples,
            rejected_samples=rejected_samples,
            sample_limit=args.sample_limit,
        )

    final_records, selection = select_final_records(candidates, max_wikipedia_share=args.max_wikipedia_share)
    val_doc_ids = choose_source_stratified_val_ids(final_records, args.val_per_mille)
    source_mix = source_stats(final_records, val_doc_ids)

    train_tokens = val_tokens = train_docs = val_docs = total_words = 0
    token_lengths: list[int] = []
    final_samples: list[dict[str, Any]] = []
    with args.train_bin.open("wb") as train_out, args.val_bin.open("wb") as val_out, args.docs_jsonl.open(
        "w", encoding="utf-8"
    ) as docs_out:
        for record in final_records:
            ids = sp.encode(record["text"], out_type=int)
            ids.append(eos_id)
            record.setdefault("meta", {})["token_count"] = len(ids)
            record["parent_doc_id"] = parent_doc_id_for(record)
            record["meta"]["split"] = record_split(record, val_doc_ids)
            record["meta"]["dataset_name"] = "glyph100_dataset_v2_2"
            record.pop("_raw_text", None)
            record.pop("_namespace", None)
            json_dump_line(docs_out, record)
            if record["meta"]["split"] == "val":
                val_docs += 1
                val_tokens += len(ids)
                write_uint16_tokens(val_out, ids)
            else:
                train_docs += 1
                train_tokens += len(ids)
                write_uint16_tokens(train_out, ids)
            total_words += word_count(record["text"])
            token_lengths.append(len(ids))
            keep_sample(
                final_samples,
                sample_payload(record, {"token_count": len(ids), "split": record["meta"]["split"]}),
                record.get("id", ""),
                args.sample_limit,
            )

    with args.rejected_jsonl.open("w", encoding="utf-8") as handle:
        for item in rejected:
            json_dump_line(handle, item)
    for path, rows in [
        (args.accepted_samples, accepted_samples),
        (args.rejected_samples, rejected_samples),
        (args.final_samples, final_samples),
    ]:
        with path.open("w", encoding="utf-8") as handle:
            for row in rows[: args.sample_limit]:
                json_dump_line(handle, row)

    total_tokens = train_tokens + val_tokens
    wiki_tokens = source_mix.get("wikipedia_pl", {}).get("tokens", 0)
    non_wiki_tokens = total_tokens - wiki_tokens
    wiki_share = wiki_tokens / max(total_tokens, 1)
    non_wiki_share = non_wiki_tokens / max(total_tokens, 1)
    if total_tokens >= 175_000_000 and wiki_share <= 0.72:
        decision_code = "A) v2.2 gotowy, można odpalić stage 3 / 50k po osobnej zgodzie."
        recommendation = (
            "A: v2.2 is a substantially better stage-3 candidate than v2.1. It is still not a huge corpus, "
            "but the source mix is much less Wikipedia-heavy and legacy remains excluded."
        )
    elif wiki_share <= 0.75 and non_wiki_tokens >= 35_000_000:
        decision_code = "B) v2.2 lepszy, ale jeszcze wymaga poprawek albo krótkiego preflightu."
        recommendation = (
            "B: v2.2 improves the mix, but token count or source balance is still marginal. "
            "Prefer a short preflight or add another clean source before full 50k."
        )
    else:
        decision_code = "C) potrzebny FinetextPL-Edu / inne źródła."
        recommendation = (
            "C: v2.2 is not balanced enough for a 50k run. FinetextPL-Edu or another clean source is needed."
        )

    stats = {
        "generated_at": now_utc(),
        "dataset_name": "glyph100_dataset_v2_2",
        "selected_variant": "A_wikipedia_max_70_nonwiki_mix_legacy_0",
        "variant": "glyph-100m",
        "scope": "source-aware cleaner dataset candidate; no training has been run on it",
        "tokenizer_path": str(args.tokenizer),
        "tokenizer_vocab_size": sp.vocab_size(),
        "train_bin": str(args.train_bin),
        "val_bin": str(args.val_bin),
        "metadata_path": str(args.metadata),
        "docs_jsonl": str(args.docs_jsonl),
        "rejected_jsonl": str(args.rejected_jsonl),
        "train_docs": train_docs,
        "val_docs": val_docs,
        "train_tokens": train_tokens,
        "val_tokens": val_tokens,
        "total_tokens": total_tokens,
        "token_word_ratio": total_tokens / max(total_words, 1),
        "word_token_ratio": total_words / max(total_tokens, 1),
        "wikipedia_tokens": wiki_tokens,
        "non_wikipedia_tokens": non_wiki_tokens,
        "wikipedia_share": wiki_share,
        "non_wikipedia_share": non_wiki_share,
        "source_mix": source_mix,
        "seen_by_source": dict(counters["seen_by_source"].most_common()),
        "accepted_by_source_before_cap": dict(counters["accepted_by_source"].most_common()),
        "tokens_by_source_before_cap": dict(counters["tokens_by_source_raw"].most_common()),
        "rejection_reasons": dict(counters["rejection_reasons"].most_common(80)),
        "selection": selection,
        "doc_token_percentiles": {
            "p50": percentile(token_lengths, 0.50),
            "p75": percentile(token_lengths, 0.75),
            "p90": percentile(token_lengths, 0.90),
            "p95": percentile(token_lengths, 0.95),
            "p99": percentile(token_lengths, 0.99),
        },
        "source_audit": source_audit,
        "quality_notes": {
            "wiki_style_residue": (
                "reduced versus v2.1 by capping Wikipedia, but still present because Wikipedia remains the largest source"
            ),
            "allegro_quality": (
                "uses only `source`; accepted samples are mostly continuous article/news/legal/business text, not summaries"
            ),
            "wikibooks_quality": "useful educational/tutorial text after wikitext cleanup; some markup/list residue is rejected",
            "wikisource_quality": "useful but stricter cleanup removes index, bibliography and technical/list pages",
        },
        "final_samples": final_samples,
        "stage3_50k_tokens": TRAINING_TOKENS_50K,
        "stage3_50k_epochs": TRAINING_TOKENS_50K / max(total_tokens, 1),
        "stage4_100k_epochs": TRAINING_TOKENS_100K / max(total_tokens, 1),
        "stage5_200k_epochs": TRAINING_TOKENS_200K / max(total_tokens, 1),
        "recommendation": recommendation,
        "decision_code": decision_code,
        "elapsed_seconds": time.time() - start,
    }
    args.stats.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    args.report.write_text(render_report(stats), encoding="utf-8")
    args.metadata.write_text(
        json.dumps(
            {
                "variant": "glyph-100m",
                "dataset_name": "glyph100_dataset_v2_2",
                "selected_variant": stats["selected_variant"],
                "scope": stats["scope"],
                "train_bin": str(args.train_bin),
                "val_bin": str(args.val_bin),
                "docs_jsonl": str(args.docs_jsonl),
                "tokenizer": str(args.tokenizer),
                "vocab_size": sp.vocab_size(),
                "train_docs": train_docs,
                "val_docs": val_docs,
                "train_tokens": train_tokens,
                "val_tokens": val_tokens,
                "total_tokens": total_tokens,
                "source_mix": source_mix,
                "wikipedia_share": wiki_share,
                "stage3_50k_epochs": stats["stage3_50k_epochs"],
                "created_at": stats["generated_at"],
                "stats_json": str(args.stats),
                "report": str(args.report),
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
                "dataset_name": "glyph100_dataset_v2_2",
                "total_tokens": total_tokens,
                "wikipedia_share": wiki_share,
                "stage3_50k_epochs": stats["stage3_50k_epochs"],
                "decision": decision_code,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    main()
