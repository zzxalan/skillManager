import type { RouteObject } from "react-router-dom";
import Home from "@/pages/home";
import NotFound from "@/pages/_builtin/404";

export const APP_NAME = "__APP_NAME__";

export const pages = {
  Home,
};

export const staticPages = {
  NotFound,
};

export const routes: RouteObject[] = [
  {
    index: true,
    element: <Home />,
  },
  {
    path: "*",
    element: <NotFound />,
  },
];
