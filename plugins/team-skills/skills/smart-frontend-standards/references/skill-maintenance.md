# 前端 skill 维护与扩展

## 适用场景

在前端开发或 review 中发现新规范、新统一组件、新踩坑结论、新评审规则，或发现现有前端 reference 粒度不合适时，读取本文件。

## 何时更新 skill

在出现以下情况时更新：

- 同类前端任务重复遵守某条新规则。
- 某个统一页面壳、统一表格、统一导航、统一请求封装、统一错误处理或统一 H5 接入方式被正式采用。
- 代码审查中重复出现同类前端问题。
- 某个 reference 已明显过大，需要继续拆分。
- 仓库真实实现与既有说明发生变化，skill 中的参考位置或链路说明需要同步。

## 如何选择落点

- 前端宿主边界、插件 API 前缀、资源入口、敏感信息：更新 `architecture-boundary.md`
- 页面结构、共享组件、布局、hooks、请求 effect：更新 `frontend-page-structure.md`
- 列表、CRUD、表格、表单、`VAObkTable`：更新 `frontend-table-list.md`
- 面包屑与导航：更新 `frontend-navigation.md`
- 视觉结构、超长文本、错误提示、交互规范：更新 `frontend-design-guidelines.md`
- H5 移动端页面开发：更新 `frontend-h5-development.md`
- qiankun、Vite、微前端接入、请求前缀与请求封装：更新 `frontend-microfrontend.md`
- 编码风格、代码注释、可读性与复杂流程说明：更新 `coding-style.md`
- 打包、复制、发布、远程更新、接口联调鉴权：更新 `integration-build-packaging.md`
- 评审要求：更新 `review-checklist.md`

若新规则跨多个主题，优先放到影响最大的主题文件；只有在规则已经形成独立专题时，才新增新的 reference 文件。

## 如何写新增规则

统一使用以下模板：

1. 适用场景
2. 强制规则
3. 推荐模式
4. 禁止做法
5. 开发或评审检查点
6. 仓库参考位置

优先写会影响决策的硬规则，不堆砌显而易见的常识。

## 如何控制膨胀

- 不把细则堆回 `SKILL.md`。
- 同一文件同时出现多个彼此独立的主题时，拆出新的 reference。
- 单条规范只保留一个权威落点，避免在多个文件重复写。
- 若某条规则只是某次任务的临时偏好，不急于沉淀进 skill。

## 更新后的最小验证

每次更新后至少执行：

1. 检查 `SKILL.md` 是否仍能把前端任务路由到正确的 reference。
2. 在 `skillManager` 仓库运行 `python3 scripts/validate-skills.py`。
3. 用一个真实前端任务回放，确认 agent 能读到新增规则并据此做决策。

## 交付要求

更新 skill 时，在交付说明中明确：

- 新增或修改了哪些规则。
- 规则落在哪个 reference。
- 为什么放在这个 reference。
- 这次更新会改善哪些后续前端开发任务或 review 场景。
