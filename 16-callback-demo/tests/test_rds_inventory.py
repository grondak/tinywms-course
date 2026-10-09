import sqlite3
import threading
import tempfile
import unittest
from pathlib import Path

from src import rds_inventory


class RdsInventoryTests(unittest.TestCase):
    def test_rows_to_inventory_preserves_contract(self):
        doc = rds_inventory.rows_to_inventory([
            {"sku": "SKU-1", "description": "Item", "bin": "A1", "quantity": 7, "unit": "each"}
        ])
        self.assertEqual(doc["inventory"][0]["sku"], "SKU-1")
        self.assertEqual(doc["inventory"][0]["bin"], "A1")
        self.assertEqual(doc["inventory"][0]["quantity"], 7)
        self.assertEqual(doc["inventory"][0]["unit"], "each")

    def sqlite_connection(self):
        connection = sqlite3.connect(":memory:")
        connection.executescript(
            """
            CREATE TABLE products (
                sku TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                unit TEXT NOT NULL
            );
            CREATE TABLE inventory_locations (
                sku TEXT NOT NULL,
                bin TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                PRIMARY KEY (sku, bin)
            );
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE order_lines (
                order_id INTEGER NOT NULL,
                line_number INTEGER NOT NULL,
                sku TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                PRIMARY KEY (order_id, line_number)
            );
            INSERT INTO products VALUES ('SKU-1001', 'Blue widget', 'each');
            INSERT INTO products VALUES ('SKU-1002', 'Red widget', 'each');
            INSERT INTO inventory_locations VALUES ('SKU-1001', 'A1-01', 24);
            INSERT INTO inventory_locations VALUES ('SKU-1002', 'A1-02', 8);
            """
        )
        return connection

    def test_create_order_with_connection_commits_rows_and_decrements_inventory(self):
        connection = self.sqlite_connection()
        result = rds_inventory.create_order_with_connection(connection, {
            "customer": "Student Store",
            "lines": [{"sku": "SKU-1001", "quantity": 2}]
        })
        self.assertEqual(result["status"], "created")
        self.assertEqual(result["lines"][0]["quantity"], 2)

        remaining = connection.execute(
            "SELECT quantity FROM inventory_locations WHERE sku = ?",
            ("SKU-1001",)
        ).fetchone()[0]
        self.assertEqual(remaining, 22)

        line_count = connection.execute("SELECT COUNT(*) FROM order_lines").fetchone()[0]
        self.assertEqual(line_count, 1)
        connection.close()

    def test_create_order_with_connection_rolls_back_on_insufficient_inventory(self):
        connection = self.sqlite_connection()
        with self.assertRaises(rds_inventory.InsufficientInventoryError):
            rds_inventory.create_order_with_connection(connection, {
                "customer": "Student Store",
                "lines": [{"sku": "SKU-1002", "quantity": 99}]
            })

        inventory = connection.execute(
            "SELECT quantity FROM inventory_locations WHERE sku = ?",
            ("SKU-1002",)
        ).fetchone()[0]
        self.assertEqual(inventory, 8)

        order_count = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        line_count = connection.execute("SELECT COUNT(*) FROM order_lines").fetchone()[0]
        self.assertEqual(order_count, 0)
        self.assertEqual(line_count, 0)
        connection.close()

    def test_concurrent_orders_do_not_oversell(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "tinywms.sqlite"
            setup = sqlite3.connect(db_path)
            setup.executescript(
                """
                CREATE TABLE products (
                    sku TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    unit TEXT NOT NULL
                );
                CREATE TABLE inventory_locations (
                    sku TEXT NOT NULL,
                    bin TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    PRIMARY KEY (sku, bin)
                );
                CREATE TABLE orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE order_lines (
                    order_id INTEGER NOT NULL,
                    line_number INTEGER NOT NULL,
                    sku TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    PRIMARY KEY (order_id, line_number)
                );
                INSERT INTO products VALUES ('SKU-1001', 'Blue widget', 'each');
                INSERT INTO inventory_locations VALUES ('SKU-1001', 'A1-01', 1);
                """
            )
            setup.commit()
            setup.close()

            results = []

            def worker(name):
                connection = sqlite3.connect(db_path, timeout=5, isolation_level=None)
                try:
                    result = rds_inventory.create_order_with_connection(connection, {
                        "customer": name,
                        "lines": [{"sku": "SKU-1001", "quantity": 1}]
                    })
                    results.append(result["status"])
                except rds_inventory.InsufficientInventoryError:
                    results.append("failed")
                finally:
                    connection.close()

            threads = [
                threading.Thread(target=worker, args=("first",)),
                threading.Thread(target=worker, args=("second",)),
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            check = sqlite3.connect(db_path)
            remaining = check.execute(
                "SELECT quantity FROM inventory_locations WHERE sku = ?",
                ("SKU-1001",)
            ).fetchone()[0]
            order_count = check.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
            check.close()

        self.assertEqual(sorted(results), ["created", "failed"])
        self.assertEqual(remaining, 0)
        self.assertEqual(order_count, 1)


if __name__ == "__main__":
    unittest.main()
