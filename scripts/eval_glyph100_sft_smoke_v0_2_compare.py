#!/usr/bin/env python3
"""Compare Glyph-100M base, SFT v0.1 and SFT v0.2."""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.eval_glyph100_sft_smoke_v0_1_fixedmask import (
    CONTINUATION_PROMPTS,
    diagnostic_score,
    instruction_prompt,
    load_model,
    select_device,
    target_score,
    continuation_score,
)
from scripts.sft_utils import END_TOKEN, load_jsonl, load_sentencepiece


MODES = {
    "greedy": {"temperature": 0.0, "top_k": None, "top_p": 1.0, "repetition_penalty": 1.0},
    "repetition_guard": {"temperature": 0.7, "top_k": 40, "top_p": 0.9, "repetition_penalty": 1.15},
}

EXTRA_DIAGNOSTICS = [
    {"id": "diag-v02-loop-01", "category": "anty_powtorzenia_i_konczenie", "instruction": "Odpowiedz jednym zdaniem i nie powtarzaj: czym jest checkpoint?"},
    {"id": "diag-v02-loop-02", "category": "anty_powtorzenia_i_konczenie", "instruction": "Zakończ po jednej myśli: co zrobić, gdy brakuje danych?"},
    {"id": "diag-v02-loop-03", "category": "anty_powtorzenia_i_konczenie", "instruction": "Nie powtarzaj frazy: czy warto trenować dalej bez evala?"},
    {"id": "diag-v02-missing-01", "category": "brak_danych", "instruction": "Czy ten wynik jest dobry, jeśli nie podałem kryteriów?"},
    {"id": "diag-v02-missing-02", "category": "brak_danych", "instruction": "Czy ta konfiguracja jest bezpieczna? Nie podaję szczegółów."},
    {"id": "diag-v02-tech-01", "category": "proste_techniczne_wyjasnienia", "instruction": "Wyjaśnij krótko, po co zapisuje się best checkpoint."},
    {"id": "diag-v02-tech-02", "category": "proste_techniczne_wyjasnienia", "instruction": "Czym różni się eval jakościowy od samego val loss?"},
    {"id": "diag-v02-rewrite-01", "category": "krotkie_poprawki_tekstu", "instruction": "Popraw tekst: Zostało wykonane przeprowadzenie testu działania modelu."},
    {"id": "diag-v02-summary-01", "category": "mini_streszczenia", "instruction": "Streść: Model może mieć niższy loss, ale nadal generować gorsze odpowiedzi w praktycznym eval."},
    {"id": "diag-v02-not-in-dataset-01", "category": "not_in_dataset", "instruction": "Czy ładny dashboard oznacza, że eksperyment jest dobry?"},
    {"id": "diag-v02-not-in-dataset-02", "category": "not_in_dataset", "instruction": "Odpowiedz ostrożnie: czy warto publikować eksperymentalny model?"},
    {"id": "diag-v02-not-in-dataset-03", "category": "not_in_dataset", "instruction": "Napisz krótką odpowiedź: co zrobić, gdy sample wygląda dziwnie?"},
]


@torch.no_grad()
def generate_one(model, sp, device: torch.device, prompt: str, max_new_tokens: int, mode: dict, seed: int) -> tuple[str, str, bool, float]:
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
    )
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    elapsed = time.perf_counter() - start
    new_ids = out[0, idx.shape[1] :].detach().cpu().tolist()
    raw_text = sp.decode(new_ids).strip()
    ended_by_end = END_TOKEN in raw_text
    text = raw_text.split(END_TOKEN, 1)[0].strip() if ended_by_end else raw_text
    return text, raw_text, ended_by_end, elapsed


def build_rows(test_jsonl: str, target_examples: int) -> list[dict]:
    loaded = load_jsonl(test_jsonl)
    rows = []
    for record in loaded.records[:target_examples]:
        rows.append(
            {
                "kind": "target_instruction",
                "id": record.get("id"),
                "category": record.get("category", "unknown"),
                "instruction": record["instruction"],
                "response": record["response"],
            }
        )
    rows.extend({"kind": "diagnostic_instruction", **row} for row in EXTRA_DIAGNOSTICS)
    rows.extend(
        {"kind": "continuation", "id": f"cont-{idx:02d}", "category": "base_lm_sanity", "prompt": prompt}
        for idx, prompt in enumerate(CONTINUATION_PROMPTS, 1)
    )
    return rows


def score_row(row: dict, output: str, ended: bool) -> dict:
    if row["kind"] == "target_instruction":
        return target_score(output, row["response"], ended, row["instruction"])
    if row["kind"] == "diagnostic_instruction":
        return diagnostic_score(row["category"], row["instruction"], output, ended)
    return continuation_score(row["prompt"], output)


