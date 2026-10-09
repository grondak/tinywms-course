import unittest

from src import rds_inventory


class RdsInventoryTests(unittest.TestCase):
    def test_rows_to_inventory_preserves_contract(self):
        doc = rds_inventory.rows_to_inventory([
            {"sku": "SKU-1", "description": "Item", "bin": "A1", "quantity": 7, "unit": "each"}
        ])
        self.assertEqual(doc["inventory"][0]["sku"], "SKU-1")
        self.assertEqual(doc["inventory"][0]["bin"], "A1")
        self.assertEqual(doc["inventory"][0]["quantity"], 7)
        self.assertEqual(doc["inventory"][0]["unit"], "each")


if __name__ == "__main__":
    unittest.main()
