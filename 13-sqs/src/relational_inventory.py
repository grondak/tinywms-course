#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path

try:
    import sqlite3
except ImportError:  # pragma: no cover
    sqlite3 = None


def inventory_to_rows(inventory_doc):
    for item in inventory_doc["inventory"]:
        yield {
            "sku": item["sku"],
            "description": item["description"],
            "unit": item["unit"],
            "bin": item["bin"],
            "quantity": item["quantity"],
        }


def load_inventory_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def rows_from_sqlite(db_path):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT p.sku, p.description, p.unit, i.bin, i.quantity
        FROM products p
        JOIN inventory_locations i ON i.sku = p.sku
        ORDER BY p.sku, i.bin
        """
    )
    rows = [
        {
            "sku": sku,
            "description": description,
            "unit": unit,
            "bin": bin_name,
            "quantity": quantity,
        }
        for sku, description, unit, bin_name, quantity in cursor.fetchall()
    ]
    connection.close()
    return rows


def main(argv):
    parser = argparse.ArgumentParser(description="TinyWMS relational inventory helper")
    parser.add_argument("--json", help="print rows derived from a JSON inventory file")
    parser.add_argument("--sqlite", help="print rows from a SQLite database file")
    args = parser.parse_args(argv[1:])

    if args.json:
        print(json.dumps({"inventory": list(inventory_to_rows(load_inventory_json(args.json)))}, indent=2, sort_keys=True))
        return 0
    if args.sqlite:
        if sqlite3 is None:
            print("sqlite3 module is not available", file=sys.stderr)
            return 1
        print(json.dumps({"inventory": rows_from_sqlite(args.sqlite)}, indent=2, sort_keys=True))
        return 0

    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
