import React, { useMemo } from "react";
import { BlankLayout, useRouter } from "@va/core/router";
import {
  layouts,
  pages,
  staticPages,
  staticRoutes,
} from "@/router/router-import";
import {
  createBrowserRouter,
  createMemoryRouter,
  RouterProvider,
  RouteObject,
} from "react-router-dom";
import { fetchRoutes } from "@/hooks/useRouter";
import { qiankunWindow } from "vite-plugin-qiankun/dist/helper";
import { RouteErrorBoundary } from "@va/ui";

const APP_NAME = "__APP_NAME__";
const APP_TITLE = "__DISPLAY_NAME__";


/**
 * 递归为所有路由添加错误边界
 */
const addErrorBoundaryToRoutes = (routes: RouteObject[]): RouteObject[] => {
  return routes.map((route) => {
    const newRoute: RouteObject = {
      ...route,
      errorElement: route.errorElement || <RouteErrorBoundary />,
    };
    
    if (route.children) {
      newRoute.children = addErrorBoundaryToRoutes(route.children);
    }
    
    return newRoute;
  });
};

function App({ props }) {
  const { router } = useRouter({
    pages,
    staticPages,
    layouts,
    staticRoutes,
    fetchRoutes,
  });

  // 为所有路由添加错误边界
  const routerWithErrorBoundary = useMemo(() => {
    return addErrorBoundaryToRoutes(router);
  }, [router]);

  const basenameConf = {
    basename: qiankunWindow.__POWERED_BY_QIANKUN__ ? "/"+APP_NAME : "/",
  };

  return (
    <>
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
                { ...basenameConf },
              )
        }
      ></RouterProvider>
    </>
  );
}

export default App;
