# Skill Manager

这个仓库用于沉淀个人和团队可复用的 AI Agent Skills。当前结构按两种使用方式设计：

- `plugins/team-skills/skills/`：团队共享的正式 skills，作为 Codex / ZCode plugin 分发。
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

## MCP 自动安装

`team-skills` 插件内置 smart-cicd MCP 配置。安装插件后客户端会自动加载 `.mcp.json`；默认连接 `http://127.0.0.1:3000/api/mcp`，部署环境请设置 `SMART_CICD_MCP_URL`。账号密码只通过 `SMART_CICD_MCP_USERNAME`、`SMART_CICD_MCP_PASSWORD` 注入请求头，MCP 地址仅限内网，不得暴露公网。Smart 项目相关操作统一使用 `smart-platform`。

## 个人使用

把某个 skill 同步或软链到本机的 skills 目录：

```bash
mkdir -p ~/.agents/skills
ln -s /home/zzx/code/skillManager/plugins/team-skills/skills/<skill-name> ~/.agents/skills/<skill-name>
```

如果某个项目专用，可以放到目标项目的 `.agents/skills/<skill-name>/`，跟随项目代码一起版本化。

## 团队分发

`plugins/team-skills/` 同时按 Codex plugin 和 ZCode plugin 结构初始化：

```text
.
├── marketplace.json                      # ZCode marketplace（仓库根目录）
└── plugins/team-skills/
    ├── .codex-plugin/plugin.json         # Codex plugin manifest
    ├── .zcode-plugin/plugin.json         # ZCode plugin manifest
    └── skills/
```

仓库内的 `.agents/plugins/marketplace.json` 是 Codex 侧的 repo-local marketplace 登记。

### 在 ZCode 中安装

ZCode 添加 marketplace 时只探测 `.claude-plugin/marketplace.json` 和仓库根目录的 `marketplace.json`，并按 `.zcode-plugin/plugin.json`（兜底 `.claude-plugin/`、`.codex-plugin/`）读取插件清单。

团队成员任选一种方式：

1. 打开 **Settings → Plugin Management → Discover**，点 **`+`** 添加 marketplace：
   - 本地目录：选择本仓库根目录；
   - 或填入 GitHub 仓库，例如 `zzxalan/skillManager`。
2. 在 Discover 列表找到 `团队技能`（`team-skills@skill-manager`），点 **Get** 安装，默认启用。
3. 在 **Settings → Skills** 或 `/` 菜单确认技能已出现。

更新 skills 后，在 marketplace 上刷新并重装插件即可拿到新版本；发布前记得把 `marketplace.json` 与 `.zcode-plugin/plugin.json`、`.codex-plugin/plugin.json` 的 `version` 保持一致（校验脚本会检查 ZCode 侧的版本一致性）。

## 设计原则

- skill 是流程和专业知识，不是泛泛的提示词合集。
- `SKILL.md` 保持短，详细内容按需拆到 `references/`。
- 脚本必须能独立运行并有清晰错误信息。
- 涉及密钥、生产系统、客户数据的 skill 默认需要人工确认和权限边界。
- 稳定后再共享给团队，避免把一次性经验固化成长期规则。

更多管理建议见 [docs/skill-management.md](docs/skill-management.md)。
