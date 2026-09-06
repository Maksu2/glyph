#!/usr/bin/env python3
"""
Preprocessing pipeline:
  1. Clean corpus.txt (remove HTML, short lines, normalize whitespace)
  2. Train SentencePiece BPE tokenizer (vocab_size=16000)
  3. Tokenize full corpus and save as tokens.bin (numpy uint16)
  4. Print statistics
"""
import os
import re
import sys
import logging
import argparse
import collections
import numpy as np
from pathlib import Path
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

CORPUS_PATH = RAW_DIR / "corpus.txt"
CLEAN_PATH = PROCESSED_DIR / "corpus_clean.txt"
TOKENIZER_PATH = PROCESSED_DIR / "tokenizer.model"
TOKENS_PATH = PROCESSED_DIR / "tokens.bin"

VOCAB_SIZE = 16000


# ---------------------------------------------------------------------------
# Step 1: Clean text
# ---------------------------------------------------------------------------

HTML_RE = re.compile(r"<[^>]+>")
URL_RE = re.compile(r"https?://\S+|www\.\S+")
MULTI_SPACE_RE = re.compile(r"[ \t]+")
MULTI_NEWLINE_RE = re.compile(r"\n{3,}")

# Characters to strip entirely
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean_text(line: str) -> str:
    line = HTML_RE.sub(" ", line)
    line = URL_RE.sub(" ", line)
    line = CONTROL_RE.sub("", line)
    line = MULTI_SPACE_RE.sub(" ", line)
    return line.strip()


def is_valid_line(line: str, min_words: int = 5) -> bool:
    words = line.split()
    if len(words) < min_words:
        return False
    # Skip lines that are mostly non-alphabetic (e.g. tables, code)
    alpha_chars = sum(c.isalpha() for c in line)
    if len(line) > 0 and alpha_chars / len(line) < 0.5:
        return False
    return True


def clean_corpus(input_path: Path, output_path: Path) -> int:
    log.info(f"Cleaning corpus: {input_path} -> {output_path}")
    written = 0
    skipped = 0

    with open(input_path, "r", encoding="utf-8", errors="replace") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:

        for raw_line in tqdm(fin, desc="Cleaning"):
            line = clean_text(raw_line)
            if is_valid_line(line):
                fout.write(line + "\n")
                written += 1
            else:
                skipped += 1

    log.info(f"  Kept {written:,} lines, skipped {skipped:,} lines")
    return written


# ---------------------------------------------------------------------------
# Step 2: Train SentencePiece tokenizer
# ---------------------------------------------------------------------------

def train_tokenizer(corpus_path: Path, model_prefix: str, vocab_size: int):
    log.info(f"Training SentencePiece BPE tokenizer (vocab_size={vocab_size}) ...")
    try:
        import sentencepiece as spm
    except ImportError:
        log.error("sentencepiece not installed: pip install sentencepiece")
        sys.exit(1)

    # Count lines to decide on input_sentence_size
    with open(corpus_path, "r", encoding="utf-8") as f:
        n_lines = sum(1 for _ in f)
    log.info(f"  Corpus has {n_lines:,} lines")

    # Use up to 5M sentences for training the tokenizer
    input_sentence_size = min(n_lines, 5_000_000)

    spm.SentencePieceTrainer.train(
        input=str(corpus_path),
        model_prefix=model_prefix,
        vocab_size=vocab_size,
        model_type="bpe",
        character_coverage=0.9995,     # high coverage for Polish chars
        pad_id=0,
        unk_id=1,
        bos_id=2,
        eos_id=3,
        pad_piece="<pad>",
        unk_piece="<unk>",
        bos_piece="<bos>",
        eos_piece="<eos>",
        user_defined_symbols=["<|user|>", "<|assistant|>", "<|end|>"],
        input_sentence_size=input_sentence_size,
        shuffle_input_sentence=True,
        num_threads=os.cpu_count(),
        train_extremely_large_corpus=(n_lines > 2_000_000),
    )
    log.info(f"  Tokenizer saved: {model_prefix}.model")


# ---------------------------------------------------------------------------
# Step 3: Tokenize corpus and save as binary
# ---------------------------------------------------------------------------

