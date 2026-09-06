#!/usr/bin/env python3
"""Validate a Glyph Colab runtime without performing any training."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import ModelConfig
from model import GPT
from scripts.colab_bundle_utils import atomic_write_json, sha256_file
from scripts.sft_utils import ASSISTANT_TOKEN, END_TOKEN, USER_TOKEN, format_sft_text, load_jsonl, load_sentencepiece


EXPECTED_TOKENIZER_SHA = "21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029"


def resolve(path: str | Path) -> Path:
    value = Path(path).expanduser()
    if not value.is_absolute():
        value = ROOT / value
    return value.resolve()


def checkpoint_metadata(state: dict) -> dict:
    model_config = state.get("model_config") or {}
    return {
        "step": int(state.get("current_step", state.get("step", 0))),
        "variant": state.get("variant"),
        "dataset": state.get("dataset_name", state.get("dataset")),
        "context_length": int(state.get("context_length", model_config.get("context_len", 0))),
        "tokenizer_sha256": state.get("tokenizer_sha256"),
        "model_config": model_config,
        "model_tensors": len(state.get("model") or {}),
    }


def environment_report() -> dict:
    disk = shutil.disk_usage("/content" if Path("/content").exists() else ROOT)
    memory_total = None
    memory_available = None
    try:
        import psutil

        memory = psutil.virtual_memory()
        memory_total = memory.total
        memory_available = memory.available
    except ImportError:
        pass

    cuda_available = torch.cuda.is_available()
    gpu = None
    if cuda_available:
        index = torch.cuda.current_device()
        props = torch.cuda.get_device_properties(index)
        free_vram, total_vram = torch.cuda.mem_get_info(index)
        gpu = {
            "name": props.name,
            "compute_capability": f"{props.major}.{props.minor}",
            "total_vram_bytes": int(total_vram),
            "free_vram_bytes": int(free_vram),
            "bf16_supported": bool(getattr(torch.cuda, "is_bf16_supported", lambda: False)()),
        }
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "pytorch": torch.__version__,
        "cuda_available": cuda_available,
        "torch_cuda": torch.version.cuda,
        "torch_hip": getattr(torch.version, "hip", None),
        "cudnn": torch.backends.cudnn.version() if cuda_available else None,
        "gpu": gpu,
        "ram_total_bytes": memory_total,
        "ram_available_bytes": memory_available,
        "content_disk_total_bytes": disk.total,
        "content_disk_free_bytes": disk.free,
        "platform": platform.platform(),
    }


def validate_checkpoint(
    path: Path,
    expected_step: int,
    expected_variant: str,
    expected_context: int,
    tokenizer_sha: str,
    expected_dataset: str | None,
) -> tuple[dict, GPT]:
    kwargs = {"map_location": "cpu", "weights_only": False}
    try:
        state = torch.load(path, mmap=True, **kwargs)
    except (TypeError, RuntimeError):
        state = torch.load(path, **kwargs)
    metadata = checkpoint_metadata(state)
    problems = []
    if metadata["step"] != expected_step:
        problems.append(f"step={metadata['step']} expected={expected_step}")
    if metadata["variant"] != expected_variant:
        problems.append(f"variant={metadata['variant']!r} expected={expected_variant!r}")
    if metadata["context_length"] != expected_context:
        problems.append(f"context={metadata['context_length']} expected={expected_context}")
    if metadata["tokenizer_sha256"] != tokenizer_sha:
        problems.append("checkpoint tokenizer SHA differs from tokenizer file")
    if expected_dataset and metadata["dataset"] != expected_dataset:
        problems.append(f"dataset={metadata['dataset']!r} expected={expected_dataset!r}")
    if not isinstance(state.get("model"), dict) or not state["model"]:
        problems.append("checkpoint has no model state")
    if problems:
        raise ValueError("Checkpoint validation failed: " + "; ".join(problems))

    allowed = ModelConfig.__dataclass_fields__
    cfg = ModelConfig(**{key: value for key, value in metadata["model_config"].items() if key in allowed})
    if cfg.context_len != expected_context:
        raise ValueError(f"model_config context_len={cfg.context_len}, expected {expected_context}")
    approved = ModelConfig(
        vocab_size=16000,
        context_len=512,
        d_model=768,
        n_heads=12,
        n_layers=12,
        ffn_mult=4,
        dropout=0.1,
    )
    if asdict(cfg) != asdict(approved):
        raise ValueError(f"Model config is not the approved Glyph-100M variant: {asdict(cfg)}")
    model = GPT(cfg)
    loaded = model.load_state_dict(state["model"], strict=True)
    if loaded.missing_keys or loaded.unexpected_keys:
        raise ValueError(f"State dict mismatch: {loaded}")
    metadata.update(
        {
            "checkpoint_path": str(path),
            "checkpoint_sha256": sha256_file(path),
            "unique_parameters": sum(parameter.numel() for parameter in model.parameters()),
            "strict_state_load": True,
        }
    )
    return metadata, model


def label_audit(dataset_path: Path, tokenizer_path: Path, context_length: int) -> dict:
    from finetune import SFTDataset

    sp = load_sentencepiece(tokenizer_path)
    loaded = load_jsonl(dataset_path)
    if loaded.invalid_json or loaded.missing_fields:
        raise ValueError(
            f"Dataset validation failed: invalid_json={len(loaded.invalid_json)} "
            f"missing_fields={len(loaded.missing_fields)}"
        )
    dataset = SFTDataset(str(dataset_path), sp, context_length)
    assistant_id = sp.piece_to_id(ASSISTANT_TOKEN)
    end_id = sp.piece_to_id(END_TOKEN)
    if assistant_id < 0 or end_id < 0:
        raise ValueError("Tokenizer is missing SFT special tokens")

    sampled = loaded.records[: min(64, len(loaded.records))]
    checks = {
        "first_assistant_token_supervised": True,
        "end_token_supervised": True,
        "prompt_not_supervised": True,
        "no_examples_without_assistant_labels": True,
    }
    examples = []
    for record in sampled:
        ids = list(sp.encode(format_sft_text(record), out_type=int))
        pair = dataset._make_pair(ids)
        if pair is None:
            checks["no_examples_without_assistant_labels"] = False
            continue
        x, labels = pair
        assistant_position = x.index(assistant_id)
        supervised = [token for token in labels if token != -100]
        checks["first_assistant_token_supervised"] &= labels[assistant_position] != -100
        checks["end_token_supervised"] &= end_id in supervised
        checks["prompt_not_supervised"] &= all(token == -100 for token in labels[:assistant_position])
        if len(examples) < 5:
            examples.append(
                {
                    "id": record.get("id"),
                    "first_supervised_piece": sp.id_to_piece(labels[assistant_position]),
                    "supervised_tokens": len(supervised),
                    "end_supervised": end_id in supervised,
                }
            )

    order = sorted(range(len(dataset.pairs)), key=lambda index: len(dataset.pairs[index][0]))
    batch_indices = [order[0], order[-1]] if len(order) > 1 else order
    _, padded_labels = dataset._batch_tensors(batch_indices, torch.device("cpu"))
    padding_ignored = True
    for row, index in enumerate(batch_indices):
        raw_length = len(dataset.pairs[index][1])
        if raw_length < padded_labels.shape[1]:
            padding_ignored &= bool(torch.all(padded_labels[row, raw_length:] == -100).item())
    checks["padding_ignore_index_minus_100"] = padding_ignored
    passed = all(checks.values()) and len(dataset.pairs) == len(loaded.records)
    result = {
        "status": "PASS" if passed else "FAIL",
        "boundary": "i < assistant_pos",
        "dataset_examples": len(loaded.records),
        "usable_examples": len(dataset.pairs),
        "sampled_examples": len(sampled),
        **checks,
        "examples": examples,
    }
    if not passed:
        raise ValueError(f"Label mask audit failed: {result}")
    return result


@torch.no_grad()
def inference_smoke(model: GPT, tokenizer_path: Path, device: torch.device) -> list[dict]:
    sp = load_sentencepiece(tokenizer_path)
    end_id = sp.piece_to_id(END_TOKEN)
    prompts = [
        "Wyjasnij krotko, czym jest model jezykowy.",
        "Czego nie da sie ocenic bez danych?",
    ]
    modes = [
        ("greedy", {"temperature": 0.0, "no_repeat_ngram_size": 0}),
        ("no_repeat_ngram_3", {"temperature": 0.0, "no_repeat_ngram_size": 3}),
    ]
    model.to(device)
    model.eval()
    outputs = []
    for prompt in prompts:
        formatted = f"{USER_TOKEN}\n{prompt}\n{ASSISTANT_TOKEN}\n"
        prompt_ids = list(sp.encode(formatted, out_type=int))
        tensor = torch.tensor([prompt_ids], dtype=torch.long, device=device)
        for mode, settings in modes:
            generated = model.generate(
                tensor,
                max_new_tokens=32,
                eos_token_id=end_id,
                **settings,
            )
            tokens = generated[0, len(prompt_ids) :].detach().cpu().tolist()
            outputs.append(
                {
                    "mode": mode,
                    "prompt": prompt,
                    "generated_tokens": len(tokens),
                    "ended_with_end_token": end_id in tokens,
                    "text": sp.decode(tokens),
                }
            )
    model.to("cpu")
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return outputs


def markdown_report(result: dict) -> str:
    env = result["environment"]
    checkpoint = result.get("checkpoint") or {}
    warnings = result.get("warnings") or []
    lines = [
        f"# Glyph Colab preflight: {result['run_id']}",
        "",
        f"**Status: {result['status']}**",
        "",
        "## Environment",
        "",
        f"- Python: `{env['python']}`",
        f"- PyTorch: `{env['pytorch']}`",
        f"- CUDA available: `{env['cuda_available']}`",
        f"- CUDA runtime: `{env['torch_cuda']}`",
        f"- GPU: `{(env.get('gpu') or {}).get('name', 'none')}`",
        f"- Free `/content` space: `{env['content_disk_free_bytes']}` bytes",
        "",
        "## Checkpoint",
        "",
        f"- Path: `{checkpoint.get('checkpoint_path', 'not validated')}`",
        f"- Step: `{checkpoint.get('step')}`",
        f"- Variant: `{checkpoint.get('variant')}`",
        f"- Context: `{checkpoint.get('context_length')}`",
        f"- Strict state load: `{checkpoint.get('strict_state_load')}`",
        "",
        "## SFT contract",
        "",
        f"- Label audit: `{(result.get('label_audit') or {}).get('status', 'skipped')}`",
        "- Boundary: `i < assistant_pos`",
        "- First assistant token and `<|end|>` must be supervised.",
        "- Prompt and padding must be ignored (`-100`).",
        "",
        "## Inference smoke",
        "",
        f"- Outputs: `{len(result.get('inference_smoke') or [])}`",
        "- This is a compatibility check, not a quality evaluation.",
        "",
        "## Warnings",
        "",
    ]
    lines.extend([f"- {warning}" for warning in warnings] or ["- None."])
    lines.extend(["", "No training was performed by this preflight.", ""])
    return "\n".join(lines)


def run(args: argparse.Namespace) -> dict:
    environment = environment_report()
    warnings = []
    if not environment["cuda_available"]:
        if not args.allow_cpu:
            raise RuntimeError("CUDA is unavailable; select a GPU runtime or pass --allow-cpu for local validation")
        warnings.append("CUDA unavailable; preflight ran in explicitly allowed CPU mode.")
    elif environment["gpu"] and environment["gpu"]["free_vram_bytes"] < args.minimum_free_vram_gb * 2**30:
        raise RuntimeError(
            f"Free VRAM is below {args.minimum_free_vram_gb:.1f} GiB: "
            f"{environment['gpu']['free_vram_bytes'] / 2**30:.2f} GiB"
        )

    checkpoint_path = resolve(args.checkpoint)
    tokenizer_path = resolve(args.tokenizer)
    dataset_path = resolve(args.dataset)
    for path in (checkpoint_path, tokenizer_path):
        if not path.is_file():
            raise FileNotFoundError(path)
    tokenizer_sha = sha256_file(tokenizer_path)
    if tokenizer_sha != args.expected_tokenizer_sha:
        raise ValueError(f"Tokenizer SHA mismatch: {tokenizer_sha}")

    checkpoint, model = validate_checkpoint(
        checkpoint_path,
        args.expected_step,
        args.expected_variant,
        args.expected_context,
        tokenizer_sha,
        args.expected_dataset or None,
    )
    audit = None
    if not args.skip_label_audit:
        if not dataset_path.is_file():
            raise FileNotFoundError(dataset_path)
        audit = label_audit(dataset_path, tokenizer_path, args.expected_context)

    with tempfile.TemporaryDirectory(prefix="glyph-colab-io-") as temp_name:
        probe = Path(temp_name) / "write-read-probe.txt"
        probe.write_text("glyph-colab-preflight\n", encoding="utf-8")
        with probe.open("rb+") as handle:
            os.fsync(handle.fileno())
        if probe.read_text(encoding="utf-8") != "glyph-colab-preflight\n":
            raise IOError("Local write/read probe failed")

    inference = []
    if not args.skip_inference:
        device = torch.device("cuda" if environment["cuda_available"] else "cpu")
        inference = inference_smoke(model, tokenizer_path, device)

    return {
        "status": "PASS",
        "run_id": args.run_id,
        "environment": environment,
        "checkpoint": checkpoint,
        "tokenizer": {"path": str(tokenizer_path), "sha256": tokenizer_sha},
        "dataset": str(dataset_path),
        "label_audit": audit,
        "inference_smoke": inference,
        "predicted_training_mode": args.precision,
        "warnings": warnings,
        "training_performed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Glyph Colab CUDA preflight (never trains)")
    parser.add_argument("--run-id", default=datetime.now(timezone.utc).strftime("preflight-%Y%m%dT%H%M%SZ"))
    parser.add_argument("--checkpoint", default="checkpoints/glyph-100m-base44k.pt")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--dataset", default="data/sft/glyph100_sft_smoke_v0_3.jsonl")
    parser.add_argument("--reports-dir", default="reports")
    parser.add_argument("--expected-step", type=int, default=44000)
    parser.add_argument("--expected-variant", default="glyph-100m")
    parser.add_argument("--expected-context", type=int, default=512)
    parser.add_argument("--expected-dataset", default="glyph100_v2_3_1")
    parser.add_argument("--expected-tokenizer-sha", default=EXPECTED_TOKENIZER_SHA)
    parser.add_argument("--minimum-free-vram-gb", type=float, default=2.0)
    parser.add_argument("--precision", choices=("fp32", "fp16", "bf16"), default="fp32")
    parser.add_argument("--allow-cpu", action="store_true")
    parser.add_argument("--skip-inference", action="store_true")
    parser.add_argument("--skip-label-audit", action="store_true")
    args = parser.parse_args()

    reports_dir = resolve(args.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    json_path = reports_dir / f"colab_preflight_{args.run_id}.json"
    md_path = reports_dir / f"colab_preflight_{args.run_id}.md"
    try:
        result = run(args)
    except Exception as exc:
        result = {
            "status": "FAIL",
            "run_id": args.run_id,
            "environment": environment_report(),
            "checkpoint": None,
            "label_audit": None,
            "inference_smoke": [],
            "warnings": [f"{type(exc).__name__}: {exc}"],
            "training_performed": False,
        }
        atomic_write_json(json_path, result)
        md_path.write_text(markdown_report(result), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(1) from exc
    atomic_write_json(json_path, result)
    md_path.write_text(markdown_report(result), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
