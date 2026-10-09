#!/usr/bin/env python3
import json
import sys


def build_audit_record(event):
    total_lines = len(event.get("lines", []))
    total_units = sum(int(line.get("quantity", 0)) for line in event.get("lines", []))
    return {
        "consumer": "audit",
        "eventType": event.get("eventType"),
        "orderId": event.get("orderId"),
        "customer": event.get("customer"),
        "version": event.get("version"),
        "totalLines": total_lines,
        "totalUnits": total_units,
    }


def main(argv):
    event = json.load(sys.stdin)
    print(json.dumps(build_audit_record(event), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