def model_outputs(name: str, checkpoint: str, rows: list[dict], modes: dict, sp, device: torch.device, max_new_tokens: int, seed: int) -> tuple[dict, dict]:
    model, state = load_model(checkpoint, device)
    outputs: dict[str, list[dict]] = {}
    for mode_name, mode in modes.items():
        mode_rows = []
        for idx, row in enumerate(rows):
            prompt = instruction_prompt(row["instruction"]) if row["kind"] != "continuation" else row["prompt"]
            text, raw_text, ended, seconds = generate_one(model, sp, device, prompt, max_new_tokens, mode, seed + idx + (1000 if mode_name != "greedy" else 0))
            mode_rows.append(
                {
                    "output": text,
                    "raw_output": raw_text,
                    "ended_by_end_token": ended,
                    "seconds": seconds,
                    "score": score_row(row, text, ended),
                }
            )
        outputs[mode_name] = mode_rows
    del model
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return outputs, state


def choose_winner(score_a: int, score_b: int, a_name: str, b_name: str) -> str:
    if score_a >= score_b + 2:
        return a_name
    if score_b >= score_a + 2:
        return b_name
    return "tie"


def summarize_model(rows: list[dict], outputs: list[dict]) -> dict:
    instruction = [(r, o) for r, o in zip(rows, outputs, strict=True) if r["kind"] != "continuation"]
    target = [(r, o) for r, o in zip(rows, outputs, strict=True) if r["kind"] == "target_instruction"]
    return {
        "avg_score": sum(o["score"]["score"] for o in outputs) / len(outputs),
        "repetition_samples": sum(1 for o in outputs if o["score"].get("repetition_ngrams", 0) > 0),
        "end_token_rate_instruction": sum(1 for _, o in instruction if o["score"].get("ended_by_end_token")) / len(instruction),
        "natural_endings": sum(1 for o in outputs if o["score"].get("natural_end")),
        "pseudo_ency": sum(1 for o in outputs if o["score"].get("pseudo_ency")),
        "web_residue": sum(1 for o in outputs if o["score"].get("web_residue")),
        "topic_drift_or_prompt_overlap": sum(1 for o in outputs if o["score"].get("prompt_overlap")),
        "generic_assistant_template": sum(1 for o in outputs if o["score"].get("generic_assistant_template")),
        "first_token_correct": sum(1 for _, o in target if o["score"].get("starts_with_target_first_word")),
        "target_overlap_ge_0_70": sum(1 for _, o in target if o["score"].get("target_overlap", 0) >= 0.70),
        "exact_target_matches": sum(1 for _, o in target if o["score"].get("exact_target_match")),
    }


def build_payload(args: argparse.Namespace) -> dict:
    rows = build_rows(args.test_jsonl, args.target_examples)
    sp = load_sentencepiece(args.tokenizer)
    device = select_device(args.device)
    checkpoints = {
        "base44k": args.base_checkpoint,
        "sft_v0_1": args.sft_v0_1_checkpoint,
        "sft_v0_2": args.sft_v0_2_checkpoint,
    }
    outputs: dict[str, dict] = {}
    states: dict[str, dict] = {}
    for name, checkpoint in checkpoints.items():
        outputs[name], states[name] = model_outputs(name, checkpoint, rows, MODES, sp, device, args.max_new_tokens, args.seed)

    mode_summaries = {}
    detailed = []
    for mode_name in MODES:
        per_model = {name: summarize_model(rows, model_modes[mode_name]) for name, model_modes in outputs.items()}
        pairwise = {}
        for a, b in (("sft_v0_2", "sft_v0_1"), ("sft_v0_2", "base44k"), ("sft_v0_1", "base44k")):
            counts = Counter()
            for idx in range(len(rows)):
                win = choose_winner(
                    outputs[a][mode_name][idx]["score"]["score"],
                    outputs[b][mode_name][idx]["score"]["score"],
                    a,
                    b,
                )
                counts[win] += 1
            pairwise[f"{a}_vs_{b}"] = dict(counts)
        mode_summaries[mode_name] = {"models": per_model, "pairwise": pairwise}
        for idx, row in enumerate(rows):
            detailed.append(
                {
                    **row,
                    "mode": mode_name,
                    "base44k": outputs["base44k"][mode_name][idx],
                    "sft_v0_1": outputs["sft_v0_1"][mode_name][idx],
                    "sft_v0_2": outputs["sft_v0_2"][mode_name][idx],
                    "winner_v0_2_vs_v0_1": choose_winner(
                        outputs["sft_v0_2"][mode_name][idx]["score"]["score"],
                        outputs["sft_v0_1"][mode_name][idx]["score"]["score"],
                        "sft_v0_2",
                        "sft_v0_1",
                    ),
                    "winner_v0_2_vs_base": choose_winner(
                        outputs["sft_v0_2"][mode_name][idx]["score"]["score"],
                        outputs["base44k"][mode_name][idx]["score"]["score"],
                        "sft_v0_2",
                        "base44k",
                    ),
                }
            )

    return {
        "summary": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "rows": len(rows),
            "target_instruction_examples": sum(1 for r in rows if r["kind"] == "target_instruction"),
            "diagnostic_examples": sum(1 for r in rows if r["kind"] == "diagnostic_instruction"),
            "continuation_examples": sum(1 for r in rows if r["kind"] == "continuation"),
            "modes": MODES,
            "checkpoints": checkpoints,
            "checkpoint_steps": {name: state.get("current_step", state.get("step")) for name, state in states.items()},
            "mode_summaries": mode_summaries,
        },
        "results": detailed,
    }


