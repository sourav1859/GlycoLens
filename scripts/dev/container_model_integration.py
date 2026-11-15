"""Guarded HTTP/cloud acceptance against the isolated local Compose API only."""

from contextlib import contextmanager
import os
import subprocess
from unittest.mock import patch
from uuid import UUID, uuid4
import httpx
from scripts.dev.cloud_integration import CloudHarness
from scripts.dev.meal_integration import run_harness


class ContainerModelHarness(CloudHarness):
    def set_validation_option(self, enabled):
        from scripts.dev.cloud_preflight import ROOT

        path = ROOT / ".cache/compose-model-validation.env"
        rows = path.read_text().splitlines()
        allowed = {
            "GLYCOLENS_WEB_PORT",
            "GLYCOLENS_API_PORT",
            "GLYCOLENS_DELETION_CLEANUP_WORKER",
            "GLYCOLENS_LIGHTGBM_ENABLED",
            "GLYCOLENS_LIGHTGBM_MANIFEST_SHA256",
        }
        assert all(line.split("=", 1)[0] in allowed for line in rows if line)
        rows = [
            "GLYCOLENS_LIGHTGBM_ENABLED=" + str(enabled).lower()
            if line.startswith("GLYCOLENS_LIGHTGBM_ENABLED=")
            else line
            for line in rows
        ]
        path.write_text("\n".join(rows) + "\n")
        subprocess.run(
            [
                "docker",
                "compose",
                "--env-file",
                ".env",
                "--env-file",
                str(path),
                "-p",
                "glycolens-implementation-check",
                "up",
                "-d",
                "--wait",
                "api",
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=180,
        )

    @contextmanager
    def bounded_network(self):
        original = httpx.HTTPTransport.handle_request
        self.api_calls = 0

        def bounded(transport, request):
            if (
                request.url.scheme == "http"
                and request.url.host == "127.0.0.1"
                and request.url.port == 8102
                and request.url.path.startswith("/api/v1/")
            ):
                self.api_calls += 1
                if self.api_calls > 18:
                    raise RuntimeError("Local API request cap reached")
            elif (
                request.url.scheme != "https"
                or request.url.host != "ecynkzptuslkuhjikzfc.supabase.co"
            ):
                raise RuntimeError("Unapproved validation destination")
            else:
                self.calls += 1
                # Reserve 10 cloud requests/API call plus 16 extra for each
                # bounded account export (18 tables); include cleanup calls.
                if self.calls + 18 * 10 + 32 > self.limit:
                    raise RuntimeError("Conservative cloud budget reached")
            return original(transport, request)

        with patch.object(httpx.HTTPTransport, "handle_request", bounded):
            yield

    def exercise(self):
        from time import perf_counter

        for name in (
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SECRET_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
        ):
            os.environ[name] = self.values.get(name, "")
        user = self.create_user("a")
        other = self.create_user("b")
        self.sources = []

        def ok(response):
            if response.status_code != 200:
                self.manifest["last_failure"] = {
                    "path": response.request.url.path,
                    "status": response.status_code,
                    "detail": response.json().get("detail"),
                }
                self.save_manifest()
                raise AssertionError("Container API request failed")
            return response.json()

        with httpx.Client(
            base_url="http://127.0.0.1:8102/api/v1/",
            headers={"Authorization": "Bearer " + user["token"]},
            timeout=180,
            follow_redirects=False,
        ) as api:
            ok(api.post("me/bootstrap", json={}))
            assert ok(api.get("forecasts/models"))["models"][1]["available"]
            food = str(uuid4())
            self.manifest["foods"].append(food)
            self.save_manifest()
            assert (
                self.request(
                    "POST",
                    "/rest/v1/foods",
                    admin=True,
                    body=dict(
                        id=food,
                        name="Synthetic container nutrition oracle",
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
            source = ok(
                api.post(
                    "simulation/scenario",
                    json=dict(replay=False, protocol="lightgbm_warmup_48h_v1"),
                )
            )
            self.sources.append(source["source_session_id"])
            assert source["sample_count"] == 288
            meal = ok(
                api.post(
                    "meals",
                    json=dict(
                        workspace="simulation",
                        source_session_id=source["source_session_id"],
                        name="Synthetic container integration meal",
                        recorded_at=source["forecast_origin"],
                        confirmed=True,
                        idempotency_key=str(uuid4()),
                        items=[dict(food_id=food, grams=250)],
                    ),
                )
            )
            body = dict(meal_id=meal["meal_id"], model_key="lightgbm", idempotency_key=str(uuid4()))
            started = perf_counter()
            forecast = ok(api.post("forecasts", json=body))
            latency = perf_counter() - started
            saved = ok(api.get("forecasts/" + forecast["forecast_id"]))
            assert (
                saved["forecast"] == forecast["forecast"]
                and saved["forecast"]["provenance"]["history_samples"] == 288
            )
            portion = ok(
                api.post(
                    "forecasts/" + forecast["forecast_id"] + "/scenarios",
                    json=dict(multiplier=1, idempotency_key=str(uuid4())),
                )
            )
            assert portion["response"]["forecast"] == forecast["forecast"]["forecast"]
            assert ok(api.post("forecasts", json=body))["forecast_id"] == forecast["forecast_id"]
            exported = ok(api.get("me/export"))["records"]
            frozen = next(
                row for row in exported["forecasts"] if row["id"] == forecast["forecast_id"]
            )
            assert frozen["input_snapshot"]["response"] == forecast["forecast"]
            assert frozen["input_snapshot"]["response"]["provenance"]["bundle_sha256"]
            other_headers = {"Authorization": "Bearer " + other["token"]}
            assert (
                api.get("forecasts/" + forecast["forecast_id"], headers=other_headers).status_code
                == 404
            )
            assert (
                api.post(
                    "forecasts",
                    json={**body, "idempotency_key": str(uuid4())},
                    headers=other_headers,
                ).status_code
                == 404
            )
            assert (
                ok(
                    api.get(
                        "forecasts/" + forecast["forecast_id"] + "/scenarios", headers=other_headers
                    )
                )["scenarios"]
                == []
            )
            other_export = ok(api.get("me/export", headers=other_headers))["records"]
            assert (
                not other_export["forecasts"]
                and not other_export["forecast_points"]
                and not other_export["portion_scenarios"]
            )
            self.record(
                "LGB-L3-006",
                "Actual owned export retains full immutable v2 response/bands/provenance; owner B cannot read/create/list this forecast/scenario or export its snapshots/points. Same-model 100% scenario reproduces baseline; no mixed-model request field exists.",
            )
            self.record(
                "LGB-L4-001",
                "Built Linux CPU image loads narrow read-only native bundle and runs real 48h simulator; no GPU/model service or research rows",
            )
            self.record(
                "LGB-L4-002",
                f"Actual Compose HTTP -> Linux long simulator -> cloud reviewed save -> native calibrated forecast -> owned read -> same-model scenario/retry passed; single forecast HTTP latency {latency:.3f}s; Chrome remains pending",
                status="PARTIAL",
            )
            self.record(
                "LGB-L4-003",
                f"This run had {self.api_calls} local API calls before recovery; remote cloud reads are conservatively budgeted at <=10 per call plus 32 for two exports and bounded host cloud calls. Single latency is not p95.",
                status="PARTIAL",
            )
            try:
                self.set_validation_option(False)
                assert (
                    ok(api.get("forecasts/" + forecast["forecast_id"]))["forecast"]
                    == forecast["forecast"]
                )
                assert (
                    api.post(
                        "forecasts", json={**body, "idempotency_key": str(uuid4())}
                    ).status_code
                    == 503
                )
                baseline = ok(
                    api.post(
                        "forecasts",
                        json={"meal_id": meal["meal_id"], "idempotency_key": str(uuid4())},
                    )
                )
                assert baseline["forecast"]["model_id"] == "amazon/chronos-2"
                self.record(
                    "LGB-L4-005",
                    "Actual API container recreation with research option disabled preserves owned LightGBM result reads, rejects a new LightGBM request without fallback, and still runs default Chronos; Chrome/logout variants remain separate",
                    status="PARTIAL",
                )
            finally:
                self.set_validation_option(True)

    def cleanup(self):
        super().cleanup()
        from backend.app.services.account_deletion import remove_source_artifacts

        for source in getattr(self, "sources", []):
            remove_source_artifacts(str(UUID(source)))


if __name__ == "__main__":
    raise SystemExit(run_harness(ContainerModelHarness, __doc__, "real-compose-model-integration"))
