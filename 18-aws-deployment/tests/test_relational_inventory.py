import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src import relational_inventory


class RelationalInventoryTests(unittest.TestCase):
    def test_json_to_rows_preserves_fields(self):
        data = {
            "inventory": [
                {"sku": "SKU-1", "description": "Item", "bin": "A1", "quantity": 7, "unit": "each"}
            ]
        }
        rows = list(relational_inventory.inventory_to_rows(data))
        self.assertEqual(rows[0]["sku"], "SKU-1")
        self.assertEqual(rows[0]["bin"], "A1")
        self.assertEqual(rows[0]["quantity"], 7)

    def test_sqlite_query_reads_seeded_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "tinywms.sqlite"
            conn = sqlite3.connect(db_path)
            conn.executescript(
                """
                CREATE TABLE products (sku TEXT PRIMARY KEY, description TEXT NOT NULL, unit TEXT NOT NULL);
                CREATE TABLE inventory_locations (sku TEXT NOT NULL, bin TEXT NOT NULL, quantity INTEGER NOT NULL, PRIMARY KEY (sku, bin));
                INSERT INTO products VALUES ('SKU-1', 'Item', 'each');
                INSERT INTO inventory_locations VALUES ('SKU-1', 'A1', 7);
                """
            )
            conn.commit()
            conn.close()
            rows = relational_inventory.rows_from_sqlite(db_path)
            self.assertEqual(rows[0]["sku"], "SKU-1")
            self.assertEqual(rows[0]["quantity"], 7)


if __name__ == "__main__":
    unittest.main()
