"use client";

import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";

export default function TrendsChart({ data }: { data: any[] }) {
  if (!data || data.length === 0) {
    return <div style={{ color: "#666" }}>No data yet. Run ingestion + detectors.</div>;
  }
  return (
    <div style={{ width: "100%", height: 320 }}>
      <ResponsiveContainer>
        <LineChart data={data}>
          <CartesianGrid />
          <XAxis dataKey="day" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="p0" />
          <Line type="monotone" dataKey="p1" />
          <Line type="monotone" dataKey="p2" />
          <Line type="monotone" dataKey="p3" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
