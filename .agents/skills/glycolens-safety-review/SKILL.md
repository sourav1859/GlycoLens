---
name: glycolens-safety-review
description: Review GlycoLens medical-facing language, forecasts, health-data handling, authentication, storage, third-party APIs, security tests, and release readiness.
---

# GlycoLens Safety Review

During ordinary development, inspect only checklist sections affected by the change. Run the complete review for release or milestone gates and changes crossing several risk areas. Use Sol with high reasoning for medical-facing behavior, authorization, leakage, privacy, and release readiness.

1. Read `SECURITY.md`, `docs/planning/GlycoLens_08_Risks_Safety_and_Scope.md`, and [references/safety-checklist.md](references/safety-checklist.md).
2. Preserve the research/education-only boundary. Reject insulin-dose advice, pump control, clinician-setting changes, diagnosis, safe/unsafe meal claims, or unsupported clinical accuracy claims.
3. Check uncertainty, provenance, missing/stale CGM behavior, out-of-distribution warnings, external-service degradation, and safe failure.
4. Check temporal and subject leakage, future-event contamination, and retrieval chronology.
5. Check server/client secret boundaries, Supabase row-level security, authorization, input validation, abuse controls, dependency risk, and privacy-safe logging.
6. Inspect the diff and Git status for PHI, credentials, tokens, private datasets, weights, local databases, caches, and sensitive generated artifacts.
7. Define only scoped, non-destructive security tests against owned local or development systems.
8. Report blocking findings separately from defense-in-depth suggestions and update affected living documents.

Never conduct intrusive testing against third-party, sandbox-provider, or production services without explicit authorization.
