# ADR 0010: Local refinement and independent external testing

Date: October 16, 2026. Status: accepted by user approval of the refinement plan.

## Context

The M2 pretrained model did not beat persistence and its nominal intervals were
under-covered. The user wants improvement toward +/-10 mg/dL, while explicitly
accepting that this is an aspiration rather than a maximum-error guarantee.

## Decision

Keep the 24-point two-hour forecast and preserve every original M2 result. Treat
the repeatedly inspected original test as diagnostic. Use the original validation
for configuration selection; reserve a target-purged tail of original development
for interval calibration. Fit only earlier training events. History survivors keep
their original event/split identities. Compare history lengths on identical events.

Run frozen Chronos C0 histories, direct Ridge/LightGBM and small frozen-Chronos
residual heads behind the common immutable adapter boundary. Use participant-equal
training weights and train-only transforms. Ambiguous basal values are omitted;
recorded bolus and past/current meal features never imply insulin action or dosing.
Separate full-nutrient and common-feature experiments.

Download/checksum AZT1D V1 under ignored data. Restrict ingestion to canonical CGM
records; never ingest visual-statistics exports. Freeze model/history selection to
an exclusive-create artifact before external predictions. No AZT1D fitting or
post-score selection is allowed in this protocol. Once scored, this holdout is
consumed for future tuning. Exact trajectory checks are not proof of subject identity.

Report participant-average MAE, +/-10 point/whole-curve rates, pooled error tails,
failure/attempted-event yields and participant-bootstrap uncertainty. Residual
interval calibration changes bands only. No clipping or outcome-based exclusions.

## Consequences

This is small-model training, not foundation-model training. MetaboNet development
is deferred because the user chose local data first. The limited training cohort
and validation selection bias must accompany every claim. No new model is promoted
to the application automatically; research artifacts remain separate from its DB.
No hosted services, paid inference, treatment recommendations or patient data uploads.

The frozen protocol and phase ledger are in
[planning document 11](../planning/GlycoLens_11_Model_Refinement.md); execution evidence
is in the [aggregate results report](../reports/model-refinement-results-2026-10-16.md).
