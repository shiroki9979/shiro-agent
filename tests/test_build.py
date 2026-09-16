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

from build import expand_includes, compile_targets, compile_skills, deploy, DEFAULT_DEPLOY_PATHS  # noqa: E402


class TestBuild(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_dir = Path(self.temp_dir.name)
        self.shared_dir = self.root_dir / "shared"
        self.shared_dir.mkdir(parents=True, exist_ok=True)

        # Create sample shared file
        self.identity_file = self.shared_dir / "identity.md"
        self.identity_file.write_text("# Identity\nName: White Hunag\n", encoding="utf-8")
        self.coding_style_file = self.shared_dir / "coding-style.md"
        self.coding_style_file.write_text("# Coding Style\nKeep it simple.\n", encoding="utf-8")

        self.codex_config_dir = self.root_dir / "configs" / "codex"
        self.codex_config_dir.mkdir(parents=True, exist_ok=True)
        (self.codex_config_dir / "AGENTS.md").write_text(
            "# Rules\n\n<!-- INCLUDE:shared/identity.md -->\n\n<!-- INCLUDE:shared/coding-style.md -->\n",
            encoding="utf-8",
        )

        # Create sample custom skills in custom-skills/
        self.custom_skill_dir = self.root_dir / "custom-skills" / "custom-skill"
        self.custom_skill_dir.mkdir(parents=True, exist_ok=True)
        (self.custom_skill_dir / "SKILL.md").write_text("# Custom Skill\n<!-- INCLUDE:shared/identity.md -->", encoding="utf-8")

        # Create sample third-party skills in .agents/skills/
        self.third_party_skill_dir = self.root_dir / ".agents" / "skills" / "vendor-skill"
        self.third_party_skill_dir.mkdir(parents=True, exist_ok=True)
        (self.third_party_skill_dir / "SKILL.md").write_text("# Vendor Skill", encoding="utf-8")

        # Create sample skills-lock.json
        self.lock_file = self.root_dir / "skills-lock.json"
        self.lock_file.write_text('{"version": 1, "skills": {}}', encoding="utf-8")

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

    def test_compile_skills_aggregates_custom_and_third_party(self):
        out_dir = self.root_dir / "dist"
        pairs = compile_skills(self.root_dir, out_dir)

        # 驗證 custom skill 展開與多平台派發輸出
        custom_dest = out_dir / ".agents" / "skills" / "custom-skill" / "SKILL.md"
        self.assertTrue(custom_dest.exists())
        self.assertEqual(custom_dest.read_text(encoding="utf-8").strip(), "# Custom Skill\n# Identity\nName: White Hunag")

        for key in ["agents", "antigravity", "claude"]:
            deploy_target = DEFAULT_DEPLOY_PATHS[key] / "skills" / "custom-skill" / "SKILL.md"
            self.assertIn((custom_dest, deploy_target), pairs)
        cursor_deploy_target = DEFAULT_DEPLOY_PATHS["cursor"] / "skills" / "custom-skill" / "SKILL.md"
        self.assertNotIn((custom_dest, cursor_deploy_target), pairs)
        self.assertFalse(any(DEFAULT_DEPLOY_PATHS["codex"] in dest.parents for _, dest in pairs))

        # 驗證 third-party skill 多平台派發輸出
        vendor_dest = out_dir / ".agents" / "skills" / "vendor-skill" / "SKILL.md"
        self.assertTrue(vendor_dest.exists())
        self.assertEqual(vendor_dest.read_text(encoding="utf-8"), "# Vendor Skill")

        for key in ["agents", "antigravity", "claude"]:
            deploy_target = DEFAULT_DEPLOY_PATHS[key] / "skills" / "vendor-skill" / "SKILL.md"
            self.assertIn((vendor_dest, deploy_target), pairs)
        cursor_deploy_target = DEFAULT_DEPLOY_PATHS["cursor"] / "skills" / "vendor-skill" / "SKILL.md"
        self.assertNotIn((vendor_dest, cursor_deploy_target), pairs)

        # 驗證 skills-lock.json 輸出
        expected_lock_dest = out_dir / ".agents" / "skills-lock.json"
        expected_lock_deploy = DEFAULT_DEPLOY_PATHS["agents"] / "skills-lock.json"
        self.assertTrue(expected_lock_dest.exists())
        self.assertIn((expected_lock_dest, expected_lock_deploy), pairs)

    def test_compile_skills_collision_error(self):
        # 建立同名衝突技能
        conflict_dir = self.root_dir / "custom-skills" / "vendor-skill"
        conflict_dir.mkdir(parents=True, exist_ok=True)
        (conflict_dir / "SKILL.md").write_text("# Conflicting Custom Skill", encoding="utf-8")

        out_dir = self.root_dir / "dist"
        with self.assertRaises(ValueError) as ctx:
            compile_skills(self.root_dir, out_dir)
        self.assertIn("Skill name collision detected", str(ctx.exception))

    def test_compile_targets_all_includes_dot_agents_skills(self):
        out_dir = self.root_dir / "dist"
        pairs = compile_targets(["all"], self.root_dir, out_dir)

        # 驗證編譯配對中包含 .agents/skills
        skill_pairs = [p for p in pairs if ".agents/skills" in str(p[0])]
        self.assertTrue(len(skill_pairs) > 0)

        codex_instruction = out_dir / "codex" / "AGENTS.md"
        self.assertTrue(codex_instruction.exists())
        self.assertIn((codex_instruction, DEFAULT_DEPLOY_PATHS["codex"] / "AGENTS.md"), pairs)

    def test_compile_codex_instruction_to_codex_home(self):
        out_dir = self.root_dir / "dist"

        pairs = compile_targets(["codex"], self.root_dir, out_dir)

        codex_instruction = out_dir / "codex" / "AGENTS.md"
        self.assertEqual(
            codex_instruction.read_text(encoding="utf-8"),
            "# Rules\n\n# Identity\nName: White Hunag\n\n# Coding Style\nKeep it simple.\n",
        )
        self.assertEqual(pairs, [(codex_instruction, DEFAULT_DEPLOY_PATHS["codex"] / "AGENTS.md")])

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
