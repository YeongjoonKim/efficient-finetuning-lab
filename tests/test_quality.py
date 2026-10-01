"""품질 검사 자체가 실제 오류를 거부하는지 검사한다."""
from pathlib import Path
import tempfile
import unittest
from scripts.check_repository import inspect_file, secret_rules, png_rules


class QualityTests(unittest.TestCase):
    def test_png_requires_valid_structure(self):
        self.assertIn("invalid-png", png_rules(b"not an image"))
        self.assertIn("invalid-png-structure", png_rules(b"\x89PNG\r\n\x1a\n"))

    def test_png_rejects_text_metadata(self):
        import struct
        import zlib
        data = b"hidden text"
        chunk = b"tEXt" + data
        png = b"\x89PNG\r\n\x1a\n" + struct.pack(">I", len(data)) + chunk + struct.pack(">I", zlib.crc32(chunk))
        self.assertIn("unexpected-png-chunk", png_rules(png))

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
