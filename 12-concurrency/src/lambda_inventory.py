#!/usr/bin/env python3
import json
import os
import sys

from src.order_service import create_order_from_event
from src.rds_inventory import inventory_json_from_rds


def build_response(status_code, body_obj):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "isBase64Encoded": False,
        "body": json.dumps(body_obj, indent=2, sort_keys=True)
    }


def db_config_from_env():
    return {
        "host": os.environ["TINYWMS_DB_HOST"],
        "port": int(os.environ.get("TINYWMS_DB_PORT", "5432")),
        "dbname": os.environ["TINYWMS_DB_NAME"],
        "user": os.environ["TINYWMS_DB_USER"],
        "password": os.environ["TINYWMS_DB_PASSWORD"],
    }


def handler(event, context):
    method = event.get("httpMethod")
    path = event.get("path")

    if method == "GET" and path == "/inventory":
        try:
            inventory_doc = inventory_json_from_rds(**db_config_from_env())
        except KeyError as exc:
            return build_response(500, {"error": "missing database configuration", "missing": str(exc)})
        except Exception as exc:
            return build_response(500, {"error": "database unavailable", "details": str(exc)})
        return build_response(200, inventory_doc)

    if method == "POST" and path == "/orders":
        try:
            return create_order_from_event(event, db_config_from_env())
        except KeyError as exc:
            return build_response(500, {"error": "missing database configuration", "missing": str(exc)})

    return build_response(404, {"error": "not found", "method": method, "path": path})


def main(argv):
    event = json.load(sys.stdin)
    response = handler(event, None)
    print(json.dumps(response, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
