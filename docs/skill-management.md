# AI Skills 管理方案

## 结论

把 skills 当成“可版本化的流程资产”管理，而不是普通 prompt 文档。一个合格 skill 应该能让 agent 在相同输入下稳定复现团队做事方式，包含必要的步骤、判断边界、工具顺序、引用资料和可执行脚本。

推荐分三层管理：

| 层级 | 适用场景 | 建议位置 |
| --- | --- | --- |
| 个人层 | 个人偏好、个人工具链、未验证流程 | `~/.agents/skills/` |
| 项目层 | 只服务某个代码仓库或业务系统 | 目标项目的 `.agents/skills/` |
| 团队层 | 多成员复用、可审查、可发布 | 本仓库 `plugins/team-skills/skills/` |

## 官方格式要点

Agent Skills 的开放格式非常轻：一个 skill 至少是一个目录加 `SKILL.md`。`SKILL.md` 顶部必须有 YAML frontmatter，核心字段是 `name` 和 `description`。`name` 需要和目录名一致，并使用小写字母、数字、连字符；`description` 要说明 skill 做什么，以及什么时候使用它。

典型结构：

```text
my-skill/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

加载模型是渐进式的：启动时通常只读取所有 skill 的 `name` 和 `description`，命中后才读取完整 `SKILL.md`，再按需读取 `references/` 或运行 `scripts/`。所以 `description` 决定触发质量，`SKILL.md` 决定执行质量。

## Skill 与 Plugin 的边界

- Skill：让 agent 按你的流程做事。适合规范、步骤、领域知识、模板、固定检查清单。
- Plugin：把 skill、MCP、app connector、hooks、assets 等打包成可安装能力。适合团队共享或跨仓库分发。

简单判断：

| 需求 | 用什么 |
| --- | --- |
| “以后都按我们的发布流程写 release note” | skill |
| “需要连接 Jira/GitHub/内部系统并带一组工作流” | plugin + skill |
| “某个仓库有独特代码风格和目录规则” | 项目内 `.agents/skills/` 或 `AGENTS.md` |
| “所有团队成员都要安装同一批能力” | plugin |

## 什么值得沉淀成 Skill

优先沉淀这几类：

- 高频重复任务：每周报告、PR review、发布检查、客户周报、测试生成。
- 需要业务上下文的任务：字段含义、口径、流程、审批规则、内部术语。
- 需要固定工具顺序的任务：先查哪个系统、再跑哪个脚本、最后如何汇总。
- 结果格式稳定的任务：邮件、文档、表格、SQL、评审报告、测试报告。
- 容易出错的任务：生产操作前检查、数据导出脱敏、安全审查。

不建议沉淀：

- “写得更好一点”“更严谨一点”这类泛化偏好，放 `AGENTS.md` 更合适。
- 一次性临时流程。
- 还没有跑通过的实验脚本。
- 会让 agent 绕过审批、密钥、权限边界的流程。

## 生命周期

建议每个 skill 经过以下状态：

| 状态 | 含义 | 进入下一阶段的条件 |
| --- | --- | --- |
| `candidate` | 候选想法，还只是 prompt 或流程草稿 | 至少有 2 个真实使用场景 |
| `draft` | 已有 `SKILL.md`，可手动调用 | 本人完成一次真实任务 |
| `pilot` | 小范围给同事试用 | 至少 2 人反馈可用 |
| `stable` | 纳入团队 plugin | 通过校验和 review |
| `deprecated` | 不再推荐使用 | 有替代 skill 或流程废弃 |

这个仓库当前没有强制 registry，避免一开始管理成本过高。团队 skills 变多后，可以再补 `catalog.json` 记录 owner、状态、适用系统和变更记录。

## 编写规范

### `description` 写法

`description` 应该包括三件事：

1. 这个 skill 能完成什么任务。
2. 什么时候应该使用。
3. 明确触发词或文件类型。

推荐：

```yaml
description: Generate release notes from merged PRs, commits, and issue links using the team release format. Use when preparing a product release, changelog, release announcement, or version summary.
```

不推荐：

```yaml
description: Helps write release notes.
```

### `SKILL.md` 内容

保持短、明确、可执行。建议包含：

- 任务入口：先确认哪些输入。
- 执行步骤：按顺序做什么。
- 工具和脚本：什么时候运行哪个脚本。
- 输出格式：标题、字段、排序、语言风格。
- 边界条件：缺数据、冲突、权限不足时怎么办。

### `references/`

用于存放较长的上下文，避免污染主 `SKILL.md`：

- `references/schema.md`：数据表、字段、接口结构。
- `references/style-guide.md`：品牌语气、文案规则。
- `references/runbook.md`：详细运维步骤。
- `references/examples.md`：输入输出样例。

### `scripts/`

用于可重复、需要确定性的动作：

- 数据转换。
- 文件解析。
- 报告生成。
- 静态检查。
- API 包装。

脚本要求：

- 不依赖隐式当前目录，路径参数显式传入。
- 出错时返回非 0。
- 输出可读，必要时支持 JSON。
- 不把密钥写入日志。

### `assets/`

用于模板、图片、字体、样例文件等静态资源。agent 应该使用它们生成最终产物，而不是把大文件加载进上下文。

## Review 清单

每次把 skill 从 `draft` 推到 `stable` 前，至少检查：

- `name` 与目录名一致，符合 kebab-case。
- `description` 足够具体，包含“什么时候使用”。
- `SKILL.md` 没有塞入大段可拆分资料。
- 文件路径都是相对 skill 根目录。
- 脚本可以在干净环境跑通。
- 没有硬编码密钥、token、个人路径。
- 涉及外部系统时说明权限、审批和失败处理。
- 输出格式能被同事复用，不只适合作者本人。

## 本仓库落地方式

当前仓库结构：

```text
.
├── .agents/plugins/marketplace.json
├── docs/skill-management.md
├── plugins/team-skills/
│   ├── .codex-plugin/plugin.json
│   └── skills/
├── scripts/validate-skills.py
└── templates/skill/
```

新增团队 skill：

```bash
mkdir -p plugins/team-skills/skills/<skill-name>
cp -R templates/skill/. plugins/team-skills/skills/<skill-name>/
```

然后修改：

- `plugins/team-skills/skills/<skill-name>/SKILL.md`
- `plugins/team-skills/skills/<skill-name>/agents/openai.yaml`

最后执行：

```bash
python3 scripts/validate-skills.py
```

## 后续建议

可以优先沉淀 3 个高价值 skill：

- `code-review`：按团队标准审查 PR，输出严重级别、文件行号、风险和测试缺口。
- `release-note`：从 PR、commit、issue 生成团队格式的 release note。
- `project-onboarding`：让新成员或 agent 快速理解项目结构、启动方式、测试策略和常见坑。

## 参考来源

- OpenAI Academy: Plugins and skills, https://openai.com/academy/codex-plugins-and-skills/
- OpenAI Skills Catalog, https://github.com/openai/skills
- OpenAI Help Center: Skills in ChatGPT, https://help.openai.com/articles/20001066-skills-in-chatgpt
- Agent Skills specification, https://agentskills.io/specification
