export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "system-ui", margin: 0 }}>
        <header style={{ padding: 16, borderBottom: "1px solid #eee" }}>
          <strong>Infra Insight MVP</strong>
          <nav style={{ marginTop: 8, display: "flex", gap: 12 }}>
            <a href="/">Overview</a>
            <a href="/findings">Findings</a>
          </nav>
        </header>
        {children}
      </body>
    </html>
  );
}
