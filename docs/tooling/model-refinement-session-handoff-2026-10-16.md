# Local model-refinement handoff - October 16, 2026

## Goal and accepted decisions

Execute the user-approved local refinement sequence and document all important
evidence. Two-hour/24-point forecasts; +/-10 mg/dL aspirational. Local data first;
MetaboNet development deferred by explicit user reply. Foundation weights frozen;
small direct/residual training allowed. No automatic application model promotion.

## Outcome

Executed four Chronos histories and 20 small-model configurations. Six hours and
Ridge alpha100 residual heads won selected validation. Shared MAE 34.246 versus
persistence 43.455; within-10 27.99% versus 19.88%. This did not generalize:
AZT1D shared MAE 34.874 versus 33.865, within-10 24.98% versus 26.80%; external
gate failed. Two of 2,610 requests failed from crossing Chronos quantiles, reproduced
without fixing scores. No reliable external advantage (paired CI crosses zero).
Do not promote the head or claim 80% tolerance performance.

Original 211 C3 results reproduced to floating-point precision, with negative output
minimum -140.82 and worst error 349.11 mg/dL. No clipping/outlier deletion. Original
test/validation hashes unchanged. A 39-file ignored source/protocol ZIP retains the
executed versions; final reporting, verification and replay-guard changes followed.

## Files and repository state

New research modules: AZT1D loader/acquisition; refinement data/metrics; tabular adapter;
study, aggregate-report and verification pipelines; four synthetic test modules.
Pinned `refinement` group in pyproject/lock. ADR 0010, protocol11, aggregate report,
module READMEs and affected planning summaries are synchronized. Pre-existing M2,
application, presentation and user edits remain in the working tree. No commit,
push, migration, deployment, external messages or paid services in this cycle.
Application paths/database/frontend were not modified by this refinement.

## Documentation reviewed and updated

Planning00/01: approved direction/navigation; 02: models/data/splits; 05: protocol,
metrics/calibration/statistics; 06/10: phase/schedule boundaries; 07: verified dataset
evidence; 08: leakage/privacy/negative outputs; 09: formal research scope; 11: executed
phases and failed gate. Product/architecture planning03/04 did not require a new change:
there is no application behavior/schema/deployment change. Root/research/dataset/adapter
READMEs, reports index, ADR index and testing strategy carry the corresponding links.

## Verification and traceability

| Requirement/risk | Scenario and fixture | Layer | Implementation/evidence | Result |
|---|---|---|---|---|
| Correct tolerance and tails | Synthetic exactly10 and isolated outlier; macro versus pooled; failed denominator | Unit | test_refinement_metrics.py / refinement_metrics.py | Passed |
| Origin-only inputs | Synthetic future meal and changed held-out target cannot change features | Unit/contract | test_refinement_models.py / refinement_data.py | Passed |
| Training/calibration isolation | Synthetic purged time cuts; train-only head and separate band fit | Unit | test_refinement_models.py / tabular.py | Passed |
| External ingestion safety | Synthetic exact repeats/conflicting CGM/nonpositive glucose and ZIP traversal | Unit | test_azt1d.py / azt1d.py / acquire_azt1d.py | Passed |
| Frozen selection and failure visibility | Synthetic immutable selection, no pre-write replay, cache identity, failed requests retained | Unit | test_refinement_pipeline.py / run_refinement.py | Passed |
| Real reproducibility | Original hashes, all result hashes, 39 snapshot files, both saved heads on 162 validation events | Local integration | verify_refinement.py / ignored verification.json | Passed; max forecast difference0 |
| Independent improvement | 2,610 AZT1D attempts; 2,608 paired successes; participant bootstrap | Real scientific evaluation | dated results report / ignored result JSONs | Gate failed; retain negative result |

Final Python regression: **109 passed, one intentional opted-out real-simulator skip**.
One existing FastAPI/Starlette deprecation warning. Ruff lint passed; affected-code
format checked. Nine repository skill validators pass. No frontend/database rerun:
their implementation did not change in this cycle. Diff/ignore/exclusion checks cover
raw archive, joblib state, predictions, logs and source snapshots. Graphify was ACTIVE;
the final code-only refresh log is `.cache/model-refinement-preflight/graphify-update.log`.
Semantic document extraction/backend upload was not requested.

## Execution records and limitations

CPU study 434.60 seconds, two Torch threads; Python3.12.5, Chronos2.3.2,
scikit-learn1.7.2, LightGBM4.6.0. Full versions/source hashes are in ignored provenance.
Study stdout confirms completion; the PowerShell redirection wrapper returned status1
while capturing native stderr/progress. Subsequent result/source/hash/saved-head
verification exits successfully. Python tests/linters and report generation are separate
successful checks. Logs remain ignored; do not treat warning output as failed forecasts.

AZT1D has 25 source participants, 24 eligible, no detailed nutrients, one CGM/BGM-labelled
column and different device/cohort characteristics. Exact fingerprint checks do not
prove no shared people. Selected validation includes only10 participants. Reused
validation scores are optimistic; UOM calibration coverage was not nominal after
source shift. Saved joblib state is trusted-local only. The consumed external test
cannot be called untouched during future tuning.

## Next action

No further input was needed for this local run. For the next improvement cycle,
obtain a larger source-distinct development cohort (MetaboNet if access is arranged),
audit event timing/missingness/source differences and freeze a new validation/test
protocol before model changes. Preserve AZT1D as consumed diagnostic evidence. Do not
promise that LoRA, TCN or more data will meet +/-10. Revisit app promotion only with
independent evidence and explicit risk handling. M2 nutrition keys/provider checks,
physical camera and presentation closure remain a separate workstream.
