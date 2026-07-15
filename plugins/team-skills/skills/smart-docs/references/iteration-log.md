# Smart Docs 迭代记录

## 待评审记录

## 已处理记录

### 2026-07-15 - smart-docs 场景验证点

- 日期：2026-07-15
- 记录人或来源：用户评审反馈
- 涉及 skill：smart-docs
- 触发任务或场景：继续评审产品需求中用户和业务场景的描述方式。
- 遇到的问题：“目标用户”和“核心使用场景”分开维护，无法直接验证具体角色执行操作后是否产生预期业务结果。
- 临时解决方式：本次将两个章节合并为“场景验证点”，并同步调整主规则、文档体系和评审清单。
- 建议优化：每个场景验证点固定包含场景、角色、操作和正常业务结果。
- 建议落点：`SKILL.md`、`references/document-system.md`、`references/document-templates.md`、`references/review-checklist.md`、`agents/openai.yaml`
- 优先级：P1
- 状态：已落地
- 评审结论或关联变更：已按用户明确要求完成 skill 更新，skill 校验和场景验证点任务静态回放均通过。

### 2026-07-15 - smart-docs 结构化列表

- 日期：2026-07-15
- 记录人或来源：用户评审反馈
- 涉及 skill：smart-docs
- 触发任务或场景：继续评审产品需求和页面结构模板的表达形式。
- 遇到的问题：文档职责、核心模块、目标用户、业务依赖、功能清单和页面元素使用 Markdown 表格，不符合期望的结构化表达方式。
- 临时解决方式：本次将 smart-docs 中的 Markdown 表格统一改为稳定标题和结构化列表。
- 建议优化：同类对象统一使用“对象名称 + 字段列表”，并将“不使用 Markdown 表格”纳入主规则和评审清单。
- 建议落点：`SKILL.md`、`references/document-system.md`、`references/document-templates.md`、`references/review-checklist.md`
- 优先级：P1
- 状态：已落地
- 评审结论或关联变更：已按用户明确要求完成 skill 更新，skill 校验和结构化列表任务静态回放均通过。

### 2026-07-15 - smart-docs 页面结构

- 日期：2026-07-15
- 记录人或来源：用户评审反馈
- 涉及 skill：smart-docs
- 触发任务或场景：继续评审产品需求中具体功能的页面描述粒度。
- 遇到的问题：具体功能只有输入、输出、权限、业务规则和验收标准，缺少可用于前端开发与测试的页面结构说明。
- 临时解决方式：本次在具体功能模板中补充页面结构，并同步调整主规则、文档体系和评审清单。
- 建议优化：有页面的功能需要描述筛选区、操作区、列表、列表规则和按钮行为；没有独立页面时明确写“无”。
- 建议落点：`SKILL.md`、`references/document-system.md`、`references/document-templates.md`、`references/review-checklist.md`、`agents/openai.yaml`
- 优先级：P1
- 状态：已落地
- 评审结论或关联变更：已按用户明确要求完成 skill 更新，skill 校验和页面结构任务静态回放均通过。

### 2026-07-15 - smart-docs

- 日期：2026-07-15
- 记录人或来源：用户评审反馈
- 涉及 skill：smart-docs
- 触发任务或场景：团队评审 smart-docs 的产品文档结构和长期文档范围。
- 遇到的问题：产品需求仍使用“功能范围”，业务规则与验收标准脱离具体功能；没有业务依赖插件说明；文档体系仍保留 ADR。
- 临时解决方式：本次按用户确认的三项评审结论直接更新主规则、文档体系、模板和检查清单。
- 建议优化：使用功能清单并在具体功能中维护业务规则和验收标准；增加相关插件业务依赖关系；移除 ADR 文档类型及其全部规则。
- 建议落点：`SKILL.md`、`references/document-system.md`、`references/document-templates.md`、`references/review-checklist.md`、`agents/openai.yaml`
- 优先级：P1
- 状态：已落地
- 评审结论或关联变更：已按用户明确要求完成 skill 更新，skill 校验和真实任务静态回放均通过。
