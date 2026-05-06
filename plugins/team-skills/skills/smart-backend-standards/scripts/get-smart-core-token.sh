#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
用法：get-smart-core-token.sh <base-url> [username] [password]

说明：
  从 smart-core 基座登录接口获取 token，默认只向 stdout 输出 token 明文，便于 curl 命令替换使用。

参数：
  base-url   目标基座地址，例如 http://host:port
  username   登录账号，默认 super_admin，也可用 SMART_CORE_USERNAME 覆盖
  password   登录密码，必须通过第三个参数或 SMART_CORE_PASSWORD 提供

环境变量：
  SMART_CORE_USERNAME       覆盖默认账号
  SMART_CORE_PASSWORD       登录密码
  SMART_CORE_CAPTCHA_KEY    验证码 key，默认 1
  SMART_CORE_CAPTCHA_CODE   验证码 code，默认与 captchaKey 相同
  SMART_CORE_REMEMBER_ME    是否记住登录，默认 true
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

base_url="${1:-}"
if [[ -z "$base_url" ]]; then
  usage >&2
  exit 2
fi

username="${2:-${SMART_CORE_USERNAME:-super_admin}}"
password="${3:-${SMART_CORE_PASSWORD:-}}"
if [[ -z "$password" ]]; then
  echo "缺少登录密码：请通过第三个参数或 SMART_CORE_PASSWORD 提供" >&2
  exit 2
fi

captcha_key="${SMART_CORE_CAPTCHA_KEY:-1}"
captcha_code="${SMART_CORE_CAPTCHA_CODE:-$captcha_key}"
remember_me="${SMART_CORE_REMEMBER_ME:-true}"
base_url="${base_url%/}"

payload=$(python3 - <<'PY' "$username" "$password" "$captcha_key" "$captcha_code" "$remember_me"
import json
import sys

username, password, captcha_key, captcha_code, remember_me = sys.argv[1:]
print(json.dumps({
    "username": username,
    "password": password,
    "captchaKey": captcha_key,
    "captchaCode": captcha_code,
    "rememberMe": remember_me.lower() == "true",
}, ensure_ascii=False))
PY
)

response=$(curl -sS --fail --max-time 15 --location --request POST "$base_url/api/user/login" \
  --header 'Content-Type: application/json' \
  --header 'Accept: */*' \
  --data-raw "$payload")

TOKEN_RESPONSE="$response" python3 - <<'PY'
import json
import os
import sys

try:
    response = json.loads(os.environ["TOKEN_RESPONSE"])
except Exception as exc:
    print(f"登录响应不是合法 JSON：{exc}", file=sys.stderr)
    sys.exit(1)

code = response.get("code")
message = response.get("msg") or response.get("message") or ""
data = response.get("data") if isinstance(response, dict) else None
token = response.get("token")
if not token and isinstance(data, dict):
    token = data.get("token")

if code not in (0, "0", None) or not token:
    print(f"获取 token 失败：code={code}, msg={message}", file=sys.stderr)
    sys.exit(1)

print(token)
PY
