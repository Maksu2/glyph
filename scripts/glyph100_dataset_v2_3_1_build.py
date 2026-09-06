#!/usr/bin/env python3
"""Build Glyph-100M dataset v2.3.1 by cleaning existing v2.3 FineWeb2 docs.

This script does not download data and does not train. It reads the already
built v2.3 docs JSONL, keeps the clean non-FineWeb sources, applies stricter
domain/content/page-quality filtering to FineWeb2 PL, and writes new v2.3.1
artifacts without overwriting v2.3.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

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
from glyph100_dataset_v2_2_build import keep_sample, load_sentencepiece, word_count  # noqa: E402
from glyph100_dataset_identity import parent_doc_id_for, parent_split_for  # noqa: E402


DEFAULT_INPUT_DOCS = Path("data/processed/glyph100_v2_3_docs.jsonl")
DEFAULT_V2_3_STATS = Path("data/reports/glyph100_dataset_v2_3_stats.json")
DEFAULT_TOKENIZER = Path("data/processed/tokenizer.model")
DEFAULT_TRAIN_BIN = Path("data/processed/glyph100_v2_3_1_train.bin")
DEFAULT_VAL_BIN = Path("data/processed/glyph100_v2_3_1_val.bin")
DEFAULT_METADATA = Path("data/processed/glyph100_v2_3_1_metadata.json")
DEFAULT_DOCS_JSONL = Path("data/processed/glyph100_v2_3_1_docs.jsonl")
DEFAULT_STATS = Path("data/reports/glyph100_dataset_v2_3_1_stats.json")
DEFAULT_REPORT = Path("data/reports/glyph100_dataset_v2_3_1_report.md")
DEFAULT_DOMAIN_AUDIT = Path("data/reports/glyph100_v2_3_domain_audit.md")
DEFAULT_ACCEPTED_SAMPLES = Path("data/reports/glyph100_dataset_v2_3_1_samples_accepted.jsonl")
DEFAULT_REJECTED_SAMPLES = Path("data/reports/glyph100_dataset_v2_3_1_samples_rejected.jsonl")
DEFAULT_FINAL_SAMPLES = Path("data/reports/glyph100_dataset_v2_3_1_samples_final_random.jsonl")
DEFAULT_DECISION_MD = Path("reports/glyph100_dataset_v2_3_1_decision_report.md")

TOKENS_PER_STEP = 4 * 512 * 8
TRAINING_TOKENS_50K = 50_000 * TOKENS_PER_STEP
TRAINING_TOKENS_100K = 100_000 * TOKENS_PER_STEP
TRAINING_TOKENS_200K = 200_000 * TOKENS_PER_STEP

HARD_DOMAIN_SUBSTRINGS = {
    "forum": "forum_domain",
    "fora.": "forum_domain",
    "wykop.pl": "social_or_comments_domain",
    "elektroda.pl": "forum_domain",
    "zapytaj": "qa_domain",
    "tripadvisor": "travel_listing_domain",
    "pinterest": "listing_or_image_board_domain",
    "empik.com": "commerce_domain",
    "ceneo.": "commerce_domain",
    "allegro.": "commerce_domain",
    "olx.": "classifieds_domain",
    "otomoto": "classifieds_domain",
    "znanylekarz": "directory_or_listing_domain",
    "booksy": "directory_or_listing_domain",
    "fandom": "fandom_or_game_wiki_domain",
    "gry-online": "gaming_clickbait_domain",
    "igry.pl": "gaming_clickbait_domain",
    "gamepressure": "gaming_clickbait_domain",
    "filmweb": "entertainment_listing_domain",
    "kozaczek": "gossip_domain",
    "pudelek": "gossip_domain",
    "plejada": "gossip_domain",
    "styl.fm": "gossip_domain",
    "jastrzabpost": "gossip_domain",
    "pomponik": "gossip_domain",
    "plotek": "gossip_domain",
    "dreamstime": "image_listing_domain",
    "gettyimages": "image_listing_domain",
    "istockphoto": "image_listing_domain",
    "shutterstock": "image_listing_domain",
    "telefon.info.pl": "contact_directory_domain",
    "telefonowal.pl": "contact_directory_domain",
    "dobrymechanik.pl": "directory_or_listing_domain",
    "gowork.pl": "directory_or_listing_domain",
    "msze.info": "directory_or_listing_domain",
    "booksy": "directory_or_listing_domain",
    "kolezanka.net": "gossip_domain",
    "astromagia.pl": "gossip_domain",
    "party.pl": "gossip_domain",
    "labizu.pl": "commerce_domain",
    "zamglawiacze.com": "commerce_domain",
    "abc-auta.pl": "product_page_domain",
    "zmidzinski.com": "service_landing_domain",
    "sztukateria-haga.pl": "service_landing_domain",
    "plklasad.com": "manual_or_boilerplate_domain",
    "tsfalenica.pl": "manual_or_boilerplate_domain",
    "wizytowki-nap.ovh": "spammy_generated_domain",
    "modne-budowanie.pl": "service_landing_domain",
    "poznanskiprestiz.pl": "travel_listing_domain",
    "blogspot.com": "blog_or_snippet_domain",
    "upadlosckonsumencka.info.pl": "loan_or_credit_spam",
    "antywindykacja.net": "loan_or_credit_spam",
    "stlouishomehealthcare.com": "spammy_generated_domain",
    "medventmedical.com": "service_landing_domain",
    "morsmordre.net": "fandom_or_roleplay_domain",
    "9lib.org": "book_piracy_or_listing_domain",
    "botheration.org": "spammy_generated_domain",
}

SOFT_RISK_DOMAIN_SUBSTRINGS = {
    "fakt.pl": "tabloid_domain",
    "se.pl": "tabloid_domain",
    "o2.pl": "portal_soft_clickbait_domain",
    "wp.pl": "portal_soft_clickbait_domain",
    "interia.pl": "portal_domain",
    "onet.pl": "portal_domain",
    "dziennik.pl": "portal_domain",
    "dlahandlu.pl": "commerce_news_domain",
    "centrumrowerowe": "commerce_domain",
    "mediaexpert": "commerce_domain",
    "leroymerlin": "commerce_domain",
    "castorama": "commerce_domain",
    "stal-mat.pl": "service_landing_domain",
}

GOOD_DOMAIN_SUBSTRINGS = {
    "kopalniawiedzy.pl": "science_or_education_domain",
    "prawo.pl": "professional_article_domain",
    "rynekzdrowia.pl": "professional_article_domain",
    "rp.pl": "news_article_domain",
    "tvn24.pl": "news_article_domain",
    "rmf24.pl": "news_article_domain",
    "portalsamorzadowy.pl": "professional_article_domain",
    "parlamentarny.pl": "professional_article_domain",
    "wirtualnemedia.pl": "media_industry_article_domain",
    "pb.pl": "business_article_domain",
}

URL_REJECT_RE = re.compile(
    r"/(kontakt|contact|regulamin|polityka-prywatnosci|privacy|cookies|koszyk|cart|checkout|produkt|product|"
    r"lp[,0-9-]|category|kategoria|tag|author|forum|opinie|cennik|oferta|uslugi|sklep|catalog|katalog)(/|$|[-_,0-9])",
    re.IGNORECASE,
)
GAMBLING_RE = re.compile(
    r"\b(kasyn[ao]|sloty|spiny|ruletka|blackjack|bonus bez depozytu|automaty do gry|bukmacher)\b",
    re.IGNORECASE,
)
LOAN_RE = re.compile(r"\b(pożyczk[ai]|chwilówk[ai]|kredyt na dowód|szybki kredyt|konsolidacja długu)\b", re.IGNORECASE)
PRICE_RE = re.compile(r"\b\d+([,.]\d+)?\s?(zł|pln|eur|usd)\b", re.IGNORECASE)
COOKIE_RE = re.compile(
    r"używamy cookies|używamy plików cookie|plików cookies?|polityka prywatności|zgoda na cookies|"
    r"strona internetowa korzysta z plików cookie",
    re.IGNORECASE,
)
FANDOM_RE = re.compile(r"(?im)^\s*(Kategorie:|Języki:|Treści społeczności|Fandom Apps|Eksploruj wiki)\b")
FORUM_RE = re.compile(r"\b(odpowiedz|cytuj|komentarze|napisał/a|postautor|dołączył|zarejestrowany)\b", re.IGNORECASE)
CLICK_RE = re.compile(
    r"\b(zobacz również|zobacz także|polecamy|więcej informacji|kliknij|czytaj także|czytaj też|"
    r"sprawdź ofertę|skontaktuj się z nami|polecany artykuł|tutaj|reklama)\b",
    re.IGNORECASE,
)
COMMERCE_RE = re.compile(
    r"\b(dodaj do koszyka|zamów|promocja|produkt|produkty|cena|cennik|dostawa|wysyłka|"
    r"w magazynie|kod produktu|opinie klientów|kup teraz|sklep internetowy|kolekcja|bransoletki|"
    r"najlepsze materiały produkcyjne|łatwy w obsłudze|model [A-Z0-9-]{2,})\b",
    re.IGNORECASE,
)
SERVICE_RE = re.compile(
    r"\b(nasza firma|świadczymy usługi|profesjonalne usługi|oferta firmy|zapraszamy do kontaktu|formularz kontaktowy|"
    r"oferowane przez nas|nasza oferta|najlepsze rozwiązania dla|dostępne w wielu kolorach)\b",
    re.IGNORECASE,
)
DIRECTORY_RE = re.compile(
    r"\b(niedziele i święta|dni powszednie|mapa dojazdu|brak informacji o|godz\.\s*\d|"
    r"szczegółowe informacje znajdą państwo|klikając w poniższy link)\b",
    re.IGNORECASE,
)
GOSSIP_RE = re.compile(
    r"\b(show-?biznes|celebryt|celebrytka|gwiazda|gwiazdy|paparazzi|hakiel|cichopek|"
    r"kurzajewski|kate moss|lila grace moss)\b",
    re.IGNORECASE,
)
SNIPPET_RE = re.compile(
    r"\b(opublikowano:|ostatnia aktualizacja:|polecamy|reklama|tutaj|zobacz jak|"
    r"więcej .* tutaj|przeczytaj także|czytaj również)\b",
    re.IGNORECASE,
)
ARTICLE_POSITIVE_RE = re.compile(
    r"\b(badanie|naukowcy|historia|raport|analiza|wyjaśnia|edukacja|uczniowie|szkoła|"
    r"samorząd|ustawa|zdrowie|medycyna|technologia|klimat|kultura|literatura)\b",
    re.IGNORECASE,
)
LIST_LINE_RE = re.compile(r"(?m)^\s*(?:[-*•]|\d+[.)])\s+")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def json_dump_line(handle, obj: dict[str, Any]) -> None:
    handle.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")


def write_uint16_tokens(handle, ids: list[int]) -> None:
    np.asarray(ids, dtype=np.uint16).tofile(handle)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            json_dump_line(handle, row)


def domain_from_url(url: str) -> str:
    return re.sub(r"^https?://", "", url or "").split("/", 1)[0].lower() or "(none)"


def path_from_url(url: str) -> str:
    return "/" + (re.sub(r"^https?://", "", url or "").split("/", 1)[1] if "/" in re.sub(r"^https?://", "", url or "") else "")


def domain_match(domain: str, patterns: dict[str, str]) -> str | None:
    for needle, reason in patterns.items():
        if needle in domain:
            return reason
    return None


def split_for(record: dict[str, Any], val_per_mille: int) -> str:
    return parent_split_for(record, val_per_mille)


def sample_payload(record: dict[str, Any], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "id": record.get("id", ""),
        "source": record.get("source", ""),
        "doc_id": record.get("doc_id", ""),
        "title": record.get("title", ""),
        "url": record.get("url", ""),
        "domain": domain_from_url(record.get("url", "")),
        "quality_score": record.get("quality_score", 0),
        "text": truncate_text(record.get("text", ""), 1100),
    }
    if extra:
        payload.update(extra)
    return payload


def ensure_safe_outputs(args: argparse.Namespace) -> None:
    forbidden = {
        Path("data/processed/tokens.bin").resolve(),
        Path("data/processed/val_tokens.bin").resolve(),
        Path("data/processed/glyph100_v2_3_train.bin").resolve(),
        Path("data/processed/glyph100_v2_3_val.bin").resolve(),
        Path("data/processed/glyph100_v2_3_docs.jsonl").resolve(),
        Path("data/processed/glyph100_v2_3_metadata.json").resolve(),
    }
    outputs = [
        args.train_bin,
        args.val_bin,
        args.metadata,
        args.docs_jsonl,
        args.stats,
        args.report,
        args.domain_audit,
        args.accepted_samples,
        args.rejected_samples,
        args.final_samples,
        args.decision_md,
    ]
    for path in outputs:
        if path.resolve() in forbidden:
            raise SystemExit(f"Refusing to overwrite protected output: {path}")
    existing = [path for path in outputs if path.exists()]
    if existing and not args.force_v2_3_1:
        formatted = "\n".join(f"- {path}" for path in existing)
        raise SystemExit(f"v2.3.1 outputs already exist. Use --force-v2-3-1 to replace only v2.3.1:\n{formatted}")
    for path in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)


def fineweb_filter_config() -> FilterConfig:
    return FilterConfig(
        min_words=120,
        max_chars=80_000,
        min_alpha_ratio=0.58,
        min_polish_stopword_ratio=0.024,
        max_punct_symbol_ratio=0.12,
        max_repetition_score=0.028,
        min_unique_word_ratio=0.25,
        max_word_frequency_ratio=0.10,
        max_urls=0,
        max_line_length=15_000,
    )


def page_quality(record: dict[str, Any], result_metrics: dict[str, Any]) -> tuple[float, list[str], list[str]]:
    text = record.get("text", "")
    lower = text.lower()
    url = record.get("url", "")
    domain = domain_from_url(url)
    reasons: list[str] = []
    labels: list[str] = []
    score = 0.0

    hard = domain_match(domain, HARD_DOMAIN_SUBSTRINGS)
    if hard:
        reasons.append(hard)
        score -= 4.0
    soft = domain_match(domain, SOFT_RISK_DOMAIN_SUBSTRINGS)
    if soft:
        labels.append(soft)
        score -= 1.0
    good = domain_match(domain, GOOD_DOMAIN_SUBSTRINGS)
    if good:
        labels.append(good)
        score += 1.2
    if URL_REJECT_RE.search(url):
        reasons.append("bad_url_path")
        score -= 2.0
    for name, regex, penalty in [
        ("gambling_spam", GAMBLING_RE, 4.0),
        ("loan_or_credit_spam", LOAN_RE, 4.0),
        ("cookie_privacy_boilerplate", COOKIE_RE, 3.0),
        ("fandom_or_category_boilerplate", FANDOM_RE, 4.0),
        ("forum_or_comment_layout", FORUM_RE, 3.0),
        ("commerce_terms", COMMERCE_RE, 3.0),
        ("service_landing_language", SERVICE_RE, 2.0),
        ("directory_or_listing_content", DIRECTORY_RE, 2.5),
        ("gossip_or_celebrity_content", GOSSIP_RE, 2.5),
    ]:
        hits = regex.findall(text)
        if hits:
            reasons.append(name)
            score -= penalty
    price_hits = PRICE_RE.findall(text)
    if len(price_hits) >= 2:
        reasons.append("prices_present")
        score -= min(3.0, len(price_hits) * 0.8)
    click_hits = CLICK_RE.findall(text)
    if len(click_hits) >= 2:
        reasons.append("clickbait_or_related_links")
        score -= 1.8
    snippet_hits = SNIPPET_RE.findall(text)
    if len(snippet_hits) >= 2:
        reasons.append("snippet_or_boilerplate_page")
        score -= 1.8
    if text.upper().count("REKLAMA") >= 2:
        reasons.append("ad_boilerplate")
        score -= 1.5
    if text.count("…") >= 2 or text.count("...") >= 2:
        reasons.append("multi_snippet_ellipsis")
        score -= 1.2
    list_lines = len(LIST_LINE_RE.findall(text))
    words = int(result_metrics.get("words") or word_count(text))
    if list_lines >= 10 and words < 700:
        reasons.append("list_heavy_page")
        score -= 1.8
    if text.count("|") >= 8:
        reasons.append("table_or_separator_heavy")
        score -= 1.5
    positive_hits = ARTICLE_POSITIVE_RE.findall(text)
    if len(positive_hits) >= 3:
        labels.append("article_or_education_signals")
        score += 0.8
    if words >= 220:
        score += 0.5
    if words >= 500:
        score += 0.4
    if float(result_metrics.get("quality_score") or 0) >= 0.94:
        score += 0.4
    if float(result_metrics.get("repetition_score") or 0) > 0.020:
        reasons.append("page_repetition_penalty")
        score -= 1.2
    if "źródło:" in lower and words < 220:
        reasons.append("short_syndicated_blurb")
        score -= 1.0
    return score, reasons, labels


def classify_domain(domain: str, docs: int, tokens: int, examples: list[str]) -> dict[str, Any]:
    hard = domain_match(domain, HARD_DOMAIN_SUBSTRINGS)
    soft = domain_match(domain, SOFT_RISK_DOMAIN_SUBSTRINGS)
    good = domain_match(domain, GOOD_DOMAIN_SUBSTRINGS)
    decision = "use"
    risk = "normal web/news article source; inspect samples"
    if hard:
        decision = "reject"
        risk = hard
    elif soft:
        decision = "penalize"
        risk = soft
    elif good:
        decision = "use"
        risk = good
    elif docs >= 300 and tokens / max(docs, 1) < 350:
        decision = "penalize"
        risk = "short_page_heavy_domain"
    return {"domain": domain, "docs": docs, "tokens": tokens, "decision": decision, "risk": risk, "examples": examples[:3]}


def write_record(
    record: dict[str, Any],
    *,
    sp,
    eos_id: int,
    train_out,
    val_out,
    docs_out,
    counters: dict[str, Any],
    final_samples: list[dict[str, Any]],
    accepted_samples: list[dict[str, Any]],
    sample_limit: int,
    val_per_mille: int,
) -> int:
    ids = sp.encode(record["text"], out_type=int)
    ids.append(eos_id)
    record["parent_doc_id"] = parent_doc_id_for(record)
    split = split_for(record, val_per_mille)
    source_state = counters["source_mix"][record["source"]]
    record.setdefault("meta", {})["token_count"] = len(ids)
    record["meta"]["word_count"] = word_count(record["text"])
    record["meta"]["split"] = split
    record["meta"]["dataset_name"] = "glyph100_dataset_v2_3_1"
    json_dump_line(docs_out, record)
    if split == "val":
        write_uint16_tokens(val_out, ids)
        counters["val_docs"] += 1
        counters["val_tokens"] += len(ids)
        source_state["val_docs"] += 1
        source_state["val_tokens"] += len(ids)
    else:
        write_uint16_tokens(train_out, ids)
        counters["train_docs"] += 1
        counters["train_tokens"] += len(ids)
        source_state["train_docs"] += 1
        source_state["train_tokens"] += len(ids)
    source_state["docs"] += 1
    source_state["tokens"] += len(ids)
    counters["total_words"] += record["meta"]["word_count"]
    counters["token_lengths"].append(len(ids))
    keep_sample(accepted_samples, sample_payload(record, {"token_count": len(ids), "split": split}), record["id"], sample_limit)
    keep_sample(final_samples, sample_payload(record, {"token_count": len(ids), "split": split}), record["id"], sample_limit)
    return len(ids)


def render_samples(samples: list[dict[str, Any]], limit: int = 20) -> str:
    if not samples:
        return "_none_"
    chunks = []
    for i, sample in enumerate(samples[:limit], 1):
        chunks.append(
            f"{i}. `{sample.get('source', '')}` `{sample.get('domain', '')}` {sample.get('title', '')} "
            f"(tokens={sample.get('token_count', 'n/a')}, score={sample.get('quality_score', 'n/a')})\n\n"
            f"   {sample.get('text', '')}"
        )
    return "\n\n".join(chunks)


def render_domain_audit(stats: dict[str, Any]) -> str:
    rows = []
    for item in stats["domain_audit_top"]:
        rows.append(
            f"| `{item['domain']}` | {item['docs']:,} | {item['tokens']:,} | "
            f"{item['decision']} | {item['risk']} |"
        )
    return f"""# Glyph-100M v2.3 FineWeb2 Domain Audit

