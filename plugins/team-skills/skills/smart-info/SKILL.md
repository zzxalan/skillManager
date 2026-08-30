---
name: smart-info
description: "用于识别 smart 电子班牌/空间管理项目的项目地图、插件术语和仓库归属。Use when Codex needs to map smart-core 基座、smart-* 插件、终端应用、插件标识 app、正式名称 appName、业务别名、工程名、Git 仓库、本地目录、基座+N 个插件关系、插件边界初判，或选择 smart 需求应查看/修改的仓库。"
---

# Smart Info

## 定位

本 skill 是 smart 项目的项目地图，不是开发规范。

它负责回答：

- smart 项目整体是什么：`smart-core` 基座 + N 个 `smart-*` 插件 + 终端/应用系统。
- 插件标识 `app`、正式名称 `appName`、业务别名、工程名、Git 仓库和本地相对目录如何对应。
- 一个需求大概率属于基座、哪个插件，还是终端/小程序。

它不负责回答代码怎么写。进入具体开发或审查时，必须继续触发对应 skill：

- 流程、边界、需求拆解、交付阶段：`smart-project-workflow`
- 后端 Java/Spring/MyBatis-Flex/插件后端接入：`smart-backend-standards`
- 前端 React/TypeScript/Vite/qiankun/页面接入：`smart-frontend-standards`
- 本地登录、token、联调会话：`smart-token-login`
- 新建 mixed 插件模板：`init-smart-plugin`

## Core Workflow

1. 读取 `references/project-map.md`，用项目地图确认基座、插件、终端应用、术语映射、仓库和本地目录。
2. 将用户给出的正式名称、插件标识、工程名或已登记别名解析到同一个项目；发生重名或歧义时，再要求用插件标识或工程名消歧。
3. 用户只问项目是什么、仓库在哪里或名称如何对应时，直接基于项目地图回答。
4. 用户要改代码、配置、接口或文档时，先判断目标仓库；如果仓库可用，再核验相关插件 `frontend/public/config.json` 的顶层 `app` 和 `appName`，然后进入 `smart-project-workflow` 或实现层 standards。
5. 需求横跨多个插件时，先列出可能涉及的仓库和数据归属疑点，不假设可以跨插件改数据。
6. 项目地图与实际仓库冲突时，按“权威性与冲突处理”执行，并指出需要回写 `references/project-map.md`。

## 使用规则

- `smart-core-mixed` 的插件标识是 `core`，架构角色是宿主基座，不按普通业务插件处理；`smart` 是项目体系名称，不用作该配置的插件标识。
- `smart-*-mixed` 通常表示同时包含后端和前端的 mixed 插件工程；`smart-tools` 是现有清单中的例外，目录和仓库名不带 `-mixed`。
- 插件标识是顶层 `app`，插件正式名称是顶层 `appName`；两者均以对应工程的 `frontend/public/config.json` 为准。
- `app` 区分大小写，不等同于工程名；不得从目录名、包名、路由、组件 `id`、`pluginId` 或 `name` 推导顶层 `app`。
- 业务别名只用于自然语言识别，不得替代 `appName`，也不得写入要求稳定标识的代码、接口参数、路由或构建产物。
- 没有 `frontend/public/config.json` 或缺少 `app` / `appName` 时，保留工程信息和业务说明，但将插件标识/正式名称记为“未配置”，不自行编造。
- 本地相对目录默认按工作区根目录下的同名目录理解，例如 `./smart-course-mixed`。
- 首次正式指代插件时，优先使用“正式名称（`app`，工程 `smart-*-mixed`）”；后续可沿用用户的无歧义别名。

## 权威性与冲突处理

- `app` / `appName`：以目标工程当前 `frontend/public/config.json` 为最高优先级。
- 工程名、仓库 URL、本地目录、业务边界：以实际仓库和用户确认的最新清单为准。
- 业务别名：可根据用户确认或工作区中的稳定用法登记，但不覆盖配置事实。
- 附件或新清单可以更新仓库和别名信息；它们与当前 `config.json` 中的 `app` / `appName` 冲突时，说明差异，不静默覆盖。
- 新增插件、术语变更、未登记别名、重名或跨插件歧义时，使用 `rg` 在 smart 工作区全局搜索工程名、`app`、`appName` 和关联称呼，并排除 `.git`、`node_modules`、`build`、`dist`、`outputs` 等目录。
- 确认变更后，同步回写 `references/project-map.md`；可用 `scripts/check-project-map.py --workspace <smart-工作区>` 检查地图与当前配置是否一致。

## 何时读取 Project Map

读取 `references/project-map.md` 的典型场景：

- 需要把正式名称或别名映射到工程，例如“考勤” -> `smart-attendance-mixed`。
- 需要把插件标识映射到工程，例如 `classPanel` -> `smart-classPanel-mixed`。
- 需要选择 repo checkout 目标。
- 需要区分微前端插件、基座、Android 终端、微信小程序。
- 需要向用户解释 smart 是“基座+n 个插件”的项目形态。
