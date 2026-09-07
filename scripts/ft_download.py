#!/usr/bin/env python3
"""v2.5/v2.5.1 stage 1: stream FinetextPL-Edu, split pdf/web, save raw JSONL.

Reconstructed 2026-09-07 after /tmp loss (reboot). Predicate VERIFIED from
data/raw/glyph100_v2_5 (edu_*.jsonl: min prediction exactly 4.0 in both files,
is_truncated always False, routing purely by dataset_source):
  accept = prediction >= --pred-min (4.0) and is_truncated is not True
  finepdfs -> edu_pdf.jsonl, fineweb2 -> edu_web.jsonl
Record schema kept as-is (text/prediction/dataset_source/id/file... url etc).
Tokens counter = len(text.split()) (whitespace estimate, as in v2_5 logs).

v2_5_1 use: --seen-ids points at v2_5 ids (skip already-downloaded docs, so the
stream fast-forwards past scanned rows and only NEW docs are written).
Stop: pdf raw tokens >= --pdf-token-target. 715M raw ~= 650M post-filter
(v2_5: 354.6M raw -> 322.6M post-tok, factor 0.91).

State file allows crash-resume within one run. Writes --done JSON at end:
{"exit": code, "pdf_docs": n, "web_docs": n, "scanned": n}.
"""
import argparse
import json
import sys
import time
from pathlib import Path

REPO = "FinetextPL/FinetextPL-Edu"
REVISION = "eefa4ea4aaea55d4267baf2411ca19ab9c532ade"  # revision serving v2_5 data


def write_done(path, exit_code, **kw):
    if not path:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    kw.update({"exit": exit_code})
    p.write_text(json.dumps(kw, ensure_ascii=False) + "\n", encoding="utf-8")


def load_ids(path):
    ids = set()
    if path and Path(path).exists():
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                ids.add(json.loads(line).get("id"))
            except Exception:
                ids.add(line)
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/raw/glyph100_v2_5_1")
    ap.add_argument("--split", default="train")
    ap.add_argument("--pred-min", type=float, default=4.0)
    ap.add_argument("--pdf-token-target", type=int, default=715_000_000)
    ap.add_argument("--seen-ids", default="",
                    help="JSONL (or id-per-line) with ids to skip, e.g. v2_5 state")
    ap.add_argument("--state", default="")
    ap.add_argument("--skip-web", action="store_true",
                    help="count/skip web docs but do not write them (v2_5_1: web complete)")
    ap.add_argument("--done", default="logs/v2_5_1/ft_download.done")
    ap.add_argument("--progress-every", type=int, default=500_000)
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    state_path = Path(a.state) if a.state else out / "download_state.json"
    pdf_path = out / "edu_pdf.jsonl"
    web_path = out / "edu_web.jsonl"

    seen = load_ids(a.seen_ids)
    counts = {"web": {"docs": 0, "tokens": 0}, "pdf": {"docs": 0, "tokens": 0}}
    scanned = 0
    if state_path.exists():
        try:
            st = json.loads(state_path.read_text(encoding="utf-8"))
            counts = st["counts"]
            scanned = st["scanned"]
            for i in st.get("seen", []):
                seen.add(i)
            print(f"RESUME: counts={counts} scanned={scanned} seen={len(seen)}", flush=True)
        except Exception as e:
            print(f"state unreadable, starting fresh: {e}", flush=True)
    own_seen = []

    from datasets import load_dataset
    ds = load_dataset(REPO, split=a.split, streaming=True, revision=REVISION)
    fp = open(pdf_path, "a", encoding="utf-8")
    fw = None if a.skip_web else open(web_path, "a", encoding="utf-8")
    t0 = time.time()
    exit_code = 0
    try:
        for row in ds:
            scanned += 1
            rid = row.get("id")
            if rid in seen:
                continue
            pred = row.get("prediction")
            if not isinstance(pred, (int, float)) or pred < a.pred_min:
                continue
            if row.get("is_truncated") is True:
                continue
            src = row.get("dataset_source")
            text = row.get("text") or ""
            if not text.strip():
                continue
            rec = {"id": rid, "dataset_source": src, "dump": row.get("dump"),
                   "duplicate_count": row.get("duplicate_count"),
                   "is_truncated": row.get("is_truncated"),
                   "minhash_cluster_size": row.get("minhash_cluster_size"),
                   "prediction": float(pred), "url": row.get("url"), "text": text}
            line = json.dumps(rec, ensure_ascii=False) + "\n"
            if src == "finepdfs":
                fp.write(line)
                counts["pdf"]["docs"] += 1
                counts["pdf"]["tokens"] += len(text.split())
                seen.add(rid)
                own_seen.append(rid)
            elif src == "fineweb2":
                if fw is not None:
                    fw.write(line)
                    counts["web"]["docs"] += 1
                    counts["web"]["tokens"] += len(text.split())
                seen.add(rid)
                own_seen.append(rid)
            else:
                continue
            if scanned % a.progress_every == 0:
                el = time.time() - t0
                print(f"scanned={scanned} web={counts['web']} pdf={counts['pdf']} "
                      f"elapsed={el:.0f}s", flush=True)
                state_path.write_text(json.dumps(
                    {"counts": counts, "scanned": scanned,
                     "seen": own_seen}, ensure_ascii=False), encoding="utf-8")
            if counts["pdf"]["tokens"] >= a.pdf_token_target:
                print(f"TARGET pdf tokens reached: {counts['pdf']}", flush=True)
                break
    except Exception:
        import traceback
        traceback.print_exc()
        exit_code = 1
    finally:
        fp.close()
        if fw is not None:
            fw.close()
        try:
            state_path.write_text(json.dumps(
                {"counts": counts, "scanned": scanned,
                 "seen": own_seen}, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"state save failed: {e}", flush=True)
    print(f"DONE web={counts['web']} pdf={counts['pdf']} scanned={scanned}", flush=True)
    write_done(a.done, exit_code, pdf_docs=counts["pdf"]["docs"],
               web_docs=counts["web"]["docs"], scanned=scanned)
    sys.stdout.flush()
    # datasets streaming teardown races at interpreter exit (GIL crash AFTER
    # all files/.done are written) -> bypass finalizers, keep .done exit code.
    import os
    os._exit(exit_code)
