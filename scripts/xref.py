#!/usr/bin/env python3
"""v2.5/v2.5.1 stage 5: cross-dedup of new chunks against v2.4.2 train AND val.

Reconstructed 2026-09-07 after /tmp loss. VERIFIED from data/raw/glyph100_v2_5:
  - ref built from v2.4.2 docs (train+val tracked separately); v2_5 ref files
    (v242ref_*) exist but their row format is unrecoverable -> this script
    rebuilds the ref from data/raw/glyph100_v2_4_2/glyph100_v2_4_2_docs.jsonl
    (keys used: text, split) into --ref-dir, reused when present
  - checks per chunk: exact sha1(text), norm sha1 (whitespace-collapsed lower),
    minhash (same 128-perm/word-5-shingle params as minhash.py) vs ref train
    and val; ANY hit drops the chunk
  - v2_5 observed hits: pdf 1 mh_vs_train; web 10 norm + 585 mh train, 2 mh val
Output keys VERIFIED (exact_vs_train/_val, norm_vs_train/_val, mh_vs_train/_val,
checked, dropped_chunks, dropped_tokens, elapsed_s) -> xref json; dropped chunk
ids -> xdrop.txt. Only chunks in --keep-ids (post-minhash) are checked.
Writes --done {exit, checked, dropped_chunks}.
"""
import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from minhash import compute_sigs, lsh_candidates  # noqa: E402

RE_WS = re.compile(r"\s+")


def norm(t):
    return RE_WS.sub(" ", (t or "").lower()).strip()


def sha1(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def write_done(path, exit_code, **kw):
    if not path:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    kw.update({"exit": exit_code})
    p.write_text(json.dumps(kw, ensure_ascii=False) + "\n", encoding="utf-8")


def load_ref(v242_docs, ref_dir):
    ref_dir = Path(ref_dir)
    meta_p = ref_dir / "v242ref_meta.json"
    sigs_p = ref_dir / "v242ref_sigs.npy"
    if meta_p.exists() and sigs_p.exists():
        print("ref ready (cached), loading...", flush=True)
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
        return meta, np.load(sigs_p)
    print("building v2.4.2 ref...", flush=True)
    texts, splits = [], []
    for line in open(v242_docs, encoding="utf-8"):
        r = json.loads(line)
        texts.append(r.get("text") or "")
        splits.append(r.get("split", "train"))
    sigs = compute_sigs(texts)
    meta = {"ids": list(range(len(texts))), "splits": splits,
            "exact_train": {}, "exact_val": {}, "norm_train": {}, "norm_val": {}}
    for i, (t, s) in enumerate(zip(texts, splits)):
        (meta["exact_train"] if s == "train" else meta["exact_val"]).setdefault(sha1(t), i)
        (meta["norm_train"] if s == "train" else meta["norm_val"]).setdefault(sha1(norm(t)), i)
    ref_dir.mkdir(parents=True, exist_ok=True)
    meta_p.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    np.save(sigs_p, sigs)
    print(f"ref ready, {len(texts)} docs", flush=True)
    return meta, sigs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="pdf | web")
    ap.add_argument("--in", dest="inp", default="")
    ap.add_argument("--keep-ids", default="")
    ap.add_argument("--v242-docs", default="data/raw/glyph100_v2_4_2/glyph100_v2_4_2_docs.jsonl")
    ap.add_argument("--ref-dir", default="")
    ap.add_argument("--drop-out", default="")
    ap.add_argument("--stats-out", default="")
    ap.add_argument("--done", default="")
    a = ap.parse_args()

    base = Path(a.inp).parent if a.inp else Path("data/raw/glyph100_v2_5_1")
    inp = Path(a.inp) if a.inp else base / f"{a.src}_tok.jsonl"
    keep_p = Path(a.keep_ids) if a.keep_ids else base / f"mh_{a.src}_ids.txt"
    ref_dir = Path(a.ref_dir) if a.ref_dir else base
    drop_out = Path(a.drop_out) if a.drop_out else base / f"{a.src}_xdrop.txt"
    stats_out = Path(a.stats_out) if a.stats_out else base / f"{a.src}_xref.json"

    t0 = time.time()
    exit_code = 0
    try:
        keep = set(l.strip() for l in open(keep_p, encoding="utf-8") if l.strip())
        meta, ref_sigs = load_ref(a.v242_docs, ref_dir)
        print(f"querying {a.src}...", flush=True)
        from collections import defaultdict
        buckets = defaultdict(list)
        for i in range(ref_sigs.shape[0]):
            for band in range(16):
                buckets[(band, tuple(ref_sigs[i, band * 8:(band + 1) * 8].tolist()))].append(i)
        st = {"exact_vs_train": 0, "exact_vs_val": 0, "norm_vs_train": 0,
              "norm_vs_val": 0, "mh_vs_train": 0, "mh_vs_val": 0,
              "checked": 0, "dropped_chunks": 0, "dropped_tokens": 0}
        dropped = []
        n = 0
        for line in open(inp, encoding="utf-8"):
            r = json.loads(line)
            if r["id"] not in keep:
                continue
            n += 1
            t = r.get("text") or ""
            hit = None
            if sha1(t) in meta["exact_train"]:
                hit = "exact_vs_train"
            elif sha1(t) in meta["exact_val"]:
                hit = "exact_vs_val"
            elif sha1(norm(t)) in meta["norm_train"]:
                hit = "norm_vs_train"
            elif sha1(norm(t)) in meta["norm_val"]:
                hit = "norm_vs_val"
            else:
                s = compute_sigs([t])[0]
                cand = set()
                for band in range(16):
                    cand.update(buckets.get(
                        (band, tuple(s[band * 8:(band + 1) * 8].tolist())), []))
                for ci in cand:
                    if np.mean(s == ref_sigs[ci]) >= 0.8:
                        hit = ("mh_vs_train" if meta["splits"][ci] == "train"
                               else "mh_vs_val")
                        break
            if hit:
                st[hit] += 1
                st["dropped_chunks"] += 1
                st["dropped_tokens"] += r["token_count"]
                dropped.append(r["id"])
            if n % 100000 == 0:
                print(f"{a.src}: {n} drops={st['dropped_chunks']} "
                      f"elapsed={time.time()-t0:.0f}s", flush=True)
        st["checked"] = n
        st["elapsed_s"] = round(time.time() - t0, 1)
        drop_out.write_text("\n".join(dropped) + ("\n" if dropped else ""),
                            encoding="utf-8")
    except Exception:
        import traceback
        traceback.print_exc()
        exit_code = 1
        st = {"error": "failed"}
    stats_out.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"DONE {a.src} xref: {json.dumps(st, ensure_ascii=False)}", flush=True)
    write_done(a.done, exit_code, checked=st.get("checked", 0),
               dropped_chunks=st.get("dropped_chunks", 0))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
