export type BackendResponse<T = unknown> = {
  code: string | number;
  msg?: string;
  data: T;
};

export type RequestInstanceState = Record<string, never>;
