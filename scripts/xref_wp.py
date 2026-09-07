#!/usr/bin/env python3
"""v2.5/v2.5.1 stage 5b: cross-dedup pdf chunks against kept web chunks (MinHash).

Reconstructed 2026-09-07 after /tmp loss. VERIFIED from data/raw/glyph100_v2_5:
  - wp_xref.json keys: pdf_checked, pdf_dropped, tokens_dropped, elapsed_s
  - v2_5 observed: 63451 pdf checked, 367 dropped, 1436071 tokens dropped
  - drops -> wp_drop.txt (pdf chunk ids also dropped at build)
Method: LSH (16 bands x 8 rows) over kept-web sigs, Jaccard >= 0.8 drops the
pdf chunk. Only post-minhash/post-xref survivors on both sides participate
(--web-keep/--web-drop and --pdf-keep/--pdf-drop id lists).
Writes --done {exit, pdf_checked, pdf_dropped}.
"""
import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from minhash import compute_sigs  # noqa: E402


def write_done(path, exit_code, **kw):
    if not path:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    kw.update({"exit": exit_code})
    p.write_text(json.dumps(kw, ensure_ascii=False) + "\n", encoding="utf-8")


def load_ids(p):
    return set(l.strip() for l in open(p, encoding="utf-8") if l.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="data/raw/glyph100_v2_5_1")
    ap.add_argument("--web-tok", default="")
    ap.add_argument("--pdf-tok", default="")
    ap.add_argument("--drop-out", default="")
    ap.add_argument("--stats-out", default="")
    ap.add_argument("--done", default="")
    a = ap.parse_args()
    base = Path(a.base)
    web_tok = Path(a.web_tok) if a.web_tok else base / "web_tok.jsonl"
    pdf_tok = Path(a.pdf_tok) if a.pdf_tok else base / "pdf_tok.jsonl"
    drop_out = Path(a.drop_out) if a.drop_out else base / "wp_drop.txt"
    stats_out = Path(a.stats_out) if a.stats_out else base / "wp_xref.json"

    t0 = time.time()
    exit_code = 0
    try:
        web_drop = load_ids(base / "mh_web_drop.txt") | load_ids(base / "web_xdrop.txt")
        web_texts = []
        for line in open(web_tok, encoding="utf-8"):
            r = json.loads(line)
            if r["id"] not in web_drop:
                web_texts.append(r["text"])
        print(f"web kept texts: {len(web_texts)}, sigs...", flush=True)
        wsigs = compute_sigs(web_texts)
        buckets = defaultdict(list)
        for i in range(wsigs.shape[0]):
            for band in range(16):
                buckets[(band, tuple(wsigs[i, band * 8:(band + 1) * 8].tolist()))].append(i)
        pdf_drop = (load_ids(base / "mh_pdf_drop.txt")
                    | load_ids(base / "pdf_xdrop.txt"))
        pdf_checked = pdf_dropped = tokens_dropped = 0
        dropped = []
        for line in open(pdf_tok, encoding="utf-8"):
            r = json.loads(line)
            if r["id"] in pdf_drop:
                continue
            pdf_checked += 1
            s = compute_sigs([r.get("text") or ""])[0]
            hit = False
            for band in range(16):
                for ci in buckets.get(
                        (band, tuple(s[band * 8:(band + 1) * 8].tolist())), []):
                    if float(np.mean(s == wsigs[ci])) >= 0.8:
                        hit = True
                        break
                if hit:
                    break
            if hit:
                pdf_dropped += 1
                tokens_dropped += r["token_count"]
                dropped.append(r["id"])
        drop_out.write_text("\n".join(dropped) + ("\n" if dropped else ""),
                            encoding="utf-8")
        st = {"pdf_checked": pdf_checked, "pdf_dropped": pdf_dropped,
              "tokens_dropped": tokens_dropped,
              "elapsed_s": round(time.time() - t0, 1)}
    except Exception:
        import traceback
        traceback.print_exc()
        exit_code = 1
        st = {"error": "failed"}
    stats_out.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"DONE wp: {json.dumps(st, ensure_ascii=False)}", flush=True)
    write_done(a.done, exit_code, pdf_checked=st.get("pdf_checked", 0),
               pdf_dropped=st.get("pdf_dropped", 0))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
