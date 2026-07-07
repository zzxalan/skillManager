export const PLUGIN_ID = "__APP_NAME__";

function resolveContextPath(pathname: string): string {
  const childAppIndex = pathname.indexOf("/child/");
  if (childAppIndex >= 0) {
    return pathname.slice(0, childAppIndex);
  }
  return "";
}

function buildPluginApiPrefix(): string {
  if (typeof window === "undefined") {
    return `/api/${PLUGIN_ID}`;
  }
  const contextPath = resolveContextPath(window.location.pathname);
  return `${contextPath}/api/${PLUGIN_ID}`;
}

export const URL_PLUGIN_PREFIX = buildPluginApiPrefix();
