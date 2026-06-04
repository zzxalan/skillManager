---
name: smart-token-login
description: "用于 smart 空间管理项目本地登录环境准备。Use when Codex needs to 获取 smart 项目 token、从数据库读取账号密码、绕过验证码、调用 /user/login、生成 cookie/localStorage 注入脚本、打开带 token 的本地前端地址，或协助 smart-core/smart-* 前端联调登录。"
---

# Smart Token Login

## Goal

为 smart 本地开发或联调环境获取可用登录 token，并把 token 注入浏览器 cookie 或本地缓存，使前端进入已登录状态。

## Safety

- 只用于本地开发、测试、联调环境。
- 不在最终回复、日志或文件中暴露真实 token、密码、数据库连接串密码。
- 如果目标是生产、客户现场或不可确认环境，先要求用户明确确认授权。

## Workflow

1. 读取 `references/smart-auth-facts.md`，确认当前 smart 基座登录事实是否仍匹配。
2. 确认输入：后端地址、前端地址、账号选择方式、数据库连接信息或直接账号密码。
3. 优先运行 `scripts/get_smart_token.py` 获取 token；缺依赖或环境不通时，把错误信息收窄到最小可行动作。
4. 验证登录响应包含 `data.token`，并检查 `data.violations.valid`；如果触发初始密码重置，提示需要先重置或换账号。
5. 按用户目标输出注入方式：
   - 前端支持 URL token 同步时，打开 `<frontend-url>?token=<token>`。
   - 需要手动注入时，给出 `document.cookie = "token=...; path=/; SameSite=Lax"`。
   - 如果项目实际使用 `@va/core/store` 的本地缓存，再根据项目代码补充 localStorage/IndexedDB 注入方式。
6. 完成后汇总使用的账号、后端地址、前端地址、注入方式与验证结果；token 默认脱敏展示。

## Script Usage

常用方式：

```bash
python3 scripts/get_smart_token.py \
  --backend-url http://127.0.0.1:8080 \
  --frontend-url http://127.0.0.1:5001 \
  --db-url jdbc:mysql://127.0.0.1:3306/smart \
  --db-user root \
  --db-password root \
  --username admin
```

直接指定明文密码：

```bash
python3 scripts/get_smart_token.py \
  --backend-url http://127.0.0.1:8080 \
  --username admin \
  --password 'Outbook@5777817'
```

输出 JSON，便于后续工具消费：

```bash
python3 scripts/get_smart_token.py --json ...
```

## Boundaries

- 默认数据库表是 `sys_user`，账号字段是 `username`，密码字段是 `password`。
- 如果密码字段为 `NULL` 或空字符串，脚本按“密码等于账号”处理。
- 如果密码字段看起来是 BCrypt 哈希，脚本不会把它当明文登录；改用 `--password`，或用 `--password-sql` 从自定义凭据表返回明文/NULL。
- 验证码通过 `captchaKey == captchaCode` 绕过，不需要请求验证码图片。
