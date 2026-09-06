#!/usr/bin/env python3
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import urllib.error
import urllib.request


INFERENCE_URL = os.environ.get("GLYPH_INFERENCE_URL", "http://127.0.0.1:8195")
API_BODY_LIMIT = int(os.environ.get("GLYPH_SITE_API_BODY_LIMIT", "4096"))


class GlyphStaticHandler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript",
        ".json": "application/json",
        ".webmanifest": "application/manifest+json",
    }

    def list_directory(self, path):
        self.send_error(404, "Directory listing disabled")
        return None

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Permissions-Policy", "geolocation=(), microphone=(), camera=()")

        request_path = self.path.split("?", 1)[0]
        if request_path.startswith("/api/"):
            self.send_header("Cache-Control", "no-store")
        elif request_path.startswith("/assets/"):
            self.send_header("Cache-Control", "public, max-age=3600")
        else:
            self.send_header("Cache-Control", "public, max-age=60")

        super().end_headers()

    def client_ip(self):
        cf_ip = self.headers.get("CF-Connecting-IP", "").strip()
        if cf_ip:
            return cf_ip[:120]
        forwarded = self.headers.get("X-Forwarded-For", "").split(",", 1)[0].strip()
        if forwarded and self.client_address and self.client_address[0] in {"127.0.0.1", "::1"}:
            return forwarded[:120]
        return self.client_address[0] if self.client_address else "unknown"

    def json_error(self, code, error, message):
        body = (f'{{"error":"{error}","message":"{message}"}}\n').encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        if self.path.split("?", 1)[0] != "/api/generate":
            self.send_error(404)
            return
        self.send_response(204)
        self.send_header("Allow", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/generate":
            self.send_error(404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
        except ValueError:
            length = 0
        if length <= 0 or length > API_BODY_LIMIT:
            self.json_error(400, "invalid_prompt", "Request body is too large or empty.")
            return

        body = self.rfile.read(length)
        request = urllib.request.Request(
            INFERENCE_URL.rstrip("/") + "/api/generate",
            data=body,
            headers={
                "Content-Type": self.headers.get("Content-Type", "application/json"),
                "Accept": "application/json",
                "X-Glyph-Client-IP": self.client_ip(),
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=70) as response:
                response_body = response.read()
                status = response.status
                content_type = response.headers.get("Content-Type", "application/json; charset=utf-8")
                retry_after = response.headers.get("Retry-After")
        except urllib.error.HTTPError as exc:
            response_body = exc.read()
            status = exc.code
            content_type = exc.headers.get("Content-Type", "application/json; charset=utf-8")
            retry_after = exc.headers.get("Retry-After")
        except urllib.error.URLError:
            self.json_error(503, "disabled", "Glyph demo is temporarily unavailable.")
            return

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(response_body)))
        if retry_after:
            self.send_header("Retry-After", retry_after)
        self.end_headers()
        self.wfile.write(response_body)


def main():
    host = os.environ.get("GLYPH_SITE_HOST", "127.0.0.1")
    port = int(os.environ.get("GLYPH_SITE_PORT", "8194"))
    root = Path(__file__).resolve().parent
    handler = partial(GlyphStaticHandler, directory=str(root))

    server = ThreadingHTTPServer((host, port), handler)
    print(f"Serving Glyph public site on http://{host}:{port}/ from {root}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
