#!/usr/bin/env python3
"""Run the matched quality gate for Glyph-100M v2.4.2 at 5k steps."""
from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import Counter
from pathlib import Path

import sentencepiece as spm
import torch

from eval_glyph100_stage2 import configure_attention_backend, generate_one, load_model, read_jsonl


ROOT = Path(__file__).resolve().parent.parent
PREFIX = "glyph100_v2_4_2_5k_gate_20260808"
TOKENIZER_SHA256 = "21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029"
CHECKPOINTS = {
    "v241_5k": {
        "path": "checkpoints/glyph-100m-v2_4_1-5k/step_0005000.pt",
        "step": 5000,
        "dataset": "glyph100_dataset_v2_4_1_core",
    },
    "v242_1k": {
        "path": "checkpoints/glyph-100m-v2_4_2-5k/step_0001000.pt",
        "step": 1000,
        "dataset": "glyph100_dataset_v2_4_2_core",
    },
    "v242_3k": {
        "path": "checkpoints/glyph-100m-v2_4_2-5k/step_0003000.pt",
        "step": 3000,
        "dataset": "glyph100_dataset_v2_4_2_core",
    },
    "v242_5k": {
        "path": "checkpoints/glyph-100m-v2_4_2-5k/step_0005000.pt",
        "step": 5000,
        "dataset": "glyph100_dataset_v2_4_2_core",
    },
}
PRESETS = {
    "conservative": {"temperature": 0.6, "top_k": 30, "max_new_tokens": 400},
    "normal": {"temperature": 0.8, "top_k": 40, "max_new_tokens": 400},
}
PSEUDO_PATTERNS = (
    "województw",
    "w gminie",
    "w powiecie",
    "miejscowość",
    "w latach 1975",
    "administracyjnie",
    "liczyła mieszkańców",
)
WEB_PATTERNS = (
    "http://",
    "https://",
    "www.",
    "strona główna",
    "używamy cookies",
    "polityka prywatności",
    "dodaj do koszyka",
    "kup teraz",
    "zaloguj się",
    "zarejestruj się",
)
WORD_RE = re.compile(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]+", re.UNICODE)
VOWELS = set("aąeęiouóyAĄEĘIOUÓY")
STEP_RE = re.compile(r"eval step=\s*(?P<step>\d+) \| val_loss=(?P<loss>[\d.]+)")


def load_tokenizer(path: Path) -> spm.SentencePieceProcessor:
    processor = spm.SentencePieceProcessor()
    if not processor.load(str(path)):
        raise RuntimeError(f"Could not load tokenizer: {path}")
    return processor


def checkpoint_contract(state: dict, spec: dict) -> dict:
    contract = {
        "step": state.get("step"),
        "current_step": state.get("current_step"),
        "variant": state.get("variant"),
        "dataset_name": state.get("dataset_name"),
        "tokenizer_sha256": state.get("tokenizer_sha256"),
        "batch_size": state.get("batch_size"),
        "gradient_accumulation_steps": state.get("gradient_accumulation_steps"),
        "effective_tokens_per_step": state.get("effective_tokens_per_step"),
        "optimizer_state_present": bool(state.get("optimizer")),
        "scheduler_state_present": bool(state.get("scheduler_state")),
        "sampler_state_present": bool(state.get("data_state")),
    }
    contract["valid"] = all(
        (
            contract["step"] == spec["step"],
            contract["current_step"] == spec["step"],
            contract["variant"] == "glyph-100m",
            contract["dataset_name"] == spec["dataset"],
            contract["tokenizer_sha256"] == TOKENIZER_SHA256,
            contract["batch_size"] == 4,
            contract["gradient_accumulation_steps"] == 8,
            contract["effective_tokens_per_step"] == 16384,
            contract["optimizer_state_present"],
            contract["scheduler_state_present"],
            contract["sampler_state_present"],
        )
    )
    return contract


