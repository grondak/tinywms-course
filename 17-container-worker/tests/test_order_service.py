import json
import os
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

    def test_success_publishes_pick_work_when_queue_url_is_set(self):
        order_result = {
            "orderId": 7,
            "customer": "Example School Store",
            "status": "created",
            "lines": [{"sku": "SKU-1001", "quantity": 2}]
        }
        with mock.patch("src.order_service.create_order_in_rds", return_value=order_result), \
             mock.patch("src.order_service.publish_json_message") as publish_json_message, \
             mock.patch.dict(os.environ, {"TINYWMS_SQS_QUEUE_URL": "https://example.com/queue"}, clear=False):
            response = order_service.create_order_from_event(
                {
                    "body": json.dumps({
                        "customer": "Example School Store",
                        "lines": [{"sku": "SKU-1001", "quantity": 2}]
                    })
                },
                {"host": "db", "port": 5432, "dbname": "tinywms", "user": "u", "password": "p"},
            )
        self.assertEqual(response["statusCode"], 201)
        publish_json_message.assert_called_once()
        args = publish_json_message.call_args[0]
        self.assertEqual(args[0], "https://example.com/queue")
        self.assertEqual(args[1]["messageType"], "PickWorkRequested")
        self.assertEqual(args[1]["orderId"], 7)

    def test_success_publishes_order_placed_event_when_bus_name_is_set(self):
        order_result = {
            "orderId": 11,
            "customer": "Example School Store",
            "status": "created",
            "lines": [{"sku": "SKU-1001", "quantity": 2}]
        }
        with mock.patch("src.order_service.create_order_in_rds", return_value=order_result), \
             mock.patch("src.order_service.publish_order_event") as publish_order_event, \
             mock.patch.dict(os.environ, {"TINYWMS_EVENT_BUS_NAME": "default"}, clear=False):
            response = order_service.create_order_from_event(
                {
                    "body": json.dumps({
                        "customer": "Example School Store",
                        "lines": [{"sku": "SKU-1001", "quantity": 2}]
                    })
                },
                {"host": "db", "port": 5432, "dbname": "tinywms", "user": "u", "password": "p"},
            )
        self.assertEqual(response["statusCode"], 201)
        publish_order_event.assert_called_once()
        args = publish_order_event.call_args[0]
        self.assertEqual(args[0]["eventType"], "OrderPlaced")
        self.assertEqual(args[0]["orderId"], 11)
        self.assertEqual(args[1], "default")

    def test_success_can_publish_both_command_and_event(self):
        order_result = {
            "orderId": 12,
            "customer": "Example School Store",
            "status": "created",
            "lines": [{"sku": "SKU-1001", "quantity": 1}]
        }
        with mock.patch("src.order_service.create_order_in_rds", return_value=order_result), \
             mock.patch("src.order_service.publish_json_message") as publish_json_message, \
             mock.patch("src.order_service.publish_order_event") as publish_order_event, \
             mock.patch.dict(os.environ, {
                 "TINYWMS_SQS_QUEUE_URL": "https://example.com/queue",
                 "TINYWMS_EVENT_BUS_NAME": "default"
             }, clear=False):
            response = order_service.create_order_from_event(
                {
                    "body": json.dumps({
                        "customer": "Example School Store",
                        "lines": [{"sku": "SKU-1001", "quantity": 1}]
                    })
                },
                {"host": "db", "port": 5432, "dbname": "tinywms", "user": "u", "password": "p"},
            )
        self.assertEqual(response["statusCode"], 201)
        publish_json_message.assert_called_once()
        publish_order_event.assert_called_once()

    def test_success_without_queue_or_event_bus_keeps_existing_response(self):
        order_result = {
            "orderId": 9,
            "customer": "Example School Store",
            "status": "created",
            "lines": [{"sku": "SKU-1001", "quantity": 1}]
        }
        with mock.patch("src.order_service.create_order_in_rds", return_value=order_result), \
             mock.patch("src.order_service.publish_json_message") as publish_json_message, \
             mock.patch("src.order_service.publish_order_event") as publish_order_event, \
             mock.patch.dict(os.environ, {}, clear=True):
            response = order_service.create_order_from_event(
                {
                    "body": json.dumps({
                        "customer": "Example School Store",
                        "lines": [{"sku": "SKU-1001", "quantity": 1}]
                    })
                },
                {"host": "db", "port": 5432, "dbname": "tinywms", "user": "u", "password": "p"},
            )
        self.assertEqual(response["statusCode"], 201)
        publish_json_message.assert_not_called()
        publish_order_event.assert_not_called()


if __name__ == "__main__":
    unittest.main()
