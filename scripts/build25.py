#!/usr/bin/env python3
"""v2.5/v2.5.1 final stage: merge kept chunks + v2.4.2 -> corpus docs + reports.

Reconstructed 2026-09-07 after /tmp loss. VERIFIED from data/raw/glyph100_v2_5
(build25.log) and data/reports/glyph100_dataset_v2_5_stats.json:
  - inputs: post-dedup pdf/web chunks (drops: mh_*_drop.txt, *_xdrop.txt,
    wp_drop.txt) + v2.4.2 docs in full (retokenized, counts must match)
  - v2_5 out: 571634 docs, train 1309237542 / val 7240792 tokens
  - spot-check chunk re-encode + full v242 re-encode count match
v2_5_1 differences (task): --web-token-target 450M subsample of web docs by
(prediction desc, doc-tokens desc); --dataset-name glyph100_v2_5_1;
per-source val files; windows file with --n-windows (default 20) NEW random
windows (seeded); report = same stats shape + per-source EOS density
(eos_1_per_n_train_tokens, already standard in v2_5).
docs.jsonl schema VERIFIED: dataset,id,parent_doc_id,source,split,text,
token_count (no ids list). Writes --done {exit, docs, total_tokens}.
"""
import argparse
import hashlib
import json
import random
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENIZER = "data/processed/tokenizer.model"


def sha256_file(p):
    import hashlib as hl
    h = hl.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def write_done(path, exit_code, **kw):
    if not path:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    kw.update({"exit": exit_code})
    p.write_text(json.dumps(kw, ensure_ascii=False) + "\n", encoding="utf-8")


