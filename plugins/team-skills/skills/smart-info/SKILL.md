---
name: smart-info
description: "用于识别 smart 电子班牌/空间管理项目的项目地图与命名信息。Use when Codex needs to understand smart-core 基座、smart-* 插件、终端应用、中文/英文项目名、plugin id、Git 仓库、相对目录、基座+n 个插件关系、插件边界初判或在 smart 项目内选择应查看/修改哪个仓库。"
---

# Smart Info

## 定位

本 skill 是 smart 项目的项目地图，不是开发规范。

它负责回答：

- smart 项目整体是什么：`smart-core` 基座 + N 个 `smart-*` 插件 + 终端/应用系统。
- 中文项目名、英文仓库名、plugin id、Git 仓库和本地相对目录如何对应。
- 一个需求大概率属于基座、哪个插件，还是终端/小程序。

它不负责回答代码怎么写。进入具体开发或审查时，必须继续触发对应 skill：

- 流程、边界、需求拆解、交付阶段：`smart-project-workflow`
- 后端 Java/Spring/MyBatis-Flex/插件后端接入：`smart-backend-standards`
- 前端 React/TypeScript/Vite/qiankun/页面接入：`smart-frontend-standards`
- 本地登录、token、联调会话：`smart-token-login`
- 新建 mixed 插件模板：`init-smart-plugin`

## Core Workflow

1. 先读取 `references/project-map.md`，用其中的项目地图确认基座、插件、终端应用、仓库和本地目录。
2. 用户只问“这个项目/插件是什么、在哪个仓库、叫什么、对应哪个英文名”时，直接基于项目地图回答。
3. 用户要做需求、改代码、查接口、建表、联调或评审时，先用项目地图判断目标仓库，再进入 `smart-project-workflow` 或实现层 standards。
4. 如果需求横跨多个插件，先列出可能涉及的仓库和数据归属疑点，不直接假设可以跨插件改数据。
5. 如果项目地图与实际仓库代码冲突，以实际仓库代码为准，并在交付中指出需要回写 `references/project-map.md`。

## 使用规则

- `smart-core-mixed` / plugin id `smart` 是基座，不按普通插件处理。
- `smart-*-mixed` 通常表示同时包含后端和前端的 mixed 插件工程；`smart-tools` 是现有清单中的例外，目录和仓库名不带 `-mixed`。
- plugin id 是运行时或菜单/插件体系识别用的短标识，不等同于仓库名。
- 本地相对目录默认按工作区根目录下的同名目录理解，例如 `./smart-course-mixed`。
- 附件或用户给出的新清单优先级高于本 skill 的静态清单；确认后应同步更新 `references/project-map.md`。

## 何时读取 Project Map

读取 `references/project-map.md` 的典型场景：

- 需要把中文名映射到英文仓库名，例如“考勤” -> `smart-attendance-mixed`。
- 需要把 plugin id 映射到仓库，例如 `classPanel` -> `smart-classPanel-mixed`。
- 需要选择 repo checkout 目标。
- 需要区分微前端插件、基座、Android 终端、微信小程序。
- 需要向用户解释 smart 是“基座+n 个插件”的项目形态。
