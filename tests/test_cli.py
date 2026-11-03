"""End-to-end tests for the commands and the saved data."""

import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from daylist.cli import main


class DaylistTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.data_file = Path(self.temp.name) / "tasks.json"

    def run_command(self, *args: str) -> tuple[int, str, str]:
        output, errors = StringIO(), StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            status = main(["--file", str(self.data_file), *args])
        return status, output.getvalue(), errors.getvalue()

    def test_add_list_complete_and_remove(self) -> None:
        self.assertEqual(self.run_command("add", "Pay rent", "--due", "2026-11-05")[0], 0)
        self.assertEqual(self.run_command("add", "Read a book")[0], 0)
        self.assertIn("#1 Pay rent (due 2026-11-05)", self.run_command("list")[1])
        self.assertEqual(self.run_command("done", "1")[0], 0)
        self.assertNotIn("Pay rent", self.run_command("list")[1])
        self.assertIn("[x] #1 Pay rent", self.run_command("list", "--all")[1])
        self.assertEqual(self.run_command("remove", "2")[0], 0)
        self.assertEqual([task["id"] for task in json.loads(self.data_file.read_text())], [1])

    def test_missing_task_does_not_change_data(self) -> None:
        self.run_command("add", "Keep this")
        original = self.data_file.read_text()
        status, _, error = self.run_command("done", "99")
        self.assertEqual(status, 1)
        self.assertIn("does not exist", error)
        self.assertEqual(self.data_file.read_text(), original)

    def test_invalid_data_is_reported(self) -> None:
        self.data_file.write_text("not JSON")
        status, _, error = self.run_command("list")
        self.assertEqual(status, 1)
        self.assertIn("Could not read", error)


if __name__ == "__main__":
    unittest.main()
