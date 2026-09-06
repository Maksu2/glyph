#!/usr/bin/env python3
"""Compare Glyph-100M v2.3.1 15k vs 25k as base-LM continuations.

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
    return {
        "path": str(path.relative_to(ROOT)),
        "step": state.get("step") or state.get("current_step"),
        "current_step": state.get("current_step"),
        "variant": state.get("variant"),
        "model_config": state.get("model_config") or {},
        "tokenizer_path": state.get("tokenizer_path") or train_config.get("tokenizer_path"),
        "tokenizer_sha256": state.get("tokenizer_sha256"),
        "dataset_name": state.get("dataset_name") or train_config.get("dataset_name"),
        "dataset_metadata_path": state.get("dataset_metadata_path") or train_config.get("dataset_metadata_path"),
    }


def compare_rows(row15: dict, row25: dict) -> dict:
    s15 = quality_score(row15)
    s25 = quality_score(row25)
    delta = s25 - s15
    if delta >= 2:
        winner = "25k"
    elif delta <= -2:
        winner = "15k"
    else:
        winner = "tie"

    improvements = []
    regressions = []
    for key, label in [
        ("repeated_4grams", "powtórzenia"),
        ("url_count", "URL"),
        ("html_count", "HTML"),
    ]:
        a = row15["analysis"].get(key, 0)
        b = row25["analysis"].get(key, 0)
        if b < a:
            improvements.append(f"mniej {label}")
        elif b > a:
            regressions.append(f"więcej {label}")
    for bucket, label in [("wiki", "wiki residue"), ("web", "web residue"), ("pseudo_ency", "pseudo-ency")]:
        a = len(row15["residue_hits"][bucket])
        b = len(row25["residue_hits"][bucket])
        if b < a:
            improvements.append(f"mniej {label}")
        elif b > a:
            regressions.append(f"więcej {label}")
    if row25["analysis"].get("ends_naturally") and not row15["analysis"].get("ends_naturally"):
        improvements.append("naturalniejsze zakończenie")
    elif row15["analysis"].get("ends_naturally") and not row25["analysis"].get("ends_naturally"):
        regressions.append("gorsze zakończenie")

    return {
        "prompt_id": row25["prompt_id"],
        "category": row25["category"],
        "preset": row25["preset"],
        "score_15k": s15,
        "score_25k": s25,
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


def render_samples_md(path: Path, rows25: list[dict], meta25: dict, tokenizer_hash: str) -> None:
    lines = [
        "# Glyph-100M v2.3.1 25k samples",
        "",
        "Base LM completion eval. To nie jest eval asystenta ani instruction-following.",
        "",
        f"- checkpoint: `{meta25['path']}`",
        f"- step: `{meta25['step']}`",
        f"- variant: `{meta25['variant']}`",
        f"- dataset: `{meta25['dataset_name']}`",
        f"- tokenizer sha256: `{tokenizer_hash}`",
        "",
    ]
    for row in rows25:
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


def render_comparison_md(path: Path, prompts: list[dict], rows15: list[dict], rows25: list[dict], comparisons: list[dict]) -> None:
    by15 = {(row["prompt_id"], row["preset"]): row for row in rows15}
    by25 = {(row["prompt_id"], row["preset"]): row for row in rows25}
    counts = Counter(row["winner"] for row in comparisons)
    lines = [
        "# Glyph-100M v2.3.1: 15k vs 25k",
        "",
        "Porównanie base LM completions. Model nie jest oceniany jako asystent.",
        "",
        "## Wynik heurystyczny",
        "",
        f"- 25k wins: {counts.get('25k', 0)}",
        f"- 15k wins: {counts.get('15k', 0)}",
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
                f"- 25k: {pc.get('25k', 0)}",
                f"- 15k: {pc.get('15k', 0)}",
                f"- tie: {pc.get('tie', 0)}",
                "",
            ]
        )

    prompt_by_id = {row["id"]: row for row in prompts}
    lines.extend(["## Próbki do ręcznej inspekcji", ""])
    for cmp_row in comparisons:
        pid = cmp_row["prompt_id"]
        preset = cmp_row["preset"]
        row15 = by15[(pid, preset)]
        row25 = by25[(pid, preset)]
        prompt = prompt_by_id.get(pid, {})
        lines.extend(
            [
                f"### {pid} · {prompt.get('category', row25['category'])} · {preset} · winner={cmp_row['winner']} · delta={cmp_row['delta']}",
                "",
                f"**Prompt:** `{row25['prompt']}`",
                "",
                f"**15k score:** {cmp_row['score_15k']} · **25k score:** {cmp_row['score_25k']}",
                "",
                f"**Poprawy:** {', '.join(cmp_row['improvements']) or 'brak wyraźnych'}",
                f"**Regresje:** {', '.join(cmp_row['regressions']) or 'brak wyraźnych'}",
                "",
                "**15k:**",
                "",
                "```text",
                row15["full_text"].strip(),
                "```",
                "",
                "**25k:**",
                "",
                "```text",
                row25["full_text"].strip(),
                "```",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def verdict_from_counts(counts: Counter, rows25: list[dict]) -> str:
    total = sum(counts.values())
    wins25 = counts.get("25k", 0)
    wins15 = counts.get("15k", 0)
    residue25 = sum(1 for row in rows25 if row["residue_hits"]["web"] or row["residue_hits"]["wiki"])
    repetition25 = sum(1 for row in rows25 if row["analysis"]["repeated_4grams"] > 0)
    if wins25 >= int(total * 0.55) and wins25 >= wins15 * 2 and residue25 <= total * 0.25:
        return "A"
    if wins25 > wins15 and repetition25 <= total * 0.35:
        return "C"
    if wins15 > wins25:
        return "D"
    return "C"


def render_report(path: Path, payload: dict) -> None:
    counts = Counter(row["winner"] for row in payload["comparisons"])
    verdict = payload["verdict"]
    verdict_text = {
        "A": "25k jest wyraźnie lepsze, można kontynuować do 35k.",
        "B": "25k jest wyraźnie lepsze i stabilne, można rozważyć 50k.",
        "C": "25k trochę lepsze, ale lepiej najpierw zrobić 35k jako kolejny punkt kontrolny.",
        "D": "Brak poprawy, nie trenować dalej na tym datasecie.",
        "E": "Model pogorszył się lub łapie za dużo pseudo-ency/web residue.",
        "F": "Warto zatrzymać pretraining i zrobić mały SFT eksperyment później.",
    }[verdict]
    lines = [
        "# Glyph-100M v2.3.1 25k eval report",
        "",
        "## Checkpointy",
        "",
        f"- 15k: `{payload['checkpoints']['15k']['path']}` · step `{payload['checkpoints']['15k']['step']}` · variant `{payload['checkpoints']['15k']['variant']}`",
        f"- 25k: `{payload['checkpoints']['25k']['path']}` · step `{payload['checkpoints']['25k']['step']}` · variant `{payload['checkpoints']['25k']['variant']}`",
        f"- tokenizer: `{payload['tokenizer']['path']}`",
        f"- tokenizer sha256: `{payload['tokenizer']['sha256']}`",
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
        f"- 25k wins: {counts.get('25k', 0)}",
        f"- 15k wins: {counts.get('15k', 0)}",
        f"- ties: {counts.get('tie', 0)}",
        "",
        "## Summary 15k",
        "",
        "```json",
        json.dumps(payload["summaries"]["15k"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Summary 25k",
        "",
        "```json",
        json.dumps(payload["summaries"]["25k"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Werdykt",
        "",
        f"**{verdict}) {verdict_text}**",
        "",
        "## Uwagi",
        "",
        "- To nadal base LM, więc porównanie mierzy kontynuacje tekstu, nie odpowiedzi asystenta.",
        "- Najważniejsze są próbki w `eval/glyph-100m/v2_3_1_15k_vs_25k.md`.",
        "- Ten raport nie uruchamia kolejnego treningu.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint-15k", default="checkpoints/glyph-100m-v2_3_1-preflight/latest.pt")
    parser.add_argument("--checkpoint-25k", default="checkpoints/glyph-100m-v2_3_1-25k/latest.pt")
    parser.add_argument("--prompts", default="eval/glyph-100m/stage2_completion_prompts.jsonl")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--attention-backend", default="math", choices=["sdpa", "math", "manual"])
    parser.add_argument("--seed", type=int, default=20260608)
    parser.add_argument("--out-json", default="eval/glyph-100m/v2_3_1_25k_samples.json")
    parser.add_argument("--out-md", default="eval/glyph-100m/v2_3_1_25k_samples.md")
    parser.add_argument("--compare-md", default="eval/glyph-100m/v2_3_1_15k_vs_25k.md")
    parser.add_argument("--report-md", default="reports/glyph100_v2_3_1_25k_eval_report.md")
    args = parser.parse_args()

    device = torch.device("cuda" if args.device == "auto" and torch.cuda.is_available() else args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA/HIP requested but torch.cuda.is_available() is false")
    configure_attention_backend(args.attention_backend)

    prompts = read_jsonl(ROOT / args.prompts)
    tokenizer_path = ROOT / args.tokenizer
    tokenizer_hash = sha256(tokenizer_path)
    sp = load_tokenizer(tokenizer_path)

    ckpt15 = ROOT / args.checkpoint_15k
    ckpt25 = ROOT / args.checkpoint_25k
    meta15 = load_checkpoint_metadata(ckpt15)
    meta25 = load_checkpoint_metadata(ckpt25)
    for label, meta, expected_step in [("15k", meta15, 15000), ("25k", meta25, 25000)]:
        if meta["variant"] != "glyph-100m":
            raise SystemExit(f"{label} checkpoint variant mismatch: {meta['variant']}")
        if int(meta["step"] or 0) != expected_step:
            raise SystemExit(f"{label} checkpoint step mismatch: {meta['step']} != {expected_step}")
        if meta["tokenizer_path"] != "data/processed/tokenizer.model":
            raise SystemExit(f"{label} tokenizer path mismatch: {meta['tokenizer_path']}")

    rows_by_checkpoint = {}
    for label, checkpoint, meta in [("15k", ckpt15, meta15), ("25k", ckpt25, meta25)]:
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

    rows15 = rows_by_checkpoint["15k"]
    rows25 = rows_by_checkpoint["25k"]
    by15 = {(row["prompt_id"], row["preset"]): row for row in rows15}
    comparisons = [compare_rows(by15[(row25["prompt_id"], row25["preset"])], row25) for row25 in rows25]
    counts = Counter(row["winner"] for row in comparisons)

    payload = {
        "checkpoints": {"15k": meta15, "25k": meta25},
        "tokenizer": {"path": args.tokenizer, "sha256": tokenizer_hash},
        "device": str(device),
        "attention_backend": args.attention_backend,
        "seed": args.seed,
        "prompts_file": args.prompts,
        "prompt_count": len(prompts),
        "presets": PRESETS,
        "summaries": {"15k": summarize_rows(rows15), "25k": summarize_rows(rows25)},
        "winner_counts": dict(counts),
        "verdict": verdict_from_counts(counts, rows25),
        "samples_15k": rows15,
        "samples_25k": rows25,
        "comparisons": comparisons,
    }

    out_json = ROOT / args.out_json
    out_md = ROOT / args.out_md
    compare_md = ROOT / args.compare_md
    report_md = ROOT / args.report_md
    for path in [out_json, out_md, compare_md, report_md]:
        path.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    render_samples_md(out_md, rows25, meta25, tokenizer_hash)
    render_comparison_md(compare_md, prompts, rows15, rows25, comparisons)
    render_report(report_md, payload)
    print(
        f"done: winners 25k={counts.get('25k', 0)} "
        f"15k={counts.get('15k', 0)} tie={counts.get('tie', 0)} "
        f"verdict={payload['verdict']}"
    )


if __name__ == "__main__":
    main()