Generated: {stats["generated_at"]}

No training was started.

## Summary

- FineWeb2 docs in v2.3: {stats["v2_3_fineweb_docs"]:,}
- FineWeb2 tokens in v2.3: {stats["v2_3_fineweb_tokens"]:,}
- FineWeb2 docs kept in v2.3.1: {stats["fineweb2_kept_docs"]:,}
- FineWeb2 tokens kept in v2.3.1: {stats["fineweb2_kept_tokens"]:,}
- FineWeb2 docs rejected by cleanup: {stats["fineweb2_rejected_docs"]:,}
- FineWeb2 tokens rejected by cleanup: {stats["fineweb2_rejected_tokens"]:,}

## Domain Decisions

| domain | docs | tokens | decision | risk |
|---|---:|---:|---|---|
{chr(10).join(rows)}

## Domain Reject/Penalty Notes

- hard reject: forums/Q&A/social comments, commerce/marketplaces/product pages, gambling/loans, fandom/game wiki/category pages, gossip/clickbait, listings/directories.
- penalty: soft portals, service/landing domains, tabloid-ish domains. These may still pass if page-level quality is strong.
- use: professional/news/education domains still go through content quality checks.

## Rejection Reasons

```json
{json.dumps(stats["rejection_reasons"], ensure_ascii=False, indent=2)}
```
"""


def render_report(stats: dict[str, Any]) -> str:
    total = max(stats["total_tokens"], 1)
    rows = []
    for source, item in stats["source_mix"].items():
        rows.append(
            f"| `{source}` | {item['docs']:,} | {item['tokens']:,} | {item['tokens'] / total:.2%} | "
            f"{item['train_tokens']:,} | {item['val_tokens']:,} |"
        )
    comparison = stats["comparison_v2_3"]
    return f"""# Glyph-100M Dataset v2.3.1 Report

