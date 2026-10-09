#!/usr/bin/env python3
import json
import sys


def build_shipping_notice(event):
    skus = [line.get("sku") for line in event.get("lines", [])]
    return {
        "consumer": "shipping",
        "eventType": event.get("eventType"),
        "orderId": event.get("orderId"),
        "customer": event.get("customer"),
        "skuCount": len(skus),
        "skus": skus,
        "message": f"shipping noticed order {event.get('orderId')} for {event.get('customer')}",
    }


def main(argv):
    event = json.load(sys.stdin)
    print(json.dumps(build_shipping_notice(event), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
