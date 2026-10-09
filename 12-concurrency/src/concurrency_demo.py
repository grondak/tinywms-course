#!/usr/bin/env python3
import json
import sqlite3
import sys
import tempfile
import threading
import time
from pathlib import Path

from src.rds_inventory import InsufficientInventoryError, create_order_with_connection


def setup_demo_db(db_path, quantity=1):
    connection = sqlite3.connect(db_path)
    connection.executescript(
        f"""
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
        INSERT INTO products VALUES ('SKU-RACE', 'Last item demo', 'each');
        INSERT INTO inventory_locations VALUES ('SKU-RACE', 'R1-01', {int(quantity)});
        """
    )
    connection.commit()
    connection.close()


def remaining_quantity(db_path):
    connection = sqlite3.connect(db_path)
    quantity = connection.execute(
        "SELECT quantity FROM inventory_locations WHERE sku = ?",
        ("SKU-RACE",),
    ).fetchone()[0]
    connection.close()
    return quantity


def order_count(db_path):
    connection = sqlite3.connect(db_path)
    count = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    connection.close()
    return count


def naive_worker(db_path, worker_name, barrier, results):
    connection = sqlite3.connect(db_path, timeout=5, isolation_level=None)
    cursor = connection.cursor()
    cursor.execute("SELECT quantity FROM inventory_locations WHERE sku = ?", ("SKU-RACE",))
    available = int(cursor.fetchone()[0])
    barrier.wait()
    if available < 1:
        results.append({"worker": worker_name, "status": "failed", "available_seen": available})
        connection.close()
        return
    time.sleep(0.1)
    cursor.execute("UPDATE inventory_locations SET quantity = ? WHERE sku = ?", (available - 1, "SKU-RACE"))
    cursor.execute("INSERT INTO orders (customer) VALUES (?)", (worker_name,))
    connection.commit()
    results.append({"worker": worker_name, "status": "created", "available_seen": available})
    connection.close()


def run_naive_demo(db_path):
    results = []
    barrier = threading.Barrier(2)
    threads = [
        threading.Thread(target=naive_worker, args=(db_path, "worker-1", barrier, results)),
        threading.Thread(target=naive_worker, args=(db_path, "worker-2", barrier, results)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return {
        "mode": "naive",
        "results": sorted(results, key=lambda item: item["worker"]),
        "remainingQuantity": remaining_quantity(db_path),
        "orderCount": order_count(db_path),
    }


def fixed_worker(db_path, worker_name, results):
    connection = sqlite3.connect(db_path, timeout=5, isolation_level=None)
    try:
        result = create_order_with_connection(
            connection,
            {
                "customer": worker_name,
                "lines": [{"sku": "SKU-RACE", "quantity": 1}],
            },
        )
        results.append({"worker": worker_name, "status": result["status"]})
    except InsufficientInventoryError as exc:
        results.append(
            {
                "worker": worker_name,
                "status": "failed",
                "error": "insufficient inventory",
                "requested": exc.requested,
                "available": exc.available,
            }
        )
    finally:
        connection.close()


def run_fixed_demo(db_path):
    results = []
    threads = [
        threading.Thread(target=fixed_worker, args=(db_path, "worker-1", results)),
        threading.Thread(target=fixed_worker, args=(db_path, "worker-2", results)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return {
        "mode": "fixed",
        "results": sorted(results, key=lambda item: item["worker"]),
        "remainingQuantity": remaining_quantity(db_path),
        "orderCount": order_count(db_path),
    }


def main(argv):
    if len(argv) != 2 or argv[1] not in {"naive", "fixed"}:
        print("usage: concurrency_demo.py <naive|fixed>", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory() as tmp:
        db_path = str(Path(tmp) / "tinywms-concurrency.sqlite")
        setup_demo_db(db_path, quantity=1)
        if argv[1] == "naive":
            result = run_naive_demo(db_path)
        else:
            result = run_fixed_demo(db_path)
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
