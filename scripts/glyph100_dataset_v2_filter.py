#!/usr/bin/env python3
"""Shared filtering helpers for the Glyph-100M source-aware dataset v2.

The functions here are intentionally lightweight. They are not a full
CommonCrawl cleaner, but they keep enough metadata and rejection reasons to make
the next training decision auditable.
"""

from __future__ import annotations

import collections
import hashlib
import html
import math
import re
from dataclasses import dataclass, field
from typing import Any


HTML_RE = re.compile(r"<[^>]+>")
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
MULTISPACE_RE = re.compile(r"[ \t\r\f\v]+")
REPEATED_PUNCT_RE = re.compile(r"([.?!,;:])\1{3,}")
WORD_RE = re.compile(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]+", re.UNICODE)
WIKI_SECTION_RE = re.compile(
    r"(?im)^\s*(==+\s*)?(przypisy|bibliografia|linki zewnętrzne|zobacz też|uwagi|źródła)(\s*==+)?\s*$"
)

POLISH_CHARS = set("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")
POLISH_STOPWORDS = {
    "i",
    "oraz",
    "że",
    "jest",
    "są",
    "nie",
    "to",
    "w",
    "we",
    "na",
    "z",
    "ze",
    "do",
    "dla",
    "po",
    "od",
    "przez",
    "który",
    "która",
    "które",
    "jako",
    "się",
    "ma",
    "był",
    "była",
    "było",
    "może",
    "ale",
    "także",
    "ten",
    "ta",
    "te",
    "tym",
    "jego",
    "jej",
    "ich",
    "więc",
    "czy",
    "których",
    "którym",
    "oraz",
    "gdy",
    "pod",
    "nad",
}

BOILERPLATE_PATTERNS = [
    "strona główna",
    "czytaj więcej",
    "zobacz także",
    "linki zewnętrzne",
    "przypisy",
    "bibliografia",
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
    "sklep internetowy",
    "zamów teraz",
    "newsletter",
    "facebook",
    "instagram",
    "twitter",
]

LEGACY_HARD_REJECT_PATTERNS = [
    "strona główna",
    "jesteś tutaj",
    "czytaj więcej",
    "dodaj komentarz",
    "napisz komentarz",
    "zaloguj się",
    "rejestracja",
    "koszyk",
    "sklep internetowy",
    "zamów teraz",
    "newsletter",
    "cookies",
    "polityka prywatności",
    "wszelkie prawa zastrzeżone",
    "postautor:",
    "autor:",
    "słowa kluczowe:",
    "home/",
    "pozycjonowanie stron",
    "pożyczki pozabankowe",
    "pożyczki",
    "chwilówki",
    "horoskop",
    "ransomware",
    "userfiles/",
    "home /",
    "posted by",
    "no comment",
    "allegro",
    "sprzedano za",
    "oficjalne archiwum",
    "gazetki",
    "promocyjne",
    "mieszkania na sprzedaż",
    "redakcja portalu",
    "komentarz",
    "sklep",
    "seo",
]


@dataclass
class FilterConfig:
    min_words: int = 40
    max_chars: int = 60_000
    min_alpha_ratio: float = 0.55
    min_polish_stopword_ratio: float = 0.015
    max_punct_symbol_ratio: float = 0.16
    max_repetition_score: float = 0.045
    min_unique_word_ratio: float = 0.26
    max_word_frequency_ratio: float = 0.14
    max_urls: int = 1
    max_line_length: int = 20_000


@dataclass
class FilterResult:
    text: str
    accepted: bool
    reasons: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def stable_bucket(text: str, modulo: int) -> int:
    digest = hashlib.blake2b(text.encode("utf-8", errors="ignore"), digest_size=8).digest()
    return int.from_bytes(digest, "big") % modulo


