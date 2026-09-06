#!/usr/bin/env python3
"""Finalize Glyph-100M SFT smoke v0.3 with training report and eval."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.eval_glyph100_sft_smoke_v0_1_fixedmask import (  # noqa: E402
    CONTINUATION_PROMPTS,
    continuation_score,
    diagnostic_score,
    instruction_prompt,
    load_model,
    select_device,
    target_score,
    words,
)
from scripts.glyph100_sft_v0_2_decoding_audit import (  # noqa: E402
    checkpoint_meta,
    compact_output,
    compare_model_tensors,
    repeated_kind,
    web_classification,
)
from scripts.sft_utils import END_TOKEN, load_jsonl, load_sentencepiece, normalize_space  # noqa: E402


MODES = {
    "greedy": {"temperature": 0.0, "top_k": None, "top_p": 1.0, "repetition_penalty": 1.0, "no_repeat_ngram_size": 0},
    "no_repeat_ngram_size_3": {"temperature": 0.7, "top_k": 40, "top_p": 1.0, "repetition_penalty": 1.0, "no_repeat_ngram_size": 3},
    "no_repeat_ngram_size_4": {"temperature": 0.7, "top_k": 40, "top_p": 1.0, "repetition_penalty": 1.0, "no_repeat_ngram_size": 4},
    "topk40_temp07": {"temperature": 0.7, "top_k": 40, "top_p": 1.0, "repetition_penalty": 1.0, "no_repeat_ngram_size": 0},
    "topk40_temp07_no_repeat_ngram_size_3": {"temperature": 0.7, "top_k": 40, "top_p": 1.0, "repetition_penalty": 1.0, "no_repeat_ngram_size": 3},
}

EXTRA_PROMPTS = [
    ("diag-anti-web-01", "anty_web_residue", "Odpowiedz bez stylu sklepu: czym jest backup?"),
    ("diag-anti-web-02", "anty_web_residue", "Wyjaśnij tokenizer bez marketingu i bez tekstu strony firmowej."),
    ("diag-anti-web-03", "anty_web_residue", "Napisz technicznie, bez reklamy: po co jest checkpoint?"),
    ("diag-anti-repeat-01", "anty_powtorzenia_i_konczenie", "Odpowiedz jednym zdaniem i nie powtarzaj: po co jest eval?"),
    ("diag-anti-repeat-02", "anty_powtorzenia_i_konczenie", "Zakończ po jednej myśli: kiedy odpowiedź jest kompletna?"),
    ("diag-anti-repeat-03", "anty_powtorzenia_i_konczenie", "Nie powtarzaj pierwszego słowa: czym jest smoke test?"),
    ("diag-missing-01", "brak_danych_bez_petli", "Czy ten laptop jest dobry? Nie podaję modelu."),
    ("diag-missing-02", "brak_danych_bez_petli", "Czy wynik jest poprawny? Nie podaję oczekiwanego wyniku."),
    ("diag-missing-03", "brak_danych_bez_petli", "Czy powinienem kontynuować trening? Nie podaję evala."),
    ("diag-tech-01", "techniczne_proste_wyjasnienia", "Czym różni się train loss od val loss?"),
    ("diag-tech-02", "techniczne_proste_wyjasnienia", "Czym jest gradient accumulation?"),
    ("diag-tech-03", "techniczne_proste_wyjasnienia", "Czym jest no-repeat ngram w generacji?"),
    ("diag-fact-01", "sanity_fakty_podstawowe", "Stolicą Polski jest"),
    ("diag-fact-02", "sanity_fakty_podstawowe", "Fakt różni się od opinii tym, że"),
    ("diag-fact-03", "sanity_fakty_podstawowe", "Kilometr to"),
    ("diag-daily-01", "codzienne_proste_pytania", "Napisz krótką wiadomość, że spóźnię się 10 minut."),
    ("diag-daily-02", "codzienne_proste_pytania", "Poproś krótko o ponowne przesłanie pliku."),
    ("diag-project-01", "mvp_first_project_advice", "Czy zaczynać projekt od UI czy od logiki?"),
    ("diag-project-02", "mvp_first_project_advice", "Czy robić od razu backend, frontend, dashboard i AI?"),
    ("diag-style-01", "not_in_dataset_style_generalization", "Czy ładna odpowiedź zawsze jest poprawna?"),
    ("diag-style-02", "not_in_dataset_style_generalization", "Czy SFT automatycznie dodaje modelowi wiedzę?"),
    ("diag-style-03", "not_in_dataset_style_generalization", "Kiedy lepiej powiedzieć, że brakuje danych?"),
]

STEP_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) safe step=\s*(?P<step>\d+)"
    r" \| loss=(?P<loss>[-+\d.]+) \| avg_loss=(?P<avg_loss>[-+\d.]+)"
    r" \| grad_norm=(?P<grad_norm>[-+\d.]+).* \| tok/s=(?P<toks>[-+\d.]+)"
)
EVAL_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) safe eval step=\s*(?P<step>\d+)"
    r" \| val_loss=(?P<val_loss>[-+\d.]+) \| batches=(?P<batches>\d+)"
)
FINAL_EVAL_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) safe final_eval step=\s*(?P<step>\d+)"
    r" \| val_loss=(?P<val_loss>[-+\d.]+) \| batches=(?P<batches>\d+)"
)


def read_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse_log(path: str) -> dict:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    steps = []
    evals = []
    final_eval = None
    checkpoints = []
    best_updates = []
    for line in lines:
        if match := STEP_RE.search(line):
            g = match.groupdict()
            steps.append(
                {
                    "ts": g["ts"],
                    "step": int(g["step"]),
                    "loss": float(g["loss"]),
                    "avg_loss": float(g["avg_loss"]),
                    "grad_norm": float(g["grad_norm"]),
                    "tokens_per_second": float(g["toks"]),
                }
            )
        elif match := EVAL_RE.search(line):
            g = match.groupdict()
            evals.append({"ts": g["ts"], "step": int(g["step"]), "val_loss": float(g["val_loss"]), "batches": int(g["batches"])})
        elif match := FINAL_EVAL_RE.search(line):
            g = match.groupdict()
            final_eval = {"ts": g["ts"], "step": int(g["step"]), "val_loss": float(g["val_loss"]), "batches": int(g["batches"])}
        if "safe checkpoint saved:" in line:
            checkpoints.append(line.split("safe checkpoint saved:", 1)[1].strip())
        if "safe best checkpoint updated:" in line:
            best_updates.append(line)
    losses = [row["loss"] for row in steps]
    toks = [row["tokens_per_second"] for row in steps]
    all_evals = evals + ([final_eval] if final_eval else [])
    return {
        "log_path": path,
        "steps_logged": len(steps),
        "first_step": steps[0] if steps else None,
        "last_step": steps[-1] if steps else None,
        "loss_start": losses[0] if losses else None,
        "loss_end": losses[-1] if losses else None,
        "avg_loss_end": steps[-1]["avg_loss"] if steps else None,
        "loss_min": min(losses) if losses else None,
        "loss_max": max(losses) if losses else None,
        "avg_tok_s": mean(toks) if toks else None,
        "max_grad_norm": max([row["grad_norm"] for row in steps]) if steps else None,
        "evals": evals,
        "final_eval": final_eval,
        "best_eval": min(all_evals, key=lambda row: row["val_loss"]) if all_evals else None,
        "checkpoint_saves": checkpoints,
        "best_updates_count": len(best_updates),
        "has_nan_or_inf": any("nan" in line.lower() or "inf" in line.lower() for line in lines),
        "has_oom_or_crash": any(any(needle in line.lower() for needle in ("out of memory", "oom", "traceback", "exception", "crash")) for line in lines),
    }


def build_rows(test_jsonl: str, train_jsonl: str, min_rows: int) -> list[dict]:
    rows = []
    test = load_jsonl(test_jsonl).records
    train = load_jsonl(train_jsonl).records
    for record in test:
        rows.append(
            {
                "kind": "target_instruction",
                "id": record.get("id"),
                "category": record.get("category", "unknown"),
                "instruction": record["instruction"],
                "response": record["response"],
            }
        )
    for row_id, category, instruction in EXTRA_PROMPTS:
        rows.append({"kind": "diagnostic_instruction", "id": row_id, "category": category, "instruction": instruction})
    for idx, prompt in enumerate(CONTINUATION_PROMPTS, 1):
        rows.append({"kind": "continuation", "id": f"cont-{idx:02d}", "category": "base_lm_sanity", "prompt": prompt})
    seen = {row.get("id") for row in rows}
    for record in train:
        if len(rows) >= min_rows:
            break
        if record.get("id") in seen:
            continue
        rows.append(
            {
                "kind": "target_instruction",
                "id": record.get("id"),
                "category": record.get("category", "unknown"),
                "instruction": record["instruction"],
                "response": record["response"],
            }
        )
    return rows[:min_rows]


@torch.no_grad()
def generate_one(model, sp, device: torch.device, prompt: str, mode: dict, max_new_tokens: int, seed: int) -> dict:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    ids = sp.encode(prompt, out_type=int)
    idx = torch.tensor([ids], dtype=torch.long, device=device)
    start = time.perf_counter()
    out = model.generate(
        idx,
        max_new_tokens=max_new_tokens,
        temperature=mode["temperature"],
        top_k=mode["top_k"],
        top_p=mode["top_p"],
        repetition_penalty=mode["repetition_penalty"],
        no_repeat_ngram_size=mode["no_repeat_ngram_size"],
    )
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    elapsed = time.perf_counter() - start
    new_ids = out[0, idx.shape[1] :].detach().cpu().tolist()
    raw_text = sp.decode(new_ids).strip()
    ended = END_TOKEN in raw_text
    text = raw_text.split(END_TOKEN, 1)[0].strip() if ended else raw_text
    return {"output": text, "raw_output": raw_text, "ended_by_end_token": ended, "seconds": elapsed, "generated_tokens": len(new_ids)}


def score_row(row: dict, output: str, ended: bool) -> dict:
    if row["kind"] == "target_instruction":
        return target_score(output, row["response"], ended, row["instruction"])
    if row["kind"] == "diagnostic_instruction":
        return diagnostic_score(row["category"], row["instruction"], output, ended)
    return continuation_score(row["prompt"], output)


def summarize(rows: list[dict], outputs: list[dict]) -> dict:
    scores = [row["score"]["score"] for row in outputs]
    instruction = [(row, out) for row, out in zip(rows, outputs, strict=True) if row["kind"] != "continuation"]
    target = [(row, out) for row, out in zip(rows, outputs, strict=True) if row["kind"] == "target_instruction"]
    return {
        "avg_score": mean(scores),
        "median_score": median(scores),
        "repetition_samples": sum(1 for out in outputs if out["score"].get("repetition_ngrams", 0) > 0),
        "end_token_rate": sum(1 for _, out in instruction if out["ended_by_end_token"]) / max(1, len(instruction)),
        "natural_endings": sum(1 for out in outputs if out["score"].get("natural_end")),
        "real_web_residue": sum(1 for out in outputs if out["score"].get("web_residue") and web_classification(out["output"]) == "real web residue"),
        "web_residue": sum(1 for out in outputs if out["score"].get("web_residue")),
        "pseudo_ency": sum(1 for out in outputs if out["score"].get("pseudo_ency")),
        "topic_drift": sum(1 for out in outputs if out["score"].get("prompt_overlap")),
        "generic_assistant_template": sum(1 for out in outputs if out["score"].get("generic_assistant_template")),
        "first_token_correct": sum(1 for _, out in target if out["score"].get("starts_with_target_first_word")),
        "avg_generated_tokens": mean([out["generated_tokens"] for out in outputs]),
        "too_short_answers": sum(1 for out in outputs if len(words(out["output"])) < 3),
        "too_long_answers": sum(1 for out in outputs if out["generated_tokens"] >= 78 and not out["ended_by_end_token"]),
    }


def choose_winner(a_score: int, b_score: int, a: str, b: str) -> str:
    if a_score >= b_score + 2:
        return a
    if b_score >= a_score + 2:
        return b
    return "tie"


def eval_all(rows: list[dict], checkpoints: dict[str, str], sp, device, max_new_tokens: int, seed: int) -> dict:
    results_by_model: dict[str, dict[str, list[dict]]] = {}
    states = {}
    for model_idx, (name, checkpoint) in enumerate(checkpoints.items()):
        print(f"model {name}", flush=True)
        model, state = load_model(checkpoint, device)
        states[name] = state
        model_modes = {}
        for mode_idx, (mode_name, mode) in enumerate(MODES.items()):
            print(f"  mode {mode_name}", flush=True)
            outputs = []
            for idx, row in enumerate(rows):
                prompt = instruction_prompt(row["instruction"]) if row["kind"] != "continuation" else row["prompt"]
                out = generate_one(model, sp, device, prompt, mode, max_new_tokens, seed + model_idx * 100000 + mode_idx * 10000 + idx)
                out["score"] = score_row(row, out["output"], out["ended_by_end_token"])
                outputs.append(out)
                if (idx + 1) % 50 == 0:
                    print(f"    {idx + 1}/{len(rows)}", flush=True)
            model_modes[mode_name] = outputs
        results_by_model[name] = model_modes
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()

    mode_summaries = {}
    for mode_name in MODES:
        model_stats = {name: summarize(rows, model_modes[mode_name]) for name, model_modes in results_by_model.items()}
        pairwise = {}
        for a, b in (
            ("sft_v0_3_best", "sft_v0_2"),
            ("sft_v0_3_best", "sft_v0_1"),
            ("sft_v0_3_best", "base44k"),
            ("sft_v0_3_best", "sft_v0_3_final"),
            ("sft_v0_3_final", "sft_v0_2"),
        ):
            counts = Counter()
            for idx in range(len(rows)):
                counts[
                    choose_winner(
                        results_by_model[a][mode_name][idx]["score"]["score"],
                        results_by_model[b][mode_name][idx]["score"]["score"],
                        a,
                        b,
                    )
                ] += 1
            pairwise[f"{a}_vs_{b}"] = dict(counts)
        mode_summaries[mode_name] = {"models": model_stats, "pairwise": pairwise}

    best_mode = max(
        mode_summaries,
        key=lambda mode: (
            mode_summaries[mode]["models"]["sft_v0_3_best"]["avg_score"]
            - 0.25 * mode_summaries[mode]["models"]["sft_v0_3_best"]["repetition_samples"]
            - 0.35 * mode_summaries[mode]["models"]["sft_v0_3_best"]["real_web_residue"]
            + 2.0 * mode_summaries[mode]["models"]["sft_v0_3_best"]["end_token_rate"]
        ),
    )

    detailed = []
    for idx, row in enumerate(rows):
        for mode_name in MODES:
            item = {**row, "mode": mode_name}
            for model_name in checkpoints:
                item[model_name] = results_by_model[model_name][mode_name][idx]
            detailed.append(item)
    return {
        "summary": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "rows": len(rows),
            "modes": MODES,
            "checkpoints": checkpoints,
            "checkpoint_steps": {name: states[name].get("current_step", states[name].get("step")) for name in states},
            "mode_summaries": mode_summaries,
            "best_mode": best_mode,
        },
        "results": detailed,
    }


def classify_worst(row: dict) -> dict:
    out = row["sft_v0_3_best"]
    score = out["score"]
    issues = []
    if score.get("repetition_ngrams", 0) > 0:
        issues.append(repeated_kind(out["output"]))
    if score.get("web_residue"):
        issues.append(web_classification(out["output"]))
    if score.get("pseudo_ency"):
        issues.append("pseudo-ency")
    if score.get("prompt_overlap"):
        issues.append("topic drift / prompt overlap")
    if score.get("generic_assistant_template"):
        issues.append("generic assistant template")
    if len(words(out["output"])) < 3:
        issues.append("too short")
    if out["generated_tokens"] >= 78 and not out["ended_by_end_token"]:
        issues.append("too long / no stop")
    if not issues:
        issues.append("low semantic score")
    return {"id": row.get("id"), "mode": row["mode"], "category": row["category"], "prompt": row.get("instruction") or row.get("prompt"), "score": score["score"], "issues": issues, "output": out["output"]}


def write_md(eval_payload: dict, path: str) -> None:
    s = eval_payload["summary"]
    lines = [
        "# Glyph-100M SFT smoke v0.3 before/after eval",
        "",
        "## Summary",
        "",
        f"- rows: `{s['rows']}`",
        f"- best mode: `{s['best_mode']}`",
        "",
    ]
    for mode, mode_summary in s["mode_summaries"].items():
        lines += [f"## Mode: {mode}", ""]
        for model, stats in mode_summary["models"].items():
            lines.append(
                f"- {model}: avg `{stats['avg_score']:.2f}`, median `{stats['median_score']:.2f}`, "
                f"rep `{stats['repetition_samples']}`, end `{stats['end_token_rate']:.2f}`, "
                f"real_web `{stats['real_web_residue']}`, pseudo `{stats['pseudo_ency']}`, first `{stats['first_token_correct']}`"
            )
        lines.append(f"- pairwise: `{mode_summary['pairwise']}`")
        lines.append("")
    best_mode = s["best_mode"]
    best_rows = [row for row in eval_payload["results"] if row["mode"] == best_mode]
    lines += [
        "## Highest-scoring 20 outputs by automated format heuristic",
        "",
        "> This ranking measures formatting, stopping and surface-level failure signals. "
        "Manual review found semantic errors even among high-scoring outputs, so it must not be read as a list of genuinely correct answers.",
        "",
    ]
    for idx, row in enumerate(sorted(best_rows, key=lambda row: row["sft_v0_3_best"]["score"]["score"], reverse=True)[:20], 1):
        lines += [f"### {idx}. {row['category']} · score={row['sft_v0_3_best']['score']['score']}", "", f"Prompt: {row.get('instruction') or row.get('prompt')}", "", compact_output(row["sft_v0_3_best"]["output"]), ""]
    lines += ["## Worst 20 v0.3 Best Outputs", ""]
    for idx, row in enumerate(sorted(best_rows, key=lambda row: row["sft_v0_3_best"]["score"]["score"])[:20], 1):
        cls = classify_worst(row)
        lines += [f"### {idx}. {row['category']} · score={cls['score']} · issues={cls['issues']}", "", f"Prompt: {cls['prompt']}", "", compact_output(cls["output"]) or "[empty]", ""]
    Path(path).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_train_report(train: dict, dataset_report: dict, md_path: str, json_path: str) -> None:
    payload = {"training": train, "dataset": dataset_report}
    Path(json_path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Glyph-100M SFT smoke v0.3 fixed-mask ROCm report",
        "",
        "## Status",
        "",
        "- run: `complete`",
        "- type: small SFT smoke v0.3, not SFT v1",
        "- base: `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`",
        "- output: `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_3-fixedmask-rocm`",
        "- 50k was not used as base.",
        "",
        "## Training",
        "",
        f"- logged steps: `{train['steps_logged']}`",
        f"- loss start/end: `{train['loss_start']}` -> `{train['loss_end']}`",
        f"- avg loss end: `{train['avg_loss_end']}`",
        f"- best val loss: `{train['best_eval']['val_loss']}` at step `{train['best_eval']['step']}`",
        f"- final val loss: `{train['final_eval']['val_loss']}` at step `{train['final_eval']['step']}`",
        f"- avg tok/s: `{train['avg_tok_s']:.1f}`",
        f"- max grad norm: `{train['max_grad_norm']}`",
        f"- NaN/Inf: `{train['has_nan_or_inf']}`",
        f"- OOM/crash: `{train['has_oom_or_crash']}`",
        "",
        "## Val Losses",
        "",
    ]
    for row in train["evals"]:
        lines.append(f"- step `{row['step']}`: `{row['val_loss']}`")
    lines.append(f"- final step `{train['final_eval']['step']}`: `{train['final_eval']['val_loss']}`")
    lines += [
        "",
        "## Dataset",
        "",
        f"- examples: `{dataset_report['stats']['examples']}`",
        f"- split: `{dataset_report['split_counts']}`",
        f"- max template tokens: `{dataset_report['stats']['token_stats']['template_max']}`",
        f"- label sanity: `{dataset_report['label_mask_sanity']['summary']}`",
    ]
    Path(md_path).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def make_decision(eval_payload: dict, train_report: dict) -> dict:
    best_mode = eval_payload["summary"]["best_mode"]
    stats = eval_payload["summary"]["mode_summaries"][best_mode]["models"]["sft_v0_3_best"]
    pair = eval_payload["summary"]["mode_summaries"][best_mode]["pairwise"]["sft_v0_3_best_vs_sft_v0_2"]
    v03_wins = pair.get("sft_v0_3_best", 0)
    v02_wins = pair.get("sft_v0_2", 0)
    criteria_a = {
        "avg_score_ge_6": stats["avg_score"] >= 6.0,
        "repetition_le_2": stats["repetition_samples"] <= 2,
        "end_rate_ge_95": stats["end_token_rate"] >= 0.95,
        "real_web_le_2": stats["real_web_residue"] <= 2,
        "v03_clear_vs_v02": v03_wins >= max(1, v02_wins * 1.5),
        "manual_semantic_review_pass": False,
    }
    if all(criteria_a.values()):
        verdict = "A"
        label = "v0.3 spełnia kryteria, można planować mały SFT v1"
        recommendation = "Można przygotować plan SFT v1, ale nie uruchamiać automatycznie."
    elif stats["avg_score"] > 5.0 and v03_wins >= v02_wins:
        verdict = "B"
        label = "v0.3 poprawia, ale nadal nie spełnia kryteriów"
        recommendation = "Nie rekomendować SFT v1; zamrozić SFT smoke jako research milestone albo zrobić punktowy dataset v0.4."
    elif v03_wins < v02_wins:
        verdict = "C"
        label = "v0.3 nie poprawia v0.2"
        recommendation = "Nie kontynuować SFT w tym kierunku."
    else:
        verdict = "E"
        label = "projekt zamrozić jako portfolio/research milestone"
        recommendation = "Bez mocniejszej bazy lub lepszego datasetu nie skalować."
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "label": label,
        "recommendation": recommendation,
        "criteria_a": criteria_a,
        "best_mode": best_mode,
        "best_mode_stats": stats,
        "v0_3_best_vs_v0_2": pair,
        "training_best_val": train_report["training"]["best_eval"],
        "manual_semantic_review": {
            "pass": False,
            "finding": "High automated scores still include factually or semantically wrong answers; format improved more than meaning.",
            "examples": [
                "Eval was incorrectly described as a graphics processor.",
                "A kilometre was incorrectly described as a projectile storing input data.",
                "Train loss and gradient accumulation definitions remained nonsensical.",
            ],
        },
        "constraints": [
            "No SFT v1 was run.",
            "No further training was run after v0.3 smoke.",
            "No pretraining was run.",
            "50k was not used as base.",
            "Model was not published as final.",
        ],
    }


def write_decision(decision: dict, md_path: str, json_path: str) -> None:
    Path(json_path).write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Glyph-100M SFT v0.3 next decision",
        "",
        "## Verdict",
        "",
        f"- verdict: `{decision['verdict']}`",
        f"- label: {decision['label']}",
        f"- recommendation: {decision['recommendation']}",
        "",
        "## Criteria A",
        "",
    ]
    for key, value in decision["criteria_a"].items():
        lines.append(f"- {key}: `{value}`")
    lines += [
        "",
        "## Evidence",
        "",
        f"- best mode: `{decision['best_mode']}`",
        f"- best mode stats: `{decision['best_mode_stats']}`",
        f"- v0.3 best vs v0.2: `{decision['v0_3_best_vs_v0_2']}`",
        f"- manual semantic review: `{decision['manual_semantic_review']}`",
        "",
        "## Constraints Honored",
        "",
    ]
    lines.extend(f"- {item}" for item in decision["constraints"])
    Path(md_path).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--base-checkpoint", default="checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt")
    parser.add_argument("--v01-checkpoint", default="checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm-latest.pt")
    parser.add_argument("--v02-checkpoint", default="checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm-best.pt")
    parser.add_argument("--v03-final-checkpoint", default="checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_3-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_3-fixedmask-rocm-final-step_000586.pt")
    parser.add_argument("--v03-best-checkpoint", default="checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_3-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_3-fixedmask-rocm-best.pt")
    parser.add_argument("--train-log", default="logs/glyph-100m-v2_3_1-44k-sft-smoke-v0_3-fixedmask-rocm/train.log")
    parser.add_argument("--dataset-report", default="data/sft/glyph100_sft_smoke_v0_3_report.json")
    parser.add_argument("--test-jsonl", default="data/sft/processed/glyph100_sft_smoke_v0_3_test.jsonl")
    parser.add_argument("--train-jsonl", default="data/sft/processed/glyph100_sft_smoke_v0_3_train.jsonl")
    parser.add_argument("--min-prompts", type=int, default=200)
    parser.add_argument("--max-new-tokens", type=int, default=80)
    parser.add_argument("--seed", type=int, default=2033)
    args = parser.parse_args()

    train = parse_log(args.train_log)
    dataset_report = read_json(args.dataset_report)
    write_train_report(
        train,
        dataset_report,
        "reports/glyph100_44k_sft_smoke_v0_3_fixedmask_rocm_report.md",
        "reports/glyph100_44k_sft_smoke_v0_3_fixedmask_rocm_report.json",
    )

    checkpoint_audit = {
        "base44k": checkpoint_meta(args.base_checkpoint),
        "sft_v0_1": checkpoint_meta(args.v01_checkpoint),
        "sft_v0_2": checkpoint_meta(args.v02_checkpoint),
        "sft_v0_3_final": checkpoint_meta(args.v03_final_checkpoint),
        "sft_v0_3_best": checkpoint_meta(args.v03_best_checkpoint),
        "v0_3_best_vs_final": compare_model_tensors(args.v03_best_checkpoint, args.v03_final_checkpoint),
    }
    rows = build_rows(args.test_jsonl, args.train_jsonl, args.min_prompts)
    sp = load_sentencepiece(args.tokenizer)
    device = select_device(args.device)
    checkpoints = {
        "base44k": args.base_checkpoint,
        "sft_v0_1": args.v01_checkpoint,
        "sft_v0_2": args.v02_checkpoint,
        "sft_v0_3_final": args.v03_final_checkpoint,
        "sft_v0_3_best": args.v03_best_checkpoint,
    }
    eval_payload = eval_all(rows, checkpoints, sp, device, args.max_new_tokens, args.seed)
    eval_payload["summary"]["checkpoint_audit"] = checkpoint_audit
    Path("eval/glyph-100m/sft_smoke_v0_3_fixedmask_before_after.json").write_text(json.dumps(eval_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_md(eval_payload, "eval/glyph-100m/sft_smoke_v0_3_fixedmask_before_after.md")

    worst_best_mode = [
        classify_worst(row)
        for row in sorted(
            [row for row in eval_payload["results"] if row["mode"] == eval_payload["summary"]["best_mode"]],
            key=lambda row: row["sft_v0_3_best"]["score"]["score"],
        )[:30]
    ]
    eval_payload["summary"]["manual_heuristic_worst_30"] = worst_best_mode
    Path("eval/glyph-100m/sft_smoke_v0_3_fixedmask_before_after.json").write_text(json.dumps(eval_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    train_report = read_json("reports/glyph100_44k_sft_smoke_v0_3_fixedmask_rocm_report.json")
    decision = make_decision(eval_payload, train_report)
    write_decision(
        decision,
        "reports/glyph100_sft_v0_3_next_decision.md",
        "reports/glyph100_sft_v0_3_next_decision.json",
    )
    print(json.dumps({"decision": decision, "best_mode": eval_payload["summary"]["best_mode"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
