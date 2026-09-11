# 后端数据访问

## 适用场景

在新增或修改实体、查询、分页、数据过滤、服务层数据访问与 Mapper 逻辑时，读取本文件。

## 强制规则

- 默认优先使用 MyBatis-Flex 体系完成数据访问。
- 默认禁止在 Controller、Service 或临时工具代码里硬编码 SQL 字符串。
- 默认优先使用实体、`BaseMapper`、`QueryWrapper`、`QueryBuilder`、`IFlexService` 等现有封装。
- 分页、条件查询、批量操作优先沿用现有 Flex 服务层和公共查询模式。
- 使用 MyBatis-Flex 的 `saveOrUpdate`、`saveOrUpdateBatch` 前，先确认主键是否由数据库生成；如果主键是业务主键、外部传入主键、手动赋值主键，或“实体一创建就会带主键”，禁止把它当作新增/更新兜底方法直接使用。
- 当实体主键不是数据库自增而是业务键时，新增或更新必须先显式判断记录是否存在，再明确调用 `save`、`saveBatch`、`updateById` 或按查询条件更新，不要依赖“主键有值”这一框架判定条件。
- 禁止把 MyBatis-Flex ActiveRecord 的 `Model.update()` / 实体 `record.update()` 当作“按主键更新当前行”。在 smart-core 的 `FlexModel` 体系中，`update()` 走的是当前实体的 `queryWrapper()`；默认 `queryWrapper()` 只带表信息，不会自动追加 `where id = ?`，可能把整张表按当前实体字段批量覆盖。
- 状态回写、快照回写、反馈回写这类只需要更新少数字段的场景，必须使用 `UpdateChain`、`updateByQuery` 加显式 `where`、或经过确认的 `updateById`，并只设置本次允许变更的字段，不要用整实体更新。
- 访问按月、按租户或按业务日期分表的数据时，必须通过模块内统一 Service 或分表处理器按业务日期路由到目标表；读写前确认目标分表存在，涉及新增字段时同步覆盖模板表、当前表和真实会访问的历史/未来分表。

## Flyway 迁移文件

- 迁移文件保持简单干净：禁止在迁移里写存储过程、函数、触发器，禁止出现带变量、游标、循环、复杂计算的过程化 SQL；复杂初始化逻辑放到插件 Java 启动逻辑或 Service 中实现，迁移只负责表达最终结果。
- 开发阶段允许直接改开发库反复验证，不必为每次调整都追加迁移文件；提交前把最终形态收敛成简单干净的迁移文件，并保证从空库执行一次就能复现最终表结构和数据。文件一旦提交进仓库即视为不可变：禁止修改内容、禁止重命名或改版本号、禁止删除，发现问题只能新增迁移文件修复。
- 动迁移文件前先用 `git status`、`git diff --stat` 自查本次是否改到了已有迁移文件；不确定某个迁移是否已在其他环境执行过时，一律按“已执行、不可改”处理。
- 表结构、字段、索引等 DDL 一律用 `V` 开头的版本化迁移，文件名 `V<秒级时间戳>__描述.sql`；版本号必须使用创建该文件时刻的秒级 Unix 时间戳（用 `date +%s` 生成），例如 `V1789118033__add_status_to_device.sql`。
- 禁止使用 `1`、`2`、`3` 这类递增序号，禁止使用 `20260911` 这类 yyyyMMdd 日期格式：序号在多人协作时必然冲突，日期格式同一天多个迁移无法区分先后。
- 同一秒内需要创建多个 `V` 迁移时，后一个文件的时间戳 +1 秒，保证版本号唯一且单调递增。
- 给表加数据（字典、默认配置、初始化数据等）一律用 `R` 开头的可重复执行迁移，文件名 `R__描述.sql`（不带版本号）；内容必须幂等，重复执行不产生重复数据（如 `INSERT ... ON DUPLICATE KEY UPDATE`、先删后插或先查后插），Flyway 会在校验和变化时自动重新执行。
- 迁移文件放在所属插件既有的 Flyway migration 目录（通常为 `backend/src/main/resources/db/migration/`），只允许操作本插件拥有的表；表归属规则见 `architecture-boundary.md`。

