import unittest

from src import demo_trace


class DemoTraceTests(unittest.TestCase):
    def test_build_demo_trace_contains_visible_boundary_artifacts(self):
        order_doc = {
            "customer": "Example School Store",
            "lines": [
                {"sku": "SKU-1001", "quantity": 2},
                {"sku": "SKU-1003", "quantity": 1},
            ],
        }
        inventory_doc = {
            "inventory": [
                {
                    "sku": "SKU-1001",
                    "description": "Blue widget",
                    "bin": "A1-01",
                    "quantity": 24,
                    "unit": "each",
                },
                {
                    "sku": "SKU-1003",
                    "description": "Packing tape",
                    "bin": "B2-04",
                    "quantity": 13,
                    "unit": "roll",
                },
            ]
        }

        trace = demo_trace.build_demo_trace(
            order_doc,
            inventory_doc,
            order_id=42,
            timestamp="2026-01-15T10:30:00Z",
        )

        self.assertEqual(trace["browserOrderRequest"]["customer"], "Example School Store")
        self.assertEqual(trace["apiGatewayLambdaEvent"]["httpMethod"], "POST")
        self.assertEqual(trace["apiGatewayLambdaEvent"]["path"], "/orders")
        self.assertIn('"customer": "Example School Store"', trace["apiGatewayLambdaEvent"]["body"])
        self.assertEqual(trace["orderResultAfterRdsCommit"]["orderId"], 42)
        self.assertEqual(trace["sqsPickWorkMessage"]["messageType"], "PickWorkRequested")
        self.assertEqual(trace["eventBridgeOrderPlaced"]["eventType"], "OrderPlaced")
        self.assertIn("Order ID: 42", trace["pickTicketText"])
        self.assertIn("SKU-1001 | Blue widget | qty 2 | bin A1-01", trace["pickTicketText"])


if __name__ == "__main__":
    unittest.main()
