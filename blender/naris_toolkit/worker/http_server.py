"""NARIS Worker v1 local HTTP bridge for Blender.

Run inside Blender's Python environment. The endpoint accepts only the
naris-worker/v1 envelope and named operations; it never executes source code.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .naris_worker_v1 import dispatch

HOST = "127.0.0.1"
PORT = 8765


class NarisWorkerHandler(BaseHTTPRequestHandler):
    server_version = "NARISWorker/1.0"

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/jobs":
            self._send(404, {"error": "NARIS_NOT_FOUND"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 1_000_000:
                self._send(400, {"error": "NARIS_INVALID_BODY_SIZE"})
                return
            request = json.loads(self.rfile.read(length).decode("utf-8"))
            event = dispatch(request)
            self._send(200, event)
        except Exception as exc:
            self._send(400, {"protocol": "naris-worker/v1", "status": "FAILED", "progress": 0, "errors": [str(exc)]})

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send(200, {"ok": True, "protocol": "naris-worker/v1"})
            return
        self._send(404, {"error": "NARIS_NOT_FOUND"})

    def log_message(self, format: str, *args: Any) -> None:
        print("[NARIS Worker] " + format % args)


def serve(host: str = HOST, port: int = PORT) -> None:
    ThreadingHTTPServer((host, port), NarisWorkerHandler).serve_forever()


if __name__ == "__main__":
    serve()
