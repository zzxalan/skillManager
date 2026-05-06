import { fileURLToPath, URL } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import qiankun from "vite-plugin-qiankun";

const APP_NAME = "__APP_NAME__";

export default defineConfig((_c) => {

  return {
    base: process.env.NODE_ENV === "production" ? `/child/${APP_NAME}` : "/",
    build: {
      chunkSizeWarningLimit: 2000,
      emptyOutDir: true,
    },
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
        "~": fileURLToPath(new URL("./", import.meta.url)),
      },
    },
    plugins: [
      react(),
      qiankun(APP_NAME, {
        useDevMode: true,
      }),
    ],
    preview: {
      port: Number(process.env.VITE_PREVIEW_PORT) || 9725,
    },
    server: {
      headers: {
        "Access-Control-Allow-Origin": "*",
      },
      cors: true,
      hmr: false,
      port: Number(process.env.VITE_PORT) || 5173,
    },
  };
});
