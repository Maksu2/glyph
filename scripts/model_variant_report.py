#!/usr/bin/env python3
"""Count parameters for Glyph model variants without training."""

from __future__ import annotations

import argparse
import json
import sys
from contextlib import redirect_stdout
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import get_model_config, model_variant_metadata
from model import GPT


def unique_parameters(model):
    seen = set()
    params = []
    for name, param in model.named_parameters(remove_duplicate=False):
        if id(param) in seen:
            continue
        seen.add(id(param))
        params.append((name, param))
    return params


def count_named(model, prefix: str, *, logical: bool = False) -> int:
    total = 0
    seen = set()
    for name, param in model.named_parameters(remove_duplicate=False):
        if not name.startswith(prefix):
            continue
        if not logical:
            if id(param) in seen:
                continue
            seen.add(id(param))
        total += param.numel()
    return total


def parameter_report(variant: str) -> dict:
    cfg = get_model_config(variant)
    meta = model_variant_metadata(variant)
    with redirect_stdout(sys.stderr):
        model = GPT(cfg)

    logical_total = sum(param.numel() for _, param in model.named_parameters(remove_duplicate=False))
    unique = unique_parameters(model)
    unique_total = sum(param.numel() for _, param in unique)
    trainable_unique = sum(param.numel() for _, param in unique if param.requires_grad)

    tok_emb = model.tok_emb.weight.numel()
    pos_emb = model.pos_emb.weight.numel()
    lm_head = model.lm_head.weight.numel()
    blocks = count_named(model, "blocks.")
    final_ln = count_named(model, "ln_f.")

    return {
        "variant": meta["variant"],
        "display_name": meta["display_name"],
        "model_config": asdict(cfg),
        "ffn_dim": cfg.d_model * cfg.ffn_mult,
        "logical_total_parameters": logical_total,
        "unique_parameters": unique_total,
        "trainable_unique_parameters": trainable_unique,
        "token_embedding_parameters": tok_emb,
        "position_embedding_parameters": pos_emb,
        "embedding_parameters": tok_emb + pos_emb,
        "transformer_block_parameters": blocks,
        "final_layernorm_parameters": final_ln,
        "lm_head_logical_parameters": lm_head,
        "lm_head_tied_to_token_embedding": model.lm_head.weight is model.tok_emb.weight,
        "non_embedding_unique_parameters": unique_total - tok_emb - pos_emb,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Report Glyph model parameter counts")
    parser.add_argument("--variant", default="glyph-100m")
    parser.add_argument("--compare", action="store_true", help="Also include glyph-27m")
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()

    reports = [parameter_report(args.variant)]
    if args.compare and args.variant != "glyph-27m":
        reports.insert(0, parameter_report("glyph-27m"))

    payload = {"reports": reports}
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for report in reports:
        print(f"{report['display_name']} ({report['variant']})")
        print(f"  config: {report['model_config']}")
        print(f"  ffn_dim: {report['ffn_dim']:,}")
        print(f"  logical total: {report['logical_total_parameters']:,}")
        print(f"  unique/trainable: {report['unique_parameters']:,} / {report['trainable_unique_parameters']:,}")
        print(f"  embeddings: {report['embedding_parameters']:,}")
        print(f"  blocks: {report['transformer_block_parameters']:,}")
        print(f"  lm_head logical tied: {report['lm_head_logical_parameters']:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
