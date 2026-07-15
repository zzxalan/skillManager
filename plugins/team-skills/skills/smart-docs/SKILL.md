---
name: smart-docs
description: "用于 smart 空间管理项目文档规范、文档体系建设和文档评审。Use when Codex creates, reviews, updates, audits, or standardizes README.md, AGENTS.md, docs/PRODUCT_REQUIREMENTS.md, docs/FEATURE_DESIGN/*.md, AI 项目上下文、场景验证点、产品功能清单、页面结构、业务依赖、需求意图、复杂功能设计、前后端项目文档沉淀。"
---

# Smart Docs

## Overview

在 smart（空间管理）项目中处理项目文档时，使用这份 skill 规范“哪些文档应该长期保留、每类文档写什么、哪些内容不要手工维护”。核心原则是：文档补足代码难以可靠表达的上下文，不复述代码可以直接查询的事实清单。

## Core Workflow

1. 先识别任务类型：初始化文档体系、补齐缺失文档、更新单篇文档、评审已有文档，或更新 `README.md` 中的 AI 项目上下文。
2. 读取当前项目已有 `README.md`、`AGENTS.md`、`docs/`、主要配置文件和目录结构；只收集和文档目标相关的信息。
3. 先读取 `references/document-system.md`，确认允许保留的文档类型、目录结构和内容边界。
4. 创建或重写具体文档时，读取 `references/document-templates.md`，按对应模板裁剪，不保留无意义占位段落。
5. 评审已有文档或交付前，读取 `references/review-checklist.md` 做自检。
6. 交付时说明新增或更新了哪些文档、哪些内容来自代码事实、哪些内容仍需产品或负责人确认。

## Reference Routing

- 文档体系、目录、保留范围、禁止复述内容：读取 `references/document-system.md`
- `README.md`（含 AI 项目上下文）、`AGENTS.md`、需求和功能设计的模板：读取 `references/document-templates.md`
- 文档评审、补齐检查、AI 可读性检查、交付自检：读取 `references/review-checklist.md`

## Working Rules

- 默认使用中文编写项目文档，除非仓库已有明确英文文档体系或用户要求英文。
- 保持项目既有文档风格、标题层级、命名规则和代码风格约定。
- 同类对象使用稳定标题和结构化列表描述，不使用 Markdown 表格。
- 长期保留的文档只包含：项目入口与 AI 项目上下文、AI 协作规则、需求与产品意图、复杂功能设计。
- 不手工维护接口完整列表、数据库完整表结构、路由完整清单、枚举完整值、组件 props 清单、Controller 方法清单等代码可直接查询的信息。
- 对接口、数据表、部署、路由、构建产物等代码或配置已有事实源的内容，只写“去哪里查”和关键入口路径。
- 不从代码强行推断产品意图；无法确认的业务目标、验收标准、角色差异和设计原因，明确标记为 `待确认`。
- 产品需求使用“场景验证点”描述典型业务使用方式，每个验证点必须包含场景、角色、操作和正常业务结果。
- 产品需求使用“功能清单”描述当前全部功能；业务规则和验收标准写在对应具体功能下，不单独维护全局清单。
- 有页面的功能需要在对应具体功能下说明页面结构，包括筛选区、操作区、列表、列表规则和按钮行为；没有独立页面时明确写“无”。
- 产品需求需要记录业务依赖关系，明确相关插件、依赖的数据或能力、受影响功能以及依赖缺失时的表现。
- 复杂功能设计只覆盖状态流转复杂、权限复杂、跨系统联动、异步任务、金额、审批、调度或容易误改的功能。

## Document Set

项目文档默认收敛为以下 4 类：

- `README.md`：项目入口 + AI 项目上下文
- `AGENTS.md`：给 AI 的协作规则
- `docs/PRODUCT_REQUIREMENTS.md`：需求与产品意图
- `docs/FEATURE_DESIGN/*.md`：单个复杂功能设计

## Conflict Order

规则冲突时，按以下顺序决策：

1. 用户当前明确要求
2. 项目根目录 `AGENTS.md`
3. 当前仓库实际代码、配置和目录结构
4. 已有长期文档中的明确约定
5. 本 skill 的 references
6. 局部最小改动原则
