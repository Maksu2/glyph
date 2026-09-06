#!/usr/bin/env python3
"""Compare Glyph-100M 10k vs v2.3.1 preflight 15k as base-LM continuations.

This script only runs inference. It does not train, mutate checkpoints or write
outside eval/reports outputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
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
    PRESETS,
    analyze_text,
    configure_attention_backend,
    generate_one,
    heuristic_score,
    load_model,
    load_tokenizer,
    qualitative_note,
    read_jsonl,
)


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
    "odkrył ją",
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
    score -= min(4, analysis.get("repeated_4grams", 0))
    if not row["new_text"].strip():
        score -= 5
    return score


def compare_rows(row10: dict, row15: dict) -> dict:
    s10 = quality_score(row10)
    s15 = quality_score(row15)
    delta = s15 - s10
    if delta >= 2:
        winner = "15k"
    elif delta <= -2:
        winner = "10k"
    else:
        winner = "tie"

    improvements = []
    regressions = []
    for key, label in [
        ("repeated_4grams", "powtórzenia"),
        ("url_count", "URL"),
        ("html_count", "HTML"),
    ]:
        a = row10["analysis"].get(key, 0)
        b = row15["analysis"].get(key, 0)
        if b < a:
            improvements.append(f"mniej {label}")
        elif b > a:
            regressions.append(f"więcej {label}")
    for bucket, label in [("wiki", "wiki residue"), ("web", "web residue"), ("pseudo_ency", "pseudo-ency")]:
        a = len(row10["residue_hits"][bucket])
        b = len(row15["residue_hits"][bucket])
        if b < a:
            improvements.append(f"mniej {label}")
        elif b > a:
            regressions.append(f"więcej {label}")
    if row15["analysis"].get("ends_naturally") and not row10["analysis"].get("ends_naturally"):
        improvements.append("naturalniejsze zakończenie")
    elif row10["analysis"].get("ends_naturally") and not row15["analysis"].get("ends_naturally"):
        regressions.append("gorsze zakończenie")

    return {
        "prompt_id": row15["prompt_id"],
        "category": row15["category"],
        "preset": row15["preset"],
        "score_10k": s10,
        "score_15k": s15,
        "delta": delta,
        "winner": winner,
        "improvements": improvements,
        "regressions": regressions,
    }


def load_checkpoint_metadata(path: Path) -> dict:
    state = torch.load(path, map_location="cpu", weights_only=False)
    train_config = state.get("train_config") or {}
    return {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "step": state.get("step") or state.get("current_step"),
        "current_step": state.get("current_step"),
        "variant": state.get("variant"),
        "model_config": state.get("model_config") or {},
        "tokenizer_path": state.get("tokenizer_path") or train_config.get("tokenizer_path"),
        "tokenizer_hash_in_checkpoint": state.get("tokenizer_hash"),
        "dataset_name": state.get("dataset_name") or train_config.get("dataset_name"),
        "dataset_metadata_path": state.get("dataset_metadata_path") or train_config.get("dataset_metadata_path"),
    }


def render_samples_md(path: Path, rows15: list[dict], meta15: dict, tokenizer_hash: str) -> None:
    lines = [
        "# Glyph-100M v2.3.1 preflight 15k samples",
        "",
        "Base LM completion eval. To nie jest eval asystenta ani instruction-following.",
        "",
        f"- checkpoint: `{meta15['path']}`",
        f"- step: `{meta15['step']}`",
        f"- variant: `{meta15['variant']}`",
        f"- tokenizer sha256: `{tokenizer_hash}`",
        "",
    ]
    for row in rows15:
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
                f"**Tok/s generation:** {row['tokens_per_second']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def render_comparison_md(path: Path, prompts: list[dict], rows10: list[dict], rows15: list[dict], comparisons: list[dict]) -> None:
    by10 = {(row["prompt_id"], row["preset"]): row for row in rows10}
    by15 = {(row["prompt_id"], row["preset"]): row for row in rows15}
    bycmp = {(row["prompt_id"], row["preset"]): row for row in comparisons}
    counts = Counter(row["winner"] for row in comparisons)
    lines = [
        "# Glyph-100M v2.3.1 preflight: 10k vs 15k",
        "",
        "Porównanie base LM completions. Model nie jest oceniany jako asystent.",
        "",
        "## Wynik heurystyczny",
        "",
        f"- 15k wins: {counts.get('15k', 0)}",
        f"- 10k wins: {counts.get('10k', 0)}",
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
                f"- 15k: {pc.get('15k', 0)}",
                f"- 10k: {pc.get('10k', 0)}",
                f"- tie: {pc.get('tie', 0)}",
                "",
            ]
        )

    lines.extend(["## Próbki do ręcznej inspekcji", ""])
    prompt_by_id = {row["id"]: row for row in prompts}
    for cmp_row in comparisons:
        pid = cmp_row["prompt_id"]
        preset = cmp_row["preset"]
        prompt = prompt_by_id.get(pid, {})
        row10 = by10[(pid, preset)]
        row15 = by15[(pid, preset)]
        lines.extend(
            [
                f"### {pid} · {prompt.get('category', row15['category'])} · {preset} · winner={cmp_row['winner']} · delta={cmp_row['delta']}",
                "",
                f"**Prompt:** `{row15['prompt']}`",
                "",
                f"**10k score:** {cmp_row['score_10k']} · **15k score:** {cmp_row['score_15k']}",
                "",
                f"**Poprawy:** {', '.join(cmp_row['improvements']) or 'brak wyraźnych'}",
                f"**Regresje:** {', '.join(cmp_row['regressions']) or 'brak wyraźnych'}",
                "",
                "**10k:**",
                "",
                "```text",
                row10["full_text"].strip(),
                "```",
                "",
                "**15k:**",
                "",
                "```text",
                row15["full_text"].strip(),
                "```",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


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
            "avg_quality_score": round(statistics.mean(quality_score(row) for row in preset_rows), 2),
        }
    return out


def verdict_from_counts(counts: Counter, rows15: list[dict]) -> str:
    total = sum(counts.values())
    wins15 = counts.get("15k", 0)
    wins10 = counts.get("10k", 0)
    residue15 = sum(1 for row in rows15 if row["residue_hits"]["web"] or row["residue_hits"]["wiki"])
    if wins15 >= max(1, int(total * 0.55)) and wins15 >= wins10 * 2 and residue15 <= total * 0.35:
        return "A"
    if wins15 > wins10:
        return "B"
    if wins10 > wins15:
        return "D"
    return "C"


def render_report(path: Path, payload: dict) -> None:
    counts = Counter(row["winner"] for row in payload["comparisons"])
    verdict = payload["verdict"]
    verdict_text = {
        "A": "15k wyraźnie lepsze, można rozważyć dalszy kontrolowany run do 25k.",
        "B": "15k trochę lepsze, ale najpierw poprawić dataset/eval.",
        "C": "Brak istotnej poprawy, nie trenować dalej bez dodatkowej decyzji.",
        "D": "Model pogorszył się / łapie residue, zatrzymać.",
    }[verdict]
    lines = [
        "# Glyph-100M v2.3.1 preflight report",
        "",
        "## Checkpointy",
        "",
        f"- 10k: `{payload['checkpoints']['10k']['path']}` · step `{payload['checkpoints']['10k']['step']}` · variant `{payload['checkpoints']['10k']['variant']}`",
        f"- 15k: `{payload['checkpoints']['15k']['path']}` · step `{payload['checkpoints']['15k']['step']}` · variant `{payload['checkpoints']['15k']['variant']}`",
        f"- tokenizer: `{payload['tokenizer']['path']}`",
        f"- tokenizer sha256: `{payload['tokenizer']['sha256']}`",
        "",
        "## Ustawienia generacji",
        "",
        "- base LM continuation, nie assistant/instruction eval",
        f"- seed base: `{payload['seed']}`",
        "- presety: conservative, normal, creative",
        "- max_new_tokens: 120",
        "",
        "## Wyniki",
        "",
        f"- 15k wins: {counts.get('15k', 0)}",
        f"- 10k wins: {counts.get('10k', 0)}",
        f"- ties: {counts.get('tie', 0)}",
        "",
        "## Summary 10k",
        "",
        "```json",
        json.dumps(payload["summaries"]["10k"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Summary 15k",
        "",
        "```json",
        json.dumps(payload["summaries"]["15k"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Werdykt",
        "",
        f"**{verdict}) {verdict_text}**",
        "",
        "## Uwagi jakościowe",
        "",
        "- Ten eval jest heurystyczny i jakościowy; najważniejsze próbki są w `eval/glyph-100m/v2_3_1_10k_vs_15k.md`.",
        "- Model nadal jest base LM, więc pseudo-encyklopedyczne completions nie są tym samym co odpowiedzi asystenta.",
        "- Dalszy trening wymaga osobnej zgody; ten raport nie uruchamia stage 3.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint-10k", default="checkpoints/glyph-100m/latest.pt")
    parser.add_argument("--checkpoint-15k", default="checkpoints/glyph-100m-v2_3_1-preflight/latest.pt")
    parser.add_argument("--prompts", default="eval/glyph-100m/stage2_completion_prompts.jsonl")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--attention-backend", default="math", choices=["sdpa", "math", "manual"])
    parser.add_argument("--seed", type=int, default=20260531)
    parser.add_argument("--max-new-tokens", type=int, default=120)
    parser.add_argument("--out-json", default="eval/glyph-100m/v2_3_1_preflight_15k_samples.json")
    parser.add_argument("--out-md", default="eval/glyph-100m/v2_3_1_preflight_15k_samples.md")
    parser.add_argument("--compare-md", default="eval/glyph-100m/v2_3_1_10k_vs_15k.md")
    parser.add_argument("--report-md", default="reports/glyph100_v2_3_1_preflight_report.md")
    args = parser.parse_args()

    device = torch.device("cuda" if args.device == "auto" and torch.cuda.is_available() else args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA/HIP requested but torch.cuda.is_available() is false")
    configure_attention_backend(args.attention_backend)

    prompts = read_jsonl(ROOT / args.prompts)
    tokenizer_path = ROOT / args.tokenizer
    tokenizer_hash = sha256(tokenizer_path)
    sp = load_tokenizer(tokenizer_path)
    presets = {
        name: {**settings, "max_new_tokens": args.max_new_tokens}
        for name, settings in PRESETS.items()
    }

    ckpt10 = ROOT / args.checkpoint_10k
    ckpt15 = ROOT / args.checkpoint_15k
    meta10 = load_checkpoint_metadata(ckpt10)
    meta15 = load_checkpoint_metadata(ckpt15)
    for label, meta, expected_step in [("10k", meta10, 10000), ("15k", meta15, 15000)]:
        if meta["variant"] != "glyph-100m":
            raise SystemExit(f"{label} checkpoint variant mismatch: {meta['variant']}")
        if int(meta["step"] or 0) != expected_step:
            raise SystemExit(f"{label} checkpoint step mismatch: {meta['step']} != {expected_step}")
        if meta["tokenizer_path"] != "data/processed/tokenizer.model":
            raise SystemExit(f"{label} tokenizer path mismatch: {meta['tokenizer_path']}")

    rows_by_checkpoint = {}
    for label, checkpoint, meta in [("10k", ckpt10, meta10), ("15k", ckpt15, meta15)]:
        model, state = load_model(checkpoint, device)
        rows = []
        for preset_name, settings in presets.items():
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

    comparisons = []
    rows10 = rows_by_checkpoint["10k"]
    rows15 = rows_by_checkpoint["15k"]
    by10 = {(row["prompt_id"], row["preset"]): row for row in rows10}
    for row15 in rows15:
        comparisons.append(compare_rows(by10[(row15["prompt_id"], row15["preset"])], row15))

    counts = Counter(row["winner"] for row in comparisons)
    payload = {
        "checkpoints": {"10k": meta10, "15k": meta15},
        "tokenizer": {"path": args.tokenizer, "sha256": tokenizer_hash},
        "device": str(device),
        "attention_backend": args.attention_backend,
        "seed": args.seed,
        "prompts_file": args.prompts,
        "prompt_count": len(prompts),
        "presets": presets,
        "summaries": {"10k": summarize_rows(rows10), "15k": summarize_rows(rows15)},
        "winner_counts": dict(counts),
        "verdict": verdict_from_counts(counts, rows15),
        "samples_10k": rows10,
        "samples_15k": rows15,
        "comparisons": comparisons,
    }

    out_json = ROOT / args.out_json
    out_md = ROOT / args.out_md
    compare_md = ROOT / args.compare_md
    report_md = ROOT / args.report_md
    for path in [out_json, out_md, compare_md, report_md]:
        path.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    render_samples_md(out_md, rows15, meta15, tokenizer_hash)
    render_comparison_md(compare_md, prompts, rows10, rows15, comparisons)
    render_report(report_md, payload)

    print(
        f"done: winners 15k={counts.get('15k', 0)} "
        f"10k={counts.get('10k', 0)} tie={counts.get('tie', 0)} "
        f"verdict={payload['verdict']}"
    )


if __name__ == "__main__":
    main()
