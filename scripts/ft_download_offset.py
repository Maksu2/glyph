#!/usr/bin/env python3
"""v2.5/v2.5.1 stage 1 with crash-safe stream offset (NOT YET DEPLOYED).

Drop-in replacement for ft_download.py, written while the first run is still
in its silent 80M-row skip phase. Deploy ONLY after the running process exits:
the new process must start with the same --out/--seen-ids, it picks up
edu_pdf.jsonl (append) + download_state.json + stream_offset.json.

What changed vs ft_download.py (predicate, schema, outputs identical):
  1. stream_offset.json: absolute stream position (rows consumed from stream
     start, INCLUDING skip discards), saved every --offset-every rows in BOTH
     phases. ft_download.py saves position only in download_state.json, only
     on progress lines, never during skip -> every crash re-discards from 0.
  2. Resume reads the offset file first (validated), falls back to the
     state's `scanned`, falls back to 0. Logs which source was used.
  3. Skip phase logs progress every --skip-log-every discards, so a long
     resume is distinguishable from a hang.
  4. Offset writes are atomic (tmp + fsync + os.replace): kill -9 mid-write
     leaves the previous intact offset, never a torn file.

--offset-every default (100_000): one atomic write of a few bytes costs
~1ms; at ~2800 stream rows/s, 100k rows ~= 35s of streaming, so overhead is
~0.003% while crash rework is capped at <1 min of re-streaming (~180MB).
--skip-log-every default (1_000_000): a heartbeat line ~every 6 min.
"""
import argparse
import json
import os
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


