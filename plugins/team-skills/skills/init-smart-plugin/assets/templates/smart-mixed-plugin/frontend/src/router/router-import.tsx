import BlankLayout from "@/layouts/BasicLayout";
import type { RouteItem } from "@va/components";
import type { ComponentType, ReactNode } from "react";

const convert = (module: { default: ComponentType }) => {
  const { default: Component, ...rest } = module;
  return { ...rest, Component };
};

export const layouts: Record<string, ReactNode> = {
  BasicLayout: <BlankLayout />,
};

export const staticPages: Record<string, () => Promise<{ Component: ComponentType }>> = {
  NotFound: () => import("@/pages/_builtin/404").then(convert),
};

export const pages: Record<string, () => Promise<{ Component: ComponentType }>> = {
  Home: () => import("@/pages/home").then(convert),
};

export const staticRoutes: RouteItem[] = [
  {
    path: "*",
    name: "NotFound",
    mark: "NotFound",
    layout: false,
  },
];

export const routes = { ...staticPages, ...pages };
