# Smart Backend Standards 迭代记录

## 待评审记录

### 2026-09-11 - MyBatis-Flex Model.update 更新条件

- 日期：2026-09-11
- 记录人或来源：用户反馈
- 涉及 skill：smart-backend-standards
- 触发任务或场景：补充后端数据访问规范，强调 MyBatis-Flex `Model.update()` 的更新条件风险。
- 遇到的问题：容易误以为 `Model.update()` 会自动按实体主键追加 `where id`，实际可能因默认 `queryWrapper` 没有条件而更新整表。
- 临时解决方式：在数据访问和评审检查中明确要求使用显式唯一条件的局部更新。
- 建议优化：在 skill 入口增加醒目高风险提示，并保留数据访问 reference 的详细说明。
- 建议落点：`SKILL.md`、`references/backend-data-access.md`、`references/review-checklist.md`
- 优先级：P1
- 状态：已落地
- 评审结论或关联变更：已按用户明确要求完成规范更新。

## 已处理记录
