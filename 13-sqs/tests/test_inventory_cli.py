import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from src import inventory_cli


class InventoryCliTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tempdir.name) / "inventory.json"
        self.path.write_text(json.dumps({"inventory": [{"sku": "SKU-1", "description": "Item", "bin": "A1", "quantity": 1, "unit": "each"}]}), encoding="utf-8")

    def tearDown(self):
        self.tempdir.cleanup()

    def test_load_inventory(self):
        data = inventory_cli.load_inventory(self.path)
        self.assertEqual(data["inventory"][0]["sku"], "SKU-1")

    def test_find_prints_json(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = inventory_cli.cmd_find(self.path, "SKU-1")
        self.assertEqual(code, 0)
        self.assertIn('"sku": "SKU-1"', buffer.getvalue())

    def test_missing_sku_fails(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = inventory_cli.cmd_find(self.path, "NOPE")
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
