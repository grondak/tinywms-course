#!/usr/bin/env python3
import json
import sys
from pathlib import Path

REQUIRED_FIELDS = ("sku", "description", "bin", "quantity", "unit")


def load_inventory(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "inventory" not in data or not isinstance(data["inventory"], list):
        raise ValueError("missing inventory array")
    for index, item in enumerate(data["inventory"]):
        if not isinstance(item, dict):
            raise ValueError(f"inventory[{index}] must be an object")
        for field in REQUIRED_FIELDS:
            if field not in item:
                raise ValueError(f"inventory[{index}] missing {field}")
    return data


def cmd_list(path):
    data = load_inventory(path)
    for item in data["inventory"]:
        print(f"{item['sku']}\t{item['description']}\t{item['bin']}\t{item['quantity']} {item['unit']}")


def cmd_find(path, sku):
    data = load_inventory(path)
    for item in data["inventory"]:
        if item["sku"] == sku:
            print(json.dumps(item, indent=2, sort_keys=True))
            return 0
    print(f"SKU not found: {sku}", file=sys.stderr)
    return 1


def cmd_emit(path):
    data = load_inventory(path)
    print(json.dumps(data, indent=2, sort_keys=True))


def main(argv):
    if len(argv) < 3:
        print("usage: inventory_cli.py <list|find|emit> <inventory.json> [sku]", file=sys.stderr)
        return 2
    command = argv[1]
    path = argv[2]
    if command == "list":
        cmd_list(path)
        return 0
    if command == "find":
        if len(argv) < 4:
            print("usage: inventory_cli.py find <inventory.json> <sku>", file=sys.stderr)
            return 2
        return cmd_find(path, argv[3])
    if command == "emit":
        cmd_emit(path)
        return 0
    print(f"unknown command: {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
