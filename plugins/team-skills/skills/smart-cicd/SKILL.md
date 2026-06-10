---
name: smart-cicd
description: 用于 smart 项目内网 CI/CD 打包、部署与发版操作；当用户说“xxx打包”“更新188”“更新201”“更新124”、执行 Gradle 发布、部署 develop/master 分支包、从 Nexus smart-package 仓库同步基座包和插件包、重启 smart-server、查看部署日志或排查部署失败时使用。
---

# Smart CI/CD

## 目标

支持本地 smart 项目打包发布到 Nexus，并从内网 Nexus 仓库 `smart-package` 下载指定分支的 smart 基座包和插件包，部署到目标服务器，重启 `smart-server`，检查服务状态和日志。

## 目标映射

| 用户说法 | 服务器 | 分支 |
| --- | --- | --- |
| `更新201` / `201` | `192.168.50.201` | `develop` |
| `更新188` / `188` | `192.168.50.188` | `master`，Nexus 路径为 `release` |
| `更新124` / `124` | `192.168.50.124` | `master`，Nexus 路径为 `release` |

## 固定环境

- Nexus：`http://192.168.50.122:8081/#browse/browse:smart-package`
- Nexus API 根地址：`http://192.168.50.122:8081`
- Nexus 仓库：`smart-package`
- 远端基座目录：`/data/smart/app`
- 远端插件目录：`/data/smart/app/plugins`
- 服务重启命令：`systemctl restart smart-server`
- 日志目录：`/data/smart/app/logs`
- 内网默认账号写在脚本中，优先使用环境变量覆盖：
  - `SMART_CICD_NEXUS_USERNAME`
  - `SMART_CICD_NEXUS_PASSWORD`
  - `SMART_CICD_SSH_USERNAME`
  - `SMART_CICD_SSH_PASSWORD`

## 打包脚本

脚本路径：`scripts/package-smart-project.py`

用户说 `xxx打包` 时，先把 `xxx` 当作项目目录名或路径，先进入它的 `frontend` 目录构建静态文件：

```bash
pnpm build
```

前端构建成功后，再进入它的 `backend` 目录执行：

```bash
./gradlew clean 发布 --refresh-dependencies -Pbranch=${branch}
```

`branch` 只能是 Gradle 发布参数使用的 `develop` 或 `release`：

- 用户明确说 `develop` 时用 `develop`。
- 用户明确说 `release`、`master`、`main` 时用 `release`。
- 用户没有说明时，读取项目 Git 分支：`develop` 分支用 `develop`，`master/main/release/*` 用 `release`。
- 如果无法推断，先询问用户要打 `develop` 还是 `release`。

常用调用。执行脚本时先进入本 skill 目录，不要写死某台电脑的绝对路径：

```bash
cd <smart-cicd-skill-dir>
python3 scripts/package-smart-project.py activity --branch develop
```

只预览命令，不执行：

```bash
cd <smart-cicd-skill-dir>
python3 scripts/package-smart-project.py activity --branch release --dry-run
```

## 部署脚本

脚本路径：`scripts/deploy-smart-package.py`

显式部署时直接运行：

```bash
cd <smart-cicd-skill-dir>
python3 scripts/deploy-smart-package.py 188 --execute
```

只预览将部署哪些包：

```bash
cd <smart-cicd-skill-dir>
python3 scripts/deploy-smart-package.py 188
```

指定分支或覆盖分类规则：

```bash
cd <smart-cicd-skill-dir>
python3 scripts/deploy-smart-package.py 201 \
  --branch develop \
  --plugin-regex '(^|/)plugins?(/|$)|-plugin-' \
  --execute
```

## 工作流

1. 如果用户说 `xxx打包`：
   - 将 `xxx` 作为项目目录名或路径，运行打包脚本。
   - 打包脚本必须先在 `frontend` 目录执行 `pnpm build`，成功后再执行后端 Gradle 发布。
   - 如果用户同时说了 `develop`、`release`、`master`、`main`，按打包分支规则传入 `--branch`。
   - 如果用户没说分支，允许脚本根据 Git 当前分支自动推断；推断失败时询问用户。
   - 前端构建或后端打包失败时保留关键错误，不要继续部署。
