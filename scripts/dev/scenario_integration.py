"""Guarded synthetic portion and genuine-source-clock follow-up acceptance."""

import os
from uuid import uuid4
from scripts.dev.cloud_integration import CloudHarness
from scripts.dev.meal_integration import run_harness


class ScenarioHarness(CloudHarness):
    def exercise(self):
        for name in (
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SECRET_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
        ):
            os.environ[name] = self.values.get(name, "")
        os.environ["HF_HUB_OFFLINE"] = "1"
        from fastapi.testclient import TestClient
        from backend.app.main import app

        a, b = self.create_user("a"), self.create_user("b")
        ha = {"Authorization": "Bearer " + a["token"]}
        hb = {"Authorization": "Bearer " + b["token"]}
        with TestClient(app) as api:
            for headers in (ha, hb):
                assert api.post("/api/v1/me/bootstrap", headers=headers, json={}).status_code == 200
            result = api.post("/api/v1/simulation/scenario", headers=ha, json={"replay": True})
            assert result.status_code == 200
            source = result.json()
            sid = source["source_session_id"]
            at = source["forecast_origin"]
            meal = api.post(
                "/api/v1/meals",
                headers=ha,
                json=dict(
                    workspace="simulation",
                    source_session_id=sid,
                    name="Synthetic scenario meal",
                    recorded_at=at,
                    consumed_at=at,
                    state="logged",
                    confirmed=True,
                    idempotency_key=str(uuid4()),
                    items=[dict(food_id="00000000-0000-4000-8000-000000000001", grams=100)],
                ),
            )
            assert meal.status_code == 200
            forecast = api.post(
                "/api/v1/forecasts",
                headers=ha,
                json={"meal_id": meal.json()["meal_id"], "idempotency_key": str(uuid4())},
            )
            assert forecast.status_code == 200
            fid = forecast.json()["forecast_id"]
            baseline = api.get(f"/api/v1/forecasts/{fid}", headers=ha).json()
            assert not api.get(f"/api/v1/forecasts/{fid}/actuals", headers=ha).json()["available"]
            before = api.get(
                f"/api/v1/nutrition?workspace=simulation&source_session_id={sid}", headers=ha
            ).json()["days"]
            for multiplier in (0.5, 0.75, 1.0):
                payload = {"multiplier": multiplier, "idempotency_key": str(uuid4())}
                result = api.post(f"/api/v1/forecasts/{fid}/scenarios", headers=ha, json=payload)
                assert result.status_code == 200
                saved = result.json()
                assert saved["response"]["history"] == baseline["forecast"]["history"]
                assert saved["response"]["model_version"] == baseline["forecast"]["model_version"]
                assert (
                    api.post(f"/api/v1/forecasts/{fid}/scenarios", headers=ha, json=payload).json()[
                        "id"
                    ]
                    == saved["id"]
                )
                if multiplier == 1:
                    assert saved["response"]["forecast"] == baseline["forecast"]["forecast"]
            assert (
                api.get(
                    f"/api/v1/nutrition?workspace=simulation&source_session_id={sid}", headers=ha
                ).json()["days"]
                == before
            )
            assert (
                len(api.get(f"/api/v1/forecasts/{fid}/scenarios", headers=ha).json()["scenarios"])
                == 3
            )
            assert (
                api.get(f"/api/v1/forecasts/{fid}/scenarios", headers=hb).json()["scenarios"] == []
            )
            self.record(
                "GL-P09-002",
                "Real 50/75/100% predictions reused frozen origin/history/model; 100% matched baseline points exactly; scenarios did not change eaten totals",
            )
            self.record(
                "GL-P09-003",
                "Three owned scenarios persisted; retries reused each ID and B saw none",
            )
            assert (
                api.post(
                    f"/api/v1/simulation/sources/{sid}/advance",
                    headers=hb,
                    json={"minutes": 120, "expected_clock": at},
                ).status_code
                == 404
            )
            advanced = api.post(
                f"/api/v1/simulation/sources/{sid}/advance",
                headers=ha,
                json={"minutes": 120, "expected_clock": at},
            )
            assert advanced.status_code == 200 and advanced.json()["added_samples"] == 24
            assert (
                api.post(
                    f"/api/v1/simulation/sources/{sid}/advance",
                    headers=ha,
                    json={"minutes": 120, "expected_clock": at},
                ).status_code
                == 409
            )
            observed = api.get(f"/api/v1/forecasts/{fid}/actuals", headers=ha)
            assert observed.status_code == 200 and observed.json()["available"]
            actual = observed.json()
            points = baseline["forecast"]["forecast"]
            values = actual["values_mg_dl"]
            expected = sum(abs(p["q50_mg_dl"] - v) for p, v in zip(points, values)) / 24
            assert actual["metrics"]["mae_mg_dl"] == expected
            assert (
                api.post(f"/api/v1/forecasts/{fid}/actuals", headers=ha, json={}).status_code == 200
            )
            assert api.get(f"/api/v1/forecasts/{fid}", headers=ha).json() == baseline
            self.record(
                "GL-P09-006",
                "Actuals unavailable before clock advance; checksum-verified reviewed trajectory supplied 24 samples only after advancing 120 minutes",
            )
            self.record(
                "GL-P09-008",
                "Observed MAE matched independently computed 24-point array; outcome persisted without changing frozen forecast",
            )
            # Outcome ends after original origin and must never appear as prior evidence for itself.
            assert (
                api.get(f"/api/v1/meals/{meal.json()['meal_id']}/similar", headers=ha).json()[
                    "meals"
                ]
                == []
            )
            self.record(
                "GL-P09-009",
                "Current meal's later outcome was excluded from its own earlier evidence query; source B advance was denied",
            )


if __name__ == "__main__":
    raise SystemExit(run_harness(ScenarioHarness, __doc__, "scenarios-followup"))
