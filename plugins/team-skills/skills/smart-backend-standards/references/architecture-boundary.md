# 架构边界

## 适用场景

在 smart（空间管理）项目的 smart-core 基座 + smart-* 插件体系中处理后端、前端、插件接入、资源注册、构建链路或代码审查任务时，先读取本文件。

## 强制规则

- 先把项目识别为“宿主基座 + 插件”体系，不把插件误当成可独立运行的普通应用。
- 先判断能力应落在插件侧还是宿主侧，优先复用宿主 `smart-core` 已有能力、配置和 Spring Bean。
- 先判断数据归属插件；表、迁移文件、表结构变更权限默认跟随所属插件，不因为当前插件里也存在同名或近似模型，就把它当成本插件可维护的数据表。
- `TimeManager` 是 `smart-core` 基座统一时间能力的入口；后端业务代码中凡是获取当前时间、当前日期、当前时区、时区偏移或基于“当前时刻”的业务判断，统一使用 `backend/src/main/java/com/outbook/smart/component/TimeManager.java` 提供的方法或字段，不直接在业务代码里写 `LocalDateTime.now()`、`Instant.now()`、`System.currentTimeMillis()`、`ZoneId.systemDefault()` 这类调用。
- `EventBusManager` 与 Quartz 调度是 `smart-core` 基座统一基础设施；插件涉及发布订阅、异步领域事件、延迟事件、周期任务或补发触发器时，优先复用宿主 `backend/src/main/java/com/outbook/smart/component/EventBusManager.java`、`backend/src/main/java/com/outbook/smart/component/quartz/SchedulerManager.java` 与 `backend/src/main/java/com/outbook/smart/listener/QuartzListener.java`，不要在插件内再平行创建第二套事件总线或调度器。
- 插件监听基座或其他模块事件时，优先把监听器声明为带 `@Service` 的 Spring Bean，并通过 `@Subscribe` 接入基座 `EventBusManager` 的自动注册机制；插件发布事件时，统一使用 `EventBusManager.postSync(...)`、`postAsync(...)` 或 `postDelayed(...)`。
- 插件新增周期任务时，优先通过 `@Bean` 暴露 `JobDetail` 与 `Trigger`，交给基座 `QuartzListener` 在插件启停时统一注册和清理；只有在“基于已有 Job 动态补发一次触发器”这类场景下，才通过 `SchedulerManager` 操作主调度器。
- 插件代码不要默认把宿主 `smart-core` 中的 Service、Manager、组件 Bean 当成本插件上下文内可直接构造器注入的本地 Bean；先确认该能力在插件态的真实注入方式。
- 需要注入宿主基座 Bean 时，优先沿用兄弟插件现有模式：通过 `@Autowired` 配合 `@AutowiredType(AutowiredType.Type.MAIN)` 注入主程序 Bean，而不是直接在插件内声明普通构造器注入。
- 校区、学院、部门这类属于宿主组织体系的关联实体，新增或更新组织基础信息时必须优先走宿主 `OrganizationService`（例如校区先创建 `ob_organization`，再由组织 id 同步生成 `ob_campus`），不要在插件侧直接把它们当普通主数据表独立创建；确需补充组织服务不维护的扩展字段时，再通过对应宿主 MAIN Bean 做最小字段更新。
- 若能力来自其他插件而不是宿主基座，优先使用 `@Caller` / `@Supplier` 这类跨插件调用模式，不要把“宿主 Bean 注入”和“跨插件能力调用”混成同一套做法。
- 使用 `@Caller` 调用其他插件 `@Supplier` 时，默认把“所有方法实参都必须非 null”当成硬约束处理；不要把 `null` 直接传入跨插件调用代理。若业务语义允许“缺省/匿名/空目标”，必须先在调用侧归一化成双方约定好的非空兜底值、空集合、空 DTO 或明确哨兵值，再发起调用。
- 若数据来自其他插件，当前插件只能通过跨插件能力或既有只读查询方式消费；除所属插件外，其他插件禁止直接写入对方表、禁止新增迁移文件修改对方表结构。
- 先确认真实入口类、真实资源目录、真实构建链路，再决定改动点。
- 先以实际仓库代码为准，再参考仓库说明文档；若说明与代码不一致，在交付中明确指出差异。
- 涉及插件入口、资源注册、自动配置放行、静态资源或前端产物接入时，同时检查启动生命周期和插件装载约束。
- 涉及内网仓库地址、上传地址、示例凭据时，按敏感信息处理，不在新增文档、代码注释或交付说明中扩散。

