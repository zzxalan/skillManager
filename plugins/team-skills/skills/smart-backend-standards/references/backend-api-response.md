# 后端接口与响应包装

## 适用场景

在新增或修改 Controller、接口返回、HTTP 方法选择、分页查询、增删改查响应结构时，读取本文件。

## 强制规则

- 对外 HTTP 响应默认统一使用 `CommonResult` 包装。
- 成功与失败返回统一使用 `CommonResult.success(...)`、`CommonResult.error(...)` 与现有错误码体系。
- 优先复用现有基础控制器与公共返回模式，保持同类接口的响应结构一致。
- 分页接口优先沿用现有 `PageVo`、`QueryBuilder`、基础分页接口模式。
- 当前 smart-* 插件对外接口默认只新增或修改为 `GET`、`POST`；受宿主网关、平台约束或统一规范影响时，不继续新增 `PUT`、`DELETE`、`PATCH` 接口。

## 推荐模式

- 控制器只保留参数接收、校验、调用服务和统一返回，业务逻辑放入 Service。
- 能复用 `FlexBaseController` 的基础增删改查时优先复用，再在钩子方法里补充特定逻辑。
- 返回错误时优先使用现有 `GlobalErrorCodeConstants` 或既有异常体系，而不是临时拼装错误语义。
- 简单读取类接口优先使用 `GET`；保存、更新、删除、批量处理、复杂查询等需要请求体或动作语义的接口统一使用 `POST`。
- 若存在历史 `PUT`、`DELETE` 接口，后续修改时优先评估迁移为 `POST`，并同步检查前端请求方法与宿主转发链路。

## 禁止做法

- 直接返回裸 `List`、裸实体、裸 `boolean`、裸字符串，导致接口风格不统一。
- 为单个接口临时设计一套与 `CommonResult` 并行的响应结构。
- 在 Controller 中堆积大量业务流程和数据访问逻辑。
- 在当前插件工程中继续新增 `@PutMapping`、`@DeleteMapping`、`@PatchMapping`，或在前端请求层继续扩散 `PUT`、`DELETE`、`PATCH` 用法。

## 开发或评审检查点

- 每个对外接口是否统一返回 `CommonResult`。
- 成功、失败、分页结构是否与现有模块保持一致。
- 错误码与错误消息是否优先复用现有枚举或异常体系。
- Controller 是否过重，是否有应下沉到 Service 的逻辑。
- 接口方法是否符合当前插件统一约束：读取用 `GET`，提交动作与批量操作用 `POST`，不新增 `PUT`、`DELETE`、`PATCH`。
- 前后端是否同步调整了请求方法，避免仅改 Controller 映射而遗漏前端 `request` 配置。

## 仓库参考位置

- `backend/src/main/java/com/outbook/smart/common/pojo/CommonResult.java`
- `backend/src/main/java/com/outbook/smart/common/controller/FlexBaseController.java`
- `backend/src/main/java/com/outbook/smart/common/pojo/QueryBuilder.java`
- `backend/src/main/java/com/outbook/smart/door/controller/DoorRuleController.java`
- `frontend/src/pages/door/api.ts`
