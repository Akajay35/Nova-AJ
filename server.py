import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class NovaWebHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/" or self.path == "/health":
            self._send_json({
                "name": "Nova-AJ",
                "status": "online",
                "service": "web",
                "message": "Nova-AJ web service is running."
            })
            return

        if self.path == "/api/status":
            self._send_json({
                "name": "Nova-AJ",
                "status": "online",
                "python": os.sys.version.split()[0]
            })
            return

        self._send_json({"error": "Not found"}, 404)

    def log_message(self, format, *args):
        print("Nova-AJ:", format % args)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), NovaWebHandler)
    print(f"Nova-AJ web service listening on port {port}")
    server.serve_forever()
