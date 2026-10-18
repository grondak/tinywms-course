"""The system on one machine: HTTP -> handler -> SQLite -> queue/event files."""
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

from src.local_aws import FileQueue  # noqa: E402


class FileQueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.url = str(Path(self.tmp.name) / 'q')
        self.queue = FileQueue()

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_queue_returns_no_messages(self):
        self.assertEqual(self.queue.receive_message(QueueUrl=self.url, WaitTimeSeconds=0), {})

    def test_messages_arrive_oldest_first_and_stay_until_deleted(self):
        for n in range(3):
            self.queue.send_message(QueueUrl=self.url, MessageBody=f'm{n}')
        first = self.queue.receive_message(QueueUrl=self.url, MaxNumberOfMessages=2)['Messages']
        self.assertEqual([m['Body'] for m in first], ['m0', 'm1'])
        again = self.queue.receive_message(QueueUrl=self.url)['Messages']
        self.assertEqual([m['Body'] for m in again], ['m0', 'm1', 'm2'])      # not deleted yet
        self.queue.delete_message(QueueUrl=self.url, ReceiptHandle=first[0]['ReceiptHandle'])
        left = self.queue.receive_message(QueueUrl=self.url)['Messages']
        self.assertEqual([m['Body'] for m in left], ['m1', 'm2'])

    def test_long_poll_waits_for_a_message(self):
        started = time.monotonic()
        self.assertEqual(self.queue.receive_message(QueueUrl=self.url, WaitTimeSeconds=1), {})
        self.assertGreaterEqual(time.monotonic() - started, 0.9)



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


    def test_order_journey(self):
        before = self.stock()
        status, body = self.request('/orders', {'order_id': 'ORD-L1', 'lines': [
            {'sku': 'SKU-1001', 'quantity': 2}, {'sku': 'SKU-2001', 'quantity': 1}]})
        self.assertEqual((status, body['status']), (201, 'accepted'))
        after = self.stock()
        self.assertEqual(after['SKU-1001'], before['SKU-1001'] - 2)
        self.assertEqual(after['SKU-2001'], before['SKU-2001'] - 1)

        # rejected orders change nothing and send nothing
        self.assertEqual(self.request('/orders', {'order_id': 'ORD-L2', 'lines': [
            {'sku': 'SKU-1002', 'quantity': 1}, {'sku': 'SKU-2001', 'quantity': 999}]})[0], 409)
        self.assertEqual(self.request('/orders', {'order_id': 'ORD-L3', 'lines': [{'sku': 'NOPE', 'quantity': 1}]})[0], 409)
        self.assertEqual(self.request('/orders', {'order_id': 'ORD-L1', 'lines': [{'sku': 'SKU-1002', 'quantity': 1}]})[0], 409)  # duplicate id
        self.assertEqual(self.request('/orders', b'not json')[0], 400)
        self.assertEqual(self.request('/orders', {'order_id': 'X', 'lines': []})[0], 400)
        self.assertEqual(self.stock(), after)


        # one pick-work command per line
        self.assertEqual(len(list((self.base / 'pick-work').glob('*.json'))), 2)



if __name__ == '__main__':
    unittest.main()
