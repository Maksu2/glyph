"""Stable document identity helpers for source-aware Glyph datasets."""

from __future__ import annotations

import re
from typing import Any

from glyph100_dataset_v2_filter import stable_bucket


CHUNK_SUFFIX_RE = re.compile(r"(?:#|[-_/])chunk[-_]?\d+$", re.IGNORECASE)


def parent_doc_id_for(record: dict[str, Any]) -> str:
    """Return an identity shared by every chunk of the same source document."""
    explicit = str(record.get("parent_doc_id") or "").strip()
    if explicit:
        return explicit

    meta = record.get("meta") or {}
    source_meta = meta.get("source_meta") or {}
    for value in (
        source_meta.get("parent_doc_id"),
        source_meta.get("slug"),
        meta.get("parent_doc_id"),
    ):
        value = str(value or "").strip()
        if value:
            return value

    source_id = str(record.get("source_id") or "").strip()
    if source_id and CHUNK_SUFFIX_RE.search(source_id):
        return CHUNK_SUFFIX_RE.sub("", source_id)

    doc_id = str(record.get("doc_id") or record.get("id") or "").strip()
    if doc_id:
        return doc_id

    return source_id


def parent_split_for(record: dict[str, Any], val_per_mille: int) -> str:
    source = str(record.get("source") or "")
    parent_doc_id = parent_doc_id_for(record)
    if not parent_doc_id:
        raise ValueError("Document has no stable parent identity")
    return "val" if stable_bucket(f"{source}:{parent_doc_id}", 1000) < val_per_mille else "train"
