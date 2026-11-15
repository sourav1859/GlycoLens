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
  schema_version: "1.0" | "2.0";
  data_mode: "synthetic_demo" | "simulated";
  model_id: string;
  model_version: string;
  context_configuration: "cgm_only" | "cgm_insulin" | "cgm_insulin_carbohydrates" | "cgm_insulin_nutrition";
  unit: "mg/dL";
  history: HistoryPoint[];
  forecast: ForecastBandPoint[];
  summary: {
    minute_30_mg_dl: number;
    minute_60_mg_dl: number;
    minute_120_mg_dl: number;
  };
  notice: string;
  interval_kind?: "model_quantiles" | "calibrated_marginal_80";
  provenance?: {
    model_key: "chronos" | "lightgbm";
    model_id: string;
    model_version: string;
    feature_version: string;
    bundle_sha256: string | null;
    calibration_sha256: string | null;
    history_samples: 24 | 288;
    interval_kind: "model_quantiles" | "calibrated_marginal_80";
    inputs: string[];
  } | null;
};

function isNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

export function isForecastResponse(value: unknown): value is ForecastResponse {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<ForecastResponse>;
  if (
    !["1.0", "2.0"].includes(candidate.schema_version ?? "") ||
    !["synthetic_demo", "simulated"].includes(candidate.data_mode ?? "") ||
    !["cgm_only", "cgm_insulin", "cgm_insulin_carbohydrates", "cgm_insulin_nutrition"].includes(candidate.context_configuration ?? "") ||
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
  if (!candidate.history.every(p=>p&&typeof p==="object") || !candidate.forecast.every(p=>p&&typeof p==="object")) return false;
  if (candidate.schema_version === "2.0") {
    const p = candidate.provenance;
    if (!p || !["chronos","lightgbm"].includes(p.model_key) || p.model_id !== candidate.model_id || p.model_version !== candidate.model_version || p.interval_kind !== candidate.interval_kind || !Array.isArray(p.inputs) || !p.inputs.length || !p.inputs.every(v=>typeof v==="string") || typeof p.feature_version!=="string") return false;
    const tabular = p.model_key === "lightgbm";
    if (p.history_samples !== (tabular ? 288 : 24) || candidate.history.length !== p.history_samples || candidate.forecast.length !== 24 || candidate.context_configuration !== (tabular ? "cgm_insulin_carbohydrates" : "cgm_insulin_nutrition") || p.interval_kind !== (tabular ? "calibrated_marginal_80" : "model_quantiles")) return false;
    if (tabular && (!/^[a-f0-9]{64}$/.test(p.bundle_sha256??"") || !/^[a-f0-9]{64}$/.test(p.calibration_sha256??"") || !p.model_version.endsWith(p.bundle_sha256!))) return false;
    if (!candidate.history.every((p,i)=>p.minute===-5*(candidate.history!.length-1-i)) || !candidate.forecast.every((p,i)=>p.minute===5*(i+1))) return false;
  }
  const historyValid = candidate.history.every(
    (point) => isNumber(point.minute) && isNumber(point.value_mg_dl) && point.value_mg_dl >=20 && point.value_mg_dl<=600 && point.minute <= 0,
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
  const boundsValid = candidate.forecast.every(p=>candidate.schema_version==="1.0"
    ? [p.q10_mg_dl,p.q50_mg_dl,p.q90_mg_dl].every(v=>v>=20&&v<=600)
    : p.q10_mg_dl>=-99999&&p.q90_mg_dl<=99999&&p.q50_mg_dl>0&&p.q50_mg_dl<=1000);
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
    boundsValid &&
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
