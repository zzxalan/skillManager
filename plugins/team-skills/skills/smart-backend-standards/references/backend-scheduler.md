# 后端定时任务

## 适用场景

在新增或修改定时任务、Job、Trigger、任务初始化、插件卸载清理与调度链路时，读取本文件。

## 强制规则

- 不到万不得已不要新增定时任务；先证明该需求不能通过实时计算、按需计算、触发式计算、查询时派生或写入时同步等方式完成，再考虑调度方案。
- 统一使用基座已有 Quartz 能力。
- 默认把 `smart-core` 的 `QuartzListener` 当成插件 Quartz 生命周期唯一入口；插件只负责提供 `JobDetail`、`Trigger` 或在必要时通过 `SchedulerManager` 操作主调度器，不再自建另一套任务注册、启动或卸载清理逻辑。
- 统一让 JobDetail 与 Trigger 通过 Spring Bean 暴露，并纳入插件生命周期管理。
- 固定周期任务通过 `JobDetail` + `Trigger` Bean 声明；基于已有 Job 的一次性补发、导入后立即执行、用户触发的即时调度等场景，才通过 `SchedulerManager` 向主调度器补充 Trigger。
- 统一考虑插件启动与停止时的任务注册、清理与补救清理逻辑。
- 任务上下文涉及插件身份时，保持 `pluginId` 透传与清理逻辑一致。

## 推荐模式

- 遇到“定时刷新状态”“定时纠偏”“定时计算派生字段”这类需求时，优先评估是否能改成读取时计算、事件触发计算、状态变更时增量更新或基于统一时间能力的即时判断。
- 使用 `@Configuration` + `@Bean` 定义 `JobDetail` 和 `Trigger`。
- 让 `JobDetail` 保持可重用，动态补发场景只创建 Trigger 并绑定现有 Job；需要补发一次时，优先参考通过 `SchedulerManager.getScheduler().scheduleJob(trigger)` 向主调度器注册 Trigger 的现有实现。
- 让插件生命周期监听器负责启动注册和卸载删除，不在业务代码里自行维护另一套任务注册表。
- 动态创建 Trigger 时，显式补齐 `pluginId`、job key、trigger identity 与必要的业务参数，避免任务能跑但无法被基座按插件维度清理。
- 复用现有 group、identity、cron 与日志风格，保持可观察性与可维护性。
- 在说明里写清楚为什么不能改成计算式方案、任务何时触发、是否幂等、时间误差容忍度以及卸载时如何回收。

## 禁止做法

- 把本可通过业务计算解决的问题默认实现成定时轮询或周期性修正任务。
- 引入与 Quartz 并行的定时框架。
- 在插件里自行创建 `SchedulerFactoryBean`、`StdSchedulerFactory`、额外 `Scheduler` Bean，或新增一套和 `QuartzListener` 并行的任务初始化/清理机制。
- 用 `@EnableScheduling`、`@Scheduled`、`SchedulingConfigurer`、`TaskScheduler` 等 Spring 定时体系绕开基座 Quartz。
- 通过裸线程、`Timer` 或临时循环任务绕开统一调度体系。
- 以为定时任务天然可靠且时间准确，忽略调度延迟、执行堆积、节点负载和停机窗口带来的时间偏差。
- 新增任务时只关注启动，不关注插件停止或重启后的清理。

## 开发或评审检查点

- 是否已经证明该需求不能优先用计算式方案替代，而是必须使用调度。
- 是否使用了基座 Quartz，而不是自建调度方案。
- 固定周期任务的 Job 和 Trigger 是否纳入 Spring Bean 与插件生命周期。
- 若存在即时补发或一次性执行，是否通过 `SchedulerManager` 操作主调度器，而不是创建新的 Scheduler。
- 动态 Trigger 是否携带 `pluginId`，从而能被基座在插件停止、卸载或补救清理时正确回收。
- 是否说明了定时执行带来的时间误差和性能开销为何仍可接受。
- 插件停用、卸载、重启后是否有任务残留风险。
- 任务 identity、group、cron 与日志是否清晰可追踪。

## 仓库参考位置

- `backend/src/main/java/com/outbook/smart/listener/QuartzListener.java`
- `backend/src/main/java/com/outbook/smart/component/quartz/SchedulerManager.java`
- `backend/src/main/java/com/outbook/smart/media/config/VideoTranscodeJobConfig.java`
- `../smart-door-mixed/backend/src/main/java/com/outbook/smart/door/config/JobConfig.java`
- `../smart-face-mixed/backend/src/main/java/com/outbook/smart/face/service/impl/FaceUploadRecordServiceImpl.java`
