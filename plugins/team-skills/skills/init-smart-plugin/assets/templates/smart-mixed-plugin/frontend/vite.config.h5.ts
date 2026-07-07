import { defineConfig } from "vite";
import { fileURLToPath, URL } from "node:url";
import { include, Inspect, removeConsole, setupAutoImport, setupUnocss, setupUnPluginIcon } from "@va/build";
import path from "node:path";
import process from "node:process";
import react from "@vitejs/plugin-react";

const APP_NAME = "__APP_NAME__";
const H5_APP_NAME = `${APP_NAME}/h5`;

export default defineConfig(() => {
  const localIconPath = path.join(process.cwd(), "src/assets/svg-icon");
  return {
    base: process.env.NODE_ENV === "production" ? `/child/${H5_APP_NAME}/` : "/",
    build: {
      chunkSizeWarningLimit: 2000,
      emptyOutDir: true,
      rollupOptions: {
        input: {
          main: path.resolve(__dirname, "h5.html"),
        },
      },
      outDir: "./dist/h5",
    },
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
        "~": fileURLToPath(new URL("./", import.meta.url)),
      },
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
    optimizeDeps: { include },
    server: {
      open: `/${H5_APP_NAME}`,
      headers: { "Access-Control-Allow-Origin": "*" },
      host: true,
      cors: true,
      port: 17014,
      origin: "http://localhost:17014",
      warmup: {
        clientFiles: ["./h5.html", "./src/h5_pages/**/*"],
      },
    },
  };
});
