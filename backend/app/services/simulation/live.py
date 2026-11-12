"""Bounded fixed live scenario; public responses omit internal synthetic insulin values."""

import json
import math
import hashlib
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import HTTPException

from backend.app.db.client import UserSession, database_call
from backend.app.db.trusted import trusted_call
from research.simulation.adapter import PYMGIPSIM_COMMIT, PyMgipsimResult, run_pymgipsim_scenario


ROOT = Path(__file__).resolve().parents[4]
SCENARIO_LOCK = Lock()


def live_scenario(session: UserSession, *, replay: bool = False):
    if not SCENARIO_LOCK.acquire(blocking=False):
        raise HTTPException(429, "A simulator scenario is already running; retry shortly")
    source_id = None
    stored = False
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
                source_directory=Path(
                    os.environ.get(
                        "GLYCOLENS_SIMULATOR_SOURCE_DIR", str(ROOT / ".cache/pymgipsim-source")
                    )
                ),
                python_executable=Path(
                    os.environ.get(
                        "GLYCOLENS_SIMULATOR_PYTHON",
                        str(
                            ROOT
                            / (
                                ".cache/pymgipsim-venv/Scripts/python.exe"
                                if os.name == "nt"
                                else ".cache/pymgipsim-venv/bin/python"
                            )
                        ),
                    )
                ),
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
        source_id = str(uuid4())
        saved_directory = directory / "sources" / source_id
        saved_directory.mkdir(parents=True, exist_ok=False)
        saved_output = output.read_bytes()
        saved_context = internal.read_bytes()
        (saved_directory / "scenario.json").write_bytes(saved_output)
        (saved_directory / "context.json").write_bytes(saved_context)
        source_id = trusted_call(
            session,
            "rpc/app_store_source_context",
            payload={
                "p_session": source_id,
                "p_mode": "replay" if replay else "simulation",
                "p_clock": (epoch + timedelta(minutes=origin)).isoformat(),
                "p_cgm": rows,
                "p_insulin": insulin,
                "p_metadata": {
                    "engine": "py-mgipsim",
                    "commit": PYMGIPSIM_COMMIT,
                    "scenario": result.scenario_name,
                    "synthetic": True,
                    "inference_context_end": (epoch + timedelta(minutes=origin)).isoformat(),
                    "trajectory_sha256": hashlib.sha256(saved_output).hexdigest(),
                    "context_sha256": hashlib.sha256(saved_context).hexdigest(),
                },
            },
        )
        stored = True
        return {
            "source": "simulated",
            "source_session_id": source_id,
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
        if source_id and not stored:
            # A concurrent account deletion can reject the final FK-bound write.
            # Remove only this newly generated UUID, never the shared replay.
            from backend.app.services.account_deletion import remove_source_artifacts
            try:
                remove_source_artifacts(source_id)
            except (OSError, ValueError):
                import logging
                logging.getLogger(__name__).warning("Uncommitted synthetic source cleanup failed")
        SCENARIO_LOCK.release()


def advance_source(session: UserSession, source_id, minutes: int, expected_clock: datetime):
    from uuid import UUID

    source_id = str(UUID(str(source_id)))
    rows = database_call(session, f"source_sessions?id=eq.{source_id}&select=*")
    if not rows:
        raise HTTPException(404, "Source not found")
    source = rows[0]
    if expected_clock.tzinfo is None or expected_clock != datetime.fromisoformat(
        source["clock_at"].replace("Z", "+00:00")
    ):
        raise HTTPException(409, "Source clock changed; reload before advancing")
    directory = ROOT / "artifacts/simulation/app/sources" / source_id
    try:
        trajectory = (directory / "scenario.json").read_bytes()
        context_bytes = (directory / "context.json").read_bytes()
        if hashlib.sha256(trajectory).hexdigest() != source["metadata"].get(
            "trajectory_sha256"
        ) or hashlib.sha256(context_bytes).hexdigest() != source["metadata"].get("context_sha256"):
            raise ValueError("source checksum changed")
        result = PyMgipsimResult.from_json(directory / "scenario.json")
        context = json.loads(context_bytes)
        previous = datetime.fromisoformat(source["clock_at"].replace("Z", "+00:00"))
        clock = previous + timedelta(minutes=minutes)
        epoch = datetime(2026, 1, 1, tzinfo=timezone.utc)
        if clock > epoch + timedelta(minutes=result.duration_minutes):
            raise HTTPException(422, "This reviewed trajectory has ended")
        cgm = [
            {
                "recorded_at": (epoch + timedelta(minutes=p.minute)).isoformat(),
                "glucose_mg_dl": p.glucose_mg_dl,
            }
            for p in result.trajectory
            if previous < epoch + timedelta(minutes=p.minute) <= clock
        ]
        insulin = [
            {
                "recorded_at": (epoch + timedelta(minutes=e["minute"])).isoformat(),
                "units": e["source_value"],
                "event_type": e["event_type"],
                "insulin_kind": e["insulin_kind"],
                "source_unit": e["source_unit"],
            }
            for e in context["insulin_events"]
            if previous < epoch + timedelta(minutes=e["minute"]) <= clock
        ]
        trusted_call(
            session,
            "rpc/app_advance_source",
            payload={
                "p_session": source_id,
                "p_previous": previous.isoformat(),
                "p_clock": clock.isoformat(),
                "p_cgm": cgm,
                "p_insulin": insulin,
            },
        )
        return {
            "source_session_id": source_id,
            "clock_at": clock.isoformat(),
            "added_samples": len(cgm),
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            503, "Reviewed source artifact unavailable or changed; no observations were invented"
        ) from None
