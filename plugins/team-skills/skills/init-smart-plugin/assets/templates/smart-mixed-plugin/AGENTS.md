# Repository Guidelines

## 项目定位

本项目是 smart-core 的 mixed 插件工程，包含 `backend/` 和 `frontend/`。后端依赖宿主加载，不按独立 Spring Boot 应用处理；前端使用 React 19、TypeScript、Vite，并通过 qiankun 接入宿主。

## 结构

- `backend/`：插件后端工程，入口类为 `PluginApplication`。
- `backend/src/main/resources/resources.json`：插件资源与权限声明。
- `frontend/`：插件前端工程，构建产物输出到 `frontend/dist`。
- `backend/build.gradle`：打包时把 `../frontend/dist` 复制到插件包内的 `web/`。

## 工作方式

- 新增后端能力时优先复用宿主 `smart-core` 的 Bean 和扩展点。
- 新增前端页面时同步检查路由 basename、qiankun app name 和 `public/config.json`。
- 改动打包链路时同步检查前端输出目录和后端资源复制配置。
- 涉及宿主能力的功能，需要在真实 smart-core 基座中加载验证。

## 常用命令

后端命令默认在 `backend/` 目录执行：

```bash
./gradlew test
./gradlew build
```

前端命令默认在 `frontend/` 目录执行：

```bash
pnpm install
pnpm build
pnpm dev
```
