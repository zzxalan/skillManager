import { StrictMode } from "react";
import { createRoot, Root } from "react-dom/client";
import {
  qiankunWindow,
  renderWithQiankun,
} from "vite-plugin-qiankun/dist/helper";
import App from "./App";
import "./index.css";

type QiankunProps = {
  container?: Element | Document;
  targetPath?: string;
};

let app: Root | null = null;

function resolveRoot(container?: Element | Document): Element {
  const root = container
    ? container.querySelector("#root")
    : document.querySelector("#root");
  if (!root) {
    throw new Error("缺少 #root 节点");
  }
  return root;
}

function setupApp(props: QiankunProps = {}) {
  app = createRoot(resolveRoot(props.container));
  app.render(
    <StrictMode>
      <App props={props} />
    </StrictMode>,
  );
}

renderWithQiankun({
  bootstrap() {
    return undefined;
  },
  mount(props) {
    setupApp(props as QiankunProps);
  },
  update() {
    return undefined;
  },
  unmount() {
    if (app) {
      app.unmount();
      app = null;
    }
  },
});

if (!qiankunWindow.__POWERED_BY_QIANKUN__) {
  setupApp();
}
