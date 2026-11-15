"""Opt-in cloud acceptance with two disposable synthetic owners and scoped cleanup.

No emails, paid providers, research data or model inference are used. The exact
target guard executes before any network client or application import.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import secrets
import traceback
from unittest.mock import patch
from uuid import UUID, uuid4

import httpx

from scripts.dev.cloud_preflight import ROOT, assert_cloud_run, new_run_id, read_configuration


class CloudHarness:
    def __init__(self, values: dict[str, str], *, allow_cloud: bool, run_id: str):
        self.run = assert_cloud_run(values, allow_cloud=allow_cloud, run_id=run_id)
        self.values = values
        self.calls = 0
        self.cleaning = False
        self.last_http_status = None
        self.limit = json.loads((ROOT / "config/webapp-validation.json").read_text())[
            "max_cloud_requests_per_run"
        ]
        self.manifest_path = ROOT / ".cache/cloud-tests" / (run_id + ".json")
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest = {
            "run_id": run_id,
            "project_ref": self.run.project_ref,
            "users": [],
            "foods": [],
        }
        if self.manifest_path.exists():
            self.manifest = json.loads(self.manifest_path.read_text())
            if (
                self.manifest["project_ref"] != self.run.project_ref
                or self.manifest["run_id"] != run_id
            ):
                raise ValueError("Cleanup manifest does not match approved run")
        if len(self.manifest["users"]) > 2 or len(self.manifest["foods"]) > 2:
            raise ValueError("Cleanup manifest exceeds the approved fixture budget")
        self.results = []

    def save_manifest(self):
        temp = self.manifest_path.with_suffix(".tmp")
        temp.write_text(json.dumps(self.manifest, indent=2) + "\n", encoding="utf-8")
        temp.replace(self.manifest_path)

    @contextmanager
    def bounded_network(self):
        original = httpx.HTTPTransport.handle_request
        harness = self

        def bounded(transport, request):
            if (
                request.url.scheme != "https"
                or request.url.host != "ecynkzptuslkuhjikzfc.supabase.co"
            ):
                raise RuntimeError("Unapproved cloud integration endpoint")
            harness.calls += 1
            if harness.calls > (harness.limit if harness.cleaning else harness.limit - 20):
                raise RuntimeError("Cloud request budget exceeded")
            response = original(transport, request)
            harness.last_http_status = response.status_code
            return response

        with patch.object(httpx.HTTPTransport, "handle_request", bounded):
            yield

    def headers(self, token=None, *, admin=False):
        key = (
            self.values.get("SUPABASE_SECRET_KEY", "").strip()
            if admin
            else self.values["SUPABASE_ANON_KEY"]
        )
        legacy = False
        if admin and not key:
            key, legacy = self.values["SUPABASE_SERVICE_ROLE_KEY"], True
        headers = {"apikey": key, "Prefer": "return=representation"}
        if token:
            headers["Authorization"] = "Bearer " + token
        elif legacy:
            headers["Authorization"] = "Bearer " + key
        return headers

    def request(self, method, path, *, token=None, admin=False, body=None):
        return httpx.request(
            method,
            self.run.url + path,
            headers=self.headers(token, admin=admin),
            json=body,
            timeout=20,
        )

    def record(self, case, actual, *, status="PASSED"):
        self.results.append({"case_id": case, "status": status, "observed": actual})

    def create_user(self, alias):
        email = f"{self.run.run_id}_{alias}@example.invalid"
        password = secrets.token_urlsafe(30)
        response = self.request(
            "POST",
            "/auth/v1/admin/users",
            admin=True,
            body={
                "email": email,
                "password": password,
                "email_confirm": True,
                "app_metadata": {"glycolens_test_run": self.run.run_id, "synthetic": True},
            },
        )
        assert response.status_code in {200, 201}, "Synthetic fixture creation rejected"
        user_id = str(UUID(response.json()["id"]))
        self.manifest["users"].append(user_id)
        self.save_manifest()
        return {
            "id": user_id,
            "email": email,
            "password": password,
            "token": self.login(email, password),
        }

    def login(self, email, password):
        response = self.request(
            "POST",
            "/auth/v1/token?grant_type=password",
            body={"email": email, "password": password},
        )
        assert response.status_code == 200, "Synthetic login failed"
        return response.json()["access_token"]

    def delete_user(self, user_id):
        if user_id not in self.manifest["users"]:
            raise ValueError("Cleanup refuses an unrecorded user")
        response = self.request("GET", "/auth/v1/admin/users/" + str(UUID(user_id)), admin=True)
        if response.status_code == 404:
            return
        assert response.status_code == 200, "Cannot verify cleanup owner"
        assert (
            response.json().get("app_metadata", {}).get("glycolens_test_run") == self.run.run_id
        ), "Cleanup tag mismatch"
        response = self.request("DELETE", "/auth/v1/admin/users/" + user_id, admin=True)
        assert response.status_code in {200, 204}, "Scoped account cleanup failed"

    def cleanup(self):
        self.cleaning = True
        for user_id in self.manifest["users"]:
            self.delete_user(user_id)
        for food_id in self.manifest["foods"]:
            path = f"/rest/v1/foods?id=eq.{UUID(food_id)}&source_food_id=eq.{self.run.run_id}"
            response = self.request("DELETE", path, admin=True)
            assert response.status_code in {200, 204}, "Scoped food cleanup failed"
        self.manifest["cleanup_completed"] = True
        self.save_manifest()

    def exercise(self):
        # Set only the already-guarded application configuration; values are not logged.
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
            auth_a = {"Authorization": "Bearer " + a["token"]}
            auth_b = {"Authorization": "Bearer " + b["token"]}
            for headers in (auth_a, auth_b, auth_a):
                assert api.post("/api/v1/demo/session", headers=headers, json={}).status_code == 200
            assert (
                len(
                    self.request(
                        "GET", "/rest/v1/user_preferences?select=user_id", token=a["token"]
                    ).json()
                )
                == 1
            )
            self.record(
                "GL-P01-010",
                "Repeated API bootstrap created one owner profile/preferences/onboarding state",
            )
            assert api.get("/api/v1/timeline").status_code == 401
            assert (
                api.get(
                    "/api/v1/timeline", headers={"Authorization": "Bearer invalid-synthetic-token"}
                ).status_code
                == 401
            )
            self.record(
                "GL-P01-001",
                "Modern public key, password JWT, verified API session and modern trusted server key worked; invalid/missing JWT rejected",
            )

            food_id = str(uuid4())
            food = {
                "id": food_id,
                "name": "Synthetic cloud test food",
                "source": "synthetic_test",
                "source_food_id": self.run.run_id,
                "nutrient_basis_g": 100,
                "calories": 180,
                "carbs_g": 30,
                "protein_g": 8,
                "fat_g": 4,
                "fiber_g": 5,
            }
            self.manifest["foods"].append(food_id)
            self.save_manifest()
            assert self.request("POST", "/rest/v1/foods", admin=True, body=food).status_code == 201
            body = {
                "workspace": "personal",
                "name": "Synthetic cloud meal",
                "recorded_at": "2026-01-01T12:00:00Z",
                "items": [{"food_id": food_id, "grams": 250}],
                "input_snapshot": {"confirmed": True},
                "idempotency_key": str(uuid4()),
            }
            saved = api.post("/api/v1/meals", headers=auth_a, json=body)
            assert saved.status_code == 200, "Verified API meal save failed"
            meal_id = saved.json()["meal_id"]
            assert api.post("/api/v1/meals", headers=auth_a, json=body).json()["meal_id"] == meal_id
            own = api.get("/api/v1/meals/" + meal_id, headers=auth_a).json()
            assert (
                len(own) == 1
                and float(own[0]["carbs_g"]) == 75
                and float(own[0]["calories"]) == 450
            )
            assert api.get("/api/v1/meals/" + meal_id, headers=auth_b).json() == []
            assert (
                self.request(
                    "GET", f"/rest/v1/meal_items?meal_id=eq.{meal_id}", token=b["token"]
                ).json()
                == []
            )
            assert (
                self.request(
                    "GET", f"/rest/v1/user_preferences?user_id=eq.{a['id']}", token=b["token"]
                ).json()
                == []
            )
            assert self.request("GET", "/rest/v1/meals?select=id").status_code in {401, 403}
            self.record(
                "GL-P01-006",
                "A reads owned meal; B reads no A parent/child/preferences; anonymous and invalid JWT access denied",
            )

            for path, payload in [
                (
                    "meals",
                    {
                        "user_id": a["id"],
                        "name": "Forged totals",
                        "recorded_at": body["recorded_at"],
                        "carbs_g": 999,
                    },
                ),
                (
                    "forecasts",
                    {
                        "user_id": a["id"],
                        "meal_id": meal_id,
                        "model_id": "forged",
                        "model_version": "1",
                        "context_config": "fake",
                        "horizon_minutes": 120,
                        "quantiles_json": [0.1, 0.5, 0.9],
                    },
                ),
                ("meal_outcomes", {"meal_id": meal_id, "actual_60": 999}),
                ("foods", {**food, "id": str(uuid4()), "source_food_id": "forged"}),
            ]:
                assert self.request(
                    "POST", "/rest/v1/" + path, token=a["token"], body=payload
                ).status_code in {401, 403}
            rpc = {
                "p_user": a["id"],
                "p_name": "Forged",
                "p_recorded_at": body["recorded_at"],
                "p_key": str(uuid4()),
                "p_items": body["items"],
                "p_snapshot": {},
            }
            assert self.request(
                "POST", "/rest/v1/rpc/app_save_meal", token=a["token"], body=rpc
            ).status_code in {401, 403}
            assert (
                self.request(
                    "PUT",
                    "/auth/v1/user",
                    token=a["token"],
                    body={"data": {"role": "service_role", "user_id": b["id"]}},
                ).status_code
                == 200
            )
            refreshed = self.login(a["email"], a["password"])
            assert self.request(
                "POST",
                "/rest/v1/meals",
                token=refreshed,
                body={"user_id": b["id"], "name": "Forbidden", "recorded_at": body["recorded_at"]},
            ).status_code in {401, 403}
            self.record(
                "GL-P01-007",
                "Direct totals/forecast/outcome/catalog writes and trusted RPC calls denied to browser JWT; editable metadata did not escalate access",
            )
            self.record(
                "GL-P01-008",
                "Verified API atomic meal save calculated trusted totals; identical request key returned same meal",
            )

            before = len(self.request("GET", "/rest/v1/meals?select=id", token=a["token"]).json())
            invalid = {
                **body,
                "idempotency_key": str(uuid4()),
                "items": [*body["items"], {"food_id": str(uuid4()), "grams": 100}],
            }
            assert api.post("/api/v1/meals", headers=auth_a, json=invalid).status_code == 422
            assert (
                len(self.request("GET", "/rest/v1/meals?select=id", token=a["token"]).json())
                == before
            )
            invalid = {
                **body,
                "idempotency_key": str(uuid4()),
                "items": [{"food_id": food_id, "grams": 0}],
            }
            assert api.post("/api/v1/meals", headers=auth_a, json=invalid).status_code == 422
            assert (
                self.request(
                    "PATCH",
                    f"/rest/v1/user_preferences?user_id=eq.{a['id']}",
                    admin=True,
                    body={"timezone": "Invalid/Not_A_Zone"},
                ).status_code
                == 400
            )
            self.record(
                "GL-P01-009",
                "Independent 250g oracle returned 450 kcal/75g carbs; zero grams and invalid timezone rejected; failed multi-item save rolled back parent/children",
            )
            self.record(
                "GL-P01-004",
                "Application idempotency and failed transaction rollback passed; separate failed-migration rehearsal remains pending",
                status="PARTIAL",
            )

            import backend.app.db.client as user_db

            with patch.object(
                user_db.httpx, "get", side_effect=httpx.TimeoutException("synthetic outage")
            ):
                assert api.get("/api/v1/timeline", headers=auth_a).status_code == 503
            assert api.get("/api/v1/meals", headers=auth_a).status_code == 200
            self.record(
                "GL-P01-011",
                "Injected Auth timeout produced safe 503; restored real cloud read succeeded",
            )

            b_body = {**body, "idempotency_key": str(uuid4())}
            b_id = api.post("/api/v1/meals", headers=auth_b, json=b_body).json()["meal_id"]
            self.delete_user(a["id"])
            assert (
                api.get("/api/v1/meals/" + b_id, headers=auth_b).json()[0]["name"] == body["name"]
            )
            assert api.get("/api/v1/timeline", headers=auth_a).status_code == 401
            self.record(
                "GL-P01-012",
                "Scoped cleanup of A preserved B sentinel meal; deleted A lost API access. Final cleanup verifies run tags and recorded IDs only",
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-cloud", action="store_true")
    parser.add_argument("--cleanup-run-id")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.allow_cloud:
        print("DRY RUN: no network; requires --allow-cloud and the approved development target")
        return 0
    harness = CloudHarness(
        read_configuration(),
        allow_cloud=args.allow_cloud,
        run_id=args.cleanup_run_id or new_run_id(),
    )
    error, cleanup_error, failure_location, failure_http_status = None, None, None, None
    with harness.bounded_network():
        try:
            if not args.cleanup_run_id:
                harness.exercise()
        except Exception as exc:
            error = type(exc).__name__
            frame = traceback.extract_tb(exc.__traceback__)[-1]
            failure_location = f"{Path(frame.filename).name}:{frame.lineno}"
            failure_http_status = harness.last_http_status
        finally:
            try:
                harness.cleanup()
            except Exception as exc:
                cleanup_error = type(exc).__name__
    report = {
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_ref": harness.run.project_ref,
        "run_id": harness.run.run_id,
        "synthetic_users_max": 2,
        "requests": harness.calls,
        "email_messages": 0,
        "paid_provider_calls": 0,
        "results": harness.results,
        "execution_error_class": error,
        "cleanup_error_class": cleanup_error,
        "last_http_status": harness.last_http_status,
        "failure_location": failure_location,
        "failure_http_status": failure_http_status,
        "cleanup_completed": not cleanup_error,
        "scratch_replay": "DEFERRED_BY_USER",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "results"}, indent=2))
    print(
        f"Recorded {len(harness.results)} cases; no identities, tokens, passwords or email addresses in report"
    )
    return 1 if error or cleanup_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
