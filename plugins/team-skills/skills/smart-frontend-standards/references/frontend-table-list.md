# 前端列表与 CRUD 页面

## 适用场景

在新增或修改列表页、CRUD 页面、表格查询、表单弹窗或后台管理页时，读取本文件。

## 强制规则

- 列表或 CRUD 页面默认优先使用 `VAObkTable`。
- 若目标项目直接使用底层 `VaTable`，按同一套标准 CRUD 容器处理；`VAObkTable` 是业务封装口径，`VaTable` 是底层能力口径，不为两者之外再造第三套表格模型。
- 列定义、搜索项和表单列优先沿用 `ProColumns`、`ProFormColumnsType` 等现有组合方式。
- 数据增删改查优先复用现有 `useCurd`、控制器接口和服务封装。
- 让列表、搜索、表单与请求关系保持统一风格，避免每页造一套交互模型。
- `columns` 负责列表列与搜索项，`formColumns` 负责弹窗表单；字段转换优先集中到 `formatData`、service 的 `formatDetail` / `formatList` 或同类统一函数中，不散落在按钮回调里。
- 需要批量删除时，必须确认底层 `rowSelection.type === "checkbox"`；只打开批量删除按钮而没有复选选择模型，属于无效配置。
- 遇到 `VAObkTable` 默认“查看 / 编辑 / 删除”操作列相关问题时，先沿真实源码链路确认生效参数，再决定改动；不要把其他表格实现的参数名直接套用到 `VAObkTable`。

## 推荐模式

- 以相似后台页面为蓝本，沿用 `columns`、`formColumns`、`request`、`create`、`update`、`detail`、`remove` 这类组合方式。
- 用 `useRef` 挂表格实例时，遵循邻近模块已有写法。
- 搜索、表单校验和枚举选择优先复用服务端下拉接口或既有组件能力。
- 排查 `VAObkTable` 默认操作列时，先看 `@va/ui/src/table/index.tsx`，确认它把参数透传给的是哪一套 `VaTable` 实现；本仓库当前实际链路是 `ObkTable -> @vlian/villianjs/dist/PopupTable.VaTable`，不是 `Curd` 那套实现。
- 使用 `VAObkTable` 时默认由封装层接管顶部搜索区：底层 `VaTable` 的原生搜索通常被关闭，查询参数按“初始 `params` + 搜索表单值 + 分页参数”进入 `request`。
- `VAObkTable` 点击查询或重置后内部会触发表格刷新；页面侧不要再对同一条件重复 `reload`，避免一次操作发两次请求。
- 查看态详情加载不要只依赖 `type === "view"` 分支；底层实现可能复用编辑态详情入口，`detail` 应兼容查看和编辑共用的详情拉取。
- `removeConfirmProps`、`beforeCreate`、`fixedSearch` 等参数要先确认属于封装层还是底层 `VaTable`。例如 `fixedSearch` 应传可用容器或返回容器的函数，不要把布尔值 `true` 当成固定搜索容器。
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
- 在 `columns`、`formColumns`、`request`、`create/update/detail/remove` 之外另起一套状态同步和字段转换流程，导致同页表格、弹窗、服务层语义不一致。
- 只打开 `showBatchDeleteBtn` 或自定义批删按钮，却没有配置复选选择模型或成功后刷新策略。
- 在没有确认 `VAObkTable` 真实透传实现前，凭参数名猜测关闭默认操作列的方式。
- 把“整列隐藏”和“隐藏列内某几个按钮”混为一谈，导致同时堆叠 `operateRender={false}` 与多组 `show*Btn={false}` 冗余配置。
- 把 `showRemoveBtn` 和其他实现里的 `showDeleteBtn` 当成同一个参数名使用。

## 开发或评审检查点

- 页面是否应使用 `VAObkTable`。
- 列、搜索、表单、请求与已有页面是否保持一致。
- 是否复用了 `useCurd` 与现有控制器接口。
- 是否避免了额外引入不必要的表格抽象。
- `columns`、`formColumns`、字段转换、详情加载和批量删除是否符合 `VAObkTable` / `VaTable` 的职责边界。
- 若存在批量删除，是否已经启用 `rowSelection.type === "checkbox"`，并确认成功后会刷新列表。
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
