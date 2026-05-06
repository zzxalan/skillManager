# 宿主消息功能接入

## 适用场景

当插件需要发送站内消息、未读提醒、任务通知、业务变更通知，定义消息模板或跳转动作，或需要接入宿主消息中心的投递、撤回、已读、未读和审计能力时，读取本文件。

## 强制规则

- 消息主记录、接收人状态、未读数、撤回、删除、审计和推送由宿主消息模块统一管理；插件不得直接写 `sys_message`、`sys_message_receiver`、`sys_message_template_override`、`sys_message_audit_log` 等宿主消息表。
- Java 插件内发送消息优先调用宿主 `MessageOpenApi`，并按 MAIN Bean 方式注入：`@Autowired` + `@AutowiredType(AutowiredType.Type.MAIN)`；不要把宿主消息 Service 当成本插件本地 Bean 做普通构造器注入。
- 发送消息的插件必须通过 `MessageTemplateExtract` 暴露模板，使用 `@Extract(bus = "MessageTemplate", scene = "<sourcePluginId>")` 注册；Extract 的 `sourcePluginId()`、`scene`、投递 DTO 的 `sourcePluginId` 必须一致。
- `templateCode` 只要求在同一个 `sourcePluginId` 下唯一；同一插件内不能重复，跨插件可按各自来源独立命名。
- 模板变量标记为必填时，投递 DTO 的 `variables` 必须提供非空值；日期、名称、摘要等变量格式化放在业务投递服务中完成。
- `requestId` 是投递幂等键，同一业务事件使用稳定值，不同发送事件不能复用固定值；需要每次都生成消息时，追加批次、摘要或 UUID。
- 投递时必须提供 `externalBizType` 与 `externalBizId`，用于来源业务反查、撤回、审计和跳转解析。
- 接收人统一用 `MessageReceiverTargetDto` 表达；已明确具体用户时优先展开为 `USER`，避免角色或组织范围变化造成误发、重复发送。
- 点击跳转优先使用模板默认动作；需要实时权限、对象存在性或动态路由判断时，再实现 `MessageActionExtract`。
- 消息通常不应阻断主业务流程；除非消息就是核心业务结果，否则捕获异常并记录来源插件、模板、业务 ID、接收人数和错误摘要。

## 推荐模式

- 插件侧按职责拆分：`extract/*MessageTemplateExtract.java` 只定义模板；`service/impl/*MessageNotifyService.java` 只负责把业务事件转换为消息投递 DTO。
- 模板编码使用稳定业务语义常量，例如 `NOTICE_PUBLISHED`、`EXAM_PLAN_NOTICE`，不要使用页面标题或可变文本。
- 模板版本从 `1` 开始；变量语义或模板结构出现兼容性变化时递增版本，避免历史消息快照和新模板语义混淆。
- `requestId` 推荐包含插件、模板或事件类型、业务 ID；重复触发只允许一条消息时使用稳定业务键，需要保留每次触发时加入事件批次或 UUID。
- 批量发送优先使用宿主批量接口，但大范围投递前要确认接收人展开数量、异步策略和失败日志。
- 撤回业务消息优先通过 `sourcePluginId + externalBizType + externalBizId` 定位，不直接操作宿主表。

## 禁止做法

- 插件新增自己的用户消息表来绕过宿主消息中心。
- 把插件消息模板硬编码到宿主消息模块；模板归属插件，通过 Extract 暴露。
- 在模板 Extract 中查询大量业务数据或执行投递逻辑；Extract 只返回模板定义。
- 模板变量名和投递变量名只靠注释约定，实际代码不一致。
- 把用户可变文本、敏感内容或超长内容拼入 `requestId`。
- 在消息跳转中硬编码不可用的插件内部路径；目标不可用时应降级为详情、无跳转或其他宿主支持的安全动作。
- 把 `@Caller` / `@Supplier` 当作消息模板发现机制；模板发现走 Extract，投递走宿主 `MessageOpenApi`。

## 开发或评审检查点

- 插件是否明确 `sourcePluginId`，且模板 Extract、投递 DTO、前端来源筛选保持一致。
- 是否新增或复用了 `MessageTemplateExtract`，并标注正确的 `bus` 与 `scene`。
- `MessageOpenApi` 是否按 MAIN Bean 注入，而不是普通构造器注入。
- 投递 DTO 是否包含 `requestId`、`sourcePluginId`、`templateCode`、`externalBizType`、`externalBizId`、`receivers`、`variables`。
- 必填模板变量是否全部提供，接收人是否为空、去重且符合业务权限和数据范围。
- 失败日志是否足够定位，且非核心消息失败不会破坏主业务。
- 若消息需要跳转，默认动作或 `MessageActionExtract` 是否能处理对象删除、无权限、插件不可用等降级场景。

## 仓库参考位置

- `smart-core-mixed/backend/src/main/java/com/outbook/smart/message/service/MessageOpenApi.java`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/message/controller/MessageOpenController.java`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/message/controller/MessageController.java`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/message/service/impl/MessageTemplateServiceImpl.java`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/message/service/impl/MessageActionServiceImpl.java`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/message/extract/MessageTemplateExtract.java`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/message/extract/MessageActionExtract.java`
- `smart-notice-mixed/backend/src/main/java/com/outbook/smart/notice/extract/NoticeMessageTemplateExtract.java`
- `smart-notice-mixed/backend/src/main/java/com/outbook/smart/notice/service/impl/NoticeMessageNotifyService.java`
- `smart-course-mixed/backend/src/main/java/com/outbook/smart/course/extract/CourseMessageTemplateExtract.java`
- `smart-exam-mixed/backend/src/main/java/com/outbook/smart/exam/service/impl/ExamMessageNotifyService.java`
