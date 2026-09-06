#!/usr/bin/env python3
"""
Download Polish text corpora:
  1. Polish Wikipedia (via HuggingFace datasets)
  2. OpenSubtitles PL (via HuggingFace datasets)
  3. Wolne Lektury (via their public API)

Output: data/raw/corpus.txt — one document per line.
"""
import os
import re
import sys
import time
import json
import logging
import argparse
from pathlib import Path

import requests
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)
CORPUS_PATH = RAW_DIR / "corpus.txt"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_line(text: str) -> str:
    """Basic inline cleaning before writing to corpus."""
    text = re.sub(r"<[^>]+>", " ", text)          # strip HTML tags
    text = re.sub(r"\s+", " ", text).strip()       # normalize whitespace
    return text


def write_docs(fout, docs, source_name: str):
    """Write cleaned documents (strings) to output file, one per line."""
    written = 0
    for doc in docs:
        doc = clean_line(doc)
        if len(doc.split()) >= 5:                  # skip very short lines
            fout.write(doc + "\n")
            written += 1
    log.info(f"  {source_name}: wrote {written:,} documents")
    return written


# ---------------------------------------------------------------------------
# 1. Polish Wikipedia
# ---------------------------------------------------------------------------

def download_wikipedia(fout):
    log.info("=== Polish Wikipedia ===")
    try:
        from datasets import load_dataset
    except ImportError:
        log.error("datasets not installed: pip install datasets")
        return 0

    try:
        log.info("Loading wikimedia/wikipedia 20231101.pl ...")
        ds = load_dataset(
            "wikimedia/wikipedia",
            "20231101.pl",
            split="train",
            trust_remote_code=False,
        )
        log.info(f"  Downloaded {len(ds):,} Wikipedia articles")

        def gen():
            for item in ds:
                text = item.get("text", "")
                if text:
                    # Replace section markers with spaces
                    text = re.sub(r"\n+", " ", text)
                    yield text

        return write_docs(fout, tqdm(gen(), total=len(ds), desc="Wikipedia"), "Wikipedia")

    except Exception as e:
        log.error(f"Wikipedia download failed: {e}")
        return 0


# ---------------------------------------------------------------------------
# 2. mC4 Polish (replaces OpenSubtitles which uses deprecated loading scripts)
# ---------------------------------------------------------------------------

def download_opensubtitles(fout):
    """
    Downloads Polish web text from mC4 (multilingual C4 / Common Crawl).
    mC4 is Parquet-based, no loading scripts, large and diverse.
    Falls back to Oscar or tatoeba if mC4 is unavailable.
    """
    log.info("=== mC4 Polish (web text corpus) ===")
    try:
        from datasets import load_dataset
    except ImportError:
        log.error("datasets not installed")
        return 0

    # --- mC4 Polish (primary) ---
    try:
        log.info("Loading allenai/c4 'pl' (mC4 Polish) ...")
        # Stream to avoid downloading everything at once; take 5M examples
        ds = load_dataset(
            "allenai/c4",
            "pl",
            split="train",
            streaming=True,
            trust_remote_code=False,
        )
        MAX_DOCS = 5_000_000

        def gen():
            for i, item in enumerate(ds):
                if i >= MAX_DOCS:
                    break
                text = item.get("text", "")
                if text:
                    # Split on double newlines to get paragraphs
                    for para in text.split("\n\n"):
                        para = para.strip()
                        if para:
                            yield para

        return write_docs(fout, tqdm(gen(), total=MAX_DOCS, desc="mC4-PL"), "mC4 Polish")

    except Exception as e:
        log.warning(f"  allenai/c4 'pl' failed: {e}")

    # --- OSCAR Polish (fallback) ---
    try:
        log.info("Trying oscar-corpus/OSCAR-2301 'pl' as fallback ...")
        ds = load_dataset(
            "oscar-corpus/OSCAR-2301",
            "pl",
            split="train",
            streaming=True,
            trust_remote_code=False,
        )
        MAX_DOCS = 2_000_000

        def gen():
            for i, item in enumerate(ds):
                if i >= MAX_DOCS:
                    break
                text = item.get("content", item.get("text", ""))
                if text:
                    yield text

        return write_docs(fout, tqdm(gen(), total=MAX_DOCS, desc="OSCAR-PL"), "OSCAR Polish")

    except Exception as e:
        log.warning(f"  OSCAR fallback failed: {e}")

    log.warning("mC4/OSCAR: all variants failed, skipping web text corpus")
    return 0


