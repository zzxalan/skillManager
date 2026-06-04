# Smart Auth Facts

基于 `/Users/zhangzx/code/outbook/smart/smart-core-mixed` 的当前实现整理。执行前若基座代码更新，优先重新 grep 验证。

## Backend

- 登录接口：`POST /user/login`
- 如果后端经由 smart 前端/网关端口暴露，登录接口可能是 `POST /api/user/login`；裸 `/user/login` 返回 `code=1010` 时，应自动改试 `/api/user/login`。
- 请求体：`username`、`password`、`captchaKey`、`captchaCode`、`rememberMe`
- 通用响应：`{ code, data, msg }`
- 成功 token 路径：`data.token`
- 登录返回：`data.userId`、`data.token`、`data.roles`、`data.violations`
- 验证码开关：`sa-token.captcha.enabled`
- 验证码绕过：`CaptchaServiceImpl.validateCaptcha` 中 `captchaKey.equalsIgnoreCase(captchaCode)` 直接通过。
- Sa-Token 名称：`application.yml` 中 `sa-token.token-name: token`，同时也是 cookie 名称。
- 默认后端端口：`server.port: 8080`
- 已验证环境：`192.168.20.213:18080` 需要走 `/api/user/login`；数据库 `192.168.20.213:3306/smart-zzx` 可连。

## User And Password

- 用户表：`sys_user`
- 账号字段：`username`
- 密码字段：`password`
- `UserServiceImpl.login` 按 `username` 查询用户，并用 `PasswordServiceImpl.verifyPassword(user, plainPassword)` 校验。
- `password` 为空时，`PasswordServiceImpl` 会使用默认密码策略生成默认密码；当前 `application.yml` 的默认策略是 fixed，值为 `Smart123456`。
- 初始化管理员迁移里还存在兜底管理员密码明文 `Outbook@5777817` 的 BCrypt 哈希。若数据库中 `admin`/`super_admin` 用该迁移初始化，可直接用该明文尝试。
- 如果外部账号密码表约定“密码为 NULL 表示密码等于账号”，脚本按该约定处理；这不是 `sys_user.password` 哈希字段的通用含义。
- 在 `smart-zzx` 中，`admin` 是 BCrypt 密码，明文 `Outbook@5777817` 可登录并返回正常 `admin` token；大量 `password is null` 的用户以“密码等于账号”登录时会触发密码强度重置，返回临时 token，不能直接作为正常登录态。

## Frontend

- 登录页调用 `fetchLogin`，成功后执行 `setStoreToken(loginReq?.token)`。
- `src/shared/auth/syncUrlToken.ts` 支持从 URL 的 `access_token` 或 `token` 参数提取 token，并写入 cookie：`token=<value>; path=/; SameSite=Lax`。
- `src/App.tsx` 会执行 `syncUrlToken(window.location.search)`。
- H5 入口也会执行 `syncUrlToken(window.location.href)`。
- 默认前端开发端口：`vite.config.ts` 中 `server.port: 5001`。

## Recommended Injection

优先使用 URL 注入：

```text
http://127.0.0.1:5001/?token=<token>
```

手动注入：

```javascript
document.cookie = "token=<token>; path=/; SameSite=Lax";
location.reload();
```
