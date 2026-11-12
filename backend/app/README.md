# Backend Application

This directory contains the FastAPI modular monolith: verified account/onboarding,
reviewed meals, provider facts, source context, immutable forecasts/scenarios,
consumed nutrition, owned notifications and export. Caller-JWT reads and narrow
owner-derived trusted writes are separate in `db/`. See the implementation report
and ADR 0019 for current evidence and pending email/catalog/policy/hosted gates.
