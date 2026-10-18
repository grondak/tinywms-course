from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_FILE = ROOT / 'data' / 'inventory.json'
DB_DSN_ENV = 'DATABASE_URL'


def load_inventory() -> list[dict[str, Any]]:
    return json.loads(INVENTORY_FILE.read_text(encoding='utf-8'))


def handler(event, context):
    event = event or {}
    query_string = event.get('queryStringParameters') or {}
    if query_string.get('demo') == 'local-json':
        payload = load_inventory()
    else:
        payload = load_inventory()
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(payload),
    }
