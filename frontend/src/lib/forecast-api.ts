import { ForecastResponse, isForecastResponse } from "../types/forecast";

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

export async function fetchDemoForecast(signal?: AbortSignal): Promise<ForecastResponse> {
  const baseUrl = (process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_BASE_URL).replace(
    /\/$/,
    "",
  );
  const response = await fetch(`${baseUrl}/api/v1/forecasts/demo`, {
    method: "GET",
    headers: { Accept: "application/json" },
    signal,
  });
  if (!response.ok) {
    throw new Error(`Forecast service returned HTTP ${response.status}`);
  }
  const payload: unknown = await response.json();
  if (!isForecastResponse(payload)) {
    throw new Error("Forecast service returned an invalid response");
  }
  return payload;
}
