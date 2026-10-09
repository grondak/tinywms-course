#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def inventory_by_sku(inventory_doc):
    return {item["sku"]: item for item in inventory_doc.get("inventory", [])}


def build_pick_ticket_text(message, inventory_lookup):
    lines = [
        "=== TinyWMS Pick Ticket ===",
        f"Order ID: {message['orderId']}",
        f"Customer: {message['customer']}",
        f"Requested At: {message['createdAt']}",
        "",
    ]
    for line in message.get("lines", []):
        sku = line["sku"]
        product = inventory_lookup.get(sku, {})
        description = product.get("description", "UNKNOWN SKU")
        bin_name = product.get("bin", "UNKNOWN BIN")
        lines.append(
            f"{line['lineNumber']}. {sku} | {description} | qty {int(line['quantity'])} | bin {bin_name}"
        )
    lines.append("")
    return "\n".join(lines)


def load_inventory_lookup(path):
    inventory_doc = json.loads(Path(path).read_text(encoding="utf-8"))
    return inventory_by_sku(inventory_doc)


def main(argv):
    if len(argv) != 2:
        print("usage: pick_ticket.py <pick-work-message.json>", file=sys.stderr)
        return 2
    message = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    lookup = load_inventory_lookup("data/inventory.json")
    print(build_pick_ticket_text(message, lookup))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
