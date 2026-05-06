# 后端 Extract 扩展机制

## 适用场景

当任务涉及宿主定义扩展点、插件通过 `@Extract` 挂接能力、宿主按接口或 `bus/scene` 收集插件实现，或需要在 Extract、宿主 MAIN Bean、跨插件 `@Caller` / `@Supplier` 之间做方案判断时，读取本文件。

## 强制规则

- `Extract` 只用于“宿主定义总线，插件贡献实现，宿主统一发现和调度”的扩展模型，不作为任意 Service 调用或跨插件调用的替代品。
- 新增 Extract 前先定义稳定接口，接口参数和返回值使用 DTO、VO 或通用模型，不暴露插件内部 Entity。
- 插件实现必须标注 `@Extract(bus = "...")`；需要按场景精确定位时，同时提供稳定的 `scene`。
- 宿主按接口聚合多个实现时，使用 `ExtractFactory` 的接口收集能力；按 `bus + scene` 精确定位时，先构造 `ExtractCoordinate`，再交给 `ExtractFactory` 获取。
- `bus`、`scene` 是跨模块协议，不在多个插件中复用同名但语义不同的值；需要带插件维度时，优先参考 `NodeFactory` 的 `pluginId_scene` 拆分模式。
- Extract 实现里调用宿主基座 Bean 时，仍按 `@Autowired` + `@AutowiredType(AutowiredType.Type.MAIN)` 处理；调用本插件 Bean 时，才按插件上下文普通 Spring 注入处理。

## 推荐模式

- 多插件共同贡献结果的能力，优先按接口批量收集，再由宿主 Service 做排序、过滤、去重和异常隔离。
- 需要按类型或场景路由到单个实现的能力，优先使用清晰的 `bus + scene` 协议，不在业务代码里散落字符串拼接。
- 已存在通用 Controller 或 Factory 能承接的能力，优先复用宿主统一入口，不为每个插件新增含义相同的接口。
- 常见 Extract 形态包括菜单贡献、字典贡献、节点树、任务处理器、WebSocket Handler、消息模板与消息跳转解析。
- 批量聚合场景要记录单个插件 Extract 异常，并按业务容忍度决定跳过、降级或失败，不要无日志吞掉。

## 禁止做法

- 把 Extract 当成绕过 `@Caller` / `@Supplier` 或 MAIN Bean 注入规则的通用工具。
- 只在文档里约定 `bus/scene`，实现类没有标注 `@Extract`。
- 在 Controller 中直接遍历插件实现并拼业务逻辑；扩展调度应放在 Service、Factory 或 Manager。
- Extract 接口返回可变内部实体，让宿主或其他插件依赖实现细节。
- 在 Extract 中吞掉异常且不记录上下文，导致插件扩展不可观测。

## 开发或评审检查点

- 当前需求是否真属于宿主调度插件扩展，而不是普通本插件 Service 调用或跨插件 Supplier 调用。
- 接口是否稳定，参数与返回值是否避免暴露内部 Entity。
- `@Extract` 的 `bus`、`scene` 是否清晰、稳定、可复用。
- 宿主侧是批量收集还是精确定位，是否选择了正确的 `ExtractFactory` 获取方式。
- Extract 内部的宿主 Bean 注入是否仍遵守 MAIN Bean 规则。
- 聚合结果是否明确了权限过滤、排序、去重和异常处理策略。

## 仓库参考位置

- `smart-core-mixed/backend/src/main/java/com/outbook/smart/service/impl/MenuServiceImpl.java`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/service/impl/DictionaryService.java`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/component/node/NodeFactory.java`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/controller/NodeController.java`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/extract/node/RoomNodeService.java`
- `smart-door-mixed/backend/src/main/java/com/outbook/smart/door/extract/node/DoorLockNodeService.java`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/flex/service/impl/TaskServiceImpl.java`
