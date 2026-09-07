#!/usr/bin/env python3
"""v2.5/v2.5.1 stage 4: internal near-dedup of chunks via MinHash LSH.

Reconstructed 2026-09-07 after /tmp loss. VERIFIED from data/raw/glyph100_v2_5:
  - 128-dim signatures (mh_*_sigs.npy bytes / docs == 1024 == 128 x int64)
  - mh_*_ids.txt = kept chunk ids (one per line), mh_*_drop.txt = dropped ids
  - pdf: 63451 docs in, 60 dups; web: 349853 in, 268 dups
ASSUMPTIONS (exact v2_5 LSH cut unrecoverable): word 5-shingles, 128 perms,
16 bands x 8 rows (~Jaccard 0.8), file order keep-first-drop-later, union-find
over candidate pairs, drop all but lowest row index per component.
Stats keys VERIFIED (docs_in, tokens_in, dups, tokens_dropped,
candidate_pairs, unions, elapsed_s). Writes --done {exit, docs_in, dups}.
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

N_PERM = 128
BANDS, ROWS = 16, 8
PRIME = (1 << 61) - 1


def shingles(text, k=5):
    w = text.split()
    if len(w) < k:
        return {hashlib.sha1(text.encode()).hexdigest()}
    return {hashlib.sha1((" ".join(w[i:i + k])).encode()).hexdigest()
            for i in range(len(w) - k + 1)}


def compute_sigs(texts):
    rng = np.random.default_rng(12345)
    a = rng.integers(1, PRIME, size=N_PERM, dtype=np.uint64)
    b = rng.integers(0, PRIME, size=N_PERM, dtype=np.uint64)
    sigs = np.zeros((len(texts), N_PERM), dtype=np.int64)
    for i, t in enumerate(texts):
        h = np.array([int(s, 16) & 0xFFFFFFFFFFFFFFFF for s in shingles(t)],
                     dtype=np.uint64)
        m = np.minimum.reduce(
            [((ai * h + bi) % PRIME).astype(np.int64) for ai, bi in zip(a, b)])
        sigs[i] = m
    return sigs


def lsh_candidates(sigs):
    buckets = {}
    for i in range(sigs.shape[0]):
        for band in range(BANDS):
            key = (band, tuple(sigs[i, band * ROWS:(band + 1) * ROWS].tolist()))
            buckets.setdefault(key, []).append(i)
    pairs = set()
    for members in buckets.values():
        if len(members) > 1:
            members = sorted(members)
            for x in range(len(members)):
                for y in range(x + 1, len(members)):
                    pairs.add((members[x], members[y]))
    return pairs


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
    ap.add_argument("--ids-out", default="")
    ap.add_argument("--drop-out", default="")
    ap.add_argument("--sigs-out", default="")
    ap.add_argument("--stats-out", default="")
    ap.add_argument("--done", default="")
    a = ap.parse_args()

    base = Path(a.inp).parent if a.inp else Path("data/raw/glyph100_v2_5_1")
    inp = Path(a.inp) if a.inp else base / f"{a.src}_tok.jsonl"
    ids_out = Path(a.ids_out) if a.ids_out else base / f"mh_{a.src}_ids.txt"
    drop_out = Path(a.drop_out) if a.drop_out else base / f"mh_{a.src}_drop.txt"
    sigs_out = Path(a.sigs_out) if a.sigs_out else base / f"mh_{a.src}_sigs.npy"
    stats_out = Path(a.stats_out) if a.stats_out else base / f"mh_{a.src}_mhstats.json"

    print(f"sigs for {a.src}...", flush=True)
    t0 = time.time()
    exit_code = 0
    try:
        ids, toks, texts = [], [], []
        for line in open(inp, encoding="utf-8"):
            r = json.loads(line)
            ids.append(r["id"])
            toks.append(r["token_count"])
            texts.append(r["text"])
        sigs = compute_sigs(texts)
        t1 = time.time()
        print(f"sigs done {t1-t0:.0f}s, LSH...", flush=True)
        pairs = lsh_candidates(sigs)
        parent = list(range(len(ids)))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[max(rx, ry)] = min(rx, ry)
                return True
            return False

        unions = sum(1 for x, y in pairs if union(x, y))
        comp = {}
        for i in range(len(ids)):
            comp.setdefault(find(i), []).append(i)
        drop = set()
        for members in comp.values():
            if len(members) > 1:
                for m in sorted(members)[1:]:
                    drop.add(m)
        tokens_dropped = sum(toks[i] for i in drop)
        with open(ids_out, "w", encoding="utf-8") as f:
            for i, cid in enumerate(ids):
                if i not in drop:
                    f.write(cid + "\n")
        with open(drop_out, "w", encoding="utf-8") as f:
            for i in sorted(drop):
                f.write(ids[i] + "\n")
        np.save(sigs_out, sigs)
        stats = {"docs_in": len(ids), "tokens_in": sum(toks), "dups": len(drop),
                 "tokens_dropped": tokens_dropped, "candidate_pairs": len(pairs),
                 "unions": unions, "elapsed_s": round(time.time() - t0, 1)}
    except Exception:
        import traceback
        traceback.print_exc()
        exit_code = 1
        stats = {"error": "failed"}
    stats_out.write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"DONE {json.dumps(stats, ensure_ascii=False)}", flush=True)
    write_done(a.done, exit_code, docs_in=stats.get("docs_in", 0),
               dups=stats.get("dups", 0))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
