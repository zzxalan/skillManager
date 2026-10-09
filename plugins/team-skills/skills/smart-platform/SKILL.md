---
name: smart-platform
description: 通过已安装的 smart-cicd MCP 统一处理 smart 项目识别、插件归属、环境诊断、构建、部署和服务重启。Use when the user asks about smart plugins, repositories, environments, packaging, releases, deployment, local JAR uploads, service restarts, service status, logs, or deployment failures.
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
- 服务：`service_status` 只读查询；`service_restart` 仅重启指定环境已登记的服务，需要 developer 或 admin
- 构建：`build_preview` 后按用户确认调用 `build_start`，用 `build_status` 查看结果
- 部署：先 `deploy_preview`，再把返回的 `confirmToken` 原样传给 `deploy_start`，用 `deploy_status` 查看结果

## 开发阶段更新

用户说“开发环境更新”“前端打包后更新”或“远程热更新”时，按下面顺序执行。MCP 负责提供环境事实和重启能力，本地负责打包以及文件传输：

1. 确认目标插件、代码仓库、分支和目标环境。使用 `catalog_list`、`resolve_plugin`、`resolve_environment` 消除名称歧义。
2. 在目标插件本地执行前端打包：进入 `frontend` 目录，执行 `pnpm install`（依赖已满足时可复用现有安装结果）和 `pnpm build`。前端失败时停止，不执行后端打包或远程更新。
3. 前端成功后进入 `backend` 目录，执行正式环境打包任务 `./gradlew clean 正式环境打包`，确认生成最终 JAR，并确认前端产物已复制进 JAR。后端打包失败时停止。
4. 调用 `inspect_environment` 或 `collect_environment`，从 MCP 返回值读取目标服务器、应用目录、插件目录、服务名和当前插件文件，禁止根据本地固定路径猜测。基座 JAR 使用应用目录，插件 JAR 使用插件目录。
5. 本地使用 MCP 返回的服务器信息执行远程文件操作：直接移除目标位置的旧 JAR，再将本次生成的 JAR 上传到对应目录。开发环境不做备份。可使用项目已有的 SSH/SCP 工具或脚本；不得把固定服务器、固定目录或凭证写回 skill。
6. 确认文件上传成功后，调用 `service_restart({environmentId})` 仅重启服务；随后用 `service_status({environmentId})` 检查服务恢复，再用 `collect_environment({environmentId})` 回读实际基座和插件版本，必要时用 `inspect_environment` 检查文件与环境。

开发阶段更新需要 developer 或 admin 权限。MCP 未返回服务器、应用目录、插件目录或服务名时，必须停止文件操作并报告缺失信息；不得猜测目标位置。

## 本地上传 JAR 后仅重启

用户明确指定本地 JAR 时复用该文件，不重新构建；用户已经上传完成且仅要求重启时，直接从环境确认和服务查询开始。

1. 用 `resolve_environment` 确认目标，用 `inspect_environment` 获取实际服务器、应用目录、插件目录及服务名。需要上传时，先核对 JAR 归属，再按“开发阶段更新”的文件传输步骤上传；上传失败不重启。
2. 调用 `service_status({environmentId})` 记录当前状态，然后调用 `service_restart({environmentId})`。只传环境 ID，服务器和服务名由平台解析。已授权的更新任务包含必要重启，不重复索要同一授权。
3. 该流程不调用 `deploy_preview` / `deploy_start`，不从制品库重新拉包，不改平台目标版本组合；正式制品部署仍按部署流程执行。
4. `restartExecuted: true` 只表示重启命令成功；服务 `active` 也不等于应用健康。用 `service_status` 做有限次数的状态查询，结合 `collect_environment` 的版本、文件和应用访问检查判断更新结果。同版本 JAR 替换还需核对上传文件或实际功能，不能仅凭版本号宣称新代码生效。
5. 返回 `statusError` 时先查询状态，不重复重启；命令超时或连接中断时执行结果可能不确定，也先查询状态。检查失败时报告已完成的上传、重启和待确认事项。
6. 如果客户端发现不到 `service_restart` / `service_status`，检查 MCP 服务是否已部署新版本，并刷新客户端工具列表。准确说明“当前 MCP 未暴露独立服务工具”，不要据此宣称平台没有重启能力，也不要用完整部署替代仅重启。

## 规则

1. 识别需求归属时先解析插件标识、正式名称、仓库和环境；发生歧义时要求用户用标识或工程名确认。
2. 只读查询和日志查看可由 viewer 完成；构建、环境采集、服务重启和部署需要 developer 或 admin。
3. 不通过 MCP 执行任意 shell、SQL 或读取凭证；本地文件上传可调用已有 SSH/SCP 工具，但凭证只能从既有安全配置读取，不得写入 skill、命令日志或回复。
4. 不执行真实构建或部署，除非用户明确要求；正式制品部署遵循预览、确认凭证、启动、状态的顺序；已授权的仅重启走 `service_restart`，不需要部署确认凭证。
5. MCP 返回权限、认证、制品、依赖或连通性错误时，保留原始错误要点并停止后续写操作。
6. 没有 MCP 返回的目标目录、重启结果和状态检查结果，不得宣称开发环境更新完成。

## 触发

用户提到 smart 插件、仓库、环境、打包、更新服务器、本地 JAR 上传、仅重启、服务状态、部署、发布或日志时，使用本 skill 调用 MCP。
