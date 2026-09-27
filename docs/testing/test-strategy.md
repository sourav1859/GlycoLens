# GlycoLens Test Strategy

## Principles

- Derive tests from requirements, risks, and safety boundaries before enumerating cases.
- Use the lowest layer that proves the behavior without duplicating the same assertion everywhere.
- Keep fixtures deterministic, synthetic, or demonstrably de-identified.
- Test safe degradation for missing, stale, delayed, malformed, and partial data.

## Planned layers

| Layer | Primary responsibility |
|---|---|
| Unit/property | Calculations, transformations, boundaries, invariants, and metric implementations. |
| Integration | Database, RLS, provider adapters, caching, retries, and partial failures. |
| Contract/API | Schemas, authorization, idempotency, malformed payloads, and error contracts. |
| Playwright/end-to-end | Mobile meal-to-forecast flow, keyboard use, accessibility, slow network, fallback, and safety messaging. |
| Security | Secrets, server/client boundaries, input validation, authorization, abuse controls, and privacy-safe logging. |
| Performance | p50/p95/p99 latency, memory, throughput, failure rate, and reproducibility. |
| Scientific evaluation | Leakage controls, subject/time splits, event boundaries, baselines, metrics, uncertainty, and unusable-run accounting. |

## Required risk coverage

Cover happy paths, boundaries, invalid inputs, missing data, time zones and DST, concurrency, retries, timeouts, external API degradation, authorization, privacy, accessibility, recovery, and stale CGM behavior where relevant.

No product test commands exist yet. Add commands only when their runners and configurations are checked in and locally executable.
