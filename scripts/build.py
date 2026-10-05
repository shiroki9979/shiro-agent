#!/usr/bin/env python3
"""Build and deployment script for agent configurations.

Compiles shared markdown guidelines into agent-specific configs,
and copies/deploys them to target environments.
"""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile
from typing import Dict, List, Optional, Tuple

INCLUDE_PATTERN = re.compile(r"<!--\s*INCLUDE:([^\s>]+)\s*-->")

# Claude Code 保留給 claude.ai 同步技能的目錄名稱，使用者技能以此命名時不會被載入
CLAUDE_RESERVED_SKILL_NAME = "synced"
CLAUDE_RESERVED_SKILL_PREFIX = "anthropic-skills"

DEFAULT_DEPLOY_PATHS: Dict[str, Path] = {
    "agents": Path.home() / ".agents",
    "antigravity": Path.home() / ".gemini" / "config",
    "cursor": Path.home() / ".cursor",
    "claude": Path.home() / ".claude",
    "codex": Path.home() / ".codex",
}

TARGET_OUTPUT_DIRS = {
    "skills": ".agents",
    "antigravity": "antigravity",
    "cursor": "cursor",
    "claude": "claude",
    "codex": "codex",
}

DEPLOY_MANIFEST_NAME = ".shiro-agent-deploy.json"
TARGET_DEPLOY_RULES = {
    "skills": {
        "agents": ["skills/", "skills-lock.json"],
        "antigravity": ["skills/"],
        "claude": ["skills/"],
    },
    "antigravity": {"antigravity": ["rules/", "mcp_config.json", "hooks.json"]},
    "cursor": {"cursor": ["rules/", "settings.json"]},
    "claude": {"claude": ["CLAUDE.md"]},
    "codex": {"codex": ["AGENTS.md"]},
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


def validate_skill_name(skill_name: str) -> None:
    """拒絕 Claude Code 保留的技能名稱，避免部署後靜默不載入。"""
    lowered = skill_name.lower()
    if lowered == CLAUDE_RESERVED_SKILL_NAME or lowered.startswith(CLAUDE_RESERVED_SKILL_PREFIX):
        raise ValueError(f"Skill name '{skill_name}' is reserved by Claude Code and would not be loaded.")


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
        validate_skill_name(skill_name)
        dest_skill_dir = target_out / skill_name
        dest_skill_dir.mkdir(parents=True, exist_ok=True)
        for item in skill_dir.glob("**/*"):
            if item.is_file() and item.name != ".gitkeep":
                rel_to_skill = item.relative_to(skill_dir)
                dest_item = dest_skill_dir / rel_to_skill
                process_file(item, dest_item, repo_root)
                for agent_key in ["agents", "antigravity", "claude"]:
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
    """編譯 Claude 全域指示。

    MCP 不在此部署：Claude Code 使用者層 MCP 存於 ~/.claude.json（含 OAuth 與狀態資料），
    須以 `claude mcp add-json --scope user` 寫入，不可由部署整檔覆寫。
    """
    pairs: List[Tuple[Path, Path]] = []
    config_dir = repo_root / "configs" / "claude"
    target_out = out_dir / "claude"

    # 編譯 CLAUDE.md
    claude_md = config_dir / "CLAUDE.md"
    if claude_md.exists():
        dest_file = target_out / "CLAUDE.md"
        process_file(claude_md, dest_file, repo_root)
        pairs.append((dest_file, DEFAULT_DEPLOY_PATHS["claude"] / "CLAUDE.md"))

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
    validate_output_dir(repo_root, out_dir)
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    all_pairs: List[Tuple[Path, Path]] = []

    target_map = {
        "skills": compile_skills,
        "antigravity": compile_antigravity,
        "cursor": compile_cursor,
        "claude": compile_claude,
        "codex": compile_codex,
    }

    selected = selected_targets(targets)
    for target in selected:
        validate_managed_path(out_dir / TARGET_OUTPUT_DIRS[target], out_dir)
    for target in selected:
        target_out = out_dir / TARGET_OUTPUT_DIRS[target]
        if target_out.exists():
            shutil.rmtree(target_out)
        all_pairs.extend(target_map[target](repo_root, out_dir))

    return all_pairs


def validate_output_dir(repo_root: Path, out_dir: Path) -> None:
    repo_root = repo_root.resolve()
    out_dir = out_dir.resolve()
    if repo_root.is_relative_to(out_dir):
        raise ValueError(f"Output directory overlaps repository: {out_dir}")
    for source_name in ["custom-skills", ".agents", "configs", "shared", ".git"]:
        source_dir = (repo_root / source_name).resolve()
        if out_dir.is_relative_to(source_dir) or source_dir.is_relative_to(out_dir):
            raise ValueError(f"Output directory overlaps source directory: {out_dir}")


def selected_targets(targets: List[str]) -> List[str]:
    selected = list(TARGET_OUTPUT_DIRS) if "all" in targets else list(dict.fromkeys(targets))
    for target in selected:
        if target not in TARGET_OUTPUT_DIRS:
            raise ValueError(f"Unknown deployment target: {target}")
    return selected


def deploy(
    file_pairs: List[Tuple[Path, Path]],
    dry_run: bool = False,
    backup: bool = True,
    *,
    targets: Optional[List[str]] = None,
) -> List[str]:
    """部署現有檔案並清理上次部署後失去來源的檔案。"""
    manifest_path = DEFAULT_DEPLOY_PATHS["agents"] / DEPLOY_MANIFEST_NAME
    validate_managed_path(manifest_path, DEFAULT_DEPLOY_PATHS["agents"])
    previous = load_deploy_manifest(manifest_path)
    selected = selected_targets(targets if targets is not None else ["all"])
    current = collect_deployment_files(file_pairs, selected)
    stale_files = stale_deployment_files(previous, current)
    destinations = [dest_file for _, dest_file in file_pairs] + stale_files
    validate_deployment_paths(destinations, backup)

    actions: List[str] = []
    for file_pair in file_pairs:
        actions.extend(copy_deployed_file(file_pair, dry_run, backup))
    for dest_file in stale_files:
        actions.extend(remove_deployed_file(dest_file, dry_run, backup))
    if not dry_run:
        save_deploy_manifest(manifest_path, {**previous, **current})
    return actions


def collect_deployment_files(file_pairs: List[Tuple[Path, Path]], selected: List[str]) -> Dict[str, List[str]]:
    current: Dict[str, List[str]] = {target: [] for target in selected}
    for src_file, dest_file in file_pairs:
        if not src_file.is_file():
            raise FileNotFoundError(f"Deployment source not found: {src_file}")
        target, _, _ = deployment_scope(dest_file)
        if target not in current:
            raise ValueError(f"Deployment file does not belong to selected targets: {dest_file}")
        current[target].append(str(dest_file))
    return {target: sorted(set(filenames)) for target, filenames in current.items()}


def stale_deployment_files(previous: Dict[str, List[str]], current: Dict[str, List[str]]) -> List[Path]:
    return [
        Path(filename)
        for target, filenames in current.items()
        for filename in sorted(set(previous.get(target, [])) - set(filenames))
    ]


def validate_deployment_paths(destinations: List[Path], backup: bool) -> None:
    for dest_file in destinations:
        _, agent, _ = deployment_scope(dest_file)
        validate_managed_path(dest_file, DEFAULT_DEPLOY_PATHS[agent])
        if dest_file.exists() and not dest_file.is_file():
            raise ValueError(f"Expected a deployment file: {dest_file}")
        if backup:
            validate_managed_path(deployment_backup_path(dest_file), DEFAULT_DEPLOY_PATHS["agents"])


def copy_deployed_file(file_pair: Tuple[Path, Path], dry_run: bool, backup: bool) -> List[str]:
    src_file, dest_file = file_pair
    if (
        dest_file.is_file()
        and stat.S_IMODE(src_file.stat().st_mode) == stat.S_IMODE(dest_file.stat().st_mode)
        and src_file.read_bytes() == dest_file.read_bytes()
    ):
        return []

    actions: List[str] = []
    if backup and dest_file.exists():
        actions.append(backup_deployed_file(dest_file, dry_run))
    if dry_run:
        return actions + [f"[DRY-RUN] Copy {src_file} -> {dest_file}"]

    dest_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, dest_file)
    return actions + [f"[DEPLOY] {src_file} -> {dest_file}"]


