# GlycoLens

**AI-Assisted Meal Understanding and Personalized Glucose Response Prediction for Type 1 Diabetes**

GlycoLens is an inference-first, application-first capstone project. It combines verified meal nutrition, recent Type 1 Diabetes context, pretrained time-series forecasting, and personal meal-history retrieval to help users understand possible post-meal glucose behavior.

> **Research and education only:** GlycoLens does not recommend insulin doses, change clinician settings, or control an insulin pump. Forecasts are estimates and are not medical advice.

## Core questions

GlycoLens helps explore:

1. What is in this meal?
2. How did similar meals affect the user previously?
3. Given current CGM and recent context, what is the forecast for the next two hours?
4. How might the predicted trajectory change with a different portion or meal composition?

## Planned stack

- **Frontend:** Next.js, TypeScript, mobile-first PWA
- **Backend:** FastAPI, Python, Pydantic
- **Database:** Supabase PostgreSQL with pgvector
- **Forecasting:** Chronos-2, TimesFM-3, optional CGMformer, persistence baseline
- **Nutrition:** USDA FoodData Central and Open Food Facts
- **CGM integration:** Dexcom Developer Sandbox
- **Simulation:** py-mgipsim
- **Testing:** Pytest and Playwright
- **Packaging:** Docker

The system is designed as a modular monolith with replaceable forecasting-model adapters.

## Repository layout

```text
frontend/              Next.js mobile-first PWA
backend/               FastAPI application and model adapters
research/              Data preparation, experiments, and evaluation
database/              Schema migrations and seed data
data/                  Local data layout; sensitive/raw data is ignored
artifacts/             Local model and experiment artifacts
docs/planning/         Living source-of-truth project documents
docs/presentations/    Capstone presentation and RIT template
docs/architecture/     Architecture diagrams and technical notes
docs/decisions/        Architecture decision records
docs/reports/          Milestone and final reports
scripts/               Development and research utilities
tests/                 Cross-system integration and end-to-end tests
```

## Documentation policy

The planning documents in `docs/planning/` are living source-of-truth artifacts. Every substantive change to scope, models, datasets, preprocessing, experiments, evaluation, features, UX, architecture, APIs, database design, integrations, safety boundaries, deliverables, or schedule must update all affected planning documents in the same work cycle.

Start with:

- [Planning Pack README](docs/planning/GlycoLens_00_README.md)
- [Updated Project Summary](docs/planning/GlycoLens_01_Updated_Project_Summary.md)
- [Tech Stack and System Architecture](docs/planning/GlycoLens_04_Tech_Stack_and_System_Architecture.md)

See [AGENTS.md](AGENTS.md) for the repository working rules.

## Data and secret handling

Do not commit:

- CGM or health records containing personal information
- Dexcom OAuth tokens or client secrets
- USDA or other API keys
- `.env` files
- downloaded datasets
- model weights or checkpoints
- generated experiment outputs containing sensitive information

Use de-identified/public datasets, virtual-patient data, and the Dexcom sandbox unless the project receives explicit approval for real-user research.

## Status

Repository initialized from the approved GlycoLens planning pack. Application implementation has not yet started.
