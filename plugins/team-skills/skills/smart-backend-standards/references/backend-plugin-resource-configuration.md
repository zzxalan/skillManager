# 插件资源与系统配置声明

## 内容导航

- [适用场景](#适用场景)
- [文件职责与路径](#文件职责与路径)
- [`resources.json` 强制规则](#resourcesjson-强制规则)
- [`config-definition.json` 强制规则](#config-definitionjson-强制规则)
- [修改流程](#修改流程)
- [禁止做法](#禁止做法)
- [开发或评审检查点](#开发或评审检查点)
- [仓库参考位置](#仓库参考位置)

## 适用场景

在新增或修改插件角色、应用入口、菜单权限、按钮权限、API 鉴权路径、数据权限，或向宿主系统设置页注册插件配置项时，读取本文件。

## 文件职责与路径

- `backend/src/main/resources/resources.json`：声明角色、应用入口、权限树、角色权限关系和 API 鉴权路径。插件启动后由宿主 `PluginResourceListener` 从类路径根目录读取。
- `backend/src/main/resources/config/config-definition.json`：声明插件系统配置分组、配置键、值类型、表单组件、默认值和校验约束。插件启动后由宿主 `ConfigDefinitionListener` 按固定类路径 `config/config-definition.json` 读取。
- 两个文件都是插件运行时协议，不是普通说明文档；修改后必须检查 JSON 语法、打包位置和宿主加载结果。

## `resources.json` 强制规则

- 顶层使用 JSON 对象，按需包含 `roles`、`apps`、`permissions` 数组。
- 字段名使用 snake_case。宿主读取时使用 `PropertyNamingStrategies.SNAKE_CASE`，不要在同一文件中混用 camelCase。
- `role_code`、`permission_code` 按全局编码理解；`app_code` 也应使用插件或业务前缀避免冲突。不要复用其他插件的编码。
- 角色项至少声明 `role_name` 和 `role_code`；应用项至少声明 `name`、`app_code`、`path` 和 `permission`。`group_name` 不为空时，宿主会确保对应应用分组存在。
- 应用的 `platform` 默认为 `pc`，`target` 默认为 `_self`，`sort` 默认为 `99`；需要 H5、新窗口或特定排序时显式声明，不依赖历史数据库值猜测默认行为。
- 应用入口的 `permission` 必须指向对应 `permission_type: "app"` 的 `permission_code`，应用、根权限和子权限必须形成完整关联。
- 根权限使用 `parent_id: 0`；子权限优先使用 `parent_code` 引用父级 `permission_code`，不硬编码数据库自增 ID。
- `permission_type` 只使用宿主枚举已支持的 `app`、`menu`、`button`。
- `roles` 中的每个值必须是已存在角色或本文件 `roles` 中声明的 `role_code`；找不到角色时，宿主只记录警告，不会自动补齐错误编码。
- `api_path` 使用 `HTTP方法:宿主挂载后路径` 格式，多个路径用英文逗号分隔，例如 `GET:/api/classPanel/config,POST:/api/classPanel/config`。
- 当前宿主权限路径缓存只显式处理 `GET` 和 `POST`；新增 `PUT`、`DELETE`、`PATCH` 之前先核对基座实现，不要只在 JSON 中声明就认为已生效。
- 路径通配符跟随宿主 Sa-Token 路径匹配语义；对路径参数使用项目已有的 `/*` 模式，不自创 Spring MVC 占位符写法。
- `resource_path` 用于声明对应前端资源或路由，`sort_order` 用于权限树排序；只有页面确实消费 `resource_path` 时才填写，排序值应与相邻模块保持稳定间隔。
- `data_type` 表示需加载的数据权限类型，多个值使用英文逗号分隔；只在对应按钮权限真正需要数据范围时声明。
- `icon` 可使用插件类路径下的相对路径，例如 `static/icon/班牌设置.png`；宿主会尝试统计并转换为文件 ID。修改图标后同时检查源文件和最终插件包。
- 插件启动时同步资源，停止时隐藏系统资源。已被用户修改的角色、权限或应用字段可能受宿主保护而不被插件默认值覆盖，验证时要区分“新安装默认值”和“已有环境用户值”。

### `resources.json` 结构示例

```json
{
  "roles": [
    {
      "role_name": "物联管理员",
      "role_code": "iot_manager"
    }
  ],
  "apps": [
    {
      "name": "班牌设置",
      "app_code": "panel_settings",
      "group_name": "班牌",
      "path": "/classPanel/device-settings",
      "permission": "class_panel_settings_app",
      "icon": "static/icon/班牌设置.png"
    }
  ],
  "permissions": [
    {
      "permission_name": "班牌设置",
      "permission_code": "class_panel_settings_app",
      "permission_type": "app",
      "parent_id": 0,
      "sort_order": 45,
      "roles": ["admin", "iot_manager"]
    },
    {
      "permission_name": "班牌设置/基础设置",
      "permission_code": "class_panel_settings_menu",
      "permission_type": "menu",
      "parent_code": "class_panel_settings_app",
      "sort_order": 46,
      "roles": ["admin", "iot_manager"]
    },
    {
      "permission_name": "查看",
      "permission_code": "panel_settings_view",
      "permission_type": "button",
      "parent_code": "class_panel_settings_menu",
      "api_path": "GET:/api/classPanel/config",
      "sort_order": 47,
      "roles": ["admin", "iot_manager"]
    }
  ]
}
```

## `config-definition.json` 强制规则

- 顶层使用 JSON 数组，每个元素是一个配置分组。
- 分组必须提供非空 `groupCode`、`groupName` 和非空 `items`；`groupOrder` 不填时按 `0` 处理。
- 配置项必须提供非空 `configKey`、`label`、`valueType` 和非 null 的 `required`；`orderNo` 不填时按 `0` 处理。
- `configKey` 是实际系统配置的键，优先使用插件或业务前缀保持全局语义清晰。即使定义层允许不同分组出现同名 `configKey`，实际配置值仍按 `configKey` 存储和读取；除非明确要共享同一值，不要跨分组或跨插件复用。
- `valueType` 必须是宿主 `ConfigValueTypeEnum` 支持的类型，常用存储语义为 `STRING`、`NUMBER`、`BOOLEAN`、`JSON`；大小写不敏感，但同一文件应保持一致。
- `formType` 控制系统设置页的表单组件，例如 `input`、`input-number`、`va-switch`、`select`、`checkbox`、`time`、`color`。先核对宿主前端已支持的 valueType 或动态上传组件，不在 JSON 中自创组件名。
- `defaultValue` 的 JSON 类型必须与 `valueType` 的序列化语义一致。数字使用 JSON number，多选值使用数组，字符串开关的 `activeValue` / `inactiveValue` 与默认值保持同类型。
- `min` / `max` 用于 NUMBER 范围校验，也会被前端组件用作边界或长度约束。整数限制使用 `extJson` 中的 `integerOnly: true`，不只依赖前端 `precision`。
- `options` 用于下拉、单选或多选项，每项使用 `label` 和 `value`。
- `accept` 用于文件上传类型限制；只在对应上传组件中声明。
- `extJson` 必须是“JSON 字符串”，不是内嵌 JSON 对象。常用结构包含 `fieldProps`、`formProps`、`integerOnly`；写入前单独校验其内层 JSON。
- 插件启动时按 `pluginId + groupCode + configKey` 同步定义，并删除本插件已不再声明的旧定义；插件停止时移除定义。
- 默认值只在对应 `configKey` 尚无已存配置值时写入。修改 `defaultValue` 不会自动覆盖现有环境的用户值，需要迁移时单独设计兼容逻辑。
- 配置保存成功且事务提交后，宿主会发布 `ConfigChangeEvent`。插件需对配置变更执行副作用时，优先监听该事件，不另起轮询或独立配置通知机制。

### `config-definition.json` 结构示例

```json
[
  {
    "groupCode": "class_panel",
    "groupName": "终端配置",
    "groupOrder": 11,
    "items": [
      {
        "configKey": "class_panel_idle",
        "label": "闲置停留时间",
        "valueType": "NUMBER",
        "formType": "input-number",
        "placeholder": "请输入闲置停留时间",
        "helpText": "超时后返回首页，单位：秒。",
        "required": true,
        "min": 0,
        "max": 120,
        "orderNo": 70,
        "defaultValue": 20
      },
      {
        "configKey": "class_panel_emergency_shutdown_btn",
        "label": "应急关机按钮",
        "valueType": "STRING",
        "formType": "va-switch",
        "placeholder": "",
        "helpText": "是否显示应急关机按钮。",
        "required": true,
        "orderNo": 71,
        "defaultValue": "0",
        "extJson": "{\"fieldProps\":{\"activeText\":\"是\",\"inactiveText\":\"否\",\"activeValue\":\"1\",\"inactiveValue\":\"0\"}}"
      }
    ]
  }
]
```

## 修改流程

1. 先搜索对应 Controller、前端路由、权限判断、配置读取与 `ConfigChangeEvent` 监听代码，确认声明与实际行为一致。
2. 修改 `resources.json` 时联动检查角色编码、应用权限、父子权限、API 方法与路径、前端入口和图标资源。
3. 修改 `config-definition.json` 时联动检查配置键消费方、默认值类型、表单组件、服务端校验和历史值兼容。
4. 先对文件执行 `jq empty <file>`；存在 `extJson` 时，再逐项解析内层 JSON。
5. 执行与改动范围匹配的后端构建或插件打包，并检查最终包中包含 `resources.json` 和 `config/config-definition.json`。
6. 在宿主环境启动或远程更新插件，验证应用入口、权限树、API 鉴权、系统设置表单、默认值和已有用户值保护。

## 禁止做法

- 只增加前端菜单或按钮，不在 `resources.json` 声明对应权限和 API 路径。
- 只声明按钮权限，却缺少 app -> menu -> button 父子链路或应用 `permission` 关联。
- 把 Controller 内相对路径直接填入 `api_path`，遗漏宿主实际挂载的 `/api/{pluginId}` 前缀。
- 把 `config-definition.json` 放在资源根目录，或随意改名为其他路径。
- 把 `extJson` 写成 JSON 对象，或写入无法被 `JSON.parse` 解析的字符串。
- 通过改默认值企图强制覆盖已有环境配置。
- 修改 JSON 后只做语法检查，不验证插件包内路径和宿主加载结果。

## 开发或评审检查点

- 文件路径、JSON 顶层结构和字段命名是否正确。
- 角色、应用、app/menu/button 权限链和 API 路径是否完整一致。
- 权限编码、应用编码和配置键是否具有稳定业务语义并避免冲突。
- `api_path` 的 HTTP 方法、宿主前缀、通配符和多路径分隔是否与真实 Controller 一致。
- 配置项的 `valueType`、`formType`、`defaultValue`、`options`、`min/max`、`accept`、`extJson` 是否相互匹配。
- 修改默认值、删除配置定义或重命名 `configKey` 时，是否评估现有配置值、事件监听和兼容迁移。
- 构建产物是否包含两个声明文件，宿主启动日志和界面是否证明注册成功。

## 仓库参考位置

- `smart-classPanel-mixed/backend/src/main/resources/resources.json`
- `smart-classPanel-mixed/backend/src/main/resources/config/config-definition.json`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/listener/PluginResourceListener.java`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/listener/ConfigDefinitionListener.java`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/flex/service/impl/PluginResourceServiceImpl.java`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/flex/service/impl/PermissionServiceImpl.java`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/flex/service/impl/ConfigDefinitionServiceImpl.java`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/flex/service/impl/ConfigDefinitionValueValidator.java`
- `smart-core-mixed/backend/src/main/java/com/outbook/smart/common/enums/ConfigValueTypeEnum.java`
- `smart-core-mixed/frontend/src/pages/system/settings.tsx`