## 推荐模式

- 先读仓库约束文档与入口实现，再按任务加载其他 reference。
- 优先跟随邻近模块与现有公共封装，而不是为单个需求重造基础设施。
- 需要复用其他插件的数据时，优先寻找该插件已有的 `@Supplier`、公共查询接口、同步快照或只读视图模式，而不是跨插件直连对方表做写操作。
- 复用宿主配置、缓存、时间管理、WebSocket 等基座能力前，先在兄弟插件中搜索该 Bean 的真实接入方式；若兄弟插件已统一使用 `@AutowiredType(AutowiredType.Type.MAIN)`，默认沿用该模式。
- 写入校区、学院、部门等组织关联数据前，先查宿主组织服务是否会自动维护同 id 关联表；若会自动维护，插件侧只负责编排组织服务调用和补齐自身需要的非组织字段。
- `TimeManager` 按“基座统一时间能力”理解和复用，不把它当成当前插件可随意替换的普通工具类；插件内若需要时间相关扩展，优先补充 `TimeManager` 的统一能力或继续复用其现有接口。
- 需要“当前时间”时，按返回值类型选择 `TimeManager.currentLocalDateTime()`、`TimeManager.currentLocalDate()`、`TimeManager.currentZonedDateTime()`、`TimeManager.currentTimeMillis()` 或 `TimeManager.currentTimeSeconds()`。
- 需要“当前时区”时，优先使用 `TimeManager.getZoneId()`、`TimeManager.getZoneOffset()`，避免绕开统一初始化逻辑。
- 需要做模块内异步解耦、跨流程通知、延迟去抖或事件驱动补偿时，先评估是否能直接复用 `EventBusManager`；监听器优先写成带 `@Service` 与 `@Subscribe` 的 Bean，而不是自己维护监听器注册表、回调列表或额外的 Guava EventBus 封装。
- 需要新增 Quartz 能力时，先区分“固定周期任务”和“基于现有 Job 的临时触发”两类场景：固定周期任务走 `JobDetail`/`Trigger` Bean，临时触发走 `SchedulerManager` 操作主调度器；两者都默认复用基座已有 Scheduler 与插件生命周期清理逻辑。
- 当基座能力既可能以共享 Bean 方式提供，也可能以跨插件服务方式提供时，先判断“是否属于主程序 Bean”还是“是否属于其他插件 Supplier”；主程序 Bean 走 `@AutowiredType(AutowiredType.Type.MAIN)`，跨插件调用走 `@Caller`。
- 设计 `@Caller` / `@Supplier` 协议时，优先约定稳定的非空入参语义：集合用空集合表示“无目标”，对象参数用字段可空但对象本身非空的 DTO，标识类参数若允许匿名或系统态调用，显式约定 `0`、`-1` 或其他业务可识别的哨兵值，并在调用入口统一归一化。
- 在交付中区分“已在本仓库验证部分”和“依赖宿主联调部分”。

## 禁止做法

- 把插件直接当成独立 Spring Boot 应用，并假设可以通过 `bootRun` 完成联调。
- 在插件里重复实现宿主已经管理的定时、鉴权、基础查询或通用基础设施。
- 为了发布订阅、异步事件或延迟事件，在插件里再 `new EventBus()`、`new AsyncEventBus()`、封装另一套 `EventBusManager`，或自己维护一套监听器注册/注销机制。
- 在插件里再启一套并行调度体系，例如自行创建 `SchedulerFactoryBean`、`StdSchedulerFactory`、额外 Quartz 实例，或通过 `@EnableScheduling`、`@Scheduled`、`SchedulingConfigurer` 把定时任务绕开基座 Quartz。
- 把其他插件拥有的数据表当成本插件的可写表处理，或因为当前插件也声明了课程、学生、设备等模型，就直接向来源插件的表执行插入、更新、删除。
- 在后端业务代码里直接使用 `LocalDateTime.now()`、`LocalDate.now()`、`Instant.now()`、`System.currentTimeMillis()`、`ZoneId.systemDefault()` 等标准库调用获取“项目当前时间/时区”，绕开 `TimeManager`。
- 把 `TimeManager` 当成当前插件私有工具类对待，并在插件内再复制一套时间管理、时区管理或时间偏移逻辑。
- 为了让 Quartz 任务运行，在插件里再写一套任务初始化、插件卸载清理或调度注册表，和基座 `QuartzListener` 并行维护生命周期。
- 直接在插件 Service 的构造器里注入宿主基座 Bean，并假设插件上下文会自动解析主程序 Bean。
- 看到某个类型在编译期可见，就默认它在插件运行时也能按普通 `@Autowired` 成功注入。
- 绕过 `OrganizationService` 直接新增校区、学院、部门等组织关联实体，导致组织树和关联业务表 id 不一致或名称不同步。
- 把宿主基座 Bean 注入问题误判成跨插件调用问题，或反过来把其他插件提供的能力误用为 `@AutowiredType(AutowiredType.Type.MAIN)` 注入。
- 把 `null` 当成 `@Caller` 的可选参数语义直接透传给其他插件，指望代理层或 `@Supplier` 入口再兜底处理。
- 在非所属插件中创建迁移文件、变更 DDL、补字段、改索引，直接修改其他插件拥有的表结构。
- 修改入口、资源、打包链路时只改一个文件，不联动检查相关配置。
- 把文档中的历史路径或历史类名直接当成当前事实。

