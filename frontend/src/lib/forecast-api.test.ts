import { afterEach, vi } from "vitest";

import { fetchDemoForecast } from "./forecast-api";


const validPayload = {
  schema_version: "1.0",
  data_mode: "synthetic_demo",
  model_id: "synthetic-demo",
  model_version: "1.0",
  context_configuration: "cgm_only",
  unit: "mg/dL",
  history: [
    { minute: -5, value_mg_dl: 120 },
    { minute: 0, value_mg_dl: 122 },
  ],
  forecast: Array.from({ length: 24 }, (_, index) => ({
    minute: (index + 1) * 5,
    q10_mg_dl: 110 + index,
    q50_mg_dl: 120 + index,
    q90_mg_dl: 130 + index,
  })),
  summary: { minute_30_mg_dl: 125, minute_60_mg_dl: 131, minute_120_mg_dl: 143 },
  notice: "Synthetic demonstration only.",
};

afterEach(() => {
  vi.unstubAllGlobals();
});

test("fetches and validates the demo contract", async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    json: async () => validPayload,
  });
  vi.stubGlobal("fetch", fetchMock);

  const result = await fetchDemoForecast();

  expect(result.model_id).toBe("synthetic-demo");
  expect(fetchMock).toHaveBeenCalledWith(
    "http://127.0.0.1:8000/api/v1/forecasts/demo",
    expect.objectContaining({ method: "GET" }),
  );
});

test("rejects HTTP failures and malformed quantiles", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValueOnce({ ok: false, status: 503 }).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        ...validPayload,
        forecast: validPayload.forecast.map((point, index) =>
          index === 0 ? { ...point, q10_mg_dl: 999 } : point,
        ),
      }),
    }),
  );

  await expect(fetchDemoForecast()).rejects.toThrow("HTTP 503");
  await expect(fetchDemoForecast()).rejects.toThrow("invalid response");
});
