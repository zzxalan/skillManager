---
name: smart-project-workflow
description: "用于 smart（空间管理）项目中 smart-core 基座与 smart-* 插件开发的流程层规范。适用于借助 AI 从需求澄清、插件边界分析、方案设计、任务拆分、实现推进、联调验证到 PR 交付的完整流程；当任务需要先明确插件边界、数据归属、接口契约、实施计划、验证记录或规范回流方式时使用。本 skill 负责交付流程编排；实际代码实现必须按任务类型配合 smart-backend-standards 或 smart-frontend-standards。"
---

# Smart Project Workflow

## 定位

本 skill 是 smart（空间管理）项目中 smart-core 基座与 smart-* 插件的 AI 交付流程规范。

术语统一：

- `smart`：空间管理项目。
- `smart-core`：基座，不是插件。
- `smart-*`：运行在 smart-core 基座上的插件或业务模块。
- `smart-backend-standards`：smart 项目后端实现层规范，负责 Java、Spring、数据访问、接口、调度、消息、插件后端接入、打包联调和后端审查。
- `smart-frontend-standards`：smart 项目前端实现层规范，负责 React、TypeScript、Vite、qiankun、页面、表格、导航、样式、前端构建接入和前端审查。
- 本 skill：流程编排层规范，负责约束插件开发中如何使用 AI 从需求走到交付。

不要把本 skill 当成代码实现规范；涉及实际代码修改时，必须按后端、前端或全栈任务进入对应实现层 skill 的路由和检查流程。

## Core Workflow

1. 先读取 `references/plugin-lifecycle.md`，确认当前任务处于哪个交付阶段。
2. 需求不清时，读取 `references/requirement-intake.md`，先形成可评审需求。
3. 涉及任何代码实现、数据库、接口、前端页面、基座能力或跨插件依赖时，先读取 `references/boundary-analysis.md`。
4. 涉及前后端协作、跨插件能力、数据读写或外部集成时，读取 `references/contract-design.md`。
5. 开发前读取 `references/implementation-plan.md`，把任务拆成 AI 可稳定执行的小步。
6. 进入编码时，读取 `references/ai-coding-execution.md`，并按任务类型触发 `smart-backend-standards`、`smart-frontend-standards` 或两者。
7. 交付前读取 `references/verification-handoff.md`，输出验证与 PR 交接材料。
8. 发现可复用规范、重复问题或新的踩坑结论时，读取 `references/workflow-maintenance.md`，决定沉淀到本 skill、实现层 standards，还是按 `team-skill-iteration` 记录待评审。

## Hard Gates

- 没有需求澄清产物，不进入技术设计。
- 没有插件边界分析，不进入代码实现。
- 没有数据归属判断，不新增表、不改表、不写入疑似其他插件拥有的数据。
- 没有接口或跨插件契约，不让前后端或插件间调用并行散写。
- 没有实施计划，不做大范围一次性修改。
- 没有验证记录，不输出完成结论。
- 交付前必须按命中的实现层 standards 的 review checklist 做自检。

## Delivery Artifacts

推荐每个需求在目标仓库保留以下稳定产物。目标仓库指当前需求实际归属的 `smart-*` 插件仓库；涉及基座改动时，目标仓库可以是 `smart-core`。

```text
<target-repo>/docs/
  spec.md
  design.md
  data-ownership.md
  plan.md
  verification.md
  pr-description.md
```

如果某个阶段文档内容较多，采用渐进式披露：保留对应的 `<target-repo>/docs/<artifact>.md` 作为主索引，只放摘要、当前状态和子文档链接；详细内容拆分到同名目录 `<target-repo>/docs/<artifact>/` 中，例如需求拆到 `docs/spec/`，方案拆到 `docs/design/`。

阶段文档必须写入后续 AI 和开发者能稳定发现的位置。默认使用目标仓库 `docs/` 下的固定文件名；如团队已有固定子目录，可以沿用该稳定目录。

模板位于 `assets/templates/`：

- `plugin-spec.md`：需求澄清模板。
- `plugin-design.md`：插件方案设计模板。
- `data-ownership.md`：数据归属与边界分析模板。
- `implementation-plan.md`：实施计划模板。
- `verification-report.md`：交付验证模板。
- `pr-description.md`：PR 描述模板。

## Relationship With Implementation Standards

本 skill 只负责回答：

> 如何借助 AI 稳定交付一个 smart-* 插件或插件功能？

实现层 standards 负责回答：

> smart-* 插件的后端或前端代码应该怎么写、怎么接入 smart-core 基座、怎么打包、怎么审查？

进入代码实现时，必须按任务类型读取：

- 后端任务：`smart-backend-standards/SKILL.md`、`references/architecture-boundary.md`、当前后端专题 reference、`references/coding-style.md`、`references/review-checklist.md`
- 前端任务：`smart-frontend-standards/SKILL.md`、`references/architecture-boundary.md`、当前前端专题 reference、`references/coding-style.md`、`references/review-checklist.md`
- 全栈、插件接入、打包或联调任务：同时读取后端和前端 standards 中命中的 reference

若本 skill 与实现层 standards 对同一实现细节有冲突，以实现层 standards 为准；若冲突发生在流程阶段、交付产物、PR 交接上，以本 skill 为准。
