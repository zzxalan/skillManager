# Document System

## Goal

为 smart 项目保留一套少而稳的长期文档。文档用于人类评审和 AI 快速建立项目心智模型，只记录代码难以稳定表达的背景、意图、边界、功能规则和业务依赖。

## Directory

```text
.
├── README.md
├── AGENTS.md
└── docs
    ├── PRODUCT_REQUIREMENTS.md
    └── FEATURE_DESIGN
        └── <feature-name>.md
```

## Document Responsibilities

- `README.md`
  - 目标读者：新成员、评审者、AI。
  - 主要职责：项目入口、AI 项目上下文、启动入口、目录导读、推荐阅读路径、文档索引、代码事实入口。
- `AGENTS.md`
  - 目标读者：AI coding agent。
  - 主要职责：协作规则、代码风格、常用命令、验证方式、禁止事项。
- `docs/PRODUCT_REQUIREMENTS.md`
  - 目标读者：产品、研发、评审者、AI。
  - 主要职责：业务背景、场景验证点、功能清单、具体功能的业务规则与验收标准、页面结构、业务依赖关系。
- `docs/FEATURE_DESIGN/*.md`
  - 目标读者：研发、评审者、AI。
  - 主要职责：单个复杂功能的流程、规则、前后端分工、异常场景。

## What To Write

- 写业务目标和产品意图。
- 使用场景验证点描述典型业务使用方式，每个验证点必须包含场景、角色、操作和正常业务结果。
- 同类对象使用稳定标题和结构化列表描述，不使用 Markdown 表格。
- 使用功能清单描述当前全部功能，并在每个具体功能下写对应的业务规则和验收标准。
- 有页面的功能在对应具体功能下写页面结构，包括筛选区、操作区、列表、列表规则和按钮行为；没有独立页面时明确写“无”。
- 写业务依赖关系，明确相关插件、依赖的数据或能力、受影响功能以及依赖缺失时的表现。
- 写模块边界、前后端职责边界、插件边界、数据归属和关键调用方向。
- 在 `README.md` 写项目目标、系统边界、核心模块、前后端关系、推荐阅读路径和关键注意事项，帮助 AI 快速建立项目心智模型。
- 写复杂功能的状态流转、权限差异、异常处理、异步影响和关键业务不变量。
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

## Update Rules

- 新增或修改典型业务场景、使用角色、操作方式或正常业务结果：同步更新 `PRODUCT_REQUIREMENTS.md` 的场景验证点。
- 新增功能：同步更新 `PRODUCT_REQUIREMENTS.md` 的功能清单，并在对应具体功能下补充业务规则和验收标准；复杂功能必要时新增 `FEATURE_DESIGN`。
- 修改业务规则或验收标准：同步更新 `PRODUCT_REQUIREMENTS.md` 中对应的具体功能，涉及复杂功能时同步更新相关功能设计。
- 修改筛选项、操作入口、列表字段、列表规则或按钮行为：同步更新 `PRODUCT_REQUIREMENTS.md` 中对应具体功能的页面结构。
- 修改业务依赖：同步更新 `PRODUCT_REQUIREMENTS.md` 的业务依赖关系及受影响功能。
- 新增项目目标、系统边界、核心模块、关键目录、启动方式、文档入口：同步更新 `README.md`。
- 新增 AI 工作约定、测试命令、禁止事项：同步更新 `AGENTS.md`。
