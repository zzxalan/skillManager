#!/usr/bin/env python3
"""Download master/release packages from the smart Nexus repository."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
import zipfile
from types import ModuleType


SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
DEPLOY_SCRIPT = SCRIPT_DIR / "deploy-smart-package.py"


class DownloadError(RuntimeError):
    pass


def load_deploy_helpers() -> ModuleType:
    spec = importlib.util.spec_from_file_location("smart_cicd_deploy_helpers", DEPLOY_SCRIPT)
    if not spec or not spec.loader:
        raise DownloadError(f"无法加载部署脚本：{DEPLOY_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


deploy_helpers = load_deploy_helpers()


def safe_package_parts(path: str) -> list[str]:
    pure_path = pathlib.PurePosixPath(path)
    parts: list[str] = []
    for part in pure_path.parts:
        if part in {"", ".", "/"}:
            continue
        if part == "..":
            raise DownloadError(f"Nexus 包路径不安全：{path}")
        parts.append(part)
    if not parts:
        raise DownloadError(f"Nexus 包路径为空：{path}")
    return parts


def safe_file_name(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip(".-")
    if name in {"", ".", ".."}:
        return "package"
    return name


def split_known_suffix(filename: str) -> tuple[str, str]:
    lower = filename.lower()
    for suffix in sorted(deploy_helpers.DEFAULT_EXTENSIONS, key=len, reverse=True):
        if lower.endswith(suffix):
            return filename[: -len(suffix)], filename[-len(suffix) :]
    path = pathlib.PurePosixPath(filename)
    if path.suffix:
        return filename[: -len(path.suffix)], path.suffix
    return filename, ""


def path_based_file_name(path: str) -> str:
    parts = safe_package_parts(path)
    filename = safe_file_name(parts[-1])
    if len(parts) == 1:
        return filename
    stem, suffix = split_known_suffix(filename)
    prefix = "-".join(safe_file_name(part) for part in parts[:-1])
    return f"{prefix}-{stem}{suffix}"


def unique_file_name(candidate: str, path: str, used: dict[str, str]) -> str:
    if candidate.lower() == "manifest.json":
        stem, suffix = split_known_suffix(candidate)
        candidate = f"{stem}-{hashlib.sha1(path.encode('utf-8')).hexdigest()[:8]}{suffix}"
    if candidate not in used or used[candidate] == path:
        used[candidate] = path
        return candidate

    stem, suffix = split_known_suffix(candidate)
    digest = hashlib.sha1(path.encode("utf-8")).hexdigest()[:8]
    renamed = f"{stem}-{digest}{suffix}"
    index = 2
    while renamed in used and used[renamed] != path:
        renamed = f"{stem}-{digest}-{index}{suffix}"
        index += 1
    used[renamed] = path
    return renamed


def flat_download_names(assets: list) -> dict[str, str]:
    filename_counts: dict[str, int] = {}
    base_names: dict[str, str] = {}
    for asset in assets:
        filename = safe_file_name(safe_package_parts(asset.path)[-1])
        base_names[asset.path] = filename
        filename_counts[filename] = filename_counts.get(filename, 0) + 1

    used: dict[str, str] = {}
    names: dict[str, str] = {}
    for asset in assets:
        base_name = base_names[asset.path]
        candidate = base_name
        if filename_counts[base_name] > 1:
            candidate = path_based_file_name(asset.path)
        names[asset.path] = unique_file_name(candidate, asset.path, used)
    return names


def safe_dir_name(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip().lower()).strip("-")
    return name or "packages"


def is_relative_to(path: pathlib.Path, parent: pathlib.Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def default_output_dir(branch: str) -> pathlib.Path:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return pathlib.Path.home() / "Downloads" / f"smart-package-{safe_dir_name(branch)}-{stamp}"


def archive_path_for(output_dir: pathlib.Path) -> pathlib.Path:
    return output_dir.parent / f"{output_dir.name}.zip"


def collect_assets(
    raw_assets: list[dict],
    branch: str,
    extensions: tuple[str, ...],
    all_files: bool,
    include_regex: str | None,
    base_regex: str,
    plugin_regex: str,
    unknown_kind: str,
    latest_only: bool,
) -> list:
    results = []
    include_pattern = re.compile(include_regex, re.IGNORECASE) if include_regex else None

    for item in raw_assets:
        path = str(item.get("path") or "")
        download_url = str(item.get("downloadUrl") or "")
        candidate = f"{path} {download_url}"
        if not path or not download_url:
            continue
        if include_pattern:
            if not include_pattern.search(candidate):
                continue
        elif not deploy_helpers.matches_branch(candidate, branch):
            continue
        if not all_files and not deploy_helpers.has_deployable_extension(path, extensions):
            continue
        kind = deploy_helpers.classify_asset(path, base_regex, plugin_regex, unknown_kind)
        results.append(deploy_helpers.Asset(path=path, download_url=download_url, kind=kind))

    if latest_only:
        results = deploy_helpers.select_latest_assets(results, branch)
    return sorted(results, key=lambda item: (item.kind, item.path))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download all master/release packages from Nexus smart-package.",
    )
    parser.add_argument(
        "--branch",
        default="master",
        help="分支过滤；master 会同时匹配 Nexus 中的 master 和 release，默认 master",
    )
    parser.add_argument("--nexus-url", default=deploy_helpers.DEFAULT_NEXUS_URL)
    parser.add_argument("--repository", default=deploy_helpers.DEFAULT_REPOSITORY)
    parser.add_argument("--nexus-username", default=deploy_helpers.DEFAULT_NEXUS_USERNAME)
    parser.add_argument("--nexus-password", default=deploy_helpers.DEFAULT_NEXUS_PASSWORD)
    parser.add_argument("--include-regex", help="覆盖默认分支过滤，按路径或下载地址匹配")
    parser.add_argument(
        "--extensions",
        default=",".join(deploy_helpers.DEFAULT_EXTENSIONS),
        help="逗号分隔的包后缀；默认 jar,war,zip,tar.gz,tgz,tar",
    )
    parser.add_argument("--all-files", action="store_true", help="不过滤文件后缀")
    version_group = parser.add_mutually_exclusive_group()
    version_group.add_argument(
        "--latest-only",
        dest="latest_only",
        action="store_true",
        default=True,
        help="每个模块只下载最新版本，默认启用",
    )
    version_group.add_argument(
        "--all-versions",
        dest="latest_only",
        action="store_false",
        help="下载所有匹配历史版本",
    )
    parser.add_argument("--base-regex", default=deploy_helpers.DEFAULT_BASE_REGEX)
    parser.add_argument("--plugin-regex", default=deploy_helpers.DEFAULT_PLUGIN_REGEX)
    parser.add_argument("--unknown-kind", choices=["plugin", "base", "fail"], default="plugin")
    parser.add_argument("--output-dir", help="下载输出目录；默认写入 ~/Downloads/smart-package-master-时间戳")
    parser.add_argument("--archive-path", help="压缩包输出路径；默认与输出目录同级，后缀 .zip")
    parser.add_argument("--no-archive", action="store_true", help="只下载目录，不生成 zip 压缩包")
    parser.add_argument("--with-manifest", action="store_true", help="额外生成 manifest.json 清单")
    parser.add_argument("--dry-run", action="store_true", help="只列出将下载的包，不创建目录、不下载")
    overwrite_group = parser.add_mutually_exclusive_group()
    overwrite_group.add_argument("--overwrite", action="store_true", help="覆盖已存在的同名文件和压缩包")
    overwrite_group.add_argument("--skip-existing", action="store_true", help="遇到已存在文件时跳过下载")
    return parser.parse_args()


def print_summary(
    branch: str,
    base_url: str,
    repository: str,
    output_dir: pathlib.Path,
    archive_path: pathlib.Path | None,
    assets: list,
    local_names: dict[str, str],
    latest_only: bool,
    with_manifest: bool,
    dry_run: bool,
) -> None:
    mode = "预览模式" if dry_run else "下载模式"
    channels = ", ".join(deploy_helpers.branch_channels(branch))
    base_count = sum(1 for asset in assets if asset.kind == "base")
    plugin_count = sum(1 for asset in assets if asset.kind == "plugin")
    print(f"[SUMMARY] {mode}")
    print(f"- Nexus：{base_url}")
    print(f"- 仓库：{repository}")
    print(f"- 分支：{branch} (匹配：{channels})")
    print(f"- 版本范围：{'每个模块最新包' if latest_only else '所有历史版本'}")
    print(f"- 包数量：{len(assets)}，基座包：{base_count}，插件包：{plugin_count}")
    print("- 打包结构：压缩包内一层目录，所有包位于该目录内")
    print(f"- 清单文件：{'生成 manifest.json' if with_manifest else '不生成'}")
    print(f"- 输出目录：{output_dir}")
    if archive_path:
        print(f"- 压缩包：{archive_path}")
    for asset in assets:
        label = "基座" if asset.kind == "base" else "插件"
        local_name = local_names.get(asset.path, asset.filename)
        rename_text = f" -> {local_name}" if local_name != asset.filename else ""
        print(f"  [{label}] {asset.path}{rename_text}")


def write_manifest(
    manifest_path: pathlib.Path,
    branch: str,
    base_url: str,
    repository: str,
    assets: list,
    downloaded_files: dict[str, pathlib.Path],
    output_dir: pathlib.Path,
) -> None:
    items: list[dict[str, object]] = []
    for asset in assets:
        local_path = downloaded_files.get(asset.path)
        item: dict[str, object] = {
            "path": asset.path,
            "filename": asset.filename,
            "kind": asset.kind,
            "downloadUrl": asset.download_url,
        }
        if local_path:
            item["localFilename"] = local_path.name
            item["localPath"] = local_path.relative_to(output_dir).as_posix()
            item["size"] = local_path.stat().st_size
        items.append(item)

    payload = {
        "generatedAt": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "nexusUrl": base_url,
        "repository": repository,
        "branch": branch,
        "branchChannels": list(deploy_helpers.branch_channels(branch)),
        "count": len(assets),
        "assets": items,
    }
    manifest_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def create_archive(
    output_dir: pathlib.Path,
    archive_path: pathlib.Path,
    overwrite: bool,
    files: list[pathlib.Path],
) -> None:
    if is_relative_to(archive_path, output_dir):
        raise DownloadError("压缩包路径不能放在输出目录内部，否则会把压缩包自身打进去。")
    if archive_path.exists() and not overwrite:
        raise DownloadError(f"压缩包已存在：{archive_path}，如需覆盖请加 --overwrite。")
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr(f"{output_dir.name}/", "")
        for child in sorted(files):
            if not child.is_file():
                raise DownloadError(f"压缩文件不存在或不是普通文件：{child}")
            if not is_relative_to(child, output_dir):
                raise DownloadError(f"压缩文件不在输出目录中：{child}")
            archive.write(child, arcname=f"{output_dir.name}/{child.name}")


def main() -> int:
    args = parse_args()
    try:
        branch = args.branch.strip().lower()
        base_url = deploy_helpers.normalize_base_url(args.nexus_url)
        extensions = tuple(item.strip() for item in args.extensions.split(",") if item.strip())
        output_dir = pathlib.Path(args.output_dir).expanduser() if args.output_dir else default_output_dir(branch)
        output_dir = output_dir.resolve()
        archive_path = None
        if not args.no_archive:
            archive_path = (
                pathlib.Path(args.archive_path).expanduser().resolve()
                if args.archive_path
                else archive_path_for(output_dir).resolve()
            )

        print(f"[NEXUS] 读取仓库资产：{base_url} / {args.repository}")
        raw_assets = deploy_helpers.list_nexus_assets(
            base_url,
            args.repository,
            args.nexus_username,
            args.nexus_password,
        )
        assets = collect_assets(
            raw_assets,
            branch,
            extensions,
            args.all_files,
            args.include_regex,
            args.base_regex,
            args.plugin_regex,
            args.unknown_kind,
            args.latest_only,
        )
        if not assets:
            raise DownloadError(
                f"没有找到分支 {branch} 的包。请确认 Nexus 路径或文件名包含分支名，"
                "或使用 --include-regex 指定匹配规则。"
            )

        local_names = flat_download_names(assets)
        print_summary(
            branch,
            base_url,
            args.repository,
            output_dir,
            archive_path,
            assets,
            local_names,
            args.latest_only,
            args.with_manifest,
            args.dry_run,
        )
        if args.dry_run:
            print("[DRY-RUN] 未下载文件，也未生成压缩包。")
            return 0

        output_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = output_dir / "manifest.json"
        if args.with_manifest and manifest_path.exists() and not args.overwrite:
            raise DownloadError(f"清单文件已存在：{manifest_path}，如需覆盖请加 --overwrite。")
        if archive_path and archive_path.exists() and not args.overwrite:
            raise DownloadError(f"压缩包已存在：{archive_path}，如需覆盖请加 --overwrite。")

        downloaded_files: dict[str, pathlib.Path] = {}
        total = len(assets)
        for index, asset in enumerate(assets, start=1):
            local_path = output_dir / local_names[asset.path]
            if local_path.exists():
                if args.skip_existing:
                    print(f"[SKIP] {index}/{total} {asset.path}")
                    downloaded_files[asset.path] = local_path
                    continue
                if not args.overwrite:
                    raise DownloadError(f"文件已存在：{local_path}，如需覆盖请加 --overwrite。")
            print(f"[DOWNLOAD] {index}/{total} {asset.path}")
            deploy_helpers.download_file(
                asset.download_url,
                local_path,
                args.nexus_username,
                args.nexus_password,
            )
            downloaded_files[asset.path] = local_path

        if args.with_manifest:
            write_manifest(manifest_path, branch, base_url, args.repository, assets, downloaded_files, output_dir)
            print(f"[MANIFEST] {manifest_path}")

        if archive_path:
            print(f"[ARCHIVE] {archive_path}")
            archive_files = list(downloaded_files.values())
            if args.with_manifest:
                archive_files.append(manifest_path)
            create_archive(output_dir, archive_path, args.overwrite, archive_files)

        print("[DONE] master 包下载完成。")
        return 0
    except (DownloadError, deploy_helpers.DeployError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
