#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timezone


def utc_now_iso8601():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_pick_work_message(order_result, created_at=None):
    timestamp = created_at or utc_now_iso8601()
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
        "messageType": "PickWorkRequested",
        "version": 1,
        "orderId": int(order_result["orderId"]),
        "customer": order_result["customer"],
        "createdAt": timestamp,
        "lines": lines,
    }


def main(argv):
    payload = json.load(sys.stdin)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
