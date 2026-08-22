#!/usr/bin/env python3
"""Unit tests for scripts/fetch_skills.py."""

import unittest
from pathlib import Path
import tempfile
import json
import sys
from unittest.mock import patch, MagicMock

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from fetch_skills import load_manifest, fetch_skill, fetch_all_skills  # noqa: E402


class TestFetchSkills(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_dir = Path(self.temp_dir.name)
        self.manifest_file = self.root_dir / "manifest.json"

        self.sample_manifest = {
            "skills": [
                {
                    "name": "test-skill",
                    "description": "Test skill description",
                    "source": "https://example.com/test/SKILL.md",
                    "destination": "skills/third-party/test-skill/SKILL.md",
                    "enabled": True,
                },
                {
                    "name": "disabled-skill",
                    "description": "Disabled skill description",
                    "source": "https://example.com/disabled/SKILL.md",
                    "destination": "skills/third-party/disabled-skill/SKILL.md",
                    "enabled": False,
                },
            ]
        }
        self.manifest_file.write_text(json.dumps(self.sample_manifest), encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_manifest(self):
        skills = load_manifest(self.manifest_file)
        self.assertEqual(len(skills), 2)
        self.assertEqual(skills[0]["name"], "test-skill")

    @patch("fetch_skills.urllib.request.urlopen")
    def test_fetch_skill_remote_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"# Downloaded Content\n"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        skill = self.sample_manifest["skills"][0]
        success = fetch_skill(skill, self.root_dir)

        self.assertTrue(success)
        dest_path = self.root_dir / skill["destination"]
        self.assertTrue(dest_path.exists())
        self.assertEqual(dest_path.read_text(encoding="utf-8"), "# Downloaded Content\n")

    def test_fetch_all_skills_respects_enabled(self):
        with patch("fetch_skills.fetch_skill") as mock_fetch:
            mock_fetch.return_value = True
            count = fetch_all_skills(self.sample_manifest["skills"], self.root_dir, force=False)
            self.assertEqual(count, 1)
            mock_fetch.assert_called_once_with(self.sample_manifest["skills"][0], self.root_dir)


if __name__ == "__main__":
    unittest.main()