def diagnostic(text: str, result: dict) -> dict:
    lowered = text.lower()
    words = WORD_RE.findall(text)
    pseudo_hits = [pattern for pattern in PSEUDO_PATTERNS if pattern in lowered]
    web_hits = [pattern for pattern in WEB_PATTERNS if pattern in lowered]
    odd_words = [word for word in words if len(word) >= 5 and not any(char in VOWELS for char in word)]
    counts = Counter(word.lower() for word in words)
    dominant_word_share = max(counts.values(), default=0) / max(1, len(words))
    repeated = result["analysis"]["repeated_4grams"] > 0 or dominant_word_share > 0.2
    natural = bool(result["ended_by_eos"] or result["analysis"]["ends_naturally"])
    cutoff = bool(result["new_tokens"] >= result["max_new_tokens"] and not result["ended_by_eos"])
    odd_ratio = len(odd_words) / max(1, len(words))

    score = 3.0
    score += 1.0 if result["analysis"]["alphabetic_ratio"] >= 0.65 else -1.0
    score += 2.0 if natural else 0.0
    score += 1.0 if not repeated else -2.0
    score -= 1.0 if cutoff else 0.0
    score -= 2.0 if pseudo_hits else 0.0
    score -= 2.0 if web_hits else 0.0
    score -= 1.0 if odd_ratio > 0.15 else 0.0
    score -= 1.0 if len(words) < 4 else 0.0
    return {
        "quality_score": round(max(0.0, min(10.0, score)), 2),
        "natural_ending": natural,
        "cutoff_like": cutoff,
        "repetition": repeated,
        "pseudo_ency_hits": pseudo_hits,
        "web_residue_hits": web_hits,
        "odd_word_ratio": round(odd_ratio, 4),
        "dominant_word_share": round(dominant_word_share, 4),
    }


def summarize(rows: list[dict]) -> dict:
    scores = [row["diagnostic"]["quality_score"] for row in rows]
    return {
        "samples": len(rows),
        "avg_quality_score": round(statistics.mean(scores), 3),
        "median_quality_score": round(statistics.median(scores), 3),
        "natural_endings": sum(row["diagnostic"]["natural_ending"] for row in rows),
        "cutoff_like": sum(row["diagnostic"]["cutoff_like"] for row in rows),
        "repetition_samples": sum(row["diagnostic"]["repetition"] for row in rows),
        "pseudo_ency_samples": sum(bool(row["diagnostic"]["pseudo_ency_hits"]) for row in rows),
        "web_residue_samples": sum(bool(row["diagnostic"]["web_residue_hits"]) for row in rows),
        "avg_generated_tokens": round(statistics.mean(row["new_tokens"] for row in rows), 2),
        "avg_generation_tokens_per_second": round(statistics.mean(row["tokens_per_second"] for row in rows), 2),
    }


def pairwise(rows: list[dict], left: str, right: str) -> dict:
    keyed = {
        (row["checkpoint_label"], row["prompt_id"], row["preset"]): row["diagnostic"]["quality_score"]
        for row in rows
    }
    wins = {left: 0, right: 0, "ties": 0}
    for prompt_id, preset in sorted({(row["prompt_id"], row["preset"]) for row in rows}):
        left_score = keyed[(left, prompt_id, preset)]
        right_score = keyed[(right, prompt_id, preset)]
        if left_score > right_score:
            wins[left] += 1
        elif right_score > left_score:
            wins[right] += 1
        else:
            wins["ties"] += 1
    return wins


def validation_losses() -> list[dict]:
    path = ROOT / "logs" / "glyph-100m-v2_4_2-5k" / "train.log"
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = STEP_RE.search(line)
        if match:
            rows.append({"step": int(match.group("step")), "val_loss": float(match.group("loss"))})
    return sorted({row["step"]: row for row in rows}.values(), key=lambda row: row["step"])


