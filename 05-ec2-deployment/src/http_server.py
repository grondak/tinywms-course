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

    def index_html(self):
        return Path("src/web/index.html").read_bytes()

    def asset(self, name):
        return Path(f"src/web/{name}").read_bytes()


class Handler(BaseHTTPRequestHandler):
    app = None

    def do_GET(self):
        if self.path == "/inventory":
            body = self.app.inventory_json()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path in ("/", "/index.html"):
            body = self.app.index_html()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/app.js":
            body = self.app.asset("app.js")
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/style.css":
            body = self.app.asset("style.css")
            self.send_response(200)
            self.send_header("Content-Type", "text/css")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"error":"not found"}')

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
