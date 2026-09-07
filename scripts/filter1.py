#!/usr/bin/env python3
"""v2.5/v2.5.1 stage 2: cleanliness filter over edu_{pdf,web}.jsonl.

Reconstructed 2026-09-07 after /tmp loss. Filter logic itself was NOT lost:
imports normalize()/reject_reasons() from scripts/finetext_filter_v25.py
(thresholds: noend_long>0.85, sp3>50, glue>200, weird>0.01, homoglyph>2,
numline>0.3, short>0.9; reject if ANY fires).
Verified output schema from data/raw/glyph100_v2_5/*_kept.jsonl:
  {dataset_source, dump, id, n_chars, prediction, source, text, url}
with source = finetext_pdf / finetext_web, text = normalized text.
Also verifies: kept+rejected == n_in. Writes --stats JSON (same keys as
filter_stats_{pdf,web}.json) and --done JSON {exit, n_in, n_kept}.
"""
import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
from finetext_filter_v25 import metrics_v2, normalize, reject_reasons  # noqa: E402


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
    ap.add_argument("--done", default="")
    a = ap.parse_args()
    assert a.src in ("pdf", "web"), a.src
    source = "finetext_pdf" if a.src == "pdf" else "finetext_web"

    inp = Path(a.inp) if a.inp else ROOT / "data" / "raw" / "glyph100_v2_5_1" / f"edu_{a.src}.jsonl"
    out = Path(a.out) if a.out else inp.parent / f"{a.src}_kept.jsonl"
    stats_p = Path(a.stats) if a.stats else inp.parent / f"filter_stats_{a.src}.json"

    with open(inp, encoding="utf-8") as f:
        n_in = sum(1 for _ in f)
    n_kept = n_rej = 0
    kept_chars = 0
    reason_hits = Counter()
    t0 = time.time()
    exit_code = 0
    try:
        with open(inp, encoding="utf-8") as fin, open(out, "w", encoding="utf-8") as fout:
            for i, line in enumerate(fin, 1):
                r = json.loads(line)
                text = normalize(r.get("text") or "")
                why = reject_reasons(metrics_v2(text))
                if why:
                    n_rej += 1
                    for w in why:
                        reason_hits[w] += 1
                else:
                    n_kept += 1
                    kept_chars += len(text)
                    fout.write(json.dumps({
                        "id": r.get("id"), "dataset_source": r.get("dataset_source"),
                        "dump": r.get("dump"), "prediction": r.get("prediction"),
                        "url": r.get("url"), "n_chars": len(text),
                        "source": source, "text": text}, ensure_ascii=False) + "\n")
                if i % 50000 == 0:
                    print(f"{a.src}: {i}/{n_in} kept={n_kept} rej={n_rej} "
                          f"elapsed={time.time()-t0:.0f}s", flush=True)
    except Exception:
        import traceback
        traceback.print_exc()
        exit_code = 1
    stats = {"src": a.src, "n_in": n_in, "n_kept": n_kept, "n_rejected": n_rej,
             "kept_chars": kept_chars, "reason_hits": dict(reason_hits),
             "elapsed_s": round(time.time() - t0, 1)}
    stats_p.write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"DONE {a.src}: {json.dumps(stats, ensure_ascii=False)}", flush=True)
    assert n_kept + n_rej == n_in, (n_kept, n_rej, n_in)
    write_done(a.done, exit_code, n_in=n_in, n_kept=n_kept)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
