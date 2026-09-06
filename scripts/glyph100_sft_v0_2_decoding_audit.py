#!/usr/bin/env python3
"""SFT v0.2 error audit, decoding sweep and next-step decision."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter, defaultdict
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
from scripts.sft_utils import END_TOKEN, load_jsonl, load_sentencepiece, normalize_space  # noqa: E402


DECODING_MODES = {
    "greedy": {
        "temperature": 0.0,
        "top_k": None,
        "top_p": 1.0,
        "repetition_penalty": 1.0,
        "no_repeat_ngram_size": 0,
    },
    "greedy_repetition_penalty_1_1": {
        "temperature": 0.0,
        "top_k": None,
        "top_p": 1.0,
        "repetition_penalty": 1.1,
        "no_repeat_ngram_size": 0,
    },
    "greedy_repetition_penalty_1_2": {
        "temperature": 0.0,
        "top_k": None,
        "top_p": 1.0,
        "repetition_penalty": 1.2,
        "no_repeat_ngram_size": 0,
    },
    "topk40_temp07": {
        "temperature": 0.7,
        "top_k": 40,
        "top_p": 1.0,
        "repetition_penalty": 1.0,
        "no_repeat_ngram_size": 0,
    },
    "topk40_temp07_repetition_penalty_1_1": {
        "temperature": 0.7,
        "top_k": 40,
        "top_p": 1.0,
        "repetition_penalty": 1.1,
        "no_repeat_ngram_size": 0,
    },
    "topk40_temp08_repetition_penalty_1_15": {
        "temperature": 0.8,
        "top_k": 40,
        "top_p": 1.0,
        "repetition_penalty": 1.15,
        "no_repeat_ngram_size": 0,
    },
    "no_repeat_ngram_size_3": {
        "temperature": 0.7,
        "top_k": 40,
        "top_p": 1.0,
        "repetition_penalty": 1.0,
        "no_repeat_ngram_size": 3,
    },
    "no_repeat_ngram_size_4": {
        "temperature": 0.7,
        "top_k": 40,
        "top_p": 1.0,
        "repetition_penalty": 1.0,
        "no_repeat_ngram_size": 4,
    },
}

EXTRA_DIAGNOSTICS = [
    ("anti-repeat-01", "anty_powtorzenia_i_konczenie", "Odpowiedz jednym zdaniem i nie powtarzaj: czym jest checkpoint?"),
    ("anti-repeat-02", "anty_powtorzenia_i_konczenie", "Zakończ po jednej myśli: co zrobić, gdy brakuje danych?"),
    ("anti-repeat-03", "anty_powtorzenia_i_konczenie", "Nie powtarzaj frazy: czy warto trenować dalej bez evala?"),
    ("anti-repeat-04", "anty_powtorzenia_i_konczenie", "Odpowiedz krótko i zakończ: dlaczego pętla w odpowiedzi jest zła?"),
    ("missing-01", "brak_danych", "Czy ten wynik jest dobry, jeśli nie podałem kryteriów?"),
    ("missing-02", "brak_danych", "Czy ta konfiguracja jest bezpieczna? Nie podaję szczegółów."),
    ("missing-03", "brak_danych", "Czy powinienem kupić ten sprzęt? Nie podałem modelu ani ceny."),
    ("missing-04", "brak_danych", "Czy moja odpowiedź jest dobra? Nie pokazuję odpowiedzi."),
    ("tech-01", "proste_techniczne_wyjasnienia", "Wyjaśnij krótko, po co zapisuje się best checkpoint."),
    ("tech-02", "proste_techniczne_wyjasnienia", "Czym różni się eval jakościowy od samego val loss?"),
    ("tech-03", "proste_techniczne_wyjasnienia", "Czym jest batch size w treningu modelu?"),
    ("tech-04", "proste_techniczne_wyjasnienia", "Czym jest tokenizer? Odpowiedz prosto."),
    ("daily-01", "codzienne_proste_pytania", "Jak krótko odmówić spotkania bez tłumaczenia się?"),
    ("daily-02", "codzienne_proste_pytania", "Napisz krótką wiadomość, że spóźnię się 10 minut."),
    ("daily-03", "codzienne_proste_pytania", "Jak poprosić o przesłanie pliku jeszcze raz?"),
    ("rewrite-01", "krotkie_poprawki_tekstu", "Popraw tekst: Zostało wykonane przeprowadzenie testu działania modelu."),
    ("rewrite-02", "krotkie_poprawki_tekstu", "Popraw tekst: W mojej opinii uważam, że to jest najlepsze."),
    ("summary-01", "mini_streszczenia", "Streść: Model może mieć niższy loss, ale nadal generować gorsze odpowiedzi w praktycznym eval."),
    ("project-01", "mvp_first_project_advice", "Czy ładny dashboard oznacza, że eksperyment jest dobry?"),
    ("project-02", "mvp_first_project_advice", "Czy warto zaczynać projekt od największej możliwej wersji?"),
    ("uncertain-01", "ostrozne_odpowiedzi_przy_niepewnosci", "Odpowiedz ostrożnie: czy warto publikować eksperymentalny model?"),
    ("uncertain-02", "ostrozne_odpowiedzi_przy_niepewnosci", "Co zrobić, gdy sample wygląda dziwnie?"),
    ("outside-01", "not_in_dataset", "Czy krótsza odpowiedź zawsze jest lepsza?"),
    ("outside-02", "not_in_dataset", "Kiedy lepiej napisać 'nie wiem' zamiast zgadywać?"),
    ("outside-03", "not_in_dataset", "Czym różni się poprawa stylu od dodania wiedzy?"),
    ("outside-04", "not_in_dataset", "Napisz jedno zdanie o tym, po co robi się smoke test."),
    ("outside-05", "not_in_dataset", "Czy model po SFT automatycznie zna więcej faktów?"),
    ("outside-06", "not_in_dataset", "Jak rozpoznać, że odpowiedź zaczyna odpływać od tematu?"),
]

WEB_REAL_PATTERNS = [
    "cookies",
    "dodaj do koszyka",
    "kup teraz",
    "zaloguj",
    "zarejestruj",
    "polityka prywatności",
    "strona główna",
    "komentarze",
    "odpowiedz",
    "cytuj",
]
WEB_FALSE_POSITIVE_HINTS = [
    "nie klikaj",
    "bez kliknięcia",
    "nie używaj",
    "nie podawaj",
]


def read_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def checkpoint_meta(path: str | Path) -> dict:
    path = Path(path)
    state = torch.load(path, map_location="cpu", weights_only=False)
    return {
        "path": str(path),
        "exists": path.exists(),
        "size": path.stat().st_size,
        "variant": state.get("variant"),
        "step": state.get("step"),
        "current_step": state.get("current_step"),
        "sft_step": state.get("sft_step"),
        "base_step": state.get("base_step"),
        "dataset_name": state.get("dataset_name"),
        "tokenizer_sha256": state.get("tokenizer_sha256"),
        "loss": state.get("loss"),
        "val_loss": state.get("val_loss"),
        "reason": state.get("reason"),
        "batch_size": state.get("batch_size"),
        "gradient_accumulation_steps": state.get("gradient_accumulation_steps"),
    }


def compare_model_tensors(path_a: str | Path, path_b: str | Path) -> dict:
    state_a = torch.load(path_a, map_location="cpu", weights_only=False)
    state_b = torch.load(path_b, map_location="cpu", weights_only=False)
    model_a = state_a["model"]
    model_b = state_b["model"]
    if model_a.keys() != model_b.keys():
        return {"same_keys": False, "same_tensors": False, "different_keys": sorted(set(model_a) ^ set(model_b))[:20]}
    different = []
    for key in model_a:
        if not torch.equal(model_a[key], model_b[key]):
            different.append(key)
            if len(different) >= 20:
                break
    return {
        "same_keys": True,
        "same_tensors": not different,
        "different_tensors_sample": different,
        "same_step": (state_a.get("step"), state_b.get("step")),
        "same_val_loss": (state_a.get("val_loss"), state_b.get("val_loss")),
    }


def repeated_kind(text: str) -> str:
    ws = words(text)
    if len(ws) < 4:
        return "none"
    word_counts = Counter(ws)
    if any(count >= 4 for count in word_counts.values()):
        return "word loop"
    for n, label in ((3, "phrase loop"), (5, "sentence loop")):
        grams = Counter(tuple(ws[i : i + n]) for i in range(max(0, len(ws) - n + 1)))
        if any(count >= 2 for count in grams.values()):
            return label
    if len(ws) > 45 and len(set(ws)) / max(1, len(ws)) < 0.45:
        return "semantic drift without literal loop"
    return "harmless repetition"


def web_classification(output: str) -> str:
    lowered = output.lower()
    if any(hint in lowered for hint in WEB_FALSE_POSITIVE_HINTS):
        return "false positive"
    if any(pattern in lowered for pattern in WEB_REAL_PATTERNS):
        return "real web residue"
    return "unclear"


def audit_previous_eval(eval_json: str, report_json: str, output_md: str, output_json: str) -> dict:
    payload = read_json(eval_json)
    train_report = read_json(report_json)
    rows = payload["results"]
    v02_rows = []
    for row in rows:
        out = row["sft_v0_2"]
        score = out["score"]
        v02_rows.append(
            {
                "mode": row["mode"],
                "kind": row["kind"],
                "category": row["category"],
                "id": row.get("id"),
                "prompt": row.get("instruction") or row.get("prompt"),
                "output": out["output"],
                "raw_output": out["raw_output"],
                "score": score,
                "score_value": score["score"],
                "ended_by_end_token": out["ended_by_end_token"],
                "repetition_classification": repeated_kind(out["output"]) if score.get("repetition_ngrams", 0) > 0 else "none",
                "web_classification": web_classification(out["output"]) if score.get("web_residue") else "none",
            }
        )

    repetition_cases = [row for row in v02_rows if row["score"].get("repetition_ngrams", 0) > 0]
    web_cases = [row for row in v02_rows if row["score"].get("web_residue")]
    best = sorted(v02_rows, key=lambda row: row["score_value"], reverse=True)[:20]
    worst = sorted(v02_rows, key=lambda row: row["score_value"])[:20]
    repetition_by_mode = Counter(row["mode"] for row in repetition_cases)
    repetition_by_category = Counter(row["category"] for row in repetition_cases)
    repetition_without_end = sum(1 for row in repetition_cases if not row["ended_by_end_token"])
    templated_starts = Counter()
    for row in v02_rows:
        ws = words(row["output"])
        if ws:
            templated_starts[ws[0]] += 1

    audit = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_eval": eval_json,
        "source_training_report": report_json,
        "v0_2_checkpoint": train_report.get("dataset", {}).get("output"),
        "counts": {
            "total_rows": len(v02_rows),
            "repetition_cases": len(repetition_cases),
            "web_residue_cases": len(web_cases),
            "repetition_without_end": repetition_without_end,
            "repetition_with_end": len(repetition_cases) - repetition_without_end,
        },
        "repetition_by_mode": dict(repetition_by_mode),
        "repetition_by_category": dict(repetition_by_category),
        "web_classification_counts": dict(Counter(row["web_classification"] for row in web_cases)),
        "repetition_classification_counts": dict(Counter(row["repetition_classification"] for row in repetition_cases)),
        "top_response_first_words": dict(templated_starts.most_common(20)),
        "best_20": best,
        "worst_20": worst,
        "repetition_cases": repetition_cases,
        "web_residue_cases": web_cases,
        "template_assessment": {
            "too_templated": templated_starts.most_common(1)[0][1] > len(v02_rows) * 0.25 if templated_starts else False,
            "comment": "No single first word dominates >25% of outputs." if templated_starts and templated_starts.most_common(1)[0][1] <= len(v02_rows) * 0.25 else "A repeated first-word pattern may be present.",
        },
    }
    Path(output_json).write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(output_md).write_text(build_error_audit_md(audit), encoding="utf-8")
    return audit


def compact_output(text: str, limit: int = 420) -> str:
    text = normalize_space(text)
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def build_error_audit_md(audit: dict) -> str:
    lines = [
        "# Glyph-100M SFT v0.2 error and decoding audit",
        "",
        "## Summary",
        "",
        f"- rows audited: `{audit['counts']['total_rows']}`",
        f"- repetition cases: `{audit['counts']['repetition_cases']}`",
        f"- web-residue heuristic cases: `{audit['counts']['web_residue_cases']}`",
        f"- repetition without `<|end|>`: `{audit['counts']['repetition_without_end']}`",
        f"- repetition by mode: `{audit['repetition_by_mode']}`",
        f"- repetition by category: `{audit['repetition_by_category']}`",
        f"- repetition classes: `{audit['repetition_classification_counts']}`",
        f"- web classes: `{audit['web_classification_counts']}`",
        f"- template assessment: `{audit['template_assessment']['comment']}`",
        "",
        "## Worst 20 v0.2 Outputs",
        "",
    ]
    for idx, row in enumerate(audit["worst_20"], 1):
        lines += [
            f"### {idx}. score={row['score_value']} · {row['mode']} · {row['category']}",
            "",
            f"Prompt: {row['prompt']}",
            "",
            compact_output(row["output"]) or "[empty]",
            "",
        ]
    lines += ["## Best 20 v0.2 Outputs", ""]
    for idx, row in enumerate(audit["best_20"], 1):
        lines += [
            f"### {idx}. score={row['score_value']} · {row['mode']} · {row['category']}",
            "",
            f"Prompt: {row['prompt']}",
            "",
            compact_output(row["output"]) or "[empty]",
            "",
        ]
    lines += ["## Repetition Cases", ""]
    for idx, row in enumerate(audit["repetition_cases"], 1):
        lines += [
            f"- {idx}. `{row['repetition_classification']}` · `{row['mode']}` · `{row['category']}` · end={row['ended_by_end_token']} · score={row['score_value']} · {row['prompt']}",
        ]
    lines += ["", "## Web-Residue Heuristic Cases", ""]
    for idx, row in enumerate(audit["web_residue_cases"], 1):
        lines += [
            f"### {idx}. {row['web_classification']} · {row['mode']} · {row['category']} · score={row['score_value']}",
            "",
            f"Prompt: {row['prompt']}",
            "",
            compact_output(row["output"]) or "[empty]",
            "",
        ]
    return "\n".join(lines).rstrip() + "\n"


def build_prompt_rows(test_jsonl: str, train_jsonl: str, min_rows: int) -> list[dict]:
    rows = []
    test = load_jsonl(test_jsonl).records
    train = load_jsonl(train_jsonl).records if train_jsonl else []
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
    for idx, (row_id, category, instruction) in enumerate(EXTRA_DIAGNOSTICS, 1):
        rows.append({"kind": "diagnostic_instruction", "id": row_id, "category": category, "instruction": instruction})
    for idx, prompt in enumerate(CONTINUATION_PROMPTS, 1):
        rows.append({"kind": "continuation", "id": f"cont-{idx:02d}", "category": "base_lm_sanity", "prompt": prompt})
    if len(rows) < min_rows:
        seen = {row.get("id") for row in rows}
        for record in train:
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
            if len(rows) >= min_rows:
                break
    return rows[: max(min_rows, len(rows))]


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
    return {
        "output": text,
        "raw_output": raw_text,
        "ended_by_end_token": ended,
        "seconds": elapsed,
        "generated_tokens": len(new_ids),
    }


def score_row(row: dict, output: str, ended: bool) -> dict:
    if row["kind"] == "target_instruction":
        return target_score(output, row["response"], ended, row["instruction"])
    if row["kind"] == "diagnostic_instruction":
        return diagnostic_score(row["category"], row["instruction"], output, ended)
    return continuation_score(row["prompt"], output)


def summarize_outputs(rows: list[dict], outputs: list[dict]) -> dict:
    scores = [out["score"]["score"] for out in outputs]
    instruction = [(row, out) for row, out in zip(rows, outputs, strict=True) if row["kind"] != "continuation"]
    target = [(row, out) for row, out in zip(rows, outputs, strict=True) if row["kind"] == "target_instruction"]
    generated_tokens = [out["generated_tokens"] for out in outputs]
    return {
        "rows": len(outputs),
        "avg_score": mean(scores),
        "median_score": median(scores),
        "repetition_samples": sum(1 for out in outputs if out["score"].get("repetition_ngrams", 0) > 0),
        "end_token_rate": sum(1 for _, out in instruction if out["ended_by_end_token"]) / max(1, len(instruction)),
        "natural_endings": sum(1 for out in outputs if out["score"].get("natural_end")),
        "pseudo_ency": sum(1 for out in outputs if out["score"].get("pseudo_ency")),
        "web_residue": sum(1 for out in outputs if out["score"].get("web_residue")),
        "topic_drift": sum(1 for out in outputs if out["score"].get("prompt_overlap")),
        "generic_assistant_template": sum(1 for out in outputs if out["score"].get("generic_assistant_template")),
        "first_token_correct": sum(1 for _, out in target if out["score"].get("starts_with_target_first_word")),
        "avg_generated_tokens": mean(generated_tokens),
        "too_short_answers": sum(1 for out in outputs if len(words(out["output"])) < 3),
        "too_long_answers": sum(1 for out in outputs if out["generated_tokens"] >= 78 and not out["ended_by_end_token"]),
    }


def run_model_modes(checkpoint: str, rows: list[dict], modes: dict, sp, device: torch.device, max_new_tokens: int, seed: int) -> tuple[dict, dict]:
    model, state = load_model(checkpoint, device)
    all_outputs: dict[str, list[dict]] = {}
    for mode_idx, (mode_name, mode) in enumerate(modes.items()):
        print(f"mode {mode_name} rows={len(rows)}", flush=True)
        outputs = []
        for idx, row in enumerate(rows):
            prompt = instruction_prompt(row["instruction"]) if row["kind"] != "continuation" else row["prompt"]
            generated = generate_one(model, sp, device, prompt, mode, max_new_tokens, seed + mode_idx * 10000 + idx)
            generated["score"] = score_row(row, generated["output"], generated["ended_by_end_token"])
            outputs.append(generated)
            if (idx + 1) % 25 == 0:
                print(f"  {mode_name}: {idx + 1}/{len(rows)}", flush=True)
        all_outputs[mode_name] = outputs
    del model
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return all_outputs, state


def choose_winner(a_score: int, b_score: int, a_name: str, b_name: str) -> str:
    if a_score >= b_score + 2:
        return a_name
    if b_score >= a_score + 2:
        return b_name
    return "tie"


def build_sweep_payload(rows: list[dict], outputs_by_mode: dict, modes: dict, checkpoint: str, state: dict) -> dict:
    summaries = {}
    results = []
    for mode_name, outputs in outputs_by_mode.items():
        summaries[mode_name] = summarize_outputs(rows, outputs)
        for row, out in zip(rows, outputs, strict=True):
            results.append({**row, "mode": mode_name, "v0_2": out})
    best_mode = max(
        summaries,
        key=lambda mode: (
            summaries[mode]["avg_score"]
            - 0.25 * summaries[mode]["repetition_samples"]
            - 0.35 * summaries[mode]["web_residue"]
            + 2.0 * summaries[mode]["end_token_rate"]
        ),
    )
    return {
        "summary": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "checkpoint": checkpoint,
            "checkpoint_step": state.get("current_step", state.get("step")),
            "rows": len(rows),
            "modes": modes,
            "mode_summaries": summaries,
            "best_mode": best_mode,
            "best_mode_selection_note": "Selected by avg_score minus repetition/web penalties plus end-token bonus.",
        },
        "results": results,
    }


def write_sweep_md(payload: dict, path: str) -> None:
    s = payload["summary"]
    lines = [
        "# Glyph-100M SFT v0.2 decoding sweep",
        "",
        "## Summary",
        "",
        f"- rows: `{s['rows']}`",
        f"- checkpoint: `{s['checkpoint']}`",
        f"- best mode: `{s['best_mode']}`",
        "",
        "## Modes",
        "",
    ]
    for mode, stats in s["mode_summaries"].items():
        lines.append(
            f"- {mode}: avg `{stats['avg_score']:.2f}`, median `{stats['median_score']:.2f}`, "
            f"rep `{stats['repetition_samples']}`, end_rate `{stats['end_token_rate']:.2f}`, "
            f"natural `{stats['natural_endings']}`, web `{stats['web_residue']}`, first `{stats['first_token_correct']}`, "
            f"avg_tokens `{stats['avg_generated_tokens']:.1f}`"
        )
    for title, reverse in (("Best 10 per sweep", True), ("Worst 10 per sweep", False)):
        lines += ["", f"## {title}", ""]
        sample = sorted(payload["results"], key=lambda row: row["v0_2"]["score"]["score"], reverse=reverse)[:10]
        for idx, row in enumerate(sample, 1):
            prompt = row.get("instruction") or row.get("prompt")
            out = row["v0_2"]
            lines += [
                f"### {idx}. {row['mode']} · {row['category']} · score={out['score']['score']}",
                "",
                f"Prompt: {prompt}",
                "",
                compact_output(out["output"]) or "[empty]",
                "",
            ]
    Path(path).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_json(path: str, payload: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def compare_models(rows: list[dict], checkpoints: dict[str, str], mode_name: str, mode: dict, sp, device, max_new_tokens: int, seed: int) -> dict:
    outputs_by_model = {}
    states = {}
    for model_idx, (name, checkpoint) in enumerate(checkpoints.items()):
        print(f"compare model {name} mode={mode_name}", flush=True)
        outputs, state = run_model_modes(checkpoint, rows, {mode_name: mode}, sp, device, max_new_tokens, seed + model_idx * 50000)
        outputs_by_model[name] = outputs[mode_name]
        states[name] = state
    summaries = {name: summarize_outputs(rows, outputs) for name, outputs in outputs_by_model.items()}
    pairwise = {}
    for a, b in (("sft_v0_2", "sft_v0_1"), ("sft_v0_2", "base44k"), ("sft_v0_1", "base44k")):
        counts = Counter()
        for idx in range(len(rows)):
            counts[
                choose_winner(
                    outputs_by_model[a][idx]["score"]["score"],
                    outputs_by_model[b][idx]["score"]["score"],
                    a,
                    b,
                )
            ] += 1
        pairwise[f"{a}_vs_{b}"] = dict(counts)
    detailed = []
    for idx, row in enumerate(rows):
        detailed.append({**row, **{name: outputs[idx] for name, outputs in outputs_by_model.items()}})
    return {
        "summary": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "mode": mode_name,
            "mode_settings": mode,
            "rows": len(rows),
            "checkpoints": checkpoints,
            "checkpoint_steps": {name: states[name].get("current_step", states[name].get("step")) for name in states},
            "models": summaries,
            "pairwise": pairwise,
        },
        "results": detailed,
    }


def write_compare_md(payload: dict, path: str) -> None:
    s = payload["summary"]
    lines = [
        "# Glyph-100M SFT v0.1 vs v0.2 best decoding",
        "",
        f"- mode: `{s['mode']}`",
        f"- rows: `{s['rows']}`",
        f"- pairwise: `{s['pairwise']}`",
        "",
        "## Model Summaries",
        "",
    ]
    for model, stats in s["models"].items():
        lines.append(
            f"- {model}: avg `{stats['avg_score']:.2f}`, median `{stats['median_score']:.2f}`, "
            f"rep `{stats['repetition_samples']}`, end_rate `{stats['end_token_rate']:.2f}`, "
            f"web `{stats['web_residue']}`, first `{stats['first_token_correct']}`"
        )
    lines += ["", "## v0.2 Improvements over v0.1", ""]
    improved = [
        row
        for row in payload["results"]
        if choose_winner(row["sft_v0_2"]["score"]["score"], row["sft_v0_1"]["score"]["score"], "v0.2", "v0.1") == "v0.2"
    ][:15]
    for idx, row in enumerate(improved, 1):
        prompt = row.get("instruction") or row.get("prompt")
        lines += [
            f"### {idx}. {row['category']}",
            "",
            f"Prompt: {prompt}",
            "",
            f"v0.1: {compact_output(row['sft_v0_1']['output'])}",
            "",
            f"v0.2: {compact_output(row['sft_v0_2']['output'])}",
            "",
        ]
    lines += ["## v0.2 Regressions vs v0.1", ""]
    regressions = [
        row
        for row in payload["results"]
        if choose_winner(row["sft_v0_2"]["score"]["score"], row["sft_v0_1"]["score"]["score"], "v0.2", "v0.1") == "v0.1"
    ][:15]
    for idx, row in enumerate(regressions, 1):
        prompt = row.get("instruction") or row.get("prompt")
        lines += [
            f"### {idx}. {row['category']}",
            "",
            f"Prompt: {prompt}",
            "",
            f"v0.1: {compact_output(row['sft_v0_1']['output'])}",
            "",
            f"v0.2: {compact_output(row['sft_v0_2']['output'])}",
            "",
        ]
    Path(path).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def make_decision(audit: dict, sweep: dict, compare: dict, checkpoint_audit: dict) -> dict:
    best_mode = sweep["summary"]["best_mode"]
    best_stats = sweep["summary"]["mode_summaries"][best_mode]
    compare_pair = compare["summary"]["pairwise"].get("sft_v0_2_vs_sft_v0_1", {})
    web_cases = audit["web_classification_counts"]
    real_web = web_cases.get("real web residue", 0)
    rep = best_stats["repetition_samples"]
    end_rate = best_stats["end_token_rate"]
    v02_wins = compare_pair.get("sft_v0_2", 0)
    v01_wins = compare_pair.get("sft_v0_1", 0)
    if rep <= 8 and real_web == 0 and end_rate >= 0.90 and v02_wins > v01_wins * 1.5:
        verdict = "A"
        label = "v0.2 + decoding wystarczająco dobre do planowania ostrożnego SFT v1"
        recommendation = "Można przygotować plan SFT v1, ale nadal bez automatycznego startu."
    elif rep <= 12 and real_web == 0 and end_rate >= 0.80 and v02_wins >= v01_wins:
        verdict = "B"
        label = "v0.2 działa, ale potrzebny dataset v0.3 przed SFT v1"
        recommendation = "Nie startować SFT v1. Najpierw dopracować dataset pod repetition, kończenie i out-of-dataset prompts."
    elif rep <= 12 and end_rate < 0.80:
        verdict = "C"
        label = "główny problem wygląda na decoding/stop behavior"
        recommendation = "Poprawić inference stop/EOS i preset przed skalowaniem datasetu."
    elif rep > 12 or real_web > 0:
        verdict = "D"
        label = "główny problem to dataset/repetition"
        recommendation = "Zrobić dataset v0.3; nie skalować SFT v0.2."
    else:
        verdict = "F"
        label = "zamrozić jako research/portfolio milestone"
        recommendation = "Nie ma wystarczającego sygnału do skalowania bez nowej decyzji."
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "label": label,
        "recommendation": recommendation,
        "evidence": {
            "best_mode": best_mode,
            "best_mode_stats": best_stats,
            "v0_2_vs_v0_1_best_decoding": compare_pair,
            "manual_web_classification_counts": web_cases,
            "checkpoint_audit": checkpoint_audit,
        },
        "constraints": [
            "No SFT v1 was run.",
            "No larger SFT was run.",
            "No pretraining was run.",
            "50k was not used as base.",
            "Model was not published as final.",
        ],
    }


def write_decision_md(payload: dict, path: str) -> None:
    lines = [
        "# Glyph-100M SFT v0.2 final next decision",
        "",
        "## Verdict",
        "",
        f"- verdict: `{payload['verdict']}`",
        f"- label: {payload['label']}",
        f"- recommendation: {payload['recommendation']}",
        "",
        "## Evidence",
        "",
        f"- best decoding mode: `{payload['evidence']['best_mode']}`",
        f"- best mode stats: `{payload['evidence']['best_mode_stats']}`",
        f"- v0.2 vs v0.1: `{payload['evidence']['v0_2_vs_v0_1_best_decoding']}`",
        f"- web classification counts: `{payload['evidence']['manual_web_classification_counts']}`",
        "",
        "## Constraints Honored",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["constraints"])
    Path(path).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--base-checkpoint", default="checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt")
    parser.add_argument("--v01-checkpoint", default="checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm-latest.pt")
    parser.add_argument("--v02-best-checkpoint", default="checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm-best.pt")
    parser.add_argument("--v02-final-checkpoint", default="checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm-final-step_000462.pt")
    parser.add_argument("--v02-latest-checkpoint", default="checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm-latest.pt")
    parser.add_argument("--previous-eval-json", default="eval/glyph-100m/sft_smoke_v0_2_fixedmask_before_after.json")
    parser.add_argument("--previous-report-json", default="reports/glyph100_44k_sft_smoke_v0_2_fixedmask_rocm_report.json")
    parser.add_argument("--test-jsonl", default="data/sft/processed/glyph100_sft_smoke_v0_2_test.jsonl")
    parser.add_argument("--train-jsonl", default="data/sft/processed/glyph100_sft_smoke_v0_2_train.jsonl")
    parser.add_argument("--min-prompts", type=int, default=150)
    parser.add_argument("--max-new-tokens", type=int, default=80)
    parser.add_argument("--seed", type=int, default=2040)
    args = parser.parse_args()

    Path("reports").mkdir(exist_ok=True)
    Path("eval/glyph-100m").mkdir(parents=True, exist_ok=True)

    checkpoint_audit = {
        "base44k": checkpoint_meta(args.base_checkpoint),
        "sft_v0_1": checkpoint_meta(args.v01_checkpoint),
        "sft_v0_2_best": checkpoint_meta(args.v02_best_checkpoint),
        "sft_v0_2_final": checkpoint_meta(args.v02_final_checkpoint),
        "sft_v0_2_latest": checkpoint_meta(args.v02_latest_checkpoint),
        "best_vs_final_model_tensors": compare_model_tensors(args.v02_best_checkpoint, args.v02_final_checkpoint),
        "best_vs_latest_model_tensors": compare_model_tensors(args.v02_best_checkpoint, args.v02_latest_checkpoint),
    }
    checkpoint_audit["v0_2_best_final_same_checkpoint"] = (
        checkpoint_audit["best_vs_final_model_tensors"]["same_tensors"]
        and checkpoint_audit["sft_v0_2_best"]["current_step"] == checkpoint_audit["sft_v0_2_final"]["current_step"]
        and checkpoint_audit["sft_v0_2_best"]["val_loss"] == checkpoint_audit["sft_v0_2_final"]["val_loss"]
    )

    audit = audit_previous_eval(
        args.previous_eval_json,
        args.previous_report_json,
        "reports/glyph100_sft_v0_2_error_and_decoding_audit.md",
        "reports/glyph100_sft_v0_2_error_and_decoding_audit.json",
    )
    audit["checkpoint_audit"] = checkpoint_audit
    write_json("reports/glyph100_sft_v0_2_error_and_decoding_audit.json", audit)
    Path("reports/glyph100_sft_v0_2_error_and_decoding_audit.md").write_text(build_error_audit_md(audit), encoding="utf-8")

    rows = build_prompt_rows(args.test_jsonl, args.train_jsonl, args.min_prompts)
    sp = load_sentencepiece(args.tokenizer)
    device = select_device(args.device)
    print(f"running sweep rows={len(rows)} device={device}", flush=True)
    sweep_outputs, sweep_state = run_model_modes(
        args.v02_best_checkpoint,
        rows,
        DECODING_MODES,
        sp,
        device,
        args.max_new_tokens,
        args.seed,
    )
    sweep = build_sweep_payload(rows, sweep_outputs, DECODING_MODES, args.v02_best_checkpoint, sweep_state)
    write_json("eval/glyph-100m/sft_v0_2_decoding_sweep.json", sweep)
    write_sweep_md(sweep, "eval/glyph-100m/sft_v0_2_decoding_sweep.md")

    best_mode = sweep["summary"]["best_mode"]
    compare = compare_models(
        rows,
        {
            "base44k": args.base_checkpoint,
            "sft_v0_1": args.v01_checkpoint,
            "sft_v0_2": args.v02_best_checkpoint,
        },
        best_mode,
        DECODING_MODES[best_mode],
        sp,
        device,
        args.max_new_tokens,
        args.seed + 100000,
    )
    write_json("eval/glyph-100m/sft_v0_1_vs_v0_2_best_decoding.json", compare)
    write_compare_md(compare, "eval/glyph-100m/sft_v0_1_vs_v0_2_best_decoding.md")

    decision = make_decision(audit, sweep, compare, checkpoint_audit)
    write_json("reports/glyph100_sft_v0_2_final_next_decision.json", decision)
    write_decision_md(decision, "reports/glyph100_sft_v0_2_final_next_decision.md")
    print(json.dumps({"decision": decision, "best_mode": best_mode}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
