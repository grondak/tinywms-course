import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import data.init_db as init_db
from src.db_adapter import SQLiteConnectionAdapter, SQLiteCursorAdapter, open_connection


ROOT = Path(__file__).resolve().parents[1]


class RelationalPersistenceTests(unittest.TestCase):
    def test_schema_adds_order_tables_without_renaming_inventory_bin(self):
        schema = (ROOT / 'data' / 'schema.sql').read_text(encoding='utf-8')
        self.assertIn('CREATE TABLE inventory', schema)
        self.assertIn('bin_location TEXT NOT NULL', schema)
        self.assertIn('quantity INTEGER NOT NULL CHECK (quantity >= 0)', schema)
        self.assertNotIn('bin ', schema)

    def test_seed_matches_inventory_schema(self):
        inventory = json.loads((ROOT / 'data' / 'inventory.json').read_text(encoding='utf-8'))
        seed = (ROOT / 'data' / 'seed.sql').read_text(encoding='utf-8')
        self.assertIn("INSERT INTO inventory (sku, description, bin_location, quantity, unit) VALUES", seed)
        for item in inventory:
            row = f"('{item['sku']}', '{item['description']}', '{item['bin_location']}', {item['quantity']}, '{item['unit']}')"
            self.assertIn(row, seed)

    def test_sqlite_initializer_loads_inventory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'tinywms.db'
            with mock.patch.dict(os.environ, {'TINYWMS_DB': 'sqlite', 'TINYWMS_SQLITE_PATH': str(db_path)}, clear=False):
                exit_code = init_db.main(['data.init_db'])
            self.assertEqual(exit_code, 0)
            connection = sqlite3.connect(db_path)
            try:
                rows = connection.execute('SELECT sku, description, bin_location, quantity, unit FROM inventory ORDER BY sku').fetchall()
            finally:
                connection.close()
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0], ('SKU-1001', 'Blue widget', 'A1-01', 24, 'each'))
        self.assertEqual(rows[2][2], 'B2-04')

    def test_sqlite_adapter_rewrites_placeholders_and_row_lock_clause(self):
        connection = sqlite3.connect(':memory:')
        try:
            adapter = SQLiteConnectionAdapter(connection)
            cursor = adapter.cursor()
            try:
                self.assertIsInstance(cursor, SQLiteCursorAdapter)
                cursor.execute('SELECT %s FOR UPDATE', ('sku',))
                self.assertEqual(cursor._cursor.lastrowid, 0)
            finally:
                cursor.close()
        finally:
            connection.close()

    def test_open_connection_sqlite_enables_foreign_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'tinywms.db'
            with mock.patch.dict(os.environ, {'TINYWMS_DB': 'sqlite', 'TINYWMS_SQLITE_PATH': str(db_path)}, clear=False):
                with open_connection() as connection:
                    cursor = connection.cursor()
                    try:
                        cursor.execute('PRAGMA foreign_keys')
                        value = cursor.fetchone()[0]
                    finally:
                        cursor.close()
        self.assertEqual(value, 1)


if __name__ == '__main__':
    unittest.main()
