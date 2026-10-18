"""Local stand-ins for SQS and EventBridge, so the whole system runs on one machine.

TINYWMS_LOCAL=1 switches the order code, the pick-ticket worker and the event
consumers from AWS to these. Every "queue" is a directory and every message is
one JSON file in it, so students can watch the system with ls, cat and tail.

Deliberate differences from real SQS (the lessons point these out):
  * no visibility timeout: a message stays put until it is deleted, so a worker
    that crashes mid-message simply sees the message again on restart
  * no at-least-once duplicates of your own: to see a duplicate, copy a file
  * oldest-first ordering (a standard SQS queue does not promise that)
"""
from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL_ENV = 'TINYWMS_LOCAL'
LOCAL_DIR_ENV = 'TINYWMS_LOCAL_DIR'
EVENT_SUBSCRIBERS = ('event-consumer-a', 'event-consumer-b')   # one queue per EventBridge rule in infra/events.yaml


def local_dir() -> Path:
    return Path(os.environ.get(LOCAL_DIR_ENV, ROOT / 'local-aws'))


def configure() -> Path:
    """Point the app at the local stand-ins and create the SQLite database on first use. Returns the state directory."""
    base = local_dir()
    base.mkdir(parents=True, exist_ok=True)
    os.environ[LOCAL_ENV] = '1'
    os.environ.setdefault('TINYWMS_DB', 'sqlite')
    os.environ.setdefault('TINYWMS_SQLITE_PATH', str(base / 'tinywms.db'))
    os.environ.setdefault('PICK_WORK_QUEUE_URL', str(base / 'pick-work'))
    os.environ.setdefault('EVENT_BUS_NAME', str(base))
    db_path = Path(os.environ['TINYWMS_SQLITE_PATH'])
    if os.environ['TINYWMS_DB'] == 'sqlite' and not db_path.exists():
        from data.init_db import init_db
        init_db()
    return base


class FileQueue:
    """The slice of the SQS client that TinyWMS uses. QueueUrl is a directory path."""

    def send_message(self, QueueUrl, MessageBody, **_):
        queue = Path(QueueUrl)
        queue.mkdir(parents=True, exist_ok=True)
        message_id = str(uuid.uuid4())
        name = f'{time.time_ns():020d}-{message_id}.json'
        tmp = queue / f'.{name}.tmp'
        tmp.write_text(json.dumps({'MessageId': message_id, 'Body': MessageBody}), encoding='utf-8')
        tmp.rename(queue / name)               # appears all at once, never half-written
        return {'MessageId': message_id}

    def receive_message(self, QueueUrl, MaxNumberOfMessages=10, WaitTimeSeconds=0, **_):
        queue = Path(QueueUrl)
        deadline = time.monotonic() + WaitTimeSeconds
        while True:
            files = sorted(queue.glob('*.json')) if queue.is_dir() else []
            if files or time.monotonic() >= deadline:
                break
            time.sleep(0.2)                    # long polling, the simple way
        messages = []
        for path in files[:MaxNumberOfMessages]:
            try:
                stored = json.loads(path.read_text(encoding='utf-8'))
            except (OSError, json.JSONDecodeError):
                continue
            messages.append({'MessageId': stored['MessageId'], 'ReceiptHandle': path.name, 'Body': stored['Body']})
        return {'Messages': messages} if messages else {}

    def delete_message(self, QueueUrl, ReceiptHandle):
        try:
            (Path(QueueUrl) / ReceiptHandle).unlink()
        except FileNotFoundError:
            pass


class FileEventBus:
    """The slice of the EventBridge client that TinyWMS uses.

    Each event is copied into every subscriber queue, in the shape EventBridge
    delivers to an SQS target: lower-case "detail-type" and "detail" is an object.
    """

    def __init__(self, base=None, subscribers=EVENT_SUBSCRIBERS):
        self.base = Path(base) if base else local_dir()
        self.subscribers = subscribers
        self.queue = FileQueue()

    def put_events(self, Entries):
        for entry in Entries:
            delivered = {
                'version': '0',
                'id': str(uuid.uuid4()),
                'detail-type': entry['DetailType'],
                'source': entry['Source'],
                'time': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                'detail': json.loads(entry['Detail']),
            }
            for subscriber in self.subscribers:
                self.queue.send_message(str(self.base / subscriber), json.dumps(delivered))
        return {'FailedEntryCount': 0, 'Entries': [{'EventId': str(uuid.uuid4())} for _ in Entries]}
