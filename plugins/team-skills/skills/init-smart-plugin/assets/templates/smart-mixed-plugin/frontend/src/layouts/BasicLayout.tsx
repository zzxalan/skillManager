import { Outlet } from "react-router-dom";

type BasicLayoutProps = {
  micro: string;
  title: string;
};

function BasicLayout({ micro, title }: BasicLayoutProps) {
  return (
    <main className="plugin-shell" data-micro={micro}>
      <header className="plugin-header">
        <h1 className="plugin-title">{title}</h1>
      </header>
      <section className="plugin-main">
        <Outlet />
      </section>
    </main>
  );
}

export default BasicLayout;
