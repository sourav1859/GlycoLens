# Backend

Current target: dedicated **cloud Supabase development** for new application DB/Auth
and integration acceptance. [Plan 17](../docs/planning/GlycoLens_17_Webapp_Implementation_Plan.md)
and [cloud setup](../docs/tooling/cloud-supabase-setup.md) specify migrations,
key-type compatibility, owner/trusted-write boundaries and evidence gates. Existing
local code/test evidence is historical. Cloud MCP access and ignored environment
configuration are now verified; cloud schema/Auth and live-provider acceptance
remain pending. `SUPABASE_SECRET_KEY` is the preferred server-only credential;
provider writes send it on `apikey` without treating it as a bearer JWT. The legacy
`SUPABASE_SERVICE_ROLE_KEY` fallback remains supported when the modern key is unset.

FastAPI modular monolith with implemented authenticated `/api/v1` meal, food,
timeline, simulation and forecast routes. Provider/live-camera acceptance remains
separate from offline contracts. Research batch execution is not a public API.

The recipe parser uses `LLM_MODEL=gpt-6-luna` and private `LLM_API_KEY` through
OpenAI Responses with strict JSON output. Its request/schema/validation behavior
is unchanged by the model setting. The bounded
[live comparison](../docs/reports/recipe-model-validation-2026-11-11.md) verified
access and synthetic extraction behavior within the USD 5 total cap; representative
accuracy and full workflow acceptance remain unproven.

The [responsive UI architecture](../docs/architecture/responsive-webapp-ui.md)
proposes additive profile/onboarding, dashboard/nutrition, validated catalog,
favorites and notification modules. These are future contracts, not existing
endpoints or migrations. Retain verified identity, owner-token RLS and atomic saves
while extracting frontend routes.

Forecasting implementations must remain behind a common model-adapter interface.