def atomic_write_json(path, obj):
    """Crash-safe write: torn file impossible, worst case keeps old version."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def load_offset(path):
    """Returns (pos or None, reason). Never raises."""
    try:
        v = json.loads(Path(path).read_text(encoding="utf-8"))["pos"]
        if isinstance(v, int) and v >= 0:
            return v, "offset-file"
        return None, f"offset-file invalid value {v!r}"
    except FileNotFoundError:
        return None, "offset-file missing"
    except Exception as e:
        return None, f"offset-file unreadable: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/raw/glyph100_v2_5_1")
    ap.add_argument("--split", default="train")
    ap.add_argument("--pred-min", type=float, default=4.0)
    ap.add_argument("--pdf-token-target", type=int, default=715_000_000)
    ap.add_argument("--seen-ids", default="",
                    help="JSONL (or id-per-line) with ids to skip, e.g. v2_5 state")
    ap.add_argument("--state", default="")
    ap.add_argument("--offset-file", default="",
                    help="default: <out>/stream_offset.json")
    ap.add_argument("--offset-every", type=int, default=100_000,
                    help="save stream offset every N consumed rows (both phases)")
    ap.add_argument("--skip-log-every", type=int, default=1_000_000,
                    help="log skip progress every N discarded rows")
    ap.add_argument("--skip-web", action="store_true",
                    help="count/skip web docs but do not write them (v2_5_1: web complete)")
    ap.add_argument("--max-retries", type=int, default=50)
    ap.add_argument("--done", default="logs/v2_5_1/ft_download.done")
    ap.add_argument("--progress-every", type=int, default=500_000)
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    state_path = Path(a.state) if a.state else out / "download_state.json"
    off_path = Path(a.offset_file) if a.offset_file else out / "stream_offset.json"
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
    # Absolute stream position. Offset file wins (it is saved during skip too,
    # the state file is not); state `scanned` is the legacy fallback.
    pos, why = load_offset(off_path)
    if pos is None:
        pos = scanned
        print(f"offset: using state scanned={pos} ({why})", flush=True)
    else:
        print(f"offset: resuming at stream pos={pos} ({why})", flush=True)
    own_seen = []

    from datasets import load_dataset

    def process_row(row):
        rid = row.get("id")
        if rid in seen:
            return
        pred = row.get("prediction")
        if not isinstance(pred, (int, float)) or pred < a.pred_min:
            return
        if row.get("is_truncated") is True:
            return
        text = row.get("text") or ""
        if not text.strip():
            return
        if row.get("dataset_source") == "finepdfs":
            fp.write(json.dumps(
                {"id": rid, "dataset_source": row.get("dataset_source"),
                 "dump": row.get("dump"),
                 "duplicate_count": row.get("duplicate_count"),
                 "is_truncated": row.get("is_truncated"),
                 "minhash_cluster_size": row.get("minhash_cluster_size"),
                 "prediction": float(pred), "url": row.get("url"),
                 "text": text}, ensure_ascii=False) + "\n")
            counts["pdf"]["docs"] += 1
            counts["pdf"]["tokens"] += len(text.split())
            seen.add(rid)
            own_seen.append(rid)
        elif row.get("dataset_source") == "fineweb2":
            if fw is not None:
                fw.write(json.dumps(
                    {"id": rid, "dataset_source": row.get("dataset_source"),
                     "dump": row.get("dump"),
                     "duplicate_count": row.get("duplicate_count"),
                     "is_truncated": row.get("is_truncated"),
                     "minhash_cluster_size": row.get("minhash_cluster_size"),
                     "prediction": float(pred), "url": row.get("url"),
                     "text": text}, ensure_ascii=False) + "\n")
                counts["web"]["docs"] += 1
                counts["web"]["tokens"] += len(text.split())
            seen.add(rid)
            own_seen.append(rid)

    def save_state():
        try:
            state_path.write_text(json.dumps(
                {"counts": counts, "scanned": scanned,
                 "seen": own_seen}, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"state save failed: {e}", flush=True)

    def save_offset():
        try:
            atomic_write_json(off_path, {"pos": pos})
        except Exception as e:
            print(f"offset save failed: {e}", flush=True)

    fp = open(pdf_path, "a", encoding="utf-8")
    fw = None if a.skip_web else open(web_path, "a", encoding="utf-8")
    t0 = time.time()
    exit_code = 0
    # Retry loop: HF streaming drops transiently. Stream order is deterministic
    # (pinned revision+split), so resume = re-iterate and discard rows < pos.
    attempt = 0
    target_hit = False
    try:
        while not target_hit:
            skip_left = pos
            skip_total = pos
            skip_mark = 0
            rows_since_save = 0
            try:
                ds = load_dataset(REPO, split=a.split, streaming=True,
                                  revision=REVISION)
                for row in ds:
                    pos += 1
                    rows_since_save += 1
                    if skip_left > 0:
                        skip_left -= 1
                        done_skip = skip_total - skip_left
                        if done_skip - skip_mark >= a.skip_log_every:
                            skip_mark = done_skip
                            el = time.time() - t0
                            print(f"skip {done_skip}/{skip_total} "
                                  f"({100.0 * done_skip / skip_total:.1f}%) "
                                  f"elapsed={el:.0f}s", flush=True)
                    else:
                        scanned += 1
                        process_row(row)
                        if scanned % a.progress_every == 0:
                            el = time.time() - t0
                            print(f"scanned={scanned} web={counts['web']} "
                                  f"pdf={counts['pdf']} elapsed={el:.0f}s", flush=True)
                            save_state()
                    if rows_since_save >= a.offset_every:
                        rows_since_save = 0
                        save_offset()
                    if counts["pdf"]["tokens"] >= a.pdf_token_target:
                        print(f"TARGET pdf tokens reached: {counts['pdf']}",
                              flush=True)
                        target_hit = True
                        break
                else:
                    print("STREAM EXHAUSTED before target", flush=True)
                    break
            except Exception:
                import traceback
                traceback.print_exc()
                attempt += 1
                save_state()
                save_offset()
                if attempt > a.max_retries:
                    print(f"too many retries ({attempt}), giving up", flush=True)
                    exit_code = 1
                    break
                wait = min(60 * 2 ** min(attempt, 4), 600)
                print(f"-- attempt {attempt}/{a.max_retries}: retry in "
                      f"{wait}s (pos={pos} scanned={scanned}) --", flush=True)
                time.sleep(wait)
    finally:
        fp.close()
        if fw is not None:
            fw.close()
        save_state()
        save_offset()
    print(f"DONE web={counts['web']} pdf={counts['pdf']} scanned={scanned} pos={pos}", flush=True)
    write_done(a.done, exit_code, pdf_docs=counts["pdf"]["docs"],
               web_docs=counts["web"]["docs"], scanned=scanned)
    sys.stdout.flush()
    # datasets streaming teardown races at interpreter exit (GIL crash AFTER
    # all files/.done are written) -> bypass finalizers, keep .done exit code.
    import os
    os._exit(exit_code)


if __name__ == "__main__":
    main()
