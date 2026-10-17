# ADR 0008: Milestone 2 evaluation and recorded-event covariates

Status: Accepted under the October 14, 2026 implementation approval.

## Decision

Preserve the immutable forecast-request/held-out-target boundary and modular monolith.
Temporal development/validation/test cuts use 60/20/20 percent of each participant's
eligible event time span, ending at the last target endpoint. Purge targets crossing
cuts. Already-observed past history may cross a cut; this is not permission to retrieve
future outcomes or select on test data. Subject holdouts must be explicit, nonempty,
disjoint and leave development subjects.

Event identity hashes pinned release, participant and meal timestamp, never outcome
values. Configuration hashes include window, split and feature versions. Manifests
and event rows stay ignored. Accuracy uses common successful events, accompanied by
requested/failure counts and participant macro averages. A failed model must not
appear more accurate merely because difficult events disappear.

Freeze validation-selected model/configuration before test evaluation. Deterministic
persistence has no probabilistic coverage claim. Report pinball losses/coverage/width;
three deciles do not define exact CRPS. CI and final test evaluation remain closure work.

## Feature representation: recorded_events_v1

C2 adds carbohydrate; C3 uses available source macros, omitting unprovided calories.
Bolus observations are additive source units. Basal observations retain insulin_kind
in separate channels and explicit source_U_or_U_per_hour units. Collapse exact
same-time repeats; reject conflicting same-kind basal values. R/L labels alone do not
justify a physiological rate/dose conversion.

Grid inputs record values and observation-count masks. Within a basal bin use the last
observation, not the sum of rates. Zero means no recorded event in that bin, not zero
active insulin. Missing streams have no channel. Older six-hour bolus totals and last
basal observations use explicit descriptors and presence flags; they are not insulin
on board or inferred active-rate schedules. These origin-known summaries repeat over
the input history grid.

Meal macros are impulses at origin. Future meal impulses are zero under the core
filtered no-follow-up-meal assumption. Unknown future insulin/activity is never
provided. No physiological absorption curve is assumed or trained.

Both models receive this representation. Empirically compare C0-C3; models are not
assumed to understand channel names or T1D physiology. Representation changes require
a new identity and validation rerun. Missing logging and source-unit ambiguity remain
limitations, not reasons to fabricate context.

## Alternatives and consequences

Mixing basal values was rejected because rate/dose semantics differ. Inferring insulin
action or an active basal schedule without source evidence was rejected. CGM-only
inference cannot answer the required ablation. Recorded-event features are reproducible
but may transfer poorly; evaluate rather than assume usefulness.

Pin TimesFM 3.0.2 and official checkpoint revision
43046b85ec22d584a13f8098c2ed39c889e129c2. Downloaded weights remain research-only,
non-commercial/non-production. Tests are offline by default; reject invalid quantiles
rather than silently repair them. Real validation is required before selection.
