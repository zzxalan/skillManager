# 集成、构建与打包链路

## 适用场景

在修改插件入口、资源注册、前端构建产物接入、Gradle 打包、发布任务、资源复制逻辑，或需要运行开发调试、远程热更新、接口联调与鉴权验证时，读取本文件。

## 强制规则

- 先以真实构建脚本与真实入口代码为准，确认前端产物目录、后端复制目录与最终打包目录。
- 修改任何一段链路时，联动检查前端输出、后端复制、入口资源注册和最终插件包结构。
- 插件联调前先在 `frontend` 目录执行 `pnpm build`，确认 PC/H5 等前端静态产物已按项目脚本生成到真实输出目录；若执行环境没有加载用户 shell 配置，先补齐当前 Node/pnpm 所在 PATH。
- 前端产物生成后，在 `backend` 目录执行 `./gradlew clean 远程更新插件` 作为开发服务器热更新主路径；该任务会触发资源处理、打包并按 `build.gradle` 中 `outbookPackager.remoteUrl` 指向的开发服务器更新插件。
- 接口联调地址优先从 `outbookPackager.remoteUrl` 推导，不手写或沿用旧文档中的主机端口；若前端代理、登录地址与 `remoteUrl` 不一致，必须先说明差异再测试。
- 用户要求“联调接口”时，默认含义是在开发服务器上验证已更新插件：先从当前插件 `backend/build.gradle` 的 `outbookPackager.remoteUrl` 读取基座地址，再用 `curl` 请求宿主挂载后的真实接口；不要优先检查本地端口、启动本地后端或假设插件项目会在本机运行。
- 仅当用户明确要求“本地运行”“本地调试”或 `remoteUrl` 不可访问时，才切换到本地启动、端口探测或浏览器本地代理排查路径；切换原因必须在交付中说明。
- 插件接口默认需要登录 token；联调前优先用 `TOKEN=$(SMART_CORE_PASSWORD=... scripts/get-smart-core-token.sh {baseUrl})` 或脚本第三个参数获取，不要停在“需要用户提供 token”。后续请求固定使用 `token` 字段作为查询参数、请求头或 cookie 名称传递。
- 同一目标环境存在多个端口时，优先在插件 API 所在的 `remoteUrl` 同源基座地址登录取 token；不要把其他端口登录得到的 token 默认复用到当前插件 API，否则可能返回重新登录或 token 失效。
- 插件 Controller 的 `@RequestMapping` 只写插件内相对路径，不重复写宿主为插件挂载的 `/api/{pluginId}` 前缀；否则真实接口会变成双前缀路径。
- 登录账号与验证码默认值由 `get-smart-core-token.sh` 统一处理；密码必须通过脚本参数或 `SMART_CORE_PASSWORD` 环境变量提供，不在 skill、联调步骤、交付说明或项目文件里固化明文密码。
- 插件内若需要 Groovy 脚本能力，优先按正常 `implementation` 依赖进入插件 `runtimeClasspath`，并确认最终包内 `BOOT-INF/lib` 与 `META-INF/RESOURCES.CONF` 一致；不要为了绕过启动错误把 Groovy 私自挪到普通资源目录。若启动期在 `BeanDefinitionLoader` 报 `groovy/lang/GroovyObject`，重点检查 Spring Boot Groovy 探测使用的线程上下文 ClassLoader：`BeanDefinitionLoader` 所在加载器与插件 Groovy 依赖加载器不一致时，不应在只由插件加载器可见 Groovy 的半可见状态下初始化 `GroovyBeanDefinitionReader`；优先采用“启动期仅隐藏 `groovy.lang.MetaClass` 探测类，启动后恢复插件 ClassLoader”的小影响面处理。
- 若修改了 `smart-core` 这类被插件通过 `mavenLocal` 依赖的共享库，验证下游插件前必须先把共享库发布到本地 Maven；不要误以为兄弟插件会直接引用当前 workspace 里的基座源码。
- 涉及发布或仓库配置时，不在代码、文档或输出中扩散敏感地址与示例凭据。
- 对于插件菜单、入口声明、静态资源说明文件，若目标项目存在 `app.json` 或同类资源文件，必须与打包结果一起检查。

## 工具脚本

- `scripts/get-smart-core-token.sh {baseUrl}`：从 smart-core 基座登录接口获取 token，并只向 stdout 输出 token，便于 `TOKEN=$(...)` 后继续调用插件接口。
- 默认账号为 `super_admin`，默认验证码 `captchaKey=1`、`captchaCode=1`；密码不内置，必须通过第三个参数或 `SMART_CORE_PASSWORD` 提供。需要覆盖账号或验证码时优先使用 `SMART_CORE_USERNAME`、`SMART_CORE_CAPTCHA_KEY`、`SMART_CORE_CAPTCHA_CODE`。

## 推荐模式

