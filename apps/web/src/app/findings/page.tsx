import { fetchJSON } from "@/lib/api";

type Finding = { id: string; type: string; severity: number; title: string; confidence: number; created_at: string };

export default async function FindingsPage() {
  const findings = await fetchJSON<Finding[]>("/findings?limit=200");

  return (
    <main style={{ padding: 24 }}>
      <h1>Findings</h1>
      <p style={{ color: "#555" }}>Click a finding to view evidence and remediation.</p>

      <div style={{ display: "grid", gap: 12 }}>
        {findings.map(f => (
          <a key={f.id} href={`/findings/${f.id}`} style={{ textDecoration: "none", color: "inherit" }}>
            <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 14 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
                <strong>{`P${f.severity}`} — {f.title}</strong>
                <span style={{ color: "#666" }}>{f.confidence}%</span>
              </div>
              <div style={{ marginTop: 6, color: "#666", fontSize: 13 }}>
                {f.type} · {new Date(f.created_at).toLocaleString()}
              </div>
            </div>
          </a>
        ))}
      </div>
    </main>
  );
}
