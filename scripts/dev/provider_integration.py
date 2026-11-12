"""At most two USDA reads and one Open Food Facts read; no LLM/email calls."""

from contextlib import contextmanager
import os
from unittest.mock import patch
import httpx
from scripts.dev.cloud_integration import CloudHarness
from scripts.dev.meal_integration import run_harness


class ProviderHarness(CloudHarness):
    @contextmanager
    def bounded_network(self):
        original = httpx.HTTPTransport.handle_request
        counts = {}

        def bounded(transport, request):
            host = request.url.host
            if request.url.scheme != "https" or host not in {
                "ecynkzptuslkuhjikzfc.supabase.co",
                "api.nal.usda.gov",
                "world.openfoodfacts.org",
            }:
                raise RuntimeError("Unapproved integration destination")
            self.calls += 1
            if self.calls > (self.limit if self.cleaning else self.limit - 20):
                raise RuntimeError("Cloud budget exceeded")
            if host != "ecynkzptuslkuhjikzfc.supabase.co":
                counts[host] = counts.get(host, 0) + 1
                if request.method != "GET" or counts[host] > (
                    2 if host == "api.nal.usda.gov" else 1
                ):
                    raise RuntimeError("Provider read budget exceeded")
            return original(transport, request)

        with patch.object(httpx.HTTPTransport, "handle_request", bounded):
            yield

    def exercise(self):
        for name in (
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SECRET_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
            "USDA_FDC_API_KEY",
        ):
            os.environ[name] = self.values.get(name, "")
        os.environ["OPEN_FOOD_FACTS_USER_AGENT"] = self.values.get("OPEN_FOOD_FACTS_USER_AGENT", "")
        from fastapi.testclient import TestClient
        from backend.app.main import app

        a = self.create_user("a")
        headers = {"Authorization": "Bearer " + a["token"]}
        with TestClient(app) as api:
            assert api.post("/api/v1/me/bootstrap", headers=headers, json={}).status_code == 200
            found = api.get("/api/v1/foods/search?q=spinach%2C%20raw", headers=headers)
            assert found.status_code == 200
            candidates = found.json().get("candidates", [])
            assert candidates
            identifier = int(candidates[0]["source_food_id"])
            food = api.get(f"/api/v1/foods/usda/{identifier}", headers=headers)
            assert food.status_code == 200
            food = food.json()
            assert (
                food["source"] == "usda"
                and food["source_food_id"] == str(identifier)
                and food["nutrient_basis_g"] == 100
            )
            self.record(
                "GL-P04-001",
                "Live USDA search/detail reached approved source and cached explicit 100-g nutrient basis; one picked candidate, no meal or clinical inference",
                status="PARTIAL",
            )
            product = api.get("/api/v1/foods/barcode/3017620422003", headers=headers)
            if product.status_code == 200:
                p = product.json()
                assert (
                    p["source"] == "open_food_facts"
                    and p["barcode"] == "3017620422003"
                    and p["nutrient_basis_g"] == 100
                )
                self.record(
                    "GL-P04-002",
                    "Live manual GTIN lookup returned explicit community-source 100-g facts; package-label and phone-camera verification remain required",
                    status="PARTIAL",
                )
            else:
                assert product.status_code in {404, 422, 503}
                self.record(
                    "GL-P04-002",
                    f"One bounded Open Food Facts lookup returned recoverable HTTP {product.status_code}; no product facts invented",
                    status="BLOCKED",
                )


if __name__ == "__main__":
    raise SystemExit(run_harness(ProviderHarness, __doc__, "bounded-live-food-providers"))
