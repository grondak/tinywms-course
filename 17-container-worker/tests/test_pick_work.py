import unittest

from src import pick_work


class PickWorkTests(unittest.TestCase):
    def test_build_pick_work_message_from_order_result(self):
        message = pick_work.build_pick_work_message(
            {
                "orderId": 42,
                "customer": "Example School Store",
                "status": "created",
                "lines": [
                    {"sku": "SKU-1001", "quantity": 2},
                    {"sku": "SKU-1003", "quantity": 1},
                ],
            },
            created_at="2026-01-15T10:30:00Z",
        )
        self.assertEqual(message["messageType"], "PickWorkRequested")
        self.assertEqual(message["version"], 1)
        self.assertEqual(message["orderId"], 42)
        self.assertEqual(message["customer"], "Example School Store")
        self.assertEqual(message["createdAt"], "2026-01-15T10:30:00Z")
        self.assertEqual(message["lines"][0]["lineNumber"], 1)
        self.assertEqual(message["lines"][1]["sku"], "SKU-1003")


if __name__ == "__main__":
    unittest.main()
