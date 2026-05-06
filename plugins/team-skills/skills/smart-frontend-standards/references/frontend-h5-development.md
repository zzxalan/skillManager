# H5 页面开发规范

## 适用场景

在插件中开发 H5 移动端页面（非 qiankun 微前端接入的独立移动端入口）时，读取本文件。

## 强制规则

- H5 入口 HTML 文件统一命名为 `h5.html`，放在 `frontend/` 根目录。
- H5 入口 TSX 文件统一命名为 `h5.tsx`，放在 `frontend/src/` 目录。
- H5 页面组件统一放在 `frontend/src/h5_pages/` 目录下，按业务域分子目录（如 `attendance/`、`notice/`）。
- H5 构建配置独立为 `vite.config.h5.ts`，与主应用 `vite.config.ts` 分离。
- H5 构建产物输出到 `dist/<plugin-name>/h5/` 子目录，确保与主应用产物隔离。
- H5 页面不使用 qiankun 微前端接入，而是作为独立移动端入口直接部署。
- H5 页面存在初始化详情请求、列表请求或路由参数驱动请求时，`useEffect` 依赖数组只保留真正影响请求参数的值，例如 `roomId`、筛选条件、分页；不要把 `useEffectEvent` 返回的请求函数直接放进依赖数组。

## 推荐模式

### 1. 目录结构

```
frontend/
├── h5.html                    # H5 入口 HTML
├── vite.config.h5.ts          # H5 独立构建配置
├── src/
│   ├── h5.tsx                 # H5 入口 TSX
│   ├── h5_pages/              # H5 页面目录
│   │   ├── attendance/
│   │   │   ├── scan-attendance-result-page.tsx
│   │   │   └── scan-attendance-result-page.css
│   │   └── ...
│   └── ...
```

### 2. H5 HTML 入口 (h5.html)

```html
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>页面标题</title>
</head>
<body>
<div id="root"></div>
<script type="module" src="/src/h5.tsx"></script>
</body>
</html>
```

### 3. H5 TSX 入口 (h5.tsx)

```tsx
import {StrictMode} from "react";
import {createRoot, Root} from "react-dom/client";
import {BrowserRouter, Navigate, Route, Routes} from "react-router-dom";
import SomePage from "@/h5_pages/domain/some-page";
import {AntdConfig} from "@va/ui";
import "./plugins/assets";

let app: Root | null = null;
const isDev = import.meta.env.DEV;
const h5Basename = isDev ? "/<plugin-name>/h5" : "/child/<plugin-name>/h5";

async function setupApp(props: any = {}) {
    const {container} = props;
    app = createRoot(
        container
            ? container.querySelector("#root")
            : document.querySelector("#root"),
    );
    app.render(
        <StrictMode>
            <AntdConfig>
                <BrowserRouter basename={h5Basename}>
                    <Routes>
                        <Route path="/" element={<div>首页</div>}/>
                        <Route path="/some-path" element={<SomePage/>}/>
                        <Route path="*" element={<Navigate to="/" replace/>}/>
                    </Routes>
                </BrowserRouter>
            </AntdConfig>
        </StrictMode>,
    );
}

void setupApp({});
```

### 4. Vite H5 配置 (vite.config.h5.ts)

```typescript
import {defineConfig} from 'vite'
import {fileURLToPath, URL} from "node:url";
import {include, Inspect, removeConsole, setupAutoImport, setupUnocss, setupUnPluginIcon} from "@va/build";
import path from "node:path";
import process from "node:process";
import react from '@vitejs/plugin-react';

const APP_NAME = "<plugin-name>";
const H5_APP_NAME = `${APP_NAME}/h5`;
const API_PROXY_TARGET = "http://<backend-host>:<port>";

export default defineConfig((_c) => {
  const localIconPath = path.join(process.cwd(), 'src/assets/svg-icon');
  return {
    base: process.env.NODE_ENV==='production' ? `/child/${H5_APP_NAME}/` : '/',
    build: {
      chunkSizeWarningLimit: 2000,
      emptyOutDir: true,
      rollupOptions: {
        input: {
          main: path.resolve(__dirname, 'h5.html'),
        }
      },
      outDir: `./dist/${H5_APP_NAME}`,
    },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
        '~': fileURLToPath(new URL('./', import.meta.url))
      }
    },
    esbuild: {
      treeShaking: true,
    },
    css: {
      modules: {
        localsConvention: 'camelCase'
      }
    },
    plugins: [
      {
        name: "h5-dev-history-fallback",
        configureServer(server) {
          server.middlewares.use((req, _res, next) => {
            const url = req.url || "";
            if (url === `/${H5_APP_NAME}` || url.startsWith(`/${H5_APP_NAME}/`)) {
              req.url = "/h5.html";
            }
            next();
          });
        },
      },
      react(),
      Inspect(),
      removeConsole(),
      setupAutoImport(),
      setupUnocss(localIconPath),
      ...setupUnPluginIcon(localIconPath, `__SVG_${APP_NAME}_ICON_LOCAL__`),
    ],
    optimizeDeps: {include},
    preview: {
      port: 9725
    },
    server: {
      open: `/${H5_APP_NAME}`,
      headers: {
        'Access-Control-Allow-Origin': '*'
      },
      historyApiFallback: true,
      cors: true,
      proxy: {
        "/api": {
          target: API_PROXY_TARGET,
          changeOrigin: true,
          secure: false
        }
      },
      port: 17001,
      origin: 'http://localhost:17001',
      warmup: {
        clientFiles: ['./h5.html', './src/{pages,components}/*']
      }
    }
  }
})
```

