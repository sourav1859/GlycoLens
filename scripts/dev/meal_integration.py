"""Guarded cloud meal lifecycle acceptance; no providers, emails or model calls."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import traceback
from uuid import uuid4

from scripts.dev.cloud_integration import CloudHarness
from scripts.dev.cloud_preflight import new_run_id, read_configuration


class MealHarness(CloudHarness):
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

        a, b = self.create_user("a"), self.create_user("b")
        with TestClient(app) as api:
            ha = {"Authorization": "Bearer " + a["token"]}
            hb = {"Authorization": "Bearer " + b["token"]}
            for headers in (ha, hb):
                assert api.post("/api/v1/me/bootstrap", headers=headers, json={}).status_code == 200
            food_id = str(uuid4())
            self.manifest["foods"].append(food_id)
            self.save_manifest()
            food = dict(
                id=food_id,
                name="Run-scoped synthetic food",
                source="synthetic_test",
                source_food_id=self.run.run_id,
                nutrient_basis_g=100,
                calories=180,
                carbs_g=30,
                protein_g=6,
                fat_g=4,
                fiber_g=None,
            )
            assert self.request("POST", "/rest/v1/foods", admin=True, body=food).status_code == 201
            body = dict(
                workspace="personal",
                name="Synthetic planned meal",
                recorded_at="2026-01-01T12:00:00Z",
                confirmed=True,
                idempotency_key=str(uuid4()),
                items=[dict(food_id=food_id, grams=100), dict(food_id=food_id, grams=25)],
            )
            first = api.post("/api/v1/meals", headers=ha, json=body)
            assert first.status_code == 200
            mid = first.json()["meal_id"]
            assert api.post("/api/v1/meals", headers=ha, json=body).json() == first.json()
            assert (
                api.post(
                    "/api/v1/meals", headers=ha, json={**body, "name": "Changed retry"}
                ).status_code
                == 409
            )
            stored = api.get(f"/api/v1/meals/{mid}", headers=ha).json()[0]
            assert stored["state"] == "planned" and stored["consumed_at"] is None
            assert (
                stored["calories"] == 225
                and stored["carbs_g"] == 37.5
                and stored["fiber_g"] is None
            )
            assert len(stored["meal_items"]) == 1 and stored["meal_items"][0]["grams"] == 125
            self.record(
                "GL-P04-009",
                "125 g from repeated 100+25 g items produced 225 kcal / 37.5 g carbs; unknown fiber remained null",
            )
            self.record(
                "GL-P04-015",
                "Identical retry reused meal/revision; changed body with same key was rejected 409",
            )
            assert api.get(f"/api/v1/meals/{mid}", headers=hb).json() == []
            assert (
                self.request(
                    "GET", "/rest/v1/meal_revisions?select=revision", token=b["token"]
                ).json()
                == []
            )
            self.record(
                "GL-P04-019",
                "Other owner could read neither meal nor revision; browser writes remain revoked",
            )
            edit = {
                **body,
                "idempotency_key": str(uuid4()),
                "revision": 1,
                "state": "logged",
                "consumed_at": "2026-01-01T12:15:00Z",
                "items": [dict(food_id=food_id, grams=250)],
            }
            # A provider refresh cannot rewrite previously reviewed ingredient facts on edit.
            assert (
                self.request(
                    "PATCH", f"/rest/v1/foods?id=eq.{food_id}", admin=True, body={"calories": 999}
                ).status_code
                == 200
            )
            saved = api.patch(f"/api/v1/meals/{mid}", headers=ha, json=edit)
            assert saved.status_code == 200 and saved.json()["revision"] == 2
            stored = api.get(f"/api/v1/meals/{mid}", headers=ha).json()[0]
            assert (
                stored["calories"] == 450
                and stored["carbs_g"] == 75
                and stored["state"] == "logged"
            )
            assert (
                api.patch(
                    f"/api/v1/meals/{mid}",
                    headers=ha,
                    json={**edit, "idempotency_key": str(uuid4())},
                ).status_code
                == 409
            )
            failed = {
                **edit,
                "revision": 2,
                "idempotency_key": str(uuid4()),
                "items": [dict(food_id=str(uuid4()), grams=1)],
            }
            assert api.patch(f"/api/v1/meals/{mid}", headers=ha, json=failed).status_code == 422
            assert api.get(f"/api/v1/meals/{mid}", headers=ha).json()[0]["revision"] == 2
            self.record(
                "GL-P04-013",
                "Edit used frozen food facts, incremented revision and rejected stale update; invalid food rolled back completely",
            )
            cancel = dict(revision=2, idempotency_key=str(uuid4()))
            result = api.request("DELETE", f"/api/v1/meals/{mid}", headers=ha, json=cancel)
            assert result.status_code == 200
            assert (
                api.request("DELETE", f"/api/v1/meals/{mid}", headers=ha, json=cancel).json()
                == result.json()
            )
            revisions = self.request(
                "GET",
                f"/rest/v1/meal_revisions?meal_id=eq.{mid}&select=revision,snapshot&order=revision",
                token=a["token"],
            ).json()
            assert [r["revision"] for r in revisions] == [1, 2, 3]
            assert [r["snapshot"]["state"] for r in revisions] == ["planned", "logged", "cancelled"]
            self.record(
                "GL-P04-014",
                "Cancellation preserved three immutable revisions; repeated cancellation reused receipt; permanent removal is not exposed",
            )


def run_harness(kind, description, output_suffix):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--allow-cloud", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.allow_cloud:
        print("DRY RUN: explicit --allow-cloud required; no network")
        return 0
    harness = kind(read_configuration(), allow_cloud=True, run_id=new_run_id())
    error = cleanup_error = location = None
    with harness.bounded_network():
        try:
            harness.exercise()
        except Exception as exc:
            error = type(exc).__name__
            frame = traceback.extract_tb(exc.__traceback__)[-1]
            location = f"{Path(frame.filename).name}:{frame.lineno}"
        finally:
            try:
                harness.cleanup()
            except Exception as exc:
                cleanup_error = type(exc).__name__
    report = dict(
        executed_at_utc=datetime.now(timezone.utc).isoformat(),
        run_id=harness.run.run_id,
        project_ref=harness.run.project_ref,
        requests=harness.calls,
        email_messages=0,
        paid_provider_calls=0,
        results=harness.results,
        execution_error_class=error,
        failure_location=location,
        cleanup_error_class=cleanup_error,
        cleanup_completed=not cleanup_error,
        suite=output_suffix,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "results"}, indent=2))
    return 1 if error or cleanup_error else 0


if __name__ == "__main__":
    raise SystemExit(run_harness(MealHarness, __doc__, "meal-lifecycle"))
