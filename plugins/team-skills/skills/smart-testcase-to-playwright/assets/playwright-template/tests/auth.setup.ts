import fs from "node:fs/promises";
import path from "node:path";

import { expect, test as setup } from "@playwright/test";

import { smartEnv } from "../helpers/env";
import { authStatePath } from "../helpers/paths";
import { injectSmartToken, resolveSmartToken } from "../helpers/smart-auth";

setup("准备 smart 登录态", async ({ page, request }) => {
  const token = await resolveSmartToken(request);
  await injectSmartToken(page.context(), token);

  await page.goto(smartEnv.frontendUrl, { waitUntil: "domcontentloaded" });

  const tokenCookie = (await page.context().cookies()).find(
    (cookie) => cookie.name === "token",
  );
  expect(tokenCookie?.value).toBeTruthy();

  await fs.mkdir(path.dirname(authStatePath), { recursive: true });
  await page.context().storageState({ path: authStatePath });
});
