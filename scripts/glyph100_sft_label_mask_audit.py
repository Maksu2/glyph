#!/usr/bin/env python3
"""Audit SFT label masking before/after the assistant boundary fix."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finetune import SFTDataset
from scripts.sft_utils import ASSISTANT_TOKEN, END_TOKEN, USER_TOKEN, format_sft_text, load_jsonl, load_sentencepiece


OLD_BOUNDARY = "i <= assistant_pos"
NEW_BOUNDARY = "i < assistant_pos"


def piece(sp, token_id: int) -> str:
    if token_id == -100:
        return "-100"
    return sp.id_to_piece(int(token_id))


def make_labels(ids: list[int], assistant_id: int, pad_id: int, old_boundary: bool) -> tuple[list[int], list[int], int] | None:
    if len(ids) < 2:
        return None
    x = list(ids[:-1])
    y = list(ids[1:])
    try:
        assistant_pos = x.index(assistant_id)
    except ValueError:
        return None
    y_masked = list(y)
    for i in range(len(y_masked)):
        if old_boundary:
            if i <= assistant_pos:
                y_masked[i] = -100
        else:
            if i < assistant_pos:
                y_masked[i] = -100
        if y[i] == pad_id:
            y_masked[i] = -100
    return x, y_masked, assistant_pos


def first_supervised(labels: list[int]) -> tuple[int | None, int | None]:
    for idx, label in enumerate(labels):
        if label != -100:
            return idx, int(label)
    return None, None


def supervised_count(labels: list[int]) -> int:
    return sum(1 for label in labels if label != -100)


def select_examples(records: list[dict]) -> list[dict]:
    selected: list[dict] = []
    requirements = [
        ("Loss", lambda r: str(r.get("response", "")).startswith("Loss pokazuje")),
        ("Nie.", lambda r: str(r.get("response", "")).startswith("Nie.")),
        ("Projekt", lambda r: str(r.get("response", "")).startswith("Projekt")),
    ]
    used_ids = set()
    for _, pred in requirements:
        for record in records:
            if pred(record) and record.get("id") not in used_ids:
                selected.append(record)
                used_ids.add(record.get("id"))
                break
    for record in records:
        if len(selected) >= 5:
            break
        if record.get("id") not in used_ids:
            selected.append(record)
            used_ids.add(record.get("id"))
    return selected


def audit_example(sp, record: dict, context_len: int) -> dict:
    pad_id = sp.pad_id()
    if pad_id < 0:
        pad_id = 0
    assistant_id = sp.piece_to_id(ASSISTANT_TOKEN)
    end_id = sp.piece_to_id(END_TOKEN)
    ids = list(sp.encode(format_sft_text(record), out_type=int))
    old_pair = make_labels(ids, assistant_id, pad_id, old_boundary=True)
    new_pair = make_labels(ids, assistant_id, pad_id, old_boundary=False)
    if old_pair is None or new_pair is None:
        raise ValueError(f"record has no assistant token: {record.get('id')}")
    x_old, y_old, assistant_pos = old_pair
    x_new, y_new, _ = new_pair
    old_idx, old_id = first_supervised(y_old)
    new_idx, new_id = first_supervised(y_new)
    return {
        "id": record.get("id"),
        "category": record.get("category"),
        "instruction": record.get("instruction"),
        "response": record.get("response"),
        "template": format_sft_text(record),
        "token_count": len(ids),
        "fits_context": len(ids) <= context_len,
        "assistant_pos_in_x": assistant_pos,
        "x_assistant_piece": piece(sp, x_new[assistant_pos]),
        "y_at_assistant_pos_piece": piece(sp, sp.encode(format_sft_text(record), out_type=int)[assistant_pos + 1]),
        "old": {
            "boundary": OLD_BOUNDARY,
            "first_supervised_index": old_idx,
            "first_supervised_piece": piece(sp, old_id) if old_id is not None else None,
            "supervised_labels": supervised_count(y_old),
            "end_token_supervised": end_id in y_old,
            "prompt_mask_ok": all(label == -100 for label in y_old[:assistant_pos]),
            "assistant_token_masked": y_old[assistant_pos - 1] == -100 if assistant_pos > 0 else None,
        },
        "new": {
            "boundary": NEW_BOUNDARY,
            "first_supervised_index": new_idx,
            "first_supervised_piece": piece(sp, new_id) if new_id is not None else None,
            "first_response_token_is_supervised": new_idx == assistant_pos,
            "supervised_labels": supervised_count(y_new),
            "end_token_supervised": end_id in y_new,
            "prompt_mask_ok": all(label == -100 for label in y_new[:assistant_pos]),
            "assistant_token_masked": y_new[assistant_pos - 1] == -100 if assistant_pos > 0 else None,
            "first_ten_supervised_pieces": [piece(sp, label) for label in y_new if label != -100][:10],
        },
    }


def build_markdown(payload: dict) -> str:
    lines = [
        "# Glyph-100M SFT label mask fix audit",
        "",
        "## Verdict",
        "",
        payload["verdict"],
        "",
        "## Boundary",
        "",
        f"- old: `{payload['old_boundary']}`",
        f"- new: `{payload['new_boundary']}`",
        "",
        "## Checks",
        "",
    ]
    for key, value in payload["checks"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Dataset-Level Counts",
            "",
            f"- train examples checked: {payload['dataset_counts']['train_records']}",
            f"- usable examples after fixed mask: {payload['dataset_counts']['usable_after_fix']}",
            f"- examples without assistant labels after fix: {payload['dataset_counts']['without_assistant_labels_after_fix']}",
            f"- total supervised labels old: {payload['dataset_counts']['total_supervised_labels_old']}",
            f"- total supervised labels new: {payload['dataset_counts']['total_supervised_labels_new']}",
            f"- supervised labels gained: {payload['dataset_counts']['supervised_labels_gained']}",
            "",
            "## Before / After Examples",
            "",
        ]
    )
    for item in payload["examples"]:
        lines.extend(
            [
                f"### {item['id']} / {item['category']}",
                "",
                f"Instruction: {item['instruction']}",
                "",
                f"Response: {item['response']}",
                "",
                f"- old first supervised piece: `{item['old']['first_supervised_piece']}`",
                f"- new first supervised piece: `{item['new']['first_supervised_piece']}`",
                f"- new first response supervised: `{item['new']['first_response_token_is_supervised']}`",
                f"- old supervised labels: `{item['old']['supervised_labels']}`",
                f"- new supervised labels: `{item['new']['supervised_labels']}`",
                f"- `<|end|>` supervised after fix: `{item['new']['end_token_supervised']}`",
                f"- prompt/user/instruction masked after fix: `{item['new']['prompt_mask_ok']}`",
                f"- first supervised sequence after fix: `{' '.join(item['new']['first_ten_supervised_pieces'])}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Previous SFT Smoke Status",
            "",
            "The previous SFT smoke run is marked invalid-for-quality because it trained with the label mask off-by-one bug.",
            "Its checkpoints and reports are preserved, but quality conclusions from that run should not be used as evidence against SFT.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit Glyph SFT label mask boundary")
    parser.add_argument("--dataset", default="data/sft/glyph100_sft_smoke_v0.jsonl")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--context-len", type=int, default=512)
    parser.add_argument("--out-md", default="reports/glyph100_sft_label_mask_fix_audit.md")
    parser.add_argument("--out-json", default="reports/glyph100_sft_label_mask_fix_audit.json")
    args = parser.parse_args()

    sp = load_sentencepiece(args.tokenizer)
    loaded = load_jsonl(args.dataset)
    pad_id = sp.pad_id()
    if pad_id < 0:
        pad_id = 0
    assistant_id = sp.piece_to_id(ASSISTANT_TOKEN)

    examples = [audit_example(sp, record, args.context_len) for record in select_examples(loaded.records)]

    total_old = 0
    total_new = 0
    without_labels = 0
    for record in loaded.records:
        ids = list(sp.encode(format_sft_text(record), out_type=int))
        old_pair = make_labels(ids, assistant_id, pad_id, old_boundary=True)
        new_pair = make_labels(ids, assistant_id, pad_id, old_boundary=False)
        if new_pair is None or supervised_count(new_pair[1]) == 0:
            without_labels += 1
        if old_pair is not None:
            total_old += supervised_count(old_pair[1])
        if new_pair is not None:
            total_new += supervised_count(new_pair[1])

    dataset = SFTDataset(args.dataset, sp, args.context_len)
    batch_x, batch_y = dataset._batch_tensors(list(range(min(4, len(dataset.pairs)))), torch.device("cpu"))
    padding_ignore_ok = True
    for row_idx, (_, labels) in enumerate(dataset.pairs[: min(4, len(dataset.pairs))]):
        raw_len = len(labels)
        if raw_len < batch_y.shape[1] and not torch.all(batch_y[row_idx, raw_len:] == -100).item():
            padding_ignore_ok = False

    checks = {
        "first_Loss_token_supervised": examples[0]["new"]["first_supervised_piece"] == "▁Los",
        "first_Nie_token_supervised": any(
            item["response"].startswith("Nie.") and item["new"]["first_supervised_piece"] == "▁Nie" for item in examples
        ),
        "first_Projekt_token_supervised": any(
            item["response"].startswith("Projekt") and item["new"]["first_supervised_piece"] == "▁Projekt" for item in examples
        ),
        "end_token_supervised_all_examples": all(item["new"]["end_token_supervised"] for item in examples),
        "padding_ignore_index_minus_100": padding_ignore_ok,
        "prompt_tokens_not_supervised_all_examples": all(item["new"]["prompt_mask_ok"] for item in examples),
        "no_examples_without_assistant_labels": without_labels == 0,
    }
    all_ok = all(bool(value) for value in checks.values())
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "verdict": "PASS: fixed label mask supervises the first assistant response token." if all_ok else "FAIL: label mask audit found issues.",
        "old_boundary": OLD_BOUNDARY,
        "new_boundary": NEW_BOUNDARY,
        "dataset": args.dataset,
        "tokenizer": args.tokenizer,
        "checks": checks,
        "dataset_counts": {
            "train_records": len(loaded.records),
            "usable_after_fix": len(dataset.pairs),
            "without_assistant_labels_after_fix": without_labels,
            "total_supervised_labels_old": total_old,
            "total_supervised_labels_new": total_new,
            "supervised_labels_gained": total_new - total_old,
            "padding_batch_shape": list(batch_x.shape),
        },
        "examples": examples,
        "previous_sft_smoke_quality_status": "invalid-for-quality",
        "previous_sft_smoke_invalid_reason": "label mask off-by-one bug masked first assistant response token",
    }

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_json).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(args.out_md).write_text(build_markdown(payload), encoding="utf-8")
    if not all_ok:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
