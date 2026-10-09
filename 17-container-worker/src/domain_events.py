#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timezone


def utc_now_iso8601():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_order_placed_event(order_result, placed_at=None):
    timestamp = placed_at or utc_now_iso8601()
    lines = []
    for index, line in enumerate(order_result["lines"], start=1):
        lines.append(
            {
                "lineNumber": index,
                "sku": line["sku"],
                "quantity": int(line["quantity"]),
            }
        )
    return {
        "eventType": "OrderPlaced",
        "version": 1,
        "orderId": int(order_result["orderId"]),
        "customer": order_result["customer"],
        "placedAt": timestamp,
        "lines": lines,
    }


def main(argv):
    payload = json.load(sys.stdin)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
