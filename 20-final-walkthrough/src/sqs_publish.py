#!/usr/bin/env python3
import json
import os
import sys
import urllib.parse
import urllib.request
from xml.etree import ElementTree


def aws_region_from_env():
    return os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"


def publish_json_message(queue_url, message_obj):
    body_text = json.dumps(message_obj, indent=2, sort_keys=True)
    form = urllib.parse.urlencode(
        {
            "Action": "SendMessage",
            "Version": "2012-11-05",
            "MessageBody": body_text,
        }
    ).encode("utf-8")
    request = urllib.request.Request(queue_url, data=form, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    request.add_header("X-TinyWMS-Region", aws_region_from_env())
    with urllib.request.urlopen(request) as response:
        xml_text = response.read().decode("utf-8")
    root = ElementTree.fromstring(xml_text)
    message_id = root.findtext(".//MessageId")
    if not message_id:
        raise RuntimeError("SQS response did not contain MessageId")
    print(f"published messageId={message_id} queueUrl={queue_url}")
    return {"messageId": message_id, "body": body_text}


def main(argv):
    if len(argv) != 2:
        print("usage: sqs_publish.py <message.json>", file=sys.stderr)
        return 2
    queue_url = os.environ.get("TINYWMS_SQS_QUEUE_URL", "").strip()
    if not queue_url:
        print("TINYWMS_SQS_QUEUE_URL is not set", file=sys.stderr)
        return 2
    with open(argv[1], "r", encoding="utf-8") as f:
        message = json.load(f)
    publish_json_message(queue_url, message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