# ---------------------------------------------------------------------------
# 3. Wolne Lektury
# ---------------------------------------------------------------------------

WL_API = "https://wolnelektury.pl/api"
WL_CACHE = RAW_DIR / "wolnelektury_cache.json"


def wl_get_json(url: str, retries=3, delay=1.5) -> dict | list | None:
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
            else:
                log.warning(f"  WL request failed ({url}): {e}")
    return None


def wl_get_book_list() -> list[dict]:
    """Fetch all book metadata from Wolne Lektury API (paginated)."""
    if WL_CACHE.exists():
        log.info("  Using cached book list")
        with open(WL_CACHE) as f:
            return json.load(f)

    books = []
    url = f"{WL_API}/books/?format=json"
    log.info("  Fetching book list from Wolne Lektury API ...")
    while url:
        data = wl_get_json(url)
        if data is None:
            break
        if isinstance(data, list):
            books.extend(data)
            break
        results = data.get("results", data if isinstance(data, list) else [])
        books.extend(results)
        url = data.get("next")
        time.sleep(0.3)

    log.info(f"  Found {len(books):,} books")
    with open(WL_CACHE, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False)
    return books


def wl_get_book_text(book: dict) -> str | None:
    """Download plain text of a single book."""
    slug = book.get("slug") or book.get("href", "").rstrip("/").split("/")[-1]
    if not slug:
        return None

    # Direct media URL — fastest, no extra API call needed
    url = f"https://wolnelektury.pl/media/book/txt/{slug}.txt"
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            return r.text
    except requests.RequestException:
        pass

    # Fallback: fetch book detail page to get txt URL
    detail_url = f"{WL_API}/books/{slug}/"
    data = wl_get_json(detail_url)
    if data:
        txt_url = data.get("txt") or data.get("simple_txt")
        if txt_url:
            try:
                r = requests.get(txt_url, timeout=60)
                if r.status_code == 200:
                    return r.text
            except requests.RequestException:
                pass

    return None


def download_wolnelektury(fout):
    log.info("=== Wolne Lektury ===")
    books = wl_get_book_list()
    if not books:
        log.warning("  Could not fetch book list, skipping")
        return 0

    written = 0
    failed = 0
    for book in tqdm(books, desc="Wolne Lektury"):
        text = wl_get_book_text(book)
        if text:
            # Split book into paragraphs, filter short ones
            paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
            for para in paragraphs:
                para = clean_line(para)
                if len(para.split()) >= 5:
                    fout.write(para + "\n")
                    written += 1
        else:
            failed += 1
        time.sleep(0.2)  # polite rate limiting

    log.info(f"  Wolne Lektury: wrote {written:,} paragraphs ({failed} books failed)")
    return written


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Download Polish text corpora")
    parser.add_argument("--skip-wiki", action="store_true", help="Skip Wikipedia download")
    parser.add_argument("--skip-subtitles", action="store_true", help="Skip OpenSubtitles download")
    parser.add_argument("--skip-lektury", action="store_true", help="Skip Wolne Lektury download")
    parser.add_argument("--append", action="store_true", help="Append to existing corpus instead of overwriting")
    args = parser.parse_args()

    mode = "a" if args.append else "w"
    total = 0

    log.info(f"Writing corpus to {CORPUS_PATH}")
    with open(CORPUS_PATH, mode, encoding="utf-8") as fout:
        if not args.skip_wiki:
            total += download_wikipedia(fout)
            fout.flush()

        if not args.skip_subtitles:
            total += download_opensubtitles(fout)
            fout.flush()

        if not args.skip_lektury:
            total += download_wolnelektury(fout)
            fout.flush()

    log.info(f"Done. Total documents written: {total:,}")
    log.info(f"Corpus saved to: {CORPUS_PATH}")
    size_mb = CORPUS_PATH.stat().st_size / 1024 / 1024
    log.info(f"Corpus size: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