Generated: {stats["generated_at"]}

No training was started.

## Verdict

{stats["recommendation"]}

## Outputs

- train bin: `{stats["train_bin"]}`
- val bin: `{stats["val_bin"]}`
- docs JSONL: `{stats["docs_jsonl"]}`
- metadata: `{stats["metadata_path"]}`
- tokenizer: `{stats["tokenizer_path"]}`

## v2.3 vs v2.3.1

| metric | v2.3 | v2.3.1 |
|---|---:|---:|
| total tokens | {comparison["v2_3_total_tokens"]:,} | {stats["total_tokens"]:,} |
| FineWeb2 tokens | {comparison["v2_3_fineweb2_tokens"]:,} | {stats["fineweb2_tokens"]:,} |
| Wikipedia share | {comparison["v2_3_wikipedia_share"]:.2%} | {stats["wikipedia_share"]:.2%} |
| FineWeb2 share | {comparison["v2_3_fineweb2_share"]:.2%} | {stats["fineweb2_share"]:.2%} |
| 50k epochs | {comparison["v2_3_stage3_epochs"]:.2f} | {stats["stage3_50k_epochs"]:.2f} |

- tokens removed from v2.3: {stats["tokens_removed_from_v2_3"]:,}
- FineWeb2 tokens removed: {stats["fineweb2_rejected_tokens"]:,}