## 开发或评审检查点

- 入口类、资源注册、前端产物接入路径是否以真实代码为准。
- 需求是否越过了宿主与插件的职责边界。
- 涉及数据库表时，是否先确认了表的所属插件，以及当前改动是否越权写入或越权改表。
- 是否复用了现有宿主能力与公共封装。
- 若复用了宿主 Bean，注入方式是否明确区分了“插件本地 Bean”“宿主 MAIN Bean”“其他插件 Supplier”三种来源。
- 宿主 Bean 的接入是否参考了兄弟插件现有写法，例如 `@Autowired + @AutowiredType(AutowiredType.Type.MAIN)`。
- 写入校区、学院、部门等组织关联实体时，是否通过 `OrganizationService` 保持组织表和关联实体表同 id 同步，并只对组织服务未维护的扩展字段做最小补写。
- 若引入了事件驱动或异步通知，是否直接复用了基座 `EventBusManager`，并采用 `@Service` + `@Subscribe` 的监听方式，而不是新建一套事件总线。
- 若引入了定时或延迟执行能力，是否区分了 `EventBusManager.postDelayed(...)`、基座 Quartz 周期任务、基于 `SchedulerManager` 的临时触发三种场景，并选用了宿主已有能力。
- 若存在 `@Caller` 调用，是否已经在调用侧消除了 `null` 实参，并与 `@Supplier` 约定的非空协议保持一致。
- 后端代码获取当前时间、日期、时间戳或时区时，是否统一走 `TimeManager`，而不是混用 JDK 原生时间入口。
- 是否把无法在当前仓库独立验证的部分说清楚。
- 是否避免在输出里扩散敏感配置。

## 仓库参考位置

- `AGENTS.md`
- `backend/src/main/java/com/outbook/smart/component/TimeManager.java`
- `backend/src/main/java/com/outbook/smart/component/EventBusManager.java`
- `backend/src/main/java/com/outbook/smart/component/quartz/SchedulerManager.java`
- `backend/src/main/java/com/outbook/smart/config/TimeManagerConfig.java`
- `backend/src/main/java/com/outbook/smart/Application.java`
- `backend/src/main/java/com/outbook/smart/listener/QuartzListener.java`
- `backend/build.gradle`
- `../smart-attendance-mixed/backend/src/main/java/com/outbook/smart/attendance/listener/AttendanceScheduleDeleteListener.java`
- `../smart-door-mixed/backend/src/main/java/com/outbook/smart/door/config/JobConfig.java`
- `../smart-face-mixed/backend/src/main/java/com/outbook/smart/face/service/impl/FaceUploadRecordServiceImpl.java`
- `../smart-attendance-mixed/backend/src/main/java/com/outbook/smart/attendance/service/impl/StudentAttendanceConfigServiceImpl.java`
- `../smart-classPanel-mixed/backend/src/main/java/com/outbook/smart/classPanel/service/impl/SettingServiceImpl.java`
- `../smart-classPanel-mixed/backend/src/main/java/com/outbook/smart/classPanel/caller/FaceConfigService.java`
- `../smart-door-mixed/backend/src/main/java/com/outbook/smart/door/service/impl/DoorRemoteServiceImpl.java`
- `../smart-core-mixed/backend/src/main/java/com/outbook/smart/flex/service/OrganizationService.java`
- `../smart-core-mixed/backend/src/main/java/com/outbook/smart/flex/service/impl/OrganizationServiceImpl.java`

## 备注

当前样例仓库的真实入口类是 `Application`，而项目说明中提到的可能是 `PluginApplication`。遇到这类差异时，以实际工程代码为准，并把差异写进交付说明。
