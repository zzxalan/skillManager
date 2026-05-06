# AI 编码执行

## 适用场景

当已经完成需求、边界、契约和计划，开始让 AI 修改 smart-* 插件代码或与 smart-core 基座交互的代码时，读取本文件。

## 必须调用的实现层规范

实际代码修改必须按任务类型使用当前团队中的实现层 standards。

执行顺序：

1. 后端任务读取 `smart-backend-standards/SKILL.md`，前端任务读取 `smart-frontend-standards/SKILL.md`，全栈或接入任务两者都读。
2. 读取命中 standards 的 `references/architecture-boundary.md`。
3. 按任务类型读取对应专题 reference。
4. 涉及代码修改时读取命中 standards 的 `references/coding-style.md`。
5. 涉及插件入口、构建、打包、资源、远程更新或接口联调时读取命中 standards 的 `references/integration-build-packaging.md`。
6. 完成前读取命中 standards 的 `references/review-checklist.md`。

## AI 执行规则

- 先读实际工程代码，再决定实现方案。
- 优先复用 smart-core 基座能力、统一封装、统一组件和邻近插件模式。
- 不为单个插件需求重造通用基础设施。
- 不绕过已有接口、服务、组件、打包链路或插件生命周期。
- 不进行与当前任务无关的大面积格式化、重构或目录调整。
- 代码实现必须同步更新必要的接口、类型、迁移、页面和接入配置。
- 每次完成后说明改了哪些文件、为什么改、如何验证。

## 前后端协作规则

- 后端接口先稳定契约，再驱动前端接入。
- 前端页面优先使用项目既有组件和布局模式。
- 列表、CRUD、导航、面包屑、错误提示等按 `smart-frontend-standards` 的前端 reference 执行。
- 前端不能用 mock 结果掩盖后端契约缺失；临时 mock 必须在交付说明中标记。

## 后端协作规则

- 接口返回、分页、数据访问、时间能力、事件、调度、消息、跨插件调用按 `smart-backend-standards` 专题规范执行。
- 涉及写库时，必须同时考虑新增和更新分支。
- 涉及状态流转时，必须避免整实体覆盖职责外字段。
- 涉及其他插件数据时，必须通过契约消费，不直接写表。

## 交付输出

每轮编码完成后，AI 至少输出：

- 改动文件。
- 实现要点。
- 已执行验证。
- 未验证部分。
- 剩余风险。
- 是否发现需要沉淀的新规范。
