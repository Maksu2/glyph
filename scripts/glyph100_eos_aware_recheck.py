#!/usr/bin/env python3
"""Small GPU-friendly 44k vs 50k recheck with correct EOS accounting."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from eval_glyph100_stage2 import configure_attention_backend, generate_one, load_model, load_tokenizer, read_jsonl  # noqa: E402
from eval_glyph100_v231_broad import enrich_result, load_checkpoint_metadata  # noqa: E402


EXPECTED_TOKENIZER_SHA = "21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029"
CHECKPOINTS = {
    "44k": Path("checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt"),
    "50k": Path("checkpoints/glyph-100m-v2_3_1-50k/latest.pt"),
}
PRESETS = {
    "greedy_80": {
        "temperature": 0.0,
        "top_k": None,
        "top_p": 1.0,
        "repetition_penalty": 1.0,
        "max_new_tokens": 80,
    },
    "current_normal_80": {
        "temperature": 0.8,
        "top_k": 40,
        "top_p": 1.0,
        "repetition_penalty": 1.0,
        "max_new_tokens": 80,
    },
    "repetition_guard_80": {
        "temperature": 0.7,
        "top_k": 40,
        "top_p": 1.0,
        "repetition_penalty": 1.15,
        "max_new_tokens": 80,
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def summarize(rows: list[dict]) -> dict:
    return {
        "count": len(rows),
        "avg_quality_score": round(statistics.mean(row["quality_score"] for row in rows), 3),
        "median_quality_score": round(statistics.median(row["quality_score"] for row in rows), 3),
        "avg_actual_new_tokens": round(statistics.mean(row["new_tokens"] for row in rows), 2),
        "eos_endings": sum(row["ended_by_eos"] for row in rows),
        "natural_endings": sum(row["analysis"]["ends_naturally"] for row in rows),
        "max_token_cutoffs": sum(
            (not row["ended_by_eos"]) and row["new_tokens"] >= row["max_new_tokens"] for row in rows
        ),
        "repetition_samples": sum(row["analysis"]["repeated_4grams"] > 0 for row in rows),
        "web_residue_samples": sum(bool(row["residue_hits"]["web"]) for row in rows),
        "wiki_residue_samples": sum(bool(row["residue_hits"]["wiki"]) for row in rows),
        "pseudo_ency_samples": sum(bool(row["residue_hits"]["pseudo_ency"]) for row in rows),
        "topic_drift_samples": sum(row["topic_drift"] for row in rows),
        "avg_tokens_per_second": round(statistics.mean(row["tokens_per_second"] for row in rows), 2),
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Glyph-100M EOS-aware checkpoint recheck",
        "",
        "This is an inference-only base-LM continuation check. Generation now stops at the SentencePiece EOS token and reports the actual generated length.",
        "",
        "## Result",
        "",
        f"- prompts: `{payload['prompt_count']}`",
        f"- generations: `{len(payload['samples'])}`",
        f"- pairwise: `{payload['pairwise']}`",
        f"- provisional winner: **{payload['provisional_winner']}**",
        "",
        "| Checkpoint / preset | avg quality | EOS | natural | max-token cutoff | repetitions | avg tokens | tok/s |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key, row in payload["summary"].items():
        lines.append(
            f"| {key} | {row['avg_quality_score']} | {row['eos_endings']}/{row['count']} | "
            f"{row['natural_endings']}/{row['count']} | {row['max_token_cutoffs']}/{row['count']} | "
            f"{row['repetition_samples']}/{row['count']} | {row['avg_actual_new_tokens']} | "
            f"{row['avg_tokens_per_second']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The old eval path treated every generation as if it consumed the full token budget. This recheck separates true EOS endings from max-token cutoffs. It is intentionally smaller than the historical broad eval and does not by itself authorize training or change the selected best checkpoint.",
            "",
            "## Largest Pairwise Differences",
            "",
        ]
    )
    for row in payload["largest_differences"]:
        lines.extend(
            [
                f"### {row['prompt_id']} · {row['preset']} · delta 50k-44k={row['delta']}",
                "",
                f"Prompt: `{row['prompt']}`",
                "",
                f"44k ({row['score_44k']}): {row['output_44k'][:700]}",
                "",
                f"50k ({row['score_50k']}): {row['output_50k'][:700]}",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", type=Path, default=Path("eval/glyph-100m/v2_3_1_broad_prompts.jsonl"))
    parser.add_argument("--tokenizer", type=Path, default=Path("data/processed/tokenizer.model"))
    parser.add_argument("--device", choices=("cpu", "cuda", "auto"), default="auto")
    parser.add_argument("--attention-backend", choices=("sdpa", "math", "manual"), default="math")
    parser.add_argument("--seed", type=int, default=20260716)
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()

    device_name = "cuda" if args.device == "auto" and torch.cuda.is_available() else args.device
    device = torch.device(device_name)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA/HIP requested but unavailable")
    configure_attention_backend(args.attention_backend)

    tokenizer_path = ROOT / args.tokenizer
    tokenizer_sha = sha256(tokenizer_path)
    if tokenizer_sha != EXPECTED_TOKENIZER_SHA:
        raise SystemExit(f"tokenizer SHA mismatch: {tokenizer_sha}")
    sp = load_tokenizer(tokenizer_path)
    prompts = read_jsonl(ROOT / args.prompts)
    samples: list[dict] = []
    existing_keys: set[tuple[str, str, str]] = set()
    if args.reuse_existing and args.json.exists():
        previous = json.loads(args.json.read_text(encoding="utf-8"))
        prompt_ids = {row["id"] for row in prompts}
        for row in previous.get("samples", []):
            key = (row.get("checkpoint"), row.get("prompt_id"), row.get("preset"))
            if key[0] in CHECKPOINTS and key[1] in prompt_ids and key[2] in PRESETS:
                samples.append(row)
                existing_keys.add(key)
    metadata: dict[str, dict] = {}

    for label, relative_path in CHECKPOINTS.items():
        path = ROOT / relative_path
        if not path.exists():
            raise SystemExit(f"missing checkpoint: {path}")
        meta = load_checkpoint_metadata(path)
        if meta["variant"] != "glyph-100m" or meta["dataset_name"] != "glyph100_v2_3_1":
            raise SystemExit(f"checkpoint metadata mismatch for {label}: {meta}")
        if meta["tokenizer_sha256"] != EXPECTED_TOKENIZER_SHA:
            raise SystemExit(f"checkpoint tokenizer mismatch for {label}")
        metadata[label] = meta
        print(f"loading {label}: {relative_path}", flush=True)
        model, state = load_model(path, device)
        for preset_name, settings in PRESETS.items():
            print(f"  {preset_name}", flush=True)
            for prompt_index, prompt_row in enumerate(prompts):
                key = (label, prompt_row["id"], preset_name)
                if key in existing_keys:
                    continue
                result = generate_one(
                    model,
                    sp,
                    device,
                    prompt_row["prompt"],
                    settings,
                    args.seed + prompt_index,
                )
                samples.append(
                    {
                        "checkpoint": label,
                        "checkpoint_step": state.get("step") or state.get("current_step"),
                        "prompt_id": prompt_row["id"],
                        "category": prompt_row["category"],
                        "preset": preset_name,
                        "settings": settings,
                        **enrich_result(result, prompt_row),
                    }
                )
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()

    grouped: dict[str, list[dict]] = defaultdict(list)
    by_key: dict[tuple[str, str, str], dict] = {}
    for row in samples:
        grouped[f"{row['checkpoint']} / {row['preset']}"].append(row)
        by_key[(row["checkpoint"], row["prompt_id"], row["preset"])] = row

    pairwise = Counter()
    differences = []
    for prompt in prompts:
        for preset_name in PRESETS:
            row44 = by_key[("44k", prompt["id"], preset_name)]
            row50 = by_key[("50k", prompt["id"], preset_name)]
            delta = row50["quality_score"] - row44["quality_score"]
            if delta >= 2:
                pairwise["50k"] += 1
            elif delta <= -2:
                pairwise["44k"] += 1
            else:
                pairwise["tie"] += 1
            differences.append(
                {
                    "prompt_id": prompt["id"],
                    "preset": preset_name,
                    "prompt": prompt["prompt"],
                    "delta": delta,
                    "score_44k": row44["quality_score"],
                    "score_50k": row50["quality_score"],
                    "output_44k": row44["new_text"],
                    "output_50k": row50["new_text"],
                }
            )
    winner = "44k" if pairwise["44k"] >= pairwise["50k"] else "50k"
    payload = {
        "device": str(device),
        "attention_backend": args.attention_backend,
        "prompt_file": str(args.prompts),
        "prompt_count": len(prompts),
        "presets": PRESETS,
        "tokenizer_sha256": tokenizer_sha,
        "checkpoints": metadata,
        "summary": {key: summarize(rows) for key, rows in grouped.items()},
        "pairwise": dict(pairwise),
        "provisional_winner": winner,
        "largest_differences": sorted(differences, key=lambda row: abs(row["delta"]), reverse=True)[:12],
        "samples": samples,
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(render_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"pairwise": dict(pairwise), "winner": winner, "summary": payload["summary"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
