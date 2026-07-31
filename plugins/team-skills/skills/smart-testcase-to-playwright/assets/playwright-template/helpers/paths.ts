import path from "node:path";
import { fileURLToPath } from "node:url";

export const testRoot = fileURLToPath(new URL("..", import.meta.url));
export const authStatePath = path.join(testRoot, ".auth", "user.json");

export const reportPaths = {
  html: path.join(testRoot, "playwright-report"),
  json: path.join(testRoot, "test-results", "results.json"),
  junit: path.join(testRoot, "test-results", "junit.xml"),
  artifacts: path.join(testRoot, "test-results", "artifacts"),
};
