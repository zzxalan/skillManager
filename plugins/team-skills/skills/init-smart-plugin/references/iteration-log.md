# Init Smart Plugin 迭代记录

## 待评审记录

## 已处理记录

### 2026-07-07 - init-smart-plugin

- 日期：2026-07-07
- 记录人或来源：用户反馈
- 涉及 skill：init-smart-plugin
- 触发任务或场景：用户检查插件初始化模板，指出生成模板没有完整复用参考插件 `smart-meeting-mixed` 的前后端依赖和前端框架骨架。
- 遇到的问题：后端依赖被按需裁剪，缺少 MyBatis-Flex 注解处理器和 smart-core 测试依赖；前端模板缺少 H5 入口、请求封装、shared/types、pnpm lockfile 等参考项目框架层文件，模板失去复用意义。
- 临时解决方式：本次直接同步参考项目工程配置和前端框架文件，删除会议业务目录后用通用占位页面替换，并将插件名、标题、包名改为模板占位符。
- 建议优化：模板维护规则明确为“先从参考项目完整复制依赖和框架，再去业务化”，禁止为了精简示例代码自行移除工程框架或依赖。
- 建议落点：`SKILL.md`、`assets/templates/smart-mixed-plugin/backend/build.gradle`、`assets/templates/smart-mixed-plugin/frontend/**`
- 优先级：P1
- 状态：已落地
- 评审结论或关联变更：已按用户明确要求更新模板资产和维护原则。
