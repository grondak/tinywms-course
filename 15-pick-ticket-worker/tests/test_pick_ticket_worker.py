import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from src import pick_ticket_worker


class PickTicketWorkerTests(unittest.TestCase):
    def sample_lookup(self):
        return {
            "SKU-1001": {"description": "Blue widget", "bin": "A1-01"},
            "SKU-1003": {"description": "Packing tape", "bin": "B2-04"},
        }

    def sample_message(self):
        return {
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

    def test_process_pick_work_message_appends_ticket_to_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "pick-tickets.txt"
            stdout_buffer = io.StringIO()
            with redirect_stdout(stdout_buffer):
                pick_ticket_worker.process_pick_work_message(self.sample_message(), self.sample_lookup(), output_path)

            text = output_path.read_text(encoding="utf-8")
            self.assertIn("Order ID: 42", text)
            self.assertIn("SKU-1001 | Blue widget | qty 2 | bin A1-01", text)
            self.assertIn("wrote pick ticket orderId=42", stdout_buffer.getvalue())

    def test_process_sqs_message_acknowledges_after_success(self):
        sqs_message = {
            "MessageId": "abc-123",
            "ReceiptHandle": "handle-1",
            "Body": '{"orderId": 42, "customer": "Example School Store", "createdAt": "2026-01-15T10:30:00Z", "lines": [{"lineNumber": 1, "sku": "SKU-1001", "quantity": 2}]}'
        }
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "pick-tickets.txt"
            stdout_buffer = io.StringIO()
            with mock.patch("src.pick_ticket_worker.delete_message") as delete_message, redirect_stdout(stdout_buffer):
                ok = pick_ticket_worker.process_sqs_message(sqs_message, self.sample_lookup(), output_path, ack=True)

        self.assertTrue(ok)
        delete_message.assert_called_once_with("handle-1")
        output = stdout_buffer.getvalue()
        self.assertIn("received messageId=abc-123", output)
        self.assertIn("acknowledged messageId=abc-123", output)

    def test_process_sqs_message_leaves_failed_message_unacked(self):
        sqs_message = {
            "MessageId": "bad-1",
            "ReceiptHandle": "handle-1",
            "Body": 'not-json'
        }
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "pick-tickets.txt"
            stderr_buffer = io.StringIO()
            with mock.patch("src.pick_ticket_worker.delete_message") as delete_message, redirect_stderr(stderr_buffer):
                ok = pick_ticket_worker.process_sqs_message(sqs_message, self.sample_lookup(), output_path, ack=True)

        self.assertFalse(ok)
        delete_message.assert_not_called()
        self.assertIn("failed messageId=bad-1", stderr_buffer.getvalue())

    def test_run_once_from_file_processes_local_example(self):
        with tempfile.TemporaryDirectory() as tmp:
            message_path = Path(tmp) / "message.json"
            output_path = Path(tmp) / "pick-tickets.txt"
            message_path.write_text(
                '{"orderId": 42, "customer": "Example School Store", "createdAt": "2026-01-15T10:30:00Z", "lines": [{"lineNumber": 1, "sku": "SKU-1001", "quantity": 2}]}',
                encoding="utf-8",
            )

            code = pick_ticket_worker.run_once_from_file(message_path, self.sample_lookup(), output_path)

            self.assertEqual(code, 0)
            self.assertIn("Order ID: 42", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
