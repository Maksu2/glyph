#!/usr/bin/env python3
"""Validate, archive and optionally copy Glyph Colab results to mounted Drive."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import ModelConfig
from model import GPT
from scripts.colab_bundle_utils import (
    atomic_copy_verified,
    atomic_write_json,
    create_tar_zst,
    file_record,
    safe_extract_tar_zst,
    sha256_file,
    write_sha256sums,
)
from scripts.sft_utils import ASSISTANT_TOKEN, END_TOKEN, USER_TOKEN, load_sentencepiece


APPROVED_TOKENIZER_SHA = "21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029"
COPY_CONFIRMATION = "COPY_VALIDATED_RESULT"


def resolve(path: str | Path) -> Path:
    value = Path(path).expanduser()
    if not value.is_absolute():
        value = ROOT / value
    return value.resolve()


def torch_load(path: Path) -> dict:
    kwargs = {"map_location": "cpu", "weights_only": False}
    try:
        return torch.load(path, mmap=True, **kwargs)
    except (TypeError, RuntimeError):
        return torch.load(path, **kwargs)


def validate_checkpoint(checkpoint: Path, tokenizer: Path) -> tuple[dict, GPT]:
    state = torch_load(checkpoint)
    model_config = state.get("model_config") or {}
    step = int(state.get("current_step", state.get("step", 0)))
    tokenizer_sha = sha256_file(tokenizer)
    problems = []
    if state.get("variant") != "glyph-100m":
        problems.append(f"variant={state.get('variant')!r}")
    if not state.get("model"):
        problems.append("model state missing")
    if int(state.get("context_length", model_config.get("context_len", 0))) != 512:
        problems.append("context length is not 512")
    if tokenizer_sha != APPROVED_TOKENIZER_SHA:
        problems.append("tokenizer file SHA is not approved")
    if state.get("tokenizer_sha256") != tokenizer_sha:
        problems.append("checkpoint tokenizer SHA mismatch")
    if problems:
        raise ValueError("Result checkpoint validation failed: " + "; ".join(problems))

    allowed = ModelConfig.__dataclass_fields__
    cfg = ModelConfig(**{key: value for key, value in model_config.items() if key in allowed})
    model = GPT(cfg)
    loaded = model.load_state_dict(state["model"], strict=True)
    if loaded.missing_keys or loaded.unexpected_keys:
        raise ValueError(f"Strict state load failed: {loaded}")
    return {
        "path": str(checkpoint),
        "sha256": sha256_file(checkpoint),
        "size": checkpoint.stat().st_size,
        "step": step,
        "variant": state.get("variant"),
        "context_length": cfg.context_len,
        "tokenizer_sha256": tokenizer_sha,
        "model_config": model_config,
        "model_tensors": len(state["model"]),
        "unique_parameters": sum(parameter.numel() for parameter in model.parameters()),
        "strict_state_load": True,
    }, model


@torch.no_grad()
def inference_smoke(model: GPT, tokenizer_path: Path) -> list[dict]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    sp = load_sentencepiece(tokenizer_path)
    end_id = sp.piece_to_id(END_TOKEN)
    prompts = [
        "Wyjasnij krotko, czym jest kopia zapasowa.",
        "Czy ten wynik jest poprawny?",
    ]
    outputs = []
    for prompt in prompts:
        formatted = f"{USER_TOKEN}\n{prompt}\n{ASSISTANT_TOKEN}\n"
        ids = list(sp.encode(formatted, out_type=int))
        source = torch.tensor([ids], dtype=torch.long, device=device)
        for name, ngram in (("greedy", 0), ("no_repeat_ngram_3", 3)):
            generated = model.generate(
                source,
                max_new_tokens=48,
                temperature=0.0,
                no_repeat_ngram_size=ngram,
                eos_token_id=end_id,
            )[0, len(ids) :].detach().cpu().tolist()
            outputs.append(
                {
                    "prompt": prompt,
                    "mode": name,
                    "generated_tokens": len(generated),
                    "ended_with_end_token": end_id in generated,
                    "text": sp.decode(generated),
                }
            )
    model.to("cpu")
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return outputs


def select_checkpoint(run_root: Path, explicit: str | None) -> Path:
    if explicit:
        path = resolve(explicit)
        if not path.is_file():
            raise FileNotFoundError(path)
        return path
    for candidate in (run_root / "checkpoints/best.pt", run_root / "checkpoints/latest.pt"):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("No best.pt or latest.pt found; pass --checkpoint explicitly")


def collect_run_files(run_root: Path, checkpoint: Path, tokenizer: Path) -> list[tuple[Path, str]]:
    entries = [
        (checkpoint, f"result/checkpoints/{checkpoint.name}"),
        (tokenizer, "result/data/tokenizer.model"),
    ]
    for relative in ("run_config.json", "run_state.json"):
        path = run_root / relative
        if path.is_file():
            entries.append((path, f"result/{relative}"))
    for directory in ("logs", "reports"):
        root = run_root / directory
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".json", ".jsonl", ".log", ".md", ".txt"}:
                entries.append((path, f"result/{path.relative_to(run_root).as_posix()}"))
    return entries


def verify_result_archive(archive: Path, manifest: dict) -> dict:
    with tempfile.TemporaryDirectory(prefix="glyph-colab-result-verify-") as temp_name:
        destination = Path(temp_name)
        extracted = safe_extract_tar_zst(archive, destination)
        for member in manifest["members"]:
            path = destination / member["path"]
            if not path.is_file():
                raise FileNotFoundError(f"Missing result archive member: {member['path']}")
            if path.stat().st_size != member["size"] or sha256_file(path) != member["sha256"]:
                raise ValueError(f"Result archive member mismatch: {member['path']}")
        internal_manifest = destination / "result/manifest.json"
        if not internal_manifest.is_file():
            raise FileNotFoundError("Internal result manifest is missing")
        loaded = json.loads(internal_manifest.read_text(encoding="utf-8"))
        if loaded.get("checkpoint", {}).get("sha256") != manifest["checkpoint"]["sha256"]:
            raise ValueError("Internal result manifest does not match external validation")
    return {"status": "PASS", "extracted_files": len(extracted), "archive_sha256": sha256_file(archive)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and export a Glyph Colab result")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--checkpoint", default=None)
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--output-dir", default="/content/glyph-output/exports")
    parser.add_argument("--copy-to", default=None, help="Mounted Drive destination; no API is used")
    parser.add_argument("--confirm-copy", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    run_root = resolve(args.run_dir)
    tokenizer = resolve(args.tokenizer)
    if not run_root.is_dir():
        raise NotADirectoryError(run_root)
    if not tokenizer.is_file():
        raise FileNotFoundError(tokenizer)
    checkpoint = select_checkpoint(run_root, args.checkpoint)
    run_id = args.run_id or run_root.name
    checkpoint_info, model = validate_checkpoint(checkpoint, tokenizer)
    inference = inference_smoke(model, tokenizer)
    entries = collect_run_files(run_root, checkpoint, tokenizer)
    preview = {
        "run_id": run_id,
        "checkpoint": checkpoint_info,
        "inference_smoke": inference,
        "files": [{"source": str(path), "archive_path": arcname, "size": path.stat().st_size} for path, arcname in entries],
        "copy_requested": bool(args.copy_to),
        "copy_confirmed": args.confirm_copy == COPY_CONFIRMATION,
    }
    if args.dry_run:
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return

    output_dir = resolve(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive = output_dir / f"glyph-result-{run_id}-{timestamp}.tar.zst"
    external_manifest = output_dir / f"glyph-result-{run_id}-{timestamp}.manifest.json"
    sums = output_dir / f"glyph-result-{run_id}-{timestamp}.SHA256SUMS"
    for path in (archive, external_manifest, sums):
        if path.exists() and not args.force:
            raise FileExistsError(path)

    members = [file_record(path, arcname) for path, arcname in entries]
    manifest = {
        "format": "glyph-colab-result-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "checkpoint": checkpoint_info,
        "tokenizer": {"path": str(tokenizer), "sha256": sha256_file(tokenizer)},
        "inference_smoke": inference,
        "members": members,
        "validation": {
            "strict_state_load": True,
            "inference_before_export": True,
            "archive_reextract_required": True,
        },
    }
    with tempfile.TemporaryDirectory(prefix="glyph-colab-result-manifest-") as temp_name:
        internal_manifest = Path(temp_name) / "manifest.json"
        atomic_write_json(internal_manifest, manifest)
        archive_entries = entries + [(internal_manifest, "result/manifest.json")]
        create_tar_zst(archive, archive_entries)
    verification = verify_result_archive(archive, manifest)
    manifest["archive"] = {"path": archive.name, "size": archive.stat().st_size, "sha256": sha256_file(archive)}
    manifest["archive_verification"] = verification
    atomic_write_json(external_manifest, manifest)
    write_sha256sums(sums, [archive, external_manifest])

    copied = []
    if args.copy_to:
        if args.confirm_copy != COPY_CONFIRMATION:
            raise SystemExit(
                f"Local export is valid, but Drive copy was not confirmed. "
                f"Set --confirm-copy {COPY_CONFIRMATION} to copy it."
            )
        destination = resolve(args.copy_to)
        destination.mkdir(parents=True, exist_ok=True)
        for source in (archive, external_manifest, sums):
            target = destination / source.name
            if target.exists() and not args.force:
                raise FileExistsError(target)
            atomic_copy_verified(source, target)
            copied.append(str(target))

    result = {
        "status": "PASS",
        "archive": str(archive),
        "manifest": str(external_manifest),
        "sha256sums": str(sums),
        "verification": verification,
        "copied_to_mounted_drive": copied,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
