import { buildLocationSearchParams } from "@/shared/url/location-search";

const URL_TOKEN_KEYS = ["access_token", "token"] as const;
const TOKEN_COOKIE_KEY = "token";
const TOKEN_COOKIE_OPTIONS = "path=/; SameSite=Lax";

export const syncUrlToken = (locationValue: string) => {
  const params = buildLocationSearchParams(locationValue);
  for (const key of URL_TOKEN_KEYS) {
    const value = params.get(key)?.trim();
    if (value) {
      document.cookie = `${TOKEN_COOKIE_KEY}=${encodeURIComponent(value)}; ${TOKEN_COOKIE_OPTIONS}`;
      return;
    }
  }
};
