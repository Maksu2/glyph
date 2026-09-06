#!/usr/bin/env python3
"""Generate a small Alpaca-style SFT seed dataset with Gemma 4."""
import argparse
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def completion(base_url: str, prompt: str, timeout: int, n_predict: int) -> str:
    req = urllib.request.Request(
        base_url.rstrip("/") + "/completion",
        data=json.dumps({
            "prompt": prompt,
            "n_predict": n_predict,
            "temperature": 0.55,
            "top_k": 40,
            "top_p": 0.9,
            "stream": False,
            "cache_prompt": False,
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8")).get("content", "").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Create Alpaca-style SFT JSONL with Gemma 4")
    parser.add_argument("--prompts", default="eval/prompts.jsonl")
    parser.add_argument("--out", default="data/sft/gemma4_seed.jsonl")
    parser.add_argument("--base-url", default="http://127.0.0.1:8182")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--n-predict", type=int, default=260)
    args = parser.parse_args()

    prompts = read_jsonl(Path(args.prompts))
    if args.limit > 0:
        prompts = prompts[: args.limit]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    created_at = datetime.now(timezone.utc).isoformat()
    with tmp.open("w", encoding="utf-8") as f:
        for item in prompts:
            answer = completion(args.base_url, item["prompt"], args.timeout, args.n_predict)
            row = {
                "instruction": item["prompt"],
                "input": "",
                "output": answer,
                "source": "gemma4",
                "prompt_id": item.get("id"),
                "category": item.get("category"),
                "created_at": created_at,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    tmp.replace(out)
    print(f"Wrote {len(prompts)} SFT examples to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
