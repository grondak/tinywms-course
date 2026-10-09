import unittest

from src import domain_events


class DomainEventsTests(unittest.TestCase):
    def test_build_order_placed_event_from_order_result(self):
        event = domain_events.build_order_placed_event(
            {
                "orderId": 42,
                "customer": "Example School Store",
                "status": "created",
                "lines": [
                    {"sku": "SKU-1001", "quantity": 2},
                    {"sku": "SKU-1003", "quantity": 1},
                ],
            },
            placed_at="2026-01-15T10:30:00Z",
        )
        self.assertEqual(event["eventType"], "OrderPlaced")
        self.assertEqual(event["version"], 1)
        self.assertEqual(event["orderId"], 42)
        self.assertEqual(event["customer"], "Example School Store")
        self.assertEqual(event["placedAt"], "2026-01-15T10:30:00Z")
        self.assertEqual(event["lines"][0]["lineNumber"], 1)
        self.assertEqual(event["lines"][1]["sku"], "SKU-1003")


if __name__ == "__main__":
    unittest.main()
