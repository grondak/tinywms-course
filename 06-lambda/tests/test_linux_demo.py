import io
import unittest
from contextlib import redirect_stdout, redirect_stderr

from src import linux_demo


class LinuxDemoTests(unittest.TestCase):
    def test_stdout_mode(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = linux_demo.main(["linux_demo.py", "stdout"])
        self.assertEqual(code, 0)
        self.assertIn("stdout is visible", buffer.getvalue())

    def test_stderr_mode(self):
        buffer = io.StringIO()
        with redirect_stderr(buffer):
            code = linux_demo.main(["linux_demo.py", "stderr"])
        self.assertEqual(code, 0)
        self.assertIn("stderr is visible", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
