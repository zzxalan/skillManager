import "dotenv/config";

import { defineConfig, devices } from "@playwright/test";

import { smartEnv } from "./helpers/env";
import { authStatePath, reportPaths, testRoot } from "./helpers/paths";

export default defineConfig({
  testDir: `${testRoot}/tests`,
  outputDir: reportPaths.artifacts,
  fullyParallel: false,
  workers: Number(process.env.PLAYWRIGHT_WORKERS ?? "1"),
  retries: process.env.CI ? 1 : 0,
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  reporter: [
    ["html", { outputFolder: reportPaths.html, open: "never" }],
    ["json", { outputFile: reportPaths.json }],
    ["junit", { outputFile: reportPaths.junit }],
  ],
  use: {
    baseURL: smartEnv.frontendUrl,
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    {
      name: "setup",
      testMatch: /.*\.setup\.ts/,
    },
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        storageState: authStatePath,
      },
      dependencies: ["setup"],
    },
  ],
});