def load_ids(p):
    p = Path(p)
    if not p.exists():
        return set()
    return set(l.strip() for l in p.read_text(encoding="utf-8").splitlines() if l.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="data/raw/glyph100_v2_5_1")
    ap.add_argument("--v242-docs", default="data/raw/glyph100_v2_4_2/glyph100_v2_4_2_docs.jsonl")
    ap.add_argument("--dataset-name", default="glyph100_v2_5_1")
    ap.add_argument("--web-token-target", type=int, default=450_000_000,
                    help="0 = keep all web docs (v2_5 behavior)")
    ap.add_argument("--n-windows", type=int, default=20)
    ap.add_argument("--seed", type=int, default=251)
    ap.add_argument("--done", default="")
    a = ap.parse_args()
    base = Path(a.base)

    t0 = time.time()
    exit_code = 0
    try:
        import sentencepiece as spm
        sp = spm.SentencePieceProcessor()
        tok_path = ROOT / TOKENIZER
        sp.load(str(tok_path))
        eos = sp.eos_id()

        rows = []  # (source, split, text, tokens, parent)
        # --- new finetext chunks after all drops ---
        for src, extra in (("finetext_pdf", ["mh_pdf_drop.txt", "pdf_xdrop.txt",
                                             "wp_drop.txt"]),
                           ("finetext_web", ["mh_web_drop.txt", "web_xdrop.txt"])):
            drop = set()
            for n in extra:
                drop |= load_ids(base / n)
            per_doc = defaultdict(list)
            order = []
            for line in open(base / (src.split("_")[1] + "_tok.jsonl"), encoding="utf-8"):
                r = json.loads(line)
                if r["id"] in drop:
                    continue
                if r["parent_doc_id"] not in per_doc:
                    order.append(r["parent_doc_id"])
                per_doc[r["parent_doc_id"]].append(r)
            if src == "finetext_web" and a.web_token_target > 0:
                scored = []
                for pid in order:
                    ch = per_doc[pid]
                    dt = sum(c["token_count"] for c in ch)
                    scored.append((-(ch[0].get("prediction") or 0), -dt, pid))
                scored.sort()
                keep_docs, acc = set(), 0
                for _, neg_dt, pid in scored:
                    keep_docs.add(pid)
                    acc += -neg_dt
                    if acc >= a.web_token_target:
                        break
                print(f"web subsample: {len(keep_docs)}/{len(order)} docs, "
                      f"{acc} tokens", flush=True)
            else:
                keep_docs = set(order)
            for pid in order:
                if pid not in keep_docs:
                    continue
                for c in per_doc[pid]:
                    rows.append((src, c["split"], c["text"], c["token_count"], pid))
            print(f"{src}: {len(keep_docs)} docs kept", flush=True)

        # --- v2.4.2 in full, re-encoded, counts must match ---
        n_v242 = 0
        for line in open(a.v242_docs, encoding="utf-8"):
            r = json.loads(line)
            ids = sp.encode(r.get("text") or "", out_type=int)
            ids.append(eos)
            assert len(ids) == r["token_count"], (r.get("id"), len(ids), r["token_count"])
            rows.append((r.get("source", "v242"), r.get("split", "train"),
                         r["text"], r["token_count"], r.get("parent_doc_id", r.get("id"))))
            n_v242 += 1
        print(f"v242 retokenized {n_v242}, all counts match", flush=True)

        # --- spot-check new chunks re-encode ---
        rng = random.Random(a.seed)
        sample = rng.sample([x for x in rows if x[0].startswith("finetext")],
                            min(3523, len(rows)))
        for src, split, text, tc, pid in sample:
            ids = sp.encode(text, out_type=int)
            ids.append(eos)
            assert len(ids) == tc, (src, len(ids), tc)
        print(f"re-encode spot-check {len(sample)} chunks OK", flush=True)

        # --- write docs.jsonl + per-source val files ---
        docs_p = base / f"{a.dataset_name}_docs.jsonl"
        val_handles = {}
        stats_src = defaultdict(lambda: {"tokens": 0, "train_tokens": 0, "val_tokens": 0,
                                         "docs": 0, "train_docs": 0, "val_docs": 0,
                                         "chars": 0})
        train_tok = val_tok = 0
        with open(docs_p, "w", encoding="utf-8") as fout:
            for i, (src, split, text, tc, pid) in enumerate(rows):
                fout.write(json.dumps({
                    "dataset": a.dataset_name,
                    "id": f"{a.dataset_name}-{i:07d}",
                    "parent_doc_id": pid, "source": src, "split": split,
                    "text": text, "token_count": tc}, ensure_ascii=False) + "\n")
                s = stats_src[src]
                s["tokens"] += tc
                s["docs"] += 1
                s["chars"] += len(text)
                if split == "val":
                    s["val_tokens"] += tc
                    s["val_docs"] += 1
                    val_tok += tc
                    if src not in val_handles:
                        val_handles[src] = open(
                            base / f"val_{src}.jsonl", "w", encoding="utf-8")
                    val_handles[src].write(json.dumps({
                        "dataset": a.dataset_name,
                        "id": f"{a.dataset_name}-{i:07d}",
                        "parent_doc_id": pid, "source": src, "split": split,
                        "text": text, "token_count": tc}, ensure_ascii=False) + "\n")
                else:
                    s["train_tokens"] += tc
                    s["train_docs"] += 1
                    train_tok += tc
        for h in val_handles.values():
            h.close()
        total = train_tok + val_tok

        # --- stats report (same shape as v2_5 + eos density per source) ---
        sources = {}
        for src, s in stats_src.items():
            sources[src] = {
                "tokens": s["tokens"], "train_tokens": s["train_tokens"],
                "val_tokens": s["val_tokens"], "docs": s["docs"],
                "train_docs": s["train_docs"], "val_docs": s["val_docs"],
                "chars": s["chars"], "share": s["tokens"] / total,
                "fertility_chars_per_token": s["chars"] / max(s["tokens"], 1),
                "eos_1_per_n_train_tokens": (
                    s["train_tokens"] / max(s["train_docs"], 1)),
            }
        stats = {
            "dataset_name": a.dataset_name,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tokenizer": TOKENIZER, "tokenizer_sha256": sha256_file(tok_path),
            "eos_id": eos, "train_tokens": train_tok, "val_tokens": val_tok,
            "total_tokens": total, "total_docs": len(rows),
            "val_share": val_tok / max(total, 1),
            "eos_density_train": total and (train_tok / max(
                sum(s["train_docs"] for s in stats_src.values()), 1)) or 0,
            "sources": sources,
        }
        rep_dir = ROOT / "data" / "reports"
        rep_dir.mkdir(parents=True, exist_ok=True)
        (rep_dir / f"glyph100_dataset_{a.dataset_name}_stats.json").write_text(
            json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")

        # --- reading windows: same format as v2_5 (windows cut from the
        # train token stream: header with train_offset + ~2000 chars) ---
        train_rows = [(src, text, tc) for (src, split, text, tc, pid) in rows
                      if split == "train"]
        offsets = []
        acc = 0
        for src, text, tc in train_rows:
            offsets.append((acc, src, text))
            acc += tc
        rng = random.Random(a.seed + 1)
        picks = sorted(rng.sample(range(acc), min(a.n_windows, acc)))
        win_lines = []
        k = 0
        for j, off in enumerate(picks):
            while k + 1 < len(offsets) and offsets[k + 1][0] <= off:
                k += 1
            win_lines.append(f"===== window {j + 1:02d} train_offset={off} =====")
            win_lines.append(offsets[k][2][:2000])
            win_lines.append("")
        (rep_dir / f"glyph100_{a.dataset_name}_windows.txt").write_text(
            "\n".join(win_lines), encoding="utf-8")

        meta = dict(stats)
        meta["val_files"] = [f"val_{s}.jsonl" for s in stats_src]
        (ROOT / "data" / "processed" / f"{a.dataset_name}_metadata.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
        el = time.time() - t0
        print(f"BUILD DONE {json.dumps({'train': train_tok, 'val': val_tok, 'total': total, 'docs': len(rows), 'sec': round(el, 1)})}",
              flush=True)
    except Exception:
        import traceback
        traceback.print_exc()
        exit_code = 1
        train_tok = val_tok = total = 0
    write_done(a.done or f"logs/v2_5_1/build25.done", exit_code,
               docs=len(rows) if exit_code == 0 else 0, total_tokens=total)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
