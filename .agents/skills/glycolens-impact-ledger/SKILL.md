---
name: glycolens-impact-ledger
description: Measure and record reproducible GlycoLens improvements in performance, cost, reliability, accessibility, model quality, or operational load.
---

# GlycoLens Impact Ledger

1. Define a hypothesis, primary metric, and success threshold before optimization.
2. Read [references/measurement-rules.md](references/measurement-rules.md) and copy [assets/measurement-record.md](assets/measurement-record.md) for the experiment.
3. Measure before and after under equivalent environment, dataset, workload, warm-up, and sample-count conditions.
4. Store raw local output under ignored `artifacts/benchmarks/` and a small sanitized report under `docs/impact/`.
5. Calculate absolute and percentage change from the same baseline. Include latency percentiles, errors, resource use, and uncertainty where meaningful.
6. Separate measured facts from estimates and hypotheses; reject cherry-picked or non-reproducible claims.
7. Add a concise ledger row only after reproduction.

Generate portfolio or resume language only from reproduced evidence and retain enough context to avoid misleading claims.
