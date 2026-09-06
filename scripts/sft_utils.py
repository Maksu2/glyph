#!/usr/bin/env python3
"""Shared helpers for Glyph SFT v0 dataset tooling."""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Iterable


REQUIRED_FIELDS = ("id", "category", "instruction", "response", "source", "quality")
USER_TOKEN = "<|user|>"
ASSISTANT_TOKEN = "<|assistant|>"
END_TOKEN = "<|end|>"


@dataclass
class JsonlLoadResult:
    path: Path
    records: list[dict]
    invalid_json: list[dict]
    missing_fields: list[dict]


def load_jsonl(path: str | Path) -> JsonlLoadResult:
    path = Path(path)
    records: list[dict] = []
    invalid_json: list[dict] = []
    missing_fields: list[dict] = []

    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            raw = line.strip()
            if not raw:
                continue
            try:
                item = json.loads(raw)
            except json.JSONDecodeError as exc:
                invalid_json.append({"line": line_no, "error": str(exc)})
                continue
            missing = [field for field in REQUIRED_FIELDS if field not in item]
            if missing:
                missing_fields.append({"line": line_no, "missing": missing})
            item["_line"] = line_no
            records.append(item)

    return JsonlLoadResult(path=path, records=records, invalid_json=invalid_json, missing_fields=missing_fields)


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def normalize_for_dupes(text: str) -> str:
    text = normalize_space(text).lower()
    text = re.sub(r"[^\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+", " ", text, flags=re.UNICODE)
    return normalize_space(text)


def format_sft_text(record: dict) -> str:
    instruction = normalize_space(record.get("instruction", ""))
    response = normalize_space(record.get("response", record.get("output", "")))
    return f"{USER_TOKEN}\n{instruction}\n{ASSISTANT_TOKEN}\n{response}\n{END_TOKEN}\n"


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ-]+\b", str(text or ""), flags=re.UNICODE))


