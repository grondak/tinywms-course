#!/usr/bin/env python3
from __future__ import annotations

import os
import threading
from dataclasses import dataclass
from pathlib import Path

from src.lambda_inventory import InventoryShortageError, OrderLine, OrderRequest, place_order


@dataclass
class DemoInventory:
    quantity: int


class DemoCursor:
    def __init__(self, inventory: DemoInventory, barrier: threading.Barrier):
        self.inventory = inventory
        self.barrier = barrier
        self.rowcount = 0
        self._row = None

    def execute(self, sql, params=None):
        if sql.startswith('SELECT sku, description, bin_location, quantity, unit FROM inventory WHERE sku = %s FOR UPDATE'):
            self.barrier.wait()
            self._row = ('SKU-DEMO', 'Demo widget', 'A1-01', self.inventory.quantity, 'each')
        elif sql.startswith('UPDATE inventory SET quantity = quantity -'):
            amount, sku, threshold = params
            if self.inventory.quantity >= threshold:
                self.inventory.quantity -= amount
                self.rowcount = 1
            else:
                self.rowcount = 0
        elif sql.startswith('INSERT INTO orders') or sql.startswith('INSERT INTO order_lines'):
            self.rowcount = 1
        elif sql == 'BEGIN':
            self.rowcount = 0
        else:
            raise AssertionError(f'unexpected SQL in demo: {sql}')

    def fetchone(self):
        return self._row

    def close(self):
        pass


class DemoConnection:
    def __init__(self, inventory: DemoInventory, barrier: threading.Barrier):
        self.inventory = inventory
        self.barrier = barrier
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return DemoCursor(self.inventory, self.barrier)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        pass



def _demo_connection_factory(inventory: DemoInventory, barrier: threading.Barrier):
    return DemoConnection(inventory, barrier)



def _run_attempt(name: str, inventory: DemoInventory, barrier: threading.Barrier, results: list[str]):
    connection = _demo_connection_factory(inventory, barrier)
    order = OrderRequest(order_id=name, lines=[OrderLine('SKU-DEMO', 1, 'Demo widget')])
    try:
        result = place_order(connection, order)
        results.append(f'{name}: accepted {result}')
    except InventoryShortageError as exc:
        results.append(f'{name}: rejected {exc}')



def main() -> int:
    stock = int(os.environ.get('TINYWMS_DEMO_STOCK', '1'))
    inventory = DemoInventory(quantity=stock)
    barrier = threading.Barrier(2)
    results: list[str] = []
    first = threading.Thread(target=_run_attempt, args=('ORD-DEMO-1', inventory, barrier, results))
    second = threading.Thread(target=_run_attempt, args=('ORD-DEMO-2', inventory, barrier, results))
    print(f'demo starting with quantity={inventory.quantity}')
    first.start()
    second.start()
    first.join()
    second.join()
    for line in results:
        print(line)
    print(f'final inventory quantity={inventory.quantity}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
