import json
import unittest
from unittest import mock

from src import order_service
from src.rds_inventory import InsufficientInventoryError


class OrderServiceTests(unittest.TestCase):
    def test_validate_order_accepts_minimal_valid_request(self):
        errors = order_service.validate_order({
            "customer": "Student Store",
            "lines": [{"sku": "SKU-1001", "quantity": 1}]
        })
        self.assertEqual(errors, [])

    def test_validate_order_rejects_missing_fields(self):
        errors = order_service.validate_order({"customer": "Student Store"})
        self.assertIn("missing lines", errors)

    def test_invalid_json_body_returns_400(self):
        response = order_service.create_order_from_event(
            {"body": "not-json"},
            {"host": "db", "port": 5432, "dbname": "tinywms", "user": "u", "password": "p"},
        )
        self.assertEqual(response["statusCode"], 400)
        body = json.loads(response["body"])
        self.assertEqual(body["error"], "invalid order request")

    def test_insufficient_inventory_returns_409(self):
        with mock.patch("src.order_service.create_order_in_rds") as create_order_in_rds:
            create_order_in_rds.side_effect = InsufficientInventoryError("SKU-1002", 99, 8)
            response = order_service.create_order_from_event(
                {
                    "body": json.dumps({
                        "customer": "Student Store",
                        "lines": [{"sku": "SKU-1002", "quantity": 99}]
                    })
                },
                {"host": "db", "port": 5432, "dbname": "tinywms", "user": "u", "password": "p"},
            )
        self.assertEqual(response["statusCode"], 409)
        body = json.loads(response["body"])
        self.assertEqual(body["error"], "insufficient inventory")
        self.assertEqual(body["available"], 8)


if __name__ == "__main__":
    unittest.main()
