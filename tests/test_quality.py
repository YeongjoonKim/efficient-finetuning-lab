"""품질 검사 자체가 실제 오류를 거부하는지 검사한다."""
from pathlib import Path
import tempfile
import unittest
from scripts.check_repository import inspect_file, secret_rules


class QualityTests(unittest.TestCase):
    def test_private_key_marker_detected(self):
        marker = "-----BEGIN " + "PRIVATE KEY-----"
        self.assertIn("private-key", secret_rules(marker))

    def test_broken_link_and_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "README.md"
            path.write_text("[missing](missing.md)\n[escape](../outside.md)\n")
            self.assertEqual(inspect_file(root, path).count("broken-local-link"), 2)

    def test_valid_link(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "README.md"
            path.write_text("[self](README.md)\n")
            self.assertEqual(inspect_file(root, path), [])

    def test_bad_python_and_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, value, rule in [("bad.py", "def (", "python-syntax"),
                                      ("bad.json", "{", "json-syntax")]:
                path = root / name
                path.write_text(value)
                self.assertIn(rule, inspect_file(root, path))

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "link.md"
            path.symlink_to(root / "missing")
            self.assertEqual(inspect_file(root, path), ["symlink"])