def remove_deployed_file(dest_file: Path, dry_run: bool, backup: bool) -> List[str]:
    actions: List[str] = []
    if backup and dest_file.exists():
        actions.append(backup_deployed_file(dest_file, dry_run))
    if dry_run:
        return actions + [f"[DRY-RUN] Remove {dest_file}"]

    if dest_file.exists():
        dest_file.unlink()
        actions.append(f"[REMOVE] {dest_file}")
    _, _, boundary = deployment_scope(dest_file)
    remove_empty_parents(dest_file.parent, boundary)
    return actions


def backup_deployed_file(dest_file: Path, dry_run: bool = False) -> str:
    backup_file = deployment_backup_path(dest_file)
    if dry_run:
        return f"[DRY-RUN] Backup {dest_file} -> {backup_file}"
    backup_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dest_file, backup_file)
    return f"[BACKUP] {dest_file} -> {backup_file}"


def deployment_backup_path(dest_file: Path) -> Path:
    _, agent, _ = deployment_scope(dest_file)
    relative_path = dest_file.relative_to(DEFAULT_DEPLOY_PATHS[agent])
    backup_file = DEFAULT_DEPLOY_PATHS["agents"] / ".shiro-agent-backups" / agent / relative_path
    return backup_file.with_suffix(backup_file.suffix + ".bak")


