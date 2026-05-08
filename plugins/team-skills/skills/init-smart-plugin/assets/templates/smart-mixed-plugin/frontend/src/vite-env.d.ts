/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_DOOR_REMOTE_MOCK?: string
}

declare global {
  interface Window {
    __POWERED_BY_QIANKUN__: any;
    __INJECTED_PUBLIC_PATH_BY_QIANKUN__: any;
    __webpack_public_path__: any;
  }
}
