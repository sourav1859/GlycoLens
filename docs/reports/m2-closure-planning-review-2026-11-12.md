# M2 closure and LightGBM planning review

Date: November 12, 2026. Baseline inspected: `75191e2f654d9e1cbe4a3676d2948131013ec94b`.
Scope: [plan 18](../planning/GlycoLens_18_M2_Closure_and_LightGBM_Integration.md),
[ADR 0022](../decisions/0022-opt-in-lightgbm-research-integration.md) and
[58 designed tests](../testing/m2-closure-lightgbm-test-cases.md).
This is a planning/readiness review, not new application acceptance.

## Accepted decisions

User chose Chronos default, opt-in LightGBM research, a separate longer synthetic
scenario, Chrome testing and future physical-camera validation. Approved OFF
application contact was saved only in ignored root `.env`; no public key/project
or new model service is needed. API reload remains necessary before using that
new setting. No tracked contact address or credentials were added.

## Readiness observed

- Value-free private configuration check: approved cloud target, public/server
  key presence, USDA/OpenAI key presence, selected parser model, frontend/backend
  cloud match, simulator environment and Chronos cache all true. OFF contact-format
  check is now true. Email-recovery UI remains disabled in development. These are
  configuration observations, not fresh successful provider/Auth journeys.
- Selected frozen LightGBM bundle and calibration bands exist. Their hashes match
  the corresponding completion manifests; completion-manifest sidecar hashes and
  calibration record checksum match, with primary candidate `lightgbm_direct`.
  No model was deserialized and no research rows were projected. This check does
  not verify all artifacts, predictions, dependencies or serving compatibility.
- Source review confirms two Chronos construction paths, two-hour current context,
  incompatible LightGBM history/unit/mask requirements, current-carb-only frozen
  meal features, placeholder direct-adapter bounds, saved calibration wrapper,
  API/SQL interval-bound mismatch and missing CPU serving packaging/loader.
- Official OFF documentation checked: public reads use custom application identity;
  v3 is recommended, v2 still supported for compatibility; provider facts and
  throughput require care. [Primary source](https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/).
- Native LightGBM persistence and trusted/version-compatible Python deserialization
  requirements support L0 packaging gates. [LightGBM](https://lightgbm.readthedocs.io/en/v4.6.0/pythonapi/lightgbm.Booster.html),
  [scikit-learn](https://scikit-learn.org/stable/model_persistence.html).

## Test/evidence disposition

All 58 supplemental tests start NOT_RUN with expected results and no actual/evidence
claim. Existing webapp ledger remains 146 cases: 22 PASS, 87 PARTIAL, 32 BLOCKED,
5 NOT_RUN. The only result-disposition change is GL-P04-003/004: earlier BLOCKED
is preserved as prior status, current NOT_RUN has DEFERRED_BY_USER scope. The
earlier checkpoint/publication counts remain historical run records. No test
was newly passed or milestone closed by this planning work.

Planning verification covers case uniqueness/counts/phase mapping, all-NOT_RUN
state, legacy camera dispositions/counts, new relative links, weighted ADR totals,
private-file exclusion, absence of keys/contact in added tracked text and whitespace.
Outcome: **PASS for these document checks**, including 58 unique planned cases,
146 preserved legacy IDs, 25 new local links and matching current phase counts.
This is document validation; it cannot satisfy any planned runtime test.

## Living documentation impact

| Reviewed planning documents | Action and reason |
|---|---|
| 00, 01 | Updated navigation/current accepted direction and planning-versus-execution status |
| 02, 11 | Updated model candidate/application follow-through; research protocols/results remain frozen |
| 03 | Planned selector, input/interval explanation and accepted Chrome/device scope |
| 04 | Planned registry/builders/artifact/transport/storage/packaging boundaries |
| 05 | Synthetic sensitivity/parity versus prospective accuracy; no consumed-cohort reuse |
| 06 | C0-C3 versus L0-L4 dependencies/estimates, accepted camera deferral, unchanged course dates |
| 08 | Artifact trust, units/masks, owner identity, intervals, provider/privacy risks |
| 09 | Scope/specification consistency without changing hypotheses or claiming completion |
| 10 | Reconciled stale prerequisite text and original M2 closure gates; historical evidence retained |
| 12–16 | Reviewed relevant feature/calibration/consumed-cohort boundaries; no protocol/result edits because no research execution or reselection is authorized |
| 17 | Supplemental track link, retained Chronos default and explicit future physical-camera acceptance |
| 18 | Created detailed remaining-work plan, prerequisites, dependencies, implementation gates and validation |

Root README, responsive UI architecture, ADR index, original test catalog/ledger
and dated presentation-note/outline status are synchronized. Native deck unchanged.
Graphify is refreshed after final supported document edits, with local structure
and curated semantics only; graph artifacts stay ignored. No remote semantic
backend, paid call, migration, model inference/training, cloud mutation, commit,
push or hosted deployment is part of this work cycle.
