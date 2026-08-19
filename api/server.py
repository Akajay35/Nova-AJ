from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from core.assistant import NovaAssistant


class NovaApiHandler(BaseHTTPRequestHandler):
    assistant = NovaAssistant()
    api_token = os.environ.get("NOVA_API_TOKEN", "")

    def _send(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self) -> bool:
        if not self.api_token:
            return False
        return self.headers.get("Authorization", "") == f"Bearer {self.api_token}"

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send(200, {"ok": True, "service": "nova-aj"})
            return
        self._send(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/v1/chat":
            self._send(404, {"error": "not_found"})
            return
        if not self._authorized():
            self._send(401, {"error": "unauthorized"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            query = data.get("message")
            if not isinstance(query, str) or not query.strip():
                self._send(400, {"error": "message_required"})
                return
            self._send(200, {"reply": self.assistant.handle(query.strip())})
        except Exception:
            self._send(500, {"error": "assistant_error"})

    def log_message(self, *_args: object) -> None:
        return


def run() -> None:
    port = int(os.environ.get("NOVA_API_PORT", "8080"))
    ThreadingHTTPServer(("0.0.0.0", port), NovaApiHandler).serve_forever()


if __name__ == "__main__":
    run()
