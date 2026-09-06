#!/usr/bin/env python3
"""Compare Glyph-100M v2.3.1 25k vs 35k as base-LM continuations.

This script runs inference only. It does not train or mutate checkpoints.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import sys
from collections import Counter
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


PRESETS = {
    "normal_80": {"temperature": 0.8, "top_k": 40, "max_new_tokens": 80},
    "normal_120": {"temperature": 0.8, "top_k": 40, "max_new_tokens": 120},
    "creative_80": {"temperature": 1.0, "top_k": 50, "max_new_tokens": 80},
    "creative_120": {"temperature": 1.0, "top_k": 50, "max_new_tokens": 120},
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
]
PSEUDO_ENCY_PATTERNS = [
    "według danych",
    "w latach",
    "województwa",
    "powiecie",
    "gminie",
    "departamencie",
    "liczba ludności",
    "powierzchnia wynosi",
    "ngc",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def residue_hits(text: str) -> dict:
    lower = text.lower()
    return {
        "wiki": [pattern for pattern in WIKI_PATTERNS if pattern in lower],
        "web": [pattern for pattern in WEB_RESIDUE_PATTERNS if pattern in lower],
        "pseudo_ency": [pattern for pattern in PSEUDO_ENCY_PATTERNS if pattern in lower],
    }


def sentenceish_score(text: str) -> int:
    stripped = text.strip()
    if not stripped:
        return 0
    score = 0
    if re.search(r"[.!?…]\s*$", stripped):
        score += 1
    if len(re.findall(r"\w+", stripped, flags=re.UNICODE)) >= 20:
        score += 1
    if len(re.findall(r"[.!?]", stripped)) >= 2:
        score += 1
    if stripped.count(" ") > 10:
        score += 1
    return score


def quality_score(row: dict) -> int:
    analysis = row["analysis"]
    hits = row["residue_hits"]
    score = heuristic_score(analysis)
    score += sentenceish_score(row["new_text"])
    score -= 2 * len(hits["web"])
    score -= len(hits["wiki"])
    score -= min(3, len(hits["pseudo_ency"]))
    score -= min(5, analysis.get("repeated_4grams", 0))
    if not row["new_text"].strip():
        score -= 5
    if analysis.get("words", 0) < 8:
        score -= 2
    return score


def load_checkpoint_metadata(path: Path) -> dict:
    state = torch.load(path, map_location="cpu", weights_only=False)
    train_config = state.get("train_config") or {}
    metadata = state.get("metadata") or {}
    return {
        "path": str(path.relative_to(ROOT)),
        "step": state.get("step") or state.get("current_step"),
        "current_step": state.get("current_step"),
        "variant": state.get("variant"),
        "model_config": state.get("model_config") or {},
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
    }


def compare_rows(row25: dict, row35: dict) -> dict:
    s25 = quality_score(row25)
    s35 = quality_score(row35)
    delta = s35 - s25
    if delta >= 2:
        winner = "35k"
    elif delta <= -2:
        winner = "25k"
    else:
        winner = "tie"

    improvements = []
    regressions = []
    for key, label in [
        ("repeated_4grams", "powtórzenia"),
        ("url_count", "URL"),
        ("html_count", "HTML"),
    ]:
        a = row25["analysis"].get(key, 0)
        b = row35["analysis"].get(key, 0)
        if b < a:
            improvements.append(f"mniej {label}")
        elif b > a:
            regressions.append(f"więcej {label}")
    for bucket, label in [("wiki", "wiki residue"), ("web", "web residue"), ("pseudo_ency", "pseudo-ency")]:
        a = len(row25["residue_hits"][bucket])
        b = len(row35["residue_hits"][bucket])
        if b < a:
            improvements.append(f"mniej {label}")
        elif b > a:
            regressions.append(f"więcej {label}")
    if row35["analysis"].get("ends_naturally") and not row25["analysis"].get("ends_naturally"):
        improvements.append("naturalniejsze zakończenie")
    elif row25["analysis"].get("ends_naturally") and not row35["analysis"].get("ends_naturally"):
        regressions.append("gorsze zakończenie")

    return {
        "prompt_id": row35["prompt_id"],
        "category": row35["category"],
        "preset": row35["preset"],
        "score_25k": s25,
        "score_35k": s35,
        "delta": delta,
        "winner": winner,
        "improvements": improvements,
        "regressions": regressions,
    }


def summarize_rows(rows: list[dict]) -> dict:
    out = {}
    for preset in PRESETS:
        preset_rows = [row for row in rows if row["preset"] == preset]
        analyses = [row["analysis"] for row in preset_rows]
        out[preset] = {
            "count": len(preset_rows),
            "avg_tokens_per_second": round(statistics.mean(row["tokens_per_second"] for row in preset_rows), 2),
            "repetition_samples": sum(1 for row in analyses if row["repeated_4grams"] > 0),
            "natural_endings": sum(1 for row in analyses if row["ends_naturally"]),
            "web_garbage_samples": sum(1 for row in analyses if row["web_garbage_hits"] or row["url_count"] or row["html_count"]),
            "wiki_residue_samples": sum(1 for row in preset_rows if row["residue_hits"]["wiki"]),
            "web_residue_samples": sum(1 for row in preset_rows if row["residue_hits"]["web"]),
            "pseudo_ency_samples": sum(1 for row in preset_rows if row["residue_hits"]["pseudo_ency"]),
            "cutoff_like_samples": sum(1 for row in analyses if not row["ends_naturally"]),
            "avg_quality_score": round(statistics.mean(quality_score(row) for row in preset_rows), 2),
        }
    return out


def render_samples_md(path: Path, rows35: list[dict], meta35: dict, tokenizer_hash: str) -> None:
    lines = [
        "# Glyph-100M v2.3.1 35k samples",
        "",
        "Base LM completion eval. To nie jest eval asystenta ani instruction-following.",
        "",
        f"- checkpoint: `{meta35['path']}`",
        f"- step: `{meta35['step']}`",
        f"- variant: `{meta35['variant']}`",
        f"- dataset: `{meta35['dataset_name']}`",
        f"- tokenizer sha256 actual: `{tokenizer_hash}`",
        "",
    ]
    for row in rows35:
        hits = row["residue_hits"]
        lines.extend(
            [
                f"## {row['prompt_id']} · {row['category']} · {row['preset']}",
                "",
                f"**Prompt:** `{row['prompt']}`",
                "",
                (
                    f"**Settings:** temp={row['settings']['temperature']} · "
                    f"top_k={row['settings']['top_k']} · "
                    f"max_new_tokens={row['settings']['max_new_tokens']} · seed={row['seed']}"
                ),
                "",
                "**Output:**",
                "",
                "```text",
                row["full_text"].strip(),
                "```",
                "",
                f"**Heurystyka:** {qualitative_note(row['analysis'])}",
                f"**Residue:** wiki={hits['wiki']} · web={hits['web']} · pseudo_ency={hits['pseudo_ency']}",
                f"**Quality score:** {quality_score(row)}",
                f"**Tok/s generation:** {row['tokens_per_second']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def render_comparison_md(path: Path, prompts: list[dict], rows25: list[dict], rows35: list[dict], comparisons: list[dict]) -> None:
    by25 = {(row["prompt_id"], row["preset"]): row for row in rows25}
    by35 = {(row["prompt_id"], row["preset"]): row for row in rows35}
    counts = Counter(row["winner"] for row in comparisons)
    lines = [
        "# Glyph-100M v2.3.1: 25k vs 35k",
        "",
        "Porównanie base LM completions. Model nie jest oceniany jako asystent.",
        "",
        "## Wynik heurystyczny",
        "",
        f"- 35k wins: {counts.get('35k', 0)}",
        f"- 25k wins: {counts.get('25k', 0)}",
        f"- ties: {counts.get('tie', 0)}",
        "",
    ]
    for preset in PRESETS:
        preset_rows = [row for row in comparisons if row["preset"] == preset]
        pc = Counter(row["winner"] for row in preset_rows)
        lines.extend(
            [
                f"### Preset `{preset}`",
                "",
                f"- 35k: {pc.get('35k', 0)}",
                f"- 25k: {pc.get('25k', 0)}",
                f"- tie: {pc.get('tie', 0)}",
                "",
            ]
        )

    prompt_by_id = {row["id"]: row for row in prompts}
    lines.extend(["## Próbki do ręcznej inspekcji", ""])
    sorted_rows = sorted(comparisons, key=lambda row: (row["winner"] != "35k", abs(row["delta"])), reverse=True)
    for cmp_row in sorted_rows:
        pid = cmp_row["prompt_id"]
        preset = cmp_row["preset"]
        row25 = by25[(pid, preset)]
        row35 = by35[(pid, preset)]
        prompt = prompt_by_id.get(pid, {})
        lines.extend(
            [
                f"### {pid} · {prompt.get('category', row35['category'])} · {preset} · winner={cmp_row['winner']} · delta={cmp_row['delta']}",
                "",
                f"**Prompt:** `{row35['prompt']}`",
                "",
                f"**25k score:** {cmp_row['score_25k']} · **35k score:** {cmp_row['score_35k']}",
                "",
                f"**Poprawy:** {', '.join(cmp_row['improvements']) or 'brak wyraźnych'}",
                f"**Regresje:** {', '.join(cmp_row['regressions']) or 'brak wyraźnych'}",
                "",
                "**25k:**",
                "",
                "```text",
                row25["full_text"].strip(),
                "```",
                "",
                "**35k:**",
                "",
                "```text",
                row35["full_text"].strip(),
                "```",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def verdict_from_counts(counts: Counter, rows35: list[dict]) -> str:
    total = sum(counts.values())
    wins35 = counts.get("35k", 0)
    wins25 = counts.get("25k", 0)
    residue35 = sum(1 for row in rows35 if row["residue_hits"]["web"] or row["residue_hits"]["wiki"])
    repetition35 = sum(1 for row in rows35 if row["analysis"]["repeated_4grams"] > 0)
    if wins35 >= int(total * 0.55) and wins35 >= wins25 * 2 and residue35 <= total * 0.25:
        return "A"
    if wins35 > wins25 and repetition35 <= total * 0.35:
        return "B"
    if wins35 > wins25:
        return "B"
    if wins25 > wins35:
        return "D"
    return "B"


def render_report(path: Path, payload: dict) -> None:
    counts = Counter(row["winner"] for row in payload["comparisons"])
    verdict = payload["verdict"]
    verdict_text = {
        "A": "Kontynuować do 50k.",
        "B": "Zrobić jeszcze checkpoint 45k.",
        "C": "Zatrzymać pretraining.",
        "D": "Poprawić dataset.",
        "E": "Zrobić dopiero mały SFT eksperyment.",
    }[verdict]
    lines = [
        "# Glyph-100M v2.3.1 35k eval report",
        "",
        "## Checkpointy",
        "",
        f"- 25k: `{payload['checkpoints']['25k']['path']}` · step `{payload['checkpoints']['25k']['step']}` · variant `{payload['checkpoints']['25k']['variant']}`",
        f"- 35k: `{payload['checkpoints']['35k']['path']}` · step `{payload['checkpoints']['35k']['step']}` · variant `{payload['checkpoints']['35k']['variant']}`",
        f"- tokenizer: `{payload['tokenizer']['path']}`",
        f"- tokenizer sha256 actual: `{payload['tokenizer']['sha256']}`",
        "",
        "## Ustawienia",
        "",
        "- base LM continuation, nie assistant/instruction eval",
        f"- prompts: `{payload['prompts_file']}`",
        f"- prompt count: `{payload['prompt_count']}`",
        f"- seed base: `{payload['seed']}`",
        "- presets: normal_80, normal_120, creative_80, creative_120",
        "",
        "## Wyniki heurystyczne",
        "",
        f"- 35k wins: {counts.get('35k', 0)}",
        f"- 25k wins: {counts.get('25k', 0)}",
        f"- ties: {counts.get('tie', 0)}",
        "",
        "## Summary 25k",
        "",
        "```json",
        json.dumps(payload["summaries"]["25k"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Summary 35k",
        "",
        "```json",
        json.dumps(payload["summaries"]["35k"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Werdykt",
        "",
        f"**{verdict}) {verdict_text}**",
        "",
        "## Uwagi",
        "",
        "- To nadal base LM, więc porównanie mierzy kontynuacje tekstu, nie odpowiedzi asystenta.",
        "- Najważniejsze są próbki w `eval/glyph-100m/v2_3_1_25k_vs_35k.md`.",
        "- Ten raport nie uruchamia kolejnego treningu.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint-25k", default="checkpoints/glyph-100m-v2_3_1-25k/latest.pt")
    parser.add_argument("--checkpoint-35k", default="checkpoints/glyph-100m-v2_3_1-35k/latest.pt")
    parser.add_argument("--prompts", default="eval/glyph-100m/stage2_completion_prompts.jsonl")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--attention-backend", default="math", choices=["sdpa", "math", "manual"])
    parser.add_argument("--seed", type=int, default=20260609)
    parser.add_argument("--out-json", default="eval/glyph-100m/v2_3_1_35k_samples.json")
    parser.add_argument("--out-md", default="eval/glyph-100m/v2_3_1_35k_samples.md")
    parser.add_argument("--compare-md", default="eval/glyph-100m/v2_3_1_25k_vs_35k.md")
    parser.add_argument("--report-md", default="reports/glyph100_v2_3_1_35k_eval_report.md")
    args = parser.parse_args()

    device = torch.device("cuda" if args.device == "auto" and torch.cuda.is_available() else args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA/HIP requested but torch.cuda.is_available() is false")
    configure_attention_backend(args.attention_backend)

    prompts = read_jsonl(ROOT / args.prompts)
    tokenizer_path = ROOT / args.tokenizer
    tokenizer_hash = sha256(tokenizer_path)
    sp = load_tokenizer(tokenizer_path)

    ckpt25 = ROOT / args.checkpoint_25k
    ckpt35 = ROOT / args.checkpoint_35k
    meta25 = load_checkpoint_metadata(ckpt25)
    meta35 = load_checkpoint_metadata(ckpt35)
    for label, meta, expected_step in [("25k", meta25, 25000), ("35k", meta35, 35000)]:
        if meta["variant"] != "glyph-100m":
            raise SystemExit(f"{label} checkpoint variant mismatch: {meta['variant']}")
        if int(meta["step"] or 0) != expected_step:
            raise SystemExit(f"{label} checkpoint step mismatch: {meta['step']} != {expected_step}")
        if meta["tokenizer_path"] != "data/processed/tokenizer.model":
            raise SystemExit(f"{label} tokenizer path mismatch: {meta['tokenizer_path']}")

    rows_by_checkpoint = {}
    for label, checkpoint in [("25k", ckpt25), ("35k", ckpt35)]:
        model, state = load_model(checkpoint, device)
        rows = []
        for preset_name, settings in PRESETS.items():
            for index, prompt in enumerate(prompts):
                seed = args.seed + index
                result = generate_one(model, sp, device, prompt["prompt"], settings, seed)
                result["residue_hits"] = residue_hits(result["new_text"])
                rows.append(
                    {
                        "checkpoint_label": label,
                        "checkpoint": str(checkpoint.relative_to(ROOT)),
                        "checkpoint_step": state.get("step") or state.get("current_step"),
                        "checkpoint_variant": state.get("variant"),
                        "prompt_id": prompt["id"],
                        "category": prompt["category"],
                        "expected": prompt.get("expected"),
                        "preset": preset_name,
                        "settings": settings,
                        "seed": seed,
                        **result,
                    }
                )
        rows_by_checkpoint[label] = rows
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()

    rows25 = rows_by_checkpoint["25k"]
    rows35 = rows_by_checkpoint["35k"]
    by25 = {(row["prompt_id"], row["preset"]): row for row in rows25}
    comparisons = [compare_rows(by25[(row35["prompt_id"], row35["preset"])], row35) for row35 in rows35]
    counts = Counter(row["winner"] for row in comparisons)

    payload = {
        "checkpoints": {"25k": meta25, "35k": meta35},
        "tokenizer": {"path": args.tokenizer, "sha256": tokenizer_hash},
        "device": str(device),
        "attention_backend": args.attention_backend,
        "seed": args.seed,
        "prompts_file": args.prompts,
        "prompt_count": len(prompts),
        "presets": PRESETS,
        "summaries": {"25k": summarize_rows(rows25), "35k": summarize_rows(rows35)},
        "winner_counts": dict(counts),
        "verdict": verdict_from_counts(counts, rows35),
        "samples_25k": rows25,
        "samples_35k": rows35,
        "comparisons": comparisons,
    }

    out_json = ROOT / args.out_json
    out_md = ROOT / args.out_md
    compare_md = ROOT / args.compare_md
    report_md = ROOT / args.report_md
    for path in [out_json, out_md, compare_md, report_md]:
        path.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    render_samples_md(out_md, rows35, meta35, tokenizer_hash)
    render_comparison_md(compare_md, prompts, rows25, rows35, comparisons)
    render_report(report_md, payload)
    print(
        f"done: winners 35k={counts.get('35k', 0)} "
        f"25k={counts.get('25k', 0)} tie={counts.get('tie', 0)} "
        f"verdict={payload['verdict']}"
    )


if __name__ == "__main__":
    main()
