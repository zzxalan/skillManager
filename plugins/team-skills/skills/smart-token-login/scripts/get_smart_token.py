#!/usr/bin/env python3
"""Get a smart project login token for local development."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SUCCESS_CODE = 0
DEFAULT_CAPTCHA = "codex-local-login"
DEFAULT_USER_SQL = (
    "select username, password from sys_user "
    "where is_deleted = 0 {username_filter} order by id asc limit 1"
)
BCRYPT_RE = re.compile(r"^\$2[aby]\$\d{2}\$")


class SmartTokenError(RuntimeError):
    pass


class LoginResponseError(SmartTokenError):
    def __init__(self, message: str, response: dict[str, Any]) -> None:
        super().__init__(message)
        self.response = response


@dataclass
class Account:
    username: str
    password: str | None
    source: str


def mask(value: str | None, keep: int = 4) -> str | None:
    if value is None:
        return None
    if len(value) <= keep * 2:
        return "*" * len(value)
    return f"{value[:keep]}...{value[-keep:]}"


def normalize_base_url(url: str) -> str:
    value = url.strip().rstrip("/")
    if not value:
        raise SmartTokenError("backend url 不能为空")
    if not re.match(r"^https?://", value):
        value = f"http://{value}"
    return value


def parse_jdbc_mysql(jdbc_url: str) -> dict[str, Any]:
    if not jdbc_url.startswith("jdbc:mysql://"):
        raise SmartTokenError("当前脚本仅内置支持 jdbc:mysql://、mysql:// 和 sqlite 文件")
    raw = jdbc_url[len("jdbc:") :]
    parsed = urllib.parse.urlparse(raw)
    if not parsed.hostname or not parsed.path.strip("/"):
        raise SmartTokenError(f"无法解析 MySQL JDBC URL: {jdbc_url}")
    return {
        "host": parsed.hostname,
        "port": parsed.port or 3306,
        "database": parsed.path.strip("/").split("/")[0],
    }


def parse_mysql_url(url: str) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme == "jdbc":
        return parse_jdbc_mysql(url)
    if parsed.scheme not in {"mysql", "mysql+pymysql"}:
        raise SmartTokenError("当前脚本仅内置支持 jdbc:mysql://、mysql:// 和 sqlite 文件")
    if not parsed.hostname or not parsed.path.strip("/"):
        raise SmartTokenError(f"无法解析 MySQL URL: {url}")
    return {
        "host": parsed.hostname,
        "port": parsed.port or 3306,
        "database": parsed.path.strip("/").split("/")[0],
        "user": urllib.parse.unquote(parsed.username) if parsed.username else None,
        "password": urllib.parse.unquote(parsed.password) if parsed.password else None,
    }


def connect_mysql(db_url: str, db_user: str | None, db_password: str | None):
    config = parse_jdbc_mysql(db_url) if db_url.startswith("jdbc:mysql://") else parse_mysql_url(db_url)
    user = db_user or config.get("user")
    password = db_password if db_password is not None else config.get("password")
    if not user:
        raise SmartTokenError("MySQL 连接缺少用户名，请传 --db-user 或在 mysql:// URL 中提供")

    try:
        import pymysql  # type: ignore
    except ImportError as exc:
        raise SmartTokenError("缺少 pymysql。请先执行：python3 -m pip install pymysql") from exc

    return pymysql.connect(
        host=config["host"],
        port=int(config["port"]),
        user=user,
        password=password or "",
        database=config["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.Cursor,
    )


def is_sqlite_url(db_url: str) -> bool:
    return db_url.startswith("sqlite://") or db_url.endswith((".db", ".sqlite", ".sqlite3"))


def connect_db(db_url: str, db_user: str | None, db_password: str | None):
    if is_sqlite_url(db_url):
        path = db_url.removeprefix("sqlite://")
        return sqlite3.connect(Path(path).expanduser())
    return connect_mysql(db_url, db_user, db_password)


def build_account_sql(sql_template: str, username: str | None) -> tuple[str, tuple[Any, ...]]:
    if "{username_filter}" in sql_template:
        username_filter = "and username = %s" if username else ""
        return sql_template.format(username_filter=username_filter), ((username,) if username else ())
    if username:
        return sql_template, (username,)
    return sql_template, ()


def adapt_placeholders(sql: str, connection: Any) -> str:
    if isinstance(connection, sqlite3.Connection):
        return sql.replace("%s", "?")
    return sql


def fetch_account_from_db(args: argparse.Namespace) -> Account:
    if not args.db_url:
        raise SmartTokenError("需要 --db-url，或直接传 --username 与 --password")

    sql_template = args.password_sql or DEFAULT_USER_SQL
    connection = connect_db(args.db_url, args.db_user, args.db_password)
    try:
        sql, params = build_account_sql(sql_template, args.username)
        sql = adapt_placeholders(sql, connection)
        cursor = connection.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()
        if not row:
            raise SmartTokenError("数据库没有查到可登录账号")
        username = str(row[0]).strip() if row[0] is not None else ""
        password = None if len(row) < 2 or row[1] is None else str(row[1])
        if not username:
            raise SmartTokenError("数据库返回的 username 为空")
        return Account(username=username, password=password, source="database")
    finally:
        connection.close()


def resolve_account(args: argparse.Namespace) -> Account:
    if not args.db_url and args.username and args.password is not None:
        return Account(username=args.username, password=args.password, source="arguments")

    account = fetch_account_from_db(args)
    if args.password is not None:
        account.password = args.password
        account.source = f"{account.source}+password-override"

    if account.password is None or account.password == "":
        account.password = account.username

    if BCRYPT_RE.match(account.password):
        raise SmartTokenError(
            "数据库 password 看起来是 BCrypt 哈希，不能当明文登录。"
            "请传 --password，或用 --password-sql 返回明文密码/NULL。"
        )

    return account


def post_json(url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SmartTokenError(f"登录接口 HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SmartTokenError(f"无法连接登录接口: {exc.reason}") from exc

    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise SmartTokenError(f"登录接口返回不是 JSON: {body[:300]}") from exc


def extract_token(response: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    code = response.get("code")
    if code != SUCCESS_CODE:
        raise LoginResponseError(f"登录失败 code={code}, msg={response.get('msg')}", response)

    data = response.get("data")
    if not isinstance(data, dict):
        raise SmartTokenError("登录响应缺少 data")

    violations = data.get("violations")
    if isinstance(violations, dict) and violations.get("valid") is False:
        raise SmartTokenError("登录成功但触发密码强度重置，当前 token 是临时 token，不能作为正常登录 token")

    token = data.get("token")
    if not token:
        raise SmartTokenError(f"登录响应缺少 data.token: {json.dumps(response, ensure_ascii=False)[:300]}")
    return str(token), data


def build_login_urls(backend_url: str) -> list[str]:
    base = normalize_base_url(backend_url)
    urls = [f"{base}/user/login"]
    if not base.endswith("/api"):
        urls.append(f"{base}/api/user/login")
    return urls


def login(args: argparse.Namespace, account: Account) -> tuple[str, dict[str, Any], str]:
    backend_url = normalize_base_url(args.backend_url)
    captcha = args.captcha or DEFAULT_CAPTCHA
    payload = {
        "username": account.username,
        "password": account.password,
        "captchaKey": captcha,
        "captchaCode": captcha,
        "rememberMe": bool(args.remember_me),
    }

    last_error: SmartTokenError | None = None
    for login_url in build_login_urls(backend_url):
        try:
            response = post_json(login_url, payload, args.timeout)
            token, data = extract_token(response)
            return token, data, login_url
        except LoginResponseError as exc:
            last_error = exc
            if exc.response.get("code") == 1010 and not login_url.endswith("/api/user/login"):
                continue
            raise exc
        except SmartTokenError as exc:
            last_error = exc
            raise exc

    raise last_error or SmartTokenError("登录失败")


def build_frontend_url(frontend_url: str | None, token: str) -> str | None:
    if not frontend_url:
        return None
    base = frontend_url.strip()
    separator = "&" if "?" in base else "?"
    return f"{base}{separator}token={urllib.parse.quote(token)}"


def build_result(
    args: argparse.Namespace,
    account: Account,
    token: str,
    data: dict[str, Any],
    login_url: str,
) -> dict[str, Any]:
    frontend_login_url = build_frontend_url(args.frontend_url, token)
    cookie_script = f'document.cookie = "token={token}; path=/; SameSite=Lax"; location.reload();'
    return {
        "username": account.username,
        "accountSource": account.source,
        "backendUrl": normalize_base_url(args.backend_url),
        "loginUrl": login_url,
        "frontendUrl": args.frontend_url,
        "frontendLoginUrl": frontend_login_url,
        "token": token,
        "tokenMasked": mask(token),
        "cookieName": "token",
        "cookieScript": cookie_script,
        "userId": data.get("userId"),
        "roles": data.get("roles"),
    }


def print_human(result: dict[str, Any], show_token: bool) -> None:
    print("Smart token 获取成功")
    print(f"- 账号: {result['username']} ({result['accountSource']})")
    print(f"- 后端: {result['backendUrl']}")
    if result.get("frontendUrl"):
        print(f"- 前端: {result['frontendUrl']}")
    print(f"- 用户ID: {result.get('userId')}")
    print(f"- 角色: {result.get('roles')}")
    print(f"- Token: {result['token'] if show_token else result['tokenMasked']}")
    if result.get("frontendLoginUrl"):
        print(f"- URL 注入: {result['frontendLoginUrl'] if show_token else result['frontendLoginUrl'].replace(result['token'], result['tokenMasked'])}")
    print("- Cookie 注入脚本:")
    print(result["cookieScript"] if show_token else result["cookieScript"].replace(result["token"], result["tokenMasked"]))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Get smart local login token.")
    parser.add_argument("--backend-url", default="http://127.0.0.1:8080", help="Smart backend base URL.")
    parser.add_argument("--frontend-url", help="Frontend URL for token query injection, e.g. http://127.0.0.1:5001/")
    parser.add_argument("--username", help="Login username or DB username filter.")
    parser.add_argument("--password", help="Plain password override.")
    parser.add_argument("--db-url", help="jdbc:mysql://host:port/db, mysql://user:pass@host/db, sqlite file path, or sqlite://path.")
    parser.add_argument("--db-user", help="Database username.")
    parser.add_argument("--db-password", help="Database password.")
    parser.add_argument(
        "--password-sql",
        help=(
            "Custom SQL returning username,password. Use %%s as username placeholder. "
            "If it contains {username_filter}, the default username filter is inserted."
        ),
    )
    parser.add_argument("--captcha", default=DEFAULT_CAPTCHA, help="captchaKey and captchaCode value.")
    parser.add_argument("--remember-me", action="store_true", help="Send rememberMe=true.")
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout seconds.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    parser.add_argument("--show-token", action="store_true", help="Print full token instead of masked token.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        account = resolve_account(args)
        token, data, login_url = login(args, account)
        result = build_result(args, account, token, data, login_url)
        if args.json:
            output = result if args.show_token else {**result, "token": result["tokenMasked"]}
            if not args.show_token and result.get("frontendLoginUrl"):
                output["frontendLoginUrl"] = result["frontendLoginUrl"].replace(result["token"], result["tokenMasked"])
                output["cookieScript"] = result["cookieScript"].replace(result["token"], result["tokenMasked"])
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            print_human(result, args.show_token)
        return 0
    except SmartTokenError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
