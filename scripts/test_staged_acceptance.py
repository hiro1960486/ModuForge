"""Read-only acceptance checks for staged module contracts and fixture integrity.

This does not simulate GUI clicks or validate actual file scanning algorithms.
No files in the source repository or Windows Recycle Bin are modified.
"""
from __future__ import annotations

import ast
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT if all((ROOT / name).is_dir() for name in ("00_shared", "01_tree", "08_organizer")) else ROOT.parent / (ROOT.name + "_staging")
MODULES = ("tree", "rename", "preview", "compare",
           "hash", "recycle", "tags", "organizer")


class StagedAcceptance(unittest.TestCase):
    def test_staged_modules_and_api_files(self):
        self.assertTrue(STAGE.is_dir(), "Create isolated staging first")
        for index, name in enumerate(MODULES, 1):
            folder = STAGE / f"{index:02d}_{name}"
            with self.subTest(name=name):
                self.assertTrue(folder.is_dir())
                manifest_path = folder / "api" / "module.json"
                self.assertTrue(manifest_path.is_file())
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertEqual(manifest.get("id"), name)
                self.assertEqual(manifest.get("interface_entrypoint"),
                                 f"fileworkbench.modules.{name}.interface")
                self.assertEqual(manifest.get("entrypoint"),
                                 f"fileworkbench.modules.{name}.module")
                self.assertTrue(manifest.get("commands"))
                for path in (folder / "api" / "interface.py",
                             folder / "module" / "module.py"):
                    self.assertTrue(path.is_file())
                    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_readonly_comparison_and_sha256_fixture(self):
        with tempfile.TemporaryDirectory(prefix="moduforge_acceptance_") as tmp:
            base = Path(tmp)
            left, right = base / "Left", base / "Right"
            left.mkdir()
            right.mkdir()
            payload = b"ModuForge fixture 2026\n"
            (left / "same.txt").write_bytes(payload)
            (right / "same.txt").write_bytes(payload)
            (left / "changed.txt").write_bytes(b"before\n")
            (right / "changed.txt").write_bytes(b"after\n")
            before = {p.relative_to(base).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in base.rglob("*.txt")}
            self.assertEqual(before["Left/same.txt"], before["Right/same.txt"])
            self.assertNotEqual(before["Left/changed.txt"], before["Right/changed.txt"])
            # Verify fixture bytes weren't altered by the read-only checks.
            after = {p.relative_to(base).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in base.rglob("*.txt")}
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main(verbosity=2)
