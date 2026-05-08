import {defineConfig} from 'vite'
import {fileURLToPath, URL} from "node:url";
import {include, Inspect, removeConsole, setupAutoImport, setupUnocss, setupUnPluginIcon} from "@va/build";
import path from "node:path";
import process from "node:process";
import react from '@vitejs/plugin-react';
import qiankun from 'vite-plugin-qiankun';

const APP_NAME = "__APP_NAME__";

export default defineConfig(() => {
  const localIconPath = path.join(process.cwd(), 'src/assets/svg-icon');
  return {
    base: process.env.NODE_ENV==='production' ? `/child/${APP_NAME}` : '/',
    // publicDir: process.env.NODE_ENV==='production' ? `/child/${APP_NAME}/` : '/',
    build: {
      chunkSizeWarningLimit: 2000,
      emptyOutDir: true,
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
        localsConvention: 'camelCase' as const // 允许 camelCase 方式访问类名
      }
    },
    plugins: [
      react(),
      Inspect(),
      removeConsole(),
      setupAutoImport(),
      setupUnocss(localIconPath),
      ...setupUnPluginIcon(localIconPath, `__SVG_${APP_NAME}_ICON_LOCAL__`),
      qiankun(APP_NAME, {
        useDevMode: true
      })

    ],
    optimizeDeps: {include},
    // 预览
    preview: {
      port: 9725
    },
    server: {
      headers: {
        'Access-Control-Allow-Origin': '*'
      },
      cors: true,
      hmr: false,
      port: 7014,
      origin: '//localhost:7014',
      warmup: {
        clientFiles: ['./index.html', './src/{pages,components}/*']
      }
    }
  }
})