- 先用“前端产物在哪里生成”“后端从哪里复制”“入口声明如何暴露资源”三问梳理链路。
- 开发联调按“前端构建 -> 后端远程更新插件 -> 脚本取 token -> 带 token 调插件接口”的顺序验证，遇到 HTML 兜底页或 404 时先检查插件是否已装载、Controller 是否重复声明宿主挂载前缀、真实 API 前缀是否正确、远程更新目标是否为当前服务器。
- 只做后端接口联调且用户没有要求更新插件时，优先按“读取 `remoteUrl` -> 推导 `/api/{pluginId}` 前缀 -> 脚本取 token -> `curl` 请求目标接口”的最短路径执行；若接口实现刚修改过，再先执行远程更新插件。
- 若仓库说明写的是旧目录，实际构建脚本写的是新目录，以实际构建脚本为准，并记录差异。
- 共享基座 API 或公共事件模型变更后，按“更新 `smart-core` -> `publishToMavenLocal` -> 再跑下游插件编译或测试”的顺序验证，避免把本地 Maven 旧产物误判成代码问题。
- 打包或复制逻辑变更后，优先运行构建命令验证链路没有断开。
- 新增脚本运行时、驱动包、解析引擎等非宿主常驻依赖时，先判断该依赖是否应作为插件运行时依赖进入 `runtimeClasspath`，并检查启动期是否会触发宿主类与插件依赖的 ClassLoader 半可见问题；只有确认该依赖不应参与插件启动装配时，才采用资源内置或执行时隔离加载。
- `outbookPackager.loadToMain` 在当前 `plugin-packager` 版本中只有配置入口和索引标记意图，源码里的 `initLoadToMainSet()` 未被调用，不能把它当作 Groovy 启动问题的可靠修复路径；优先用实际包结构和宿主远程更新结果验证。
- 接口测试脚本或临时命令只输出 token 是否获取成功、响应码和脱敏后的响应结构，不在日志、文档、提交说明或 skill 中落明文密码、token、内网地址清单。

## 禁止做法

- 只改前端输出目录，不改后端复制逻辑。
- 只改资源复制逻辑，不检查入口资源注册。
- 把历史文档中的 `web/`、`public/` 或 `app.json` 路径直接当成当前事实。
- 跳过前端构建直接执行远程更新，导致开发服务器仍使用旧静态资源。
- 为了绕过启动错误，把 Groovy 等插件运行时依赖移出 `runtimeClasspath` 或改成普通资源，导致 `BOOT-INF/lib`、`META-INF/RESOURCES.CONF` 和插件启动 ClassLoader 处理逻辑不一致。
- 用户说“联调接口”时把插件误当成本地 Spring Boot 应用处理，例如先查本地监听端口、尝试启动本地后端，或用 Vite 代理地址代替 `outbookPackager.remoteUrl`。
- 将登录 token、远程服务器地址、明文密码或仓库上传凭据写入新增代码、公开文档、测试快照或交付总结。

## 开发或评审检查点

- 前端 `build` 输出目录是否与后端复制目录匹配。
- 入口类注册的静态资源目录是否覆盖最终产物位置。
- 打包任务、文件名、插件 ID、发布路径是否被连带影响。
- 是否已按项目真实脚本运行 `pnpm build`，并确认产物时间或内容更新。
- 是否已按后端真实任务运行 `./gradlew clean 远程更新插件`，并确认任务成功、目标服务器来自 `outbookPackager.remoteUrl`。
- 接口联调是否从当前插件 `outbookPackager.remoteUrl` 推导开发服务器地址，并用 `curl` 请求宿主挂载后的 `/api/{pluginId}` 接口，而不是误用本地端口或旧文档地址。
- 接口测试是否先通过 `get-smart-core-token.sh` 获取 token，并固定使用 `token` 字段传参；若返回前端 HTML、登录页或权限错误，是否已区分“未装载/路由不对/鉴权失败/权限不足”。
- 插件 Controller 映射是否避免重复 `/api/{pluginId}`，接口是否能通过宿主挂载后的单前缀地址访问。
- 插件包内 Groovy 等运行时依赖是否按预期进入 `BOOT-INF/lib` 与 `META-INF/RESOURCES.CONF`；插件入口是否处理 Spring Boot Groovy 探测的 ClassLoader 边界，远程更新任务和宿主挂载后的真实接口是否通过。
- 若本次修改触及 `smart-core` 对外暴露的类、事件或接口，下游插件验证前是否已同步刷新本地 Maven 依赖。
- 输出或文档中是否避免泄露敏感配置。

## 仓库参考位置

- `backend/build.gradle`
- `backend/src/main/java/com/outbook/smart/Application.java`
- `frontend/package.json`
- `frontend/vite.config.ts`

## 备注

当前样例仓库之间的资源目录可能不同：有的 `processResources` 从 `../frontend/dist` 复制到 `public`，有的复制到 `web`。此类差异必须以当前项目 `backend/build.gradle` 为准，不可套用历史说明。
