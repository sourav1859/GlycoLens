# Measurement Protocol

Define the hypothesis, metric, and success threshold before optimization. Compare before and after results using equivalent hardware, runtime, dataset, workload, warm-up, and sample-count conditions.

Record:

- date, branch, and commit identifiers;
- operating system, hardware, runtime, dependency, and model versions;
- exact commands and configurations;
- dataset or synthetic workload identity and sample count;
- p50, p95, and p99 where meaningful;
- error rate, CPU, memory, and compute cost where meaningful;
- variance, confidence interval, or repeated-run spread;
- raw artifact location under ignored `artifacts/benchmarks/`;
- limitations and any uncontrolled variables.

Calculate absolute and percentage change from the same baseline. Do not promote cherry-picked, incomparable, or unreproduced results. Store only small sanitized summaries in `docs/impact/`.
