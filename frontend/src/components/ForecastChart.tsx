import { ForecastResponse } from "../types/forecast";
import { useEffect, useRef } from "react";

type ChartPoint = { x: number; y: number };

const WIDTH = 760;
const HEIGHT = 390;
const PADDING = { top: 28, right: 24, bottom: 52, left: 58 };

function polyline(points: ChartPoint[]): string {
  return points.map((point) => `${point.x.toFixed(2)},${point.y.toFixed(2)}`).join(" ");
}

export function ForecastChart({ data, unit="mg/dL" }: { data: ForecastResponse; unit?:"mg/dL"|"mmol/L" }) {
  const calibrated = data.interval_kind === "calibrated_marginal_80";
  const intervalLabel = calibrated ? "Calibrated marginal 80% interval" : "q10–q90 interval";
  const visibleHistory = data.history.slice(-24);
  const format=(value:number)=>unit==="mmol/L"?(value/18.0182).toFixed(1):Math.round(value);
  const chartContainer = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const container = chartContainer.current;
    if (container) container.scrollLeft = container.scrollWidth - container.clientWidth;
  }, [data]);
  const allMinutes = [...visibleHistory.map((point) => point.minute), ...data.forecast.map((point) => point.minute)];
  const allValues = [
    ...visibleHistory.map((point) => point.value_mg_dl),
    ...data.forecast.flatMap((point) => [point.q10_mg_dl, point.q90_mg_dl]),
  ];
  const minMinute = Math.min(...allMinutes);
  const maxMinute = Math.max(...allMinutes);
  const rawMinValue = Math.min(...allValues);
  const rawMaxValue = Math.max(...allValues);
  const valuePadding = Math.max(10, (rawMaxValue - rawMinValue) * 0.12);
  const minValue = Math.floor((rawMinValue - valuePadding) / 10) * 10;
  const maxValue = Math.ceil((rawMaxValue + valuePadding) / 10) * 10;
  const innerWidth = WIDTH - PADDING.left - PADDING.right;
  const innerHeight = HEIGHT - PADDING.top - PADDING.bottom;
  const scaleX = (minute: number) =>
    PADDING.left + ((minute - minMinute) / (maxMinute - minMinute)) * innerWidth;
  const scaleY = (value: number) =>
    PADDING.top + ((maxValue - value) / (maxValue - minValue)) * innerHeight;

  const historyPoints = visibleHistory.map((point) => ({
    x: scaleX(point.minute),
    y: scaleY(point.value_mg_dl),
  }));
  const medianPoints = data.forecast.map((point) => ({
    x: scaleX(point.minute),
    y: scaleY(point.q50_mg_dl),
  }));
  const upperPoints = data.forecast.map((point) => ({
    x: scaleX(point.minute),
    y: scaleY(point.q90_mg_dl),
  }));
  const lowerPoints = [...data.forecast]
    .reverse()
    .map((point) => ({ x: scaleX(point.minute), y: scaleY(point.q10_mg_dl) }));
  const bandPoints = polyline([...upperPoints, ...lowerPoints]);
  const xTicks = [-120, -60, 0, 30, 60, 90, 120].filter(
    (minute) => minute >= minMinute && minute <= maxMinute,
  );
  const yTicks = [minValue, Math.round((minValue + maxValue) / 2), maxValue];

  return (
    <section className="forecast-card" aria-labelledby="forecast-heading">
      <div className="forecast-heading-row">
        <div>
          <p className="eyebrow">{data.data_mode === "simulated" ? calibrated ? "Simulated patient · LightGBM research forecast" : "Simulated patient · Pretrained model forecast" : "Synthetic API demonstration"}</p>
          <h2 id="forecast-heading">Two-hour glucose forecast</h2>
        </div>
        <span className="model-badge">{data.model_id}</span>
      </div>

      <div className="chart-wrap" ref={chartContainer} tabIndex={0} aria-label="Glucose chart; scroll horizontally to inspect history and forecast">
        <svg
          viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
          role="img"
          aria-labelledby="forecast-chart-title forecast-chart-description"
        >
          <title id="forecast-chart-title">{data.data_mode==="simulated"?"Virtual-patient two-hour glucose forecast":"Synthetic two-hour glucose forecast"}</title>
          <desc id="forecast-chart-description">
            Observed glucose history followed by a median forecast with a shaded {intervalLabel}.
            Values are simulated and are not treatment guidance.
          </desc>
          {yTicks.map((value) => (
            <g key={value}>
              <line
                x1={PADDING.left}
                x2={WIDTH - PADDING.right}
                y1={scaleY(value)}
                y2={scaleY(value)}
                className="chart-grid"
              />
              <text x={PADDING.left - 10} y={scaleY(value) + 4} className="chart-label" textAnchor="end">
                {format(value)}
              </text>
            </g>
          ))}
          {xTicks.map((minute) => (
            <g key={minute}>
              <line
                x1={scaleX(minute)}
                x2={scaleX(minute)}
                y1={PADDING.top}
                y2={HEIGHT - PADDING.bottom}
                className={minute === 0 ? "chart-now-line" : "chart-grid"}
              />
              <text
                x={scaleX(minute)}
                y={HEIGHT - PADDING.bottom + 25}
                className="chart-label"
                textAnchor="middle"
              >
                {minute === 0 ? "now" : minute}
              </text>
            </g>
          ))}
          <text x={16} y={18} className="chart-axis-title">{unit}</text>
          <text x={WIDTH / 2} y={HEIGHT - 10} className="chart-axis-title" textAnchor="middle">
            Minutes relative to forecast start
          </text>
          <polygon points={bandPoints} className="forecast-band" data-testid="forecast-band" />
          <polyline points={polyline(historyPoints)} className="history-line" />
          <polyline points={polyline(medianPoints)} className="forecast-line" />
        </svg>
      </div>

      <div className="chart-legend" aria-label="Chart legend">
        <span><i className="legend-line history" />Observed history</span>
        <span><i className="legend-line forecast" />Median forecast</span>
        <span><i className="legend-band" />{intervalLabel}</span>
      </div>

      <dl className="forecast-summary">
        <div><dt>30 min</dt><dd>{format(data.summary.minute_30_mg_dl)} {unit}</dd></div>
        <div><dt>60 min</dt><dd>{format(data.summary.minute_60_mg_dl)} {unit}</dd></div>
        <div><dt>120 min</dt><dd>{format(data.summary.minute_120_mg_dl)} {unit}</dd></div>
      </dl>
      <p className="safety-notice">{data.notice}</p>
      {data.provenance&&<details><summary>Model inputs and version</summary><p className="small">{data.provenance.inputs.join("; ")}. Used {data.provenance.history_samples} history readings; chart shows the latest two hours.</p><p className="small model-version">Model version: {data.model_version}<br/>Features: {data.provenance.feature_version}{calibrated&&<><br/>Calibration: {data.provenance.calibration_sha256}</>}</p></details>}
      <details><summary>Forecast data table</summary><div className="table-scroll" tabIndex={0} role="region" aria-label="Forecast values; scroll for all columns"><table><caption>{intervalLabel} and median ({unit})</caption><thead><tr><th>Minutes</th><th>{calibrated?"Lower band":"q10"}</th><th>Median</th><th>{calibrated?"Upper band":"q90"}</th></tr></thead><tbody>{data.forecast.map(p=><tr key={p.minute}><th>+{p.minute}</th>{[p.q10_mg_dl,p.q50_mg_dl,p.q90_mg_dl].map((n,i)=><td key={i}>{format(n)}</td>)}</tr>)}</tbody></table></div></details>
    </section>
  );
}
