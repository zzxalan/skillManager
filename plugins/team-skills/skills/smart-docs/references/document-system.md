# Document System

## Goal

为 smart 项目保留一套少而稳的长期文档。文档用于人类评审和 AI 快速建立项目心智模型，只记录代码难以稳定表达的背景、意图、边界和决策。

## Directory

```text
.
├── README.md
├── AGENTS.md
└── docs
    ├── PRODUCT_REQUIREMENTS.md
    ├── FEATURE_DESIGN
    │   └── <feature-name>.md
    └── ADR
        └── 0001-<decision-name>.md
```

## Document Responsibilities

| 文档 | 目标读者 | 主要职责 |
| --- | --- | --- |
| `README.md` | 新成员、评审者、AI | 项目入口、AI 项目上下文、启动入口、目录导读、推荐阅读路径、文档索引、代码事实入口 |
| `AGENTS.md` | AI coding agent | 协作规则、代码风格、常用命令、验证方式、禁止事项 |
| `docs/PRODUCT_REQUIREMENTS.md` | 产品、研发、评审者、AI | 业务背景、目标用户、功能范围、业务规则、验收标准 |
| `docs/FEATURE_DESIGN/*.md` | 研发、评审者、AI | 单个复杂功能的流程、规则、前后端分工、异常场景 |
| `docs/ADR/*.md` | 研发、架构评审者、AI | 关键架构或设计决策的背景、原因、影响和替代方案 |

## What To Write

- 写业务目标、用户角色、核心场景、产品意图和验收标准。
- 写模块边界、前后端职责边界、插件边界、数据归属和关键调用方向。
- 在 `README.md` 写项目目标、系统边界、核心模块、前后端关系、推荐阅读路径和关键注意事项，帮助 AI 快速建立项目心智模型。
- 写复杂功能的状态流转、权限差异、异常处理、异步影响和关键业务不变量。
- 写架构决策背后的原因、放弃的备选方案、已知代价和后续动作。
- 写 AI 阅读代码的推荐顺序和关键入口文件路径。

## What Not To Maintain Manually

不要在长期文档里手工复制以下内容：

- 接口完整列表、请求参数完整清单、响应字段完整清单。
- 数据库完整表结构、字段逐项说明、索引逐项说明。
- 前端路由完整清单、组件 props 完整清单、枚举值完整复制。
- 后端 Controller 方法清单、Service 方法清单、Mapper XML 逐项解释。
- CI/CD 脚本、部署命令、环境变量完整清单。

这些内容应该以代码、OpenAPI、实体、migration、配置、脚本或 CI 文件为事实源。文档中只写关键入口和查询位置。

## Source Of Truth Pointers

当文档需要提到代码可查询事实时，使用“入口指针”替代复制：

```markdown
## 代码事实入口

- 接口定义：查看 `<path-to-controller-or-api-folder>`
- 前端请求：查看 `<path-to-request-folder>`
- 数据模型：查看 `<path-to-entity-or-migration-folder>`
- 路由配置：查看 `<path-to-router-folder>`
- 构建与部署：查看 `<path-to-ci-or-script>`
```

## Feature Design Threshold

只有满足以下任一条件的功能，才创建 `docs/FEATURE_DESIGN/*.md`：

- 权限、角色、租户或数据范围规则复杂。
- 状态流转不可随意回退，或会影响审批、账务、调度、审计。
- 前后端、多个插件、第三方系统或异步任务共同参与。
- 业务规则从代码反推成本高，且误改风险高。
- 已在评审、联调或维护中反复产生理解偏差。

普通 CRUD、简单页面调整、纯样式变更不创建长期功能设计文档。

## ADR Threshold

满足以下任一条件时，创建 `docs/ADR/0001-<decision-name>.md`：

- 决策会长期影响模块边界、技术栈、权限模型、数据归属或扩展方式。
- 存在多个可行方案，需要记录为什么选择当前方案。
- 当前方案有明确代价、技术债或后续迁移计划。
- 未来维护者或 AI 容易误判“为什么这里不按常规写”。

ADR 文件按递增编号命名，标题使用短横线小写英文或项目已有命名风格。

## Update Rules

- 新增复杂功能：同步补充或更新 `PRODUCT_REQUIREMENTS.md`，必要时新增 `FEATURE_DESIGN`。
- 修改核心业务规则：同步更新需求文档和相关功能设计。
- 修改模块边界、权限归属、数据归属、扩展方式：同步新增或更新 ADR。
- 新增项目目标、系统边界、核心模块、关键目录、启动方式、文档入口：同步更新 `README.md`。
- 新增 AI 工作约定、测试命令、禁止事项：同步更新 `AGENTS.md`。
