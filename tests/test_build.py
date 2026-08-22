#!/usr/bin/env python3
"""Unit tests for scripts/build.py."""

import unittest
from pathlib import Path
import tempfile
import shutil
import sys
import os

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from build import expand_includes, compile_targets, deploy  # noqa: E402


class TestBuild(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_dir = Path(self.temp_dir.name)
        self.shared_dir = self.root_dir / "shared"
        self.shared_dir.mkdir(parents=True, exist_ok=True)

        # Create sample shared file
        self.identity_file = self.shared_dir / "identity.md"
        self.identity_file.write_text("# Identity\nName: White Hunag\n", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_expand_includes_success(self):
        template = "# Header\n<!-- INCLUDE:shared/identity.md -->\nFooter"
        result = expand_includes(template, self.root_dir)
        expected = "# Header\n# Identity\nName: White Hunag\nFooter"
        self.assertEqual(result.strip(), expected.strip())

    def test_expand_includes_file_not_found(self):
        template = "<!-- INCLUDE:shared/missing.md -->"
        with self.assertRaises(FileNotFoundError):
            expand_includes(template, self.root_dir)

    def test_compile_and_deploy_dry_run(self):
        src_file = self.root_dir / "sample.txt"
        src_file.write_text("Hello", encoding="utf-8")
        dest_dir = self.root_dir / "deployed"
        dest_file = dest_dir / "sample.txt"

        files_to_deploy = [(src_file, dest_file)]
        actions = deploy(files_to_deploy, dry_run=True, backup=False)

        self.assertEqual(len(actions), 1)
        self.assertFalse(dest_file.exists())

    def test_compile_and_deploy_with_backup(self):
        src_file = self.root_dir / "sample.txt"
        src_file.write_text("New content", encoding="utf-8")

        dest_dir = self.root_dir / "deployed"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / "sample.txt"
        dest_file.write_text("Old content", encoding="utf-8")

        files_to_deploy = [(src_file, dest_file)]
        actions = deploy(files_to_deploy, dry_run=False, backup=True)

        self.assertTrue(dest_file.exists())
        self.assertEqual(dest_file.read_text(encoding="utf-8"), "New content")
        backup_file = dest_dir / "sample.txt.bak"
        self.assertTrue(backup_file.exists())
        self.assertEqual(backup_file.read_text(encoding="utf-8"), "Old content")


if __name__ == "__main__":
    unittest.main()
