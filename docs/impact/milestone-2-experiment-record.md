# Milestone 2 experiment record

Date: October 14, 2026. Initial full experiment, not a reproduced optimization or
portfolio improvement claim. No improvement row is added to the impact ledger.

Hypotheses: pretrained error below persistence; insulin/nutrition improve CGM-only
inference. Primary metric: participant-average meal-window MAE, lower is better.
Selection is validation-based; no statistical success is presumed.

Source base: 971a8c8b2bc4fd033c0eb643d5228037de69f17d with approved uncommitted M2 changes.
Runtime: Windows, Python 3.12.5, CPU PyTorch 2.14.0, Chronos package 2.3.2, TimesFM 3.0.2,
eight physical/sixteen logical CPUs, 27.72 GiB RAM. Exact dependency lockfiles and
checkpoint pins identify the implementation. No GPU or weight training is used.

Workload: pinned T1D-UOM V1.0.4, 927 eligible events; 177 validation and 211 test
requests per configuration. Identical requested events, horizon and feature representation
within each split. Loading is separate; wall percentiles include conversion/scoring.
RSS samples are post-run observations, not peak-memory claims. Event sets with
failures use explicit common-success intersections and reported denominators.

Results, paired participant intervals, load/latency and limitations are in the
model-results report and ignored artifacts/evaluation-results/m2-validation.json
and m2-test.json. The selected Chronos C3 does not beat persistence on held-out error.
Context comparisons are observational model results, not causal physiology or
clinical benefit. Independent full reproduction remains future work; do not promote
initial context-error differences into an unqualified improvement claim.
