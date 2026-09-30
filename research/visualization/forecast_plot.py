"""Render relative-time forecast figures without identifiers or absolute timestamps."""

from __future__ import annotations

from pathlib import Path

from research.models.adapters import ForecastExample, ForecastResult


def save_forecast_plot(
    example: ForecastExample,
    result: ForecastResult,
    output_path: Path,
    *,
    include_held_out_target: bool = False,
) -> dict[str, object]:
    """Save a research-only PNG and return a non-sensitive shape summary."""

    try:
        import matplotlib

        matplotlib.use("Agg")
        from matplotlib import pyplot as plt
    except ImportError as error:
        raise RuntimeError("Install the pinned plotting dependency group") from error

    request = example.request
    if result.forecast_timestamps != request.forecast_timestamps:
        raise ValueError("forecast result does not match the example time grid")

    history_minutes = tuple(
        (point.timestamp - request.context_end).total_seconds() / 60
        for point in request.target_history
    )
    forecast_minutes = tuple(
        (timestamp - request.context_end).total_seconds() / 60
        for timestamp in result.forecast_timestamps
    )
    q10 = result.quantile_values(0.1)
    q50 = result.quantile_values(0.5)
    q90 = result.quantile_values(0.9)

    figure, axis = plt.subplots(figsize=(9, 5.2), constrained_layout=True)
    axis.plot(
        history_minutes,
        tuple(point.value for point in request.target_history),
        color="#16697a",
        linewidth=2.2,
        label="Observed CGM history",
    )
    axis.fill_between(
        forecast_minutes,
        q10,
        q90,
        color="#f4a261",
        alpha=0.25,
        label="Forecast q10–q90",
    )
    axis.plot(
        forecast_minutes,
        q50,
        color="#e76f51",
        linewidth=2.4,
        label="Forecast median (q50)",
    )
    if include_held_out_target:
        target_minutes = tuple(
            (point.timestamp - request.context_end).total_seconds() / 60
            for point in example.target.points
        )
        axis.plot(
            target_minutes,
            tuple(point.value for point in example.target.points),
            color="#2a9d8f",
            linewidth=2,
            linestyle="--",
            label="Held-out actual CGM",
        )

    axis.axvline(0, color="#334155", linewidth=1.2, linestyle=":", label="Forecast start")
    axis.set_title("Chronos-2 two-hour forecast — research view")
    axis.set_xlabel("Minutes relative to forecast start")
    axis.set_ylabel("Glucose (mg/dL)")
    axis.grid(alpha=0.2)
    axis.legend(loc="best", frameon=False)
    figure.text(
        0.5,
        0.005,
        "Research and education only — not treatment or insulin-dosing guidance.",
        ha="center",
        fontsize=8,
        color="#475569",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=160, metadata={"Title": "GlycoLens research forecast"})
    plt.close(figure)
    return {
        "history_points": len(history_minutes),
        "forecast_points": len(forecast_minutes),
        "held_out_target_included": include_held_out_target,
        "uses_relative_minutes": True,
        "contains_participant_identifier": False,
        "contains_absolute_timestamp": False,
    }
