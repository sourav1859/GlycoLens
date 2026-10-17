"""Bounded fixed live scenario; public responses omit internal synthetic insulin values."""

import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
from uuid import UUID, uuid5

from fastapi import HTTPException

from backend.app.db.client import UserSession, database_call
from research.simulation.adapter import PYMGIPSIM_COMMIT, PyMgipsimResult, run_pymgipsim_scenario


ROOT = Path(__file__).resolve().parents[4]
SCENARIO_LOCK = Lock()


def live_scenario(session: UserSession, *, replay: bool = False):
    if not SCENARIO_LOCK.acquire(blocking=False):
        raise HTTPException(429, "A simulator scenario is already running; retry shortly")
    try:
        directory = ROOT / "artifacts/simulation/app"
        directory.mkdir(parents=True, exist_ok=True)
        output, internal = directory / "scenario.json", directory / "context.json"
        if replay:
            if not output.is_file() or not internal.is_file():
                raise HTTPException(
                    404, "No reviewed replay is available; run the live scenario first"
                )
            result = PyMgipsimResult.from_json(output)
        else:
            result = run_pymgipsim_scenario(
                source_directory=ROOT / ".cache/pymgipsim-source",
                python_executable=ROOT / ".cache/pymgipsim-venv/Scripts/python.exe",
                output_json=output,
                internal_context_output=internal,
            )
        context = json.loads(internal.read_text(encoding="utf-8"))
        if context["upstream_commit"] != PYMGIPSIM_COMMIT:
            raise ValueError("unreviewed internal context")
        origin = int(context["origin_minute"])
        if not 120 <= origin <= 1200 or origin % 5:
            raise ValueError("invalid simulation origin")
        epoch = datetime(2026, 1, 1, tzinfo=timezone.utc)
        rows = [
            {
                "user_id": session.user_id,
                "recorded_at": (epoch + timedelta(minutes=p.minute)).isoformat(),
                "glucose_mg_dl": p.glucose_mg_dl,
                "source": "simulation",
            }
            for p in result.trajectory
            if p.minute <= origin
        ]
        database_call(
            session,
            "cgm_readings?on_conflict=user_id,recorded_at,source",
            method="POST",
            payload=rows,
        )
        database_call(session, "insulin_events?source=eq.simulation", method="DELETE")
        insulin = []
        for event in context["insulin_events"]:
            at, value = float(event["minute"]), float(event["source_value"])
            if not math.isfinite(value) or value < 0 or not 0 <= at <= origin:
                raise ValueError("invalid synthetic insulin context")
            insulin.append(
                {
                    "user_id": session.user_id,
                    "recorded_at": (epoch + timedelta(minutes=at)).isoformat(),
                    "event_type": event["event_type"],
                    "units": value,
                    "insulin_kind": event["insulin_kind"],
                    "source_unit": event["source_unit"],
                    "source": "simulation",
                }
            )
        if insulin:
            database_call(session, "insulin_events", method="POST", payload=insulin)
        # One earlier completed synthetic meal provides honest numeric-retrieval evidence.
        points = {p.minute: p.glucose_mg_dl for p in result.trajectory}
        for past_meal in context["meal_events"]:
            meal_minute = int(math.ceil(past_meal["minute"] / 5) * 5)
            if meal_minute + 120 > origin:
                continue
            historical_id = database_call(
                session,
                "rpc/save_meal",
                method="POST",
                payload={
                    "p_name": "Virtual-patient earlier meal (illustrative nutrition)",
                    "p_recorded_at": (epoch + timedelta(minutes=meal_minute)).isoformat(),
                    "p_key": str(
                        uuid5(UUID(session.user_id), "simulated-history-" + str(meal_minute))
                    ),
                    "p_items": [
                        {
                            "food_id": "00000000-0000-4000-8000-000000000001",
                            "grams": past_meal["carbs_g"] / 30 * 100,
                        }
                    ],
                    "p_snapshot": {
                        "source": "synthetic_illustrative_macros",
                        "trajectory_source": "py-mgipsim",
                    },
                },
            )
            database_call(
                session,
                "meal_outcomes?on_conflict=meal_id",
                method="POST",
                payload={
                    "meal_id": historical_id,
                    "actual_30": points[meal_minute + 30],
                    "actual_60": points[meal_minute + 60],
                    "actual_120": points[meal_minute + 120],
                    "available_at": (epoch + timedelta(minutes=meal_minute + 120)).isoformat(),
                },
            )
        return {
            "source": "simulated",
            "execution": "cached_replay" if replay else "live",
            "forecast_origin": (epoch + timedelta(minutes=origin)).isoformat(),
            "sample_count": len(rows),
            "scenario": result.scenario_name,
            "notice": "Fixed virtual-patient scenario; synthetic research data only",
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            503, "Simulator unavailable; run the isolated setup or use reviewed replay"
        ) from None
    finally:
        SCENARIO_LOCK.release()
