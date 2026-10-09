import unittest

from src import event_consumer_audit, event_consumer_shipping


class EventConsumersTests(unittest.TestCase):
    def setUp(self):
        self.event = {
            "eventType": "OrderPlaced",
            "version": 1,
            "orderId": 42,
            "customer": "Example School Store",
            "placedAt": "2026-01-15T10:30:00Z",
            "lines": [
                {"lineNumber": 1, "sku": "SKU-1001", "quantity": 2},
                {"lineNumber": 2, "sku": "SKU-1003", "quantity": 1},
            ],
        }

    def test_shipping_consumer_reacts_to_same_event(self):
        notice = event_consumer_shipping.build_shipping_notice(self.event)
        self.assertEqual(notice["consumer"], "shipping")
        self.assertEqual(notice["eventType"], "OrderPlaced")
        self.assertEqual(notice["orderId"], 42)
        self.assertEqual(notice["skuCount"], 2)
        self.assertEqual(notice["skus"], ["SKU-1001", "SKU-1003"])

    def test_audit_consumer_reacts_to_same_event(self):
        record = event_consumer_audit.build_audit_record(self.event)
        self.assertEqual(record["consumer"], "audit")
        self.assertEqual(record["eventType"], "OrderPlaced")
        self.assertEqual(record["orderId"], 42)
        self.assertEqual(record["totalLines"], 2)
        self.assertEqual(record["totalUnits"], 3)


if __name__ == "__main__":
    unittest.main()
