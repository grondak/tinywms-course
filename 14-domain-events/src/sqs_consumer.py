#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from xml.etree import ElementTree


def aws_region_from_env():
    return os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"


def queue_url_from_env():
    queue_url = os.environ.get("TINYWMS_SQS_QUEUE_URL", "").strip()
    if not queue_url:
        raise RuntimeError("TINYWMS_SQS_QUEUE_URL is not set")
    return queue_url


def sqs_request(action, params):
    queue_url = queue_url_from_env()
    form = {"Action": action, "Version": "2012-11-05"}
    form.update(params)
    data = urllib.parse.urlencode(form).encode("utf-8")
    request = urllib.request.Request(queue_url, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    request.add_header("X-Amz-Target", f"AmazonSQS.{action}")
    request.add_header("X-TinyWMS-Region", aws_region_from_env())
    with urllib.request.urlopen(request) as response:
        return response.read().decode("utf-8")


def parse_receive_message_response(xml_text):
    root = ElementTree.fromstring(xml_text)
    messages = []
    for message in root.findall(".//Message"):
        entry = {}
        for child in message:
            if child.tag == "Attribute":
                name = child.findtext("Name")
                value = child.findtext("Value")
                entry.setdefault("attributes", {})[name] = value
            else:
                entry[child.tag] = child.text or ""
        messages.append(entry)
    return messages


def receive_messages(max_messages=1, visibility_timeout=30, wait_time=0):
    xml_text = sqs_request(
        "ReceiveMessage",
        {
            "MaxNumberOfMessages": str(max_messages),
            "VisibilityTimeout": str(visibility_timeout),
            "WaitTimeSeconds": str(wait_time),
            "AttributeName.1": "ApproximateReceiveCount",
            "AttributeName.2": "SentTimestamp",
        },
    )
    return parse_receive_message_response(xml_text)


def delete_message(receipt_handle):
    sqs_request("DeleteMessage", {"ReceiptHandle": receipt_handle})


def print_message(message, ack=False):
    metadata = {
        "messageId": message.get("MessageId"),
        "receiptHandle": message.get("ReceiptHandle"),
        "receiveCount": message.get("attributes", {}).get("ApproximateReceiveCount"),
        "sentTimestamp": message.get("attributes", {}).get("SentTimestamp"),
    }
    print(json.dumps({"metadata": metadata}, indent=2, sort_keys=True))
    body_text = message.get("Body", "")
    try:
        body_json = json.loads(body_text)
        print(json.dumps(body_json, indent=2, sort_keys=True))
    except json.JSONDecodeError:
        print(body_text)

    if ack:
        delete_message(message["ReceiptHandle"])
        print(f"acknowledged messageId={message.get('MessageId')}")
    else:
        print(f"left messageId={message.get('MessageId')} on queue for retry")


def main(argv):
    parser = argparse.ArgumentParser(description="Receive TinyWMS pick-work messages from SQS")
    parser.add_argument("--max-messages", type=int, default=1)
    parser.add_argument("--visibility-timeout", type=int, default=30)
    parser.add_argument("--wait-time", type=int, default=0)
    parser.add_argument("--ack", action="store_true", help="delete each received message after printing it")
    args = parser.parse_args(argv[1:])

    try:
        messages = receive_messages(
            max_messages=args.max_messages,
            visibility_timeout=args.visibility_timeout,
            wait_time=args.wait_time,
        )
    except (RuntimeError, urllib.error.URLError, ElementTree.ParseError) as exc:
        print(f"consumer error: {exc}", file=sys.stderr)
        return 1

    if not messages:
        print("no messages available")
        return 0

    for message in messages:
        print_message(message, ack=args.ack)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
