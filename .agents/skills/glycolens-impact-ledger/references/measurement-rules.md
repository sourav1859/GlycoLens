# Measurement Rules

Record tool, dependency, model, operating-system, and runtime versions; hardware; commands; configuration; branch and commit identifiers; data/workload identity; warm-up; sample count; p50/p95/p99 where relevant; error rate; CPU/memory/compute cost; variance or confidence interval; raw artifact paths; and limitations.

Use:

- absolute change = after - before;
- percentage change = `(after - before) / before * 100` when the baseline is nonzero;
- percentage improvement with an explicit direction, because lower latency/error and higher throughput/accuracy use opposite signs.

Do not compare different datasets, hardware, concurrency, caches, model versions, or measurement windows without labeling the result non-equivalent.
