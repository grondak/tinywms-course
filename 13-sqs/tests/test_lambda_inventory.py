import json
import os
import unittest
from unittest import mock

from src import lambda_inventory


class LambdaInventoryTests(unittest.TestCase):
    def test_handler_returns_inventory(self):
        with mock.patch.dict(os.environ, {
            "TINYWMS_DB_HOST": "db.example",
            "TINYWMS_DB_PORT": "5432",
            "TINYWMS_DB_NAME": "tinywms",
            "TINYWMS_DB_USER": "tinywms",
            "TINYWMS_DB_PASSWORD": "secret",
        }), mock.patch("src.lambda_inventory.inventory_json_from_rds") as inventory_json_from_rds:
            inventory_json_from_rds.return_value = {
                "inventory": [
                    {
                        "sku": "SKU-1001",
                        "description": "Blue widget",
                        "bin": "A1-01",
                        "quantity": 24,
                        "unit": "each",
                    }
                ]
            }
            response = lambda_inventory.handler({"httpMethod": "GET", "path": "/inventory"}, None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["inventory"][0]["sku"], "SKU-1001")

    def test_handler_creates_order(self):
        event = {
            "httpMethod": "POST",
            "path": "/orders",
            "body": json.dumps({
                "customer": "Example School Store",
                "lines": [{"sku": "SKU-1001", "quantity": 2}]
            })
        }
        with mock.patch.dict(os.environ, {
            "TINYWMS_DB_HOST": "db.example",
            "TINYWMS_DB_PORT": "5432",
            "TINYWMS_DB_NAME": "tinywms",
            "TINYWMS_DB_USER": "tinywms",
            "TINYWMS_DB_PASSWORD": "secret",
        }), mock.patch("src.order_service.create_order_in_rds") as create_order_in_rds:
            create_order_in_rds.return_value = {
                "orderId": 7,
                "customer": "Example School Store",
                "status": "created",
                "lines": [{"sku": "SKU-1001", "quantity": 2}]
            }
            response = lambda_inventory.handler(event, None)
        self.assertEqual(response["statusCode"], 201)
        body = json.loads(response["body"])
        self.assertEqual(body["orderId"], 7)
        self.assertEqual(body["status"], "created")

    def test_handler_rejects_wrong_route(self):
        response = lambda_inventory.handler({"httpMethod": "GET", "path": "/nope"}, None)
        self.assertEqual(response["statusCode"], 404)
        body = json.loads(response["body"])
        self.assertEqual(body["error"], "not found")

    def test_handler_reports_missing_config(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            response = lambda_inventory.handler({"httpMethod": "GET", "path": "/inventory"}, None)
        self.assertEqual(response["statusCode"], 500)
        body = json.loads(response["body"])
        self.assertEqual(body["error"], "missing database configuration")


if __name__ == "__main__":
    unittest.main()