## Source Mix

| source | docs | tokens | share | train tokens | val tokens |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

## Rejection Reasons

```json
{json.dumps(stats["rejection_reasons"], ensure_ascii=False, indent=2)}
```

## Training Math

- stage 3 / 50k total: {TRAINING_TOKENS_50K:,} tokens = {stats["stage3_50k_epochs"]:.2f} epochs
- 100k total: {TRAINING_TOKENS_100K:,} tokens = {stats["stage4_100k_epochs"]:.2f} epochs
- 200k total: {TRAINING_TOKENS_200K:,} tokens = {stats["stage5_200k_epochs"]:.2f} epochs

## Quality Notes

- Legacy remains 0.
- FineWeb2 is filtered through domain hard rejects, URL rejects, content boilerplate patterns and a simple page-quality classifier.
- v2.3.1 is intentionally smaller than v2.3 if the cleanup works.
- Remaining risk: accepted FineWeb2 can still contain normal web/news style and occasional mild portal residue. Inspect samples before any 50k run.

## Final Random Samples

{render_samples(stats["final_samples"], 50)}
"""


def render_decision(stats: dict[str, Any]) -> str:
    return f"""# Glyph-100M Dataset v2.3.1 Decision Report

Generated: {stats["generated_at"]}

No training was started.