2. 如果用户说更新服务器，解析部署目标：
   - 用户说 `更新188`、`更新201`、`更新124` 时，按目标映射选择服务器和分支。
   - 如果用户只说“更新服务器”但没有目标，先询问目标服务器。
   - 不要部署到映射外服务器，除非用户明确给出 IP、分支和确认。
3. 对明确的更新请求，运行部署脚本并加 `--execute`。
4. 部署脚本会：
   - 通过 Nexus REST API 列出 `smart-package` 仓库资产。
   - 过滤路径或文件名中包含目标分支的包；`master` 会按 Nexus 中的 `release` 包处理。
   - 默认只部署 `.jar`、`.war`、`.zip`、`.tar.gz`、`.tgz`、`.tar` 文件。
   - Nexus 保留多版本历史时，默认按模块只取最新版本；需要部署所有历史版本时才加 `--all-versions`。
   - 依据包路径或文件名分类：匹配基座规则的放入 `/data/smart/app`，其余默认放入 `/data/smart/app/plugins`。
   - 上传前备份远端同名文件到 `/data/smart/app/backups/deploy-<timestamp>`。
   - 如果本次包含插件包，上传插件前先把 `/data/smart/app/plugins` 现有内容备份到 `/data/smart/app/backups/deploy-<timestamp>/plugins-before-clear`，再清空 plugins 目录，避免旧版本插件 jar 残留。
   - 上传包、重启 `smart-server`、检查 `systemctl is-active`，并输出最新日志尾部。
   - SSH 优先使用 `paramiko`，其次使用 `sshpass`，都没有时使用 macOS/Linux 标准库 `pty` 调用系统 `ssh/scp`。
5. 如果脚本提示没有匹配包、分类不符合预期、Nexus API 不通、SSH 依赖缺失或服务未启动，停止并把错误、已执行步骤和下一步建议反馈给用户。

## 安全规则

- 不要删除远端基座目录中未被本次包覆盖的文件；插件目录例外，部署插件包时必须先备份并清空 `/data/smart/app/plugins`。
- 不要把 `master` 包部署到 `201`，也不要把 `develop` 包部署到 `188` 或 `124`，除非用户明确要求覆盖默认映射。
- 如果只是用户问“有哪些包”“先看一下”“dry run”，不要加 `--execute`。
- 如果只是用户问“打包命令是什么”“先看一下打包”，打包脚本加 `--dry-run`。
- 不要跳过前端 `pnpm build`，除非用户明确说明只打后端或临时跳过前端。
- 部署插件包时默认必须先备份并清空 `/data/smart/app/plugins`，防止旧版本包留在目录里；只有用户明确要求保留旧插件时才加 `--no-clear-plugins`。
- 如果部署失败，不要连续盲目重启；先读取 `systemctl status smart-server` 和 `/data/smart/app/logs` 最新日志。
- 如果包分类看起来异常，例如所有包都被识别为插件包但用户期望包含基座包，先用 dry run 输出清单并调整 `--base-regex` 或 `--plugin-regex`。

## 常用排查

打包 activity 的 develop 包：

```bash
cd <smart-cicd-skill-dir>
python3 scripts/package-smart-project.py activity --branch develop
```

打包 activity 的 release 包：

```bash
cd <smart-cicd-skill-dir>
python3 scripts/package-smart-project.py activity --branch release
```

查看 188 的部署预览：

```bash
cd <smart-cicd-skill-dir>
python3 scripts/deploy-smart-package.py 188
```

部署 124 的 master 包：

```bash
cd <smart-cicd-skill-dir>
python3 scripts/deploy-smart-package.py 124 --execute
```

部署 201 的 develop 包：

```bash
cd <smart-cicd-skill-dir>
python3 scripts/deploy-smart-package.py 201 --execute
```
