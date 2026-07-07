import React, { useMemo } from "react";
import { BlankLayout, useRouter } from "@va/core/router";
import {
  createBrowserRouter,
  createMemoryRouter,
  RouterProvider,
  type RouteObject,
} from "react-router-dom";
import { qiankunWindow } from "vite-plugin-qiankun/dist/helper";
import { fetchRoutes } from "@/hooks/useRouter";
import { layouts, pages, staticPages, staticRoutes } from "@/router/router-import";
import { RouteErrorBoundary } from "@va/ui";

const APP_NAME = "__APP_NAME__";
const APP_TITLE = "__DISPLAY_NAME__";

function App({ props = {} }: { props?: { targetPath?: string } }) {
  const { router } = useRouter({
    pages,
    staticPages,
    layouts,
    staticRoutes,
    fetchRoutes,
  });

  const routerWithErrorBoundary = useMemo(
    () =>
      router.map((route) => ({
        ...route,
        errorElement: route.errorElement ?? <RouteErrorBoundary />,
      })) as RouteObject[],
    [router],
  );

  const basenameConf = {
    basename: qiankunWindow.__POWERED_BY_QIANKUN__ ? `/${APP_NAME}` : "/",
  };

  return (
    <RouterProvider
      router={
        props.targetPath
          ? createMemoryRouter(routerWithErrorBoundary, {
              ...basenameConf,
              initialEntries: [props.targetPath],
            })
          : createBrowserRouter(
              [
                {
                  element: <BlankLayout micro={APP_NAME} />,
                  errorElement: <RouteErrorBoundary />,
                  children: routerWithErrorBoundary,
                  loader: () => ({
                    name: APP_NAME,
                    isMicroApp: true,
                    title: APP_TITLE,
                  }),
                },
              ],
              basenameConf,
            )
      }
    />
  );
}

export default App;
