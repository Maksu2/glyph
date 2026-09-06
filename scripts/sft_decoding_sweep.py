#!/usr/bin/env python3
"""Decoding sweep for Glyph-27M SFT v0.

This does not train anything. It loads one SFT checkpoint and compares named
sampling presets on a fixed diagnostic prompt set.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import Counter
from dataclasses import asdict
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.eval_base_vs_sft import (
    END_TOKEN,
    GenerationSettings,
    generate_ids,
    load_model,
    load_sentencepiece,
    make_prompt,
    score_output,
    select_device,
)
from scripts.eval_base_vs_sft_v2 import score_output_v2


SWEEP_PROMPTS = [
    ("brak_danych", "Czy ten laptop jest dobry?"),
    ("brak_danych", "Czy powinienem to kupić?"),
    ("brak_danych", "Czy to jest bezpieczne?"),
    ("pisanie_i_poprawianie", "Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób."),
    ("pisanie_i_poprawianie", "Popraw tekst, żeby brzmiał naturalniej: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie."),
    ("pisanie_i_poprawianie", "Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj."),
    ("streszczanie", "Streść w jednym zdaniu: Duże projekty często upadają nie dlatego, że są niemożliwe, ale dlatego, że zaczynają się od zbyt szerokiego zakresu."),
    ("streszczanie", "Wyciągnij najważniejszą myśl: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem."),
    ("proste_wyjasnienia", "Wyjaśnij prosto, czym różni się pogoda od klimatu."),
    ("proste_wyjasnienia", "Wyjaśnij, czym jest inflacja."),
    ("proste_wyjasnienia", "Czym różni się fakt od opinii?"),
    ("decyzje_projektowe", "Mam zacząć projekt od UI czy od logiki?"),
    ("korekta_zalozen", "Popraw błędne założenie: jeśli projekt używa AI, to automatycznie jest bardziej zaawansowany."),
    ("techniczne_proste", "Czym jest backup?"),
    ("anty_petle", "Odpowiedz krótko: czego nie da się ocenić bez danych?"),
    ("anty_petle", "Odpowiedz krótko i zakończ po jednej myśli: co zrobić, gdy brakuje informacji?"),
]


PRESETS = {
    "strict_short": {
        "temperature": 0.45,
        "top_k": 20,
        "top_p": 0.85,
        "repetition_penalty": 1.20,
        "max_new_tokens": 60,
    },
    "strict_medium": {
        "temperature": 0.55,
        "top_k": 30,
        "top_p": 0.90,
        "repetition_penalty": 1.20,
        "max_new_tokens": 80,
    },
    "balanced_low_temp": {
        "temperature": 0.65,
        "top_k": 30,
        "top_p": 0.90,
        "repetition_penalty": 1.15,
        "max_new_tokens": 80,
    },
    "balanced_current": {
        "temperature": 0.75,
        "top_k": 40,
        "top_p": 0.92,
        "repetition_penalty": 1.15,
        "max_new_tokens": 120,
    },
    "anti_repeat": {
        "temperature": 0.55,
        "top_k": 20,
        "top_p": 0.85,
        "repetition_penalty": 1.25,
        "max_new_tokens": 80,
    },
    "strict_100": {
        "temperature": 0.45,
        "top_k": 30,
        "top_p": 0.90,
        "repetition_penalty": 1.20,
        "max_new_tokens": 100,
    },
    "low_temp_k40": {
        "temperature": 0.55,
        "top_k": 40,
        "top_p": 0.92,
        "repetition_penalty": 1.15,
        "max_new_tokens": 80,
    },
    "mid_temp_anti_repeat": {
        "temperature": 0.65,
        "top_k": 20,
        "top_p": 0.85,
        "repetition_penalty": 1.25,
        "max_new_tokens": 80,
    },
    "balanced_100": {
        "temperature": 0.65,
        "top_k": 40,
        "top_p": 0.92,
        "repetition_penalty": 1.20,
        "max_new_tokens": 100,
    },
    "creative_controlled": {
        "temperature": 0.75,
        "top_k": 30,
        "top_p": 0.90,
        "repetition_penalty": 1.25,
        "max_new_tokens": 100,
    },
}


def settings_from_preset(name: str, seed: int) -> GenerationSettings:
    values = PRESETS[name]
    return GenerationSettings(
        temperature=values["temperature"],
        top_k=values["top_k"],
        top_p=values["top_p"],
        max_new_tokens=values["max_new_tokens"],
        repetition_penalty=values["repetition_penalty"],
        seed=seed,
    )


def run_preset(name: str, model, cfg, sp, device: torch.device, seed: int) -> dict:
    settings = settings_from_preset(name, seed)
    end_id = sp.piece_to_id(END_TOKEN)
    if end_id < 0:
        end_id = None
    rows = []
    started = time.perf_counter()
    for index, (category, prompt) in enumerate(SWEEP_PROMPTS, 1):
        torch.manual_seed(settings.seed + index)
        if device.type == "cuda":
            torch.cuda.manual_seed_all(settings.seed + index)
        prompt_ids = sp.encode(make_prompt(prompt), out_type=int)
        prompt_ids = prompt_ids[-(cfg.context_len - 1) :]
        input_ids = torch.tensor([prompt_ids], dtype=torch.long, device=device)
        ids, ended_by_end, duration = generate_ids(model, input_ids, settings, end_id)
        output = sp.decode(ids).replace("<|user|>", "").replace("<|assistant|>", "").replace("<|end|>", "").strip()
        old = score_output(category, prompt, output, ended_by_end, len(ids), settings.max_new_tokens)
        score = score_output_v2(category, prompt, output, old)
        rows.append(
            {
                "index": index,
                "category": category,
                "prompt": prompt,
                "output": output,
                "generated_tokens": len(ids),
                "duration_seconds": duration,
                "tokens_per_second": len(ids) / duration if duration > 0 else None,
                "ended_by_end": ended_by_end,
                "score": score,
            }
        )
        print(
            f"{name} {index:02d}/{len(SWEEP_PROMPTS)} sem={score['semantic_relevance']} "
            f"task={score['task_completion']} rep={score['repetition']}",
            flush=True,
        )
    return {
        "name": name,
        "settings": asdict(settings),
        "duration_seconds": time.perf_counter() - started,
        "rows": rows,
        "summary": summarize_preset(rows),
    }


def summarize_preset(rows: list[dict]) -> dict:
    sem = [row["score"]["semantic_relevance"] for row in rows]
    task = [row["score"]["task_completion"] for row in rows]
    coherence = [row["score"]["coherence"] for row in rows]
    phrases = Counter()
    for row in rows:
        phrases.update(row["score"].get("sft_phrase_counts") or {})
    usable = [
        row
        for row in rows
        if row["score"]["semantic_relevance"] >= 2
        and row["score"]["task_completion"] >= 2
        and row["score"]["repetition"] <= 1
        and row["score"]["web_garbage_score"] == 0
        and not row["score"]["question_echo"]
    ]
    weak = [row for row in rows if row["score"]["semantic_relevance"] <= 1 or row["score"]["task_completion"] <= 1]
    repeated = [row for row in rows if row["score"]["repetition"] >= 2]
    drift = [row for row in rows if row["score"]["project_advice_drift"]]
    score = (
        len(usable) * 10
        + statistics.mean(sem) * 3
        + statistics.mean(task) * 3
        + statistics.mean(coherence)
        - len(repeated) * 2
        - len(drift) * 1.5
        - sum(phrases.values()) * 0.4
        - len(weak) * 2
    )
    return {
        "usable_count": len(usable),
        "weak_count": len(weak),
        "repetition_count": len(repeated),
        "project_advice_drift_count": len(drift),
        "question_echo_count": sum(1 for row in rows if row["score"]["question_echo"]),
        "ended_by_end_count": sum(1 for row in rows if row["score"]["ended_by_end"]),
        "avg_semantic_relevance": round(statistics.mean(sem), 3),
        "avg_task_completion": round(statistics.mean(task), 3),
        "avg_coherence": round(statistics.mean(coherence), 3),
        "avg_generated_tokens": round(statistics.mean(row["generated_tokens"] for row in rows), 3),
        "avg_tokens_per_second": round(statistics.mean(row["tokens_per_second"] or 0 for row in rows), 3),
        "sft_phrase_counts": dict(phrases),
        "preset_score": round(score, 3),
    }


def render_markdown(results: list[dict], best_name: str, demo_name: str) -> str:
    lines = [
        "# Glyph-27M SFT v0 decoding sweep",
        "",
        "This sweep tests decoding settings only. No training was run.",
        "",
        f"- prompts: {len(SWEEP_PROMPTS)}",
        f"- presets: {len(results)}",
        f"- best overall preset: `{best_name}`",
        f"- recommended public-demo preset: `{demo_name}`",
        "",
        "## Summary",
        "",
        "| preset | usable | weak | repeat | drift | avg_sem | avg_task | avg_tok | score |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in sorted(results, key=lambda row: row["summary"]["preset_score"], reverse=True):
        s = item["summary"]
        lines.append(
            f"| `{item['name']}` | {s['usable_count']} | {s['weak_count']} | {s['repetition_count']} | "
            f"{s['project_advice_drift_count']} | {s['avg_semantic_relevance']:.2f} | "
            f"{s['avg_task_completion']:.2f} | {s['avg_generated_tokens']:.1f} | {s['preset_score']:.1f} |"
        )
    lines += ["", "## Prompt-level outputs", ""]
    for item in results:
        lines += [
            f"## Preset: {item['name']}",
            "",
            f"Settings: `{json.dumps(item['settings'], ensure_ascii=False)}`",
            "",
        ]
        for row in item["rows"]:
            score = row["score"]
            lines += [
                f"### {row['index']:02d}. {row['category']}",
                "",
                f"Prompt: {row['prompt']}",
                "",
                row["output"] or "(empty)",
                "",
                f"Score: sem={score['semantic_relevance']} task={score['task_completion']} "
                f"coh={score['coherence']} rep={score['repetition']} can_win={score['can_win']}",
                "",
            ]
    return "\n".join(lines)


def render_summary(results: list[dict], best_name: str, demo_name: str) -> str:
    best = next(item for item in results if item["name"] == best_name)
    demo = next(item for item in results if item["name"] == demo_name)
    current = next((item for item in results if item["name"] == "balanced_current"), None)
    strict = next((item for item in results if item["name"] == "strict_medium"), None)
    lines = [
        "# Glyph-27M SFT v0 decoding sweep summary",
        "",
        f"- best overall preset: `{best_name}`",
        f"- best public-demo preset: `{demo_name}`",
        f"- best usable outputs: {best['summary']['usable_count']}/{len(SWEEP_PROMPTS)}",
        f"- demo usable outputs: {demo['summary']['usable_count']}/{len(SWEEP_PROMPTS)}",
        "",
        "## Read",
        "",
    ]
    if current and strict:
        current_s = current["summary"]
        strict_s = strict["summary"]
        direction = "helped" if strict_s["usable_count"] > current_s["usable_count"] else "did not help on its own"
        lines.append(
            f"- Lower temperature {direction} if `strict_medium` vs `balanced_current` is used as the comparison: "
            f"usable {strict_s['usable_count']} vs {current_s['usable_count']}, "
            f"weak {strict_s['weak_count']} vs {current_s['weak_count']}."
        )
    anti = next((item for item in results if item["name"] == "anti_repeat"), None)
    if anti:
        lines.append(
            f"- Higher repetition penalty in `anti_repeat` produced usable={anti['summary']['usable_count']} "
            f"and repetition_count={anti['summary']['repetition_count']}."
        )
    short = next((item for item in results if item["name"] == "strict_short"), None)
    if short:
        lines.append(
            f"- max_new_tokens=60 reduced length to avg {short['summary']['avg_generated_tokens']:.1f} tokens, "
            f"but weak outputs remained {short['summary']['weak_count']}."
        )
    lines += [
        "",
        "## Recommendation",
        "",
        f"Use `{demo_name}` for public-facing SFT v0 generation if SFT v0 must be exposed. "
        "It is more conservative than the previous preset, but decoding does not fix the core dataset/style problems.",
        "",
        "## Cases decoding does not fix",
        "",
    ]
    weak_rows = [row for row in demo["rows"] if row["score"]["semantic_relevance"] <= 1 or row["score"]["task_completion"] <= 1]
    for row in weak_rows[:8]:
        lines.append(f"- {row['index']:02d}. `{row['category']}`: {row['prompt']}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SFT v0 decoding sweep")
    parser.add_argument("--checkpoint", default="checkpoints/sft-v0/glyph-27m-sft-v0-final.pt")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--out-dir", default="eval/sft-v0")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    device = select_device(args.device)
    sp = load_sentencepiece(args.tokenizer)
    model, cfg = load_model(args.checkpoint, device)
    results = []
    for name in PRESETS:
        print(f"=== preset {name} ===", flush=True)
        results.append(run_preset(name, model, cfg, sp, device, args.seed))
    del model
    if device.type == "cuda":
        torch.cuda.empty_cache()

    best_name = max(results, key=lambda item: item["summary"]["preset_score"])["name"]
    demo_candidates = [item for item in results if item["summary"]["avg_generated_tokens"] <= 85]
    demo_name = max(demo_candidates or results, key=lambda item: item["summary"]["preset_score"])["name"]
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "checkpoint": args.checkpoint,
        "prompt_count": len(SWEEP_PROMPTS),
        "best_overall_preset": best_name,
        "recommended_demo_preset": demo_name,
        "results": results,
    }
    (out / "decoding_sweep.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "decoding_sweep.md").write_text(render_markdown(results, best_name, demo_name), encoding="utf-8")
    (out / "decoding_sweep_summary.md").write_text(render_summary(results, best_name, demo_name), encoding="utf-8")
    print(f"Wrote {out / 'decoding_sweep_summary.md'}")
    print(json.dumps({"best": best_name, "demo": demo_name}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
