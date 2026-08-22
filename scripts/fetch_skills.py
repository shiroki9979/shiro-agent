#!/usr/bin/env python3
"""Fetch and update third-party skills from external sources."""

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Tuple
import urllib.error
import urllib.request


def resolve_source_and_name(source_str: str, default_name: Optional[str] = None) -> Tuple[str, str]:
    """解析各類型來源格式（skills.sh、GitHub URL、Raw URL），返回 (下載URL, Skill名稱)。"""
    source = source_str.strip()
    extracted_name = default_name

    # 1. 處理 CLI flag 格式: "repo --skill name" 或 "url --skill name"
    if "--skill" in source:
        parts = re.split(r"\s+--skill\s+", source, maxsplit=1)
        if len(parts) == 2:
            source = parts[0].strip()
            if not extracted_name:
                extracted_name = parts[1].strip()

    # 2. 處理 npm / skills.sh 格式: "owner/repo@skill"
    if "@" in source and not (source.startswith("http://") or source.startswith("https://")):
        repo_part, skill_part = source.split("@", 1)
        source = repo_part.strip()
        if not extracted_name:
            extracted_name = skill_part.strip()

    # 3. 處理 GitHub 網頁 URL
    github_blob_match = re.match(r"^https?://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)$", source)
    if github_blob_match:
        owner, repo, branch, path = github_blob_match.groups()
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
        if not extracted_name:
            # 從路徑推導名稱，如 skills/find-skills/SKILL.md -> find-skills
            path_parts = [p for p in path.split("/") if p and p != "SKILL.md"]
            extracted_name = path_parts[-1] if path_parts else repo
        return raw_url, extracted_name

    github_tree_match = re.match(r"^https?://github\.com/([^/]+)/([^/]+)/tree/([^/]+)/(.+)$", source)
    if github_tree_match:
        owner, repo, branch, path = github_tree_match.groups()
        if not path.endswith(".md"):
            path = f"{path.rstrip('/')}/SKILL.md"
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
        if not extracted_name:
            path_parts = [p for p in path.split("/") if p and p != "SKILL.md"]
            extracted_name = path_parts[-1] if path_parts else repo
        return raw_url, extracted_name

    # 4. 處理 GitHub Repo 簡寫 "owner/repo" 或 "https://github.com/owner/repo"
    github_repo_match = re.match(r"^(?:https?://github\.com/)?([a-zA-Z0-9_\-\.]+)/([a-zA-Z0-9_\-\.]+)$", source)
    if github_repo_match and not source.startswith("https://raw.githubusercontent.com"):
        owner, repo = github_repo_match.groups()
        if extracted_name:
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/skills/{extracted_name}/SKILL.md"
        else:
            extracted_name = repo
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/SKILL.md"
        return raw_url, extracted_name

    # 5. 處理 Raw URL 或一般網址
    if source.startswith("http://") or source.startswith("https://"):
        if not extracted_name:
            path_parts = [p for p in source.rstrip("/").split("/") if p and p != "SKILL.md"]
            extracted_name = path_parts[-1] if path_parts else "unnamed-skill"
        return source, extracted_name

    # 6. 本地路徑
    if not extracted_name:
        extracted_name = Path(source).stem if Path(source).stem != "SKILL" else Path(source).parent.name
    return source, extracted_name or "unnamed-skill"


def normalize_skill(skill: Dict[str, Any]) -> Dict[str, Any]:
    """將 Skill 定義標準化並自動補全預設欄位。"""
    raw_source = skill.get("source", "")
    explicit_name = skill.get("name")
    resolved_source, deduced_name = resolve_source_and_name(raw_source, explicit_name)

    name = explicit_name or deduced_name
    destination = skill.get("destination") or f"skills/third-party/{name}/SKILL.md"
    enabled = skill.get("enabled", True)
    description = skill.get("description", "")

    return {
        "name": name,
        "description": description,
        "source": raw_source,
        "_resolved_source": resolved_source,
        "destination": destination,
        "enabled": enabled,
    }


def load_manifest(manifest_path: Path) -> List[Dict[str, Any]]:
    """讀取並解析 Skills 清單設定檔。"""
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise ValueError(f"Invalid JSON in manifest file {manifest_path}: {err}") from err

    skills = data.get("skills", [])
    if not isinstance(skills, list):
        raise ValueError("Manifest 'skills' property must be a list")

    return skills


