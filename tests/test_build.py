#!/usr/bin/env python3
"""Unit tests for scripts/build.py."""

import unittest
import json
from pathlib import Path
import tempfile
import shutil
import stat
import sys
import os
from unittest.mock import patch

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from build import expand_includes, compile_targets, compile_skills, deploy, DEFAULT_DEPLOY_PATHS  # noqa: E402


class TestBuild(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_dir = Path(self.temp_dir.name)
        deploy_paths = {key: self.root_dir / "home" / key for key in DEFAULT_DEPLOY_PATHS}
        self.deploy_paths_patch = patch.dict(DEFAULT_DEPLOY_PATHS, deploy_paths)
        self.deploy_paths_patch.start()
        self.addCleanup(self.deploy_paths_patch.stop)
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

    def test_rebuild_removes_deleted_skills_and_files_only_from_selected_target(self):
        reference = self.custom_skill_dir / "reference.md"
        reference.write_text("Old reference", encoding="utf-8")
        out_dir = self.root_dir / "dist"
        compile_targets(["all"], self.root_dir, out_dir)

        reference.unlink()
        shutil.rmtree(self.third_party_skill_dir)
        compile_targets(["skills"], self.root_dir, out_dir)

        skills_out = out_dir / ".agents" / "skills"
        self.assertFalse((skills_out / "vendor-skill").exists())
        self.assertFalse((skills_out / "custom-skill" / "reference.md").exists())
        self.assertTrue((skills_out / "custom-skill" / "SKILL.md").exists())
        self.assertTrue((out_dir / "codex" / "AGENTS.md").exists())

    def test_compile_codex_instruction_to_codex_home(self):
        out_dir = self.root_dir / "dist"

        pairs = compile_targets(["codex"], self.root_dir, out_dir)

        codex_instruction = out_dir / "codex" / "AGENTS.md"
        self.assertEqual(
            codex_instruction.read_text(encoding="utf-8"),
            "# Rules\n\n# Identity\nName: White Hunag\n\n# Coding Style\nKeep it simple.\n",
        )
        self.assertEqual(pairs, [(codex_instruction, DEFAULT_DEPLOY_PATHS["codex"] / "AGENTS.md")])

    def test_build_rejects_output_directory_overlapping_sources(self):
        repo_dir = self.root_dir / "repository"
        shutil.copytree(self.root_dir / ".agents", repo_dir / ".agents")
        for out_dir in [repo_dir, self.root_dir, repo_dir / ".agents" / "output"]:
            with self.subTest(out_dir=out_dir):
                with self.assertRaisesRegex(ValueError, "Output directory overlaps"):
                    compile_targets(["skills"], repo_dir, out_dir)

        skill_file = repo_dir / ".agents" / "skills" / "vendor-skill" / "SKILL.md"
        self.assertEqual(skill_file.read_text(), "# Vendor Skill")

    def test_build_rejects_symlinked_output_target(self):
        out_dir = self.root_dir / "dist"
        compile_targets(["skills"], self.root_dir, out_dir)
        external_out = self.root_dir / "external-output"
        (out_dir / ".agents").rename(external_out)
        (out_dir / ".agents").symlink_to(external_out, target_is_directory=True)

        with self.assertRaisesRegex(ValueError, "Symlink in managed path"):
            compile_targets(["skills"], self.root_dir, out_dir)

        self.assertEqual((external_out / "skills" / "vendor-skill" / "SKILL.md").read_text(), "# Vendor Skill")

    def test_compile_claude_deploys_only_instruction_file(self):
        # Claude Code 不讀取 ~/.claude/mcp_config.json；使用者層 MCP 僅存於 ~/.claude.json
        claude_config_dir = self.root_dir / "configs" / "claude"
        claude_config_dir.mkdir(parents=True, exist_ok=True)
        (claude_config_dir / "CLAUDE.md").write_text("# Rules\n\n<!-- INCLUDE:shared/identity.md -->\n", encoding="utf-8")
        (claude_config_dir / "mcp_config.json").write_text('{"mcpServers": {}}', encoding="utf-8")
        out_dir = self.root_dir / "dist"

        pairs = compile_targets(["claude"], self.root_dir, out_dir)

        claude_instruction = out_dir / "claude" / "CLAUDE.md"
        self.assertEqual(claude_instruction.read_text(encoding="utf-8"), "# Rules\n\n# Identity\nName: White Hunag\n")
        self.assertEqual(pairs, [(claude_instruction, DEFAULT_DEPLOY_PATHS["claude"] / "CLAUDE.md")])

    def test_compile_skills_rejects_claude_reserved_names(self):
        for reserved_name in ["synced", "Synced", "anthropic-skills-demo"]:
            with self.subTest(reserved_name=reserved_name):
                reserved_dir = self.root_dir / "custom-skills" / reserved_name
                reserved_dir.mkdir(parents=True, exist_ok=True)
                (reserved_dir / "SKILL.md").write_text("# Reserved", encoding="utf-8")

                with self.assertRaises(ValueError) as ctx:
                    compile_skills(self.root_dir, self.root_dir / "dist")
                self.assertIn(f"Skill name '{reserved_name}' is reserved by Claude Code", str(ctx.exception))

                shutil.rmtree(reserved_dir)

    def test_compile_and_deploy_dry_run(self):
        src_file = self.root_dir / "sample.txt"
        src_file.write_text("Hello", encoding="utf-8")
        dest_dir = DEFAULT_DEPLOY_PATHS["agents"] / "skills" / "sample"
        dest_file = dest_dir / "sample.txt"

        files_to_deploy = [(src_file, dest_file)]
        actions = deploy(files_to_deploy, dry_run=True, backup=False)

        self.assertEqual(len(actions), 1)
        self.assertFalse(dest_file.exists())

    def test_compile_and_deploy_with_backup(self):
        src_file = self.root_dir / "sample.txt"
        src_file.write_text("New content", encoding="utf-8")

        dest_dir = DEFAULT_DEPLOY_PATHS["agents"] / "skills" / "sample"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / "sample.txt"
        dest_file.write_text("Old content", encoding="utf-8")

        files_to_deploy = [(src_file, dest_file)]
        actions = deploy(files_to_deploy, dry_run=False, backup=True)

        self.assertTrue(dest_file.exists())
        self.assertEqual(dest_file.read_text(encoding="utf-8"), "New content")
        backup_file = DEFAULT_DEPLOY_PATHS["agents"] / ".shiro-agent-backups" / "agents" / "skills" / "sample" / "sample.txt.bak"
        self.assertTrue(backup_file.exists())
        self.assertEqual(backup_file.read_text(encoding="utf-8"), "Old content")

    def test_removed_skill_is_backed_up_outside_skill_directories(self):
        out_dir = self.root_dir / "dist"
        deploy(compile_targets(["skills"], self.root_dir, out_dir), targets=["skills"])
        (self.third_party_skill_dir / "SKILL.md").write_text("# Updated Vendor Skill", encoding="utf-8")
        deploy(compile_targets(["skills"], self.root_dir, out_dir), targets=["skills"])
        shutil.rmtree(self.third_party_skill_dir)

        deploy(compile_targets(["skills"], self.root_dir, out_dir), targets=["skills"])

        for agent in ["agents", "antigravity", "claude"]:
            self.assertFalse((DEFAULT_DEPLOY_PATHS[agent] / "skills" / "vendor-skill").exists())
            backup_file = (
                DEFAULT_DEPLOY_PATHS["agents"] / ".shiro-agent-backups" / agent
                / "skills" / "vendor-skill" / "SKILL.md.bak"
            )
            self.assertEqual(backup_file.read_text(), "# Updated Vendor Skill")

    def test_unchanged_deploy_preserves_existing_backup_and_file_timestamp(self):
        out_dir = self.root_dir / "dist"
        deploy(compile_targets(["skills"], self.root_dir, out_dir), targets=["skills"])
        (self.third_party_skill_dir / "SKILL.md").write_text("# Updated Vendor Skill", encoding="utf-8")
        pairs = compile_targets(["skills"], self.root_dir, out_dir)
        deploy(pairs, targets=["skills"])
        dest_file = DEFAULT_DEPLOY_PATHS["agents"] / "skills" / "vendor-skill" / "SKILL.md"
        original_timestamp = dest_file.stat().st_mtime_ns

        actions = deploy(pairs, targets=["skills"])

        self.assertEqual(actions, [])
        self.assertEqual(dest_file.stat().st_mtime_ns, original_timestamp)
        backup_file = (
            DEFAULT_DEPLOY_PATHS["agents"] / ".shiro-agent-backups" / "agents"
            / "skills" / "vendor-skill" / "SKILL.md.bak"
        )
        self.assertEqual(backup_file.read_text(), "# Vendor Skill")

    @unittest.skipUnless(os.name == "posix", "POSIX file permissions are required")
    def test_deploy_updates_executable_permissions_when_content_is_unchanged(self):
        src_file = self.root_dir / "script.sh"
        src_file.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        src_file.chmod(0o600)
        dest_file = DEFAULT_DEPLOY_PATHS["agents"] / "skills" / "sample" / "script.sh"
        deploy([(src_file, dest_file)], backup=False, targets=["skills"])
        src_file.chmod(0o700)

        deploy([(src_file, dest_file)], backup=False, targets=["skills"])

        self.assertEqual(stat.S_IMODE(dest_file.stat().st_mode), 0o700)

    def test_redeploy_removes_deleted_managed_files_and_preserves_unmanaged_skills(self):
        reference = self.custom_skill_dir / "reference.md"
        reference.write_text("Old reference", encoding="utf-8")
        out_dir = self.root_dir / "dist"
        deploy(compile_targets(["all"], self.root_dir, out_dir), backup=False)
        skill_roots = [DEFAULT_DEPLOY_PATHS[key] / "skills" for key in ["agents", "antigravity", "claude"]]
        for skill_root in skill_roots:
            user_skill = skill_root / "user-skill"
            user_skill.mkdir()
            (user_skill / "SKILL.md").write_text("# User Skill", encoding="utf-8")

        reference.unlink()
        shutil.rmtree(self.third_party_skill_dir)
        self.lock_file.unlink()
        deploy(compile_targets(["all"], self.root_dir, out_dir), backup=False)

        for skill_root in skill_roots:
            self.assertFalse((skill_root / "vendor-skill").exists())
            self.assertFalse((skill_root / "custom-skill" / "reference.md").exists())
            self.assertTrue((skill_root / "custom-skill" / "SKILL.md").exists())
            self.assertEqual((skill_root / "user-skill" / "SKILL.md").read_text(), "# User Skill")
        self.assertFalse((DEFAULT_DEPLOY_PATHS["agents"] / "skills-lock.json").exists())

    def test_partial_deploy_cleans_empty_target_and_retains_other_target_history(self):
        out_dir = self.root_dir / "dist"
        deploy(compile_targets(["all"], self.root_dir, out_dir), backup=False)
        (self.codex_config_dir / "AGENTS.md").unlink()
        shutil.rmtree(self.custom_skill_dir)
        shutil.rmtree(self.third_party_skill_dir)
        self.lock_file.unlink()

        deploy(compile_targets(["codex"], self.root_dir, out_dir), backup=False, targets=["codex"])

        self.assertFalse((DEFAULT_DEPLOY_PATHS["codex"] / "AGENTS.md").exists())
        skill_file = DEFAULT_DEPLOY_PATHS["agents"] / "skills" / "custom-skill" / "SKILL.md"
        self.assertTrue(skill_file.exists())

        deploy(compile_targets(["skills"], self.root_dir, out_dir), backup=False, targets=["skills"])

        self.assertFalse(skill_file.parent.exists())
        self.assertFalse((DEFAULT_DEPLOY_PATHS["agents"] / "skills" / "vendor-skill").exists())

    def test_dry_run_previews_removal_and_backup_without_changing_deployment(self):
        out_dir = self.root_dir / "dist"
        deploy(compile_targets(["skills"], self.root_dir, out_dir), targets=["skills"])
        manifest = DEFAULT_DEPLOY_PATHS["agents"] / ".shiro-agent-deploy.json"
        original_manifest = manifest.read_bytes()
        shutil.rmtree(self.third_party_skill_dir)

        actions = deploy(
            compile_targets(["skills"], self.root_dir, out_dir), dry_run=True, targets=["skills"]
        )

        dest_file = DEFAULT_DEPLOY_PATHS["agents"] / "skills" / "vendor-skill" / "SKILL.md"
        self.assertIn(f"[DRY-RUN] Remove {dest_file}", actions)
        self.assertTrue(any(action.startswith("[DRY-RUN] Backup ") for action in actions))
        self.assertEqual(dest_file.read_text(), "# Vendor Skill")
        self.assertEqual(manifest.read_bytes(), original_manifest)
        self.assertFalse((DEFAULT_DEPLOY_PATHS["agents"] / ".shiro-agent-backups").exists())

    def test_deploy_rejects_paths_with_parent_traversal(self):
        src_file = self.root_dir / "sample.txt"
        src_file.write_text("Managed content", encoding="utf-8")
        dest_file = DEFAULT_DEPLOY_PATHS["agents"] / "skills" / ".." / "notes.md"

        with self.assertRaisesRegex(ValueError, "Invalid deployment path"):
            deploy([(src_file, dest_file)], backup=False)

        self.assertFalse((DEFAULT_DEPLOY_PATHS["agents"] / "notes.md").exists())

    def test_deploy_rejects_symlinked_skill_directory_before_cleanup(self):
        out_dir = self.root_dir / "dist"
        deploy(compile_targets(["skills"], self.root_dir, out_dir), backup=False, targets=["skills"])
        deployed_skill = DEFAULT_DEPLOY_PATHS["agents"] / "skills" / "vendor-skill"
        external_skill = self.root_dir / "external-skill"
        deployed_skill.rename(external_skill)
        deployed_skill.symlink_to(external_skill, target_is_directory=True)
        shutil.rmtree(self.third_party_skill_dir)
        manifest = DEFAULT_DEPLOY_PATHS["agents"] / ".shiro-agent-deploy.json"
        original_manifest = manifest.read_bytes()

        with self.assertRaisesRegex(ValueError, "Symlink in managed path"):
            deploy(compile_targets(["skills"], self.root_dir, out_dir), backup=False, targets=["skills"])

        self.assertEqual((external_skill / "SKILL.md").read_text(), "# Vendor Skill")
        self.assertEqual(manifest.read_bytes(), original_manifest)

    def test_deploy_preserves_legacy_skills_and_user_files_inside_removed_skill(self):
        skill_root = DEFAULT_DEPLOY_PATHS["agents"] / "skills"
        legacy_skill = skill_root / "legacy-skill" / "SKILL.md"
        legacy_skill.parent.mkdir(parents=True)
        legacy_skill.write_text("# Legacy Skill", encoding="utf-8")
        out_dir = self.root_dir / "dist"
        deploy(compile_targets(["skills"], self.root_dir, out_dir), backup=False, targets=["skills"])
        user_file = skill_root / "vendor-skill" / "user-note.txt"
        user_file.write_text("User notes", encoding="utf-8")
        shutil.rmtree(self.third_party_skill_dir)

        deploy(compile_targets(["skills"], self.root_dir, out_dir), backup=False, targets=["skills"])

        self.assertEqual(legacy_skill.read_text(), "# Legacy Skill")
        self.assertEqual(user_file.read_text(), "User notes")
        self.assertFalse((skill_root / "vendor-skill" / "SKILL.md").exists())

    def test_invalid_deploy_manifest_aborts_before_changing_files(self):
        out_dir = self.root_dir / "dist"
        pairs = compile_targets(["skills"], self.root_dir, out_dir)
        deploy(pairs, backup=False, targets=["skills"])
        manifest = DEFAULT_DEPLOY_PATHS["agents"] / ".shiro-agent-deploy.json"
        dest_file = DEFAULT_DEPLOY_PATHS["agents"] / "skills" / "custom-skill" / "SKILL.md"
        dest_file.write_text("Local edits", encoding="utf-8")
        user_file = self.root_dir / "user-notes.txt"
        user_file.write_text("User notes", encoding="utf-8")
        invalid_manifests = [
            "{broken JSON",
            json.dumps({"version": 1, "targets": {"skills": [str(user_file)]}}),
            json.dumps({"version": 1, "targets": {"codex": [str(dest_file)]}}),
            json.dumps({"version": 99, "targets": {}}),
        ]

        for content in invalid_manifests:
            with self.subTest(content=content):
                manifest.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    deploy(pairs, backup=False, targets=["skills"])
                self.assertEqual(dest_file.read_text(), "Local edits")
                self.assertEqual(user_file.read_text(), "User notes")

    def test_missing_deployment_source_aborts_before_copying_or_updating_manifest(self):
        out_dir = self.root_dir / "dist"
        pairs = compile_targets(["skills"], self.root_dir, out_dir)
        deploy(pairs, backup=False, targets=["skills"])
        manifest = DEFAULT_DEPLOY_PATHS["agents"] / ".shiro-agent-deploy.json"
        original_manifest = manifest.read_bytes()
        pairs[0][1].write_text("Local edits", encoding="utf-8")
        pairs[-1][0].unlink()

        with self.assertRaisesRegex(FileNotFoundError, "Deployment source not found"):
            deploy(pairs, backup=False, targets=["skills"])

        self.assertEqual(pairs[0][1].read_text(), "Local edits")
        self.assertEqual(manifest.read_bytes(), original_manifest)


if __name__ == "__main__":
    unittest.main()
