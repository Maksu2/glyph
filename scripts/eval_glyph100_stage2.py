#!/usr/bin/env python3
"""Quick qualitative completion eval for Glyph-100M stage 2.

This is a lightweight base-LM eval. It does not score the model as an
assistant and it does not run training.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import ModelConfig  # noqa: E402
from model import GPT  # noqa: E402


PRESETS = {
    "conservative": {"temperature": 0.6, "top_k": 30, "max_new_tokens": 120},
    "normal": {"temperature": 0.8, "top_k": 40, "max_new_tokens": 120},
    "creative": {"temperature": 1.0, "top_k": 50, "max_new_tokens": 120},
}

WEB_PATTERNS = [
    "http://",
    "https://",
    "www.",
    "<html",
    "</",
    "czytaj więcej",
    "strona główna",
    "dodane:",
    "komentarze",
    "anonimowy",
    "invalid argument",
    "foreach()",
]


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def configure_attention_backend(name: str) -> None:
    name = name.strip().lower()
    if name == "manual":
        import os

        os.environ["GLYPH_ATTENTION_IMPL"] = "manual"
        return
    if name == "math":
        try:
            torch.backends.cuda.enable_flash_sdp(False)
            torch.backends.cuda.enable_mem_efficient_sdp(False)
            torch.backends.cuda.enable_math_sdp(True)
            if hasattr(torch.backends.cuda, "enable_cudnn_sdp"):
                torch.backends.cuda.enable_cudnn_sdp(False)
        except Exception:
            pass


def load_tokenizer(path: Path):
    import sentencepiece as spm

    sp = spm.SentencePieceProcessor()
    sp.load(str(path))
    return sp


def model_config_from_checkpoint(state: dict) -> ModelConfig:
    cfg_dict = state.get("model_config") or {}
    values = {key: value for key, value in cfg_dict.items() if key in ModelConfig.__dataclass_fields__}
    return ModelConfig(**values)


def load_model(path: Path, device: torch.device) -> tuple[GPT, dict]:
    state = torch.load(path, map_location="cpu", weights_only=False)
    cfg = model_config_from_checkpoint(state)
    model = GPT(cfg)
    model.load_state_dict(state["model"])
    model.to(device)
    model.eval()
    return model, state


def decode_new_text(sp, prompt: str, output_ids: torch.Tensor, prompt_len: int) -> tuple[str, str, bool]:
    all_ids = output_ids[0].tolist()
    generated_ids = all_ids[prompt_len:]
    ended_by_eos = bool(generated_ids and generated_ids[-1] == sp.eos_id())
    text_ids = generated_ids[:-1] if ended_by_eos else generated_ids
    full_text = sp.decode(all_ids[:prompt_len] + text_ids)
    new_text = sp.decode(text_ids)
    return full_text, new_text, ended_by_eos


def repeated_ngrams(text: str, n: int = 4) -> int:
    words = re.findall(r"\w+", text.lower(), flags=re.UNICODE)
    if len(words) < n * 2:
        return 0
    ngrams = [tuple(words[i : i + n]) for i in range(len(words) - n + 1)]
    counts = Counter(ngrams)
    return sum(count - 1 for count in counts.values() if count > 1)


def analyze_text(text: str) -> dict:
    stripped = text.strip()
    chars = len(stripped)
    letters = sum(1 for char in stripped if char.isalpha())
    polish_chars = sum(1 for char in stripped.lower() if char in "ąćęłńóśźż")
    words = re.findall(r"\w+", stripped, flags=re.UNICODE)
    lower = stripped.lower()
    web_hits = [pattern for pattern in WEB_PATTERNS if pattern in lower]
    url_count = len(re.findall(r"https?://|www\\.", lower))
    html_count = len(re.findall(r"<[^>]+>", stripped))
    usernames_or_dates = len(re.findall(r"\b\d{1,2}\s+(?:sty|lut|mar|kwi|maj|cze|lip|sie|wrz|paź|lis|gru)", lower))
    return {
        "chars": chars,
        "words": len(words),
        "alphabetic_ratio": round(letters / max(chars, 1), 3),
        "polish_char_count": polish_chars,
        "repeated_4grams": repeated_ngrams(stripped, 4),
        "web_garbage_hits": web_hits,
        "url_count": url_count,
        "html_count": html_count,
        "date_like_count": usernames_or_dates,
        "ends_naturally": bool(re.search(r"[.!?…]\s*$", stripped)),
    }


def generate_one(model, sp, device, prompt: str, settings: dict, seed: int) -> dict:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    prompt_ids = sp.encode(prompt, out_type=int)
    idx = torch.tensor([prompt_ids], dtype=torch.long, device=device)
    started = time.perf_counter()
    with torch.no_grad():
        out = model.generate(
            idx,
            max_new_tokens=settings["max_new_tokens"],
            temperature=settings["temperature"],
            top_k=settings["top_k"],
            top_p=settings.get("top_p", 1.0),
            repetition_penalty=settings.get("repetition_penalty", 1.0),
            eos_token_id=sp.eos_id(),
        )
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    duration = time.perf_counter() - started
    full_text, new_text, ended_by_eos = decode_new_text(sp, prompt, out.detach().cpu(), len(prompt_ids))
    actual_new_tokens = out.size(1) - len(prompt_ids)
    analysis = analyze_text(new_text)
    analysis["ended_by_eos"] = ended_by_eos
    analysis["ends_naturally"] = analysis["ends_naturally"] or ended_by_eos
    return {
        "prompt": prompt,
        "full_text": full_text,
        "new_text": new_text,
        "duration_seconds": round(duration, 3),
        "new_tokens": actual_new_tokens,
        "max_new_tokens": settings["max_new_tokens"],
        "ended_by_eos": ended_by_eos,
        "tokens_per_second": round(actual_new_tokens / duration, 2) if duration > 0 else None,
        "analysis": analysis,
    }


def qualitative_note(analysis: dict) -> str:
    issues = []
    if analysis["alphabetic_ratio"] < 0.55:
        issues.append("niski udział liter")
    if analysis["repeated_4grams"] > 0:
        issues.append(f"powtórzenia {analysis['repeated_4grams']}")
    if analysis["web_garbage_hits"] or analysis["url_count"] or analysis["html_count"]:
        issues.append("web/forum garbage")
    if not analysis["ends_naturally"]:
        issues.append("ucięte zakończenie")
    if not issues:
        return "OK jako krótka kontynuacja base LM."
    return "Problemy: " + ", ".join(issues) + "."


def write_samples_md(path: Path, rows: list[dict], checkpoint_label: str) -> None:
    lines = [
        f"# Glyph-100M stage 2 samples ({checkpoint_label})",
        "",
        "Base LM completion eval. To nie jest eval asystenta ani instruction-following.",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"## {row['prompt_id']} · {row['category']} · {row['preset']}",
                "",
                f"**Prompt:** `{row['prompt']}`",
                "",
                f"**Settings:** temp={row['settings']['temperature']} · top_k={row['settings']['top_k']} · max_new_tokens={row['settings']['max_new_tokens']}",
                "",
                "**Output:**",
                "",
                "```text",
                row["full_text"].strip(),
                "```",
                "",
                f"**Heurystyka:** {qualitative_note(row['analysis'])}",
                "",
                f"**Tok/s generation:** {row['tokens_per_second']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_comparison_md(path: Path, prompts: list[dict], glyph100_rows: list[dict], glyph27_rows: list[dict]) -> None:
    g100 = {row["prompt_id"]: row for row in glyph100_rows if row["preset"] == "normal"}
    g27 = {row["prompt_id"]: row for row in glyph27_rows}
    lines = [
        "# Glyph-100M stage 2 vs Glyph-27M base",
        "",
        "Szybkie porównanie base LM na tym samym presecie `normal`: temp=0.8, top_k=40.",
        "",
    ]
    for prompt in prompts:
        pid = prompt["id"]
        lines.extend(
            [
                f"## {pid} · {prompt['category']}",
                "",
                f"**Prompt:** `{prompt['prompt']}`",
                "",
                "**Glyph-27M:**",
                "",
                "```text",
                (g27.get(pid) or {}).get("full_text", "").strip(),
                "```",
                "",
                "**Glyph-100M 10k:**",
                "",
                "```text",
                (g100.get(pid) or {}).get("full_text", "").strip(),
                "```",
                "",
                "**Krótki wniosek:** "
                + compare_note((g27.get(pid) or {}).get("analysis", {}), (g100.get(pid) or {}).get("analysis", {})),
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def compare_note(a27: dict, a100: dict) -> str:
    if not a27 or not a100:
        return "brak pełnych danych."
    score27 = heuristic_score(a27)
    score100 = heuristic_score(a100)
    if score100 > score27:
        return "100M wygląda lepiej heurystycznie: mniej śmieci/pętli albo naturalniejsze zakończenie."
    if score27 > score100:
        return "27M wygląda lepiej heurystycznie w tej próbce; trzeba obejrzeć tekst ręcznie."
    return "remis heurystyczny; decyduje ręczna ocena spójności."


def heuristic_score(analysis: dict) -> int:
    score = 0
    if analysis.get("alphabetic_ratio", 0) >= 0.55:
        score += 1
    if analysis.get("repeated_4grams", 0) == 0:
        score += 1
    if not analysis.get("web_garbage_hits") and not analysis.get("url_count") and not analysis.get("html_count"):
        score += 1
    if analysis.get("ends_naturally"):
        score += 1
    return score


def summary(rows: list[dict]) -> dict:
    by_preset = defaultdict(list)
    for row in rows:
        by_preset[row["preset"]].append(row)
    presets = {}
    for name, preset_rows in by_preset.items():
        analyses = [row["analysis"] for row in preset_rows]
        presets[name] = {
            "count": len(preset_rows),
            "avg_tokens_per_second": round(statistics.mean(row["tokens_per_second"] for row in preset_rows), 2),
            "web_garbage_samples": sum(1 for item in analyses if item["web_garbage_hits"] or item["url_count"] or item["html_count"]),
            "repetition_samples": sum(1 for item in analyses if item["repeated_4grams"] > 0),
            "natural_endings": sum(1 for item in analyses if item["ends_naturally"]),
            "avg_alphabetic_ratio": round(statistics.mean(item["alphabetic_ratio"] for item in analyses), 3),
        }
    return {"preset_summary": presets}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", default="eval/glyph-100m/stage2_completion_prompts.jsonl")
    parser.add_argument("--checkpoint", default="checkpoints/glyph-100m/latest.pt")
    parser.add_argument("--compare-checkpoint", default="checkpoints/final.pt")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--out-json", default="eval/glyph-100m/stage2_samples.json")
    parser.add_argument("--out-md", default="eval/glyph-100m/stage2_samples.md")
    parser.add_argument("--compare-md", default="eval/glyph-100m/stage2_vs_27m.md")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--attention-backend", default="math", choices=["sdpa", "math", "manual"])
    parser.add_argument("--seed", type=int, default=20260531)
    parser.add_argument(
        "--presets",
        default=",".join(PRESETS),
        help="Comma-separated preset names; defaults to all built-in presets",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=None,
        help="Optional max-new-tokens override applied to selected presets",
    )
    args = parser.parse_args()

    preset_names = [name.strip() for name in args.presets.split(",") if name.strip()]
    unknown_presets = [name for name in preset_names if name not in PRESETS]
    if not preset_names or unknown_presets:
        raise SystemExit(f"Invalid --presets value; unknown={unknown_presets}, available={sorted(PRESETS)}")
    selected_presets = {
        name: {
            **PRESETS[name],
            **({"max_new_tokens": args.max_new_tokens} if args.max_new_tokens is not None else {}),
        }
        for name in preset_names
    }

    device = torch.device("cuda" if args.device == "auto" and torch.cuda.is_available() else args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA/HIP requested but torch.cuda.is_available() is false")
    configure_attention_backend(args.attention_backend)

    prompts = read_jsonl(ROOT / args.prompts)
    sp = load_tokenizer(ROOT / args.tokenizer)

    model, state = load_model(ROOT / args.checkpoint, device)
    rows = []
    for preset_name, settings in selected_presets.items():
        for index, prompt in enumerate(prompts):
            result = generate_one(model, sp, device, prompt["prompt"], settings, args.seed + index)
            rows.append(
                {
                    "prompt_id": prompt["id"],
                    "category": prompt["category"],
                    "expected": prompt.get("expected"),
                    "preset": preset_name,
                    "settings": settings,
                    "checkpoint": args.checkpoint,
                    "checkpoint_step": state.get("step"),
                    "checkpoint_variant": state.get("variant"),
                    **result,
                }
            )

    out_json = ROOT / args.out_json
    out_md = ROOT / args.out_md
    out_json.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "checkpoint": args.checkpoint,
        "checkpoint_step": state.get("step"),
        "checkpoint_variant": state.get("variant"),
        "device": str(device),
        "presets": selected_presets,
        "summary": summary(rows),
        "samples": rows,
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_samples_md(out_md, rows, f"{state.get('variant')} step {state.get('step')}")

    if args.compare_checkpoint:
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()
        model27, state27 = load_model(ROOT / args.compare_checkpoint, device)
        compare_rows = []
        normal = PRESETS["normal"]
        for index, prompt in enumerate(prompts):
            result = generate_one(model27, sp, device, prompt["prompt"], normal, args.seed + index)
            compare_rows.append(
                {
                    "prompt_id": prompt["id"],
                    "category": prompt["category"],
                    "preset": "normal",
                    "settings": normal,
                    "checkpoint": args.compare_checkpoint,
                    "checkpoint_step": state27.get("step"),
                    "checkpoint_variant": state27.get("variant"),
                    **result,
                }
            )
        write_comparison_md(ROOT / args.compare_md, prompts, rows, compare_rows)


if __name__ == "__main__":
    main()
