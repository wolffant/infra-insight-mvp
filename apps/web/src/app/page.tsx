import { fetchJSON } from "@/lib/api";
import TrendsChart from "./trends";

type TrendRow = { day: string; p0: number; p1: number; p2: number; p3: number };

export default async function Home() {
  const trends = await fetchJSON<TrendRow[]>("/findings/trends/daily?days=14");
  const weekly = await fetchJSON<any>("/reports/weekly");

  return (
    <main style={{ padding: 24 }}>
      <h1>Overview</h1>

      <section style={{ padding: 16, border: "1px solid #eee", borderRadius: 12, marginBottom: 16 }}>
        <h2 style={{ marginTop: 0 }}>Weekly summary</h2>
        <pre style={{ whiteSpace: "pre-wrap", margin: 0 }}>{JSON.stringify(weekly.summary, null, 2)}</pre>
      </section>

      <section style={{ padding: 16, border: "1px solid #eee", borderRadius: 12 }}>
        <h2 style={{ marginTop: 0 }}>Findings trends (last 14 days)</h2>
        <TrendsChart data={trends} />
      </section>
    </main>
  );
}
