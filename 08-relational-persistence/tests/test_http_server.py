import json
import unittest
from http.client import HTTPConnection
from threading import Thread

from src import http_server


class HttpServerTests(unittest.TestCase):
    def test_inventory_handler(self):
        http_server.Handler.app = http_server.App("data/inventory.json")
        server = http_server.HTTPServer(("127.0.0.1", 0), http_server.Handler)
        port = server.server_port
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        conn = HTTPConnection("127.0.0.1", port)
        conn.request("GET", "/inventory")
        resp = conn.getresponse()
        body = resp.read().decode("utf-8")
        server.shutdown()
        self.assertEqual(resp.status, 200)
        self.assertEqual(json.loads(body)["inventory"][0]["sku"], "SKU-1001")


if __name__ == "__main__":
    unittest.main()
