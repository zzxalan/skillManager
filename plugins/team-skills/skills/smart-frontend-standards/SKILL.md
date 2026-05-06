---
name: smart-frontend-standards
description: "用于 smart 空间管理项目 smart-core + smart-* 插件 前端 开发规范。Use when Codex works on React TypeScript Vite qiankun Ant Design Pro Components UnoCSS CSS Modules theme.useToken VaTable VAObkTable useBreadcrumb H5 页面 插件前端构建 接口请求 或前端页面审查。"
---

# Smart Frontend Standards

## Overview

在 smart（空间管理）项目的 `smart-core` 基座 + `smart-*` 插件体系中处理前端开发任务时，先把这份 skill 当成前端规范路由器使用。先识别任务类型，再按需读取最相关的 reference，不要一次性加载所有规则。

## Core Workflow

1. 先识别任务类型，再决定读取哪些 reference。
2. 所有前端任务先读取 `references/architecture-boundary.md`。
3. 按任务读取对应前端专题 reference。
4. 只要涉及代码修改，额外读取 `references/coding-style.md`。
5. 涉及插件入口、构建产物、资源接入、远程更新或接口联调时，读取 `references/integration-build-packaging.md`。
6. 完成实现或 review 前，读取 `references/review-checklist.md` 做自检。

## Reference Routing

- 页面、布局、目录组织、共享组件、路由接入、请求 effect：读取 `references/frontend-page-structure.md`
- 列表页、CRUD 页、表格、查询、表单弹窗、`VAObkTable`、底层 `VaTable`：读取 `references/frontend-table-list.md`
- 面包屑、返回路径、页面导航：读取 `references/frontend-navigation.md`
- 视觉结构、交互布局、超长文本、CSS Modules、antd token、页面错误提示策略：读取 `references/frontend-design-guidelines.md`
- H5 移动端页面、独立入口、H5 Vite 配置：读取 `references/frontend-h5-development.md`
- qiankun、Vite、微前端接入、前端 API 前缀与请求封装：读取 `references/frontend-microfrontend.md`
- 任意代码修改、命名、格式、中文注释与可读性：读取 `references/coding-style.md`
- 插件入口、构建打包、远程更新、接口联调鉴权：读取 `references/integration-build-packaging.md`
- 前端代码审查与交付检查：读取 `references/review-checklist.md`

## Working Rules

- 先看实际工程代码，再看仓库说明文档；两者不一致时，以实际代码为准，并在交付中说明差异。
- 保持现有 React、TypeScript、Vite、qiankun、Ant Design、Pro Components、UnoCSS 与项目请求封装。
- 优先复用已有页面壳、统一组件、统一 hooks、统一请求封装和邻近页面模式。
- 页面请求只由真正影响参数的响应式值触发，避免 `useEffectEvent` 被误放进依赖数组造成循环请求。
- 受宿主环境、内网依赖或联调条件限制时，明确区分已验证部分与未验证部分。
- 开发或审查中发现可复用的新前端规范时，优先按 `team-skill-iteration` 记录；用户明确要求立即沉淀时，再补到最贴近的 frontend reference，不堆到 `SKILL.md`。

## Conflict Order

规则冲突时，按以下顺序决策：

1. `references/architecture-boundary.md`
2. `references/integration-build-packaging.md`
3. 当前任务直接命中的前端专题 reference
4. `references/coding-style.md`
5. 邻近页面现有实现
6. 局部最小改动原则
