# 流程维护与规范回流

## 适用场景

当开发、联调或 review 中发现新的通用流程、重复踩坑、评审规则或实现规范时，读取本文件。

## 判断沉淀位置

沉淀到本 skill 的情况：

- 需求澄清、边界分析、契约设计、计划拆分、验证交付流程发生变化。
- 插件开发协作方式、PR 交接方式、阶段产物模板发生变化。
- AI 使用流程、阶段门禁或任务拆分方式需要统一。

沉淀到 `smart-backend-standards` 的情况：

- 后端接口、数据访问、MyBatis-Flex、CommonResult、Quartz、EventBus、TimeManager 等实现规则。
- Extract 扩展、消息能力、NodeService、插件后端打包联调等实现规则。

沉淀到 `smart-frontend-standards` 的情况：

- 前端页面结构、VAObkTable、useBreadcrumb、qiankun、Vite、Ant Design、UnoCSS 等实现规则。
- 代码审查中发现的实现层高频问题。

按 `team-skill-iteration` 记录待评审的情况：

- 新规则来自单次任务，还没有形成稳定共识。
- 规则可能影响多个 skill 的触发、职责边界或默认流程。
- 需要团队评审后再决定是否立即沉淀。

## 更新原则

- 不把实现细节堆到本 skill。
- 不把流程门禁堆到后端或前端 standards。
- 单条规则只保留一个权威落点。
- 新规则必须来自真实任务、重复问题或明确的团队约定。
- 临时偏好不沉淀。

## 更新后的检查

- `SKILL.md` 是否仍然只承担路由和核心流程。
- reference 是否放在最贴近的主题文件。
- 模板是否与流程阶段一致。
- 是否能用一个真实插件需求回放流程。
- 若更新了后端或前端 standards，按对应 skill 的 `review-checklist.md` 和本仓库 skill 校验脚本执行最小验证。

## 交付说明

更新流程或规范后，交付中说明：

- 更新了哪个 skill。
- 更新了哪些 reference 或模板。
- 为什么放在这个位置。
- 后续能减少哪类跑偏、返工或 review 成本。