def tokenize_corpus(
    corpus_path: Path,
    tokenizer_path: Path,
    output_path: Path,
    chunk_size: int = 100_000,
) -> dict:
    log.info(f"Tokenizing corpus -> {output_path}")
    try:
        import sentencepiece as spm
    except ImportError:
        log.error("sentencepiece not installed")
        sys.exit(1)

    sp = spm.SentencePieceProcessor()
    sp.load(str(tokenizer_path))

    total_tokens = 0
    doc_lengths = []
    token_counts = collections.Counter()

    with open(corpus_path, "r", encoding="utf-8") as fin, \
         open(output_path, "wb") as fout:

        buffer = []
        buffer_tokens = 0

        for line in tqdm(fin, desc="Tokenizing"):
            line = line.rstrip("\n")
            if not line:
                continue

            ids = sp.encode(line, out_type=int)
            ids.append(sp.eos_id())  # separate documents with EOS

            doc_lengths.append(len(ids))
            buffer.extend(ids)
            buffer_tokens += len(ids)

            for tok_id in ids:
                token_counts[tok_id] += 1

            if buffer_tokens >= chunk_size:
                arr = np.array(buffer, dtype=np.uint16)
                fout.write(arr.tobytes())
                total_tokens += buffer_tokens
                buffer = []
                buffer_tokens = 0

        # flush remaining
        if buffer:
            arr = np.array(buffer, dtype=np.uint16)
            fout.write(arr.tobytes())
            total_tokens += buffer_tokens

    log.info(f"  Total tokens: {total_tokens:,}")
    log.info(f"  Unique tokens used: {len(token_counts):,} / {sp.vocab_size():,}")
    log.info(f"  Output size: {output_path.stat().st_size / 1024**2:.1f} MB")

    return {
        "total_tokens": total_tokens,
        "unique_tokens": len(token_counts),
        "n_docs": len(doc_lengths),
        "doc_lengths": doc_lengths,
        "token_counts": token_counts,
    }


# ---------------------------------------------------------------------------
# Step 4: Print statistics
# ---------------------------------------------------------------------------

def print_stats(stats: dict):
    doc_lengths = stats["doc_lengths"]
    if not doc_lengths:
        return

    lengths = np.array(doc_lengths)
    log.info("=== Corpus Statistics ===")
    log.info(f"  Documents: {stats['n_docs']:,}")
    log.info(f"  Total tokens: {stats['total_tokens']:,}")
    log.info(f"  Unique tokens: {stats['unique_tokens']:,}")
    log.info(f"  Doc length (tokens): min={lengths.min()} max={lengths.max()} "
             f"mean={lengths.mean():.1f} median={np.median(lengths):.1f}")

    percentiles = [10, 25, 50, 75, 90, 95, 99]
    pcts = np.percentile(lengths, percentiles)
    log.info("  Doc length percentiles:")
    for p, v in zip(percentiles, pcts):
        log.info(f"    p{p:2d}: {v:.0f} tokens")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Preprocess Polish text corpus")
    parser.add_argument("--skip-clean", action="store_true", help="Skip cleaning step (use existing clean corpus)")
    parser.add_argument("--skip-tokenizer", action="store_true", help="Skip tokenizer training (use existing model)")
    parser.add_argument("--vocab-size", type=int, default=VOCAB_SIZE)
    parser.add_argument("--corpus", type=str, default=str(CORPUS_PATH), help="Input corpus path")
    args = parser.parse_args()

    corpus_path = Path(args.corpus)
    if not corpus_path.exists():
        log.error(f"Corpus not found: {corpus_path}")
        log.error("Run: python data/download.py")
        sys.exit(1)

    # Step 1: Clean
    if args.skip_clean and CLEAN_PATH.exists():
        log.info(f"Skipping cleaning, using: {CLEAN_PATH}")
    else:
        clean_corpus(corpus_path, CLEAN_PATH)

    # Step 2: Train tokenizer
    model_prefix = str(PROCESSED_DIR / "tokenizer")
    if args.skip_tokenizer and TOKENIZER_PATH.exists():
        log.info(f"Skipping tokenizer training, using: {TOKENIZER_PATH}")
    else:
        train_tokenizer(CLEAN_PATH, model_prefix, args.vocab_size)

    if not TOKENIZER_PATH.exists():
        log.error(f"Tokenizer model not found at {TOKENIZER_PATH}")
        sys.exit(1)

    # Step 3: Tokenize
    stats = tokenize_corpus(CLEAN_PATH, TOKENIZER_PATH, TOKENS_PATH)

    # Step 4: Stats
    print_stats(stats)
    log.info(f"Tokenized corpus saved to: {TOKENS_PATH}")


if __name__ == "__main__":
    main()
