import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import src.lambda_inventory as lambda_inventory


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows
        self.executed = []
        self.closed = False

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def fetchall(self):
        return self.rows

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, rows):
        self.rows = rows
        self.cursor_obj = FakeCursor(rows)
        self.closed = False

    def cursor(self):
        return self.cursor_obj

    def close(self):
        self.closed = True


class LambdaInventoryTests(unittest.TestCase):
    def test_inventory_handler_returns_rows_from_database_connection(self):
        connection = FakeConnection([
            ('SKU-DB-1', 'Database widget', 'R1-01', 7, 'each'),
            ('SKU-DB-2', 'Database tape', 'R2-02', 4, 'roll'),
        ])

        response = lambda_inventory.handler(
            {'httpMethod': 'GET'},
            None,
            connection_factory=lambda: connection,
        )

        self.assertEqual(response['statusCode'], 200)
        payload = json.loads(response['body'])
        self.assertEqual(payload[0]['sku'], 'SKU-DB-1')
        self.assertEqual(payload[0]['description'], 'Database widget')
        self.assertEqual(payload[0]['bin_location'], 'R1-01')
        self.assertEqual(payload[1]['quantity'], 4)
        self.assertEqual(connection.cursor_obj.executed[0][0], lambda_inventory.INVENTORY_QUERY_SQL)
        self.assertTrue(connection.cursor_obj.closed)
        self.assertTrue(connection.closed)

    def test_handler_uses_local_json_demo_path_without_database_connection(self):
        with mock.patch.object(lambda_inventory, '_load_inventory', return_value=[{'sku': 'LOCAL', 'description': 'Local demo', 'bin_location': 'A1', 'quantity': 1, 'unit': 'each'}]) as load_inventory:
            response = lambda_inventory.handler({'httpMethod': 'GET', 'queryStringParameters': {'demo': 'local-json'}}, None)
        self.assertEqual(response['statusCode'], 200)
        payload = json.loads(response['body'])
        self.assertEqual(payload[0]['sku'], 'LOCAL')
        load_inventory.assert_called_once()

    def test_postgres_database_backend_is_default(self):
        self.assertEqual(lambda_inventory.os.environ.get(lambda_inventory.TINYWMS_DB_ENV, 'postgres'), 'postgres')

    def test_handler_raises_visible_error_when_database_url_is_missing_for_postgres(self):
        with mock.patch.dict(lambda_inventory.os.environ, {lambda_inventory.TINYWMS_DB_ENV: 'postgres'}, clear=True):
            with self.assertRaises(RuntimeError) as ctx:
                with lambda_inventory.open_connection():
                    pass
        self.assertIn('DATABASE_URL is required', str(ctx.exception))

    def test_map_inventory_row_accepts_mapping_rows_with_bin_location(self):
        mapped = lambda_inventory._map_inventory_row({'sku': 'SKU-1', 'description': 'Widget', 'bin_location': 'A1', 'quantity': 3, 'unit': 'each'})
        self.assertEqual(mapped['bin_location'], 'A1')
        self.assertEqual(mapped['sku'], 'SKU-1')

    def test_map_inventory_row_accepts_mapping_rows_with_bin_alias(self):
        mapped = lambda_inventory._map_inventory_row({'sku': 'SKU-1', 'description': 'Widget', 'bin': 'A1', 'quantity': 3, 'unit': 'each'})
        self.assertEqual(mapped['bin_location'], 'A1')

    def test_read_inventory_rows_executes_inventory_query(self):
        connection = FakeConnection([('SKU-1', 'Widget', 'A1', 3, 'each')])
        rows = lambda_inventory._read_inventory_rows(connection)
        self.assertEqual(rows[0]['sku'], 'SKU-1')
        self.assertEqual(connection.cursor_obj.executed[0][0], lambda_inventory.INVENTORY_QUERY_SQL)


if __name__ == '__main__':
    unittest.main()
