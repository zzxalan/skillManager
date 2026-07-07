import { createFlatRequest } from "@vlian/utils";
import { message } from "antd";
import { getStoreToken } from "@va/core/store";
import { buildLocationSearchParams } from "@/shared/url/location-search";

type BackendResponse = {
  code?: string | number;
  msg?: string;
  data?: unknown;
};

function getPluginIdFromUrl(url?: string): string {
  if (!url) return "__APP_NAME__";
  const match = url.match(/\/api\/([^/]+)/);
  return match?.[1] || "__APP_NAME__";
}

function getTokenFromRuntime(): string {
  const searchParams = buildLocationSearchParams(window.location.href);
  const searchValue =
    searchParams.get("token") ||
    searchParams.get("access_token") ||
    searchParams.get("authorization");
  if (searchValue) {
    return searchValue.replace(/^Bearer\s+/i, "");
  }
  const raw = window.localStorage.getItem("access_token");
  if (!raw) return "";
  try {
    const parsed = JSON.parse(raw);
    if (typeof parsed === "string") {
      return parsed.replace(/^Bearer\s+/i, "");
    }
  } catch {
    return raw.replace(/^Bearer\s+/i, "");
  }
  return "";
}

export const request = createFlatRequest<BackendResponse, Record<string, never>>(
  { baseURL: "", headers: {}, timeout: 30000 },
  {
    isBackendSuccess(response: { data?: BackendResponse }) {
      const code = String(response?.data?.code ?? "");
      return code === "0" || code === "200";
    },
    async onRequest(config: any) {
      const enableTokenAuth = config?.enableTokenAuth !== false;
      let token: string | undefined;
      if (enableTokenAuth) {
        const storeToken = await getStoreToken();
        token = typeof storeToken === "string" ? storeToken.replace(/^Bearer\s+/i, "") : "";
        if (!token) token = getTokenFromRuntime();
      }
      Object.assign(config.headers, {
        Authorization: token ? `Bearer ${token}` : undefined,
        token,
        PluginId: getPluginIdFromUrl(config?.url as string),
      });
      return config;
    },
    onError(error: { response?: { data?: { msg?: string } }; message?: string }) {
      message.error(error?.response?.data?.msg || error?.message || "请求失败");
    },
    async onBackendFail(response: { data?: { msg?: string } }) {
      message.error(response?.data?.msg || "请求失败");
    },
    transformBackendResponse(response: { data?: BackendResponse }) {
      return response?.data?.data;
    },
  },
);
