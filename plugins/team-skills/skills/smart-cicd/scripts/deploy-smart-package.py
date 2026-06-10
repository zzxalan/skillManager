#!/usr/bin/env python3
"""Deploy smart base and plugin packages from Nexus to an internal server."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import pathlib
import pty
import re
import select
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


TARGETS = {
    "201": {"host": "192.168.50.201", "branch": "develop"},
    "192.168.50.201": {"host": "192.168.50.201", "branch": "develop"},
    "188": {"host": "192.168.50.188", "branch": "master"},
    "192.168.50.188": {"host": "192.168.50.188", "branch": "master"},
    "124": {"host": "192.168.50.124", "branch": "master"},
    "192.168.50.124": {"host": "192.168.50.124", "branch": "master"},
}

DEFAULT_NEXUS_URL = os.environ.get("SMART_CICD_NEXUS_URL", "http://192.168.50.122:8081")
DEFAULT_REPOSITORY = os.environ.get("SMART_CICD_NEXUS_REPOSITORY", "smart-package")
DEFAULT_NEXUS_USERNAME = os.environ.get("SMART_CICD_NEXUS_USERNAME", "admin")
DEFAULT_NEXUS_PASSWORD = os.environ.get("SMART_CICD_NEXUS_PASSWORD", "admin")
DEFAULT_SSH_USERNAME = os.environ.get("SMART_CICD_SSH_USERNAME", "root")
DEFAULT_SSH_PASSWORD = os.environ.get("SMART_CICD_SSH_PASSWORD", "root")

DEFAULT_BASE_DIR = os.environ.get("SMART_CICD_BASE_DIR", "/data/smart/app")
DEFAULT_PLUGIN_DIR = os.environ.get("SMART_CICD_PLUGIN_DIR", "/data/smart/app/plugins")
DEFAULT_LOG_DIR = os.environ.get("SMART_CICD_LOG_DIR", "/data/smart/app/logs")
DEFAULT_SERVICE = os.environ.get("SMART_CICD_SERVICE", "smart-server")

DEFAULT_BASE_REGEX = os.environ.get(
    "SMART_CICD_BASE_REGEX",
    r"(^|[/_.-])(base|app|smart-server|smart-core|outbook-core)([/_.-]|$)",
)
DEFAULT_PLUGIN_REGEX = os.environ.get(
    "SMART_CICD_PLUGIN_REGEX",
    r"(^|[/_.-])plugins?([/_.-]|$)|(^|[/_.-]).*plugin.*([/_.-]|$)",
)
DEFAULT_EXTENSIONS = (
    ".jar",
    ".war",
    ".zip",
    ".tar.gz",
    ".tgz",
    ".tar",
)
BRANCH_CHANNELS = {
    "master": ("master", "release"),
    "release": ("release",),
    "develop": ("develop",),
}


@dataclass(frozen=True)
class Asset:
    path: str
    download_url: str
    kind: str

    @property
    def filename(self) -> str:
        return pathlib.PurePosixPath(self.path).name


class DeployError(RuntimeError):
    pass


def normalize_base_url(value: str) -> str:
    base = value.split("#", 1)[0].rstrip("/")
    if not base:
        raise DeployError(f"Nexus 地址无效：{value}")
    return base


def basic_auth_header(username: str, password: str) -> dict[str, str]:
    raw = f"{username}:{password}".encode("utf-8")
    token = base64.b64encode(raw).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def http_json(url: str, username: str, password: str) -> dict:
    request = urllib.request.Request(url, headers=basic_auth_header(username, password))
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise DeployError(f"Nexus API 请求失败：HTTP {exc.code} {url}\n{body}") from exc
    except urllib.error.URLError as exc:
        raise DeployError(f"Nexus API 无法访问：{url}\n{exc}") from exc


def list_nexus_assets(base_url: str, repository: str, username: str, password: str) -> list[dict]:
    assets: list[dict] = []
    continuation = None
    while True:
        params = {"repository": repository}
        if continuation:
            params["continuationToken"] = continuation
        query = urllib.parse.urlencode(params)
        url = f"{base_url}/service/rest/v1/search/assets?{query}"
        payload = http_json(url, username, password)
        assets.extend(payload.get("items", []))
        continuation = payload.get("continuationToken")
        if not continuation:
            return assets


def has_deployable_extension(path: str, extensions: tuple[str, ...]) -> bool:
    lower = path.lower()
    return any(lower.endswith(ext.lower()) for ext in extensions)


def classify_asset(path: str, base_regex: str, plugin_regex: str, unknown_kind: str) -> str:
    if re.search(base_regex, path, re.IGNORECASE):
        return "base"
    if re.search(plugin_regex, path, re.IGNORECASE):
        return "plugin"
    if unknown_kind == "fail":
        raise DeployError(f"无法判断包类型：{path}")
    return unknown_kind


def branch_channels(branch: str) -> tuple[str, ...]:
    return BRANCH_CHANNELS.get(branch.lower(), (branch.lower(),))


def matches_branch(candidate: str, branch: str) -> bool:
    lower = candidate.lower()
    return any(channel in lower for channel in branch_channels(branch))


def version_tokens(text: str) -> list[str]:
    return re.findall(
        r"(?<![A-Za-z0-9])(\d+(?:\.\d+)+(?:[-_][A-Za-z][A-Za-z0-9]*)?)(?=$|[^A-Za-z0-9])",
        text,
    )


def parse_version(token: str) -> tuple[tuple[int, ...], int, str]:
    token = token.replace("_", "-")
    main, _, qualifier = token.partition("-")
    numbers = tuple(int(part) for part in main.split(".") if part.isdigit())
    qualifier_lower = qualifier.lower()
    stable_rank = 1 if not qualifier_lower else 0
    return numbers, stable_rank, qualifier_lower


def asset_sort_key(asset: Asset, branch: str) -> tuple[int, tuple[int, ...], int, str, str]:
    parts = asset.path.strip("/").split("/")
    channels = branch_channels(branch)
    filename_has_version = bool(version_tokens(asset.filename))
    direct_channel_file = (
        len(parts) == 3
        and parts[1].lower() in channels
        and not filename_has_version
    )
    if direct_channel_file:
        return 2, (999999,), 1, "", asset.path

    tokens = version_tokens(asset.path)
    if not tokens:
        return 0, (0,), 0, "", asset.path
    numbers, stable_rank, qualifier = parse_version(tokens[-1])
    return 1, numbers, stable_rank, qualifier, asset.path


def asset_group_key(asset: Asset, branch: str) -> tuple[str, str]:
    parts = asset.path.strip("/").split("/")
    channels = set(branch_channels(branch))
    for index, part in enumerate(parts):
        if part.lower() in channels and index > 0:
            return asset.kind, parts[index - 1]
    stem = pathlib.PurePosixPath(asset.filename).stem
    stem = re.sub(r"[-_](develop|master|release)[-_].*$", "", stem, flags=re.IGNORECASE)
    return asset.kind, stem


def select_latest_assets(assets: list[Asset], branch: str) -> list[Asset]:
    selected: dict[tuple[str, str], Asset] = {}
    for asset in assets:
        key = asset_group_key(asset, branch)
        if key not in selected:
            selected[key] = asset
            continue
        if asset_sort_key(asset, branch) > asset_sort_key(selected[key], branch):
            selected[key] = asset
    return list(selected.values())


def filter_assets(
    raw_assets: list[dict],
    branch: str,
    extensions: tuple[str, ...],
    all_files: bool,
    include_regex: str | None,
    base_regex: str,
    plugin_regex: str,
    unknown_kind: str,
    all_versions: bool,
) -> list[Asset]:
    results: list[Asset] = []
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
        elif not matches_branch(candidate, branch):
            continue
        if not all_files and not has_deployable_extension(path, extensions):
            continue
        kind = classify_asset(path, base_regex, plugin_regex, unknown_kind)
        results.append(Asset(path=path, download_url=download_url, kind=kind))

    if not all_versions:
        results = select_latest_assets(results, branch)

    dedupe: dict[tuple[str, str], Asset] = {}
    for asset in results:
        key = (asset.kind, asset.filename)
        if key in dedupe and dedupe[key].path != asset.path:
            raise DeployError(
                "发现同名部署目标，无法安全覆盖：\n"
                f"- {dedupe[key].path}\n"
                f"- {asset.path}\n"
                "请清理 Nexus 或使用 --include-regex 缩小范围。"
            )
        dedupe[key] = asset
    return sorted(dedupe.values(), key=lambda item: (item.kind, item.path))


def download_file(url: str, dest: pathlib.Path, username: str, password: str) -> None:
    request = urllib.request.Request(url, headers=basic_auth_header(username, password))
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            with dest.open("wb") as file:
                shutil.copyfileobj(response, file)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise DeployError(f"下载失败：HTTP {exc.code} {url}\n{body}") from exc
    except urllib.error.URLError as exc:
        raise DeployError(f"下载失败：{url}\n{exc}") from exc


class RemoteClient:
    def exec(self, command: str, check: bool = True) -> tuple[int, str, str]:
        raise NotImplementedError

    def put(self, local_path: pathlib.Path, remote_path: str) -> None:
        raise NotImplementedError

    def close(self) -> None:
        pass


class ParamikoRemoteClient(RemoteClient):
    def __init__(self, host: str, username: str, password: str) -> None:
        try:
            import paramiko  # type: ignore
        except ImportError as exc:
            raise DeployError("paramiko 不可用") from exc

        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._client.connect(
            hostname=host,
            username=username,
            password=password,
            look_for_keys=False,
            allow_agent=False,
            timeout=20,
        )
        self._sftp = self._client.open_sftp()

    def exec(self, command: str, check: bool = True) -> tuple[int, str, str]:
        stdin, stdout, stderr = self._client.exec_command(command)
        del stdin
        exit_code = stdout.channel.recv_exit_status()
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        if check and exit_code != 0:
            raise DeployError(f"远端命令失败({exit_code})：{command}\nSTDOUT:\n{out}\nSTDERR:\n{err}")
        return exit_code, out, err

    def put(self, local_path: pathlib.Path, remote_path: str) -> None:
        self._sftp.put(str(local_path), remote_path)

    def close(self) -> None:
        self._sftp.close()
        self._client.close()


class SshpassRemoteClient(RemoteClient):
    def __init__(self, host: str, username: str, password: str) -> None:
        if not shutil.which("sshpass"):
            raise DeployError(
                "缺少 SSH 依赖：请安装 paramiko 或 sshpass。\n"
                "示例：python3 -m pip install paramiko"
            )
        self.host = host
        self.username = username
        self.password = password
        self.target = f"{username}@{host}"
        self.options = [
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
        ]

    def _run(self, command: list[str], check: bool = True) -> tuple[int, str, str]:
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        if check and completed.returncode != 0:
            raise DeployError(
                f"本地 SSH 命令失败({completed.returncode})：{' '.join(shlex.quote(x) for x in command)}\n"
                f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )
        return completed.returncode, completed.stdout, completed.stderr

    def exec(self, command: str, check: bool = True) -> tuple[int, str, str]:
        cmd = ["sshpass", "-p", self.password, "ssh", *self.options, self.target, command]
        return self._run(cmd, check=check)

    def put(self, local_path: pathlib.Path, remote_path: str) -> None:
        cmd = [
            "sshpass",
            "-p",
            self.password,
            "scp",
            *self.options,
            str(local_path),
            f"{self.target}:{remote_path}",
        ]
        self._run(cmd)


class PtyRemoteClient(RemoteClient):
    def __init__(self, host: str, username: str, password: str) -> None:
        if not shutil.which("ssh") or not shutil.which("scp"):
            raise DeployError("缺少系统 ssh/scp 命令。")
        self.host = host
        self.username = username
        self.password = password
        self.target = f"{username}@{host}"
        self.options = [
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
        ]

    def _redact(self, text: str) -> str:
        return text.replace(self.password, "***") if self.password else text

    def _run(self, command: list[str], check: bool = True, timeout: int = 300) -> tuple[int, str, str]:
        master_fd, slave_fd = pty.openpty()
        proc = subprocess.Popen(
            command,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
        )
        os.close(slave_fd)

        output = bytearray()
        password_prompts = 0
        deadline = time.monotonic() + timeout
        try:
            while True:
                if time.monotonic() > deadline:
                    proc.kill()
                    raise DeployError(f"SSH 命令超时：{' '.join(shlex.quote(x) for x in command)}")

                ready, _, _ = select.select([master_fd], [], [], 0.2)
                if ready:
                    try:
                        chunk = os.read(master_fd, 4096)
                    except OSError:
                        chunk = b""
                    if chunk:
                        output.extend(chunk)
                        tail = output[-4096:].lower()
                        if b"are you sure you want to continue connecting" in tail:
                            os.write(master_fd, b"yes\n")
                        if b"password:" in tail and password_prompts < 3:
                            os.write(master_fd, (self.password + "\n").encode("utf-8"))
                            password_prompts += 1
                    elif proc.poll() is not None:
                        break

                if proc.poll() is not None:
                    while True:
                        ready, _, _ = select.select([master_fd], [], [], 0)
                        if not ready:
                            break
                        try:
                            chunk = os.read(master_fd, 4096)
                        except OSError:
                            break
                        if not chunk:
                            break
                        output.extend(chunk)
                    break
        finally:
            os.close(master_fd)

        exit_code = proc.wait()
        text = self._redact(output.decode("utf-8", errors="replace"))
        if check and exit_code != 0:
            raise DeployError(
                f"SSH 命令失败({exit_code})：{' '.join(shlex.quote(x) for x in command)}\n{text}"
            )
        return exit_code, text, ""

    def exec(self, command: str, check: bool = True) -> tuple[int, str, str]:
        cmd = ["ssh", *self.options, self.target, command]
        return self._run(cmd, check=check)

    def put(self, local_path: pathlib.Path, remote_path: str) -> None:
        cmd = ["scp", *self.options, str(local_path), f"{self.target}:{remote_path}"]
        self._run(cmd)


def connect_remote(host: str, username: str, password: str, backend: str) -> RemoteClient:
    if backend in {"auto", "paramiko"}:
        try:
            return ParamikoRemoteClient(host, username, password)
        except DeployError as exc:
            if backend == "paramiko":
                raise
            print(f"[WARN] paramiko 不可用，尝试 sshpass：{exc}", file=sys.stderr)
    if backend in {"auto", "sshpass"}:
        try:
            return SshpassRemoteClient(host, username, password)
        except DeployError as exc:
            if backend == "sshpass":
                raise
            print(f"[WARN] sshpass 不可用，尝试系统 ssh/scp：{exc}", file=sys.stderr)
    return PtyRemoteClient(host, username, password)


def q(value: str) -> str:
    return shlex.quote(value)


def remote_deploy(
    client: RemoteClient,
    downloads: list[tuple[Asset, pathlib.Path]],
    base_dir: str,
    plugin_dir: str,
    log_dir: str,
    service: str,
    wait_seconds: int,
    log_lines: int,
    clear_plugins: bool,
) -> None:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = f"{base_dir.rstrip('/')}/backups/deploy-{stamp}"
    remote_tmp = f"/tmp/smart-cicd-{stamp}"

    client.exec(
        "mkdir -p "
        f"{q(base_dir)} {q(plugin_dir)} {q(backup_dir)} {q(remote_tmp)}"
    )

    remote_files: list[tuple[Asset, str]] = []
    for index, (asset, local_path) in enumerate(downloads, start=1):
        tmp_name = f"{index:03d}-{asset.filename}"
        tmp_path = f"{remote_tmp}/{tmp_name}"
        print(f"[STAGE] {asset.path} -> {tmp_path}")
        client.put(local_path, tmp_path)
        remote_files.append((asset, tmp_path))

    has_plugin_packages = any(asset.kind == "plugin" for asset, _ in downloads)
    if has_plugin_packages and clear_plugins:
        plugin_backup_dir = f"{backup_dir}/plugins-before-clear"
        print(f"[CLEAR] backup and clear plugins: {plugin_dir}")
        client.exec(
            "set -e; "
            f"plugin_dir={q(plugin_dir.rstrip('/'))}; "
            f"backup={q(plugin_backup_dir)}; "
            "mkdir -p \"$plugin_dir\" \"$backup\"; "
            "if find \"$plugin_dir\" -mindepth 1 -maxdepth 1 | grep -q .; then "
            "cp -a \"$plugin_dir\"/. \"$backup\"/; "
            "find \"$plugin_dir\" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +; "
            "fi"
        )
    elif has_plugin_packages:
        print("[WARN] 已按参数跳过清空 plugins 目录，旧版本插件包可能残留。")

    for asset, tmp_path in remote_files:
        dest_dir = base_dir if asset.kind == "base" else plugin_dir
        dest_path = f"{dest_dir.rstrip('/')}/{asset.filename}"
        print(f"[INSTALL] {asset.path} -> {dest_path}")
        client.exec(
            "set -e; "
            f"dest={q(dest_path)}; "
            f"backup={q(backup_dir + '/' + asset.kind)}; "
            "mkdir -p \"$backup\"; "
            "if [ -e \"$dest\" ]; then cp -a \"$dest\" \"$backup\"/; fi; "
            f"install -m 0644 {q(tmp_path)} \"$dest\""
        )

    print(f"[RESTART] systemctl restart {service}")
    client.exec(f"systemctl restart {q(service)}")
    if wait_seconds > 0:
        time.sleep(wait_seconds)

    _, active_out, active_err = client.exec(f"systemctl is-active {q(service)}", check=False)
    active = (active_out or active_err).strip()
    print(f"[STATUS] {service}: {active}")

    log_command = (
        f"latest=$(ls -1t {q(log_dir)}/*.log 2>/dev/null | head -1); "
        "if [ -n \"$latest\" ]; then "
        "echo \"===== $latest =====\"; "
        f"tail -n {int(log_lines)} \"$latest\"; "
        "else echo \"未找到日志文件\"; fi"
    )
    _, log_out, log_err = client.exec(log_command, check=False)
    print("[LOGS]")
    print((log_out or log_err).rstrip())

    client.exec(f"rm -rf {q(remote_tmp)}", check=False)
    if active != "active":
        raise DeployError(f"{service} 重启后状态不是 active：{active}")


def resolve_target(target: str | None, branch_arg: str) -> tuple[str, str, str]:
    if not target:
        raise DeployError("缺少目标服务器，请传入 188、201、124 或完整 IP。")
    if target in TARGETS:
        mapped = TARGETS[target]
        branch = mapped["branch"] if branch_arg == "auto" else branch_arg
        return target, mapped["host"], branch
    if branch_arg == "auto":
        raise DeployError(f"未知服务器 {target}，请显式传入 --branch master 或 --branch develop。")
    return target, target, branch_arg


def print_summary(alias: str, host: str, branch: str, assets: list[Asset], execute: bool) -> None:
    base_count = sum(1 for asset in assets if asset.kind == "base")
    plugin_count = sum(1 for asset in assets if asset.kind == "plugin")
    mode = "执行部署" if execute else "预览模式"
    print(f"[SUMMARY] {mode}")
    print(f"- 目标：{alias} ({host})")
    print(f"- 分支：{branch}")
    print(f"- 基座包：{base_count}")
    print(f"- 插件包：{plugin_count}")
    for asset in assets:
        label = "基座" if asset.kind == "base" else "插件"
        print(f"  [{label}] {asset.path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deploy smart packages from Nexus smart-package repository.",
    )
    parser.add_argument("target", nargs="?", help="目标服务器：188、201、124 或完整 IP")
    parser.add_argument("--branch", default="auto", help="分支：auto、master、develop")
    parser.add_argument("--execute", action="store_true", help="实际上传包并重启服务；不加则只预览")
    parser.add_argument("--nexus-url", default=DEFAULT_NEXUS_URL)
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    parser.add_argument("--nexus-username", default=DEFAULT_NEXUS_USERNAME)
    parser.add_argument("--nexus-password", default=DEFAULT_NEXUS_PASSWORD)
    parser.add_argument("--ssh-username", default=DEFAULT_SSH_USERNAME)
    parser.add_argument("--ssh-password", default=DEFAULT_SSH_PASSWORD)
    parser.add_argument("--base-dir", default=DEFAULT_BASE_DIR)
    parser.add_argument("--plugin-dir", default=DEFAULT_PLUGIN_DIR)
    parser.add_argument("--log-dir", default=DEFAULT_LOG_DIR)
    parser.add_argument("--service", default=DEFAULT_SERVICE)
    parser.add_argument("--include-regex", help="覆盖默认分支过滤，按路径或下载地址匹配")
    parser.add_argument("--base-regex", default=DEFAULT_BASE_REGEX)
    parser.add_argument("--plugin-regex", default=DEFAULT_PLUGIN_REGEX)
    parser.add_argument("--unknown-kind", choices=["plugin", "base", "fail"], default="plugin")
    parser.add_argument(
        "--extensions",
        default=",".join(DEFAULT_EXTENSIONS),
        help="逗号分隔的可部署文件后缀；默认 jar,war,zip,tar.gz,tgz,tar",
    )
    parser.add_argument("--all-files", action="store_true", help="不过滤文件后缀")
    parser.add_argument("--all-versions", action="store_true", help="部署匹配到的所有历史版本；默认每个模块只取最新包")
    parser.add_argument("--no-clear-plugins", action="store_true", help="上传插件前不清空 plugins 目录；默认会备份后清空")
    parser.add_argument("--ssh-backend", choices=["auto", "paramiko", "sshpass", "pty"], default="auto")
    parser.add_argument("--wait-seconds", type=int, default=8)
    parser.add_argument("--log-lines", type=int, default=120)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        alias, host, branch = resolve_target(args.target, args.branch)
        base_url = normalize_base_url(args.nexus_url)
        extensions = tuple(item.strip() for item in args.extensions.split(",") if item.strip())

        print(f"[NEXUS] 读取仓库资产：{base_url} / {args.repository}")
        raw_assets = list_nexus_assets(
            base_url,
            args.repository,
            args.nexus_username,
            args.nexus_password,
        )
        assets = filter_assets(
            raw_assets,
            branch,
            extensions,
            args.all_files,
            args.include_regex,
            args.base_regex,
            args.plugin_regex,
            args.unknown_kind,
            args.all_versions,
        )
        if not assets:
            raise DeployError(
                f"没有找到分支 {branch} 的可部署包。"
                "请确认 Nexus 路径或文件名包含分支名，或使用 --include-regex。"
            )

        print_summary(alias, host, branch, assets, args.execute)
        if not args.execute:
            print("[DRY-RUN] 未加 --execute，不会上传、覆盖或重启。")
            return 0

        with tempfile.TemporaryDirectory(prefix="smart-cicd-") as tmp_dir:
            tmp_path = pathlib.Path(tmp_dir)
            downloads: list[tuple[Asset, pathlib.Path]] = []
            for asset in assets:
                local_path = tmp_path / asset.filename
                print(f"[DOWNLOAD] {asset.path}")
                download_file(
                    asset.download_url,
                    local_path,
                    args.nexus_username,
                    args.nexus_password,
                )
                downloads.append((asset, local_path))

            client = connect_remote(host, args.ssh_username, args.ssh_password, args.ssh_backend)
            try:
                remote_deploy(
                    client,
                    downloads,
                    args.base_dir,
                    args.plugin_dir,
                    args.log_dir,
                    args.service,
                    args.wait_seconds,
                    args.log_lines,
                    not args.no_clear_plugins,
                )
            finally:
                client.close()

        print("[DONE] 部署完成。")
        return 0
    except DeployError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
