#!/usr/bin/env python3
"""检查 Smart Project Map 中的 app/appName 是否与插件配置一致。"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


UNCONFIGURED = "未配置"


class ValidationError(RuntimeError):
    """地图或插件配置无法校验。"""


@dataclass(frozen=True)
class MapEntry:
    project: str
    app: str
    app_name: str
    line_number: int


def parse_args(argv: list[str]) -> argparse.Namespace:
    default_map = Path(__file__).resolve().parents[1] / "references" / "project-map.md"
    parser = argparse.ArgumentParser(
        description="检查 project-map.md 与 smart-*-mixed/frontend/public/config.json 的一致性",
    )
    parser.add_argument(
        "--workspace",
        required=True,
        type=Path,
        help="包含 smart-*-mixed 目录的 smart 工作区根目录",
    )
    parser.add_argument(
        "--project-map",
        type=Path,
        default=default_map,
        help=f"项目地图路径，默认 {default_map}",
    )
    parser.add_argument(
        "--require-all",
        action="store_true",
        help="地图中的 mixed 工程未出现在工作区时也判定失败",
    )
    return parser.parse_args(argv)


def clean_cell(value: str) -> str:
    return value.strip().strip("`").strip()


def load_map(path: Path) -> dict[str, MapEntry]:
    if not path.is_file():
        raise ValidationError(f"项目地图不存在：{path}")

    entries: dict[str, MapEntry] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.startswith("|"):
            continue
        cells = [clean_cell(cell) for cell in line.strip().strip("|").split("|")]
        if len(cells) < 7:
            continue

        project = cells[3]
        if not (project.startswith("smart-") and project.endswith("-mixed")):
            continue
        if project in entries:
            previous = entries[project]
            raise ValidationError(
                f"地图重复登记 {project}：第 {previous.line_number} 行和第 {line_number} 行",
            )
        entries[project] = MapEntry(
            project=project,
            app=cells[0],
            app_name=cells[1],
            line_number=line_number,
        )

    if not entries:
        raise ValidationError(f"项目地图中未找到 mixed 工程清单：{path}")
    return entries


def load_config(path: Path) -> tuple[str, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"无法读取插件配置 {path}：{exc}") from exc

    app = payload.get("app")
    app_name = payload.get("appName")
    if not isinstance(app, str) or not app.strip():
        raise ValidationError(f"插件配置缺少有效的顶层 app：{path}")
    if not isinstance(app_name, str) or not app_name.strip():
        raise ValidationError(f"插件配置缺少有效的顶层 appName：{path}")
    return app, app_name


def validate(
    workspace: Path,
    entries: dict[str, MapEntry],
    require_all: bool,
) -> tuple[list[str], list[str]]:
    if not workspace.is_dir():
        raise ValidationError(f"smart 工作区不存在：{workspace}")

    errors: list[str] = []
    notes: list[str] = []
    discovered: set[str] = set()

    for project_dir in sorted(workspace.glob("smart-*-mixed")):
        if not project_dir.is_dir():
            continue
        project = project_dir.name
        discovered.add(project)
        entry = entries.get(project)
        if entry is None:
            errors.append(f"地图缺少工作区已存在的工程：{project}")
            continue

        config_path = project_dir / "frontend" / "public" / "config.json"
        if not config_path.is_file():
            if entry.app != UNCONFIGURED or entry.app_name != UNCONFIGURED:
                errors.append(
                    f"{project} 无 config.json，但地图第 {entry.line_number} 行登记为 "
                    f"app={entry.app!r}, appName={entry.app_name!r}",
                )
            continue

        try:
            app, app_name = load_config(config_path)
        except ValidationError as exc:
            errors.append(str(exc))
            continue

        if entry.app != app:
            errors.append(
                f"{project} app 不一致：地图第 {entry.line_number} 行为 {entry.app!r}，"
                f"配置为 {app!r}",
            )
        if entry.app_name != app_name:
            errors.append(
                f"{project} appName 不一致：地图第 {entry.line_number} 行为 {entry.app_name!r}，"
                f"配置为 {app_name!r}",
            )

    missing_projects = sorted(set(entries) - discovered)
    if missing_projects:
        message = "地图中的工程未出现在当前工作区：" + "、".join(missing_projects)
        if require_all:
            errors.append(message)
        else:
            notes.append(message)

    return errors, notes


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        project_map = args.project_map.expanduser().resolve()
        workspace = args.workspace.expanduser().resolve()
        entries = load_map(project_map)
        errors, notes = validate(workspace, entries, args.require_all)
    except ValidationError as exc:
        print(f"校验失败：{exc}", file=sys.stderr)
        return 2

    for note in notes:
        print(f"提示：{note}")
    if errors:
        for error in errors:
            print(f"错误：{error}", file=sys.stderr)
        print(f"校验失败：共 {len(errors)} 个问题。", file=sys.stderr)
        return 1

    print(f"校验通过：{len(entries)} 个 mixed 工程与当前配置一致。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
