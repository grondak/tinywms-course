#!/usr/bin/env python3
import json
import os
from pathlib import Path
from urllib.parse import quote_plus

try:
    import psycopg2
except ImportError:  # pragma: no cover
    psycopg2 = None


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
