#!/usr/bin/env python3
"""Audit train/validation leakage at parent-document level."""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from glyph100_dataset_identity import parent_doc_id_for  # noqa: E402


def audit(path: Path) -> dict:
    parents: dict[tuple[str, str], dict] = {}
    docs = 0
    missing_split = 0
    missing_parent = 0
    source_docs: collections.Counter[str] = collections.Counter()
    source_parents: dict[str, set[str]] = collections.defaultdict(set)

    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            docs += 1
            source = str(record.get("source") or "unknown")
            split = str((record.get("meta") or {}).get("split") or record.get("split") or "")
            if not split:
                missing_split += 1
            parent_id = parent_doc_id_for(record)
            if not parent_id:
                missing_parent += 1
                parent_id = f"__missing__:{docs}"
            key = (source, parent_id)
            state = parents.setdefault(
                key,
                {"source": source, "parent_doc_id": parent_id, "splits": set(), "docs": 0, "examples": []},
            )
            state["splits"].add(split)
            state["docs"] += 1
            if len(state["examples"]) < 4:
                state["examples"].append(
                    {
                        "doc_id": record.get("doc_id"),
                        "source_id": record.get("source_id"),
                        "split": split,
                        "title": record.get("title"),
                    }
                )
            source_docs[source] += 1
            source_parents[source].add(parent_id)

    leaked = []
    for state in parents.values():
        meaningful = {split for split in state["splits"] if split}
        if len(meaningful) > 1:
            leaked.append({**state, "splits": sorted(meaningful)})
    leaked.sort(key=lambda row: (-row["docs"], row["source"], row["parent_doc_id"]))

    return {
        "docs_jsonl": str(path),
        "documents": docs,
        "parent_documents": len(parents),
        "missing_split": missing_split,
        "missing_parent_identity": missing_parent,
        "leaked_parent_documents": len(leaked),
        "leaked_document_chunks": sum(row["docs"] for row in leaked),
        "source_documents": dict(source_docs),
        "source_parent_documents": {source: len(values) for source, values in source_parents.items()},
        "leakage_examples": leaked[:100],
        "passes_no_parent_leakage": len(leaked) == 0 and missing_split == 0 and missing_parent == 0,
    }


def render_markdown(payload: dict) -> str:
    verdict = "PASS" if payload["passes_no_parent_leakage"] else "FAIL"
    lines = [
        "# Glyph-100M Parent-Document Split Audit",
        "",
        f"**Verdict: {verdict}.**",
        "",
        f"- documents: `{payload['documents']:,}`",
        f"- parent documents: `{payload['parent_documents']:,}`",
        f"- leaked parents: `{payload['leaked_parent_documents']:,}`",
        f"- chunks belonging to leaked parents: `{payload['leaked_document_chunks']:,}`",
        f"- missing split: `{payload['missing_split']:,}`",
        f"- missing parent identity: `{payload['missing_parent_identity']:,}`",
        "",
        "## Leakage Examples",
        "",
    ]
    if not payload["leakage_examples"]:
        lines.append("No parent document appears in both train and validation.")
    for row in payload["leakage_examples"]:
        lines.extend(
            [
                f"### {row['source']} / {row['parent_doc_id']}",
                "",
                f"Splits: `{', '.join(row['splits'])}`; chunks: `{row['docs']}`",
                "",
                "```json",
                json.dumps(row["examples"], ensure_ascii=False, indent=2),
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs", type=Path, default=Path("data/processed/glyph100_v2_3_1_docs.jsonl"))
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()

    payload = audit(args.docs)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(render_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ["documents", "parent_documents", "leaked_parent_documents", "passes_no_parent_leakage"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
