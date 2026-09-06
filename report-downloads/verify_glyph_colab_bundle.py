#!/usr/bin/env python3
"""Verify Glyph Colab archives, metadata, model tensors and SFT labels."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.colab_bundle_utils import read_sha256sums, safe_extract_tar_zst, sha256_file


EXPECTED_TOKENIZER_SHA = "21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029"


def load_manifest(bundle_dir: Path) -> dict:
    manifest_path = bundle_dir / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("bundle_version") != "1.0":
        raise ValueError(f"Unsupported bundle version: {manifest.get('bundle_version')!r}")
    return manifest


def verify_outer_files(bundle_dir: Path, manifest: dict) -> dict:
    sums_path = bundle_dir / "SHA256SUMS"
    if not sums_path.is_file():
        raise FileNotFoundError(sums_path)
    expected = read_sha256sums(sums_path)
    required = ["manifest.json"]
    required.extend(item["path"] for item in manifest.get("archives", []))
    required.extend(item["path"] for item in manifest.get("external_files", []))
    checked = []
    for name in required:
        path = bundle_dir / name
        if not path.is_file():
            raise FileNotFoundError(path)
        if name not in expected:
            raise ValueError(f"SHA256SUMS does not list {name}")
        actual = sha256_file(path)
        if actual != expected[name]:
            raise ValueError(f"Outer file SHA mismatch for {name}: {actual} != {expected[name]}")
        checked.append(name)
    return {"sha256sums": str(sums_path), "checked_files": checked}


def verify_archives(bundle_dir: Path, manifest: dict, extract_root: Path) -> list[dict]:
    results = []
    for archive in manifest.get("archives", []):
        path = bundle_dir / archive["path"]
        if not path.is_file():
            raise FileNotFoundError(path)
        actual = sha256_file(path)
        if actual != archive["sha256"]:
            raise ValueError(f"Archive SHA mismatch for {path.name}: {actual} != {archive['sha256']}")
        extracted = safe_extract_tar_zst(path, extract_root)
        results.append({"role": archive["role"], "path": path.name, "sha256": actual, "extracted": len(extracted)})

    for archive in manifest.get("archives", []):
        for member in archive.get("members", []):
            path = extract_root / member["path"]
            if not path.is_file():
                raise FileNotFoundError(f"Missing archive member: {member['path']}")
            if path.stat().st_size != member["size"]:
                raise ValueError(f"Size mismatch for {member['path']}")
            actual = sha256_file(path)
            if actual != member["sha256"]:
                raise ValueError(f"SHA mismatch for extracted member {member['path']}")
    return results


def checkpoint_metadata(state: dict) -> dict:
    cfg = state.get("model_config") or {}
    return {
        "step": int(state.get("current_step", state.get("step", 0))),
        "variant": state.get("variant"),
        "dataset": state.get("dataset_name", state.get("dataset")),
        "context_length": int(state.get("context_length", cfg.get("context_len", 0))),
        "tokenizer_sha256": state.get("tokenizer_sha256"),
        "model_config": cfg,
    }


def validate_metadata(metadata: dict) -> None:
    if metadata["step"] != 44_000:
        raise ValueError(f"Expected step 44000, got {metadata['step']}")
    if metadata["variant"] != "glyph-100m":
        raise ValueError(f"Expected glyph-100m, got {metadata['variant']!r}")
    if metadata["context_length"] != 512:
        raise ValueError(f"Expected context 512, got {metadata['context_length']}")
    if metadata["tokenizer_sha256"] != EXPECTED_TOKENIZER_SHA:
        raise ValueError("Checkpoint metadata has the wrong tokenizer SHA")
    if metadata["dataset"] != "glyph100_v2_3_1":
        raise ValueError(f"Unexpected pretraining dataset metadata: {metadata['dataset']!r}")


def activate_extracted_code(root: Path) -> None:
    sys.path.insert(0, str(root))
    scripts_package = sys.modules.get("scripts")
    if scripts_package is not None and hasattr(scripts_package, "__path__"):
        scripts_path = str(root / "scripts")
        if scripts_path not in scripts_package.__path__:
            scripts_package.__path__.insert(0, scripts_path)
    for name in ("config", "model", "model.transformer", "finetune", "scripts.sft_utils"):
        sys.modules.pop(name, None)


def run_label_audit(root: Path, dataset_path: Path, tokenizer_path: Path) -> dict:
    activate_extracted_code(root)
    from finetune import SFTDataset
    from scripts.sft_utils import ASSISTANT_TOKEN, END_TOKEN, format_sft_text, load_jsonl, load_sentencepiece

    sp = load_sentencepiece(tokenizer_path)
    assistant_id = sp.piece_to_id(ASSISTANT_TOKEN)
    end_id = sp.piece_to_id(END_TOKEN)
    if assistant_id < 0 or end_id < 0:
        raise ValueError("SFT special tokens are missing from tokenizer")
    loaded = load_jsonl(dataset_path)
    if loaded.invalid_json or loaded.missing_fields:
        raise ValueError("Dataset JSONL validation failed")
    dataset = SFTDataset(str(dataset_path), sp, 512)

    checked = 0
    first_response_supervised = True
    prompt_masked = True
    end_supervised = True
    for record in loaded.records[: min(64, len(loaded.records))]:
        ids = list(sp.encode(format_sft_text(record), out_type=int))
        pair = dataset._make_pair(ids)
        if pair is None:
            raise ValueError(f"No assistant labels in record {record.get('id')}")
        x, labels = pair
        assistant_pos = x.index(assistant_id)
        first_response_supervised &= labels[assistant_pos] != -100
        prompt_masked &= all(value == -100 for value in labels[:assistant_pos])
        end_supervised &= end_id in labels
        checked += 1

    order = sorted(range(len(dataset.pairs)), key=lambda idx: len(dataset.pairs[idx][0]))
    chosen = [order[0], order[-1]] if len(order) > 1 else order
    _, padded_labels = dataset._batch_tensors(chosen, torch.device("cpu"))
    padding_ignored = True
    for row, pair_idx in enumerate(chosen):
        raw_len = len(dataset.pairs[pair_idx][1])
        if raw_len < padded_labels.shape[1]:
            padding_ignored &= bool(torch.all(padded_labels[row, raw_len:] == -100).item())

    result = {
        "dataset_examples": len(dataset.pairs),
        "sampled_examples": checked,
        "boundary": "i < assistant_pos",
        "first_assistant_response_token_supervised": first_response_supervised,
        "prompt_not_supervised": prompt_masked,
        "end_token_supervised": end_supervised,
        "padding_ignore_index_minus_100": padding_ignored,
    }
    if not all(value for key, value in result.items() if isinstance(value, bool)):
        raise ValueError(f"SFT label audit failed: {result}")
    return result


def load_and_validate_model(root: Path, checkpoint_path: Path) -> tuple[object, dict]:
    activate_extracted_code(root)
    from config import ModelConfig
    from model import GPT

    state = torch.load(checkpoint_path, map_location="cpu", weights_only=False, mmap=True)
    metadata = checkpoint_metadata(state)
    validate_metadata(metadata)
    cfg = ModelConfig(**{key: value for key, value in metadata["model_config"].items() if key in ModelConfig.__dataclass_fields__})
    model = GPT(cfg)
    result = model.load_state_dict(state["model"], strict=True)
    if result.missing_keys or result.unexpected_keys:
        raise ValueError(f"State dict mismatch: {result}")
    return model, {
        **metadata,
        "model_tensors": len(state["model"]),
        "unique_parameters": sum(parameter.numel() for parameter in model.parameters()),
        "missing_keys": list(result.missing_keys),
        "unexpected_keys": list(result.unexpected_keys),
    }


@torch.no_grad()
def cpu_inference(model, tokenizer_path: Path) -> dict:
    from scripts.sft_utils import ASSISTANT_TOKEN, END_TOKEN, USER_TOKEN, load_sentencepiece

    sp = load_sentencepiece(tokenizer_path)
    prompt = f"{USER_TOKEN}\nWyjaśnij krótko, czym jest model językowy.\n{ASSISTANT_TOKEN}\n"
    input_ids = list(sp.encode(prompt, out_type=int))
    tensor = torch.tensor([input_ids], dtype=torch.long)
    end_id = sp.piece_to_id(END_TOKEN)
    output = model.generate(tensor, max_new_tokens=12, temperature=0.0, eos_token_id=end_id)
    generated = output[0, len(input_ids):].tolist()
    return {
        "prompt": prompt,
        "generated_tokens": len(generated),
        "text": sp.decode(generated),
    }


def verify(bundle_dir: Path, work_dir: Path, structural_only: bool, run_cpu_inference: bool) -> dict:
    manifest = load_manifest(bundle_dir)
    outer_files = verify_outer_files(bundle_dir, manifest)
    work_dir.mkdir(parents=True, exist_ok=True)
    archives = verify_archives(bundle_dir, manifest, work_dir)

    tokenizer_path = work_dir / manifest["tokenizer"]["path"]
    tokenizer_sha = sha256_file(tokenizer_path)
    if tokenizer_sha != manifest["tokenizer"]["sha256"] or tokenizer_sha != EXPECTED_TOKENIZER_SHA:
        raise ValueError("Tokenizer SHA verification failed")

    dataset_path = work_dir / manifest["dataset"]["source_path"]
    if not dataset_path.is_file():
        raise FileNotFoundError(dataset_path)
    if sha256_file(dataset_path) != manifest["dataset"]["sha256"]:
        raise ValueError("Dataset SHA verification failed")

    label_audit = run_label_audit(work_dir, dataset_path, tokenizer_path)
    test_mode = bool(manifest.get("test_mode"))
    checkpoint_info: dict
    inference = None
    if test_mode or structural_only:
        if test_mode:
            fixture = work_dir / manifest["checkpoint"]["bundle_path"]
            fixture_meta = json.loads(fixture.read_text(encoding="utf-8"))
            validate_metadata(fixture_meta)
            checkpoint_info = {**fixture_meta, "validation": "metadata-only structural fixture"}
        else:
            checkpoint_info = {**manifest["checkpoint"], "validation": "skipped by --structural-only"}
    else:
        checkpoint_path = work_dir / manifest["checkpoint"]["bundle_path"]
        model, checkpoint_info = load_and_validate_model(work_dir, checkpoint_path)
        if run_cpu_inference:
            inference = cpu_inference(model, tokenizer_path)

    return {
        "status": "PASS",
        "bundle_version": manifest["bundle_version"],
        "test_mode": test_mode,
        "archives": archives,
        "outer_files": outer_files,
        "tokenizer_sha256": tokenizer_sha,
        "dataset": {"path": manifest["dataset"]["source_path"], "examples": manifest["dataset"]["examples"]},
        "checkpoint": checkpoint_info,
        "label_audit": label_audit,
        "cpu_inference": inference,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a Glyph Colab bundle")
    parser.add_argument("--bundle-dir", default="dist/glyph-colab")
    parser.add_argument("--work-dir", default=None)
    parser.add_argument("--structural-only", action="store_true")
    parser.add_argument("--cpu-inference", action="store_true")
    parser.add_argument("--keep-extracted", action="store_true")
    parser.add_argument("--report-json", default=None)
    args = parser.parse_args()

    bundle_dir = Path(args.bundle_dir).expanduser().resolve()
    if args.work_dir:
        work_dir = Path(args.work_dir).expanduser().resolve()
        if work_dir.exists() and any(work_dir.iterdir()):
            raise FileExistsError(f"Verifier work directory is not empty: {work_dir}")
        result = verify(bundle_dir, work_dir, args.structural_only, args.cpu_inference)
    else:
        temp = tempfile.TemporaryDirectory(prefix="glyph-colab-verify-")
        try:
            work_dir = Path(temp.name)
            result = verify(bundle_dir, work_dir, args.structural_only, args.cpu_inference)
            if args.keep_extracted:
                kept = bundle_dir / "verified-extracted"
                if kept.exists():
                    raise FileExistsError(kept)
                shutil.copytree(work_dir, kept)
                result["kept_extracted"] = str(kept)
        finally:
            temp.cleanup()

    if args.report_json:
        Path(args.report_json).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
