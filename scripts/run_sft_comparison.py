#!/usr/bin/env python3
"""Generate fixed SFT comparison samples for Glyph base vs SFT checkpoints."""

from __future__ import annotations

import argparse
import sys
from contextlib import redirect_stdout
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import ModelConfig
from model import GPT
from scripts.sft_utils import ASSISTANT_TOKEN, USER_TOKEN, load_sentencepiece


DEFAULT_PROMPTS = [
    "Czy warto robić projekt od UI?",
    "Czy ten laptop jest dobry?",
    "Popraw tekst: Ten projekt posiada wiele funkcji i działa w dobry sposób.",
    "Streść w jednym zdaniu: Duże projekty często upadają przez zbyt duży zakres.",
    "Wyjaśnij prosto, czym różni się pogoda od klimatu.",
    "Nie znam szczegółów. Jak powinienem odpowiedzieć?",
    "Czy AI automatycznie ulepsza projekt?",
]


def load_model(path: str) -> tuple[GPT, ModelConfig]:
    state = torch.load(path, map_location="cpu", weights_only=False)
    cfg_dict = state.get("model_config", {})
    cfg = ModelConfig(**{k: v for k, v in cfg_dict.items() if k in ModelConfig.__dataclass_fields__})
    with redirect_stdout(sys.stderr):
        model = GPT(cfg)
    model.load_state_dict(state["model"])
    model.eval()
    return model, cfg


def make_prompt(text: str) -> str:
    return f"{USER_TOKEN}\n{text.strip()}\n{ASSISTANT_TOKEN}\n"


@torch.no_grad()
def generate(model: GPT, cfg: ModelConfig, sp, prompt: str, args) -> str:
    ids = sp.encode(make_prompt(prompt), out_type=int)
    ids = ids[-(cfg.context_len - 1) :]
    idx = torch.tensor([ids], dtype=torch.long)
    out = model.generate(
        idx,
        max_new_tokens=args.max_tokens,
        temperature=args.temperature,
        top_k=args.top_k if args.top_k > 0 else None,
        top_p=args.top_p,
        repetition_penalty=args.repetition_penalty,
        no_repeat_ngram_size=args.no_repeat_ngram_size,
    )
    new_ids = out[0].tolist()[len(ids) :]
    text = sp.decode(new_ids)
    return text.replace("<|end|>", "").replace(USER_TOKEN, "").replace(ASSISTANT_TOKEN, "").strip()


def render_samples(title: str, checkpoint: str, rows: list[dict], args) -> str:
    lines = [
        f"# {title}",
        "",
        f"- checkpoint: `{checkpoint}`",
        f"- max_tokens: {args.max_tokens}",
        f"- temperature: {args.temperature}",
        f"- top_k: {args.top_k}",
        f"- top_p: {args.top_p}",
        f"- repetition_penalty: {args.repetition_penalty}",
        f"- no_repeat_ngram_size: {args.no_repeat_ngram_size}",
        "",
    ]
    for row in rows:
        lines += [
            f"## {row['idx']}. Prompt",
            "",
            row["prompt"],
            "",
            "### Output",
            "",
            row["output"] or "(empty)",
            "",
        ]
    return "\n".join(lines)


def render_comparison(base_rows: list[dict], sft_rows: list[dict]) -> str:
    lines = [
        "# Glyph SFT v0 comparison",
        "",
        "Fixed prompt comparison between Glyph-27M Base and Glyph-27M SFT v0.",
        "",
    ]
    for base, sft in zip(base_rows, sft_rows, strict=True):
        lines += [
            f"## {base['idx']}. {base['prompt']}",
            "",
            "### Base",
            "",
            base["output"] or "(empty)",
            "",
            "### SFT v0",
            "",
            sft["output"] or "(empty)",
            "",
        ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate base vs SFT comparison samples")
    parser.add_argument("--base-checkpoint", default="checkpoints/final.pt")
    parser.add_argument("--sft-checkpoint", default="checkpoints/sft-v0/glyph-27m-sft-v0-final.pt")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--out-dir", default="eval/sft-v0")
    parser.add_argument("--max-tokens", type=int, default=90)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-k", type=int, default=40)
    parser.add_argument("--top-p", type=float, default=0.92)
    parser.add_argument("--repetition-penalty", type=float, default=1.12)
    parser.add_argument("--no-repeat-ngram-size", type=int, default=4)
    args = parser.parse_args()

    sp = load_sentencepiece(args.tokenizer)
    base_model, base_cfg = load_model(args.base_checkpoint)
    sft_model, sft_cfg = load_model(args.sft_checkpoint)

    base_rows = []
    sft_rows = []
    for idx, prompt in enumerate(DEFAULT_PROMPTS, 1):
        base_rows.append({"idx": idx, "prompt": prompt, "output": generate(base_model, base_cfg, sp, prompt, args)})
        sft_rows.append({"idx": idx, "prompt": prompt, "output": generate(sft_model, sft_cfg, sp, prompt, args)})
        print(f"generated {idx}/{len(DEFAULT_PROMPTS)}")

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "base_samples.md").write_text(
        render_samples("Glyph-27M Base samples", args.base_checkpoint, base_rows, args),
        encoding="utf-8",
    )
    (out / "sft_v0_samples.md").write_text(
        render_samples("Glyph-27M SFT v0 samples", args.sft_checkpoint, sft_rows, args),
        encoding="utf-8",
    )
    (out / "comparison.md").write_text(render_comparison(base_rows, sft_rows), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