## Recommendation

{stats["decision_code"]}

{stats["recommendation"]}

## Key Numbers

- total tokens: {stats["total_tokens"]:,}
- train tokens: {stats["train_tokens"]:,}
- val tokens: {stats["val_tokens"]:,}
- Wikipedia share: {stats["wikipedia_share"]:.2%}
- FineWeb2 PL share: {stats["fineweb2_share"]:.2%}
- legacy share: 0.00%
- stage 3 / 50k epochs: {stats["stage3_50k_epochs"]:.2f}
- FineWeb2 docs kept/rejected: {stats["fineweb2_kept_docs"]:,} / {stats["fineweb2_rejected_docs"]:,}
- FineWeb2 tokens kept/rejected: {stats["fineweb2_tokens"]:,} / {stats["fineweb2_rejected_tokens"]:,}
- tokens removed from v2.3: {stats["tokens_removed_from_v2_3"]:,}

## Source Mix

```json
{json.dumps(stats["source_mix"], ensure_ascii=False, indent=2)}
```

## Decision Options

- A) v2.3.1 gotowy do stage 3 / 50k po osobnej zgodzie.
- B) jeszcze poprawić filtry.
- C) FineWeb2 jest za brudny i trzeba inne źródło.
- D) zrobić krótki preflight, nie 50k.

