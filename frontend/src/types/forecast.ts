export type HistoryPoint = {
  minute: number;
  value_mg_dl: number;
};

export type ForecastBandPoint = {
  minute: number;
  q10_mg_dl: number;
  q50_mg_dl: number;
  q90_mg_dl: number;
};

export type ForecastResponse = {
  schema_version: "1.0";
  data_mode: "synthetic_demo";
  model_id: string;
  model_version: string;
  context_configuration: "cgm_only";
  unit: "mg/dL";
  history: HistoryPoint[];
  forecast: ForecastBandPoint[];
  summary: {
    minute_30_mg_dl: number;
    minute_60_mg_dl: number;
    minute_120_mg_dl: number;
  };
  notice: string;
};

function isNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

export function isForecastResponse(value: unknown): value is ForecastResponse {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<ForecastResponse>;
  if (
    candidate.schema_version !== "1.0" ||
    candidate.data_mode !== "synthetic_demo" ||
    candidate.context_configuration !== "cgm_only" ||
    candidate.unit !== "mg/dL" ||
    typeof candidate.model_id !== "string" ||
    typeof candidate.model_version !== "string" ||
    typeof candidate.notice !== "string" ||
    !Array.isArray(candidate.history) ||
    candidate.history.length < 2 ||
    !Array.isArray(candidate.forecast) ||
    candidate.forecast.length < 1 ||
    !candidate.summary
  ) {
    return false;
  }
  const historyValid = candidate.history.every(
    (point) => isNumber(point.minute) && isNumber(point.value_mg_dl) && point.minute <= 0,
  );
  const forecastValid = candidate.forecast.every(
    (point) =>
      isNumber(point.minute) &&
      isNumber(point.q10_mg_dl) &&
      isNumber(point.q50_mg_dl) &&
      isNumber(point.q90_mg_dl) &&
      point.minute > 0 &&
      point.q10_mg_dl <= point.q50_mg_dl &&
      point.q50_mg_dl <= point.q90_mg_dl,
  );
  const historyOrdered = candidate.history.every(
    (point, index) => index === 0 || point.minute > candidate.history![index - 1].minute,
  );
  const forecastOrdered = candidate.forecast.every(
    (point, index) => index === 0 || point.minute > candidate.forecast![index - 1].minute,
  );
  const medianByMinute = new Map(
    candidate.forecast.map((point) => [point.minute, point.q50_mg_dl]),
  );
  return (
    historyValid &&
    forecastValid &&
    historyOrdered &&
    forecastOrdered &&
    isNumber(candidate.summary.minute_30_mg_dl) &&
    isNumber(candidate.summary.minute_60_mg_dl) &&
    isNumber(candidate.summary.minute_120_mg_dl) &&
    medianByMinute.get(30) === candidate.summary.minute_30_mg_dl &&
    medianByMinute.get(60) === candidate.summary.minute_60_mg_dl &&
    medianByMinute.get(120) === candidate.summary.minute_120_mg_dl
  );
}
