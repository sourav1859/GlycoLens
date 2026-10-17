# ADR 0013: frozen Chronos corrections with matched direct controls

Date: October 16, 2026. Status: accepted within the approved Phase 5 implementation.

## Context

Phase 4 improved average validation error but within +/-10 remained poor. A correction
must demonstrate value beyond the stronger direct model, without changing foundation
weights or consuming independent tests. Training backbone failures can also change
the available training population and confound an unpaired comparison.

## Decision

Use the frozen six-hour C2 backbone, the best failure-free Chronos variant from
Phase 3. Cache one origin-known training forecast per Phase 4 common-pool meal,
persist failures without retries and keep labels out of the forecast cache. Fit
correction heads only where the frozen forecast exists. Fit fixed direct controls
on exactly those same meals, with the same participant weights and subject folds.

Reuse the 24-hour glucose / six-hour event features and add the 24 frozen predicted
changes, preserving recorded units/masks. Extract shared regression helpers without
changing direct-model behavior. Compare four fixed Ridge/LightGBM corrections using
training-only CV; freeze winners/refits before validation. Reuse identical verified
validation C2 predictions and original Phase 3/4 results.

Keep lowest-MAE validation ranking separate from advancement. A correction needs
at least 5% lower macro MAE than original Phase 4 LightGBM, nondecreasing within-10,
nonincreasing pooled p95 and zero failures to advance. Otherwise retain the incumbent.
Matched-control differences and descriptive participant intervals accompany the
decision; selected validation evidence is not independent confirmation.

Save only small head state; strip a live backbone during serialization and require
explicit attachment or verified cached predictions after reload. Corrected quantiles
are deterministic placeholders, not shifted/claimed native probability bands. Public
live-backbone adapter latency includes backbone work; cached batch-head timings are
labeled separately. Two execution/source freezes cover backbone caching and head
training. All health artifacts and weights remain ignored; no application change.

## Consequences

This tests a bounded correction design while separating training-population effects.
Frozen predicted future trajectories are valid inputs; observed future glucose stays
in labels. Corrections carry the backbone's inference cost and failure dependency.
They may lose to a simpler direct model. Neither a gate pass nor failure establishes
clinical accuracy or exhausts other possible correction architectures. Calibration
and reserved tests remain for Phase 6.

See [protocol 15](../planning/GlycoLens_15_MetaboNet_Chronos_Correction.md).
