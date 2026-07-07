import { theme } from "antd";
import { useEffect } from "react";

export function H5AntdMobileThemeBridge() {
  const { token } = theme.useToken();

  useEffect(() => {
    const rootStyle = document.documentElement.style;
    rootStyle.setProperty("--adm-color-primary", token.colorPrimary);
    rootStyle.setProperty("--adm-color-warning", token.colorWarning);
    return () => {
      rootStyle.removeProperty("--adm-color-primary");
      rootStyle.removeProperty("--adm-color-warning");
    };
  }, [token.colorPrimary, token.colorWarning]);

  return null;
}
