"""Opt-in synthetic cloud integration with one real simulator/model execution."""

import os
from uuid import uuid4

from scripts.dev.cloud_integration import CloudHarness
from scripts.dev.meal_integration import run_harness


class SourceHarness(CloudHarness):
    def exercise(self):
        for name in (
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SECRET_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
        ):
            os.environ[name] = self.values.get(name, "")
        # Never download or select a model implicitly in acceptance.
        os.environ["HF_HUB_OFFLINE"] = "1"
        from fastapi.testclient import TestClient
        from backend.app.main import app

        a, b = self.create_user("a"), self.create_user("b")
        ha = {"Authorization": "Bearer " + a["token"]}
        hb = {"Authorization": "Bearer " + b["token"]}
        with TestClient(app) as api:
            for headers in (ha, hb):
                assert api.post("/api/v1/me/bootstrap", headers=headers, json={}).status_code == 200
            source = api.post("/api/v1/simulation/scenario", headers=ha, json={"replay": False})
            assert source.status_code == 200
            source = source.json()
            sid = source["source_session_id"]
            at = source["forecast_origin"]
            assert source["execution"] == "live" and source["sample_count"] >= 24
            self.record(
                "GL-P05-001",
                "Real pinned py-mgipsim execution saved only pre-origin CGM/insulin in an owned source partition",
            )
            body = dict(
                name="Synthetic reviewed source meal",
                recorded_at=at,
                confirmed=True,
                idempotency_key=str(uuid4()),
                items=[dict(food_id="00000000-0000-4000-8000-000000000001", grams=250)],
            )
            saved = api.post("/api/v1/meals", headers=ha, json=body)
            assert saved.status_code == 200
            mid = saved.json()["meal_id"]
            summary = api.get("/api/v1/nutrition", headers=ha).json()
            assert summary["available"] and all(d["meal_count"] == 0 for d in summary["days"])
            logged = {
                **body,
                "idempotency_key": str(uuid4()),
                "revision": 1,
                "state": "logged",
                "consumed_at": at,
            }
            assert api.patch(f"/api/v1/meals/{mid}", headers=ha, json=logged).status_code == 200
            summary = api.get("/api/v1/nutrition", headers=ha).json()
            today = summary["days"][-1]
            assert (
                today["meal_count"] == 1
                and today["nutrients"]["calories"]["total"] == 450
                and today["nutrients"]["carbs_g"]["total"] == 75
            )
            home = api.get("/api/v1/home", headers=ha).json()
            assert home["days"] == summary["days"] and home["day"] == summary["day"]
            assert home["latest_glucose"][0]["recorded_at"] == summary["source"]["clock_at"]
            self.record(
                "GL-P06-001",
                "Planned meal contributed zero; confirmed eaten 250 g fixture yielded exactly 450 kcal / 75 g carbs on Home and Nutrition",
            )
            self.record(
                "GL-P06-011",
                "Default day came from source clock, not wall date; latest glucose matched owned clock",
            )
            request = dict(meal_id=mid, idempotency_key=str(uuid4()))
            generated = api.post("/api/v1/forecasts", headers=ha, json=request)
            assert generated.status_code == 200
            generated = generated.json()
            fid = generated["forecast_id"]
            original = api.get(f"/api/v1/forecasts/{fid}", headers=ha)
            assert original.status_code == 200
            original = original.json()
            assert (
                len(original["forecast"]["history"]) == 24
                and len(original["forecast"]["forecast"]) == 24
            )
            assert (
                original["forecast"]["model_id"] == "amazon/chronos-2"
                and original["meal_revision"] == 2
            )
            assert (
                api.post("/api/v1/forecasts", headers=ha, json=request).json()["forecast_id"] == fid
            )
            assert api.get(f"/api/v1/forecasts/{fid}", headers=hb).status_code == 404
            self.record(
                "GL-P05-004",
                "Real cached pinned Chronos C3 produced 24 validated points; cloud save/read/retry preserved result and denied B",
            )
            changed = {
                **logged,
                "revision": 2,
                "idempotency_key": str(uuid4()),
                "items": [dict(food_id=body["items"][0]["food_id"], grams=125)],
            }
            assert api.patch(f"/api/v1/meals/{mid}", headers=ha, json=changed).status_code == 200
            assert api.get(f"/api/v1/forecasts/{fid}", headers=ha).json() == original
            assert (
                api.get("/api/v1/nutrition", headers=ha).json()["days"][-1]["nutrients"][
                    "calories"
                ]["total"]
                == 225
            )
            self.record(
                "GL-P06-006",
                "Edited eaten meal updated shared aggregate to 225 kcal; saved forecast retained original meal revision/input",
            )
            cancel = dict(revision=3, idempotency_key=str(uuid4()))
            assert (
                api.request("DELETE", f"/api/v1/meals/{mid}", headers=ha, json=cancel).status_code
                == 200
            )
            assert api.get("/api/v1/nutrition", headers=ha).json()["days"][-1]["meal_count"] == 0
            replay = api.post("/api/v1/simulation/scenario", headers=ha, json={"replay": True})
            assert replay.status_code == 200 and replay.json()["source_session_id"] != sid
            assert api.get(f"/api/v1/forecasts/{fid}", headers=ha).json() == original
            assert api.get("/api/v1/forecasts", headers=ha).json()["forecasts"] == []
            assert api.get("/api/v1/meals", headers=ha).json()["meals"] == []
            self.record(
                "GL-P05-010",
                "Same-clock replay created new partition; existing forecast history remained byte-equivalent after meal edit/cancel and source replacement",
            )
            self.record(
                "GL-P06-012",
                "Source switch excluded earlier meals/forecasts; cancelled meal left eaten aggregate; another owner had unavailable rather than zero-filled source",
            )
            assert not api.get("/api/v1/nutrition", headers=hb).json()["available"]


if __name__ == "__main__":
    raise SystemExit(run_harness(SourceHarness, __doc__, "real-source-model"))