def validate_managed_path(path: Path, root: Path) -> None:
    for candidate in [path, *path.parents]:
        if candidate.is_symlink():
            raise ValueError(f"Symlink in managed path: {candidate}")
        if candidate == root:
            return
    raise ValueError(f"Path is outside managed root '{root}': {path}")


def deployment_scope(dest_file: Path) -> Tuple[str, str, Path]:
    if not dest_file.is_absolute() or ".." in dest_file.parts:
        raise ValueError(f"Invalid deployment path: {dest_file}")
    for target, agent_rules in TARGET_DEPLOY_RULES.items():
        for agent, rules in agent_rules.items():
            root = DEFAULT_DEPLOY_PATHS[agent]
            for rule in rules:
                path = root / rule
                if rule.endswith("/") and dest_file != path and dest_file.is_relative_to(path):
                    return target, agent, path
                if not rule.endswith("/") and dest_file == path:
                    return target, agent, root
    raise ValueError(f"Deployment path is outside managed locations: {dest_file}")


def load_deploy_manifest(manifest_path: Path) -> Dict[str, List[str]]:
    if not manifest_path.exists():
        return {}
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid deployment manifest: {manifest_path}: {error}") from error
    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("targets"), dict):
        raise ValueError(f"Invalid deployment manifest format: {manifest_path}")
    for target, filenames in data["targets"].items():
        if target not in TARGET_DEPLOY_RULES or not isinstance(filenames, list):
            raise ValueError(f"Invalid deployment manifest target: {target}")
        for filename in filenames:
            if not isinstance(filename, str) or not Path(filename).is_absolute() or ".." in Path(filename).parts:
                raise ValueError(f"Invalid deployment manifest path: {filename!r}")
            scope, _, _ = deployment_scope(Path(filename))
            if scope != target:
                raise ValueError(f"Deployment manifest path does not match target '{target}': {filename}")
    return data["targets"]


def remove_empty_parents(directory: Path, boundary: Path) -> None:
    while directory != boundary and directory.is_relative_to(boundary):
        if not directory.exists() or any(directory.iterdir()):
            return
        directory.rmdir()
        directory = directory.parent


def save_deploy_manifest(manifest_path: Path, targets: Dict[str, List[str]]) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=manifest_path.parent,
            prefix=manifest_path.name + ".", suffix=".tmp", delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            temporary_file.write(json.dumps({"version": 1, "targets": targets}, indent=2) + "\n")
        os.replace(temporary_path, manifest_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


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
        help="Deploy compiled files and remove obsolete managed files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compile output and preview deployment without modifying target files",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Disable centralized .bak backups when overwriting or removing files",
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
        actions = deploy(pairs, dry_run=args.dry_run, backup=not args.no_backup, targets=args.target)
        for action in actions:
            print(f"  {action}")
        print(f"\nCompleted {len(actions)} deployment operation(s).")


if __name__ == "__main__":
    main()
