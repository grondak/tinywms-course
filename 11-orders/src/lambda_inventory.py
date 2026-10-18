from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.db_adapter import SQLiteCursorAdapter, open_connection as open_db_connection

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_FILE = ROOT / 'data' / 'inventory.json'
DB_DSN_ENV = 'DATABASE_URL'
TINYWMS_DB_ENV = 'TINYWMS_DB'
TINYWMS_SQLITE_PATH_ENV = 'TINYWMS_SQLITE_PATH'
INVENTORY_QUERY_SQL = 'SELECT sku, description, bin_location, quantity, unit FROM inventory ORDER BY sku'
ORDER_INSERT_SQL = 'INSERT INTO orders (order_id, status) VALUES (%s, %s)'
ORDER_LINE_INSERT_SQL = 'INSERT INTO order_lines (order_id, sku, quantity) VALUES (%s, %s, %s)'
INVENTORY_UPDATE_SQL = 'UPDATE inventory SET quantity = quantity - %s WHERE sku = %s AND quantity >= %s'
INVENTORY_LOOKUP_SQL = 'SELECT sku, description, bin_location, quantity, unit FROM inventory WHERE sku = %s'


class InventoryError(Exception):
    pass


class OrderValidationError(InventoryError):
    pass


class InventoryShortageError(InventoryError):
    pass


@dataclass(frozen=True)
class InventoryRow:
    sku: str
    description: str
    bin_location: str
    quantity: int
    unit: str


@dataclass(frozen=True)
class OrderLine:
    sku: str
    quantity: int
    description: str = ''


@dataclass(frozen=True)
class OrderRequest:
    order_id: str
    lines: list[OrderLine]


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


def open_connection(dsn: str | None = None):
    backend = os.environ.get(TINYWMS_DB_ENV, 'postgres').strip().lower()
    if backend == 'sqlite':
        return open_db_connection()
    return _postgres_connection() if dsn is None else _postgres_connection_from_dsn(dsn)


def _postgres_connection_from_dsn(dsn: str):
    try:
        import psycopg
    except ModuleNotFoundError:
        import psycopg2 as psycopg  # type: ignore
    return psycopg.connect(dsn)


def _validate_order(order: OrderRequest) -> None:
    if not order.order_id:
        raise OrderValidationError('order_id must be a non-empty string')
    if not order.lines:
        raise OrderValidationError('lines must be a non-empty array')
    for line in order.lines:
        if not line.sku:
            raise OrderValidationError('line sku must be a non-empty string')
        if line.quantity < 1:
            raise OrderValidationError('line quantity must be a positive integer')


def _normalize_order(order) -> OrderRequest:
    if isinstance(order, OrderRequest):
        return order
    lines = [OrderLine(**line) for line in order['lines']]
    return OrderRequest(order_id=order['order_id'], lines=lines)


def place_order(connection, order: OrderRequest) -> dict[str, Any]:
    _validate_order(order)
    cursor = _cursor_for_connection(connection)
    try:
        cursor.execute(ORDER_INSERT_SQL, (order.order_id, 'accepted'))
        for line in order.lines:
            cursor.execute(INVENTORY_LOOKUP_SQL, (line.sku,))
            row = cursor.fetchone()
            if row is None:
                raise InventoryShortageError(f'unknown sku: {line.sku}')
            inventory = _map_inventory_row(row)
            if inventory['quantity'] < line.quantity:
                raise InventoryShortageError(f'insufficient inventory for {line.sku}')
            cursor.execute(ORDER_LINE_INSERT_SQL, (order.order_id, line.sku, line.quantity))
            cursor.execute(INVENTORY_UPDATE_SQL, (line.quantity, line.sku, line.quantity))
            if cursor.rowcount != 1:
                raise InventoryShortageError(f'insufficient inventory for {line.sku}')
        connection.commit()
        return {
            'order_id': order.order_id,
            'status': 'accepted',
            'lines': [
                {'sku': line.sku, 'quantity': line.quantity, 'description': line.description}
                for line in order.lines
            ],
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()


def handler(event, context, connection_factory=None):
    event = event or {}
    query_string = event.get('queryStringParameters') or {}
    if query_string.get('demo') == 'local-json':
        payload = _load_inventory()
    else:
        connection = (connection_factory or open_connection)()
        try:
            payload = _read_inventory_rows(connection)
        finally:
            connection.close()
    return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps(payload)}
