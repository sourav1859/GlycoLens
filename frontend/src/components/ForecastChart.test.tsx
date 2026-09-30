import { render, screen } from "@testing-library/react";

import { ForecastChart } from "./ForecastChart";
import { ForecastResponse } from "../types/forecast";


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
  summary: {
    minute_30_mg_dl: 125,
    minute_60_mg_dl: 131,
    minute_120_mg_dl: 143,
  },
  notice: "Synthetic demonstration only. Not treatment guidance.",
};


test("renders an accessible forecast, uncertainty band, summaries, and safety notice", () => {
  render(<ForecastChart data={fixture} />);

  expect(
    screen.getByRole("img", { name: /Synthetic two-hour glucose forecast/ }),
  ).toBeVisible();
  expect(screen.getByTestId("forecast-band")).toBeInTheDocument();
  expect(screen.getByText("Observed history")).toBeVisible();
  expect(screen.getByText("Median forecast")).toBeVisible();
  expect(screen.getByText("q10–q90 interval")).toBeVisible();
  expect(screen.getByText("125 mg/dL")).toBeVisible();
  expect(screen.getByText("131 mg/dL")).toBeVisible();
  expect(screen.getByText("143 mg/dL")).toBeVisible();
  expect(screen.getByText(/Synthetic demonstration only/)).toBeVisible();
});
