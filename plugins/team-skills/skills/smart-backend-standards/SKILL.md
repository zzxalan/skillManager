---
name: smart-backend-standards
description: "用于 smart 空间管理项目 smart-core + smart-* 插件 后端 开发规范。Use when Codex works on Java Spring Controller Service Mapper MyBatis-Flex CommonResult TimeManager EventBus Quartz NodeService Extract 插件打包 接口联调 或后端代码审查。"
---

# Smart Backend Standards

## Overview

在 smart（空间管理）项目的 `smart-core` 基座 + `smart-*` 插件体系中处理后端开发任务时，先把这份 skill 当成后端规范路由器使用。先识别任务类型，再按需读取最相关的 reference，不要一次性加载所有规则。

## Core Workflow

1. 先识别任务类型，再决定读取哪些 reference。
2. 所有后端任务先读取 `references/architecture-boundary.md`。
3. 按任务读取对应后端专题 reference。
4. 只要涉及代码修改，额外读取 `references/coding-style.md`。
5. 涉及插件入口、资源接入、打包、远程更新或接口联调时，读取 `references/integration-build-packaging.md`。
6. 完成实现或 review 前，读取 `references/review-checklist.md` 做自检。

## Reference Routing

- 后端接口、Controller、HTTP 方法、分页返回、响应包装：读取 `references/backend-api-response.md`
- 数据访问、实体、Mapper、Service、查询、分页、状态回写：读取 `references/backend-data-access.md`
- 包结构、Controller / Service / DTO 落点、测试与验证范围：读取 `references/backend-module-structure.md`
- 节点树、`NodeService`、`@Extract`、通用节点接口：读取 `references/backend-node-service.md`
- 定时任务、Quartz、Job、Trigger、调度清理：读取 `references/backend-scheduler.md`
- 任意代码修改、命名、格式、中文注释与可读性：读取 `references/coding-style.md`
- 插件入口、资源接入、构建打包、远程更新、接口联调鉴权：读取 `references/integration-build-packaging.md`
- 后端代码审查与交付检查：读取 `references/review-checklist.md`

## Working Rules

- 先看实际工程代码，再看仓库说明文档；两者不一致时，以实际代码为准，并在交付中说明差异。
- 先判断能力属于宿主基座、本插件还是其他插件，避免越过职责边界。
- 优先复用宿主能力、统一封装、统一响应、统一数据访问模式和邻近模块实现。
- 不因存量代码缺注释而跳过本次改动应补的中文职责说明。
- 受宿主环境、内网依赖或联调条件限制时，明确区分已验证部分与未验证部分。

## Conflict Order

规则冲突时，按以下顺序决策：

1. `references/architecture-boundary.md`
2. `references/integration-build-packaging.md`
3. 当前任务直接命中的后端专题 reference
4. `references/coding-style.md`
5. 邻近模块现有实现
6. 局部最小改动原则