No stage 3 command was executed.
"""


def load_v2_3_stats(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Glyph-100M dataset v2.3.1 cleanup")
    parser.add_argument("--input-docs", type=Path, default=DEFAULT_INPUT_DOCS)
    parser.add_argument("--v2-3-stats", type=Path, default=DEFAULT_V2_3_STATS)
    parser.add_argument("--tokenizer", type=Path, default=DEFAULT_TOKENIZER)
    parser.add_argument("--train-bin", type=Path, default=DEFAULT_TRAIN_BIN)
    parser.add_argument("--val-bin", type=Path, default=DEFAULT_VAL_BIN)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--docs-jsonl", type=Path, default=DEFAULT_DOCS_JSONL)
    parser.add_argument("--stats", type=Path, default=DEFAULT_STATS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--domain-audit", type=Path, default=DEFAULT_DOMAIN_AUDIT)
    parser.add_argument("--accepted-samples", type=Path, default=DEFAULT_ACCEPTED_SAMPLES)
    parser.add_argument("--rejected-samples", type=Path, default=DEFAULT_REJECTED_SAMPLES)
    parser.add_argument("--final-samples", type=Path, default=DEFAULT_FINAL_SAMPLES)
    parser.add_argument("--decision-md", type=Path, default=DEFAULT_DECISION_MD)
    parser.add_argument("--sample-limit", type=int, default=50)
    parser.add_argument("--val-per-mille", type=int, default=5)
    parser.add_argument("--min-page-score", type=float, default=0.75)
    parser.add_argument("--progress-every", type=int, default=100_000)
    parser.add_argument("--force-v2-3-1", action="store_true")
    args = parser.parse_args()

    ensure_safe_outputs(args)
    sp = load_sentencepiece(args.tokenizer)
    eos_id = sp.eos_id()
    v2_3_stats = load_v2_3_stats(args.v2_3_stats)
    start = time.time()

    counters: dict[str, Any] = {
        "train_docs": 0,
        "val_docs": 0,
        "train_tokens": 0,
        "val_tokens": 0,
        "total_words": 0,
        "token_lengths": [],
        "source_mix": collections.defaultdict(
            lambda: {"docs": 0, "tokens": 0, "train_docs": 0, "val_docs": 0, "train_tokens": 0, "val_tokens": 0}
        ),
        "rejection_reasons": collections.Counter(),
    }
    domain_docs: collections.Counter[str] = collections.Counter()
    domain_tokens: collections.Counter[str] = collections.Counter()
    domain_examples: dict[str, list[str]] = collections.defaultdict(list)
    accepted_samples: list[dict[str, Any]] = []
    rejected_samples: list[dict[str, Any]] = []
    final_samples: list[dict[str, Any]] = []
    exact_seen: set[str] = set()
    normalized_seen: set[str] = set()
    near_seen: set[str] = set()
    fineweb_seen_docs = fineweb_seen_tokens = 0
    fineweb_kept_docs = fineweb_rejected_docs = 0
    fineweb_rejected_tokens = 0
    config = fineweb_filter_config()

    with args.train_bin.open("wb") as train_out, args.val_bin.open("wb") as val_out, args.docs_jsonl.open(
        "w", encoding="utf-8"
    ) as docs_out, args.input_docs.open(encoding="utf-8") as docs_in:
        for i, line in enumerate(docs_in, 1):
            if not line.strip():
                continue
            record = json.loads(line)
            old_tokens = int((record.get("meta") or {}).get("token_count") or 0)
            source = record.get("source", "")
            if source == "fineweb2_pl":
                fineweb_seen_docs += 1
                fineweb_seen_tokens += old_tokens
                domain = domain_from_url(record.get("url", ""))
                domain_docs[domain] += 1
                domain_tokens[domain] += old_tokens
                if len(domain_examples[domain]) < 3:
                    domain_examples[domain].append(record.get("url", ""))
                result = evaluate_document(
                    record.get("text", ""),
                    source="fineweb2_pl",
                    config=config,
                    exact_seen=exact_seen,
                    normalized_seen=normalized_seen,
                    near_seen=near_seen,
                )
                page_score, page_reasons, labels = page_quality(record, result.metrics)
                reasons = []
                if not result.accepted:
                    reasons.extend(result.reasons)
                reasons.extend(page_reasons)
                if page_score < args.min_page_score:
                    reasons.append("low_page_quality_score")
                if reasons:
                    fineweb_rejected_docs += 1
                    fineweb_rejected_tokens += old_tokens
                    for reason in reasons:
                        counters["rejection_reasons"][reason] += 1
                    reject_record = sample_payload(
                        record,
                        {
                            "reject_reason": reasons[0],
                            "reject_reasons": reasons,
                            "page_score": round(page_score, 3),
                            "page_labels": labels,
                            "token_count": old_tokens,
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
                    )
                    keep_sample(rejected_samples, reject_record, f"reject:{record.get('id','')}", args.sample_limit)
                    continue
                record["text"] = result.text
                record["quality_score"] = round(float(result.metrics.get("quality_score", record.get("quality_score", 0))), 4)
                record.setdefault("meta", {})["v2_3_1_cleanup"] = {
                    "page_score": round(page_score, 3),
                    "page_labels": labels,
                    "domain": domain,
                }
                for key in ["exact_hash", "normalized_hash", "near_hash"]:
                    value = result.metrics.get(key)
                    if key == "exact_hash" and value:
                        exact_seen.add(str(value))
                    if key == "normalized_hash" and value:
                        normalized_seen.add(str(value))
                    if key == "near_hash" and value:
                        near_seen.add(str(value))
                fineweb_kept_docs += 1
            else:
                record.setdefault("meta", {})["v2_3_1_cleanup"] = {"kept_non_fineweb_source": True}
            write_record(
                record,
                sp=sp,
                eos_id=eos_id,
                train_out=train_out,
                val_out=val_out,
                docs_out=docs_out,
                counters=counters,
                final_samples=final_samples,
                accepted_samples=accepted_samples,
                sample_limit=args.sample_limit,
                val_per_mille=args.val_per_mille,
            )
            if args.progress_every and i % args.progress_every == 0:
                print(
                    f"seen={i:,} fineweb_kept={fineweb_kept_docs:,} fineweb_rejected={fineweb_rejected_docs:,} "
                    f"train_tokens={counters['train_tokens']:,}",
                    flush=True,
                )

    write_jsonl(args.accepted_samples, accepted_samples[: args.sample_limit])
    write_jsonl(args.rejected_samples, rejected_samples[: args.sample_limit])
    write_jsonl(args.final_samples, final_samples[: args.sample_limit])
    train_tokens = int(counters["train_tokens"])
    val_tokens = int(counters["val_tokens"])
    total_tokens = train_tokens + val_tokens
    source_mix = {source: dict(item) for source, item in counters["source_mix"].items()}
    wiki_tokens = source_mix.get("wikipedia_pl", {}).get("tokens", 0)
    fineweb_tokens = source_mix.get("fineweb2_pl", {}).get("tokens", 0)
    wikipedia_share = wiki_tokens / max(total_tokens, 1)
    fineweb_share = fineweb_tokens / max(total_tokens, 1)
    v2_3_total = int(v2_3_stats.get("total_tokens") or 0)
    v2_3_fineweb = int((v2_3_stats.get("source_mix") or {}).get("fineweb2_pl", {}).get("tokens") or 0)
    stage3_epochs = TRAINING_TOKENS_50K / max(total_tokens, 1)

    if total_tokens >= 220_000_000 and stage3_epochs <= 3.8 and fineweb_share >= 0.35:
        decision_code = "A) v2.3.1 gotowy do stage 3 / 50k po osobnej zgodzie."
        recommendation = (
            "v2.3.1 removes a large amount of FineWeb web residue while keeping enough tokens for a practical 50k run. "
            "Inspect final random samples before approving training."
        )
    elif total_tokens >= 150_000_000:
        decision_code = "D) zrobić krótki preflight, nie 50k."
        recommendation = (
            "v2.3.1 is cleaner but now marginal for a full 50k run. Prefer a short preflight or more clean sources."
        )
    else:
        decision_code = "C) FineWeb2 jest za brudny i trzeba inne źródło."
        recommendation = "The stricter cleanup removed too much FineWeb2 to support stage 3."

    domain_audit_top = [
        classify_domain(domain, domain_docs[domain], domain_tokens[domain], domain_examples[domain])
        for domain, _ in domain_tokens.most_common(100)
    ]
    stats = {
        "generated_at": now_utc(),
        "dataset_name": "glyph100_dataset_v2_3_1",
        "selected_variant": "v2_3_cleanup_fineweb2_domain_page_quality",
        "variant": "glyph-100m",
        "scope": "cleanup of glyph100_dataset_v2_3; no training has been run on it",
        "tokenizer_path": str(args.tokenizer),
        "tokenizer_vocab_size": sp.vocab_size(),
        "train_bin": str(args.train_bin),
        "val_bin": str(args.val_bin),
        "metadata_path": str(args.metadata),
        "docs_jsonl": str(args.docs_jsonl),
        "train_docs": counters["train_docs"],
        "val_docs": counters["val_docs"],
        "train_tokens": train_tokens,
        "val_tokens": val_tokens,
        "total_tokens": total_tokens,
        "token_word_ratio": total_tokens / max(counters["total_words"], 1),
        "word_token_ratio": counters["total_words"] / max(total_tokens, 1),
        "source_mix": source_mix,
        "wikipedia_tokens": wiki_tokens,
        "fineweb2_tokens": fineweb_tokens,
        "wikipedia_share": wikipedia_share,
        "fineweb2_share": fineweb_share,
        "legacy_share": 0.0,
        "v2_3_fineweb_docs": fineweb_seen_docs,
        "v2_3_fineweb_tokens": fineweb_seen_tokens,
        "fineweb2_kept_docs": fineweb_kept_docs,
        "fineweb2_kept_tokens": fineweb_tokens,
        "fineweb2_rejected_docs": fineweb_rejected_docs,
        "fineweb2_rejected_tokens": fineweb_rejected_tokens,
        "tokens_removed_from_v2_3": max(0, v2_3_total - total_tokens),
        "rejection_reasons": dict(counters["rejection_reasons"].most_common(100)),
        "domain_audit_top": domain_audit_top,
        "doc_token_percentiles": {
            "p50": percentile(counters["token_lengths"], 0.50),
            "p75": percentile(counters["token_lengths"], 0.75),
            "p90": percentile(counters["token_lengths"], 0.90),
            "p95": percentile(counters["token_lengths"], 0.95),
            "p99": percentile(counters["token_lengths"], 0.99),
        },
        "comparison_v2_3": {
            "v2_3_total_tokens": v2_3_total,
            "v2_3_fineweb2_tokens": v2_3_fineweb,
            "v2_3_wikipedia_share": float(v2_3_stats.get("wikipedia_share") or 0),
            "v2_3_fineweb2_share": float(v2_3_stats.get("fineweb2_share") or 0),
            "v2_3_stage3_epochs": float(v2_3_stats.get("stage3_50k_epochs") or 0),
        },
        "stage3_50k_tokens": TRAINING_TOKENS_50K,
        "stage3_50k_epochs": stage3_epochs,
        "stage4_100k_epochs": TRAINING_TOKENS_100K / max(total_tokens, 1),
        "stage5_200k_epochs": TRAINING_TOKENS_200K / max(total_tokens, 1),
        "final_samples": final_samples,
        "decision_code": decision_code,
        "recommendation": recommendation,
        "elapsed_seconds": time.time() - start,
    }

    args.stats.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    args.report.write_text(render_report(stats), encoding="utf-8")
    args.domain_audit.write_text(render_domain_audit(stats), encoding="utf-8")
    args.metadata.write_text(
        json.dumps(
            {
                "variant": "glyph-100m",
                "dataset_name": "glyph100_dataset_v2_3_1",
                "selected_variant": stats["selected_variant"],
                "scope": stats["scope"],
                "train_bin": str(args.train_bin),
                "val_bin": str(args.val_bin),
                "docs_jsonl": str(args.docs_jsonl),
                "tokenizer": str(args.tokenizer),
                "vocab_size": sp.vocab_size(),
                "train_docs": counters["train_docs"],
                "val_docs": counters["val_docs"],
                "train_tokens": train_tokens,
                "val_tokens": val_tokens,
                "total_tokens": total_tokens,
                "source_mix": source_mix,
                "wikipedia_share": wikipedia_share,
                "fineweb2_share": fineweb_share,
                "legacy_share": 0.0,
                "stage3_50k_epochs": stage3_epochs,
                "created_at": stats["generated_at"],
                "stats_json": str(args.stats),
                "report": str(args.report),
                "split_note": (
                    "document-level stable source/doc hash split with at least one validation document per source; "
                    "v2.3.1 cleanup of FineWeb2 PL; no legacy source included"
                ),
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
                "dataset_name": "glyph100_dataset_v2_3_1",
                "total_tokens": total_tokens,
                "wikipedia_share": wikipedia_share,
                "fineweb2_share": fineweb_share,
                "stage3_50k_epochs": stage3_epochs,
                "fineweb2_rejected_tokens": fineweb_rejected_tokens,
                "decision": decision_code,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    main()
