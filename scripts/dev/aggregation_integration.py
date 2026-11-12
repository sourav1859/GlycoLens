"""Known direct synthetic fixtures for DST, full-dataset totals and DB concurrency."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import os
from uuid import uuid4
from scripts.dev.cloud_integration import CloudHarness
from scripts.dev.meal_integration import run_harness


class AggregateHarness(CloudHarness):
    def exercise(self):
        for name in (
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SECRET_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
        ):
            os.environ[name] = self.values.get(name, "")
        from fastapi.testclient import TestClient
        from backend.app.main import app

        a = self.create_user("a")
        headers = {"Authorization": "Bearer " + a["token"]}
        with TestClient(app) as api:
            assert api.post("/api/v1/me/bootstrap", headers=headers, json={}).status_code == 200
            sid = str(uuid4())
            at = "2026-11-02T12:00:00Z"
            assert (
                self.request(
                    "POST",
                    "/rest/v1/source_sessions",
                    admin=True,
                    body=dict(
                        id=sid,
                        user_id=a["id"],
                        mode="replay",
                        clock_at=at,
                        metadata={"synthetic_test_only": True, "run": self.run.run_id},
                    ),
                ).status_code
                == 201
            )
            assert (
                self.request(
                    "PATCH",
                    f"/rest/v1/user_preferences?user_id=eq.{a['id']}",
                    admin=True,
                    body={
                        "source_session_id": sid,
                        "timezone": "America/New_York",
                        "source_mode": "replay",
                    },
                ).status_code
                == 200
            )
            start = datetime(2026, 11, 1, 4, tzinfo=timezone.utc)
            meals = []
            for i in range(30):
                instant = (
                    start + timedelta(minutes=i * 5)
                    if i < 29
                    else datetime(2026, 11, 2, 4, 59, tzinfo=timezone.utc)
                )
                meals.append(
                    dict(
                        user_id=a["id"],
                        source_session_id=sid,
                        name="Synthetic aggregate oracle",
                        recorded_at=instant.isoformat(),
                        state="logged",
                        consumed_at=instant.isoformat(),
                        meal_type="lunch",
                        calories=100,
                        carbs_g=10,
                        protein_g=2,
                        fat_g=1,
                        fiber_g=None if i == 0 else 1,
                    )
                )
            meals.append(
                {
                    **meals[0],
                    "consumed_at": "2026-11-02T05:00:00Z",
                    "recorded_at": "2026-11-02T05:00:00Z",
                }
            )
            for state in ("planned", "cancelled"):
                meals.append({**meals[0], "state": state, "consumed_at": None, "calories": 999})
            assert self.request("POST", "/rest/v1/meals", admin=True, body=meals).status_code == 201
            summary = api.get("/api/v1/nutrition?day=2026-11-01", headers=headers)
            assert summary.status_code == 200
            day = summary.json()["days"][-1]
            assert (
                day["meal_count"] == 30
                and day["nutrients"]["calories"]["total"] == 3000
                and day["nutrients"]["carbs_g"]["total"] == 300
            )
            assert (
                day["nutrients"]["fiber_g"]["total"] is None
                and day["nutrients"]["fiber_g"]["known_total"] == 29
                and day["nutrients"]["fiber_g"]["missing_meals"] == 1
            )
            listing = api.get("/api/v1/meals?day=2026-11-01&slot=lunch&limit=20", headers=headers)
            assert listing.status_code == 200
            assert len(listing.json()["meals"]) == 20 and listing.json()["has_more"]
            assert (
                len(
                    api.get(
                        "/api/v1/meals?day=2026-11-01&slot=lunch&offset=20", headers=headers
                    ).json()["meals"]
                )
                == 12
            )
            self.record(
                "GL-P06-005",
                "30 eaten rows totaled 3000 kcal/300 g carbs despite 20-card pagination; planned/cancelled 999-kcal sentinels excluded",
            )
            self.record(
                "GL-P06-002",
                "25-hour New York fall-back day included UTC 04:00 start through next-day 04:59 and excluded exact UTC 05:00 end",
            )
            self.record(
                "GL-P06-004",
                "One unknown fiber yielded null full total, 29-g known subtotal and exactly one missing-meal count",
            )
            assert (
                api.patch(
                    "/api/v1/me/preferences",
                    headers=headers,
                    json={"revision": 0, "timezone": "UTC"},
                ).status_code
                == 200
            )
            assert (
                api.get("/api/v1/nutrition?day=2026-11-01", headers=headers).json()["days"][-1][
                    "meal_count"
                ]
                == 29
            )
            self.record(
                "GL-P06-003",
                "Changing timezone regrouped immutable instants from 30 to 29 eaten rows on the selected day",
            )
            fid = str(uuid4())
            assert (
                self.request(
                    "POST",
                    "/rest/v1/forecasts",
                    admin=True,
                    body=dict(
                        id=fid,
                        user_id=a["id"],
                        model_id="synthetic_database_fixture",
                        model_version="test",
                        context_config="cgm_only",
                        horizon_minutes=120,
                        quantiles_json=[],
                        input_snapshot={"synthetic_test_only": True},
                    ),
                ).status_code
                == 201
            )

            def attempt(_):
                return self.request(
                    "POST",
                    "/rest/v1/rpc/app_save_scenario",
                    admin=True,
                    body={
                        "p_user": a["id"],
                        "p_forecast": fid,
                        "p_multiplier": 0.5,
                        "p_key": str(uuid4()),
                        "p_response": {"synthetic_test_only": True},
                    },
                ).status_code

            with ThreadPoolExecutor(max_workers=4) as pool:
                statuses = list(pool.map(attempt, range(12)))
            assert statuses.count(200) == 10 and statuses.count(429) == 2
            assert (
                len(
                    self.request(
                        "GET",
                        f"/rest/v1/portion_scenarios?forecast_id=eq.{fid}&select=id",
                        token=a["token"],
                    ).json()
                )
                == 10
            )
            self.record(
                "GL-P09-004",
                "12 concurrent trusted synthetic DB saves produced exactly 10 rows and two 429 rejections under the per-parent lock; no model calls",
            )


if __name__ == "__main__":
    raise SystemExit(run_harness(AggregateHarness, __doc__, "aggregation-and-concurrency"))
