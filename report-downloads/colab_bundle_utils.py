#!/usr/bin/env python3
"""Small, dependency-light helpers shared by the Glyph Colab tooling."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tarfile
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Iterable, Iterator


CHUNK_SIZE = 4 * 1024 * 1024


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: str | Path, logical_path: str | None = None) -> dict:
    target = Path(path)
    return {
        "path": logical_path or target.as_posix(),
        "size": target.stat().st_size,
        "sha256": sha256_file(target),
    }


def atomic_write_json(path: str | Path, payload: dict | list) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, target)


def atomic_copy_verified(source: str | Path, destination: str | Path) -> Path:
    source = Path(source)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_suffix(destination.suffix + ".tmp")
    shutil.copy2(source, tmp)
    if sha256_file(source) != sha256_file(tmp):
        tmp.unlink(missing_ok=True)
        raise IOError(f"SHA256 mismatch while copying {source} to {destination}")
    with tmp.open("rb+") as handle:
        os.fsync(handle.fileno())
    os.replace(tmp, destination)
    return destination


def _clean_arcname(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError(f"Unsafe archive path: {value!r}")
    return path.as_posix()


@contextmanager
def _compressed_writer(path: Path, level: int = 6) -> Iterator[BinaryIO]:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import zstandard as zstd
    except ImportError:
        with path.open("wb") as output:
            proc = subprocess.Popen(
                ["zstd", "-q", f"-{level}", "-T0", "-c"],
                stdin=subprocess.PIPE,
                stdout=output,
            )
            if proc.stdin is None:
                raise RuntimeError("Could not open zstd stdin")
            try:
                yield proc.stdin
            finally:
                proc.stdin.close()
                if proc.wait() != 0:
                    raise RuntimeError("zstd compression failed")
    else:
        with path.open("wb") as output:
            compressor = zstd.ZstdCompressor(level=level, threads=-1)
            with compressor.stream_writer(output, closefd=False) as writer:
                yield writer


@contextmanager
def _compressed_reader(path: Path) -> Iterator[BinaryIO]:
    try:
        import zstandard as zstd
    except ImportError:
        proc = subprocess.Popen(
            ["zstd", "-q", "-d", "-c", str(path)],
            stdout=subprocess.PIPE,
        )
        if proc.stdout is None:
            raise RuntimeError("Could not open zstd stdout")
        try:
            yield proc.stdout
        finally:
            proc.stdout.close()
            if proc.wait() != 0:
                raise RuntimeError(f"zstd decompression failed for {path}")
    else:
        with path.open("rb") as source:
            decompressor = zstd.ZstdDecompressor()
            with decompressor.stream_reader(source, closefd=False) as reader:
                yield reader


def create_tar_zst(
    output_path: str | Path,
    entries: Iterable[tuple[str | Path, str]],
    *,
    level: int = 6,
) -> Path:
    """Create a .tar.zst containing regular files only."""
    output = Path(output_path)
    normalized = [(Path(source), _clean_arcname(arcname)) for source, arcname in entries]
    if not normalized:
        raise ValueError("Refusing to create an empty archive")
    for source, _ in normalized:
        if not source.is_file():
            raise FileNotFoundError(source)

    tmp = output.with_suffix(output.suffix + ".tmp")
    tmp.unlink(missing_ok=True)
    try:
        with _compressed_writer(tmp, level=level) as compressed:
            with tarfile.open(fileobj=compressed, mode="w|") as archive:
                for source, arcname in normalized:
                    info = archive.gettarinfo(str(source), arcname=arcname)
                    if not info.isfile():
                        raise ValueError(f"Only regular files may enter a bundle: {source}")
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    with source.open("rb") as handle:
                        archive.addfile(info, handle)
        os.replace(tmp, output)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    return output


def safe_extract_tar_zst(archive_path: str | Path, destination: str | Path) -> list[Path]:
    """Extract regular files/directories while rejecting traversal and links."""
    archive_path = Path(archive_path)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    extracted: list[Path] = []

    with _compressed_reader(archive_path) as decompressed:
        with tarfile.open(fileobj=decompressed, mode="r|") as archive:
            for member in archive:
                name = _clean_arcname(member.name)
                target = (destination / name).resolve()
                if root != target and root not in target.parents:
                    raise ValueError(f"Archive path escapes destination: {member.name}")
                if member.issym() or member.islnk() or member.isdev():
                    raise ValueError(f"Links and device nodes are forbidden: {member.name}")
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                if not member.isfile():
                    raise ValueError(f"Unsupported archive member: {member.name}")
                source = archive.extractfile(member)
                if source is None:
                    raise IOError(f"Could not read archive member: {member.name}")
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("wb") as output:
                    shutil.copyfileobj(source, output, length=CHUNK_SIZE)
                os.chmod(target, member.mode & 0o777)
                extracted.append(target)
    return extracted


def write_sha256sums(path: str | Path, files: Iterable[str | Path]) -> None:
    target = Path(path)
    lines = [f"{sha256_file(file)}  {Path(file).name}" for file in files]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_sha256sums(path: str | Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(None, 1)
        result[name.strip()] = digest
    return result
