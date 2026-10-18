import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.inventory_watcher import snapshot


class InventoryWatcherTests(unittest.TestCase):
    def test_snapshot_reports_count_and_skus(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            inventory_path = Path(tmpdir) / 'inventory.json'
            inventory_path.write_text(json.dumps([
                {'sku': 'SKU-1', 'description': 'A', 'bin_location': 'A1', 'quantity': 1, 'unit': 'each'},
                {'sku': 'SKU-2', 'description': 'B', 'bin_location': 'B1', 'quantity': 2, 'unit': 'each'},
            ]), encoding='utf-8')
            summary = json.loads(snapshot(inventory_path))
        self.assertEqual(summary['count'], 2)
        self.assertEqual(summary['skus'], ['SKU-1', 'SKU-2'])

    def test_snapshot_uses_inventory_file_contents(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            inventory_path = Path(tmpdir) / 'inventory.json'
            inventory_path.write_text(json.dumps([
                {'sku': 'SKU-9', 'description': 'X', 'bin_location': 'Z9', 'quantity': 9, 'unit': 'each'}
            ]), encoding='utf-8')
            summary = json.loads(snapshot(inventory_path))
        self.assertEqual(summary['skus'], ['SKU-9'])


if __name__ == '__main__':
    unittest.main()
