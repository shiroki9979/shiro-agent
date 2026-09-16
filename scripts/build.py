#!/usr/bin/env python3
"""Build and deployment script for agent configurations.

Compiles shared markdown guidelines into agent-specific configs,
and copies/deploys them to target environments.
"""

import argparse
import os
from pathlib import Path
import re
import shutil
import sys
from typing import Dict, List, Optional, Tuple

INCLUDE_PATTERN = re.compile(r"<!--\s*INCLUDE:([^\s>]+)\s*-->")

DEFAULT_DEPLOY_PATHS: Dict[str, Path] = {
    "agents": Path.home() / ".agents",
    "antigravity": Path.home() / ".gemini" / "config",
    "cursor": Path.home() / ".cursor",
    "claude": Path.home() / ".claude",
    "codex": Path.home() / ".codex",
}


def expand_includes(content: str, root_dir: Path) -> str:
    """展開模板中的 <!-- INCLUDE:path --> 標籤。

    為實現單一真實來源 (Single Source of Truth)，將共用規範動態注入目標設定。
    """
    def _replacer(match: re.Match) -> str:
        rel_path = match.group(1).strip()
        target_path = (root_dir / rel_path).resolve()

        if not target_path.exists() or not target_path.is_file():
            raise FileNotFoundError(f"Included file not found: {rel_path} (resolved: {target_path})")

        included_content = target_path.read_text(encoding="utf-8").rstrip("\r\n")
        # 遞迴展開巢狀 include
        return expand_includes(included_content, root_dir)

    return INCLUDE_PATTERN.sub(_replacer, content)


def process_file(src_path: Path, dest_path: Path, root_dir: Path) -> None:
    """處理單一檔案，若為 markdown 則展開 include，其餘直接複製。"""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if src_path.suffix.lower() in [".md", ".mdc"]:
        raw_text = src_path.read_text(encoding="utf-8")
        compiled_text = expand_includes(raw_text, root_dir)
        dest_path.write_text(compiled_text, encoding="utf-8")
    else:
        shutil.copy2(src_path, dest_path)


def compile_skills(repo_root: Path, out_dir: Path) -> List[Tuple[Path, Path]]:
    """編譯自建 Skills (custom-skills/) 與第三方 Skills (.agents/skills/) 至輸出與部署路徑。"""
    pairs: List[Tuple[Path, Path]] = []
    target_out = out_dir / ".agents" / "skills"

    custom_root = repo_root / "custom-skills"
    third_party_root = repo_root / ".agents" / "skills"

    # 收集自建與第三方技能目錄並檢驗名稱衝突
    discovered_skills: Dict[str, Tuple[str, Path]] = {}

    if custom_root.exists():
        for skill_dir in custom_root.glob("*"):
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                discovered_skills[skill_dir.name] = ("custom", skill_dir)

    if third_party_root.exists():
        for skill_dir in third_party_root.glob("*"):
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                skill_name = skill_dir.name
                if skill_name in discovered_skills:
                    raise ValueError(
                        f"Skill name collision detected for '{skill_name}': exists in both 'custom-skills/' and '.agents/skills/'."
                    )
                discovered_skills[skill_name] = ("third-party", skill_dir)

    for skill_name, (_, skill_dir) in discovered_skills.items():
        dest_skill_dir = target_out / skill_name
        dest_skill_dir.mkdir(parents=True, exist_ok=True)
        for item in skill_dir.glob("**/*"):
            if item.is_file() and item.name != ".gitkeep":
                rel_to_skill = item.relative_to(skill_dir)
                dest_item = dest_skill_dir / rel_to_skill
                process_file(item, dest_item, repo_root)
                for agent_key in ["agents", "antigravity", "claude", "cursor"]:
                    deploy_path = DEFAULT_DEPLOY_PATHS[agent_key] / "skills" / skill_name / rel_to_skill
                    pairs.append((dest_item, deploy_path))

    # 同步 skills-lock.json 至全域 .agents 目錄
    lock_file = repo_root / "skills-lock.json"
    if lock_file.exists():
        dest_lock = out_dir / ".agents" / "skills-lock.json"
        process_file(lock_file, dest_lock, repo_root)
        pairs.append((dest_lock, DEFAULT_DEPLOY_PATHS["agents"] / "skills-lock.json"))

    return pairs


def compile_antigravity(repo_root: Path, out_dir: Path) -> List[Tuple[Path, Path]]:
    """編譯 Antigravity 設定檔與規則。"""
    pairs: List[Tuple[Path, Path]] = []
    config_dir = repo_root / "configs" / "antigravity"
    target_out = out_dir / "antigravity"

    # 編譯 rules
    rules_src = config_dir / "rules"
    if rules_src.exists():
        for rule_file in rules_src.glob("*"):
            if rule_file.is_file():
                dest_file = target_out / "rules" / rule_file.name
                process_file(rule_file, dest_file, repo_root)
                pairs.append((dest_file, DEFAULT_DEPLOY_PATHS["antigravity"] / "rules" / rule_file.name))

    # 複製 mcp_config.json 與 hooks.json
    for json_name in ["mcp_config.json", "hooks.json"]:
        json_src = config_dir / json_name
        if json_src.exists():
            dest_file = target_out / json_name
            process_file(json_src, dest_file, repo_root)
            pairs.append((dest_file, DEFAULT_DEPLOY_PATHS["antigravity"] / json_name))

    return pairs


