"""Real cloud session/onboarding acceptance; no email delivery or paid providers."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import traceback

from scripts.dev.cloud_integration import CloudHarness
from scripts.dev.cloud_preflight import read_configuration, new_run_id


class AccountHarness(CloudHarness):
    def exercise(self):
        import os

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
            headers = {"Authorization": "Bearer " + a["token"]}
            other = {"Authorization": "Bearer " + b["token"]}

            def call(method, path, body=None):
                return api.request(method, "/api/v1/me" + path, headers=headers, json=body)

            assert api.get("/api/v1/me").status_code == 401
            for auth in (headers, other):
                assert api.post("/api/v1/me/bootstrap", headers=auth, json={}).status_code == 200
            me = call("GET", "").json()
            assert me["user_id"] == a["id"] and me["onboarding"]["step"] == "preferences"
            assert (
                call(
                    "POST",
                    "/onboarding/complete",
                    {"revision": 0, "notice_version": "research-v1", "acknowledged": True},
                ).status_code
                == 422
            )
            assert (
                call(
                    "PATCH",
                    "/onboarding",
                    {"revision": 0, "step": "source", "values": {"source_mode": "simulation"}},
                ).status_code
                == 422
            )
            result = call(
                "PATCH",
                "/onboarding",
                {
                    "revision": 0,
                    "step": "preferences",
                    "values": {"timezone": "America/New_York", "glucose_unit": "mmol/L"},
                },
            )
            assert result.status_code == 200
            me = result.json()
            assert (
                me["onboarding"]["step"] == "source"
                and me["preferences"]["timezone"] == "America/New_York"
            )
            assert (
                call(
                    "PATCH",
                    "/onboarding",
                    {"revision": 0, "step": "source", "values": {"source_mode": "simulation"}},
                ).status_code
                == 409
            )
            self.record(
                "GL-P03-010",
                "Server rejected skipping required setup; accepted explicit IANA timezone/unit confirmation",
            )
            self.record(
                "GL-P03-014",
                "Stale onboarding revision returned HTTP 409 without overwriting saved values",
            )

            # Exercise actual refresh and local logout. A second A session exists,
            # so the check must match this session_id rather than any session of A.
            details = self.request(
                "POST",
                "/auth/v1/token?grant_type=password",
                body={"email": a["email"], "password": a["password"]},
            ).json()
            refreshed = self.request(
                "POST",
                "/auth/v1/token?grant_type=refresh_token",
                body={"refresh_token": details["refresh_token"]},
            )
            assert refreshed.status_code == 200
            active_token = refreshed.json()["access_token"]
            active_headers = {"Authorization": "Bearer " + active_token}
            assert api.get("/api/v1/me", headers=active_headers).status_code == 200
            assert self.request(
                "POST", "/auth/v1/logout?scope=local", token=active_token
            ).status_code in {200, 204}
            assert api.get("/api/v1/me", headers=active_headers).status_code == 401
            assert (
                self.request(
                    "GET", "/rest/v1/user_preferences?select=user_id", token=active_token
                ).json()
                == []
            )
            self.record(
                "GL-P03-006",
                "Real refresh succeeded; logged-out session JWT lost API and direct Data API row access even while another A session existed",
            )
            a["token"] = self.login(a["email"], a["password"])
            headers["Authorization"] = "Bearer " + a["token"]
            me = call("GET", "").json()
            assert (
                me["onboarding"]["step"] == "source"
                and me["preferences"]["glucose_unit"] == "mmol/L"
            )
            self.record(
                "GL-P03-011",
                "Saved progress/timezone/unit survived logout and a fresh password sign-in",
            )
            me = call(
                "PATCH",
                "/onboarding",
                {
                    "revision": me["onboarding"]["revision"],
                    "step": "source",
                    "values": {"source_mode": "simulation"},
                },
            ).json()
            me = call(
                "PATCH",
                "/onboarding",
                {"revision": me["onboarding"]["revision"], "step": "optional", "values": {}},
            ).json()
            assert (
                me["onboarding"]["step"] == "review"
                and me["goals"] == []
                and me["display_name"] == "GlycoLens member"
            )
            self.record(
                "GL-P03-012",
                "Optional nickname/preferences/goals were skipped; no medical/body fields or default nutrition target were required",
            )
            me = call(
                "PATCH",
                "/onboarding",
                {
                    "revision": me["onboarding"]["revision"],
                    "step": "preferences",
                    "values": {"timezone": "Asia/Kolkata", "glucose_unit": "mg/dL"},
                },
            ).json()
            assert (
                me["onboarding"]["step"] == "review"
                and me["preferences"]["timezone"] == "Asia/Kolkata"
            )
            self.record(
                "GL-P03-013",
                "Review edit persisted the new timezone/unit without erasing later completed steps",
            )
            revision = me["onboarding"]["revision"]
            body = {"revision": revision, "notice_version": "research-v1", "acknowledged": True}
            assert (
                call("POST", "/onboarding/complete", {**body, "acknowledged": False}).status_code
                == 422
            )
            assert (
                call("POST", "/onboarding/complete", {**body, "notice_version": "old"}).status_code
                == 422
            )
            me = call("POST", "/onboarding/complete", body).json()
            assert me["onboarding"]["step"] == "complete" and me["onboarding"]["completed_at"]
            assert call("POST", "/onboarding/complete", body).status_code == 200
            acknowledgements = self.request(
                "GET", "/rest/v1/notice_acknowledgements?select=notice_version", token=a["token"]
            ).json()
            assert acknowledgements == [{"notice_version": "research-v1"}]
            assert (
                self.request(
                    "GET",
                    f"/rest/v1/notice_acknowledgements?user_id=eq.{a['id']}",
                    token=b["token"],
                ).json()
                == []
            )
            self.record(
                "GL-P03-016",
                "Completion required the current acknowledged notice; repeat completion was idempotent and acknowledgement was owner-scoped",
            )
            me = call("GET", "").json()
            pref = me["preferences"]["revision"]
            updated = call(
                "PATCH",
                "/preferences",
                {"revision": pref, "display_name": "Synthetic nickname", "glucose_unit": "mmol/L"},
            )
            assert (
                updated.status_code == 200
                and updated.json()["display_name"] == "Synthetic nickname"
            )
            assert (
                call(
                    "PATCH", "/preferences", {"revision": pref, "glucose_unit": "mg/dL"}
                ).status_code
                == 409
            )
            other_me = api.get("/api/v1/me", headers=other).json()
            assert (
                other_me["display_name"] == "GlycoLens member"
                and not other_me["onboarding"]["completed_at"]
            )
            assert self.request(
                "PATCH",
                f"/rest/v1/onboarding_state?user_id=eq.{a['id']}",
                token=a["token"],
                body={"completed_at": "2026-01-01T00:00:00Z"},
            ).status_code in {401, 403}
            self.record(
                "GL-P03-003",
                "Real password sign-in returned independent completed/incomplete account states for routing; browser routing covered separately",
            )
            self.record(
                "GL-P03-007",
                "Logout revoked the selected session and A updates did not appear in B; client cache clearing covered separately",
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-cloud", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.allow_cloud:
        print("DRY RUN: no network; pass --allow-cloud for the approved synthetic cloud checks")
        return 0
    harness = AccountHarness(read_configuration(), allow_cloud=True, run_id=new_run_id())
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
    report = {
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": harness.run.run_id,
        "project_ref": harness.run.project_ref,
        "requests": harness.calls,
        "email_messages": 0,
        "paid_provider_calls": 0,
        "results": harness.results,
        "execution_error_class": error,
        "failure_location": location,
        "cleanup_error_class": cleanup_error,
        "cleanup_completed": not cleanup_error,
        "email_verification_and_recovery": "NOT_RUN_SMTP_DEFERRED",
        "anonymous_upgrade": "NOT_RUN_REQUIRES_VERIFIED_LINKING",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "results"}, indent=2))
    print(
        f"Recorded {len(harness.results)} account cases; no private identities/credentials in evidence"
    )
    return 1 if error or cleanup_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
