#!/usr/bin/env python3
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


def load_inventory(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


class App:
    def __init__(self, inventory_path):
        self.inventory_path = inventory_path

    def inventory_json(self):
        return json.dumps(load_inventory(self.inventory_path), indent=2, sort_keys=True).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    app = None

    def do_GET(self):
        if self.path != "/inventory":
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error":"not found"}')
            return
        body = self.app.inventory_json()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        sys.stderr.write(format % args + "\n")


def main(argv):
    inventory_path = argv[1] if len(argv) > 1 else "data/inventory.json"
    port = int(os.environ.get("TINYWMS_PORT", "8000"))
    Handler.app = App(inventory_path)
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"listening on http://0.0.0.0:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
