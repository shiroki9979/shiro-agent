#!/usr/bin/env python3
"""Fetch and update third-party skills from external sources."""

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any, Dict, List
import urllib.error
import urllib.request


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


def fetch_skill(skill: Dict[str, Any], root_dir: Path, timeout: int = 15) -> bool:
    """下載或複製單一第三方 Skill 至指定目錄。"""
    name = skill.get("name", "unnamed")
    source = skill.get("source")
    dest_rel = skill.get("destination")

    if not source or not dest_rel:
        print(f"Skipping {name}: missing 'source' or 'destination'")
        return False

    dest_path = root_dir / dest_rel
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Fetching '{name}' from {source}...")

    try:
        if source.startswith("http://") or source.startswith("https://"):
            req = urllib.request.Request(
                source,
                headers={"User-Agent": "shiro-agent-sync/1.0"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read()
                dest_path.write_bytes(content)
        else:
            # 本地檔案來源
            local_src = (root_dir / source).resolve()
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
        is_enabled = skill.get("enabled", True)
        if is_enabled or force:
            if fetch_skill(skill, root_dir):
                success_count += 1
        else:
            print(f"Skipping disabled skill: {skill.get('name')}")
    return success_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and sync third-party skills from manifest.")
    parser.add_argument(
        "--manifest",
        type=str,
        default="skills/manifest.json",
        help="Path to manifest JSON (default: skills/manifest.json)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all skills defined in manifest",
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Fetch a specific skill by name",
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

    try:
        skills = load_manifest(manifest_path)
    except Exception as err:
        print(f"Failed to load manifest: {err}", file=sys.stderr)
        sys.exit(1)

    if args.list:
        print(f"Skills in manifest ({len(skills)} found):")
        for idx, skill in enumerate(skills, start=1):
            status = "enabled" if skill.get("enabled", True) else "disabled"
            print(f"  {idx}. {skill.get('name')} [{status}] - {skill.get('description', 'No description')}")
            print(f"     Source: {skill.get('source')}")
            print(f"     Target: {skill.get('destination')}")
        return

    if args.name:
        matched = [s for s in skills if s.get("name") == args.name]
        if not matched:
            print(f"Skill '{args.name}' not found in manifest.", file=sys.stderr)
            sys.exit(1)
        success = fetch_skill(matched[0], repo_root)
        sys.exit(0 if success else 1)

    if args.all:
        count = fetch_all_skills(skills, repo_root, force=args.force)
        print(f"\nSuccessfully fetched {count} skill(s).")
    else:
        print("Specify --all, --name <name>, or --list. Use -h for help.")


if __name__ == "__main__":
    main()
