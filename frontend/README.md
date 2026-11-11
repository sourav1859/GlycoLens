# Frontend

New implementation uses a dedicated **cloud Supabase development project**, with
verified email/password accounts. Follow [plan 17](../docs/planning/GlycoLens_17_Webapp_Implementation_Plan.md)
and [cloud setup](../docs/tooling/cloud-supabase-setup.md). The existing anonymous
demo remains baseline code until cloud account routes are implemented;
do not run the old local-key configuration helper for the new workflow.
Cloud URL/publishable-key configuration is saved in ignored `.env.local`;
`.env.example` documents the public build variables. Private keys stay in root `.env`.

Mobile-first Progressive Web App built with Next.js and TypeScript.

The current `/` entry renders the authenticated anonymous-demo `MealWorkflow`:
simulator/replay context, food/barcode/recipe input, confirmed meal save, Chronos
forecast and numeric historical matches. It uses plain CSS and an SVG chart.
Live food-provider and physical camera acceptance remain open.

The November 10 [responsive UI architecture](../docs/architecture/responsive-webapp-ui.md)
defines the planned shared shell, account/onboarding and multi-page extraction for
mobile/tablet/desktop. Its routes are a design contract, not implemented pages.
The [Figma audit](../docs/reports/figma-reference-review-2026-11-10.md) records the
reference adaptations and exclusions.

Milestone 1 includes a synthetic demonstration flow that calls the local FastAPI service and
renders observed CGM history, a median two-hour forecast, a q10-q90 uncertainty band, and
30/60/120-minute summaries. It is a contract and visualization demonstration, not a clinical tool.

## Commands

Run from the repository root after `pnpm install --frozen-lockfile`:

```powershell
pnpm frontend:dev
pnpm frontend:lint
pnpm frontend:test
pnpm frontend:typecheck
pnpm frontend:build
```

Target feature areas (not a completion checklist):

- onboarding and demo mode
- CGM timeline
- barcode, food-search, and recipe meal capture
- nutrition verification and provenance
- two-hour probabilistic forecast visualization
- similar-meal history
- portion comparison
- actual-versus-predicted follow-up

The root workspace pins the supported Node and pnpm versions. Never place private provider or
Supabase secret/service-role keys in `NEXT_PUBLIC_*` variables; those values enter the browser
bundle. Supabase publishable/anon configuration is browser-visible by design and still requires RLS.
`NEXT_PUBLIC_API_URL` may contain only the public FastAPI origin and defaults to
`http://127.0.0.1:8000`.
