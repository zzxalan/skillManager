# 节点树、NodeService 与 Extract 扩展

## 适用场景

当任务涉及以下内容时，读取本文件：

- 插件新增或改造节点树能力。
- 基于 `@Extract(bus = "NodeService", scene = "...")` 提供节点服务。
- 复用宿主通用节点接口 `/node/init`、`/node/search`、`/node/children`。
- 需要把校区、楼栋、房间、设备等层级结构接入树选择器。
- 需要按权限过滤节点树，或把已有 Node 树兼容转换为业务接口返回结构。

## 强制规则

- 节点树是 `Extract` 的专项场景；通用扩展点设计、`bus/scene` 命名和宿主获取方式先遵守 `backend-extract-extension.md`，本文件只补充 `NodeService` 相关约束。
- 节点树能力优先走宿主 `NodeService` 总线，不要先在 Controller 或普通业务 Service 中手拼一套独立树结构。
- 插件提供节点服务时，必须通过 `@Extract(bus = "NodeService", scene = "...")` 注册 scene；不要只约定字符串或只在文档里声明。
- 若插件代码要调用宿主里的 `NodeFactory`、`DataPermissionService`、`RoomService` 等主程序 Bean，必须按宿主注入方式接入，不要在插件里重复造一套实现。
- 节点查询、懒加载、搜索要当作同一组能力设计；改 `initTree` 时，同时检查 `getChildren`、`searchNode(String)`、`searchNode(List<Node>)` 是否仍然一致。
- 节点树做权限裁剪时，除了过滤叶子节点，还要递归移除无子节点的中间容器节点，不能把空校区、空楼栋、空房间继续返回给前端。
- 如果前端已经能直接接宿主通用节点接口，优先复用 `NodeController`，不要再额外定义一套含义相同的树接口。
- 如果历史页面暂时还依赖自定义树结构，自定义接口只能作为兼容层存在，底层仍应以 NodeService 产出的 `Node` 树为准。

## 推荐模式

- 需要房间树、教室树、教室下挂设备时，优先从宿主现有节点服务继承或复用，例如 `RoomNodeService`、`ClassPanelNodeService`，只覆盖当前插件真正不同的筛选和挂载逻辑。
- 设备类节点推荐在房间节点下追加叶子节点，节点 `dataType` 保持宿主已有枚举语义；如果前端历史接口需要业务化类型名，只在 Controller 兼容转换层映射。
- 插件内如果要主动调用节点服务，优先通过 `NodeFactory.getNodeServiceByCoordinate("pluginId_scene")` 获取，而不是直接 new 或绕开总线调用实现类。
- 权限过滤推荐先拿到可访问的房间或资源 ID 集合，再查询并挂载叶子设备，最后统一裁剪空容器节点。
- 兼容旧前端时，Controller 只负责把 `Node` 转为页面所需结构；节点构造、权限过滤、搜索逻辑仍放在节点服务中维护。

## 禁止做法

- 禁止在已经存在明确节点树语义的场景里，绕开 `NodeService` 总线直接在 Controller 手写树。
- 禁止为只读查询模型额外补一套没有必要的 Mapper/Service，只是为了给节点树查设备。
- 禁止只过滤叶子设备，不清理被过滤后为空的上级节点。
- 禁止把业务 VO 结构当作节点树的唯一事实来源，再倒推搜索、懒加载和权限逻辑。
- 禁止插件和宿主混用错误的 Bean 注入方式，导致实际运行时拿不到主程序能力。

## 开发或评审检查点

- `@Extract` 的 `bus` 和 `scene` 是否准确，命名是否稳定可复用。
- 节点服务是否优先复用了宿主已有的房间树或设备树实现，而不是重复造轮子。
- `initTree`、`getChildren`、`searchNode` 是否保持同一套权限和过滤语义。
- 权限过滤后是否已经移除所有空容器节点。
- 自定义 Controller 是否只是兼容层，而不是重新承担节点树拼装职责。
- 设备节点的数据类型和业务类型转换是否只发生在边界层。

## 仓库参考位置

- 宿主通用节点接口：`smart-core-mixed/backend/src/main/java/com/outbook/smart/controller/NodeController.java`
- 宿主节点服务工厂：`smart-core-mixed/backend/src/main/java/com/outbook/smart/component/node/NodeFactory.java`
- 宿主房间节点服务：`smart-core-mixed/backend/src/main/java/com/outbook/smart/extract/node/RoomNodeService.java`
- 宿主教室屏节点服务：`smart-core-mixed/backend/src/main/java/com/outbook/smart/extract/node/ClassPanelNodeService.java`
- pubInfo 按权限挂设备示例：`smart-pubInfo-mixed/backend/src/main/java/com/outbook/smart/pubInfo/extract/node/PubScreenClassPanelNodeService.java`
- 门锁节点服务示例：`smart-door-mixed/backend/src/main/java/com/outbook/smart/door/extract/node/DoorLockNodeService.java`
- 门锁页直接调用通用节点接口示例：`smart-door-mixed/frontend/src/pages/door/api.ts`
- 门锁页消费嵌套节点树示例：`smart-door-mixed/frontend/src/pages/door-settings/index.tsx`
