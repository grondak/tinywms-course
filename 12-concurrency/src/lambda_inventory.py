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
INVENTORY_FOR_UPDATE_SQL = 'SELECT sku, description, bin_location, quantity, unit FROM inventory WHERE sku = %s FOR UPDATE'
DECREMENT_INVENTORY_SQL = 'UPDATE inventory SET quantity = quantity - %s WHERE sku = %s AND quantity >= %s'
INSERT_ORDER_SQL = 'INSERT INTO orders (order_id, status) VALUES (%s, %s)'
INSERT_ORDER_LINE_SQL = 'INSERT INTO order_lines (order_id, sku, quantity) VALUES (%s, %s, %s)'


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


class DuplicateOrderError(InventoryError):
    pass


def _parse_body(event: dict[str, Any]) -> dict[str, Any]:
    body = event.get('body') or '{}'
    if isinstance(body, str):
        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise OrderValidationError('request body must be JSON') from exc
    if isinstance(body, dict):
        return body
    raise OrderValidationError('request body must be JSON')


def parse_order_request(event: dict[str, Any]) -> OrderRequest:
    body = _parse_body(event)
    if 'order_id' not in body or 'lines' not in body:
        raise OrderValidationError('invalid order')
    if not isinstance(body['order_id'], str) or not body['order_id']:
        raise OrderValidationError('order_id must be a non-empty string')
    if not isinstance(body['lines'], list) or not body['lines']:
        raise OrderValidationError('lines must be a non-empty array')
    lines: list[OrderLine] = []
    for item in body['lines']:
        if not isinstance(item, dict):
            raise OrderValidationError('each order line must be an object')
        sku = item.get('sku')
        quantity = item.get('quantity')
        description = item.get('description')
        if not isinstance(sku, str) or not sku:
            raise OrderValidationError('line sku must be a non-empty string')
        if not isinstance(quantity, int) or quantity < 1:
            raise OrderValidationError('line quantity must be a positive integer')
        if description is not None and not isinstance(description, str):
            raise OrderValidationError('line description must be a string when present')
        lines.append(OrderLine(sku=sku, quantity=quantity, description=description or ''))
    return OrderRequest(order_id=body['order_id'], lines=lines)


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


def _open_default_connection():
    """Connection used when the caller does not inject one: SQLite when TINYWMS_DB=sqlite, otherwise PostgreSQL."""
    if os.environ.get(TINYWMS_DB_ENV, 'postgres').strip().lower() == 'sqlite':
        from src.db_adapter import connect_sqlite
        return connect_sqlite()
    return _postgres_connection()


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
        cursor.execute('BEGIN')
        locked_rows: list[dict[str, Any]] = []
        for line in order.lines:
            cursor.execute(INVENTORY_FOR_UPDATE_SQL, (line.sku,))
            row = cursor.fetchone()
            if row is None:
                raise InventoryShortageError(f'unknown sku: {line.sku}')
            inventory = _map_inventory_row(row)
            if inventory['quantity'] < line.quantity:
                raise InventoryShortageError(f'insufficient inventory for {line.sku}')
            cursor.execute(DECREMENT_INVENTORY_SQL, (line.quantity, line.sku, line.quantity))
            if cursor.rowcount != 1:
                raise InventoryShortageError(f'insufficient inventory for {line.sku}')
            locked_rows.append(inventory)
        try:
            cursor.execute(INSERT_ORDER_SQL, (order.order_id, 'accepted'))
        except Exception as exc:
            if type(exc).__name__ in ('IntegrityError', 'UniqueViolation'):
                raise DuplicateOrderError(f'order already exists: {order.order_id}') from exc
            raise
        for line in order.lines:
            cursor.execute(INSERT_ORDER_LINE_SQL, (order.order_id, line.sku, line.quantity))
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


def _json_response(status: int, payload: Any) -> dict[str, Any]:
    return {'statusCode': status, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps(payload)}


def handler(event, context, connection_factory=None):
    event = event or {}
    if event.get('httpMethod') == 'POST':
        try:
            order = parse_order_request(event)
            connection = (connection_factory or _open_default_connection)()
            try:
                result = place_order(connection, order)
            finally:
                connection.close()
            return _json_response(201, result)
        except OrderValidationError as exc:
            return _json_response(400, {'error': str(exc)})
        except (InventoryShortageError, DuplicateOrderError) as exc:
            return _json_response(409, {'error': str(exc)})
    query_string = event.get('queryStringParameters') or {}
    if query_string.get('demo') == 'local-json':
        payload = _load_inventory()
    else:
        connection = (connection_factory or _open_default_connection)()
        try:
            payload = _read_inventory_rows(connection)
        finally:
            connection.close()
    return _json_response(200, payload)
