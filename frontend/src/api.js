import { MOCK_RESPONSE, MOCK_POINTS } from "./mockData";

/**
 * Fetch prediction from the API or return mock data.
 * @param {Array} points - array of metric point objects
 * @param {number} windowMinutes - prediction window in minutes
 * @returns {Promise<{probability: number, shap_values: Object}>}
 */
export async function fetchPrediction(points, windowMinutes) {
  if (import.meta.env.VITE_USE_MOCK === "true") {
    await new Promise((resolve) => setTimeout(resolve, 300));
    return MOCK_RESPONSE;
  }

  const url = import.meta.env.VITE_API_URL + "/predict";
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ points, window_minutes: windowMinutes }),
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

/**
 * Return mock metric points for initial state / mock mode.
 * @returns {Array}
 */
export function getMockPoints() {
  return MOCK_POINTS;
}
