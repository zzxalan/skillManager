#!/usr/bin/env python3
"""Validate local Agent Skills and the repo-local plugin manifest."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class Reporter:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)


def parse_frontmatter(path: Path, reporter: Reporter) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        reporter.error(f"{path}: SKILL.md 必须以 YAML frontmatter 开头")
        return {}

    try:
        end = lines.index("---", 1)
    except ValueError:
        reporter.error(f"{path}: YAML frontmatter 缺少结束分隔符 ---")
        return {}

    data: dict[str, str] = {}
    current_key: str | None = None
    for raw_line in lines[1:end]:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        if raw_line.startswith((" ", "\t")):
            if current_key and current_key in data:
                data[current_key] = f"{data[current_key]} {raw_line.strip()}".strip()
            continue

        if ":" not in raw_line:
            reporter.error(f"{path}: frontmatter 行格式无效: {raw_line}")
            continue

        key, value = raw_line.split(":", 1)
        current_key = key.strip()
        data[current_key] = value.strip().strip("'\"")

    return data


def skill_dirs(skills_root: Path) -> list[Path]:
    if not skills_root.exists():
        return []
    return sorted(
        path
        for path in skills_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )


def validate_skill(skill_dir: Path, reporter: Reporter) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        reporter.warning(f"{skill_dir}: 缺少 SKILL.md，已跳过")
        return

    data = parse_frontmatter(skill_md, reporter)
    name = data.get("name", "")
    description = data.get("description", "")

    if not name:
        reporter.error(f"{skill_md}: 缺少 name")
    elif not NAME_RE.match(name):
        reporter.error(f"{skill_md}: name 必须是小写字母、数字和连字符，且不能以连字符开头或结尾")
    elif len(name) > 64:
        reporter.error(f"{skill_md}: name 长度不能超过 64")
    elif name != skill_dir.name:
        reporter.error(f"{skill_md}: name `{name}` 必须和目录名 `{skill_dir.name}` 一致")

    if not description:
        reporter.error(f"{skill_md}: 缺少 description")
    elif len(description) > 1024:
        reporter.error(f"{skill_md}: description 长度不能超过 1024")
    elif len(description.split()) < 8:
        reporter.warning(f"{skill_md}: description 过短，可能影响自动触发")

    line_count = len(skill_md.read_text(encoding="utf-8").splitlines())
    if line_count > 500:
        reporter.warning(f"{skill_md}: 超过 500 行，建议拆分到 references/")


def validate_plugin(plugin_root: Path, reporter: Reporter) -> list[Path]:
    manifest = plugin_root / ".codex-plugin" / "plugin.json"
    if not manifest.exists():
        reporter.error(f"{manifest}: 缺少 plugin manifest")
        return []

    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        reporter.error(f"{manifest}: JSON 格式错误: {exc}")
        return []

    name = data.get("name", "")
    if not name:
        reporter.error(f"{manifest}: 缺少 name")
    elif not NAME_RE.match(name):
        reporter.error(f"{manifest}: name 必须使用 kebab-case")
    elif name != plugin_root.name:
        reporter.error(f"{manifest}: name `{name}` 必须和插件目录名 `{plugin_root.name}` 一致")

    skills_path = data.get("skills")
    if not skills_path:
        return []
    if not isinstance(skills_path, str) or not skills_path.startswith("./"):
        reporter.error(f"{manifest}: skills 路径必须是以 ./ 开头的相对路径")
        return []

    skills_root = (plugin_root / skills_path).resolve()
    if not skills_root.exists():
        reporter.error(f"{manifest}: skills 路径不存在: {skills_path}")
        return []

    return [skills_root]


def validate_marketplace(repo_root: Path, reporter: Reporter) -> None:
    marketplace = repo_root / ".agents" / "plugins" / "marketplace.json"
    if not marketplace.exists():
        reporter.warning(f"{marketplace}: 缺少 repo-local marketplace")
        return

    try:
        data = json.loads(marketplace.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        reporter.error(f"{marketplace}: JSON 格式错误: {exc}")
        return

    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        reporter.error(f"{marketplace}: plugins 必须是数组")
        return

    for index, plugin in enumerate(plugins):
        path = plugin.get("source", {}).get("path")
        name = plugin.get("name")
        if not path or not isinstance(path, str):
            reporter.error(f"{marketplace}: plugins[{index}] 缺少 source.path")
            continue
        if not path.startswith("./"):
            reporter.error(f"{marketplace}: plugins[{index}].source.path 必须以 ./ 开头")
            continue
        plugin_root = (repo_root / path).resolve()
        if not plugin_root.exists():
            reporter.error(f"{marketplace}: plugins[{index}] 路径不存在: {path}")
        elif name and plugin_root.name != name:
            reporter.error(f"{marketplace}: plugins[{index}] name `{name}` 必须和目录名 `{plugin_root.name}` 一致")

        policy = plugin.get("policy", {})
        if "installation" not in policy or "authentication" not in policy:
            reporter.error(f"{marketplace}: plugins[{index}] 必须包含 policy.installation 和 policy.authentication")
        if "category" not in plugin:
            reporter.error(f"{marketplace}: plugins[{index}] 缺少 category")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Agent Skills in this repository.")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root. Defaults to current directory.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    reporter = Reporter()
    skills_roots: list[Path] = []

    for plugin_root in sorted((repo_root / "plugins").glob("*")):
        if plugin_root.is_dir():
            skills_roots.extend(validate_plugin(plugin_root, reporter))

    validate_marketplace(repo_root, reporter)

    for skills_root in skills_roots:
        for skill_dir in skill_dirs(skills_root):
            validate_skill(skill_dir, reporter)

    if reporter.warnings:
        print("Warnings:")
        for item in reporter.warnings:
            print(f"  - {item}")

    if reporter.errors:
        print("Errors:")
        for item in reporter.errors:
            print(f"  - {item}")
        return 1

    checked = sum(len(skill_dirs(root)) for root in skills_roots)
    print(f"OK: plugin manifest 和 {checked} 个 skill 校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
