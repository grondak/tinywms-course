import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

from src.inventory_cli import load_inventory, main


class InventoryCliTests(unittest.TestCase):
    def test_load_inventory_returns_items(self):
        items = load_inventory(Path('data/inventory.json'))
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]['sku'], 'SKU-1001')
        self.assertEqual(items[0]['bin_location'], 'A1-01')

    def test_list_prints_visible_inventory_rows(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(['data/inventory.json', 'list'])
        self.assertEqual(exit_code, 0)
        output = stdout.getvalue().strip().splitlines()
        self.assertIn('SKU-1001\tBlue widget\tA1-01\t24 each', output)
        self.assertIn('SKU-2001\tPacking tape roll\tB2-04\t8 roll', output)

    def test_find_emits_json_for_matching_sku(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(['data/inventory.json', 'find', 'SKU-1002'])
        self.assertEqual(exit_code, 0)
        item = json.loads(stdout.getvalue())
        self.assertEqual(item['sku'], 'SKU-1002')
        self.assertEqual(item['description'], 'Red widget')

    def test_find_missing_sku_reports_error_and_exit_code(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main(['data/inventory.json', 'find', 'SKU-DOES-NOT-EXIST'])
        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), '')
        self.assertIn('error: SKU not found: SKU-DOES-NOT-EXIST', stderr.getvalue())

    def test_dump_emits_valid_json_array(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(['data/inventory.json', 'dump'])
        self.assertEqual(exit_code, 0)
        dumped = json.loads(stdout.getvalue())
        self.assertIsInstance(dumped, list)
        self.assertEqual(dumped[1]['bin_location'], 'A1-02')

    def test_missing_required_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / 'inventory.json'
            temp_path.write_text(json.dumps([{'sku': 'SKU-1'}]), encoding='utf-8')
            with self.assertRaises(SystemExit) as ctx:
                load_inventory(temp_path)
        self.assertIn('missing required fields', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
