import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { HashRouter, Navigate, Route, Routes } from "react-router-dom";
import { getAuthInfo, setAuthInfo } from "@va/core/store";
import { fetchUserPermissionList } from "@va/services";
import { AntdConfig } from "@va/ui";
import { H5AntdMobileThemeBridge } from "@/h5_pages/mobile-theme-bridge";
import H5HomePage from "@/h5_pages/home";
import { syncUrlToken } from "@/shared/auth/syncUrlToken";
import "antd-mobile/es/global";
import "@/h5_pages/styles.css";

async function bootstrapAuth() {
  if (getAuthInfo() == null) {
    setAuthInfo([]);
  }

  try {
    const { data } = await fetchUserPermissionList();
    setAuthInfo(Array.isArray(data) ? data : []);
  } catch {
    if (getAuthInfo() == null) {
      setAuthInfo([]);
    }
  }
}

async function bootstrap() {
  syncUrlToken(window.location.href);
  await bootstrapAuth();

  createRoot(document.getElementById("root")!).render(
    <StrictMode>
      <AntdConfig>
        <H5AntdMobileThemeBridge />
        <HashRouter>
          <Routes>
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="/home" element={<H5HomePage />} />
            <Route path="*" element={<Navigate to="/home" replace />} />
          </Routes>
        </HashRouter>
      </AntdConfig>
    </StrictMode>,
  );
}

void bootstrap();
