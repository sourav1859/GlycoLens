"""Opt-in scoped cloud acceptance with real native LightGBM/Chronos and simulator.

No LLM/provider calls, training, reserved cohort projection or broad cleanup.
"""

from copy import deepcopy
import os
from pathlib import Path
from uuid import UUID, uuid4

from scripts.dev.cloud_integration import CloudHarness
from scripts.dev.meal_integration import run_harness


class LightGBMHarness(CloudHarness):
    def exercise(self):
        for name in (
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SECRET_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
        ):
            os.environ[name] = self.values.get(name, "")
        root = Path(__file__).resolve().parents[2]
        os.environ.update(
            GLYCOLENS_LIGHTGBM_ENABLED="true",
            GLYCOLENS_LIGHTGBM_MANIFEST_SHA256=(root / "artifacts/models/lightgbm/manifest.sha256")
            .read_text()
            .strip(),
            GLYCOLENS_DELETION_CLEANUP_WORKER="0",
            HF_HUB_OFFLINE="1",
        )
        from fastapi.testclient import TestClient
        from backend.app.main import app
        from backend.app.db.client import UserSession, database_call
        from backend.app.db.trusted import trusted_call

        def ok(response):
            if response.status_code != 200:
                self.manifest["last_failure"] = dict(
                    status=response.status_code,
                    path=response.request.url.path,
                    detail=response.json().get("detail"),
                )
                self.save_manifest()
                raise AssertionError("Integration response failed")
            return response.json()

        a, b = self.create_user("a"), self.create_user("b")
        ha, hb = ({"Authorization": "Bearer " + u["token"]} for u in (a, b))
        owner = UserSession(a["token"], a["id"])
        self.manifest["sources"] = []
        with TestClient(app) as api:
            for headers in (ha, hb):
                ok(api.post("/api/v1/me/bootstrap", headers=headers, json={}))
            assert ok(api.get("/api/v1/forecasts/models", headers=ha))["models"][1]["available"]
            food_id = str(uuid4())
            self.manifest["foods"].append(food_id)
            self.save_manifest()
            assert (
                self.request(
                    "POST",
                    "/rest/v1/foods",
                    admin=True,
                    body=dict(
                        id=food_id,
                        name="Run-scoped synthetic nutrition oracle",
                        source="synthetic_test",
                        source_food_id=self.run.run_id,
                        nutrient_basis_g=100,
                        calories=100,
                        carbs_g=4,
                        protein_g=5,
                        fat_g=7,
                        fiber_g=1,
                    ),
                ).status_code
                == 201
            )
            short = ok(api.post("/api/v1/simulation/scenario", headers=ha, json={"replay": False}))
            self.manifest["sources"].append(short["source_session_id"])
            self.save_manifest()

            def meal(at, source_id):
                return ok(
                    api.post(
                        "/api/v1/meals",
                        headers=ha,
                        json=dict(
                            workspace="simulation",
                            source_session_id=source_id,
                            name="Synthetic model-integration meal",
                            recorded_at=at,
                            confirmed=True,
                            idempotency_key=str(uuid4()),
                            items=[dict(food_id=food_id, grams=250)],
                        ),
                    )
                )["meal_id"]

            short_meal = meal(short["forecast_origin"], short["source_session_id"])
            assert (
                api.post(
                    "/api/v1/forecasts",
                    headers=ha,
                    json=dict(
                        meal_id=short_meal, idempotency_key=str(uuid4()), model_key="lightgbm"
                    ),
                ).status_code
                == 422
            )
            chrono = ok(
                api.post(
                    "/api/v1/forecasts",
                    headers=ha,
                    json=dict(meal_id=short_meal, idempotency_key=str(uuid4())),
                )
            )
            assert chrono["forecast"]["model_id"] == "amazon/chronos-2"
            self.record(
                "LGB-L2-001",
                "Omitted model runs real pinned Chronos; explicit LightGBM on old source rejected without fallback",
            )
            long = ok(
                api.post(
                    "/api/v1/simulation/scenario",
                    headers=ha,
                    json=dict(replay=False, protocol="lightgbm_warmup_48h_v1"),
                )
            )
            self.manifest["sources"].append(long["source_session_id"])
            self.save_manifest()
            assert long["sample_count"] == 288
            mid = meal(long["forecast_origin"], long["source_session_id"])
            request = dict(meal_id=mid, idempotency_key=str(uuid4()), model_key="lightgbm")
            predicted = ok(api.post("/api/v1/forecasts", headers=ha, json=request))
            fid = predicted["forecast_id"]
            response = predicted["forecast"]
            assert (
                response["schema_version"] == "2.0"
                and response["provenance"]["history_samples"] == 288
            )
            assert (
                len(response["forecast"]) == 24
                and response["interval_kind"] == "calibrated_marginal_80"
            )
            assert ok(api.post("/api/v1/forecasts", headers=ha, json=request))["forecast_id"] == fid
            assert ok(api.get(f"/api/v1/forecasts/{fid}", headers=ha))["forecast"] == response
            assert (
                api.post(
                    "/api/v1/forecasts", headers=ha, json={**request, "model_key": "chronos"}
                ).status_code
                == 409
            )
            assert api.get(f"/api/v1/forecasts/{fid}", headers=hb).status_code == 404
            assert (
                self.request(
                    "GET", f"/rest/v1/forecast_points?forecast_id=eq.{fid}", token=b["token"]
                ).json()
                == []
            )
            self.record(
                "LGB-L2-005",
                "Real native/calibrated forecast cloud save/read/retry retains full identity; changed model reusing key conflicts",
            )
            self.record("LGB-L2-006", "Actual user API and child-point RLS deny owner B")
            for multiplier in (1, 0.5):
                body = dict(multiplier=multiplier, idempotency_key=str(uuid4()))
                scenario = ok(api.post(f"/api/v1/forecasts/{fid}/scenarios", headers=ha, json=body))
                if multiplier == 1:
                    assert scenario["response"]["forecast"] == response["forecast"]
                assert scenario["response"]["provenance"] == response["provenance"]
                assert (
                    ok(api.post(f"/api/v1/forecasts/{fid}/scenarios", headers=ha, json=body))["id"]
                    == scenario["id"]
                )
            self.record(
                "LGB-L2-007",
                "100% same-model scenario reproduces every endpoint; 50% and idempotent retries keep complete frozen identity",
            )
            raw = database_call(owner, f"forecasts?id=eq.{fid}&select=*")[0]
            frozen = deepcopy(raw["input_snapshot"])
            frozen["response"]["forecast"][0]["q10_mg_dl"] = -5
            tail = trusted_call(
                owner,
                "rpc/app_commit_forecast",
                payload=dict(
                    p_meal=mid,
                    p_revision=raw["meal_revision"],
                    p_key=str(uuid4()),
                    p_model=raw["model_id"],
                    p_version=raw["model_version"],
                    p_context=raw["context_config"],
                    p_origin=raw["forecast_origin"],
                    p_latency=0,
                    p_provenance=raw["context_provenance"],
                    p_points=frozen["response"]["forecast"],
                    p_input=frozen,
                ),
            )
            assert (
                ok(api.get(f"/api/v1/forecasts/{tail}", headers=ha))["forecast"]["forecast"][0][
                    "q10_mg_dl"
                ]
                == -5
            )
            assert (
                float(
                    database_call(
                        owner, f"forecast_points?forecast_id=eq.{tail}&order=forecast_at&limit=1"
                    )[0]["q10"]
                )
                == -5
            )
            self.record(
                "LGB-L2-003",
                "Explicit synthetic signed-tail fixture round-trips API/snapshot/actual SQL points without clipping; not a claim that the real model produced that tail",
            )
            old = database_call(owner, f"forecasts?id=eq.{chrono['forecast_id']}&select=*")[0]
            legacy = deepcopy(old["input_snapshot"])
            legacy.pop("model_identity", None)
            legacy["response"].update(
                schema_version="1.0", provenance=None, interval_kind="model_quantiles"
            )
            legacy_id = trusted_call(
                owner,
                "rpc/app_commit_forecast",
                payload=dict(
                    p_meal=short_meal,
                    p_revision=old["meal_revision"],
                    p_key=str(uuid4()),
                    p_model=old["model_id"],
                    p_version=old["model_version"],
                    p_context=old["context_config"],
                    p_origin=old["forecast_origin"],
                    p_latency=0,
                    p_provenance={"source": "simulated"},
                    p_points=legacy["response"]["forecast"],
                    p_input=legacy,
                ),
            )
            assert (
                ok(api.get(f"/api/v1/forecasts/{legacy_id}", headers=ha))["forecast"][
                    "schema_version"
                ]
                == "1.0"
            )
            self.record(
                "LGB-L2-004",
                "Forward migration accepts current 288-point owned snapshots and a scoped legacy-v1 fixture; scratch replay remains deferred",
                status="PARTIAL",
            )
            self.record(
                "LGB-L4-002",
                "Real host API/native model/simulator/cloud path passed; this run is not a Docker or browser journey",
                status="PARTIAL",
            )

    def cleanup(self):
        super().cleanup()
        from backend.app.services.account_deletion import remove_source_artifacts

        for source in self.manifest.get("sources", []):
            remove_source_artifacts(str(UUID(source)))


if __name__ == "__main__":
    raise SystemExit(run_harness(LightGBMHarness, __doc__, "real-lightgbm-model-integration"))
