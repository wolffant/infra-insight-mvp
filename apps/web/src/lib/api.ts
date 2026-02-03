export async function fetchJSON<T>(path: string): Promise<T> {
  // Use Docker service name for server-side fetches, localhost for client-side
  const base = typeof window === "undefined"
    ? (process.env.API_BASE_URL || "http://api:8000")
    : (process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000");
  const res = await fetch(`${base}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
