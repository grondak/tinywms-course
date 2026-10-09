import json
import unittest

from src import lambda_inventory


class LambdaInventoryTests(unittest.TestCase):
    def test_handler_returns_inventory(self):
        response = lambda_inventory.handler({"httpMethod": "GET", "path": "/inventory"}, None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["inventory"][0]["sku"], "SKU-1001")

    def test_handler_rejects_wrong_route(self):
        response = lambda_inventory.handler({"httpMethod": "GET", "path": "/nope"}, None)
        self.assertEqual(response["statusCode"], 404)
        body = json.loads(response["body"])
        self.assertEqual(body["error"], "not found")


if __name__ == "__main__":
    unittest.main()
