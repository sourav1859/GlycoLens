"""Opt-in live local Auth -> simulator -> meal -> pretrained forecast -> retrieval check.

Print booleans/counts only. Session tokens and row-level trajectories never leave this process.
"""

import argparse
import json
from pathlib import Path
from uuid import uuid4

import httpx
from fastapi.testclient import TestClient

from backend.app.core.settings import load_local_configuration, required_setting
from backend.app.main import app


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-live-local", action="store_true")
    args = parser.parse_args()
    if not args.allow_live_local:
        raise SystemExit(
            "Pass --allow-live-local to acknowledge local synthetic writes and real model execution."
        )
    load_local_configuration()
    url = required_setting("SUPABASE_URL")
    if not url.startswith(("http://127.0.0.1:", "http://localhost:")):
        raise SystemExit("Verification is restricted to local Supabase.")
    key = required_setting("SUPABASE_ANON_KEY")
    sessions = []
    for _ in range(2):
        response = httpx.post(
            url + "/auth/v1/signup", headers={"apikey": key}, json={"data": {}}, timeout=15
        )
        if response.status_code != 200:
            raise SystemExit("Local anonymous Auth is unavailable; restart the configured stack.")
        sessions.append({"Authorization": "Bearer " + response.json()["access_token"]})
    evidence = {}
    with TestClient(app) as client:
        for session in sessions:
            assert client.post("/api/v1/demo/session", headers=session).status_code == 200
        result = client.post(
            "/api/v1/simulation/scenario", headers=sessions[0], json={"replay": False}
        )
        if result.status_code != 200:
            raise SystemExit(
                "Live simulator application check failed; inspect safe server error behavior."
            )
        evidence["live_scenario"] = True
        evidence["simulation_samples"] = result.json()["sample_count"]
        origin = result.json()["forecast_origin"]
        body = {
            "name": "Synthetic acceptance meal",
            "recorded_at": origin,
            "idempotency_key": str(uuid4()),
            "items": [{"food_id": "00000000-0000-4000-8000-000000000001", "grams": 150}],
            "input_snapshot": {"source": "synthetic_fixture"},
        }
        saved = client.post("/api/v1/meals", headers=sessions[0], json=body)
        assert saved.status_code == 200
        meal_id = saved.json()["meal_id"]
        repeated = client.post("/api/v1/meals", headers=sessions[0], json=body)
        evidence["meal_idempotency"] = repeated.json()["meal_id"] == meal_id
        other = client.get(f"/api/v1/meals/{meal_id}", headers=sessions[1])
        evidence["session_isolation"] = other.json() == []
        forecast_body = {"meal_id": meal_id, "idempotency_key": str(uuid4())}
        forecast = client.post("/api/v1/forecasts", headers=sessions[0], json=forecast_body)
        if forecast.status_code != 200:
            raise SystemExit("Real-model forecast API check failed; no completion claim is made.")
        data = forecast.json()
        evidence["real_model_forecast_points"] = len(data["forecast"]["forecast"])
        evidence["simulated_provenance"] = data["forecast"]["data_mode"] == "simulated"
        again = client.post("/api/v1/forecasts", headers=sessions[0], json=forecast_body)
        evidence["forecast_idempotency"] = again.json()["forecast_id"] == data["forecast_id"]
        recovered = client.get("/api/v1/forecasts/" + data["forecast_id"], headers=sessions[0])
        evidence["persisted_forecast_read"] = recovered.status_code == 200
        denied = client.get("/api/v1/forecasts/" + data["forecast_id"], headers=sessions[1])
        evidence["forecast_owner_isolation"] = denied.status_code == 404
        similar = client.get(f"/api/v1/meals/{meal_id}/similar", headers=sessions[0])
        evidence["similar_meal_count"] = len(similar.json()["meals"])
    if not all(evidence.values()):
        raise SystemExit("An application acceptance condition failed.")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    Path(".cache/m2-application-evidence.json").write_text(
        json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
