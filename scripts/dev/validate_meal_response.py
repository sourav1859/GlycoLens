"""Opt-in synthetic model sensitivity/performance; no cloud, paid calls or refit."""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
from time import perf_counter


ROOT = Path(__file__).resolve().parents[2]


def synthetic_context(history="flat"):
    origin = datetime(2026, 1, 2, 12, tzinfo=timezone.utc)
    slope = {"flat": 0, "falling": 0.08, "rising": -0.08}[history]
    cgm = [
        dict(
            recorded_at=(origin - timedelta(minutes=5 * i)).isoformat(),
            glucose_mg_dl=120 + slope * i,
            source="simulation",
        )
        for i in range(287, -1, -1)
    ]
    insulin = [
        dict(
            recorded_at=(origin - timedelta(hours=6)).isoformat(),
            event_type="basal",
            units=1.2,
            source_unit="U/h",
            insulin_kind="R",
        ),
        dict(
            recorded_at=(origin - timedelta(minutes=30)).isoformat(),
            event_type="bolus",
            units=2,
            source_unit="U",
            insulin_kind="R",
        ),
    ]
    metadata = dict(
        scenario="lightgbm_warmup_48h_v1",
        event_coverage_start=(origin - timedelta(hours=24)).isoformat(),
        event_coverage_end=origin.isoformat(),
        meal_events=[dict(recorded_at=(origin - timedelta(minutes=180)).isoformat(), carbs_g=30)],
    )
    return origin, cgm, insulin, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-models", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.allow_models:
        print("DRY RUN: --allow-models required; no model execution")
        return
    import numpy as np
    import psutil
    import torch
    from backend.app.services.inference.application import build_model_request
    from backend.app.services.inference.registry import resolve_model
    from research.models.adapters.metabonet_tabular import request_features

    torch.set_num_threads(2)
    os.environ["HF_HUB_OFFLINE"] = "1"
    fixture_bytes = (ROOT / "config/meal-response-validation.json").read_bytes()
    fixture = json.loads(fixture_bytes)
    targets = json.loads((ROOT / "config/webapp-validation.json").read_text())
    process = psutil.Process()
    peak = process.memory_info().rss
    rows = []
    runs = []
    inputs = {}
    summaries = {}
    for key in ("chronos", "lightgbm"):
        cold = perf_counter()
        spec = resolve_model(key)
        spec.adapter()
        cold_seconds = perf_counter() - cold

        def predict(nutrients, history):
            nonlocal peak
            origin, cgm, insulin, metadata = synthetic_context(history)
            request = build_model_request(
                spec,
                dict(recorded_at=origin.isoformat(), **nutrients),
                cgm[-spec.history_samples :],
                insulin,
                metadata,
            )
            start = perf_counter()
            result = spec.predict(request)
            elapsed = perf_counter() - start
            peak = max(peak, process.memory_info().rss)
            points = np.array([result.quantile_values(q) for q in (0.1, 0.5, 0.9)])
            assert (
                points.shape == (3, 24)
                and np.isfinite(points).all()
                and np.all(np.diff(points, axis=0) >= 0)
            )
            snapshot = dict(
                history=[
                    dict(at=p.timestamp.isoformat(), value=p.value) for p in request.target_history
                ],
                past=[
                    dict(
                        name=s.name,
                        unit=s.unit,
                        points=[dict(at=p.timestamp.isoformat(), value=p.value) for p in s.points],
                    )
                    for s in request.past_covariates
                ],
                known=[
                    dict(
                        name=s.name,
                        unit=s.unit,
                        points=[dict(at=p.timestamp.isoformat(), value=p.value) for p in s.points],
                    )
                    for s in request.known_covariates
                ],
            )
            digest = hashlib.sha256(
                json.dumps(snapshot, sort_keys=True, allow_nan=False).encode()
            ).hexdigest()
            inputs[digest] = snapshot
            runs.append(
                dict(
                    model=key,
                    history=history,
                    input_sha256=digest,
                    quantile_levels=[0.1, 0.5, 0.9],
                    quantiles_mg_dl=points.tolist(),
                    elapsed_seconds=elapsed,
                    status="PASS",
                )
            )
            return points, request, elapsed

        def contrast(curve, base):
            delta = curve - base
            return dict(
                max_endpoint_delta_mg_dl=float(np.max(np.abs(delta))),
                max_median_delta_mg_dl=float(np.max(np.abs(delta[1]))),
                mean_median_delta_mg_dl=float(np.mean(np.abs(delta[1]))),
                horizon_changes={
                    str(minute): dict(
                        lower_delta_mg_dl=float(delta[0, index]),
                        median_delta_mg_dl=float(delta[1, index]),
                        upper_delta_mg_dl=float(delta[2, index]),
                        interval_width_delta_mg_dl=float(
                            (curve[2, index] - curve[0, index]) - (base[2, index] - base[0, index])
                        ),
                    )
                    for minute, index in ((30, 5), (60, 11), (120, 23))
                },
            )

        repeats = []
        for history in fixture["histories"]:
            for name, profile in fixture["profiles"].items():
                base, _, _ = predict(profile, history)
                for portion in fixture["portions"]:
                    nutrients = {field: value * portion for field, value in profile.items()}
                    curve, request, _ = predict(nutrients, history)
                    known = {
                        series.name: series.points[0].value for series in request.known_covariates
                    }
                    assert abs(known["meal_carbohydrates"] - profile["carbs_g"] * portion) < 1e-10
                    rows.append(
                        dict(
                            model=key,
                            history=history,
                            profile=name,
                            portion=portion,
                            **contrast(curve, base),
                        )
                    )
            base = fixture["single_nutrient_base"]
            original, request, _ = predict(base, history)
            for _ in range(fixture["identical_repeats"]):
                repeated, _, _ = predict(base, history)
                error = float(np.max(np.abs(original - repeated)))
                repeats.append(error)
                assert error <= fixture["repeat_tolerance_mg_dl"]
            for field in ("carbs_g", "protein_g", "fat_g", "fiber_g"):
                changed, other, _ = predict({**base, field: base[field] * 2}, history)
                delta = float(np.max(np.abs(changed - original)))
                if key == "lightgbm" and field != "carbs_g":
                    assert np.array_equal(
                        request_features(request, history_hours=24, profile="events")[0],
                        request_features(other, history_hours=24, profile="events")[0],
                        equal_nan=True,
                    )
                    assert delta <= fixture["repeat_tolerance_mg_dl"]
                rows.append(
                    dict(
                        model=key,
                        history=history,
                        single_nutrient=field,
                        **contrast(changed, original),
                    )
                )
        palak = []
        for portion in (1, 2.5):
            curve, _, _ = predict(
                {field: value * portion for field, value in fixture["palak_paneer_100g"].items()},
                "flat",
            )
            palak.append(curve)
        warm = [
            predict(fixture["single_nutrient_base"], "flat")[2]
            for _ in range(fixture["warm_benchmark_requests"])
        ]
        summaries[key] = dict(
            model_identity=spec.identity,
            cold_load_seconds=cold_seconds,
            warm_samples=len(warm),
            warm_median_seconds=float(np.median(warm)),
            warm_p95_seconds=float(np.percentile(warm, 95)),
            identical_repeat_max_error_mg_dl=max(repeats),
            palak_100_250_max_endpoint_delta_mg_dl=float(np.max(np.abs(palak[0] - palak[1]))),
            sensitivity_rows=sum(r["model"] == key for r in rows),
            flat_contrast_count=sum(
                r["model"] == key
                and r["max_endpoint_delta_mg_dl"] <= fixture["repeat_tolerance_mg_dl"]
                for r in rows
            ),
        )
        assert cold_seconds <= targets["cold_readiness_seconds_target"]
        assert (
            summaries[key]["warm_p95_seconds"] <= targets["warm_single_forecast_p95_seconds_target"]
        )
    total = psutil.virtual_memory().total
    cgroup = Path("/sys/fs/cgroup/memory.max")
    if cgroup.is_file() and cgroup.read_text().strip().isdigit():
        total = min(total, int(cgroup.read_text().strip()))
    report = dict(
        status="PASS",
        fixture_version=fixture["version"],
        fixture_sha256=hashlib.sha256(fixture_bytes).hexdigest(),
        models=summaries,
        rows=rows,
        runs=runs,
        input_snapshots=inputs,
        requested_predictions=len(runs),
        completed_predictions=len(runs),
        process_peak_sampled_rss_bytes=peak,
        memory_denominator_bytes=total,
        memory_fraction=peak / total,
        scope="Model-only cold/warm inference and handcrafted input sensitivity; excludes cloud/HTTP/simulator latency and is not accuracy evidence",
        cpu_threads=2,
        failures=0,
        cloud_requests=0,
        paid_calls=0,
        weights_fitted=False,
        calibration_refitted=False,
        reserved_cohort_rows=0,
    )
    assert report["memory_fraction"] <= targets["peak_host_memory_fraction_target"]
    from scripts.dev.summarize_meal_response import summarize

    report["engineering_checks"] = "PASS"
    report["capability_assessment"] = summarize(report)
    report["status"] = (
        "PARTIAL"
        if any(
            value["status"] == "FAIL_INVARIANT"
            for value in report["capability_assessment"]["models"].values()
        )
        else "ENGINEERING_PASS"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: v
                for k, v in report.items()
                if k not in {"rows", "models", "runs", "input_snapshots"}
            }
        )
    )
    print(
        json.dumps(
            {
                key: {k: v for k, v in value.items() if k != "model_identity"}
                for key, value in summaries.items()
            }
        )
    )


if __name__ == "__main__":
    main()
