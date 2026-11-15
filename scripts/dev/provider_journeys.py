"""Explicitly opted-in real-provider -> review -> save -> Chronos -> cloud read checks.

At most four USDA reads, one OFF read and one synthetic OpenAI request. No browser
or physical-device acceptance is claimed. Cloud owners/cleanup are run-scoped.
"""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import json
import os
from pathlib import Path
from unittest.mock import patch
from uuid import UUID, uuid4

import httpx
from scripts.dev.cloud_integration import CloudHarness
from scripts.dev.cloud_preflight import ROOT, read_configuration, new_run_id


class ProviderJourneyHarness(CloudHarness):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fixture = json.loads((ROOT / "config/provider-journey-validation.json").read_text())
        self.provider_counts = {}
        self.usage = {}
        self.cost = Decimal(0)
        self.provider_statuses = {}
        self.sources = []

    @contextmanager
    def bounded_network(self):
        original = httpx.HTTPTransport.handle_request

        def bounded(transport, request):
            host = request.url.host
            allowed = {
                "ecynkzptuslkuhjikzfc.supabase.co",
                "api.nal.usda.gov",
                "world.openfoodfacts.org",
                "api.openai.com",
            }
            if request.url.scheme != "https" or host not in allowed:
                raise RuntimeError("Destination outside approved synthetic test scope")
            self.calls += 1
            if self.calls > (self.limit if self.cleaning else self.limit - 20):
                raise RuntimeError("Scoped request cap reached")
            if host != "ecynkzptuslkuhjikzfc.supabase.co":
                self.provider_counts[host] = self.provider_counts.get(host, 0) + 1
                cap = {"api.nal.usda.gov": 4, "world.openfoodfacts.org": 1, "api.openai.com": 1}[
                    host
                ]
                if self.provider_counts[host] > cap:
                    raise RuntimeError("Bounded provider call limit reached")
                if host == "api.openai.com":
                    body = json.loads(request.content)
                    if (
                        request.method != "POST"
                        or request.url.path != "/v1/responses"
                        or body.get("input") != self.fixture["recipe_text"]
                        or body.get("store") is not False
                        or body.get("model") != "gpt-6-luna"
                    ):
                        raise RuntimeError(
                            "Only predeclared synthetic recipe extraction is authorized"
                        )
                elif request.method != "GET":
                    raise RuntimeError("Nutrition providers are read-only")
            response = original(transport, request)
            if host != "ecynkzptuslkuhjikzfc.supabase.co":
                self.provider_statuses.setdefault(host, []).append(response.status_code)
            if host == "api.openai.com" and response.is_success:
                response.read()  # Transport responses stream until the client consumes them.
                usage = response.json().get("usage", {})
                self.usage = {
                    name: usage.get(name, 0)
                    for name in ("input_tokens", "output_tokens", "total_tokens")
                }
                cached = usage.get("input_tokens_details", {}).get("cached_tokens", 0)
                self.cost = (
                    Decimal(self.usage["input_tokens"] - cached) * Decimal("0.10")
                    + Decimal(cached) * Decimal("0.01")
                    + Decimal(self.usage["output_tokens"]) * Decimal("0.50")
                ) / Decimal(1000000)
                assert self.cost <= Decimal("0.01")
            return response

        with patch.object(httpx.HTTPTransport, "handle_request", bounded):
            yield

    def exercise(self):
        for name in (
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SECRET_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
            "USDA_FDC_API_KEY",
            "OPEN_FOOD_FACTS_USER_AGENT",
            "LLM_MODEL",
            "LLM_API_KEY",
        ):
            os.environ[name] = self.values.get(name, "")
        os.environ.update(HF_HUB_OFFLINE="1", GLYCOLENS_DELETION_CLEANUP_WORKER="0")
        from fastapi.testclient import TestClient
        from backend.app.main import app

        user = self.create_user("a")
        headers = {"Authorization": "Bearer " + user["token"]}

        def ok(response):
            assert response.status_code == 200, "Actual API journey failed"
            return response.json()

        with TestClient(app) as api:
            ok(api.post("/api/v1/me/bootstrap", headers=headers, json={}))
            source = ok(
                api.post("/api/v1/simulation/scenario", headers=headers, json={"replay": True})
            )
            self.sources.append(source["source_session_id"])

            def search(query):
                found = ok(api.get("/api/v1/foods/search", headers=headers, params={"q": query}))
                chosen = next(
                    (
                        p
                        for p in found.get("foods", [])
                        if p.get("source") == "usda"
                        and all(
                            p.get(f) is not None
                            for f in ("calories", "carbs_g", "protein_g", "fat_g", "fiber_g")
                        )
                    ),
                    None,
                )
                if not chosen:
                    candidate = found["candidates"][0]
                    chosen = ok(
                        api.get(
                            "/api/v1/foods/usda/" + candidate["source_food_id"], headers=headers
                        )
                    )
                return chosen

            def save_forecast(food, method, grams):
                if any(
                    food.get(f) is None
                    for f in ("calories", "carbs_g", "protein_g", "fat_g", "fiber_g")
                ):
                    self.record(
                        "M2C-C2-" + {"search": "001", "barcode": "002", "recipe": "003"}[method],
                        "Live source has unknown nutrients; do not invent values to force a forecast",
                        status="PARTIAL",
                    )
                    return
                body = dict(
                    workspace="simulation",
                    source_session_id=source["source_session_id"],
                    name="Synthetic grounded " + method + " journey",
                    recorded_at=source["forecast_origin"],
                    confirmed=True,
                    idempotency_key=str(uuid4()),
                    items=[dict(food_id=food["id"], grams=grams)],
                    input_snapshot=dict(entry_method=method, confirmed=True),
                )
                mid = ok(api.post("/api/v1/meals", headers=headers, json=body))["meal_id"]
                assert ok(api.post("/api/v1/meals", headers=headers, json=body))["meal_id"] == mid
                saved = ok(api.get("/api/v1/meals/" + mid, headers=headers))[0]
                for field in ("calories", "carbs_g", "protein_g", "fat_g", "fiber_g"):
                    expected = (
                        Decimal(str(food[field]))
                        * Decimal(str(grams))
                        / Decimal(str(food["nutrient_basis_g"]))
                    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    assert abs(Decimal(str(saved[field])) - expected) <= Decimal("0.01")
                forecast = ok(
                    api.post(
                        "/api/v1/forecasts",
                        headers=headers,
                        json=dict(meal_id=mid, idempotency_key=str(uuid4())),
                    )
                )
                restored = ok(
                    api.get("/api/v1/forecasts/" + forecast["forecast_id"], headers=headers)
                )
                assert restored["forecast"] == forecast["forecast"] and restored["meal_id"] == mid
                self.record(
                    "M2C-C2-" + {"search": "001", "barcode": "002", "recipe": "003"}[method],
                    "Actual provider facts/reviewed grams/cloud save/default Chronos/persisted read pass through API; Chrome journey still pending",
                    status="PARTIAL",
                )

            palak = search(self.fixture["search"])
            save_forecast(palak, "search", self.fixture["reviewed_grams"])
            product = ok(
                api.get("/api/v1/foods/barcode/" + self.fixture["barcode"], headers=headers)
            )
            save_forecast(product, "barcode", self.fixture["reviewed_grams"])
            extracted = ok(
                api.post(
                    "/api/v1/meals/parse-recipe",
                    headers=headers,
                    json=dict(text=self.fixture["recipe_text"]),
                )
            )
            assert extracted["servings"] == 1 and len(extracted["ingredients"]) == 1
            ingredient = extracted["ingredients"][0]
            assert (
                ingredient["name"].lower().strip() in self.fixture["recipe_expected_names"]
                and ingredient["quantity"] == 100
                and ingredient["unit"] in {"g", "gram", "grams"}
            )
            assert (
                "nutrition" not in extracted
                and extracted["verification"] == "user_confirmation_required"
            )
            spinach = search("spinach, raw")
            save_forecast(spinach, "recipe", 100)
            self.record(
                "M2C-C1-006",
                "One frozen synthetic recipe passed actual reserved API extraction and independent quantity/unit/name oracle; prior eight-case selected-model fixtures remain separate, representative real-world accuracy unproven",
                status="PARTIAL",
            )

    def cleanup(self):
        super().cleanup()
        from backend.app.services.account_deletion import remove_source_artifacts

        for source in self.sources:
            remove_source_artifacts(str(UUID(source)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-cloud", action="store_true")
    parser.add_argument("--allow-paid", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.allow_cloud or not args.allow_paid:
        print("DRY RUN: explicit cloud and paid opt-ins required; zero calls")
        return 0
    harness = ProviderJourneyHarness(read_configuration(), allow_cloud=True, run_id=new_run_id())
    error = cleanup_error = None
    with harness.bounded_network():
        try:
            harness.exercise()
        except Exception as exc:
            error = type(exc).__name__
        finally:
            try:
                harness.cleanup()
            except Exception as exc:
                cleanup_error = type(exc).__name__
    accounting = json.loads((ROOT / "config/webapp-validation.json").read_text())
    prior_known = Decimal(accounting["llm_reconciled_known_estimated_test_spend_usd"])
    prior_uncertain = Decimal(accounting["llm_unreconciled_test_cost_reserve_usd"])
    new_uncertain = (
        Decimal("0.01")
        if harness.provider_counts.get("api.openai.com") and not harness.usage
        else Decimal(0)
    )
    report = dict(
        executed_at_utc=datetime.now(timezone.utc).isoformat(),
        run_id=harness.run.run_id,
        results=harness.results,
        requests=harness.calls,
        provider_calls=harness.provider_counts,
        provider_statuses=harness.provider_statuses,
        usage=harness.usage,
        estimated_new_token_cost_usd=str(harness.cost) if harness.usage else None,
        prior_known_estimated_spend_usd=str(prior_known),
        known_estimated_cumulative_token_cost_usd=str(prior_known + harness.cost),
        server_budget_reservation_per_request_usd="0.01",
        prior_uncertain_cost_reserve_usd=str(prior_uncertain),
        new_uncertain_cost_reserve_usd=str(new_uncertain),
        cumulative_estimate_plus_uncertain_reserve_usd=str(
            prior_known + harness.cost + prior_uncertain + new_uncertain
        ),
        execution_error_class=error,
        cleanup_error_class=cleanup_error,
        cleanup_completed=cleanup_error is None,
        chrome_or_camera_acceptance=False,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "results"}))
    return 1 if error or cleanup_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