def normalize_for_hash(text: str) -> str:
    text = text.lower()
    text = URL_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def strip_wikipedia_tail(text: str) -> tuple[str, int]:
    """Remove common low-value tail sections from a Wikipedia article."""
    match = WIKI_SECTION_RE.search(text)
    if not match:
        return text, 0
    return text[: match.start()].rstrip(), 1


def clean_text(text: str, source: str = "") -> tuple[str, dict[str, int]]:
    raw_url_count = len(URL_RE.findall(text))
    raw_html_count = len(HTML_RE.findall(text))
    text = html.unescape(text)
    if source == "wikipedia_pl":
        text, wiki_tail_removed = strip_wikipedia_tail(text)
    else:
        wiki_tail_removed = 0
    text = HTML_RE.sub(" ", text)
    text = URL_RE.sub(" ", text)
    text = CONTROL_RE.sub("", text)
    text = REPEATED_PUNCT_RE.sub(r"\1\1", text)
    text = MULTISPACE_RE.sub(" ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip(), {
        "urls": raw_url_count,
        "html_tags": raw_html_count,
        "wiki_tail_removed": wiki_tail_removed,
    }


def words_for_text(text: str) -> list[str]:
    return [w.lower() for w in WORD_RE.findall(text)]


def repetition_score(words: list[str]) -> float:
    if len(words) < 24:
        return 0.0
    grams = [" ".join(words[i : i + 4]) for i in range(len(words) - 3)]
    counts = collections.Counter(grams)
    repeated = sum(count - 1 for count in counts.values() if count > 1)
    return repeated / max(len(grams), 1)


def near_duplicate_key(words: list[str]) -> str:
    if len(words) < 32:
        normalized = " ".join(words)
        return sha1_text(normalized)[:16]
    shingles = [" ".join(words[i : i + 5]) for i in range(0, max(1, len(words) - 4), 3)]
    hashed = sorted(hashlib.blake2b(s.encode("utf-8"), digest_size=8).hexdigest() for s in shingles)
    sketch = " ".join(hashed[:24])
    prefix = " ".join(words[:80])
    return sha1_text(prefix + "\n" + sketch)[:20]


def text_metrics(text: str) -> dict[str, Any]:
    words = words_for_text(text)
    chars = len(text)
    alpha = sum(ch.isalpha() for ch in text)
    polish_chars = sum(ch in POLISH_CHARS for ch in text)
    punct_or_symbol = sum((not ch.isalnum()) and (not ch.isspace()) for ch in text)
    stop_hits = sum(1 for w in words if w in POLISH_STOPWORDS)
    unique_words = len(set(words))
    max_word_freq = max(collections.Counter(words).values(), default=0)
    lines = text.splitlines() or [text]
    return {
        "chars": chars,
        "words": len(words),
        "alpha_ratio": alpha / max(chars, 1),
        "polish_char_ratio": polish_chars / max(alpha, 1),
        "polish_stopword_ratio": stop_hits / max(len(words), 1),
        "control_count": len(CONTROL_RE.findall(text)),
        "punct_symbol_ratio": punct_or_symbol / max(chars, 1),
        "unique_word_ratio": unique_words / max(len(words), 1),
        "max_word_frequency_ratio": max_word_freq / max(len(words), 1),
        "repetition_score": repetition_score(words),
        "line_count": len(lines),
        "max_line_length": max((len(line) for line in lines), default=0),
    }


def quality_score(metrics: dict[str, Any], raw_markers: dict[str, int], suspicious_hits: int) -> float:
    score = 1.0
    score -= max(0.0, 0.62 - float(metrics["alpha_ratio"])) * 1.2
    score -= max(0.0, 0.035 - float(metrics["polish_stopword_ratio"])) * 4.0
    score -= min(0.25, float(metrics["punct_symbol_ratio"]))
    score -= min(0.25, float(metrics["repetition_score"]) * 2.5)
    score -= min(0.20, raw_markers.get("urls", 0) * 0.05)
    score -= min(0.20, suspicious_hits * 0.04)
    return max(0.0, min(1.0, score))


