#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / 'src' / 'web'
DEFAULT_INVENTORY = ROOT / 'data' / 'inventory.json'
PORT = int(os.environ.get('TINYWMS_PORT', '8000'))
INVENTORY_FILE = Path(os.environ.get('TINYWMS_INVENTORY_FILE', str(DEFAULT_INVENTORY)))
# TINYWMS_LOCAL=1: serve /inventory through the same handler code that Lambda runs,
# reading from SQLite instead of RDS (see src/local_aws.py).
LOCAL = bool(os.environ.get('TINYWMS_LOCAL'))


def _content_type(path: str) -> str:
    if path.endswith('.html'):
        return 'text/html; charset=utf-8'
    if path.endswith('.js'):
        return 'application/javascript; charset=utf-8'
    if path.endswith('.css'):
        return 'text/css; charset=utf-8'
    return 'application/octet-stream'


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload) -> None:
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        body = path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', _content_type(path.name))
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_handler_response(self, method: str) -> None:
        from src.lambda_inventory import handler
        try:
            response = handler({'httpMethod': method}, None)
        except Exception as exc:                      # a Lambda that raises becomes a 5xx; do the same
            return self._send_json(500, {'error': f'{type(exc).__name__}: {exc}'})
        payload = response['body'].encode('utf-8')
        self.send_response(response['statusCode'])
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/':
            return self._send_file(WEB_DIR / 'index.html')
        if parsed.path == '/index.html':
            return self._send_file(WEB_DIR / 'index.html')
        if parsed.path == '/app.js':
            return self._send_file(WEB_DIR / 'app.js')
        if parsed.path == '/style.css':
            return self._send_file(WEB_DIR / 'style.css')
        if parsed.path == '/inventory':
            if LOCAL:
                return self._send_handler_response('GET')
            return self._send_json(200, json.loads(INVENTORY_FILE.read_text(encoding='utf-8')))
        self._send_json(404, {'error': 'not found'})

    def log_message(self, format, *args):
        print(self.address_string(), format % args)


def main() -> int:
    if LOCAL:
        sys.path.insert(0, str(ROOT))                 # so "src.lambda_inventory" and "data.init_db" import
        from src.local_aws import configure
        state_dir = configure()
    server = ThreadingHTTPServer(('0.0.0.0', PORT), Handler)
    print(f'listening on {server.server_address[1]}', flush=True)
    if LOCAL:
        print(f'local mode: database {os.environ["TINYWMS_SQLITE_PATH"]}, state under {state_dir}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
