"""Synthetic owned notifications/export acceptance; no paid API or emails."""

import os
from uuid import uuid4
from scripts.dev.cloud_integration import CloudHarness
from scripts.dev.meal_integration import run_harness


class PrivacyHarness(CloudHarness):
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
        ha = {"Authorization": "Bearer " + a["token"]}
        hb = {"Authorization": "Bearer " + b["token"]}
        with TestClient(app) as api:
            for headers in (ha, hb):
                assert api.post("/api/v1/me/bootstrap", headers=headers, json={}).status_code == 200
            body = dict(
                workspace="personal",
                name="Synthetic notification meal",
                recorded_at="2026-01-01T12:00:00Z",
                confirmed=True,
                idempotency_key=str(uuid4()),
                items=[dict(food_id="00000000-0000-4000-8000-000000000001", grams=100)],
            )
            first = api.post("/api/v1/meals", headers=ha, json=body)
            assert (
                first.status_code == 200
                and api.post("/api/v1/meals", headers=ha, json=body).json() == first.json()
            )
            events = api.get("/api/v1/notifications", headers=ha).json()["notifications"]
            assert (
                len(events) == 1
                and events[0]["kind"] == "meal_saved"
                and events[0]["read_at"] is None
            )
            assert api.get("/api/v1/notifications", headers=hb).json()["notifications"] == []
            ids = [events[0]["id"]]
            assert api.patch(
                "/api/v1/notifications/read", headers=hb, json={"ids": ids}
            ).json() == {"updated": 0}
            assert api.patch(
                "/api/v1/notifications/read", headers=ha, json={"ids": ids}
            ).json() == {"updated": 1}
            assert api.patch(
                "/api/v1/notifications/read", headers=ha, json={"ids": ids}
            ).json() == {"updated": 0}
            assert self.request(
                "POST",
                "/rest/v1/notifications",
                token=a["token"],
                body={
                    "user_id": a["id"],
                    "kind": "forecast_ready",
                    "entity_id": str(uuid4()),
                    "event_key": "forged",
                },
            ).status_code in {401, 403}
            self.record(
                "GL-P08-009",
                "Trusted meal event was deduplicated on retry; browser could not fabricate system event",
            )
            self.record(
                "GL-P08-010",
                "B saw no A events and could not mark A read; A mark-read was idempotent",
            )
            exported = api.get("/api/v1/me/export", headers=ha)
            assert (
                exported.status_code == 200
                and exported.headers["cache-control"] == "private, no-store"
            )
            payload = exported.json()
            assert payload["user_id"] == a["id"]
            assert (
                len(payload["records"]["meals"]) == 1
                and payload["records"]["meals"][0]["id"] == first.json()["meal_id"]
            )
            assert a["token"] not in exported.text and b["id"] not in exported.text
            other = api.get("/api/v1/me/export", headers=hb).json()
            assert other["records"]["meals"] == [] and other["records"]["notifications"] == []
            assert api.get("/api/v1/me/export").status_code == 401
            self.record(
                "GL-P08-005",
                "Bounded no-store export included only owned records and snapshots, excluded JWTs and denied unauthenticated access",
            )


if __name__ == "__main__":
    raise SystemExit(run_harness(PrivacyHarness, __doc__, "privacy-notifications"))
