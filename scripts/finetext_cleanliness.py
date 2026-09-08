#!/usr/bin/env python3
"""Phase 2: cleanliness metrics for pilot docs with prediction>=4.

Reads data/raw/finetext_pilot/pilot_*.jsonl, writes
reports/finetext_cleanliness.json. No .bin, no training, no downloads.
"""
import json
import re
import unicodedata
from collections import Counter
from urllib.parse import urlparse

import numpy as np

PILOT = "/home/maksu/ai-model/data/raw/finetext_pilot"
OUT = "/home/maksu/ai-model/reports/finetext_cleanliness.json"

ENDMARK = set(".!?…")
PUNCT_OK = set(".,;:!?-–—()\"'„”‘’…%/+=*<>@#&_^~|$\\[]{}")
PL = set("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")
RE_SLAJD = re.compile(r"slajd\s*\d", re.IGNORECASE)
RE_STRONA = re.compile(r"strona\s*\d+\s*z\s*\d+", re.IGNORECASE)
RE_NUMLINE = re.compile(r"^\d+$")
RE_DOTS = re.compile(r"\.{3,}|…{2,}")
RE_SP3 = re.compile(r" {3,}")


def metrics(text):
    text = text or ""
    lines = text.split("\n")
    n_lines = max(len(lines), 1)
    short = sum(1 for l in lines if len(l.strip()) < 40)
    noend = sum(1 for l in lines
                if l.strip() and l.strip()[-1] not in ENDMARK)
    numline = sum(1 for l in lines if RE_NUMLINE.match(l.strip()))
    n_chars = max(len(text), 1)
    weird = sum(1 for c in text
                if not (c.isalnum() or c.isspace() or c in PUNCT_OK))
    nonlatin = sum(1 for c in text
                   if c.isalpha() and not ("a" <= c.lower() <= "z"
                                           or c in PL))
    runs = re.findall(r"\S+", text)
    longest = max((len(r) for r in runs), default=0)
    return {
        "short_line_share": short / n_lines,
        "noend_share": noend / n_lines,
        "numline_share": numline / n_lines,
        "weird_share": weird / n_chars,
        "nonlatin_share": nonlatin / n_chars,
        "slajd": len(RE_SLAJD.findall(text)),
        "strona": len(RE_STRONA.findall(text)),
        "dots": len(RE_DOTS.findall(text)),
        "sp3": len(RE_SP3.findall(text)),
        "longest_nospace": longest,
        "n_chars": len(text),
    }


def domain_of(url):
    try:
        return urlparse(url or "").netloc.lower()
    except Exception:
        return ""


docs = []
for src in ("fineweb2", "finepdfs"):
    with open(f"{PILOT}/pilot_{src}.jsonl", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d["prediction"] >= 4.0:
                m = metrics(d.get("text") or "")
                m["tokens_est"] = None
                docs.append((src, d, m))
print(f"n={len(docs)}", flush=True)

# token counts via sentencepiece (for token-loss accounting)
import sentencepiece as spm
sp = spm.SentencePieceProcessor(
    model_file="/home/maksu/ai-model/data/processed/tokenizer.model")
for _, d, m in docs:
    m["tokens_est"] = len(sp.encode(str(d.get("text") or ""), out_type=int))
print("tokenized", flush=True)


def group_of(src, d):
    if src == "fineweb2":
        dom = domain_of(d.get("url"))
        if dom == "docplayer.pl":
            return "docplayer.pl"
        if dom == "slideplayer.pl":
            return "slideplayer.pl"
        return "web-rest"
    return ("pdf-trunc" if d.get("is_truncated") else "pdf-ok")


KEYS = ["short_line_share", "noend_share", "numline_share", "weird_share",
        "nonlatin_share", "slajd", "strona", "dots", "sp3",
        "longest_nospace"]
groups = {}
for src, d, m in docs:
    groups.setdefault(group_of(src, d), []).append((src, d, m))

dist = {}
for g, items in groups.items():
    arr = {k: np.array([m[k] for _, _, m in items]) for k in KEYS}
    dist[g] = {
        "n": len(items),
        "tok": int(sum(m["tokens_est"] for _, _, m in items)),
        "mean": {k: float(arr[k].mean()) for k in KEYS},
        "p50": {k: float(np.percentile(arr[k], 50)) for k in KEYS},
        "p90": {k: float(np.percentile(arr[k], 90)) for k in KEYS},
    }
    print(f"--- {g}: n={len(items)}")
    for k in KEYS:
        print(f"  {k}: mean={dist[g]['mean'][k]:.4f} "
              f"p50={dist[g]['p50'][k]:.4f} p90={dist[g]['p90'][k]:.4f}")

report = {"dist": dist, "docs": []}
for src, d, m in docs:
    report["docs"].append({
        "id": d.get("id"), "source": src, "group": group_of(src, d),
        "prediction": d["prediction"], "url": d.get("url"),
        "truncated": bool(d.get("is_truncated")),
        "tokens_est": m["tokens_est"], "metrics": {k: m[k] for k in KEYS},
    })
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False)
print(f"wrote {OUT}", flush=True)
