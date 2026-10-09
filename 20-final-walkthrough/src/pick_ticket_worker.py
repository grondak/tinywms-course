#!/usr/bin/env python3
import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path

from src.pick_ticket import build_pick_ticket_text, load_inventory_lookup
from src.sqs_consumer import delete_message, receive_messages


class StopWorker(Exception):
    pass


def default_output_path():
    return os.environ.get("TINYWMS_PICK_TICKETS_PATH", "pick-tickets.txt")


def append_ticket(output_path, ticket_text):
    path = Path(output_path)
    with path.open("a", encoding="utf-8") as f:
        f.write(ticket_text)
        if not ticket_text.endswith("\n"):
            f.write("\n")
        f.write("\n")


def process_pick_work_message(message_obj, inventory_lookup, output_path):
    ticket_text = build_pick_ticket_text(message_obj, inventory_lookup)
    append_ticket(output_path, ticket_text)
    print(
        f"wrote pick ticket orderId={message_obj.get('orderId')} lines={len(message_obj.get('lines', []))} output={output_path}",
        flush=True,
    )
    return ticket_text


def process_sqs_message(sqs_message, inventory_lookup, output_path, ack=False):
    message_id = sqs_message.get("MessageId")
    receipt_handle = sqs_message.get("ReceiptHandle")
    body_text = sqs_message.get("Body", "")
    print(f"received messageId={message_id}", flush=True)
    try:
        message_obj = json.loads(body_text)
        process_pick_work_message(message_obj, inventory_lookup, output_path)
    except Exception as exc:
        print(f"failed messageId={message_id}: {exc}", file=sys.stderr, flush=True)
        return False

    if ack and receipt_handle:
        delete_message(receipt_handle)
        print(f"acknowledged messageId={message_id}", flush=True)
    else:
        print(f"left messageId={message_id} on queue for retry", flush=True)
    return True


def run_once_from_file(message_file, inventory_lookup, output_path):
    message_obj = json.loads(Path(message_file).read_text(encoding="utf-8"))
    process_pick_work_message(message_obj, inventory_lookup, output_path)
    return 0


def run_forever(inventory_lookup, output_path, poll_seconds=2, ack=True):
    stop_requested = {"value": False}

    def handle_signal(signum, frame):
        stop_requested["value"] = True
        print(f"received signal {signum}, shutting down worker", flush=True)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    print(f"starting pick-ticket worker output={output_path} ack={ack}", flush=True)
    while not stop_requested["value"]:
        try:
            messages = receive_messages(max_messages=1, visibility_timeout=30, wait_time=0)
        except Exception as exc:
            print(f"worker poll error: {exc}", file=sys.stderr, flush=True)
            time.sleep(poll_seconds)
            continue

        if not messages:
            print("no messages available", flush=True)
            time.sleep(poll_seconds)
            continue

        for message in messages:
            process_sqs_message(message, inventory_lookup, output_path, ack=ack)

    print("worker stopped", flush=True)
    return 0


def main(argv):
    parser = argparse.ArgumentParser(description="TinyWMS pick-ticket worker")
    parser.add_argument("--output", default=default_output_path(), help="path to appended pick-ticket text file")
    parser.add_argument("--inventory", default="data/inventory.json", help="inventory JSON used for SKU description and bin lookup")
    parser.add_argument("--message-file", help="process one local pick-work JSON file instead of polling SQS")
    parser.add_argument("--once", action="store_true", help="required together with --message-file for local one-shot processing")
    parser.add_argument("--poll-seconds", type=int, default=2, help="seconds to sleep between empty polls or poll errors")
    parser.add_argument("--no-ack", action="store_true", help="leave processed SQS messages on the queue for retry")
    args = parser.parse_args(argv[1:])

    inventory_lookup = load_inventory_lookup(args.inventory)

    if args.message_file:
        if not args.once:
            print("--message-file requires --once", file=sys.stderr)
            return 2
        return run_once_from_file(args.message_file, inventory_lookup, args.output)

    return run_forever(inventory_lookup, args.output, poll_seconds=args.poll_seconds, ack=not args.no_ack)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
