import unittest
from pathlib import Path


class EndToEndDocTests(unittest.TestCase):
    def test_end_to_end_document_exists(self):
        self.assertTrue(Path("docs/end-to-end.md").exists())

    def test_end_to_end_document_mentions_required_final_components(self):
        text = Path("docs/end-to-end.md").read_text(encoding="utf-8")
        required_terms = [
            "Browser",
            "API Gateway",
            "Lambda",
            "RDS",
            "SQS",
            "EventBridge",
            "pick-tickets.txt",
            "PickWorkRequested",
            "OrderPlaced",
            "Mermaid",
        ]
        for term in required_terms:
            self.assertIn(term, text)

    def test_end_to_end_document_calls_out_linux_and_failure_visibility(self):
        text = Path("docs/end-to-end.md").read_text(encoding="utf-8")
        self.assertIn("Raspberry Pi/Linux connection", text)
        self.assertIn("Possible failure", text)
        self.assertIn("Responsible operator/provider", text)

    def test_end_to_end_document_includes_validation_commands(self):
        text = Path("docs/end-to-end.md").read_text(encoding="utf-8")
        self.assertIn("python3 -m unittest discover -s tests", text)
        self.assertIn("python3 src/demo_trace.py --order-file data/order-example.json", text)


if __name__ == "__main__":
    unittest.main()
