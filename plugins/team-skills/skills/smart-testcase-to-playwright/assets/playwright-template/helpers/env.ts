function readRequiredEnv(name: string): string {
  const value = process.env[name]?.trim();
  if (!value) {
    throw new Error(`缺少环境变量 ${name}`);
  }
  return value;
}

function readOptionalEnv(name: string): string | undefined {
  const value = process.env[name]?.trim();
  return value || undefined;
}

export const smartEnv = {
  frontendUrl: readRequiredEnv("SMART_FRONTEND_URL").replace(/\/$/, ""),
  backendUrl: readOptionalEnv("SMART_BACKEND_URL")?.replace(/\/$/, ""),
  username: readOptionalEnv("SMART_USERNAME"),
  password: readOptionalEnv("SMART_PASSWORD"),
  token: readOptionalEnv("SMART_TOKEN"),
};
