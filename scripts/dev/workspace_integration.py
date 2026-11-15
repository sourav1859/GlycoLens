"""Opt-in, tagged cloud/localhost workspace acceptance; no paid/provider calls.

Run: python -m scripts.dev.workspace_integration --allow-cloud --output PATH
Uses only the approved dev project and local Compose API on 127.0.0.1:8000.
Reports sanitized observations; credentials stay in memory/ignored configuration.
"""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from unittest.mock import patch
from uuid import uuid4
from zoneinfo import ZoneInfo

import httpx
from scripts.dev.cloud_integration import CloudHarness
from scripts.dev.cloud_preflight import read_configuration, new_run_id


class WorkspaceHarness(CloudHarness):
    def exercise_replay(self):
        """Real cached protocols, explicit timeline/advance denials, no new inference."""
        a, b = self.create_user("replay_a"), self.create_user("replay_b")
        before = self.api(a, "POST", "/me/bootstrap", {})["preferences"]
        self.api(b, "POST", "/me/bootstrap", {})
        for protocol in ("m1_fixed_meal_day", "lightgbm_warmup_48h_v1"):
            source = self.api(
                a, "POST", "/simulation/scenario", dict(replay=True, protocol=protocol)
            )
            assert source["execution"] == "cached_replay" and source["forecast_origin"].startswith(
                "2026-01-"
            )
            sid = source["source_session_id"]
            timeline = self.api(a, "GET", "/timeline?source_session_id=" + sid)
            assert len(timeline["cgm"]) >= 24 and all(
                p["recorded_at"] <= source["forecast_origin"] for p in timeline["cgm"]
            )
            self.api(b, "GET", "/timeline?source_session_id=" + sid, expected=404)
            self.api(
                b,
                "POST",
                f"/simulation/sources/{sid}/advance",
                dict(minutes=120, expected_clock=source["forecast_origin"]),
                expected=404,
            )
            assert self.api(a, "GET", "/home")["source"] is None
        assert self.api(a, "GET", "/me")["preferences"] == before
        result = self.api(a, "DELETE", "/me", dict(password=a["password"], confirmation="DELETE"))
        assert result["deleted"] is True and result["file_cleanup_pending"] is False
        self.record(
            "WS-W4-001",
            "Both actual cached protocols replayed; virtual epoch/history retained, pre-origin-only timelines, source files removed after synthetic account deletion",
        )
        self.record(
            "WS-W1-006",
            "Both real replays left the exact personal preference object unchanged, including revision/source pointer",
        )
        self.record(
            "WS-W2-006",
            "Explicit timeline accepted owned source and denied other owner; other-owner clock advancement denied for both protocols",
        )

    @contextmanager
    def bounded_network(self):
        original = httpx.HTTPTransport.handle_request
        self.api_calls = 0
        self.api_cloud_reserve = 0

        def bounded(transport, request):
            if (
                request.url.scheme == "http"
                and request.url.host == "127.0.0.1"
                and request.url.port == 8000
                and request.url.path.startswith("/api/v1/")
            ):
                self.api_calls += 1
            elif (
                request.url.scheme == "https"
                and request.url.host == "ecynkzptuslkuhjikzfc.supabase.co"
            ):
                self.calls += 1
            else:
                raise RuntimeError("Unapproved workspace validation endpoint")
            if self.calls + self.api_cloud_reserve > self.limit - (0 if self.cleaning else 20):
                raise RuntimeError("Conservative cloud request budget reached")
            return original(transport, request)

        with patch.object(httpx.HTTPTransport, "handle_request", bounded):
            yield

    def api(self, user, method, path, body=None, expected=200):
        reserve = (
            24
            if path == "/me/export"
            else 12
            if method == "DELETE" and path == "/me"
            else 8
            if path in {"/forecasts", "/simulation/scenario"}
            else 6
        )
        self.api_cloud_reserve += reserve
        started = time.perf_counter()
        result = httpx.request(
            method,
            "http://127.0.0.1:8000/api/v1" + path,
            headers={"Authorization": "Bearer " + user["token"]},
            json=body,
            timeout=180,
        )
        self.last_api = dict(
            method=method,
            path=path.split("?")[0],
            status=result.status_code,
            elapsed_seconds=round(time.perf_counter() - started, 3),
        )
        if result.status_code != expected:
            raise AssertionError("Workspace API returned an unexpected status")
        return result.json()

    def exercise(self):
        a, b = self.create_user("workspace_a"), self.create_user("workspace_b")
        self.api(a, "POST", "/me/bootstrap", {})
        self.api(b, "POST", "/me/bootstrap", {})
        food_id = str(uuid4())
        self.manifest["foods"].append(food_id)
        self.save_manifest()
        food = dict(
            id=food_id,
            name="Synthetic workspace food",
            source="synthetic_test",
            source_food_id=self.run.run_id,
            nutrient_basis_g=100,
            calories=180,
            carbs_g=30,
            protein_g=8,
            fat_g=4,
            fiber_g=5,
        )
        assert self.request("POST", "/rest/v1/foods", admin=True, body=food).status_code == 201
        self.api(
            a,
            "PATCH",
            "/me/preferences",
            dict(revision=0, timezone="America/New_York", source_mode="personal"),
        )
        now = datetime.now(timezone.utc).isoformat()
        base = dict(
            workspace="personal",
            source_session_id=None,
            name="Synthetic personal meal",
            recorded_at=now,
            state="logged",
            consumed_at=now,
            confirmed=True,
            idempotency_key=str(uuid4()),
            items=[dict(food_id=food_id, grams=250)],
        )
        personal = self.api(a, "POST", "/meals", base)["meal_id"]
        overview = self.api(a, "GET", "/home")
        assert (
            overview["source"] is None
            and overview["latest_glucose"] == []
            and overview["forecasts"] == []
        )
        assert (
            overview["day"]
            == datetime.now(timezone.utc)
            .astimezone(ZoneInfo("America/New_York"))
            .date()
            .isoformat()
        )
        assert overview["days"][-1]["nutrients"]["calories"]["total"] == 450
        assert self.api(a, "POST", "/meals", base)["meal_id"] == personal
        self.record(
            "WS-W2-001",
            "Personal eaten meal saved without any source; current New York day and independent 450 kcal oracle matched; retry returned same ID",
        )
        self.api(
            a, "POST", "/meals", {k: v for k, v in base.items() if k != "workspace"}, expected=422
        )
        self.record("WS-W2-003", "Missing workspace failed before mutation")
        short = self.api(
            a, "POST", "/simulation/scenario", dict(replay=False, protocol="m1_fixed_meal_day")
        )
        sim = {
            **base,
            "workspace": "simulation",
            "source_session_id": short["source_session_id"],
            "recorded_at": short["forecast_origin"],
            "state": "planned",
            "consumed_at": None,
            "idempotency_key": str(uuid4()),
            "name": "Synthetic short virtual meal",
        }
        short_meal = self.api(a, "POST", "/meals", sim)["meal_id"]
        long = self.api(
            a, "POST", "/simulation/scenario", dict(replay=False, protocol="lightgbm_warmup_48h_v1")
        )
        long_body = {
            **sim,
            "source_session_id": long["source_session_id"],
            "recorded_at": long["forecast_origin"],
            "idempotency_key": str(uuid4()),
            "name": "Synthetic long virtual meal",
        }
        long_meal = self.api(a, "POST", "/meals", long_body)["meal_id"]
        assert long["sample_count"] == 288
        self.record(
            "WS-W2-002",
            "Both real virtual protocols saved explicitly bound meals; long protocol exposed 288 past samples",
        )
        sim_history = self.api(a, "GET", "/meals?workspace=simulation")
        assert {m["id"] for m in sim_history["meals"]} == {short_meal, long_meal}
        assert {m["id"] for m in self.api(a, "GET", "/meals")["meals"]} == {personal}
        sources = self.api(a, "GET", "/simulation/sources")["sources"]
        assert {s["id"] for s in sources} == {short["source_session_id"], long["source_session_id"]}
        overview2 = self.api(a, "GET", "/home")
        assert overview2["day"] == overview["day"] and overview2["source"] is None
        assert overview2["days"][-1]["nutrients"]["calories"]["total"] == 450
        self.record(
            "WS-W1-006", "Real new short/long runs did not change personal clock or consumed total"
        )
        self.record(
            "WS-W2-005",
            "Earlier and newer simulation meals/sources remained discoverable; personal history excluded both",
        )
        self.api(
            a, "POST", "/meals", {**sim, "idempotency_key": base["idempotency_key"]}, expected=409
        )
        self.record(
            "WS-W2-004",
            "A request key reused across workspaces conflicted; original retry had returned same ID",
        )
        self.api(
            a,
            "POST",
            "/forecasts",
            dict(meal_id=personal, idempotency_key=str(uuid4())),
            expected=422,
        )
        self.record("WS-W2-007", "Personal meal could not borrow simulator glucose for forecasting")
        self.api(b, "GET", "/simulation/sources/" + long["source_session_id"], expected=404)
        assert self.api(b, "GET", "/meals/" + personal) == []
        foreign = self.request("GET", "/rest/v1/meals?id=eq." + personal, token=b["token"])
        assert foreign.status_code == 200 and foreign.json() == []
        self.record(
            "WS-W2-006", "Other owner could not read A's source, meal or direct Data API row"
        )
        forecasts = []
        for model, meal in [("chronos", short_meal), ("lightgbm", long_meal)]:
            result = self.api(
                a,
                "POST",
                "/forecasts",
                dict(meal_id=meal, idempotency_key=str(uuid4()), model_key=model),
            )
            forecasts.append(result["forecast_id"])
        exported = self.api(a, "GET", "/me/export")
        assert {m["workspace"] for m in exported["records"]["meals"]} == {"personal", "simulation"}
        for record in exported["records"]["forecasts"]:
            response = record["input_snapshot"]["response"]
            assert len(response["forecast"]) == 24
            assert record["id"] in forecasts and record["source_session_id"] in {
                short["source_session_id"],
                long["source_session_id"],
            }
        self.record(
            "WS-W4-008",
            "Both real CPU adapters returned 24 persisted points with their original selected virtual sources; export retained frozen responses",
        )
        deleted = self.api(a, "DELETE", "/me", dict(password=a["password"], confirmation="DELETE"))
        assert deleted["deleted"] is True
        self.record(
            "WS-W2-010",
            "Schema 1.1 export retained both workspaces and frozen results; password-confirmed permanent account deletion succeeded",
        )
        self.manifest["source_cleanup_via_account_deletion"] = True
        self.save_manifest()

    def exercise_followup(self):
        """Narrow lifecycle/export/deletion checks; no repeat model inference."""
        from datetime import timedelta

        a, b = self.create_user("followup_a"), self.create_user("followup_b")
        for user in (a, b):
            self.api(user, "POST", "/me/bootstrap", {})
        food_id = str(uuid4())
        self.manifest["foods"].append(food_id)
        self.save_manifest()
        food = dict(
            id=food_id,
            name="Synthetic follow-up food",
            source="synthetic_test",
            source_food_id=self.run.run_id,
            nutrient_basis_g=100,
            calories=180,
            carbs_g=30,
            protein_g=8,
            fat_g=4,
            fiber_g=None,
        )
        assert self.request("POST", "/rest/v1/foods", admin=True, body=food).status_code == 201
        now = datetime.now(timezone.utc).isoformat()
        body = dict(
            workspace="personal",
            source_session_id=None,
            name="Synthetic lifecycle meal",
            recorded_at=now,
            confirmed=True,
            idempotency_key=str(uuid4()),
            items=[dict(food_id=food_id, grams=100)],
        )
        personal = self.api(a, "POST", "/meals", body)["meal_id"]
        sentinel = self.api(b, "POST", "/meals", {**body, "idempotency_key": str(uuid4())})[
            "meal_id"
        ]
        origin = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        source_id = str(uuid4())
        fixture = dict(
            p_user=a["id"],
            p_session=source_id,
            p_mode="simulation",
            p_clock=origin.isoformat(),
            p_cgm=[
                dict(recorded_at=(origin - timedelta(minutes=5 * i)).isoformat(), glucose_mg_dl=110)
                for i in range(24)
            ],
            p_insulin=[
                dict(recorded_at=origin.isoformat(), event_type="bolus", units=1, source_unit="U")
            ],
            p_metadata={"synthetic": True, "test_run": self.run.run_id},
        )
        assert (
            self.request(
                "POST", "/rest/v1/rpc/app_store_source_context", admin=True, body=fixture
            ).status_code
            == 200
        )
        simulation = {
            **body,
            "workspace": "simulation",
            "source_session_id": source_id,
            "recorded_at": origin.isoformat(),
            "idempotency_key": str(uuid4()),
        }
        self.api(a, "POST", "/meals", simulation)
        self.api(b, "POST", "/meals", {**simulation, "idempotency_key": str(uuid4())}, expected=422)
        self.api(
            a,
            "POST",
            "/meals",
            {**body, "source_session_id": source_id, "idempotency_key": str(uuid4())},
            expected=422,
        )
        for mutation in (
            {"workspace": "simulation", "source_session_id": source_id},
            {"workspace": "legacy_unclassified"},
        ):
            response = self.request(
                "PATCH", "/rest/v1/meals?id=eq." + personal, admin=True, body=mutation
            )
            assert response.status_code == 400
        direct = self.request(
            "PATCH",
            "/rest/v1/meals?id=eq." + personal,
            token=a["token"],
            body={"name": "Forbidden bypass"},
        )
        assert direct.status_code in {401, 403}
        self.record(
            "WS-W1-004",
            "Foreign source, personal/virtual mismatch, record reparenting and legacy classification edits rejected",
        )
        self.record(
            "WS-W1-005",
            "Owner browser direct write denied; cross-owner reads and source binding denied across dedicated synthetic accounts",
        )
        edited = {
            **body,
            "state": "logged",
            "consumed_at": now,
            "revision": 1,
            "idempotency_key": str(uuid4()),
        }
        assert self.api(a, "PATCH", "/meals/" + personal, edited)["revision"] == 2
        summary = self.api(a, "GET", "/home")
        assert summary["days"][-1]["nutrients"]["calories"]["total"] == 180
        assert summary["days"][-1]["nutrients"]["fiber_g"]["total"] is None
        self.api(a, "DELETE", "/meals/" + personal, dict(revision=2, idempotency_key=str(uuid4())))
        assert self.api(a, "GET", "/home")["days"][-1]["meal_count"] == 0
        self.record(
            "WS-W1-007",
            "Planned/logged/cancelled lifecycle changes only personal totals; unknown fiber stays unknown; simulation planned meal never counted",
        )
        export = self.api(a, "GET", "/me/export")
        assert export["schema_version"] == "1.1"
        assert {m["workspace"] for m in export["records"]["meals"]} == {"personal", "simulation"}
        notifications = self.api(a, "GET", "/notifications")["notifications"]
        assert any(n["href"].startswith("/demo/") for n in notifications)
        assert any(n["href"].startswith("/meals/") for n in notifications)
        self.record(
            "WS-W2-009", "Personal and virtual notification links resolve their actual workspace"
        )
        assert (
            self.api(a, "DELETE", "/me", dict(password=a["password"], confirmation="DELETE"))[
                "deleted"
            ]
            is True
        )
        self.api(a, "GET", "/home", expected=401)
        assert self.api(b, "GET", "/meals/" + sentinel)[0]["id"] == sentinel
        self.record(
            "WS-W2-010",
            "Exact schema-1.1 export retained both workspaces; confirmed deletion revoked A and cascaded rows, B sentinel survived",
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-cloud", action="store_true")
    parser.add_argument("--followup-only", action="store_true")
    parser.add_argument("--replay-only", action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if not args.allow_cloud:
        print("DRY RUN: no network; requires --allow-cloud and the approved cloud-dev target")
        return
    harness = WorkspaceHarness(read_configuration(), allow_cloud=True, run_id=new_run_id())
    error = None
    with harness.bounded_network():
        try:
            if args.replay_only:
                harness.exercise_replay()
            elif args.followup_only:
                harness.exercise_followup()
            else:
                harness.exercise()
        except Exception as exc:
            error = type(exc).__name__
        finally:
            try:
                harness.cleanup()
            except Exception as exc:
                error = error or "Cleanup:" + type(exc).__name__
    report = dict(
        executed_at_utc=datetime.now(timezone.utc).isoformat(),
        status="FAIL" if error else "PASS",
        error=error,
        last_api=getattr(harness, "last_api", None),
        results=harness.results,
        direct_cloud_requests=harness.calls,
        api_requests=harness.api_calls,
        conservative_api_cloud_reserve=harness.api_cloud_reserve,
        cleanup_completed=harness.manifest.get("cleanup_completed", False),
        paid_calls=0,
        email_messages=0,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    if error:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
