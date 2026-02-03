import { fetchJSON } from "@/lib/api";

export default async function FindingDetail({ params }: { params: { id: string } }) {
  const f = await fetchJSON<any>(`/findings/${params.id}`);

  if (f?.error === "not_found") {
    return <main style={{ padding: 24 }}><h1>Not found</h1></main>;
  }

  return (
    <main style={{ padding: 24 }}>
      <a href="/findings">← Back</a>
      <h1 style={{ marginBottom: 6 }}>{`P${f.severity}`} — {f.title}</h1>
      <div style={{ color: "#666", marginBottom: 16 }}>
        {f.type} · confidence {f.confidence}% · created {new Date(f.created_at).toLocaleString()}
      </div>

      {f.summary && (
        <section style={{ border: "1px solid #eee", borderRadius: 12, padding: 16, marginBottom: 16 }}>
          <h2 style={{ marginTop: 0 }}>Summary</h2>
          <p style={{ margin: 0 }}>{f.summary}</p>
        </section>
      )}

      <section style={{ border: "1px solid #eee", borderRadius: 12, padding: 16, marginBottom: 16 }}>
        <h2 style={{ marginTop: 0 }}>Evidence</h2>
        <pre style={{ whiteSpace: "pre-wrap", margin: 0 }}>{JSON.stringify(f.evidence, null, 2)}</pre>
      </section>

      <section style={{ border: "1px solid #eee", borderRadius: 12, padding: 16 }}>
        <h2 style={{ marginTop: 0 }}>Remediation</h2>
        <pre style={{ whiteSpace: "pre-wrap", margin: 0 }}>{JSON.stringify(f.remediation, null, 2)}</pre>
      </section>
    </main>
  );
}
