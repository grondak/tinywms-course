import json
import tempfile
import threading
import unittest
from contextlib import contextmanager
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

import src.http_server as http_server


@contextmanager
def server_in_thread(inventory_path: Path):
    old_inventory = http_server.INVENTORY_FILE
    old_port = http_server.PORT
    http_server.INVENTORY_FILE = inventory_path
    http_server.PORT = 0
    server = http_server.ThreadingHTTPServer(('127.0.0.1', 0), http_server.Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        http_server.INVENTORY_FILE = old_inventory
        http_server.PORT = old_port


class HttpServerTests(unittest.TestCase):
    def test_get_inventory_returns_json_with_status_and_headers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            inventory_path = Path(tmpdir) / 'inventory.json'
            inventory_path.write_text(json.dumps([
                {'sku': 'SKU-1001', 'description': 'Blue widget', 'bin_location': 'A1-01', 'quantity': 3, 'unit': 'each'}
            ]), encoding='utf-8')
            with server_in_thread(inventory_path) as port:
                with urlopen(f'http://127.0.0.1:{port}/inventory') as response:
                    body = json.loads(response.read().decode('utf-8'))
                    self.assertEqual(response.status, 200)
                    self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(body[0]['sku'], 'SKU-1001')
        self.assertEqual(body[0]['bin_location'], 'A1-01')

    def test_missing_path_returns_not_found_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            inventory_path = Path(tmpdir) / 'inventory.json'
            inventory_path.write_text('[]', encoding='utf-8')
            with server_in_thread(inventory_path) as port:
                with self.assertRaises(HTTPError) as ctx:
                    urlopen(f'http://127.0.0.1:{port}/nope')
                self.assertEqual(ctx.exception.code, 404)
                body = json.loads(ctx.exception.read().decode('utf-8'))
                self.assertEqual(body['error'], 'not found')


if __name__ == '__main__':
    unittest.main()