def compile_cursor(repo_root: Path, out_dir: Path) -> List[Tuple[Path, Path]]:
    """編譯 Cursor 設定檔與規則。"""
    pairs: List[Tuple[Path, Path]] = []
    config_dir = repo_root / "configs" / "cursor"
    target_out = out_dir / "cursor"

    # 編譯 rules
    rules_src = config_dir / "rules"
    if rules_src.exists():
        for rule_file in rules_src.glob("*"):
            if rule_file.is_file():
                dest_file = target_out / "rules" / rule_file.name
                process_file(rule_file, dest_file, repo_root)
                pairs.append((dest_file, DEFAULT_DEPLOY_PATHS["cursor"] / "rules" / rule_file.name))

    # 複製 settings.json
    settings_src = config_dir / "settings.json"
    if settings_src.exists():
        dest_file = target_out / "settings.json"
        process_file(settings_src, dest_file, repo_root)
        pairs.append((dest_file, DEFAULT_DEPLOY_PATHS["cursor"] / "settings.json"))

    return pairs


def compile_claude(repo_root: Path, out_dir: Path) -> List[Tuple[Path, Path]]:
    """編譯 Claude 指示與 MCP 設定。"""
    pairs: List[Tuple[Path, Path]] = []
    config_dir = repo_root / "configs" / "claude"
    target_out = out_dir / "claude"

    # 編譯 CLAUDE.md
    claude_md = config_dir / "CLAUDE.md"
    if claude_md.exists():
        dest_file = target_out / "CLAUDE.md"
        process_file(claude_md, dest_file, repo_root)
        pairs.append((dest_file, DEFAULT_DEPLOY_PATHS["claude"] / "CLAUDE.md"))

    # 複製 mcp_config.json
    mcp_src = config_dir / "mcp_config.json"
    if mcp_src.exists():
        dest_file = target_out / "mcp_config.json"
        process_file(mcp_src, dest_file, repo_root)
        pairs.append((dest_file, DEFAULT_DEPLOY_PATHS["claude"] / "mcp_config.json"))

    return pairs


def compile_codex(repo_root: Path, out_dir: Path) -> List[Tuple[Path, Path]]:
    """編譯 Codex 全域指示。"""
    config_dir = repo_root / "configs" / "codex"
    codex_instruction = config_dir / "AGENTS.md"

    if not codex_instruction.exists():
        return []

    dest_file = out_dir / "codex" / "AGENTS.md"
    process_file(codex_instruction, dest_file, repo_root)
    return [(dest_file, DEFAULT_DEPLOY_PATHS["codex"] / "AGENTS.md")]


def compile_targets(targets: List[str], repo_root: Path, out_dir: Path) -> List[Tuple[Path, Path]]:
    """依指定目標列表編譯所有設定檔。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    all_pairs: List[Tuple[Path, Path]] = []

    target_map = {
        "skills": compile_skills,
        "antigravity": compile_antigravity,
        "cursor": compile_cursor,
        "claude": compile_claude,
        "codex": compile_codex,
    }

    selected = target_map.keys() if "all" in targets else targets
    for target in selected:
        if target in target_map:
            all_pairs.extend(target_map[target](repo_root, out_dir))

    return all_pairs


def deploy(file_pairs: List[Tuple[Path, Path]], dry_run: bool = False, backup: bool = True) -> List[str]:
    """將編譯好的檔案複製至目標系統路徑。"""
    actions: List[str] = []

    for src_file, dest_file in file_pairs:
        if not src_file.exists():
            continue

        if dry_run:
            actions.append(f"[DRY-RUN] Copy {src_file} -> {dest_file}")
            continue

        dest_file.parent.mkdir(parents=True, exist_ok=True)

        if backup and dest_file.exists():
            backup_file = dest_file.with_suffix(dest_file.suffix + ".bak")
            shutil.copy2(dest_file, backup_file)
            actions.append(f"[BACKUP] {dest_file} -> {backup_file}")

        shutil.copy2(src_file, dest_file)
        actions.append(f"[DEPLOY] {src_file} -> {dest_file}")

    return actions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile and deploy agent configurations.")
    parser.add_argument(
        "--target",
        nargs="+",
        choices=["all", "skills", "antigravity", "cursor", "claude", "codex"],
        default=["all"],
        help="Target configurations to compile/deploy (default: all)",
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Deploy compiled files to target system paths",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate deployment actions without modifying files",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Disable creating .bak files when deploying over existing files",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="dist",
        help="Directory to store compiled output (default: dist/)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = (repo_root / args.out_dir).resolve()

    print(f"Compiling targets: {', '.join(args.target)}")
    pairs = compile_targets(args.target, repo_root, out_dir)
    print(f"Successfully compiled {len(pairs)} file(s) into {out_dir}")

    if args.deploy or args.dry_run:
        print("\nDeploying configurations...")
        actions = deploy(pairs, dry_run=args.dry_run, backup=not args.no_backup)
        for action in actions:
            print(f"  {action}")
        print(f"\nCompleted {len(actions)} deployment operation(s).")


if __name__ == "__main__":
    main()