def percentile(values: list[int | float], pct: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    if len(values) == 1:
        return float(values[0])
    k = (len(values) - 1) * pct
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return float(values[lo])
    return float(values[lo] * (hi - k) + values[hi] * (k - lo))


def load_sentencepiece(tokenizer_path: str | Path):
    import sentencepiece as spm

    sp = spm.SentencePieceProcessor()
    sp.load(str(tokenizer_path))
    return sp


def token_ids(sp, text: str) -> list[int]:
    return list(sp.encode(text, out_type=int))


def has_bad_control_chars(text: str) -> bool:
    return any((ord(ch) < 32 and ch not in "\n\r\t") or ord(ch) == 127 for ch in str(text or ""))


def english_pattern(text: str) -> bool:
    return bool(
        re.search(
            r"\b(as an ai|language model|the user|you should|answer the|explain briefly|step by step)\b",
            str(text or ""),
            flags=re.IGNORECASE,
        )
    )


def collect_dataset_stats(records: list[dict], sp=None, context_len: int = 256) -> dict:
    categories = Counter(str(r.get("category", "")).strip() for r in records)
    qualities = Counter(str(r.get("quality", "")).strip() for r in records)
    sources = Counter(str(r.get("source", "")).strip() for r in records)

    instr_chars = [len(normalize_space(r.get("instruction", ""))) for r in records]
    resp_chars = [len(normalize_space(r.get("response", r.get("output", "")))) for r in records]
    instr_words = [word_count(r.get("instruction", "")) for r in records]
    resp_words = [word_count(r.get("response", r.get("output", ""))) for r in records]

    normalized_instructions = [normalize_for_dupes(r.get("instruction", "")) for r in records]
    normalized_pairs = [
        normalize_for_dupes(r.get("instruction", "")) + "\n" + normalize_for_dupes(r.get("response", r.get("output", "")))
        for r in records
    ]
    instruction_dupes = sum(count - 1 for count in Counter(normalized_instructions).values() if count > 1)
    pair_dupes = sum(count - 1 for count in Counter(normalized_pairs).values() if count > 1)

    bad = {
        "empty_instruction": sum(1 for r in records if not normalize_space(r.get("instruction", ""))),
        "empty_response": sum(1 for r in records if not normalize_space(r.get("response", r.get("output", "")))),
        "very_short_response_lt_8_words": sum(1 for words in resp_words if words < 8),
        "very_long_response_gt_120_words": sum(1 for words in resp_words if words > 120),
        "control_chars": sum(
            1
            for r in records
            if has_bad_control_chars(r.get("instruction", ""))
            or has_bad_control_chars(r.get("response", r.get("output", "")))
        ),
        "as_language_model_phrase": sum(
            1
            for r in records
            if re.search(r"jako model językowy|jako sztuczna inteligencja", r.get("response", ""), re.IGNORECASE)
        ),
        "english_pattern": sum(
            1 for r in records if english_pattern(r.get("instruction", "")) or english_pattern(r.get("response", ""))
        ),
    }

    token_stats = None
    if sp is not None:
        template_lengths = [len(token_ids(sp, format_sft_text(r))) for r in records]
        instruction_tokens = [len(token_ids(sp, normalize_space(r.get("instruction", "")))) for r in records]
        response_tokens = [len(token_ids(sp, normalize_space(r.get("response", r.get("output", ""))))) for r in records]
        token_stats = {
            "template_total_tokens": int(sum(template_lengths)),
            "template_min": min(template_lengths) if template_lengths else 0,
            "template_max": max(template_lengths) if template_lengths else 0,
            "template_avg": mean(template_lengths) if template_lengths else 0,
            "template_p50": percentile(template_lengths, 0.50),
            "template_p90": percentile(template_lengths, 0.90),
            "template_p95": percentile(template_lengths, 0.95),
            "template_p99": percentile(template_lengths, 0.99),
            "instruction_avg_tokens": mean(instruction_tokens) if instruction_tokens else 0,
            "response_avg_tokens": mean(response_tokens) if response_tokens else 0,
            "fits_context": sum(1 for n in template_lengths if n <= context_len),
            "over_context": sum(1 for n in template_lengths if n > context_len),
            "over_context_lines": [
                int(r.get("_line", i + 1))
                for i, (r, n) in enumerate(zip(records, template_lengths, strict=False))
                if n > context_len
            ][:50],
        }

    return {
        "examples": len(records),
        "categories": dict(categories),
        "qualities": dict(qualities),
        "sources": dict(sources),
        "instruction_chars_avg": mean(instr_chars) if instr_chars else 0,
        "response_chars_avg": mean(resp_chars) if resp_chars else 0,
        "instruction_words_avg": mean(instr_words) if instr_words else 0,
        "response_words_avg": mean(resp_words) if resp_words else 0,
        "instruction_words_total": int(sum(instr_words)),
        "response_words_total": int(sum(resp_words)),
        "total_words": int(sum(instr_words) + sum(resp_words)),
        "instruction_duplicate_extra": instruction_dupes,
        "instruction_response_duplicate_extra": pair_dupes,
        "bad_patterns": bad,
        "token_stats": token_stats,
    }


def similar_instruction_pairs(records: list[dict], limit: int = 30) -> list[dict]:
    """Cheap near-duplicate detector based on word-set Jaccard."""
    buckets: dict[str, list[tuple[int, str, set[str]]]] = defaultdict(list)
    for idx, record in enumerate(records):
        norm = normalize_for_dupes(record.get("instruction", ""))
        words = {w for w in norm.split() if len(w) > 2}
        if not words:
            continue
        key = " ".join(sorted(words)[:2])
        buckets[key].append((idx, norm, words))

    pairs: list[dict] = []
    for bucket in buckets.values():
        if len(bucket) < 2:
            continue
        for i in range(len(bucket)):
            idx_a, norm_a, words_a = bucket[i]
            for j in range(i + 1, len(bucket)):
                idx_b, norm_b, words_b = bucket[j]
                union = words_a | words_b
                if not union:
                    continue
                score = len(words_a & words_b) / len(union)
                if score >= 0.88 and norm_a != norm_b:
                    pairs.append(
                        {
                            "score": round(score, 3),
                            "line_a": int(records[idx_a].get("_line", idx_a + 1)),
                            "line_b": int(records[idx_b].get("_line", idx_b + 1)),
                            "instruction_a": records[idx_a].get("instruction", ""),
                            "instruction_b": records[idx_b].get("instruction", ""),
                        }
                    )
                    if len(pairs) >= limit:
                        return pairs
    return pairs


def write_json(path: str | Path, data: dict | list) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: str | Path, records: Iterable[dict]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8") as f:
        for record in records:
            clean = {k: v for k, v in record.items() if not k.startswith("_")}
            f.write(json.dumps(clean, ensure_ascii=False, sort_keys=True) + "\n")
