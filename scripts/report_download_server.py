#!/usr/bin/env python3
"""Small read-only report server with ZIP download for selected files."""

from __future__ import annotations

import json
import os
import tempfile
import zipfile
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


REPORT_ROOT = Path(os.environ.get("GLYPH_REPORTS_ROOT", "/srv/reports")).resolve()
HOST = os.environ.get("GLYPH_REPORTS_HOST", "0.0.0.0")
PORT = int(os.environ.get("GLYPH_REPORTS_PORT", "8101"))
MAX_FILES = int(os.environ.get("GLYPH_REPORTS_MAX_FILES", "250"))
MAX_TOTAL_BYTES = int(os.environ.get("GLYPH_REPORTS_MAX_TOTAL_BYTES", str(256 * 1024 * 1024)))
MAX_BODY_BYTES = int(os.environ.get("GLYPH_REPORTS_MAX_BODY_BYTES", str(64 * 1024)))


class ReportHandler(SimpleHTTPRequestHandler):
    server_version = "GlyphReportServer/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(REPORT_ROOT), **kwargs)

    def do_POST(self) -> None:
        if self.path != "/api/download-zip":
            self.send_error(HTTPStatus.NOT_FOUND, "not found")
            return
        try:
            self._handle_zip_request()
        except ValueError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "bad_request", "message": str(exc)})
        except Exception:
            self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "internal_error", "message": "Could not build ZIP."})

    def _handle_zip_request(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            raise ValueError("Empty request body.")
        if length > MAX_BODY_BYTES:
            raise ValueError("Request body is too large.")

        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        names = payload.get("files")
        if not isinstance(names, list) or not names:
            raise ValueError("Select at least one file.")
        if len(names) > MAX_FILES:
            raise ValueError(f"Too many files selected. Limit: {MAX_FILES}.")

        files = self._resolve_files(names)
        total = sum(path.stat().st_size for path in files)
        if total > MAX_TOTAL_BYTES:
            raise ValueError(f"Selected files are too large. Limit: {MAX_TOTAL_BYTES // (1024 * 1024)} MB.")

        archive_name = self._safe_archive_name(payload.get("name"))
        with tempfile.SpooledTemporaryFile(max_size=32 * 1024 * 1024, mode="w+b") as tmp:
            with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
                for path in files:
                    archive.write(path, arcname=path.name)
            size = tmp.tell()
            tmp.seek(0)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Length", str(size))
            self.send_header("Content-Disposition", f'attachment; filename="{archive_name}"')
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            while True:
                chunk = tmp.read(1024 * 256)
                if not chunk:
                    break
                self.wfile.write(chunk)

    def _resolve_files(self, names: list[object]) -> list[Path]:
        files: list[Path] = []
        seen: set[str] = set()
        for raw_name in names:
            if not isinstance(raw_name, str):
                raise ValueError("Invalid file name.")
            name = raw_name.strip()
            if not name or name in seen:
                continue
            if "/" in name or "\\" in name or name.startswith("."):
                raise ValueError("Invalid file name.")
            path = (REPORT_ROOT / name).resolve()
            if path.parent != REPORT_ROOT or not path.is_file():
                raise ValueError(f"File not found: {name}")
            if path.name == "index.html":
                raise ValueError("index.html cannot be archived.")
            files.append(path)
            seen.add(name)
        if not files:
            raise ValueError("No valid files selected.")
        return files

    def _safe_archive_name(self, value: object) -> str:
        if not isinstance(value, str):
            return "glyph-reports.zip"
        name = value.strip().lower().replace(" ", "-")
        safe = "".join(char for char in name if char.isalnum() or char in ("-", "_", "."))
        if not safe:
            return "glyph-reports.zip"
        if not safe.endswith(".zip"):
            safe += ".zip"
        return safe

    def _send_json(self, status: HTTPStatus, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    if not REPORT_ROOT.exists():
        raise SystemExit(f"Report root does not exist: {REPORT_ROOT}")
    server = ThreadingHTTPServer((HOST, PORT), ReportHandler)
    print(f"serving {REPORT_ROOT} on {HOST}:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