### 5. 路由 basename 规则

- 开发环境：`/<plugin-name>/h5`
- 生产环境：`/child/<plugin-name>/h5`

示例：
```typescript
const h5Basename = isDev ? "/attendance/h5" : "/child/attendance/h5";
```

### 6. 构建产物路径

- H5 产物输出到 `frontend/dist/<plugin-name>/h5/`
- 后端 `build.gradle` 的 `processResources` 会将 `../frontend/dist` 复制到 `web` 目录
- 最终访问路径：`/child/<plugin-name>/h5/`

### 7. H5 请求触发模式

- H5 页面初始化请求优先采用“`useEffect` 负责依赖收敛，函数体内直接调用请求函数”的模式。
- 若请求函数需要在“首次进入页面”和“提交动作后刷新”两处复用，再根据用途选择：
  `useEffectEvent`：只在 effect 或事件处理中调用，不参与 `useEffect` 依赖比较。
  `useCallback`：当函数本身确实要参与依赖比较或被多个回调稳定复用时再使用。
- 排查 H5 页面循环请求时，先检查是否存在“`useEffect` 依赖包含函数引用 -> 请求后 `setState` -> render -> effect 再次触发”的链路，再区分是否只是开发环境 `StrictMode` 的双调用。

## 禁止做法

- 不要把 H5 页面放在 `src/pages/` 目录下（该目录保留给 qiankun 微前端页面）。
- 不要给 H5 配置添加 qiankun 插件（H5 是独立入口，不走微前端）。
- 不要把 H5 和主应用构建配置混在一起，必须独立为 `vite.config.h5.ts`。
- 不要修改 H5 输出目录后不检查后端的资源复制逻辑。
- 不要把 `useEffectEvent` 封装出来的请求函数放进 H5 页面初始化 `useEffect` 的依赖数组，导致详情页、列表页在 `setState` 后反复发请求。

## 开发或评审检查点

- [ ] H5 入口文件是否遵循命名规范（`h5.html`、`h5.tsx`）
- [ ] H5 页面是否放在 `h5_pages/` 目录下
- [ ] `vite.config.h5.ts` 是否独立配置，与主应用分离
- [ ] H5 构建产物目录是否与后端 `processResources` 复制逻辑匹配
- [ ] H5 路由 basename 是否区分开发和生产环境
- [ ] H5 是否未引入 qiankun 插件
- [ ] H5 页面是否适配移动端 viewport
- [ ] H5 页面的初始化请求是否只由路由参数、筛选条件、分页等必要依赖驱动
- [ ] 若使用了 `useEffectEvent` 封装请求函数，是否避免把返回函数加入 `useEffect` 依赖数组

## 仓库参考位置

- `frontend/h5.html`
- `frontend/src/h5.tsx`
- `frontend/src/h5_pages/`
- `frontend/src/h5_pages/door/room-detail-page.tsx`
- `frontend/vite.config.h5.ts`
- `backend/build.gradle` (processResources 任务)

## 开发命令

```bash
# 开发模式启动 H5
pnpm dev:h5

# 构建 H5
pnpm build:h5
```

需要在 `package.json` 中添加对应 scripts：
```json
{
  "scripts": {
    "dev:h5": "vite --config vite.config.h5.ts",
    "build:h5": "tsc && vite build --config vite.config.h5.ts"
  }
}
```
