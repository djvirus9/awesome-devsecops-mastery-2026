"""Regular-file, bounded-read, and error-output behavior for the local CLI."""

import importlib.util
import io
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


CLI_PATH = Path(__file__).resolve().parents[1] / "samples/sample-cli/main.py"
SPEC = importlib.util.spec_from_file_location("sample_cli", CLI_PATH)
cli = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cli)


class SampleCliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "input.txt"

    def invoke(self, path=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
            status = cli.main(["--input", str(path or self.path)])
        return status, stdout.getvalue(), stderr.getvalue()

    def assert_input_error(self, fragment, path=None):
        status, stdout, stderr = self.invoke(path)
        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn(fragment, stderr)
        self.assertNotIn("Traceback", stderr)

    def test_utf8_text_preserves_original_strip_and_print_behavior(self):
        self.path.write_text("  Hello, नमस्ते\nsecond line  \n", encoding="utf-8")
        self.assertEqual(self.invoke(), (0, "Hello, नमस्ते\nsecond line\n", ""))

    def test_json_extension_does_not_change_plain_text_semantics(self):
        path = self.path.with_suffix(".json")
        path.write_text("  {this is ordinary text, not valid JSON}  ", encoding="utf-8")
        self.assertEqual(self.invoke(path), (0, "{this is ordinary text, not valid JSON}\n", ""))

    def test_empty_file_is_valid_text(self):
        self.path.write_bytes(b"")
        self.assertEqual(self.invoke(), (0, "\n", ""))

    def test_missing_file_is_reported_without_traceback(self):
        self.assert_input_error("does not exist")

    def test_directory_and_symlink_are_rejected(self):
        self.assert_input_error("regular file", Path(self.directory.name))
        self.path.write_text("text", encoding="utf-8")
        link = self.path.with_name("linked.txt")
        link.symlink_to(self.path)
        self.assert_input_error("regular file", link)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "Named pipes require a POSIX platform")
    def test_named_pipe_is_rejected_without_waiting_for_a_writer(self):
        os.mkfifo(self.path)
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "--input", str(self.path)],
            capture_output=True, text=True, timeout=3,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("regular file", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_permission_and_read_errors_are_concise(self):
        self.path.write_text("text", encoding="utf-8")
        with mock.patch.object(cli.os, "open", side_effect=PermissionError("private diagnostic")):
            self.assert_input_error("not readable")
        with mock.patch.object(cli.os, "open", side_effect=OSError("private diagnostic")):
            status, stdout, stderr = self.invoke()
        self.assertEqual((status, stdout), (1, ""))
        self.assertIn("could not be read", stderr)
        self.assertNotIn("private diagnostic", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_invalid_utf8_is_rejected_before_output(self):
        self.path.write_bytes(b"prefix\xffsuffix")
        self.assert_input_error("valid UTF-8")

    def test_exact_byte_limit_is_accepted(self):
        self.path.write_bytes(b"x" * cli.MAX_INPUT_BYTES)
        self.assertEqual(len(cli.read_input(self.path)), cli.MAX_INPUT_BYTES)

    def test_one_byte_over_limit_is_rejected(self):
        self.path.write_bytes(b"x" * (cli.MAX_INPUT_BYTES + 1))
        self.assert_input_error("1 MiB")

    def test_read_limit_still_applies_when_metadata_understates_size(self):
        self.path.write_bytes(b"x" * (cli.MAX_INPUT_BYTES + 1))
        small_file = SimpleNamespace(st_mode=stat.S_IFREG | 0o600, st_size=0)
        with mock.patch.object(Path, "lstat", return_value=small_file), mock.patch.object(
            cli.os, "fstat", return_value=small_file
        ):
            self.assert_input_error("1 MiB")

    def test_opened_descriptor_must_still_be_regular(self):
        self.path.write_text("text", encoding="utf-8")
        special_file = SimpleNamespace(st_mode=stat.S_IFIFO, st_size=0)
        with mock.patch.object(cli.os, "fstat", return_value=special_file):
            self.assert_input_error("regular file")

    def test_missing_required_argument_keeps_usage_exit_status(self):
        result = subprocess.run([sys.executable, str(CLI_PATH)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--input", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
