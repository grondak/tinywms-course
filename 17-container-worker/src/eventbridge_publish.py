#!/usr/bin/env python3
import json
import os
import sys
import urllib.parse
import urllib.request
from xml.etree import ElementTree


def aws_region_from_env():
    return os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"


def event_bus_name_from_env():
    return os.environ.get("TINYWMS_EVENT_BUS_NAME", "").strip() or "default"


def publish_order_event(event_obj, event_bus_name=None):
    bus_name = (event_bus_name or event_bus_name_from_env()).strip()
    body_text = json.dumps(event_obj, indent=2, sort_keys=True)
    form = urllib.parse.urlencode(
        {
            "Action": "PutEvents",
            "Version": "2015-10-07",
            "Entries.member.1.Source": "tinywms.orders",
            "Entries.member.1.DetailType": event_obj["eventType"],
            "Entries.member.1.EventBusName": bus_name,
            "Entries.member.1.Detail": body_text,
        }
    ).encode("utf-8")
    request = urllib.request.Request("https://events.amazonaws.com/", data=form, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    request.add_header("X-TinyWMS-Region", aws_region_from_env())
    with urllib.request.urlopen(request) as response:
        xml_text = response.read().decode("utf-8")
    root = ElementTree.fromstring(xml_text)
    event_id = root.findtext(".//EventId")
    if not event_id:
        raise RuntimeError("EventBridge response did not contain EventId")
    print(f"published eventId={event_id} eventBusName={bus_name}")
    return {"eventId": event_id, "body": body_text, "eventBusName": bus_name}


def main(argv):
    if len(argv) != 2:
        print("usage: eventbridge_publish.py <event.json>", file=sys.stderr)
        return 2
    with open(argv[1], "r", encoding="utf-8") as f:
        event = json.load(f)
    publish_order_event(event)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
