import React from "react";

/**
 * Circular risk gauge showing incident probability as a percentage.
 * Color: green (<0.4), yellow (<0.7), red (>=0.7).
 */
export default function RiskGauge({ probability }) {
  let color;
  let label;
  if (probability < 0.4) {
    color = "#22c55e";
    label = "Low";
  } else if (probability < 0.7) {
    color = "#eab308";
    label = "Medium";
  } else {
    color = "#ef4444";
    label = "High";
  }

  const percent = Math.round(probability * 100);
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (probability * circumference);

  return (
    <div className="flex flex-col items-center justify-center p-6 bg-slate-800/60 rounded-2xl backdrop-blur">
      <h2 className="text-lg font-semibold text-slate-300 mb-4">Incident Risk</h2>
      <div className="relative w-44 h-44">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 160 160">
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            stroke="#334155"
            strokeWidth="12"
          />
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 0.6s ease, stroke 0.3s ease" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold" style={{ color }}>
            {percent}%
          </span>
          <span className="text-sm text-slate-400 mt-1">{label}</span>
        </div>
      </div>
    </div>
  );
}
