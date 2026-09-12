---
name: smart-platform
description: 通过已安装的 smart-cicd MCP 统一处理 smart 项目识别、插件归属、环境诊断、构建和部署。Use when the user asks about smart plugins, repositories, environments, packaging, releases, deployment, logs, or deployment failures.
---
# Smart Platform

## 入口

优先调用已安装的 `smart-cicd` MCP，不从固定清单或硬编码服务器推断事实。插件、仓库、环境、制品和实际版本以 MCP 返回为准。

如果识别到 `smart-cicd` MCP 未安装，先告知用户安装后再继续，并提供以下配置：

- 地址固定为 `http://192.168.20.213:3300/api/mcp`
- 在请求 headers 中填写 `X-CICD-Username`（账号）和 `X-CICD-Password`（密码）

账号密码只放在 MCP 客户端的 headers 配置中，不写入 skill、代码、命令或回复内容。未完成安装和连通性验证前，不执行后续 smart 项目操作。

- 项目识别：`catalog_list`、`resolve_plugin`、`resolve_environment`
- 环境查看：`inspect_environment`、`diagnose_environment`、`collect_environment`
- 构建：`build_preview` 后按用户确认调用 `build_start`，用 `build_status` 查看结果
- 部署：先 `deploy_preview`，再把返回的 `confirmToken` 原样传给 `deploy_start`，用 `deploy_status` 查看结果

## 开发阶段更新

用户说“开发环境更新”“前端打包后更新”或“远程热更新”时，按下面顺序执行。MCP 负责提供环境事实和重启能力，本地负责打包以及文件传输：

1. 确认目标插件、代码仓库、分支和目标环境。使用 `catalog_list`、`resolve_plugin`、`resolve_environment` 消除名称歧义。
2. 在目标插件本地执行前端打包：进入 `frontend` 目录，执行 `pnpm install`（依赖已满足时可复用现有安装结果）和 `pnpm build`。前端失败时停止，不执行后端打包或远程更新。
3. 前端成功后进入 `backend` 目录，执行正式环境打包任务 `./gradlew clean 正式环境打包`，确认生成最终 JAR，并确认前端产物已复制进 JAR。后端打包失败时停止。
4. 调用 `inspect_environment` 或 `collect_environment`，从 MCP 返回值读取目标服务器、应用目录、插件目录、服务名和当前插件文件，禁止根据本地固定路径猜测。基座 JAR 使用应用目录，插件 JAR 使用插件目录。
5. 本地使用 MCP 返回的服务器信息执行远程文件操作：直接移除目标位置的旧 JAR，再将本次生成的 JAR 上传到对应目录。开发环境不做备份。可使用项目已有的 SSH/SCP 工具或脚本；不得把固定服务器、固定目录或凭证写回 skill。
6. 文件上传完成后，通过 MCP 执行目标服务重启，并用环境检查、服务状态或日志确认服务恢复、插件文件存在且版本已回读。

开发阶段更新需要 developer 或 admin 权限。MCP 未返回服务器、应用目录、插件目录或服务名时，必须停止文件操作并报告缺失信息；不得猜测目标位置。

## 规则

1. 识别需求归属时先解析插件标识、正式名称、仓库和环境；发生歧义时要求用户用标识或工程名确认。
2. 只读查询和日志查看可由 viewer 完成；构建、环境采集和部署需要 developer 或 admin。
3. 不通过 MCP 执行任意 shell、SQL 或读取凭证；本地文件上传可调用已有 SSH/SCP 工具，但凭证只能从既有安全配置读取，不得写入 skill、命令日志或回复。
4. 不执行真实构建或部署，除非用户明确要求；部署永远遵循预览、确认凭证、启动、状态的顺序。
5. MCP 返回权限、认证、制品、依赖或连通性错误时，保留原始错误要点并停止后续写操作。
6. 没有 MCP 返回的目标目录、重启结果和状态检查结果，不得宣称开发环境更新完成。

## 触发

用户提到 smart 插件、仓库、环境、打包、更新服务器、部署、发布或日志时，使用本 skill 调用 MCP。
