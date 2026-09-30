# Frontend

Mobile-first Progressive Web App built with Next.js and TypeScript.

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

Primary feature areas:

- onboarding and demo mode
- CGM timeline
- barcode, food-search, and recipe meal capture
- nutrition verification and provenance
- two-hour probabilistic forecast visualization
- similar-meal history
- portion comparison
- actual-versus-predicted follow-up

The root workspace pins the supported Node and pnpm versions. Do not place API credentials in
`NEXT_PUBLIC_*` variables because browser-visible variables are included in the client bundle.
`NEXT_PUBLIC_API_URL` may contain only the public FastAPI origin and defaults to
`http://127.0.0.1:8000`.
