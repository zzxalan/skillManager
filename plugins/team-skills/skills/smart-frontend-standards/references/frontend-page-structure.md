# 前端页面结构

## 适用场景

在新增或修改页面、布局、页面级组件、共享组件、路由接入与页面目录结构时，读取本文件。

## 强制规则

- 延续现有 React 19 + TypeScript + Vite + Ant Design + Pro Components + UnoCSS + qiankun 技术栈。
- 页面优先放在 `frontend/src/pages` 对应域目录下，共享组件优先放在 `frontend/src/components` 或页面局部 `components` 下。
- 优先保持邻近页面的 import 顺序、命名、缩进和组织方式，不做与任务无关的大面积格式化。
- 需要布局能力时优先沿用现有布局、Breadcrumb、PageContainer 与路由接入方式。
- 页面级数据请求由 `useEffect` 触发时，依赖数组只放真正影响请求参数的响应式值，例如路由参数、分页、筛选条件；不要把仅用于执行请求的事件函数误放进依赖数组。
- 在 React 19 中，若用 `useEffectEvent` 封装请求函数，默认把它当作“effect 内可调用的非响应式事件函数”，不要再把它加入 `useEffect` 依赖；若确实需要稳定函数参与依赖比较，再明确改用 `useCallback`。

## 推荐模式

- 先查看相邻业务页面，复用它们的页面壳、布局容器、数据加载方式与拆分粒度。
- 只在确实跨页面复用时抽到共享组件，否则放到局部 `components`。
- 结合现有 `layouts`、`hooks`、`router` 与 `services` 组织页面行为。
- 页面初始化请求优先采用“`useEffect` 负责依赖收敛，`useEffectEvent` 负责执行请求”的模式，先列清楚哪些值会改变请求参数，再决定 effect 依赖。
- 对“详情请求 + 记录列表请求 + 衍生状态刷新”并存的页面，优先把路由参数、分页、筛选条件这类真正驱动请求的响应式值收敛到 `useEffect`，把执行请求的逻辑留在 `useEffectEvent`；若因此需要忽略 `react-hooks/exhaustive-deps`，在 effect 附近补一行中文注释说明原因。
- 排查重复请求时先检查 `useEffect` 依赖是否包含会在每次 render 变化的函数引用，再区分是否只是开发环境 `StrictMode` 的双调用现象。
- 若页面出现“某个详情接口或事件接口持续反复请求”，先排查 `useEffect` 是否误依赖了 `useEffectEvent` 返回函数，再判断是否真是后端字段、分页结构或表结构改动导致的参数变化；不要因为最近改过事件表，就先把根因归到后端。

## 禁止做法

- 脱离现有栈，临时引入另一套页面框架或布局系统。
- 仅凭个人偏好重构整个目录。
- 把页面逻辑、布局逻辑与共享组件逻辑混在一个超大文件里。
- 把 `useEffectEvent` 返回的函数直接放进 `useEffect` 依赖数组，导致“请求 -> setState -> render -> effect 再次触发”的循环请求。
- 为了消除 hooks lint 提示，把详情页或列表页里多个 `useEffectEvent` 请求函数一股脑加入依赖数组，结果把原本一次性的详情请求放大成持续重复请求。
- 还没确认触发链路前，就为了压住循环把请求函数整体改成 `useCallback` 或随意删依赖，结果把首次请求或后续筛选刷新一起改没。

## 开发或评审检查点

- 页面落点是否合理，是否沿用了现有目录和布局模式。
- 是否复用了现有 hooks、services、layout 与组件。
- 是否做了不必要的大面积重排或风格切换。
- 页面初始化、分页、筛选触发的请求是否只由必要依赖驱动。
- 若使用了 `useEffectEvent`，是否避免把返回函数加入 `useEffect` 依赖数组。
- 若 effect 为了保持正确依赖而忽略了 `react-hooks/exhaustive-deps`，是否已经用中文注释写清楚“为什么这里不把 `useEffectEvent` 放进依赖”。

## 仓库参考位置

- `frontend/src/pages`
- `frontend/src/components`
- `frontend/src/layouts/BasicLayout.tsx`
- `frontend/package.json`
- `frontend/src/pages/door-room-detail/index.tsx`