def save_manifest(manifest_path: Path, skills: List[Dict[str, Any]]) -> None:
    """將 Skills 清單寫回 JSON 檔案。"""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_data = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "skills": skills,
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fetch_skill(skill: Dict[str, Any], root_dir: Path, timeout: int = 15) -> bool:
    """下載或複製單一第三方 Skill 至指定目錄。"""
    norm = normalize_skill(skill)
    name = norm["name"]
    source_url = norm["_resolved_source"]
    dest_rel = norm["destination"]

    if not source_url:
        print(f"Skipping {name}: empty source", file=sys.stderr)
        return False

    dest_path = root_dir / dest_rel
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Fetching '{name}' from {source_url}...")

    try:
        if source_url.startswith("http://") or source_url.startswith("https://"):
            req = urllib.request.Request(
                source_url,
                headers={"User-Agent": "shiro-agent-sync/1.0"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read()
                dest_path.write_bytes(content)
        else:
            local_src = (root_dir / source_url).resolve()
            if not local_src.exists():
                raise FileNotFoundError(f"Local source not found: {local_src}")
            dest_path.write_bytes(local_src.read_bytes())

        print(f"  -> Saved to {dest_rel}")
        return True
    except (urllib.error.URLError, OSError, TimeoutError) as err:
        print(f"  -> Error fetching '{name}': {err}", file=sys.stderr)
        return False


def fetch_all_skills(skills: List[Dict[str, Any]], root_dir: Path, force: bool = False) -> int:
    """批量下載所有啟用中的 Skills。"""
    success_count = 0
    for skill in skills:
        norm = normalize_skill(skill)
        if norm["enabled"] or force:
            if fetch_skill(skill, root_dir):
                success_count += 1
        else:
            print(f"Skipping disabled skill: {norm['name']}")
    return success_count


def add_skill(
    manifest_path: Path,
    source: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    destination: Optional[str] = None,
    deploy: bool = False,
    root_dir: Optional[Path] = None,
) -> bool:
    """新增或更新 Skill 定義至清單並執行下載（可選自動部署）。"""
    if root_dir is None:
        root_dir = manifest_path.resolve().parent.parent

    # 解析來源與名稱
    resolved_url, deduced_name = resolve_source_and_name(source, name)
    skill_name = name or deduced_name

    skill_entry: Dict[str, Any] = {
        "name": skill_name,
        "source": source,
    }
    if description:
        skill_entry["description"] = description
    if destination:
        skill_entry["destination"] = destination

    # 讀取現有清單
    try:
        skills = load_manifest(manifest_path)
    except FileNotFoundError:
        skills = []

    # 若已存在則更新，否則加入
    existing_idx = next((i for i, s in enumerate(skills) if s.get("name") == skill_name), None)
    if existing_idx is not None:
        skills[existing_idx] = skill_entry
        print(f"Updated existing skill entry '{skill_name}' in manifest.")
    else:
        skills.append(skill_entry)
        print(f"Added new skill entry '{skill_name}' to manifest.")

    save_manifest(manifest_path, skills)

    # 執行下載
    success = fetch_skill(skill_entry, root_dir)
    if not success:
        return False

    # 若要求部署，調用 build 模組
    if deploy:
        print("\nTriggering deployment...")
        try:
            from build import compile_skills, deploy as run_deploy  # noqa: E402
            out_dir = (root_dir / "dist").resolve()
            pairs = compile_skills(root_dir, out_dir)
            actions = run_deploy(pairs, dry_run=False, backup=True)
            for action in actions:
                print(f"  {action}")
            print("Deployment completed successfully.")
        except Exception as err:
            print(f"Deployment failed: {err}", file=sys.stderr)
            return False

    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and sync third-party skills from manifest.")
    parser.add_argument(
        "--manifest",
        type=str,
        default="skills/manifest.json",
        help="Path to manifest JSON (default: skills/manifest.json)",
    )

    # 支援子命令 (add) 或傳統旗標
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    add_parser = subparsers.add_parser("add", help="Add and fetch a new third-party skill")
    add_parser.add_argument("source", type=str, help="Skill source (e.g. vercel-labs/agent-skills@find-skills or URL)")
    add_parser.add_argument("--name", type=str, help="Custom skill name")
    add_parser.add_argument("--description", type=str, help="Skill description")
    add_parser.add_argument("--dest", type=str, help="Destination relative path")
    add_parser.add_argument("--deploy", action="store_true", help="Deploy to global config after downloading")

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all skills defined in manifest",
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Fetch a specific skill by name from manifest",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Fetch all enabled skills in manifest",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force fetch even if marked as disabled",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    manifest_path = (repo_root / args.manifest).resolve()

    if args.command == "add":
        success = add_skill(
            manifest_path=manifest_path,
            source=args.source,
            name=args.name,
            description=args.description,
            destination=args.dest,
            deploy=args.deploy,
            root_dir=repo_root,
        )
        sys.exit(0 if success else 1)

    try:
        skills = load_manifest(manifest_path)
    except Exception as err:
        print(f"Failed to load manifest: {err}", file=sys.stderr)
        sys.exit(1)

    if args.list:
        print(f"Skills in manifest ({len(skills)} found):")
        for idx, raw_skill in enumerate(skills, start=1):
            skill = normalize_skill(raw_skill)
            status = "enabled" if skill["enabled"] else "disabled"
            desc = skill["description"] or "No description"
            print(f"  {idx}. {skill['name']} [{status}] - {desc}")
            print(f"     Source: {skill['source']}")
            print(f"     Target: {skill['destination']}")
        return

    if args.name:
        matched = [s for s in skills if normalize_skill(s)["name"] == args.name]
        if not matched:
            print(f"Skill '{args.name}' not found in manifest.", file=sys.stderr)
            sys.exit(1)
        success = fetch_skill(matched[0], repo_root)
        sys.exit(0 if success else 1)

    if args.all:
        count = fetch_all_skills(skills, repo_root, force=args.force)
        print(f"\nSuccessfully fetched {count} skill(s).")
    else:
        print("Specify 'add <source>', '--all', '--name <name>', or '--list'. Use -h for help.")


if __name__ == "__main__":
    main()