def write_samples_md(path: Path, rows: list[dict]) -> None:
    lines = [
        "# Glyph-100M v2.4.2 5k quality-gate samples",
        "",
        "Matched base-LM continuation eval. This is not an assistant benchmark.",
        "",
    ]
    for row in rows:
        diag = row["diagnostic"]
        lines.extend(
            [
                f"## {row['checkpoint_label']} · {row['prompt_id']} · {row['preset']}",
                "",
                f"**Prompt:** `{row['prompt']}`",
                "",
                "```text",
                row["full_text"],
                "```",
                "",
                f"Score `{diag['quality_score']}` · natural `{diag['natural_ending']}` · "
                f"cutoff `{diag['cutoff_like']}` · repetition `{diag['repetition']}` · "
                f"pseudo-ency `{bool(diag['pseudo_ency_hits'])}` · web `{bool(diag['web_residue_hits'])}`",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prompts",
        default="eval/glyph-100m/glyph100_v2_4_1_5k_eval_20260717_prompts.jsonl",
    )
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--device", default="cuda", choices=["cpu", "cuda"])
    parser.add_argument("--attention-backend", default="sdpa", choices=["sdpa", "math", "manual"])
    parser.add_argument("--seed", type=int, default=20260717)
    args = parser.parse_args()

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA/HIP requested but unavailable")
    configure_attention_backend(args.attention_backend)
    prompts = read_jsonl(ROOT / args.prompts)
    tokenizer = load_tokenizer(ROOT / args.tokenizer)
    rows: list[dict] = []
    contracts: dict[str, dict] = {}

    for checkpoint_index, (label, spec) in enumerate(CHECKPOINTS.items()):
        print(f"loading {label}: {spec['path']}", flush=True)
        model, state = load_model(ROOT / spec["path"], device)
        contracts[label] = checkpoint_contract(state, spec)
        if not contracts[label]["valid"]:
            raise SystemExit(f"checkpoint contract failed for {label}: {contracts[label]}")
        for preset_name, settings in PRESETS.items():
            for prompt_index, prompt in enumerate(prompts):
                result = generate_one(
                    model,
                    tokenizer,
                    device,
                    prompt["prompt"],
                    settings,
                    args.seed + prompt_index,
                )
                row = {
                    "checkpoint_label": label,
                    "checkpoint": spec["path"],
                    "checkpoint_step": state.get("step"),
                    "prompt_id": prompt["id"],
                    "category": prompt["category"],
                    "expected": prompt.get("expected"),
                    "preset": preset_name,
                    "settings": settings,
                    **result,
                }
                row["diagnostic"] = diagnostic(row["new_text"], row)
                rows.append(row)
        del model, state
        if device.type == "cuda":
            torch.cuda.empty_cache()
        print(f"completed {label}: {len(prompts) * len(PRESETS)} samples", flush=True)

    summaries = {}
    for label in CHECKPOINTS:
        label_rows = [row for row in rows if row["checkpoint_label"] == label]
        summaries[label] = {
            "overall": summarize(label_rows),
            "by_preset": {
                preset: summarize([row for row in label_rows if row["preset"] == preset])
                for preset in PRESETS
            },
        }
    pairwise_results = {
        "v241_5k_vs_v242_5k": pairwise(rows, "v241_5k", "v242_5k"),
        "v242_1k_vs_v242_5k": pairwise(rows, "v242_1k", "v242_5k"),
        "v242_3k_vs_v242_5k": pairwise(rows, "v242_3k", "v242_5k"),
    }
    validation = validation_losses()
    best_label = max(CHECKPOINTS, key=lambda label: summaries[label]["overall"]["avg_quality_score"])
    payload = {
        "run_id": PREFIX,
        "scope": "matched base-LM continuation quality gate; no training performed",
        "prompts": len(prompts),
        "presets": PRESETS,
        "checkpoints": CHECKPOINTS,
        "checkpoint_contracts": contracts,
        "v242_validation_losses": validation,
        "summaries": summaries,
        "pairwise": pairwise_results,
        "heuristic_best_checkpoint": best_label,
        "methodology_note": "Scores are deterministic diagnostics; semantic samples require manual review.",
        "samples": rows,
    }

    eval_dir = ROOT / "eval" / "glyph-100m"
    eval_dir.mkdir(parents=True, exist_ok=True)
    samples_json = eval_dir / f"{PREFIX}_samples.json"
    samples_md = eval_dir / f"{PREFIX}_samples.md"
    comparison_json = eval_dir / f"{PREFIX}_comparison.json"
    comparison_md = eval_dir / f"{PREFIX}_comparison.md"
    samples_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_samples_md(samples_md, rows)

    compact = {key: value for key, value in payload.items() if key != "samples"}
    comparison_json.write_text(json.dumps(compact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Glyph-100M v2.4.2 5k matched quality gate",
        "",
        "| checkpoint | avg score | median | natural | cutoff | repetition | pseudo-ency | web residue |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label in CHECKPOINTS:
        item = summaries[label]["overall"]
        lines.append(
            f"| {label} | {item['avg_quality_score']:.3f} | {item['median_quality_score']:.3f} | "
            f"{item['natural_endings']}/{item['samples']} | {item['cutoff_like']}/{item['samples']} | "
            f"{item['repetition_samples']}/{item['samples']} | {item['pseudo_ency_samples']}/{item['samples']} | "
            f"{item['web_residue_samples']}/{item['samples']} |"
        )
    lines.extend(
        [
            "",
            "## Pairwise heuristic",
            "",
            f"- v2.4.1 5k vs v2.4.2 5k: `{pairwise_results['v241_5k_vs_v242_5k']}`",
            f"- v2.4.2 1k vs 5k: `{pairwise_results['v242_1k_vs_v242_5k']}`",
            f"- v2.4.2 3k vs 5k: `{pairwise_results['v242_3k_vs_v242_5k']}`",
            f"- heuristic best checkpoint: `{best_label}`",
            "",
            "## v2.4.2 validation loss",
            "",
        ]
    )
    for row in validation:
        lines.append(f"- step `{row['step']}`: `{row['val_loss']}`")
    lines.extend(
        [
            "",
            "The score is a deterministic diagnostic for endings, loops and residue. Manual semantic review is part of the gate.",
            "",
        ]
    )
    comparison_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote consolidated outputs with prefix {PREFIX}", flush=True)


if __name__ == "__main__":
    main()
