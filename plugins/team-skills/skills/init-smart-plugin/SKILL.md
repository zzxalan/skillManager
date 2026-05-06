---
name: init-smart-plugin
description: 用于创建 smart-mixed 初始插件、初始化 smart-core 插件工程、生成后端 Gradle 与前端 React/Vite/qiankun 插件模板；当用户手动调用 $init-smart-plugin 生成 smart-* mixed 插件项目时使用。
---

# Init Smart Plugin

## 目标

生成一个去业务化的 `smart-mixed` 初始插件项目，包含最小后端插件入口、资源声明、前端 React 19 + TypeScript + Vite + qiankun 接入结构，以及前端产物复制到后端插件包 `web/` 的链路。

## 工作流

1. 先收集必填输入：
   - 插件名称：英文插件 ID，使用 kebab-case，例如 `access-control`。
   - 中文名称：插件展示名称。
   - 基座版本：写入 `backend/gradle/libs.versions.toml` 的 `outbook-core`；如目标上下文已有 `backend/gradle/libs.versions.toml`，优先读取其中的 `outbook-core` 作为默认值。
2. 确定生成位置；默认项目目录名为 `smart-<插件名称>-mixed`。
3. 从插件名称派生：
   - Java 包名片段：默认去掉连字符并转小写。
   - 前端 app name：默认等于插件名称。
   - 资源编码片段：默认将连字符替换为下划线。
   如派生值可能与团队命名预期不一致，先询问用户。
4. 生成前必须输出确认摘要，至少包含：生成目录、插件 ID、中文名称、Java 包名片段、前端 app name、smart-core 版本。
5. 只有用户明确确认后，才运行脚本生成项目。

## 脚本

脚本路径：`scripts/init-smart-plugin.py`

常用调用：

```bash
python3 scripts/init-smart-plugin.py \
  --plugin-name demo \
  --display-name 示例插件 \
  --base-version 5.0.6 \
  --output-dir /tmp/demo \
  --yes
```

可选参数：

- `--java-package-fragment`：覆盖默认 Java 包名片段。
- `--dry-run`：只输出将创建的目录和摘要，不写入文件。
- `--force`：目标项目目录已存在时先删除再生成；默认不覆盖。
- `--yes`：跳过脚本内确认，适合已经由 agent 向用户确认过的场景。

## 冲突处理

- 目标目录已存在时默认失败，并说明需要更换目录或显式使用 `--force`。
- 参数不合法时停止生成，用中文说明缺失项或格式问题。
- 不要修改参考项目；模板与脚本只使用当前 skill 下的 `assets/`。

## 交付输出

生成完成后说明项目目录、关键文件、建议验证命令，并明确仍需在真实 smart-core 基座中加载验证。
