"""Atomic stale-food conflict and refreshed-copy acceptance with synthetic fixtures."""

import os
from uuid import uuid4
from scripts.dev.cloud_integration import CloudHarness
from scripts.dev.meal_integration import run_harness


class ReviewedFactsHarness(CloudHarness):
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
            food_id = str(uuid4())
            self.manifest["foods"].append(food_id)
            self.save_manifest()
            facts = dict(
                nutrient_basis_g=100, calories=180, carbs_g=30, protein_g=6, fat_g=4, fiber_g=5
            )
            assert (
                self.request(
                    "POST",
                    "/rest/v1/foods",
                    admin=True,
                    body=dict(
                        id=food_id,
                        name="Synthetic review-conflict oracle",
                        source="synthetic_test",
                        source_food_id=self.run.run_id,
                        **facts,
                    ),
                ).status_code
                == 201
            )
            body = dict(
                workspace="personal",
                name="Synthetic reviewed meal",
                recorded_at="2026-01-01T12:00:00Z",
                confirmed=True,
                idempotency_key=str(uuid4()),
                items=[dict(food_id=food_id, grams=100, expected_facts=facts)],
            )
            assert (
                self.request(
                    "PATCH", f"/rest/v1/foods?id=eq.{food_id}", admin=True, body={"calories": 999}
                ).status_code
                == 200
            )
            assert api.post("/api/v1/meals", headers=headers, json=body).status_code == 409
            assert api.get("/api/v1/meals", headers=headers).json()["meals"] == []
            refreshed = api.post("/api/v1/foods/cached", headers=headers, json={"ids": [food_id]})
            assert refreshed.status_code == 200
            assert refreshed.json()["foods"][0]["calories"] == 999
            body["items"][0]["expected_facts"] = {**facts, "calories": 999}
            saved = api.post("/api/v1/meals", headers=headers, json=body)
            assert saved.status_code == 200
            mid = saved.json()["meal_id"]
            assert (
                self.request(
                    "PATCH", f"/rest/v1/foods?id=eq.{food_id}", admin=True, body={"calories": 1000}
                ).status_code
                == 200
            )
            edit = {**body, "revision": 1, "idempotency_key": str(uuid4())}
            assert api.patch(f"/api/v1/meals/{mid}", headers=headers, json=edit).status_code == 200
            detail = api.get(f"/api/v1/meals/{mid}", headers=headers).json()[0]
            assert (
                detail["calories"] == 999 and detail["meal_items"][0]["foods"]["calories"] == 1000
            )
            copied = {
                **body,
                "name": "Synthetic copied meal",
                "idempotency_key": str(uuid4()),
                "items": [
                    dict(food_id=food_id, grams=100, expected_facts={**facts, "calories": 1000})
                ],
            }
            copied_id = api.post("/api/v1/meals", headers=headers, json=copied).json()["meal_id"]
            assert (
                api.get(f"/api/v1/meals/{copied_id}", headers=headers).json()[0]["calories"] == 1000
            )
            self.record(
                "GL-P04-019",
                "A changed food cache caused atomic 409 with no meal; refresh required re-review; edits retained frozen 999-kcal facts while copied draft used current 1000-kcal facts",
            )
            self.record(
                "GL-P04-016",
                "Copy read exposes current trusted ingredient facts separately from original frozen snapshots; new meal used reviewed refreshed facts and did not rewrite original",
            )


if __name__ == "__main__":
    raise SystemExit(run_harness(ReviewedFactsHarness, __doc__, "reviewed-fact-conflicts"))
