# 前端列表与 CRUD 页面

## 适用场景

在新增或修改列表页、CRUD 页面、表格查询、表单弹窗或后台管理页时，读取本文件。

## 强制规则

- 列表或 CRUD 页面默认优先使用 `VAObkTable`。
- 列定义、搜索项和表单列优先沿用 `ProColumns`、`ProFormColumnsType` 等现有组合方式。
- 数据增删改查优先复用现有 `useCurd`、控制器接口和服务封装。
- 让列表、搜索、表单与请求关系保持统一风格，避免每页造一套交互模型。
- 遇到 `VAObkTable` 默认“查看 / 编辑 / 删除”操作列相关问题时，先沿真实源码链路确认生效参数，再决定改动；不要把其他表格实现的参数名直接套用到 `VAObkTable`。

## 推荐模式

- 以相似后台页面为蓝本，沿用 `columns`、`formColumns`、`request`、`create`、`update`、`detail`、`remove` 这类组合方式。
- 用 `useRef` 挂表格实例时，遵循邻近模块已有写法。
- 搜索、表单校验和枚举选择优先复用服务端下拉接口或既有组件能力。
- 排查 `VAObkTable` 默认操作列时，先看 `@va/ui/src/table/index.tsx`，确认它把参数透传给的是哪一套 `VaTable` 实现；本仓库当前实际链路是 `ObkTable -> @vlian/villianjs/dist/PopupTable.VaTable`，不是 `Curd` 那套实现。
- 需要整列隐藏默认操作列时，优先使用 `operateRender={false}`。这会直接不生成默认“操作”列，适合页面自己在 `columns` 里定义自有操作列的场景。
- 需要保留默认“操作”列，但只隐藏部分默认按钮时，再使用 `showViewBtn={false}`、`showUpdateBtn={false}`、`showRemoveBtn={false}` 这类细粒度参数。
- `showViewBtn` 只控制默认“查看”按钮是否出现；`showUpdateBtn` 只控制默认“编辑”按钮；`showRemoveBtn` 只控制默认“删除”按钮。它们都不负责隐藏整列。
- `operateRender` 用于控制整列默认操作渲染。传 `false` 时整列消失；传函数时是在保留默认操作列的前提下重写该列内容。
- 当 `operateRender={false}` 已经满足需求时，不要再重复叠加 `showViewBtn/showUpdateBtn/showRemoveBtn={false}` 作为常驻代码；这些参数在这种场景下只是冗余噪音。
- `showBatchDeleteBtn` 控制的是工具栏里的批量删除按钮，不是行内默认操作列；它和 `operateRender/showViewBtn/showUpdateBtn/showRemoveBtn` 不是同一层能力。
- 若文档、经验或其他页面里出现 `operate={false}`、`showDeleteBtn={false}` 这类写法，先确认它们属于哪套表格实现；对本仓库当前 `VAObkTable` 这条链路，不要默认把它们当作关闭默认操作列的权威参数。

## 禁止做法

- 已属于标准列表 / CRUD 页面却绕开 `VAObkTable` 自建一套表格容器。
- 为单页需求引入与现有管理页并行的新表格方案。
- 把查询、表单和请求流做成与既有页面完全不同的模式。
- 在没有确认 `VAObkTable` 真实透传实现前，凭参数名猜测关闭默认操作列的方式。
- 把“整列隐藏”和“隐藏列内某几个按钮”混为一谈，导致同时堆叠 `operateRender={false}` 与多组 `show*Btn={false}` 冗余配置。
- 把 `showRemoveBtn` 和其他实现里的 `showDeleteBtn` 当成同一个参数名使用。

## 开发或评审检查点

- 页面是否应使用 `VAObkTable`。
- 列、搜索、表单、请求与已有页面是否保持一致。
- 是否复用了 `useCurd` 与现有控制器接口。
- 是否避免了额外引入不必要的表格抽象。
- 若页面需要关闭默认操作列，是否已经确认真实源码链路与当前生效参数。
- 是否区分了 `operateRender={false}` 的“整列关闭”与 `showViewBtn/showUpdateBtn/showRemoveBtn` 的“按钮级关闭”。
- 若页面已有自定义操作列，是否只保留必要参数，避免为了排查遗留重复配置。

## 仓库参考位置

- `frontend/src/pages/face/components/classPanel/index.tsx`
- `frontend/src/types/auto-imports.d.ts`
- `frontend/node_modules/@va/ui/src/table/index.tsx`
- `frontend/node_modules/@vlian/villianjs/dist/PopupTable/typings.d.ts`
- `frontend/node_modules/@vlian/villianjs/dist/PopupTable/table.js`
- `frontend/src/pages/door-password/index.tsx`
