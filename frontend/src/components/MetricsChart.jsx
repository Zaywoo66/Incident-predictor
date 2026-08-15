import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

/**
 * Time-series chart for CPU, RAM, and latency metrics.
 * CPU (blue #3b82f6) and RAM (green #22c55e) use the left Y-axis.
 * Latency (orange #f97316) uses the right Y-axis.
 */
export default function MetricsChart({ points }) {
  const data = points.map((p) => ({
    ...p,
    time: p.timestamp.slice(11, 19),
  }));

  return (
    <div className="p-6 bg-slate-800/60 rounded-2xl backdrop-blur">
      <h2 className="text-lg font-semibold text-slate-300 mb-4">Infrastructure Metrics</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="time" stroke="#94a3b8" tick={{ fontSize: 12 }} />
          <YAxis yAxisId="left" stroke="#94a3b8" tick={{ fontSize: 12 }} />
          <YAxis yAxisId="right" orientation="right" stroke="#94a3b8" tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1e293b",
              border: "1px solid #334155",
              borderRadius: "8px",
              color: "#e2e8f0",
            }}
          />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="cpu"
            stroke="#3b82f6"
            name="CPU %"
            strokeWidth={2}
            dot={false}
          />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="ram"
            stroke="#22c55e"
            name="RAM %"
            strokeWidth={2}
            dot={false}
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="latency"
            stroke="#f97316"
            name="Latency ms"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
