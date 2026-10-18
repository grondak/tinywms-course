from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator

from src.db_adapter import SQLiteCursorAdapter, open_connection as open_db_connection

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_FILE = ROOT / 'data' / 'inventory.json'
DB_DSN_ENV = 'DATABASE_URL'
TINYWMS_DB_ENV = 'TINYWMS_DB'
TINYWMS_SQLITE_PATH_ENV = 'TINYWMS_SQLITE_PATH'
INVENTORY_QUERY_SQL = 'SELECT sku, description, bin_location, quantity, unit FROM inventory ORDER BY sku'


class InventoryError(Exception):
    pass


class DatabaseInventoryError(InventoryError):
    pass


@dataclass(frozen=True)
class InventoryRow:
    sku: str
    description: str
    bin_location: str
    quantity: int
    unit: str


def _load_inventory() -> list[dict[str, Any]]:
    return json.loads(INVENTORY_FILE.read_text(encoding='utf-8'))


def _map_inventory_row(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        bin_location = row.get('bin_location', row.get('bin'))
        return {
            'sku': row['sku'],
            'description': row['description'],
            'bin_location': bin_location,
            'quantity': row['quantity'],
            'unit': row['unit'],
        }
    return {
        'sku': row[0],
        'description': row[1],
        'bin_location': row[2],
        'quantity': row[3],
        'unit': row[4],
    }


def _cursor_for_connection(connection):
    cursor = connection.cursor()
    if connection.__class__.__module__ == 'sqlite3':
        return SQLiteCursorAdapter(cursor)
    return cursor


def _read_inventory_rows(connection) -> list[dict[str, Any]]:
    cursor = _cursor_for_connection(connection)
    try:
        cursor.execute(INVENTORY_QUERY_SQL)
        rows = cursor.fetchall()
        return [_map_inventory_row(row) for row in rows]
    finally:
        cursor.close()


def _postgres_connection():
    dsn = os.environ.get(DB_DSN_ENV)
    if not dsn:
        raise RuntimeError('DATABASE_URL is required when TINYWMS_DB=postgres')
    try:
        import psycopg
    except ModuleNotFoundError:
        import psycopg2 as psycopg  # type: ignore
    return psycopg.connect(dsn)


@contextmanager
def open_connection(dsn: str | None = None) -> Iterator[Any]:
    backend = os.environ.get(TINYWMS_DB_ENV, 'postgres').strip().lower()
    if backend == 'sqlite':
        with open_db_connection() as connection:
            yield connection
        return
    connection = _postgres_connection() if dsn is None else _postgres_connection_from_dsn(dsn)
    try:
        yield connection
    finally:
        connection.close()


def _postgres_connection_from_dsn(dsn: str):
    try:
        import psycopg
    except ModuleNotFoundError:
        import psycopg2 as psycopg  # type: ignore
    return psycopg.connect(dsn)


def handler(event, context, connection_factory: Callable[[], Any] | None = None):
    event = event or {}
    query_string = event.get('queryStringParameters') or {}
    if query_string.get('demo') == 'local-json':
        payload = _load_inventory()
    else:
        factory = connection_factory or open_connection
        connection = factory()
        try:
            payload = _read_inventory_rows(connection)
        finally:
            connection.close()
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(payload),
    }
