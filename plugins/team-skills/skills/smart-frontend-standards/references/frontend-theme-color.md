# 前端主题色规范

## 目录

- [适用场景](#适用场景)
- [主题来源与链路](#主题来源与链路)
- [强制规则](#强制规则)
- [Token 选择](#token-选择)
- [推荐模式](#推荐模式)
- [禁止做法](#禁止做法)
- [开发或评审检查点](#开发或评审检查点)
- [仓库参考位置](#仓库参考位置)

## 适用场景

在新增或修改主题色、选中态、链接色、品牌强调色、动态换肤、Ant Design token、CSS 变量、antd-mobile 主题，或处理 PC、qiankun 微应用、独立 H5 的主题接入时，读取本文件。

## 主题来源与链路

- 系统主题色配置键是 `colorPrimary`，当前默认值是 `#01d0bb`。
- `@va/core/store` 将系统设置保存到共享的 `setting` 缓存；`@va/ui` 的 `AntdConfig` 从该缓存读取 `colorPrimary`，再注入 Ant Design `ConfigProvider`。
- `AntdConfig` 默认开启 Ant Design CSS Variables，并根据当前主题色生成 `colorPrimaryBg`、`colorPrimaryBorder`、`colorPrimaryHover`、`colorPrimaryActive` 等派生 token。
- smart-core PC 入口使用自定义 CSS 变量前缀 `outbook`，插件侧 `AntdConfig` 默认使用 Ant Design 前缀；业务代码不能假定全局变量一定叫 `--ant-color-primary` 或 `--outbook-color-primary`。
- 系统设置变化后，`AntdConfig` 会重新读取 `setting` 缓存并刷新 token；业务组件只要消费 token 或由 token 映射出的局部变量，就应跟随主题变化。

## 强制规则

- React 组件内优先使用 `const { token } = theme.useToken()` 获取当前主题，不导入或复制默认主题色常量。
- 主操作、链接、选中态、焦点态等主题语义使用 `colorPrimary` 系列；成功、警告、失败、信息状态分别使用 `colorSuccess*`、`colorWarning*`、`colorError*`、`colorInfo*`，不要用主题色代替业务状态色。
- hover、active、浅色背景和边框必须优先使用 Ant Design 已生成的对应 token，不手写颜色，不通过字符串拼接透明度自行推导主题色。
- Ant Design 和 Pro Components 自带的主题行为优先交给组件 token；只有组件 API 无法表达设计时，才增加局部样式映射或局部 `ConfigProvider` 覆盖。
- CSS Modules 或普通 CSS 需要使用主题值时，在组件根节点把 token 映射为业务作用域 CSS 变量，例如 `--door-h5-primary`、`--message-primary`；CSS 文件只消费这些局部变量。
- 不在业务 CSS 中直接依赖 `--ant-color-*`、`--outbook-color-*` 等全局前缀变量。确需兼容纯 CSS 首屏或 Provider 挂载前状态时，可以把全局变量作为回退值，但组件挂载后仍由 token 显式注入局部变量。
- antd-mobile 页面必须把 Ant Design token 桥接到 antd-mobile CSS 变量，至少同步 `--adm-color-primary`；业务自定义 CSS 同时使用页面或模块专属变量，避免污染其他 H5 页面。
- 独立 H5 若不能保证由 smart-core 先完成系统设置初始化，必须在渲染 `AntdConfig` 前调用现有 `syncSettings()`，或沿用当前项目的 `SettingsController.getDefinitionsConfigMap()` + `setSettingInfo()` 模式。
- qiankun PC 插件入口继续由 `AntdConfig` 包裹；默认读取宿主已写入的共享 `setting` 缓存，不在插件内再创建另一套主题上下文或硬编码主题色。
- 新增主题实现时同时检查亮色、暗色和动态修改 `colorPrimary` 后的表现；不能只验证默认色。

## Token 选择

| 视觉语义 | 优先 token |
| --- | --- |
| 主按钮、主链接、关键图标、选中态 | `colorPrimary` |
| 悬浮态 | `colorPrimaryHover` |
| 按下或激活态 | `colorPrimaryActive` |
| 浅色主题背景 | `colorPrimaryBg` |
| 浅色背景悬浮态 | `colorPrimaryBgHover` |
| 主题边框 | `colorPrimaryBorder` |
| 主题边框悬浮态 | `colorPrimaryBorderHover` |
| 正文与次级文字 | `colorText`、`colorTextSecondary` |
| 容器与页面背景 | `colorBgContainer`、`colorBgLayout` |
| 普通边框 | `colorBorder`、`colorBorderSecondary` |
| 成功、警告、失败、信息 | 对应的 `colorSuccess*`、`colorWarning*`、`colorError*`、`colorInfo*` |

## 推荐模式

### React 内联样式或组件属性

```tsx
import { theme } from "antd";

function PrimaryLink() {
  const { token } = theme.useToken();

  return <a style={{ color: token.colorPrimary }}>查看详情</a>;
}
```

只在确实需要自定义样式时使用 token；普通 `Button type="primary"`、`Tabs`、`Tag` 等优先使用组件原生主题能力。

### CSS Modules 主题桥接

```tsx
const { token } = theme.useToken();

return (
  <section
    className={styles.page}
    style={
      {
        "--feature-primary": token.colorPrimary,
        "--feature-primary-hover": token.colorPrimaryHover,
        "--feature-primary-bg": token.colorPrimaryBg,
        "--feature-primary-border": token.colorPrimaryBorder,
      } as React.CSSProperties
    }
  >
    {/* 页面内容 */}
  </section>
);
```

```css
.actionLink {
  color: var(--feature-primary);
}

.actionLink:hover {
  color: var(--feature-primary-hover);
}

.selectedCard {
  background: var(--feature-primary-bg);
  border-color: var(--feature-primary-border);
}
```

- 变量名带页面、模块或组件前缀，避免使用过于宽泛的 `--primary-color`。
- token 到 CSS 变量的映射放在能够覆盖整个模块且作用域最小的根节点。
- `style` 对象较大时用 `useMemo`，依赖真实使用的 token；不要为了形式对简单映射过度封装。

### antd-mobile 主题桥接

```tsx
function H5ThemeBridge() {
  const { token } = theme.useToken();

  useEffect(() => {
    const rootStyle = document.documentElement.style;
    rootStyle.setProperty("--adm-color-primary", token.colorPrimary);
    rootStyle.setProperty("--feature-h5-primary", token.colorPrimary);
    rootStyle.setProperty("--feature-h5-primary-bg", token.colorPrimaryBg);

    return () => {
      rootStyle.removeProperty("--adm-color-primary");
      rootStyle.removeProperty("--feature-h5-primary");
      rootStyle.removeProperty("--feature-h5-primary-bg");
    };
  }, [token.colorPrimary, token.colorPrimaryBg]);

  return null;
}
```

- Bridge 必须挂在 `AntdConfig` 内部，确保 `theme.useToken()` 读取到系统主题。
- effect 清理时移除本组件写入的变量，避免微应用卸载或 H5 路由切换后残留。
- 同一 H5 入口只保留一个全局 antd-mobile Bridge；页面专属变量优先绑定在页面根节点，不全部写到 `documentElement`。

### 独立 H5 初始化

```tsx
async function setupApp() {
  await syncSettings();

  createRoot(document.getElementById("root")!).render(
    <AntdConfig>
      <H5ThemeBridge />
      <App />
    </AntdConfig>,
  );
}
```

若入口已有等价的设置同步逻辑，直接复用，不重复请求。

## 禁止做法

- 在新增代码中写死 `#01d0bb`、`#1677ff`、`#1890ff` 等颜色来表达系统主题。
- 用 `rgba(...)`、`${token.colorPrimary}1a`、固定渐变色等方式自行制造主题色派生值，而已有语义 token 可以满足需求。
- 把所有状态统一渲染成 `colorPrimary`，导致成功、告警和失败语义丢失。
- 在页面内再套一层 `ConfigProvider` 并覆盖全局 `colorPrimary`，只为修改单个组件颜色。
- 直接修改 `document.documentElement` 的主题变量却不清理，或让多个页面重复写同一全局变量。
- 只改 CSS 默认值，不接入 `theme.useToken()`，导致后台切换系统主题后页面仍显示旧颜色。
- 假设宿主和插件的 Ant Design CSS 变量前缀相同。
- 独立 H5 在系统设置尚未同步时直接渲染，并把 `AntdConfig` 的默认色误当成最终主题色。

## 开发或评审检查点

- 主题值是否来自 `theme.useToken()` 或组件 token，而不是固定色值。
- 主色派生状态是否选用了正确的 hover、active、bg、border token。
- 成功、警告、失败、信息是否使用各自的语义色。
- CSS 是否通过模块专属变量接收 token，没有依赖不稳定的全局 CSS 变量前缀。
- antd-mobile 是否同步了 `--adm-color-primary`，Bridge 是否位于 `AntdConfig` 内并完成清理。
- 独立 H5 是否在渲染前同步系统设置，qiankun 插件是否继续复用共享主题链路。
- 动态修改 `colorPrimary` 后，自定义样式是否和 Ant Design 组件一起更新。
- 暗色模式下文字、背景、边框和主题色组合是否仍可读。

## 仓库参考位置

- `smart-front-reconstruction/packages/ui/src/AntdConfig.tsx`
- `smart-front-reconstruction/packages/core/src/store/store/settings.ts`
- `smart-core-mixed/frontend/src/main.tsx`
- `smart-core-mixed/frontend/src/h5.tsx`
- `smart-core-mixed/frontend/src/h5_pages/mobile-theme-bridge.tsx`
- `smart-core-mixed/frontend/src/pages/page-builder/components/library/business/personal-card/personal-card.tsx`
- `smart-door-mixed/frontend/src/h5_pages/door/room-detail-page.tsx`
- `smart-uniTask-mixed/frontend/src/pages/h5/mobile-theme-bridge.tsx`
- `smart-basic-mixed/backend/src/main/resources/config/config-definition.json`
