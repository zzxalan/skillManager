#!/usr/bin/env python3
"""生成 smart-mixed 初始插件项目。"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


PLUGIN_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
PACKAGE_RE = re.compile(r"^[a-z][a-z0-9]*$")


class UsageError(Exception):
    """用户输入错误。"""


@dataclass(frozen=True)
class PluginConfig:
    plugin_name: str
    display_name: str
    base_version: str
    output_dir: Path
    java_package_fragment: str

    @property
    def project_dir_name(self) -> str:
        return f"smart-{self.plugin_name}-mixed"

    @property
    def target_dir(self) -> Path:
        return self.output_dir / self.project_dir_name

    @property
    def app_name(self) -> str:
        return self.plugin_name

    @property
    def app_code(self) -> str:
        return self.plugin_name.replace("-", "_")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成 smart-mixed 初始插件项目")
    parser.add_argument("--plugin-name", help="插件 ID，使用 kebab-case，例如 access-control")
    parser.add_argument("--display-name", help="插件中文展示名")
    parser.add_argument("--base-version", help="smart-core 版本，写入 outbook-core")
    parser.add_argument("--output-dir", help="输出父目录，脚本会在其下创建 smart-<插件名称>-mixed")
    parser.add_argument("--java-package-fragment", help="Java 包名片段，默认去掉插件 ID 中的连字符")
    parser.add_argument("--dry-run", action="store_true", help="只输出将创建的路径，不写入文件")
    parser.add_argument("--force", action="store_true", help="目标项目目录存在时先删除再生成")
    parser.add_argument("--yes", action="store_true", help="跳过脚本内确认")
    return parser.parse_args(argv)


def prompt_missing(value: str | None, label: str, arg_name: str) -> str:
    if value:
        return value.strip()
    if not sys.stdin.isatty():
        raise UsageError(f"缺少参数：{arg_name}")
    raw = input(f"{label}: ").strip()
    if not raw:
        raise UsageError(f"{label}不能为空")
    return raw


def normalize_config(args: argparse.Namespace) -> PluginConfig:
    plugin_name = prompt_missing(args.plugin_name, "插件名称", "--plugin-name")
    display_name = prompt_missing(args.display_name, "中文名称", "--display-name")
    base_version = prompt_missing(args.base_version, "smart-core 版本", "--base-version")
    output_dir_raw = prompt_missing(args.output_dir, "输出父目录", "--output-dir")
    java_package_fragment = (
        args.java_package_fragment.strip().lower()
        if args.java_package_fragment
        else plugin_name.replace("-", "")
    )

    if not PLUGIN_RE.fullmatch(plugin_name):
        raise UsageError("插件名称必须使用 kebab-case，且以小写字母开头")
    if not display_name:
        raise UsageError("中文名称不能为空")
    if not base_version:
        raise UsageError("smart-core 版本不能为空")
    if not PACKAGE_RE.fullmatch(java_package_fragment):
        raise UsageError("Java 包名片段只能包含小写字母和数字，且必须以小写字母开头")

    return PluginConfig(
        plugin_name=plugin_name,
        display_name=display_name,
        base_version=base_version,
        output_dir=Path(output_dir_raw).expanduser().resolve(),
        java_package_fragment=java_package_fragment,
    )


def print_summary(config: PluginConfig) -> None:
    print("生成确认摘要：")
    print(f"  生成目录: {config.target_dir}")
    print(f"  插件 ID: {config.plugin_name}")
    print(f"  中文名称: {config.display_name}")
    print(f"  Java 包名片段: {config.java_package_fragment}")
    print(f"  前端 app name: {config.app_name}")
    print(f"  smart-core 版本: {config.base_version}")


def ask_confirmation() -> bool:
    if not sys.stdin.isatty():
        raise UsageError("未传入 --yes，且当前环境无法交互确认")
    answer = input("确认生成？请输入 yes 或 确认: ").strip().lower()
    return answer in {"yes", "y", "确认"}


def replace_tokens(value: str, replacements: dict[str, str]) -> str:
    result = value
    for token, replacement in replacements.items():
        result = result.replace(token, replacement)
    return result


def copy_template(template_dir: Path, target_dir: Path, replacements: dict[str, str]) -> None:
    for source in sorted(template_dir.rglob("*")):
        relative = source.relative_to(template_dir)
        rendered_parts = [replace_tokens(part, replacements) for part in relative.parts]
        destination = target_dir.joinpath(*rendered_parts)

        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        raw = source.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            destination.write_bytes(raw)
            shutil.copymode(source, destination)
            continue

        destination.write_text(replace_tokens(text, replacements), encoding="utf-8")
        shutil.copymode(source, destination)


def generate(config: PluginConfig, force: bool) -> None:
    skill_root = Path(__file__).resolve().parents[1]
    template_dir = skill_root / "assets" / "templates" / "smart-mixed-plugin"
    if not template_dir.exists():
        raise UsageError(f"模板目录不存在：{template_dir}")

    if config.target_dir.exists():
        if not force:
            raise UsageError(f"目标目录已存在，默认不覆盖：{config.target_dir}")
        shutil.rmtree(config.target_dir)

    config.output_dir.mkdir(parents=True, exist_ok=True)
    replacements = {
        "__PLUGIN_ID__": config.plugin_name,
        "__DISPLAY_NAME__": config.display_name,
        "__BASE_VERSION__": config.base_version,
        "__JAVA_PACKAGE_FRAGMENT__": config.java_package_fragment,
        "__APP_NAME__": config.app_name,
        "__APP_CODE__": config.app_code,
    }
    copy_template(template_dir, config.target_dir, replacements)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        config = normalize_config(args)
        print_summary(config)

        if args.dry_run:
            print("dry-run 模式：未写入任何文件。")
            return 0

        if not args.yes and not ask_confirmation():
            print("已取消生成。")
            return 0

        generate(config, force=args.force)
        print(f"已生成项目：{config.target_dir}")
        print("建议后续验证：")
        print(f"  cd {config.target_dir / 'frontend'} && pnpm install && pnpm build")
        print(f"  cd {config.target_dir / 'backend'} && ./gradlew build")
        return 0
    except UsageError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"文件系统错误：{exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
