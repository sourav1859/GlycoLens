"use client";

import { useEffect, useState } from "react";

import { ForecastChart } from "../../components/ForecastChart";
import { fetchDemoForecast } from "../../lib/forecast-api";
import { ForecastResponse } from "../../types/forecast";

export function ForecastDemo() {
  const [data, setData] = useState<ForecastResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    fetchDemoForecast(controller.signal)
      .then((forecast) => {
        setData(forecast);
        setError(null);
      })
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) {
          setError(reason instanceof Error ? reason.message : "Forecast service is unavailable");
        }
      });
    return () => controller.abort();
  }, [attempt]);

  const retry = () => {
    setData(null);
    setError(null);
    setAttempt((value) => value + 1);
  };

  if (error) {
    return (
      <section className="forecast-card status-card" role="alert">
        <h2>Forecast unavailable</h2>
        <p>{error}</p>
        <button type="button" onClick={retry}>
          Try again
        </button>
      </section>
    );
  }
  if (!data) {
    return (
      <section className="forecast-card status-card" aria-live="polite" aria-busy="true">
        <h2>Loading synthetic forecast</h2>
        <p>Connecting to the local GlycoLens API…</p>
      </section>
    );
  }
  return <ForecastChart data={data} />;
}