def evaluate_document(
    raw_text: str,
    *,
    source: str,
    config: FilterConfig,
    exact_seen: set[str] | None = None,
    normalized_seen: set[str] | None = None,
    near_seen: set[str] | None = None,
) -> FilterResult:
    clean, raw_markers = clean_text(raw_text, source=source)
    metrics = text_metrics(clean)
    words = words_for_text(clean)
    lower = clean.lower()
    suspicious = [pattern for pattern in BOILERPLATE_PATTERNS if pattern in lower]

    exact_hash = sha1_text(clean)
    normalized_hash = sha1_text(normalize_for_hash(clean))
    near_hash = near_duplicate_key(words)

    metrics.update(
        {
            "raw_url_count": raw_markers["urls"],
            "raw_html_tag_count": raw_markers["html_tags"],
            "wiki_tail_removed": raw_markers["wiki_tail_removed"],
            "suspicious_section_count": len(suspicious),
            "suspicious_patterns": suspicious[:8],
            "exact_hash": exact_hash,
            "normalized_hash": normalized_hash,
            "near_hash": near_hash,
        }
    )
    metrics["quality_score"] = quality_score(metrics, raw_markers, len(suspicious))

    reasons: list[str] = []
    if not clean:
        reasons.append("empty_after_clean")
    if metrics["words"] < config.min_words:
        reasons.append("too_short")
    if metrics["chars"] > config.max_chars:
        reasons.append("too_long")
    if raw_markers["html_tags"] > 0:
        reasons.append("html_present")
    if raw_markers["urls"] > config.max_urls and source != "wolne_lektury":
        reasons.append("too_many_urls")
    if metrics["alpha_ratio"] < config.min_alpha_ratio:
        reasons.append("low_alpha_ratio")
    if (
        metrics["polish_stopword_ratio"] < config.min_polish_stopword_ratio
        and metrics["polish_char_ratio"] < 0.002
        and metrics["words"] >= 30
    ):
        reasons.append("low_polish_signal")
    if metrics["punct_symbol_ratio"] > config.max_punct_symbol_ratio:
        reasons.append("too_much_punctuation_or_symbols")
    if metrics["max_line_length"] > config.max_line_length:
        reasons.append("very_long_line")
    if metrics["unique_word_ratio"] < config.min_unique_word_ratio and metrics["words"] >= 100:
        reasons.append("low_unique_word_ratio")
    if metrics["max_word_frequency_ratio"] > config.max_word_frequency_ratio and metrics["words"] >= 100:
        reasons.append("single_word_repetition")
    if metrics["repetition_score"] > config.max_repetition_score:
        reasons.append("repeated_ngrams")
    if len(suspicious) >= 3 and source != "wikipedia_pl":
        reasons.append("too_many_boilerplate_patterns")
    if source == "legacy_mixed_corpus" and any(pattern in lower for pattern in LEGACY_HARD_REJECT_PATTERNS):
        reasons.append("legacy_web_garbage_pattern")
    if source == "legacy_mixed_corpus" and metrics["polish_stopword_ratio"] < 0.035 and metrics["words"] >= 60:
        reasons.append("legacy_low_polish_stopword_signal")
    if source == "legacy_mixed_corpus" and len(re.findall(r"\b\d{1,2}:\d{2}\b", clean)) >= 4:
        reasons.append("legacy_comment_or_listing_times")
    if exact_seen is not None and exact_hash in exact_seen:
        reasons.append("exact_duplicate")
    if normalized_seen is not None and normalized_hash in normalized_seen:
        reasons.append("normalized_duplicate")
    if near_seen is not None and near_hash in near_seen and metrics["words"] >= 80:
        reasons.append("near_duplicate")

    return FilterResult(text=clean, accepted=not reasons, reasons=reasons, metrics=metrics)


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


def truncate_text(text: str, max_chars: int = 900) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."
