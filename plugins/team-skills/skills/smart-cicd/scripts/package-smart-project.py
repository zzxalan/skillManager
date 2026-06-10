#!/usr/bin/env python3
"""Run the smart backend Gradle publish command for a local project."""

from __future__ import annotations

import argparse
import os
import pathlib
import shutil
import subprocess
import sys


DEFAULT_SEARCH_ROOTS = [
    pathlib.Path.cwd(),
    pathlib.Path.cwd().parent,
    pathlib.Path.home() / "code",
]


class PackageError(RuntimeError):
    pass


def normalize_branch(value: str) -> str:
    branch = value.strip().lower()
    if branch in {"develop", "dev"}:
        return "develop"
    if branch in {"release", "master", "main"} or branch.startswith("release/"):
        return "release"
    if branch == "auto":
        return "auto"
    raise PackageError("branch 只能是 develop 或 release；master/main 会映射为 release。")


def run_git_branch(path: pathlib.Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--abbrev-ref", "HEAD"],
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def infer_branch(project_dir: pathlib.Path, backend_dir: pathlib.Path) -> str:
    for path in (project_dir, backend_dir):
        git_branch = run_git_branch(path)
        if not git_branch:
            continue
        lower = git_branch.lower()
        if lower == "develop" or lower.startswith("develop/"):
            return "develop"
        if lower in {"master", "main", "release"} or lower.startswith("release/"):
            return "release"
    raise PackageError("无法根据 Git 当前分支推断发布分支，请显式传入 --branch develop 或 --branch release。")


def split_search_roots(values: list[str] | None) -> list[pathlib.Path]:
    roots: list[pathlib.Path] = []
    env_roots = os.environ.get("SMART_CICD_PROJECT_ROOTS", "")
    for raw in env_roots.split(os.pathsep):
        if raw.strip():
            roots.append(pathlib.Path(raw).expanduser())
    for raw in values or []:
        if raw.strip():
            roots.append(pathlib.Path(raw).expanduser())
    roots.extend(DEFAULT_SEARCH_ROOTS)

    unique: list[pathlib.Path] = []
    seen: set[pathlib.Path] = set()
    for root in roots:
        resolved = root.resolve() if root.exists() else root
        if resolved not in seen:
            unique.append(root)
            seen.add(resolved)
    return unique


def candidate_names(name: str) -> list[str]:
    normalized = name.strip().rstrip("/")
    base = pathlib.Path(normalized).name
    names = [
        base,
        f"smart-{base}",
        f"smart-{base}-mixed",
        f"smart-{base}-plugin",
    ]
    if base.startswith("smart-"):
        names.append(base.removeprefix("smart-"))
    return list(dict.fromkeys(names))


def find_project_dir(project: str, search_roots: list[pathlib.Path]) -> pathlib.Path:
    project_path = pathlib.Path(project).expanduser()
    if project_path.exists():
        return project_path.resolve()

    names = set(candidate_names(project))
    matches: list[pathlib.Path] = []
    for root in search_roots:
        root = root.expanduser()
        for name in names:
            direct = root / name
            if direct.is_dir():
                matches.append(direct.resolve())
        if root.is_dir():
            try:
                for child in root.iterdir():
                    if child.is_dir() and child.name in names:
                        matches.append(child.resolve())
            except PermissionError:
                continue

    matches = sorted(set(matches))
    if not matches:
        roots = ", ".join(str(root) for root in search_roots)
        raise PackageError(f"找不到项目目录：{project}。已搜索：{roots}")
    if len(matches) > 1:
        options = "\n".join(f"- {match}" for match in matches)
        raise PackageError(f"找到多个候选项目目录，请直接传完整路径：\n{options}")
    return matches[0]


def find_backend_dir(project_dir: pathlib.Path) -> pathlib.Path:
    if project_dir.name == "backend" and (project_dir / "gradlew").exists():
        return project_dir
    backend = project_dir / "backend"
    if backend.is_dir() and (backend / "gradlew").exists():
        return backend
    if (project_dir / "gradlew").exists():
        return project_dir
    raise PackageError(f"找不到后端 Gradle 目录：{project_dir}/backend，且项目根目录也没有 gradlew。")


def find_frontend_dir(project_dir: pathlib.Path, skip_frontend: bool) -> pathlib.Path | None:
    if skip_frontend:
        return None
    candidates = [
        project_dir / "frontend",
        project_dir / "front",
        project_dir / "web",
    ]
    if (project_dir / "package.json").exists():
        candidates.append(project_dir)
    for candidate in candidates:
        if candidate.is_dir() and (candidate / "package.json").exists():
            return candidate
    raise PackageError(f"找不到前端目录：{project_dir}/frontend，无法先执行 pnpm build。")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package a smart backend project with Gradle.")
    parser.add_argument("project", help="项目目录名或路径，例如 activity 或 ~/code/activity")
    parser.add_argument("--branch", default="auto", help="develop、release、master、main；默认根据 Git 分支推断")
    parser.add_argument("--search-root", action="append", help="额外搜索项目目录的根路径，可重复传入")
    parser.add_argument("--dry-run", action="store_true", help="只打印将执行的命令，不真正打包")
    parser.add_argument("--skip-frontend", action="store_true", help="跳过前端 pnpm build，仅在用户明确要求时使用")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        branch = normalize_branch(args.branch)
        search_roots = split_search_roots(args.search_root)
        project_dir = find_project_dir(args.project, search_roots)
        frontend_dir = find_frontend_dir(project_dir, args.skip_frontend)
        backend_dir = find_backend_dir(project_dir)
        if branch == "auto":
            branch = infer_branch(project_dir, backend_dir)

        gradlew = backend_dir / "gradlew"
        frontend_command = ["pnpm", "build"]
        backend_command = [
            "./gradlew",
            "clean",
            "发布",
            "--refresh-dependencies",
            f"-Pbranch={branch}",
        ]
        print(f"[PROJECT] {project_dir}")
        if frontend_dir:
            print(f"[FRONTEND] {frontend_dir}")
        print(f"[BACKEND] {backend_dir}")
        print(f"[BRANCH] {branch}")
        if frontend_dir:
            print("[FRONTEND COMMAND] " + " ".join(frontend_command))
        print("[BACKEND COMMAND] " + " ".join(backend_command))
        if args.dry_run:
            print("[DRY-RUN] 未执行前端构建和 Gradle 打包。")
            return 0
        if frontend_dir and not shutil.which("pnpm"):
            raise PackageError("找不到 pnpm，请先安装或配置 pnpm。")
        if not gradlew.exists():
            raise PackageError(f"gradlew 不存在：{gradlew}")
        if not os.access(gradlew, os.X_OK):
            raise PackageError(f"gradlew 没有执行权限：{gradlew}，请先执行 chmod +x。")

        if frontend_dir:
            print("[BUILD] 开始执行 pnpm build")
            frontend_result = subprocess.run(frontend_command, cwd=str(frontend_dir), check=False)
            if frontend_result.returncode != 0:
                raise PackageError(f"前端 pnpm build 失败，退出码：{frontend_result.returncode}")

        print("[PACKAGE] 开始执行 Gradle 发布")
        completed = subprocess.run(backend_command, cwd=str(backend_dir), check=False)
        if completed.returncode != 0:
            raise PackageError(f"Gradle 打包失败，退出码：{completed.returncode}")
        print("[DONE] 打包发布完成。")
        return 0
    except PackageError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
