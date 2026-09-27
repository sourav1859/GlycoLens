# Architecture Decision Framework

Use weights that reflect the decision rather than forcing a default. Score each option from 1 (poor) to 5 (strong), multiply by weight, and explain every non-obvious score.

Suggested criteria:

| Criterion | Typical concern |
|---|---|
| Delivery fit | Semester schedule and one-developer complexity |
| Safety/privacy | Health-data exposure and safe failure behavior |
| Correctness/reliability | Data integrity, retries, partial failure, recovery |
| Performance/cost | Latency, memory, compute, external-service cost |
| Maintainability/testability | Clear boundaries, replacement, deterministic tests |
| Observability | Provenance, model/config identity, diagnosable failures |
| Migration/rollback | Reversibility and data/schema compatibility |

Document assumptions, confidence, decisive evidence, and the condition that would reverse the decision.
