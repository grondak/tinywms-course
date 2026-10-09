import unittest

from src import pick_ticket


class PickTicketTests(unittest.TestCase):
    def test_build_pick_ticket_text_contains_human_readable_lines(self):
        message = {
            "messageType": "PickWorkRequested",
            "version": 1,
            "orderId": 42,
            "customer": "Example School Store",
            "createdAt": "2026-01-15T10:30:00Z",
            "lines": [
                {"lineNumber": 1, "sku": "SKU-1001", "quantity": 2},
                {"lineNumber": 2, "sku": "SKU-1003", "quantity": 1},
            ],
        }
        lookup = {
            "SKU-1001": {"description": "Blue widget", "bin": "A1-01"},
            "SKU-1003": {"description": "Packing tape", "bin": "B2-04"},
        }

        text = pick_ticket.build_pick_ticket_text(message, lookup)

        self.assertIn("=== TinyWMS Pick Ticket ===", text)
        self.assertIn("Order ID: 42", text)
        self.assertIn("Customer: Example School Store", text)
        self.assertIn("1. SKU-1001 | Blue widget | qty 2 | bin A1-01", text)
        self.assertIn("2. SKU-1003 | Packing tape | qty 1 | bin B2-04", text)

    def test_build_pick_ticket_text_marks_unknown_sku(self):
        message = {
            "orderId": 7,
            "customer": "Example School Store",
            "createdAt": "2026-01-15T10:30:00Z",
            "lines": [{"lineNumber": 1, "sku": "SKU-MISSING", "quantity": 1}],
        }

        text = pick_ticket.build_pick_ticket_text(message, {})

        self.assertIn("UNKNOWN SKU", text)
        self.assertIn("UNKNOWN BIN", text)


if __name__ == "__main__":
    unittest.main()