def build_markdown(payload: dict) -> str:
    s = payload["summary"]
    lines = [
        "# Glyph-100M SFT smoke v0.2 comparison eval",
        "",
        "## Summary",
        "",
        f"- rows: {s['rows']} ({s['target_instruction_examples']} held-out target, {s['diagnostic_examples']} diagnostic, {s['continuation_examples']} continuation)",
        "- prompt template for instruction rows: `<|user|>\\n{prompt}\\n<|assistant|>\\n`",
        "",
    ]
    for mode, summary in s["mode_summaries"].items():
        lines += [f"## Mode: {mode}", ""]
        for model, stats in summary["models"].items():
            lines.append(
                f"- {model}: avg={stats['avg_score']:.2f}, rep={stats['repetition_samples']}, "
                f"end_rate={stats['end_token_rate_instruction']:.2f}, natural={stats['natural_endings']}, "
                f"pseudo={stats['pseudo_ency']}, web={stats['web_residue']}, first={stats['first_token_correct']}"
            )
        lines.append(f"- pairwise: `{summary['pairwise']}`")
        lines.append("")

    for title, key, reverse in (
        ("Best v0.2 examples", "sft_v0_2", True),
        ("Worst v0.2 examples", "sft_v0_2", False),
    ):
        lines += [f"## {title}", ""]
        sample = sorted(payload["results"], key=lambda r: r[key]["score"]["score"], reverse=reverse)[:10]
        for idx, row in enumerate(sample, 1):
            prompt = row.get("instruction") or row.get("prompt")
            score = row[key]["score"]["score"]
            lines += [f"### {idx}. {row['mode']} / {row['kind']} / {row['category']} / score={score}", "", f"Prompt: {prompt}", "", row[key]["output"] or "[empty]", ""]

    lines += ["## v0.2 improved over v0.1", ""]
    improved = [r for r in payload["results"] if r["winner_v0_2_vs_v0_1"] == "sft_v0_2"][:10]
    for idx, row in enumerate(improved, 1):
        prompt = row.get("instruction") or row.get("prompt")
        lines += [f"### {idx}. {row['mode']} / {row['category']}", "", f"Prompt: {prompt}", "", "v0.1:", "", row["sft_v0_1"]["output"] or "[empty]", "", "v0.2:", "", row["sft_v0_2"]["output"] or "[empty]", ""]

    lines += ["## v0.2 damaged vs v0.1", ""]
    damaged = [r for r in payload["results"] if r["winner_v0_2_vs_v0_1"] == "sft_v0_1"][:10]
    for idx, row in enumerate(damaged, 1):
        prompt = row.get("instruction") or row.get("prompt")
        lines += [f"### {idx}. {row['mode']} / {row['category']}", "", f"Prompt: {prompt}", "", "v0.1:", "", row["sft_v0_1"]["output"] or "[empty]", "", "v0.2:", "", row["sft_v0_2"]["output"] or "[empty]", ""]
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare Glyph SFT smoke v0.2")
    parser.add_argument("--test-jsonl", default="data/sft/processed/glyph100_sft_smoke_v0_2_test.jsonl")
    parser.add_argument("--base-checkpoint", required=True)
    parser.add_argument("--sft-v0-1-checkpoint", required=True)
    parser.add_argument("--sft-v0-2-checkpoint", required=True)
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--target-examples", type=int, default=80)
    parser.add_argument("--max-new-tokens", type=int, default=80)
    parser.add_argument("--seed", type=int, default=2030)
    parser.add_argument("--output-md", default="eval/glyph-100m/sft_smoke_v0_2_fixedmask_before_after.md")
    parser.add_argument("--output-json", default="eval/glyph-100m/sft_smoke_v0_2_fixedmask_before_after.json")
    args = parser.parse_args()
    payload = build_payload(args)
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(args.output_md).write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
