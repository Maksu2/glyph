#!/usr/bin/env python3
"""Broad checkpoint/preset eval for Glyph-100M v2.3.1.

Inference only. This script does not train and does not mutate checkpoints.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from eval_glyph100_stage2 import (  # noqa: E402
    analyze_text,
    configure_attention_backend,
    generate_one,
    heuristic_score,
    load_model,
    load_tokenizer,
    qualitative_note,
    read_jsonl,
)


EXPECTED_TOKENIZER_SHA = "21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029"

CHECKPOINTS = [
    ("35k", "checkpoints/glyph-100m-v2_3_1-35k/latest.pt", 35000),
    ("36k", "checkpoints/glyph-100m-v2_3_1-45k/step_0036000.pt", 36000),
    ("38k", "checkpoints/glyph-100m-v2_3_1-45k/step_0038000.pt", 38000),
    ("40k", "checkpoints/glyph-100m-v2_3_1-45k/step_0040000.pt", 40000),
    ("42k", "checkpoints/glyph-100m-v2_3_1-45k/step_0042000.pt", 42000),
    ("44k", "checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt", 44000),
    ("45k", "checkpoints/glyph-100m-v2_3_1-45k/latest.pt", 45000),
]

PRESETS = {
    "current_normal_80": {"temperature": 0.8, "top_k": 40, "top_p": 1.0, "repetition_penalty": 1.0, "max_new_tokens": 80},
    "current_normal_120": {"temperature": 0.8, "top_k": 40, "top_p": 1.0, "repetition_penalty": 1.0, "max_new_tokens": 120},
    "safer_low_temp_80": {"temperature": 0.6, "top_k": 30, "top_p": 1.0, "repetition_penalty": 1.0, "max_new_tokens": 80},
    "safer_low_temp_120": {"temperature": 0.6, "top_k": 30, "top_p": 1.0, "repetition_penalty": 1.0, "max_new_tokens": 120},
    "nucleus_safe_80": {"temperature": 0.7, "top_k": None, "top_p": 0.9, "repetition_penalty": 1.0, "max_new_tokens": 80},
    "nucleus_safe_120": {"temperature": 0.7, "top_k": None, "top_p": 0.9, "repetition_penalty": 1.0, "max_new_tokens": 120},
    "repetition_guard_80": {"temperature": 0.7, "top_k": 40, "top_p": 1.0, "repetition_penalty": 1.15, "max_new_tokens": 80},
    "repetition_guard_120": {"temperature": 0.7, "top_k": 40, "top_p": 1.0, "repetition_penalty": 1.15, "max_new_tokens": 120},
}

WIKI_PATTERNS = [
    "przypisy",
    "bibliografia",
    "linki zewnętrzne",
    "zobacz też",
    "kategoria:",
    "źródła",
]
WEB_RESIDUE_PATTERNS = [
    "dodaj do koszyka",
    "koszyk",
    "promocja",
    "produkt",
    "polityka prywatności",
    "cookies",
    "zaloguj",
    "zarejestruj",
    "komentarze",
    "odpowiedz",
    "cytuj",
    "czytaj więcej",
    "więcej informacji",
    "kliknij",
    "forum",
    "fandom",
    "treści społeczności",
    "strona główna",
]
PSEUDO_ENCY_PATTERNS = [
    "według danych",
    "według najnowszych danych",
    "w latach",
    "województwa",
    "województwie",
    "powiecie",
    "gminie",
    "departamencie",
    "liczba ludności",
    "powierzchnia wynosi",
    "spisu",
    "ngc",
]
GEOGRAPHY_HISTORY_SUSPECT = [
    "województwie",
    "powiecie",
    "gminie",
    "liczba ludności",
    "powierzchnia wynosi",
    "według danych",
    "spisu",
    "w latach",
]
STOPWORDS = {
    "i",
    "w",
    "na",
    "z",
    "do",
    "że",
    "to",
    "jest",
    "się",
    "nie",
    "oraz",
    "dla",
    "od",
    "po",
    "tym",
    "ten",
    "ta",
    "te",
    "a",
    "o",
    "jak",
    "gdy",
    "przez",
    "pod",
    "nad",
    "bez",
    "czy",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_checkpoint_metadata(path: Path) -> dict:
    state = torch.load(path, map_location="cpu", weights_only=False)
    train_config = state.get("train_config") or {}
    metadata = state.get("metadata") or {}
    return {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "step": state.get("step") or state.get("current_step"),
        "current_step": state.get("current_step"),
        "variant": state.get("variant") or metadata.get("variant"),
        "model_config": state.get("model_config") or metadata.get("model_config") or {},
        "tokenizer_path": state.get("tokenizer_path") or train_config.get("tokenizer_path") or metadata.get("tokenizer_path"),
        "tokenizer_sha256": state.get("tokenizer_sha256")
        or train_config.get("tokenizer_sha256")
        or metadata.get("tokenizer_sha256"),
        "dataset_name": state.get("dataset_name") or train_config.get("dataset_name") or metadata.get("dataset_name"),
        "dataset_metadata_path": state.get("dataset_metadata_path")
        or train_config.get("dataset_metadata_path")
        or metadata.get("dataset_metadata_path"),
        "batch_size": state.get("batch_size") or train_config.get("batch_size") or metadata.get("batch_size"),
        "gradient_accumulation_steps": state.get("gradient_accumulation_steps")
        or train_config.get("gradient_accumulation_steps")
        or metadata.get("gradient_accumulation_steps"),
        "effective_tokens_per_step": state.get("effective_tokens_per_step")
        or train_config.get("effective_tokens_per_step")
        or metadata.get("effective_tokens_per_step"),
    }


def residue_hits(text: str) -> dict:
    lower = text.lower()
    return {
        "wiki": [pattern for pattern in WIKI_PATTERNS if pattern in lower],
        "web": [pattern for pattern in WEB_RESIDUE_PATTERNS if pattern in lower],
        "pseudo_ency": [pattern for pattern in PSEUDO_ENCY_PATTERNS if pattern in lower],
        "geo_history_suspect": [pattern for pattern in GEOGRAPHY_HISTORY_SUSPECT if pattern in lower],
    }


def words(text: str) -> list[str]:
    return [w.lower() for w in re.findall(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9]+", text)]


def content_words(text: str) -> set[str]:
    return {w for w in words(text) if len(w) >= 4 and w not in STOPWORDS}


def topic_overlap(prompt: str, text: str) -> float:
    p = content_words(prompt)
    if not p:
        return 0.0
    t = content_words(text)
    return len(p & t) / len(p)


def sentenceish_score(text: str) -> int:
    stripped = text.strip()
    if not stripped:
        return 0
    score = 0
    if re.search(r"[.!?…]\s*$", stripped):
        score += 2
    if len(re.findall(r"\w+", stripped, flags=re.UNICODE)) >= 20:
        score += 1
    if len(re.findall(r"[.!?]", stripped)) >= 2:
        score += 1
    if stripped.count(" ") > 10:
        score += 1
    return score


def grammar_readability_score(analysis: dict) -> int:
    score = 0
    if analysis.get("alphabetic_ratio", 0) >= 0.62:
        score += 2
    if analysis.get("words", 0) >= 20:
        score += 1
    if analysis.get("polish_char_count", 0) >= 2:
        score += 1
    if analysis.get("repeated_4grams", 0) == 0:
        score += 2
    if analysis.get("web_garbage_hits") or analysis.get("url_count") or analysis.get("html_count"):
        score -= 4
    return score


def quality_score(row: dict) -> int:
    analysis = row["analysis"]
    hits = row["residue_hits"]
    overlap = row["topic_overlap"]
    score = heuristic_score(analysis)
    score += sentenceish_score(row["new_text"])
    score += grammar_readability_score(analysis)
    if overlap >= 0.5:
        score += 2
    elif overlap >= 0.25:
        score += 1
    else:
        score -= 1
    score -= 3 * len(hits["web"])
    score -= 2 * len(hits["wiki"])
    score -= min(6, 2 * len(hits["pseudo_ency"]))
    score -= min(4, len(hits["geo_history_suspect"]))
    score -= min(6, analysis.get("repeated_4grams", 0) * 2)
    if not row["new_text"].strip():
        score -= 8
    if analysis.get("words", 0) < 8:
        score -= 3
    if row.get("topic_drift"):
        score -= 2
    return int(score)


def enrich_result(result: dict, prompt_row: dict) -> dict:
    hits = residue_hits(result["new_text"])
    overlap = topic_overlap(prompt_row["prompt"], result["new_text"])
    topic_drift = overlap < 0.15 and prompt_row["category"] not in {
        "web_forum_garbage_traps",
        "pseudo_ency_traps",
        "naturalne_zakonczenia",
    }
    geography_history_suspect = bool(hits["geo_history_suspect"])
    result["residue_hits"] = hits
    result["topic_overlap"] = round(overlap, 3)
    result["topic_drift"] = topic_drift
    result["geography_history_suspect"] = geography_history_suspect
    result["quality_score"] = quality_score(result)
    return result


def summarize(rows: list[dict]) -> dict:
    if not rows:
        return {}
    analyses = [row["analysis"] for row in rows]
    return {
        "count": len(rows),
        "avg_quality_score": round(statistics.mean(row["quality_score"] for row in rows), 3),
        "median_quality_score": round(statistics.median(row["quality_score"] for row in rows), 3),
        "avg_tokens_per_second": round(statistics.mean(row["tokens_per_second"] for row in rows), 2),
        "repetition_samples": sum(1 for a in analyses if a["repeated_4grams"] > 0),
        "natural_endings": sum(1 for a in analyses if a["ends_naturally"]),
        "eos_endings": sum(1 for a in analyses if a.get("ended_by_eos")),
        "cutoff_like_samples": sum(1 for a in analyses if not a["ends_naturally"]),
        "web_garbage_samples": sum(1 for a in analyses if a["web_garbage_hits"] or a["url_count"] or a["html_count"]),
        "web_residue_samples": sum(1 for row in rows if row["residue_hits"]["web"]),
        "wiki_residue_samples": sum(1 for row in rows if row["residue_hits"]["wiki"]),
        "pseudo_ency_samples": sum(1 for row in rows if row["residue_hits"]["pseudo_ency"]),
        "geo_history_suspect_samples": sum(1 for row in rows if row["geography_history_suspect"]),
        "topic_drift_samples": sum(1 for row in rows if row["topic_drift"]),
        "avg_topic_overlap": round(statistics.mean(row["topic_overlap"] for row in rows), 3),
    }


def compare_to_baseline(samples: list[dict], baseline_label: str = "35k") -> list[dict]:
    by_key = {
        (row["prompt_id"], row["preset"], row["checkpoint_label"]): row
        for row in samples
    }
    out = []
    for row in samples:
        if row["checkpoint_label"] == baseline_label:
            continue
        baseline = by_key.get((row["prompt_id"], row["preset"], baseline_label))
        if not baseline:
            continue
        delta = row["quality_score"] - baseline["quality_score"]
        if delta >= 2:
            winner = row["checkpoint_label"]
        elif delta <= -2:
            winner = baseline_label
        else:
            winner = "tie"
        out.append(
            {
                "checkpoint": row["checkpoint_label"],
                "prompt_id": row["prompt_id"],
                "category": row["category"],
                "preset": row["preset"],
                "score_baseline": baseline["quality_score"],
                "score_candidate": row["quality_score"],
                "delta": delta,
                "winner": winner,
                "candidate_repetition": row["analysis"]["repeated_4grams"],
                "baseline_repetition": baseline["analysis"]["repeated_4grams"],
                "candidate_pseudo_ency": row["residue_hits"]["pseudo_ency"],
                "baseline_pseudo_ency": baseline["residue_hits"]["pseudo_ency"],
                "candidate_topic_drift": row["topic_drift"],
                "baseline_topic_drift": baseline["topic_drift"],
            }
        )
    return out


def grouped_summary(rows: list[dict], key: str) -> dict:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row[key]].append(row)
    return {name: summarize(values) for name, values in sorted(grouped.items())}


def winner_counts(comparisons: list[dict]) -> dict:
    by_checkpoint: dict[str, Counter] = defaultdict(Counter)
    by_preset: dict[str, Counter] = defaultdict(Counter)
    for row in comparisons:
        by_checkpoint[row["checkpoint"]][row["winner"]] += 1
        by_preset[row["preset"]][row["winner"]] += 1
    return {
        "by_checkpoint": {k: dict(v) for k, v in sorted(by_checkpoint.items())},
        "by_preset": {k: dict(v) for k, v in sorted(by_preset.items())},
    }


def best_worst(rows: list[dict], checkpoint: str | None = None, n: int = 8) -> dict:
    selected = [row for row in rows if checkpoint is None or row["checkpoint_label"] == checkpoint]
    return {
        "best": sorted(selected, key=lambda row: row["quality_score"], reverse=True)[:n],
        "worst": sorted(selected, key=lambda row: row["quality_score"])[:n],
    }


def regression_examples(samples: list[dict], baseline_label: str = "35k", candidate_label: str = "45k", n: int = 8) -> list[dict]:
    by_key = {
        (row["prompt_id"], row["preset"], row["checkpoint_label"]): row
        for row in samples
    }
    rows = []
    for (prompt_id, preset, label), row in by_key.items():
        if label != candidate_label:
            continue
        baseline = by_key.get((prompt_id, preset, baseline_label))
        if not baseline:
            continue
        delta = row["quality_score"] - baseline["quality_score"]
        if delta < 0:
            rows.append({"delta": delta, "baseline": baseline, "candidate": row})
    return sorted(rows, key=lambda row: row["delta"])[:n]


def improvement_examples(samples: list[dict], baseline_label: str = "35k", candidate_label: str = "45k", n: int = 8) -> list[dict]:
    by_key = {
        (row["prompt_id"], row["preset"], row["checkpoint_label"]): row
        for row in samples
    }
    rows = []
    for (prompt_id, preset, label), row in by_key.items():
        if label != candidate_label:
            continue
        baseline = by_key.get((prompt_id, preset, baseline_label))
        if not baseline:
            continue
        delta = row["quality_score"] - baseline["quality_score"]
        if delta > 0:
            rows.append({"delta": delta, "baseline": baseline, "candidate": row})
    return sorted(rows, key=lambda row: row["delta"], reverse=True)[:n]


def compact_sample(row: dict) -> dict:
    return {
        "checkpoint": row["checkpoint_label"],
        "preset": row["preset"],
        "prompt_id": row["prompt_id"],
        "category": row["category"],
        "prompt": row["prompt"],
        "quality_score": row["quality_score"],
        "analysis": row["analysis"],
        "residue_hits": row["residue_hits"],
        "topic_overlap": row["topic_overlap"],
        "topic_drift": row["topic_drift"],
        "output": row["full_text"].strip(),
    }


def render_table_summary(title: str, summary: dict, order: list[str] | None = None) -> list[str]:
    keys = order or sorted(summary)
    lines = [
        f"## {title}",
        "",
        "| item | avg_q | rep | natural | cutoff | pseudo | web | wiki | drift | overlap |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key in keys:
        row = summary[key]
        count = row["count"]
        lines.append(
            f"| {key} | {row['avg_quality_score']} | {row['repetition_samples']}/{count} | "
            f"{row['natural_endings']}/{count} | {row['cutoff_like_samples']}/{count} | "
            f"{row['pseudo_ency_samples']}/{count} | {row['web_residue_samples']}/{count} | "
            f"{row['wiki_residue_samples']}/{count} | {row['topic_drift_samples']}/{count} | "
            f"{row['avg_topic_overlap']} |"
        )
    lines.append("")
    return lines


def render_checkpoint_eval_md(path: Path, payload: dict) -> None:
    checkpoint_order = [label for label, _, _ in CHECKPOINTS if label in payload["summary_by_checkpoint"]]
    lines = [
        "# Glyph-100M v2.3.1 broad checkpoint eval",
        "",
        "Base LM continuation eval. Nie ocenia instrukcyjności ani zachowania chatbota.",
        "",
        f"- prompts: `{payload['prompt_count']}`",
        f"- checkpoints: `{len(payload['checkpoint_order'])}`",
        f"- presets: `{len(payload['presets'])}`",
        f"- total generations: `{len(payload['samples'])}`",
        "",
    ]
    lines.extend(render_table_summary("Checkpoint Quality", payload["summary_by_checkpoint"], checkpoint_order))
    lines.extend(
        [
            "## Wins vs 35k",
            "",
            "| checkpoint | candidate wins | 35k wins | ties |",
            "|---|---:|---:|---:|",
        ]
    )
    for checkpoint in checkpoint_order:
        if checkpoint == "35k":
            continue
        counts = payload["winner_counts"]["by_checkpoint"].get(checkpoint, {})
        lines.append(
            f"| {checkpoint} | {counts.get(checkpoint, 0)} | {counts.get('35k', 0)} | {counts.get('tie', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Best Samples",
            "",
        ]
    )
    for row in payload["best_samples"]:
        lines.extend(sample_block(row))
    lines.extend(["## Worst Samples", ""])
    for row in payload["worst_samples"]:
        lines.extend(sample_block(row))
    lines.extend(["## 45k Regressions vs 35k", ""])
    for item in payload["regression_examples"]:
        lines.extend(comparison_block(item))
    lines.extend(["## 45k Improvements vs 35k", ""])
    for item in payload["improvement_examples"]:
        lines.extend(comparison_block(item))
    path.write_text("\n".join(lines), encoding="utf-8")


def render_preset_eval_md(path: Path, payload: dict) -> None:
    lines = [
        "# Glyph-100M v2.3.1 inference preset eval",
        "",
        "Ten raport rozdziela jakość checkpointu od jakości ustawień generacji.",
        "",
    ]
    lines.extend(render_table_summary("Preset Quality Across Checkpoints", payload["summary_by_preset"], list(PRESETS)))
    lines.extend(
        [
            "## Preset Wins vs 35k Baseline",
            "",
            "| preset | candidate wins | 35k wins | ties |",
            "|---|---:|---:|---:|",
        ]
    )
    for preset in PRESETS:
        rows = [row for row in payload["comparisons"] if row["preset"] == preset]
        counts = Counter(row["winner"] for row in rows)
        candidate_wins = sum(count for winner, count in counts.items() if winner not in {"35k", "tie"})
        lines.append(f"| {preset} | {candidate_wins} | {counts.get('35k', 0)} | {counts.get('tie', 0)} |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            f"- best preset by avg quality: `{payload['best_preset']}`",
            f"- best checkpoint by avg quality: `{payload['best_checkpoint']}`",
            "- `nucleus_safe` uses top_p=0.9 with top_k disabled.",
            "- `repetition_guard` uses repetition_penalty=1.15.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def sample_block(row: dict) -> list[str]:
    text = row["output"][:1200]
    return [
        f"### {row['checkpoint']} · {row['preset']} · {row['prompt_id']} · score={row['quality_score']}",
        "",
        f"**Prompt:** `{row['prompt']}`",
        "",
        f"**Residue:** {row['residue_hits']} · **drift:** `{row['topic_drift']}` · **overlap:** `{row['topic_overlap']}`",
        "",
        "```text",
        text,
        "```",
        "",
    ]


def comparison_block(item: dict) -> list[str]:
    baseline = compact_sample(item["baseline"])
    candidate = compact_sample(item["candidate"])
    return [
        f"### {candidate['prompt_id']} · {candidate['preset']} · delta={item['delta']}",
        "",
        f"**Prompt:** `{candidate['prompt']}`",
        "",
        f"**35k score:** `{baseline['quality_score']}` · **45k score:** `{candidate['quality_score']}`",
        "",
        "**35k:**",
        "",
        "```text",
        baseline["output"][:1000],
        "```",
        "",
        "**45k:**",
        "",
        "```text",
        candidate["output"][:1000],
        "```",
        "",
    ]


def choose_verdict(payload: dict) -> tuple[str, str]:
    summary = payload["summary_by_checkpoint"]
    best = payload["best_checkpoint"]
    wins_45 = payload["winner_counts"]["by_checkpoint"].get("45k", {}).get("45k", 0)
    losses_45 = payload["winner_counts"]["by_checkpoint"].get("45k", {}).get("35k", 0)
    q35 = summary.get("35k", {}).get("avg_quality_score", -999)
    q45 = summary.get("45k", {}).get("avg_quality_score", -999)
    if best == "45k" and wins_45 >= losses_45:
        return "C", "45k wins the broader eval."
    if best in {"40k", "42k", "44k"}:
        return "B", f"{best} has the best broad quality score."
    if best == "35k" and q35 >= q45:
        return "A", "35k remains the best quality checkpoint in this eval."
    return "E", "The result is mixed enough to avoid 50k; use a small SFT or extra targeted eval next."


def render_decision(path: Path, payload: dict) -> None:
    verdict, reason = choose_verdict(payload)
    payload["decision"] = {"verdict": verdict, "reason": reason}
    options = {
        "A": "35k zostaje best checkpoint",
        "B": "40k/42k/44k zostaje best checkpoint",
        "C": "45k jednak wygrywa po szerszym eval",
        "D": "zrobić 50k",
        "E": "nie robić 50k, przejść do SFT test",
        "F": "poprawić dataset v2.4 przed dalszym pretrainingiem",
    }
    lines = [
        "# Glyph-100M v2.3.1 best checkpoint decision",
        "",
        f"**Verdict: {verdict}) {options[verdict]}**",
        "",
        f"Reason: {reason}",
        "",
        "## Direct Answers",
        "",
        f"1. Best qualitative checkpoint: `{payload['best_checkpoint']}`.",
        f"2. 45k worse than 35k: `{payload['summary_by_checkpoint']['45k']['avg_quality_score'] < payload['summary_by_checkpoint']['35k']['avg_quality_score']}` by aggregate quality score.",
        f"3. Best intermediate checkpoint: `{payload['best_intermediate_checkpoint']}`.",
        f"4. Best inference preset: `{payload['best_preset']}`.",
        "5. 50k: not recommended from this eval unless a later manual review overturns it.",
        "6. Next: small SFT test is more rational than more pretraining on the same data if the goal is useful behavior.",
        "7. Problem shape: mostly dataset/style and base-LM sampling limits; not a training crash. The model still has cutoff-like completions and pseudo-ency tendencies.",
        "",
    ]
    lines.extend(render_table_summary("Checkpoint Summary", payload["summary_by_checkpoint"], payload["checkpoint_order"]))
    lines.extend(render_table_summary("Preset Summary", payload["summary_by_preset"], list(PRESETS)))
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", default="eval/glyph-100m/v2_3_1_broad_prompts.jsonl")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--attention-backend", default="math", choices=["sdpa", "math", "manual"])
    parser.add_argument("--seed", type=int, default=20260611)
    parser.add_argument("--checkpoint-json", default="eval/glyph-100m/v2_3_1_broad_checkpoint_eval.json")
    parser.add_argument("--checkpoint-md", default="eval/glyph-100m/v2_3_1_broad_checkpoint_eval.md")
    parser.add_argument("--preset-json", default="eval/glyph-100m/v2_3_1_inference_preset_eval.json")
    parser.add_argument("--preset-md", default="eval/glyph-100m/v2_3_1_inference_preset_eval.md")
    parser.add_argument("--decision-json", default="reports/glyph100_v2_3_1_best_checkpoint_decision.json")
    parser.add_argument("--decision-md", default="reports/glyph100_v2_3_1_best_checkpoint_decision.md")
    args = parser.parse_args()

    device = torch.device("cuda" if args.device == "auto" and torch.cuda.is_available() else args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA/HIP requested but torch.cuda.is_available() is false")
    configure_attention_backend(args.attention_backend)

    prompts = read_jsonl(ROOT / args.prompts)
    tokenizer_path = ROOT / args.tokenizer
    tokenizer_hash = sha256(tokenizer_path)
    if tokenizer_hash != EXPECTED_TOKENIZER_SHA:
        raise SystemExit(f"tokenizer sha mismatch: {tokenizer_hash}")
    sp = load_tokenizer(tokenizer_path)

    checkpoint_meta = {}
    available_checkpoints = []
    skipped = []
    for label, rel, expected_step in CHECKPOINTS:
        path = ROOT / rel
        if not path.exists():
            skipped.append({"label": label, "path": rel, "reason": "missing"})
            continue
        meta = load_checkpoint_metadata(path)
        errors = []
        if meta["variant"] != "glyph-100m":
            errors.append(f"variant={meta['variant']}")
        if meta["dataset_name"] != "glyph100_v2_3_1":
            errors.append(f"dataset={meta['dataset_name']}")
        if meta["tokenizer_sha256"] != EXPECTED_TOKENIZER_SHA:
            errors.append(f"tokenizer_sha={meta['tokenizer_sha256']}")
        if int(meta["step"] or 0) != expected_step:
            errors.append(f"step={meta['step']} expected={expected_step}")
        if int(meta["batch_size"] or 0) != 4:
            errors.append(f"batch_size={meta['batch_size']}")
        if int(meta["gradient_accumulation_steps"] or 0) != 8:
            errors.append(f"gradient_accumulation_steps={meta['gradient_accumulation_steps']}")
        if errors:
            skipped.append({"label": label, "path": rel, "reason": "; ".join(errors)})
            continue
        checkpoint_meta[label] = meta
        available_checkpoints.append((label, path))

    if "35k" not in {label for label, _ in available_checkpoints}:
        raise SystemExit("35k baseline checkpoint is required")

    samples = []
    for label, checkpoint in available_checkpoints:
        print(f"loading {label}: {checkpoint.relative_to(ROOT)}", flush=True)
        model, state = load_model(checkpoint, device)
        for preset_index, (preset_name, settings) in enumerate(PRESETS.items(), start=1):
            print(f"  preset {preset_index}/{len(PRESETS)} {preset_name}", flush=True)
            for prompt_index, prompt_row in enumerate(prompts):
                seed = args.seed + prompt_index
                result = generate_one(model, sp, device, prompt_row["prompt"], settings, seed)
                result = enrich_result(result, prompt_row)
                samples.append(
                    {
                        "checkpoint_label": label,
                        "checkpoint": str(checkpoint.relative_to(ROOT)),
                        "checkpoint_step": state.get("step") or state.get("current_step"),
                        "checkpoint_variant": state.get("variant"),
                        "prompt_id": prompt_row["id"],
                        "category": prompt_row["category"],
                        "expected_behavior": prompt_row.get("expected_behavior", ""),
                        "preset": preset_name,
                        "settings": settings,
                        "seed": seed,
                        **result,
                    }
                )
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()

    comparisons = compare_to_baseline(samples)
    summary_by_checkpoint = grouped_summary(samples, "checkpoint_label")
    summary_by_preset = grouped_summary(samples, "preset")
    checkpoint_order = [label for label, _ in available_checkpoints]
    best_checkpoint = max(summary_by_checkpoint.items(), key=lambda item: item[1]["avg_quality_score"])[0]
    intermediate_labels = [label for label in checkpoint_order if label not in {"35k", "45k"}]
    best_intermediate = (
        max(intermediate_labels, key=lambda label: summary_by_checkpoint[label]["avg_quality_score"])
        if intermediate_labels
        else None
    )
    best_preset = max(summary_by_preset.items(), key=lambda item: item[1]["avg_quality_score"])[0]
    examples = best_worst(samples, n=10)
    payload = {
        "device": str(device),
        "attention_backend": args.attention_backend,
        "seed": args.seed,
        "prompts_file": args.prompts,
        "prompt_count": len(prompts),
        "checkpoint_order": checkpoint_order,
        "checkpoints": checkpoint_meta,
        "skipped_checkpoints": skipped,
        "tokenizer": {"path": args.tokenizer, "sha256": tokenizer_hash},
        "presets": PRESETS,
        "samples": samples,
        "comparisons": comparisons,
        "winner_counts": winner_counts(comparisons),
        "summary_by_checkpoint": summary_by_checkpoint,
        "summary_by_preset": summary_by_preset,
        "best_checkpoint": best_checkpoint,
        "best_intermediate_checkpoint": best_intermediate,
        "best_preset": best_preset,
        "best_samples": [compact_sample(row) for row in examples["best"]],
        "worst_samples": [compact_sample(row) for row in examples["worst"]],
        "regression_examples": regression_examples(samples),
        "improvement_examples": improvement_examples(samples),
    }
    verdict, reason = choose_verdict(payload)
    payload["decision"] = {"verdict": verdict, "reason": reason}

    checkpoint_json = ROOT / args.checkpoint_json
    preset_json = ROOT / args.preset_json
    decision_json = ROOT / args.decision_json
    for path in [checkpoint_json, preset_json, decision_json, ROOT / args.checkpoint_md, ROOT / args.preset_md, ROOT / args.decision_md]:
        path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    preset_payload = {k: payload[k] for k in ["summary_by_preset", "summary_by_checkpoint", "winner_counts", "best_preset", "best_checkpoint", "comparisons", "presets", "decision"]}
    preset_json.write_text(json.dumps(preset_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    decision_payload = {k: payload[k] for k in ["decision", "best_checkpoint", "best_intermediate_checkpoint", "best_preset", "summary_by_checkpoint", "summary_by_preset", "winner_counts", "skipped_checkpoints"]}
    decision_json.write_text(json.dumps(decision_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    render_checkpoint_eval_md(ROOT / args.checkpoint_md, payload)
    render_preset_eval_md(ROOT / args.preset_md, payload)
    render_decision(ROOT / args.decision_md, payload)
    print(
        f"done: best_checkpoint={best_checkpoint} best_preset={best_preset} "
        f"verdict={verdict} reason={reason}",
        flush=True,
    )


if __name__ == "__main__":
    main()
