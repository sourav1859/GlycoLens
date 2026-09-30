import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import { fetchDemoForecast } from "../../lib/forecast-api";
import { ForecastResponse } from "../../types/forecast";
import { ForecastDemo } from "./ForecastDemo";


vi.mock("../../lib/forecast-api", () => ({ fetchDemoForecast: vi.fn() }));

const fixture: ForecastResponse = {
  schema_version: "1.0",
  data_mode: "synthetic_demo",
  model_id: "synthetic-demo",
  model_version: "1.0",
  context_configuration: "cgm_only",
  unit: "mg/dL",
  history: Array.from({ length: 24 }, (_, index) => ({
    minute: -115 + index * 5,
    value_mg_dl: 100 + index,
  })),
  forecast: Array.from({ length: 24 }, (_, index) => ({
    minute: 5 + index * 5,
    q10_mg_dl: 110 + index,
    q50_mg_dl: 120 + index,
    q90_mg_dl: 130 + index,
  })),
  summary: { minute_30_mg_dl: 125, minute_60_mg_dl: 131, minute_120_mg_dl: 143 },
  notice: "Synthetic demonstration only. Not treatment guidance.",
};

const mockedFetch = vi.mocked(fetchDemoForecast);

beforeEach(() => {
  mockedFetch.mockReset();
});

test("shows loading and then renders API data", async () => {
  mockedFetch.mockResolvedValue(fixture);
  render(<ForecastDemo />);

  expect(screen.getByText("Loading synthetic forecast")).toBeVisible();
  expect(
    await screen.findByRole("img", { name: /Synthetic two-hour glucose forecast/ }),
  ).toBeVisible();
});

test("shows a recoverable error and retries", async () => {
  mockedFetch.mockRejectedValueOnce(new Error("Forecast service is unavailable"));
  mockedFetch.mockResolvedValueOnce(fixture);
  const user = userEvent.setup();
  render(<ForecastDemo />);

  expect(await screen.findByRole("alert")).toHaveTextContent("Forecast service is unavailable");
  await user.click(screen.getByRole("button", { name: "Try again" }));
  await waitFor(() => expect(mockedFetch).toHaveBeenCalledTimes(2));
  expect(
    await screen.findByRole("img", { name: /Synthetic two-hour glucose forecast/ }),
  ).toBeVisible();
});
