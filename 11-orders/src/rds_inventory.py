#!/usr/bin/env python3
try:
    import psycopg2
except ImportError:  # pragma: no cover
    psycopg2 = None


class InsufficientInventoryError(Exception):
    def __init__(self, sku, requested, available):
        super().__init__(f"insufficient inventory for {sku}: requested {requested}, available {available}")
        self.sku = sku
        self.requested = requested
        self.available = available


def rows_to_inventory(rows):
    inventory = []
    for row in rows:
        inventory.append(
            {
                "sku": row["sku"],
                "description": row["description"],
                "bin": row["bin"],
                "quantity": int(row["quantity"]),
                "unit": row["unit"],
            }
        )
    return {"inventory": inventory}


def fetch_inventory_rows(host, port, dbname, user, password):
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is not available in this Python environment")
    connection = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.sku, p.description, i.bin, i.quantity, p.unit
                FROM products p
                JOIN inventory_locations i ON i.sku = p.sku
                ORDER BY p.sku, i.bin
                """
            )
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return [dict(zip(column_names, row)) for row in rows]
    finally:
        connection.close()


def inventory_json_from_rds(host, port, dbname, user, password):
    return rows_to_inventory(fetch_inventory_rows(host, port, dbname, user, password))


def connect_postgres(host, port, dbname, user, password):
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is not available in this Python environment")
    return psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
    )


def create_order_in_rds(order_doc, host, port, dbname, user, password):
    connection = connect_postgres(host, port, dbname, user, password)
    try:
        return create_order_with_connection(connection, order_doc)
    finally:
        connection.close()


def create_order_with_connection(connection, order_doc):
    # Production uses PostgreSQL, while the local continuity tests use SQLite.
    # Keep the small SQL-dialect difference visible instead of hiding it behind
    # an ORM or a database framework.
    sqlite_connection = connection.__class__.__module__ == "sqlite3"
    placeholder = "?" if sqlite_connection else "%s"

    try:
        cursor = connection.cursor()
        if sqlite_connection:
            cursor.execute(
                "INSERT INTO orders (customer) VALUES (?)",
                (order_doc["customer"],),
            )
            order_id = cursor.lastrowid
        else:
            cursor.execute(
                "INSERT INTO orders (customer) VALUES (%s) RETURNING id",
                (order_doc["customer"],),
            )
            order_id = cursor.fetchone()[0]

        committed_lines = []
        for line_number, line in enumerate(order_doc["lines"], start=1):
            cursor.execute(
                f"SELECT quantity FROM inventory_locations WHERE sku = {placeholder}",
                (line["sku"],),
            )
            row = cursor.fetchone()
            available = 0 if row is None else int(row[0])
            requested = int(line["quantity"])
            if row is None or available < requested:
                raise InsufficientInventoryError(line["sku"], requested, available)

            cursor.execute(
                "UPDATE inventory_locations "
                f"SET quantity = quantity - {placeholder} WHERE sku = {placeholder}",
                (requested, line["sku"]),
            )
            cursor.execute(
                "INSERT INTO order_lines (order_id, line_number, sku, quantity) "
                f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})",
                (order_id, line_number, line["sku"], requested),
            )
            committed_lines.append({"sku": line["sku"], "quantity": requested})

        connection.commit()
        return {
            "orderId": order_id,
            "customer": order_doc["customer"],
            "status": "created",
            "lines": committed_lines,
        }
    except Exception:
        connection.rollback()
        raise
