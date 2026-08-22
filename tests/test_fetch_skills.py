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

from fetch_skills import (  # noqa: E402
    load_manifest,
    normalize_skill,
    resolve_source_and_name,
    fetch_skill,
    fetch_all_skills,
    add_skill,
)


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

    def test_normalize_skill_defaults(self):
        raw_skill = {
            "name": "minimal-skill",
            "source": "https://example.com/SKILL.md",
        }
        normalized = normalize_skill(raw_skill)
        self.assertEqual(normalized["name"], "minimal-skill")
        self.assertEqual(normalized["destination"], "skills/third-party/minimal-skill/SKILL.md")
        self.assertTrue(normalized["enabled"])

    def test_resolve_source_at_syntax(self):
        url, name = resolve_source_and_name("vercel-labs/agent-skills@find-skills")
        self.assertEqual(name, "find-skills")
        self.assertEqual(
            url,
            "https://raw.githubusercontent.com/vercel-labs/agent-skills/main/skills/find-skills/SKILL.md",
        )

    def test_resolve_source_flag_syntax(self):
        url, name = resolve_source_and_name("https://github.com/vercel-labs/skills --skill find-skills")
        self.assertEqual(name, "find-skills")
        self.assertEqual(
            url,
            "https://raw.githubusercontent.com/vercel-labs/skills/main/skills/find-skills/SKILL.md",
        )

    def test_resolve_source_github_blob_url(self):
        url, name = resolve_source_and_name("https://github.com/owner/repo/blob/main/skills/custom-skill/SKILL.md")
        self.assertEqual(name, "custom-skill")
        self.assertEqual(
            url,
            "https://raw.githubusercontent.com/owner/repo/main/skills/custom-skill/SKILL.md",
        )

    def test_resolve_source_github_tree_url(self):
        url, name = resolve_source_and_name("https://github.com/owner/repo/tree/main/skills/custom-skill")
        self.assertEqual(name, "custom-skill")
        self.assertEqual(
            url,
            "https://raw.githubusercontent.com/owner/repo/main/skills/custom-skill/SKILL.md",
        )

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

    @patch("fetch_skills.urllib.request.urlopen")
    def test_add_skill_updates_manifest_and_downloads(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"# Find Skills Content\n"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        success = add_skill(
            manifest_path=self.manifest_file,
            source="vercel-labs/agent-skills@find-skills",
            root_dir=self.root_dir,
        )
        self.assertTrue(success)

        # 驗證 manifest.json 已新增
        updated_skills = load_manifest(self.manifest_file)
        self.assertEqual(len(updated_skills), 3)
        added = [s for s in updated_skills if s["name"] == "find-skills"][0]
        self.assertEqual(added["name"], "find-skills")
        self.assertEqual(normalize_skill(added)["destination"], "skills/third-party/find-skills/SKILL.md")

        # 驗證檔案已下載
        saved_file = self.root_dir / "skills/third-party/find-skills/SKILL.md"
        self.assertTrue(saved_file.exists())
        self.assertEqual(saved_file.read_text(encoding="utf-8"), "# Find Skills Content\n")


if __name__ == "__main__":
    unittest.main()
