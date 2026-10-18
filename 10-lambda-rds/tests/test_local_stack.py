"""The system on one machine: HTTP -> handler -> SQLite."""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class LocalSystemTests(unittest.TestCase):
    """Starts the real server in local mode and drives it over HTTP."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name) / 'local-aws'
        cls.env = {**os.environ, 'TINYWMS_LOCAL': '1', 'TINYWMS_LOCAL_DIR': str(cls.base), 'TINYWMS_PORT': '0'}
        for key in ('TINYWMS_DB', 'TINYWMS_SQLITE_PATH', 'PICK_WORK_QUEUE_URL', 'EVENT_BUS_NAME'):
            cls.env.pop(key, None)
        cls.proc = subprocess.Popen([sys.executable, str(ROOT / 'src' / 'http_server.py')], env=cls.env, cwd=ROOT,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        ready = cls.proc.stdout.readline().strip()
        cls.port = int(ready.rsplit(' ', 1)[-1])

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait(timeout=5)
        cls.proc.stdout.close()
        cls.proc.stderr.close()
        cls.tmp.cleanup()

    def request(self, path, body=None):
        data = None if body is None else (body if isinstance(body, bytes) else json.dumps(body).encode())
        req = urllib.request.Request(f'http://127.0.0.1:{self.port}{path}', data=data)
        try:
            with urllib.request.urlopen(req) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read())

    def stock(self):
        return {i['sku']: i['quantity'] for i in self.request('/inventory')[1]}

    def run_module(self, *args):
        return subprocess.run([sys.executable, *args], env=self.env, cwd=ROOT, capture_output=True, text=True, timeout=30)

    def test_inventory_comes_from_sqlite(self):
        self.assertEqual(set(self.stock()), {'SKU-1001', 'SKU-1002', 'SKU-2001'})
        self.assertEqual(self.request('/nothing')[0], 404)
        self.assertTrue(Path(self.env['TINYWMS_LOCAL_DIR'], 'tinywms.db').exists())



if __name__ == '__main__':
    unittest.main()
