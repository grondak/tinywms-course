#!/usr/bin/env python3
import json
import sys
from pathlib import Path

INVENTORY_PATH = Path("data/inventory.json")


def load_inventory(path=INVENTORY_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_response(status_code, body_obj):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "isBase64Encoded": False,
        "body": json.dumps(body_obj, indent=2, sort_keys=True)
    }


def handler(event, context):
    method = event.get("httpMethod")
    path = event.get("path")
    if method != "GET" or path != "/inventory":
        return build_response(404, {"error": "not found", "method": method, "path": path})
    return build_response(200, load_inventory())


def main(argv):
    event = json.load(sys.stdin)
    response = handler(event, None)
    print(json.dumps(response, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
