#!/usr/bin/env python3
"""v2.5/v2.5.1 stage 3: tokenize kept docs -> 8192-token chunks with train/val.

Reconstructed 2026-09-07 after /tmp loss. Parameters VERIFIED from
data/raw/glyph100_v2_5 (pdf_tok.jsonl: 44713 docs -> 63451 chunks, max chunk
9585 tokens, split per-DOC zero mixed, val ~0.53% tokens; web same):
  - tokenizer data/processed/tokenizer.model (sentencepiece), EOS id appended
    to EVERY chunk, token_count includes EOS
  - text whitespace-collapsed, greedy sentence packing to >=8192 then cut
    (one sentence overflow allowed -> chunks may exceed 8192)
  - split per parent doc: docs ordered by sha1(id), prefix up to 0.55% of
    source tokens -> val (ASSUMPTION: reproduces observed ~0.53% token share)
Chunk schema VERIFIED (keys: chunk,id,ids,n_chunks,parent_doc_id,prediction,
source,split,text,token_count; id = parent#chunk-NNNN).
Writes --stats JSON (keys as tok_stats_{pdf,web}.json) and --done.
"""
import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHUNK = 8192
VAL_TOKEN_SHARE = 0.0055
RE_SENT = re.compile(r"(?<=[.!?…])\s+")
RE_WS = re.compile(r"\s+")


def write_done(path, exit_code, **kw):
    if not path:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    kw.update({"exit": exit_code})
    p.write_text(json.dumps(kw, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="pdf | web")
    ap.add_argument("--in", dest="inp", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--stats", default="")
    ap.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    ap.add_argument("--done", default="")
    a = ap.parse_args()

    import sentencepiece as spm
    sp = spm.SentencePieceProcessor()
    sp.load(str(ROOT / a.tokenizer))
    eos = sp.eos_id()

    inp = Path(a.inp) if a.inp else ROOT / "data" / "raw" / "glyph100_v2_5_1" / f"{a.src}_kept.jsonl"
    out = Path(a.out) if a.out else inp.parent / f"{a.src}_tok.jsonl"
    stats_p = Path(a.stats) if a.stats else inp.parent / f"tok_stats_{a.src}.json"

    docs = [json.loads(l) for l in open(inp, encoding="utf-8")]
    order = sorted(range(len(docs)),
                   key=lambda i: hashlib.sha1(str(docs[i].get("id")).encode()).hexdigest())
    total_est = sum(len(RE_WS.split(d.get("text") or "")) for d in docs)
    val_budget = total_est * VAL_TOKEN_SHARE
    is_val = set()
    acc = 0
    for i in order:
        if acc >= val_budget:
            break
        is_val.add(i)
        acc += len(RE_WS.split(docs[i].get("text") or ""))

    t0 = time.time()
    n_chunks = 0
    tokens = 0
    split_tokens = {"train": 0, "val": 0}
    exit_code = 0
    try:
        with open(out, "w", encoding="utf-8") as fout:
            for di, d in enumerate(docs):
                text = RE_WS.sub(" ", d.get("text") or "").strip()
                if not text:
                    continue
                split = "val" if di in is_val else "train"
                sents = RE_SENT.split(text)
                cur, cur_n = [], 0
                pieces = []
                for s in sents:
                    ids = sp.encode(s, out_type=int)
                    if cur and cur_n + len(ids) > CHUNK:
                        pieces.append(" ".join(cur))
                        cur, cur_n = [], 0
                    cur.append(s)
                    cur_n += len(ids)
                if cur:
                    pieces.append(" ".join(cur))
                n_c = len(pieces)
                for ci, piece in enumerate(pieces):
                    ids = sp.encode(piece, out_type=int)
                    ids.append(eos)
                    tc = len(ids)
                    n_chunks += 1
                    tokens += tc
                    split_tokens[split] += tc
                    fout.write(json.dumps({
                        "id": f"{d.get('id')}#chunk-{ci:04d}",
                        "parent_doc_id": d.get("id"), "chunk": ci, "n_chunks": n_c,
                        "source": d.get("source"), "prediction": d.get("prediction"),
                        "split": split, "text": piece, "token_count": tc,
                        "ids": ids}, ensure_ascii=False) + "\n")
                if (di + 1) % 50000 == 0:
                    print(f"{a.src}: {(di+1)}/{len(docs)} chunks={n_chunks} tok={tokens} "
                          f"elapsed={time.time()-t0:.0f}s", flush=True)
    except Exception:
        import traceback
        traceback.print_exc()
        exit_code = 1
    stats = {"src": a.src, "docs_in": len(docs), "chunks": n_chunks, "tokens": tokens,
             "split_tokens": split_tokens, "elapsed_s": round(time.time() - t0, 1)}
    stats_p.write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"DONE {a.src}: {json.dumps(stats, ensure_ascii=False)}", flush=True)
    write_done(a.done, exit_code, docs_in=len(docs), chunks=n_chunks)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
