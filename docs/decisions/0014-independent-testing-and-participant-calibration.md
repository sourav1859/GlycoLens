# ADR 0014: Frozen independent testing and participant calibration

Accepted October 16, 2026.

## Decision

Freeze original Phase 4 LightGBM as the primary research candidate, original Ridge
as a diagnostic challenger and persistence as the baseline. Neither Phase 5 correction
passed its incremental gate. Do not refit point models or select a new winner on test.

Use one deterministic hash-selected eligible meal per separate calibration participant.
At target coverage 80%, compute the exact finite-sample order statistic separately for
each horizon and separately for maximum trajectory error. Save immutable interval
state before reserved CGM/event projection. The symmetric interval wrapper preserves
the common contract and point forecast; it does not inherit deterministic placeholders
or claim learned conditional quantiles. Exchangeability and coverage under study shift
are unverified.

Access reserved data through a dedicated, completed-calibration gate. Keep the existing
development iterator's role guard. Primary identities are absent from all publisher
training; pediatric PEDAP is a separate source test. Keep publisher file segments
separate, cap hash-selected origins before eligibility and screen partial exact
trajectory duplicates before scoring. No outcome-driven exclusions or replacements.

Two checksummed execution/source freezes share candidate/input/model hashes and chain
test execution to completed calibration. Point-model states must remain unchanged.
Preload numerical libraries before applying resource limits and record actual pools.
Completed stages refuse replay; failures/partial artifacts remain for review.

## Consequences

The final stage can confirm or reject the frozen development improvement gate. It
cannot authorize promotion through a better test score. Broad uncertainty ranges do
not solve point accuracy. Report failures, tails, whole-curve tolerance, marginal and
simultaneous coverage, participant variation and predeclared source/origin/meal/mask
subgroups. After execution both reserved cohorts are consumed; future tuning needs
fresh confirmation. No application/database change, foundation training, clinical
claim, dosing behavior or deployment follows from this decision.

See [protocol 16](../planning/GlycoLens_16_MetaboNet_Independent_Evaluation.md),
[results](../reports/metabonet-phase6-independent-2026-10-16.md) and
[verification handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md).