## 推荐模式

- 先查找邻近模块已有的实体、Service、Mapper 或查询封装，再决定扩展点。
- 简单查询优先使用 `QueryWrapper`、`QueryBuilder` 或现有 Service 默认方法。
- 复杂查询若无法通过现有封装清晰表达，优先沉到 Mapper 层或框架支持的位置，并在实现说明里写清原因。
- 尽量让查询条件与实体字段、数据权限逻辑保持同一套命名和封装方式。
- 遇到“按业务主键同步快照、状态、配置、映射关系”这类场景时，先在服务层写清楚“首次创建”和“后续更新”的分支，再决定是否补唯一索引、并发兜底或重试策略。
- 对状态流转类更新，优先写成“按主键条件 + 明确字段集合”的局部更新，例如只更新 `status`、`error_msg`、`update_time` 等职责内字段；更新后若排查数据污染问题，应回读数据库确认真实落库值。
- 考勤记录等 `*_yyyyMM` 分表读写，优先复用模块已有带日期参数的方法；不要直接调用会落到默认动态表的 `save`、`updateById`、`getOneOpt` 等便捷方法。

## 禁止做法

- 在业务代码中直接拼接原始 SQL。
- 为了图快绕开既有实体和 Service，直接在 Controller 中做数据库访问。
- 为局部需求新建与 MyBatis-Flex 并行的另一套 ORM 或数据库访问框架。
- 明知实体主键已手动赋值，仍直接调用 `saveOrUpdate`、`saveOrUpdateBatch`，把“是否更新”交给框架按主键非空推断。
- 直接调用从 `getById`、`one()`、`selectOneById` 等查询结果得到的实体对象的 `update()`，除非已经明确确认该实体对象携带的 `queryWrapper` 带有正确且唯一的 `where` 条件；常规业务代码默认不要这样写。
- 在状态同步或回执处理里用“带全量字段的旧实体”执行整实体更新，导致设备归属、业务归属、创建参数等非本次职责字段被覆盖。
- 给分表实体新增字段后，只修改模板表、当前月表或单个迁移脚本，遗漏历史月份、未来月份或业务查询实际访问的目标月份。

## 开发或评审检查点

- 是否优先使用了 MyBatis-Flex 与现有公共封装。
- 是否存在硬编码 SQL、字符串拼接查询或散落的数据访问逻辑。
- 查询、分页和批量操作是否复用了现有模式。
- 数据访问位置是否合理，是否留在 Service / Mapper 而非 Controller。
- 若代码使用了 `saveOrUpdate` 或 `saveOrUpdateBatch`，主键策略是否真的支持这种写法，而不是业务主键导致新增被误判成更新。
- 若代码使用了实体 `update()`，是否已经证明它不会无条件更新整表；否则必须改为显式 `where id` 或其他唯一条件的局部更新。
- 对快照同步、状态同步、配置回写等“按业务键落库”的逻辑，是否显式覆盖了首条插入与后续更新两个分支。
- 对控制记录、设备事件、反馈、快照等链路型数据，状态回写是否只更新状态职责字段，没有覆盖 `device_id`、`room_id`、`model`、`params`、`remark` 等归属字段。
- 涉及分表时，是否按业务日期定位目标表，并覆盖分表不存在、旧分表缺字段、历史数据读写和未来月份建表等场景。

## 仓库参考位置

- `backend/build.gradle`
- `backend/src/main/resources/application.yml`
- `backend/src/main/java/com/outbook/smart/common/pojo/QueryBuilder.java`
- `backend/src/main/java/com/outbook/smart/component/mybatisflex/IFlexService.java`
- `backend/src/main/java/com/outbook/smart/flex/service`
- `../smart-attendance-mixed/backend/src/main/java/com/outbook/smart/attendance/service/impl/AttendanceRecordServiceImpl.java`
- `../smart-attendance-mixed/backend/src/main/java/com/outbook/smart/attendance/bean/AttendanceShardTableHandler.java`
