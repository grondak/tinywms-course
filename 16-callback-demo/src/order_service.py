#!/usr/bin/env python3
import json
import os

from src.domain_events import build_order_placed_event
from src.eventbridge_publish import publish_order_event
from src.pick_work import build_pick_work_message
from src.rds_inventory import InsufficientInventoryError, create_order_in_rds
from src.sqs_publish import publish_json_message

REQUIRED_TOP_LEVEL_FIELDS = ("customer", "lines")
REQUIRED_LINE_FIELDS = ("sku", "quantity")


def build_response(status_code, body_obj):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "isBase64Encoded": False,
        "body": json.dumps(body_obj, indent=2, sort_keys=True)
    }


def parse_order_event_body(event):
    body = event.get("body")
    if body in (None, ""):
        raise ValueError("request body is required")
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError(f"request body is not valid JSON: {exc.msg}")
    if not isinstance(payload, dict):
        raise ValueError("request body must be a JSON object")
    return payload


def validate_order(order_doc):
    errors = []
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in order_doc:
            errors.append(f"missing {field}")

    if errors:
        return errors

    if not isinstance(order_doc["customer"], str) or not order_doc["customer"].strip():
        errors.append("customer must be a non-empty string")

    lines = order_doc["lines"]
    if not isinstance(lines, list) or not lines:
        errors.append("lines must be a non-empty array")
        return errors

    for index, line in enumerate(lines):
        if not isinstance(line, dict):
            errors.append(f"lines[{index}] must be an object")
            continue
        for field in REQUIRED_LINE_FIELDS:
            if field not in line:
                errors.append(f"lines[{index}] missing {field}")
        if "sku" in line and (not isinstance(line["sku"], str) or not line["sku"].strip()):
            errors.append(f"lines[{index}].sku must be a non-empty string")
        if "quantity" in line and (not isinstance(line["quantity"], int) or line["quantity"] <= 0):
            errors.append(f"lines[{index}].quantity must be a positive integer")
    return errors


def maybe_publish_pick_work(order_result):
    queue_url = os.environ.get("TINYWMS_SQS_QUEUE_URL", "").strip()
    if not queue_url:
        return None
    message = build_pick_work_message(order_result)
    return publish_json_message(queue_url, message)


def maybe_publish_order_placed_event(order_result):
    event_bus_name = os.environ.get("TINYWMS_EVENT_BUS_NAME", "").strip()
    if not event_bus_name:
        return None
    event = build_order_placed_event(order_result)
    return publish_order_event(event, event_bus_name)


def create_order_from_event(event, db_config):
    try:
        order_doc = parse_order_event_body(event)
    except ValueError as exc:
        return build_response(400, {"error": "invalid order request", "details": str(exc)})

    errors = validate_order(order_doc)
    if errors:
        return build_response(400, {"error": "invalid order request", "details": errors})

    try:
        result = create_order_in_rds(order_doc, **db_config)
        maybe_publish_pick_work(result)
        maybe_publish_order_placed_event(result)
    except InsufficientInventoryError as exc:
        return build_response(
            409,
            {
                "error": "insufficient inventory",
                "sku": exc.sku,
                "requested": exc.requested,
                "available": exc.available,
            },
        )
    except Exception as exc:
        return build_response(500, {"error": "database unavailable", "details": str(exc)})

    return build_response(201, result)
