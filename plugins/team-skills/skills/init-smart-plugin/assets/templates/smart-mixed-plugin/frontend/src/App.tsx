import { useMemo } from "react";
import {
  createBrowserRouter,
  createMemoryRouter,
  RouterProvider,
  type RouteObject,
} from "react-router-dom";
import { qiankunWindow } from "vite-plugin-qiankun/dist/helper";
import BasicLayout from "@/layouts/BasicLayout";
import { routes } from "@/router/router-import";

const APP_NAME = "__APP_NAME__";
const APP_TITLE = "__DISPLAY_NAME__";

type AppProps = {
  props?: {
    targetPath?: string;
  };
};

const rootRoutes: RouteObject[] = [
  {
    element: <BasicLayout micro={APP_NAME} title={APP_TITLE} />,
    children: routes,
    loader: () => ({
      name: APP_NAME,
      isMicroApp: true,
      title: APP_TITLE,
    }),
  },
];

function App({ props = {} }: AppProps) {
  const basename = qiankunWindow.__POWERED_BY_QIANKUN__ ? `/${APP_NAME}` : "/";
  const router = useMemo(() => {
    if (props.targetPath) {
      return createMemoryRouter(rootRoutes, {
        basename,
        initialEntries: [props.targetPath],
      });
    }
    return createBrowserRouter(rootRoutes, { basename });
  }, [basename, props.targetPath]);

  return <RouterProvider router={router} />;
}

export default App;
