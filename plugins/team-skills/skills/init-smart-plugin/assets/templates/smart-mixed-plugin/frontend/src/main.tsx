import { StrictMode } from "react";
import { createRoot, Root } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";
import "./plugins/assets";
import {
  renderWithQiankun,
  qiankunWindow,
} from "vite-plugin-qiankun/dist/helper";
import { AntdConfig } from "@va/ui";

let app: Root | null = null;
async function setupApp(props: any = {}) {
  const { container } = props;
  app = createRoot(
    container
      ? container.querySelector("#root")
      : document.querySelector("#root"),
  );

  app.render(
    <StrictMode>
      <AntdConfig>
        <App props={props} />
      </AntdConfig>
    </StrictMode>,
  );
}

// some code
renderWithQiankun({
  update(): void | Promise<void> {
    return undefined;
  },
  mount(props) {
    console.log("mount");
    setupApp(props);
  },
  bootstrap() {
    console.log("bootstrap");
  },
  unmount() {
    if (app) {
      app.unmount();
      app = null;
    }
  },
});

if (!qiankunWindow.__POWERED_BY_QIANKUN__) {
  setupApp({});
}
