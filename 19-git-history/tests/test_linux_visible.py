import io
import os
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

from src import linux_visible


class LinuxVisibleTests(unittest.TestCase):
    def test_env_prints_visible_environment_value(self):
        stdout = io.StringIO()
        with mock.patch.dict(os.environ, {'TINYWMS_DEMO': 'hello'}, clear=True), redirect_stdout(stdout):
            exit_code = linux_visible.main(['linux_visible.py', 'env'])
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue().strip(), 'hello')

    def test_echo_reads_stdin_when_available(self):
        stdout = io.StringIO()
        with mock.patch('sys.stdin', io.StringIO('from-stdin\n')), redirect_stdout(stdout):
            exit_code = linux_visible.main(['linux_visible.py', 'echo'])
        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue().strip(), 'from-stdin')

    def test_fail_writes_stderr_and_nonzero_exit(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = linux_visible.main(['linux_visible.py', 'fail'])
        self.assertEqual(exit_code, 3)
        self.assertEqual(stdout.getvalue(), '')
        self.assertIn('intentional failure for exit-code practice', stderr.getvalue())

    def test_unknown_command_reports_usage_problem(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = linux_visible.main(['linux_visible.py', 'nope'])
        self.assertEqual(exit_code, 2)
        self.assertIn('Unknown command: nope', stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
