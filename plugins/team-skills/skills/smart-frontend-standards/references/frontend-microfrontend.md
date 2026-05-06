# 前端微前端接入

## 适用场景

在处理 qiankun 接入、微应用容器、Vite 构建、宿主嵌入或前端资源入口时，读取本文件。

## 强制规则

- 保持现有 React + Vite + qiankun 接入方式，不无故切换微前端实现。
- 先确认前端构建产物位置，再确认后端或宿主如何消费这些产物。
- 调整路由、资源基路径、微应用容器时，同时检查布局容器与构建配置。
- 插件前端调用插件后端接口时，优先沿用统一路径约定：接口前缀使用 `/api/<插件ID>/...`，不要直接写裸路径如 `/config/...` 或自行猜测宿主转发规则。
- 前端请求层优先沿用现有插件通用封装，例如 `@va/services` 的 `request`，并跟随邻近插件现有的 `data / error` 处理方式，不为单个页面重新手写一套 `axios + CommonResult` 解析。

## 推荐模式

- 先读 `vite.config.ts` 与布局中的微应用容器实现，再决定改动范围。
- 以现有布局中的 `microApp-container`、菜单布局和判断逻辑为准，补充而不是重写。
- 在交付说明中明确前端产物如何进入插件包或宿主环境。
- 先从 `backend/build.gradle` 或同类打包配置确认插件 ID，再用该 ID 组织前端 API 前缀，例如 `/api/door/...`、`/api/notice/...`。
- 先查看兄弟插件的 `services.ts` / `api.ts`，复用它们的请求封装、URL 常量命名和错误处理模式，再决定当前插件的请求层写法。

## 禁止做法

- 不看现有接入方式就直接替换 qiankun 或构建链路。
- 修改前端入口或路由基路径时不联动检查后端资源复制或宿主挂载方式。
- 在插件前端里直接请求不带插件 ID 的后端裸路径，导致宿主代理、网关或插件路由前缀不一致。
- 只根据当前后端 Controller 上的局部 `@RequestMapping` 拼接前端 URL，而忽略实际宿主暴露给插件页面的 `/api/<插件ID>/...` 访问形式。

## 开发或评审检查点

- qiankun / 微前端接入方式是否保持一致。
- 路由、容器、基路径与构建产物链路是否联动检查。
- 是否在说明里讲清了前端产物如何被宿主消费。
- 插件前端请求路径是否包含正确的插件 ID 前缀，且与 `backend/build.gradle` 中的插件 ID 一致。
- 是否复用了现有请求封装与兄弟插件一致的响应处理模式，而不是临时发明另一套前端请求层。

## 仓库参考位置

- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/src/layouts/BasicLayout.tsx`
- `backend/build.gradle`
- `frontend/src/pages/door/api.ts`
- `../smart-notice-mixed/frontend/src/pages/notice/services.ts`
