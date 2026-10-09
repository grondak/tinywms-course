#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def load_inventory(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sql_quote(text):
    return "'" + text.replace("'", "''") + "'"


def emit_seed_sql(inventory_path):
    data = load_inventory(inventory_path)
    print("-- Generated TinyWMS seed data from JSON")
    print("INSERT INTO products (sku, description, unit) VALUES")
    product_rows = []
    location_rows = []
    for item in data["inventory"]:
        product_rows.append(
            f"  ({sql_quote(item['sku'])}, {sql_quote(item['description'])}, {sql_quote(item['unit'])})"
        )
        location_rows.append(
            f"  ({sql_quote(item['sku'])}, {sql_quote(item['bin'])}, {int(item['quantity'])})"
        )
    print(",\n".join(product_rows) + ";")
    print()
    print("INSERT INTO inventory_locations (sku, bin, quantity) VALUES")
    print(",\n".join(location_rows) + ";")


def main(argv):
    if len(argv) != 2:
        print("usage: load_from_json.py <inventory.json>", file=sys.stderr)
        return 2
    emit_seed_sql(argv[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
