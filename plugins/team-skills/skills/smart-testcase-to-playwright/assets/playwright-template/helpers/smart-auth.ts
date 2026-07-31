import type { APIRequestContext, BrowserContext } from "@playwright/test";

import { smartEnv } from "./env";

interface SmartLoginResponse {
  code?: number | string;
  msg?: string;
  data?: {
    token?: string;
    violations?: {
      valid?: boolean;
    };
  };
}

async function requestToken(
  request: APIRequestContext,
  endpoint: string,
  username: string,
  password: string,
): Promise<{ token?: string; error?: string }> {
  const captcha = `playwright-${Date.now()}`;
  const response = await request.post(endpoint, {
    data: {
      username,
      password,
      captchaKey: captcha,
      captchaCode: captcha,
      rememberMe: true,
    },
  });

  let payload: SmartLoginResponse;
  try {
    payload = (await response.json()) as SmartLoginResponse;
  } catch {
    return { error: `${endpoint} 返回了非 JSON 响应（HTTP ${response.status()}）` };
  }

  if (payload.data?.violations?.valid === false) {
    return { error: `${endpoint} 登录态不可用：${payload.msg ?? "账号需要处理密码或安全策略"}` };
  }

  if (payload.data?.token) {
    return { token: payload.data.token };
  }

  return {
    error: `${endpoint} 登录失败：code=${payload.code ?? "unknown"} msg=${payload.msg ?? "unknown"}`,
  };
}

export async function resolveSmartToken(request: APIRequestContext): Promise<string> {
  if (smartEnv.token) {
    return smartEnv.token;
  }

  if (!smartEnv.backendUrl || !smartEnv.username || !smartEnv.password) {
    throw new Error(
      "未设置 SMART_TOKEN 时，必须提供 SMART_BACKEND_URL、SMART_USERNAME 和 SMART_PASSWORD",
    );
  }

  const errors: string[] = [];
  for (const path of ["/api/user/login", "/user/login"]) {
    const result = await requestToken(
      request,
      `${smartEnv.backendUrl}${path}`,
      smartEnv.username,
      smartEnv.password,
    );
    if (result.token) {
      return result.token;
    }
    if (result.error) {
      errors.push(result.error);
    }
  }

  throw new Error(`smart 登录失败：${errors.join("；")}`);
}

export async function injectSmartToken(
  context: BrowserContext,
  token: string,
): Promise<void> {
  const frontendUrl = new URL(smartEnv.frontendUrl);
  await context.addCookies([
    {
      name: "token",
      value: token,
      url: frontendUrl.origin,
      httpOnly: false,
      secure: frontendUrl.protocol === "https:",
      sameSite: "Lax",
    },
  ]);
}
