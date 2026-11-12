"""Opt-in immediate deletion acceptance with two tagged disposable cloud accounts.

No email or paid provider calls. The optional private-fixture handshake lets the
MCP SQL operator seed/check non-exposed rows using the recorded run identity.
"""

import json
import os
import time
from unittest.mock import patch
from uuid import uuid4

from scripts.dev.cloud_integration import CloudHarness
from scripts.dev.cloud_preflight import ROOT
from scripts.dev.meal_integration import run_harness


class DeletionHarness(CloudHarness):
    def insert(self, table, body):
        response = self.request("POST", "/rest/v1/" + table, admin=True, body=body)
        assert response.status_code in {200, 201}, "Synthetic child fixture rejected: " + table
        return response.json()

    def exercise(self):
        for name in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SECRET_KEY", "SUPABASE_SERVICE_ROLE_KEY"):
            os.environ[name] = self.values.get(name, "")
        os.environ["GLYCOLENS_DELETION_CLEANUP_WORKER"] = "0"
        from fastapi.testclient import TestClient
        from backend.app.main import app
        from backend.app.services import account_deletion as deletion

        a, b = self.create_user("a"), self.create_user("b")
        ha, hb = ({"Authorization": "Bearer " + owner["token"]} for owner in (a, b))
        with TestClient(app) as api:
            source_ids, meal_ids, forecast_ids = [], [], []
            for owner, headers in ((a, ha), (b, hb)):
                assert api.post("/api/v1/me/bootstrap", headers=headers, json={}).status_code == 200
                self.insert("notice_acknowledgements", {"user_id": owner["id"], "notice_version": "research-v1"})
                self.insert("nutrition_goals", {"user_id": owner["id"], "nutrient": "fiber_g", "target": 20, "unit": "g", "effective_date": "2026-01-01"})
                sid = str(uuid4()); source_ids.append(sid)
                # Deliberately simple synthetic DB fixtures: no forecast accuracy claim.
                self.insert("source_sessions", {"id": sid, "user_id": owner["id"], "mode": "simulation", "clock_at": "2026-01-01T12:00:00Z", "metadata": {"synthetic": True, "test_run": self.run.run_id}})
                directory = deletion.SOURCE_ROOT / sid
                directory.mkdir(parents=True, exist_ok=False)
                (directory / "context.json").write_text("synthetic deletion fixture", encoding="utf-8")
                for table, extra in (("cgm_readings", {"glucose_mg_dl": 120}), ("insulin_events", {"units": 0, "event_type": "basal"}), ("activity_events", {"steps": 10})):
                    self.insert(table, {"user_id": owner["id"], "source_session_id": sid, "recorded_at": "2026-01-01T11:55:00Z", "source": "synthetic_test", **extra})
                body = {"name": "Synthetic deletion meal", "recorded_at": "2026-01-01T12:00:00Z", "confirmed": True, "idempotency_key": str(uuid4()), "items": [{"food_id": "00000000-0000-4000-8000-000000000001", "grams": 100}]}
                meal = api.post("/api/v1/meals", headers=headers, json=body)
                assert meal.status_code == 200
                mid = meal.json()["meal_id"]; meal_ids.append(mid)
                fid = str(uuid4()); forecast_ids.append(fid)
                self.insert("forecasts", {"id": fid, "user_id": owner["id"], "meal_id": mid, "source_session_id": sid, "meal_revision": 1, "model_id": "synthetic-deletion-fixture", "model_version": "test-only", "context_config": "C3", "horizon_minutes": 120, "quantiles_json": [0.1, 0.5, 0.9], "input_snapshot": {"synthetic": True}})
                self.insert("forecast_points", {"forecast_id": fid, "forecast_at": "2026-01-01T12:05:00Z", "q10": 100, "q50": 120, "q90": 150})
                self.insert("portion_scenarios", {"user_id": owner["id"], "forecast_id": fid, "multiplier": 0.75, "idempotency_key": str(uuid4()), "response": {"synthetic": True}})
                self.insert("meal_outcomes", {"meal_id": mid, "actual_30": 120})

            # Live private seed/check is optional so ordinary users can run this
            # harness without an MCP operator. This run explicitly enables it.
            marker = ROOT / ".cache/cloud-tests" / (self.run.run_id + "-private-seed.json")
            ready = ROOT / ".cache/deletion-fixture-ready.json"
            if os.environ.get("GLYCOLENS_PRIVATE_DELETION_FIXTURE") == "1":
                ready.write_text(json.dumps({"run_id": self.run.run_id, "users": [a["id"], b["id"]], "marker": str(marker.relative_to(ROOT))}), encoding="utf-8")
                print("Awaiting run-scoped private synthetic fixture seed", flush=True)
                deadline = time.monotonic() + 180
                while not marker.exists() and time.monotonic() < deadline:
                    time.sleep(0.5)
                assert marker.exists(), "Private fixture handshake timed out"
                assert json.loads(marker.read_text())["run_id"] == self.run.run_id

            denied = api.request("DELETE", "/api/v1/me", json={"password": a["password"], "confirmation": "DELETE"})
            assert denied.status_code == 401
            for body in ({"password": a["password"], "confirmation": "delete"}, {"password": a["password"], "confirmation": "DELETE", "user_id": b["id"]}):
                assert api.request("DELETE", "/api/v1/me", headers=ha, json=body).status_code == 422
            assert api.request("DELETE", "/api/v1/me", headers=ha, json={"password": b["password"], "confirmation": "DELETE"}).status_code == 403
            self.record("GL-P08-006", "Missing session, incorrect confirmation, foreign owner and B password under A token did not delete either account")

            for rpc in ("app_deletion_artifacts", "app_reserve_deletion_attempt"):
                assert self.request("POST", "/rest/v1/rpc/" + rpc, token=b["token"], body={} if rpc.endswith("artifacts") else {"p_user": a["id"]}).status_code in {401, 403}
            for _ in range(5):
                result = self.request("POST", "/rest/v1/rpc/app_reserve_deletion_attempt", admin=True, body={"p_user": b["id"]})
                assert result.status_code in {200, 204}
            assert self.request("POST", "/rest/v1/rpc/app_reserve_deletion_attempt", admin=True, body={"p_user": b["id"]}).status_code == 429
            self.record("GL-P08-006", "Service-only deletion RPCs denied caller JWT; atomic sixth reauthentication reservation was rate-limited")

            login = self.request("POST", "/auth/v1/token?grant_type=password", body={"email": a["email"], "password": a["password"]}).json()
            # Capture shared replay bytes, without reading/publishing their content.
            import hashlib
            shared = deletion.SOURCE_ROOT.parent / "scenario.json"
            shared_before = hashlib.sha256(shared.read_bytes()).hexdigest() if shared.exists() else None
            with patch.object(deletion, "remove_source_artifacts", side_effect=OSError("synthetic storage failure")):
                removed = api.request("DELETE", "/api/v1/me", headers=ha, json={"password": a["password"], "confirmation": "DELETE"})
            assert removed.status_code == 200 and removed.json() == {"deleted": True, "file_cleanup_pending": True}
            assert removed.headers["cache-control"] == "private, no-store"
            assert api.get("/api/v1/me", headers=ha).status_code == 401
            assert api.request("DELETE", "/api/v1/me", headers=ha, json={"password": a["password"], "confirmation": "DELETE"}).status_code == 401
            assert self.request("GET", "/auth/v1/admin/users/" + a["id"], admin=True).status_code == 404
            assert self.request("POST", "/auth/v1/token?grant_type=password", body={"email": a["email"], "password": a["password"]}).status_code == 400
            assert self.request("POST", "/auth/v1/token?grant_type=refresh_token", body={"refresh_token": login["refresh_token"]}).status_code == 400
            assert self.request("POST", "/rest/v1/rpc/current_session_active", token=login["access_token"], body={}).json() is False
            assert self.request("GET", "/rest/v1/foods?select=id&limit=1", token=a["token"]).json() == []
            self.record("GL-P08-006", "Hard deletion removed managed Auth identity, blocked old and second-session JWT access, refresh and fresh password login; retry was denied, with no recovery window")

            for table in ("users", "user_preferences", "onboarding_state", "notice_acknowledgements", "nutrition_goals", "source_sessions", "meals", "meal_revisions", "cgm_readings", "insulin_events", "activity_events", "forecasts", "notifications", "portion_scenarios"):
                key = "id" if table == "users" else "user_id"
                assert self.request("GET", f"/rest/v1/{table}?{key}=eq.{a['id']}&select=*", admin=True).json() == [], table
                assert self.request("GET", f"/rest/v1/{table}?{key}=eq.{b['id']}&select=*", admin=True).json(), table
            for table, key, ids in (("meal_items", "meal_id", meal_ids), ("meal_outcomes", "meal_id", meal_ids), ("forecast_points", "forecast_id", forecast_ids)):
                assert self.request("GET", f"/rest/v1/{table}?{key}=eq.{ids[0]}&select=*", admin=True).json() == []
                assert self.request("GET", f"/rest/v1/{table}?{key}=eq.{ids[1]}&select=*", admin=True).json()
            assert api.get("/api/v1/me", headers=hb).status_code == 200
            self.record("GL-P08-006", "All populated owned public and child records disappeared for A; B remained populated and usable")

            assert (deletion.SOURCE_ROOT / source_ids[0]).exists()
            assert deletion.drain_artifact_cleanup()
            assert not (deletion.SOURCE_ROOT / source_ids[0]).exists()
            assert (deletion.SOURCE_ROOT / source_ids[1] / "context.json").exists()
            assert self.request("POST", "/rest/v1/rpc/app_deletion_artifacts", admin=True, body={}).json() == []
            assert (hashlib.sha256(shared.read_bytes()).hexdigest() if shared.exists() else None) == shared_before
            self.record("GL-P08-006", "Injected storage failure retained a durable source-UUID-only job; retry removed only A directory, acknowledged the job, preserved B and shared replay")

    def cleanup(self):
        super().cleanup()
        from backend.app.services.account_deletion import drain_artifact_cleanup
        assert drain_artifact_cleanup(), "Synthetic private file cleanup remains pending"


if __name__ == "__main__":
    raise SystemExit(run_harness(DeletionHarness, __doc__, "immediate-account-deletion"))
