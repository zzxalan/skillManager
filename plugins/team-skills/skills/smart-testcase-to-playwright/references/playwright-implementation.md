# Smart Playwright 实现规则

## 工程放置

- 固定输出到主要业务插件根目录的 `test/`。
- `test/` 已存在时，先读取现有配置、包管理器、测试结构和代码风格，只做增量修改。
- `test/` 不存在时，复制 `assets/playwright-template/`，再安装依赖和生成业务测试。
- 不把 Playwright 依赖加入插件 `frontend/` 或仓库根工程，除非现有项目已经采用这种结构。

## 环境变量

默认使用：

| 变量 | 用途 |
| --- | --- |
| `SMART_FRONTEND_URL` | smart 前端测试环境地址 |
| `SMART_BACKEND_URL` | smart 后端或网关地址 |
| `SMART_USERNAME` | 测试账号 |
| `SMART_PASSWORD` | 测试账号密码 |
| `SMART_TOKEN` | 可选的临时 token；存在时可不使用账号密码登录 |
| `PLAYWRIGHT_WORKERS` | 并发数，默认 `1` |

- 提交 `.env.example`，不得提交 `.env`。
- 不把 token、密码、数据库连接信息写进测试源码、报告或最终回复。
- 默认通过 `auth.setup.ts` 创建 `.auth/user.json`，业务测试复用 storage state。

## 用例结构

- 文件名使用业务功能 kebab-case，例如 `booking-approval.spec.ts`。
- 测试标题使用 `[CASE-ID] 用例标题`。
- 使用 `test.describe` 按功能模块组织，不要把整份文档塞进一个超长测试。
- 飞书链接或 Excel 来源位置使用 `test.info().annotations` 或短注释记录。
- 仅在重复操作明显时提取 helper、fixture 或 page object；不要为单个短用例建立过度抽象。

## 定位器优先级

按以下顺序选择稳定定位器：

1. `getByRole`
2. `getByLabel`
3. `getByPlaceholder`
4. `getByText`
5. `getByTestId`
6. 简短且稳定的 CSS

禁止默认使用：

- 长 XPath。
- 依赖 DOM 层级位置的 `nth()`。
- 依赖动态 class 名的选择器。
- 仅凭截图坐标的点击。

确实缺少稳定定位器时，记录需要业务代码补充的 `data-testid`。

## 等待与异步

- 使用 Playwright 自动等待、`expect` 重试和明确的页面状态。
- 对接口驱动操作使用 `page.waitForResponse`、`expect.poll` 或页面可见结果。
- 对下载使用 `page.waitForEvent('download')`。
- 对新页面使用 `page.waitForEvent('popup')`。
- 对 iframe 使用 `frameLocator`。
- 禁止用 `waitForTimeout` 作为正常同步手段。

## 断言

- 每个文档预期结果必须对应至少一个可观察断言。
- 优先断言用户可见结果、数据状态、URL、按钮状态、表格内容、详情值或下载文件。
- 不要只断言页面打开、接口返回 200 或某个容器存在。
- 成功提示会短暂消失时，同时断言持久化后的业务状态。
- 列表和分页场景要限定到目标行，不对整页模糊文本做宽泛断言。
- 文档预期与真实产品冲突时，将测试失败保留为证据，不要降低断言来强行通过。

## 数据准备与清理

- 优先使用专用测试账号和专用测试数据。
- 新建数据使用带用例编号和唯一后缀的名称。
- 测试前检查重名、前置状态和依赖数据。
- 测试后清理能够安全删除的数据；清理失败不能掩盖主测试失败。
- 删除、审批、发布和真实设备操作严格遵循 `SKILL.md` 的安全边界。
- 测试之间不得依赖执行顺序或上一次运行残留状态。

## 登录

- 生成的测试必须能够在新进程中重建登录态，不能依赖探索浏览器的现有 session。
- `auth.setup.ts` 优先读取 `SMART_TOKEN`；没有 token 时调用 smart 登录接口获取 token。
- 默认先尝试 `/api/user/login`，失败后再尝试 `/user/login`。
- 检查返回中的 `data.token` 和 `data.violations.valid`。
- token 只写入被 `.gitignore` 排除的 `.auth/user.json`。

## 报告与失败证据

默认配置：

- HTML：`playwright-report/`
- JSON：`test-results/results.json`
- JUnit：`test-results/junit.xml`
- 运行产物：`test-results/artifacts/`
- 失败截图：`only-on-failure`
- trace：`retain-on-failure`
- video：`retain-on-failure`

最终汇报测试总数、通过数、失败数、跳过数、失败用例编号和报告路径。

## 完成标准

只有同时满足以下条件才能称为“已完成并验证”：

1. 测试代码写入正确插件的 `test/`。
2. 类型检查通过。
3. Playwright 测试至少实际运行一次。
4. 报告文件成功生成。
5. 没有在版本库中写入凭据或 storage state。
6. 失败用例有明确证据，且没有使用固定休眠或弱化断言掩盖问题。
