# Skill Manager

这个仓库用于沉淀个人和团队可复用的 AI Agent Skills。当前结构按两种使用方式设计：

- `plugins/team-skills/skills/`：团队共享的正式 skills，作为 Codex plugin 分发。
- `templates/skill/`：创建新 skill 时复制的模板。

## 推荐流程

1. 先把高频、步骤稳定、反复需要解释给 AI 的流程写成候选 skill。
2. 在 `templates/skill/` 的基础上创建目录，放到 `plugins/team-skills/skills/<skill-name>/`。
3. 写清 `SKILL.md` 的 `name` 和 `description`，这是 agent 判断是否加载 skill 的入口。
4. 复杂资料放 `references/`，可重复执行的逻辑放 `scripts/`，模板和素材放 `assets/`。
5. 执行校验：

```bash
python3 scripts/validate-skills.py
```

## 个人使用

把某个 skill 同步或软链到本机的 skills 目录：

```bash
mkdir -p ~/.agents/skills
ln -s /home/zzx/code/skillManager/plugins/team-skills/skills/<skill-name> ~/.agents/skills/<skill-name>
```

如果某个项目专用，可以放到目标项目的 `.agents/skills/<skill-name>/`，跟随项目代码一起版本化。

## 团队分发

`plugins/team-skills/` 已经按 Codex plugin 结构初始化：

```text
plugins/team-skills/
├── .codex-plugin/plugin.json
└── skills/
```

当前仓库也包含 `.agents/plugins/marketplace.json`，用于把本仓库内的 `team-skills` 插件登记为 repo-local plugin。团队成员后续可以按仓库路径安装，或把这个 plugin 发布到内部插件目录。

## 设计原则

- skill 是流程和专业知识，不是泛泛的提示词合集。
- `SKILL.md` 保持短，详细内容按需拆到 `references/`。
- 脚本必须能独立运行并有清晰错误信息。
- 涉及密钥、生产系统、客户数据的 skill 默认需要人工确认和权限边界。
- 稳定后再共享给团队，避免把一次性经验固化成长期规则。

更多管理建议见 [docs/skill-management.md](docs/skill-management.md)。
