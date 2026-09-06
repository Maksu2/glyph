#!/usr/bin/env python3
"""Fetch only audited Polish Dynaword source files with size guards."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "configs/glyph100_v2_4_core.json"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_file(url: str, target: Path, expected_bytes: int, *, dry_run: bool) -> dict[str, Any]:
    target.parent.mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {
        "url": url,
        "path": str(target.relative_to(ROOT)),
        "expected_bytes": expected_bytes,
        "downloaded": False,
    }
    if target.exists() and target.stat().st_size == expected_bytes:
        result.update(size_bytes=target.stat().st_size, sha256=sha256_file(target), status="already_present")
        return result
    if dry_run:
        result.update(size_bytes=target.stat().st_size if target.exists() else 0, status="dry_run")
        return result

    partial = target.with_suffix(target.suffix + ".part")
    offset = partial.stat().st_size if partial.exists() else 0
    headers = {"User-Agent": "GlyphDatasetBuilder/2.4"}
    if offset:
        headers["Range"] = f"bytes={offset}-"
    with requests.get(url, headers=headers, stream=True, timeout=(30, 180)) as response:
        if offset and response.status_code != 206:
            partial.unlink(missing_ok=True)
            offset = 0
            response.close()
            return fetch_file(url, target, expected_bytes, dry_run=dry_run)
        response.raise_for_status()
        mode = "ab" if offset else "wb"
        started = time.monotonic()
        with partial.open(mode) as handle:
            for chunk in response.iter_content(chunk_size=8 * 1024 * 1024):
                if chunk:
                    handle.write(chunk)
        result["download_seconds"] = round(time.monotonic() - started, 3)
    size = partial.stat().st_size
    if size != expected_bytes:
        raise RuntimeError(f"size mismatch for {target}: expected {expected_bytes}, got {size}")
    os.replace(partial, target)
    result.update(
        size_bytes=size,
        sha256=sha256_file(target),
        downloaded=True,
        status="downloaded",
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-total-gb", type=float, default=2.5)
    args = parser.parse_args()

    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    raw_root = ROOT / config["raw_root"]
    if "sources" in config:
        sources = [source for source in config["sources"] if source["kind"] == "dynaword_parquet"]
    else:
        sources = [config["supplement"]]
    total = sum(int(source["expected_bytes"]) for source in sources)
    if total > args.max_total_gb * 1024**3:
        raise SystemExit(f"refusing {total / 1024**3:.2f} GiB download; limit is {args.max_total_gb:.2f} GiB")

    rows = []
    for source in sources:
        target = raw_root / source["name"] / f"{source['name']}.parquet"
        print(f"{source['name']}: {source['expected_bytes'] / 1024**2:.1f} MiB -> {target}", flush=True)
        rows.append(fetch_file(source["url"], target, int(source["expected_bytes"]), dry_run=args.dry_run))

    manifest_path = raw_root / "manifest.json"
    previous: dict[str, Any] = {}
    if manifest_path.exists():
        try:
            previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous = {}
    merged_sources = {str(row.get("path")): row for row in previous.get("sources", [])}
    merged_sources.update({str(row.get("path")): row for row in rows})
    configs = set(previous.get("configs", []))
    if previous.get("config"):
        configs.add(str(previous["config"]))
    configs.add(str(config_path.relative_to(ROOT)))
    manifest = {
        "generated_at": now_utc(),
        "configs": sorted(configs),
        "dry_run": args.dry_run,
        "total_expected_bytes": sum(int(row.get("expected_bytes") or 0) for row in merged_sources.values()),
        "sources": sorted(merged_sources.values(), key=lambda row: str(row.get("path"))),
    }
    if not args.dry_run:
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
