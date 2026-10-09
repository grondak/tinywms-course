#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

from src.domain_events import build_order_placed_event
from src.pick_ticket import build_pick_ticket_text, load_inventory_lookup
from src.pick_work import build_pick_work_message


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_order_result_from_order(order_doc, order_id=42):
    return {
        "orderId": int(order_id),
        "customer": order_doc["customer"],
        "status": "created",
        "lines": [
            {"sku": line["sku"], "quantity": int(line["quantity"])}
            for line in order_doc.get("lines", [])
        ],
    }


def build_lambda_order_event(order_doc):
    return {
        "httpMethod": "POST",
        "path": "/orders",
        "headers": {
            "content-type": "application/json",
            "accept": "application/json",
        },
        "queryStringParameters": None,
        "body": json.dumps(order_doc, indent=2),
        "isBase64Encoded": False,
    }


def build_demo_trace(order_doc, inventory_doc, order_id=42, timestamp="2026-01-15T10:30:00Z"):
    inventory_lookup = {item["sku"]: item for item in inventory_doc.get("inventory", [])}
    order_result = build_order_result_from_order(order_doc, order_id=order_id)
    pick_work_message = build_pick_work_message(order_result, created_at=timestamp)
    order_placed_event = build_order_placed_event(order_result, placed_at=timestamp)
    pick_ticket_text = build_pick_ticket_text(pick_work_message, inventory_lookup)
    return {
        "browserOrderRequest": order_doc,
        "apiGatewayLambdaEvent": build_lambda_order_event(order_doc),
        "orderResultAfterRdsCommit": order_result,
        "sqsPickWorkMessage": pick_work_message,
        "eventBridgeOrderPlaced": order_placed_event,
        "pickTicketText": pick_ticket_text,
    }


def main(argv):
    parser = argparse.ArgumentParser(description="Print visible TinyWMS callback demo artifacts")
    parser.add_argument("--order-file", default="data/order-example.json", help="order JSON used as the browser request")
    parser.add_argument("--inventory-file", default="data/inventory.json", help="inventory JSON used for pick-ticket lookup")
    parser.add_argument("--order-id", type=int, default=42, help="example committed order id to show in derived artifacts")
    parser.add_argument("--timestamp", default="2026-01-15T10:30:00Z", help="example timestamp used in derived artifacts")
    args = parser.parse_args(argv[1:])

    order_doc = load_json(args.order_file)
    inventory_doc = load_json(args.inventory_file)
    trace = build_demo_trace(order_doc, inventory_doc, order_id=args.order_id, timestamp=args.timestamp)
    print(json.dumps(trace, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
