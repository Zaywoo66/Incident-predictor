import React, { useState, useEffect } from "react";
import { fetchPrediction, getMockPoints } from "./api";
import RiskGauge from "./components/RiskGauge";
import MetricsChart from "./components/MetricsChart";
import ShapChart from "./components/ShapChart";

const IS_MOCK = import.meta.env.VITE_USE_MOCK === "true";

export default function App() {
  const [prediction, setPrediction] = useState(null);
  const [points, setPoints] = useState(getMockPoints());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let interval = null;

    async function load() {
      try {
        setLoading(true);
        setError(null);
        const result = await fetchPrediction(points, 5);
        setPrediction(result);
      } catch (err) {
        setError(err.message || "Failed to fetch prediction");
      } finally {
        setLoading(false);
      }
    }

    load();

    if (!IS_MOCK) {
      interval = setInterval(load, 15000);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, []);

  if (loading && !prediction) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block w-10 h-10 border-4 border-slate-600 border-t-blue-500 rounded-full animate-spin mb-4" />
          <p className="text-slate-400 text-lg">Loading prediction…</p>
        </div>
      </div>
    );
  }

  if (error && !prediction) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center p-8 bg-slate-800/60 rounded-2xl backdrop-blur max-w-md">
          <div className="text-red-400 text-5xl mb-4">⚠</div>
          <h2 className="text-xl font-semibold text-red-400 mb-2">Connection Error</h2>
          <p className="text-slate-400">{error}</p>
          <p className="text-slate-500 text-sm mt-4">
            Make sure the API is running or set VITE_USE_MOCK=true
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 md:p-10">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-white">
          🛡️ Incident Predictor
        </h1>
        <p className="text-slate-400 mt-1">
          Real-time risk monitoring dashboard
          {IS_MOCK && (
            <span className="ml-2 text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded">
              MOCK MODE
            </span>
          )}
        </p>
        {error && (
          <p className="text-red-400 text-sm mt-2">⚠ Update failed: {error}</p>
        )}
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <RiskGauge probability={prediction.probability} />
        </div>
        <div className="lg:col-span-2">
          <MetricsChart points={points} />
        </div>
      </div>

      <div className="mt-6">
        <ShapChart shapValues={prediction.shap_values} />
      </div>
    </div>
  );
}
