import unittest
from pathlib import Path


class GitMilestonesDocTests(unittest.TestCase):
    def test_milestone_document_exists(self):
        self.assertTrue(Path("docs/git-milestones.md").exists())

    def test_milestone_document_mentions_required_major_checkpoints(self):
        text = Path("docs/git-milestones.md").read_text(encoding="utf-8")
        required_tags = [
            "lesson-01-json-cli",
            "lesson-03-pi-http",
            "lesson-05-ec2-http",
            "lesson-04-browser",
            "lesson-06-lambda",
            "lesson-07-api-gateway",
            "lesson-08-relational-db",
            "lesson-09-rds",
            "lesson-12-transactional-orders",
            "lesson-14-queue-event",
            "lesson-15-pick-ticket-worker",
            "lesson-17-container-worker",
            "lesson-18-aws-deployment",
        ]
        for tag in required_tags:
            self.assertIn(tag, text)

    def test_milestone_document_includes_checkout_and_verification_commands(self):
        text = Path("docs/git-milestones.md").read_text(encoding="utf-8")
        self.assertIn("git checkout lesson-01-json-cli", text)
        self.assertIn("git switch --detach lesson-01-json-cli", text)
        self.assertIn("python3 src/inventory_cli.py list data/inventory.json", text)
        self.assertIn("TINYWMS_PORT=8000 python3 src/http_server.py data/inventory.json", text)


if __name__ == "__main__":
    unittest.main()
