# 插件 AI 交付生命周期

## 适用场景

当使用 AI 开发 smart（空间管理）项目的 smart-* 插件、插件功能或插件内前后端闭环需求时，先读取本文件。

## 生命周期阶段

0. 范围冻结：确认做/不做范围、交付介质、数据归属、环境前置、阶段验收和任务依赖。
1. 需求进入：确认业务目标、插件范围、用户角色和验收标准。
2. 边界分析：确认能力属于基座、当前插件还是其他插件。
3. 契约设计：确认接口、数据、跨插件调用、前端路由、权限和打包接入。
4. 任务拆分：把需求拆成 AI 可执行、可验证的小任务。
5. 编码执行：按任务类型调用 `smart-backend-standards`、`smart-frontend-standards` 或两者，按后端、前端、数据访问、打包等专题实现。
6. 联调验证：验证插件自身、基座装载、前后端链路、跨插件调用和打包产物。
7. Review 交付：输出 PR 描述、验证记录、风险说明和规范回流结论。

## 强制规则

- 每个阶段都要有明确输出，不接受只停留在聊天记录里的结论。
- 阶段产物可以轻量，但必须足以让其他人审查。
- 阶段产物默认写入目标插件仓库的 `docs/` 下，并使用稳定文件名。
- AI 可以辅助生成方案和代码，但关键边界判断必须由开发者确认。
- 涉及基座能力、跨插件能力、数据归属、权限、安全、删除数据、迁移文件时，必须显式写入设计或验证文档。

## 推荐输出

轻量场景默认使用目标仓库 `docs/` 下的稳定文件：

- 需求进入：`<target-repo>/docs/spec.md`
- 边界分析：`<target-repo>/docs/data-ownership.md`
- 契约设计：`<target-repo>/docs/design.md`
- 任务拆分：`<target-repo>/docs/plan.md`
- 联调验证：`<target-repo>/docs/verification.md`
- Review 交付：`<target-repo>/docs/pr-description.md`

当文档内容较多时，采用渐进式披露结构：

- 需求进入：`<target-repo>/docs/spec.md` + `<target-repo>/docs/spec/`
- 边界分析：`<target-repo>/docs/data-ownership.md` + `<target-repo>/docs/data-ownership/`
- 契约设计：`<target-repo>/docs/design.md` + `<target-repo>/docs/design/`
- 任务拆分：`<target-repo>/docs/plan.md` + `<target-repo>/docs/plan/`
- 联调验证：`<target-repo>/docs/verification.md` + `<target-repo>/docs/verification/`
- Review 交付：`<target-repo>/docs/pr-description.md` + `<target-repo>/docs/pr-description/`

每个主文档只保留摘要、当前状态、文档目录和关键结论；详细规则、过程记录和验证证据放入对应的同名目录子文档。

若目标仓库已经有团队约定的稳定文档子目录，可以沿用该目录。后续补充、修订或验证回写应继续更新同一组稳定文件。

## 阶段推进条件

- 范围冻结完成：做什么、不做什么、交付介质、数据归属、环境前置和当前阶段验收明确。
- 需求进入完成：需求目标、范围、不做范围和验收标准明确。
- 边界分析完成：基座、当前插件、其他插件的职责边界明确。
- 契约设计完成：接口、数据读写、跨插件协议和前端入口明确。
- 任务拆分完成：每个任务都有改动范围、验证方式和风险点。
- 编码执行完成：代码实现、必要测试和本地验证完成。
- 联调验证完成：已验证和未验证部分被明确区分。
- Review 交付完成：PR 描述能让 reviewer 快速判断风险和验证充分性。
