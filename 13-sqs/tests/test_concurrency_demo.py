import tempfile
import unittest
from pathlib import Path

from src import concurrency_demo


class ConcurrencyDemoTests(unittest.TestCase):
    def test_naive_demo_oversells_last_unit(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "tinywms.sqlite")
            concurrency_demo.setup_demo_db(db_path, quantity=1)
            result = concurrency_demo.run_naive_demo(db_path)

        self.assertEqual(result["mode"], "naive")
        self.assertEqual(result["orderCount"], 2)
        self.assertEqual(result["remainingQuantity"], 0)
        self.assertEqual([item["status"] for item in result["results"]], ["created", "created"])

    def test_fixed_demo_allows_only_one_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "tinywms.sqlite")
            concurrency_demo.setup_demo_db(db_path, quantity=1)
            result = concurrency_demo.run_fixed_demo(db_path)

        self.assertEqual(result["mode"], "fixed")
        self.assertEqual(result["orderCount"], 1)
        self.assertEqual(result["remainingQuantity"], 0)
        statuses = sorted(item["status"] for item in result["results"])
        self.assertEqual(statuses, ["created", "failed"])


if __name__ == "__main__":
    unittest.main()
